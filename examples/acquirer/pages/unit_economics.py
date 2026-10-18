import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data import BY, CUR, DAYS, MDAYS, MONTHLY, NAME, STREAMS, pace  # noqa: E402
from kit import bars, dollars, dots, esc, fig, mlab, mname, nice, page, para, pct, row, section, table, usd  # noqa: E402

full = [r for r in MONTHLY if not r["partial"]]
cur, sep, first = BY[CUR], BY["2026-09"], MONTHLY[0]
xlab = {i: mlab(r["month"]) for i, r in enumerate(MONTHLY) if i % 3 == 0 or r["partial"]}
big = STREAMS[0]
COSTS = sorted(sep["cost"], key=lambda k: -sep["cost"][k])
per = lambda v: v / sep["tpv"] * 100


def cents(v, plus=False):
    a, sign = abs(v), "\u2212" if v < 0 else ("+" if plus else "")
    return f"{sign}${a:.3f}" if a < 0.1 else f"{sign}${a:.2f}"


def ledger(rows, W=400, lab=150, room=48):
    """a bar table: one row per line of the $100, each bar from zero on one scale; rows are (label, value, cls, sign, rule_above, gap_above)"""
    top = max(abs(v) for _, v, *_ in rows)
    sx = lambda v: (W - lab - 6 - room) * abs(v) / top
    y, g = 4.0, []
    for label, v, cls, plus, rule, gap in rows:
        y += gap
        if rule:
            g.append(f'<line x1="{lab - 120}" x2="{W - room + 2}" y1="{y - 2:.1f}" y2="{y - 2:.1f}" class="leader"/>')
        w = max(0.8, sx(v))
        fill = {"acc": "var(--acc)", "dim": "var(--fill)", "": "var(--ink)"}[cls]
        g.append(f'<text x="{lab}" y="{y + 9:.1f}" class="lab{" acc" if cls == "acc" else ""}" text-anchor="end">{esc(label)}</text>')
        g.append(f'<rect x="{lab + 6}" y="{y + 1.5:.1f}" width="{w:.1f}" height="9" style="fill:{fill}"><title>{esc(label)}: {esc(cents(v, plus))}</title></rect>')
        g.append(f'<text x="{lab + 6 + w + 4:.1f}" y="{y + 9:.1f}" class="lab{" acc" if cls == "acc" else (" dim" if cls == "dim" else "")}">{esc(cents(v, plus))}</text>')
        y += 15
    g.append(f'<line x1="{lab + 6}" x2="{lab + 6}" y1="2" y2="{y + 2:.1f}" class="axis"/>')
    return f'<svg viewBox="0 0 {W} {y + 6:.0f}" role="img" aria-label="Where $100 of September card volume goes">' + "".join(g) + "</svg>"


other = {k: per(sep["streams"][k]) for k in sorted(STREAMS[1:], key=lambda k: -sep["streams"][k])}
rows = [("Merchant pays", sep["msc"] * 100, "", False, False, 0),
        ("Interchange to the issuer", -sep["ic"] * 100, "dim", False, False, 0),
        ("Scheme fees", -sep["scheme"] * 100, "dim", False, False, 0),
        ("Acme fee margin", per(sep["streams"][big]), "", False, True, 6)]
rows += [(k, v, "", True, False, 10 if i == 0 else 0) for i, (k, v) in enumerate(other.items())]
rows += [("Net revenue", per(sep["rev"]), "", False, True, 6)]
rows += [(k, -per(sep["cost"][k]), "dim", False, False, 10 if i == 0 else 0) for i, k in enumerate(COSTS)]
rows += [("Contribution", per(sep["contrib"]), "acc", False, True, 6)]
ledger_svg = ledger(rows)

c_pace = pace("contrib")
contrib_svg = bars([(f"{mname(r['month'])} {r['month'][:4]}: {dollars(r['contrib'])}", r["contrib"]) for r in full], top=400_000,
                   ticks=[0, 200_000, 400_000], xlab=xlab,
                   partial=dict(banked=cur["contrib"], pace=c_pace, title=f"October 1 to {DAYS}: {dollars(cur['contrib'])} banked, pace {dollars(c_pace)}"),
                   right=[(sep["contrib"], f"Sep {usd(sep['contrib'])}", ""), (c_pace, f"Oct pace {usd(c_pace)}", "acc")], room=92,
                   aria="Contribution by month")
