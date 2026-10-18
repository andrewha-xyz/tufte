"""Page kit for the Acme Payments examples: number formats, one stylesheet, static SVG charts, tables.
Marks follow the skill's state-or-flow test: a total per period is one bar from zero; a ratio or reading per period is one dot;
a running total is a step; the current, partial period is drawn as what is banked plus an open dashed pace mark, never joined to
the series. Charts are at most 400 units wide so they stay legible when a phone scales them down."""
import html

MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
FULL = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
esc = html.escape


def _trim(x):
    return x.rstrip("0").rstrip(".") if "." in x else x


def usd(v):
    a, s = abs(v), "-" if v < 0 else ""
    if a < 1e3:
        return f"{s}${a:,.0f}"
    if a < 1e5:
        return f"{s}${_trim(f'{a / 1e3:.1f}')}k"
    if a < 1e6:
        return f"{s}${a / 1e3:.0f}k"
    return f"{s}${_trim(f'{a / 1e6:.2f}')}M" if a < 1e8 else f"{s}${a / 1e6:.0f}M"


def nice(v):
    """the smallest of 1, 2, 2.5, 5 times a power of ten at or above v"""
    import math
    e = 10 ** math.floor(math.log10(v))
    return next(m * e for m in (1, 2, 2.5, 5, 10) if m * e >= v)


def _labels(g, items, x, ys):
    """right-hand labels at their values' heights, pushed apart so none overlap"""
    placed = []
    for v, text, cls in sorted(items, key=lambda it: ys(it[0])):
        y = ys(v) + 3.5
        while any(abs(y - q) < 12 for q in placed):
            y += 12
        placed.append(y)
        g.append(f'<text x="{x:.1f}" y="{y:.1f}" class="lab {cls}">{esc(text)}</text>')


def dollars(v):
    return f"-${-v:,.0f}" if v < 0 else f"${v:,.0f}"


def num(v):
    return f"{v:,.0f}"


def pct(v, d=0):
    return f"{v * 100:.{d}f} %"


def bps(v, d=0):
    return f"{v * 1e4:.{d}f} bps"


def mlab(m):
    return MON[int(m[5:7]) - 1]


def mname(m):
    return FULL[int(m[5:7]) - 1]


