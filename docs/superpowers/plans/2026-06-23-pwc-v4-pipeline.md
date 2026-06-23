# Perfect Web Clone v4 Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the v4 layers that decouple clean code from pixel fidelity — a semantic IR, a clean codegen, a recognizer registry, and three deterministic acceptance gates plus a self-heal loop — so the output is clean by construction and fidelity is enforced as a measured gate.

**Architecture:** See `docs/architecture.md`. Capture → Semantic IR (+ design tokens) → Recognizers → Clean codegen → Verify/self-heal, with `fingerprint_gate`, `weight_gate`, `fidelity_gate` as hard gates. All tools are deterministic Python (no LLM); Claude Code only drives Layer-4 repair.

**Tech Stack:** Python 3.11, Pydantic v2, BeautifulSoup4, Playwright, Pillow + scikit-image (SSIM), pytest. Output artifact: Vite + React + Tailwind static build.

---

## Conventions for every task
- TDD: write the failing test first, watch it fail, implement minimally, watch it pass, commit.
- New code lives under `core/ir/`, `core/recognizers/`, `core/codegen/`, `core/gates/`.
- Tests live under `tests/` mirroring the module path (e.g. `tests/ir/test_tokens.py`).
- Run a single test: `.venv/bin/python -m pytest tests/<path>::<name> -v`.
- Keep each module pure and import-light; no module under `core/` may import `anthropic`/`openai`.
- Commit message style: `feat(ir): …`, `feat(gates): …`, `test(...)`, `feat(codegen): …`.

---

## Task 1: IR schema (the stable contract)

**Files:**
- Create: `core/ir/__init__.py`
- Create: `core/ir/schema.py`
- Test: `tests/ir/test_schema.py`

- [ ] **Step 1 — failing test:** assert an `IRNode` round-trips through `model_dump()/model_validate()` and that required fields (`id`, `role`, `layout`, `style`, `children`) exist; assert a `Design Tokens` table holds `colors/space/type/radius/shadow` maps; assert `IRDocument(root, tokens, breakpoints)` validates.

```python
from core.ir.schema import IRNode, IRDocument, DesignTokens
def test_irnode_roundtrip():
    n = IRNode(id="n1", role="hero", layout={"mode":"flex"}, style={"color":"token.color.ink"}, children=[])
    assert IRNode.model_validate(n.model_dump()).id == "n1"
def test_document():
    doc = IRDocument(root=IRNode(id="r", role="page", layout={"mode":"block"}, style={}, children=[]),
                     tokens=DesignTokens(colors={"ink":"#111"}, space={"4":"16px"}, type={}, radius={}, shadow={}),
                     breakpoints=[1440,768,375])
    assert 1440 in doc.breakpoints and doc.tokens.colors["ink"] == "#111"
```

- [ ] **Step 2 — run, see it fail** (`ModuleNotFoundError`).
- [ ] **Step 3 — implement** `core/ir/schema.py`: Pydantic v2 models `IRNode` (fields per `docs/architecture.md` §5: id, role, tag, layout: dict, style: dict, content: dict, component: str|None, componentProps: dict, sourceBBox: dict|None, children: list[IRNode]), `DesignTokens` (colors/space/type/radius/shadow: dict[str,str]), `IRDocument` (root: IRNode, tokens: DesignTokens, breakpoints: list[int]). Enable recursive model via `model_config` + forward ref `IRNode.model_rebuild()`.
- [ ] **Step 4 — run, see it pass.**
- [ ] **Step 5 — commit:** `feat(ir): add IR schema (IRNode, DesignTokens, IRDocument)`.

---

## Task 2: Design-token extractor

**Files:**
- Create: `core/ir/tokens.py`
- Test: `tests/ir/test_tokens.py`

- [ ] **Step 1 — failing test:** given a list of resolved style dicts with repeated values, `extract_tokens(styles)` returns a `DesignTokens` where each *distinct* color/space value is assigned one stable token name, and `tokenize_value(value, kind, tokens)` returns the `token.color.x` ref for a known value and the raw value for an unknown one.

