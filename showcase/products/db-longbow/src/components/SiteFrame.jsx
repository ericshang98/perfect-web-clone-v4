export default function SiteFrame() {
  return (
    <>
      <div data-name="main-child" className="container container--lines" style={{ 'display': 'flex' }}>
        <div className="vertical-lines">
          <div className="vertical-line"></div>
          <div className="vertical-line vertical-line--25"></div>
          <div className="vertical-line vertical-line--33" style={{ 'display': 'none !important' }}></div>
          <div className="vertical-line vertical-line--50"></div>
          <div className="vertical-line vertical-line--66" style={{ 'display': 'none !important' }}></div>
          <div className="vertical-line vertical-line--75"></div>
          <div className="vertical-line vertical-line--100"></div>
        </div>
      </div>
    </>
  );
}
