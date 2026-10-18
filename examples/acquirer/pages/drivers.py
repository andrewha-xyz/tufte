import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data import BY, CHANNELS, CUR, DAYS, MDAYS, MONTHLY, NAME, PLAN, SEGMENTS, VALUE_MARGIN, pace, sensitivity  # noqa: E402
from kit import bars, dollars, dots, fig, heat, mlab, mname, num, page, para, pct, row, section, table, usd  # noqa: E402

full = [r for r in MONTHLY if not r["partial"]]
cur, sep, first = BY[CUR], BY["2026-09"], MONTHLY[0]
xlab = {i: mlab(r["month"]) for i, r in enumerate(MONTHLY) if i % 3 == 0 or r["partial"]}
rpm = lambda r: r["rev"] / r["active"]
new_pace = cur["new"] * MDAYS / DAYS

new_svg = bars([(f"{mname(r['month'])} {r['month'][:4]}: {num(r['new'])}", r["new"]) for r in full], top=250, ticks=[0, 100, 200], fmt=num,
               xlab=xlab, partial=dict(banked=cur["new"], pace=new_pace, title=f"October 1 to {DAYS}: {num(cur['new'])} new, pace {num(new_pace)}"),
               right=[(sep["new"], f"Sep {num(sep['new'])}", ""), (new_pace, f"Oct pace {num(new_pace)}", "acc")], room=88,
               aria="New merchants by month")

kept_rows = [(MONTHLY[i - 1], r) for i, r in enumerate(MONTHLY) if r["lost"] is not None]
kept = lambda p, r: (p["active"] - r["lost"]) / p["active"]
klab = {i: mlab(r["month"]) for i, (_, r) in enumerate(kept_rows) if r["month"][5:] in ("11", "02", "05", "08")}
kept_svg = dots([(f"{mname(r['month'])}: {pct(kept(p, r), 1)} of {num(p['active'])} kept", kept(p, r)) for p, r in kept_rows],
                lo=0.96, hi=0.99, ticks=[0.96, 0.97, 0.98, 0.99], fmt=lambda v: f"{v * 100:.0f} %", xlab=klab,
                right=[(kept(*kept_rows[-1]), f"Sep {pct(kept(*kept_rows[-1]), 1)}", "")], room=64,
                aria="Share of last month's merchants kept")

rpm_pace = pace("rev") / cur["active"]
rpm_svg = dots([(f"{mname(r['month'])}: {dollars(rpm(r))}", rpm(r)) for r in full], lo=300, hi=450, ticks=[300, 350, 400, 450],
               fmt=lambda v: f"${v:.0f}", xlab=xlab, partial=(f"October pace: {dollars(rpm_pace)} per merchant active so far", rpm_pace),
               right=[(rpm(sep), f"Sep {dollars(rpm(sep))}", "")], aria="Net revenue per active merchant")

seg_rows = []
for s in SEGMENTS:
    seg_rows.append(("", [s["segment"], pct(s["merchants"]), pct(s["tpv"]), pct(s["retention"], 1), f"{1 / (1 - s['retention']):.0f}",
                          dollars(s["rev_per"])]))
seg_head = ["Card volume a month", "Share of merchants", "Share of volume", "Kept a month", "Months expected to stay", "Net revenue a merchant a month"]

avg = rpm(sep)
r_kept = (MONTHLY[-3]["active"] - sep["lost"]) / MONTHLY[-3]["active"]
stay = sum(r_kept ** k for k in range(12))
value = lambda c: c["activation"] * avg * VALUE_MARGIN * stay
ratio = lambda c: value(c) / c["cac"]
best = max(CHANNELS, key=ratio)
ch_rows = []
for c in CHANNELS:
    ch_rows.append(("", [c["channel"], usd(c["budget"]), num(c["signed"]), num(c["activated"]), pct(c["activation"]), dollars(c["cac"]),
                         dollars(value(c)), f'<span class="acc">{ratio(c):.1f}</span>' if c is best else f"{ratio(c):.1f}"]))
tb, ts, ta = sum(c["budget"] for c in CHANNELS), sum(c["signed"] for c in CHANNELS), sum(c["activated"] for c in CHANNELS)
tv = ta / ts * avg * VALUE_MARGIN * stay
ch_rows.append(("tot gap", ["September, all channels", usd(tb), num(ts), num(ta), pct(ta / ts), dollars(tb / ts), dollars(tv), f"{tv / (tb / ts):.1f}"]))
ch_head = ["Channel", "Budget", "Signed", "Activated", "Activation", "Cost per signed", "Value per signed", "Value ÷ cost"]
under = [c["channel"] for c in CHANNELS if ratio(c) < 1]
ranked = sorted(CHANNELS, key=ratio, reverse=True)
worth = (f"{ranked[0]['channel']} return the most per dollar ({ratio(ranked[0]):.1f}), {ranked[1]['channel'].lower()} next ({ratio(ranked[1]):.1f}); "
         + (f"{' and '.join(u.lower() for u in under)} earns less in its first twelve months than it costs to sign "
            f"({' and '.join(f'{ratio(c):.1f}' for c in CHANNELS if ratio(c) < 1)})." if under else "every channel earns back its cost within twelve months."))

