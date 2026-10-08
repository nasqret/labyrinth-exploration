#!/usr/bin/env python3
"""The labyrinth engine: one map of what is proved, computed, conjectured, refuted and still dark.

Files in <repo>/labyrinth/ (only knowledge.json is required):
    knowledge.json   curated nodes (results, conjectures, hunches, open doors, dead ends, families,
                     methods, sources); optional "meta" (dashboard title) and "frontier_history"
    events.jsonl     append-only log of discoveries
    frontier.json    the frontier map: for each size, which values are realized, impossible,
                     conditional, conjecturally impossible; everything else is unknown (see frontier())
    scatter.json     optional secondary scatter for the dashboard (see scatter())
    sota.json        optional state-of-the-art table with history (see sota_build())
    dashboard/template.html  ->  dashboard/index.html (data inlined) and dashboard/data.json
    STATUS.md        generated summary

Commands:
    python labyrinth/lab.py event TYPE "summary" [--nodes a,b] [--evidence e1,e2]
    python labyrinth/lab.py build     # data.json, index.html, STATUS.md and the optional tables
    python labyrinth/lab.py check     # validation; exit status 1 if anything is wrong
    python labyrinth/lab.py status    # the summary, printed

Every result has a *tier*, which keeps proof apart from speculation:
    T1 proved in the literature or standard
    T2 proved here, not peer reviewed (the "review" field records referee passes)
    T3 exhaustive computation (certified enumeration)
    T4 computational evidence (sampled or partial)
    T5 conjecture (a bold, testable prediction)
    T6 hunch (a vivid speculation, explicitly not a claim)
Dead ends, questions, families, methods and sources carry no tier.

Your computation scripts write frontier.json (and scatter.json); the engine itself contains nothing
specific to a domain. An optional blueprint of statements with dependencies can be imported from
tools/blueprint_data.py (a list N of dicts with id, kind, prov, title, stmt, where, group, uses).
"""
import heapq
import json
import math
import sys
from bisect import bisect_right
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labyrinth"
sys.path.insert(0, str(ROOT / "tools"))

TIERS = {
    "T1": "proved (literature or standard)",
    "T2": "proved here (not peer reviewed)",
    "T3": "exhaustive computation",
    "T4": "computational evidence",
    "T5": "conjecture",
    "T6": "hunch (speculation)",
}
KINDS = ["theorem", "exhaustive", "evidence", "conjecture", "hunch", "question",
         "deadend", "family", "method", "source"]
RELS = ["uses", "supports", "refutes", "modifies", "generalizes", "suggests", "answers",
        "tests", "instance-of", "cites"]
EVENT_TYPES = ["proposed", "computed", "proved", "refuted", "modified", "literature", "question",
               "answered", "reviewed", "documented", "monitor", "milestone"]
# Review state of a T2/T3 result (node field "review"). A referee is independent: its own code and
# its own reasoning, never the author's scripts. A referee raises the review state, never the tier.
REVIEW_STATES = ["unreviewed", "under-review", "refereed", "human-checked"]
# Frontier statuses, by priority: a value claimed by several statuses gets the highest one.
STATUSES = ["realized", "impossible", "gap-conditional", "conj-impossible", "unknown"]
PRIORITY = {"unknown": 0, "conj-impossible": 1, "gap-conditional": 2, "impossible": 3, "realized": 4}
RUN_LIMIT = 1500   # a size with more runs than this is drawn as bins
NBINS = 400
# Optional generated files (None: not written).
SOTA_TEX = None     # e.g. ROOT / "notes" / "sota-table.tex" (needs longtable, booktabs, array, cleveref)
SOTA_MD = None      # e.g. ROOT / "book" / "sota.md"
BOOK_STATUS = None  # e.g. ROOT / "book" / "labyrinth-status.md"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def review_state(n):
    rv = n.get("review")
    return rv.get("state") if isinstance(rv, dict) else None


def load_json(name, default=None):
    p = LAB / name
    return json.loads(p.read_text()) if p.exists() else default


