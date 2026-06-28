#!/usr/bin/env bash
#
# Build the workshop's TDD branch history (branch per checkpoint).
#
# The default branch is the RED starting line, and the solution is *added* as you
# go — so anyone who clones and lands on `main` sees the workshop's starting point,
# not the answer key. The complete reference lives on the last branch.
#
#   main / start  all agent modules stubbed (RED: `uv run pytest` fails)  ← root
#   checkpoint-02 + tools solution        (GREEN: tests/test_tools.py passes)
#   checkpoint-03 + loop solution         (GREEN: tests/test_loop_recorded.py passes)
#   checkpoint-04 + graph solution
#   checkpoint-05 + mcp solution
#   checkpoint-06 + observability solution
#   checkpoint-07 + evals solution        = the complete reference (answer key)
#
# Each checkpoint-NN branches from checkpoint-(NN-1) and restores exactly the
# module(s) for that checkpoint from the reference, so `git diff checkpoint-02
# checkpoint-03` is precisely the solution for checkpoint 03.
#
# Run this from the repo root **on the complete reference, with a clean tree**
# (i.e. the agent modules in src/meteo_agent are fully implemented). The script
# captures that reference, then makes the RED stub state the root commit of `main`
# and `start`, walks the checkpoints up to the complete `checkpoint-07`, and drops
# the captured reference. No answer-key commit is left in the history.
#
# This script is the ONLY git automation in the workshop — run it yourself.
#
# Usage:
#   bash setup-branches.sh
#
set -euo pipefail

die () { echo "$@" >&2; exit 1; }

# --- preflight -------------------------------------------------------------
git rev-parse --git-dir >/dev/null 2>&1 || die "not a git repo"
[ -d src/meteo_agent ] || die "run from the repo root (src/meteo_agent not found)"
[ -d starter/src/meteo_agent ] || die "starter stubs not found"
git rev-parse --verify -q HEAD >/dev/null || die "no commits yet — commit the reference first"

if ! git diff --quiet || ! git diff --cached --quiet; then
  die "working tree is dirty — commit or stash the reference first"
fi

TEACHING=(start checkpoint-02 checkpoint-03 checkpoint-04 checkpoint-05 checkpoint-06 checkpoint-07)
for b in "${TEACHING[@]}"; do
  if git rev-parse --verify -q "$b" >/dev/null; then
    echo "teaching branches already exist — delete them first:" >&2
    echo "  git branch -D ${TEACHING[*]}" >&2
    exit 1
  fi
done

STUB="starter/src/meteo_agent"

# --- 0. capture the complete reference -------------------------------------
# The current HEAD is the finished reference; keep it on a temp branch so the
# checkpoints can restore real modules from it. It is deleted at the end, so it
# leaves no permanent commit in the history.
echo "==> capturing the reference (current HEAD)"
git branch _reference HEAD

# --- 1. main / start (RED): stub every agent module ------------------------
# An orphan branch makes the RED state a true root commit (no answer-key parent).
echo "==> creating the RED root (all modules stubbed)"
git checkout -q --orphan _newroot
cp "$STUB"/tools.py "$STUB"/loop.py "$STUB"/graph.py \
   "$STUB"/mcp_server.py "$STUB"/mcp_agent.py "$STUB"/observability.py \
   src/meteo_agent/
cp "$STUB"/evals/dataset.py "$STUB"/evals/run_experiment.py src/meteo_agent/evals/
git add -A
git commit -q -m "start: RED starting point — agent modules stubbed (uv run pytest fails)"

# --- 2..7. checkpoints (GREEN, cumulative) --------------------------------
checkpoint () {  # <new-branch> <from-branch> <message> <file...>
  local new="$1" from="$2" msg="$3"; shift 3
  echo "==> $new"
  git switch -q -c "$new" "$from"
  git checkout -q _reference -- "$@"
  git commit -q -m "$msg"
}

checkpoint checkpoint-02 _newroot      "checkpoint-02: tools solution (GREEN — test_tools.py)" \
  src/meteo_agent/tools.py
checkpoint checkpoint-03 checkpoint-02 "checkpoint-03: loop solution (GREEN — test_loop_recorded.py)" \
  src/meteo_agent/loop.py
checkpoint checkpoint-04 checkpoint-03 "checkpoint-04: graph solution (LangGraph)" \
  src/meteo_agent/graph.py
checkpoint checkpoint-05 checkpoint-04 "checkpoint-05: mcp solution (FastMCP server + adapter agent)" \
  src/meteo_agent/mcp_server.py src/meteo_agent/mcp_agent.py
checkpoint checkpoint-06 checkpoint-05 "checkpoint-06: observability solution (Langfuse)" \
  src/meteo_agent/observability.py
checkpoint checkpoint-07 checkpoint-06 "checkpoint-07: evals solution — complete reference (answer key)" \
  src/meteo_agent/evals/dataset.py src/meteo_agent/evals/run_experiment.py

# --- 8. verify checkpoint-07 == reference before discarding it -------------
git diff --quiet checkpoint-07 _reference \
  || die "checkpoint-07 does not match the reference — aborting (history left intact for inspection)"

# --- 9. finalize refs ------------------------------------------------------
# main and start both become the RED root; the captured reference is discarded.
git branch -f main  _newroot
git branch -f start _newroot
git switch -q main
git branch -D _newroot _reference >/dev/null

# --- done ------------------------------------------------------------------
echo
echo "done. branches:"
git branch --list main start 'checkpoint-*'
echo
echo "you are on 'main' (== start), the RED starting line. Sanity check:"
echo "  uv sync && uv run pytest        # expect failures (NotImplementedError)"
echo "verify the last branch is the complete solution:"
echo "  git diff --stat main checkpoint-07   # expect the 8 agent modules"
