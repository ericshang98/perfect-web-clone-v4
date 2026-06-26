// Section7Section — clean JSX (route-(c) phase 2; theme.css styles real class names)
export default function Section7Section() {
  return (
    <div className="pwc-section pwc-section-7">
      <div className="site-section" id="site-section-d9cedfa4-3f81-444c-812c-591cf292c7d0">
        <section className="Section">
          <div className="featured_product_img" style={{ display: 'grid' }}>
            <div className="FeaturedProduct" style={{ width: '720px', maxWidth: '100%' }}>
              <div className="heading">
                <h2>
                  Signature Collar
                </h2>
              </div>
              <a className="FeaturedProduct__Gallery" href="/products/the-dorro-luxury-collar">
                <div className="AspectRatio" style={{ maxWidth: '1500px', '--aspect-ratio': '0.7735946364105208' }}>
                  <img src="/assets/images/PAGERIE-PDP-The-Sahara-Collection-The-Dorro-Luxury-Pet-Collar-Saddle-01-FINAL-V2_1200x.317dbc.png" alt="The Dórro" className="Image--lazyLoad Image--lazyLoaded Image--fadeIn" data-sizes="auto" data-src="/assets/images/PAGERIE-PDP-The-Sahara-Collection-The-Dorro-Luxury-Pet-Collar-Saddle-01-FINAL-V2_1200x.317dbc.png" data-widths="[200,300,400,600,700,800,900,1000]" />
                  <span className="Image__Loader" style={{ display: 'none !important' }} />
                </div>
              </a>
              <div className="FeaturedProduct__Info" style={{ display: 'grid' }}>
                <h5 className="product_title">
                  <a href="/products/the-dorro-luxury-collar">
                    The Dórro
                  </a>
                </h5>
                <div className="FeaturedProduct__ViewWrapper">
                  <a className="Link Link--underline" href="/products/the-dorro-luxury-collar">
                    Shop Now
                  </a>
                </div>
              </div>
            </div>
            <div className="product_img" style={{ width: '720px', maxWidth: '100%' }}>
              <img src="/assets/images/PAGERIE_Luxury_Dog_accessories_HERO.jpg" />
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
