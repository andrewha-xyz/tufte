import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.append(str(HERE.parent / "acquirer"))
from data import CUR_DAYS, CUR_WEEK, LEAVER, LEAVER_DAY, NAME, PEOPLE, PRS, TEAMS, TRAIN_END, WEEKS, quartiles, week, weekly  # noqa: E402
from kit import _labels, esc, fig, num, page, para, pct, row, section, table  # noqa: E402

TEAM = list(TEAMS)
RISK = "Risk and disputes"
day = lambda d: f"{d:%b} {d.day}"
xlab = {i: f"{w:%b}" for i, w in enumerate(WEEKS) if w.day <= 7}
W = {t: weekly(t) for t in TEAM}
STAGES = [("coding", "coding, before opening"), ("pickup", "waiting for a first review"), ("review", "review to merge"),
          ("deploy_wait", "merge to production")]
month = lambda t, m: [p for p in PRS if p["team"] == t and f"{p['merged']:%Y-%m}" == m]
med = lambda xs: statistics.median(xs)


def hours(h):
    return f"{h:.1f} h" if h < 10 else f"{h:.0f} h"


def stages_svg(W_=400, left=132, room=40):
    """a bar table: per team one row per stage, one scale for all, the value printed at the end of each bar"""
    sep = {t: {k: med([p[k] for p in month(t, "2026-09")]) for k, _ in STAGES} for t in TEAM}
    hi = max(v for s in sep.values() for v in s.values())
    span = W_ - left - room
    xs = lambda v: left + span * v / hi
    rh, gh, bh = 14, 22, 8
    H = len(TEAM) * (gh + len(STAGES) * rh) + 4
    g = [f'<svg viewBox="0 0 {W_} {H}" role="img" aria-label="Median hours in each stage of a merged pull request, September, by team">']
    y = 0
    for t in TEAM:
        y += gh
        g.append(f'<text x="0" y="{y - 6}" class="lab" style="font-style:italic">{esc(t)}</text>')
        for k, name in STAGES:
            v = sep[t][k]
            acc = t == RISK and k == "pickup"
            g.append(f'<text x="{left - 8}" y="{y + bh - 0.5:.1f}" class="tick" text-anchor="end">{esc(name)}</text>')
            g.append(f'<rect x="{left}" y="{y + 1:.1f}" width="{max(0.8, xs(v) - left):.1f}" height="{bh}" class="bar{" acc" if acc else ""}"'
                     f'{" style=" + chr(34) + "fill:var(--acc)" + chr(34) if acc else ""}><title>{esc(t)}, {esc(name)}: median {hours(v)}</title></rect>')
            g.append(f'<text x="{xs(v) + 4:.1f}" y="{y + bh - 0.5:.1f}" class="lab{" acc" if acc else ""}">{hours(v)}</text>')
            y += rh
        g.append(f'<line x1="{left}" x2="{left}" y1="{y - len(STAGES) * rh}" y2="{y + 1}" class="axis"/>')
    g.append("</svg>")
    return "".join(g), sep


def pickup_svg(t, W_=300, H=140, room=70, hi=24):
    """per week a line from the first to the third quartile of first-review waits, broken around the median dot"""
    rows = [r for r in W[t] if r["pickup"][1]]
    n = len(WEEKS)
    pr, top, b = W_ - room, 8, H - 22
    ys = lambda v: top + (b - top) * (hi - min(hi, v)) / hi
    slot = pr / n
    g = [f'<svg viewBox="0 0 {W_} {H}" role="img" aria-label="{esc(t)}: wait for a first review, quartiles by week">']
    for v in (0, 10, 20):
        g.append(f'<text x="-7" y="{ys(v) + 3.5:.1f}" class="tick" text-anchor="end">{v} h</text>')
    if t == RISK:
        x = WEEKS.index(week(LEAVER_DAY)) * slot
        g.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{b}" class="ref"/>')
        g.append(f'<text x="{x - 4:.1f}" y="{top + 8}" class="lab dim" text-anchor="end">{LEAVER} leaves, {day(LEAVER_DAY)}</text>')
    for r in rows:
        x = WEEKS.index(r["week"]) * slot + slot / 2
        q1, md, q3 = r["pickup"]
        cls = "line acc" if r["partial"] else "line"
        if ys(q1) - ys(md) > 3:
            g.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{ys(q1):.1f}" y2="{ys(md) + 2.5:.1f}" class="{cls}" style="stroke-width:1"/>')
        if ys(md) - ys(q3) > 3:
            g.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{ys(md) - 2.5:.1f}" y2="{ys(q3):.1f}" class="{cls}" style="stroke-width:1"/>')
        g.append(f'<circle cx="{x:.1f}" cy="{ys(md):.1f}" r="1.8" class="{"hollow" if r["partial"] else "dot"}"><title>Week of {day(r["week"])}'
                 f'{f", {CUR_DAYS} of 5 days" if r["partial"] else ""}: median {hours(md)}, middle half {hours(q1)} to {hours(q3)}</title></circle>')
    g.append(f'<line x1="0" x2="{pr:.1f}" y1="{b + 2}" y2="{b + 2}" class="axis"/>')
    for i, txt in xlab.items():
        g.append(f'<text x="{i * slot + slot / 2:.1f}" y="{b + 17}" class="tick" text-anchor="middle">{txt}</text>')
    last = [r for r in rows if not r["partial"]][-1]
    _labels(g, [(last["pickup"][1], f"{day(last['week'])} {hours(last['pickup'][1])}", "acc" if t == RISK else "")], pr + 8, ys)
    g.append("</svg>")
    return "".join(g)


