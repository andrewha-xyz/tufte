# Acme Payments: ten dashboards for an invented acquirer

Ten static pages for a merchant acquirer that does not exist, drawn with the tufte skill's rules. Every figure comes from `data.py`, a seeded generator; nothing is real. Each page is one self-contained HTML file in `out/`, and the render script writes a desktop (1440 px wide, 2x) and a phone (390 px wide, 2x) JPEG of each into out/jpg, which is not committed. The published images are on the [gallery branch](https://github.com/andrewha-xyz/tufte/tree/gallery/examples/acquirer).

| Page | What it shows |
|---|---|
| `monthly-revenue` | net revenue a month, earned to date, take rate, revenue by stream, the ledger |
| `weekly-revenue` | the same at weekly grain: revenue, volume, transactions, approval rate, active merchants |
| `revenue-ledger` | revenue, fee margin and other fees on one scale; the rates behind them; the full ledger |
| `revenue-ledger-grid` | nine metrics as small multiples of one size |
| `sparkline-ledger` | the month in one sparkline table, Tufte's answer to the KPI dashboard |
| `plan-vs-actual` | actuals against plan and stretch ticks, the fourth quarter range, objectives |
| `merchant-growth` | active, new and lost merchants, cohort retention, segments as a slopegraph |
| `unit-economics` | where $100 of card volume goes, contribution, cost lines on one scale |
| `driver-model` | new merchants, retention and revenue per merchant; channels; a sensitivity grid |
| `forecast` | a model made in May against what happened, and December under four cases |

The rules the pages follow, from `skills/tufte`:

- A total over a period (revenue, volume, transactions, fees) is one bar per period from zero. A ratio or a reading per period (take rate, approval rate, chargebacks per 10,000) is one dot. A running total is a step.
- The current month is half finished, so it is drawn as what is banked (grey) and its pace for the whole month (dashed), never joined to the finished months; as a dot it is hollow.
- Panels that are compared share one scale; when a scale differs, the caption says so.
- Labels sit on the graphic at the value they name; there are no legends. Grey carries context and one accent colour carries the finding.
- Every chart is at most 400 units wide, and tables drop secondary columns on a phone, so the same page reads on a desk and in a hand.

Build and render:

```
uv run python pages/monthly.py        # one page; each script in pages/ writes out/<name>.html
uv run render.py                      # every page in out/ to desktop and phone JPEGs, using the installed Chrome
uv run check.py                       # fails if a page in pages.txt is missing or anything overflows a 360, 375 or 390 px phone
# both take another example's folder first: uv run render.py ../engineering
```
