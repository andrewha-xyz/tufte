import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data import BY, CUR, DAYS, MDAYS, MONTHLY, NAME, STREAMS, pace  # noqa: E402
from kit import nice, bars, dollars, dots, fig, lines, mlab, mname, num, page, para, pct, row, section, table, usd  # noqa: E402

full = [r for r in MONTHLY if not r["partial"]]
cur, sep, aug, first = BY[CUR], BY["2026-09"], BY["2026-08"], MONTHLY[0]
rev_pace = pace("rev")
xlab = {i: mlab(r["month"]) for i, r in enumerate(MONTHLY) if i % 3 == 0 or r["partial"]}

rev_svg = bars([(f"{mname(r['month'])} {r['month'][:4]}: {dollars(r['rev'])}", r["rev"]) for r in full], top=1_000_000,
               ticks=[0, 500_000, 1_000_000], xlab=xlab,
               partial=dict(banked=cur["rev"], pace=rev_pace, title=f"October 1 to {DAYS}: {dollars(cur['rev'])} banked, pace {dollars(rev_pace)}"),
               right=[(sep["rev"], f"Sep {usd(sep['rev'])}", ""), (rev_pace, f"Oct pace {usd(rev_pace)}", "acc")], room=92,
               aria="Net revenue by month")

cum, run = [], 0.0
for r in MONTHLY:
    run += r["rev"]
    cum.append(run)
cum_svg = lines([dict(values=cum[:-1], step=True, label=f"{usd(cum[-2])} to Sep"),
                 dict(values=[None] * 12 + [cum[-1]], step=True, cls="line acc", label=f"{usd(cum[-1])} to Oct {DAYS}")],
                n=13, top=9_000_000, ticks=[0, 4_000_000, 8_000_000], xlab=xlab, room=96, aria="Net revenue earned to date")

take_svg = dots([(f"{mname(r['month'])}: {r['take'] * 1e4:.1f} bps", r["take"]) for r in full], lo=0.0080, hi=0.0100,
                ticks=[0.0080, 0.0090, 0.0100], fmt=lambda v: f"{v * 1e4:.0f}", xlab=xlab,
                partial=(f"October 1 to {DAYS}: {cur['take'] * 1e4:.1f} bps", cur["take"]),
                right=[(sep["take"], f"Sep {sep['take'] * 1e4:.1f}", "")], aria="Take rate by month, basis points")

big, small = STREAMS[0], STREAMS[1:]
stop = nice(max(max([r["streams"][k] for r in full] + [pace(k)]) for k in small))
stream_figs = [fig(big, bars([(f"{mname(r['month'])}: {dollars(r['streams'][big])}", r["streams"][big]) for r in full], top=1_000_000,
                             ticks=[0, 500_000, 1_000_000], xlab=xlab, W=280, H=110, room=48,
                             partial=dict(banked=cur["streams"][big], pace=pace(big), title="October so far")), width=280)]
for k in small:
    stream_figs.append(fig(k, bars([(f"{mname(r['month'])}: {dollars(r['streams'][k])}", r["streams"][k]) for r in full], top=stop,
                                   ticks=[0, stop / 2, stop], xlab=xlab, W=280, H=110, room=48,
                                   partial=dict(banked=cur["streams"][k], pace=pace(k), title="October so far")), width=280))

head = ["Month", "Net revenue", "Change", "Earned to date", "Fee margin", "Other fees", "Card volume", "Transactions", "Active merchants", "Take rate"]
rows, prev = [], None
for r, c in zip(MONTHLY, cum):
    other = r["rev"] - r["streams"][big]
    chg = "" if prev is None or r["partial"] else pct(r["rev"] / prev - 1)
    label = f"{mname(r['month'])} {r['month'][:4]}" if not r["partial"] else f"October 1 to {DAYS}"
    rows.append(("part" if r["partial"] else ("gap" if r["month"] == "2026-01" else ""),
                 [label, dollars(r["rev"]), chg, dollars(c), dollars(r["streams"][big]), dollars(other), f"${r['tpv'] / 1e6:.1f}M",
                  num(r["txns"]), num(r["active"]), f"{r['take'] * 1e4:.1f} bps"]))
    prev = r["rev"]
rows.append(("part", [f"October pace, {MDAYS} days", dollars(rev_pace), pct(rev_pace / sep["rev"] - 1), "", dollars(pace(big)),
                      dollars(rev_pace - pace(big)), f"${pace('tpv') / 1e6:.1f}M", num(pace("txns")), "", ""]))

lede = (f"Net revenue was {usd(sep['rev'])} in September, {pct(sep['rev'] / aug['rev'] - 1)} more than August and "
        f"{sep['rev'] / first['rev']:.1f} times October 2025. October has {DAYS} of {MDAYS} days banked and is on pace for "
        f"{usd(rev_pace)}. The take rate fell from {first['take'] * 1e4:.0f} to {sep['take'] * 1e4:.0f} basis points: the fee merchants "
        f"pay fell {(first['msc'] - sep['msc']) * 1e4:.0f} points of volume while interchange fell only {(first['ic'] - sep['ic']) * 1e4:.0f}.")
html = page(
    "Monthly net revenue", f"{NAME}, an invented merchant acquirer · October 2025 to {DAYS} October 2026 · every figure is made up", lede,
    [section("Revenue",
             row(fig("Net revenue a month", rev_svg, f"One bar per month from zero. October is drawn as what is banked (grey) and its pace for "
                                                      f"{MDAYS} days (dashed), never joined to the finished months.", 320),
                 fig("Earned to date", cum_svg, "A running total of a flow is a step, flat within each month.", 360),
                 fig("Take rate, basis points of card volume", take_svg, "One dot per month; a ratio has no bar. October is hollow: half a month.", 320),
                 cols=3, colw=330)),
     section("Where it comes from",
             para(f"The margin on merchant fees (what merchants pay, less interchange and scheme fees) is {pct(sep['streams'][big] / sep['rev'])} "
                  f"of September. The four smaller streams share one scale, {usd(stop)} at the top against {usd(1_000_000)}, so they compare with each other at their true size."),
             row(*stream_figs, cols=3, colw=290)),
     section("The ledger",
             table(head, rows, num=range(1, 10), hide=(2, 4, 5, 7, 8, 9)))],
    "Sources: none. Acme Payments does not exist; the figures come from a seeded generator in the tufte repository "
    "(examples/acquirer/data.py) and are drawn with the tufte skill's rules: bars from zero for totals per period, dots for ratios, "
    "a step for a running total, the partial month as banked plus pace.")
out = Path(__file__).resolve().parent.parent / "out" / "monthly-revenue.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html)
print(out)
