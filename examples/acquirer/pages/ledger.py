import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data import BY, CUR, DAYS, MDAYS, MONTHLY, NAME, STREAMS  # noqa: E402
from kit import bars, dollars, dots, fig, mlab, mname, para, pct, row, section, table, usd, page  # noqa: E402

big = STREAMS[0]
full = [r for r in MONTHLY if not r["partial"]]
cur, sep, aug, first = BY[CUR], BY["2026-09"], BY["2026-08"], MONTHLY[0]
k = MDAYS / DAYS
xlab = {i: mlab(r["month"]) for i, r in enumerate(MONTHLY) if i % 3 == 0 or r["partial"]}
lines = {"Net revenue": lambda r: r["rev"], big: lambda r: r["streams"][big], "All other fees": lambda r: r["rev"] - r["streams"][big]}
LO = min([0.0] + [f(r) for f in lines.values() for r in MONTHLY] + [f(cur) * k for f in lines.values()])


def money(name, f):
    p = f(cur) * k
    return fig(name, bars([(f"{mname(r['month'])} {r['month'][:4]}: {dollars(f(r))}", f(r)) for r in full], top=1_000_000, lo=LO,
                          ticks=[0, 500_000, 1_000_000], xlab=xlab,
                          partial=dict(banked=f(cur), pace=p, title=f"October 1 to {DAYS}: {dollars(f(cur))} banked, pace {dollars(p)}"),
                          right=[(f(sep), f"Sep {usd(f(sep))}", ""), (p, f"Oct pace {usd(p)}", "acc")], room=92, aria=f"{name} by month"), width=320)


def rate(name, key, lo, hi, ticks, fmt, lab, cap):
    return fig(name, dots([(f"{mname(r['month'])}: {lab(r[key])}", r[key]) for r in full], lo=lo, hi=hi, ticks=ticks, fmt=fmt, xlab=xlab,
                          partial=(f"October 1 to {DAYS}: {lab(cur[key])}", cur[key]), right=[(sep[key], f"Sep {lab(sep[key])}", "")],
                          room=64, aria=f"{name} by month"), cap, 320)


b = lambda v: f"{v * 1e4:.0f}"
bp = lambda r, key: f"{r['streams'][key] / r['tpv'] * 1e4:.0f}"
musd = lambda v: f"${v / 1e6:.2f}M"
b1 = lambda v: f"{v * 1e4:.1f}"
rates = [rate("Take rate, basis points of volume", "take", 0.0075, 0.0100, [0.0080, 0.0090, 0.0100], b, b1,
              "Net revenue over card volume: what Acme keeps from each dollar. One dot per month; October is hollow, half a month."),
         rate("Merchant fee rate, basis points", "msc", 0.0175, 0.0200, [0.0180, 0.0190, 0.0200], b, b1,
              "What merchants are charged per dollar of volume, before anything is passed on."),
         rate("Interchange rate, basis points", "ic", 0.0100, 0.0125, [0.0100, 0.0110, 0.0120], b, b1,
              "Paid on to the card issuers. The three basis-point panels span the same 25 points, so their slopes compare."),
         rate("Cross-border share of volume", "xb", 0.14, 0.25, [0.15, 0.20, 0.25], lambda v: f"{v * 100:.0f} %", lambda v: pct(v, 1),
              "Volume on cards issued abroad, which carries the FX markup.")]

head = ["Month", "Card volume", "Merchant fees charged", "Interchange", "Scheme fees", "Fee margin", "Other fees", "Net revenue"]


def cells(r, f=1.0):
    return [musd(r["tpv"] * f), dollars(r["tpv"] * r["msc"] * f), dollars(r["tpv"] * r["ic"] * f), dollars(r["tpv"] * r["scheme"] * f),
            dollars(r["streams"][big] * f), dollars((r["rev"] - r["streams"][big]) * f), dollars(r["rev"] * f)]


rows = [("gap" if r["month"] == "2026-01" else "", [f"{mname(r['month'])} {r['month'][:4]}"] + cells(r)) for r in full]
rows.append(("part", [f"October 1 to {DAYS}"] + cells(cur)))
rows.append(("part", ["October pace"] + cells(cur, k)))

charged = sep["tpv"] * sep["msc"]
lede = (f"In September merchants paid Acme {usd(charged)} in fees on {usd(sep['tpv'])} of card volume. {usd(sep['tpv'] * sep['ic'])} went on to card "
        f"issuers as interchange and {usd(sep['tpv'] * sep['scheme'])} to the card schemes, leaving a fee margin of {usd(sep['streams'][big])}; "
        f"other fees added {usd(sep['rev'] - sep['streams'][big])} for net revenue of {usd(sep['rev'])}. "
        f"October has {DAYS} of {MDAYS} days banked and is on pace for {usd(cur['rev'] * k)}.")
html = page(
    "Revenue ledger", f"{NAME}, an invented merchant acquirer · October 2025 to {DAYS} October 2026 · every figure is made up", lede,
    [section("Revenue on one scale",
             para(f"The three panels share one scale, {usd(1_000_000)} at the top, so the fee margin and the other fees read as parts of net revenue at their true size."),
             row(*[money(n, f) for n, f in lines.items()], cols=3, colw=330),
             para(f"One bar per month from zero. October is drawn as what is banked (grey) and its pace for {MDAYS} days (dashed), never joined to the finished months.")
             .replace("<p>", '<p class="cap">', 1)),
     section("The rates behind it",
             para(f"The take rate fell from {first['take'] * 1e4:.0f} to {sep['take'] * 1e4:.0f} basis points. The merchant fee rate fell "
                  f"{(first['msc'] - sep['msc']) * 1e4:.0f} points while interchange fell {(first['ic'] - sep['ic']) * 1e4:.0f}, so the fee margin went from "
                  f"{bp(first, big)} to {bp(sep, big)} points of volume. The FX markup, on a cross-border share up from "
                  f"{pct(first['xb'])} to {pct(sep['xb'])}, rose from {bp(first, 'FX markup')} to {bp(sep, 'FX markup')} points, and instant payouts "
                  f"added {bp(sep, 'Instant payouts')}, which made up part of the difference."),
             row(*rates, cols=2, colw=330)),
     section("The ledger",
             para("Each row adds up: merchant fees charged, less interchange and scheme fees, is the fee margin; the fee margin plus the other fees is net revenue."),
             table(head, rows, num=range(1, 8), hide=(1, 3, 4, 6)))],
    "Sources: none. Acme Payments does not exist; the figures come from a seeded generator in the tufte repository "
    "(examples/acquirer/data.py) and are drawn with the tufte skill's rules: bars from zero for totals per month on one shared scale, "
    "dots for rates, the partial month as banked plus pace.")
out = Path(__file__).resolve().parent.parent / "out" / "revenue-ledger.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html)
print(out)
