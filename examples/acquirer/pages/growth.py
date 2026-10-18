import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data import BY, COHORTS, CUR, DAYS, MDAYS, MONTHLY, NAME, SEGMENTS, pace  # noqa: E402
from kit import bars, dollars, dots, fig, heat, mlab, mname, num, page, para, pct, row, section, slope, table, usd  # noqa: E402

full = [r for r in MONTHLY if not r["partial"]]
cur, sep, first = BY[CUR], BY["2026-09"], MONTHLY[0]
xlab = {i: mlab(r["month"]) for i, r in enumerate(MONTHLY) if i % 3 == 0 or r["partial"]}
when = lambda r: f"{mname(r['month'])} {r['month'][:4]}"

act_svg = dots([(f"{when(r)}: {num(r['active'])}", r["active"]) for r in full], lo=1_000, hi=2_400, ticks=[1_000, 1_500, 2_000], fmt=num,
               xlab=xlab, room=96, partial=(f"October 1 to {DAYS}: {num(cur['active'])}", cur["active"]),
               right=[(sep["active"], f"Sep {num(sep['active'])}", ""), (cur["active"], f"Oct to date {num(cur['active'])}", "acc")],
               aria="Active merchants by month")

per = lambda r: r["rev"] / r["active"]
per_pace = pace("rev") / cur["active"]
per_svg = dots([(f"{when(r)}: ${per(r):,.0f}", per(r)) for r in full], lo=300, hi=420, ticks=[300, 350, 400], fmt=lambda v: f"${v:.0f}",
               xlab=xlab, partial=(f"October estimate: ${per_pace:,.0f}", per_pace), room=96,
               right=[(per(sep), f"Sep ${per(sep):.0f}", ""), (per_pace, f"Oct est. ${per_pace:.0f}", "acc")],
               aria="Net revenue per active merchant by month")

new_svg = bars([(f"{when(r)}: {num(r['new'])}", r["new"]) for r in full], top=250, ticks=[0, 100, 200], fmt=num, xlab=xlab, room=96,
               partial=dict(banked=cur["new"], pace=pace("new"), title=f"October 1 to {DAYS}: {num(cur['new'])}, pace {num(pace('new'))}"),
               right=[(sep["new"], f"Sep {num(sep['new'])}", ""), (pace("new"), f"Oct pace {num(pace('new'))}", "acc")],
               aria="New merchants by month")

lost_svg = bars([(f"{when(r)}: {num(r['lost'])}" if r["lost"] is not None else f"{when(r)}: not counted", r["lost"] or 0) for r in MONTHLY],
                top=250, ticks=[0, 100, 200], fmt=num, xlab=xlab, room=96,
                right=[(sep["lost"], f"Sep {num(sep['lost'])}", "")], aria="Merchants lost by month")

k = max(len(c["retention"]) for c in COHORTS) - 1
heat_tbl = heat([(f"{mname(c['month'])[:3]} · {c['size']}", c["retention"][1:] + [None] * (k - len(c["retention"]) + 1)) for c in COHORTS if len(c["retention"]) > 1],
                ["Joined · merchants"] + [str(i) for i in range(1, k + 1)], lo=0.6, hi=0.9)

seg_svg = slope([s["merchants"] for s in SEGMENTS], [s["tpv"] for s in SEGMENTS], [s["segment"] for s in SEGMENTS], fmt=pct,
                W=360, H=210, lt="Merchants", rt="Card volume", acc={3}, aria="Each segment's share of merchants and of card volume")
seg_svg = seg_svg.replace('viewBox="0 0 360 210"', 'viewBox="0 -12 360 222"').replace('y="8" class="tick"', 'y="-2" class="tick"')
seg_rows = [("", [s["segment"], pct(s["retention"], 1), dollars(s["rev_per"]), pct(s["merchants"]), pct(s["tpv"])]) for s in SEGMENTS]
seg_tbl = table(["Monthly volume", "Kept each month", "Net revenue per merchant a month", "Share of merchants", "Share of card volume"],
                seg_rows, num=range(1, 5), hide=(3, 4), cls="seg")

jan, aug = COHORTS[0], COHORTS[-2]
big = SEGMENTS[-1]
lede = (f"Acme had {num(sep['active'])} active merchants in September, {sep['active'] / first['active']:.1f} times October 2025. "
        f"September added {num(sep['new'])} and lost {num(sep['lost'])}. Merchants who joined in August kept "
        f"{pct(aug['retention'][1], 1)} into their second month, against {pct(jan['retention'][1], 1)} for January's intake.")
html = page(
    "Merchant growth", f"{NAME}, an invented merchant acquirer · October 2025 to {DAYS} October 2026 · every figure is made up", lede,
    [section("The base",
             row(fig("Active merchants a month", act_svg, "A count of merchants is a state read once a month, so one dot per month, not a bar. October, hollow, "
                                                         "is a month-to-date count of distinct merchants; it does not scale with days, so it has no pace.", 320),
                 fig("Net revenue per active merchant", per_svg, f"A ratio, so one dot per month. October, hollow, is the {MDAYS}-day revenue pace over "
                                                                f"the month-to-date merchant count, and runs high until the count fills in.", 320),
                 cols=2, colw=330)),
     section("In and out",
             row(fig("New merchants a month", new_svg, f"Totals per month, bars from zero. October is the banked {DAYS} days in grey and the "
                                                       f"{MDAYS}-day pace dashed.", 320),
                 fig("Merchants lost a month", lost_svg, "Same scale as new merchants, so the two compare at their true size. Losses are counted "
                                                         "when a month closes: none for October 2025 or October 2026.", 320),
                 cols=2, colw=330)),
     section("Cohorts",
             para(f"Each row is the merchants who took their first payment in one month; each column is the share still active that many months later. "
                  f"Darker is higher. April's intake of {COHORTS[3]['size']} was the largest, and it has held as well as smaller ones."),
             heat_tbl),
     section("Segments",
             para(f"The {pct(big['merchants'])} of merchants processing {usd(250_000)} or more a month bring {pct(big['tpv'])} of card volume; "
                  f"the {pct(SEGMENTS[0]['merchants'])} under {usd(10_000)} bring {pct(SEGMENTS[0]['tpv'])}."),
             fig("Share of merchants against share of card volume", seg_svg, "Two points per segment, so a slopegraph: the steeper the rise, "
                                                                            "the more volume each merchant brings.", 360),
             seg_tbl)],
    "Sources: none. Acme Payments does not exist; the figures come from a seeded generator in the tufte repository "
    "(examples/acquirer/data.py) and are drawn with the tufte skill's rules: bars from zero for totals per period, dots for ratios, "
    "the partial month as banked plus pace, a shaded table for cohorts, a slopegraph for two points per item.",
    desc="Active, new and lost merchants, cohort retention and segments of an invented merchant acquirer.")
html = html.replace("</style>", "@media (max-width:700px){.heat td{min-width:0;padding:0 3px}.heat th{padding-right:6px}"
                                ".seg th{white-space:normal}.seg tbody th{min-width:120px}}</style>")
out = Path(__file__).resolve().parent.parent / "out" / "merchant-growth.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html.replace(" %", "\u00a0%"))
print(out)
