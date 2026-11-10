#!/usr/bin/env python3
"""svgkit — hand-placed inline-SVG diagram helpers for artifact pages.

Import from a page builder:  sys.path.insert(0, <skill>/scripts); from svgkit import *
Fig(...).zone/box/chevron/edge/chip/text, then render(aria). WARN collects estimated
overflow / overlap problems; print them before publishing. CSS/JS give the themed
vocabulary (light + dark tokens) and the flow-filter buttons. privacy_scan() greps the
finished HTML for identifiers that must not ship.
"""
import html
import sys
from pathlib import Path

WARN = []


def esc(s):
    return html.escape(str(s), quote=True)


def tw(s, size):
    """Rough rendered width of a string (IBM Plex Sans Latin + Noto Sans SC CJK)."""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if (0x2E80 <= o <= 0x9FFF) or (0x3000 <= o <= 0x303F) or (0xFF00 <= o <= 0xFFEF) or (0xF900 <= o <= 0xFAFF):
            w += size
        elif ch in '→←↑↓↔⇢≤≥×':
            w += size * 0.9
        elif ch in '·‹›':
            w += size * 0.36
        elif ch == ' ':
            w += size * 0.27
        elif ch in "il.,:;|!'`()[]/":
            w += size * 0.3
        elif ch in 'mwMW@%':
            w += size * 0.86
        elif ch.isupper() or ch.isdigit():
            w += size * 0.62
        else:
            w += size * 0.54
    return w * 1.05


def fit(label, s, size, maxw):
    w = tw(s, size)
    if w > maxw:
        WARN.append(f'[overflow] {label}: {s!r} ~{w:.0f}px > {maxw:.0f}px')


