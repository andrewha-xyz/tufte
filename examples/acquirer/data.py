"""Acme Payments, an invented merchant acquirer. Every number on every page comes from this file and nothing else.
Months run October 2025 to October 2026; October is the 1st to the 15th."""
import calendar
import datetime as dt
import math
import random

R = random.Random(20261018)
NAME = "Acme Payments"
ASOF = dt.date(2026, 10, 15)
MONTHS = [f"{2025 + (9 + i) // 12}-{(9 + i) % 12 + 1:02d}" for i in range(13)]
CUR = MONTHS[-1]
DAYS, MDAYS = 15, 31

ACTIVE = [1240, 1290, 1350, 1410, 1460, 1540, 1720, 1830, 1920, 2040, 2170, 2310, 2280]
NEW = [72, 80, 88, 79, 84, 115, 228, 160, 151, 174, 186, 204, 96]
SEASON = {"2025-11": 1.03, "2025-12": 1.09, "2026-01": 0.93, "2026-02": 0.95, "2026-07": 1.02, "2026-08": 1.01}

STREAMS = ["Merchant fee margin", "FX markup", "Terminal rental", "Instant payouts", "Chargeback fees"]


def _lin(a, b, i, n=12):
    return a + (b - a) * i / n


def _month(i, m):
    full = MDAYS if m == CUR else calendar.monthrange(int(m[:4]), int(m[5:]))[1]
    days = DAYS if m == CUR else full
    share = days / full
    per = (38_400 + 520 * i) * SEASON.get(m, 1.0) * (1 + R.gauss(0, 0.012))
    tpv = ACTIVE[i] * per * share
    ticket = _lin(37.2, 40.6, i) * (1 + R.gauss(0, 0.01))
    txns = tpv / ticket
    msc = _lin(0.0194, 0.0179, i) + R.gauss(0, 0.0002)
    ic = _lin(0.01132, 0.01081, i) + R.gauss(0, 0.00008)
    scheme = 0.00152 + R.gauss(0, 0.00003)
    xb = _lin(0.161, 0.221, i) + R.gauss(0, 0.004)
    terminals = round(ACTIVE[i] * _lin(0.66, 0.58, i))
    payout_share = 0.0 if m < "2026-06" else min(0.16, 0.035 + 0.032 * (i - 8)) * (1 + R.gauss(0, 0.05))
    cb_bps = _lin(31, 23, i) + R.gauss(0, 0.8)
    approval = _lin(0.921, 0.943, i) + R.gauss(0, 0.0015)
    streams = {
        "Merchant fee margin": tpv * (msc - ic - scheme),
        "FX markup": tpv * xb * 0.0085,
        "Terminal rental": terminals * 11.0 * share,
        "Instant payouts": tpv * payout_share * 0.0025,
        "Chargeback fees": txns * cb_bps / 10_000 * 15.0,
    }
    rev = sum(streams.values())
    cost = {
        "Processing": txns * 0.011,
        "Risk losses": tpv * 0.00018,
        "Support": ACTIVE[i] * 9.0 * share,
        "Onboarding checks": NEW[i] * 34.0,
        "Platform": _lin(330_000, 420_000, i) * share,
        "Partner commissions": tpv * 0.00045,
    }
    return dict(month=m, days=days, month_days=full, partial=m == CUR, active=ACTIVE[i], new=NEW[i], attempts=txns / approval,
                lost=(ACTIVE[i - 1] + NEW[i] - ACTIVE[i]) if i and m != CUR else None,
                tpv=tpv, txns=txns, ticket=ticket, msc=msc, ic=ic, scheme=scheme, xb=xb, terminals=terminals,
                payout_share=payout_share, cb_bps=cb_bps, approval=approval, streams=streams, rev=rev,
                cost=cost, contrib=rev - sum(cost.values()), take=rev / tpv)


MONTHLY = [_month(i, m) for i, m in enumerate(MONTHS)]
BY = {r["month"]: r for r in MONTHLY}


def pace(key):
    r = BY[CUR]
    v = r[key] if key in r else r["streams"][key]
    return v * MDAYS / DAYS