def size_svg(W_=400, left=104, mid=262, d0=292, d1=360, lo=4, hi=8000):
    """Tufte's quartile plot of lines changed per pull request, log scale, beside a dot for the share over 400 lines"""
    rh, top = 26, 20
    H = top + len(TEAM) * rh + 22
    xs = lambda v: left + (mid - left) * (math.log(max(lo, v)) - math.log(lo)) / (math.log(hi) - math.log(lo))
    smax = 0.25
    xd = lambda v: d0 + (d1 - d0) * v / smax
    b = top + len(TEAM) * rh
    g = [f'<svg viewBox="0 0 {W_} {H}" role="img" aria-label="Lines changed per pull request, quartiles by team, and the share over 400 lines">']
    g.append(f'<text x="{left}" y="10" class="tick">lines changed, log scale</text><text x="{d0}" y="10" class="tick">over 400 lines</text>')
    x4 = xs(400)
    g.append(f'<line x1="{x4:.1f}" x2="{x4:.1f}" y1="{top}" y2="{b}" class="ref"/>')
    out = {}
    for i, t in enumerate(TEAM):
        s = sorted(p["size"] for p in PRS if p["team"] == t)
        q1, md, q3 = quartiles(s)
        share = sum(v > 400 for v in s) / len(s)
        out[t] = (md, share)
        y = top + i * rh + rh / 2
        g.append(f'<text x="0" y="{y + 3.5:.1f}" class="lab">{esc(t)}</text>')
        tip = f"{esc(t)}: {len(s)} pull requests, smallest {s[0]}, quartiles {q1:.0f}, {md:.0f}, {q3:.0f} lines, largest {num(s[-1])}"
        g.append(f'<g><title>{tip}</title>')
        g.append(f'<line x1="{xs(s[0]):.1f}" x2="{xs(q1):.1f}" y1="{y:.1f}" y2="{y:.1f}" class="line" style="stroke-width:.8;stroke:var(--grey)"/>')
        g.append(f'<line x1="{xs(q3):.1f}" x2="{xs(s[-1]):.1f}" y1="{y:.1f}" y2="{y:.1f}" class="line" style="stroke-width:.8;stroke:var(--grey)"/>')
        g.append(f'<line x1="{xs(q1):.1f}" x2="{xs(md) - 3:.1f}" y1="{y - 3:.1f}" y2="{y - 3:.1f}" class="line" style="stroke-width:1.6"/>')
        g.append(f'<line x1="{xs(md) + 3:.1f}" x2="{xs(q3):.1f}" y1="{y - 3:.1f}" y2="{y - 3:.1f}" class="line" style="stroke-width:1.6"/>')
        g.append(f'<circle cx="{xs(md):.1f}" cy="{y - 3:.1f}" r="2.2" class="dot"/></g>')
        g.append(f'<circle cx="{xd(share):.1f}" cy="{y:.1f}" r="2.6" class="dot"><title>{esc(t)}: {pct(share, 1)} of pull requests over 400 lines</title></circle>')
        g.append(f'<text x="{xd(share) + 6:.1f}" y="{y + 3.5:.1f}" class="lab">{pct(share)}</text>')
    g.append(f'<line x1="{left}" x2="{mid}" y1="{b + 2}" y2="{b + 2}" class="axis"/><line x1="{d0}" x2="{d1}" y1="{b + 2}" y2="{b + 2}" class="axis"/>')
    for v, lab in ((10, "10"), (100, "100"), (400, "400"), (5000, "5,000")):
        g.append(f'<text x="{xs(v):.1f}" y="{b + 16}" class="tick" text-anchor="middle">{lab}</text>')
    for v in (0, 0.2):
        g.append(f'<text x="{xd(v):.1f}" y="{b + 16}" class="tick" text-anchor="middle">{pct(v)}</text>')
    g.append("</svg>")
    return "".join(g), out


