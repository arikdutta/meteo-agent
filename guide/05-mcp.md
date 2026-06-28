# Checkpoint 05 — Tools as a protocol (MCP)

**Goal:** serve the same two tools over the **Model Context Protocol** with a
self-built FastMCP server, and drive the LangGraph agent against them. Same
tools, third delivery mechanism.

**Files:** `src/meteo_agent/mcp_server.py`, `src/meteo_agent/mcp_agent.py`
**Proof:** `uv run meteo-mcp-agent "..."`

## Why MCP, and why build our own

MCP standardizes how a model's host discovers and calls tools over a wire
protocol — so a tool server can be reused across many agents and clients. The
natural question: "isn't there an official SQLite MCP server?" There is, but it's
**archived and flagged vulnerable** — a perfect teachable moment. We wrap our own
`run_sql` in FastMCP instead, and learn both sides of the protocol: the server
that exposes tools, and the client that consumes them.

## What to implement

### `mcp_server.py` (the server)

Work through the `# TODO(checkpoint 05)` markers: register two `@mcp.tool()`
functions, `run_sql(query: str) -> str` and `get_schema() -> str`, each
delegating to the imported pure functions (`_run_sql` / `_get_schema`). Keep the
descriptions identical to the ones in `tools.OPENAI_TOOLS`. Once more: you are
**re-exposing**, not rewriting.

Smoke-test the server alone:

```bash
uv run meteo-mcp        # starts a stdio MCP server; Ctrl-C to stop
```

### `mcp_agent.py` (the client)

- **`SERVER_CONFIG`** — already points at launching `meteo-mcp` over stdio.
- **`load_mcp_tools()`** — connect with `MultiServerMCPClient(SERVER_CONFIG)` and
  return its tools. `langchain-mcp-adapters` hands you back LangChain-compatible
  tools, which means...
- **`run_agent(...)`** — you can pass those tools straight into the **same**
  `build_agent` from checkpoint 04. The graph doesn't know or care that its tools
  now arrive over a protocol. `ainvoke` it (MCP is async) and return the content.

## Run it

```bash
uv run meteo-mcp-agent "What was the wettest month on record?"
```

## Discuss

- Three implementations now share one `tools.py`. The pure-function core was the
  right abstraction boundary all along.
- The graph accepted MCP tools with zero changes because both `StructuredTool`
  (04) and the MCP adapter produce the same LangChain tool interface.
- Tradeoff: MCP adds a process boundary and async — real cost, bought in exchange
  for reuse and isolation.

## Checkpoint

- [ ] `meteo-mcp` starts a server; `meteo-mcp-agent` answers a question
- [ ] `tools.py` and `graph.py`'s `build_agent` are unchanged
- [ ] You can explain why we didn't use the official SQLite MCP server

**Solution:** `git diff checkpoint-05 -- src/meteo_agent/mcp_server.py src/meteo_agent/mcp_agent.py`.

Next: [06 — Observability](06-observability.md).
