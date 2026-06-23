import { useState } from "react";

// section-2 — "mobile-video-section section-dark"
// Mobile-only video block (Vimeo player). Hidden on desktop (>991px),
// shown as a 16:9 rounded video card with thumbnail poster + play button on
// tablet/mobile. The live Vimeo iframe can't run statically, so we reproduce
// the container at the exact size/background and show the poster + play UI.
export default function Section2Section() {
  const [playing, setPlaying] = useState(false);

  return (
    <section
      className="mobile-video-section hidden max-[991px]:block bg-black"
      style={{
        // padding: 40px var(--page-padding) 20px  (page-padding = 24px @ <=991, 16px @ <=767)
        paddingTop: "40px",
        paddingBottom: "20px",
        paddingLeft: "var(--_spacing---page-padding, 24px)",
        paddingRight: "var(--_spacing---page-padding, 24px)",
      }}
    >
      <div
        className="mobile-video-container relative overflow-hidden w-full"
        style={{
          zIndex: 100,
          aspectRatio: "16 / 9",
          borderRadius: "var(--_spacing---radius-md, 8px)",
          transition: "all .4s cubic-bezier(.25,.46,.45,.94)",
        }}
      >
        {/* video player wrapper (iframe lives here at runtime) */}
        <div
          className="video-player relative w-full h-full overflow-hidden"
          style={{ borderRadius: "var(--_spacing---radius-md, 8px)" }}
          aria-hidden={!playing}
        />

        {/* thumbnail poster */}
        <img
          alt=""
          loading="lazy"
          src="/assets/images/68cc6bc71c2bb26185f63729_179713f5e2784f429fc11eed262248eb_video_thumbnail.webp"
          className="video-thumbnail absolute inset-0 w-full h-full object-cover"
          style={{
            zIndex: 6,
            borderRadius: "var(--_spacing---radius-md, 8px)",
            opacity: playing ? 0 : 1,
            transition: "opacity .3s cubic-bezier(.25,.46,.45,.94)",
          }}
          onError={(e) => {
            e.currentTarget.style.display = "none";
          }}
        />

        {/* play button */}
        <div
          role="button"
          onClick={() => setPlaying(true)}
          className="video-button video-button-play absolute flex items-center justify-center rounded-full cursor-pointer
                     w-20 min-w-20 h-20 max-[767px]:w-[60px] max-[767px]:min-w-[60px] max-[767px]:h-[60px]"
          style={{
            zIndex: 7,
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            border: "1px solid var(--_colors---glass-border, #e5e3e033)",
            backgroundColor: "var(--_colors---glass, #94939059)",
            backdropFilter: "blur(5px)",
            WebkitBackdropFilter: "blur(5px)",
            opacity: playing ? 0 : 1,
            transition: "opacity .2s cubic-bezier(.25,.46,.45,.94)",
            pointerEvents: playing ? "none" : "auto",
          }}
        >
          <img
            alt=""
            loading="lazy"
            src="/assets/images/68b616bb0d02cd0f0f21b499_Play.png"
            onError={(e) => {
              e.currentTarget.style.display = "none";
            }}
          />
        </div>
      </div>
    </section>
  );
}
