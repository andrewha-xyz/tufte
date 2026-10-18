import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.append(str(HERE.parent / "acquirer"))
from data import CUR_DAYS, CUR_WEEK, LEAVER, LEAVER_DAY, NAME, PEOPLE, PRS, TEAMS, WEEKS, week  # noqa: E402
from kit import num, page, para, pct, section, table  # noqa: E402

day = lambda d: f"{d:%b} {d.day}"
gone = WEEKS.index(week(LEAVER_DAY))


def spk(vals, top, w=104, h=18):
    slot, bw = w / len(vals), max(1.0, w / len(vals) - 1.2)
    y = lambda v: h - ((h - 1) * v / top if v else 0)
    g = [f'<svg class="spark" viewBox="0 0 {w} {h}" width="{w}" height="{h}" aria-hidden="true">']
    for i, v in enumerate(vals):
        if v is None:
            continue
        x = i * slot
        if i == len(vals) - 1 and not v:
            g.append(f'<line x1="{x:.1f}" x2="{x + bw:.1f}" y1="{h - 0.6:.1f}" y2="{h - 0.6:.1f}" style="stroke:var(--acc);stroke-width:1.2"/>')
            continue
        if i == len(vals) - 1:
            g.append(f'<rect x="{x + 0.4:.1f}" y="{y(v):.1f}" width="{bw - 0.8:.1f}" height="{h - y(v):.1f}" '
                     f'style="fill:var(--paper);stroke:var(--acc);stroke-width:.8"/>')
            continue
        g.append(f'<rect x="{x:.1f}" y="{y(v):.1f}" width="{bw:.1f}" height="{h - y(v):.1f}" class="s"/>')
    g.append("</svg>")
    return "".join(g)


def cut(p, key):
    vals = list(p[key])
    return vals[:gone] + [None] * (len(vals) - gone) if p["left"] else vals


top_m = max(max(p["merged_weekly"]) for p in PEOPLE)
top_r = max(max(p["reviews_weekly"]) for p in PEOPLE)
rows, groups = [], []
for t in TEAMS:
    rows.append(("gap", [f"<i>{t}</i>", "", "", "", "", "", ""]))
    groups.append(t)
    for p in sorted((p for p in PEOPLE if p["team"] == t), key=lambda p: p["person"]):
        who = p["person"] + (f' <span class="dim">left {day(p["left"])}</span>' if p["left"] else "")
        rows.append(("", [who, spk(cut(p, "merged_weekly"), top_m), spk(cut(p, "reviews_weekly"), top_r), num(p["merged"]),
                          num(p["reviews"]), f"{p['median_size']:.0f}", f"{p['median_cycle']:.1f}"]))

team_rows, busiest = [], {}
for t, d in TEAMS.items():
    ps = [p for p in PEOPLE if p["team"] == t]
    total = sum(p["reviews"] for p in ps)
    top = max(ps, key=lambda p: p["reviews"])
    busiest[t] = (top["person"], top["reviews"] / total)
    team_rows.append(("", [t, str(len(ps)), num(sum(p["merged"] for p in ps)), num(total), top["person"], pct(top["reviews"] / total),
                           pct(1 / len(ps))]))

risk = [x for x in PRS if x["team"] == "Risk and disputes"]
wait_before = statistics.median([x["pickup"] for x in risk if f"{x['merged']:%Y-%m}" == "2026-06"])
wait_after = statistics.median([x["pickup"] for x in risk if f"{x['merged']:%Y-%m}" == "2026-09"])
hi_t = max(busiest, key=lambda t: busiest[t][1])
lo_t = min(busiest, key=lambda t: busiest[t][1])
merged_all, reviews_all = sum(p["merged"] for p in PEOPLE), sum(p["reviews"] for p in PEOPLE)

lede = (f"Twenty-two engineers merged {num(merged_all)} pull requests between April 13 and October 15 and gave {num(reviews_all)} reviews. "
        f"Within each team the busiest reviewer gave more than an even share, from {pct(busiest[lo_t][1])} of their team's reviews "
        f"({busiest[lo_t][0]}, {lo_t}) to {pct(busiest[hi_t][1])} ({busiest[hi_t][0]}, {hi_t}). After {LEAVER} left on {day(LEAVER_DAY)}, "
        f"Risk and disputes' median wait for a first review went from {wait_before:.1f} h in June to {wait_after:.1f} h in September.")

head = ["", "Merged a week", "Reviews given a week", "Merged, April to October", "Reviews given", "Median size, lines",
        "Median hours, opened to merged"]
reading = (f"One row per engineer, grouped by team and sorted by name. Each sparkline is 27 weeks of counts as bars from zero, April 13 at the "
           f"left; every row in a column shares one scale, so the tallest merged bar is {top_m} pull requests and the tallest review bar "
           f"{top_r} reviews. The week of {day(CUR_WEEK)} has {CUR_DAYS} of 5 working days and is drawn open in red. {LEAVER}'s bars stop "
           f"the week of {day(LEAVER_DAY)}.")
advice = ("The table shows how pull requests and review load are spread across people. A pattern such as one person giving most of a "
          "team's reviews, or a team's wait for a first review growing after someone leaves, is a prompt for a conversation with that team, "
          "not a ranking. Counts of pull requests are not a measure of performance, and the columns are deliberately not sortable or scored.")

html = page(
    "The team in one table", f"{NAME}, an invented team of 22 · 13 April to 15 October 2026 · every figure is made up", lede,
    [section("Twenty-two engineers, 27 weeks", para(reading),
             table(head, rows, num=range(3, 7), hide=(2, 5, 6), cls="sl")),
     section("How to read it", para(advice)),
     section("By team",
             table(["Team", "Engineers", "Merged", "Reviews given", "Busiest reviewer", "Their share of the team's reviews", "Even split"],
                   team_rows, num=(1, 2, 3, 5, 6), hide=(1, 6)))],
    "Sources: none. Acme Payments and its engineers do not exist; every pull request and review comes from a seeded generator in the "
    "tufte repository (examples/engineering/data.py), set with the tufte skill's rules for a sparkline table: word-sized graphics beside "
    "their numbers, bars from zero for counts per week, one scale per column, the partial week drawn open.",
    desc="A sparkline table of an invented engineering organisation: merges and reviews per engineer per week.")
for t in groups:
    html = html.replace(f'<tr class="gap"><th><i>{t}</i></th>' + "<td></td>" + '<td class="m-hide"></td>' + '<td class="n"></td>' * 2
                        + '<td class="n m-hide"></td>' * 2 + "</tr>", f'<tr class="gap"><th colspan="7"><i>{t}</i></th></tr>')
html = html.replace("</style>", ".dim{color:var(--grey)}.sl td:nth-child(2),.sl td:nth-child(3){padding-right:20px}"
                                ".sl tr.gap th{color:var(--grey);white-space:nowrap}.sl thead th.n{width:6.5em}"
                                "@media (max-width:700px){.sl td:nth-child(2){padding-right:8px}.spark{width:78px;height:auto}}</style>")
out = HERE / "out" / "team-table.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html.replace(" %", " %"))
print(out)
