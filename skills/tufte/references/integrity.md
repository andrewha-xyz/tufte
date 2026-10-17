# Graphical integrity

Source: VDQI ch. 2 (Graphical Integrity, pp. 53 to 77) and ch. 9 (Aesthetics and Technique, shape pp. 186 to 190), verified against the full text; Visual Explanations ch. 2 (Visual and Statistical Thinking, pp. 27 to 53), verified against a scan of the chapter; Beautiful Evidence ch. 6, from excerpts.

## Lie factor (VDQI p. 57)

    lie factor = (size of effect shown in graphic) / (size of effect in data)
    size of effect = (second value - first value) / first value

Tufte: a lie factor greater than 1.05 or less than 0.95 indicates substantial distortion; almost all distortions overstate, and factors of two to five are not uncommon. His canonical example (New York Times, 1978) draws an 18 to 27.5 mpg change (53%) as a 0.6 to 5.3 inch line (783%): lie factor 14.8.

Compute it with `scripts/lie_factor.py` (path in SKILL.md) whenever a mark is scaled to a value. Common hiding places:

- area or volume used to show a one-dimensional quantity: Tufte's shrinking-doctor and shrinking-dollar examples (pp. 69 to 71) multiply the lie by scaling in two or three dimensions at once
- perspective or 3D depth that enlarges the front of the series
- a truncated bar baseline (bars compare lengths, so the length must start at zero)
- exaggerated aspect ratio that steepens a gentle slope
- inconsistent intervals on the time axis (irregular years spaced evenly)
- money over time shown in nominal units, so inflation masquerades as growth

Tufte rejects the defense that the true numbers are printed on the graphic (p. 76): not lying in one place does not justify a fifteenfold lie elsewhere.

## State or flow: what a line claims

Before drawing any series over time, ask what the number is between two observations.

- **A state** (temperature, a price, a balance, a headcount) has a value at every instant, but a line between two observations is honest only when the quantity changes gradually between them (temperature, a market price sampled often). When it changes in jumps (a balance, a headcount, a policy rate), draw a step that holds each value until the next change only if the change times are known (a rate decision, a posted transaction); if the data are snapshots that do not say when the jumps happened, draw dots and let the gaps stay empty. The question is what happened between the samples, not whether a value existed.
- **A flow** (revenue, fees, spend, orders, deaths, rainfall) is a total over an interval. It has no value between period ends, so a line through monthly totals asserts a continuity that does not exist and hides the period boundary the decision is about. Draw one mark per period: dots, bars from a zero baseline, or a step line that holds each period's value; a thin grey connecting line is at most a reading aid. A running total of discrete events (orders, payments) is a step function; a continuously accumulating quantity (rainfall, energy) is a gradually changing state and may be a line. A projection for the current period (month-to-date pace) is an open, dashed, labelled mark, never part of the line.

