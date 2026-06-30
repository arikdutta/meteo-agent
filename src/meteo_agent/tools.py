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
    path = database_path().resolve()
    return sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)


def ensure_read_only(query: str) -> None:
    stripped = query.strip()
    first_token = stripped.split()[0].lower() if stripped.split() else ""
    if first_token not in ("select", "with"):
        raise ValueError(f"only SELECT or WITH queries are allowed, got: {first_token!r}")
    without_trailing = stripped.rstrip(";")
    if ";" in without_trailing:
        raise ValueError("multiple statements are not allowed")
    tokens = set(re.findall(r"\b[a-zA-Z_]+\b", query.lower()))
    forbidden = tokens & FORBIDDEN_KEYWORDS
    if forbidden:
        raise ValueError(f"forbidden keyword(s): {forbidden}")


def render_table(columns: list[str], rows: list[tuple]) -> str:
    if not rows:
        return "(no rows)"
    truncated = len(rows) > MAX_ROWS
    display_rows = rows[:MAX_ROWS]
    header = " | ".join(columns)
    body = "\n".join(" | ".join("" if v is None else str(v) for v in row) for row in display_rows)
    result = f"{header}\n{body}"
    if truncated:
        result += f"\n(truncated to {MAX_ROWS} rows)"
    return result


def run_sql(query: str) -> str:
    ensure_read_only(query)
    try:
        conn = read_only_connection()
        cursor = conn.execute(query)
        columns = [d[0] for d in cursor.description]
        rows = cursor.fetchmany(MAX_ROWS + 1)
        conn.close()
        return render_table(columns, rows)
    except sqlite3.Error as e:
        return f"error: {e}"


def get_schema() -> str:
    conn = read_only_connection()
    cursor = conn.execute(
        "SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view') ORDER BY type, name"
    )
    objects = cursor.fetchall()
    lines = []
    for name, obj_type in objects:
        col_cursor = conn.execute(f"PRAGMA table_info({name})")
        columns = [row[1] for row in col_cursor.fetchall()]
        lines.append(f"{obj_type} {name}: {', '.join(columns)}")
    conn.close()
    return "\n".join(lines)


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