grid, rets = sensitivity()
target = PLAN["2026-12"]["active"]
cells = [(abs(v - target), g["new"], r, v) for g in grid for r, v in zip(rets, g["values"])]
_, t_new, t_ret, t_val = min(cells)
lo, hi = min(min(g["values"]) for g in grid), max(max(g["values"]) for g in grid)
heat_html = heat([(num(g["new"]), g["values"]) for g in grid], ["New"] + [f"{r * 100:g}" for r in rets], fmt=num, lo=lo, hi=hi)
heat_html = "<style>@media (max-width:700px){.heat tbody th{min-width:0}}</style>" + re.sub(rf'(<td style="[^"]*)(">{re.escape(num(t_val))}</td>)', r"\1;outline:1.5px solid var(--acc);outline-offset:-2px\2", heat_html, count=1)

grow_a, grow_r = sep["active"] / first["active"], rpm(sep) / rpm(first)
lede = (f"Net revenue is active merchants times net revenue per active merchant. In September that was {num(sep['active'])} × "
        f"{dollars(rpm(sep))} = {usd(sep['rev'])}. Since October 2025 the merchant count grew {pct(grow_a - 1)} and revenue per merchant "
        f"{pct(grow_r - 1)}, so nearly all of the growth is merchants: how many start taking payments, and how many stay.")
html = page(
    "What drives revenue", f"{NAME}, an invented merchant acquirer · October 2025 to {DAYS} October 2026 · every figure is made up", lede,
    [section("The three drivers",
             row(fig("New merchants a month", new_svg, f"A count per month is a bar from zero. October is banked (grey) plus its {MDAYS}-day pace (dashed).", 320),
                 fig("Share of last month's merchants kept", kept_svg, "A ratio is a dot. The month's losses are known only once it closes, so October is left out.", 320),
                 fig("Net revenue per active merchant", rpm_svg, "A ratio is a dot. October, hollow, is its revenue pace over the merchants active so far.", 320),
                 cols=3, colw=330)),
     section("Who stays",
             para("Small merchants are almost half the count and a fourteenth of the volume; they also leave fastest. A merchant kept "
                  f"{pct(SEGMENTS[0]['retention'], 1)} a month stays about {1 / (1 - SEGMENTS[0]['retention']):.0f} months; one kept "
                  f"{pct(SEGMENTS[-1]['retention'], 1)} stays about {1 / (1 - SEGMENTS[-1]['retention']):.0f} months."),
             table(seg_head, seg_rows, num=range(1, 6), hide=(2, 4))),
     section("What a signed merchant is worth, September",
             para(f"September's channels signed {num(ts)} merchants, of whom {num(ta)} became active: the {num(sep['new'])} new merchants above. "
                  f"Value per signed merchant is its first twelve months of contribution: the share activated × {dollars(avg)} (September's net "
                  f"revenue per active merchant) × {pct(VALUE_MARGIN)} contribution margin × {stay:.1f}, the expected months of the first twelve a "
                  f"merchant stays when {pct(r_kept, 1)} are kept each month. {worth[0].upper() + worth[1:]}"),
             table(ch_head, ch_rows, num=range(1, 8), hide=(1, 2, 3, 4))),
     section("December under other assumptions",
             fig("Active merchants in December, by new merchants a month (rows) and per cent kept a month (columns)", heat_html,
                 f"Each cell compounds September's {num(sep['active'])} merchants for three months; darker is more. The outlined cell, "
                 f"{num(t_new)} new a month kept at {t_ret * 100:g} %, gives {num(t_val)}, nearest the plan's {num(target)}. September added "
                 f"{num(sep['new'])} and kept {pct(kept(*kept_rows[-1]), 1)}.", 400))],
    "Sources: none. Acme Payments does not exist; the figures come from a seeded generator in the tufte repository "
    "(examples/acquirer/data.py) and are drawn with the tufte skill's rules: bars from zero for counts per period, dots for ratios, "
    "the partial month as banked plus pace, a shaded table for a grid of outcomes.")
out = Path(__file__).resolve().parent.parent / "out" / "driver-model.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html)
print(out)
