"""Acme Payments engineering, invented: four teams, 22 engineers named after the NATO alphabet, 13 April to 15 October 2026.
Every pull request, deploy and incident is generated here; nothing is real. Two stories are built in: Merchant dashboard leaves
its weekly release train for continuous deploys on 3 August, and Risk and disputes loses a reviewer on 6 July, so its pull
requests wait longer for a first review."""
import datetime as dt
import math
import random
import statistics

R = random.Random(20261018)
NAME = "Acme Payments engineering"
START, END = dt.date(2026, 4, 13), dt.date(2026, 10, 15)
TRAIN_END, LEAVER_DAY, ROLLBACK_DAY = dt.date(2026, 8, 3), dt.date(2026, 7, 6), dt.date(2026, 7, 20)

TEAMS = {
    "Payments core": dict(people=["Alfa", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot"], size=180, fail=0.045),
    "Risk and disputes": dict(people=["Golf", "Hotel", "India", "Juliett", "Kilo"], size=140, fail=0.035),
    "Merchant dashboard": dict(people=["Lima", "Mike", "November", "Oscar", "Papa", "Quebec"], size=120, fail=0.06),
    "Platform": dict(people=["Romeo", "Sierra", "Uniform", "Victor", "Whiskey"], size=90, fail=0.03),
}
LEAVER = "Kilo"
TEAM_OF = {p: t for t, d in TEAMS.items() for p in d["people"]}
RATE = {p: R.uniform(2.0, 5.5) for p in TEAM_OF}
RATE.update(Alfa=6.2, Romeo=6.8, India=2.4)
REVIEW_WEIGHT = {p: R.uniform(0.6, 1.6) for p in TEAM_OF}
REVIEW_WEIGHT.update(Golf=2.6, Charlie=2.2)


def _hours(median, spread):
    return median * math.exp(R.gauss(0, spread))


def _workday(d):
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


def _at(day, hours):
    return dt.datetime.combine(day, dt.time(9)) + dt.timedelta(hours=hours)


def _poisson(lam):
    k, t = 0, math.exp(-lam)
    p = R.random()
    while p > t:
        k += 1
        p *= R.random()
    return k


def _prs():
    out, n = [], 0
    d = START
    while d <= END:
        if d.weekday() < 5:
            for p, t in TEAM_OF.items():
                if p == LEAVER and d >= LEAVER_DAY:
                    continue
                for _ in range(_poisson(RATE[p] / 5)):
                    n += 1
                    team = TEAMS[t]
                    size = max(4, round(team["size"] * math.exp(R.gauss(0, 0.9))))
                    coding = _hours(10, 0.8)
                    mates = [q for q in team["people"] if q != p and not (q == LEAVER and d >= LEAVER_DAY)]
                    load = 1.0 + (0.9 if t == "Risk and disputes" and d >= LEAVER_DAY else 0.0)
                    pickup = _hours(3.5 * load, 0.7)
                    review = _hours(2.0 + size / 90, 0.6)
                    opened = _at(d, R.uniform(0, 8))
                    first_commit = opened - dt.timedelta(hours=coding)
                    first_review = opened + dt.timedelta(hours=pickup)
                    merged = first_review + dt.timedelta(hours=review)
                    reviewers = R.choices(mates, weights=[REVIEW_WEIGHT[q] for q in mates], k=1 if size < 150 else 2)
                    if t == "Merchant dashboard" and merged.date() < TRAIN_END:
                        rel = _workday(merged.date() + dt.timedelta(days=(3 - merged.weekday()) % 7 or 7))
                        deployed = _at(rel, 6)
                    else:
                        deployed = merged + dt.timedelta(hours=_hours(0.8 if t == "Platform" else 1.6, 0.5))
                    out.append(dict(id=n, team=t, author=p, size=size, train=t == "Merchant dashboard" and merged.date() < TRAIN_END,
                                    shipped=deployed.date() <= END, first_commit=first_commit, opened=opened,
                                    first_review=first_review, merged=merged, deployed=deployed, reviewers=sorted(set(reviewers)),
                                    coding=coding, pickup=pickup, review=review,
                                    deploy_wait=(deployed - merged).total_seconds() / 3600,
                                    lead=(deployed - first_commit).total_seconds() / 3600))
        d += dt.timedelta(days=1)
    return [p for p in out if p["merged"].date() <= END]


PRS = _prs()


def _deploys():
    out = {}
    for p in PRS:
        if not p["shipped"]:
            continue
        key = (p["team"], p["train"], p["deployed"].date() if p["train"] else p["deployed"])
        out.setdefault(key, []).append(p["id"])
    deploys = []
    for (team, train, when), ids in sorted(out.items(), key=lambda kv: (kv[0][0], str(kv[0][2]))):
        day = when if isinstance(when, dt.date) and not isinstance(when, dt.datetime) else when.date()
        batch = len(ids)
        failed = R.random() < 1 - (1 - TEAMS[team]["fail"]) ** min(batch, 6)
        deploys.append(dict(team=team, day=day, prs=batch, train=train, failed=failed))
    return deploys


DEPLOYS = _deploys()


def _incidents():
    out = []
    for dpl in DEPLOYS:
        if not dpl["failed"]:
            continue
        median = 2.4 if dpl["team"] != "Platform" or dpl["day"] < ROLLBACK_DAY else 0.7
        out.append(dict(team=dpl["team"], day=dpl["day"], restore=_hours(median, 0.7)))
    return out


INCIDENTS = _incidents()


def week(d):
    d = d.date() if isinstance(d, dt.datetime) else d
    return d - dt.timedelta(days=d.weekday())


WEEKS = sorted({week(START + dt.timedelta(days=i)) for i in range((END - START).days + 1)})
CUR_WEEK = WEEKS[-1]
CUR_DAYS = (END - CUR_WEEK).days + 1
MONTHS = ["2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]


def quartiles(xs):
    xs = sorted(xs)
    if len(xs) < 4:
        m = statistics.median(xs) if xs else None
        return (m, m, m)
    q = statistics.quantiles(xs, n=4)
    return (q[0], q[1], q[2])


def weekly(team=None):
    rows = []
    for w in WEEKS:
        prs = [p for p in PRS if p["shipped"] and week(p["deployed"]) == w and (team is None or p["team"] == team)]
        dps = [d for d in DEPLOYS if week(d["day"]) == w and (team is None or d["team"] == team)]
        merged = [p for p in PRS if week(p["merged"]) == w and (team is None or p["team"] == team)]
        rows.append(dict(week=w, partial=w == CUR_WEEK, deploys=len(dps), failed=sum(d["failed"] for d in dps),
                         merged=len(merged), lead=quartiles([p["lead"] for p in prs]),
                         pickup=quartiles([p["pickup"] for p in merged])))
    return rows


def monthly(team=None):
    rows = []
    for m in MONTHS:
        dps = [d for d in DEPLOYS if f"{d['day']:%Y-%m}" == m and (team is None or d["team"] == team)]
        inc = [i for i in INCIDENTS if f"{i['day']:%Y-%m}" == m and (team is None or i["team"] == team)]
        rows.append(dict(month=m, partial=m == MONTHS[-1], deploys=len(dps), failed=sum(d["failed"] for d in dps),
                         cfr=(sum(d["failed"] for d in dps) / len(dps)) if dps else None,
                         restore=statistics.median([i["restore"] for i in inc]) if inc else None))
    return rows


def people():
    out = []
    for t, d in TEAMS.items():
        for p in d["people"]:
            mine = [x for x in PRS if x["author"] == p]
            given = [x for x in PRS if p in x["reviewers"]]
            out.append(dict(person=p, team=t, left=LEAVER_DAY if p == LEAVER else None,
                            merged_weekly=[sum(1 for x in mine if week(x["merged"]) == w) for w in WEEKS],
                            reviews_weekly=[sum(1 for x in given if week(x["first_review"]) == w) for w in WEEKS],
                            merged=len(mine), reviews=len(given),
                            median_size=statistics.median([x["size"] for x in mine]) if mine else None,
                            median_cycle=statistics.median([(x["merged"] - x["opened"]).total_seconds() / 3600 for x in mine]) if mine else None))
    return out


PEOPLE = people()

if __name__ == "__main__":
    print(len(PRS), "prs", len(DEPLOYS), "deploys", len(INCIDENTS), "incidents", CUR_WEEK, CUR_DAYS, "days in last week")
    for t in TEAMS:
        w = weekly(t)
        m = monthly(t)
        print(f"{t:<20} deploys/wk {[r['deploys'] for r in w][-8:]} lead med {[round(r['lead'][1] or 0) for r in w][::4]} "
              f"pickup {[round(r['pickup'][1] or 0, 1) for r in w][::4]} cfr {[round(r['cfr'] * 100) if r['cfr'] else None for r in m]} "
              f"restore {[round(r['restore'], 1) if r['restore'] else None for r in m]}")
    for p in PEOPLE[:6]:
        print(p["person"], p["merged"], p["reviews"], p["median_size"], round(p["median_cycle"], 1))
