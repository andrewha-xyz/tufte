# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.8", "numpy", "pandas"]
# ///
import os, sys, textwrap
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "skills", "tufte", "scripts"))
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
import tufte_mpl as t

t.use()
T = pd.Timestamp
X0, X1 = T("1946-01-01"), T("2027-01-01")


def fred(s):
    df = pd.read_csv(f"{HERE}/data/{s}.csv", na_values=".")
    df.columns = ["date", s]
    return df.assign(date=pd.to_datetime(df.date)).set_index("date")[s].dropna()


debt, gdp = fred("TCMDO") / 1000, fred("GDP")
ratio = (debt / gdp * 100).dropna()
rate = fred("TB3MS")["1946":]
fed_gdp = ((fred("WALCL") / 1000).resample("QS").mean() / gdp * 100).dropna()
unemp = fred("UNRATE")
at = lambda s, when: s.asof(T(when))
top_date = ratio["2008":"2010"].idxmax()


def banked_height(s, width, ylim, floor=1.4):
    """Panel height so the median absolute segment slope sits at 45 degrees (Cleveland) on the
    axes as drawn (x over the shared time span, y over this panel's declared limits); flat
    segments excluded; never below the legibility floor."""
    x = (s.index - X0).days / (X1 - X0).days
    y = (s.values - ylim[0]) / (ylim[1] - ylim[0])
    dx, dy = np.diff(x), np.diff(y)
    keep = (dx > 0) & (dy != 0)
    return max(floor, width / np.median(np.abs(dy[keep] / dx[keep])))


# ---- the page: inner before outer (GI inside a block, G between blocks, MARGIN around), one left edge L -----
MARGIN, G, GI = 0.6, 0.32, 0.16   # inches: page margin; the gap between blocks; the gap inside a block, a title to its plot
HANG, RIGHT = 0.55, 0.95       # inches: room for hung y labels on the left, end labels on the right
PW = 8.0                       # plot width, inches
LINE = 9 / 72 * 1.35           # body line height, inches (9 pt type)
HEAD = 11 / 72 * 1.4           # headline line height
TITLE = 10 / 72 * 1.3          # panel title line height
LABELS = 0.22                  # room under the bottom panel for its year labels

panels = [("Debt, all sectors, % of GDP", ratio, [100, 200, 300, 400], (100, 445)),
          ("3-month Treasury rate, %", rate, [0, 5, 10, 15], (0, 17)),
          ("Fed assets, % of GDP", fed_gdp, [0, 20, 40], (0, 40)),
          ("Unemployment, %", unemp, [0, 5, 10, 15], (0, 16))]
heights = [banked_height(s, PW, ylim) for _, s, _, ylim in panels]
ABOVE, BELOW = 0.14, 0.10      # room inside a plot block for a label above the axes and the lowest tick label below

fed_mult = at(fed_gdp, "2014-10-01") / at(fed_gdp, "2007-07-01")
headline = (f"US debt rose from {ratio.iloc[0]:.0f}% of GDP in {ratio.index[0].year} to {ratio[top_date]:.0f}% at the "
            f"2009 top and stands at {ratio.iloc[-1]:.0f}% in {ratio.index[-1].year}. The top was followed by seven "
            f"years at zero rates, Fed assets up {fed_mult:.0f}-fold relative to GDP, and 10% unemployment: Dalio's "
            f"deleveraging, in the data.")
source = ("Sources: FRED, fetched 2026-10-17. Debt = all sectors, debt securities and loans (TCMDO), quarterly, divided by "
          "nominal GDP at a seasonally adjusted annual rate; 3-month Treasury bill (TB3MS), monthly; Fed total assets (WALCL), "
          "weekly, averaged to quarters; unemployment (UNRATE), monthly. Each series is a state that changes gradually at the "
          "resolution shown (quarter-end debt divided by annualized quarterly GDP, a monthly average of a daily rate, a quarterly average of a weekly "
          "balance sheet, a monthly survey rate), so a line between observations is an honest interpolation; each panel's "
          "height banks its median segment slope toward 45 degrees on the axes as drawn, subject to a legibility floor. The 1929 to 1945 cycle is not "
          "shown: no comparable public series. Phase names follow Dalio, Principles for Navigating Big Debt Crises (2018).")
W = MARGIN + HANG + PW + RIGHT + MARGIN
measure = PW + RIGHT                                   # text blocks run from L to the page's right margin
head_lines = textwrap.wrap(headline, int(measure * 72 / (11 * 0.55)))
src_lines = textwrap.wrap(source, int(measure * 72 / (7.5 * 0.55)))
H = (MARGIN + len(head_lines) * HEAD + G + sum(TITLE + GI + ABOVE + h + BELOW + G for h in heights) + LABELS
     + len(src_lines) * LINE * 7.5 / 9 + MARGIN)
fig = plt.figure(figsize=(W, H), dpi=200)
L = MARGIN + HANG
fx, fy = lambda x: x / W, lambda y: 1 - y / H         # inches from the left / from the top

