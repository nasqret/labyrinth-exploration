# Maintaining the skill

The installed skill (`~/.claude/skills/labyrinth-exploration/`) is a clone of this
repository. An edit to the skill is an edit to the repository, so every update goes
through the same steps.

## Making a change

1. **Edit** `SKILL.md`, `references/`, `templates/` or `examples/`. Keep the skill
   **domain-neutral**: no results, paths, cluster names or numbers from a particular
   research project. Project-specific material belongs in that project's repository.
2. **Test**:
   ```bash
   python3 -m unittest discover -s tests -v
   ```
   The tests check:
   - the engine against a brute-force reference;
   - the example end to end;
   - the validation messages;
   - the skill's own consistency: the description stays within 1024 characters, every file
     that `SKILL.md` and the docs refer to exists, the relative links resolve, and the
     generated graphics are up to date.
3. **Regenerate** what the change affects:
   - the graphics: `python3 tools/make_graphics.py`, after editing the generator;
   - the screenshots: `python3 tools/screenshots.py`, after changing the dashboard or the
     example (needs Chrome).
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
| the method, artifacts, hard rules | `SKILL.md` (under 300 lines; a test checks it) |
| details read on demand | `references/*.md` |
| what gets copied into a project | `templates/` |
| something to run or look at | `examples/` |
| explanations for people | `README.md`, `docs/tutorial.md` |
