# Checkpoint 06 — Seeing inside the agent (Langfuse)

**Goal:** trace the graph agent to Langfuse so every run shows its prompts, tool
calls, SQL, and token usage. You can't operate a non-deterministic system you
can't see.

**File:** `src/meteo_agent/observability.py`  **Proof:** a trace in Langfuse

## Why this is a first-class step, not an add-on

A deterministic program either returns the right value or it doesn't, and a stack
trace tells you why. An agent can "succeed" with a wrong answer, take a weird
tool path, or quietly burn tokens. The only way to debug, evaluate, and improve
it is to **record what actually happened** on every run. Tracing is to agents
what logging-plus-a-debugger is to ordinary code.

## Start the stack

Langfuse runs from the shared docker compose at the repo root:

```bash
docker compose up -d        # from the repo root
# UI: http://localhost:3000   login admin@example.com / workshop123
```

The `.env` keys already match the project the stack auto-provisions.

## What to implement

LangChain has a callback mechanism; Langfuse plugs into it. The whole integration
is a callback handler threaded through the `config` you already plumbed in
checkpoint 04. Work through the `# TODO(checkpoint 06)` markers:

1. **`langfuse_handler()`** — return a Langfuse LangChain `CallbackHandler`.
2. **`traced_config()`** — return `{"callbacks": [langfuse_handler()]}`.
3. **`run_traced(question, model)`** — call the graph's `run_agent` with
   `config=traced_config()` so the run is recorded, then **flush** the client
   before returning (short-lived CLI processes exit before the async export
   otherwise).

Notice you are **not** touching `graph.py`. The `config` seam from checkpoint 04
is exactly the injection point — tracing is a cross-cutting concern bolted on
from outside, not woven into the agent.

## Run it

```bash
uv run meteo-trace "What was the average temperature in 2003?"
```

Open Langfuse → you should see a trace: the system prompt, the model turns, each
`run_sql` call with its SQL and result, and token counts.

## Discuss

- The `config` parameter looked pointless in checkpoint 04. This is why it's there
  — design your seams before you need them.
- What would you put on a production dashboard? Latency, cost per question, tool
  error rate, and answer-quality (checkpoint 07) — not just "did it run."

## Checkpoint

- [ ] `docker compose up -d` brings up Langfuse
- [ ] `meteo-trace "..."` produces a visible trace with the SQL in it
- [ ] `graph.py` is unchanged

**Solution:** `git diff checkpoint-06 -- src/meteo_agent/observability.py`.

Next: [07 — Evals](07-evals.md).
