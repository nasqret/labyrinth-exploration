"""Tests for the labyrinth engine (templates/lab.py) and the runnable example.

    python3 -m unittest discover -s tests -v

Standard library only. The frontier classifier is checked against a brute-force reference on
random inputs; the example is built end to end in a temporary directory.
"""
import importlib.util
import json
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LAB_PY = REPO / "templates" / "lab.py"
EXAMPLE = REPO / "examples" / "triangle-counts"
STATUSES = ["realized", "impossible", "gap-conditional", "conj-impossible"]


def load_lab():
    spec = importlib.util.spec_from_file_location("lab_under_test", LAB_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(mod)
    return mod


lab = load_lab()


def brute(lo, hi, step, claims):
    """Status of every admissible value, by the precedence rule (first claim wins ties)."""
    out, v = {}, lo
    while v <= hi:
        best = (0, -1, "unknown", "")
        for i, (a, b, st, why) in enumerate(claims):
            if a <= v <= b:
                p = lab.PRIORITY[st]
                if p > best[0] or (p == best[0] and best[1] == -1):
                    best = (p, i, st, why)
        out[v] = (best[2], best[3])
        v += step
    return out


def run(cmd, cwd):
    return subprocess.run([sys.executable, *cmd], cwd=cwd, capture_output=True, text=True)


class Classifier(unittest.TestCase):
    def test_against_brute_force(self):
        rnd = random.Random(1)
        for _ in range(800):
            step = rnd.choice([1, 2, 3, 5])
            lo = rnd.randint(-5, 20)
            hi = lo + rnd.randint(-3, 120)
            claims = [(a, a + rnd.randint(0, 40) * rnd.choice([0, 1]), rnd.choice(STATUSES), rnd.choice(["x", "y", ""]))
                      for a in (rnd.randint(lo - 10, hi + 10) for _ in range(rnd.randint(0, 12)))]
            segs = lab.classify(lo, hi, step, claims)
            got = {}
            for s in segs:
                self.assertEqual((s["v0"] - lo) % step, 0)
                for v in range(s["v0"], s["v1"] + 1, step):
                    self.assertNotIn(v, got)
                    got[v] = (s["status"], s["why"])
            self.assertEqual(got, brute(lo, hi, step, claims))
            for x, y in zip(segs, segs[1:]):
                self.assertEqual(x["v1"] + step, y["v0"])
            if segs:
                top = segs[-1]["v1"]
                for log in (False, True):
                    bins = lab.bins_of(segs, lo, top, step, log)
                    total = Counter()
                    for b in bins:
                        total.update(b["counts"])
                    self.assertEqual(total, Counter(st for st, _ in got.values()))
                    self.assertEqual((bins[0]["v0"], bins[-1]["v1"]), (lo, top))

    def test_conflicts_against_brute_force(self):
        rnd = random.Random(7)
        tmp = Path(tempfile.mkdtemp())
        (tmp / "labyrinth").mkdir()
        old = lab.LAB
        lab.LAB = tmp / "labyrinth"
        try:
            for _ in range(600):
                step, lo = rnd.choice([1, 2, 3]), rnd.randint(0, 10)
                hi = lo + rnd.randint(0, 80)
                real = [(v, v) for v in rnd.sample(range(lo - 5, hi + 5), rnd.randint(0, 8))]
                real += [(a, a + rnd.randint(1, 15)) for a in rnd.sample(range(lo - 5, hi + 5), rnd.randint(0, 3))]
                imps = [(a, a + rnd.randint(0, 20)) for a in rnd.sample(range(lo - 5, hi + 5), rnd.randint(0, 5))]
                row = {"size": 1, "lo": lo, "hi": hi, "step": step,
                       "realized": [[a, ""] for a, b in real if a == b],
                       "intervals": [{"v0": a, "v1": b, "status": "realized"} for a, b in real if a != b]
                                    + [{"v0": a, "v1": b, "status": "impossible"} for a, b in imps]}
                (lab.LAB / "frontier.json").write_text(json.dumps({"sizes": [row]}))
                adm = lambda v: v >= lo and (v - lo) % step == 0
                expected = any(adm(v) and any(a2 <= v <= b2 for a2, b2 in imps) for a, b in real for v in range(a, b + 1))
                self.assertEqual(bool(lab.frontier_conflicts()), expected)
        finally:
            lab.LAB = old
            shutil.rmtree(tmp)


class Escaping(unittest.TestCase):
    def test_tex(self):
        self.assertEqual(lab.tex_escape("a_b & 50% $x$ #1 {y} ~ ^ | < >"),
                         r"a\_b \& 50\% \$x\$ \#1 \{y\} \textasciitilde{} \textasciicircum{} \textbar{} \textless{} \textgreater{}")
        self.assertEqual(lab.tex_escape("\\"), r"\textbackslash{}")

    def test_markdown(self):
        self.assertEqual(lab.md_cell("a | b\nc"), "a \\| b c")


class Projects(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "labyrinth" / "dashboard").mkdir(parents=True)
        shutil.copy(LAB_PY, self.tmp / "labyrinth" / "lab.py")
        shutil.copy(REPO / "templates" / "dashboard.html", self.tmp / "labyrinth" / "dashboard" / "template.html")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_empty_project_builds(self):
        self.assertEqual(run(["labyrinth/lab.py", "check"], self.tmp).stdout.strip(), "ok")
        r = run(["labyrinth/lab.py", "build"], self.tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.tmp / "labyrinth" / "dashboard" / "index.html").exists())

    def test_example_builds(self):
        for f in ("knowledge.json", "events.jsonl", "sota.json"):
            shutil.copy(EXAMPLE / f, self.tmp / "labyrinth" / f)
        r = run([str(EXAMPLE / "make_example.py"), "labyrinth"], self.tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(run(["labyrinth/lab.py", "check"], self.tmp).stdout.strip(), "ok")
        r = run(["labyrinth/lab.py", "build"], self.tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads((self.tmp / "labyrinth" / "dashboard" / "data.json").read_text())
        res = {m["size"]: m["resolved_fraction"] for m in data["frontier"]}
        self.assertEqual([res[n] for n in range(3, 8)], [1.0] * 5)
        self.assertAlmostEqual(res[8], 44 / 57)
        n8 = next(m for m in data["frontier"] if m["size"] == 8)
        self.assertEqual(n8["counts"], {"realized": 39, "impossible": 5, "conj-impossible": 7, "unknown": 6})
        self.assertEqual(data["summary"]["under_review"], 1)
        html = (self.tmp / "labyrinth" / "dashboard" / "index.html").read_text()
        self.assertNotIn("/*LABYRINTH_DATA*/null", html)

    @unittest.skipUnless(importlib.util.find_spec("numpy"), "the exhaustive test needs numpy")
    def test_tutorial_iteration_leaves_a_consistent_map(self):
        """docs/tutorial.md, section 6: after exhaustive_n8.py --write, every artifact agrees."""
        for f in ("knowledge.json", "events.jsonl", "sota.json"):
            shutil.copy(EXAMPLE / f, self.tmp / "labyrinth" / f)
        self.assertEqual(run([str(EXAMPLE / "make_example.py"), "labyrinth"], self.tmp).returncode, 0)
        r = run([str(EXAMPLE / "exhaustive_n8.py"), "--write", "labyrinth"], self.tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("missing: [37, 42, 43, 46, 47, 48, 49, 51, 52, 53, 54, 55]", r.stdout)
        self.assertEqual(run(["labyrinth/lab.py", "check"], self.tmp).stdout.strip(), "ok")
        self.assertEqual(run(["labyrinth/lab.py", "build"], self.tmp).returncode, 0)
        data = json.loads((self.tmp / "labyrinth" / "dashboard" / "data.json").read_text())
        self.assertEqual({m["size"]: m["resolved_fraction"] for m in data["frontier"]}[8], 1.0)
        nodes = {n["id"]: n for n in data["nodes"]}
        self.assertEqual((nodes["k.n8"]["kind"], nodes["k.n8"]["tier"]), ("exhaustive", "T3"))
        self.assertEqual(nodes["q.unknown8"]["status"], "answered")
        self.assertEqual(data["summary"]["questions_open"], 0)
        self.assertEqual(data["frontier_history"][-1]["resolved"], 1.0)
        row = next(e for e in data["sota"]["entries"] if e["id"] == "tc-n8")
        self.assertEqual(row["kind"], "exhaustive")
        self.assertEqual(row["previous"][-1]["was"], "39 of 57 counts realized, 5 impossible, 7 conjecturally impossible, 6 unknown")

    def test_check_catches_planted_errors(self):
        L = self.tmp / "labyrinth"
        (L / "knowledge.json").write_text(json.dumps({"nodes": [
            {"id": "a", "kind": "theorem", "tier": "T2", "status": "established", "title": "A", "statement": "a", "review": "refereed"},
            {"id": "b", "kind": "theorem", "tier": "T2", "status": "established", "title": "B", "statement": "b", "review": {"state": "under review"}},
            {"id": "x", "kind": "deadend", "status": "refuted", "title": "X", "statement": "x"},
            {"id": "k", "kind": "conjecture", "tier": "T5", "status": "open", "title": "K", "statement": "k", "links": [{"to": "zz", "rel": "uses"}]},
            {"id": "h", "kind": "hunch", "tier": "T4", "status": "live", "title": "H", "statement": "h"}]}))
        (L / "events.jsonl").write_text(json.dumps({"ts": "2026-01-01T00:00:00Z", "type": "tested", "summary": "s", "nodes": ["a"], "evidence": []}) + "\n")
        (L / "frontier.json").write_text(json.dumps({"sizes": [
            {"size": 3, "lo": 1, "hi": 9, "step": 2, "realized": [5], "intervals": [{"v0": 5, "v1": 7, "status": "impossible"}]},
            {"size": 4, "lo": 0}]}))
        (L / "sota.json").write_text(json.dumps({"groups": ["G"], "entries": [
            {"id": "s1", "group": "H", "cls": "c", "result": "r", "status": "proved", "refs": [], "lit": [], "updated": "2026-01-01",
             "kind": "maybe", "previous": [{"date": "2026-01-01"}]}]}))
        r = run(["labyrinth/lab.py", "check"], self.tmp)
        self.assertEqual(r.returncode, 1)
        out = r.stdout
        for needle in ("a: review must be an object", "b: unknown review state", "x: a dead end needs its lesson",
                       "k: open conjecture without a stated test", "k: link to unknown node zz", "h: a hunch must be tier T6",
                       "unknown type tested", "frontier row 4: missing hi", "5 is claimed realized and impossible",
                       "sota s1: unknown group H", "sota s1: kind must be one of", "every previous entry needs a date"):
            self.assertIn(needle, out)
        r = run(["labyrinth/lab.py", "build"], self.tmp)     # build survives bad data; check reports it
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("skipping an invalid row", r.stderr)

    def test_event_types_are_enforced(self):
        (self.tmp / "labyrinth" / "knowledge.json").write_text('{"nodes": []}')
        self.assertNotEqual(run(["labyrinth/lab.py", "event", "conjectured", "x"], self.tmp).returncode, 0)
        self.assertEqual(run(["labyrinth/lab.py", "event", "reviewed", "x"], self.tmp).returncode, 0)


if __name__ == "__main__":
    unittest.main()
