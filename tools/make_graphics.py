#!/usr/bin/env python3
"""Generate the README graphics in assets/ (SVG, light and dark mode, no external resources).

    python3 tools/make_graphics.py [output directory, default assets/]

The colours are the dashboard's tokens (templates/dashboard.html), so the pictures and the
dashboard read as one system. Rerun after editing; commit the SVGs together with this script.
"""
import math
import random
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets"

LIGHT = dict(bg="#EEF1F5", panel="#F7F8FA", card="#FFFFFF", ink="#17202B", ink2="#465163", ink3="#6F7A8C",
             rule="#D3D9E2", fog="#E2E6EC", fog2="#CFD6DF", neutral="#939DAC", known="#1F5FA6", wall="#B8462A",
             evid="#00897B", door="#A87400", conj="#7A4FB5", hunch="#D0508F")
DARK = dict(bg="#0B0F14", panel="#10151C", card="#141B24", ink="#E6EBF2", ink2="#AEB8C7", ink3="#808B9C",
            rule="#263041", fog="#1A212B", fog2="#242D39", neutral="#6E7989", known="#4A8CDA", wall="#D2603C",
            evid="#11A392", door="#B5821A", conj="#9670E2", hunch="#E45A9C")
SERIF = "Georgia, 'Iowan Old Style', 'Palatino Linotype', 'Times New Roman', serif"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"


def style(extra=""):
    def block(p):
        return "".join(f"--{k}:{v};" for k, v in p.items())
    return f"""<style>
svg {{ {block(LIGHT)} }}
@media (prefers-color-scheme: dark) {{ svg {{ {block(DARK)} }} }}
.bg {{ fill: var(--bg); }} .panel {{ fill: var(--panel); stroke: var(--rule); }} .card {{ fill: var(--card); stroke: var(--rule); }}
.ink {{ fill: var(--ink); }} .ink2 {{ fill: var(--ink2); }} .ink3 {{ fill: var(--ink3); }}
.serif {{ font-family: {SERIF}; }} .sans {{ font-family: {SANS}; }} .mono {{ font-family: {MONO}; }}
.f-known {{ fill: var(--known); }} .f-wall {{ fill: var(--wall); }} .f-evid {{ fill: var(--evid); }} .f-door {{ fill: var(--door); }}
.f-conj {{ fill: var(--conj); }} .f-hunch {{ fill: var(--hunch); }} .f-neutral {{ fill: var(--neutral); }}
.s-known {{ stroke: var(--known); }} .s-wall {{ stroke: var(--wall); }} .s-evid {{ stroke: var(--evid); }} .s-door {{ stroke: var(--door); }}
.s-conj {{ stroke: var(--conj); }} .s-hunch {{ stroke: var(--hunch); }} .s-ink {{ stroke: var(--ink); }} .s-ink3 {{ stroke: var(--ink3); }}
.s-rule {{ stroke: var(--rule); }} .s-neutral {{ stroke: var(--neutral); }}
{extra}
</style>"""


def defs():
    return """<defs>
  <pattern id="hatch-wall" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <rect width="7" height="7" style="fill: var(--panel)"/><line x1="0" y1="0" x2="0" y2="7" style="stroke: var(--wall); stroke-width: 3.2"/>
  </pattern>
  <pattern id="fogdots" width="9" height="9" patternUnits="userSpaceOnUse">
    <rect width="9" height="9" style="fill: var(--fog)"/><circle cx="2.5" cy="3" r="0.9" style="fill: var(--fog2)"/><circle cx="7" cy="7.5" r="0.9" style="fill: var(--fog2)"/>
  </pattern>
  <marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" style="fill: var(--ink3)"/>
  </marker>
  <marker id="arrow-known" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" style="fill: var(--known)"/>
  </marker>
</defs>"""


