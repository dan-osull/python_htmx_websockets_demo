import json
from asyncio import create_task
from enum import StrEnum, auto
from typing import Any, Awaitable, Callable
from uuid import UUID

import tortoise.connection
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import AnyHttpUrl, BaseModel, ValidationError
from tortoise import Tortoise

from .config import SQLITE_DB_URL, TEMPLATES_PATH
from .db import Link
from .emoji import Emoji, get_random_emoji
from .html import render_all_links_html, render_append_html, render_delete_html
from .http_client import save_and_broadcast_new_link_url_and_title
from .logging import log
from .websockets import ConnectionManager

RequestDict = dict[str, Any]
"""JSON payload from Websocket client"""


class FormCreate(BaseModel):
    url: AnyHttpUrl


async def create_link(
    request: RequestDict, connection_manager: ConnectionManager, user_emoji: Emoji
) -> None:
    form = FormCreate(**request)
    link = Link(url=form.url, user_emoji=user_emoji)
    await link.save()

    response = render_append_html(link=link)
    log.debug(response)
    await connection_manager.broadcast(response)

    create_task(
        save_and_broadcast_new_link_url_and_title(
            link=link, connection_manager=connection_manager
        )
    )


class FormDelete(BaseModel):
    id: UUID


async def delete_link(
    request: RequestDict, connection_manager: ConnectionManager, _user_emoji: Emoji
) -> None:
    form = FormDelete(**request)
    link = await Link.get(id=form.id)
    await link.delete()

    response = render_delete_html(link)
    log.debug(response)
    await connection_manager.broadcast(response)


class ApiAction(StrEnum):
    CREATE = auto()
    DELETE = auto()


ApiActionFunc = Callable[[RequestDict, ConnectionManager, Emoji], Awaitable[None]]
API_ACTION_FUNC_TABLE: dict[ApiAction, ApiActionFunc] = {
    ApiAction.CREATE: create_link,
    ApiAction.DELETE: delete_link,
}
app = FastAPI()
connection_manager = ConnectionManager()


@app.on_event("startup")
async def init_orm() -> None:
    """Based on `tortoise.contrib.fastapi.register_tortoise`"""
    await Tortoise.init(db_url=SQLITE_DB_URL, modules={"models": ["src.db"]})
    await Tortoise.generate_schemas()


@app.on_event("shutdown")
async def close_orm() -> None:
    await tortoise.connection.connections.close_all()


INDEX_PATH = TEMPLATES_PATH / "index.html"
with open(INDEX_PATH, "r") as file:
    INDEX_HTML = file.read()


@app.get("/")
async def index_html() -> HTMLResponse:
    return HTMLResponse(INDEX_HTML)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    # Register new connection in manager so it gets broadcast messages
    await connection_manager.connect(websocket)

    try:
        # Send HTML for existing Links to this new client
        links = await Link.all()
        await websocket.send_text(render_all_links_html(links))

        user_emoji = get_random_emoji()
        while True:
            # Wait for a message from the client
            raw_request: str = await websocket.receive_text()
            log.debug(raw_request)
            request: RequestDict = json.loads(raw_request)
            action = ApiAction(request["action"])
            function = API_ACTION_FUNC_TABLE[action]

            try:
                # Run the function for the requested action
                await function(request, connection_manager, user_emoji)
            except ValidationError as exception:
                # Pydantic error - triggered if Link URL is invalid
                log.warning(exception)

    except WebSocketDisconnect as exception:
        connection_manager.disconnect(websocket)
        if exception.code not in [1001, 1006]:
            # Codes seen in normal operation:
            # 1001 Going away
            # 1006 Closed abnormally
            # https://www.rfc-editor.org/rfc/rfc6455#section-7.4.1
            raise exception
