import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data import BY, CUR, DAYS, MDAYS, NAME, OBJECTIVES, PLAN, STRETCH, pace  # noqa: E402
from kit import _frame, _labels, _xlabels, esc, fig, mlab, mname, num, page, para, pct, row, section, table, usd  # noqa: E402

YEAR = [f"2026-{m:02d}" for m in range(1, 13)]
DONE = [m for m in YEAR if m < CUR]
xlab = {i: mlab(m) for i, m in enumerate(YEAR) if m in ("2026-01", "2026-04", "2026-07", CUR, "2026-12")}
sep = BY["2026-09"]


def year_bars(key, *, top, ticks, fmt, banked, pace_v=None, right, W=320, H=170, room=96, aria="", dot=False, lo=0):
    n, pr, t, b = 12, W - room, 6, H - 22
    ys = lambda v: t + (b - t) * (top - v) / (top - lo)
    slot = pr / n
    bw = slot - 2
    k = YEAR.index(CUR)
    g = _frame(W, H, aria)
    for v in ticks:
        g.append(f'<text x="-7" y="{ys(v) + 3.5:.1f}" class="tick" text-anchor="end">{esc(fmt(v))}</text>')
    for i, m in enumerate(DONE if not dot else []):
        v = BY[m][key]
        g.append(f'<rect x="{i * slot:.1f}" y="{ys(v):.1f}" width="{bw:.1f}" height="{ys(0) - ys(v):.1f}" class="bar"><title>{esc(mname(m))}: {esc(fmt(v))}</title></rect>')
    for i, m in enumerate(DONE if dot else []):
        v = BY[m][key]
        g.append(f'<circle cx="{i * slot + bw / 2:.1f}" cy="{ys(v):.1f}" r="2.6" class="dot"><title>{esc(mname(m))}: {esc(fmt(v))}</title></circle>')
    if dot:
        g.append(f'<circle cx="{k * slot + bw / 2:.1f}" cy="{ys(banked):.1f}" r="2.6" class="hollow"><title>October 1 to {DAYS}: {esc(fmt(banked))}</title></circle>')
    else:
        g.append(f'<rect x="{k * slot:.1f}" y="{ys(banked):.1f}" width="{bw:.1f}" height="{ys(0) - ys(banked):.1f}" class="banked"><title>October 1 to {DAYS}: {esc(fmt(banked))}</title></rect>')
    if pace_v is not None:
        g.append(f'<rect x="{k * slot + 0.5:.1f}" y="{ys(pace_v):.1f}" width="{bw - 1:.1f}" height="{ys(0) - ys(pace_v):.1f}" class="pace"/>')
    for src, cls in ((PLAN, "plan"), (STRETCH, "plan str")):
        for i, m in enumerate(YEAR):
            p = src.get(m, {}).get(key)
            if p is not None:
                g.append(f'<line x1="{i * slot - 2:.1f}" x2="{i * slot + bw + 2:.1f}" y1="{ys(p):.1f}" y2="{ys(p):.1f}" class="{cls}"><title>{esc(mname(m))} {"plan" if cls == "plan" else "stretch"}: {esc(fmt(p))}</title></line>')
    g.append(f'<line x1="0" x2="{n * slot:.1f}" y1="{ys(lo) + (2 if dot else 0):.1f}" y2="{ys(lo) + (2 if dot else 0):.1f}" class="axis"/>')
    b = b + (2 if dot else 0)
    _xlabels(g, xlab, slot, b)
    _labels(g, right, pr + 8, ys)
    g.append("</svg>")
    return "".join(g)


cur, dec, decs = BY[CUR], PLAN["2026-12"], STRETCH["2026-12"]
rev_svg = year_bars("rev", top=1_300_000, ticks=[0, 500_000, 1_000_000], fmt=usd, banked=cur["rev"], pace_v=pace("rev"),
                    right=[(pace("rev"), f"Oct pace {usd(pace('rev'))}", "acc"), (dec["rev"], f"Dec plan {usd(dec['rev'])}", "dim"),
                           (decs["rev"], f"Dec stretch {usd(decs['rev'])}", "acc")], aria="Net revenue by month against plan, 2026")
tpv_svg = year_bars("tpv", top=130_000_000, ticks=[0, 50_000_000, 100_000_000], fmt=usd, banked=cur["tpv"], pace_v=pace("tpv"),
                    right=[(pace("tpv"), f"Oct pace {usd(pace('tpv'))}", "acc"), (dec["tpv"], f"Dec plan {usd(dec['tpv'])}", "dim")],
                    aria="Card volume by month against plan, 2026")