y = MARGIN
fig.text(fx(L), fy(y), "\n".join(head_lines), fontsize=11, va="top", ha="left", linespacing=1.4)
y += len(head_lines) * HEAD + G
decades = pd.to_datetime([f"{yr}-01-01" for yr in range(1950, 2030, 10)])
axs, blocks = [], [("headline", MARGIN, len(head_lines) * HEAD)]
for i, ((title, s, yticks, ylim), h) in enumerate(zip(panels, heights)):
    fig.text(fx(L), fy(y), title, fontsize=10, va="top", ha="left")
    blocks.append(("title", y, TITLE))
    y += TITLE + GI
    ax = fig.add_axes([fx(L), fy(y + ABOVE + h), PW / W, h / H])   # the block holds the axes plus label room
    ax.plot(s, color=t.INK, lw=0.9)
    last = i == len(panels) - 1
    t.frame(ax, decades, yticks, xlim=(X0, X1), ylim=ylim, span=(s.index[0], s.index[-1]),
            xlabels=[str(x.year) for x in decades] if last else [""] * len(decades))
    blocks.append(("plot", y, ABOVE + h + BELOW + (LABELS if last else 0)))
    y += ABOVE + h + BELOW + (LABELS if last else 0) + G
    axs.append(ax)
fig.text(fx(L), fy(y), "\n".join(src_lines), fontsize=7.5, va="top", ha="left", color=t.GREY, linespacing=1.35)
blocks.append(("source", y, len(src_lines) * LINE * 7.5 / 9))
a, b, c, d = axs

t.note(a, T("2005-01-01"), at(ratio, "2005-01-01"), "bubble: debt rising faster than income, 2003 to 2007", side="left")
t.note(a, top_date, ratio[top_date], f"top, {top_date.to_period('Q')}: {ratio[top_date]:.0f}%", side="left", dy=8)
t.note(a, T("2020-04-01"), at(ratio, "2020-04-01"), "2020: GDP fell, debt jumped, then the ratio came back down", side="left", dy=9)
t.callout(a, T("2013-01-01"), at(ratio, "2013-01-01"),
          "beautiful deleveraging: the ratio stays flat for a decade\nwhile rates sit at zero and the Fed prints", at=(T("1988-01-01"), 185))
t.note(b, T("1981-05-01"), at(rate, "1981-05-01"), "%.0f%% in 1981" % at(rate, "1981-05-01"), dy=4)
t.callout(b, T("2011-01-01"), at(rate, "2011-01-01"), "zero from 2009 to 2015 and again in 2020 to 2021:\npushing on a string", at=(T("1997-01-01"), 12.5))
t.callout(b, T("2020-10-01"), at(rate, "2020-10-01"), "", at=(T("2011-06-01"), 10.3))
t.note(c, T("2007-07-01"), at(fed_gdp, "2007-07-01"), "%.0f%% before the top" % at(fed_gdp, "2007-07-01"), side="left", dy=6)
t.note(c, T("2014-10-01"), at(fed_gdp, "2014-10-01"), "after QE1 to QE3: %.0f%%" % at(fed_gdp, "2014-10-01"), side="left", dy=6)
t.note(c, T("2021-10-01"), at(fed_gdp, "2021-10-01"), "2021: %.0f%%" % at(fed_gdp, "2021-10-01"), dy=5)
c.text(T("1950-01-01"), 20, "weekly series begins in 2002", fontsize=8, color=t.GREY, va="center")
t.note(d, T("2009-10-01"), at(unemp, "2009-10-01"), "%.1f%% in October 2009" % at(unemp, "2009-10-01"), side="left", dy=6)
t.note(d, T("2020-04-01"), at(unemp, "2020-04-01"), "%.1f%% in April 2020" % at(unemp, "2020-04-01"), dy=5)

if "--structure" in sys.argv:                        # show the page's blocks and the two gap sizes between them
    for kind, top, hgt in blocks:
        fig.add_artist(Rectangle((fx(L), fy(top + hgt)), measure / W, hgt / H, fc="none", ec=t.ACCENT, lw=0.5, ls=":"))
    for (k1, t1, h1), (k2, t2, h2) in zip(blocks, blocks[1:]):
        fig.add_artist(Rectangle((fx(L), fy(t2)), measure / W, (t2 - t1 - h1) / H, fc=t.ACCENT, alpha=0.08, lw=0))
    fig.add_artist(Rectangle((fx(MARGIN), fy(H - MARGIN)), (W - 2 * MARGIN) / W, (H - 2 * MARGIN) / H, fc="none", ec=t.GREY, lw=0.4, ls=":"))
    fig.add_artist(plt.Line2D([fx(L), fx(L)], [fy(H - MARGIN), fy(MARGIN)], color=t.ACCENT, lw=0.4, ls=":"))
    fig.text(fx(W - MARGIN), fy(H - MARGIN + 0.05), f"page {W:.1f} x {H:.1f} in; margin {MARGIN} in; gap between blocks G = {G} in, inside a block GI = {GI} in; "
             f"axes heights banked toward 45 degrees on the drawn limits (floor 1.4 in): " + ", ".join(f"{h:.2f}" for h in heights),
             fontsize=7, color=t.ACCENT, ha="right", va="top")

out = os.path.abspath("big-debt-cycle" + ("-structure" if "--structure" in sys.argv else "") + ".rendered.png")
with mpl.rc_context({"savefig.bbox": None}):        # the page is the figure; the theme's tight crop would remove the margins
    fig.savefig(out)
print(out, f"{W:.2f} x {H:.2f} in")
