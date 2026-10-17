# Recipes

Defaults that comply by construction. Colors: ink `#1a1a1a`, grey `#707070` (passes 4.5:1 on white), light grey `#c8c8c8` (context only, fails 3:1 by design), accent `#b22222` (one hue, used on one series or one point). Swap the accent for the brand hue if one exists; run `check_contrast.py` on the result.

## matplotlib

`scripts/tufte_mpl.py` carries PEP 723 metadata, but uv only installs the dependencies of the script it executes, not of imported modules. Every chart script therefore starts with its own header and imports the module by path:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.8", "numpy"]
# ///
import sys
sys.path.insert(0, "<skill dir>/scripts")   # <skill dir> = the directory holding SKILL.md, ${CLAUDE_SKILL_DIR}
import matplotlib.pyplot as plt
import numpy as np
import tufte_mpl as t
t.use()
```

Write the real absolute path into generated code; `${CLAUDE_SKILL_DIR}` is substituted in SKILL.md, not in Python.

Lock it once with `uv lock --script chart.py` and run it with `uv run --locked chart.py`; the header and the lockfile are the whole dependency story.

Forms provided: `t.range_frame(ax, x, y)`, `t.frame(ax, xticks, yticks, xlim=None, ylim=None, span=None)` (range frame with chosen ticks; `span` makes the axis line run exactly the data's length; dates allowed), `t.dot_dash(ax, x, y)`, `t.sparkline(ax, y, label=...)`, `t.slopegraph(ax, left, right, names, highlight=(...), ylim=None)` (labels nudge apart on ties and stay inside the panel, horizontal room is reserved for the names; the lines stay true; call it last, once every title, label and panel of the figure is in place; panels that share a y-axis pass the same ascending `ylim`, and `sharex` is refused; it raises with the needed height or width when the rows or names cannot fit), `t.quartile(ax, groups, labels)`. `use()` sets the color cycle to ink, grey, accent, so ordinary `ax.plot` calls stay monochrome. Self-check: `uv run --locked "<skill dir>/scripts/tufte_mpl.py" demo` writes `tufte-demo.png` in the working directory.

Small multiples, one panel per series, grid sized from the series count, one faint reference line (the mean across series) per panel instead of redrawing every series everywhere:

```python
import math
names = list(series)
cols = 4
rows = math.ceil(len(names) / cols)
ref = np.mean([series[n] for n in names], axis=0)
fig, axs = plt.subplots(rows, cols, figsize=(2 * cols, 1.4 * rows), sharex=True, sharey=True,
                        layout="constrained", squeeze=False)
for ax, name in zip(axs.flat, names):
    ax.plot(ref, color=t.LIGHT, lw=0.6)
    ax.plot(series[name], color=t.INK, lw=1)
    ax.text(0.02, 0.88, name, transform=ax.transAxes, fontsize=8)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
for ax in axs.flat[len(names):]:
    ax.axis("off")
fig.suptitle("Monthly orders by region, 2024 to 2026; grey line is the mean of all regions",
             x=0.01, ha="left", fontsize=9)
```

Sparkline table (one row per entity, one scale for the whole table so equal rises mean equal changes; use per-row scales only when the rows are in different units, and say so):

```python
rows = [("Lisbon", y1), ("Porto", y2), ("Faro", y3)]
lim = (min(map(min, (y for _, y in rows))), max(map(max, (y for _, y in rows))))
fig = plt.figure(figsize=(5, 0.25 * len(rows)))
for i, (name, y) in enumerate(rows):
    ax = fig.add_axes([0.25, 1 - (i + 1) / len(rows), 0.5, 0.9 / len(rows)])
    t.sparkline(ax, y, label=name, ylim=lim, text_at="center")
```

`text_at="center"` keeps each row's name and value on the row's centre line; with `"data"` (the default for inline sparklines) they follow the first and last values and can collide across tightly stacked rows.

Words on the graphic. `headline` and `source` wrap by measuring the rendered text against the figure's width (an optional `width` gives the starting character count); `note` and `callout` put text exactly where you say, so choose empty space and check the render:

```python
t.headline(fig, "Orders fell 12% in the quarter after the stockout and have not recovered; "
                "the two regions that kept stock grew 4%.")          # wrapped to the figure width
t.note(ax, x_event, y_event, "stockout, March", side="left", dy=6)    # beside the mark, on the empty side
t.callout(ax, x_peak, y_peak, "record quarter: 1,240 orders\nbefore the stockout",
          at=(x_empty, y_empty))                                     # in empty space, thin grey leader
t.callout(ax, x_other, y_other, "", at=(x_empty, y_empty))           # second leader to the same words
t.frame(ax, xticks=years, yticks=[0, 500, 1000], ylim=(0, 1300), span=(x[0], x[-1]))   # bottom spine spans the data, left spine the ticks
t.source(fig, "Source: orders table, fetched 2026-10-17; a quarter is three calendar months.")
```

For a time axis pass `xticks` as datetimes; `frame` converts them. Set `ylim` to cover both the data and the tick range, or tick labels outside the data range will not print.

## plotly

```python
import plotly.graph_objects as go

