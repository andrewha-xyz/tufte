import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data import BY, CUR, DAYS, FORECAST, MDAYS, MONTHLY, NAME, PLAN, STRETCH, pace  # noqa: E402
from kit import _labels, bars, dollars, esc, fig, mlab, mname, num, page, para, pct, row, section, table, usd  # noqa: E402

full = [r for r in MONTHLY if not r["partial"]]
cur, sep, jun = BY[CUR], BY["2026-09"], BY["2026-06"]
FC = {f["month"]: f for f in FORECAST}
xlab = {i: mlab(r["month"]) for i, r in enumerate(MONTHLY) if i % 3 == 0 or r["partial"]}
after = [r["month"] for r in MONTHLY if r["month"] >= "2026-05"]
rev_pace = pace("rev")
fsep, foct, fdec = FC["2026-09"], FC[CUR], FC["2026-12"]


def active_svg(W=320, H=170, room=100, lo=1000, hi=3500):
    n, t, b = len(MONTHLY), 8, H - 22
    pr = W - room
    slot = pr / n
    ys = lambda v: t + (b - t) * (hi - v) / (hi - lo)
    xs = lambda i: i * slot + slot / 2
    g = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Active merchants against the May forecast">']
    for v in (1000, 2000, 3000):
        g.append(f'<text x="-7" y="{ys(v) + 3.5:.1f}" class="tick" text-anchor="end">{num(v)}</text>')
    pts = [(i, FC[r["month"]]["active"]) for i, r in enumerate(MONTHLY) if r["month"] >= "2026-05"]
    d = " ".join(f'{"M" if j == 0 else "L"}{xs(i):.1f},{ys(v):.1f}' for j, (i, v) in enumerate(pts))
    g.append(f'<path d="{d}" class="line dim"><title>May forecast</title></path>')
    for i, r in enumerate(MONTHLY):
        cls = "hollow" if r["partial"] else "dot"
        tip = f"October 1 to {DAYS}: {num(r['active'])} active so far" if r["partial"] else f"{mname(r['month'])} {r['month'][:4]}: {num(r['active'])}"
        g.append(f'<circle cx="{xs(i):.1f}" cy="{ys(r["active"]):.1f}" r="2.6" class="{cls}"><title>{esc(tip)}</title></circle>')
    g.append(f'<line x1="0" x2="{n * slot:.1f}" y1="{b + 2:.1f}" y2="{b + 2:.1f}" class="axis"/>')
    for i, txt in xlab.items():
        g.append(f'<text x="{xs(i):.1f}" y="{b + 17:.1f}" class="tick" text-anchor="middle">{esc(txt)}</text>')
    _labels(g, [(foct["active"], f"May forecast {num(foct['active'])}", "dim"), (sep["active"], f"Sep {num(sep['active'])}", "")], pr + 8, ys)
    g.append("</svg>")
    return "".join(g)


def fan(start, cases, *, lo, hi, fmt, aria, W=320, H=150, left=58, room=124):
    """two points per case from one shared start: September actual on the left, December under each case on the right"""
    x0, x1, t, b = left, W - room, 10, H - 20
    ys = lambda v: t + (b - t) * (hi - v) / (hi - lo)
    g = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(aria)}">']
    g.append(f'<text x="{x0 - 6}" y="{ys(start) + 3.5:.1f}" class="lab" text-anchor="end">{esc(fmt(start))}</text>')
    for name, v, cls in cases:
        style = "stroke-dasharray:3 3;stroke-width:1.1" + (";stroke:var(--grey)" if cls == "dim" else "")
        g.append(f'<line x1="{x0}" x2="{x1}" y1="{ys(start):.1f}" y2="{ys(v):.1f}" class="line{" acc" if cls == "acc" else ""}" style="{style}"><title>{esc(name)}: {esc(fmt(v))}</title></line>')
        g.append(f'<circle cx="{x1}" cy="{ys(v):.1f}" r="2.2" class="{"dot acc" if cls == "acc" else "dot"}"{" style=" + chr(34) + "fill:var(--grey)" + chr(34) if cls == "dim" else ""}/>')
    g.append(f'<circle cx="{x0}" cy="{ys(start):.1f}" r="2.6" class="dot"/>')
    _labels(g, [(v, f"{name} {fmt(v)}", cls) for name, v, cls in cases], x1 + 8, ys)
    g.append(f'<text x="{x0}" y="{H - 4}" class="tick" text-anchor="middle">Sep</text><text x="{x1}" y="{H - 4}" class="tick" text-anchor="middle">Dec</text>')
    g.append("</svg>")
    return "".join(g)


rev_svg = bars([(f"{mname(r['month'])} {r['month'][:4]}: {dollars(r['rev'])}", r["rev"]) for r in full], top=1_500_000,
               ticks=[0, 500_000, 1_000_000, 1_500_000], xlab=xlab,
               partial=dict(banked=cur["rev"], pace=rev_pace, title=f"October 1 to {DAYS}: {dollars(cur['rev'])} banked, pace {dollars(rev_pace)}"),
               plans=[FC[r["month"]]["rev"] if r["month"] >= "2026-05" else None for r in MONTHLY],
               right=[(foct["rev"], f"May forecast {usd(foct['rev'])}", "dim"), (rev_pace, f"Oct pace {usd(rev_pace)}", "acc"),
                      (sep["rev"], f"Sep {usd(sep['rev'])}", "")], room=112, aria="Net revenue against the May forecast")

