# Checkpoint 03 — The agent loop, by hand

**Goal:** build the agent loop yourself with native tool calls — no framework —
and make `tests/test_loop_recorded.py` pass. You'll feel exactly what an "agent"
is before any library hides it.

**File:** `src/meteo_agent/loop.py`  **Test:** `tests/test_loop_recorded.py`

```bash
uv run pytest tests/test_loop_recorded.py   # red
```

## What an agent loop actually is

Strip away the vocabulary and an agent is a `while` loop around a chat model:

```
seed messages with [system, user]
repeat (up to a limit):
    response = model.chat(messages, tools=TOOLS)
    if response has no tool calls:   -> return its text   (done)
    for each tool call:
        result = run the tool
        append {role: "tool", tool_call_id, content: result}
    # loop again — the model now sees the results and decides what's next
```

That's it. The model emits structured `tool_calls`; you execute them and feed
the results back; it either calls more tools or answers. The "intelligence" is
the model deciding; the "agency" is your loop letting it act and react.

## What to implement

Work through the `# TODO(checkpoint 03)` markers in `loop.py`:

| Function | Job |
|---|---|
| `dispatch_tool(name, arguments)` | route to `run_sql` / `get_schema`; validate `run_sql` args with `RunSqlArgs`; return `"error: ..."` for unknown tools or exceptions (never raise) |
| `assistant_message(message)` | convert the SDK's assistant message into the plain dict you append (its `content` plus any `tool_calls`) |
| `run_agent(question, client, model, trace)` | the loop above, capped at `MAX_STEPS`; call `trace(name, args)` before each tool if given; return a `"stopped: ..."` string if the cap is hit |

The message bookkeeping is the fiddly part and the whole point:
- After the model replies, append the **assistant** message (including its
  `tool_calls`) *before* appending the tool results — order matters to the API.
- Each tool result is `{"role": "tool", "tool_call_id": call.id, "content": ...}`.
- Tool-call `arguments` arrive as a JSON **string** — `json.loads` it.

## Why the test uses a fake client

`tests/test_loop_recorded.py` injects a `FakeClient` with a **scripted**
sequence of model responses — first a `run_sql` tool call, then a final answer.
No network, no model, fully deterministic. This is how you test non-deterministic
systems: pin the model's outputs and assert on your **orchestration** —
- the tool actually ran and its result was fed back as a `role: "tool"` message,
- a tool *error* is also fed back (so the model can self-correct),
- the final answer is returned.

Read the fake before you implement; it documents the exact shapes
(`message.tool_calls`, `call.function.arguments`, `choices[0].message`) your code
must handle.

## Run it for real (optional, needs a model + DB)

```bash
uv run meteo-loop "What was the hottest day on record? Use the daily view."
```

You'll see the tool calls logged to stderr and a prose answer on stdout.

## Checkpoint

```bash
uv run pytest tests/test_loop_recorded.py   # green
uv run pytest                               # tools + loop green; integration skipped
```

- [ ] Tool results (and errors) are appended as `role: "tool"` messages
- [ ] The loop terminates when the model stops calling tools
- [ ] `MAX_STEPS` prevents an infinite loop

**Solution:** `git diff checkpoint-03 -- src/meteo_agent/loop.py`. Keep this
picture in mind for the next checkpoint — everything LangGraph does, you just did
by hand.

Next: [04 — LangGraph](04-graph.md).
