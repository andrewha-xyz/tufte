# Data density, small multiples, sparklines, layering

Source: VDQI ch. 8 (Data Density and Small Multiples, pp. 161 to 175, verified against the full text); Envisioning Information ch. 1 to 4 (Escaping Flatland, Micro/Macro Readings, Layering and Separation, Small Multiples; from course notes, pages marked "around" are unverified); Beautiful Evidence ch. 2 (Sparklines, pp. 46 to 63, verified against Tufte's online version of the chapter).

## Data density (VDQI pp. 162 to 169)

    data density = number of entries in the data matrix / area of the data graphic

Tufte's principle: maximize data density and the size of the data matrix, within reason. Most published graphics are sparse (his first example scores 0.15 numbers per square inch); the eye resolves far more than a slide-sized chart with four bars gives it, and the more on one page, the more comparative the eye can be. As the volume of data increases, the data measures must shrink: smaller dots for scatters, thinner lines for busy time series; chartjunk costs more in a data-rich design.

**The shrink principle (p. 169).** Tufte: graphics can be shrunk way down; many can be reduced to half their published area with virtually no loss in legibility and information. Repeated application of the shrink principle leads to the small multiple. This skill's working test: reduce the chart until the type stops being legible, then back off one step.

**Data-rich, not data-thin.** When there are more numbers than the graphic shows, the question is why they were cut. A rule of thumb: if the whole series fits, show the whole series; aggregate only when the raw data cannot be read, and say so.

## Small multiples (VDQI pp. 170 to 175; Envisioning Information ch. 4)

Tufte's definition: a series of graphics, showing the same combination of variables, indexed by changes in another variable. The design remains constant through all the frames, so that attention is devoted entirely to shifts in the data. Once the reader has learned one panel, every other panel is free. Rules:

- identical scales, axes, and encodings in every panel (design variation here reads as data variation)
- ordered meaningfully: by value, by time, by geography, never alphabetically unless lookup is the task
- light labels on each panel, shared axis titles once
- many small panels beat one large chart with many lines; the spaghetti plot is the failure mode small multiples exist to prevent
- for comparison without a legend, one faint reference line per panel (the total or the average), not every other series redrawn in every panel
- comparisons must be enforced within the eyespan: all panels on one page, side by side

## Sparklines (Beautiful Evidence ch. 2)

Tufte's definition: a small, intense, simple, word-sized graphic with typographic resolution; datawords, data-intense, design-simple, word-sized. A sparkline is set at the size of the surrounding type, so it can sit inline in a sentence or in a table cell.

- Tufte's examples carry no axes, gridlines, or frame; the context comes from the words and numbers around the line.
- Tie the latest value to a number: in his glucose example a red dot marks the latest reading and the same red prints the number at the right, so the dot refers to a specific number.
- A grey band behind the line can show the normal range, so excursions read without a scale.
- In the exchange-rate table, color also marks the oldest and newest readings and the yearly low and high; use such marks when the question calls for them, not by default.
- Aspect ratio: wide and short, about 5:1 for finance, 20:1 for a baseball season, 300:1 for a DNA sequence; the average slope should be about 45 degrees (Cleveland), giving a lumpy rather than spiky line; in practice bank the median absolute segment slope, as in `integrity.md`.
- Density: about 500 sparklines on an A3 sheet for monitoring data; screens run at 10 to 15 percent of paper resolution, so print the sheet when it matters. A sparkline table (one row per entity: name, sparkline, latest value, change) shows the whole year and reduces recency bias; it is Tufte's answer to the dashboard. Sparklines are approximately right rather than exactly wrong.
- Binary outcomes (win/loss) can be shown as ticks up or down per event; Tufte warns that such sparklines can produce accidental white-space patterns that read as shape.
- Period totals (a flow) make a dot-per-period sparkline or tiny bars, not a line; see the state-or-flow test in `integrity.md`.

## Dashboards (the sparkline table, extended)

Tufte's dashboard is the sparkline table above; he says little about a screen of several charts. These rules come from a secondary source, the dashboard pages at bureau.ru (under https://bureau.ru/soviet/: 20241211 one encoding, 20240221 logic and usability, 20260318 and 20260415 assembly, 20260610 a critique, 20090820 a sensor sheet answered with Tufte's patient summary), and do not conflict with his.

