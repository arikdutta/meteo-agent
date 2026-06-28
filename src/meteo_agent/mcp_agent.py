from __future__ import annotations

import asyncio
import sys

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

from meteo_agent.graph import build_agent
from meteo_agent.prompt import SYSTEM_PROMPT

# TODO(checkpoint 05): describe how to launch the MCP server as a subprocess
# over stdio. The command runs the `meteo-mcp` script (i.e. mcp_server.main).
SERVER_CONFIG = {
    "meteobeguda": {
        "command": "uv",
        "args": ["run", "meteo-mcp"],
        "transport": "stdio",
    }
}


async def load_mcp_tools():
    # TODO(checkpoint 05): connect with MultiServerMCPClient(SERVER_CONFIG) and
    # return its tools (already LangChain-compatible).
    raise NotImplementedError("implement load_mcp_tools")


async def run_agent(question: str, model=None, config=None) -> str:
    # TODO(checkpoint 05): load the MCP tools, build the SAME graph from
    # checkpoint 04 with those tools, and ainvoke it. Return the final content.
    raise NotImplementedError("implement run_agent")


def main() -> None:
    if len(sys.argv) < 2:
        print('usage: meteo-mcp-agent "your question"', file=sys.stderr)
        raise SystemExit(1)
    question = " ".join(sys.argv[1:])
    print(asyncio.run(run_agent(question)))


if __name__ == "__main__":
    main()