TUFTE = dict(
    template="none", plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Georgia, serif", color="#1a1a1a", size=12),
    title=dict(x=0, xanchor="left", font=dict(size=14)),
    xaxis=dict(showgrid=False, zeroline=False, showline=True, linecolor="#707070", linewidth=1,
               ticks="outside", tickcolor="#707070", ticklen=3, tickangle=0),
    yaxis=dict(showgrid=False, zeroline=False, showline=True, linecolor="#707070", linewidth=1,
               ticks="outside", tickcolor="#707070", ticklen=3),
    showlegend=False, margin=dict(l=50, r=100, t=50, b=40),
)
fig = go.Figure(layout=TUFTE)
```

Range frame: set `xaxis.range=[min(x), max(x)]`, `yaxis.range=[min(y), max(y)]` and `tickvals=[min, max]` on each axis; with `showline=True` the axis line then spans exactly the data range. Add a little padding on the opposite side with `layout.margin` rather than by widening the range.

Direct label: `fig.add_annotation(x=x[-1], y=y[-1], text="Region A", showarrow=False, xanchor="left", font=dict(color="#b22222"))`.

Bars at zero: `yaxis=dict(rangemode="tozero")`. Lines: leave the range free.

Small multiples: `plotly.subplots.make_subplots(rows, cols, shared_xaxes="all", shared_yaxes="all", horizontal_spacing=0.03, vertical_spacing=0.06)`; `True` would share x only within a column and y only within a row, which breaks the identical-scales rule. Apply the axis style to every subplot with `fig.update_xaxes(**TUFTE["xaxis"])` and `fig.update_yaxes(**TUFTE["yaxis"])`.

## vega-lite

```json
{
  "config": {
    "background": "white",
    "view": {"stroke": null},
    "font": "Georgia, serif",
    "axis": {"domainColor": "#707070", "tickColor": "#707070", "labelColor": "#1a1a1a",
             "titleColor": "#1a1a1a", "grid": false, "labelAngle": 0, "tickSize": 3},
    "title": {"anchor": "start", "fontSize": 14, "fontWeight": "normal", "color": "#1a1a1a"},
    "legend": {"disable": true},
    "line": {"color": "#1a1a1a", "strokeWidth": 1},
    "bar": {"color": "#707070"},
    "point": {"color": "#1a1a1a", "size": 12}
  }
}
```

Range frame: `"axis": {"domain": true, "values": [min, max]}` on each encoding plus `"scale": {"nice": false, "zero": false}` so the domain ends at the data (without `zero: false` a positive scatter still extends the frame to zero).

Highlight one series: `"color": {"condition": {"test": "datum.region === 'A'", "value": "#b22222"}, "value": "#c8c8c8"}` together with `"detail": {"field": "region", "type": "nominal"}`, which keeps each region its own line; color alone does not group the paths.

Small multiples, top-level facet operator: `{"facet": {"field": "region", "type": "nominal"}, "columns": 4, "spec": {...}, "resolve": {"scale": {"x": "shared", "y": "shared"}}}` (`columns` sits beside `facet`, not inside it).

Sparkline: `"width": 80, "height": 14`, both axes `null`, a `point` layer filtered to the last row with a `text` layer for the value.

Bars: quantitative scale `{"zero": true}`; lines: `{"zero": false}`.

## Raw SVG (for HTML and artifacts)

A sparkline with no library:

```html
<svg width="150" height="18" viewBox="0 0 150 18" aria-label="orders, last 24 months, latest 412">
  <polyline fill="none" stroke="#1a1a1a" stroke-width="0.8" points="0,12 5,11 10,13 ... 112,6"/>
  <circle cx="112" cy="6" r="1.6" fill="#b22222"/>
  <text x="118" y="8" font-size="7" fill="#b22222" font-family="Georgia, serif">412</text>
</svg>
```

The viewport is wider than the plotted line (150 against 112) so the value has room; SVG clips overflow by default.

Scaling, with the two degenerate cases handled:

```js
const w = 112, h = 18, pad = 2;   // w is the plot width, not the viewport width
const lo = Math.min(...v), hi = Math.max(...v), n = v.length;
const x = i => n === 1 ? w / 2 : i * w / (n - 1);
const y = val => hi === lo ? h / 2 : h - pad - (val - lo) / (hi - lo) * (h - 2 * pad);
const points = v.map((val, i) => `${x(i)},${y(val)}`).join(" ");
```

Set it inline in a sentence with `vertical-align: middle` and the height equal to the line height.

Table-graphic (slopegraph) in SVG: two `text` columns right- and left-anchored at x = 40 and x = 160, one `line` per row between them, grey by default and the accent hue for the one or two highlighted rows. No axes. Nudge colliding labels apart by the font size while leaving the line endpoints at their true values.

## Checks after generating

```
uv run --locked "<skill dir>/scripts/lie_factor.py" --data a b --graphic a2 b2
uv run --locked "<skill dir>/scripts/check_contrast.py" '#1a1a1a' '#ffffff'
uv run --locked "<skill dir>/scripts/check_palette.py" '#1a1a1a,#707070,#b22222' --bg '#ffffff'
```

SKILL.md gives `<skill dir>` as `${CLAUDE_SKILL_DIR}`.

Then open the rendered file and look at it. Overlapping text, a legend that crept back in, and a color cycle that reset are invisible in code.
