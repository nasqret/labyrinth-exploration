# Maintaining the skill

The installed skill is a clone of this repository: normally under
`~/.agents/skills/labyrinth-exploration/` in Codex or
`~/.claude/skills/labyrinth-exploration/` in Claude Code. An edit to the skill is an edit to
the repository, so every update goes through the same steps. Keep one shared research
method; put client-specific operating guidance in references.

## Making a change

1. **Edit** `SKILL.md`, `agents/openai.yaml`, `references/`, `templates/` or `examples/`.
   Keep the skill **domain-neutral**: no results, paths, cluster names or numbers from a particular
   research project. Project-specific material belongs in that project's repository.
2. **Test**:
   ```bash
   python3 -m unittest discover -s tests -v
   ```
   Install `numpy` and `PyYAML` for the complete suite; without them their optional tests
   are skipped. The engine and initial example still require only the standard library.
   The tests check:
   - the engine against a brute-force reference;
   - the example end to end;
   - the validation messages;
   - the skill's own consistency: the description stays within 1024 characters, every file
     that `SKILL.md` and the docs refer to exists, the relative links resolve, and the
     generated graphics are up to date;
   - Codex interface metadata parses as YAML and its invocation prompt names this skill.
   For Codex loader and live behavior checks, follow [the Codex testing guide](docs/codex-testing.md).
3. **Regenerate** what the change affects:
   - the graphics: `python3 tools/make_graphics.py`, after editing the generator;
   - the screenshots: `python3 tools/screenshots.py`, after changing the dashboard or the
     example (needs Chrome);
   - the social preview: `python3 tools/screenshots.py social`, after changing the hero
     graphic. Then upload `assets/social-preview.png` again under the repository's
     Settings, Social preview (GitHub has no API for it).
4. **Record** the change under "Unreleased" in [`CHANGELOG.md`](CHANGELOG.md).
5. **Commit and push.** CI runs the same tests on every push.

## Releasing

When "Unreleased" holds a coherent set of changes:
1. Move the entries under a new version heading. Use a patch release for fixes and
   wording, a minor release for new features, and a major release for breaking changes to
   the data files or the method.
2. Commit, then make an annotated tag that carries the changelog section:
   `git tag -a vX.Y.Z -m "<the changelog section>" && git push --follow-tags`.
3. `gh release create vX.Y.Z --notes-from-tag`.

Installed copies update with `git pull`.

## What belongs where

| change | file |
|---|---|
| when the skill should trigger | the `description` in `SKILL.md` (at most 1024 characters) |
| Codex display name and starting prompt | `agents/openai.yaml` |
| Codex tools, permissions and delegation | `references/codex.md` |
| the method, artifacts, hard rules | `SKILL.md` (under 300 lines; a test checks it) |
| details read on demand | `references/*.md` |
| what gets copied into a project | `templates/` |
| something to run or look at | `examples/` |
| explanations for people | `README.md`, `docs/tutorial.md` |
| native Codex validation | `tools/codex_smoke.py`, `docs/codex-testing.md` |
