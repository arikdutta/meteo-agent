# Branch-per-checkpoint (TDD red → green)

The workshop ships as a branch history so participants can start from a stubbed
project and check their work against a solution at any point. The default branch
is the RED starting line — clone the repo and you land on the workshop's starting
point, not the answer key. The solution is *added* as you go; the complete
reference is the last branch.

```
main / start  all agent modules stubbed              ← RED, you start here
checkpoint-02 + tools solution                       ← GREEN
checkpoint-03 + loop solution                        ← GREEN
checkpoint-04 + graph solution
checkpoint-05 + mcp solution
checkpoint-06 + observability solution
checkpoint-07 + evals solution        = complete reference (answer key)
```

Each `checkpoint-NN` is the **cumulative** solution through checkpoint NN (and
stubs for everything after). So the diff between consecutive branches is exactly
one checkpoint's solution:

```bash
git diff checkpoint-02 checkpoint-03 -- src/meteo_agent/   # the loop solution
```

## Creating the branches

The branches are built by a script (the only git automation in the repo). Run it
from the repo root **on the complete reference, with a clean tree** (the agent
modules in `src/meteo_agent/` fully implemented):

```bash
bash setup-branches.sh
```

It captures the reference, commits the stubbed (RED) state as the root of `main`
and `start`, then walks the checkpoints — restoring one checkpoint's module(s)
from the reference each step — up to `checkpoint-07`, which it verifies equals the
reference. The captured reference is then discarded, so no answer-key commit is
left in the history. It refuses to run if the teaching branches already exist.

## Participant workflow

You start on `main`, the RED starting line (`start` is the same commit, kept as an
alias — `git switch start` is optional):

```bash
uv sync && cp .env.example .env
uv run pytest               # red — modules raise NotImplementedError
```

Then, per checkpoint (following `guide/`):

```bash
# implement the # TODO(checkpoint NN) markers in src/meteo_agent/<module>.py
uv run pytest tests/test_tools.py      # turn it green (cp02/03 have unit tests)
```

**Stuck, or want to check?** The solution for checkpoint NN lives on
`checkpoint-NN`:

```bash
git diff checkpoint-02 -- src/meteo_agent/tools.py    # see the solution as a diff
git checkout checkpoint-02 -- src/meteo_agent/tools.py # ...or take it and move on
```

**Behind, or want a clean slate for the next checkpoint?** Jump straight to the
cumulative solution and start the next one from there:

```bash
git switch -c my-work checkpoint-03   # tools+loop solved; ready for checkpoint-04
```

## Red vs green by checkpoint

| Checkpoint | "Red" proof | "Green" proof |
|---|---|---|
| 02 tools | `tests/test_tools.py` fails | `tests/test_tools.py` passes |
| 03 loop | `tests/test_loop_recorded.py` fails | it passes |
| 04 graph | `uv run meteo-graph "..."` raises / integration skipped | the agent answers; `pytest -m integration` passes against a live stack |
| 05 mcp | `uv run meteo-mcp-agent "..."` raises | the agent answers over MCP |
| 06 observability | `uv run meteo-trace "..."` raises | a trace appears in Langfuse |
| 07 evals | `uv run meteo-eval` raises | the eval prints a score |

Checkpoints 02–03 are pure offline red→green (no model, no network — the tests
use an in-memory SQLite). 04–07 are validated by **running the agent**, so their
"red" is "it doesn't run yet" and "green" is a successful run or trace.

## Note on `starter/`

`starter/` is the source of the stub files the script copies onto
`start`, and doubles as a self-contained directory for anyone who prefers not to
use the branches. The two delivery modes share the same stubs and guide.
