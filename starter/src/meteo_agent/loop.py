from __future__ import annotations

import json
import sys

from meteo_agent.config import model_name, openai_client
from meteo_agent.prompt import SYSTEM_PROMPT
from meteo_agent.tools import OPENAI_TOOLS, RunSqlArgs, get_schema, run_sql

MAX_STEPS = 8


def dispatch_tool(name: str, arguments: dict) -> str:
    # TODO(checkpoint 03): route a tool call by name to run_sql / get_schema.
    # Validate run_sql args with RunSqlArgs. Return "error: ..." for unknown
    # tools or raised exceptions (never raise out of here).
    raise NotImplementedError("implement dispatch_tool")


def assistant_message(message) -> dict:
    # TODO(checkpoint 03): convert an OpenAI SDK assistant message into the
    # plain-dict form you append to `messages` (content + any tool_calls).
    raise NotImplementedError("implement assistant_message")


def run_agent(question: str, client=None, model: str | None = None, trace=None) -> str:
    # TODO(checkpoint 03): drive the agent loop by hand.
    #   1. seed messages with SYSTEM_PROMPT + the user question
    #   2. up to MAX_STEPS times: call the chat completions API with OPENAI_TOOLS
    #   3. if the model returned no tool_calls, return its content (done)
    #   4. otherwise run each tool call, append a {"role": "tool", ...} result,
    #      and loop. Call trace(name, arguments) before each tool if provided.
    # Return a "stopped: ..." message if MAX_STEPS is exhausted.
    client = client or openai_client()
    model = model or model_name()
    raise NotImplementedError("implement run_agent")


def log_tool_call(name: str, arguments: dict) -> None:
    print(f"  -> {name}({json.dumps(arguments, ensure_ascii=False)})", file=sys.stderr)


def main() -> None:
    if len(sys.argv) < 2:
        print('usage: meteo-loop "your question"', file=sys.stderr)
        raise SystemExit(1)
    question = " ".join(sys.argv[1:])
    print(run_agent(question, trace=log_tool_call))


if __name__ == "__main__":
    main()
