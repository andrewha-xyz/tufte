import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.append(str(HERE.parent / "acquirer"))
from data import (CUR_DAYS, CUR_WEEK, DEPLOYS, END, INCIDENTS, NAME, PRS, ROLLBACK_DAY, TEAMS, TRAIN_END, WEEKS, monthly,  # noqa: E402
                  week, weekly)
from kit import _labels, bars, dots, esc, fig, page, para, pct, row, section, table  # noqa: E402

TEAM = list(TEAMS)
day = lambda d: f"{d:%b} {d.day}"
_past = [d for d in DEPLOYS if week(d["day"]) < CUR_WEEK]
SHARE = sum(1 for d in _past if d["day"].weekday() < CUR_DAYS) / len(_past)
pace = 1 / SHARE
xlab = {i: f"{w:%b}" for i, w in enumerate(WEEKS) if w.day <= 7}
W = {t: weekly(t) for t in TEAM}
M = {t: monthly(t) for t in TEAM}
LAST = WEEKS[-2]


def hours(h):
    return f"{h:.0f} h" if h < 48 else f"{h / 24:.0f} days"


def deploy_fig(t):
    rows = W[t]
    full, cur = rows[:-1], rows[-1]
    return fig(t, bars([(f"Week of {day(r['week'])}: {r['deploys']} deploys", r["deploys"]) for r in full], top=40, ticks=[0, 20, 40],
                       fmt=lambda v: f"{v:.0f}", xlab=xlab, W=300, H=120, room=70,
                       partial=dict(banked=cur["deploys"], pace=cur["deploys"] * pace, title=f"Week of {day(cur['week'])}, {CUR_DAYS} days: {cur['deploys']}"),
                       right=[(full[-1]["deploys"], f"{day(full[-1]['week'])} {full[-1]['deploys']}", "")], aria=f"{t}: deploys a week"), width=300)


def lead_svg(t, W_=300, H=140, room=70, lo=4, hi=400):
    """Tufte's quartile plot: per week a line from the first to the third quartile with a gap around the median dot, log scale"""
    rows = [r for r in W[t] if r["lead"][1]]
    n = len(WEEKS)
    pr, top, b = W_ - room, 8, H - 22
    ys = lambda v: top + (b - top) * (math.log(hi) - math.log(max(lo, min(hi, v)))) / (math.log(hi) - math.log(lo))
    slot = pr / n
    g = [f'<svg viewBox="0 0 {W_} {H}" role="img" aria-label="{esc(t)}: lead time a week, quartiles">']
    for v, lab in ((4, "4 h"), (24, "1 day"), (72, "3 days"), (168, "1 week")):
        g.append(f'<text x="-7" y="{ys(v) + 3.5:.1f}" class="tick" text-anchor="end">{lab}</text>')
    if t == "Merchant dashboard":
        x = WEEKS.index(TRAIN_END - __import__("datetime").timedelta(days=TRAIN_END.weekday())) * slot
        g.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{b}" class="ref"/>')
        g.append(f'<text x="{x + 4:.1f}" y="{top + 8}" class="lab dim">release train ends</text>')
    for r in rows:
        i = WEEKS.index(r["week"])
        x = i * slot + slot / 2
        q1, md, q3 = r["lead"]
        part = r["partial"]
        cls = "line acc" if part else "line"
        if ys(q1) - ys(md) > 3:
            g.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{ys(q1):.1f}" y2="{ys(md) + 2.5:.1f}" class="{cls}" style="stroke-width:1"/>')
        if ys(md) - ys(q3) > 3:
            g.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{ys(md) - 2.5:.1f}" y2="{ys(q3):.1f}" class="{cls}" style="stroke-width:1"/>')
        g.append(f'<circle cx="{x:.1f}" cy="{ys(md):.1f}" r="1.8" class="{"hollow" if part else "dot"}"><title>Week of {day(r["week"])}: '
                 f'median {hours(md)}, middle half {hours(q1)} to {hours(q3)}</title></circle>')
    g.append(f'<line x1="0" x2="{pr:.1f}" y1="{b + 2}" y2="{b + 2}" class="axis"/>')
    for i, txt in xlab.items():
        g.append(f'<text x="{i * slot + slot / 2:.1f}" y="{b + 17}" class="tick" text-anchor="middle">{txt}</text>')
    last = [r for r in rows if not r["partial"]][-1]
    _labels(g, [(last["lead"][1], f"{day(last['week'])} {hours(last['lead'][1])}", "")], pr + 8, ys)
    g.append("</svg>")
    return "".join(g)


