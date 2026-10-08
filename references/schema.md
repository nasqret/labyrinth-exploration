# Schema

All files live in `<repo>/labyrinth/`. Only `knowledge.json` is required; the example in
`examples/triangle-counts/` has one of each.

## `knowledge.json`

`{"schema": 1, "meta": {title, eyebrow, subtitle}, "nodes": [...], "blueprint_overrides":
{...}, "frontier_history": [{date, size, resolved, why}]}`. Only `nodes` is needed.
- `schema` is the version of this format, 1 for now.
- `meta` sets the dashboard's title.
- `frontier_history` records milestones of the resolved fraction per size.

**Blueprint (optional).** A project that already keeps its statements with dependencies can
expose them as `tools/blueprint_data.py`, a list `N` of dicts `{id, kind, prov, title, stmt,
where, group, uses}`. The engine imports them instead of copying them:
- `prov` gives the tier: `classical` and `literature` → T1, `project` and `paper` → T2,
  `conjecture` → T5;
- `uses` becomes `uses` links;
- `blueprint_overrides` (keyed by id) can change the tier, status, links or review of any
  of these nodes.

## Node (in `knowledge.json` → `nodes`)

| field | type | notes |
|---|---|---|
| `id` | string | stable, prefixed by kind: `x.` dead end, `q.` door, `h.` hunch, `f.` family, `m.` method, `src.` source, `k.` conjecture, others free |
| `kind` | enum | theorem, exhaustive, evidence, conjecture, hunch, question, deadend, family, method, source |
| `tier` | T1–T6 or null | required for theorem, exhaustive, evidence, conjecture, hunch |
| `status` | string | theorem: established; conjecture: open / modified / refuted / proved; question: open / partial / answered; hunch: live / testing / modified / dropped / promoted; deadend: refuted |
| `title`, `statement` | string | the statement is precise enough to be tested |
| `links` | list of {to, rel} | relations: uses, supports, refutes, modifies, generalizes, suggests, answers, tests, instance-of, cites; stored on the source node |
| `evidence` | list of strings | scripts, counts, outputs |
| `where` | list of strings | documents where it is written up |
| `review` | object, optional | for T2 and T3 results: `{state, by, verdict, date}`; `state` is `unreviewed`, `under-review`, `refereed` or `human-checked`; `by` lists the referees (their directories) and is required once refereed |
| `created`, `updated` | ISO date | |
| optional | | `why`, `next` (doors), `vivid`, `test` (hunches and conjectures), `lesson` (dead ends), `answer` (answered doors), `note` |

Blueprint nodes (statements with dependencies, from `tools/blueprint_data.py`) are
imported, not copied. Their tier, status and review may be overridden in
`blueprint_overrides`.

## Tiers

| tier | meaning | may be cited as |
|---|---|---|
| T1 | proved in the literature (published, peer reviewed) or standard | fact |
| T2 | proved here, not peer reviewed | result, with the caveat and the review state |
| T3 | exhaustive computation with certified code, validated against an independent implementation | fact for the stated sizes |
| T4 | computational evidence | evidence only |
| T5 | conjecture with a stated test | conjecture |
| T6 | hunch, explicitly not a claim | a direction only |

Referees change the review state, not the tier. A result of the programme becomes T1 only
once it is published. A certificate run that exists once stays T3 with its review state
saying that an independent second run is open. Keep the review provenance in the status
text as well ("proved (2 independent AI referees; human check pending)"), because that
text is what readers of the state-of-the-art table see.

## Agent labels, tiers and events

| an agent reports | after the referee's verdict | event |
|---|---|---|
| PROVED | T2, review `refereed` (or a GAP/FALSE verdict: back to conjecture or dead end) | `proved`, then `reviewed` |
| PROVED-CONDITIONAL | T2 for the implication; the hypothesis is a conjecture node | `proved`, then `reviewed` |
| COMPUTED (exact, certified) | T3, review `refereed` | `computed`, then `reviewed` |
| EVIDENCE | T4 | `computed` |
| CONJECTURE | T5, with its test | `proposed` |
| REFUTED | a dead end with its counterexample | `refuted` |
| DEAD END | a dead end with its lesson | `refuted` or `modified` |

Until the verdict, the summary of the event says "(under review)" and the node's review
state is `under-review`.

## Event (one JSON object per line in `events.jsonl`)

