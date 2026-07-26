# Livora SilkGlide Pro 2.0 visual clone

Standalone, data-driven Vite + React reproduction of the accepted Livora
capture `livora.co-1784826866-453146`.

## Run

```bash
npm install
npm run dev
```

Production bundle:

```bash
npm run build
```

## Acceptance evidence

- Reference: `core/extractor/_sources/livora.co-1784826866-453146/screenshots/primary_full.png`
- Candidate: `shots/desktop_current.png`
- Labeled comparison: `shots/sidebyside.png`
- 1440px full-page fidelity: `0.748043` (threshold `0.72`)
- Page geometry: `1440 × 9188`, matching the accepted raster
- Fingerprints: `0`
- Gzipped code: `54.907 KB` (budget `100 KB`)
- Broken images: `0`
- Broken videos: `0`
- Placeholder/root-relative links: `0`
- 390px horizontal overflow: `false`
- 390px primary navigation: `5/5` visible, horizontally scrollable
- Dependency audit: `0` vulnerabilities (`npm audit` and
  `npm audit --omit=dev`)

The clone intentionally preserves the captured 1,612px source-page spacer
before the FAQ. The closed cart drawer is omitted; the captured sticky add-to-
cart bar remains visible. The five UGC cards use localized MP4s with localized
poster frames. All accepted site navigation, account, cart, and footer links use
absolute `https://livora.co/...` destinations so they remain valid from a clone
deployment.
