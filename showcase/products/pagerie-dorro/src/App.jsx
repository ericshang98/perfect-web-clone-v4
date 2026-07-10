import Section from './components/sections/section/Section.jsx'
import Section2Section from './components/sections/section-2/Section2Section.jsx'
import HeaderSection from './components/sections/header/HeaderSection.jsx'
import GallerySection from './components/sections/gallery/GallerySection.jsx'
import ProductSection from './components/sections/product/ProductSection.jsx'
import Section3Section from './components/sections/section-3/Section3Section.jsx'
import Section4Section from './components/sections/section-4/Section4Section.jsx'
import Section5Section from './components/sections/section-5/Section5Section.jsx'
import Product2Section from './components/sections/product-2/Product2Section.jsx'
import Section6Section from './components/sections/section-6/Section6Section.jsx'
import FooterSection from './components/sections/footer/FooterSection.jsx'

export default function App() {
  return (
    <>
      <Section />
      <Section2Section />
      <HeaderSection />
      <div className="pwc-pdp-row"><GallerySection /><ProductSection /></div>
      <Section3Section />
      <Section4Section />
      <Section5Section />
      <Product2Section />
      <Section6Section />
      <FooterSection />
    </>
  )
}
