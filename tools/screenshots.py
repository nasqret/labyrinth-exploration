#!/usr/bin/env python3
"""Build the triangle-counts example in a temporary directory and screenshot dashboard tabs into assets/.

    python3 tools/screenshots.py [tab ...]  # needs Google Chrome or Chromium (set CHROME=/path/to/chrome)

Local tool, not run in CI. Rerun when the dashboard or the example changes, and commit the PNGs.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ASSETS = REPO / "assets"
EXAMPLE = REPO / "examples" / "triangle-counts"
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
SHOTS = [  # (tab, output name, window height, hide the page header)
    ("map", "dashboard-map.png", 1240, False),
    ("sota", "dashboard-sota.png", 560, True),
    ("graph", "dashboard-graph.png", 880, True),
    ("board", "dashboard-board.png", 900, True),
    ("frontier", "dashboard-frontier.png", 1000, True),
]


def build(tmp):
    lab = tmp / "labyrinth"
    (lab / "dashboard").mkdir(parents=True)
    shutil.copy(REPO / "templates" / "lab.py", lab / "lab.py")
    shutil.copy(REPO / "templates" / "dashboard.html", lab / "dashboard" / "template.html")
    for f in ("knowledge.json", "events.jsonl", "sota.json"):
        shutil.copy(EXAMPLE / f, lab / f)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    subprocess.run([sys.executable, str(EXAMPLE / "make_example.py"), str(lab)], check=True, env=env, stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, str(lab / "lab.py"), "build"], check=True, cwd=tmp, env=env, stdout=subprocess.DEVNULL)
    return lab / "dashboard" / "index.html"


def shot(index, tab, out, height, hide_header, profile):
    page = index.parent / f"shot-{tab}.html"
    css = "<style>header.top{display:none} nav.tabs{position:static}</style>" if hide_header else ""
    page.write_text(index.read_text() + css)
    # ?tab= selects the tab inside the dashboard's own script, before the first paint
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--disable-background-networking",
           "--disable-component-update", "--disable-sync", "--no-default-browser-check", f"--user-data-dir={profile}",
           "--hide-scrollbars", f"--window-size=1240,{height}", "--virtual-time-budget=9000",
           f"--screenshot={ASSETS / out}", page.as_uri() + f"?tab={tab}"]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    except subprocess.TimeoutExpired:
        pass  # Chrome sometimes lingers after writing the screenshot
    print("wrote", ASSETS / out)


def main():
    tmp = Path(tempfile.mkdtemp())
    try:
        index = build(tmp)
        wanted = set(sys.argv[1:])            # optional: only these tabs, e.g. "graph frontier"
        for tab, out, height, hide in SHOTS:
            if not wanted or tab in wanted:
                shot(index, tab, out, height, hide, tmp / "profile")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
