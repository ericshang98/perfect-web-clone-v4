export default function Section8Section() {
  // Collaborator logos — order mirrors the source DOM. local_url is null for all,
  // so we hotlink the remote source and hide on error.
  const collaborators = [
    { href: "https://www.visioneeringstudios.com/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68df1587b10a87cfe44b2f44_V3D%20Collab%20Logos-Visoneering.png" },
    { href: "https://www.kxlab.la/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e02782ac0cf5e9af5e0f51_V3D%20Collab%20Logos-Kxlab.png" },
    { href: "https://www.pneu.haus/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68df142eeda329be91feca4f_V3D%20Collab%20Logos-Pneuhaus.png" },
    { href: "https://www.andari.com/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68df25f4497f392d36808669_V3D%20Collab%20Logos-Andari.png" },
    { href: "https://www.aiknit.com/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e03145a95beb5bf4612b2b_V3D%20Collab%20Logos-AI%20KNIT.png" },
    { href: "https://www.nilit.com/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68df145229e11b852fbea634_V3D%20Collab%20Logos-Nilit.png" },
    { href: "https://www.woolmark.com/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68df0d34fda93f12d2e248f1_V3D%20Collab%20Logos-Wallmark.png" },
    { href: "https://www.artcenter.edu/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68df0edfdb138008fe6ec241_V3D%20Collab%20Logos-Artcenter.png" },
    { href: "https://www.abundance360.com/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68df262f4a93b3105352391f_V3D%20Collab%20Logos-A360.png" },
    { href: "https://affoa.org/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e00a19f94a55e226a04146_V3D%20Collab%20Logos-affa.png" },
    { href: "http://apparel.pi.tv/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e004f206cbdbc9448596e0_V3D%20Collab%20Logos-PI%20Apparel.png" },
    { href: "https://www.lalaland-design.com/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e032d7ae60ee5a4cfa4adc_V3D%20Collab%20Logos-Lalaland.png" },
    { href: "https://eco-age.com/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e00f8b34fcc78aef74a355_V3D%20Collab%20Logos-Ecoage.png" },
    { href: "https://slicelab.com/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68df0d03ba6a24de8b852ebd_V3D%20Collab%20Logos-Slicelab.png" },
    { href: "https://www.evrnu.com/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68df267789049965434b23d1_V3D%20Collab%20Logos-enrnu.png" },
    { href: "https://www.newlab.com/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e00b16fe92c50f654ce525_V3D%20Collab%20Logos-Newlab.png" },
    { href: "https://www.suedwollegroup.com/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e00a3eff46f7e6358b61e0_V3D%20Collab%20Logos-Sudwolle.png" },
    { href: "https://eco-age.com/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68df0e97e7e9714368012a2f_V3D%20Collab%20Logos-Isac.png" },
    { href: "https://shop.cta.tech/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e006e5523905099b7b5c90_V3D%20Collab%20Logos-CES.png" },
    { href: "https://www.ernsteverything.com/about", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68df269fcd6e195243f9a132_V3D%20Collab%20Logos-Ernst.png" },
    { href: "https://eco-age.com/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68df0e7c47263f2a1c2fb460_V3D%20Collab%20Logos-Laci.png" },
    { href: "https://www.intel.com/content/www/us/en/homepage.html", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68df1027ff15b447d6e06715_V3D%20Collab%20Logos-Intel.png" },
    { href: "https://nexusglobal.org/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e02c7a422948e5d9eb29f9_V3D%20Collab%20Logos-Nexus.png" },
    { href: "https://www.nearfuturesummit.com/", src: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e0053623d7128022715449_V3D%20Collab%20Logos-Nearfuture.png" },
  ];

  const hideOnError = (e) => {
    e.currentTarget.style.visibility = "hidden";
  };

  const LogoItem = ({ item }) => (
    <div
      role="listitem"
      className="collaborators-list-item flex shrink-0 grow-0 items-center justify-center"
      style={{
        minWidth: "14vw",
        height: "130px",
      }}
    >
      <a
        href={item.href}
        target="_blank"
        rel="noopener noreferrer"
        className="w-inline-block flex max-w-full shrink-0 grow-0 items-center justify-center"
        style={{ width: "182px" }}
      >
        <img
          src={item.src}
          alt=""
          loading="lazy"
          onError={hideOnError}
          className="collaborator-logo max-w-full transition-opacity duration-300"
          style={{ opacity: 0.25 }}
        />
      </a>
    </div>
  );

  // The source duplicates the full list twice inside the marquee for a seamless loop.
  const Track = () => (
    <div
      role="list"
      className="collaborators-list flex"
      style={{ transform: "translateX(-2px)" }}
    >
      {collaborators.map((item, i) => (
        <LogoItem key={i} item={item} />
      ))}
    </div>
  );

  return (
    <section className="w-full overflow-hidden bg-black text-white">
      <style>{`
        @keyframes v3d-collab-marquee {
          from { transform: translateX(-2px); }
          to   { transform: translateX(calc(-50% - 2px)); }
        }
        .v3d-collab-track {
          display: flex;
          width: max-content;
          animation: v3d-collab-marquee 40s linear infinite;
        }
        .v3d-collab-wrapper:hover .v3d-collab-track {
          animation-play-state: paused;
        }
        .collaborator-logo:hover { opacity: 1 !important; }
        @media (max-width: 991px) {
          .collaborators-list-item { min-width: 40vw !important; }
          .v3d-collab-gradient { width: 15vw !important; }
        }
        @media (max-width: 767px) {
          .collaborators-list-item { min-width: 33vw !important; }
        }
      `}</style>

      <div className="collaborators-marquee-wrapper v3d-collab-wrapper relative flex overflow-hidden">
        {/* left fade */}
        <div
          className="v3d-collab-gradient pointer-events-none absolute left-0 top-0 h-full"
          style={{
            zIndex: 10,
            width: "250px",
            backgroundImage:
              "linear-gradient(90deg, #000000, transparent)",
          }}
        />
        {/* right fade */}
        <div
          className="v3d-collab-gradient pointer-events-none absolute right-0 top-0 h-full"
          style={{
            zIndex: 10,
            width: "250px",
            backgroundImage:
              "linear-gradient(280deg, #000000, transparent)",
          }}
        />

        <div className="collaborators-list-wrapper v3d-collab-track flex flex-row">
          <Track />
          <Track />
        </div>
      </div>
    </section>
  );
}
