export default function GallerySection() {
  // Faithful reproduction of the variant3d.io "KnitSmarter" home gallery section.
  // Dark, full-bleed section with a sticky centered display heading and scattered
  // product shots + glass "UI" cards positioned absolutely with vw/vh units.
  // CSS variables and the 4 responsive breakpoints (base / <=767 / <=991 / >=1440)
  // are reproduced verbatim from the extracted css_rules.

  const hideOnError = (e) => {
    e.currentTarget.style.display = "none";
  };

  return (
    <>
    <section className="v3-gallery section-dark section-home-gallery">
      <style>{`
        .v3-gallery {
          /* color + spacing tokens from the original site */
          --_colors---font-light: #f5f3f0;
          --_colors---brand: #f75f2d;
          --_colors---glass: #94939059;
          --_colors---glass-border: #e5e3e033;
          --_spacing---radius-md: 12px;
          --_font-sizes---font-lg: 100px;

          width: 100%;
          height: 184vh;
          position: relative;
          background-color: #000;
          color: var(--_colors---font-light);
          font-family: 'Founders Grotesk', Foundersgrotesk, Arial, sans-serif;
        }

        /* ---- sticky centered heading ---- */
        .v3-gallery .home-gallery-title-wrapper {
          z-index: 5;
          justify-content: center;
          align-items: center;
          width: 100%;
          height: 100vh;
          display: flex;
          position: sticky;
          top: 0;
        }
        .v3-gallery .text-large {
          color: var(--_colors---font-light);
          font-family: 'Founders Grotesk', Foundersgrotesk, Arial, sans-serif;
          font-size: var(--_font-sizes---font-lg);
          text-transform: uppercase;
          white-space: pre-line;
          margin-top: 0;
          margin-bottom: 0;
          font-weight: 300;
          line-height: 75%;
        }
        .v3-gallery .text-large.text-center {
          z-index: 5;
          text-align: center;
          position: relative;
          width: 500px;
          max-width: 100%;
        }

        /* ---- gallery canvas ---- */
        .v3-gallery .home-gallery {
          width: 100%;
          height: 100%;
          position: absolute;
          inset: 0%;
          overflow: hidden;
        }

        /* ---- product images (base) ---- */
        .v3-gallery .home-gallery-image-1 {
          z-index: 7; aspect-ratio: 1;
          border-radius: var(--_spacing---radius-md);
          object-fit: cover; width: 16.4vw;
          position: absolute; top: 20vh; left: -9px;
        }
        .v3-gallery .home-gallery-image-2 {
          z-index: 4; aspect-ratio: 328 / 330;
          border-radius: var(--_spacing---radius-md);
          object-fit: cover; width: 25.6vw;
          position: absolute; top: 9.86vh; right: 1.25vw;
        }
        .v3-gallery .home-gallery-image-3 {
          z-index: 1; aspect-ratio: 334 / 321;
          border-radius: var(--_spacing---radius-md);
          object-fit: cover; width: 26.1vw;
          position: absolute; top: 69.8vh; left: 16.6vw;
        }
        .v3-gallery .home-gallery-image-4 {
          aspect-ratio: 452 / 602;
          border-radius: var(--_spacing---radius-md);
          object-fit: cover; width: 35.3vw;
          position: absolute; top: 62vh; right: -24.68vw;
        }
        .v3-gallery .home-gallery-image-5 {
          aspect-ratio: 204 / 196;
          border-radius: var(--_spacing---radius-md);
          object-fit: cover; width: 15.9vw;
          position: absolute; bottom: 11.4vh; left: -7.9vw;
        }
        .v3-gallery .home-gallery-image-6 {
          z-index: 4; aspect-ratio: 4 / 3;
          border-radius: var(--_spacing---radius-md);
          object-fit: cover; width: 31.25vw;
          position: absolute; bottom: 9.25vh; right: 3.6vw;
        }

        /* ---- glass UI cards (base) ---- */
        .v3-gallery .home-gallery-ui-1 {
          z-index: 10;
          border: 1px solid var(--_colors---glass-border);
          border-radius: var(--_spacing---radius-md);
          background-color: var(--_colors---glass);
          -webkit-backdrop-filter: blur(5px); backdrop-filter: blur(5px);
          width: 12.5vw; position: absolute; top: 47.5vh; left: 17.7vw;
        }
        .v3-gallery .home-gallery-ui-1-text { width: 100%; display: block; }
        .v3-gallery .home-gallery-ui-1-icon {
          width: 6.25vw; position: absolute; top: 0; left: 0%;
          transform: translate(-72%, -72%);
        }
        .v3-gallery .home-gallery-ui-2 {
          z-index: 4;
          border: 1px solid var(--_colors---glass-border);
          border-radius: var(--_spacing---radius-md);
          background-color: var(--_colors---glass);
          -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px);
          width: 16.48vw; position: absolute; top: 36vh; right: 23.75vw;
        }
        .v3-gallery .home-gallery-ui-3 {
          z-index: 10;
          border-radius: var(--_spacing---radius-md);
          width: 16.4vw; position: absolute; top: 103vh; left: 7.1vw;
        }
        .v3-gallery .home-gallery-ui-4 {
          z-index: 10;
          border: 1px solid var(--_colors---glass-border);
          border-radius: var(--_spacing---radius-md);
          background-color: var(--_colors---glass);
          -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px);
          width: 7.26vw; position: absolute; top: 101.2vh; right: 7.1vw;
        }
        .v3-gallery .home-gallery-ui-5 {
          z-index: 10;
          border: 1px solid var(--_colors---glass-border);
          border-radius: var(--_spacing---radius-md);
          background-color: var(--_colors---glass);
          -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px);
          width: 26vw; position: absolute; bottom: 31.4vh; left: 3.125px;
        }
        .v3-gallery .home-gallery-ui-6 {
          z-index: 4;
          border: 1px solid var(--_colors---glass-border);
          border-radius: var(--_spacing---radius-md);
          background-color: var(--_colors---glass);
          -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px);
          width: 26.1vw; position: absolute; bottom: 42vh; right: 18.9vw;
        }
        .v3-gallery .home-gallery-ui-2,
        .v3-gallery .home-gallery-ui-3,
        .v3-gallery .home-gallery-ui-4,
        .v3-gallery .home-gallery-ui-5,
        .v3-gallery .home-gallery-ui-6 { display: block; }

        /* ===== >= 1440px ===== */
        @media screen and (min-width: 1440px) {
          .v3-gallery { --_font-sizes---font-lg: 120px; height: 200vh; }
          .v3-gallery .home-gallery-image-1 { width: 13.88vw; top: 17.8vh; left: 7.1vw; }
          .v3-gallery .home-gallery-image-2 { width: 21.7vw; top: 8.6vh; right: 10.71vw; }
          .v3-gallery .home-gallery-image-3 { width: 22.1vw; top: 61.4vh; left: 21.76vw; }
          .v3-gallery .home-gallery-image-4 { width: 29.89vw; top: 54.6vh; right: -13.2vw; }
          .v3-gallery .home-gallery-image-5 { width: 13.49vw; bottom: 10vh; left: -2.3vw; }
          .v3-gallery .home-gallery-image-6 { width: 26.45vw; bottom: 7vh; right: 4.5vw; }
          .v3-gallery .home-gallery-ui-1 { width: 11vw; top: 41.9vh; left: 22.68vw; }
          .v3-gallery .home-gallery-ui-1-icon { width: 5.29vw; }
          .v3-gallery .home-gallery-ui-2 { width: 13.95vw; top: 35.8vh; right: 27.7vw; }
          .v3-gallery .home-gallery-ui-3 { width: 13.89vw; top: 90vh; left: 13.7vw; }
          .v3-gallery .home-gallery-ui-4 { width: 6.15vw; top: 89vh; right: 13.6vw; }
          .v3-gallery .home-gallery-ui-5 { width: 22vw; bottom: 25vh; left: 7px; }
          .v3-gallery .home-gallery-ui-6 { width: 20vw; bottom: 32vh; right: 17vw; }
        }

        /* ===== <= 991px ===== */
        @media screen and (max-width: 991px) {
          .v3-gallery {
            --_spacing---radius-md: 8px;
            --_font-sizes---font-lg: 80px;
            height: 158vh;
          }
        }

        /* ===== <= 767px ===== */
        @media screen and (max-width: 767px) {
          .v3-gallery { height: 106vh; }
          .v3-gallery .home-gallery-image-1 { width: 22.82vw; top: 17.7vh; left: -9.7vw; }
          .v3-gallery .home-gallery-image-2 { width: 35.64vw; top: 9.23vh; right: 5.22vw; }
          .v3-gallery .home-gallery-image-3 { width: 36.3vw; top: 35.74vh; left: 5.95vw; }
          .v3-gallery .home-gallery-image-4 { width: 49.13vw; top: 40.75vh; }
          .v3-gallery .home-gallery-image-5 { width: 22.2vw; bottom: 10.93vh; left: -11.4vw; }
          .v3-gallery .home-gallery-image-6 { width: 43.47vw; bottom: 8.4vh; right: -9.2vw; }
          .v3-gallery .home-gallery-ui-1 { width: 16.72vw; top: 29vh; left: 16.16vw; }
          .v3-gallery .home-gallery-ui-1-icon { width: 8.69vw; }
          .v3-gallery .home-gallery-ui-2 {
            -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px);
            width: 22.9vw; top: 22vh; right: 33vw;
          }
          .v3-gallery .home-gallery-ui-3 { width: 22.8vw; top: 49.5vh; left: -7.5vw; }
          .v3-gallery .home-gallery-ui-4 { width: 10.1vw; top: 50.3vh; right: 14vw; }
          .v3-gallery .home-gallery-ui-5 {
            -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px);
            width: 36.3vw; bottom: 19.3vh; left: -7.2vw;
          }
          .v3-gallery .home-gallery-ui-6 {
            -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px);
            width: 36.3vw; bottom: 22vh; right: 21.4vw;
          }
        }
      `}</style>

      <div className="home-gallery-title-wrapper" style={{ display: "flex" }}>
        <h2 className="text-large text-center">
          Knit<br />Smarter
        </h2>
      </div>

      <div className="home-gallery">
        {/* image 1 — car */}
        <img
          alt=""
          className="home-gallery-image-1"
          loading="lazy"
          src="/assets/images/68ffb9f56487fe5be48a62b8_car-home.webp"
          onError={hideOnError}
        />

        {/* UI 1 — lamp panel w/ cursor */}
        <div className="home-gallery-ui-1">
          <img
            alt=""
            className="home-gallery-ui-1-text"
            loading="lazy"
            src="/assets/images/68b9a6481fa06eecae860753_Lamp.png"
            onError={hideOnError}
          />
          <img
            alt=""
            className="home-gallery-ui-1-icon"
            loading="lazy"
            src="/assets/images/68b9a6480c18b174176e9a00_Cursor.png"
            onError={hideOnError}
          />
        </div>

        {/* image 2 — diffuse leggings */}
        <img
          alt=""
          className="home-gallery-image-2"
          loading="lazy"
          src="/assets/images/68ffb9f5e00c6ccf35a3d25b_diffuse-leggings-home.webp"
          onError={hideOnError}
        />

        {/* UI 2 — legging panel */}
        <img
          alt=""
          className="home-gallery-ui-2"
          loading="lazy"
          src="/assets/images/68b986d03aa1da74d9aac448_113ff116bcd6780d86c275cbf22236b1_Legging.png"
          onError={hideOnError}
        />

        {/* image 3 — lamp */}
        <img
          alt=""
          className="home-gallery-image-3"
          loading="lazy"
          src="/assets/images/68ffb9f578acf1358264f060_lamp-home.webp"
          onError={hideOnError}
        />

        {/* UI 3 — colorways */}
        <img
          alt=""
          className="home-gallery-ui-3"
          loading="lazy"
          src="/assets/images/68ffee9f5acb14b5b2b467eb_Colorways.png"
          onError={hideOnError}
        />

        {/* image 4 — bevans */}
        <img
          alt=""
          className="home-gallery-image-4"
          loading="lazy"
          src="/assets/images/68ffb9f4569f180783c9bc28_bevans-home.webp"
          onError={hideOnError}
        />

        {/* UI 4 — arrow */}
        <img
          alt=""
          className="home-gallery-ui-4"
          loading="lazy"
          src="/assets/images/68b9873c836a2543ba6760cb_Arrow.png"
          onError={hideOnError}
        />

        {/* image 5 — A360 (no local asset → remote + hide on error) */}
        <img
          alt=""
          className="home-gallery-image-5"
          loading="lazy"
          src="https://cdn.prod.website-files.com/685c9371c8316839f0948d31/68d2fe023806802a1419f94c_A360_4.webp"
          onError={hideOnError}
        />

        {/* UI 5 — shoe */}
        <img
          alt=""
          className="home-gallery-ui-5"
          loading="lazy"
          src="/assets/images/68b986d0e7f07f380b3525f1_Shoe.png"
          onError={hideOnError}
        />

        {/* image 6 — chair */}
        <img
          alt=""
          className="home-gallery-image-6"
          loading="lazy"
          src="/assets/images/68ffb9f4d8e6b8f92c47fc45_Chair-home.webp"
          onError={hideOnError}
        />

        {/* UI 6 — comment */}
        <img
          alt=""
          className="home-gallery-ui-6"
          loading="lazy"
          src="/assets/images/68b986d0374a72ac997174a6_Comment.png"
          onError={hideOnError}
        />
      </div>
    </section>

    {/* ===== features-section (id="features") — faithful to raw_html ===== */}
    {/* On the live site a Swiper turns each .features-block into a vertical-scroll
        slide; only the active slide is visible at a time. Reproduced here as a
        light section with the three Features product shots stacked as slides. */}
    <section className="v3-features section-light features-section" id="features">
      <style>{`
        .v3-features {
          --_colors---bg-light: #f5f3f0;
          --_colors---brand: #f75f2d;
          --_colors---gray-300: #cfcdc9;
          --_spacing---page-padding: 5vw;
          width: 100%;
          background-color: var(--_colors---bg-light);
          font-family: 'Founders Grotesk', Foundersgrotesk, Arial, sans-serif;
        }
        .v3-features .features-container {
          display: flex;
          align-items: stretch;
          min-height: 100vh;
        }
        .v3-features .features-texts-swiper-container {
          flex: 0 0 35%;
          display: flex;
          flex-direction: column;
          justify-content: center;
          gap: 24px;
          padding: 0 var(--_spacing---page-padding);
        }
        .v3-features .features-text-title {
          font-size: 52px;
          line-height: 0.8;
          text-transform: lowercase;
          font-weight: 300;
          margin: 0;
        }
        .v3-features .features-text {
          font-size: 24px;
          line-height: 1.1;
          margin: 0;
        }
        .v3-features .features-swiper-container {
          flex: 1 1 65%;
          display: flex;
          flex-direction: column;
          gap: 24px;
          padding-right: var(--_spacing---page-padding);
          justify-content: center;
        }
        .v3-features .swiper-slide-features {
          background-color: var(--_colors---bg-light);
        }
        .v3-features .features-block-image {
          width: 100%;
          height: auto;
          display: block;
          border-radius: 12px;
          object-fit: cover;
        }
        @media screen and (max-width: 991px) {
          .v3-features .features-container { flex-direction: column; }
        }
      `}</style>

      <div className="features-container">
        <div className="features-texts-swiper-container">
          <div className="swiper-slide swiper-slide-features-texts">
            <p className="features-text-title">true creative<br />freedom</p>
            <p className="features-text">
              What you envision is what you make,<br />no matter how complex.
            </p>
          </div>
          <div className="swiper-slide swiper-slide-features-texts">
            <p className="features-text-title">built for speed</p>
            <p className="features-text">
              More ideas, less waiting. Launch quality products in days, not months.
            </p>
          </div>
          <div className="swiper-slide swiper-slide-features-texts">
            <p className="features-text-title">scale<br />with purporse</p>
            <p className="features-text">
              Unite teams around design intent—one platform where iterative truth drives production.
            </p>
          </div>
        </div>

        <div className="features-swiper-container">
          {/* Features-01 */}
          <div className="swiper-slide swiper-slide-features">
            <img
              alt=""
              className="features-block-image clipped-image"
              data-clip-id="1"
              loading="lazy"
              src="/assets/images/68cc021dce63864d530595be_7e9054c46306bfd0e8aa5e2dff4792b3_Features-01.webp"
              onError={hideOnError}
            />
          </div>
          {/* Features-02 */}
          <div className="swiper-slide swiper-slide-features">
            <img
              alt=""
              className="features-block-image clipped-image"
              data-clip-id="2"
              loading="lazy"
              src="/assets/images/68cb553c634ed645ceb6e098_e332dbd42107854ce08217d7a868075c_Features-02.webp"
              onError={hideOnError}
            />
          </div>
          {/* Features-03a */}
          <div className="swiper-slide swiper-slide-features">
            <img
              alt=""
              className="features-block-image clipped-image"
              data-clip-id="3"
              loading="lazy"
              src="/assets/images/68cb553dc05c947223270a8c_4bb4afa051583f45bd34b8763f29cbf0_Features-03a.webp"
              onError={hideOnError}
            />
          </div>
        </div>
      </div>
    </section>
    </>
  );
}