# ---------------------------------------------------------------- knowledge graph
def load_knowledge():
    """knowledge.json = {"meta": {...}, "nodes": [...], "blueprint_overrides": {...}, "frontier_history": [...]};
    only "nodes" is needed, and a missing file counts as an empty map."""
    return load_json("knowledge.json", {"nodes": []})


def load_blueprint():
    """Statements with dependencies from tools/blueprint_data.py, if the project has a blueprint."""
    if not (ROOT / "tools" / "blueprint_data.py").exists():
        return []
    from blueprint_data import N     # a broken blueprint fails loudly instead of vanishing
    return N


def blueprint_tier(node):
    return {"classical": "T1", "literature": "T1", "project": "T2", "paper": "T2",
            "conjecture": "T5"}.get(node.get("prov"), "T2")


def merged_nodes():
    """Blueprint nodes (with overrides) plus the curated labyrinth nodes."""
    K = load_knowledge()
    over = K.get("blueprint_overrides", {})
    out = []
    for n in load_blueprint():
        o = over.get(n["id"], {})
        kind = o.get("kind") or ("conjecture" if n.get("prov") == "conjecture" else
                                 "method" if n.get("kind") == "definition" else "theorem")
        out.append({
            "id": n["id"], "kind": kind, "tier": o.get("tier", blueprint_tier(n)),
            "status": o.get("status", "open" if kind == "conjecture" else "established"),
            "title": n["title"], "statement": n.get("stmt", ""), "where": [n.get("where", "")],
            "links": [{"to": u, "rel": "uses"} for u in n.get("uses", [])] + o.get("links", []),
            "note": o.get("note", n.get("note", "")), "source": "blueprint",
            "tags": o.get("tags", [n.get("group", "")]),
            **{k: o[k] for k in ("review", "evidence", "why", "next", "test", "lesson") if k in o},
        })
    for n in K["nodes"]:
        m = dict(n)
        m.setdefault("links", [])
        m.setdefault("tags", [])
        m["source"] = "labyrinth"
        out.append(m)
    return out


# ---------------------------------------------------------------- events
def append_event(etype, summary, nodes=(), evidence=()):
    if etype not in EVENT_TYPES:
        sys.exit(f"unknown event type {etype!r}; use one of {', '.join(EVENT_TYPES)}")
    ev = {"ts": now(), "type": etype, "summary": summary,
          "nodes": list(nodes), "evidence": list(evidence)}
    with open(LAB / "events.jsonl", "a") as fh:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")
    return ev