def daily():
    out, wd = [], [0.94, 1.0, 1.02, 1.04, 1.13, 1.09, 0.78]
    for r in MONTHLY:
        y, mo = int(r["month"][:4]), int(r["month"][5:])
        ds = [dt.date(y, mo, d) for d in range(1, r["days"] + 1)]
        w = [wd[d.weekday()] * (1 + R.gauss(0, 0.05)) for d in ds]
        s = sum(w)
        for d, x in zip(ds, w):
            f = x / s
            out.append(dict(day=d, tpv=r["tpv"] * f, txns=r["txns"] * f, rev=r["rev"] * f,
                            attempts=r["txns"] * f / (r["approval"] + R.gauss(0, 0.002)), streams={k: v * f for k, v in r["streams"].items()}))
    for r in MONTHLY:
        r["attempts"] = sum(d["attempts"] for d in out if f"{d['day']:%Y-%m}" == r["month"])
        r["approval"] = r["txns"] / r["attempts"]
    return out


DAILY = daily()


def weekly(start=dt.date(2026, 4, 13)):
    weeks = {}
    for d in DAILY:
        if d["day"] < start:
            continue
        w = d["day"] - dt.timedelta(days=d["day"].weekday())
        x = weeks.setdefault(w, dict(week=w, days=0, tpv=0.0, txns=0.0, rev=0.0, attempts=0.0, streams={k: 0.0 for k in STREAMS}))
        x["days"] += 1
        x["tpv"] += d["tpv"]
        x["txns"] += d["txns"]
        x["rev"] += d["rev"]
        x["attempts"] += d["attempts"]
        for k, v in d["streams"].items():
            x["streams"][k] += v
    out = []
    for w in sorted(weeks):
        x = weeks[w]
        x["approval"] = x["txns"] / x["attempts"]
        x["partial"] = x["days"] < 7
        x["active"] = round(BY[f"{w:%Y-%m}"]["active"] * 0.84 * (1 + R.gauss(0, 0.015)) * (x["days"] / 7) ** 0.35)
        out.append(x)
    return out


WEEKLY = weekly()

PLAN = {"2026-07": dict(rev=760_000, tpv=88_000_000, active=2020), "2026-08": dict(rev=815_000, tpv=94_500_000, active=2160),
        "2026-09": dict(rev=890_000, tpv=101_000_000, active=2330), "2026-10": dict(rev=960_000, tpv=108_000_000, active=2500),
        "2026-11": dict(rev=1_030_000, tpv=115_000_000, active=2660), "2026-12": dict(rev=1_120_000, tpv=125_000_000, active=2840)}
STRETCH = {"2026-10": dict(rev=1_010_000, active=2600), "2026-11": dict(rev=1_120_000, active=2850), "2026-12": dict(rev=1_260_000, active=3150)}


def forecast():
    """the model made in May: fitted to actuals through April, then 285 new merchants in May rising by 25 a month, 97.5 % kept"""
    out, act = [], None
    for i in range(27):
        y, mo = 2025 + (9 + i) // 12, (9 + i) % 12 + 1
        m = f"{y}-{mo:02d}"
        if m <= "2026-04":
            r = BY[m]
            out.append(dict(month=m, active=r["active"], new=r["new"], rev=round(r["rev"]), tpv=round(r["tpv"]), fitted=True))
            act = r["active"]
            continue
        k = i - MONTHS.index("2026-04")
        new = 260 + 25 * k
        act = round(act * 0.975 + new)
        out.append(dict(month=m, active=act, new=new, rev=round(act * (372 + 4 * k)), tpv=round(act * (41_000 + 600 * k)), fitted=False))
    return out


FORECAST = forecast()

SEGMENTS = [dict(segment="Under $10k a month", merchants=0.46, tpv=0.07, retention=0.952, rev_per=47.0),
            dict(segment="$10k to $50k", merchants=0.33, tpv=0.21, retention=0.974, rev_per=228.0),
            dict(segment="$50k to $250k", merchants=0.17, tpv=0.38, retention=0.986, rev_per=874.0),
            dict(segment="$250k and above", merchants=0.04, tpv=0.34, retention=0.995, rev_per=3_380.0)]

