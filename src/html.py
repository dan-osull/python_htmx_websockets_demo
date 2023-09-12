from fastapi import Request
from fastapi.templating import Jinja2Templates

from .config import TEMPLATES_PATH
from .db import Link

templates = Jinja2Templates(directory=TEMPLATES_PATH)


def render_link_html(link: Link) -> str:
    template_response = templates.TemplateResponse(
        "render_link.jinja2",
        {
            "request": Request(scope={"type": "http"}),
            "link": link,
        },
    )
    return template_response.body.decode()


def render_all_links_html(all_links: list[Link]) -> str:
    link_html = '<div id="main">'
    for link in all_links:
        link_html += render_link_html(link=link)
    return link_html + "</div>"


def render_append_html(link: Link) -> str:
    return (
        '<div id="main" hx-swap-oob="beforeend">'
        + render_link_html(link=link)
        + "</div>"
    )


def render_delete_html(link: Link) -> str:
    return f'<div id="{link.div_id}" hx-swap-oob="delete"></div>'
