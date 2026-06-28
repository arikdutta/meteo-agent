from __future__ import annotations

import sys
from functools import lru_cache


def langfuse_handler():
    # TODO(checkpoint 06): return a Langfuse LangChain CallbackHandler.
    raise NotImplementedError("implement langfuse_handler")


@lru_cache
def langfuse_client():
    from langfuse import get_client

    return get_client()


def traced_config() -> dict:
    # TODO(checkpoint 06): return the LangChain config dict that attaches the
    # Langfuse callback handler: {"callbacks": [...]}.
    raise NotImplementedError("implement traced_config")


def run_traced(question: str, model=None) -> str:
    # TODO(checkpoint 06): run the graph agent with traced_config() so the run
    # shows up in Langfuse, then flush the client before returning the answer.
    raise NotImplementedError("implement run_traced")


def main() -> None:
    if len(sys.argv) < 2:
        print('usage: meteo-trace "your question"', file=sys.stderr)
        raise SystemExit(1)
    print(run_traced(" ".join(sys.argv[1:])))


if __name__ == "__main__":
    main()
