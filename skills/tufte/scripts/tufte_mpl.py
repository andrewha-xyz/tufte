# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.8", "numpy"]
# ///
"""Tufte theme and forms for matplotlib.

Forms: range_frame, frame, dot_dash, sparkline, slopegraph, quartile.
Words on the graphic: note (sentence beside a mark), callout (sentence in empty space with a
leader), headline (wrapped finding at the top), source (wrapped sources at the bottom).

The inline metadata above only installs dependencies when THIS file is the script
uv runs. A chart script that imports this module declares matplotlib and numpy itself
(copy the header block), is locked once with `uv lock --script chart.py`, and
runs with `uv run --locked chart.py`.
Then: sys.path.insert(0, "<skill dir>/scripts"); import tufte_mpl, where <skill dir> is the
directory holding SKILL.md (Claude sees it as ${CLAUDE_SKILL_DIR}).
Self-check: uv run --locked "<skill dir>/scripts/tufte_mpl.py" demo  (writes tufte-demo.png).
"""
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler

INK, GREY, LIGHT, ACCENT = "#1a1a1a", "#707070", "#c8c8c8", "#b22222"
# GREY passes 4.5:1 on white (text and marks); LIGHT is for de-emphasized context only.

RC = {
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": GREY, "axes.linewidth": 0.6,
    "axes.prop_cycle": cycler(color=[INK, GREY, ACCENT]),
    "axes.grid": False, "axes.titlelocation": "left", "axes.titleweight": "normal",
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "xtick.direction": "out", "ytick.direction": "out",
    "xtick.major.size": 3, "ytick.major.size": 3,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "font.family": "serif", "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "legend.frameon": False, "lines.linewidth": 1.0, "lines.color": INK,
    "savefig.dpi": 200, "savefig.bbox": "tight",
}


def use():
    mpl.rcParams.update(RC)


def _pair(a, b):
    """Shortest formatting that still tells the two extremes apart."""
    for p in range(3, 12):
        sa, sb = f"{a:.{p}g}", f"{b:.{p}g}"
        if sa != sb:
            return sa, sb
    return f"{a}", f"{b}"


def range_frame(ax, x, y):
    """Axis lines span only the data range; ticks at the extremes (VDQI p. 130)."""
    ax.spines["bottom"].set_bounds(min(x), max(x))
    ax.spines["left"].set_bounds(min(y), max(y))
    ax.set_xticks([min(x), max(x)], _pair(min(x), max(x)))
    ax.set_yticks([min(y), max(y)], _pair(min(y), max(y)))


def dot_dash(ax, x, y):
    """Scatter whose marginal rugs replace the axes (VDQI p. 133)."""
    ax.scatter(x, y, s=6, c=INK, lw=0)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.set_xticks(x)
    ax.set_yticks(y)
    ax.tick_params(length=4, width=0.5, labelbottom=False, labelleft=False)


def sparkline(ax, y, label=None, last=True, ylim=None, text_at="data"):
    """Word-sized graphic: no axes, endpoint marked, label as text (Beautiful Evidence ch. 2).

    Rows of a sparkline table pass a common ylim so equal rises mean equal changes, and
    text_at="center" so the name and value sit on the row's centre line instead of following
    the data to the row edges."""
    y = np.asarray(y, dtype=float)
    ax.plot(y, color=INK, lw=0.8)
    if ylim is not None:
        ax.set_ylim(*ylim)
    ax.axis("off")
    mid = sum(ax.get_ylim()) / 2
    ty0, ty1 = (mid, mid) if text_at == "center" else (y[0], y[-1])
    if last:
        ax.plot(len(y) - 1, y[-1], "o", ms=3, color=ACCENT)
        ax.annotate(f"{y[-1]:g}", (len(y) - 1, ty1), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=7, color=ACCENT)
    if label:
        ax.annotate(label, (0, ty0), xytext=(-4, 0), textcoords="offset points",
                    ha="right", va="center", fontsize=7, color=INK)


def _spread(values, gap, y0=-np.inf, y1=np.inf):
    """Nudge label positions apart so none sit closer than gap and all stay within [y0, y1];
    order preserved. Pushes up from each value, then down off the top edge, then up off the bottom."""
    order = np.argsort(values)
    pos = np.array(values, dtype=float)
    for k in range(1, len(order)):
        lo, hi = order[k - 1], order[k]
        if pos[hi] - pos[lo] < gap:
            pos[hi] = pos[lo] + gap
    top = y1 - gap / 2
    for idx in order[::-1]:
        pos[idx] = min(pos[idx], top)
        top = pos[idx] - gap
    bottom = y0 + gap / 2
    for idx in order:
        pos[idx] = max(pos[idx], bottom)
        bottom = pos[idx] + gap
    return pos


