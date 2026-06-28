from __future__ import annotations

import re
import sqlite3

from pydantic import BaseModel, Field

from meteo_agent.config import database_path

MAX_ROWS = 100
FORBIDDEN_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "attach",
    "detach",
    "truncate",
}


class RunSqlArgs(BaseModel):
    query: str = Field(
        description="A single read-only SQL SELECT statement against the meteobeguda SQLite database."
    )


def read_only_connection() -> sqlite3.Connection:
    # TODO(checkpoint 02): open the SQLite database at database_path() in
    # read-only mode (hint: the `file:...?mode=ro` URI form + uri=True).
    raise NotImplementedError("implement read_only_connection")


def ensure_read_only(query: str) -> None:
    # TODO(checkpoint 02): raise ValueError unless `query` is a single
    # read-only statement. The tests in tests/test_tools.py define the contract:
    #   - allow only statements starting with SELECT or WITH
    #   - reject more than one statement (a ';' in the middle)
    #   - reject any FORBIDDEN_KEYWORDS token
    raise NotImplementedError("implement ensure_read_only")


def render_table(columns: list[str], rows: list[tuple]) -> str:
    # TODO(checkpoint 02): render rows as a pipe-delimited table the model can
    # read. Return "(no rows)" when empty; show None as an empty string; cap at
    # MAX_ROWS and note the truncation. See tests for the exact format.
    raise NotImplementedError("implement render_table")


def run_sql(query: str) -> str:
    # TODO(checkpoint 02): validate with ensure_read_only, execute against a
    # read_only_connection, fetch up to MAX_ROWS + 1, and render. Return DB
    # errors as text ("error: ...") rather than raising, so the model can
    # self-correct. ValueError from ensure_read_only should still propagate.
    raise NotImplementedError("implement run_sql")


def get_schema() -> str:
    # TODO(checkpoint 02): return a compact description of meteobeguda_events
    # plus the daily/monthly/yearly views (names + columns), built from
    # PRAGMA table_info and sqlite_master.
    raise NotImplementedError("implement get_schema")


OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_sql",
            "description": "Run a single read-only SQL SELECT query and return the rows.",
            "parameters": RunSqlArgs.model_json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_schema",
            "description": "Return the database schema: the events table and the daily/monthly/yearly views.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

TOOL_FUNCTIONS = {"run_sql": run_sql, "get_schema": get_schema}
