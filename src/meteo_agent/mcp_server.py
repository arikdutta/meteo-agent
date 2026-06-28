from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from meteo_agent.tools import get_schema as _get_schema
from meteo_agent.tools import run_sql as _run_sql

mcp = FastMCP("meteobeguda")


# TODO(checkpoint 05): expose the SAME pure functions over MCP.
# Register two @mcp.tool() functions, run_sql(query: str) -> str and
# get_schema() -> str, each delegating to the imported _run_sql / _get_schema.
# Keep the descriptions identical to the ones in tools.OPENAI_TOOLS.


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
