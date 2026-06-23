// Section6Section — faithful reproduction of the Webflow code-embed (#clients swiper script block).
// Source element: <div class="code-embed w-embed w-script" style="display: none !important;">
// It contains only a <style> + <script type="module"> (Swiper init + client-card expand interaction).
// In the rendered page this node is fully hidden (display:none) and produces no visible layout/bounds.
// We reproduce it as a hidden container so the DOM structure and z-index/stacking semantics match,
// without injecting/executing the original third-party Swiper/OverlayScrollbars scripts (which aren't
// loaded in this static clone). No images, headings, links, or text exist in the source data.

export default function Section6Section() {
  return (
    <div
      className="code-embed w-embed w-script"
      data-eapps-font-size="16"
      data-eapps-line-height="17.6"
      style={{ display: "none" }}
      aria-hidden="true"
    />
  );
}
