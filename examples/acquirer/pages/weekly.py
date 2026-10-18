import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data import NAME, WEEKLY  # noqa: E402
from kit import MON, bars, dollars, dots, fig, num, page, para, pct, row, section, table, usd  # noqa: E402

full = [w for w in WEEKLY if not w["partial"]]
part, last, first = WEEKLY[-1], full[-1], full[0]
k = 7 / part["days"]


def day(d):
    return f"{MON[d.month - 1]} {d.day}"


span = f"{day(part['week'])} to {(part['week'] + dt.timedelta(days=part['days'] - 1)).day}"
xlab = {i: MON[w["week"].month - 1] for i, w in enumerate(full) if w["week"].day <= 7}


def weekbars(key, top, ticks, fmt, short):
    p = part[key] * k
    return bars([(f"Week of {day(w['week'])}: {short(w[key])}", w[key]) for w in full], top=top, ticks=ticks, fmt=fmt, xlab=xlab,
                partial=dict(banked=part[key], pace=p, title=f"{span}: {short(part[key])} banked, pace {short(p)} for 7 days"),
                right=[(last[key], f"{day(last['week'])} {fmt(last[key])}", ""), (p, f"pace {fmt(p)}", "acc")], room=78,
                aria=f"{key} by week")


kilo = lambda v: f"{v / 1e3:.0f}k" if v else "0"
rev_svg = weekbars("rev", 250_000, [0, 100_000, 200_000], usd, dollars)
tpv_svg = weekbars("tpv", 25_000_000, [0, 10_000_000, 20_000_000], usd, usd)
txn_svg = weekbars("txns", 650_000, [0, 300_000, 600_000], kilo, num)

appr_svg = dots([(f"Week of {day(w['week'])}: {pct(w['approval'], 2)}", w["approval"]) for w in full], lo=0.930, hi=0.946,
                ticks=[0.930, 0.935, 0.940, 0.945], fmt=lambda v: f"{v * 100:.1f}", xlab=xlab,
                partial=(f"{span}: {pct(part['approval'], 2)}", part["approval"]),
                right=[(last["approval"], f"{day(last['week'])} {pct(last['approval'], 1)}", ""),
                       (part["approval"], f"{part['days']} days {pct(part['approval'], 1)}", "dim")], room=104,
                aria="Approval rate by week")
act_svg = dots([(f"Week of {day(w['week'])}: {num(w['active'])}", w["active"]) for w in full], lo=1300, hi=2000,
               ticks=[1400, 1700, 2000], fmt=num, xlab=xlab, partial=(f"{span}: {num(part['active'])} so far", part["active"]),
               right=[(last["active"], f"{day(last['week'])} {num(last['active'])}", "")], room=104,
               aria="Active merchants by week")

head = ["Week from", "Net revenue", "Card volume", "Transactions", "Approval", "Active merchants"]
rows = [("gap" if w["week"].day <= 7 and i else "", [day(w["week"]), dollars(w["rev"]), f"${w['tpv'] / 1e6:.2f}M", num(w["txns"]), pct(w["approval"], 1), num(w["active"])])
        for i, w in enumerate(full)]
rows.append(("part", [f"{span}, {part['days']} days", dollars(part["rev"]), f"${part['tpv'] / 1e6:.2f}M", num(part["txns"]), pct(part["approval"], 1), num(part["active"])]))
rows.append(("part", ["that week's pace", dollars(part["rev"] * k), f"${part['tpv'] * k / 1e6:.2f}M", num(part["txns"] * k), "", ""]))

lede = (f"Net revenue was {usd(last['rev'])} in the week from {day(last['week'])}, {last['rev'] / first['rev']:.2f} times the week from "
        f"{day(first['week'])}. The current week has {part['days']} of 7 days banked, {usd(part['rev'])}, and is on pace for {usd(part['rev'] * k)}. "
        f"The approval rate rose from {pct(first['approval'], 1)} to {pct(last['approval'], 1)} over the same {len(full)} weeks.")
html = page(
    "Weekly net revenue", f"{NAME}, an invented merchant acquirer · {first['week'].day} {first['week']:%B} to {part['week'].day + part['days'] - 1} {part['week']:%B %Y} · every figure is made up", lede,
    [section("What came in",
             row(fig("Net revenue a week", rev_svg, f"One bar per week from zero. The week from {day(part['week'])} is what is banked (grey) "
                                                     f"and its pace for 7 days (dashed): the {part['days']} days so far times 7 over {part['days']}.", 320),
                 fig("Card volume a week", tpv_svg, "Volume is a total per week, so it is a bar from zero; the partial week is drawn the same way.", 320),
                 fig("Transactions a week", txn_svg, "A count per week is a total too. Month names sit under each month's first Monday.", 320),
                 cols=3, colw=330)),
     section("Readings",
             para("A rate or a count of merchants is a reading of the week, not something that adds up across weeks, so each week is one dot and no line joins them."),
             row(fig("Approval rate, per cent of attempts", appr_svg, f"One dot per week. The current week is hollow: {part['days']} days of readings.", 320),
                 fig("Active merchants a week", act_svg, f"Merchants with at least one payment in the week. The hollow dot counts {part['days']} days only, "
                                                         "so fewer merchants have had a sale yet; it has no pace.", 320),
                 cols=2, colw=330)),
     section("The weeks",
             table(head, rows, num=range(1, 6), hide=(3, 5)))],
    "Sources: none. Acme Payments does not exist; the figures come from a seeded generator in the tufte repository "
    "(examples/acquirer/data.py) and are drawn with the tufte skill's rules: bars from zero for totals per week, dots for rates and "
    "readings, the partial week as banked plus pace.")
out = Path(__file__).resolve().parent.parent / "out" / "weekly-revenue.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html)
print(out)