CSS = """
:root{--paper:#fffff8;--ink:#111;--grey:#6b6b6b;--rule:#d4d1c7;--acc:#a12a1d;--fill:#d9d6cc;
--serif:"Source Serif 4","Iowan Old Style",Palatino,"Palatino Linotype",Georgia,serif;
--g1:6px;--g2:14px;--g3:32px;--g4:56px;--margin:72px;--hang:44px;--measure:640px}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);font-size:15px;line-height:24px;
font-variant-numeric:oldstyle-nums proportional-nums;-webkit-font-smoothing:antialiased}
.page{max-width:calc(1040px + 2 * var(--margin));margin:0 auto;padding:var(--margin) var(--margin) var(--margin) calc(var(--margin) + var(--hang))}
.page *{margin:0}
.head > * + *{margin-top:var(--g1)}
.head > .lede{margin-top:var(--g2)}
.page > section{margin-top:var(--g4)}
section > * + *{margin-top:var(--g3)}
section > h2 + *{margin-top:var(--g2)}
figure > * + *{margin-top:var(--g1)}
p + p{margin-top:var(--g2)}
h1{font-weight:400;font-size:30px;line-height:36px;text-wrap:balance}
h2{font-weight:400;font-style:italic;font-size:20px;line-height:26px}
p{max-width:var(--measure)}
.sub,.cap,.src{font-size:13px;line-height:20px;color:var(--grey)}
.sub,.cap{font-style:italic}
.lede{font-size:17px;line-height:26px}
.ptitle{font-style:italic;font-size:14px;line-height:20px}
.acc{color:var(--acc)}
.row{display:grid;grid-template-columns:repeat(var(--cols,3),minmax(0,var(--colw,300px)));column-gap:calc(var(--g3) + var(--hang));row-gap:var(--g3)}
figure{max-width:var(--figw,400px)}
figure svg{display:block;width:100%;height:auto;overflow:visible}
svg text{font-family:var(--serif);fill:var(--ink)}
svg .tick{font-size:10.5px;fill:var(--grey);font-variant-numeric:lining-nums tabular-nums}
svg .lab{font-size:11px;font-variant-numeric:lining-nums tabular-nums}
svg .lab.acc{fill:var(--acc)}
svg .lab.dim{fill:var(--grey)}
svg .axis{stroke:var(--grey);stroke-width:.7;fill:none}
svg .bar{fill:var(--ink)}
svg .bar.dim{fill:var(--fill)}
svg .banked{fill:var(--fill)}
svg .pace{fill:none;stroke:var(--acc);stroke-width:1;stroke-dasharray:2 2}
svg .plan{stroke:var(--grey);stroke-width:1.6}
svg .plan.str{stroke:var(--acc);stroke-width:1.2}
svg .ref{stroke:var(--grey);stroke-width:.7;stroke-dasharray:2 3;fill:none}
svg .line{stroke:var(--ink);stroke-width:1.3;fill:none;stroke-linejoin:round}
svg .line.acc{stroke:var(--acc)}
svg .line.dim{stroke:var(--grey);stroke-width:1;stroke-dasharray:3 3}
svg .dot{fill:var(--ink)}
svg .dot.acc{fill:var(--acc)}
svg .hollow{fill:var(--paper);stroke:var(--acc);stroke-width:1.2}
svg .leader{stroke:var(--rule);stroke-width:.8;fill:none}
.spark{vertical-align:-2px}
.spark .s{fill:var(--grey)}
.spark .a{fill:var(--acc)}
.tbl{max-width:100%;overflow-x:auto}
table{border-collapse:collapse;font-size:14px;line-height:22px;font-variant-numeric:lining-nums tabular-nums}
th,td{padding:0 16px 0 0;text-align:left;font-weight:400;white-space:nowrap;vertical-align:baseline}
th:last-child,td:last-child{padding-right:0}
thead th{white-space:normal;font-style:italic;color:var(--grey);font-size:13px;padding-bottom:6px;vertical-align:bottom}
td.n,th.n{text-align:right}
tbody th{padding-right:24px}
tr.gap > *{padding-top:10px}
tr.tot th,tr.part th,tr.part td{font-style:italic}
tr.part th,tr.part td{color:var(--grey)}
td.on{color:var(--ink)} td.risk{color:var(--acc)} td.off{color:var(--acc);font-style:italic}
.heat td{text-align:right;padding:0 4px;min-width:38px}
.src{margin-top:var(--g4)}
@media (max-width:1100px){.row{grid-template-columns:repeat(2,minmax(0,var(--colw,300px)))}}
@media (max-width:700px){
 :root{--margin:20px;--hang:30px;--g3:26px;--g4:44px}
 body{font-size:15px}
 h1{font-size:25px;line-height:31px}
 .row{grid-template-columns:minmax(0,1fr)}
 figure{max-width:100%}
 table{font-size:12px;line-height:18px}
 thead th{font-size:11px}
 th,td{padding-right:8px}
 tbody th{padding-right:10px;white-space:normal;min-width:5.5em}
 .m-hide{display:none}
}
"""


def page(title, sub, lede, sections, source, desc=""):
    body = "".join(sections)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(title)}</title><meta name="description" content="{esc(desc or sub)}"><style>{CSS}</style></head><body><main class="page">'
            f'<header class="head"><h1>{esc(title)}</h1><p class="sub">{sub}</p><p class="lede">{lede}</p></header>{body}'
            f'<p class="src">{source}</p></main></body></html>')


def section(h2, *blocks):
    return f'<section><h2>{h2}</h2>{"".join(blocks)}</section>'


def fig(title, svg, cap="", width=400):
    return f'<figure style="--figw:{width}px"><p class="ptitle">{title}</p>{svg}{f"<p class=cap>{cap}</p>" if cap else ""}</figure>'


def row(*figs, cols=3, colw=300):
    return f'<div class="row" style="--cols:{cols};--colw:{colw}px">{"".join(figs)}</div>'


def para(*ps):
    return "".join(f"<p>{p}</p>" for p in ps)


def _frame(W, H, aria):
    return [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(aria)}">']


def _xlabels(g, xlab, slot, b):
    for i, t in (xlab or {}).items():
        g.append(f'<text x="{i * slot + slot / 2:.1f}" y="{b + 15:.1f}" class="tick" text-anchor="middle">{esc(t)}</text>')