- One particle, one encoding. Every chart of one dataset is built from that dataset's particle (SKILL.md step 0), so the same thing looks the same everywhere; a page with two datasets (purchases and tickets) has two particles, each consistent across its own charts: one color scale for the key variable, never two overlapping scales; one variable keeps one encoding wherever it appears (the same mark, color and scale), its subsets (branches, products) are small multiples of one form, and a second form of the same variable (a timeline beside a quartile plot) answers a second, stated comparison; a different variable gets the form its state-or-flow test and comparison call for, not a matching one for symmetry.
- Replicate, do not invent. Draw one zone, one branch, one entity, and repeat it; position then identifies the entity. Readings that compare in absolute terms share one physical scale; when each entity has its own normal range (the sensor sheet), draw the deviation from that range as the measure, labelled as such, so the aligned ticks mean the same thing in every row. Print the latest value to the right of each sparkline, as the sparkline table does.
- The biggest format anchors the layout (a map, the main series). On an interactive screen the side charts filter it and detail sits behind a click; a printed sheet keeps the detail on the page. Blocks ordered big to small and important to less so; a control sits beside the block it controls (a period selector far from its chart is the first defect found in review).
- A number without its unit and its period is not a number. Decimals trimmed to what the decision needs. Each top-level figure is decomposed on the page into the components it comes from.
- One screen is not a thing in itself: identical terms for identical concepts across screens, and the page answers the stated business questions, or nothing else matters.
- Show more, not less, while it stays legible: enlarge the sparklines before adding a tile.

Rubric: `review-rubric.md` A9, D8.

## Micro/macro readings (Envisioning Information ch. 2)

A dense display that reads at two levels: the overall pattern from across the room, the individual entries up close. Tufte's examples are maps, the Vietnam Veterans Memorial (58,000 names, readable as one shape and as each name), the Tokyo population map, a rail timetable. His stated strategy, which he calls his most unconventional (p. 37): to clarify, add detail. Design the macro first (what shape should the whole make), then make sure every micro entry is legible and labeled. Confusion and clutter are failures of design, not attributes of information (ch. 3, around p. 51 to 53): the fix is better layering, not fewer numbers. Comparisons must be enforced within the scope of the eyespan: put the things to be compared on one page, side by side, so the eye and not the memory does the comparing. Multifunctioning graphical elements (p. 47): one mark that carries two variables (a tick that is also a data point, a label that is also a scale) raises density without adding ink.

## Layering and separation (Envisioning Information ch. 3)

**1 + 1 = 3 or more.** Tufte takes the formula from Josef Albers: two marks placed near each other create a third visual event, the space between them, which the reader also sees, and the unintended events multiply with every added mark. Heavy outlines around bars produce a picket fence of white stripes; a thick frame around a chart adds a halo (these two are the skill's examples, not Tufte's). Remove outlines, soften edges, use fill without stroke, and look for the shapes the negative space is making.

**Layer by weight.** Data in the foreground (darkest, most saturated), labels next, structure (axes, ticks, reference lines) in the background grey. The reader should be able to attend to one layer and ignore the others. The same principle appears in Visual Explanations ch. 4 as the smallest effective difference; see `analytical-design.md`.

**Color.** The rules are in `analytical-design.md` (Color and Information): spots of strong color on a light grey or muted field, nature's palette, never red versus green as the only distinction. Verify with `scripts/check_palette.py` and `scripts/check_contrast.py`.

## Escaping flatland (Envisioning Information ch. 1)

Every display is a flat surface trying to show a multidimensional world. The chapter's methods, as summarized by readers of it rather than ranked by Tufte: overview plus perspective views, small multiples, two-dimensional indexing (tables and timetables), layering and separation, multifunctioning elements, small intense color spots. For the common case of a few variables on a screen, small multiples do most of the work. 3D rendering of two-dimensional data violates the dimension rule in VDQI (graphic dimensions never exceed data dimensions) and is not among the methods.
