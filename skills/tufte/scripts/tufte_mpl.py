# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.8", "numpy"]
# ///
"""Tufte theme and forms for matplotlib.

Forms: range_frame, frame, dot_dash, sparkline, slopegraph, quartile.
Layout: page (Müller-Brockmann grid: margins, baseline, columns, fields; field/text/headline/show).
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
    "xtick.major.pad": 2, "ytick.major.pad": 2,
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


def frame(ax, xticks, yticks, xlim=None, ylim=None, xlabels=None):
    """Range frame with chosen ticks: spines span the first to last tick, limits cover the data.

    Use when min/max ticks alone would not read (time axes, round numbers). xticks may be dates."""
    ax.set_xticks(xticks, xlabels)
    ax.set_yticks(yticks)
    if xlim is not None:
        ax.set_xlim(*xlim)
    if ylim is not None:
        ax.set_ylim(*ylim)
    x0, x1 = ax.convert_xunits(xticks[0]), ax.convert_xunits(xticks[-1])
    ax.spines["bottom"].set_bounds(x0, x1)
    ax.spines["left"].set_bounds(min(yticks), max(yticks))
    ax.tick_params(length=3)


def mark(ax, x, y):
    """One accent dot at a data point; returns nothing, use with note or callout."""
    ax.plot([x], [y], "o", ms=3, color=ACCENT, zorder=3)


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


def _fit(fig, artist, text, fontsize, width, avail_px=None, strict=False):
    """Set wrapped text on the artist; measure it; narrow the wrap until it fits.

    avail_px: the width to fit, in pixels; default 98 percent of fig's width. Starts from the
    serif estimate (about 0.55 em per character) or the caller's width, then measures the
    rendered block, so unusual fonts still fit. Works for a Figure or SubFigure.
    strict=False (headline, source): long words are broken across lines as a last resort and
    the call always returns. strict=True (page.text): words stay whole and a word that cannot
    fit raises ValueError after removing the artist."""
    import textwrap
    fig.canvas.draw()                         # settle layout before measuring the space
    avail = avail_px if avail_px is not None else fig.bbox.width * 0.98
    if width is None:                         # start from one line, so a line that fits is never split
        width = max(len(text), int(avail / fig.dpi * 72 / (fontsize * 0.55)))
    width = max(1, width)
    while True:                               # width strictly decreases, so this terminates
        artist.set_text(textwrap.fill(text, width, break_long_words=not strict, break_on_hyphens=not strict))
        fig.canvas.draw()
        if avail_px is None:
            avail = fig.bbox.width * 0.98     # a SubFigure may have shrunk during the draw
        if artist.get_window_extent().width <= avail or (width == 1 and not strict):
            return
        if width == 1:
            artist.remove()
            raise ValueError("text does not fit the available width without breaking a word; "
                             "widen the figure or span, or shorten the words")
        width = max(1, int(width * 0.9))


def headline(fig, text, width=None, fontsize=11):
    """The finding as a sentence at the top left, wrapped by measurement so the export keeps
    the figure's width. `width` is a character-count starting point, not a guarantee."""
    _fit(fig, fig.suptitle("", x=0.01, ha="left", fontsize=fontsize), text, fontsize, width)


def source(fig, text, width=None, fontsize=7.5):
    """Sources, definitions and caveats under the figure, wrapped by measurement, in grey."""
    _fit(fig, fig.text(0.01, -0.02, "", fontsize=fontsize, color=GREY, va="top"), text, fontsize, width)


