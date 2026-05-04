"""Render the Wrapped poster (HTML + Jinja2) to a print-quality A3 PDF.

The template lives at ``darkroom/templates/wrapped/poster.html`` and is
treated as immutable: we only inject data and run headless Chromium.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "wrapped"


def _absolutize(image: str) -> str:
    p = Path(image)
    if not p.is_absolute():
        p = TEMPLATES_DIR / image
    return p.resolve().as_uri()


def render_pdf(
    scenes: Sequence[dict[str, Any]],
    stats: dict[str, Any],
    closing_line: str,
    out_path: str,
) -> str:
    """Render scenes + stats into ``out_path`` as a single A3-portrait PDF.

    ``stats`` is the surrounding metadata dict — ``title``, ``subtitle``,
    ``signature``, plus the stats list under key ``stats``. This shape
    matches ``templates/wrapped/sample.json`` minus scenes/closing_line.
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    rendered_scenes: list[dict[str, Any]] = []
    for scene in scenes:
        sc = dict(scene)
        sc["image"] = _absolutize(sc["image"])
        rendered_scenes.append(sc)

    payload = {
        "title": stats.get("title", ""),
        "subtitle": stats.get("subtitle", ""),
        "signature": stats.get("signature", ""),
        "style": stats.get("style", "dark-editorial"),
        "stats": stats.get("stats", []),
        "scenes": rendered_scenes,
        "closing_line": closing_line,
    }

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    env.filters["split"] = lambda s, sep="\n": s.split(sep)
    html = env.get_template("poster.html").render(**payload)

    rendered_html = out.with_suffix(".html")
    rendered_html.write_text(html)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(rendered_html.resolve().as_uri(), wait_until="networkidle")
        page.wait_for_timeout(800)
        page.pdf(
            path=str(out),
            width="297mm",
            height="420mm",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            prefer_css_page_size=True,
        )
        browser.close()

    return str(out)