def bars(vals, *, top, lo=None, ticks=None, fmt=usd, W=320, H=170, room=64, xlab=None, partial=None, plans=None, stretch=None,
         right=None, dim=None, aria=""):
    """vals: list of (hover title, value). lo: shared lower bound for compared panels (default: zero or the lowest value).
    partial: dict(banked, pace, title). plans/stretch: value or None per slot.
    right: list of (value, text, cls) set in the right-hand room at the value's height. dim: indices drawn light."""
    n = len(vals) + (1 if partial else 0)
    pr, t, b = W - room, 6, H - 22
    lo = lo if lo is not None else min([0.0] + [v for _, v in vals] + ([partial["banked"], partial["pace"]] if partial else []))
    ys = lambda v: t + (b - t) * (top - v) / (top - lo)
    box = lambda v: (ys(max(v, 0)), abs(ys(v) - ys(0)))
    slot = pr / n
    bw = max(1.0, slot - 1.5)
    g = _frame(W, H, aria)
    for v in ticks if ticks is not None else [0, top / 2]:
        g.append(f'<text x="-7" y="{ys(v) + 3.5:.1f}" class="tick" text-anchor="end">{esc(fmt(v))}</text>')
    for i, (title, v) in enumerate(vals):
        cls = "bar dim" if dim and i in dim else "bar"
        y, h = box(v)
        g.append(f'<rect x="{i * slot:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" class="{cls}"><title>{esc(title)}</title></rect>')
    if partial:
        k = len(vals)
        (y, h), (yp, hp) = box(partial["banked"]), box(partial["pace"])
        g.append(f'<rect x="{k * slot:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" class="banked"><title>{esc(partial.get("title", ""))}</title></rect>')
        g.append(f'<rect x="{k * slot + 0.5:.1f}" y="{yp:.1f}" width="{bw - 1:.1f}" height="{hp:.1f}" class="pace"/>')
    for series, cls in ((plans, "plan"), (stretch, "plan str")):
        for i, p in enumerate(series or []):
            if p is not None:
                g.append(f'<line x1="{i * slot - 2:.1f}" x2="{i * slot + bw + 2:.1f}" y1="{ys(p):.1f}" y2="{ys(p):.1f}" class="{cls}"/>')
    g.append(f'<line x1="0" x2="{n * slot:.1f}" y1="{ys(0):.1f}" y2="{ys(0):.1f}" class="axis"/>')
    _xlabels(g, xlab, slot, b)
    _labels(g, right or [], pr + 8, ys)
    g.append("</svg>")
    return "".join(g)


def dots(vals, *, lo, hi, ticks, fmt, W=320, H=150, room=64, xlab=None, ref=None, partial=None, right=None, acc=None, aria=""):
    """one dot per period for a ratio or a reading. ref: (value, text) dashed reference. partial: (title, value) drawn hollow."""
    n = len(vals) + (1 if partial else 0)
    pr, t, b = W - room, 8, H - 22
    ys = lambda v: t + (b - t) * (hi - v) / (hi - lo)
    slot = pr / n
    g = _frame(W, H, aria)
    for v in ticks:
        g.append(f'<text x="-7" y="{ys(v) + 3.5:.1f}" class="tick" text-anchor="end">{esc(fmt(v))}</text>')
    if ref:
        g.append(f'<line x1="0" x2="{pr:.1f}" y1="{ys(ref[0]):.1f}" y2="{ys(ref[0]):.1f}" class="ref"/>')
        g.append(f'<text x="{pr + 8:.1f}" y="{ys(ref[0]) + 3.5:.1f}" class="lab dim">{esc(ref[1])}</text>')
    for i, (title, v) in enumerate(vals):
        g.append(f'<circle cx="{i * slot + slot / 2:.1f}" cy="{ys(v):.1f}" r="2.6" class="dot{" acc" if acc and i in acc else ""}"><title>{esc(title)}</title></circle>')
    if partial:
        g.append(f'<circle cx="{len(vals) * slot + slot / 2:.1f}" cy="{ys(partial[1]):.1f}" r="2.6" class="hollow"><title>{esc(partial[0])}</title></circle>')
    g.append(f'<line x1="0" x2="{n * slot:.1f}" y1="{b + 2:.1f}" y2="{b + 2:.1f}" class="axis"/>')
    _xlabels(g, xlab, slot, b + 2)
    _labels(g, right or [], pr + 8, ys)
    g.append("</svg>")
    return "".join(g)


