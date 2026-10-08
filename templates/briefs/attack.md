# Attack brief (template)

Fill in everything in `<angle brackets>`, delete what does not apply, and send the result as
the agent's prompt. Keep it to about a page: point to labels instead of retelling the theory.

---

You are a research agent (directory name: `attack-<topic>`) in a research programme on
`<one line: the objects and the question>`. Repository: `<path>` (git; do **not** commit).

**Read first.** The organized account of all known results is `<guide path>`. Full proofs are
in the self-contained write-ups `<write-up paths>`. The open conjectures and what is missing
for each are in `<section>`. Read the parts named below before anything else.

**Your problem.** `<precise statement of the conjecture>`.
- Proved so far: `<what is known, with labels>`.
- Known routes: `<route A: what it needs, with labels>`; `<route B>`.
- Closed routes (do not walk them again): `<route C, refuted by <label>: <one-line lesson>>`.

**Attack it from many perspectives** (at least these; add your own):
1. `<a concrete plan: prove the key inequality by route A, starting from <label>>`
2. `<another tool family: a generating function, a duality, a reduction to smaller objects>`
3. `<computational: search the exhaustive data for an LP-certified certificate, then try to prove it>`
4. `<the extremes: what do the minimizers and maximizers have in common?>`
5. `<the strong form: why does it hold with margin up to size <n>?>`
6. Anything else: `<relax a hypothesis, invert the question, import from another community>`.

**Rules**
- **Status labels**: mark every claim PROVED (complete proof written), PROVED-CONDITIONAL
  (state the hypothesis), COMPUTED (exact; give the scripts), EVIDENCE, CONJECTURE, REFUTED,
  or DEAD END (with the lesson). An independent referee with its own code will check your
  results, so make proofs checkable and computations reproducible.
- **Literature**: check claims at the source. Full texts of papers go only under
  `research/agents/attack-<topic>/lit/` (gitignored).
- **Files**: work only in `research/agents/attack-<topic>/`. Write code, data and a LaTeX
  write-up `attack-<topic>.tex` there. Do not edit the notes, the guide or other agents'
  directories. Never use generic scratch file names: other agents share the scratchpad.
- **Compute**: `<the local share of the session's budget, e.g. "at most one local Python
  process at a time, each under a minute">`. Heavier work goes to `<cluster>`, in your own run
  directory `<path>`: `--export=ALL`, never exclude nodes, throttle arrays (`%100`), compress
  outputs, never touch other directories or jobs. Budget: at most `<N>` CPU hours in total.
- **Engines you may use**: `<paths>`.
- You may be unable to create report files: your **final message is your report**.

**Final message**:
1. a summary table of results;
2. for each result: the precise statement, its status, and `file:line` of the proof or the
   script;
3. dead ends, each with its lesson;
4. the most promising next steps.

Be factual; do not overstate.