```python
from core.ir.tokens import extract_tokens, tokenize_value
def test_dedup_colors():
    styles = [{"color":"#111111"},{"color":"#111111"},{"background":"#ffffff"}]
    t = extract_tokens(styles)
    assert len(t.colors) == 2                      # #111111 and #ffffff, deduped
def test_tokenize_value():
    styles = [{"color":"#111111"}]
    t = extract_tokens(styles)
    assert tokenize_value("#111111","color",t).startswith("token.color.")
    assert tokenize_value("#abcabc","color",t) == "#abcabc"   # unknown → passthrough
```

- [ ] **Step 2 — run, see it fail.**
- [ ] **Step 3 — implement:** walk all style values; bucket by kind (color via hex/rgb regex; space via px/rem; type via font shorthand; radius; shadow). Assign deterministic names (sorted by frequency then value, e.g. `c1,c2…` or nearest semantic). Provide `tokenize_value`.
- [ ] **Step 4 — run, see it pass.**
- [ ] **Step 5 — commit:** `feat(ir): design-token extraction + value tokenization`.

---

## Task 3: IR builder (DOM + computed styles → normalized tree)

**Files:**
- Create: `core/ir/builder.py`
- Test: `tests/ir/test_builder.py`

- [ ] **Step 1 — failing test:** feed a small `dom.json`-shaped dict (a node with `display:flex`, a child with a `shopify-section` class and a `template--x__main` id) into `build_ir(dom, css)`. Assert: returns an `IRDocument`; the flex node's `layout.mode == "flex"`; **no node retains `shopify-section` in any class and no `template--` id survives** (normalized away); style values are tokenized; geometry copied into `sourceBBox`.

```python
from core.ir.builder import build_ir
def test_normalizes_shopify_names_and_layout():
    dom = {"tag":"div","id":"template--123__main","classes":["shopify-section"],
           "rect":{"x":0,"y":0,"width":1440,"height":100},
           "styles":{"display":"flex","color":"#111111"},"children":[]}
    doc = build_ir(dom, css={})
    node = doc.root
    assert node.layout["mode"] == "flex"
    blob = doc.model_dump_json()
    assert "shopify-section" not in blob and "template--" not in blob
```

- [ ] **Step 2 — run, see it fail.**
- [ ] **Step 3 — implement:** recursive walk; map `display` → `layout.mode` (flex/grid/block) and copy `flex-direction/gap/grid-template-columns/justify/align`; copy `position/top/z-index` into `style` (sticky-guard needs these); derive `role` from tag + heuristics (header/footer/nav/section/figure→media); **drop fingerprint classes/ids** (`shopify*`, `template--…`); tokenize style values via Task 2; fill `sourceBBox` from `rect`. Build `DesignTokens` once at document level.
- [ ] **Step 4 — run, see it pass.**
- [ ] **Step 5 — commit:** `feat(ir): build normalized IR from DOM + computed styles`.

---

## Task 4: fingerprint_gate (R1)

**Files:**
- Create: `core/gates/__init__.py`
- Create: `core/gates/fingerprint.py`
- Test: `tests/gates/test_fingerprint.py`

- [ ] **Step 1 — failing test:** `scan_tree(dirpath)` over a temp dir with a file containing `shopify-section`, `template--9__main`, `original.css`, `data-shopify-x` returns `ok=False` with counts per pattern; a clean dir returns `ok=True, total=0`.

```python
from core.gates.fingerprint import scan_tree
def test_detects(tmp_path):
    (tmp_path/"a.css").write_text(".shopify-section{} /* template--9__main */")
    (tmp_path/"i.html").write_text('<link href="original.css"> data-shopify-x')
    r = scan_tree(str(tmp_path))
    assert r["ok"] is False and r["total"] >= 3
def test_clean(tmp_path):
    (tmp_path/"a.css").write_text(".hero{color:#111}")
    assert scan_tree(str(tmp_path))["ok"] is True
```

