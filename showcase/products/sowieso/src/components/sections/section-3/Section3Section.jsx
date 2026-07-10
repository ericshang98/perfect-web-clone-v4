// Section3Section — partner logo wall. The real site renders these 76
// payment-partner logos via a Lottie animation (runtime-drawn, not in the
// static DOM); reconstructed here as a clean, data-driven static grid from the
// captured partner assets. Heading class names are styled by public/theme.css.
const PARTNERS = [
  { src: "/assets/images/abn-amro.png", alt: "Abn Amro" },
  { src: "/assets/images/adyen.png", alt: "Adyen" },
  { src: "/assets/images/airwallex.png", alt: "Airwallex" },
  { src: "/assets/images/alipay.png", alt: "Alipay" },
  { src: "/assets/images/asn-bank.png", alt: "Asn Bank" },
  { src: "/assets/images/better-world-payments.png", alt: "Better World Payments" },
  { src: "/assets/images/bluesnap.png", alt: "Bluesnap" },
  { src: "/assets/images/bng-bank.png", alt: "Bng Bank" },
  { src: "/assets/images/bnp-paribas.png", alt: "Bnp Paribas" },
  { src: "/assets/images/boku.png", alt: "Boku" },
  { src: "/assets/images/brite.png", alt: "Brite" },
  { src: "/assets/images/buckaroo.png", alt: "Buckaroo" },
  { src: "/assets/images/bunq-black-white.png", alt: "Bunq Black White" },
  { src: "/assets/images/ccv.png", alt: "Ccv" },
  { src: "/assets/images/certo-escrow.png", alt: "Certo Escrow" },
  { src: "/assets/images/chase-paymentech.png", alt: "Chase Paymentech" },
  { src: "/assets/images/checkout-dot-com.png", alt: "Checkout . Com" },
  { src: "/assets/images/cm.png", alt: "Cm" },
  { src: "/assets/images/curo-payments.png", alt: "Curo Payments" },
  { src: "/assets/images/daopay.png", alt: "Daopay" },
  { src: "/assets/images/deutsche-bank.png", alt: "Deutsche Bank" },
  { src: "/assets/images/ease2pay.png", alt: "Ease2Pay" },
  { src: "/assets/images/ecommbx.png", alt: "Ecommbx" },
  { src: "/assets/images/embed.png", alt: "Embed" },
  { src: "/assets/images/finby.png", alt: "Finby" },
  { src: "/assets/images/first-data-fiserv.png", alt: "First Data Fiserv" },
  { src: "/assets/images/gocredible.png", alt: "Gocredible" },
  { src: "/assets/images/hipay.png", alt: "Hipay" },
  { src: "/assets/images/icepay.png", alt: "Icepay" },
  { src: "/assets/images/ing-bank.png", alt: "Ing Bank" },
  { src: "/assets/images/ingenico.png", alt: "Ingenico" },
  { src: "/assets/images/isbank.png", alt: "Isbank" },
  { src: "/assets/images/knab.png", alt: "Knab" },
  { src: "/assets/images/lyra.png", alt: "Lyra" },
  { src: "/assets/images/mangopay.png", alt: "Mangopay" },
  { src: "/assets/images/mollie.png", alt: "Mollie" },
  { src: "/assets/images/monext.png", alt: "Monext" },
  { src: "/assets/images/multisafepay.png", alt: "Multisafepay" },
  { src: "/assets/images/mypos.png", alt: "Mypos" },
  { src: "/assets/images/novalnet.png", alt: "Novalnet" },
  { src: "/assets/images/nuvei.png", alt: "Nuvei" },
  { src: "/assets/images/nwb-bank.png", alt: "Nwb Bank" },
  { src: "/assets/images/online-payment-platform.png", alt: "Online Payment Platform" },
  { src: "/assets/images/pay.png", alt: "Pay" },
  { src: "/assets/images/pay-dot-com.png", alt: "Pay . Com" },
  { src: "/assets/images/payabl.png", alt: "Payabl" },
  { src: "/assets/images/paycomet.png", alt: "Paycomet" },
  { src: "/assets/images/pay-fast-forward.png", alt: "Pay Fast Forward" },
  { src: "/assets/images/payone.png", alt: "Payone" },
  { src: "/assets/images/paypal.png", alt: "Paypal" },
  { src: "/assets/images/payplug.png", alt: "Payplug" },
  { src: "/assets/images/paypro.png", alt: "Paypro" },
  { src: "/assets/images/paysafe.png", alt: "Paysafe" },
  { src: "/assets/images/pingpong.png", alt: "Pingpong" },
  { src: "/assets/images/pprop.png", alt: "Pprop" },
  { src: "/assets/images/rabobank-logo.png", alt: "Rabobank Logo" },
  { src: "/assets/images/rootline.png", alt: "Rootline" },
  { src: "/assets/images/shift4.png", alt: "Shift4" },
  { src: "/assets/images/sibs-pagamentos.png", alt: "Sibs Pagamentos" },
  { src: "/assets/images/stripe.png", alt: "Stripe" },
  { src: "/assets/images/sumup.png", alt: "Sumup" },
  { src: "/assets/images/takeaway.png", alt: "Takeaway" },
  { src: "/assets/images/thunes.png", alt: "Thunes" },
  { src: "/assets/images/trust-payments.png", alt: "Trust Payments" },
  { src: "/assets/images/trustly.png", alt: "Trustly" },
  { src: "/assets/images/unified-post-payments.png", alt: "Unified Post Payments" },
  { src: "/assets/images/unlimit.png", alt: "Unlimit" },
  { src: "/assets/images/unzer.png", alt: "Unzer" },
  { src: "/assets/images/viva-wallet.png", alt: "Viva Wallet" },
  { src: "/assets/images/windcave.png", alt: "Windcave" },
  { src: "/assets/images/worldline.png", alt: "Worldline" },
  { src: "/assets/images/worldpay.png", alt: "Worldpay" },
  { src: "/assets/images/xplor.png", alt: "Xplor" },
  { src: "/assets/images/yabandpay.png", alt: "Yabandpay" },
  { src: "/assets/images/yoursafe.png", alt: "Yoursafe" },
  { src: "/assets/images/zen.png", alt: "Zen" }
];

export default function Section3Section() {
  return (
    <section className="partners-section" id="psp-partners">
      <div className="partners-section__title-container">
        <p className="partners-section__top-title">Always available with all our partners</p>
        <h2 className="partners-section__title">READY FOR<br />A GREAT<br />FUTURE</h2>
      </div>
      <div className="mx-auto grid max-w-6xl grid-cols-3 gap-3 px-4 py-10 sm:grid-cols-4 md:grid-cols-6">
        {PARTNERS.map((p) => (
          <div
            key={p.src}
            className="flex aspect-[3/2] items-center justify-center rounded-xl bg-white p-4 shadow-sm"
          >
            <img src={p.src} alt={p.alt} loading="lazy" className="max-h-10 max-w-full object-contain" />
          </div>
        ))}
      </div>
    </section>
  );
}
