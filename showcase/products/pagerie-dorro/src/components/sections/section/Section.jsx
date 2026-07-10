// Section — deterministic faithful reconstruction (cleaned HTML + global theme CSS)
const __html = "<div class=\"site-section\" id=\"site-section-popup\"></div>";

export default function Section() {
  return <div className="pwc-section pwc-section" dangerouslySetInnerHTML={{ __html }} />;
}