- [ ] **Step 2 — run, see it fail.**
- [ ] **Step 3 — implement:** patterns = `[r"shopify", r"myshopify", r"template--[\w-]+__", r"data-shopify", r"original\.css", r"shopify-section"]` (case-insensitive); walk text files (.html/.css/.js/.jsx/.json), count matches per pattern, return `{ok, total, by_pattern, files:[…]}`. Skip binary/asset files.
- [ ] **Step 4 — run, see it pass.**
- [ ] **Step 5 — commit:** `feat(gates): fingerprint_gate scans dist for Shopify traces`.

---

## Task 5: weight_gate (R3)

**Files:**
- Create: `core/gates/weight.py`
- Test: `tests/gates/test_weight.py`

- [ ] **Step 1 — failing test:** `measure_dist(dirpath, budget_kb=120)` sums gzipped sizes of html/css/js (assets counted at raw size), returns `{ok, total_kb, budget_kb, by_type}`; a tiny dir passes, a dir with a 300 KB JS file fails.
- [ ] **Step 2 — run, see it fail.**
- [ ] **Step 3 — implement:** walk `dist/`, gzip-compress text assets to estimate transfer, sum; compare to budget; return breakdown. Default budget 120 KB, target note 50–80 KB.
- [ ] **Step 4 — run, see it pass.**
- [ ] **Step 5 — commit:** `feat(gates): weight_gate measures dist transfer size`.

---

## Task 6: fidelity_gate — SSIM scoring + region localization (R4)

**Files:**
- Modify: `core/visual_diff.py` (add SSIM + keep mean-abs fallback)
- Create: `core/gates/fidelity.py`
- Test: `tests/gates/test_fidelity.py`

- [ ] **Step 1 — failing test:** `score(ref_png, cand_png)` returns 1.0 for identical images and < 0.9 for an image with a large black band painted over it; `worst_regions(ref, cand, rows=12)` returns the band index with the lowest local SSIM.
- [ ] **Step 2 — run, see it fail.**
- [ ] **Step 3 — implement:** use `skimage.metrics.structural_similarity` on grayscale, resized to common dims; `worst_regions` splits into `rows` bands, computes per-band SSIM, returns sorted worst-first with bbox ranges (maps back to IR via y-range). Add `scikit-image` + `Pillow` to `pyproject.toml`.
- [ ] **Step 4 — run, see it pass.**
- [ ] **Step 5 — commit:** `feat(gates): fidelity_gate via SSIM + region localization`.

---

## Task 7: Recognizer framework + registry

**Files:**
- Create: `core/recognizers/__init__.py` (registry: `register`, `run_all(doc) -> doc`)
- Test: `tests/recognizers/test_registry.py`

- [ ] **Step 1 — failing test:** a dummy recognizer registered via `@register` that sets `node.component="X"` on nodes with `role=="reviews"` is applied by `run_all(doc)`; recognizers run in registration order; an exception in one recognizer is caught and recorded, not fatal.
- [ ] **Step 2 — run, see it fail.**
- [ ] **Step 3 — implement:** `Recognizer = Callable[[IRDocument], IRDocument]`; module-level list; `register` decorator; `run_all` folds the doc through each, collecting `{name, changed, error}` reports.
- [ ] **Step 4 — run, see it pass.**
- [ ] **Step 5 — commit:** `feat(recognizers): pluggable recognizer registry`.

---

## Task 8: sticky-guard recognizer (R6)

**Files:**
- Create: `core/recognizers/sticky.py`
- Test: `tests/recognizers/test_sticky.py`

- [ ] **Step 1 — failing test:** given an IR where a `position:sticky` node has an ancestor with `overflow:hidden` (or `overflow-x:hidden`), the recognizer rewrites every such ancestor's overflow to `clip`/`visible` so sticky can work; a sticky node with clean ancestors is untouched; the sticky node keeps `position:sticky` + `top`.

```python
from core.recognizers.sticky import sticky_guard
# ancestor overflow hidden must become non-scroll-container
```

- [ ] **Step 2 — run, see it fail.**
- [ ] **Step 3 — implement:** walk tree tracking ancestor chain; for each `position in (sticky,fixed)` node, for each ancestor whose `overflow*`∈{hidden,auto,scroll}, set `overflow-x:clip`/`overflow-y:visible` (never `hidden`, which forces a scroll container). Preserve containing block (do not reparent).
- [ ] **Step 4 — run, see it pass.**
- [ ] **Step 5 — commit:** `feat(recognizers): sticky-guard fixes overflow-clipped ancestors`.

