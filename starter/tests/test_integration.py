from __future__ import annotations

import os
import urllib.request

import pytest

pytestmark = pytest.mark.integration


def ollama_reachable(base_url: str) -> bool:
    root = base_url.removesuffix("/v1")
    try:
        urllib.request.urlopen(f"{root}/api/tags", timeout=2)
        return True
    except Exception:
        return False


def test_graph_answers_hottest_day_against_real_stack():
    base_url = os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1")
    if not ollama_reachable(base_url):
        pytest.skip("ollama is not reachable; start the docker stack to run integration tests")

    from meteo_agent.graph import run_agent

    answer = run_agent("What was the hottest day on record? Use the daily view.")
    assert "2010" in answer
