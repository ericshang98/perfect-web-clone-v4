# FlipClocker semantic clone

Source: <https://flipclocker.com/>

This project is the corrected dark-theme result from the semantic-comparison
A/B trial. The live clock digits are treated as a dynamic region: the harness
checks their geometry and behavior instead of requiring identical pixels.
Navigation, information content, feature cards, footer, and settings controls
remain strict static/interaction checks.

See `VERIFICATION.json` for the compact machine evidence and
`docs/validation/2026-07-26-flipclocker-semantic-ab.md` in the repository root
for the full validation narrative.

## Run

```bash
npm install
npm run dev
```
