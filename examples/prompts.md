# Prompts, and what they make the agent do

You do not need special words: the skill triggers on what you ask for. These prompts show
the main entry points and, for each, what the skill makes Codex or Claude Code do. In Codex,
prefix a request with `$labyrinth-exploration` for explicit invocation; in Claude Code use
`/labyrinth-exploration`. Matching research requests also select the skill automatically.

### Set up a new programme

> Set up the labyrinth for this project. Our objects are cubic graphs, the size is the number
> of vertices, and the invariant is the crossing number. Map what is known.

1. The agent analyzes the project's distinctive features: a computable ground truth, a finite
   enumeration per size, cross-checks, the communities that touch the objects, the
   available compute.
2. It creates `labyrinth/` (the engine, the dashboard template and `knowledge.json`), and
   writes a script that produces `frontier.json`.
3. It seeds the graph: known theorems, refuted claims, open questions, two or three hunches,
   families, methods and sources.
4. It backfills the event log, starts `sota.json`, builds the dashboard, and proposes the
   first doors.

### Push the bounds

> Push the bounds on the minimum. Bootstrap all techniques we have.

1. The agent reads the frontier (`lab.py status`) and picks one to three doors where one
   computation or proof step would move the map.
2. It launches literature sweeps in the background and runs small computations at the
   same time.
3. It writes a bold conjecture *with its test* before running the test, logs every outcome
   at once, sends results to a referee, and updates the map.
4. A refutation becomes a dead end with its lesson, followed by the modified statement.

### Find what is still unknown

> What is still unknown about this question? Show me where it is dark.

The agent reports the unknown bands of the frontier and the open doors, with the cheapest
experiment that could move each one. It also lists the hunches: clearly marked as
speculation, and kept because they point at corridors nobody has entered.

### Check results from elsewhere

> GPT and two subagents sent these proofs and computations. Check them critically before we
> use anything.

1. The coordinator saves each report verbatim.
2. It launches an independent referee for each one. The referee writes its own code and
   returns a verdict per item (ESTABLISHED, WITH CORRECTIONS, GAP, FALSE) with corrections
   ready to apply.
3. The coordinator adds its own spot check.
4. Only then does anything enter the notes, with every correction applied. Until then it
   is logged as "under review".

### A broad attack

> Make a broad attack on the open conjectures. Generate multiple approaches and study them
> from as many perspectives as possible.

1. The coordinator prepares a briefing pack.
2. It launches attack agents, one per conjecture or group of conjectures, each with at
   least five perspectives and the closed routes listed. A literature agent forwards leads
   to them.
3. It sends a referee for every report and writers after the verdicts, then integrates the
   results as the coordinator.
4. It staggers the launches to respect the session's limits, and keeps every agent in its
   own directory.

### When nothing moves

> We seem stuck. Climb the saturation ladder.

The agent climbs the ladder, one rung at a time:
1. change the tool family;
2. change the size parameter or the invariant;
3. go to the extreme cases;
4. relax a hypothesis;
5. invert the question ("what would a counterexample look like?");
6. import from another community;
7. reread the proofs for what a new lemma makes unnecessary;
8. consult the side projects and people;
9. change the scale: a broad attack.

Each rung is logged.

### End of session

> Let's close the session.

The coordinator updates the state-of-the-art rows (old results into the history), the nodes and the
frontier. It then runs `lab.py check && lab.py build`, rebuilds the documents with zero
warnings, refreshes the local dashboard or the authorized private deployment, updates the
project journal and memory, and commits when in scope.
It finishes by reporting the change in numbers.