def slopegraph(ax, left, right, names, highlight=(), fontsize=7, ylim=None):
    """Table-graphic: two columns of values joined by lines, names typeset, no axes (VDQI p. 158).

    Call it last, after every title, label and panel of the figure is in place: it measures the
    panel once and does not re-fit if layout changes afterwards. Limits come from the data (or
    from `ylim`, ascending, which panels sharing a y-axis must pass in common); axes sharing x
    are refused because each panel sets its own x-range for its labels. Labels are spaced one
    line of type apart and kept inside the panel; type shrinks to fit, down to 5 pt, and below
    that the function raises with the panel height it needs. Horizontal room for the labels is
    reserved inside the axes, so tight export keeps them and layout engines are not disturbed."""
    if not len(left) == len(right) == len(names):
        raise ValueError(f"slopegraph: left, right and names must match: {len(left)}, {len(right)}, {len(names)}")
    if len(ax.get_shared_x_axes().get_siblings(ax)) > 1:
        raise ValueError("slopegraph: axes shares x with another panel; create the panels without sharex")
    if ylim is not None and ylim[1] <= ylim[0]:
        raise ValueError("slopegraph: ylim must be ascending")
    lo, hi = min(min(left), min(right)), max(max(left), max(right))
    pad = 0.04 * ((hi - lo) or 1.0)
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(*(ylim if ylim is not None else (lo - pad, hi + pad)))
    ax.axis("off")                   # hide decorations first so the panel is measured as drawn
    ax.figure.canvas.draw()          # settle any layout engine before measuring
    extent = ax.get_window_extent()
    height_pt = extent.height * 72 / ax.figure.dpi
    need_pt = 1.3 * 5.0 * len(names)
    if height_pt < need_pt:
        raise ValueError(f"slopegraph: {len(names)} rows need a panel at least {need_pt / 72:.1f} in tall "
                         f"at 5 pt type; this one is {height_pt / 72:.1f} in")
    fontsize = min(fontsize, height_pt / (1.3 * len(names)))
    y0, y1 = ax.get_ylim()
    gap = fontsize * 1.3 / height_pt * (y1 - y0)
    la, ra = _spread(left, gap, y0, y1), _spread(right, gap, y0, y1)
    colors = [ACCENT if n in highlight else GREY for n in names]
    texts_l = [ax.text(-0.03, ya, f"{n}  {a:g}", ha="right", va="center", fontsize=fontsize, color=c,
                       in_layout=False) for n, a, ya, c in zip(names, left, la, colors)]
    texts_r = [ax.text(1.03, yb, f"{b:g}  {n}", ha="left", va="center", fontsize=fontsize, color=c,
                       in_layout=False) for n, b, yb, c in zip(names, right, ra, colors)]
    ax.figure.canvas.draw()
    wl = max(tx.get_window_extent().width for tx in texts_l)
    wr = max(tx.get_window_extent().width for tx in texts_r)
    frac = (wl + wr + 0.04 * extent.width) / extent.width
    if (1 - frac) / 1.06 < 0.25:                 # lines would get under a quarter of the panel
        for tx in texts_l + texts_r:
            tx.remove()
        root = ax.figure.canvas.figure
        need_in = (wl + wr) / 0.695 / extent.width * root.get_figwidth()
        raise ValueError(f"slopegraph: labels would leave less than a quarter of the panel for the lines; "
                         f"widen the figure to about {need_in:.1f} in or shorten the names")
    span = 1.06 / (1 - frac)
    ax.set_xlim(-0.03 - wl / extent.width * span - 0.02 * span, 1.03 + wr / extent.width * span + 0.02 * span)
    for a, b, c, n in zip(left, right, colors, names):
        ax.plot([0, 1], [a, b], color=c, lw=1.2 if n in highlight else 0.8)


def quartile(ax, groups, labels):
    """Tufte box plot: median dot, gap for the interquartile box, thin whiskers (VDQI p. 125)."""
    for i, g in enumerate(groups):
        q1, med, q3 = np.percentile(g, [25, 50, 75])
        ax.plot([i, i], [min(g), q1], color=INK, lw=0.6)
        ax.plot([i, i], [q3, max(g)], color=INK, lw=0.6)
        ax.plot(i, med, "o", ms=3, color=INK)
    ax.set_xticks(range(len(groups)), labels)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="x", length=0)


def frame(ax, xticks, yticks, xlim=None, ylim=None, xlabels=None, span=None):
    """Range frame with chosen ticks. The bottom spine spans the data (`span` = (first, last)
    x of the data, which is the range-frame idea) or, without `span`, the first to last tick;
    the left spine spans the ticks; limits cover the data.

    Use when min/max ticks alone would not read (time axes, round numbers). xticks and span
    may be dates."""
    ax.set_xticks(xticks, xlabels)
    ax.set_yticks(yticks)
    if xlim is not None:
        ax.set_xlim(*xlim)
    if ylim is not None:
        ax.set_ylim(*ylim)
    lo, hi = span if span is not None else (xticks[0], xticks[-1])
    lo, hi = sorted((ax.convert_xunits(lo), ax.convert_xunits(hi)))
    xb0, xb1 = ax.get_xbound()                                   # ascending even on a reversed axis
    if hi < xb0 or lo > xb1:
        ax.spines["bottom"].set_visible(False)                   # nothing of the span is in view
    else:
        ax.spines["bottom"].set_visible(True)
        ax.spines["bottom"].set_bounds(max(lo, xb0), min(hi, xb1))   # never past the axes box
    ax.spines["left"].set_bounds(min(yticks), max(yticks))
    ax.tick_params(length=3)


