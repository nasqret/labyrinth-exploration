#!/usr/bin/env python3
"""Toy programme for the labyrinth templates: how many triangles can a graph on n vertices have?

Claim tested: for n <= 7 the script lists exactly the triangle counts t that occur among all graphs on
n vertices (exhaustive: every graph on n vertices is a graph on n - 1 vertices plus one vertex joined
to a set S, which adds e(G[S]) triangles). For n = 8 it only samples graphs on 7 vertices, so some
values stay unknown. Proved (node th.topband): a graph other than K_n has at most C(n,3) - (n-2)
triangles, since a missing edge uv destroys the n - 2 triangles uvw.

Writes <labyrinth>/frontier.json and <labyrinth>/scatter.json. Standard library only, a few seconds.
Usage: python make_example.py path/to/labyrinth
"""
import itertools
import json
import random
import sys
from math import comb
from pathlib import Path

CONJ_N8 = [37, 42, 43, 46, 47, 48, 49]      # toy conjecture k.n8 (impossible for n = 8)


def graphs_with_counts(m):
    """(edge mask, edges, triangles) for every graph on m labelled vertices, plus the edge index."""
    E = list(itertools.combinations(range(m), 2))
    idx = {e: i for i, e in enumerate(E)}
    tri = [(1 << idx[(a, b)]) | (1 << idx[(a, c)]) | (1 << idx[(b, c)]) for a, b, c in itertools.combinations(range(m), 3)]
    out = [(g, bin(g).count("1"), sum(1 for t in tri if g & t == t)) for g in range(1 << len(E))]
    return out, E, idx


def subset_masks(m, E, idx):
    """For every vertex set S of [m], the mask of the edges inside S."""
    masks = []
    for S in range(1 << m):
        mk = 0
        for a, b in E:
            if S >> a & 1 and S >> b & 1:
                mk |= 1 << idx[(a, b)]
        masks.append((S, mk))
    return masks


def extend(graphs, m, E, idx):
    """All (edges, triangles) pairs on m + 1 vertices from all graphs on m vertices."""
    masks = subset_masks(m, E, idx)
    pairs = set()
    for g, e, t in graphs:
        for S, mk in masks:
            pairs.add((e + bin(S).count("1"), t + bin(g & mk).count("1")))
    return pairs


def main(lab):
    lab = Path(lab)
    sizes, points = [], []
    exact = {}
    for m in (3, 4, 5):
        exact[m] = {(e, t) for _, e, t in graphs_with_counts(m)[0]}
    g6, E6, idx6 = graphs_with_counts(6)
    exact[6] = {(e, t) for _, e, t in g6}
    exact[7] = extend(g6, 6, E6, idx6)
    # n = 8: a seeded sample of graphs on 7 vertices, each extended by every vertex set S
    rng = random.Random(8)
    E7 = list(itertools.combinations(range(7), 2))
    idx7 = {e: i for i, e in enumerate(E7)}
    tri7 = [(1 << idx7[(a, b)]) | (1 << idx7[(a, c)]) | (1 << idx7[(b, c)]) for a, b, c in itertools.combinations(range(7), 3)]
    sample = []
    for _ in range(8):
        p = rng.random()
        g = sum(1 << i for i in range(len(E7)) if rng.random() < p)
        sample.append((g, bin(g).count("1"), sum(1 for t in tri7 if g & t == t)))
    sampled8 = extend(sample, 7, E7, idx7)
    named8 = {comb(8, 3): "K_8 (family f.cliques)", comb(8, 3) - 6: "K_8 minus an edge", comb(7, 3): "K_7 plus an isolated vertex"}
    for n in range(3, 9):
        top = comb(n, 3)
        band = top - (n - 2)                 # th.topband: nothing strictly between band and top
        vals = {t for _, t in (exact[n] if n in exact else sampled8)} | (set() if n in exact else set(named8))
        intervals = []
        if band + 1 <= top - 1:
            intervals.append({"v0": band + 1, "v1": top - 1, "status": "impossible",
                              "why": "th.topband: a missing edge destroys n - 2 triangles"})
        if n in exact:
            for v in range(top + 1):
                if v not in vals and not band < v < top:
                    intervals.append({"v0": v, "v1": v, "status": "impossible",
                                      "why": "ex.small: no graph on n vertices has it (exhaustive)"})
        else:
            for v in CONJ_N8:
                intervals.append({"v0": v, "v1": v, "status": "conj-impossible", "why": "k.n8 (toy conjecture)"})
        sizes.append({
            "size": n, "label": f"n = {n}", "lo": 0, "hi": top, "step": 1,
            "realized": [[v, "exhaustive enumeration" if n in exact else named8.get(v, "sampled graph plus one vertex")] for v in sorted(vals)],
            "intervals": intervals,
            "bounds": {"upper": top, "upper_kind": "exact"},
        })
    for n in (5, 6):
        points += [{"x": e, "y": t, "series": f"n{n}", "src": "exhaustive"} for e, t in sorted(exact[n])]
    (lab / "frontier.json").write_text(json.dumps({
        "meta": {"size_name": "n", "value_name": "triangles", "value_scale": "linear"}, "sizes": sizes}, indent=1))
    (lab / "scatter.json").write_text(json.dumps({
        "title": "Edges versus triangles", "tab": "Edges and triangles",
        "subtitle": "Every (edges, triangles) pair that occurs on 5 and 6 vertices (exhaustive).",
        "x_name": "edges", "y_name": "triangles", "y_scale": "linear",
        "series": [{"key": "n5", "label": "n = 5"}, {"key": "n6", "label": "n = 6"}], "points": points}, indent=1))
    for s in sizes:
        missing = [v for v in range(s["hi"] + 1) if v not in {r[0] for r in s["realized"]}]
        print(f"n = {s['size']}: {len(s['realized'])} of {s['hi'] + 1} values realized; not realized: {missing}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "labyrinth")
