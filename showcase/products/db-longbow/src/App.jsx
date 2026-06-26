// App.jsx — Longbow clone (db-longbow.webflow.io), structurally faithful to .main.
import SiteFrame from "./components/SiteFrame.jsx";
import HeroSection from "./components/sections/hero/HeroSection.jsx";
import SpeedsterSection from "./components/sections/speedster/SpeedsterSection.jsx";
import RoadsterSection from "./components/sections/roadster/RoadsterSection.jsx";
import PhilosophySection from "./components/sections/philosophy/PhilosophySection.jsx";
import CreatingSection from "./components/sections/creating/CreatingSection.jsx";
import PreviewSection from "./components/sections/preview/PreviewSection.jsx";
import SpeedSection from "./components/sections/speed/SpeedSection.jsx";
import GallerySection from "./components/sections/gallery/GallerySection.jsx";
import VisionSection from "./components/sections/vision/VisionSection.jsx";
import BottomSection from "./components/sections/bottom/BottomSection.jsx";

export default function App() {
  return (
    <div id="main" className="main">
      <SiteFrame />
      <HeroSection />
      <SpeedsterSection />
      <RoadsterSection />
      <PhilosophySection />
      <CreatingSection />
      <PreviewSection />
      <SpeedSection />
      <GallerySection />
      <VisionSection />
      <BottomSection />
    </div>
  );
}
