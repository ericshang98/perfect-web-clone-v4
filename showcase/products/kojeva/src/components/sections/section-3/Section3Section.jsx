const statistics = [
  ["96% of", "Customers saw visible de-puffing after one use (~90 seconds)."],
  ["91% of", "Reported a more defined jawline/cheekbones within 1 week of daily use."],
  ["86% of", "Said it’s easier and gentler than tools with oils—quick, non-messy, A.M. friendly."],
];

export default function Section3Section() {
  return (
    <section className="satisfaction-section">
      <div className="satisfaction-card">
        <div className="satisfaction-title">
          <h2>satisfaction<br /><span>you can trust.</span></h2>
          <p>We have the data to prove our product works.</p>
        </div>
        <div className="statistics">
          {statistics.map(([value, text]) => (
            <div className="stat-row" key={value}>
              <strong>{value}</strong><p>{text}</p>
            </div>
          ))}
          <div className="study-note"><span aria-hidden="true">●</span> * Based on internal studies and customer<br />feedback surveys.</div>
        </div>
      </div>
    </section>
  );
}
