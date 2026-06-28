# Checkpoint 07 — Grading against ground truth

**Goal:** measure whether the agent is actually *right*, not just whether it
runs, by scoring its answers against values computed from the database.

**Files:** `src/meteo_agent/evals/dataset.py`, `evals/run_experiment.py`
**Proof:** `uv run meteo-eval` prints a score

## The idea: ground truth from the database

"Did it run" (checkpoint 06) and "is it correct" are different questions. To
answer the second you need reference answers — and the trap is reference answers
that drift out of date as the data grows. We avoid that entirely: each eval case
carries a **reference SQL query**, and the expected answer is computed by running
that SQL against the live database. The eval set can never go stale, because it's
derived from the same source of truth the agent queries.

`CASES` (already given in `dataset.py`) pairs five natural-language questions with
the SQL that answers each.

## What to implement

### `dataset.py`

- **`ground_truth(case)`** — run `case.reference_sql` on a read-only connection
  and return the scalar result as a string.
- **`local_dataset()`** — turn `CASES` into a list of
  `{"input", "expected_output", "metadata"}` dicts, computing `expected_output`
  via `ground_truth`.

### `run_experiment.py`

- **`contains_reference(...)`** — return a Langfuse `Evaluation` named
  `contains_reference` whose value is `True` when `expected_output` appears
  (case-insensitively) in the agent's `output`. (A substring check is deliberately
  lenient — the agent answers in prose; we're checking the number is present, not
  that the sentence matches.)

The rest is given: `main()` runs the experiment in Langfuse if it's configured,
or prints a local PASS/FAIL table otherwise.

## Run it

```bash
uv run meteo-eval                 # local table, or a Langfuse experiment
uv run meteo-eval --limit 2       # quick subset while iterating
```

## Discuss

- You now have the feedback loop that makes "improve the agent" a measurable
  activity: change the prompt or model, re-run, compare scores.
- This is where the day's pieces meet: a tool you can trust (02), a loop you
  understand (03–05), traces to debug failures (06), and a score to chase (07).
- **Grow the eval set from real failures.** When the agent gets something wrong in
  the trace, add it as a case. That's the production flywheel.

## Checkpoint

- [ ] `meteo-eval` prints a score over the canonical questions
- [ ] You can add a new `EvalCase` and see it scored
- [ ] You can articulate why reference-SQL ground truth doesn't go stale

**Solution:** `git diff checkpoint-07 -- src/meteo_agent/evals/`.

## Where to go next (production)

The agent works and is measured. The road to production from here:

- Pin models; version prompts as artifacts.
- Retries, timeouts, fallbacks at every API boundary.
- Sandbox tools; assume prompt injection.
- Budget cost and latency, not just correctness.
- Grow the eval set from real failures.

You've built the foundation those rest on.
