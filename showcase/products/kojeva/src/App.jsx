import HeaderSection from "./components/sections/header/HeaderSection";
import Header2Section from "./components/sections/header-2/Header2Section";
import MainProductSection from "./components/sections/section/Section";
import ProductSection from "./components/sections/product/ProductSection";
import FeatureSection from "./components/sections/section-2/Section2Section";
import SatisfactionSection from "./components/sections/section-3/Section3Section";
import FaqSection from "./components/sections/faq/FaqSection";
import AboutSection from "./components/sections/about/AboutSection";
import FooterSection from "./components/sections/footer/FooterSection";
import Footer2Section from "./components/sections/footer-2/Footer2Section";

export default function App() {
  return (
    <>
      <div data-pwc-section="header"><HeaderSection /></div>
      <div data-pwc-section="header-2"><Header2Section /></div>
      <main>
        <div data-pwc-section="section"><MainProductSection /></div>
        <div data-pwc-section="product"><ProductSection /></div>
        <div data-pwc-section="section-2"><FeatureSection /></div>
        <div data-pwc-section="section-3"><SatisfactionSection /></div>
        <div data-pwc-section="faq"><FaqSection /></div>
        <div data-pwc-section="about"><AboutSection /></div>
      </main>
      <div data-pwc-section="footer"><FooterSection /></div>
      <div data-pwc-section="footer-2"><Footer2Section /></div>
    </>
  );
}
