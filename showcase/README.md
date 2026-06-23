# Clone Showcase · 克隆产品集

A curated collection of websites cloned with the **Perfect Web Clone v3** pipeline
(Claude Code as the brain, deterministic zero-LLM Python tools as the hands). Each
entry is a self-contained, runnable **Vite + React + Tailwind** static project with a
prebuilt `dist/`.

> Delivery + showcase only — **these are never deployed online.**

## Browse

Open `index.html` for the visual gallery (full-page screenshots, source links, tech
stack, and run commands). Easiest:

```bash
cd showcase
python3 -m http.server 9000   # then open http://localhost:9000
```

(Opening `index.html` directly via `file://` also works for the gallery + screenshots.)

## Run a single clone live

Each clone uses absolute `/assets/...` paths, so it must be served at a **server root**
(not a subfolder). Run it on its own:

```bash
cd products/db-longbow      # or products/withnovu
npm install
npm run preview             # serves the prebuilt dist/
# or: npm run dev           # live dev server
```

## Contents

| Clone | Source | Sections | Notes |
|-------|--------|----------|-------|
| **VARIANT3D** | variant3d.io | 14 | Self-hosted Founders Grotesk; dark 3D product site (scroll-pinned WebGL → static fallback); desktop+mobile verified |
| **Longbow** | db-longbow.webflow.io | 16 | Self-hosted Bebas Neue / EB Garamond / Geist Mono; desktop+mobile verified |
| **Novu** | withnovu.com | 5 | Inter + Lora long landing page; desktop+mobile verified |

The canonical working copies live in `../clones/<name>/`; this folder is the curated,
self-contained collection. New clones get added here as they're finished.
