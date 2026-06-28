from __future__ import annotations

import json
from types import SimpleNamespace

from meteo_agent import loop


class FakeFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class FakeToolCall:
    def __init__(self, call_id, name, arguments):
        self.id = call_id
        self.type = "function"
        self.function = FakeFunction(name, arguments)


class FakeMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls


class FakeCompletions:
    def __init__(self, scripted):
        self.scripted = list(scripted)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=self.scripted.pop(0))])


class FakeClient:
    def __init__(self, scripted):
        self.chat = SimpleNamespace(completions=FakeCompletions(scripted))


def test_loop_runs_tool_then_returns_answer(meteo_db):
    query = "SELECT date FROM meteobeguda_daily ORDER BY temperature_max DESC LIMIT 1"
    scripted = [
        FakeMessage(tool_calls=[FakeToolCall("c1", "run_sql", json.dumps({"query": query}))]),
        FakeMessage(content="The hottest day was 2010-08-16."),
    ]
    client = FakeClient(scripted)
    traced = []

    answer = loop.run_agent(
        "What was the hottest day?",
        client=client,
        model="fake",
        trace=lambda name, args: traced.append(name),
    )

    assert answer == "The hottest day was 2010-08-16."
    assert traced == ["run_sql"]

    second_request = client.chat.completions.calls[1]["messages"]
    assert any(
        message.get("role") == "tool" and "2010-08-16" in message["content"]
        for message in second_request
    )


def test_loop_feeds_tool_errors_back_to_model(meteo_db):
    scripted = [
        FakeMessage(tool_calls=[FakeToolCall("c1", "run_sql", json.dumps({"query": "DROP TABLE x"}))]),
        FakeMessage(content="I cannot run that."),
    ]
    client = FakeClient(scripted)

    answer = loop.run_agent("delete everything", client=client, model="fake")

    assert answer == "I cannot run that."
    second_request = client.chat.completions.calls[1]["messages"]
    tool_message = next(m for m in second_request if m.get("role") == "tool")
    assert tool_message["content"].startswith("error:")
