# Meta Muse pixel clone design

## Scope
Build a standalone Vite + React page at `showcase/products/muse` that mirrors https://ai.meta.com/muse/ across desktop and mobile. Include the full single page: global nav, animated hero, feature tabs, security section, Muse in action media panel, creator story carousel, Mac download section, CTA, FAQ accordion, product cards, and footer.

## Visual contract
- Black and deep charcoal base with large rounded cards and high-contrast white typography.
- Desktop-first layouts at 1440/1280 widths with a mobile breakpoint around 760px.
- Hero is full viewport height with a pool/water-inspired gradient surface, a centered 3-line statement, sticky transparent nav and blue CTA.
- Sections use large editorial headings, generous vertical rhythm, blue accent buttons, muted gray body copy, and rounded 24–36px cards.
- Dynamic video footage is replaced by CSS animated gradients and abstract masks so the visual treatment is deterministic and local.

## Interaction contract
- Nav menu items link to page anchors; Try Muse opens the external Muse URL in a new tab.
- Feature tabs switch the supporting media card and copy.
- Creator stories carousel supports previous/next buttons and dot indicators.
- FAQ rows expand/collapse independently.
- Media panels include play/mute affordances with local UI state.
- Download and learn-more CTAs remain functional links.

## Architecture
- `src/App.jsx` owns page content and UI state.
- `src/index.css` contains all layout, typography, gradients, responsive rules, and keyframe animations.
- `index.html` sets metadata and viewport.
- No external runtime dependencies beyond React and Vite.

## Verification
Run `npm install`, `npm run build`, then serve the app and inspect the page at desktop and mobile widths. Confirm no console errors, all controls change state, and the page remains readable at narrow widths.
