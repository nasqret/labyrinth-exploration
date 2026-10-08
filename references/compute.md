# Compute: the local machine and shared clusters

Computations are the T3 and T4 backbone of the map. On shared resources, a careless job
costs other people's work, so the etiquette below is part of the method. Copy the relevant
rules verbatim into every agent brief that computes.

## Local machine

- Agree on a limit with the user (for example, one or two processes, short runs) and ask
  before anything heavy or long. The limit is for the **whole session**: when several
  agents run, split it in their briefs.
- Check memory (RSS) early in a long run. Avoid unbounded caches.
- Pin one environment that has the libraries you need, and name it in the briefs.

## Shared cluster etiquette

- **Own run directory per agent.** Never touch other directories, other projects or other
  users' jobs.
- **Never exclude nodes** (`--exclude`, `-x`, `ExcNodeList`). In one programme an agent
  hard-coded the exclusion of a large node after a burst of held tasks. The node was not
  faulty, and the exclusion stayed long after the problem was gone. If an exclusion is
  ever unavoidable, record the evidence (job ids, states), keep it narrow, and lift it as
  soon as possible.
- **Slurm**: `--export=ALL`, never `--export=NONE`. With NONE, Slurm rebuilds the login
  environment at each task start. When many tasks start at once on a big node this times
  out, and the tasks end up held (`user_env_retrieval_failed_requeued_held`). Throttle
  arrays (`%40` to `%100`).
- **Never infer a node fault from a user-wide `sacct`.** Filter to your own job names; the
  failures may belong to the user's other projects.
- **Budgets**: per agent and in total, with a threshold above which you ask the user (for
  example 200 CPU hours per agent, ask above 2000). Estimates overrun on a busy cluster
  (in one run, nearly five times the planned time per task): budget with margin, and have
  agents report overruns early. Reports state the CPU time used.
- Preemptible partitions cancel long tasks; put long tasks on the regular partition.
- Keep foreground ssh commands short (under two minutes, BatchMode, ConnectTimeout).
  Long work goes through the batch system.
- If the cluster is unreachable, diagnose (route, port check), never change network
  settings, and ask the user (VPN).

## Quotas: bytes and files

- Shared homes often have a **file-count quota** as well as a byte quota. Array tasks with
  one log file each exhaust it quickly. When it filled up in one programme, tasks failed
  to create their logs, and other tasks skipped work silently.
- Rules:
  - array tasks log to `/dev/null` or share one log per job;
  - aggregate per-task outputs into one file;
  - write to a temporary file and then move it, so that a partial file is never counted;
  - detect tasks that a quota error made skip work, and rerun them.
- **Archive finished run directories**:
  - one `.tar.gz` per directory, with a manifest;
  - delete the originals only after the archive lists every file (compare the counts);
  - leave a README that explains how to restore.
- **Cleanup commands can reach further than intended.** A package-manager clean also
  emptied an account-wide cache used by other environments. Look at the target before
  deleting.

## Certificate runs (T3 at scale)

- **Chunk the enumeration.** Each chunk writes a small summary atomically: counts, the
  smallest margin, violations.
- **Write a check script** that verifies that every chunk is present, that the counts add
  up to the total, and that there are no violations. Resubmit dead chunks and record their
  job ids.
- **Validate the certificate code before trusting it**: a referee runs it in full on the
  previous size and compares with an independent implementation. Only then run the new
  size.
- **Record the provenance** as evidence of the T3 node: job ids, chunks, counts, time,
  where it ran. Until an independent second run exists, list it as an open verification
  item in the review state.