def lines(series, *, n, top, ticks, fmt=usd, lo=0, W=360, H=190, room=84, xlab=None, aria=""):
    """series: list of dict(values=[v or None per slot], cls='line'|'line acc'|'line dim', step=False, label=text, dots=False).
    labels sit in the right-hand room at each series' last value."""
    pr, t, b = W - room, 8, H - 22
    ys = lambda v: t + (b - t) * (top - v) / (top - lo)
    slot = pr / n
    xs = lambda i: i * slot + slot / 2
    g = _frame(W, H, aria)
    for v in ticks:
        g.append(f'<text x="-7" y="{ys(v) + 3.5:.1f}" class="tick" text-anchor="end">{esc(fmt(v))}</text>')
    placed = []
    for s in series:
        pts = [(i, v) for i, v in enumerate(s["values"]) if v is not None]
        if s.get("step"):
            d = []
            for j, (i, v) in enumerate(pts):
                x0, x1 = i * slot, (i + 1) * slot
                d.append(f'{"M" if j == 0 else "L"}{x0:.1f},{ys(v):.1f} L{x1:.1f},{ys(v):.1f}')
            g.append(f'<path d="{" ".join(d)}" class="{s.get("cls", "line")}"/>')
        else:
            d = " ".join(f'{"M" if j == 0 else "L"}{xs(i):.1f},{ys(v):.1f}' for j, (i, v) in enumerate(pts))
            g.append(f'<path d="{d}" class="{s.get("cls", "line")}"/>')
        if s.get("dots"):
            for i, v in pts:
                g.append(f'<circle cx="{xs(i):.1f}" cy="{ys(v):.1f}" r="2.3" class="dot{" acc" if "acc" in s.get("cls", "") else ""}"/>')
        if s.get("label") and pts:
            y = ys(pts[-1][1]) + 3.5
            while any(abs(y - p) < 12 for p in placed):
                y += 12
            placed.append(y)
            g.append(f'<text x="{pr + 8:.1f}" y="{y:.1f}" class="lab{" acc" if "acc" in s.get("cls", "") else ""}">{esc(s["label"])}</text>')
    g.append(f'<line x1="0" x2="{n * slot:.1f}" y1="{b + 2:.1f}" y2="{b + 2:.1f}" class="axis"/>')
    _xlabels(g, xlab, slot, b + 2)
    g.append("</svg>")
    return "".join(g)


def table(head, rows, *, num=(), hide=(), cls=""):
    """head: column titles. rows: list of (row_class, [cells]); the first cell is a row header. num: right-aligned column indices.
    hide: column indices dropped on a phone."""
    def cell(j, v, tag):
        c = " ".join(x for x in ("n" if j in num else "", "m-hide" if j in hide else "") if x)
        return f'<{tag}{f" class={chr(34)}{c}{chr(34)}" if c else ""}>{v}</{tag}>'
    h = "".join(cell(j, v, "th") for j, v in enumerate(head))
    body = []
    for rc, cells in rows:
        tds = cell(0, cells[0], "th") + "".join(cell(j, v, "td") for j, v in enumerate(cells) if j)
        body.append(f'<tr{f" class={chr(34)}{rc}{chr(34)}" if rc else ""}>{tds}</tr>')
    return f'<div class="tbl"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def heat(rows, cols, *, fmt=lambda v: f"{v * 100:.0f}", lo=0.5, hi=1.0):
    """grey-shaded cells, darker for higher values; text flips to paper on the darkest cells"""
    out = ['<div class="tbl"><table class="heat"><thead><tr>' + "".join(f'<th class="n">{c}</th>' for c in cols) + "</tr></thead><tbody>"]
    for head, vals in rows:
        cells = [f"<th>{head}</th>"]
        for v in vals:
            if v is None:
                cells.append("<td></td>")
                continue
            f = max(0.0, min(1.0, (v - lo) / (hi - lo)))
            shade = round(248 - 150 * f)
            ink = "#fffff8" if shade < 150 else "#111"
            cells.append(f'<td style="background:rgb({shade},{shade - 2},{shade - 10});color:{ink}">{fmt(v)}</td>')
        out.append("<tr>" + "".join(cells) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def slope(left, right, names, *, fmt, W=360, H=220, lt="", rt="", acc=None, aria=""):
    """table-graphic for two points per item: shares at the left and right with the names beside the left values"""
    hi = max(left + right)
    ys = lambda v: 18 + (H - 30) * (hi - v) / hi
    x0, x1 = 150, W - 60
    g = _frame(W, H, aria)
    g.append(f'<text x="{x0}" y="8" class="tick" text-anchor="end">{esc(lt)}</text><text x="{x1}" y="8" class="tick">{esc(rt)}</text>')
    for i, (a, b, nm) in enumerate(zip(left, right, names)):
        c = " acc" if acc and i in acc else ""
        g.append(f'<line x1="{x0 + 6}" x2="{x1 - 6}" y1="{ys(a):.1f}" y2="{ys(b):.1f}" class="line{c}" style="stroke-width:1"/>')
        g.append(f'<text x="{x0}" y="{ys(a) + 3.5:.1f}" class="lab{c}" text-anchor="end">{esc(nm)} {esc(fmt(a))}</text>')
        g.append(f'<text x="{x1}" y="{ys(b) + 3.5:.1f}" class="lab{c}">{esc(fmt(b))}</text>')
    g.append("</svg>")
    return "".join(g)
