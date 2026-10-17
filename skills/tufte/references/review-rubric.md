# Review rubric

Input: an image, chart code, or a description. Work through the four blocks in order; integrity findings outrank everything else. Score each line 0 (fails), 1 (partial), 2 (passes); report the score per block and the findings, not the total.

## Block A: integrity (blocking)

| # | Check | How |
|---|---|---|
| A1 | lie factor within 0.95 to 1.05 | measure two marks and their values; `uv run --locked "${CLAUDE_SKILL_DIR}/scripts/lie_factor.py" --data a b --graphic a2 b2` (path as given in SKILL.md) |
| A2 | no area or volume for 1-D quantities; no 3D | look for icons, bubbles, cylinders, perspective |
| A3 | bars start at zero; line range does not exaggerate slope; a line chart's aspect is near 45-degree banking of its median absolute segment slope, flat and vertical segments excluded (shared across panels compared in the same units; a mixed-unit stack banks each on its own scale), not dictated by a layout; dots, bars, steps and mostly flat series use the wider-than-tall default; legibility floor overrides | read the axis; estimate the median absolute segment slope of line charts |
| A4 | consistent intervals; money in constant currency when the span is long (rebasing to 100 is not deflation) | read tick spacing and units |
| A5 | one scale per variable across all panels | compare panel axes |
| A6 | enough context: the series around the highlighted change is shown | ask what was cut |
| A7 | ordered by the causal variable when causality is the claim | ask what the x-axis is and why |
| A8 | comparison, sources, scales, dates documented on the graphic | read the margins |
| A9 | every printed number carries its unit and its period; decimals trimmed to the decision; a top-level figure on a dashboard is decomposed into its components | read each number |

## Block B: form and comparison

| # | Check | How |
|---|---|---|
| B1 | the graphic answers a stated comparison ("compared with what?") and, when it is a graphic rather than a table, reveals something the table could not (a pattern, an anomaly, a counterexample) | name both; if you cannot, B1 = 0 |
| B2 | form matches data: a gradually changing state → line/sparkline; a state that jumps → step when change times are known, dots when not; a flow (totals per period) → one mark per period, never a smoothed line; two dates → table-graphic (slopegraph); distribution → quartile plot / dot-dash-plot; rank → sorted dot; many series → small multiples | see `integrity.md` (state or flow), `data-ink.md` |
| B3 | no pie, gauge, dual axis, word cloud | look |
| B4 | multivariate where the question is multivariate | count the variables shown versus the ones in the question |
| B5 | labels on the marks, no legend lookup | look for a legend |
| B6 | annotation states the finding in a sentence on the graphic | read the title and notes |
| B7 | tables only (no table scores 2): compared numbers aligned by digit place (units under units: a right edge or a shared decimal column, in tabular figures so the places stay straight), one header tier with the unit, no vertical header text, no cell repeating the header, one number format per column, no rules or zebra, rows in a logical order | see `tables.md` |

## Block C: ink and density

| # | Check | How |
|---|---|---|
| C1 | data-ink ratio: estimate the fraction of ink that is data; list the erasable items | border, grid, fills, legend, redundant labels, markers |
| C2 | chartjunk: moire, heavy grid, ducks | look |
| C3 | redundant data-ink thinned (bar sides, filled areas, every-point markers) | look |
| C4 | data density: could the same area carry the full series, or more series as small multiples | count numbers shown versus available |
| C5 | shrink test: would it survive at half size | imagine or render at half size |

## Block D: layering, type, color (polish)

| # | Check | How |
|---|---|---|
| D1 | smallest effective difference: structure grey and thin, one saturated hue at most | count hues and line weights |
| D2 | no 1+1=3 artefacts: outlines, halos, picket fences | look at bar edges and frames |
| D3 | type horizontal, upper and lower case, words spelled out, modest weight | look |
| D4 | contrast: text 4.5:1, marks 3:1 against background | sample hex values, `uv run --locked "${CLAUDE_SKILL_DIR}/scripts/check_contrast.py" '#fg' '#bg'`; if colors cannot be sampled, report "unverified", never guess |
| D5 | palette readable by colorblind readers; red/green never the only distinction | `uv run --locked "${CLAUDE_SKILL_DIR}/scripts/check_palette.py" '#a,#b,...'` |
| D6 | shape serves the slopes (wider than tall by default) | measure |
| D7 | fixed-page compositions only (a single figure exported tight scores 2 here): inner before outer at every level (title to plot no larger than plot to next block, block gap no larger than margin, visibly smaller where the eye must group), one left edge for page text and for the plots of a stack (in a grid, page text on the first column, each panel's title and caption on its own column) with axis labels hung into the margin, blocks that include their own labels and annotations, no repeated rhythm on adjacent rows unless the panels compare, a real margin, export at page size; block sizes from content, never from a layout | draw the blocks and gaps (the Dalio example's `--structure` flag); an inner gap larger than its outer, unrelated blocks that share both a gap and a width, or an edge that drifts is a finding; see `analytical-design.md`, The page |
| D8 | dashboards only (a single chart scores 2): one encoding per variable across every chart, the same comparison of the same data in the same form, one color scale for the key variable, controls beside what they control, latest value beside each sparkline, leader lines thin and uncrossed | see `density-multiples.md`, Dashboards |

## Output format

```
## Verdict
one sentence: publish / fix integrity first / redesign

## Scores
A integrity  n/18   B form n/14   C ink n/10   D polish n/16

## Findings (most severe first)
1. [A3] bars start at 40, not 0: the 12% difference reads as 3x. Fix: zero baseline, or switch to a dot plot if the range matters.
2. [B2] seven lines on one chart. Fix: small multiples, 7 panels, shared y, ordered by final value.
...

## Rewrite
the form and the annotation sentence you would use instead, with a recipe reference
```

Every finding carries a rule id, the evidence you saw, and a concrete fix. Do not pad with items that pass; say "A: no issues" and move on.
