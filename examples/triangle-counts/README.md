# Example: how many triangles can a graph on n vertices have?

A small public programme that exercises every part of the engine: exhaustive data (n ≤ 7),
a proved theorem (the top band), a refuted claim with its lesson, a conjecture with a test,
a hunch, an open door, a state-of-the-art table with history, a value still under review,
and a secondary scatter (edges against triangles).

The generated frontier has rows for n = 3 through 8; n = 3 through 7 is exhaustive and
n = 8 is partial. For n below 3, the only triangle count is zero, so those trivial rows
are omitted.

The example's review metadata illustrates the schema; the referenced referee reports are
not bundled. Building the demo does not perform those independent checks. If you import it
into a working programme, record which checks you actually ran and keep missing review
evidence pending.

Build it in an empty directory (standard library only, a few seconds):

```
mkdir -p demo/labyrinth/dashboard && cd demo
cp <skill>/templates/lab.py labyrinth/
cp <skill>/templates/dashboard.html labyrinth/dashboard/template.html
cp <skill>/examples/triangle-counts/{knowledge.json,events.jsonl,sota.json} labyrinth/
python3 <skill>/examples/triangle-counts/make_example.py labyrinth   # writes frontier.json and scatter.json
python3 labyrinth/lab.py check && python3 labyrinth/lab.py build
open labyrinth/dashboard/index.html
```

What the map shows:
- n ≤ 7 is fully resolved by exhaustive enumeration (`ex.small`), using the one-vertex
  extension (`m.extend`);
- above C(n,3) − (n − 2) nothing occurs except C(n,3) itself (`th.topband`, with a
  one-line proof);
- for n = 8 a small sample leaves six counts unknown (`q.unknown8`), and seven more are
  conjectured impossible (`k.n8`, with the exhaustive test that would settle it).

To start your own programme, replace `make_example.py` by a script that writes your
`frontier.json`, and the three JSON files by your own nodes, events and table
(`references/schema.md`).
