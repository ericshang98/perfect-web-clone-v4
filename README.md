# Perfect Web Clone v4

A complete rebuild of the web-cloning system that uses **Claude Code as the brain** and a
**deterministic MCP toolbelt as the hands and eyes**.

The North Star is **fidelity** — cloning a page so it looks as close to the original as
possible. Deployment is a side effect of producing build-grade output, not a goal.

## Agent-facing Harness

Perfect Web Clone is a Harness for Claude Code, Codex, and equivalent coding
agents. The user gives the agent one natural-language request, for example
`复刻 https://example.com`, and the loaded Skill requires that same agent to
continue through capture, full-page authoring, interaction implementation,
build, measured comparison, repair, and review handoff.

There is no separate user-facing CLI or cloning API. The connected agent is the
runtime and decision-maker; the `pwc4` MCP server supplies deterministic capture,
filesystem, browser, build, replay, and measurement tools. “One request” means
one user operation, not one model call—the agent may perform multiple internal
tool calls and repair iterations without asking the user to manage the workflow.

Every run maintains `.pwc/run.json` and an Agent-authored
`.pwc/comparison-contract.json`; a new source automatically receives a clean
sandbox so a prior website's components cannot leak into the next clone.
Detailed Token events are appended to `.pwc/token-usage.jsonl`; the run ledger
keeps compact actual/estimated totals, cached versus non-cached input, output,
phase/Agent attribution, budgets, and repair efficiency. Provider usage is used
when available and deterministic estimates remain explicitly separate.
Static UI remains pixel-strict. Live media, clocks, personalized content, and
third-party creatives must name the exact changing observation and replace it
with measured geometry, style, controls, and behavior invariants.
The Harness may report `ready_for_user_review` or
`failed_with_residuals`; only the user accepts the result.

## Four-reference acceptance run

The current client delivery run covers ReelShort, Livora, Kojeva, and TryKojiva.
Its machine-readable capture identities, fresh build results, link/weight checks,
responsive checks, fidelity scores, exact evidence paths, and unresolved local
visual residuals are recorded in:

- `delivery/four-reference-sites.json`
- `delivery/four-reference-sites.md`

The ledger is historical evidence, not an acceptance verdict. Numeric visual
scores are diagnostics only: a missing critical region or required common
interaction is now a hard failure, and final acceptance always belongs to the
user.

## What v4 is

v4 is a Python MCP server (built on the official `mcp` package, `FastMCP`, exposed over
**stdio**) plus a Claude Code **Skill** that scripts the continuous clone workflow:

1. **Extract** — `extract_page(url)` captures immutable raw evidence, compares
   it with the normalized derivative, discovers common interactions, and
   retries structural inconsistencies up to three times. The canonical raster
   preserves the authored default theme, including named dark themes; generated
   light/dark variants never replace it.
2. **Understand** — `get_comparison_evidence(source_id)` returns bounded
   volatility, critical-region, and interaction evidence; the Agent persists a
   fail-closed region contract.
3. **Section plan** — `get_section_plan(source_id)` returns the deterministic chunking plan.
4. **Single-agent reproduction** — one owning agent keeps whole-page context while writing each isolated `sections/{namespace}/` component. Sections are repair units; delegation is opt-in.
5. **Assemble** — `assemble_project(source_id)` deterministically wires up `App.jsx` / routes / `index.css`.
6. **Preview and compare** — `score_semantic_fidelity` measures static pixels
   and replays declared dynamic invariants without treating a random runtime
   frame as CSS.
7. **Targeted repair** — a worst-region packet stays under 16 KiB; only strict
   improvements with no hard-gate regression replace the best candidate.
8. **Production self-check** — `npm run build` must pass; re-screenshot the build output.
9. **Token accounting** — `begin_token_accounting`,
   `checkpoint_token_accounting`, `get_token_report`, and
   `finalize_token_accounting` measure the source-scoped run; a 250K soft /
   500K hard non-cached-input-plus-output budget stops low-value iteration
   without waiving red gates.
10. **Review handoff** — produce a deploy-grade `dist/` and report
   `ready_for_user_review`; the user makes the acceptance decision.

### The iron rule

> **The MCP tools NEVER call any LLM / Anthropic API / OpenAI API.**

Every tool is pure, deterministic Python: extract, chunk, write the sandbox, execute, screenshot,
build, diagnose. All "thinking / writing code / judging whether it looks alike" is done by
**Claude Code itself**, using the user's subscription — no `ANTHROPIC_API_KEY`, no metered billing.

## Relationship to v2

v2 (in `../perfect-web-clone_V2`) is a FastAPI + Next.js app with a hand-written agent harness
(`claude_agent.py`, `worker_agent.py`, `worker_manager.py`, `memory_sdk.py`, a giant
`mcp_tools.py`, Master/Worker orchestration).

v2's winning idea — **"session chunking → reproduce per chunk"** — is fully preserved in v4.
What v4 drops is the hand-written harness: instead of maintaining our own agent loop, message
format, retries, context compression, and concurrency orchestration, **we let Claude Code be the
brain.**

v3 reuses v2's LLM-decoupled assets as deterministic tools:

- `extractor/` (Playwright extraction)
- `section_analyzer` (pure-logic chunking)
- `boxlite/` sandbox (write / execute / preview / three-layer error detection — minus the LLM loop)

v2 is left **untouched**; the two repos coexist for long-term comparison.

## Tech stack of the produced artifact

**Vite + React + Tailwind, static build** (`npm run build` → pure static). The static output hosts
directly on Cloudflare Pages and maps cleanly onto v2's section-component model.

## Installation

```bash
# Python side (the MCP server)
python -m venv .venv
source .venv/bin/activate
pip install -e .
playwright install chromium
```

## Connecting from Claude Code via `.mcp.json`

v3 ships an example `.mcp.json` at the repo root that registers a stdio MCP server named **`pwc4`**:

```json
{
  "mcpServers": {
    "pwc4": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/absolute/path/to/perfect-web-clone-v4",
      "env": {
        "PYTHONPATH": "/absolute/path/to/perfect-web-clone-v4"
      }
    }
  }
}
```

Steps:

1. Copy `.mcp.json` into your project (or merge it into an existing one) and adjust `cwd` /
   `PYTHONPATH` to the absolute path of this repo (or run from inside it).
2. Make sure the `.venv` is active or `python` resolves to an interpreter with the deps installed.
3. Start Claude Code in that directory. It launches the `pwc4` server over stdio and the
   `extract_page`, `get_section_plan`, `sandbox_*`, `start_preview`, `build_project`, etc. tools
   become available.
4. Invoke the Skill (`skill/SKILL.md`) to run the continuous clone playbook.

## Repository layout

```
perfect-web-clone-v4/
├─ skill/                 # SKILL.md — the seven-phase clone playbook (the soul of v3)
├─ mcp_server/            # MCP server entry + tools (deterministic, no LLM)
│  └─ tools/
├─ core/                  # LLM-decoupled assets ported from v2
│  ├─ extractor/          # Playwright extraction
│  └─ boxlite/            # sandbox: write / exec / preview / error detection
├─ templates/             # base Vite + React + Tailwind project template
│  └─ base-project/
├─ pyproject.toml
├─ .mcp.json              # example Claude Code MCP config (server: pwc4)
└─ README.md
```
