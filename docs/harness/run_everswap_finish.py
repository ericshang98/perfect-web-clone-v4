#!/usr/bin/env python3
"""Finish everswap clone: author 8 section components from cleaned section HTML
(strip HTML comments + animation-frozen inline styles), append a de-animate
override so the scroll-pinned layout stacks statically, then npm build + screenshot.
This is the proven dorro/pagerie recipe (cleaned dangerouslySetInnerHTML + theme.css)."""
import json, re, subprocess
from pathlib import Path

DEST = Path("/Users/eric/AI_development/perfect-web-clone-v4/showcase/products/everswap")
SECDATA = DEST / "_secdata"
COMP = DEST / "src/components/sections"

ORDER = ["section","section-2","section-3","section-4","section-5","section-6","footer","navigation"]
COMPNAME = {
    "section":"Section","section-2":"Section2Section","section-3":"Section3Section",
    "section-4":"Section4Section","section-5":"Section5Section","section-6":"Section6Section",
    "footer":"FooterSection","navigation":"NavigationSection",
}

def clean(html: str) -> str:
    html = re.sub(r"(?s)<!--.*?-->", "", html)          # drop comments
    html = re.sub(r'\sstyle="[^"]*"', "", html)          # drop animation-frozen inline styles
    html = re.sub(r'\s(data-scroll[a-z-]*|data-aos[a-z-]*)="[^"]*"', "", html)  # scroll-anim hooks
    return html.strip()

for name in ORDER:
    d = json.load(open(SECDATA / f"{name}.json"))
    inner = clean(d.get("full_html") or "")
    # escape backtick/${ for JS template literal
    inner_js = inner.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    comp = COMPNAME[name]
    code = (
        f"// {comp} — authored from captured section '{name}' (cleaned HTML + theme.css).\n"
        f"export default function {comp}() {{\n"
        f"  return (\n"
        f'    <div className="pwc-section pwc-{name}" dangerouslySetInnerHTML={{{{ __html: `{inner_js}` }}}} />\n'
        f"  );\n"
        f"}}\n"
    )
    p = COMP / name / f"{comp}.jsx"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(code, encoding="utf-8")
    print(f"wrote {name:14s} {len(inner):6d}B -> {p.relative_to(DEST)}")

# de-animate override: neutralize scroll-pinning so content stacks & is visible
override = """
/* --- pwc de-animate override: scroll-choreography -> static stack (everswap is a
   pinned/absolute scroll site; force readable static layout) --- */
#root .pwc-section { position: relative !important; display: block !important;
  width: 100%; max-width: 100%; opacity: 1 !important; transform: none !important;
  filter: none !important; visibility: visible !important; min-height: auto !important;
  height: auto !important; overflow: visible !important; padding: 40px 24px; }
#root .pwc-section * { position: static !important; opacity: 1 !important;
  transform: none !important; filter: none !important; visibility: visible !important;
  display: revert !important; animation: none !important; transition: none !important;
  clip-path: none !important; }
#root .pwc-section [class*="title"], #root .pwc-section h1 { display: block !important; }
"""
idx = DEST / "src/index.css"
idx.write_text(idx.read_text() + override, encoding="utf-8")
print("appended de-animate override to index.css")

# build
print("=== npm install (if needed) + build ===")
if not (DEST / "node_modules").exists():
    subprocess.run(["npm","install"], cwd=DEST, check=False, capture_output=True)
r = subprocess.run(["npm","run","build"], cwd=DEST, capture_output=True, text=True)
print("build rc:", r.returncode)
print((r.stdout + r.stderr)[-1500:])
