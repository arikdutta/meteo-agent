# Checkpoint 02 — Tools

**Goal:** implement the two pure tools the agent will use — `run_sql` and
`get_schema` — and make `tests/test_tools.py` pass. These functions are the
foundation reused unchanged by all three agent implementations.

**File:** `src/meteo_agent/tools.py`  **Test:** `tests/test_tools.py`

```bash
uv run pytest tests/test_tools.py   # red
```

## The idea: tools are just functions

An "agent tool" is nothing exotic — it's a plain function with a typed signature
and a description. The model decides *when* to call it; your code decides *what
it does* and *what it's allowed to do*. Keep tools pure (input → output, no
hidden global state) and they're trivial to test without a model in the loop —
which is exactly what this checkpoint does.

We expose two:

- `run_sql(query: str) -> str` — run a read-only SELECT, return rendered rows.
- `get_schema() -> str` — describe the table and views so the model can write
  correct SQL.

## Read-only by construction

The single most important design choice here: the agent writes SQL, but it must
**never** be able to mutate the database. We enforce that two ways, belt and
braces:

1. **Open the connection read-only.** SQLite's URI form
   `file:<path>?mode=ro` (with `uri=True`) makes writes fail at the driver level.
2. **Validate the query** before running it: allow only `SELECT`/`WITH`, reject
   multiple statements, reject a denylist of mutating keywords.

The tests encode the exact contract — let them drive you.

## What to implement

Work through the `# TODO(checkpoint 02)` markers:

| Function | Contract (from the tests) |
|---|---|
| `read_only_connection()` | open `database_path()` with `mode=ro` |
| `ensure_read_only(query)` | `ValueError` unless a single `SELECT`/`WITH`; reject `;`-joined statements and any `FORBIDDEN_KEYWORDS` token |
| `render_table(columns, rows)` | `"(no rows)"` when empty; `None` → `""`; pipe-delimited; cap at `MAX_ROWS` and note truncation |
| `run_sql(query)` | validate → execute on a read-only connection → render; return DB errors as `"error: ..."` text (don't raise), but let `ValueError` from validation propagate |
| `get_schema()` | list `meteobeguda_events` columns + the three views (use `PRAGMA table_info` and `sqlite_master`) |

Tips:
- Tokenize the lowercased query with a simple regex (`[a-z_]+`) and intersect
  with `FORBIDDEN_KEYWORDS` — substring matching would false-positive on column
  names like `updated_at`.
- Returning DB errors as a string (instead of raising) is deliberate: in the
  loop, that text goes back to the model so it can fix its own SQL.

## Why `RunSqlArgs` and `OPENAI_TOOLS` are already given

The Pydantic args model and the `OPENAI_TOOLS` schema are provided so you can see
how a tool's JSON schema is *derived from a type* (`RunSqlArgs.model_json_schema()`),
not hand-written. You'll feed `OPENAI_TOOLS` to the model in checkpoint 03.

## Checkpoint

```bash
uv run pytest tests/test_tools.py   # green — all 9 pass
```

- [ ] Writes are blocked both by validation and by the read-only connection
- [ ] A bad column name comes back as `"error: ..."`, not an exception
- [ ] `get_schema()` mentions the table and the yearly view

**Solution:** `git diff checkpoint-02 -- src/meteo_agent/tools.py` (or, in
directory mode, `../src/meteo_agent/tools.py`). Note how small it is — the
discipline is in the contract, not the line count.

Next: [03 — The loop](03-loop.md).
