# Acme Payments engineering: delivery dashboards for an invented team

Three static pages about an engineering organisation that does not exist: four teams, 22 engineers named after the NATO alphabet, 13 April to 15 October 2026. Every pull request, deploy and incident comes from `data.py`, a seeded generator. Two stories are built into the data so the graphics have something to find: Merchant dashboard leaves its weekly release train for continuous deploys on 3 August, and Risk and disputes loses a reviewer on 6 July.

| Page | What it shows |
|---|---|
| `delivery` | the four delivery measures: deploys a week, lead time from first commit to production, change failure rate, time to restore |
| `pull-request-flow` | where a pull request's time goes, the wait for a first review, pull request size, review load per engineer |
| `team-table` | every engineer in one sparkline table, grouped by team, with a note on reading it |

The graphics follow the skill's rules: a count per week is a bar from zero; a distribution per week is Tufte's quartile plot, a line from the first to the third quartile broken around the median; a rate is a dot; one event (an incident) is one dot at its date; the unfinished week is banked plus pace or a hollow mark. Hours and weeks share a log scale where both matter. The team table is not sorted or scored: output counts are not performance, and the page says so.

The pages reuse the acquirer example's kit (`../acquirer/kit.py`), renderer and phone check:

```
uv run python pages/delivery.py              # each script in pages/ writes out/<name>.html
uv run ../acquirer/render.py .               # desktop and phone JPEGs of every page in out/
uv run ../acquirer/check.py .                # fails if a page in pages.txt is missing or anything overflows a phone
```