def mark(ax, x, y):
    """One accent dot at a data point, drawn unclipped so a point on the axes edge (a zero, a
    maximum at the top of the range) keeps its whole dot; use with note or callout."""
    ax.plot([x], [y], "o", ms=3, color=ACCENT, zorder=3, clip_on=False)


def note(ax, x, y, text, side="right", dy=0, fontsize=8):
    """Mark the point and set a sentence beside it, on the side where the panel is empty.

    side: "right" or "left" of the point; dy in points lifts or drops the text."""
    mark(ax, x, y)
    dx = 5 if side == "right" else -5
    ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points",
                ha="left" if side == "right" else "right", va="center", fontsize=fontsize, color=ACCENT)


def callout(ax, x, y, text, at, ha="left", fontsize=8):
    """Mark the point and set the sentence in empty space at data coords `at`, joined by a thin
    grey leader. Use when no side of the point is free. A second leader to another point:
    callout(ax, x2, y2, "", at) with the same `at`; it runs from the same anchor, so put the
    words where that second line does not cross them. Placement is the caller's; look at the
    render."""
    mark(ax, x, y)
    ax.annotate(text, (x, y), xytext=at, textcoords="data", ha=ha, va="center", fontsize=fontsize,
                color=ACCENT, arrowprops=dict(arrowstyle="-", color=GREY, lw=0.5, shrinkB=3))


def _fit(fig, artist, text, fontsize, width):
    """Set wrapped text on the artist; measure it; narrow the wrap until it fits fig's width.

    Starts from the serif estimate (about 0.55 em per character) or the caller's width, then
    measures the rendered block, so unusual fonts still fit. Works for a Figure or SubFigure."""
    import textwrap
    fig.canvas.draw()                         # settle layout before measuring the space
    avail = fig.bbox.width * 0.98
    if width is None:
        width = int(avail / fig.dpi * 72 / (fontsize * 0.55))
    width = max(1, width)
    while True:                               # width strictly decreases, so this terminates
        artist.set_text(textwrap.fill(text, width))
        fig.canvas.draw()
        avail = fig.bbox.width * 0.98         # a SubFigure may have shrunk during the draw
        if artist.get_window_extent().width <= avail or width == 1:
            return
        width = max(1, int(width * 0.9))


def headline(fig, text, width=None, fontsize=11):
    """The finding as a sentence at the top left, wrapped by measurement so the export keeps
    the figure's width. `width` is a character-count starting point, not a guarantee."""
    _fit(fig, fig.suptitle("", x=0.01, ha="left", fontsize=fontsize), text, fontsize, width)


def source(fig, text, width=None, fontsize=7.5):
    """Sources, definitions and caveats under the figure, wrapped by measurement, in grey."""
    _fit(fig, fig.text(0.01, -0.02, "", fontsize=fontsize, color=GREY, va="top"), text, fontsize, width)


def demo(path="tufte-demo.png"):
    use()
    rng = np.random.default_rng(1)
    fig, axs = plt.subplots(2, 2, figsize=(7, 5), layout="constrained")
    x = np.sort(rng.uniform(0, 10, 40))
    y = 2 * x + rng.normal(0, 2, 40)
    axs[0, 0].plot(x, y, color=INK)
    range_frame(axs[0, 0], x, y)
    axs[0, 0].set_title("range frame")
    i = int(np.argmax(y))
    note(axs[0, 0], x[i], y[i], f"peak {y[i]:.1f}", side="left", dy=6)
    headline(fig, "Four Tufte forms from tufte_mpl.py: the range frame reports the data extremes, the dot-dash "
                  "replaces axes with rugs, the slopegraph typesets its values, the quartile plot erases the box.")
    source(fig, "Synthetic data, seed 1. Rendered by `uv run --locked tufte_mpl.py demo`.")
    dot_dash(axs[0, 1], x, y)
    axs[0, 1].set_title("dot-dash")
    axs[1, 0].set_title("slopegraph")
    slopegraph(axs[1, 0], [30, 25, 20, 15], [35, 20, 28, 10], list("ABCD"), highlight=("C",))
    quartile(axs[1, 1], [rng.normal(m, 1, 50) for m in (0, 1, 3)], ["a", "b", "c"])
    axs[1, 1].set_title("quartile plot")
    fig.savefig(path)
    print(path)


if __name__ == "__main__":
    demo() if "demo" in sys.argv else print(__doc__)   # uv run --locked "<skill dir>/scripts/tufte_mpl.py" demo