act_svg = year_bars("active", top=3_200, lo=1_200, ticks=[1_500, 2_000, 2_500, 3_000], fmt=num, banked=cur["active"], dot=True,
                    right=[(cur["active"], f"Oct to date {num(cur['active'])}", "acc"), (dec["active"], f"Dec plan {num(dec['active'])}", "dim"),
                           (decs["active"], f"Dec stretch {num(decs['active'])}", "acc")], aria="Active merchants by month against plan, 2026")

q4 = ["2026-10", "2026-11", "2026-12"]
low_rev, low_tpv, low_act = 3 * pace("rev"), 3 * pace("tpv"), cur["active"]
plan_rev, plan_tpv = sum(PLAN[m]["rev"] for m in q4), sum(PLAN[m]["tpv"] for m in q4)
str_rev = sum(STRETCH[m]["rev"] for m in q4)
minus = lambda s: s.replace("-", "−")
gap = lambda a, b, f: [minus(f(a - b)), minus(f"{(a / b - 1) * 100:+.0f} %")]
q4_rows = [("", ["Net revenue, October to December", usd(low_rev), usd(plan_rev), usd(str_rev), *gap(low_rev, plan_rev, usd)]),
           ("", ["Card volume, October to December", usd(low_tpv), usd(plan_tpv), "", *gap(low_tpv, plan_tpv, usd)]),
           ("", ["Active merchants in December", num(low_act), num(dec["active"]), num(decs["active"]), *gap(low_act, dec["active"], num)])]

words = {"on": "on track", "risk": "at risk", "off": "off track"}
obj_rows = [("", [o["title"], o["target"], o["now"], f'<span class="{o["status"]}">{words[o["status"]]}</span>']) for o in OBJECTIVES]
obj_tbl = table(["Objective", "Target", "Now", "Status"], obj_rows, cls="obj", hide=(2,))
for o in OBJECTIVES:
    obj_tbl = obj_tbl.replace(f'<td><span class="{o["status"]}">', f'<td class="{o["status"]}"><span>', 1)

lede = (f"September brought {usd(sep['rev'])} of net revenue against a plan of {usd(PLAN['2026-09']['rev'])}, "
        f"{pct(1 - sep['rev'] / PLAN['2026-09']['rev'])} short, and {num(sep['active'])} active merchants against {num(PLAN['2026-09']['active'])}. "
        f"October is on pace for {usd(pace('rev'))}, short of its plan of {usd(PLAN[CUR]['rev'])}. If November and December only match that pace, "
        f"the fourth quarter ends {usd(plan_rev - low_rev)} below plan.")
html = page(
    "Plan against actual", f"{NAME}, an invented merchant acquirer · January to December 2026, actuals to {DAYS} October · every figure is made up", lede,
    [section("The year so far",
             row(fig("Net revenue a month", rev_svg, "One bar per month from zero; the plan is a grey tick from July, the stretch target a red tick from October, "
                                                   "so the gap is read against the bar, not a line drawn through months.", 320),
                 fig("Card volume a month", tpv_svg, f"October is the banked {DAYS} days in grey and the {MDAYS}-day pace as a dashed outline; "
                                                     "November and December are empty slots, left for the months to come.", 320),
                 fig("Active merchants a month", act_svg, "A count of merchants is a state read once a month, so one dot per month, not a bar. October, hollow, "
                                                          "is the month-to-date count of distinct merchants, which does not scale with days, so it has no pace.", 320),
                 cols=3, colw=330)),
     section("The fourth quarter",
             para(f"The low case takes October at its pace and assumes November and December do no better: three months of "
                  f"{usd(pace('rev'))} in net revenue and {usd(pace('tpv'))} in card volume, and active merchants held at October's "
                  f"{num(cur['active'])}. Volume has no stretch target."),
             table(["", "Low case", "Plan", "Stretch", "Low case against plan", "In per cent"], q4_rows, num=range(1, 6), hide=(3, 5), cls="q4")),
     section("Objectives",
             obj_tbl)],
    "Sources: none. Acme Payments does not exist; the figures, the plan and the objectives come from a seeded generator in the tufte repository "
    "(examples/acquirer/data.py) and are drawn with the tufte skill's rules: bars from zero for totals per period, targets as ticks on "
    "their own month, the partial month as banked plus pace, status written in words as well as colour.",
    desc="Net revenue, card volume and active merchants against plan and stretch for an invented merchant acquirer, 2026.")
html = html.replace("</style>", "@media (max-width:700px){.q4 th,.obj th,.obj td:nth-child(2){white-space:normal}.q4 tbody th,.obj tbody th{min-width:110px}}</style>")
out = Path(__file__).resolve().parent.parent / "out" / "plan-vs-actual.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html.replace(" %", "\u00a0%"))
print(out)
