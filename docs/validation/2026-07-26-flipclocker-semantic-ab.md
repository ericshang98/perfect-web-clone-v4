# FlipClocker semantic comparison A/B

**Date:** 2026-07-26  
**Held-out source:** <https://flipclocker.com/>  
**Source id:** `flipclocker.com-1785045707-54a88d`  
**Viewport / page:** `1440×900`, full page `1440×1596`

This public, unauthenticated page was not used while implementing the semantic
gate. It contains a clock that changes every second, a changing third-party ad
creative, stable navigation/content/footer UI, and settings interactions.

## Source integrity

- Capture integrity: passed on the first attempt.
- Critical regions: navigation, clock hero, information hero, footer.
- Planned section defects were not trusted: the deterministic plan reported a
  zero-height header and failed to assign the two hero owners. Raw critical
  evidence and the source raster were retained as the authority.
- Two earlier candidate pages (PlainClock and Simple Stopwatch) remained
  fail-closed because duplicate heading fingerprints triggered source-integrity
  collapse errors. Their red gates were not waived.

## A/B result

| Measurement | Previous raw workflow | Semantic workflow |
|---|---:|---:|
| Whole-page SSIM | `0.7335` initial / `0.8361–0.8664` final samples | diagnostic only |
| Valid static-region aggregate | not available | `0.9958` |
| Navigation | mixed into whole page | `0.9839`, pass |
| Information heading | mixed into whole page | `1.0000`, pass |
| Feature grid | mixed into whole page | `0.9998`, pass |
| Footer | mixed into whole page | `0.9970`, pass |
| Live clock | arbitrary digits caused false failure | bounds + aspect pass |
| Third-party ad | creative pixels caused false failure | surface geometry/style pass |
| Settings / hide seconds / hide labels / classic mode | presence only | four click/assert replays pass |
| Mobile menu | not isolated | open/controlled-surface replay pass |

The raw score changes between refreshes and remains below `0.97` even though
every valid static crop exceeds its threshold and every declared dynamic
invariant passes. This is the intended result: changing digits and ad pixels no
longer decide whether CSS is correct.

## Comparison-driven repairs

The first semantic run passed live-clock and ad invariants while keeping these
real failures visible:

- information heading `0.6574`;
- feature grid `0.7349`;
- footer `0.8472`;
- navigation `0.9068`;
- settings submenu actions failed because their required “open settings” prefix
  was absent.

Repairs restored the source font-weight mapping, exact inherited tracking,
heading/card line heights, navigation gap, footer flex geometry, and the
settings action sequence. All four recorded visual attempts improved strictly
and introduced no hard-gate regression.

The worst-region packet measured `16,061` UTF-8 bytes (about `4,016` estimated
tokens), included only the owning `section` sources, and truncated unrelated CSS
under the `16 KiB` budget.

## Evidence

- Reference raster:
  `.artifacts/semantic-ab/sources/flipclocker.com-1785045707-54a88d/screenshots/primary_full.png`
- Final candidate:
  `.artifacts/semantic-ab/optimized-clone/final.png`
- Mobile interaction review:
  `.artifacts/semantic-ab/optimized-clone/mobile-review.png`
- Contract:
  `.artifacts/semantic-ab/optimized-clone/.pwc/comparison-contract.json`
- Monotonic ledger:
  `.artifacts/semantic-ab/sources/flipclocker.com-1785045707-54a88d/iteration-ledger.json`
- Production build:
  `.artifacts/semantic-ab/optimized-clone/dist/`
- Local review URL:
  <http://127.0.0.1:4174/>

Machine status: `ready_for_user_review`. This is not user acceptance.
