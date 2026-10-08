# Lessons from a long programme

This method was developed on one research programme in pure mathematics: which values an
integer invariant takes on a family of objects of each size. The programme ran for about
two weeks, with notes growing to about 400 pages. Its mathematics is not published yet,
so only the process is described here.

## What shaped the method

- **An exact ground truth.** A formula computed the invariant for small objects, so every
  conjecture could be tested in seconds.
- **A finite enumeration per size**, taken from a classical enumeration in another
  community. It gave exhaustive maps (T3) for the small sizes.
- **An explosion beyond them**, so structure theory was needed: gluing rules, atoms, and a
  monotone operation.
- **Several independent formulas** for the same number, which cross-checked each other.
- **Four communities** that touch the objects, each with its own literature and named
  families.
- **External inputs**: a co-author's observation, a formalization effort in another
  repository (monitored read-only), and AI referee passes.

## How the loop moved the map

1. **The exhaustive backbone came first.** Exact minima and maxima for the small sizes
   turned every later hunch into a quick test.
2. **Bold conjectures were refuted quickly**, eight in the first days, each leaving a
   one-line lesson. Some examples:
   - a rule for the maximizer failed at the next size, because the right selection is
     subtler;
   - a structural description of the minimizers failed, because an operation that lowers
     the invariant does not reach its minimum;
   - two local weights that were to carry a lower bound failed, because the quantity is
     not local.
3. **Ideas transferred across communities.** The co-author's observation identified one
   notion with another community's notion. A classical enumeration gave named families,
   and a counting theorem from a third community bounded the invariant.
4. **A new lemma gave shortcuts.** One question about the objects removed three heavy
   tools from the main proof, and the short proof then gave a new theorem.
5. **Literature claims were verified at the source before use.** Twice, reading a
   quantifier at the source (a restriction to a subclass, a range of sizes) settled
   exactly what a cited theorem covers, and both checks immediately extended a proved
   theorem.
6. **A published value was contradicted, and the disagreement was explained** rather
   than just flagged: the publication had computed a different quantity.
7. **Engineering became the bottleneck.** A cheaper formula plus faster exact arithmetic
   made the core computation 25 times faster: a 3-hour atlas took 7 minutes. A monotone
   operation then turned "enumerate everything" into "close upward from a few top seeds".
8. **The programme scaled up.**
   - It ran fourteen loop iterations in four days, each aimed at one missing ingredient.
   - Its state-of-the-art table reached 42 rows, 31 with a recorded history.
   - The graph reached 426 nodes, 156 of them imported from a blueprint, and the log 338
     events.
   - A cluster certificate run was trusted only after a referee had validated its code in
     full on the previous size. Then every chunk certified, with no violation.
   - A guide and nineteen self-contained write-ups became the briefing pack for agents.
9. **A broad attack** on nineteen open conjectures ran overnight in about fifteen hours
   (`campaigns.md`):
   - eight attack agents, a literature sweep, ten referee passes, six writers and an
     editor;
   - one conjecture settled, one older question settled, and most of the others moved;
   - no false theorem entered the notes;
   - the referees caught a lemma false as stated, a stale comparison table and mislabeled
     values in older text;
   - the coordinator undid a writer's unsupported weakening of a conjecture.
10. **Infrastructure incidents**, each of which became a rule in every later brief:
    - an agent excluded a large cluster node after held tasks whose real cause was
      `--export=NONE`;
    - the shared file-count quota filled up;
    - an agent's draft was overwritten through a shared scratch name;
    - about ten concurrent agents exhausted the session's usage limit, twice;
    - several agents each assumed they owned the local process budget;
    - an agent asked the coordinator to cancel a job that its own permissions had
      refused. The coordinator refused and told the user.
11. **A drift between two artifacts.** One size's frontier kept a generic upper bound
    after the state-of-the-art table had recorded the exact maximum, so its resolved
    fraction was computed over the wrong range. An independent review of the tooling
    found it.

## Lessons for other projects

- **Build the exhaustive backbone early.** It turns every later hunch into a quick test.
- **Refutations are the fastest teachers.** Keep the counterexamples and write the lesson
  in one sentence.
- **The best new ideas came from outside**: a co-author, a classical enumeration, and
  another community's counting theorem. Always run literature sweeps in parallel with
  computations.
- **After each new lemma, reread the main proofs.** The short route was hiding in plain
  sight.
- **Keep hunches on the board.** A near-coincidence in the data (the same ratio at two
  sizes) became a testable conjecture at the next size.
- **Put the map in data.** A dashboard showing unknown bands per size makes "how much is
  left" undeniable, and shows where the next computation should go.
- **Before a heavy run, look for monotonicity.** One monotone operation turned a full
  enumeration into a closure from a few seeds, and settled the top of a spectrum in
  minutes.
- **Profile before you scale.** The expensive part (2.4 GB for one object) was a
  consistency check, not the quantity needed. Strip checks from production runs, but
  validate the stripped code against the full one first.
- **Check literature claims at the source,** especially quantifiers, before promoting a
  theorem that uses them.
- **Referee everything that will be cited, including your own runs.** Agents' results
  were usually right in substance and often wrong in details: about one item in five
  needed a correction. The details are exactly where a later reader trips.
- **Build the briefing pack before the broad attack.** A guide with status tags,
  write-ups with full proofs, and a "what is missing" list per conjecture turned each
  attack brief into about a page that points to labels instead of retelling the theory.
- **Tell every agent the closed routes.** Put the dead ends, with their lessons, into the
  brief, so that the agent's effort goes to new routes.
- **Keep the coordinator's hands on the canonical text.** Writers produce drafts and
  exact edits; the coordinator reads them against the referee's verdicts.
- **Generate every table from one source.** A bound kept in two places drifts.
- **Turn every infrastructure incident into a rule in the briefs.** Shared resources
  (cluster quotas, nodes, the scratchpad, the session's usage limit) fail in the same way
  again unless the next brief prevents it.
