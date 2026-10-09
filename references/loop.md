# One iteration of the loop, in detail

## 0. Before the first iteration: analyze the project's distinctive features

Answer these in the project notes. The answers decide which tools pay off.

- **Is there a computable ground truth?** Does an exact formula or algorithm give the
  invariant for small cases? If yes, every conjecture can be tested quickly, so aim for
  bold ones.
- **Is there a finite enumeration per size?** (In the example: all graphs on n vertices.
  Elsewhere it may be a classical enumeration, sometimes decades old.) If yes, build
  exhaustive maps for small sizes; they are the T3 backbone.
- **Where does enumeration break?** Something structural must reach beyond it: a gluing
  rule, a recursion, an extension lemma (in the example, every graph on n vertices is a
  graph on n − 1 vertices plus one vertex).
- **Independent cross-checks.** Two formulas or two programs for the same number catch
  bugs and suggest identities.
- **Which communities touch the objects?** Each one is a literature sweep. Named families
  in one community are test cases in another.
- **Who injects ideas?** Co-authors, referees, a formalization effort. Their observations
  are events of type `literature`, and they are often the most valuable doors.
- **What is the rigor anchor?** A formalization or referee pass fixes what counts as
  proved. Monitor it.
- **What compute is there, and who shares it?** The local machine's limits (for the whole
  session, not per agent), a cluster, its quotas (bytes *and* files) and its other users.
  Read `compute.md` before the first heavy run.
- **What is the documentation chain?** Decide early which document holds the proofs (the
  notes) and which ones are derived from it (a guide, write-ups, a book, generated
  tables). Derived documents are extracted by anchors and rebuilt. If one becomes a
  working copy, record it, stop regenerating it, and say which copy is canonical.

## 1. Read the frontier

- Run `lab.py status`. Look at the resolved fraction per size and at the unknown bands.
- For each open door ask:
  - what is the cheapest experiment that could move it?
  - which proof step would it unlock?
- Pick at most three items. Write them down as the iteration's goal.
- If there are many more promising doors than three, consider a campaign
  (`campaigns.md`) instead of a longer iteration.

## 2. Explore (in parallel)

- **Literature:** launch background agents with precise prompts, one per community, each
  asking for exact statements, numbers and "ideas we could exploit". Mark unverified
  claims as such. Store the useful results as `source` and `family` nodes. Check every
  claim you will use at the source, quantifiers included ("connected", "for all sizes",
  "for n ≤ N").
- **Computation:**
  - keep local runs small; send heavy runs to the cluster in chunks with a check script
    (`compute.md`);
  - write the script so that it states the claim it tests in its docstring;
  - save its outputs as JSON next to the script, and regenerate `frontier.json` from them.
- **Examples:** named families, extreme cases (minimum and maximum), degenerate cases,
  and the first case where a pattern could break.
- **Transfer:** does a notion from another field index our objects? Does a counting
  theorem elsewhere bound ours?

## 3. Predict boldly

- Formulate the strongest statement the data allow, with its test.
- Record near-coincidences as hunches with a `vivid` field: the same ratio at two sizes,
  the same count in two places, a power of two.
- Prefer predictions for the next size, where they can fail.

## 4. Test, and log at once

- `lab.py event proposed "..." --nodes ...` before running.
- `lab.py event refuted|computed|proved "..." --nodes ... --evidence script,output`
  after.
- Keep failing cases: count them, print the smallest, save them.
- When an agent reports, save its final message verbatim as its `report.md` and log the
  result with "(under review)" in the summary.

## 5. Referee

- **Who:** an independent agent with its own code, written from the definitions (it may
  read the author's scripts for definitions, never reuse them), or a co-author.
- **What:** every proof and every count that will be cited. Counts are recomputed member
  by member, not just as totals; if that is too expensive, a stated random sample is
  used. Give the referee the specific worries for each item: quantifiers, hypotheses,
  degenerate cases, signs in a summation.
- **Verdicts:** ESTABLISHED, ESTABLISHED WITH CORRECTIONS, GAP or FALSE, each with a
  one-line reason, and corrections worded as exact replacements.
- **Your own spot check:** a small exact recomputation with a reference implementation.
- **Logging:** a `reviewed` event with the verdict; set the node's `review` field; the
  state-of-the-art status names the referees.
- Example: a referee found that a certificate script read a state-table index as if it
  were a parity vector. The certificate was redone before anything used it.

## 6. Update the map

- **Refuted:** add a `deadend` node with the counterexample and a `lesson`, and link it
  (`refutes`) from what refutes it. Then write the modified statement and test it.
  Example: a local weight that was supposed to carry a lower bound, then a second one,
  both refuted. Lesson: the quantity is not local.
- **Confirmed on data:** T4. **Exhaustive with independently validated certificate code:**
  T3 for the stated sizes. **Proved:** T2, with
  the proof written in the notes. The review state is updated separately.
- **State of the art:** if a best known result changed, move the old one into `previous`
  with its date, write the new one, and rebuild.
- **Frontier:** if a realized value, an impossibility or a bound changed, regenerate
  `frontier.json` and rebuild. Keep the frontier's bounds in step with the
  state-of-the-art table: a bound improved in one and not the other silently distorts
  the resolved fractions.

## 7. Look for shortcuts

After any new lemma, reread the main proofs and ask what it makes unnecessary. In one
programme, a single new question about the objects replaced three heavy tools in the
proof of the main theorem, and the short proof then gave a new theorem as well.

## 8. Close the iteration

- `lab.py check`, then `lab.py build`, then refresh the local dashboard or the authorized
  private deployment.
- Write one journal paragraph: what was tried, what the map now says, what is still under
  review, and the next door.
