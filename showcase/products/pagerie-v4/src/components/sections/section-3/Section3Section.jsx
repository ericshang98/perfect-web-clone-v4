// Section3Section — clean JSX (v4 new-code pipeline)
export default function Section3Section() {
  return (
    <div className="pwc-section pwc-section-3">
      <div className="shop-section shop-section--slideshow" id="shop-section-slideshow">
        <section data-section-id="slideshow" data-section-type="slideshow" id="section-slideshow">
          <div className="Slideshow Slideshow--fullscreen">
            <div className="Slideshow__Carousel Carousel Carousel--fadeIn Carousel--fixed Carousel--insideDots flickity-enabled" data-flickity-config={"{\n  \"prevNextButtons\": false,\n  \"setGallerySize\": false,\n  \"adaptiveHeight\": false,\n  \"wrapAround\": true,\n  \"dragThreshold\": 15,\n  \"pauseAutoPlayOnHover\": false,\n  \"autoPlay\": 8000,\n  \"pageDots\": false\n}"} tabIndex="0">
              <div className="flickity-viewport">
                <div className="flickity-slider" style={{ left: '0px', transform: 'translateX(0%)' }}>
                  <div className="Slideshow__Slide Carousel__Cell is-selected" data-slide-index="0" id="Slideslide-0" style={{ visibility: 'inherit', position: 'absolute', left: '0%', opacity: '1' }}>
                    <div className="Slideshow__ImageContainer overlay hidden-tablet-and-up" style={{ backgroundImage: 'url("/assets/images/PAGERIE_Luxury_Dog_accessories_MOBILE_1x1.jpg")', display: 'none !important' }}>
                      <img alt="" className="Slideshow__Image Image--lazyLoad" data-src="/cdn/shop/files/PAGERIE_Luxury_Dog_accessories_MOBILE_x800.jpg?v=1778791671" src="/assets/images/PAGERIE_Luxury_Dog_accessories_MOBILE_1x1.jpg" style={{ opacity: '1' }} />
                    </div>
                    <div className="Slideshow__ImageContainer overlay hidden-phone" style={{ backgroundImage: 'url(/assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_1x1.jpg)' }}>
                      <img alt="" className="Slideshow__Image hide-no-js lazyautosizes Image--lazyLoaded" data-optimumx="1.2" data-sizes="auto" data-srcset="/cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_400x.jpg?v=1778792154 400w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_600x.jpg?v=1778792154 600w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_800x.jpg?v=1778792154 800w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_1000x.jpg?v=1778792154 1000w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_1200x.jpg?v=1778792154 1200w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_1400x.jpg?v=1778792154 1400w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_1600x.jpg?v=1778792154 1600w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_1800x.jpg?v=1778792154 1800w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_2000x.jpg?v=1778792154 2000w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_2200x.jpg?v=1778792154 2200w" data-widths="[400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2200]" sizes="1440px" srcSet="/cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_400x.jpg?v=1778792154 400w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_600x.jpg?v=1778792154 600w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_800x.jpg?v=1778792154 800w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_1000x.jpg?v=1778792154 1000w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_1200x.jpg?v=1778792154 1200w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_1400x.jpg?v=1778792154 1400w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_1600x.jpg?v=1778792154 1600w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_1800x.jpg?v=1778792154 1800w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_2000x.jpg?v=1778792154 2000w, /cdn/shop/files/PAGERIE_Luxury_Dog_accessories_DESKTOP_2200x.jpg?v=1778792154 2200w" style={{ opacity: '1' }} />
                    </div>
                    <div className="Slideshow__Content Slideshow__Content--middleLeft Mobi_Slideshow__Content--middleCenter" id="block-slide-0">
                      <header className="SectionHeader" style={{ visibility: 'inherit', opacity: '1', transform: 'matrix(1, 0, 0, 1, 0, 0)' }}>
                        <h3 className="SectionHeader__SubHeading Heading u-h6" style={{ lineHeight: '35px', letterSpacing: '1px' }}>
                          THE NEW NEUTRAL
                        </h3>
                        <h2 className="SectionHeader__Heading SectionHeader__Heading--emphasize Heading u-h1" style={{ letterSpacing: '0px', lineHeight: '30px' }}>
                          Granite
                        </h2>
                        <div className="description">
                          <p>
                            Think neutrals have to be boring? Think again.
                            <br />
                            Understated. Sculpted. We’ve called our new colourway Granite, but this hue’s strong as steel.
                          </p>
                        </div>
                        <div className="SectionHeader__ButtonWrapper" style={{ visibility: 'inherit', opacity: '1', transform: 'matrix(1, 0, 0, 1, 0, 0)' }}>
                          <div className="ButtonGroup ButtonGroup--spacingSmall" style={{ display: 'flex' }}>
                            <a className="ButtonGroup__Item Button" href="/products/the-dorro-luxury-collar" style={{ margin: '8px', lineHeight: '27px', letterSpacing: '2px' }}>
                              SHOP NOW
                            </a>
                          </div>
                        </div>
                      </header>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <span className="Anchor" id="section-slideshow-end" style={{ display: 'none !important' }} />
        </section>
      </div>
    </div>
  );
}
