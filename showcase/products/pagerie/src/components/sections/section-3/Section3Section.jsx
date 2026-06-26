// Section3Section — clean JSX (route-(c) phase 2; theme.css styles real class names)
export default function Section3Section() {
  return (
    <div className="pwc-section pwc-section-3">
      <div className="site-section site-section--slideshow" id="site-section-slideshow">
        <section id="section-slideshow">
          <div className="Slideshow Slideshow--fullscreen">
            <div className="Slideshow__Carousel Carousel Carousel--fadeIn Carousel--fixed Carousel--insideDots flickity-enabled" data-flickity-config={"{\n  \"prevNextButtons\": false,\n  \"setGallerySize\": false,\n  \"adaptiveHeight\": false,\n  \"wrapAround\": true,\n  \"dragThreshold\": 15,\n  \"pauseAutoPlayOnHover\": false,\n  \"autoPlay\": 8000,\n  \"pageDots\": false\n}"} tabIndex="0">
              <div className="flickity-viewport">
                <div className="flickity-slider" style={{ left: '0px', transform: 'translateX(0%)' }}>
                  <div className="Slideshow__Slide Carousel__Cell is-selected" data-slide-index="0" id="Slideslide-0" style={{ visibility: 'inherit', position: 'absolute', left: '0%', opacity: '1' }}>
                    <div className="Slideshow__ImageContainer overlay hidden-tablet-and-up" style={{ backgroundImage: 'url("/assets/images/PAGERIE_Luxury_Dog_accessories_MOBILE_1x1.jpg")', display: 'none !important' }}>
                      <img alt="" className="Slideshow__Image Image--lazyLoad Image--lazyLoaded" data-src="/assets/images/PAGERIE_Luxury_Dog_accessories_MOBILE_x800.e7e18a.jpg" src="/assets/images/PAGERIE_Luxury_Dog_accessories_MOBILE_1x1.jpg" style={{ opacity: '1' }} />
                    </div>
                    <div className="Slideshow__ImageContainer overlay hidden-phone" style={{ backgroundImage: 'url(/assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_1x1.jpg)' }}>
                      <img alt="" className="Slideshow__Image hide-no-js lazyautosizes Image--lazyLoad Image--lazyLoadeded" data-optimumx="1.2" data-sizes="auto" data-srcset="/assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_400x.f776b0.jpg 400w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_600x.cfe02e.jpg 600w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_800x.87fc41.jpg 800w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_1000x.34c2c2.jpg 1000w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_1200x.0b6540.jpg 1200w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_1400x.b170eb.jpg 1400w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_1600x.adb563.jpg 1600w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_1800x.2ef13a.jpg 1800w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_2000x.d6fa9d.jpg 2000w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_2200x.94cc55.jpg 2200w" data-widths="[400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2200]" sizes="1440px" srcSet="/assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_400x.f776b0.jpg 400w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_600x.cfe02e.jpg 600w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_800x.87fc41.jpg 800w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_1000x.34c2c2.jpg 1000w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_1200x.0b6540.jpg 1200w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_1400x.b170eb.jpg 1400w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_1600x.adb563.jpg 1600w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_1800x.2ef13a.jpg 1800w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_2000x.d6fa9d.jpg 2000w, /assets/images/PAGERIE_Luxury_Dog_accessories_DESKTOP_2200x.94cc55.jpg 2200w" style={{ opacity: '1' }} />
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
