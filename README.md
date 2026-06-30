# meteo-agent

A production-grade LLM agent in Python, built for the workshop **"Building a
Production-Grade AI Agent with Python."**

The agent answers natural-language questions about weather observed at the **[Meteobeguda](http://www.meteobeguda.cat/) weather
station** (676,595 readings, 2002 → today) by writing read-only SQL. We build it
three times — from scratch, in LangGraph, and behind MCP — and harden it with
tests, observability, and evals.

## Workshop delivery

This repo ships as a **branch-per-checkpoint TDD history** so you start from a
stubbed project and can check your work against a solution at any point. The
default branch (`main`) **is** the RED starting line — clone it and you're already
at the workshop's starting point; the complete reference is the last branch,
`checkpoint-07`.

```bash
uv run pytest            # red — you start here, on main (== start)
```

The branches are pre-built; maintainers regenerate them with `bash setup-branches.sh`
(it rebuilds `main`/`start` as the RED root and `checkpoint-02..07` on top — see
BRANCHES.md).

See [BRANCHES.md](BRANCHES.md) for the branch map and participant workflow, and
[`guide/`](guide/) for the step-by-step build, one checkpoint at a time.
`starter/` is the stub source the script uses (and a self-contained copy if you'd
rather not use branches).

### The arc (≈5 hours)

We build one agent — a SQL analyst over the Beguda weather station — **three
times**, then harden it. Each step reuses the same pure tools; it's a refactor,
not a rewrite.

| # | Checkpoint | Module(s) built | Big idea | ~time |
|---|---|---|---|---|
| 01 | [Setup & data](guide/01-setup-and-data.md) | — | the project, the DB, the model seam | 30 min |
| 02 | [Tools](guide/02-tools.md) | `tools.py` | pure, typed, read-only-by-construction tools | 45 min |
| 03 | [The loop](guide/03-loop.md) | `loop.py` | the agent loop by hand (native tool calls) | 50 min |
| 04 | [LangGraph](guide/04-graph.md) | `graph.py` | the same agent in a framework | 40 min |
| 05 | [MCP](guide/05-mcp.md) | `mcp_server.py`, `mcp_agent.py` | tools as a protocol | 45 min |
| 06 | [Observability](guide/06-observability.md) | `observability.py` | seeing inside a non-deterministic system | 35 min |
| 07 | [Evals](guide/07-evals.md) | `evals/*.py` | grading against ground truth | 40 min |

### How each checkpoint works

1. **Read** the guide section — goal, concept, contract.
2. **Run the failing test** (or the agent) to see red.
3. **Implement** the `# TODO`s in the matching `src/meteo_agent` module.
4. **Go green** — the checkpoint's test passes (or the agent answers).
5. **Compare** with the solution — `git diff checkpoint-NN -- <file>` — and
   discuss the tradeoffs.

### For the instructor

- Participants build `data/meteobeguda.sqlite` with `uv run python data/build_db.py`
  (it downloads the source period files from the public `meteobeguda-etl` repo).
  The unit + recorded tests need neither the big DB nor a network, so checkpoints
  02–03 work fully offline.
- A reliable tool-calling model matters for the live demo. `qwen2.5:7b` works
  locally; `qwen2.5:72b` on Ollama Cloud is steadier on stage. Avoid `phi3:mini`
  (poor tool-calling). Any OpenAI-compatible endpoint works — see guide 01.

## Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/)
- Docker + Docker Compose (for self-hosted Langfuse)
- An LLM over an OpenAI-compatible endpoint. The default is local
  [ollama](https://ollama.com); any provider works (see Configuration).

## Quickstart

```bash
# 1. install dependencies
uv sync

# 2. configure
cp .env.example .env        # defaults target local ollama + self-hosted Langfuse

# 3. build the consolidated database (downloads the source files; see Dataset)
uv run python data/build_db.py

# 4. (optional) a local model
ollama pull qwen2.5:7b      # or run it in the container: see Docker stack

# 5. ask a question
uv run meteo-graph "How many days in 2023 had a maximum above 35 C?"
```

## The three agents (one set of tools)

The pure tools live in `src/meteo_agent/tools.py` (`run_sql`, `get_schema`) and
are reused across all three implementations — each step is a refactor, not a
rewrite.

| Module | Entry point | What it shows |
|--------|-------------|---------------|
| `loop.py` | `uv run meteo-loop "..."` | the agent loop by hand, native `tool_calls` |
| `graph.py` | `uv run meteo-graph "..."` | the same agent in LangGraph (`StateGraph` + `ToolNode`) |
| `mcp_server.py` + `mcp_agent.py` | `uv run meteo-mcp-agent "..."` | tools served over MCP (FastMCP), consumed via `langchain-mcp-adapters` |
| `observability.py` | `uv run meteo-trace "..."` | the graph agent, traced to Langfuse |
| `evals/run_experiment.py` | `uv run meteo-eval` | scored eval over canonical questions |

## Configuration

All model access is OpenAI-compatible. Swapping providers is an env change:

```bash
# local ollama (free)
OPENAI_BASE_URL=http://localhost:11434/v1                          OPENAI_API_KEY=ollama    MODEL=qwen2.5:7b
# Ollama Cloud (reliable tool-calling for a live demo)
OPENAI_BASE_URL=https://ollama.com/v1                              OPENAI_API_KEY=<key>     MODEL=qwen2.5:72b
# OpenAI
OPENAI_BASE_URL=https://api.openai.com/v1                          OPENAI_API_KEY=sk-...    MODEL=gpt-4o-mini
# Anthropic (Claude)
OPENAI_BASE_URL=https://api.anthropic.com/v1/                      OPENAI_API_KEY=sk-ant-... MODEL=claude-opus-4-8
# Google (Gemini)
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/  OPENAI_API_KEY=<key>  MODEL=gemini-2.5-pro
```

> The Anthropic and Google URLs are **OpenAI-compatibility endpoints** — convenient
> for a swap, but shims rather than each provider's native API (tool-calling,
> thinking, and streaming are lossy through them). For production, use the native
> integrations (`langchain-anthropic` / `langchain-google-genai`, and the native
> `anthropic` SDK for the from-scratch loop). See `guide/01-setup-and-data.md`.

`METEO_DB_PATH` points at the SQLite database (default `data/meteobeguda.sqlite`).
`LANGFUSE_*` configure tracing; the defaults match the keys auto-provisioned by
the Docker stack.

## Docker stack (self-hosted Langfuse, optional ollama)

```bash
docker compose up -d                        # Langfuse v3 (uses ollama on the host)
docker compose --profile with-ollama up -d  # also run ollama in a container + pull MODEL
```

Langfuse UI: <http://localhost:3000> — login `admin@example.com` / `workshop123`.
The stack auto-provisions a project with the API keys in `.env.example`.

> All secrets in `docker-compose.yml` are playground-safe defaults. Regenerate
> them before any non-local use (`openssl rand -hex 32` for `ENCRYPTION_KEY`,
> `openssl rand -base64 32` for `SALT` / `NEXTAUTH_SECRET`).

## Testing

A test pyramid for non-deterministic code:

```bash
uv run pytest                 # unit + recorded-fixture (no network)
uv run pytest -m integration  # end-to-end vs a live ollama + Langfuse stack
```

- **unit** (`test_tools.py`) — read-only SQL guard, rendering, schema.
- **recorded fixture** (`test_loop_recorded.py`) — the loop driven by a scripted
  client, zero live calls; asserts orchestration and error feedback.
- **integration** (`test_integration.py`) — real model; skipped when the stack
  is down. Excluded by default via `addopts`.

## Slides

```bash
presenterm slides/meteo-agent.md
```

## Decisions & tradeoffs

- **From scratch *then* a framework.** You can only judge what LangGraph buys
  you after feeling its absence. The from-scratch tools are designed to carry
  forward.
- **OpenAI-compatible everywhere.** Model-agnostic with no abstraction layer to
  maintain; `base_url` is the seam.
- **Self-built MCP server.** The official SQLite MCP server is archived and
  flagged vulnerable — we wrap our own `run_sql` in FastMCP instead, and learn
  both sides of the protocol.
- **Read-only by construction.** The DB is opened `mode=ro` and queries are
  validated; tool errors are returned to the model, not raised, so it can
  self-correct.
- **Evals against ground truth.** Reference answers are computed from the
  database, so the eval set can't go stale.

## Dataset

`data/meteobeguda.sqlite` is a build artifact (~145 MB) and is gitignored.
`uv run python data/build_db.py` downloads the four period source databases from
the public `meteobeguda-etl` repo and consolidates them into one: it `UNION`s
`meteobeguda_events` and recreates the daily / monthly / yearly views. No local
source files are needed; override the location with `--base-url` if you mirror
them elsewhere.

## Next steps to production

- Pin models; version prompts as artifacts.
- Retries, timeouts, fallbacks at every API boundary.
- Sandbox tools; assume prompt injection.
- Budget cost and latency, not just correctness.
- Grow the eval set from real failures.
