from __future__ import annotations

import sys

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from meteo_agent.config import chat_model
from meteo_agent.prompt import SYSTEM_PROMPT
from meteo_agent.tools import RunSqlArgs, get_schema, run_sql

# TODO(checkpoint 04): wrap the SAME pure functions from tools.py as LangChain
# tools. Use StructuredTool.from_function; give run_sql the RunSqlArgs schema.
LANGCHAIN_TOOLS = []


def build_agent(model=None, tools=None):
    # TODO(checkpoint 04): build the LangGraph ReAct loop.
    #   - bind the tools to the chat model
    #   - a "model" node that invokes the bound model on state["messages"]
    #   - a prebuilt ToolNode for "tools"
    #   - edges: START -> model, model -conditional-> tools/END, tools -> model
    # Return the compiled graph.
    tools = tools or LANGCHAIN_TOOLS
    raise NotImplementedError("implement build_agent")


def run_agent(question: str, model=None, config=None) -> str:
    # TODO(checkpoint 04): invoke the compiled graph with a SystemMessage +
    # HumanMessage and return the final message's content.
    raise NotImplementedError("implement run_agent")


def main() -> None:
    if len(sys.argv) < 2:
        print('usage: meteo-graph "your question"', file=sys.stderr)
        raise SystemExit(1)
    question = " ".join(sys.argv[1:])
    print(run_agent(question))


if __name__ == "__main__":
    main()