def load_events(problems=None):
    """The event log; a malformed line is skipped (and reported to `problems` when given)."""
    p = LAB / "events.jsonl"
    out = []
    if not p.exists():
        return out
    for k, line in enumerate(p.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except ValueError:
            if problems is not None:
                problems.append(f"events.jsonl line {k}: invalid JSON")
            continue
        if not isinstance(e, dict):
            if problems is not None:
                problems.append(f"events.jsonl line {k}: not an object")
            continue
        out.append(e)
    return out


# ---------------------------------------------------------------- the frontier map
def claims_of(row):
    """The status claims of one size as (v0, v1, status, why), in the order given."""
    out = []
    for item in row.get("realized", []):
        v, why = (item[0], item[1] if len(item) > 1 else "") if isinstance(item, (list, tuple)) else (item, "")
        out.append((v, v, "realized", why))
    for iv in row.get("intervals", []):
        out.append((iv["v0"], iv["v1"], iv["status"], iv.get("why", "")))
    return out


def classify(lo, hi, step, claims):
    """Disjoint segments covering the admissible values lo, lo + step, ... <= hi.

    Each segment carries the highest-priority status that claims it (ties: the claim listed first);
    values nobody claims are unknown. A sweep over the claim ends, so large ranges cost nothing."""
    top = lo + (hi - lo) // step * step
    if top < lo:
        return []
    up = lambda a: lo if a <= lo else lo + -(-(a - lo) // step) * step
    down = lambda b: lo + (b - lo) // step * step
    snapped = [(lo, top, "unknown", "")]
    for a, b, st, why in claims:
        if b < lo or a > top:
            continue
        a2, b2 = up(max(a, lo)), down(min(b, top))
        if a2 <= b2:
            snapped.append((a2, b2, st, why))
    events = sorted([(a, 0, i) for i, (a, _, _, _) in enumerate(snapped)]
                    + [(b + step, 1, i) for i, (_, b, _, _) in enumerate(snapped)])
    heap, active, segs, k = [], set(), [], 0
    while k < len(events):
        x = events[k][0]
        while k < len(events) and events[k][0] == x:
            _, kind, i = events[k]
            if kind == 0:
                active.add(i)
                heapq.heappush(heap, (-PRIORITY[snapped[i][2]], i))
            else:
                active.discard(i)
            k += 1
        while heap and heap[0][1] not in active:
            heapq.heappop(heap)
        if not heap or k >= len(events) or x > top:
            continue
        i = heap[0][1]
        v0, v1, st, why = x, min(events[k][0] - step, top), snapped[i][2], snapped[i][3]
        if segs and segs[-1]["status"] == st and segs[-1]["why"] == why and segs[-1]["v1"] + step == v0:
            segs[-1]["v1"] = v1
        else:
            segs.append({"v0": v0, "v1": v1, "status": st, "why": why})
    return segs


def runs_of(segs, step):
    """Adjacent segments with the same status merged for display (the first reason is kept)."""
    runs = []
    for s in segs:
        if runs and runs[-1]["status"] == s["status"] and runs[-1]["v1"] + step == s["v0"]:
            r = runs[-1]
            r["v1"], r["n_reasons"] = s["v1"], r["n_reasons"] + 1
        else:
            runs.append({**s, "n_reasons": 1})
    for r in runs:
        if r.pop("n_reasons") > 1:
            r["why"] = (r["why"] + " (and other witnesses or reasons)").strip()
    return runs


def bins_of(segs, lo, top, step, log_scale):
    """Status counts in NBINS bins (geometric if log_scale and lo > 0, else linear)."""
    if log_scale and lo > 0:
        edges = [lo * ((top + step) / lo) ** (j / NBINS) for j in range(NBINS + 1)]
    else:
        edges = [lo + (top + step - lo) * j / NBINS for j in range(NBINS + 1)]
    snap = lambda a: lo + max(0, math.ceil((a - lo) / step)) * step
    edges = sorted({snap(e) for e in edges if e < top + step} | {lo, top + step})
    bins, j = [], 0
    for a, b in zip(edges, edges[1:]):
        b -= step                                   # bin = admissible values in [a, b]
        if a > b:
            continue
        counts = Counter()
        while j < len(segs) and segs[j]["v1"] < a:
            j += 1
        jj = j
        while jj < len(segs) and segs[jj]["v0"] <= b:
            s = segs[jj]
            lo2, hi2 = max(a, s["v0"]), min(b, s["v1"])
            if lo2 <= hi2:
                counts[s["status"]] += (hi2 - lo2) // step + 1
            jj += 1
        bins.append({"v0": a, "v1": b, "counts": dict(counts)})
    return bins


def frontier():
    """labyrinth/frontier.json -> one row per size for the dashboard and STATUS.md.

    frontier.json = {"meta": {"size_name": "n", "value_name": "triangles", "value_scale": "linear" | "log"},
                     "sizes": [{"size": 6, "label": "n = 6", "lo": 0, "hi": 20, "step": 1,
                                "realized": [[16, "K_6 minus an edge"], 12, ...],
                                "intervals": [{"v0": 17, "v1": 19, "status": "impossible", "why": "th.topband"}, ...],
                                "bounds": {"upper": 20, "upper_kind": "exact"}}]}
    Statuses: realized, impossible (proved or exhaustive), gap-conditional (impossible under a
    named hypothesis), conj-impossible (outside a conjectured bound); every other admissible value
    is unknown. A realized interval is allowed ("every value in [a, b] has a witness")."""
    F = load_json("frontier.json")
    if not F:
        return []
    log_scale = F.get("meta", {}).get("value_scale") == "log"
    name = F.get("meta", {}).get("size_name", "size")
    out = []
    for row in F["sizes"]:
        if not all(k in row for k in ("size", "lo", "hi")) or row.get("step", 1) <= 0:
            print(f"frontier: skipping an invalid row ({row.get('size', '?')}); run lab.py check", file=sys.stderr)
            continue
        lo, hi, step = row["lo"], row["hi"], row.get("step", 1)
        segs = classify(lo, hi, step, claims_of(row))
        top = segs[-1]["v1"] if segs else lo
        cnt = Counter()
        for s in segs:
            cnt[s["status"]] += (s["v1"] - s["v0"]) // step + 1
        total = sum(cnt.values())
        runs = runs_of(segs, step)
        realized = [s for s in segs if s["status"] == "realized"]
        out.append({
            "size": row["size"], "label": row.get("label", f"{name} = {row['size']}"),
            "lo": lo, "hi": top, "step": step, "admissible": total,
            "counts": dict(cnt), "resolved_fraction": (cnt["realized"] + cnt["impossible"]) / total if total else 1.0,
            "runs": runs if len(runs) <= RUN_LIMIT else None,
            "bins": None if len(runs) <= RUN_LIMIT else bins_of(segs, lo, top, step, log_scale),
            "bounds": row.get("bounds", {}),
            "best_known": max(s["v1"] for s in realized) if realized else None,
            "note": row.get("note", ""),
        })
    return out


def frontier_conflicts():
    """Values claimed both realized and impossible: one of the two claims is wrong."""
    F = load_json("frontier.json") or {"sizes": []}
    problems = []
    for row in F["sizes"]:
        if not all(k in row for k in ("size", "lo", "hi")) or row.get("step", 1) <= 0:
            continue                                # reported by check() as a malformed row
        lo, step = row["lo"], row.get("step", 1)
        claims = claims_of(row)
        imp = []                                    # impossible claims, merged into disjoint intervals
        for a, b in sorted((a, b) for a, b, st, _ in claims if st == "impossible"):
            if imp and a <= imp[-1][1]:
                imp[-1][1] = max(imp[-1][1], b)
            else:
                imp.append([a, b])
        starts = [a for a, _ in imp]
        for a, b, st, _ in claims:
            if st != "realized":
                continue
            k = bisect_right(starts, b) - 1         # ends increase with k: walk back while they reach a
            while k >= 0 and imp[k][1] >= a:
                x0, x1 = max(a, imp[k][0]), min(b, imp[k][1])
                first = lo + max(0, math.ceil((x0 - lo) / step)) * step   # first admissible value >= x0
                if first <= x1:
                    problems.append(f"frontier size {row['size']}: {first} is claimed realized and impossible")
                    break
                k -= 1
    return problems


def scatter():
    """labyrinth/scatter.json (optional): {"title", "x_name", "y_name", "y_scale": "linear" | "log",
    "series": [{"key", "label"}], "points": [{"x", "y", "series", "src"}]}."""
    return load_json("scatter.json")


# ---------------------------------------------------------------- state of the art table
SOTA_KINDS = ["proved", "exhaustive", "computed", "partial", "conjecture", "refuted"]
TEX_ESC = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
           "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
           "|": r"\textbar{}", "<": r"\textless{}", ">": r"\textgreater{}"}


def tex_escape(s):
    """Plain text for LaTeX (used where no *_tex field is given)."""
    return "".join(TEX_ESC.get(c, c) for c in str(s))


def md_cell(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def sota_build():
    """labyrinth/sota.json -> data for the dashboard, plus the optional LaTeX and Markdown tables.

    sota.json = {"groups": [names], "entries": [{id, group, cls, result, status, refs, lit, updated,
    previous: [{date, was}]}]}, with optional cls_tex and result_tex for LaTeX. To record progress,
    move the old result into `previous` (with its date), write the new one, and rebuild.
    """
    S = load_json("sota.json")
    if S is None:
        return None
    groups = [(g, [e for e in S.get("entries", []) if e.get("group") == g]) for g in S.get("groups", [])]
    groups = [(g, rows) for g, rows in groups if rows]
    if SOTA_TEX:
        T = ["% Generated by labyrinth/lab.py from labyrinth/sota.json. Do not edit by hand.",
             r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.21\textwidth}>{\raggedright\arraybackslash}p{0.38\textwidth}"
             r">{\raggedright\arraybackslash}p{0.13\textwidth}>{\raggedright\arraybackslash}p{0.20\textwidth}@{}}",
             r"\toprule", r"class & best known result & status & proof \\", r"\midrule", r"\endhead"]
        for g, rows in groups:
            T.append(r"\multicolumn{4}{@{}l}{\emph{" + tex_escape(g) + r"}}\\[2pt]")
            for e in rows:
                refs = r"\cref{" + ",".join(e.get("refs", [])) + "}" if e.get("refs") else ""
                lit = r"\cite{" + ",".join(e.get("lit", [])) + "}" if e.get("lit") else ""
                where = "; ".join(x for x in (refs, lit) if x)
                cls = e.get("cls_tex", tex_escape(e.get("cls", "")))
                res = e.get("result_tex", tex_escape(e.get("result", "")))
                T.append(f"{cls} & {res} & {tex_escape(e.get('status', ''))} & {where}\\\\")
            T.append(r"\addlinespace")
        T += [r"\bottomrule", r"\end{longtable}"]
        Path(SOTA_TEX).write_text("\n".join(T) + "\n")
    if SOTA_MD:
        M = ["# State of the art (generated)", "",
             "The best known result for each question, with its status and where it is proved. Generated by "
             "`labyrinth/lab.py build` from `labyrinth/sota.json`; *previously* keeps the history of each entry.", ""]
        for g, rows in groups:
            M += [f"## {g}", "", "| class | best known result | status | proof | updated | previously |",
                  "|---|---|---|---|---|---|"]
            for e in rows:
                where = " · ".join(x for x in (", ".join(f"`{r}`" for r in e.get("refs", [])), ", ".join(e.get("lit", []))) if x)
                prev = "; ".join(f"{p.get('date', '?')}: {p.get('was', '?')}" for p in e.get("previous", [])) or "–"
                M.append("| " + " | ".join(md_cell(x) for x in (e.get("cls", ""), e.get("result", ""), e.get("status", ""),
                                                                where, e.get("updated", ""), prev)) + " |")
            M.append("")
        Path(SOTA_MD).write_text("\n".join(M))
    return S


# ---------------------------------------------------------------- build / check / status
def build():
    nodes = merged_nodes()
    events = load_events()
    fr = frontier()
    K = load_knowledge()
    meta = {**(load_json("frontier.json") or {}).get("meta", {}), **K.get("meta", {})}
    data = {
        "generated": now(), "tiers": TIERS, "meta": meta,
        "nodes": nodes, "events": events, "frontier": fr, "scatter": scatter(),
        "frontier_history": K.get("frontier_history", []),
        "sota": sota_build(), "summary": summary(nodes, fr),
    }
    (LAB / "dashboard").mkdir(exist_ok=True)
    blob = json.dumps(data, ensure_ascii=False)
    (LAB / "dashboard" / "data.json").write_text(blob)
    tpl = LAB / "dashboard" / "template.html"
    if not tpl.exists():
        print("build: no dashboard/template.html, so no index.html (copy templates/dashboard.html there)", file=sys.stderr)
    else:
        safe = blob.replace("</", "<\\/")
        page = tpl.read_text()
        key = "const DATA = /*LABYRINTH_DATA*/null" if "const DATA = /*LABYRINTH_DATA*/null" in page else "/*LABYRINTH_DATA*/null"
        (LAB / "dashboard" / "index.html").write_text(page.replace(key, key.replace("/*LABYRINTH_DATA*/null", safe), 1))
    md = status_md(nodes, fr, events)
    (LAB / "STATUS.md").write_text(md)
    if BOOK_STATUS:
        Path(BOOK_STATUS).write_text("# Labyrinth status (generated)\n\n" + md.split("\n", 1)[1])
    return data


def summary(nodes, fr):
    c = Counter((n.get("kind"), n.get("status")) for n in nodes)
    t = Counter(n.get("tier") for n in nodes)
    return {
        "by_tier": {k: t.get(k, 0) for k in TIERS},
        "conjectures_open": sum(v for (k, s), v in c.items() if k == "conjecture" and s == "open"),
        "conjectures_modified": sum(v for (k, s), v in c.items() if k == "conjecture" and s == "modified"),
        "deadends": sum(v for (k, s), v in c.items() if k == "deadend"),
        "questions_open": sum(v for (k, s), v in c.items() if k == "question" and s != "answered"),
        "hunches_live": sum(v for (k, s), v in c.items() if k == "hunch" and s in ("live", "testing")),
        "under_review": sum(1 for n in nodes if review_state(n) == "under-review"),
        "resolved_by_size": {str(m["size"]): round(m["resolved_fraction"], 4) for m in fr},
    }


def status_md(nodes, fr, events):
    L = ["# Labyrinth status", "",
         f"Generated {now()} by `labyrinth/lab.py build`. Do not edit by hand.", ""]
    if fr:
        L += ["## The frontier", "",
              "| size | admissible | realized | impossible | conditional | conj. impossible | unknown | resolved | bounds |",
              "|---|---|---|---|---|---|---|---|---|"]
        for m in fr:
            c = m["counts"]
            b = ", ".join(f"{k} {v}" for k, v in m["bounds"].items())
            L.append(f"| {m['label']} | {m['admissible']} | {c.get('realized', 0)} | {c.get('impossible', 0)} | "
                     f"{c.get('gap-conditional', 0)} | {c.get('conj-impossible', 0)} | {c.get('unknown', 0)} | "
                     f"{100 * m['resolved_fraction']:.1f}% | {b} |")
    for kind, head in (("conjecture", "Conjectures"), ("question", "Open doors (questions)"),
                       ("hunch", "Hunches (speculation, not claims)"), ("deadend", "Dead ends (refuted)")):
        rows = [n for n in nodes if n.get("kind") == kind]
        L += ["", f"## {head} ({len(rows)})", ""]
        for n in rows:
            L.append(f"- **{n.get('title', '?')}** [`{n.get('id', '?')}`, {n.get('status', '')}] {n.get('statement', '')}")
    review = [n for n in nodes if review_state(n) == "under-review"]
    if review:
        L += ["", f"## Under review ({len(review)})", ""] + [f"- **{n.get('title', '?')}** [`{n.get('id', '?')}`]" for n in review]
    L += ["", f"## Recent events ({len(events)} total)", ""]
    for e in events[-25:]:
        L.append(f"- {str(e.get('ts', ''))[:16]} · {e.get('type', '?')} · {e.get('summary', '')}")
    return "\n".join(L) + "\n"


def check():
    nodes = merged_nodes()
    ids = {n.get("id") for n in nodes}
    problems = []
    for k, n in enumerate(nodes):
        nid = n.get("id") or f"node #{k + 1} (no id)"
        kind = n.get("kind")
        if not n.get("id"):
            problems.append(f"{nid}: missing id")
        if kind not in KINDS:
            problems.append(f"{nid}: unknown kind {kind}")
        if kind in ("theorem", "exhaustive", "evidence", "conjecture", "hunch") and n.get("tier") not in TIERS:
            problems.append(f"{nid}: missing tier")
        if kind == "hunch" and n.get("tier") != "T6":
            problems.append(f"{nid}: a hunch must be tier T6")
        if kind == "theorem" and n.get("tier") in ("T5", "T6"):
            problems.append(f"{nid}: a theorem cannot be a conjecture or hunch")
        if kind == "conjecture" and n.get("status") == "open" and not n.get("test") and n.get("source") == "labyrinth":
            problems.append(f"{nid}: open conjecture without a stated test")
        if kind == "deadend" and not n.get("lesson"):
            problems.append(f"{nid}: a dead end needs its lesson")
        rv = n.get("review")
        if rv is not None and not isinstance(rv, dict):
            problems.append(f"{nid}: review must be an object {{state, by, verdict, date}}")
        elif rv is not None:
            if rv.get("state") not in REVIEW_STATES:
                problems.append(f"{nid}: unknown review state {rv.get('state')}")
            elif rv["state"] in ("refereed", "human-checked") and not rv.get("by"):
                problems.append(f"{nid}: a refereed result names its referees (review.by)")
        for l in n.get("links", []):
            if not isinstance(l, dict) or "to" not in l:
                problems.append(f"{nid}: a link needs a target (to)")
                continue
            if l["to"] not in ids:
                problems.append(f"{nid}: link to unknown node {l['to']}")
            if l.get("rel") not in RELS:
                problems.append(f"{nid}: unknown relation {l.get('rel')}")
    for e in load_events(problems):
        ts = e.get("ts", "?")
        if e.get("type") not in EVENT_TYPES:
            problems.append(f"event {ts}: unknown type {e.get('type')}")
        for i in e.get("nodes", []):
            if i not in ids:
                problems.append(f"event {ts}: unknown node {i}")
    F = load_json("frontier.json")
    if F is not None:
        for row in F.get("sizes", []):
            miss = [k for k in ("size", "lo", "hi") if k not in row]
            if miss:
                problems.append(f"frontier row {row.get('size', '?')}: missing {', '.join(miss)}")
            elif row.get("step", 1) <= 0:
                problems.append(f"frontier size {row['size']}: step must be positive")
            for iv in row.get("intervals", []):
                if iv.get("status") not in PRIORITY or iv.get("status") == "unknown":
                    problems.append(f"frontier size {row.get('size', '?')}: unknown status {iv.get('status')}")
        problems += frontier_conflicts()
    S = load_json("sota.json")
    if S is not None:
        for key in ("groups", "entries"):
            if key not in S:
                problems.append(f"sota.json: missing {key}")
        S.setdefault("groups", [])
        for e in S.get("entries", []):
            eid = e.get("id", "?")
            miss = [k for k in ("id", "group", "cls", "result", "status", "refs", "lit", "updated") if k not in e]
            if miss:
                problems.append(f"sota {eid}: missing {', '.join(miss)}")
            if e.get("group") not in S["groups"]:
                problems.append(f"sota {eid}: unknown group {e.get('group')}")
            if "kind" in e and e["kind"] not in SOTA_KINDS:
                problems.append(f"sota {eid}: kind must be one of {', '.join(SOTA_KINDS)}")
            if any(not {"date", "was"} <= set(p) for p in e.get("previous", [])):
                problems.append(f"sota {eid}: every previous entry needs a date and the old result (was)")
    return problems


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[0]
    if cmd == "event":
        if len(argv) < 3 or len(argv) % 2 == 0:
            print('usage: lab.py event TYPE "summary" [--nodes a,b] [--evidence e1,e2]', file=sys.stderr)
            return 2
        etype, summ = argv[1], argv[2]
        opts = dict(zip(argv[3::2], argv[4::2]))
        unknown = set(opts) - {"--nodes", "--evidence"}
        if unknown:
            print(f"unknown option(s): {', '.join(sorted(unknown))}; use --nodes and --evidence", file=sys.stderr)
            return 2
        ev = append_event(etype, summ, [x for x in opts.get("--nodes", "").split(",") if x],
                          [x for x in opts.get("--evidence", "").split(",") if x])
        print(json.dumps(ev, ensure_ascii=False))
    elif cmd == "build":
        d = build()
        print(json.dumps(d["summary"], indent=1))
    elif cmd == "check":
        p = check()
        print("\n".join(p) if p else "ok")
        return 1 if p else 0
    elif cmd == "status":
        print(status_md(merged_nodes(), frontier(), load_events()))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