g_rev = (sep["rev"] / jun["rev"]) ** (1 / 3)
g_act = (sep["active"] / jun["active"]) ** (1 / 3)
dec_rev = rev_pace * g_rev ** 2
dec_act = sep["active"] * g_act ** 3
act_cases = [("May forecast", fdec["active"], "dim"), ("Stretch", STRETCH["2026-12"]["active"], ""), ("Plan", PLAN["2026-12"]["active"], ""),
             ("Pace", dec_act, "acc")]
rev_cases = [("May forecast", fdec["rev"], "dim"), ("Stretch", STRETCH["2026-12"]["rev"], ""), ("Plan", PLAN["2026-12"]["rev"], ""),
             ("Pace", dec_rev, "acc")]
fan_act = fan(sep["active"], act_cases, lo=2000, hi=4400, fmt=num, aria="Active merchants: September and December under four cases")
fan_rev = fan(sep["rev"], rev_cases, lo=800_000, hi=1_760_000, fmt=usd, aria="Net revenue: September and December under four cases")

gap = lambda v: pct(v).replace("-", "\u2212")
tab = []
for m in after:
    r, f = BY[m], FC[m]
    rv = rev_pace if r["partial"] else r["rev"]
    label = "October, revenue at pace" if r["partial"] else f"{mname(m)} {m[:4]}"
    tab.append(("part" if r["partial"] else "", [label, dollars(rv), dollars(f["rev"]), gap(rv / f["rev"] - 1), num(r["active"]), num(f["active"]),
                                                 gap(r["active"] / f["active"] - 1)]))
head = ["Month", "Net revenue", "May forecast", "Revenue gap", "Active merchants", "May forecast", "Merchant gap"]

kept = [(BY[a]["active"] - BY[b]["lost"]) / BY[a]["active"] for a, b in zip(after[:-2], after[1:-1])]
news = [BY[m]["new"] for m in after[:-1]]
fnew = [FC[m]["new"] for m in after[:-1]]
rpm, frpm = sep["rev"] / sep["active"], fsep["rev"] / fsep["active"]
share = math.log(sep["active"] / fsep["active"]) / math.log(sep["rev"] / fsep["rev"])
lede = (f"The model made in May, fitted to the months through April, expected {num(fsep['active'])} active merchants and "
        f"{usd(fsep['rev'])} of net revenue in September. September came in at {num(sep['active'])} and {usd(sep['rev'])}, "
        f"{pct(1 - sep['active'] / fsep['active'])} and {pct(1 - sep['rev'] / fsep['rev'])} short. The miss is in new merchants: the model assumed "
        f"{num(fnew[0])} new merchants a month rising to {num(fnew[-1])}, and {NAME} added between {num(min(news))} and {num(max(news))}.")
html = page(
    "Forecast against actual", f"{NAME}, an invented merchant acquirer · October 2025 to {DAYS} October 2026 · every figure is made up", lede,
    [section("Actual against the May forecast",
             row(fig("Active merchants", active_svg(), "A count of merchants is a state, so one dot a month; the forecast is a projection, "
                                                        "drawn as a dashed grey line from May and labelled. October, hollow, counts half a month.", 320),
                 fig("Net revenue a month", rev_svg, f"Actual revenue is a bar from zero; each grey tick is the May forecast for that month. "
                                                      f"October is banked (grey) plus its {MDAYS}-day pace (dashed).", 320),
                 cols=2, colw=340),
             para(f"Of the revenue gap in September, about {pct(share)} is fewer merchants and the rest is lower revenue per merchant: "
                  f"{dollars(rpm)} against the model's {dollars(frpm)}. Merchants were kept at {pct(min(kept), 1)} to {pct(max(kept), 1)} "
                  f"a month against the model's 97.5 %.")),
     section("December 2026",
             row(fig("Active merchants", fan_act, "Two points per case, so a table-graphic: September's actual on the left, December under each "
                                                  "case on the right. Every December value is a projection, so every line is dashed.", 320),
                 fig("Net revenue a month", fan_rev, f"The pace case, in red, grows October's revenue pace ({usd(rev_pace)}) and September's merchant "
                                                      f"count at their average monthly growth from June to September, {pct(g_rev - 1, 1)} and "
                                                      f"{pct(g_act - 1, 1)}: {pct(dec_rev / PLAN['2026-12']['rev'])} of the plan's revenue, "
                                                      f"{pct(dec_act / PLAN['2026-12']['active'])} of its merchants.", 320),
                 cols=2, colw=340)),
     section("Month by month",
             table(head, tab, num=range(1, 7), hide=(2, 4, 5)))],
    "Sources: none. Acme Payments does not exist; the figures come from a seeded generator in the tufte repository "
    "(examples/acquirer/data.py) and are drawn with the tufte skill's rules: bars from zero for totals per period, dots for a state "
    "read monthly, a projection as a dashed labelled mark never joined to the actuals, the partial month as banked plus pace.")
out = Path(__file__).resolve().parent.parent / "out" / "forecast.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html)
print(out)