---

## Task 9: footer-rebuild recognizer (R7)

**Files:**
- Create: `core/recognizers/footer.py`
- Test: `tests/recognizers/test_footer.py`

- [ ] **Step 1 — failing test:** a `role=="footer"` node whose layout is grid keeps explicit `grid-template-columns`/`gap` on its `layout`; if those were dropped, the recognizer reconstructs columns from the children's source bboxes (count distinct x-positions). Assert columns count matches child column count.
- [ ] **Step 2 — run, see it fail.**
- [ ] **Step 3 — implement:** ensure footer container layout carries explicit columns/gap; if missing, infer column count by clustering children `sourceBBox.x`; set `layout.columns = f"repeat({n}, 1fr)"`.
- [ ] **Step 4 — run, see it pass.**
- [ ] **Step 5 — commit:** `feat(recognizers): footer-rebuild preserves grid columns`.

---

## Task 10: reviews recognizer (R8)

**Files:**
- Create: `core/recognizers/reviews.py`
- Test: `tests/recognizers/test_reviews.py`

- [ ] **Step 1 — failing test:** given an IR subtree carrying review markup (detected by judge.me/loox/yotpo/okendo class signatures present on the raw node `data`), the recognizer sets `node.component="Reviews"` and fills `componentProps.items = [{author, rating, text, date}, …]` extracted from the subtree; a non-reviews node is untouched.
- [ ] **Step 2 — run, see it fail.**
- [ ] **Step 3 — implement:** signature match on class/id substrings (`judgeme`,`jdgm`,`loox`,`yotpo`,`okeReviews`,`okendo`,`spr-`,`stamped`); parse child nodes for author/rating(star count)/text/date; set component + props; drop the raw subtree children (replaced by component).
- [ ] **Step 4 — run, see it pass.**
- [ ] **Step 5 — commit:** `feat(recognizers): reviews → data-driven component`.

---

## Task 11: video-collector recognizer + extractor media download (R9)

**Files:**
- Create: `core/recognizers/video.py`
- Modify: `core/extractor/service.py` (download `<video>`/`<source>` media; resolve lazy `data-src`)
- Test: `tests/recognizers/test_video.py`

- [ ] **Step 1 — failing test:** an IR media node referencing a `<video>` with a resolved local `assetRef` gets `component="VideoPlayer"` with `componentProps.src` pointing at the local asset; a youtube/vimeo iframe node becomes `component="VideoEmbed"` with the embed URL; a node with only `data-src` has it promoted to `src`.
- [ ] **Step 2 — run, see it fail.**
- [ ] **Step 3 — implement:** recognizer maps media roles to VideoPlayer/VideoEmbed and promotes lazy attrs. In `service.py`, extend `_download_resources` to also fetch `<video>`/`<source>` urls (raise the type allowlist; cap size, configurable) and record them in `DownloadedResources`.
- [ ] **Step 4 — run, see it pass.**
- [ ] **Step 5 — commit:** `feat(recognizers): video-collector + media download in extractor`.

---

## Task 12: Clean codegen (IR → React + Tailwind)

**Files:**
- Create: `core/codegen/__init__.py`
- Create: `core/codegen/react.py`
- Create: `core/codegen/tailwind_theme.py`
- Test: `tests/codegen/test_react.py`

- [ ] **Step 1 — failing test:** `emit_component(node)` for a flex hero with tokenized styles returns JSX using Tailwind utility classes (e.g. `flex`), **no inline `style={{…}}` raw dump**, and the output string contains **no** `shopify`/`template--`; `emit_tailwind_theme(tokens)` returns a `tailwind.config.js` theme extending colors/space from the token table.

```python
from core.codegen.react import emit_component
from core.ir.schema import IRNode
def test_clean_jsx():
    n = IRNode(id="h", role="hero", layout={"mode":"flex","direction":"row"},
               style={"bg":"token.color.surface"}, children=[])
    jsx = emit_component(n)
    assert "flex" in jsx and "shopify" not in jsx.lower() and "<style" not in jsx
```

