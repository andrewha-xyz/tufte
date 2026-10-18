import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data import BY, DAYS, MDAYS, MONTHLY, NAME, pace  # noqa: E402
from kit import num, page, para, pct, section, table, usd  # noqa: E402

sep = BY["2026-09"]
other = lambda r: r["rev"] - r["streams"]["Merchant fee margin"]


def spk(vals, kind="bar", banked=None, w=104, h=18):
    n, real = len(vals), [v for v in vals if v is not None]
    lo, hi = (0, max(real + [banked or 0])) if kind == "bar" else (min(real), max(real))
    hi = hi if hi > lo else lo + 1
    slot, last = w / n, max(i for i, v in enumerate(vals) if v is not None)
    g = [f'<svg class="spark" viewBox="0 0 {w} {h}" width="{w}" height="{h}" aria-hidden="true">']
    for i, v in enumerate(vals):
        if v is None:
            continue
        cls = "a" if i == last else "s"
        if kind == "bar":
            y = lambda x: h - max(0.6, (h - 1) * (x - lo) / (hi - lo))
            x, bw = i * slot, max(1.0, slot - 1.2)
            if banked is not None and i == n - 1:
                g.append(f'<rect x="{x:.1f}" y="{y(banked):.1f}" width="{bw:.1f}" height="{h - y(banked):.1f}" style="fill:var(--fill)"/>')
                if v != banked:
                    g.append(f'<rect x="{x + 0.4:.1f}" y="{y(v):.1f}" width="{bw - 0.8:.1f}" height="{h - y(v):.1f}" '
                             f'style="fill:none;stroke:var(--acc);stroke-width:.8;stroke-dasharray:1.6 1.1"/>')
                continue
            g.append(f'<rect x="{x:.1f}" y="{y(v):.1f}" width="{bw:.1f}" height="{h - y(v):.1f}" class="{cls}"/>')
        else:
            cy = 2 + (h - 4) * (hi - v) / (hi - lo)
            hollow = banked is not None and i == n - 1
            style = ' style="fill:var(--paper);stroke:var(--acc);stroke-width:.8"' if hollow else ""
            g.append(f'<circle cx="{i * slot + slot / 2:.1f}" cy="{cy:.1f}" r="1.5" class="{cls}"{style}/>')
    g.append("</svg>")
    return "".join(g)


minus = lambda s: s.replace("-", "−")
rel = lambda a, b, d=0: minus(f"{(a / b - 1) * 100:+.{d}f} %")
pts = lambda a, b, unit, k=100, d=1: minus(f"{round((a - b) * k, d) or 0:{'+' if round((a - b) * k, d) else ''}.{d}f} {unit}".rstrip())
mil = lambda v: f"{v / 1e6:.2f}M"
ser = lambda f: [f(r) for r in MONTHLY]


def flow(name, f, fmt, pace_v):
    vals = ser(f)
    return ("", [name, spk(vals[:-1] + [pace_v], banked=vals[-1]), fmt(vals[-2]), f"{fmt(pace_v)} pace",
                 rel(vals[-2], vals[-3]), rel(vals[-2], vals[0])])


def ratio(name, f, fmt, chg):
    vals = ser(f)
    return ("", [name, spk(vals, "dot", banked=vals[-1]), fmt(vals[-2]), f"{fmt(vals[-1])} so far",
                 chg(vals[-2], vals[-3]), chg(vals[-2], vals[0])])


def group(name):
    return ("gap", [f"<i>{name}</i>", "", "", "", "", ""])


lost = [r["lost"] for r in MONTHLY]
act = ser(lambda r: r["active"])
rows = [group("Volume"),
        flow("Card volume", lambda r: r["tpv"], usd, pace("tpv")),
        flow("Transactions", lambda r: r["txns"], mil, pace("txns")),
        ratio("Average ticket", lambda r: r["ticket"], lambda v: f"${v:.2f}", lambda a, b: rel(a, b, 1)),
        group("Revenue"),
        flow("Net revenue", lambda r: r["rev"], usd, pace("rev")),
        flow("Merchant fee margin", lambda r: r["streams"]["Merchant fee margin"], usd, pace("Merchant fee margin")),
        flow("Other fees", other, usd, pace("rev") - pace("Merchant fee margin")),
        ratio("Take rate", lambda r: r["take"], lambda v: f"{v * 1e4:.1f} bps", lambda a, b: pts(a, b, "bps", 1e4)),
        group("Quality"),
        ratio("Approval rate", lambda r: r["approval"], lambda v: pct(v, 1), lambda a, b: pts(a, b, "pt")),
        ratio("Chargebacks per 10,000", lambda r: r["cb_bps"], lambda v: f"{v:.1f}", lambda a, b: pts(a, b, "", 1)),
        ratio("Cross-border share", lambda r: r["xb"], lambda v: pct(v, 1), lambda a, b: pts(a, b, "pt")),
        group("Merchants"),
        ("", ["Active", spk(act, "dot", banked=act[-1]), num(act[-2]), f"{num(act[-1])} to date", rel(act[-2], act[-3]), rel(act[-2], act[0])]),
        flow("New", lambda r: r["new"], num, pace("new")),
        ("", ["Lost", spk(lost), num(lost[-2]), "at month end", rel(lost[-2], lost[-3]), ""])]

head = ["", "October 2025 to October 2026", "September", "October", "September on August", "September on October 2025"]
lede = (f"September closed with {usd(sep['rev'])} of net revenue on {usd(sep['tpv'])} of card volume from {num(sep['active'])} active merchants. "
        f"With {DAYS} of {MDAYS} days banked, October is on pace for {usd(pace('rev'))}, "
        f"{rel(pace('rev'), sep['rev'])} on September. Every measure the business watches is one row below.")
how = (f"Each row is one measure over thirteen months, October 2025 at the left. Totals are tiny bars from zero; ratios and counts of merchants are dots on the row's own "
       f"range, so a row's shape compares with itself, not with its neighbours. The red mark is the latest: for totals October is the banked "
       f"{DAYS} days in grey with its {MDAYS}-day pace as an open dashed bar, for ratios October's reading so far is a hollow dot. "
       f"Active merchants are a headcount, a state read once a month, so they are dots too; October's month-to-date count does not scale with days and has no pace. "
       f"Lost merchants are counted when a month closes, from November 2025. Changes compare September, the last whole month.")
html = page(
    "The month in one table", f"{NAME}, an invented merchant acquirer · October 2025 to {DAYS} October 2026 · every figure is made up", lede,
    [section("Thirteen months, thirteen measures",
             para(how),
             table(head, rows, num=range(2, 6), hide=(3, 5), cls="sl"))],
    "Sources: none. Acme Payments does not exist; the figures come from a seeded generator in the tufte repository "
    "(examples/acquirer/data.py) and are set with the tufte skill's rules for a sparkline table: word-sized graphics beside their latest "
    "values, bars from zero for totals, dots for ratios, the partial month as banked plus pace.",
    desc="A sparkline table of thirteen measures of an invented merchant acquirer.")
html = html.replace("</style>", ".sl td:nth-child(2){padding-right:20px}.sl tr.gap i{color:var(--grey)}"
                                "@media (max-width:700px){.sl th,.sl td{white-space:normal}.sl td:nth-child(2){padding-right:8px}.spark{width:78px;height:auto}}</style>")
out = Path(__file__).resolve().parent.parent / "out" / "sparkline-ledger.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html.replace(" %", "\u00a0%"))
print(out)