`{ts, type, summary, nodes: [ids], evidence: [paths or links], backfilled?}`. Types:
proposed, computed, proved, refuted, modified, literature, question, answered,
reviewed, documented, monitor, milestone. `lab.py event` refuses other types, because
synonyms such as "conjectured" or "tested" split the timeline.

## Frontier map (`frontier.json`)

```
{"meta": {"size_name": "n", "value_name": "triangles", "value_scale": "linear" | "log"},
 "sizes": [{"size": 6, "label": "n = 6", "lo": 0, "hi": 20, "step": 1,
            "realized": [[16, "K_6 minus an edge"], 12, ...],
            "intervals": [{"v0": 17, "v1": 19, "status": "impossible", "why": "th.topband"},
                          {"v0": 0, "v1": 13, "status": "realized", "why": "a family covers every value"}],
            "bounds": {"lower_proved": 0, "lower_conj": 0, "upper": 20, "upper_kind": "exact"}}]}
```

- The admissible values of a size are lo, lo + step, … ≤ hi.
- Statuses: `realized` (a witness exists), `impossible` (proved or exhaustive),
  `gap-conditional` (impossible under a named hypothesis), `conj-impossible` (outside a
  conjectured bound). Everything else is `unknown`.
- A value claimed by several statuses gets the highest: realized, then impossible, then
  gap-conditional, then conj-impossible. `lab.py check` reports a value that is claimed
  both realized and impossible, since one of the claims is wrong.
- The resolved fraction is (realized + impossible) / admissible. The engine draws a size
  with many runs as bins, so ranges of millions of values are fine.
- Write `frontier.json` from your computation outputs with a script, never by hand, and
  keep its bounds in step with the state-of-the-art table.

## Scatter (`scatter.json`, optional)

`{title, tab, subtitle, x_name, y_name, y_scale, series: [{key, label}], points: [{x, y,
series, src}]}`: any secondary picture of the data (in the example, edges against
triangles).

## State-of-the-art entry (`sota.json` → `entries`)

`sota.json` is `{about, groups: [names in display order], entries: [...]}`. Required in every
entry: `id`, `group`, `cls`, `result`, `status`, `refs`, `lit`, `updated` (the other fields
are optional).

| field | type | notes |
|---|---|---|
| `id` | string | stable, for example `lb-all` |
| `group` | string | one of `groups` |
| `cls`, `result` | string | the class of objects and the best known result, in plain text |
| `cls_tex`, `result_tex` | string, optional | the same in LaTeX; without them the plain text is escaped |
| `status` | string | proved / exhaustive / computer-assisted / conjecture ..., with the review provenance |
| `kind` | enum, optional | proved, exhaustive, computed, partial, conjecture, refuted: sets the dashboard colour |
| `refs`, `lit` | lists | labels in the notes; citation keys |
| `updated` | ISO date | |
| `previous` | list of {date, was} | every earlier best result, oldest first; never delete history |

## Engine and dashboard switches

- In `lab.py`: `SOTA_TEX` and `SOTA_MD` (paths, default `None`) also write the
  state-of-the-art table as a LaTeX longtable and as Markdown, and `BOOK_STATUS` copies
  `STATUS.md` somewhere else.
- In the dashboard: `index.html?tab=<id>` (or `#<id>`) opens a tab directly. The ids are
  `map`, `sota`, `frontier`, `scatter`, `graph`, `timeline`, `board` and `tables`.

## Agent directory (`research/agents/<name>/`)

- `report.md`: the agent's final message, verbatim. Its first line is a provenance
  header: agent, date, referee status. Update the header once the referee has reported.
- Code and data, with the scripts named in the report. Full texts of papers go in
  `lit/`, which is gitignored.
- Cluster scripts in `cluster/`; the run directory on the cluster has the same name.
- Referee: `research/agents/referee-<name>/` with its own `report.md` and its own code.

## Validation (`lab.py check`)

- The kind is known, and tiers are present where required.
- A hunch is T6, and a theorem is never T5 or T6.
- An open curated conjecture has a `test`, and a dead end has a `lesson`.
- Every link and every node id in an event resolves.
- Event types belong to the fixed list.
- A `review` is an object with a known state, and a refereed node names its referees.
- Frontier rows have `size`, `lo` and `hi`, a positive step and known statuses, and no
  value is claimed both realized and impossible.
- State-of-the-art entries have the required fields, a known group and kind, and every
  `previous` item has a date and the old result.