def review_svg(W_=400, H=290, room=8):
    """one dot per engineer: pull requests authored against reviews given; names only where they do not collide"""
    xhi = 50 * math.ceil(max(p["merged"] for p in PEOPLE) / 50)
    yhi = 50 * math.ceil(max(p["reviews"] for p in PEOPLE) / 50)
    pr, top, b = W_ - room, 14, H - 40
    xs = lambda v: pr * v / xhi
    ys = lambda v: top + (b - top) * (yhi - v) / yhi
    g = [f'<svg viewBox="0 0 {W_} {H}" role="img" aria-label="Pull requests authored against reviews given, one dot per engineer">']
    for v in (0, 100, 200):
        g.append(f'<text x="-7" y="{ys(v) + 3.5:.1f}" class="tick" text-anchor="end">{v}</text>')
    for v in range(0, xhi + 1, 50):
        g.append(f'<text x="{xs(v):.1f}" y="{b + 16}" class="tick" text-anchor="middle">{v}</text>')
    g.append(f'<line x1="0" x2="{pr}" y1="{b + 4}" y2="{b + 4}" class="axis"/><line x1="-4" x2="-4" y1="{top}" y2="{b}" class="axis"/>')
    g.append(f'<text x="{pr}" y="{b + 32}" class="tick" text-anchor="end">pull requests authored, April to October</text>')
    g.append(f'<text x="0" y="{top - 4}" class="tick">reviews given</text>')
    top2 = {p["person"] for p in sorted(PEOPLE, key=lambda p: -p["reviews"])[:2]}
    pts = [(xs(p["merged"]), ys(p["reviews"])) for p in PEOPLE]
    boxes = [(x - 7, y - 4, x + 7, y + 4) for x, y in pts] + [(-40, top - 14, 60, top), (150, b + 22, pr, b + 36)]
    hit = lambda a: any(a[0] < c[2] and c[0] < a[2] and a[1] < c[3] and c[1] < a[3] for c in boxes)
    for p in sorted(PEOPLE, key=lambda p: (p["person"] not in top2, -p["reviews"])):
        x, y = xs(p["merged"]), ys(p["reviews"])
        acc = p["person"] in top2
        g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" class="dot{" acc" if acc else ""}"><title>{esc(p["person"])}, {esc(p["team"])}: '
                 f'{p["merged"]} pull requests, {p["reviews"]} reviews</title></circle>')
        w = len(p["person"]) * 5.6 + 2
        own = (x - 4, y - 4, x + 4, y + 4)
        boxes.remove((x - 7, y - 4, x + 7, y + 4))
        boxes.append(own)
        tries = [(x + 5, y + 3.5, "start", (x + 4, y - 5, x + 5 + w, y + 5)), (x - 5, y + 3.5, "end", (x - 5 - w, y - 5, x - 4, y + 5)),
                 (x, y - 6, "middle", (x - w / 2, y - 15, x + w / 2, y - 4)), (x, y + 13, "middle", (x - w / 2, y + 4, x + w / 2, y + 15))]
        for tx, ty, anchor, box in tries:
            if box[0] >= -2 and box[2] <= W_ and box[3] <= b + 2 and (acc or not hit(box)):
                boxes.append(box)
                g.append(f'<text x="{tx:.1f}" y="{ty:.1f}" class="lab{" acc" if acc else ""}" text-anchor="{anchor}">{esc(p["person"])}</text>')
                break
    g.append("</svg>")
    return "".join(g)


stages, _ = stages_svg()
sizes, size_of = size_svg()
md_dash = [p for p in PRS if p["team"] == "Merchant dashboard"]
train_wait = med([p["deploy_wait"] for p in md_dash if p["merged"].date() < TRAIN_END])
cont_wait = med([p["deploy_wait"] for p in md_dash if p["merged"].date() >= TRAIN_END])
all_sep = [p for p in PRS if f"{p['merged']:%Y-%m}" == "2026-09"]
org = {k: med([p[k] for p in all_sep]) for k, _ in STAGES}
wait = {(t, m): med([p["pickup"] for p in month(t, m)]) for t in TEAM for m in ("2026-06", "2026-07", "2026-09")}
others_sep = med([p["pickup"] for p in all_sep if p["team"] != RISK])
rev = sorted(PEOPLE, key=lambda p: -p["reviews"])
total_rev = sum(p["reviews"] for p in PEOPLE)
top5_share = sum(p["reviews"] for p in rev[:5]) / total_rev
bot5_share = sum(p["reviews"] for p in rev[-5:]) / total_rev
med_rev = med([p["reviews"] for p in PEOPLE])
big = {t: size_of[t][1] for t in TEAM}

