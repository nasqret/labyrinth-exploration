# Testing the Codex integration

The engine suite, native discovery and live workflow tests establish different things.
Use only the public triangle-count example in integration tests. Keep test projects and
transcripts outside this repository and never upload credentials or private research.

## Engine and package checks

```bash
python3 -m pip install numpy PyYAML  # in your development environment
python3 -m unittest discover -s tests -v
```

The suite checks the frontier classifier against a brute-force reference, the example
and its exhaustive tutorial iteration, malformed-data diagnostics, YAML metadata,
reference paths, links and graphics. NumPy and PyYAML are test dependencies; the engine
and initial example use only the standard library. Tests needing a missing optional
dependency report a skip, so report the skip count along with the result.

## Native Codex discovery, without model calls

With Codex CLI installed, run from this repository:

```bash
python3 tools/codex_smoke.py --output /tmp/labyrinth-codex-discovery.json
```

This creates a temporary project, symlinks the whole skill into `.agents/skills/`, starts
the installed CLI's stdio app-server, initializes it, and calls `skills/list`. It checks
that Codex discovers this exact `SKILL.md` as an enabled project skill and loads the
display name, description and `$labyrinth-exploration` starting prompt. It reports the
installed CLI version and exits nonzero on a failure. It makes **no model calls**, edits
no global configuration, and removes its temporary project on exit. The app-server
protocol is versioned by the installed CLI; a protocol failure is not a behavioral pass.

## Isolated live workflow checks

These tests use the signed-in Codex account and consume model tokens. Make a fresh
temporary project for each case and symlink this repository into its
`.agents/skills/labyrinth-exploration/`. Run from that project. For example:

```bash
LABYRINTH_SOURCE_DIR="$(pwd)"
LABYRINTH_TEST_DIR="$(mktemp -d "${TMPDIR:-/tmp}/labyrinth-workflow.XXXXXX")"
mkdir -p "$LABYRINTH_TEST_DIR/.agents/skills"
ln -s "$LABYRINTH_SOURCE_DIR" "$LABYRINTH_TEST_DIR/.agents/skills/labyrinth-exploration"
codex exec --ephemeral --sandbox workspace-write --skip-git-repo-check \
  -C "$LABYRINTH_TEST_DIR" --json - \
  > "$LABYRINTH_TEST_DIR/trace.jsonl" <<'PROMPT'
Use $labyrinth-exploration to initialize a local research map for triangle counts of
simple graphs, using the packaged public example. Build and validate the dashboard,
identify what remains unknown, and leave a project journal and a dashboard handoff.
The bundled make_example.py is allowed for setup; do not run exhaustive_n8.py or any
additional enumeration. Do not delegate, use the network, publish, commit, or change
persistent client memory. Stop after the setup
and report the current frontier and outstanding review.
PROMPT
```

Check actual artifacts and command events, not only the final response:

- Codex reads the installed `SKILL.md` and the Codex adapter, and resolves bundled files
  from the skill location while writing project artifacts into the temporary project.
- `python3 labyrinth/lab.py check` and `build` succeed. `dashboard/index.html` contains
  embedded data, and `dashboard/data.json` agrees with the graph, frontier and table.
- The example has resolved fraction 1 for n = 3 through 7 and 44/57 for n = 8. Its n = 8
  counts remain 39 realized, 5 impossible, 7 conjecturally impossible and 6 unknown.
- The under-review result is preserved; setup does not manufacture a referee or promote
  a conjecture. The handoff links the local HTML and names pending independent review.
- The installed source is unchanged, and no publishing, commits or client-memory edits
  occur. The user's no-delegation constraint overrides the normal campaign protocol.

Repeat with a fresh project and **omit** `Use $labyrinth-exploration` from the same
research request to test implicit selection. A generic one-off proof or code review
should not trigger the skill; include one as a negative routing check when changing its
description.

For delegation, use another fresh project and request a bounded review of a supplied
candidate claim about triangle counts on four vertices. Permit one fresh referee, its
own small enumeration, and local report files. Check the actual child thread and its
code, the saved verbatim report, a verdict supported by its computation, and the
coordinator's spot check. Claims enter canonical data only after that review. This tests
native orchestration and the review gate; it does not certify the entire research method.

If the client cannot connect or delegate, record that exact limitation instead of
calling the workflow passed. A separately run independent Codex subagent can test the
briefs and artifact behavior, but it does not replace the native loader check above.