class page:
    """Müller-Brockmann grid for a figure: margins, a baseline, columns with one gutter, fields.

    cols: number of columns; baseline: points; margins: inches (left, right, top, bottom);
    gutter: points, default two baselines so hung axis labels fit between panels. Rows count
    baselines from the top margin; a text baseline sits 0.3 of the leading above its row's
    bottom edge. Nothing global is changed.
    field(c0, span, row, rows, pad=(1, 1)) returns an Axes inside those columns and baselines,
    keeping pad[0] baselines above for the title and pad[1] below for tick labels (pad=(0, 0)
    for a bare field such as a table or an image);
    title(ax, text) sets the one-line panel title with its baseline on the grid row above the axes;
    text(c0, span, row, text, ...) sets wrapped text, measured to the span, with its first
    baseline on that row and the lines one baseline apart;
    headline(text, rows) is text across all columns that raises if it needs more rows;
    save(path) exports at the page size and the figure's dpi (set dpi on the figure first;
    the theme's tight bbox would crop the margins). Sources and footers go through text()
    on reserved rows: the module-level source() sits outside a fixed page. Images in a bare
    field need ax.set_adjustable("datalim") or aspect="auto", or imshow shrinks the axes
    rectangle off the column lines;
    show() draws dotted column lines and row edges and solid text baselines for checking."""

    def __init__(self, fig, cols=12, baseline=14.0, margins=(0.6, 0.6, 0.7, 0.6), gutter=None):
        self.fig, self.cols, self.baseline = fig, cols, float(baseline)
        self.gutter = 2 * self.baseline if gutter is None else float(gutter)
        w, h = fig.get_size_inches()
        self.W, self.H = w * 72, h * 72
        ml, mr, mt, mb = (m * 72 for m in margins)
        self.x0, self.top, self.bottom = ml, self.H - mt, mb
        self.colw = (self.W - ml - mr - (cols - 1) * self.gutter) / cols

    def rect(self, c0, span, row, rows):
        """Figure-fraction (x, y, w, h) for columns c0..c0+span and baselines row..row+rows."""
        x = self.x0 + c0 * (self.colw + self.gutter)
        w = span * self.colw + (span - 1) * self.gutter
        y_top = self.top - row * self.baseline
        hgt = rows * self.baseline
        return x / self.W, (y_top - hgt) / self.H, w / self.W, hgt / self.H

    def field(self, c0, span, row, rows, pad=(1, 1)):
        return self.fig.add_axes(self.rect(c0, span, row + pad[0], rows - pad[0] - pad[1]))

    def title(self, ax, text, **kw):
        """Panel title whose baseline sits on the grid row above the axes (pad = 0.3 baseline).
        y=1.0 pins it there: matplotlib would otherwise lift it over an axis offset label, so
        avoid scientific-notation offsets (use a tick formatter) in gridded panels."""
        if "\n" in text:
            raise ValueError("page.title: one line only; a second line would leave the baseline grid. "
                             "Put the rest in a note with page.text")
        return ax.set_title(text, loc=kw.pop("loc", "left"), y=1.0, pad=0.3 * self.baseline, **kw)

    def baseline_y(self, row):
        """Figure-fraction y of the text baseline of `row`."""
        return (self.top - (row + 1) * self.baseline + 0.3 * self.baseline) / self.H

    def text(self, c0, span, row, text, fontsize=None, color=INK, weight="normal", rows=None):
        """Wrapped text measured to the span's width, one Text artist per line, each on its own
        baseline from `row` downwards (matplotlib lays multi-line text out by glyph extents, so
        a single artist cannot hold a baseline grid). Returns the list of line artists. With
        `rows`, raises if the text needs more rows than that; raises if a word cannot fit."""
        fontsize = fontsize or self.baseline / 1.4
        x, _, w, _ = self.rect(c0, span, row, 1)
        probe = self.fig.text(x, self.baseline_y(row), "", fontsize=fontsize, weight=weight, va="baseline", ha="left")
        _fit(self.fig, probe, text, fontsize, None, avail_px=w * self.W / 72 * self.fig.dpi, strict=True)
        lines = probe.get_text().split("\n")
        probe.remove()
        if rows is not None and len(lines) > rows:
            raise ValueError(f"page.text: {len(lines)} lines need {len(lines)} rows, {rows} given; "
                             "shorten the text, widen the span, or allow more rows")
        return [self.fig.text(x, self.baseline_y(row + i), line, fontsize=fontsize, color=color,
                              weight=weight, va="baseline", ha="left") for i, line in enumerate(lines)]

    def headline(self, text, rows=2, fontsize=None):
        """The finding across all columns, starting on row 0; raises if it needs more than `rows`."""
        return self.text(0, self.cols, 0, text, fontsize=fontsize or self.baseline * 1.1, rows=rows)

    def save(self, path, **kw):
        """Export the page at its configured size and at the figure's own dpi, so the text that
        was measured is the text that is drawn (the theme's tight bbox would crop the margins,
        and bbox_inches=None only defers to that setting, so both are overridden here)."""
        kw.setdefault("dpi", self.fig.dpi)
        with mpl.rc_context({"savefig.bbox": None}):
            self.fig.savefig(path, **kw)

    def show(self):
        """Overlay for checking: dotted column lines, dotted row edges (where panel edges sit) and
        solid text baselines, 0.3 baseline above each row edge."""
        right = (self.x0 + self.cols * self.colw + (self.cols - 1) * self.gutter) / self.W
        for c in range(self.cols):
            x, _, w, _ = self.rect(c, 1, 0, 1)
            self.fig.add_artist(plt.Rectangle((x, self.bottom / self.H), w, (self.top - self.bottom) / self.H,
                                              fc="none", ec=LIGHT, lw=0.4, ls=":"))
        for r in range(int((self.top - self.bottom) / self.baseline) + 1):
            edge = (self.top - r * self.baseline) / self.H
            self.fig.add_artist(plt.Line2D([self.x0 / self.W, right], [edge, edge], color=LIGHT, lw=0.3, ls=":"))
            if edge > self.bottom / self.H:
                y = self.baseline_y(r)
                self.fig.add_artist(plt.Line2D([self.x0 / self.W, right], [y, y], color=LIGHT, lw=0.3))


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
