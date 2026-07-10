import './index.css';
import Section from './components/sections/section/Section.jsx';
import Section2Section from './components/sections/section-2/Section2Section.jsx';
import HeaderSection from './components/sections/header/HeaderSection.jsx';
import Section3Section from './components/sections/section-3/Section3Section.jsx';
import Section4Section from './components/sections/section-4/Section4Section.jsx';
import Section5Section from './components/sections/section-5/Section5Section.jsx';
import FeaturesSection from './components/sections/features/FeaturesSection.jsx';
import Section6Section from './components/sections/section-6/Section6Section.jsx';
import ProductSection from './components/sections/product/ProductSection.jsx';
import Product2Section from './components/sections/product-2/Product2Section.jsx';
import Section7Section from './components/sections/section-7/Section7Section.jsx';
import Section8Section from './components/sections/section-8/Section8Section.jsx';
import FooterSection from './components/sections/footer/FooterSection.jsx';

export default function App() {
  return (
    <div className="pwc-clone">
      <Section />
      <Section2Section />
      <HeaderSection />
      <Section3Section />
      <Section4Section />
      <Section5Section />
      <FeaturesSection />
      <Section6Section />
      <ProductSection />
      <Product2Section />
      <Section7Section />
      <Section8Section />
      <FooterSection />
    </div>
  );
}
