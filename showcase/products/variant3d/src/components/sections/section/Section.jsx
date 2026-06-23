const POSTER_URL =
  "https://cdn.prod.website-files.com/685c9371c8316839f0948d31%2F68cab5308c6b5e4df8bf1e39_V3D%20Hero%20background%20video-poster-00001.jpg";
const VIDEO_MP4 =
  "https://cdn.prod.website-files.com/685c9371c8316839f0948d31%2F68cab5308c6b5e4df8bf1e39_V3D%20Hero%20background%20video-transcode.mp4";
const VIDEO_WEBM =
  "https://cdn.prod.website-files.com/685c9371c8316839f0948d31%2F68cab5308c6b5e4df8bf1e39_V3D%20Hero%20background%20video-transcode.webm";

export default function Section() {
  return (
    <section
      className="intro section-dark relative flex flex-col"
      style={{
        height: "100vh",
        backgroundColor: "#000",
      }}
    >
      {/* Background video, full-bleed, behind the headline */}
      <div
        className="background-video absolute left-0 top-0 w-full overflow-hidden"
        style={{
          minHeight: "100vh",
          maxHeight: "100vh",
          color: "#fff",
          backgroundColor: "#000",
        }}
      >
        <video
          autoPlay
          loop
          muted
          playsInline
          poster={POSTER_URL}
          className="absolute inset-0 m-auto h-full w-full"
          style={{
            objectFit: "cover",
            backgroundImage: `url("${POSTER_URL}")`,
            backgroundPosition: "50%",
            backgroundSize: "cover",
            zIndex: -100,
          }}
          onError={(e) => {
            // Remote video may fail in static preview; fall back to poster bg only.
            e.currentTarget.style.display = "none";
          }}
        >
          <source src={VIDEO_MP4} type="video/mp4" />
          <source src={VIDEO_WEBM} type="video/webm" />
        </video>
      </div>

      {/* Large uppercase hero headline, anchored bottom-left */}
      <p
        className="text-large intro-text intro-text-home absolute bottom-0 left-0 m-0 uppercase"
        style={{
          zIndex: 5,
          color: "#f5f3f0",
          fontFamily: "'Founders Grotesk', Foundersgrotesk, Arial, sans-serif",
          fontWeight: 300,
          fontSize: "var(--hero-font-lg)",
          lineHeight: "75%",
          whiteSpace: "pre-line",
          paddingLeft: "var(--hero-page-padding)",
          paddingRight: "var(--hero-padding-right)",
          paddingBottom: "var(--hero-page-padding)",
          maxWidth: "100%",
        }}
      >
        {"software\nthat knits"}
      </p>

      {/* Responsive CSS variables faithful to the original Webflow breakpoints */}
      <style>{`
        .intro {
          --hero-font-lg: 100px;
          --hero-page-padding: 32px;
          --hero-padding-right: 32px;
        }
        @media screen and (min-width: 1440px) {
          .intro {
            --hero-font-lg: 120px;
            --hero-page-padding: 40px;
            --hero-padding-right: 40px;
          }
        }
        @media screen and (min-width: 1920px) {
          .intro {
            --hero-font-lg: 180px;
          }
        }
        @media screen and (max-width: 991px) {
          .intro {
            --hero-font-lg: 80px;
            --hero-page-padding: 24px;
            --hero-padding-right: 300px;
          }
        }
        @media screen and (max-width: 767px) {
          .intro {
            --hero-font-lg: 52px;
            --hero-page-padding: 16px;
            --hero-padding-right: 16px;
          }
        }
      `}</style>
    </section>
  );
}
