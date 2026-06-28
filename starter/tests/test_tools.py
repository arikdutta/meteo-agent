from __future__ import annotations

import pytest

from meteo_agent.tools import ensure_read_only, get_schema, render_table, run_sql


@pytest.mark.parametrize(
    "query",
    [
        "DROP TABLE meteobeguda_events",
        "DELETE FROM meteobeguda_events",
        "UPDATE meteobeguda_events SET rain = 0",
        "SELECT 1; SELECT 2",
        "INSERT INTO meteobeguda_events VALUES (1)",
    ],
)
def test_ensure_read_only_blocks_writes(query):
    with pytest.raises(ValueError):
        ensure_read_only(query)


@pytest.mark.parametrize(
    "query",
    [
        "SELECT * FROM meteobeguda_daily",
        "  select date from meteobeguda_events  ",
        "WITH t AS (SELECT 1 AS n) SELECT n FROM t",
    ],
)
def test_ensure_read_only_allows_selects(query):
    ensure_read_only(query)


def test_render_table_handles_empty():
    assert render_table(["date"], []) == "(no rows)"


def test_render_table_renders_none_as_blank():
    assert render_table(["a", "b"], [(1, None)]) == "a | b\n1 | "


def test_run_sql_returns_expected_value(meteo_db):
    output = run_sql(
        "SELECT date FROM meteobeguda_daily ORDER BY temperature_max DESC LIMIT 1"
    )
    assert "2010-08-16" in output


def test_run_sql_rejects_write(meteo_db):
    with pytest.raises(ValueError):
        run_sql("DELETE FROM meteobeguda_events")


def test_run_sql_returns_db_errors_as_text(meteo_db):
    output = run_sql("SELECT no_such_column FROM meteobeguda_events")
    assert output.startswith("error:")


def test_get_schema_lists_table_and_views(meteo_db):
    schema = get_schema()
    assert "meteobeguda_events" in schema
    assert "meteobeguda_yearly" in schema