- [ ] **Step 2 — run, see it fail.**
- [ ] **Step 3 — implement:** map `layout.mode`→`flex`/`grid` utilities, direction/gap/columns→Tailwind classes; map token style refs→theme classes; render component nodes (Reviews/VideoPlayer/VideoEmbed) as imports of shared components in `templates/assembly/components/`; one component file per section; `emit_tailwind_theme` builds the theme from `DesignTokens`.
- [ ] **Step 4 — run, see it pass.**
- [ ] **Step 5 — commit:** `feat(codegen): clean IR → React + Tailwind emitter`.

---

## Task 13: cleanliness_gate (R2)

**Files:**
- Create: `core/gates/cleanliness.py`
- Test: `tests/gates/test_cleanliness.py`

- [ ] **Step 1 — failing test:** `check(dirpath, max_inline_css=400)` fails a dir whose component contains a `<style>` block or an inline `style={{` with > `max_inline_css` chars; passes utility-class-only components.
- [ ] **Step 2 — run, see it fail.**
- [ ] **Step 3 — implement:** scan `.jsx` files; flag `<style`, large inline style objects, and `className` strings that embed raw CSS; return `{ok, violations:[…]}`.
- [ ] **Step 4 — run, see it pass.**
- [ ] **Step 5 — commit:** `feat(gates): cleanliness_gate rejects inline CSS dumps`.

---

## Task 14: MCP tool wiring

**Files:**
- Create: `mcp_server/tools/pipeline.py` (`build_ir`, `run_recognizers`, `generate_code`, `check_fingerprints`, `check_weight`, `score_fidelity`, `compare_to_baseline`)
- Modify: `mcp_server/server.py` (register new tools; rename server `pwc3`→`pwc4`)
- Modify: `.mcp.json`, `pyproject.toml`, `README.md` (v3→v4, pwc3→pwc4, cwd path)
- Test: `tests/mcp/test_pipeline_tools.py`

- [ ] **Step 1 — failing test:** each new tool function returns a JSON-serializable dict with an `ok` key; `check_fingerprints(dir)` proxies `core.gates.fingerprint.scan_tree`; `score_fidelity(ref,cand)` proxies the fidelity gate.
- [ ] **Step 2 — run, see it fail.**
- [ ] **Step 3 — implement** thin deterministic wrappers (NO LLM) over the core modules; register in `server.py`; update identifiers.
- [ ] **Step 4 — run, see it pass.**
- [ ] **Step 5 — commit:** `feat(mcp): wire v4 pipeline tools; rename pwc3→pwc4`.

---

## Task 15: SKILL update — the v4 playbook + self-heal loop

**Files:**
- Modify: `skill/SKILL.md`
- Test: manual (documentation) — verify the phase list references the new tools and gates.

- [ ] **Step 1:** Rewrite phases so reproduction is: extract → `build_ir` → `run_recognizers` → `generate_code` → assemble → build. Replace the eyeball verify with the **gate-driven self-heal loop**: run `check_fingerprints`, `check_weight`, `score_fidelity`; on any failure, localize via `worst_regions`, CC repairs the offending IR component, regenerate, re-gate; loop until all gates green or budget hit (then report residuals). Keep the iron rule note (tools never call an LLM; CC only repairs).
- [ ] **Step 2 — commit:** `docs(skill): v4 gate-driven self-heal playbook`.

---

## Self-Review checklist (run after building)
1. **Spec coverage:** R1→Task 4; R2→Task 13; R3→Task 5; R4→Task 6; R5→`compare_to_baseline` (Task 14); R6→Task 8; R7→Task 9; R8→Task 10; R9→Task 11. IR keystone→Tasks 1–3; codegen→Task 12; loop→Task 15. ✓
2. **Placeholder scan:** none — every task has concrete test code or explicit interface.
3. **Type consistency:** `IRNode/IRDocument/DesignTokens` names are used identically across Tasks 1,3,7,8,9,10,11,12. Gate functions return `{ok, …}` dicts uniformly.