margin = lambda r: r["contrib"] / r["rev"]
margin_svg = dots([(f"{mname(r['month'])}: {pct(margin(r), 1)}", margin(r)) for r in full], lo=0.0, hi=0.5,
                  ticks=[0.0, 0.25, 0.5], fmt=lambda v: f"{v * 100:.0f} %", xlab=xlab,
                  partial=(f"October 1 to {DAYS}: {pct(margin(cur), 1)}", margin(cur)),
                  right=[(margin(sep), f"Sep {pct(margin(sep))}", "")], aria="Contribution margin by month")

ctop = nice(max(max(r["cost"][k] for r in full) for k in COSTS))
cost_figs = [fig(k, bars([(f"{mname(r['month'])}: {dollars(r['cost'][k])}", r["cost"][k]) for r in full], top=ctop,
                         ticks=[0, ctop / 2, ctop], xlab=xlab, W=280, H=110, room=56,
                         partial=dict(banked=cur["cost"][k], pace=cur["cost"][k] * MDAYS / DAYS, title="October so far"),
                         right=[(sep["cost"][k], f"Sep {usd(sep['cost'][k])}", "")], aria=f"{k} by month"), width=280) for k in COSTS]

short = {"Onboarding checks": "Onboarding", "Partner commissions": "Partners", "Risk losses": "Risk"}
head = ["Month", "Net revenue"] + [short.get(k, k) for k in COSTS] + ["Contribution", "Margin"]
tab = []
for r in MONTHLY:
    label = f"{mname(r['month'])} {r['month'][:4]}" if not r["partial"] else f"October 1 to {DAYS}"
    tab.append(("part" if r["partial"] else ("gap" if r["month"] == "2026-01" else ""),
                [label, dollars(r["rev"])] + [dollars(r["cost"][k]) for k in COSTS] + [dollars(r["contrib"]), pct(margin(r))]))

plat = sep["cost"]["Platform"] / sum(sep["cost"].values())
lede = (f"Of every $100 a merchant ran through {NAME} in September, the merchant paid {cents(sep['msc'] * 100)}; "
        f"{cents((sep['ic'] + sep['scheme']) * 100)} went on to issuers and card schemes, {cents(per(sep['rev']))} stayed as net revenue and "
        f"{cents(per(sep['contrib']))} was left after costs. Contribution margin rose from {pct(margin(first))} in October 2025 to "
        f"{pct(margin(sep))} because the platform, {pct(plat)} of September's costs, grows slower than volume.")
html = page(
    "Unit economics", f"{NAME}, an invented merchant acquirer · October 2025 to {DAYS} October 2026 · every figure is made up", lede,
    [section("Where $100 goes",
             fig("$100 of September card volume", ledger_svg,
                 "One bar per line, each from zero on one scale, so a pass-through and a margin compare at their true size. Grey is money "
                 "that leaves; black is what Acme keeps; the contribution line is the one that matters.", 400)),
     section("Contribution",
             row(fig("Contribution a month", contrib_svg, f"A total per month is a bar from zero. October is banked (grey) plus its {MDAYS}-day pace (dashed), never joined to the finished months.", 320),
                 fig("Contribution margin, share of net revenue", margin_svg, "A ratio is a dot, not a bar. October is hollow: half a month.", 320),
                 cols=2, colw=340)),
     section("Six cost lines",
             para(f"All six panels share one scale, {usd(ctop)} at the top, so the platform's fixed cost and the five other lines "
                  f"are seen at their true size: the five together were {usd(sum(sep['cost'].values()) - sep['cost']['Platform'])} in September."),
             row(*cost_figs, cols=3, colw=290)),
     section("Profit and loss by month",
             table(head, tab, num=range(1, len(head)), hide=tuple(range(2, 2 + len(COSTS)))))],
    "Sources: none. Acme Payments does not exist; the figures come from a seeded generator in the tufte repository "
    "(examples/acquirer/data.py) and are drawn with the tufte skill's rules: a bar table for the parts of one total, bars from zero for "
    "totals per period, dots for ratios, small multiples on one scale, the partial month as banked plus pace.")
out = Path(__file__).resolve().parent.parent / "out" / "unit-economics.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html)
print(out)
