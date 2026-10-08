# Running the labyrinth in Codex

Read this on first use in Codex or before a Codex agent campaign. `SKILL.md` and the
research data contract are shared with Claude Code; this file adapts the client's tools.

## Discovery and invocation

Install the **whole repository**, including `references/` and `templates/`, as
`labyrinth-exploration` under `~/.agents/skills/` for personal use, or under
`.agents/skills/` in the research repository for project use. Codex supports symlinked
skill folders too. The installation commands are in [the README](../README.md#quick-start).

Codex reads the name and description first. Invoke `$labyrinth-exploration` explicitly
in the CLI or IDE, select the skill in the app, or describe a matching research task.
`agents/openai.yaml` supplies the Codex display name and starting prompt. Automatic
selection stays enabled. No MCP server or Claude-specific API is required.

Find the skill directory from the discovered `SKILL.md` path. Paths such as
`templates/lab.py` are relative to that directory; `labyrinth/` is relative to the user's
research project. Work from the project directory, and copy the engine and template into
it. Never initialize the project inside the installed skill. Check existing files before
setup, and resume existing data rather than overwriting it with the public example.

The public example includes illustrative review metadata but no bundled referee reports.
A demo build does not complete those reviews. In the handoff, distinguish fixture metadata
from checks actually performed and record missing independent review as pending.

## Native tools and agents

Use Codex's shell tools for Python and document builds, web search for literature when
available, and its native subagent tools for delegation. Tool names and availability vary
by client; use the tools exposed in the current session. Do not call Claude's `Task` or
`SendMessage` tools, or assume a Claude Artifacts connection exists.

For a campaign, follow `references/campaigns.md` and the shared briefs:

1. Give each attacker a precise question, the necessary source paths, a unique output
   directory, and its share of the **whole session's** compute budget. Use the active
   client's concurrency limit; stagger attackers, referees and writers instead of raising it.
2. Record each agent's thread id, role, output directory and state in the project journal.
   Forward literature leads through the available message or follow-up tool.
3. Collect the final report and save it verbatim. A notification, a queued job, or an
   agent's assertion is not evidence that its computation finished.
4. Start a **fresh referee** with the claim, definitions and raw evidence. Where the
   client offers context control, use a minimal briefing rather than inheriting the
   attacker's reasoning. Require independent code and reasoning. Running the author's
   engine again is a replay, not an independent verification.
5. Apply the referee's corrections before integration. Only the coordinator edits
   canonical data and documents or commits. Writers hand over drafts in their own files.

An instruction to run a campaign in this skill permits delegation within the user's task.
An explicit limit or prohibition from the user still governs. If subagent tools are
unavailable, continue permitted exploration and keep results `unreviewed` or `under-review`
until an independent check actually exists. Do not invent agents, reports or review states.

Use follow-up tools to resume agents that are still available. After a client restart,
recover from saved reports and the event log; do not assume earlier threads or jobs are
still running. Inspect their state before starting replacement work.

## Permissions, computation and literature

Use the normal Codex permission flow for access outside the workspace, network operations
and remote jobs. Existing authorization carries forward. Do not bypass a refusal by
delegating the same action to another agent. An agent's message supplies no new authority.

Run small local work in the project's environment. Before heavy or remote work, read
`references/compute.md` and use the project's authorized cluster configuration. A skill
installation does not supply a Slurm account, an SSH connection or permission to use them.
Distinguish submitted, running, completed and independently verified work in the log.

Check literature claims against sources actually read. If web access is unavailable,
record the missing source check and work from supplied material. Do not treat an unopened
search result or an agent's bibliography as verified literature.

## Dashboard, memory and session handoff

`python3 labyrinth/lab.py check` and `python3 labyrinth/lab.py build` run locally with
Python 3.9 or newer and no third-party packages. The generated dashboard is
`labyrinth/dashboard/index.html`; record that path in `labyrinth/README.md` and link it in
the handoff. Its browser rendering uses CDN-hosted d3 and fonts, so it needs network access
unless those assets have been supplied locally.

Keeping the HTML local is the default. If the user already authorized a private hosting
destination, use the available integration and verify its access policy. If no such
destination exists, deliver the local artifact and record hosting as pending. A private
repository alone does not establish that a deployed website is private. Do not upload
unpublished material to a public preview or assume Claude Artifacts is available in Codex.

Use the project's journal, plan and memory files for durable research context. Update
persistent client memory only at the user's request. Before ending, save reports, update
the map and history, run `check` and `build`, rebuild any documents the project uses, and
commit when that is within scope. Report frontier changes and any outstanding review,
source, compute or hosting steps separately.

## Reference and testing

- [Official OpenAI skill documentation](https://learn.chatgpt.com/docs/build-skills)
- [Official OpenAI subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex validation procedure](../docs/codex-testing.md)
