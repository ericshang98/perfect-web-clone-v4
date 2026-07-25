# Four-reference delivery ledger

This ledger is evidence for the client’s end-to-end milestone. Machine-readable
status lives in `four-reference-sites.json`; values are updated only from fresh
captures and gate output.

The delivery ledger uses the explicitly recorded `0.72` visual threshold for
the current static-clone milestone. The repository's stricter `0.97` default is
also recorded separately and is not silently represented as passing.

| Site | Accepted capture | Identity check | Current state |
|---|---|---|---|
| ReelShort | `www.reelshort.com-1784826796-22e26a` | `ReelShort: Cada Segundo es Drama`, 6450 px | Build/full-page 0.931 and section aggregate 0.819 pass; 89/89 full static hrefs |
| Livora | `livora.co-1784826866-453146` | `SilkGlide Pro 2.0™`, 9188 px | Build/full-page gate pass at 0.748; local-band residual recorded |
| Kojeva | `kojeva.com-1784828890-25edd7` | `Kojeva Lymphatic Face Brush`, 6185 px | Build/full and weighted-section gates pass at 0.762; 3 section residuals recorded |
| TryKojiva | `trykojiva.com-1784828343-ab1ef0` | `Linfae™`, 8432 px | Clean rebuild passes full-page SSIM at 0.7204; section aggregate 0.667 is recorded as a residual |

## Run a clone locally

Each product is a standalone Vite project. Replace `<site>` with `reelshort`,
`livora`, `kojeva`, or `trykojiva`.

```bash
cd showcase/products/<site>
npm ci
npm run dev -- --host 127.0.0.1
```

Use `npm run build` for a fresh production build. The exact accepted source,
reference raster, candidate raster, side-by-side evidence, score, threshold,
responsive result, and remaining visual residuals are recorded in the JSON
ledger.

## Capture validation

- Accepted captures must match the contracted URL’s product identity, have a
  nontrivial page height, and include a full-page PNG.
- Search results, access-denied pages, generic error pages, and blank/unpainted
  rasters are rejected even when the extraction command returns success.
- Kojeva's earlier `Search – Kojeva` captures remain rejected; only the later,
  validated product raster is assigned to the ledger.

## Acceptance evidence required per site

- fresh production build;
- zero fingerprint findings;
- code weight within the configured budget;
- preserved real links;
- full-page and section fidelity scores with the exact reference/candidate paths;
- labeled side-by-side image;
- explicit residuals for anything that cannot be graded.