def cfr_fig(t):
    rows = M[t]
    full, cur = rows[:-1], rows[-1]
    vals = [(f"{r['month']}: {r['failed']} of {r['deploys']} deploys failed", r["cfr"] or 0) for r in full]
    return fig(t, dots(vals, lo=0, hi=1.0, ticks=[0, 0.5, 1.0], fmt=lambda v: f"{v * 100:.0f} %", W=300, H=110, room=70,
                       xlab={i: f"{r['month'][5:]}" and ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"][i] for i, r in enumerate(rows)},
                       partial=(f"October 1 to 15: {cur['failed']} of {cur['deploys']}", cur["cfr"] or 0),
                       right=[(full[-1]["cfr"] or 0, f"Sep {pct(full[-1]['cfr'] or 0)}", "")], aria=f"{t}: change failure rate a month"), width=300)


def restore_svg(W_=400, H=170, room=72, lo=0.25, hi=24):
    """every incident is one dot at its date and its time to restore, log scale; Platform in the accent colour"""
    pr, top, b = W_ - room, 8, H - 22
    span = (END - WEEKS[0]).days
    xs = lambda d: (d - WEEKS[0]).days / span * pr
    ys = lambda v: top + (b - top) * (math.log(hi) - math.log(max(lo, min(hi, v)))) / (math.log(hi) - math.log(lo))
    g = [f'<svg viewBox="0 0 {W_} {H}" role="img" aria-label="Time to restore, every incident">']
    for v, lab in ((0.25, "15 min"), (1, "1 h"), (4, "4 h"), (24, "1 day")):
        g.append(f'<text x="-7" y="{ys(v) + 3.5:.1f}" class="tick" text-anchor="end">{lab}</text>')
    x = xs(ROLLBACK_DAY)
    g.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{b}" class="ref"/><text x="{x + 4:.1f}" y="{top + 8}" class="lab dim">Platform: one-step rollback</text>')
    for i in INCIDENTS:
        acc = i["team"] == "Platform"
        g.append(f'<circle cx="{xs(i["day"]):.1f}" cy="{ys(i["restore"]):.1f}" r="2.3" class="dot{" acc" if acc else ""}" style="opacity:{1 if acc else 0.55}">'
                 f'<title>{esc(i["team"])}, {day(i["day"])}: restored in {i["restore"]:.1f} h</title></circle>')
    g.append(f'<line x1="0" x2="{pr:.1f}" y1="{b + 2}" y2="{b + 2}" class="axis"/>')
    for w in WEEKS:
        if w.day <= 7:
            g.append(f'<text x="{xs(w):.1f}" y="{b + 17}" class="tick" text-anchor="middle">{w:%b}</text>')
    before = statistics.median([i["restore"] for i in INCIDENTS if i["team"] == "Platform" and i["day"] < ROLLBACK_DAY])
    after = statistics.median([i["restore"] for i in INCIDENTS if i["team"] == "Platform" and i["day"] >= ROLLBACK_DAY])
    _labels(g, [(after, f"Platform {hours(after)}", "acc")], pr + 8, ys)
    g.append("</svg>")
    return "".join(g), before, after


restore, before, after = restore_svg()
others = [i["restore"] for i in INCIDENTS if i["team"] != "Platform"]

lead_sep = {t: statistics.median([p["lead"] for p in PRS if p["shipped"] and p["team"] == t and f"{p['deployed']:%Y-%m}" == "2026-09"]) for t in TEAM}
lead_jul = {t: statistics.median([p["lead"] for p in PRS if p["shipped"] and p["team"] == t and f"{p['deployed']:%Y-%m}" == "2026-07"]) for t in TEAM}
dep_last = sum(W[t][-2]["deploys"] for t in TEAM)
cfr_all = sum(d["failed"] for d in DEPLOYS) / len(DEPLOYS)
train = [d for d in DEPLOYS if d["team"] == "Merchant dashboard" and d["train"]]
after_train = [d for d in DEPLOYS if d["team"] == "Merchant dashboard" and not d["train"]]

head = ["Team", "Deploys in September", "Lead time, September median", "July median", "Change failure, April to October", "Incidents", "Median restore"]
rows = []
for t in TEAM:
    ds = [d for d in DEPLOYS if d["team"] == t]
    inc = [i["restore"] for i in INCIDENTS if i["team"] == t]
    rows.append(("", [t, str(sum(1 for d in ds if f"{d['day']:%Y-%m}" == "2026-09")), hours(lead_sep[t]), hours(lead_jul[t]),
                      pct(sum(d["failed"] for d in ds) / len(ds), 1), str(len(inc)), f"{statistics.median(inc):.1f} h" if inc else ""]))

lede = (f"The four teams deployed {dep_last} times in the week of {day(LAST)}. Merchant dashboard shipped once a week until {day(TRAIN_END)}; "
        f"its median time from first commit to production fell from {hours(lead_jul['Merchant dashboard'])} in July to "
        f"{hours(lead_sep['Merchant dashboard'])} in September once every merged change deployed on its own. Its weekly releases failed "
        f"{pct(sum(d['failed'] for d in train) / len(train))} of the time, its single-change deploys {pct(sum(d['failed'] for d in after_train) / len(after_train))}.")

html = page(
    "Delivery", f"{NAME}, an invented team of 22 · 13 April to 15 October 2026 · every figure is made up", lede,
    [section("Deploys a week",
             para(f"One panel per team on one scale. A deploy is a count over a week, so it is a bar from zero; the week of {day(CUR_WEEK)} has "
                  f"{CUR_DAYS} days so far, drawn as banked plus its pace: the past weeks put {pct(SHARE)} of their deploys, weekends included, "
                  f"on those {CUR_DAYS} weekdays."),
             row(*[deploy_fig(t) for t in TEAM], cols=2, colw=320)),
     section("Lead time, first commit to production",
             para("Each week is a quartile plot: the line runs from the first to the third quartile of that week's changes, broken around the "
                  "median dot. The scale is logarithmic so an hour and a week both read; the current week is hollow."),
             row(*[fig(t, lead_svg(t), width=300) for t in TEAM], cols=2, colw=320)),
     section("Failures and restores",
             para(f"A change failure rate is a ratio, so one dot a month; hover a dot for the deploys behind it, because a month with few deploys "
                  f"swings hard. {pct(cfr_all, 1)} of all {len(DEPLOYS):,} deploys failed."),
             row(*[cfr_fig(t) for t in TEAM], cols=2, colw=320),
             row(fig("Time to restore, every incident", restore,
                     f"One dot per incident at its date and its time to restore. Platform, in red, restored in a median {hours(before)} before "
                     f"its one-step rollback on {day(ROLLBACK_DAY)} and {hours(after)} after; the other teams' {len(others)} incidents took a "
                     f"median {statistics.median(others):.1f} h.", 400), cols=1, colw=420)),
     section("By team", table(head, rows, num=range(1, 7), hide=(3, 4, 5)))],
    "Sources: none. Acme Payments and its engineers do not exist; every pull request, deploy and incident comes from a seeded generator in "
    "the tufte repository (examples/engineering/data.py), drawn with the tufte skill's rules: bars from zero for counts per week, a quartile "
    "plot for a distribution per week, dots for rates, one dot per event, the partial week as banked plus pace.")
out = HERE / "out" / "delivery.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html.replace(" %", " %"))
print(out)
