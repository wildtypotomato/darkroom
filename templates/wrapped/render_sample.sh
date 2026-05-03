#!/usr/bin/env bash
# Renders the sample Wrapped poster (PDF) and recap (MP4) from sample.json.
# Pure preview pipeline — does not touch memory_book/src/.
#
# Outputs:
#   /tmp/wrapped_sample/poster.pdf
#   /tmp/wrapped_sample/recap.mp4

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="/tmp/wrapped_sample"
mkdir -p "$OUT"

echo "==> Working dir: $HERE"
echo "==> Output dir:  $OUT"

# ---------- 1. Render poster.html → PDF via Playwright ----------

echo ""
echo "==> [1/2] Rendering poster.pdf …"

# Pick a python that has playwright; install it on demand.
PYBIN="${PYTHON:-python3}"
if ! "$PYBIN" -c "import playwright, jinja2" 2>/dev/null; then
  echo "    installing playwright + jinja2 (one-time) …"
  "$PYBIN" -m pip install --quiet --break-system-packages playwright jinja2 || \
    "$PYBIN" -m pip install --quiet playwright jinja2
  "$PYBIN" -m playwright install chromium >/dev/null
fi

"$PYBIN" - "$HERE" "$OUT" <<'PY'
import json, sys, asyncio, pathlib
from jinja2 import Environment, FileSystemLoader, select_autoescape

here = pathlib.Path(sys.argv[1])
out  = pathlib.Path(sys.argv[2])

data = json.loads((here / "sample.json").read_text())

# Resolve image paths against the template dir so the rendered HTML
# (which lives in /tmp) still finds the photos.
def absolutize(rel):
    return (here / rel).resolve().as_uri()

for s in data["scenes"]:
    s["image"] = absolutize(s["image"])

env = Environment(
    loader=FileSystemLoader(str(here)),
    autoescape=select_autoescape(["html"]),
)
# expose str.split inside the template
env.filters["split"] = lambda s, sep="\n": s.split(sep)

tmpl = env.get_template("poster.html")
html = tmpl.render(**data)

rendered = out / "poster.html"
rendered.write_text(html)

from playwright.async_api import async_playwright

async def render():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.goto(rendered.resolve().as_uri(), wait_until="networkidle")
        # Give web fonts a beat to settle
        await page.wait_for_timeout(800)
        await page.pdf(
            path=str(out / "poster.pdf"),
            width="297mm",
            height="420mm",
            print_background=True,
            margin={"top":"0","right":"0","bottom":"0","left":"0"},
            prefer_css_page_size=True,
        )
        await browser.close()

asyncio.run(render())
print(f"    wrote {out/'poster.pdf'}")
PY

# ---------- 2. Render Remotion → MP4 ----------

echo ""
echo "==> [2/2] Rendering recap.mp4 …"

VIDEO_DIR="$HERE/video"
cd "$VIDEO_DIR"

if [ ! -d node_modules ]; then
  echo "    installing node deps (one-time) …"
  if command -v bun >/dev/null 2>&1; then
    bun install --silent
  elif command -v pnpm >/dev/null 2>&1; then
    pnpm install --silent
  else
    npm install --silent --no-audit --no-fund
  fi
fi

mkdir -p out
npx remotion render src/index.ts Recap "out/recap.mp4" \
  --log=info --concurrency=1 --overwrite

cp -f out/recap.mp4 "$OUT/recap.mp4"
echo "    wrote $OUT/recap.mp4"

echo ""
echo "==> Done."
echo "    open $OUT/poster.pdf"
echo "    open $OUT/recap.mp4"
