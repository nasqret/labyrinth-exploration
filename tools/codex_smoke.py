#!/usr/bin/env python3
"""Check native Codex skill discovery without a model call or a personal installation.

    python3 tools/codex_smoke.py [--output report.json]

Requires an installed Codex CLI. Uses its stdio app-server in a temporary project and
leaves global configuration, credentials and installed skills untouched.
"""
import argparse
import json
import queue
import re
import shutil
import subprocess
import tempfile
import threading
import time
from pathlib import Path


class AppServer:
    def __init__(self, command, cwd, timeout):
        self.timeout = timeout
        self.stderr = tempfile.TemporaryFile(mode="w+b")
        try:
            self.proc = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE, stderr=self.stderr)
        except Exception:
            self.stderr.close()
            raise
        self.messages = queue.Queue()
        self.reader = threading.Thread(target=self._read_stdout, daemon=True)
        self.reader.start()

    def _read_stdout(self):
        for line in iter(self.proc.stdout.readline, b""):
            self.messages.put(line)
        self.messages.put(None)

    def send(self, message):
        self.proc.stdin.write((json.dumps(message) + "\n").encode("utf-8"))
        self.proc.stdin.flush()

    def request(self, request_id, method, params):
        self.send({"id": request_id, "method": method, "params": params})
        deadline = time.monotonic() + self.timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RuntimeError(f"Timed out waiting for {method}")
            try:
                line = self.messages.get(timeout=remaining)
            except queue.Empty:
                raise RuntimeError(f"Timed out waiting for {method}") from None
            if line is None:
                self.stderr.seek(0)
                diagnostic = self.stderr.read().decode("utf-8", errors="replace").strip()
                raise RuntimeError(f"Codex app-server closed while waiting for {method}: "
                                   f"{diagnostic[-2000:]}")
            if not line.strip():
                continue
            message = json.loads(line)
            if message.get("id") == request_id:
                if "error" in message:
                    raise RuntimeError(f"{method}: {message['error']}")
                return message["result"]

    def close(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
        self.proc.stdin.close()
        self.reader.join(timeout=5)
        self.proc.stdout.close()
        self.stderr.close()


def check_discovery(skill_dir, codex_bin, timeout=30):
    skill_dir = Path(skill_dir).resolve()
    manifest = skill_dir / "SKILL.md"
    text = manifest.read_text(encoding="utf-8")
    name_match = re.search(r"^name: ([a-z0-9-]+)$", text, re.M)
    if not name_match:
        raise RuntimeError("Missing skill name in SKILL.md")
    name = name_match.group(1)
    version = subprocess.run([codex_bin, "--version"], capture_output=True, text=True,
                             check=True, timeout=timeout).stdout.strip()

    with tempfile.TemporaryDirectory(prefix="labyrinth-codex-") as tmp:
        project = Path(tmp)
        installed = project / ".agents" / "skills" / name
        installed.parent.mkdir(parents=True)
        installed.symlink_to(skill_dir, target_is_directory=True)
        server = AppServer([codex_bin, "app-server", "--stdio"], project, timeout)
        try:
            server.request(1, "initialize", {
                "clientInfo": {"name": "labyrinth-smoke", "version": "1.0.0"}})
            server.send({"method": "initialized"})
            result = server.request(2, "skills/list", {
                "cwds": [str(project)], "forceReload": True})
        finally:
            server.close()

        entries = result.get("data", [])
        matching = [skill for entry in entries for skill in entry.get("skills", [])
                    if skill.get("name") == name and
                    Path(skill.get("path", "")).resolve() == manifest]
        errors = [error for entry in entries for error in entry.get("errors", [])
                  if Path(error.get("path", "")).resolve() in
                  {manifest, skill_dir / "agents" / "openai.yaml"}]
        if errors:
            raise RuntimeError(f"Codex rejected the skill: {errors}")
        if len(matching) != 1:
            raise RuntimeError(f"Expected one discovered {name} skill, got {len(matching)}")
        skill = matching[0]
        if not skill.get("enabled") or skill.get("scope") != "repo":
            raise RuntimeError("The temporary project skill is not enabled with repo scope")
        interface = skill.get("interface") or {}
        if not interface.get("displayName") or not interface.get("shortDescription"):
            raise RuntimeError("Codex did not load the interface name and description")
        if "$" + name not in (interface.get("defaultPrompt") or ""):
            raise RuntimeError("Codex did not load the skill's explicit invocation prompt")
        if not skill.get("description"):
            raise RuntimeError("Codex did not load the skill description")
        return {"passed": True, "codex_version": version, "name": name,
                "scope": skill["scope"], "enabled": skill["enabled"],
                "interface": {key: interface[key] for key in
                              ("displayName", "shortDescription", "defaultPrompt")},
                "checks": ["project discovery", "symlink discovery", "frontmatter",
                           "interface metadata", "explicit invocation prompt"],
                "model_calls": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--codex-bin", default=shutil.which("codex"))
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.codex_bin:
        parser.error("Codex CLI is not installed or is not on PATH")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    try:
        report = check_discovery(args.skill_dir, args.codex_bin, args.timeout)
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        report = {"passed": False, "error": str(error)}
    payload = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
