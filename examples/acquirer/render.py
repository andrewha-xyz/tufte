# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.47.0", "pillow"]
# ///
"""Full-page JPEGs of every page in out/: desktop (1440 px wide at 2x) and phone (390 px wide at 2x), via the locally installed Chrome.
Each JPEG is progressive, carries no colour profile, EXIF or comment, and stays within 8000 px on its longer side (directory and upload limits).
usage: uv run render.py [example dir] [name ...]; the dir defaults to this folder, names to the pages listed in its pages.txt"""
import io
import re
import sys
from pathlib import Path

from PIL import Image

from playwright.sync_api import sync_playwright

args = sys.argv[1:]
base = Path(args.pop(0)).resolve() if args and Path(args[0]).is_dir() else Path(__file__).resolve().parent
OUT = base / "out"
SIZES = {"desktop": dict(viewport=dict(width=1440, height=900), device_scale_factor=2),
         "mobile": dict(viewport=dict(width=390, height=844), device_scale_factor=2, is_mobile=True, has_touch=True)}
LIMIT = 8000


def save(png, dst):
    """progressive JPEG with no colour profile, EXIF or comment; refuse anything over LIMIT px; prefer an encoding without long printable byte runs"""
    im = Image.open(io.BytesIO(png)).convert("RGB")
    if max(im.size) > LIMIT:
        sys.exit(f"{dst.name} is {im.size[0]} x {im.size[1]} px, over the {LIMIT} px limit; shorten the page or lower the scale")
    tries = []
    for q, sub in ((92, 2), (92, 0), (91, 2), (90, 0), (93, 1), (89, 2)):
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=q, subsampling=sub, progressive=True, optimize=True)
        tries.append(buf.getvalue())
        if not re.search(rb"[ -~]{24,}", tries[-1]):
            break
    else:
        print(f"warning: {dst.name} holds a long printable byte run from compressed flat background in every encoding tried", file=sys.stderr)
    dst.write_bytes(tries[-1] if not re.search(rb"[ -~]{24,}", tries[-1]) else tries[0])
    return im.size


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
            w, h = save(pg.screenshot(full_page=True), dst)
            print(dst.name, f"{w} x {h}")
        ctx.close()
    browser.close()
