# tufte gallery

Rendered images of the examples on `main`, kept on their own branch so the plugin itself ships no image files. Every figure in them is invented.

- [examples/acquirer](examples/acquirer): ten dashboards for Acme Payments, an invented merchant acquirer, each as a desktop (1440 px wide) and a phone (390 px wide) image.
- [examples/engineering](examples/engineering): three delivery pages for an invented engineering team, in the same two sizes.

They are regenerated from the HTML on `main` with `uv run examples/acquirer/render.py` (and `uv run examples/acquirer/render.py examples/engineering`).
