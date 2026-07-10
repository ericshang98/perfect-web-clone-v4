// Section2Section — "qa" section: three centered question blocks stacked
// vertically on the yellow (#fff48d) Wero background. Each block has a small
// label, a big bold headline with one phrase inside a colored highlight box,
// and a large 3D object below it (cropped from the reference, blends on yellow).
// Pixel-matched to /tmp/pwc_sections/ref_qa.png.

const INK = '#1d1c1c';
const HL = { green: '#83f582', pink: '#fd74fd', blue: '#7af7f7' };

// Each block: label, lines (array of segments), object image + sizing.
// widths/margins are in vw (relative to the 1440px reference) so the whole
// section keeps the reference proportions at any viewport width.
const BLOCKS = [
  {
    label: 'We understand there are questions:',
    lines: [
      [{ t: 'WILL WERO' }],
      [{ t: 'BE' }],
      [{ t: 'AS RELIABLE', hl: 'green' }],
      [{ t: 'AS iDEAL?' }],
    ],
    upper: false, // keep the lowercase "i" in iDEAL
    obj: { src: '/assets/images/obj-lock.png', width: 53.5, marginTop: 0 },
    gapAfter: 38,
  },
  {
    label: 'We understand there are questions:',
    lines: [
      [{ t: 'WILL WERO BE' }],
      [{ t: 'JUST AS EASY', hl: 'pink' }, { t: ' FOR MY' }],
      [{ t: 'CUSTOMERS TO USE?' }],
    ],
    upper: true,
    obj: { src: '/assets/images/obj-clock.png', width: 54.2, marginTop: 0 },
    gapAfter: 50,
  },
  {
    label: 'We understand there are questions:',
    lines: [
      [{ t: 'ARE ' }, { t: 'ALL', hl: 'blue' }, { t: ' THE' }],
      [{ t: 'DUTCH BANKS' }],
      [{ t: 'PARTICIPATING?' }],
    ],
    upper: true,
    obj: { src: '/assets/images/obj-piggy.png', width: 54.2, marginTop: 16 },
    gapAfter: 14,
  },
];

function Highlight({ children, color }) {
  return (
    <span
      style={{
        display: 'inline-block',
        backgroundColor: HL[color],
        border: `1px solid ${INK}`,
        borderRadius: '12px',
        padding: '0 12px',
        lineHeight: 1,
      }}
    >
      {children}
    </span>
  );
}

export default function Section2Section() {
  return (
    <section
      className="faq-section"
      data-v-41ebc710=""
      style={{
        backgroundColor: '#fff48d',
        color: INK,
        fontFamily: '"GT Walsheim Wero", sans-serif',
        fontFeatureSettings: '"ss06" on',
        textAlign: 'center',
        overflow: 'hidden',
        width: '100%',
        paddingTop: '20vw',
        paddingBottom: '24vw',
      }}
    >
      {BLOCKS.map((block, bi) => (
        <div
          key={bi}
          className="faq-section__block"
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: bi < BLOCKS.length - 1 ? `${block.gapAfter}vw` : 0,
          }}
        >
          <p
            className="faq-section__top-title"
            style={{
              fontSize: 'clamp(1rem, 0.2589vw + 0.9393rem, 1.25rem)',
              fontWeight: 500,
              lineHeight: '135%',
              marginBottom: '35px',
            }}
          >
            {block.label}
          </p>

          <h2
            className="faq-section__title"
            style={{
              fontSize: 'clamp(3.875rem, 3.125vw + 1.875rem, 5.625rem)',
              fontWeight: 800,
              letterSpacing: '-2.209px',
              lineHeight: '100%',
              textTransform: block.upper ? 'uppercase' : 'none',
              maxWidth: '90vw',
            }}
          >
            {block.lines.map((segs, li) => (
              <span key={li} style={{ display: 'block' }}>
                {segs.map((s, si) =>
                  s.hl ? (
                    <Highlight key={si} color={s.hl}>
                      {s.t}
                    </Highlight>
                  ) : (
                    <span key={si}>{s.t}</span>
                  )
                )}
              </span>
            ))}
          </h2>

          <img
            className="faq-section__animation"
            src={block.obj.src}
            alt=""
            aria-hidden="true"
            style={{
              display: 'block',
              width: `${block.obj.width}vw`,
              height: 'auto',
              marginLeft: 'auto',
              marginRight: 'auto',
              marginTop: `${block.obj.marginTop}vw`,
              pointerEvents: 'none',
            }}
          />
        </div>
      ))}
    </section>
  );
}
