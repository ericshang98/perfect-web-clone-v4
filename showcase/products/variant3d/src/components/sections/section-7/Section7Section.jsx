import { useRef } from "react";

// Data-driven from section-7.json. All images have local_url=null,
// so remote src is used with onError hide. Order/tags/names preserved.
const CLIENTS = [
  {
    name: "Abundance360",
    tags: ["Footwear"],
    img: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e066d2ed83b612fd7a0305_Screenshot%202025-10-03%20at%205.05.03%20PM.png",
  },
  {
    name: "David Horvitz",
    tags: ["Art"],
    img: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68a7c55539674637013b752b_58b180dc927ecf8f85e018f6f24c8348acebffc7.png",
  },
  {
    name: "Nucycl | Bevans",
    tags: ["Apparel"],
    img: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68a7c68ffea1dd5d06d58d82_f58459ce4854af693bacd65a5dcd4276647ecda0.jpg",
  },
  {
    name: "LACI",
    tags: ["Installation", "Furniture"],
    img: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68a7c6b95c4b8363c0748f88_bccd54a0908c46cb9328609c7c83eeeb04ded445.png",
  },
  {
    name: "Pierre Cardin",
    tags: ["Apparel"],
    img: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68a873ff0e9791ab0445e9be_0768c45929c3fb3fc7182577f4f08008ada98aee.png",
  },
  {
    name: "Slicelab",
    tags: ["Footwear"],
    img: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e0666faca239f0eb2c6280_Screenshot%202025-10-03%20at%205.11.18%20PM.jpg",
  },
  {
    name: "Carlos Campos",
    tags: ["Apparel"],
    img: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e0645a973359ef99d9706d_Screenshot%202025-10-03%20at%205.02.56%20PM.png",
  },
  {
    name: "The Surrey",
    tags: ["Home Decor"],
    img: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e04fe11c6d99d8dc478d80_THE%20SURREY_Collab1.png",
  },
  {
    name: "Xprize",
    tags: ["Accessories"],
    img: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e04da4196b3d1ba554b326_XPRIZE_Collab.jpg",
  },
  {
    name: "Virgin",
    tags: ["Home Decor"],
    img: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e04e4fdd30fe1e99ba0e76_Virgin_Collab.png",
  },
  {
    name: "Calamigos Ranch",
    tags: ["Furniture"],
    img: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e04d62ce228628f8d55aa6_CALAMIGOS_Couch.jpg",
  },
  {
    name: "Universal Monsters",
    tags: ["Apparel"],
    img: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e04d72099ad02396a2eed5_Universal_Studios_Monsters_Collab.jpg",
  },
  {
    name: "Desert International Horse Park",
    tags: ["Home Decor"],
    img: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e04d7cf3b0bdd7c847f968_Dessert%20International%20Horse%20Park_Collab.jpg",
  },
  {
    name: "Shred Cycle",
    tags: ["Transportation"],
    img: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e04f002d91b9e48865ea3a_Shred%20Cycle_Collab.jpg",
  },
  {
    name: "Prism",
    tags: ["Footwear"],
    img: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e04f7bc37ed11fd079a96d_PRISM_Collab.jpg",
  },
  {
    name: "Rhude",
    tags: ["Accessories"],
    img: "https://cdn.prod.website-files.com/689fdd2ce6036517904752cd/68e0522938047ab7144e79d5_68a7c6d438b7ca10c9ae2577_a9eb6205fb5d3376c3203476da9584043a3c988c.png",
  },
];

export default function Section7Section() {
  const trackRef = useRef(null);

  return (
    <section className="clients-swiper relative w-full overflow-hidden bg-black text-white">
      {/* horizontal scroll track (Swiper free-mode reproduced as native scroll) */}
      <div
        ref={trackRef}
        className="swiper-wrapper flex w-full overflow-x-auto px-8 max-[991px]:px-6 max-[767px]:px-4"
        style={{
          scrollSnapType: "x proximity",
          scrollbarWidth: "none",
          msOverflowStyle: "none",
          gap: "24px",
        }}
      >
        {CLIENTS.map((client, i) => (
          <div
            key={i}
            role="group"
            aria-label={`${i + 1} / ${CLIENTS.length}`}
            className="client-slide shrink-0 basis-auto"
            style={{
              width: "400px",
              maxWidth: "100%",
              minWidth: "min(45vw, 400px)",
              scrollSnapAlign: "start",
            }}
          >
            <div className="client-card group relative w-full cursor-pointer rounded-[12px] bg-white pt-[20px] pl-[20px] pr-[20px] pb-[46px] max-[991px]:rounded-[8px] max-[991px]:p-[12px] max-[991px]:pb-[38px] xl:pt-[24px] xl:pl-[24px] xl:pr-[24px]">
              <div className="client-card-wrapper flex flex-col gap-[20px] xl:gap-[24px]">
                {/* tags */}
                <div className="collection-list-2 flex gap-[8px]">
                  {client.tags.map((tag, t) => (
                    <div
                      key={t}
                      className="client-tag flex h-[36px] items-center justify-center rounded-[8px] border border-[#cccac8] px-[12px] max-[991px]:h-[36px] max-[767px]:h-[30px]"
                    >
                      <p className="client-tag-text m-0 flex items-center justify-center font-medium uppercase text-[#1a1919] leading-none max-[991px]:text-[14px]">
                        {tag}
                      </p>
                    </div>
                  ))}
                </div>

                {/* image */}
                <img
                  alt=""
                  loading="lazy"
                  src={client.img}
                  onError={(e) => {
                    e.currentTarget.style.visibility = "hidden";
                  }}
                  className="client-image w-full rounded-[12px] object-cover max-[991px]:rounded-[8px]"
                  style={{ aspectRatio: "538 / 346", objectPosition: "50% 50%" }}
                />

                {/* name */}
                <div>
                  <h2 className="client-name m-0 font-light text-[#1a1919]"
                    style={{
                      fontSize: "clamp(30px, 4vw, 52px)",
                      lineHeight: "80%",
                    }}
                  >
                    {client.name}
                  </h2>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* scrollbar pagination (hidden under 991px per css) */}
      <div className="clients-pagination-container relative mx-auto mt-[60px] w-[78.5%] max-[991px]:hidden xl:mt-[80px]">
        <div className="clients-pagination h-[6px] w-full overflow-hidden rounded-[10px] bg-white/10">
          <div
            className="swiper-scrollbar-drag h-full rounded-[10px] bg-white/50"
            style={{ width: "240px" }}
          />
        </div>
      </div>

      {/* title */}
      <p
        className="collaborators-title m-0 pt-[18px] pb-[18px] text-center font-light text-[#b2b1af]"
        style={{ fontSize: "clamp(20px, 1.6vw, 24px)" }}
      >
        In collaboration with
      </p>
    </section>
  );
}
