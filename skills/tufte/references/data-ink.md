# Data-ink and chartjunk

Source: VDQI ch. 4 (Data-Ink and Graphical Redesign, p. 91), ch. 5 (Chartjunk: Vibrations, Grids, and Ducks, p. 107), ch. 6 (Data-Ink Maximization and Graphical Design, p. 123). Verified against the full text; page numbers are the book's own.

## The ratio (p. 93)

    data-ink ratio = data-ink / total ink used to print the graphic
                   = 1.0 - proportion of a graphic that can be erased without loss of data-information

Data-ink is the non-erasable core: the ink that changes when the data change. Everything else is a candidate for erasure.

## Five principles of data-ink (p. 105)

1. Above all else, show the data.
2. Maximize the data-ink ratio.
3. Erase non-data-ink.
4. Erase redundant data-ink.
5. Revise and edit.

In the body of the chapter principles 2, 3, and 4 each end "within reason"; the closing list drops the phrase. A little redundancy that aids reading (a tick label at both ends, a second scale on a long chart) can stay. The test is whether the ink does work for the reader.

## Erasure checklist

Non-data-ink to remove first:

- chart border and plot-area box
- background fill, zebra bands, drop shadows
- gridlines (if some are needed, make them faint grey and sparse, or erase the data over them so the data win)
- legend (replace by labels on the marks)
- tick marks that do not mark anything the reader needs; ticks every unit when every fifth will do
- axis lines that extend beyond the data
- repeated units on every label (put "%" or "$" once, on the axis title)
- decorative color, gradients, textured fills

Redundant data-ink to thin:

- a bar's two sides, top, fill, and the label above it all encode the same number; one of them is enough
- a filled area under a line adds nothing to the line
- a point marker on every point of a dense line
- the same value stated in the title, on the mark, and in a table beside it

## Chartjunk (pp. 107 to 121)

Three species, all to be removed:

- **Moire vibration (p. 107).** Hatching, cross-hatching, dense patterns that shimmer. Replace with flat grey tones or direct labels.
- **The grid (p. 112).** Tufte: dark grid lines are chartjunk; a gray grid works well, muted relative to the data. Fade it, thin it, or remove it; the reader can estimate values from a few labeled ticks.
- **The duck (p. 116).** A graphic whose form is decided by something other than the data: 3D bars, icons as bars, pictorial charts, anything that exists to be noticed rather than read. Named, via Venturi's Learning from Las Vegas, after the Big Duck, a duck-shaped store in Flanders, New York.

## Redesigned forms

Each is a standard form with the redundant ink removed (ch. 6). `scripts/tufte_mpl.py` implements the first four for matplotlib; `references/recipes.md` has the others.

**Range-frame (p. 130).** The frame lines extend only to the measured limits of the data, so the frame itself reports the minimum and maximum. Ticks at the extremes; optionally marks at the quartiles.

**Dot-dash-plot (p. 133).** A scatterplot whose axes are replaced by marginal rugs: one short dash per observation on each axis. The frame now shows both marginal distributions. Tufte traces it to the old dot diagram.

**Quartile plot (pp. 124 to 125).** The box plot with the box erased: a line from the minimum to the first quartile, a gap or a dot at the median, a line from the third quartile to the maximum. Tufte's preferred form offsets the middle half sideways so the interquartile range reads at a glance; changing line weight is the alternative. Several side by side read faster than boxes and shrink to small-multiple size.

**Table-graphic, later called slopegraph (pp. 158 to 159).** Two columns of values at two points in time, each name typeset beside its value, joined by lines; Tufte's example is fifteen countries' tax rates in 1970 and 1979. Slope encodes change, vertical position encodes rank at each date. No axes, no legend; the typography is the chart. The name slopegraph is later (2011) and not in VDQI. This skill's rule of thumb: beyond about thirty rows, label only the rows that matter and let the rest run grey.

**White grid (pp. 127 to 129).** Where a grid is wanted on bars, draw it in white across the bars rather than in black behind them: the data stay solid and the grid reads as subtraction. Tufte's redesigned bar chart has no frame and no vertical axis.

**Erased-bar / line-only bar.** For a single series, the bar's top edge alone, or a dot at the value, carries the information; the fill is redundant.

**Stem-and-leaf, dot plot, sorted dot plot.** For rankings, a dot per category on a common scale, sorted, beats bars: less ink, same precision, long labels fit.

## Table versus graphic

Tufte is not anti-table. For up to about twenty numbers, a well-set table (right-aligned, consistent precision, units in the header, grouped by white space) is usually better than a chart. Tables are for looking up values; graphics are for seeing shape. When both are needed, the slopegraph and the sparkline table combine them.
