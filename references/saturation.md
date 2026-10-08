# Saturation, and how to break it

## Signals that the current tools are saturated

- Several iterations without a new refutation, conjecture or change in the frontier.
- New computations only confirm what is known.
- Every door waits on the same missing ingredient: a conjecture everyone uses but nobody
  proves.

## The escalation ladder

Climb the ladder one rung at a time, and log each rung as an event.

1. **Change the tool family.** Move from combinatorics to geometry, geometry to algebra,
   or algebra to computation. Example: a sum of local contributions, read first
   combinatorially, then through a generating function, then through a known duality.
2. **Change the parameter.**
   - Look at the same data by another size: vertices versus edges, dimension versus degree.
   - Look at another invariant: a degree or a count that controls the one you want.
3. **Go to the extremes.** Take the minimizers and the maximizers and ask what they have
   in common. Then take the first size where the pattern could break and compute there.
4. **Relax a hypothesis.** Drop connectivity, a non-degeneracy assumption or a minimality
   condition, and see which argument still works. Short proofs are often found this way.
5. **Invert the question.** Instead of "is the bound true?", ask "what would a
   counterexample have to look like?" Search for the smallest candidate.
6. **Import from another community.** Look for named families, counting theorems and
   dualities. Old literature is included: classical enumerations are sometimes decades
   old and still the best data available.
7. **Ask what a new lemma makes unnecessary.** Reread the main proofs after every new
   tool.
8. **Consult the side projects and people.** Ask a co-author, read the formalization's
   blockers, or read a referee's objections. Each is a door.
9. **Change the scale.** Launch a broad attack: one agent per open conjecture or group of
   related conjectures, each told to try at least five perspectives, with a literature
   agent feeding leads to all of them and a referee for every report (`campaigns.md`). In
   one programme a broad attack on nineteen open conjectures ran overnight in about
   fifteen hours. It settled one conjecture and one older question, and most of the
   others gained partial results, new exact data or sharper reductions. It works best
   once a briefing pack exists: statements, status, and "what is missing" for each
   conjecture.

## Generating doors deliberately

- **Every proof step that uses a cited deep result** is a door: can the step avoid it?
- **Every exhaustive range** is a door at the next size.
- **Every coincidence in the data** is a hunch until tested. Examples: equal ratios, the
  same count in two places, a power of two.
- **Every refutation** contains its own door: the modified statement.
- **Every conditional result** is a door: remove the condition.
- **Every referee correction** marks a place where the statement was sharper than it
  looked. A hypothesis had to be added, or "iff" became "if". Ask whether the corrected
  form is optimal: a counterexample to the old form is a new extreme example.
- **Every dead end of an agent** is a door for the next brief, with its lesson attached,
  so that nobody walks it again.
