"""Consistency tests for the skill itself: frontmatter, references, links, graphics.

    python3 -m unittest discover -s tests -v
"""
import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOCS = ["README.md", "docs/tutorial.md", "examples/README.md", "examples/prompts.md", "MAINTAINING.md",
        "CHANGELOG.md", "examples/triangle-counts/README.md"]
PROJECT_SIDE = {"tools/blueprint_data.py"}   # paths inside the user's project, not in this repository
SKILL_TEXTS = ["SKILL.md", *[str(p.relative_to(REPO)) for p in sorted((REPO / "references").glob("*.md"))],
               *[str(p.relative_to(REPO)) for p in sorted((REPO / "templates" / "briefs").glob("*.md"))]]


def frontmatter():
    """Parse the frontmatter strictly enough to catch what YAML parsers reject (stdlib only)."""
    text = (REPO / "SKILL.md").read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "SKILL.md must start with a frontmatter block"
    out = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(": ")
        v = v.strip()
        if v[:1] == "'":
            assert v.endswith("'") and "'" not in v[1:-1].replace("''", ""), f"{k}: bad single quoting"
            v = v[1:-1].replace("''", "'")
        elif v[:1] == '"':
            assert v.endswith('"') and '"' not in v[1:-1].replace('\\"', ""), f"{k}: bad double quoting"
            v = v[1:-1]
        else:
            # plain YAML scalars may not contain ": " or " #", and may not start with an indicator
            assert ": " not in v and " #" not in v, f"{k}: quote this value (it contains ': ' or ' #')"
            assert v[:1] not in "&*!|>%@`[]{},?-", f"{k}: quote this value (it starts with an indicator)"
        out[k.strip()] = v
    return out


class Frontmatter(unittest.TestCase):
    def test_name_and_description(self):
        fm = frontmatter()
        self.assertEqual(fm.get("name"), "labyrinth-exploration")
        d = fm.get("description", "")
        self.assertTrue(0 < len(d) <= 1024, f"description has {len(d)} characters (limit 1024)")
        self.assertNotRegex(d, r"[<>]", "no angle brackets in the description")

    def test_skill_md_length(self):
        self.assertLess(len((REPO / "SKILL.md").read_text().splitlines()), 300)


class References(unittest.TestCase):
    def test_paths_mentioned_in_the_skill_exist(self):
        pat = re.compile(r"`((?:references|templates|examples|docs|tools|tests)/[A-Za-z0-9_./-]+)`")
        for f in SKILL_TEXTS + DOCS:
            for path in pat.findall((REPO / f).read_text()):
                path = path.split("#")[0].rstrip("/.")
                if "<" in path or "*" in path or path in PROJECT_SIDE:
                    continue
                self.assertTrue((REPO / path).exists(), f"{f} mentions {path}, which does not exist")

    def test_relative_links_resolve(self):
        link = re.compile(r"\]\(([^)\s]+)\)|<img[^>]+src=\"([^\"]+)\"|<a href=\"([^\"]+)\"")
        for f in DOCS:
            base = (REPO / f).parent
            for groups in link.findall((REPO / f).read_text()):
                target = next(g for g in groups if g)
                if re.match(r"^(https?:|mailto:|#)", target):
                    continue
                target = target.split("#")[0]
                self.assertTrue((base / target).exists(), f"{f} links to {target}, which does not exist")

    def test_no_personal_paths(self):
        for p in REPO.rglob("*"):
            if p.is_file() and ".git" not in p.parts and p.suffix in (".md", ".py", ".json", ".jsonl", ".html", ".svg", ".yml"):
                self.assertNotRegex(p.read_text(errors="ignore"), r"/Users/[a-z]|/home/[a-z]", f"personal path in {p}")


class Graphics(unittest.TestCase):
    def test_svgs_are_up_to_date(self):
        spec = importlib.util.spec_from_file_location("make_graphics", REPO / "tools" / "make_graphics.py")
        mod = importlib.util.module_from_spec(spec)
        sys.dont_write_bytecode = True
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp:
            mod.main(tmp, verbose=False)
            for name, _ in mod.GRAPHICS:
                self.assertEqual((Path(tmp) / f"{name}.svg").read_text(), (REPO / "assets" / f"{name}.svg").read_text(),
                                 f"assets/{name}.svg is stale: run python3 tools/make_graphics.py")


if __name__ == "__main__":
    unittest.main()