Sparklines follow the same rule: readings make a line; period totals make a dot-per-period sparkline or tiny bars. This is integrity principle 2 applied to the mark itself: the encoding must not claim more than the data contain. The same conclusion is reached independently at bureau.ru (Misyutina, https://bureau.ru/soviet/20240821/): the confusion comes from drawing time as continuous while the values are computed over intervals; her fix is unfilled stepped bars from zero, the same form at every period length, so the reader never guesses the period.

## Six principles of graphical integrity (VDQI p. 77, Tufte's wording)

1. The representation of numbers, as physically measured on the surface of the graphic itself, should be directly proportional to the numerical quantities represented.
2. Clear, detailed, and thorough labeling should be used to defeat graphical distortion and ambiguity. Write out explanations of the data on the graphic itself. Label important events in the data.
3. Show data variation, not design variation.
4. In time-series displays of money, deflated and standardized units of monetary measurement are nearly always better than nominal units.
5. The number of information-carrying (variable) dimensions depicted should not exceed the number of dimensions in the data.
6. Graphics must not quote data out of context.

## Applying them

**Baseline.** Bars encode length, so bars start at zero; that is general practice and this skill's rule, not a sentence in VDQI. For time series Tufte's documented advice (edwardtufte.com, "Baseline for amount scale", 2001) is to use a baseline that shows the data, not the zero point, and not to spend empty vertical space reaching down to zero. The question for a line is whether the chosen range exaggerates the slope, which is an aspect-ratio question.

**Aspect ratio (pp. 186 to 190).** Tufte calls the Golden Section a venerable but dubious rule and finds the psychology studies behind it hardly decisive. His conclusions: if the nature of the data suggests the shape of the graphic, follow that suggestion; otherwise move toward horizontal graphics about fifty percent wider than tall. His reasons: the horizon analogy, ease of labeling, emphasis on the causal variable running left to right, Tukey's counsel (a smoothly changing curve can stand being taller than wide, a wiggly curve needs to be wider than tall), and Playfair's practice (92 percent of his 89 graphics are wider than tall). Cleveland's banking to 45 degrees (not Tufte) is the compatible practical rule for choosing the height of a line chart: pick the aspect so the median absolute slope of the line's segments is about 45 degrees, where slope judgments are most accurate (Tufte's sparkline chapter states it as an average slope near 45 degrees; use the median, which outliers do not swing). Flat and vertical segments have no slope to bank, so leave them out; if nothing remains, or the series is mostly flat, fall back to the wider-than-tall default. Do this first; a page layout may then place the panel and scale it proportionally (above the legibility floor, compared panels together) but must not change its aspect. Panels meant to be compared in the same units (small multiples of one variable, a sparkline table of one measure) bank once, on all their segments pooled, and share that one aspect and physical scale; banking each separately would make equal changes look unequal. Panels in different units (a stack of debt, rates and unemployment sharing a time axis) have no common physical scale: bank each on its own declared scale, then give them the same width and, where the data allow, the same height, so the row reads as one. Banking does not apply to forms without sloped segments (dots, bars, steps); there use Tufte's wider-than-tall default. A sparkline table of one measure banks once for the whole table, on the rows' pooled segments, and every row takes that height; a table of mixed units keeps its declared per-row scales and banks on the rows after those scales are applied. Floor: a panel too short to read its own labels is wrong whatever the banking says.

**Context.** A single quarter's drop means nothing without the quarters around it. Show enough of the series that the reader can judge the change against normal variation. If the message needs a comparison, draw the comparison; a chart with one line and an implied counterfactual is a pitch, not evidence.

**Order by the suspected cause (Visual Explanations ch. 2).** Tufte's rule: if the substantive matter is a possible cause-effect relationship, graphs should organize the data to illuminate that link; the passage of time is a poor explanatory variable. His Challenger account: the night before the launch, the Thiokol engineers faxed 13 charts arguing against launching at a forecast 26 to 29 degrees F. The charts were thinking causally but not displaying causally: the temperature chart omitted most of the temperature data, the flights without damage were left out, and the argument rested on an anecdotal pairing of one cold (53 degrees) and one warm (75 degrees) flight. Tufte's redrawn scatterplot of all 24 prior launches, ordered by temperature, shows damage on every launch below 66 degrees and a forecast temperature far outside the experienced range. A later display prepared for the presidential commission ordered the same flights by launch date, which Tufte calls the fatal flaw of that chart: wrong order hides the relation. Numbers become evidence by being in relation to something.

Caveat for the skill's user: Tufte's Challenger redraw is contested (Robison, Boisjoly, Hoeker and Young 2002, Science and Engineering Ethics 8:59 to 81): the plotted temperatures mix calculated O-ring temperatures with ambient readings, the engineers' concern was blow-by rather than the erosion Tufte plots, and the launch decision was management's. Use the example for the principle (order by the suspected cause, include the damage-free cases, show the whole range) rather than as proof of what the engineers knew.

**Deflate.** Revenue, salaries, prices over more than a few years: convert to constant currency with a price index first, and say which index and base year. Rebasing a nominal series to 100 does not remove inflation; it only changes the units. Index the real series afterwards if the comparison wants it.

**Design variation.** One scale per axis across a whole figure. Panels in small multiples share scales. Do not change the bin width, the color meaning, or the symbol size between adjacent panels; the reader will read the change as data.

## Corruption in evidence presentations (Beautiful Evidence ch. 6)

Tufte's chapter title is a list of the sins: effects without causes, cherry picking, overreaching, chartjunk, and the rage to conclude. Its stance: presenting evidence is a moral act as well as an intellectual one, and consumers should hold presenters intellectually and ethically responsible. Points from the chapter:

- Published data have been selected, sorted, edited, summarized, and massaged; insist on an adequate description of that process. Cherry picking (evidence selection, culled data) is the most serious threat to learning the truth.
- A credible explanation needs explanatory theory, empirical evidence, and the rejection of competing explanations.
- Tufte's closing questions: Are the substantive findings a result of the methods used to construct the evidence? Did a favored view compromise the integrity of the analysis? How much does the decision at hand depend on this report's evidence?

Self-check questions adapted from the chapter for use before publishing: Is the comparison the right one or the convenient one? Which dates, denominators, and samples were chosen, and is the choice disclosed? Does the chart imply a cause it has not earned? Are sources, measurement, and scale on the graphic? A graphic that passes the lie factor but fails these is still a lie.
