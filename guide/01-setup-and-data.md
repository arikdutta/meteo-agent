# Checkpoint 01 — Setup & data

**Goal:** a running project, a database to query, and a model behind a single
swappable seam. By the end, `uv run pytest` collects the test suite (all red)
and you understand where the model comes from.

## 1. The project

The workshop is delivered as a branch history (see [BRANCHES.md](../BRANCHES.md)).
Start on the RED branch and work at the repo root:

```bash
git switch start        # all agent modules stubbed
uv sync                 # creates .venv, installs deps
cp .env.example .env
uv run pytest
```

You should see failing tests, not import errors. Red is the starting line — the
modules are stubs that `raise NotImplementedError`. If you get a *collection*
error (something can't import), flag it now; the rest of the day builds on a
clean import graph.

> Prefer not to use git branches? `cd starter` is a self-contained copy
> with the same stubs and tests — run the same `uv sync` / `pytest` there. The
> guide assumes the branch workflow; in directory mode, "the reference" is at
> `../src/meteo_agent/` instead of on a `checkpoint-NN` branch.

## 2. The data

The agent answers questions about the **Beguda weather station** — 676,595
sub-daily readings from 2002 to today, in one SQLite file with three
pre-aggregated views (`meteobeguda_daily`, `_monthly`, `_yearly`).

IN order to get the data, you need to run a download script: `uv run python data/build_db.py` downloads the four period
  databases from the public `meteobeguda-etl` repo, consolidates them into one,
  and recreates the views. (Override the source with `--base-url`.)

You don't need this file for checkpoints 02–03: the tests build their own tiny
in-memory database (`tests/conftest.py`). You just need it in order to *run* the agent.

Sanity check (once you have the file):

```bash
uv run python -c "import sqlite3,os; \
print(sqlite3.connect(os.environ.get('METEO_DB_PATH','../data/meteobeguda.sqlite')).execute('select count(*) from meteobeguda_events').fetchone())"
```

## 3. The model seam

Open `src/meteo_agent/config.py`. This is the **only** place the project knows
about a model provider. Everything goes through an **OpenAI-compatible** surface,
and the *only* thing that changes between providers is three environment
variables:

```bash
OPENAI_BASE_URL=...   # the endpoint
OPENAI_API_KEY=...    # the credential
MODEL=...             # the model name
```

`config.py` exposes both an `openai_client()` (used by the from-scratch loop)
and a `chat_model()` (a LangChain `ChatOpenAI`, used by the graph). Same seam,
two consumers.

### Switching providers (env-only)

The default is local **ollama** (free, offline). The same code runs against any
OpenAI-compatible endpoint — just change the three vars in `.env`:

```bash
# OpenAI
OPENAI_BASE_URL=https://api.openai.com/v1   OPENAI_API_KEY=sk-...   MODEL=gpt-4o-mini
# Anthropic (Claude)
OPENAI_BASE_URL=https://api.anthropic.com/v1/   OPENAI_API_KEY=sk-ant-...   MODEL=claude-opus-4-8
# Google (Gemini)
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/   OPENAI_API_KEY=<key>   MODEL=gemini-2.5-pro
```

> **The production caveat — worth a minute of discussion.**
> Anthropic's and Google's OpenAI-compatible endpoints are **compatibility
> shims**, not their real APIs. They exist for quick comparison and testing, and
> they're lossy: tool-calling fidelity, extended thinking, streaming, and error
> shapes don't all survive the translation. For a demo they're fine; for
> production you'd switch to the native integration — `langchain-anthropic`
> (`ChatAnthropic`) or `langchain-google-genai` (`ChatGoogleGenerativeAI`) for
> the graph, and the native `anthropic` SDK for the from-scratch loop. The graph
> swaps cleanly (it only wants a `BaseChatModel`); the from-scratch loop does
> not, because the native message/tool shapes differ — which is exactly what the
> OpenAI tool-calling format is abstracting. That's the lesson: one seam buys you
> reach, but a shim is not the real surface.

For the workshop we stay on the single OpenAI-compatible seam everywhere.

## Checkpoint

- [ ] `uv sync` succeeds and `.env` exists
- [ ] `uv run pytest` runs and reports failures (not import errors)
- [ ] You can name the three environment variables that switch providers
- [ ] You can point at the database and read a row count

Next: [02 — Tools](02-tools.md), where the red starts turning green.
