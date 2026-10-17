---
name: tufte
description: >-
  Tufte-native data graphics. Use when designing, coding, or reviewing ANY chart,
  sparkline, slopegraph, small multiples, table-graphic, dashboard, or infographic;
  when asked for data-ink ratio, lie factor, chartjunk audit, data density, or to
  "make it Tufte". Three modes - design (default), review of an image, code or
  description, and infographic.
allowed-tools: Bash(uv run --locked "${CLAUDE_SKILL_DIR}/scripts/lie_factor.py" *) Bash(uv run --locked "${CLAUDE_SKILL_DIR}/scripts/check_contrast.py" *) Bash(uv run --locked "${CLAUDE_SKILL_DIR}/scripts/check_palette.py" *) Bash(uv run --locked "${CLAUDE_SKILL_DIR}/scripts/tufte_mpl.py" *)
---

# Tufte

Request: "$ARGUMENTS"

Doctrine from Tufte's five books, grounded against the texts where they could be read (see the repository README). Print-first; screen deviations are listed at the end. If a palette or design-system skill is also loaded, this skill governs form and integrity and the other governs color tokens.

This skill's scripts live at `${CLAUDE_SKILL_DIR}/scripts`. Use that absolute path, double-quoted, in every command below and in any chart code you generate; it is the same whether the skill is installed as a plugin or copied into `~/.claude/skills`.

## The twelve rules

1. Above all else, show the data.
2. Maximize the data-ink ratio, within reason. Erase non-data-ink; then erase redundant data-ink; revise and edit.
3. Lie factor = 1 (Tufte: outside 0.95 to 1.05 is substantial distortion). The size of an effect on paper must equal the size of the effect in the data. No area or volume for one-dimensional quantities. Printing the true numbers on a lying graphic is no defense.
4. Information-carrying dimensions in the graphic never exceed the dimensions in the data. No 3D, no decorative depth.
5. Show variation in data, not variation in design. Same scales across panels; one legend-free encoding per variable.
6. Never quote data out of context. Show enough of the series to judge the change. Bars encode length, so bar baselines sit at zero (general practice); for a time series Tufte's own advice is a baseline that shows the data, not the zero point.
7. Label on the graphic itself, not in a legend. Clear, detailed, thorough labeling defeats distortion and ambiguity.
8. Maximize data density and the size of the data matrix, within reason. Graphics can be shrunk way down. Small multiples beat one big chart.
9. Layering and separation: the smallest effective difference. Spots of strong color on a light grey or muted field; never red versus green as the only distinction. Watch for 1 + 1 = 3 clutter from unintended interactions.
10. Analytical design: show comparisons; show causality and mechanism; show multivariate data; integrate words, numbers, images; thoroughly describe the evidence; and let the content, not the design, carry the presentation.
11. Words, numbers, and pictures together, in sentences. Slides are a very low-resolution medium; put the evidence on one dense page and let people read it.
12. The friendly data graphic: words spelled out and running left to right, little messages explaining the data, labels on the graphic, colors the color-deficient can read, type clear and modest in upper and lower case with serifs, a shape about fifty percent wider than tall unless the data say otherwise.

Tufte's own caveat (VDQI epilogue): principles are not to be applied rigidly or in a peevish spirit; it is better to violate any of them than to place graceless marks on paper.

Banned without discussion: pie charts (and especially several of them), 3D, dual y-axes, moire fills, dark grids, chart borders, gradient bars, gauges, word clouds.

## Workflow: design (default)

1. **What is the comparison?** Name the question the graphic answers and the variables it must carry. If the answer is one or two numbers, write the sentence, no chart.
2. **Pick the form** from `references/data-ink.md` and `references/density-multiples.md`: time series → line / sparkline / small multiples; two time points → table-graphic (slopegraph); distribution → quartile plot / dot-dash-plot; ranking → sorted dot plot; many series → small multiples, never a spaghetti plot; precise lookup → table.
3. **Integrity pass** (`references/integrity.md`): compute the lie factor if any mark is scaled; check aspect ratio, baseline, context, and whether the data are ordered by the suspected cause.
4. **Erase** (`references/data-ink.md`): remove frames, grids, fills, legends, tick clutter; try the range-frame; label directly.
5. **Layer** (`references/analytical-design.md`): grey for structure and context, one strong color for the finding; annotate the finding in a sentence on the graphic. Words on the graphic have rules of their own: the headline and the source line are wrapped to the figure's width so a long sentence never widens the export and shrinks the panels; a label sits beside its mark only on the side where the panel is empty, otherwise it goes into empty space with a thin grey leader, and its placement is the author's responsibility, so look at the render; y-limits cover both the data and the tick range, so nothing is clipped and every tick label prints. `scripts/tufte_mpl.py` has `headline`, `source`, `note`, `callout`, `frame` for exactly this.
6. **Verify with scripts.** Always through `uv run --locked` with the quoted path (the scripts ship lockfiles):
   ```
   uv run --locked "${CLAUDE_SKILL_DIR}/scripts/lie_factor.py" --data a b --graphic a2 b2
   uv run --locked "${CLAUDE_SKILL_DIR}/scripts/check_contrast.py" '#fg' '#bg'
   uv run --locked "${CLAUDE_SKILL_DIR}/scripts/check_palette.py" '#a,#b,#c' --bg '#fff'
   ```
   Render and look at the output; never ship unseen.
7. **Generate** from `references/recipes.md` (matplotlib via `scripts/tufte_mpl.py`, plotly, vega-lite, SVG).

## Workflow: review

Use `references/review-rubric.md`. Score lie factor, data-ink ratio (estimate), data density, each integrity principle, each analytical-design principle. Report findings ordered by severity (integrity > form > ink > polish), each with the rule id and a concrete rewrite. When colors are visible, sample hex values and run the scripts; otherwise mark contrast as unverified.

## Workflow: infographic

Tufte's visual confection (`references/analytical-design.md`): an assembly of visual events that makes one argument, with the explanatory weight on one multifaceted image and the words integrated. Apply all twelve rules; embellishment only where it carries meaning.

## Screen deviations

Hover can replace some labels but never the headline annotation. Dark backgrounds invert the grey rules. Dashboards: sparkline tables and small multiples, not KPI tiles; Tufte notes screens run at a fraction of paper resolution, so print dense monitoring sheets when they matter. Responsive: small multiples reflow, never rescale axes per panel.

## Sources

VDQI 1983 (2nd ed. 2001) · Envisioning Information 1990 · Visual Explanations 1997 · Beautiful Evidence 2006 · The Cognitive Style of PowerPoint 2003. Pages, verification status, and URLs in the repository README.
