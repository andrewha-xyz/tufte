# Tables

Tufte gives tables one page (VDQI pp. 178 to 179: tables beat graphics for small data sets of up to about twenty numbers and for precise lookup; the table-graphic of pp. 158 to 159 is a table with slopes drawn). What follows fills the gap from a secondary source, Ilya Birman's answers in the bureau.ru advice column (the collection "Бирман пилит таблицы", https://bureau.ru/soviet/selected/dima-shishkin/birman-pilit-tablitsy/, 2010 to 2018). Verdicts whose argument was a before-and-after picture are marked as such; the rest is his stated rule. Where bureau and Tufte differ it is said.

## Alignment

- Left-align the table, numbers included; "right-align numbers" is a convention, not a rule (20170110). When numbers in a column are compared, align them by digit place, units under units and tens under tens, on a shared decimal column, in tabular (monospaced) figures so the places stay straight; left alignment alone does not do this (9 above 100 puts units under hundreds). Tufte's practice is a right-aligned numeric column, which gives place alignment for integers; the goal is the same, digits in columns.
- A sign (+, −, ±) stands in front of the number; keep it when its absence would change the meaning (20170110).
- Mixed decimals in one column (10,5 above 8,0): align by the digit place, not by the right edge; do not shift numbers to make room for brackets (20180410).
- Adjacent values use one number format: "2,00 €" next to "2 €" reads as a difference in meaning. Keep the currency unit; with it a number reads as a price at once (20120208).

## Header

- One header tier. Say in the title what the table contains, before the data; cut filler ("offers its subscribers the following plans") and attach a condition to the thing it limits, not to the row name (20110928, 20110105).
- No vertical text over a numeric body: the reader keeps returning to the header. Transpose, abbreviate with abbreviations the audience knows, or move repeated words out of the cells. Never flip rows and columns only to save width (20180410, 20111123).
- Units: Birman's list puts them in the body, Tufte and Milchin in the header. The reasoning was not available; the skill keeps the unit in the header unless a column mixes units.

## Cells

- Never repeat in a cell what the header already says: "no", not "no bonus" (20110928).
- Show what is present rather than what is absent: state when a plan's advertised speed applies instead of a column of "no" (20110928).
- A word-learning table is the exception to "move the common part out of the brackets": learners memorize whole phrases, so every case is written out, rows aligned, identical parts in one color (20131217).

## Rules, space, order

- No ruling lines; group by spacing (Gorbunov's inner before outer, `analytical-design.md`). Even out the horizontal gaps unless you mean to group columns (20140812, 20170110).
- Rows and columns in a logical order (time, rank, the reader's mental model); the sort key comes first (20131217, 20140812).
- Watch for ragged left edges: a score set between two team names rags both; left-aligning the names fixes the edge but breaks proximity. The chosen third version was a picture (20121009).
- Color only for meaning. A colored background against the table's own background is noise; zebra striping is junk; a legend that must be learned is a defect (20180410, 20110105). Color that marks identical parts of repeated phrases reads at two distances, structure from afar and words up close (20131217).
- Before compressing a wide table, ask a subject expert what each column means; slimming lost the difference between a heater and a desoldering tool (20130101, a picture).

## When a table should stop being a table

Birman never turns a table into a chart in these pages; at twenty by thirty cells he still abbreviates headers and keeps the grid. The skill keeps Tufte's preference instead: up to about twenty numbers a table is usually the better form, laid out as above, unless the comparison is a shape (a crossover between two dates, a ranking) that the table-graphic or sorted dots show at a glance; above it, ask what the comparison is (SKILL.md step 1) and consider the table-graphic, the sorted dot plot, or small multiples. The comparison and the lookup task decide, not the count.

Rubric: `review-rubric.md` B7.
