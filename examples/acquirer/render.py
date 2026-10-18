# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.47.0"]
# ///
"""Full-page JPEGs of every page in out/: desktop (1440 px wide at 2x) and phone (390 px wide at 3x), via the locally installed Chrome.
usage: uv run render.py [example dir] [name ...]; the dir defaults to this folder, names to the pages listed in its pages.txt"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

args = sys.argv[1:]
base = Path(args.pop(0)).resolve() if args and Path(args[0]).is_dir() else Path(__file__).resolve().parent
OUT = base / "out"
SIZES = {"desktop": dict(viewport=dict(width=1440, height=900), device_scale_factor=2),
         "mobile": dict(viewport=dict(width=390, height=844), device_scale_factor=3, is_mobile=True, has_touch=True)}

inventory = base / "pages.txt"
names = args or (inventory.read_text().split() if inventory.exists() else [p.stem for p in sorted(OUT.glob("*.html"))])
missing = [n for n in names if not (OUT / f"{n}.html").exists()]
if not names or missing:
    sys.exit(f"missing pages in {OUT}: {', '.join(missing) or 'all'}; build them first")
(OUT / "jpg").mkdir(exist_ok=True)
with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="chrome")
    for kind, opts in SIZES.items():
        ctx = browser.new_context(**opts, color_scheme="light")
        pg = ctx.new_page()
        for n in names:
            pg.goto((OUT / f"{n}.html").as_uri())
            pg.wait_for_timeout(150)
            dst = OUT / "jpg" / f"{n}-{kind}.jpg"
            pg.screenshot(path=str(dst), type="jpeg", quality=92, full_page=True)
            print(dst.name)
        ctx.close()
    browser.close()