lede = (f"In September a merged pull request spent a median {hours(org['coding'])} being written before it was opened, "
        f"{hours(org['pickup'])} waiting for its first review, {hours(org['review'])} in review and {hours(org['deploy_wait'])} between merge and production. "
        f"Risk and disputes lost a reviewer on {day(LEAVER_DAY)}: its median wait for a first review went from {hours(wait[(RISK, '2026-06')])} in June "
        f"to {hours(wait[(RISK, '2026-09')])} in September, while the other three teams waited {hours(others_sep)}. "
        f"Of {num(total_rev)} reviews, {rev[0]['person']} gave {rev[0]['reviews']} and {rev[1]['person']} {rev[1]['reviews']}; the median engineer gave {med_rev:.0f}.")

ptab = [("", [p["person"], esc(p["team"]), str(p["merged"]), str(p["reviews"])]) for p in rev]
head = ["Team", "Pull requests merged, April to October", "Median size, lines", "Median wait for a first review, July", "September",
        "Over 400 lines"]
rows = [("", [t, num(sum(1 for p in PRS if p["team"] == t)), f"{size_of[t][0]:.0f}", hours(wait[(t, "2026-07")]), hours(wait[(t, "2026-09")]),
              pct(big[t])]) for t in TEAM]

html = page(
    "Pull request flow", f"{NAME}, an invented team of 22 · 13 April to 15 October 2026 · every figure is made up", lede,
    [section("Where the time goes",
             para("A median is a single number per stage, so each is one bar from zero on one scale for every team; the value is printed at the "
                  "end of the bar instead of on an axis. Each stage has its own median, so the four do not add up to the median pull request."),
             row(fig("Median hours per stage, pull requests merged in September", stages,
                     f"Risk and disputes, in red, waits longest for a first review. Merchant dashboard deployed on a weekly release train until "
                     f"{day(TRAIN_END)}: a merged change then waited a median {hours(train_wait)} for production, against {hours(cont_wait)} "
                     f"since every merge deploys on its own.", 400), cols=1, colw=420)),
     section("Waiting for a first review, by week",
             para(f"A week's waits are a distribution, so each week is a quartile plot: the line runs from the first to the third quartile of "
                  f"the pull requests merged that week, broken around the median dot. One scale for all four teams; the week of "
                  f"{day(CUR_WEEK)} has {CUR_DAYS} of 5 working days and is drawn hollow."),
             row(*[fig(t, pickup_svg(t), width=300) for t in TEAM], cols=2, colw=320)),
     section("Pull request size",
             para("One quartile plot per team, Tufte's redesign of the box plot: grey lines from the smallest pull request to the first quartile "
                  "and from the third quartile to the largest, the middle half in black, offset, broken by the median dot. Size spans three "
                  "orders of magnitude, so the scale is logarithmic. The share over 400 lines is a ratio, so it is a dot."),
             row(fig("Lines changed per pull request, April to October", sizes,
                     f"The dashed line marks 400 lines. Payments core opens the largest pull requests: {pct(big['Payments core'])} are over "
                     f"400 lines, against {pct(big['Platform'])} at Platform.", 400), cols=1, colw=420)),
     section("Review load",
             para(f"One dot per engineer: pull requests authored across, reviews given up. Names are printed wherever they fit; "
                  f"hover any dot for the rest."),
             row(fig("Pull requests authored and reviews given, per engineer", review_svg(),
                     f"Across the whole team reviews are spread fairly evenly: {rev[0]['person']} and {rev[1]['person']}, in red, gave {rev[0]['reviews']} and "
                     f"{rev[1]['reviews']} reviews against the median engineer's {med_rev:.0f}; the top five gave {pct(top5_share)} of all reviews, "
                     f"the bottom five {pct(bot5_share)}. The team table shows each team's busiest reviewer. {LEAVER} left on {day(LEAVER_DAY)}.", 400), cols=1, colw=420),
             table(["Engineer", "Team", "Pull requests authored", "Reviews given"], ptab, num=(2, 3))),
     section("By team", table(head, rows, num=range(1, 6), hide=(1, 2)))],
    "Sources: none. Acme Payments and its engineers do not exist; every pull request and review comes from a seeded generator in the tufte "
    "repository (examples/engineering/data.py), drawn with the tufte skill's rules: a bar from zero for a single number per stage, a quartile "
    "plot for a distribution per week or per team, a dot for a ratio, one dot per engineer, labels on the marks instead of a legend, the "
    "partial week hollow.")
out = HERE / "out" / "pull-request-flow.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html.replace(" %", " %"))
print(out)
