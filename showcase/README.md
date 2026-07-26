# Clone Gallery · 复刻结果归档

This directory is the local review Gallery for Perfect Web Clone harness runs.
It keeps runnable source projects, desktop/mobile screenshots, side-by-side
evidence, and the machine-validation context needed for user review.

Machine gates do not represent user acceptance. They show whether the recorded
evidence satisfies the harness contract; the user makes the final decision.

## Open the Gallery

```bash
cd showcase
python3 -m http.server 8080 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8080/>.

The Gallery itself is plain HTML, CSS, and JavaScript. Its filters work without
a build step.

## Run one clone

Most clones are independent Vite projects:

```bash
cd showcase/products/reelshort
npm install
npm run dev
```

`oryzo-pixel` is a static HTML project and can be served directly.

## Recent harness cases

| Clone | Source | Archived evidence |
|---|---|---|
| Naro AI · Order | `naroai.co/order` | Desktop/mobile screenshots and interaction verification; Gallery case, not the requested client target |
| FlipClocker | `flipclocker.com` | Corrected dark-theme clone, desktop/mobile screenshots, semantic A/B validation |
| ReelShort · Español | `reelshort.com/es` | Runnable clone, full-page/tablet screenshots, side-by-side and gate report |
| Livora | `livora.co` | Runnable clone, desktop/mobile screenshots, side-by-side and gate report |
| Kojeva | `kojeva.com` | Runnable clone, quality-iteration desktop/mobile screenshots, side-by-side and gate report |
| Linfae · TryKojiva | `trykojiva.com/brush` | Runnable clone, clean desktop/mobile screenshots, side-by-side and residual report |

## Historical archive

The Gallery also retains ORYZO, VARIANT3D, Longbow, Novu, Pagerie, Pagerie
product-page variants, Everswap, Sowieso, and ORYZO Pixel.