def channels(month="2026-09"):
    """September's new merchants (first payment that month) split by channel; signed = activated / activation; cost per signed merchant = budget / signed"""
    spec = [("Direct sales", 60_000, 0.82, 0.16), ("ISO partners", 40_000, 0.74, 0.27), ("Platform plug-ins", 15_000, 0.48, 0.22),
            ("Referrals", 10_000, 0.66, 0.14), ("Paid search", 25_000, 0.41, 0.21)]
    total = BY[month]["new"]
    act = [round(total * sh) for *_, sh in spec]
    act[1] += total - sum(act)
    out = []
    for (name, budget, activation, _), a in zip(spec, act):
        signed = round(a / activation)
        out.append(dict(channel=name, month=month, budget=budget, activation=activation, activated=a, signed=signed, cac=round(budget / signed)))
    return out


CHANNELS = channels()
VALUE_MARGIN = BY["2026-09"]["contrib"] / BY["2026-09"]["rev"]


def cohorts():
    out = []
    for m in MONTHS[3:12]:
        i = MONTHS.index(m)
        lift = 0.004 * (i - 3)
        row, cur = [1.0], 1.0
        for k in range(1, 12 - i):
            cur *= (0.86 + lift if k == 1 else 0.955 + lift / 2) + R.gauss(0, 0.006)
            row.append(round(min(cur, 1.0), 3))
        out.append(dict(month=m, size=NEW[i], retention=row))
    return out


COHORTS = cohorts()


def sensitivity(news=(150, 200, 250, 300, 350, 400), rets=(0.95, 0.96, 0.97, 0.975, 0.98, 0.985)):
    base = BY["2026-09"]["active"]
    return [dict(new=n, values=[round(base * r ** 3 + n * (1 + r + r * r)) for r in rets]) for n in news], list(rets)


_Q4 = sum(PLAN[m]["rev"] for m in ("2026-10", "2026-11", "2026-12"))
_SEP = BY["2026-09"]
_Q4_LOW = pace("rev") * 3
_DEC_LOW = _SEP["active"] * (_SEP["active"] / BY["2026-06"]["active"])
_st = lambda ok, near: "on" if ok else ("risk" if near else "off")
OBJECTIVES = [dict(title="Net revenue, fourth quarter", target=f"${_Q4 / 1e6:.2f}M", now=f"${_Q4_LOW / 1e6:.2f}M at the October pace",
                   status=_st(_Q4_LOW >= _Q4, _Q4_LOW >= 0.85 * _Q4)),
              dict(title="Active merchants in December", target=f"{PLAN['2026-12']['active']:,}", now=f"{_SEP['active']:,} in September",
                   status=_st(_DEC_LOW >= PLAN["2026-12"]["active"], _DEC_LOW >= 0.9 * PLAN["2026-12"]["active"])),
              dict(title="Approval rate", target="94.0 % or better", now=f"{_SEP['approval'] * 100:.1f} % in September",
                   status=_st(_SEP["approval"] >= 0.94, _SEP["approval"] >= 0.935)),
              dict(title="Chargebacks", target="25 per 10,000 or fewer", now=f"{_SEP['cb_bps']:.0f} in September",
                   status=_st(_SEP["cb_bps"] <= 25, _SEP["cb_bps"] <= 27)),
              dict(title="Days from application to first payment", target="2", now="3.4 median in September", status=_st(3.4 <= 2, 3.4 <= 2.5)),
              dict(title="Instant payouts share of volume", target="15 %", now=f"{_SEP['payout_share'] * 100:.0f} % in September",
                   status=_st(_SEP["payout_share"] >= 0.15, _SEP["payout_share"] >= 0.11))]

if __name__ == "__main__":
    for r in MONTHLY:
        print(r["month"], f"active {r['active']:>5} tpv {r['tpv'] / 1e6:6.1f}M rev {r['rev'] / 1e3:6.0f}k take {r['take'] * 1e4:5.1f}bps "
              f"approval {r['approval'] * 100:4.1f} cb {r['cb_bps']:4.1f} contrib {r['contrib'] / 1e3:6.0f}k")
    print(len(WEEKLY), "weeks", WEEKLY[-1]["week"], WEEKLY[-1]["days"], "days")
    print([(f["month"], f["active"], f["rev"]) for f in FORECAST if f["month"] >= "2026-07"][:8])
