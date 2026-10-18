import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data import BY, CUR, DAYS, MDAYS, MONTHLY, NAME  # noqa: E402
from kit import bars, dollars, dots, fig, mlab, mname, num, page, para, row, section, table, usd  # noqa: E402

full = [r for r in MONTHLY if not r["partial"]]
cur, sep, aug = BY[CUR], BY["2026-09"], BY["2026-08"]
k = MDAYS / DAYS
xlab = {i: mlab(r["month"]) for i, r in enumerate(MONTHLY) if i % 4 == 0}
W, H, ROOM = 280, 110, 70
M = lambda v: f"{v / 1e6:.0f}M" if v else "0"


def total(title, key, top, ticks, fmt, lab, cap):
    svg = bars([(f"{mname(r['month'])}: {lab(r[key])}", r[key]) for r in full], top=top, ticks=ticks, fmt=fmt, xlab=xlab, W=W, H=H, room=ROOM,
               right=[(sep[key], f"Sep {lab(sep[key])}", "")],
               partial=dict(banked=cur[key], pace=cur[key] * k, title=f"October 1 to {DAYS}: {lab(cur[key])}, pace {lab(cur[key] * k)}"), aria=title)
    return fig(title, svg, cap, W)


def ratio(title, key, lo, hi, ticks, fmt, lab, cap):
    svg = dots([(f"{mname(r['month'])}: {lab(r[key])}", r[key]) for r in full], lo=lo, hi=hi, ticks=ticks, fmt=fmt, xlab=xlab, W=W, H=H,
               room=ROOM, partial=(f"October 1 to {DAYS}: {lab(cur[key])}", cur[key]), right=[(sep[key], f"Sep {lab(sep[key])}", "")], aria=title)
    return fig(title, svg, cap, W)


bps = lambda v: f"{v * 1e4:.1f}"
pc = lambda v: f"{v * 100:.1f} %"
figs = [total("Card volume a month", "tpv", 110e6, [0, 50e6, 100e6], usd, usd, "A total per month: bars from zero, October banked plus pace."),
        total("Transactions a month", "txns", 2.75e6, [0, 1e6, 2e6], M, lambda v: f"{v / 1e6:.2f}M", "A count per month is a total too."),
        ratio("Average ticket", "ticket", 36, 42, [36, 39, 42], lambda v: f"${v:.0f}", lambda v: f"${v:.2f}",
              "Volume over transactions, a ratio: one dot a month, October hollow."),
        ratio("Active merchants", "active", 1200, 2400, [1200, 1800, 2400], num, num,
              f"A headcount is a state, not a flow: one dot a month; October is hollow, {DAYS} days so far, with no pace."),
        total("New merchants", "new", 250, [0, 100, 200], num, num, "First payment in the month, a flow: October banked plus pace."),
        total("Net revenue", "rev", 1_000_000, [0, 500_000, 1_000_000], usd, usd, "The headline total, bars from zero."),
        ratio("Take rate, basis points", "take", 0.0080, 0.0100, [0.0080, 0.0090, 0.0100], lambda v: f"{v * 1e4:.0f}", bps,
              "Net revenue over volume: a ratio, one dot a month."),
        ratio("Approval rate", "approval", 0.920, 0.945, [0.920, 0.930, 0.940], lambda v: f"{v * 100:.0f} %", pc,
              "Approved over attempted payments, a ratio."),
        ratio("Chargebacks per 10,000 payments", "cb_bps", 20, 32, [20, 25, 30], lambda v: f"{v:.0f}", lambda v: f"{v:.1f}",
              "A rate, so a dot; lower is better.")]


def sign(v, f):
    t = f(abs(v))
    return t if float(t.split()[0]) == 0 else ("+" if v > 0 else "−") + t


rel = lambda key: sign(sep[key] / aug[key] - 1, lambda v: f"{v * 100:.1f} %")
spec = [("Card volume", "tpv", lambda v: f"${v / 1e6:.1f}M", True, rel("tpv")),
        ("Transactions", "txns", lambda v: f"{v / 1e6:.2f}M", True, rel("txns")),
        ("New merchants", "new", num, True, rel("new")),
        ("Net revenue", "rev", usd, True, rel("rev")),
        ("Average ticket", "ticket", lambda v: f"${v:.2f}", False, rel("ticket")),
        ("Active merchants", "active", num, False, rel("active")),
        ("Take rate, bps", "take", lambda v: f"{v * 1e4:.1f}", False, sign(sep["take"] - aug["take"], lambda v: f"{v * 1e4:.1f}")),
        ("Approval rate, %", "approval", lambda v: f"{v * 100:.1f}", False, sign(sep["approval"] - aug["approval"], lambda v: f"{v * 100:.1f}")),
        ("Chargebacks /10k", "cb_bps", lambda v: f"{v:.1f}", False, sign(sep["cb_bps"] - aug["cb_bps"], lambda v: f"{v:.1f}"))]
sub = lambda t: f'<span style="font-style:italic;color:var(--grey)">{t}</span>'
rows = []
for name, key, f, p, chg in spec:
    if not p and not any(r[1][0] == sub("Ratio or headcount") for r in rows):
        rows.append(("gap", [sub("Ratio or headcount"), "", sub("October so far"), ""]))
    rows.append(("", [name, f(sep[key]), f(cur[key] * k) if p else f(cur[key]), chg]))

lede = (f"Nine measures of September on panels of one size: card volume {usd(sep['tpv'])}, {num(sep['active'])} active merchants, "
        f"{num(sep['new'])} new ones, net revenue {usd(sep['rev'])}. Totals are bars from zero and October is banked plus pace; "
        f"ratios and the headcount are dots and October is hollow. Chargebacks fell to {sep['cb_bps']:.1f} per 10,000 payments while approvals reached "
        f"{pc(sep['approval']).replace(' ', '&nbsp;')}.")
html = page(
    "The ledger as small multiples", f"{NAME}, an invented merchant acquirer · October 2025 to {DAYS} October 2026 · every figure is made up", lede,
    [section("Nine panels, one size",
             para("Each panel has its own vertical scale, since the units differ; the shape and the September label are what compare across them."),
             row(*figs, cols=3, colw=300)),
     section("September at a glance",
             para(f"Totals add up across days, so October is shown at its pace for {MDAYS} days; ratios and the headcount of merchants do not, "
                  f"so October is the {DAYS} days so far."),
             table(["Total a month", "September", "October pace", "Change on August"], rows, num=(1, 2, 3)))],
    "Sources: none. Acme Payments does not exist; the figures come from a seeded generator in the tufte repository "
    "(examples/acquirer/data.py) and are drawn with the tufte skill's rules: small multiples of one size, bars from zero for totals, "
    "dots for ratios, the partial month as banked plus pace.")
out = Path(__file__).resolve().parent.parent / "out" / "revenue-ledger-grid.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html)
print(out)