class Fig:
    FLOWS = ['auto', 'manual', 'gov', 'sync', 'model']

    def __init__(self, pid, W, H, label):
        self.pid, self.W, self.H, self.label = pid, W, H, label
        self.bg, self.zones, self.edges, self.nodes, self.labels = [], [], [], [], []
        self.rects = []  # (name, x, y, w, h) for overlap checks

    # ---------- primitives ----------
    def mk(self, flow):
        return f'url(#{self.pid}-mk-{flow})'

    def defs(self):
        ms = []
        for f in self.FLOWS + ['ink']:
            ms.append(
                f'<marker id="{self.pid}-mk-{f}" viewBox="0 0 10 10" refX="9" refY="5" '
                f'markerUnits="userSpaceOnUse" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
                f'<path class="mk mk-{f}" d="M0,0 L10,5 L0,10 z"/></marker>')
        grid = (f'<pattern id="{self.pid}-grid" width="16" height="16" patternUnits="userSpaceOnUse">'
                f'<path class="gridline" d="M16 0H0V16" fill="none"/></pattern>')
        return '<defs>' + ''.join(ms) + grid + '</defs>'

    def sheet(self):
        self.bg.append(f'<rect class="sheet-bg" x="0" y="0" width="{self.W}" height="{self.H}"/>')
        self.bg.append(f'<rect x="0" y="0" width="{self.W}" height="{self.H}" fill="url(#{self.pid}-grid)"/>')

    def chip(self, right, baseline, text):
        """Redaction chip, right-aligned so it never depends on the width of the text before it."""
        w = tw(text, 9.5) + 14
        x = right - w
        y = baseline - 11
        svg = (f'<rect class="redact" x="{x:.1f}" y="{y}" width="{w:.1f}" height="15" rx="3"/>'
               f'<text class="t-redact" x="{x + w / 2:.1f}" y="{y + 11}" text-anchor="middle">{esc(text)}</text>')
        return svg, w

    def zone(self, x, y, w, h, key, tag, title, note=None):
        tx, ty = x + 12, y + 7
        tag_w = tw(tag, 9.5) + 12
        s = [f'<g class="zone">',
             f'<rect class="zbg z-{key}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>',
             f'<rect class="ztag" x="{tx}" y="{ty}" width="{tag_w:.1f}" height="15" rx="7.5"/>',
             f'<text class="t-ztag" x="{tx + tag_w / 2:.1f}" y="{ty + 11}" text-anchor="middle">{esc(tag)}</text>',
             f'<text class="t-zone" x="{tx + tag_w + 7:.1f}" y="{ty + 11.5}">{esc(title)}</text>']
        if note:
            s.append(f'<text class="t-znote" x="{x + w - 12}" y="{ty + 11.5}" text-anchor="end">{esc(note)}</text>')
            room = w - 24 - (tag_w + 7 + tw(title, 12)) - 16
            fit(f'zone note {title}', note, 10.5, room)
        s.append('</g>')
        self.zones.append(''.join(s))

    def box(self, x, y, w, h, title, lines=(), flows='all', cls='box', chip=None,
            tsize=12.5, bsize=11, lh=14, pad=10, title_dy=18, first_dy=16, name=None,
            title_cls='t-title', body_cls='t-body', chip_on_line=None):
        name = name or title
        self.rects.append((name, x, y, w, h))
        s = [f'<g class="node" data-f="{flows}">',
             f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>']
        ty = y + title_dy
        chip_w = 0
        if chip is not None and chip_on_line is None:
            c_svg, chip_w = self.chip(x + w - pad, ty, chip)
            s.append(c_svg)
        fit(f'{name} title', title, tsize, w - 2 * pad - (chip_w + 6 if chip_w else 0))
        s.append(f'<text class="{title_cls}" x="{x + pad}" y="{ty}">{esc(title)}</text>')
        for i, line in enumerate(lines):
            ly = ty + first_dy + i * lh
            room = w - 2 * pad
            if chip is not None and chip_on_line == i:
                c_svg, cw = self.chip(x + w - pad, ly, chip)
                s.append(c_svg)
                room -= cw + 6
            fit(f'{name} line{i}', line, bsize, room)
            s.append(f'<text class="{body_cls}" x="{x + pad}" y="{ly}">{esc(line)}</text>')
        last = ty + first_dy + (len(lines) - 1) * lh if lines else ty
        if last + 4 > y + h:
            WARN.append(f'[vertical] {name}: last baseline {last} beyond box bottom {y + h}')
        s.append('</g>')
        self.nodes.append(''.join(s))

    def chevron(self, x, y, w, h, title, lines, flows='auto', first=False, notch=12, lh=13):
        self.rects.append((title, x, y, w, h))
        if first:
            pts = [(x, y), (x + w - notch, y), (x + w, y + h / 2), (x + w - notch, y + h), (x, y + h)]
        else:
            pts = [(x, y), (x + w - notch, y), (x + w, y + h / 2), (x + w - notch, y + h), (x, y + h),
                   (x + notch, y + h / 2)]
        p = ' '.join(f'{a},{b}' for a, b in pts)
        tx = x + (10 if first else 19)
        room = (x + w - notch - 3) - tx
        s = [f'<g class="node" data-f="{flows}">', f'<polygon class="chev" points="{p}"/>',
             f'<text class="t-title t-chev" x="{tx}" y="{y + 17}">{esc(title)}</text>']
        fit(f'chev {title}', title, 12, room)
        for i, line in enumerate(lines):
            fit(f'chev {title} line{i}', line, 10.5, room)
            s.append(f'<text class="t-body t-small" x="{tx}" y="{y + 31 + i * lh}">{esc(line)}</text>')
        s.append('</g>')
        self.nodes.append(''.join(s))

    def raw_node(self, svg, flows='all'):
        self.nodes.append(f'<g class="node" data-f="{flows}">{svg}</g>')

    def edge(self, pts=None, flows='auto', label=None, lx=None, ly=None, anchor='start', arrow=True,
             d=None, start_arrow=False, extra=''):
        f1 = flows.split()[0]
        if d is None:
            d = 'M' + ' L'.join(f'{a},{b}' for a, b in pts)
        me = f' marker-end="{self.mk(f1)}"' if arrow else ''
        ms = f' marker-start="{self.mk(f1)}"' if start_arrow else ''
        self.edges.append(f'<g class="edge" data-f="{flows}"><path class="e e-{f1}" d="{d}"{me}{ms}/>{extra}</g>')
        if label:
            self.labels.append(f'<g class="edge" data-f="{flows}"><text class="t-edge te-{f1}" x="{lx}" y="{ly}" '
                               f'text-anchor="{anchor}">{esc(label)}</text></g>')

    def text(self, x, y, s, cls='t-body', anchor='start', layer='labels'):
        getattr(self, layer).append(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{s}</text>')

    def check_overlaps(self):
        r = self.rects
        for i in range(len(r)):
            for j in range(i + 1, len(r)):
                a, b = r[i], r[j]
                if a[1] < b[1] + b[3] and b[1] < a[1] + a[3] and a[2] < b[2] + b[4] and b[2] < a[2] + a[4]:
                    WARN.append(f'[overlap] {self.pid}: {a[0]} x {b[0]}')

    def render(self, aria):
        self.check_overlaps()
        body = ''.join(self.bg + self.zones + self.edges + self.nodes + self.labels)
        return (f'<svg viewBox="0 0 {self.W} {self.H}" role="img" aria-label="{esc(aria)}" '
                f'xmlns="http://www.w3.org/2000/svg">{self.defs()}{body}</svg>')


# =====================================================================================
CSS = r"""
:root {
  /* Layout: a drafting sheet. Title block on top, wide figures on gridded paper, zones tinted by layer, flows colored by who drives them. */
  --bg: #eef1f3;
  --sheet: #fbfcfc;
  --grid: #e6ebee;
  --ink: #18212b;
  --ink-2: #44525f;
  --ink-3: #6f7d8a;
  --rule: #cdd5db;
  --box: #ffffff;
  --box-stroke: #b6c1ca;
  --ext-stroke: #8d9aa6;
  --law-stroke: #cbc1e0;
  --z-ui: #e9eff8;
  --z-law: #f1edf8;
  --z-run: #e5f2ee;
  --z-in: #edf4ea;
  --z-data: #f9f1e4;
  --z-base: #eceef1;
  --z-gov: #f8ebea;
  --f-auto: #0f7466;
  --f-manual: #2a5ca3;
  --f-gov: #b2412c;
  --f-sync: #6e4bb0;
  --f-model: #56636f;
  --seg-a: #cfe8e2;
  --seg-b: #e2efec;
  --seg-c: #e6e9ec;
  --redact: #1f242b;
  --redact-ink: #f2f4f6;
  --font-ui: "IBM Plex Sans", "Noto Sans SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  --font-mono: "IBM Plex Mono", "Noto Sans SC", ui-monospace, "Cascadia Mono", monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0e1215; --sheet: #13181c; --grid: #1c2328; --ink: #e3e8ec; --ink-2: #aab5bf; --ink-3: #7f8b96;
    --rule: #2f3941; --box: #192026; --box-stroke: #3a4651; --ext-stroke: #5d6a76; --law-stroke: #4a4065;
    --z-ui: #172130; --z-law: #1e1a2a; --z-run: #12231f; --z-in: #172219; --z-data: #251f15; --z-base: #1a1f24; --z-gov: #28191a;
    --f-auto: #4cbba8; --f-manual: #79a6ec; --f-gov: #ee7f69; --f-sync: #ac90e8; --f-model: #9aa7b3;
    --seg-a: #1d3a34; --seg-b: #172a27; --seg-c: #20262b;
    --redact: #d4dae0; --redact-ink: #101418;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #0e1215; --sheet: #13181c; --grid: #1c2328; --ink: #e3e8ec; --ink-2: #aab5bf; --ink-3: #7f8b96;
  --rule: #2f3941; --box: #192026; --box-stroke: #3a4651; --ext-stroke: #5d6a76; --law-stroke: #4a4065;
  --z-ui: #172130; --z-law: #1e1a2a; --z-run: #12231f; --z-in: #172219; --z-data: #251f15; --z-base: #1a1f24; --z-gov: #28191a;
  --f-auto: #4cbba8; --f-manual: #79a6ec; --f-gov: #ee7f69; --f-sync: #ac90e8; --f-model: #9aa7b3;
  --seg-a: #1d3a34; --seg-b: #172a27; --seg-c: #20262b;
  --redact: #d4dae0; --redact-ink: #101418;
  color-scheme: dark;
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font-family: var(--font-ui); font-size: 15px; line-height: 1.65; }
.wrap { max-width: 1440px; margin: 0 auto; padding-block: 28px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
h1, h2, h3 { text-wrap: balance; line-height: 1.3; }
code, .mono { font-family: var(--font-mono); font-size: .92em; }

/* title block, in the manner of a drawing's 图签 */
.titleblock { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 380px); border: 1.5px solid var(--ink);
  background: var(--sheet); }
.tb-main { padding: 22px 26px 24px; min-width: 0; }
.tb-kicker { font-size: 12px; letter-spacing: .14em; color: var(--ink-3); margin: 0 0 6px; }
.tb-main h1 { font-size: clamp(26px, 3.4vw, 38px); margin: 0 0 12px; font-weight: 700; letter-spacing: .01em; }
.tb-main p.lede { margin: 0; max-width: 64ch; color: var(--ink-2); }
.tb-fields { margin: 0; border-left: 1.5px solid var(--ink); display: grid; grid-template-rows: repeat(4, auto); min-width: 0; }
.tb-fields div { display: grid; grid-template-columns: 64px minmax(0, 1fr); border-top: 1px solid var(--rule); }
.tb-fields div:first-child { border-top: none; }
.tb-fields dt { padding: 9px 10px; font-size: 12px; letter-spacing: .08em; color: var(--ink-3); border-right: 1px solid var(--rule); }
.tb-fields dd { margin: 0; padding: 9px 12px; font-size: 13.5px; min-width: 0; overflow-wrap: anywhere; }

.redact-chip { display: inline-block; background: var(--redact); color: var(--redact-ink); font-size: 11.5px; font-weight: 600;
  letter-spacing: .06em; padding: 0 7px; border-radius: 3px; line-height: 1.55; margin: 0 2px; vertical-align: 1px; }

section { margin-top: 44px; }
.sec-head { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 14px; margin-bottom: 8px; }
.sec-head .fig-no { font-family: var(--font-mono); font-size: 12px; color: var(--ink-3); letter-spacing: .06em; }
.sec-head h2 { font-size: 21px; margin: 0; }
.intro { margin: 0 0 14px; max-width: 78ch; color: var(--ink-2); }

.controls { display: flex; flex-wrap: wrap; gap: 8px 10px; align-items: center; margin-bottom: 12px; }
.flt { font: inherit; font-size: 13px; color: var(--ink); background: var(--sheet); border: 1px solid var(--rule);
  border-radius: 999px; padding: 4px 12px; cursor: pointer; display: inline-flex; align-items: center; gap: 7px; }
.flt:hover { border-color: var(--ink-3); }
.flt[aria-pressed="true"] { background: var(--ink); color: var(--sheet); border-color: var(--ink); }
.flt:focus-visible { outline: 2px solid var(--f-manual); outline-offset: 2px; }
.sw { width: 18px; height: 0; border-top: 2.5px solid currentColor; display: inline-block; }
.sw-auto { border-color: var(--f-auto); } .sw-manual { border-color: var(--f-manual); } .sw-gov { border-color: var(--f-gov); }
.sw-sync { border-color: var(--f-sync); border-top-style: dashed; } .sw-model { border-color: var(--f-model); border-top-style: dotted; }
.legend { display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: 12.5px; color: var(--ink-3); margin: 0 0 12px; }
.legend span { display: inline-flex; align-items: center; gap: 6px; }
.lg-box { width: 18px; height: 12px; border: 1px solid var(--box-stroke); background: var(--box); border-radius: 3px; }
.lg-ext { width: 18px; height: 12px; border: 1px dashed var(--ext-stroke); background: var(--sheet); border-radius: 3px; }
.lg-chev { width: 20px; height: 12px; background: var(--f-auto); clip-path: polygon(0 0, 70% 0, 100% 50%, 70% 100%, 0 100%, 30% 50%); }
.lg-owner { width: 20px; height: 12px; background: var(--ink); border-radius: 6px; }
.lg-red { width: 22px; height: 12px; background: var(--redact); border-radius: 2px; }

figure { margin: 0; }
.figscroll { overflow-x: auto; border: 1px solid var(--rule); background: var(--sheet); border-radius: 4px; }
.figscroll svg { display: block; width: 100%; height: auto; min-width: 1240px; }
figcaption { font-size: 13px; color: var(--ink-3); margin-top: 8px; max-width: 90ch; }
.scroll-hint { display: none; font-size: 12.5px; color: var(--ink-3); margin: 0 0 6px; }
@media (max-width: 900px) { .scroll-hint { display: block; } }

/* svg vocabulary */
svg text { font-family: var(--font-ui); }
.sheet-bg { fill: var(--sheet); }
.gridline { stroke: var(--grid); stroke-width: 1; }
.host { fill: none; stroke: var(--ink-3); stroke-width: 1.3; stroke-dasharray: 7 5; }
.t-hostwrap { font-size: 12px; }
.t-host-b { font-weight: 700; fill: var(--ink); }
.t-host { fill: var(--ink-3); }
.z-ui { fill: var(--z-ui); } .z-law { fill: var(--z-law); } .z-run { fill: var(--z-run); } .z-in { fill: var(--z-in); }
.z-data { fill: var(--z-data); } .z-base { fill: var(--z-base); } .z-gov { fill: var(--z-gov); }
.ztag { fill: none; stroke: var(--ink-3); stroke-width: 1; }
.t-ztag { font-size: 9.5px; font-weight: 600; fill: var(--ink-2); letter-spacing: .03em; }
.t-zone { font-size: 12px; font-weight: 600; fill: var(--ink); }
.t-znote { font-size: 10.5px; fill: var(--ink-3); }
.t-rowlab { font-size: 10.5px; font-weight: 600; fill: var(--ink-2); }
.box { fill: var(--box); stroke: var(--box-stroke); stroke-width: 1; }
.box.entry { stroke-dasharray: none; }
.box.gov { stroke: color-mix(in srgb, var(--f-gov) 45%, var(--box-stroke)); }
.box.card { stroke: color-mix(in srgb, var(--f-auto) 55%, var(--box-stroke)); }
.box.ok { stroke: var(--f-auto); stroke-dasharray: 3 3; }
.box.decide { fill: var(--box); stroke: var(--f-auto); stroke-width: 1.2; }
.box.mini { rx: 5px; }
.box.links, .box.rule { fill: var(--sheet); }
.box.ladder.later { stroke-dasharray: 4 3; }
.ext { fill: var(--sheet); stroke: var(--ext-stroke); stroke-width: 1; stroke-dasharray: 4 3; }
.ext-sync { stroke: var(--f-sync); }
.chev { fill: var(--box); stroke: var(--f-auto); stroke-width: 1.2; stroke-linejoin: round; }
.chip { fill: var(--box); stroke: var(--law-stroke); stroke-width: 1; }
.t-chip { font-size: 10.5px; fill: var(--ink-2); }
.owner { fill: var(--ink); }
.t-owner { fill: var(--sheet); font-size: 13px; font-weight: 600; }
.t-title { font-size: 12.5px; font-weight: 600; fill: var(--ink); }
.t-chev { font-size: 12px; }
.t-mini { font-size: 11.5px; font-weight: 500; fill: var(--ink); }
.t-body { font-size: 11px; fill: var(--ink-2); }
.t-small { font-size: 10.5px; }
.t-strong { font-weight: 600; fill: var(--ink); }
.t-dim { fill: var(--ink-3); font-weight: 400; }
.t-machine { font-size: 13px; }
.t-lanehead { font-size: 12px; fill: var(--ink-2); }
.t-note { font-size: 10.5px; fill: var(--ink-3); }
.t-tick { font-size: 10px; fill: var(--ink-3); font-variant-numeric: tabular-nums; }
.tick { stroke: var(--ink-3); stroke-width: 1; }
.seg-a { fill: var(--seg-a); } .seg-b { fill: var(--seg-b); } .seg-c { fill: var(--seg-c); }
.t-seg { font-size: 10.5px; fill: var(--ink); font-weight: 500; }
.tag { fill: var(--sheet); stroke: var(--ext-stroke); stroke-width: 1; stroke-dasharray: 3 2; }
.t-tag { font-size: 10px; fill: var(--ink-2); }
.tagtick { stroke: var(--ext-stroke); stroke-width: 1; }
.t-chsub { font-size: 10px; fill: var(--ink-3); paint-order: stroke; stroke: var(--sheet); stroke-width: 3px; stroke-linejoin: round; }
.machine { fill: var(--z-ui); stroke: var(--ink-3); stroke-width: 1.2; }
.machine-mac { fill: var(--z-law); stroke-dasharray: 6 4; }
.redact { fill: var(--redact); }
.t-redact { fill: var(--redact-ink); font-size: 9.5px; font-weight: 600; letter-spacing: .05em; }
.e { fill: none; stroke-width: 1.5; stroke-linejoin: round; stroke-linecap: round; }
.e-auto { stroke: var(--f-auto); } .e-manual { stroke: var(--f-manual); } .e-gov { stroke: var(--f-gov); }
.e-sync { stroke: var(--f-sync); stroke-dasharray: 5 4; } .e-model { stroke: var(--f-model); stroke-dasharray: 2 3; }
.mk-auto { fill: var(--f-auto); } .mk-manual { fill: var(--f-manual); } .mk-gov { fill: var(--f-gov); }
.mk-sync { fill: var(--f-sync); } .mk-model { fill: var(--f-model); } .mk-ink { fill: var(--ink-2); }
.dot-model { fill: var(--f-model); }
.t-edge { font-size: 10px; font-weight: 600; paint-order: stroke; stroke: var(--sheet); stroke-width: 3px; stroke-linejoin: round; }
.te-auto { fill: var(--f-auto); } .te-manual { fill: var(--f-manual); } .te-gov { fill: var(--f-gov); }
.te-sync { fill: var(--f-sync); } .te-model { fill: var(--f-model); }
.node, .edge { transition: opacity .18s ease; }
.edge.dim { opacity: .08; }
.node.dim { opacity: .3; }
@media (prefers-reduced-motion: reduce) { .node, .edge { transition: none; } }

/* tables and lists */
.tablewrap { overflow-x: auto; border: 1px solid var(--rule); background: var(--sheet); border-radius: 4px; }
table { border-collapse: collapse; width: 100%; min-width: 760px; font-size: 14px; }
th, td { text-align: left; vertical-align: top; padding: 9px 12px; border-top: 1px solid var(--rule); }
thead th { border-top: none; font-size: 12px; letter-spacing: .08em; color: var(--ink-3); font-weight: 600; background: var(--bg); }
td.when { white-space: nowrap; font-variant-numeric: tabular-nums; }
td.name { white-space: nowrap; font-weight: 600; }
.pill { display: inline-block; font-size: 12px; padding: 0 8px; border-radius: 999px; border: 1px solid var(--rule); color: var(--ink-2); white-space: nowrap; }
.pill.script { border-color: var(--f-auto); color: var(--f-auto); }
.pill.kanban { border-color: var(--f-manual); color: var(--f-manual); }
.foot { font-size: 13px; color: var(--ink-3); margin: 8px 0 0; max-width: 90ch; }
.cols { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 420px), 1fr)); gap: 18px 36px; }
.rules { margin: 0; padding: 0; list-style: none; display: grid; gap: 10px; }
.rules li { padding-left: 14px; border-left: 2px solid var(--rule); max-width: 70ch; }
.rules b { font-weight: 600; }
dl.mask { margin: 0; display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: 6px 16px; font-size: 14px; }
dl.mask dt { color: var(--ink-2); }
dl.mask dd { margin: 0; min-width: 0; }
.srcs { font-size: 13px; color: var(--ink-2); columns: 2 320px; column-gap: 32px; padding-left: 18px; margin: 0; }
.srcs li { break-inside: avoid; margin-bottom: 4px; }
@media (max-width: 760px) {
  .titleblock { grid-template-columns: minmax(0, 1fr); }
  .tb-fields { border-left: none; border-top: 1.5px solid var(--ink); }
}
"""

JS = r"""
(function () {
  var fig = document.getElementById('fig-overview');
  if (!fig) return;
  var buttons = document.querySelectorAll('.flt');
  var items = fig.querySelectorAll('.edge, .node');
  function apply(f) {
    for (var i = 0; i < items.length; i++) {
      var el = items[i];
      var fl = (el.getAttribute('data-f') || 'all').split(' ');
      var keep = f === 'all' || fl.indexOf('all') >= 0 || fl.indexOf(f) >= 0;
      el.classList.toggle('dim', !keep);
    }
    for (var j = 0; j < buttons.length; j++) {
      buttons[j].setAttribute('aria-pressed', buttons[j].getAttribute('data-flt') === f ? 'true' : 'false');
    }
    try { localStorage.setItem('arch-filter', f); } catch (e) {}
  }
  for (var k = 0; k < buttons.length; k++) {
    buttons[k].addEventListener('click', function () { apply(this.getAttribute('data-flt')); });
  }
  var saved = 'all';
  try { saved = localStorage.getItem('arch-filter') || 'all'; } catch (e) {}
  apply(saved);
})();
"""


def privacy_scan(html_text, terms):
    """Return [(term, count)] for every term (str or regex) found in the page. Empty list = clean."""
    import re
    hits = []
    for t in terms:
        n = len(re.findall(t, html_text, flags=re.I))
        if n:
            hits.append((t, n))
    return hits


def default_private_terms():
    """Identifiers this machine leaks by default: login name, home path, git identity and remotes."""
    import getpass, os, re, subprocess
    terms = set()
    user = getpass.getuser()
    if len(user) >= 3:
        terms.add(re.escape(user))
    home = os.path.expanduser('~').replace('\\', '/')
    terms.add(re.escape(home))
    terms.add(re.escape(home.replace('/', '\\')))
    for cmd in (['git', 'config', 'user.email'], ['git', 'config', 'user.name'], ['git', 'remote', '-v']):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=5).stdout
        except Exception:
            continue
        for tok in re.findall(r'[\w.+-]+@[\w.-]+|github\.com[:/][\w.-]+/[\w.-]+|^[\w.-]{4,}$', out, flags=re.M):
            terms.add(re.escape(tok.strip()))
    terms.add(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')   # IPv4
    terms.add(r'[\w.+-]+@(?!media|font|import|keyframes|supports)[\w-]+\.[\w.]+')  # e-mail
    return sorted(terms)


def write_page(out, body):
    from pathlib import Path
    Path(out).write_text(body, encoding='utf-8', newline='\n')
