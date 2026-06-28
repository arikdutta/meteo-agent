# meteo-agent — workshop starter

This is the **starter** for *Building a Production-Grade AI Agent with Python* —
the `meteo_agent` modules are stubs with `# TODO(checkpoint NN)` markers you fill
in. The completed version lives at the repo root (`../src/meteo_agent/`).

> **Primary delivery is git branches**, not this directory. Run
> `bash ../setup-branches.sh` once, then `git switch start` and work at the repo
> root; see [`../BRANCHES.md`](../BRANCHES.md). This directory is the stub source
> the script uses, and a self-contained fallback if you'd rather not use branches.

Follow the build-along guide in [`../guide/`](../guide/), one checkpoint at a time.

## Setup (checkpoint 01)

```bash
uv sync                 # install dependencies into .venv
cp .env.example .env    # defaults target local ollama
uv run pytest           # everything is RED — that's the starting line
```

You do **not** need the 145 MB database or the docker stack to run the unit and
recorded-fixture tests: `tests/conftest.py` builds a tiny in-memory SQLite with
the same schema. You only need the real database and a model to *run* the agent
end to end (see guide 01).

## The loop you'll repeat

Each checkpoint is a small red→green step:

```bash
uv run pytest tests/test_tools.py        # see the failing tests for a checkpoint
# ...implement the TODOs in the matching module...
uv run pytest tests/test_tools.py        # green
```

| Checkpoint | You implement | Tests / proof |
|---|---|---|
| 01 setup & data | nothing — get the project running | `uv run pytest` collects |
| 02 tools | `src/meteo_agent/tools.py` | `tests/test_tools.py` |
| 03 loop | `src/meteo_agent/loop.py` | `tests/test_loop_recorded.py` |
| 04 graph | `src/meteo_agent/graph.py` | `uv run meteo-graph "..."` |
| 05 mcp | `src/meteo_agent/mcp_server.py`, `mcp_agent.py` | `uv run meteo-mcp-agent "..."` |
| 06 observability | `src/meteo_agent/observability.py` | a trace in Langfuse |
| 07 evals | `src/meteo_agent/evals/*.py` | `uv run meteo-eval` |

Stuck? The reference implementation of each file is one directory up at
`../src/meteo_agent/<same-file>`. Peek when you're ready, not before.
