from asyncio import get_running_loop
from concurrent.futures import ProcessPoolExecutor

import httpx
from bs4 import BeautifulSoup, SoupStrainer
from httpx import HTTPError

from .db import Link
from .html import render_link_html
from .logging import log
from .websockets import ConnectionManager

process_pool = ProcessPoolExecutor(max_workers=1)


async def _get_new_link_url_and_title(link: Link) -> Link:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(str(link.url), follow_redirects=True)
        except HTTPError:
            log.info(f"HTTPError: {link.url}")
            return link
    link.url = str(response.url)  # type: ignore

    loop = get_running_loop()
    link_title_awaitable = loop.run_in_executor(
        process_pool, _parse_content_for_link_title, link, response.text
    )
    link = await link_title_awaitable

    return link


def _parse_content_for_link_title(link: Link, content: str) -> Link:
    """CPU bound, so runs in a separate process to avoid locking event loop"""
    strainer = SoupStrainer("title")
    soup = BeautifulSoup(content, features="lxml", parse_only=strainer)
    title_tag = soup.find("title")
    if title_tag is not None:
        link.title = title_tag.text  # type: ignore
    return link


async def save_and_broadcast_new_link_url_and_title(
    link: Link, connection_manager: ConnectionManager
) -> None:
    """
    Navigates to the user provided URL, checks for an updated address or title,
    saves to DB and broadcasts to clients (if necessary)
    """
    updated_link = await _get_new_link_url_and_title(link=link)
    if (link.url != updated_link.url) or (link.title != updated_link.title):
        await updated_link.save()
        response = render_link_html(link=updated_link)
        log.debug(response)
        await connection_manager.broadcast(response)
