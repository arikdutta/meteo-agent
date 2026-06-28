# Checkpoint 04 — The same agent, in LangGraph

**Goal:** rebuild the loop you just wrote as a LangGraph `StateGraph`, reusing
the *same* `tools.py` functions. You'll see exactly what the framework gives you
and what it costs.

**File:** `src/meteo_agent/graph.py`  **Proof:** `uv run meteo-graph "..."`

> Why rebuild something that works? Because you can only judge what a framework
> buys you after feeling its absence. You hand-wrote the loop in checkpoint 03;
> now compare.

## The mapping

Everything you did by hand has a LangGraph equivalent:

| You wrote by hand (03) | LangGraph (04) |
|---|---|
| `messages` list you appended to | `MessagesState` (managed for you) |
| the `while` loop | the graph's edges |
| "did the model call a tool?" branch | `tools_condition` |
| `dispatch_tool` + append result | `ToolNode` |
| `OPENAI_TOOLS` JSON schema | `StructuredTool.from_function(...)` |

## What to implement

Work through the `# TODO(checkpoint 04)` markers:

1. **`LANGCHAIN_TOOLS`** — wrap the same `run_sql` / `get_schema` from `tools.py`
   with `StructuredTool.from_function`. Give `run_sql` the `RunSqlArgs` schema and
   keep the descriptions identical to checkpoint 02. *You are not rewriting the
   tools — you are re-exposing them.*
2. **`build_agent(model, tools)`** — bind the tools to `chat_model()`, then build
   the graph: a `model` node that invokes the bound model on `state["messages"]`,
   a prebuilt `ToolNode("tools")`, and edges `START → model`,
   `model -(tools_condition)→ tools/END`, `tools → model`. Compile and return it.
3. **`run_agent(question, model, config)`** — invoke the compiled graph with a
   `SystemMessage(SYSTEM_PROMPT)` + `HumanMessage(question)` and return the last
   message's content. (The `config` parameter is the hook checkpoint 06 uses to
   attach tracing — leave it threaded through.)

## Run it

```bash
uv run meteo-graph "How many days in 2023 had a maximum above 35 C?"
```

Needs a model and the database. If you have a live ollama stack, the integration
test now passes too:

```bash
uv run pytest -m integration
```

## Discuss

- The graph is ~15 lines because `ToolNode` + `tools_condition` *are* your loop.
- The seam held: `tools.py` didn't change at all. That's the payoff of pure tools.
- What did you give up? Explicitness. The control flow is now declared, not
  written — great until you need to debug it (which is what checkpoint 06 is for).

## Checkpoint

- [ ] `meteo-graph` answers a question end to end
- [ ] `tools.py` is byte-for-byte unchanged from checkpoint 02
- [ ] You can point at where the "loop" lives in the graph

**Solution:** `git diff checkpoint-04 -- src/meteo_agent/graph.py` (see
[BRANCHES.md](../BRANCHES.md)).

Next: [05 — MCP](05-mcp.md).
