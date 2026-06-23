# Requirements — Jose Gallardo engagement

**Client:** Jose Gallardo Lopez (info@josegallardolopez.com), freelancer/company in Spain. Personal
use only (not reselling cloning as a service).

**Deal (agreed 2026-06-23):** Option B — a self-serve, paste-a-URL tool that returns a
pixel-perfect, clean, standalone React project. Fixed **$4,000**, payment **40% deposit / 30% at
working end-to-end pipeline / 30% on acceptance**. Deposit $1,600 via Wise.

## Hard requirements (both, simultaneously — non-negotiable)
1. **Cleanest possible code** — readable, maintainable; no Shopify fingerprints; no raw inline-CSS
   dumps; no `original.css`.
2. **Pixel-perfect visual fidelity** — matches the original at agreed breakpoints and key states.

Jose's priority order: visual fidelity is the priority; he handles **interactive behavior himself**
(accordions, variant switching, timers). So the tool targets *visual* fidelity of those in their
captured states, not full behavioral equivalence.

## Concrete defects found in the v3-era build (must be fixed at the architecture level)
- `shopify` appears 70×; 357 Shopify template refs (`template--20593513300135__main`-style).
- 64 raw inline-CSS blocks, 225 KB total, all on Shopify style variables.
- An `original.css` file is loaded.
- Page weight 510 KB (a clean React page like this should be ~50–80 KB).
- **Functional:** sticky element no longer follows scroll; footer disassembled; reviews section is
  a static image instead of the real widget; videos missing entirely.

## Acceptance criterion (Jose's own, 6/13)
For each reference URL, the new pipeline's output, placed **side by side** with the current repo's
output, must be **clearly better**. Milestone-1 single-URL test already passed.

## Reference URLs
- https://www.reelshort.com/es  (multimedia, not a store)
- https://livora.co/products/painless-hair-removal-epilator-…  (Shopify product page)
- https://kojeva.com/products/kojeva-lymphatic-face-brush  (Shopify product page)
- https://trykojiva.com/brush

## Standing constraints (from project memory)
- **Never deploy clones** — deliver local `dist/` only.
- Tools stay **LLM-free**; Claude Code is the only brain.
