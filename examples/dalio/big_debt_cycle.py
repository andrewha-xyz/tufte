# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.8", "numpy", "pandas"]
# ///
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "skills", "tufte", "scripts"))
import matplotlib.pyplot as plt
import pandas as pd
import tufte_mpl as t

t.use()
T = pd.Timestamp


def fred(s):
    df = pd.read_csv(f"{HERE}/data/{s}.csv", na_values=".")
    df.columns = ["date", s]
    return df.assign(date=pd.to_datetime(df.date)).set_index("date")[s]


debt, gdp = fred("TCMDO") / 1000, fred("GDP")          # both billions
ratio = (debt / gdp * 100).dropna()
rate = fred("TB3MS")
fed_gdp = ((fred("WALCL") / 1000).resample("QS").mean() / gdp * 100).dropna()
unemp = fred("UNRATE")
at = lambda s, when: s.asof(T(when))

decades = pd.to_datetime([f"{yr}-01-01" for yr in range(1950, 2030, 10)])
span = (T("1946-01-01"), T("2027-01-01"))
fig, axs = plt.subplots(4, 1, figsize=(10, 7.5), sharex=True, layout="constrained",
                        height_ratios=[3, 1.3, 1.3, 1.3])
a, b, c, d = axs

top_date = ratio["2008":"2010"].idxmax()
a.plot(ratio, color=t.INK)
t.frame(a, decades, [100, 200, 300, 400], xlim=span, ylim=(100, 445), xlabels=[str(x.year) for x in decades], span=(ratio.index[0], ratio.index[-1]))
a.set_ylabel("debt, % of GDP")
t.note(a, T("2005-01-01"), at(ratio, "2005-01-01"), "bubble: debt rising faster than income, 2003 to 2007", side="left")
t.note(a, top_date, ratio[top_date], f"top, {top_date.to_period('Q')}: {ratio[top_date]:.0f}%", side="left", dy=8)
t.note(a, T("2020-04-01"), at(ratio, "2020-04-01"), "2020: GDP fell, debt jumped, then the ratio came back down", side="left", dy=9)
t.callout(a, T("2013-01-01"), at(ratio, "2013-01-01"),
          "beautiful deleveraging: the ratio stays flat for a decade\nwhile rates sit at zero and the Fed prints",
          at=(T("1988-01-01"), 185))

b.plot(rate, color=t.INK, lw=0.8)
t.frame(b, decades, [0, 5, 10, 15], ylim=(0, 17), span=(rate.index[0], rate.index[-1]))
b.set_ylabel("3-month rate, %")
t.note(b, T("1981-05-01"), at(rate, "1981-05-01"), "%.0f%% in 1981" % at(rate, "1981-05-01"), dy=4)
words = (T("1997-01-01"), 12.5)
t.callout(b, T("2011-01-01"), at(rate, "2011-01-01"),
          "zero from 2009 to 2015 and again in 2020 to 2021:\npushing on a string", at=words)
t.callout(b, T("2020-10-01"), at(rate, "2020-10-01"), "", at=(T("2011-06-01"), 10.3))

c.plot(fed_gdp, color=t.INK, lw=0.8)
t.frame(c, decades, [0, 20, 40], ylim=(0, 40), span=(fed_gdp.index[0], fed_gdp.index[-1]))
c.set_ylabel("Fed assets, % of GDP")
t.note(c, T("2007-07-01"), at(fed_gdp, "2007-07-01"), "%.0f%% before the top" % at(fed_gdp, "2007-07-01"), side="left", dy=6)
t.note(c, T("2014-10-01"), at(fed_gdp, "2014-10-01"), "after QE1 to QE3: %.0f%%" % at(fed_gdp, "2014-10-01"), side="left", dy=6)
t.note(c, T("2021-10-01"), at(fed_gdp, "2021-10-01"), "2021: %.0f%%" % at(fed_gdp, "2021-10-01"), dy=5)
c.text(T("1950-01-01"), 20, "weekly series begins in 2002", fontsize=8, color=t.GREY, va="center")

d.plot(unemp, color=t.INK, lw=0.8)
t.frame(d, decades, [0, 5, 10, 15], ylim=(0, 16), span=(unemp.index[0], unemp.index[-1]))
d.set_ylabel("unemployment, %")
t.note(d, T("2009-10-01"), at(unemp, "2009-10-01"), "%.1f%% in October 2009" % at(unemp, "2009-10-01"), side="left", dy=6)
t.note(d, T("2020-04-01"), at(unemp, "2020-04-01"), "%.1f%% in April 2020" % at(unemp, "2020-04-01"), dy=5)

fed_mult = at(fed_gdp, "2014-10-01") / at(fed_gdp, "2007-07-01")
t.headline(fig, f"US debt rose from {ratio.iloc[0]:.0f}% of GDP in {ratio.index[0].year} to {ratio[top_date]:.0f}% at the "
                f"2009 top and stands at {ratio.iloc[-1]:.0f}% in {ratio.index[-1].year}. The top was followed by seven "
                f"years at zero rates, Fed assets up {fed_mult:.0f}-fold relative to GDP, and 10% unemployment: Dalio's deleveraging, "
                f"in the data.")
t.source(fig, "Sources: FRED, fetched 2026-10-17. Debt = all sectors, debt securities and loans (TCMDO), quarterly, divided by "
              "nominal GDP at a seasonally adjusted annual rate; 3-month Treasury bill (TB3MS), monthly; Fed total assets (WALCL), "
              "weekly, averaged to quarters; unemployment (UNRATE), monthly. The 1929 to 1945 cycle is not shown: no comparable "
              "public series. Phase names follow Dalio, Principles for Navigating Big Debt Crises (2018).")
out = os.path.abspath("big-debt-cycle.rendered.png")   # written to the working directory
fig.savefig(out)
print(out)
