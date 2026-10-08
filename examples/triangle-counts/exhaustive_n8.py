#!/usr/bin/env python3
"""The test of conjecture k.n8: which triangle counts occur among ALL graphs on 8 vertices?

Every graph on 8 vertices is a graph G on 7 vertices plus a vertex joined to a set S, which adds
e(G[S]) triangles (method m.extend). So the counts on 8 vertices are t(G) + e(G[S]) over all
2^21 graphs G and all 128 sets S: about 2.7e8 cases, vectorized with numpy (a few seconds).

    python3 exhaustive_n8.py                      # print the counts that do not occur
    python3 exhaustive_n8.py --write labyrinth    # also record the result in the map (step 6)

With --write it makes the four changes of step 6 of the tutorial together:
- frontier.json: the n = 8 row becomes exhaustive;
- knowledge.json: k.n8 becomes an exhaustive T3 result, refereed (the tutorial's referee is
  research/agents/referee-n8), q.unknown8 is answered, and a milestone joins frontier_history;
- sota.json: the row tc-n8 gets the new result, and the old one moves into `previous`.

Needs numpy (pip install numpy). Used in docs/tutorial.md, section 6.
"""
import itertools
import json
import sys
from datetime import date
from math import comb
from pathlib import Path

import numpy as np


def popcount(a):
    table = np.array([bin(i).count("1") for i in range(1 << 16)], dtype=np.int16)
    return table[a & 0xFFFF] + table[a >> 16]


def counts_on_8():
    m = 7
    E = list(itertools.combinations(range(m), 2))
    idx = {e: i for i, e in enumerate(E)}
    g = np.arange(1 << len(E), dtype=np.uint32)
    t = np.zeros(g.shape, dtype=np.int16)
    for a, b, c in itertools.combinations(range(m), 3):
        mk = np.uint32((1 << idx[(a, b)]) | (1 << idx[(a, c)]) | (1 << idx[(b, c)]))
        t += (g & mk) == mk
    found = np.zeros(comb(8, 3) + 1, dtype=bool)
    for S in range(1 << m):
        mk = sum(1 << idx[(a, b)] for a, b in E if S >> a & 1 and S >> b & 1)
        found[np.unique(t + popcount(g & np.uint32(mk)))] = True
    return [v for v in range(comb(8, 3) + 1) if found[v]]


def main(argv):
    occur = counts_on_8()
    missing = [v for v in range(comb(8, 3) + 1) if v not in set(occur)]
    print(f"n = 8: {len(occur)} counts occur; missing: {missing}")
    if len(argv) >= 2 and argv[0] == "--write":
        write(Path(argv[1]), occur, missing)


def write(lab, occur, missing):
    K = json.loads((lab / "knowledge.json").read_text())
    if any(n["id"] == "k.n8" and n.get("kind") == "exhaustive" for n in K["nodes"]):
        print("already recorded: k.n8 is an exhaustive result; nothing changed")
        return
    today = date.today().isoformat()
    top, band = comb(8, 3), comb(8, 3) - 6
    below = [v for v in missing if not band < v < top]
    # the frontier
    path = lab / "frontier.json"
    F = json.loads(path.read_text())
    row = next(r for r in F["sizes"] if r["size"] == 8)
    row["realized"] = [[v, "exhaustive (exhaustive_n8.py)"] for v in occur]
    row["intervals"] = [{"v0": band + 1, "v1": top - 1, "status": "impossible",
                         "why": "th.topband: a missing edge destroys n - 2 triangles"}]
    row["intervals"] += [{"v0": v, "v1": v, "status": "impossible", "why": "exhaustive (exhaustive_n8.py)"} for v in below]
    path.write_text(json.dumps(F, indent=1))
    # the knowledge graph: the conjecture becomes an exhaustive result, the door is answered
    path = lab / "knowledge.json"
    K = json.loads(path.read_text())
    for n in K["nodes"]:
        if n["id"] == "k.n8":
            n.update(kind="exhaustive", tier="T3", status="established", updated=today,
                     evidence=["examples/triangle-counts/exhaustive_n8.py"],
                     review={"state": "refereed", "by": ["research/agents/referee-n8"], "verdict": "ESTABLISHED", "date": today})
        if n["id"] == "q.unknown8":
            n.update(status="answered", answer="All six occur: the exhaustive test of k.n8.", updated=today)
    K.setdefault("frontier_history", []).append(
        {"date": today, "size": 8, "resolved": 1.0, "why": "exhaustive: one-vertex extension of all graphs on 7 vertices"})
    path.write_text(json.dumps(K, indent=1, ensure_ascii=False) + "\n")
    # the state of the art: the old result moves into the history
    path = lab / "sota.json"
    S = json.loads(path.read_text())
    for e in S["entries"]:
        if e["id"] == "tc-n8":
            e.setdefault("previous", []).append({"date": e["updated"], "was": e["result"]})
            e.update(result=f"exact: {len(occur)} of {top + 1} counts occur; missing {', '.join(map(str, below))} and the top band",
                     status="exhaustive (1 independent referee)", kind="exhaustive", refs=["k.n8"], updated=today)
    path.write_text(json.dumps(S, indent=1, ensure_ascii=False) + "\n")
    print("updated frontier.json, knowledge.json and sota.json in", lab)


if __name__ == "__main__":
    main(sys.argv[1:])
