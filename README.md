# Perfect Web Clone v4

A complete rebuild of the web-cloning system that uses **Claude Code as the brain** and a
**deterministic MCP toolbelt as the hands and eyes**.

The North Star is **fidelity** — cloning a page so it looks as close to the original as
possible. Deployment is a side effect of producing build-grade output, not a goal.

## What v3 is

v3 is a Python MCP server (built on the official `mcp` package, `FastMCP`, exposed over
**stdio**) plus a Claude Code **Skill** that scripts the seven-phase clone workflow:

1. **Extract** — `extract_page(url)` runs Playwright, captures DOM/CSS/assets/themes, returns a `source_id`.
2. **Section plan** — `get_section_plan(source_id)` returns the deterministic chunking plan.
3. **Parallel reproduction** — Claude Code spawns one native Task subagent per section; each writes only its own `sections/{namespace}/`.
4. **Assemble** — `assemble_project(source_id)` deterministically wires up `App.jsx` / routes / `index.css`.
5. **Preview self-check (dev)** — start a Vite dev server, screenshot, compare to the original, iterate.
6. **Production self-check (build)** — `npm run build` must pass; re-screenshot the build output.
7. **Deliver** — produce a deploy-grade `dist/` (optional Dockerfile / Cloudflare Pages deploy).

### The iron rule

> **The MCP tools NEVER call any LLM / Anthropic API / OpenAI API.**

Every tool is pure, deterministic Python: extract, chunk, write the sandbox, execute, screenshot,
build, diagnose. All "thinking / writing code / judging whether it looks alike" is done by
**Claude Code itself**, using the user's subscription — no `ANTHROPIC_API_KEY`, no metered billing.

## Relationship to v2

v2 (in `../perfect-web-clone_V2`) is a FastAPI + Next.js app with a hand-written agent harness
(`claude_agent.py`, `worker_agent.py`, `worker_manager.py`, `memory_sdk.py`, a giant
`mcp_tools.py`, Master/Worker orchestration).

v2's winning idea — **"session chunking → reproduce per chunk"** — is fully preserved in v3.
What v3 drops is the hand-written harness: instead of maintaining our own agent loop, message
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
4. Invoke the Skill (`skill/SKILL.md`) to run the seven-phase clone playbook.

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
