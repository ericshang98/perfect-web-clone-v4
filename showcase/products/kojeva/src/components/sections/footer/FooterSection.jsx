const footerLinks = [
  ["Contact Us", "https://kojeva.com/pages/contact"],
  ["Track Your Order", "https://kojeva.com/apps/parcelpanel"],
  ["Privacy Policy", "https://kojeva.com/policies/privacy-policy"],
  ["Return and Refund Policy", "https://kojeva.com/policies/refund-policy"],
  ["Shipping Policy", "https://kojeva.com/policies/shipping-policy"],
  ["Terms of Service", "https://kojeva.com/policies/terms-of-service"],
  ["Billing Terms and Conditions", "https://kojeva.com/pages/billing-terms-and-condition"],
];

export default function FooterSection() {
  return (
    <footer className="site-footer">
      <div className="footer-grid">
        <a href="https://kojeva.com/" className="footer-logo"><img src="/assets/images/Kojeva_Logo.png" alt="Kojeva" /></a>
        <div className="footer-links">
          <h2>Quick links</h2>
          {footerLinks.map(([label, href]) => <a href={href} key={href}>{label}</a>)}
        </div>
        <div className="store-info">
          <h2>Store Information</h2>
          <p>Customer Support : 9:00 am to 5:00 pm</p>
          <p>Address: Oklahoma, United States</p>
          <p>Phone: (918) 921-1596</p>
          <p>Email: support@kojeva.com</p>
        </div>
      </div>
      <div className="subscribe">
        <h2>Subscribe to our emails</h2>
        <label><span className="sr-only">Email</span><input type="email" placeholder="Email" /><button type="button" aria-label="Subscribe">→</button></label>
      </div>
    </footer>
  );
}
