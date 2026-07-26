# FlipClocker semantic comparison A/B

**Date:** 2026-07-26  
**Held-out source:** <https://flipclocker.com/>  
**Valid source id:** `flipclocker.com-1785049907-54a88d`
**Viewport / page:** `1440×900`, full page `1440×1442`

This public, unauthenticated page was not used while implementing the semantic
gate. It contains a clock that changes every second, stable
navigation/content/footer UI, and settings interactions.

## Theme-baseline correction

The first A/B result in this report was invalid. User review revealed that the
live source was dark while the clone was light. The extractor recognized only
literal `dark` / `dark-mode` names, misclassified the source's authored
`data-theme="business"` state as light, mutated it to `data-theme="light"`,
and then replaced the canonical screenshot with the generated light variant.

The original `0.9958` static score therefore compared the clone to the wrong
reference and is withdrawn. After fixing non-destructive theme detection, the
source is captured as `current_theme=dark`; its authored `business` root state
and dark primary raster remain intact.

## Source integrity

- Capture integrity: passed on the first attempt.
- Authored default theme: `business`, computed color scheme `dark`.
- Critical regions: navigation, clock hero, information hero, footer.
- Planned section defects were not trusted: the deterministic plan reported a
  zero-height header and failed to assign the two hero owners. Raw critical
  evidence and the source raster were retained as the authority.
- Two earlier candidate pages (PlainClock and Simple Stopwatch) remained
  fail-closed because duplicate heading fingerprints triggered source-integrity
  collapse errors. Their red gates were not waived.

## A/B result

| Measurement | Wrong light clone vs corrected source | Corrected semantic workflow |
|---|---:|---:|
| Whole-page SSIM | `0.1446` | `0.8883–0.8926`, diagnostic only |
| Valid static-region aggregate | `0.0930`, fail | `0.9963`, pass |
| Navigation | `0.1760`, fail | `0.9833`, pass |
| Information heading | `0.0000`, fail | `0.9997`, pass |
| Feature grid | `0.0386`, fail | `0.9999`, pass |
| Footer | `0.1446`, fail | `0.9992`, pass |
| Live clock | arbitrary digits caused false failure | bounds + aspect pass |
| Settings / hide seconds / hide labels / classic mode | presence only | four click/assert replays pass |
| Mobile menu | not isolated | open/controlled-surface replay pass |

The raw score changes between refreshes and remains below `0.97` even though
every valid static crop exceeds its threshold and every declared dynamic
invariant passes. This is the intended result: changing digits no longer decide
whether CSS is correct, while a whole-page light/dark mismatch now fails the
static regions immediately.

## Comparison-driven repairs

The corrected semantic run rejects the old white clone and keeps these real
theme failures visible:

- information heading `0.0000`;
- feature grid `0.0386`;
- footer `0.1446`;
- navigation `0.1760`.

Repairs preserve the source's authored `business` theme and dark color scheme,
then reproduce its root surface, navigation, button palette, cards, footer, and
settings action sequence. The third-party ad placeholder from the invalid light
capture was removed because it was not present in the corrected authored
default capture.

The original worst-region packet measured `16,061` UTF-8 bytes (about `4,016`
estimated tokens), included only the owning `section` sources, and truncated
unrelated CSS under the `16 KiB` budget. The theme correction reused that bounded
owner context rather than resending the full source capture.

## Token-accounting validation

The earlier FlipClocker clone predated the run ledger. Reconstruction from the
owning Codex session gives approximately `41.12M` gross processed tokens,
including `39.64M` cached input and `1.48M` non-cached input plus output. This is
a historical estimate, not a provider-backed per-run record.

The new accounting path was exercised against the same source in a dedicated
run (`da32bfd1-8920-484f-ac71-e6ef3a2a7a52`) with a real bounded repair packet.
It recorded two provider-backed intervals:

| Measurement | Recorded value |
|---|---:|
| Gross input + output | `698,053` |
| Cached input | `682,240` |
| Non-cached input | `13,906` |
| Output | `1,907` |
| Non-cached input + output budget use | `15,813` |
| Repair-packet context | `814` bytes / `204` estimated tokens |
| Accepted repairs | `1` |
| Tokens per accepted repair | `10,209` |
| Tokens per quality point | `1,182.97` |

The final report is `measurement_status=actual`,
`accounting_complete=true`, has no missing segments, and remains below the
`250K` soft budget. The detailed JSONL stores compact metrics, paths, and
digests—not prompt or tool-output bodies. Estimated context remains separate
from actual provider usage.

This smoke run proves collection, phase attribution, idempotent persistence,
budgeting, and efficiency reporting. It is not a clean from-scratch clone and
therefore does **not** prove a `50%` end-to-end Token reduction. That claim must
wait for the next full clone to produce a directly comparable per-run ledger.

## Evidence

- Reference raster:
  `.artifacts/semantic-ab/sources/flipclocker.com-1785049907-54a88d/screenshots/primary_full.png`
- Final candidate:
  `.artifacts/semantic-ab/optimized-clone/dark-final.png`
- Mobile interaction review:
  `.artifacts/semantic-ab/optimized-clone/mobile-dark-review.png`
- Contract:
  `.artifacts/semantic-ab/optimized-clone/.pwc/comparison-contract.json`
- Monotonic ledger:
  `.artifacts/semantic-ab/sources/flipclocker.com-1785049907-54a88d/iteration-ledger.json`
- Production build:
  `.artifacts/semantic-ab/optimized-clone/dist/`
- Token-accounting smoke report:
  `.artifacts/semantic-ab/token-accounting-smoke/run.json`
- Token-accounting event ledger:
  `.artifacts/semantic-ab/token-accounting-smoke/token-usage.jsonl`
- Bounded smoke repair packet:
  `.artifacts/semantic-ab/token-accounting-smoke/smoke-packet.json`
- Local review URL:
  <http://127.0.0.1:4174/>

Regression status: `475 passed, 13 skipped`; the two warnings are pre-existing
Pydantic class-config deprecations in `core/extractor/models.py`.

Machine status: `ready_for_user_review`. This is not user acceptance.
