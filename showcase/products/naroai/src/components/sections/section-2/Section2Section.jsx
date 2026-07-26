import { useMemo, useState } from "react";

const products = {
  silver: [
    "/assets/images/naro-silver-front-back.png",
    "/assets/images/naro-silver-combo.png",
    "/assets/images/naro-silver-necklace.png",
  ],
  black: [
    "/assets/images/naro-black-front-back.png",
    "/assets/images/naro-black-combo.png",
    "/assets/images/naro-black-necklace.png",
  ],
};

const labels = ["Front and back", "Wearable and accessories", "Necklace"];

function Chevron({ direction }) {
  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" d={direction === "left" ? "m15 18-6-6 6-6" : "m9 18 6-6-6-6"} />
    </svg>
  );
}

export default function Section2Section() {
  const [color, setColor] = useState("silver");
  const [slide, setSlide] = useState(0);
  const [quantity, setQuantity] = useState(1);
  const allImages = useMemo(() => [...products.silver, ...products.black], []);
  const activeIndex = (color === "silver" ? 0 : 3) + slide;
  const move = (delta) => setSlide((value) => (value + delta + 3) % 3);

  return (
    <main
      data-pwc-critical="hero-1"
      className="flex min-h-[822px] flex-col bg-white pt-14 text-[#141414] lg:h-[822px] lg:min-h-0 lg:flex-row lg:pt-20"
    >
      <div
        data-pwc-critical="hero-2"
        className="relative flex h-[65vh] w-full shrink-0 flex-col justify-between overflow-hidden bg-[#f9f9f9] lg:sticky lg:top-20 lg:h-[742px] lg:min-h-0 lg:w-1/2 lg:flex-none"
      >
        <div className="absolute inset-0 flex items-center justify-center p-0 lg:p-16">
          {allImages.map((src, index) => (
            <img
              key={src}
              alt="Naro wearable device"
              className="absolute h-full w-full max-w-3xl object-contain transition-opacity duration-500 ease-out scale-[1.35] sm:scale-110 lg:scale-100"
              src={src}
              loading={index === 0 ? "eager" : "lazy"}
              style={{ opacity: index === activeIndex ? 1 : 0, zIndex: index === activeIndex ? 1 : 0 }}
            />
          ))}
        </div>
        <div className="pointer-events-none relative z-10 flex h-full flex-col items-center justify-end pb-14 lg:pb-12">
          <p className="pointer-events-auto mb-6 max-w-[80%] rounded-full border border-black/10 bg-white/60 px-5 py-2 text-center text-sm font-medium text-black/80 shadow-sm backdrop-blur-md">
            {labels[slide]}
          </p>
          <div className="pointer-events-auto flex items-center gap-6">
            <button data-pwc-interaction="product-previous" aria-label="Previous image" className="flex h-10 w-10 items-center justify-center rounded-full border border-black/10 bg-white/40 text-black/70 backdrop-blur-sm transition-colors hover:bg-white/80 hover:text-black" onClick={() => move(-1)}>
              <Chevron direction="left" />
            </button>
            <div className="flex gap-3" aria-label="Product images">
              {[0, 1, 2].map((index) => (
                <button
                  key={index}
                  aria-label={`Go to image ${index + 1}`}
                  className={`h-2.5 w-2.5 rounded-full transition-all duration-300 ${slide === index ? "scale-110 bg-black" : "bg-black/20 hover:bg-black/40"}`}
                  onClick={() => setSlide(index)}
                />
              ))}
            </div>
            <button data-pwc-interaction="product-next" aria-label="Next image" className="flex h-10 w-10 items-center justify-center rounded-full border border-black/10 bg-white/40 text-black/70 backdrop-blur-sm transition-colors hover:bg-white/80 hover:text-black" onClick={() => move(1)}>
              <Chevron direction="right" />
            </button>
          </div>
        </div>
      </div>

      <div className="relative z-20 -mt-8 flex-1 rounded-t-[2.5rem] bg-white shadow-[0_-8px_30px_rgba(0,0,0,0.04)] lg:mt-0 lg:w-1/2 lg:max-w-none lg:flex-none lg:rounded-none lg:border-l lg:border-black/10 lg:shadow-none">
        <div className="sticky top-24 flex flex-col gap-8 p-6 pt-10 lg:p-12">
          <div>
            <h1 className="text-3xl font-semibold lowercase tracking-tight">naro</h1>
            <p className="mt-2 text-[#737373]">AI personal assistant, made wearable</p>
          </div>

          <div className="border-t border-black/10 pt-8">
            <p className="mb-1 text-sm text-[#737373]">Color</p>
            <p className="mb-3 text-base font-medium capitalize">{color}</p>
            <div className="flex gap-3">
              <button aria-label="Silver" className={`h-8 w-8 rounded-full border-2 transition-all ${color === "silver" ? "scale-110 border-black" : "border-black/10"}`} style={{ background: "linear-gradient(135deg,#d4d4d4,#a3a3a3)" }} onClick={() => setColor("silver")} />
              <button aria-label="Black" className={`h-8 w-8 rounded-full border-2 transition-all ${color === "black" ? "scale-110 border-black" : "border-black/10"}`} style={{ background: "linear-gradient(135deg,#404040,#171717)" }} onClick={() => setColor("black")} />
            </div>
          </div>

          <div className="border-t border-black/10 pt-8">
            <div className="mb-6 flex items-start justify-between">
              <div>
                <h3 className="text-lg font-medium">Batch 2</h3>
                <p className="mt-1 text-sm text-[#737373]">Delivery starts mid 2026</p>
              </div>
              <div className="flex items-center justify-end gap-1.5 text-xl leading-none">
                <span className="text-[#b6b6b6] line-through">$169</span>
                <span>$109</span>
              </div>
            </div>

            <div className="mb-8 rounded-2xl border border-black/10 bg-[#f5f5f5]/70 p-5 text-sm leading-relaxed text-[#737373]">
              Includes <span className="font-medium text-[#141414]">one-month subscription ($20/mo)</span> and <span className="font-medium text-[#141414]">hardware package ($149)</span>.
              <ul className="mt-4 space-y-2.5">
                <li className="flex items-start gap-3"><span className="mt-0.5 text-xs text-black/30">◆</span><span>Includes wearable, magnetic clip, necklace, and charging dock.</span></li>
                <li className="flex items-start gap-3"><span className="mt-0.5 text-xs text-black/30">◆</span><span><strong className="text-[#141414]">Fully refundable</strong> within 30 days after delivery.</span></li>
              </ul>
            </div>

            <div className="mb-6 flex items-center justify-between">
              <p className="text-sm text-[#737373]">Package</p>
              <div className="flex items-center gap-3">
                <button aria-label="Decrease package quantity" className="flex h-8 w-8 items-center justify-center rounded-full border border-black/10 text-sm transition-colors hover:bg-black/5" onClick={() => setQuantity((value) => Math.max(1, value - 1))}>−</button>
                <span className="w-6 text-center font-medium" data-pwc-controlled="package-quantity">{quantity}</span>
                <button aria-label="Increase package quantity" className="flex h-8 w-8 items-center justify-center rounded-full border border-black/10 text-sm transition-colors hover:bg-black/5" onClick={() => setQuantity((value) => value + 1)}>+</button>
              </div>
            </div>

            <button type="button" className="flex h-14 w-full items-center justify-center rounded-full bg-[#141414] text-base font-medium text-white shadow-md transition-all hover:-translate-y-0.5 hover:bg-black/90 hover:shadow-lg active:translate-y-0">Proceed to payment</button>
          </div>
        </div>
      </div>
    </main>
  );
}