def svg(w, h, body, title, desc, extra_style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-labelledby="t d">\n<title id="t">{title}</title>\n<desc id="d">{desc}</desc>\n'
            f'{style(extra_style)}\n{defs()}\n{body}\n</svg>\n')


# Helvetica advance widths in 1/1000 em (from its AFM); other characters count as 600.
_W = dict(zip(" abcdefghijklmnopqrstuvwxyz", [278, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556,
                                              556, 556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500]))
_W.update(dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", [667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778,
                                                  667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611])))
_W.update({c: 556 for c in "0123456789?–"}, **{c: 278 for c in ",.;:/!"}, **{c: 333 for c in "-()"}, **{"·": 278, "'": 191, "“": 333, "”": 333, "≥": 549})


def fit(s, size, width, weight=400):
    """Refuse text that would overflow its box: Helvetica widths plus a margin for wider UI fonts."""
    est = sum(_W.get(c, 600) for c in s) / 1000 * size * (1.12 if weight >= 600 else 1.06)
    if est > width:
        raise ValueError(f"text does not fit ({est:.0f} > {width} px): {s!r}")
    return s


def text(x, y, s, cls="ink sans", size=16, weight=400, anchor="start", extra=""):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" {extra}>{s}</text>'


# ---------------------------------------------------------------- hero: the labyrinth
def maze(cols, rows, seed, start):
    rnd = random.Random(seed)
    adj = {(c, r): set() for c in range(cols) for r in range(rows)}
    seen, stack = {start}, [start]
    while stack:
        c, r = stack[-1]
        nb = [(c + dc, r + dr) for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (c + dc, r + dr) in adj and (c + dc, r + dr) not in seen]
        if not nb:
            stack.pop()
            continue
        n = rnd.choice(nb)
        adj[(c, r)].add(n)
        adj[n].add((c, r))
        seen.add(n)
        stack.append(n)
    return adj


def layout(seed, cols, rows, start, share):
    """The maze, its distances from the entrance, and the charted ball holding about `share` of the cells."""
    adj = maze(cols, rows, seed=seed, start=start)
    dist, parent, order = {start: 0}, {start: None}, [start]
    for u in order:
        for v in adj[u]:
            if v not in dist:
                dist[v], parent[v] = dist[u] + 1, u
                order.append(v)
    ds = sorted(dist.values())
    D = ds[int(share * len(ds))]
    charted = {u for u, d in dist.items() if d <= D}
    doors = {u for u, d in dist.items() if d == D + 1}
    # walled off: the charted dead-end branches (leaves and their short stems)
    walled = set()
    for u in charted:
        if len(adj[u]) == 1 and u != start:
            v, k = u, 0
            while v is not None and v in charted and len(adj[v]) <= 2 and k < 3:
                walled.add(v)
                v, k = parent[v], k + 1
    return adj, dist, parent, charted, doors, walled


