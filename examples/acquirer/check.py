# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.47.0"]
# ///
"""Phone-fit check: every page at 360, 375 and 390 px; reports tables that need sideways scrolling and anything drawn past the screen edge.
usage: uv run check.py [name ...]; exit 1 if anything overflows"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent / "out"
JS = """() => {
  const W = document.documentElement.clientWidth, bad = [];
  document.querySelectorAll('.tbl').forEach((t, i) => { if (t.scrollWidth > t.clientWidth + 1) bad.push(`table ${i + 1} needs ${t.scrollWidth}px in ${t.clientWidth}px`); });
  document.querySelectorAll('figure, p, h1, h2, svg text').forEach(e => { const r = e.getBoundingClientRect(); if (r.right > W + 1) bad.push(`${e.tagName.toLowerCase()} "${(e.textContent || '').trim().slice(0, 40)}" ends at ${Math.round(r.right)}px of ${W}`); });
  return bad;
}"""
PAGES = ["monthly-revenue", "weekly-revenue", "revenue-ledger", "revenue-ledger-grid", "sparkline-ledger", "plan-vs-actual",
         "merchant-growth", "unit-economics", "driver-model", "forecast"]
names = sys.argv[1:] or PAGES
missing = [n for n in names if not (OUT / f"{n}.html").exists()]
if missing:
    sys.exit(f"missing pages: {', '.join(missing)}; build them first")
fails = 0
with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="chrome")
    for w in (360, 375, 390):
        ctx = browser.new_context(viewport=dict(width=w, height=800), is_mobile=True, has_touch=True)
        pg = ctx.new_page()
        for n in names:
            pg.goto((OUT / f"{n}.html").as_uri())
            for b in pg.evaluate(JS):
                fails += 1
                print(f"{w}px {n}: {b}")
        ctx.close()
    browser.close()
print("ok" if not fails else f"{fails} overflow(s)")
sys.exit(1 if fails else 0)