def hero():
    W, H = 1280, 600
    cols, rows, cell = 20, 15, 32
    ox, oy = 572, 60
    start = (0, 7)
    # a seed whose picture shows every state: several doors, several dead ends, a long route
    def score(seed):
        adj, dist, parent, charted, doors, walled = layout(seed, cols, rows, start, 0.40)
        return (4 <= len(doors) <= 8) + (10 <= len(walled) <= 26) + (max(u[0] for u in doors) >= 10), seed
    seed = max(score(k) for k in range(1, 400))[1]
    adj, dist, parent, charted, doors, walled = layout(seed, cols, rows, start, 0.40)
    # the explorer's route: from the entrance to the door that is farthest to the right
    target = max(doors, key=lambda u: (u[0], -abs(u[1] - 7)))
    route = []
    v = target
    while v is not None:
        route.append(v)
        v = parent[v]
    route.reverse()
    on_route = set(route)
    walled -= on_route
    # hunches: a few spots in the dark, far from the map
    rnd = random.Random(5)
    dark = [u for u in adj if u not in charted and u not in doors and u[0] >= 12]
    hunches = rnd.sample(sorted(dark), 3)

    cx = lambda u: ox + u[0] * cell + cell / 2
    cy = lambda u: oy + u[1] * cell + cell / 2
    B = [f'<rect class="bg" x="0" y="0" width="{W}" height="{H}" rx="28"/>']
    # maze panel
    B.append(f'<rect class="panel" x="{ox - 16}" y="{oy - 16}" width="{cols * cell + 32}" height="{rows * cell + 32}" rx="18" stroke-width="1"/>')
    for u in adj:
        x, y = ox + u[0] * cell, oy + u[1] * cell
        if u in walled:
            B.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="url(#hatch-wall)"/>')
        elif u in charted:
            B.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" class="f-known" fill-opacity="0.16"/>')
        elif u in doors:
            B.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" class="f-door" fill-opacity="0.22"/>')
        else:
            B.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="url(#fogdots)"/>')
    # walls are known only where the map reaches: charted cells, doors, and their borders
    seen_walls = set()
    for u in adj:
        known = u in charted or u in doors
        c, r = u
        x, y = ox + c * cell, oy + r * cell
        for (dc, dr), seg in (((0, -1), (x, y, x + cell, y)), ((1, 0), (x + cell, y, x + cell, y + cell)),
                              ((0, 1), (x, y + cell, x + cell, y + cell)), ((-1, 0), (x, y, x, y + cell))):
            v = (c + dc, r + dr)
            if v in adj[u]:
                continue
            key = tuple(sorted([u, v]))
            if key in seen_walls:
                continue
            seen_walls.add(key)
            vk = v in charted or v in doors
            if known or vk:
                B.append(f'<line x1="{seg[0]}" y1="{seg[1]}" x2="{seg[2]}" y2="{seg[3]}" class="s-ink" stroke-width="3" stroke-linecap="round"/>')
            else:
                B.append(f'<line x1="{seg[0]}" y1="{seg[1]}" x2="{seg[2]}" y2="{seg[3]}" class="s-neutral" stroke-width="1.2" stroke-linecap="round" stroke-opacity="0.35"/>')
    # the entrance
    B.append(f'<line x1="{ox}" y1="{oy + 7 * cell + 4}" x2="{ox}" y2="{oy + 8 * cell - 4}" class="s-known" stroke-width="5" stroke-linecap="round"/>')
    # the route through the charted corridors
    pts = " ".join(f"{cx(u):.1f},{cy(u):.1f}" for u in route)
    B.append(f'<polyline points="{ox - 26},{cy(start):.1f} {pts}" fill="none" class="s-known" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
    B.append(f'<circle cx="{cx(target):.1f}" cy="{cy(target):.1f}" r="9" class="f-door" stroke-width="3" style="stroke: var(--panel)"/>')
    # doors: small gold bars where the charted region meets the unknown
    for d in doors:
        p = parent[d]
        if p is None:
            continue
        mx, my = (cx(d) + cx(p)) / 2, (cy(d) + cy(p)) / 2
        if d[0] != p[0]:
            B.append(f'<rect x="{mx - 3}" y="{my - 11}" width="6" height="22" rx="2" class="f-door"/>')
        else:
            B.append(f'<rect x="{mx - 11}" y="{my - 3}" width="22" height="6" rx="2" class="f-door"/>')
    for hnt in hunches:
        B.append(f'<circle cx="{cx(hnt):.1f}" cy="{cy(hnt):.1f}" r="10" fill="none" class="s-hunch" stroke-width="2.4" stroke-dasharray="3 3"/>')
        B.append(f'<circle cx="{cx(hnt):.1f}" cy="{cy(hnt):.1f}" r="2.6" class="f-hunch"/>')
    # text
    B.append(text(64, 112, "A CLAUDE CODE SKILL", "ink3 sans", 15, 700, extra='letter-spacing="2.2"'))
    B.append(text(60, 186, "Labyrinth", "ink serif", 68, 700))
    B.append(text(60, 258, "exploration", "ink serif", 68, 700))
    for i, line in enumerate(["Research as mapping a labyrinth: what is",
                              "proved, what is walled off, which doors",
                              "are open, and where it is still dark."]):
        B.append(text(64, 312 + 30 * i, line, "ink2 sans", 21))
    legend = [("known", "Charted: proved or exhaustive"), ("wall", "Walled off: refuted or impossible"),
              ("door", "Open doors: questions, conjectures"), ("hunch", "Hunches: speculation, kept vivid"),
              ("fog", "Still dark: unknown")]
    for i, (k, lab) in enumerate(legend):
        y = 430 + 30 * i
        if k == "known":
            B.append(f'<rect x="64" y="{y - 13}" width="22" height="16" rx="3" class="f-known" fill-opacity="0.85"/>')
        elif k == "wall":
            B.append(f'<rect x="64" y="{y - 13}" width="22" height="16" rx="3" fill="url(#hatch-wall)"/>')
        elif k == "door":
            B.append(f'<rect x="64" y="{y - 13}" width="22" height="16" rx="3" class="f-door"/>')
        elif k == "hunch":
            B.append(f'<circle cx="75" cy="{y - 5}" r="8" fill="none" class="s-hunch" stroke-width="2.2" stroke-dasharray="3 3"/>')
        else:
            B.append(f'<rect x="64" y="{y - 13}" width="22" height="16" rx="3" fill="url(#fogdots)" class="s-rule"/>')
        B.append(text(98, y, lab, "ink2 sans", 16))
    return svg(W, H, "\n".join(B), "Labyrinth exploration",
               "A maze in which the explored part is charted in blue, refuted dead ends are hatched in rust, "
               "open doors at the edge of the map are gold, hunches in the dark are dashed pink circles, and the "
               "rest of the maze is grey fog.")


# ---------------------------------------------------------------- the loop
def loop():
    W, H = 1200, 740
    cx0, cy0, rx, ry = 600, 412, 380, 222
    steps = [("Read the frontier", "pick 1–3 doors to enter"),
             ("Explore", "literature, code, examples"),
             ("Predict boldly", "a conjecture with its test"),
             ("Test and log", "every outcome is an event"),
             ("Referee", "own code; a verdict per item"),
             ("Update the map", "a dead end, or a new tier"),
             ("Look for shortcuts", "what can a new lemma remove?")]
    n = len(steps)
    ang = [-math.pi / 2 + 2 * math.pi * i / n for i in range(n)]
    pos = [(cx0 + rx * math.cos(a), cy0 + ry * math.sin(a)) for a in ang]
    B = [f'<rect class="bg" x="0" y="0" width="{W}" height="{H}" rx="28"/>']
    B.append(text(60, 70, "The loop", "ink serif", 34, 700))
    B.append(text(60, 102, "One iteration changes the map. A refutation is progress: it turns a corridor into a wall.", "ink2 sans", 17))
    # the ring
    B.append(f'<ellipse cx="{cx0}" cy="{cy0}" rx="{rx}" ry="{ry}" fill="none" class="s-rule" stroke-width="2" stroke-dasharray="2 7"/>')
    # arrows between consecutive steps along the ellipse
    for i in range(n):
        a0, a1 = ang[i], ang[(i + 1) % n] + (2 * math.pi if i == n - 1 else 0)
        pts = []
        for k in range(21):
            t = a0 + (a1 - a0) * (0.30 + 0.40 * k / 20)
            pts.append(f"{cx0 + rx * math.cos(t):.1f},{cy0 + ry * math.sin(t):.1f}")
        B.append(f'<polyline points="{" ".join(pts)}" fill="none" class="s-ink3" stroke-width="2.2" marker-end="url(#arrow)"/>')
    # the map in the centre
    B.append(f'<ellipse cx="{cx0}" cy="{cy0}" rx="172" ry="92" class="card" stroke-width="1.5"/>')
    B.append(text(cx0, cy0 - 22, "the map", "ink serif", 26, 700, "middle"))
    B.append(text(cx0, cy0 + 8, "knowledge graph · tiers T1–T6", "ink2 sans", 15, 400, "middle"))
    B.append(text(cx0, cy0 + 30, "frontier · state of the art", "ink2 sans", 15, 400, "middle"))
    B.append(text(cx0, cy0 + 52, "event log · dashboard", "ink2 sans", 15, 400, "middle"))
    colours = ["known", "evid", "conj", "known", "door", "wall", "evid"]
    for i, ((x, y), (title, sub)) in enumerate(zip(pos, steps)):
        w, h = 260, 66
        fit(title, 16, w - 64, 700)
        fit(sub, 12.5, w - 64)
        B.append(f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w}" height="{h}" rx="12" class="card" stroke-width="1.5"/>')
        B.append(f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="6" height="{h}" rx="3" class="f-{colours[i]}"/>')
        B.append(f'<circle cx="{x - w / 2 + 28:.1f}" cy="{y:.1f}" r="14" class="f-{colours[i]}"/>')
        B.append(text(x - w / 2 + 28, y + 5, str(i + 1), "sans", 15, 700, "middle", extra='style="fill: var(--card)"'))
        B.append(text(x - w / 2 + 52, y - 4, title, "ink sans", 16, 700))
        B.append(text(x - w / 2 + 52, y + 17, sub, "ink2 sans", 12.5))
    # side notes
    B.append(f'<rect x="36" y="626" width="262" height="90" rx="12" class="panel" stroke-width="1"/>')
    B.append(text(52, 654, "Refuted?", "sans", 15, 700, extra='style="fill: var(--wall)"'))
    B.append(text(52, 677, "A dead end with its lesson,", "ink2 sans", 14))
    B.append(text(52, 698, "then the modified statement.", "ink2 sans", 14))
    B.append(f'<rect x="902" y="626" width="262" height="90" rx="12" class="panel" stroke-width="1"/>')
    B.append(text(918, 654, "Saturated?", "sans", 15, 700, extra='style="fill: var(--conj)"'))
    B.append(text(918, 677, "Climb the ladder: new tools,", "ink2 sans", 14))
    B.append(text(918, 698, "extremes, … a broad attack.", "ink2 sans", 14))
    return svg(W, H, "\n".join(B), "The loop of labyrinth exploration",
               "Seven steps around a map: read the frontier, explore, predict boldly, test and log, referee, update "
               "the map, look for shortcuts. Refuted claims become dead ends with lessons; saturation is broken by "
               "an escalation ladder.")


# ---------------------------------------------------------------- tiers
def tiers():
    W, H = 1200, 470
    B = [f'<rect class="bg" x="0" y="0" width="{W}" height="{H}" rx="28"/>']
    B.append(text(60, 70, "Tiers keep proof apart from speculation", "ink serif", 34, 700))
    B.append(text(60, 102, "Every result, conjecture and hunch carries one. Nothing below T3 is ever cited as a fact.", "ink2 sans", 17))
    T = [("T1", "literature", "proved, or standard", "known"),
         ("T2", "proved here", "not peer reviewed", "known"),
         ("T3", "exhaustive", "certified computation", "known"),
         ("T4", "evidence", "sampled or partial", "evid"),
         ("T5", "conjecture", "with a stated test", "conj"),
         ("T6", "hunch", "a direction only", "hunch")]
    x0, y0, w, h, gap = 60, 168, 166, 132, 16
    for i, (t, a, b, c) in enumerate(T):
        x = x0 + i * (w + gap) + (24 if i >= 3 else 0)
        dash = ' stroke-dasharray="5 4"' if c == "hunch" else ""
        B.append(f'<rect x="{x}" y="{y0}" width="{w}" height="{h}" rx="14" class="card s-{c}" stroke-width="{2.4 if c == "hunch" else 1.5}"{dash}/>')
        if c != "hunch":
            B.append(f'<rect x="{x}" y="{y0}" width="{w}" height="10" rx="5" class="f-{c}"/>')
        B.append(text(x + 18, y0 + 52, t, f"mono f-{c}", 30, 700))
        B.append(text(x + 18, y0 + 86, fit(a, 16, w - 24, 700), "ink sans", 16, 700))
        B.append(text(x + 18, y0 + 109, fit(b, 13.5, w - 24), "ink2 sans", 13.5))
    # brackets
    def bracket(xa, xb, label, cls):
        y = y0 - 22
        return (f'<path d="M{xa},{y + 10} L{xa},{y} L{xb},{y} L{xb},{y + 10}" fill="none" class="s-{cls}" stroke-width="2"/>'
                + text((xa + xb) / 2, y - 10, label, f"sans f-{cls}", 14, 700, "middle"))
    B.append(bracket(x0 + 4, x0 + 3 * w + 2 * gap - 4, "may be cited as fact (for the stated sizes)", "known"))
    xs = x0 + 3 * (w + gap) + 24
    B.append(bracket(xs + 4, xs + w - 4, "evidence only", "evid"))
    B.append(bracket(xs + w + gap + 4, xs + 3 * w + 2 * gap - 4, "speculation, kept vivid", "conj"))
    # the divider between proof and speculation
    xd = x0 + 3 * (w + gap) + 4
    B.append(f'<line x1="{xd}" y1="{y0 - 8}" x2="{xd}" y2="{y0 + h + 8}" class="s-ink3" stroke-width="2" stroke-dasharray="4 4"/>')
    # review states
    yr = y0 + h + 62
    B.append(text(60, yr - 20, "T2 and T3 results also carry a review state; a referee raises it, never the tier:", "ink2 sans", 15))
    states = [("unreviewed", "neutral"), ("under-review", "door"), ("refereed (by whom)", "known"), ("human-checked", "evid")]
    x = 60
    for i, (s, c) in enumerate(states):
        wd = 26 + 9.2 * len(s)
        B.append(f'<rect x="{x}" y="{yr}" width="{wd:.0f}" height="34" rx="17" class="card s-{c}" stroke-width="2"/>')
        B.append(text(x + wd / 2, yr + 22, s, f"mono f-{c}", 14, 600, "middle"))
        if i < len(states) - 1:
            B.append(f'<line x1="{x + wd + 6:.0f}" y1="{yr + 17}" x2="{x + wd + 38:.0f}" y2="{yr + 17}" class="s-ink3" stroke-width="2" marker-end="url(#arrow)"/>')
        x += wd + 46
    B.append(text(x + 4, yr + 22, "→ T1 only once published", "ink3 sans", 14))
    return svg(W, H, "\n".join(B), "Tiers T1 to T6",
               "Six tiers: T1 literature, T2 proved here, T3 exhaustive computation may be cited as facts; T4 is "
               "evidence; T5 conjectures and T6 hunches are speculation. T2 and T3 results also carry a review state.")


# ---------------------------------------------------------------- campaigns
def campaign():
    W, H = 1200, 600
    B = [f'<rect class="bg" x="0" y="0" width="{W}" height="{H}" rx="28"/>']
    B.append(text(60, 70, "Campaigns: scaling the loop with agents", "ink serif", 34, 700))
    B.append(text(60, 102, "Many attackers, one referee per report, writers on copies, one coordinator who owns the canonical text.", "ink2 sans", 17))
    cols = [("Attack agents", "known", ["≥ 5 perspectives each", "closed routes listed", "status labels"]),
            ("Reports", "neutral", ["saved verbatim", "logged “under review”", "one directory each"]),
            ("Referees", "door", ["own code, own reasoning", "verdict per item", "fixes ready to apply"]),
            ("Writers", "conj", ["block + exact edits", "tested on a copy", "never upgrade a status"]),
            ("Coordinator", "evid", ["review against verdicts", "integrate, update map", "commit"])]
    x0, y0, w, h, gap = 60, 190, 200, 250, 26
    for i, (title, c, lines) in enumerate(cols):
        x = x0 + i * (w + gap)
        B.append(f'<rect x="{x}" y="{y0}" width="{w}" height="{h}" rx="16" class="card" stroke-width="1.5"/>')
        B.append(f'<rect x="{x}" y="{y0}" width="{w}" height="10" rx="5" class="f-{c}"/>')
        B.append(text(x + 18, y0 + 46, title, "ink sans", 18, 700))
        # little stacks of documents or agents
        for k in range(3 if i in (0, 2) else 2):
            xx, yy = x + 18 + k * 10, y0 + 66 + k * 8
            B.append(f'<rect x="{xx}" y="{yy}" width="58" height="40" rx="7" class="panel s-{c}" stroke-width="1.6"/>')
            B.append(f'<line x1="{xx + 10}" y1="{yy + 14}" x2="{xx + 46}" y2="{yy + 14}" class="s-rule" stroke-width="3" stroke-linecap="round"/>')
            B.append(f'<line x1="{xx + 10}" y1="{yy + 25}" x2="{xx + 38}" y2="{yy + 25}" class="s-rule" stroke-width="3" stroke-linecap="round"/>')
        for j, line in enumerate(lines):
            B.append(text(x + 18, y0 + 160 + 26 * j, fit("· " + line, 13, w - 30), "ink2 sans", 13))
        if i < len(cols) - 1:
            ya = y0 + 92
            B.append(f'<line x1="{x + w + 4}" y1="{ya}" x2="{x + w + gap - 4}" y2="{ya}" class="s-ink3" stroke-width="2.4" marker-end="url(#arrow)"/>')
    # literature agent feeding the attackers
    B.append(f'<rect x="{x0}" y="128" width="{w}" height="40" rx="10" class="panel s-evid" stroke-width="1.5"/>')
    B.append(text(x0 + 16, 154, "Literature agent", "sans f-evid", 15, 700))
    B.append(f'<line x1="{x0 + w / 2}" y1="170" x2="{x0 + w / 2}" y2="{y0 - 4}" class="s-ink3" stroke-width="2" marker-end="url(#arrow)"/>')
    B.append(text(x0 + w / 2 + 10, 182, "leads, as they come", "ink3 sans", 12))
    # verdicts strip
    xv = x0 + 2 * (w + gap)
    B.append(text(xv + w / 2, y0 + h + 30, "ESTABLISHED · WITH CORRECTIONS · GAP · FALSE", "mono f-door", 12.5, 600, "middle"))
    # rules
    rules = "one owner per file  ·  agents carry no authority  ·  stagger launches  ·  tell every agent about an incident"
    right = x0 + len(cols) * w + (len(cols) - 1) * gap
    B.append(f'<rect x="{x0}" y="{H - 82}" width="{right - x0}" height="46" rx="12" class="panel" stroke-width="1"/>')
    B.append(text((x0 + right) / 2, H - 52, rules, "ink2 sans", 15, 400, "middle"))
    return svg(W, H, "\n".join(B), "Campaigns of agents",
               "A pipeline: attack agents fed by a literature agent produce reports, saved verbatim; referees with "
               "their own code return verdicts; writers draft text and exact edits on a copy; the coordinator "
               "reviews, integrates and commits.")


GRAPHICS = (("hero", hero), ("loop", loop), ("tiers", tiers), ("campaign", campaign))


def main(out=ASSETS, verbose=True):
    out = Path(out)
    out.mkdir(exist_ok=True)
    for name, fn in GRAPHICS:
        (out / f"{name}.svg").write_text(fn())
        if verbose:
            print("wrote", out / f"{name}.svg")


if __name__ == "__main__":
    import sys
    main(*sys.argv[1:2])
