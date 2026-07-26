const projects = [
  {
    slug: "naroai",
    group: "recent",
    kicker: "Gallery case · 非客户指定目标",
    title: "Naro AI · Order",
    source: "https://naroai.co/order",
    sourceLabel: "naroai.co/order",
    image: "thumbs/naroai.jpg",
    desktop: "products/naroai/shots/desktop_full.png",
    mobile: "products/naroai/shots/mobile_full.png",
    badge: "桌面整页 · hover 滚动",
    status: "系统静态与交互证据已生成，保留在 Gallery，等待用户按用途审阅。",
    tone: "review",
    tags: ["SSIM 0.992", "轮播", "颜色/数量选择", "移动端无溢出"],
  },
  {
    slug: "flipclocker",
    group: "recent",
    kicker: "Semantic comparison A/B",
    title: "FlipClocker",
    source: "https://flipclocker.com/",
    sourceLabel: "flipclocker.com",
    image: "thumbs/flipclocker.jpg",
    desktop: "products/flipclocker/shots/desktop_full.png",
    mobile: "products/flipclocker/shots/mobile_full.png",
    badge: "动态时钟 · 静态区域语义验证",
    status: "已修正深浅主题误判；动态数字只验证边界，静态区域和交互单独验证。",
    tone: "review",
    tags: ["静态区域 0.996", "动态区域豁免", "Settings", "移动菜单"],
  },
  {
    slug: "reelshort",
    group: "recent",
    kicker: "Client reference run",
    title: "ReelShort · Español",
    source: "https://www.reelshort.com/es",
    sourceLabel: "reelshort.com/es",
    image: "thumbs/reelshort.jpg",
    desktop: "products/reelshort/shots/desktop_full.png",
    compare: "products/reelshort/shots/sidebyside.png",
    badge: "完整 Hero + 内容结构",
    status: "结构完整性门禁保留了 Hero；代码、整页截图与并排证据已归档。",
    tags: ["SSIM 0.931", "89/89 静态链接", "Hero 轮播", "桌面/平板"],
  },
  {
    slug: "livora",
    group: "recent",
    kicker: "Client reference run",
    title: "Livora",
    source: "https://livora.co",
    sourceLabel: "livora.co",
    image: "thumbs/livora.jpg",
    desktop: "products/livora/shots/desktop_current.png",
    mobile: "products/livora/shots/mobile_390.png",
    compare: "products/livora/shots/sidebyside.png",
    badge: "长页面 · 桌面与移动证据",
    status: "构建、链接、资源和响应式门禁已记录；视觉结果保留给用户审阅。",
    tags: ["SSIM 0.748", "9188px 长页", "0 broken media", "390px mobile"],
  },
  {
    slug: "kojeva",
    group: "recent",
    kicker: "Client reference run",
    title: "Kojeva",
    source: "https://kojeva.com",
    sourceLabel: "kojeva.com",
    image: "thumbs/kojeva.jpg",
    desktop: "products/kojeva/shots/desktop.png",
    mobile: "products/kojeva/shots/mobile-390.png",
    compare: "products/kojeva/shots/sidebyside.png",
    badge: "质量迭代后整页",
    status: "代码、质量迭代截图、移动端和分区残差证据已归档。",
    tags: ["SSIM 0.762", "47 links", "390px mobile", "分区残差保留"],
  },
  {
    slug: "trykojiva",
    group: "recent",
    kicker: "Client reference run",
    title: "Linfae · TryKojiva",
    source: "https://trykojiva.com/brush",
    sourceLabel: "trykojiva.com/brush",
    image: "thumbs/trykojiva.jpg",
    desktop: "products/trykojiva/shots/desktop_clean.png",
    mobile: "products/trykojiva/shots/mobile_clean.png",
    compare: "products/trykojiva/shots/sidebyside_clean.png",
    badge: "干净 React 重建",
    status: "全页门槛已记录；产品内容与评论分区仍保留残差，未替用户做最终验收。",
    tone: "review",
    tags: ["全页 0.720", "分区 0.667", "0 指纹", "移动端无溢出"],
  },
  {
    slug: "oryzo",
    group: "archive",
    kicker: "Historical clone",
    title: "ORYZO",
    source: "https://oryzo.ai",
    sourceLabel: "oryzo.ai",
    image: "thumbs/oryzo.jpg",
    desktop: "products/oryzo/shots/desktop_full.png",
    mobile: "products/oryzo/shots/mobile_full.png",
    badge: "WebGL 场景编排",
    status: "历史可运行项目，保留桌面与移动整页证据。",
    tags: ["react-three-fiber", "14 scroll scenes", "GLB", "responsive"],
  },
  {
    slug: "variant3d",
    group: "archive",
    kicker: "Historical clone",
    title: "VARIANT3D",
    source: "https://variant3d.io",
    sourceLabel: "variant3d.io",
    image: "thumbs/variant3d.jpg",
    desktop: "products/variant3d/shots/desktop_full.png",
    mobile: "products/variant3d/shots/mobile_full.png",
    badge: "深色 3D 产品站",
    status: "历史可运行项目，桌面与移动证据已归档。",
    tags: ["14 sections", "self-hosted fonts", "dark UI", "responsive"],
  },
  {
    slug: "db-longbow",
    group: "archive",
    kicker: "Historical clone",
    title: "Longbow",
    source: "https://db-longbow.webflow.io",
    sourceLabel: "db-longbow.webflow.io",
    image: "thumbs/db-longbow.jpg",
    desktop: "products/db-longbow/shots/desktop_full.png",
    mobile: "products/db-longbow/shots/mobile_full.png",
    badge: "Webflow landing page",
    status: "历史可运行项目，桌面与移动证据已归档。",
    tags: ["16 sections", "self-hosted fonts", "desktop", "mobile"],
  },
  {
    slug: "withnovu",
    group: "archive",
    kicker: "Historical clone",
    title: "Novu",
    source: "https://www.withnovu.com",
    sourceLabel: "withnovu.com",
    image: "thumbs/withnovu.jpg",
    desktop: "products/withnovu/shots/desktop.jpg",
    mobile: "products/withnovu/shots/mobile.jpg",
    badge: "产品着陆页",
    status: "历史可运行项目，桌面与移动证据已归档。",
    tags: ["5 sections", "Inter + Lora", "landing page", "responsive"],
  },
  {
    slug: "pagerie",
    group: "archive",
    kicker: "Historical clone",
    title: "Pagerie",
    source: "https://www.pagerie.com",
    sourceLabel: "pagerie.com",
    image: "thumbs/pagerie.jpg",
    desktop: "products/pagerie/shots/clone-full.png",
    compare: "products/pagerie/shots/sidebyside.png",
    badge: "Shopify 奢侈宠物品牌",
    status: "历史可运行项目，整页和并排证据已归档。",
    tags: ["13 sections", "Shopify", "sticky PDP", "image gallery"],
  },
  {
    slug: "pagerie-dorro",
    group: "archive",
    kicker: "Historical clone",
    title: "Pagerie · The Dorro",
    source: "https://www.pagerie.com",
    sourceLabel: "pagerie.com",
    image: "thumbs/pagerie-dorro.jpg",
    desktop: "products/pagerie-dorro/shots/desktop_full.png",
    compare: "products/pagerie-dorro/shots/sidebyside.png",
    badge: "产品详情页",
    status: "历史可运行项目，整页和并排证据已归档。",
    tags: ["11 sections", "product gallery", "sticky details", "Shopify"],
  },
  {
    slug: "pagerie-v4",
    group: "archive",
    kicker: "Historical clone",
    title: "Pagerie · v4 Rebuild",
    source: "https://www.pagerie.com",
    sourceLabel: "pagerie.com",
    image: "thumbs/pagerie-v4.jpg",
    desktop: "products/pagerie-v4/shots/desktop_full.png",
    compare: "products/pagerie-v4/shots/compare.png",
    badge: "确定性 v4 流程重建",
    status: "历史可运行项目，整页和对比证据已归档。",
    tags: ["13 sections", "v4 pipeline", "fidelity gate", "React"],
  },
  {
    slug: "everswap",
    group: "archive",
    kicker: "Historical clone",
    title: "Everswap",
    source: "https://everswap.com",
    sourceLabel: "everswap.com",
    image: "thumbs/everswap.jpg",
    desktop: "products/everswap/shots/desktop_full.png",
    badge: "长页面复刻",
    status: "历史可运行项目，桌面整页证据已归档。",
    tags: ["8 sections", "landing page", "Vite", "React"],
  },
  {
    slug: "sowieso",
    group: "archive",
    kicker: "Historical clone",
    title: "Sowieso",
    source: "https://sowieso.wero-wallet.eu",
    sourceLabel: "sowieso.wero-wallet.eu",
    image: "thumbs/sowieso.jpg",
    desktop: "products/sowieso/shots/desktop_full.png",
    badge: "品牌长页面",
    status: "历史可运行项目，桌面整页证据已归档。",
    tags: ["11 sections", "brand site", "Vite", "React"],
  },
  {
    slug: "oryzo-pixel",
    group: "archive",
    kicker: "Historical clone",
    title: "ORYZO · Pixel",
    source: "https://oryzo.ai",
    sourceLabel: "oryzo.ai",
    image: "thumbs/oryzo-pixel.jpg",
    desktop: "products/oryzo-pixel/shots/desktop_full.png",
    badge: "无构建静态复刻",
    status: "历史静态单页，桌面证据已归档。",
    tags: ["static HTML", "pixel gate", "no build", "desktop"],
    static: true,
  },
];

const groupCopy = {
  recent: {
    title: "近期流程验证",
    description:
      "本轮 harness 与客户参考任务。自动分数只表示系统证据，不替代用户验收。",
  },
  archive: {
    title: "历史归档",
    description:
      "此前完成的复刻项目，保留可运行源码与截图，便于回看和回归。",
  },
};

const gallery = document.querySelector("#gallery");
const resultCount = document.querySelector("#result-count");
const filterButtons = [...document.querySelectorAll("[data-filter]")];

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function cardTemplate(project) {
  const secondary = project.compare
    ? `<a class="btn" href="${project.compare}" target="_blank" rel="noopener">并排对比</a>`
    : project.mobile
      ? `<a class="btn" href="${project.mobile}" target="_blank" rel="noopener">移动截图</a>`
      : "";

  const extraMobile =
    project.compare && project.mobile
      ? `<a class="btn" href="${project.mobile}" target="_blank" rel="noopener">移动截图</a>`
      : "";

  const command = project.static
    ? `open showcase/products/${project.slug}/index.html`
    : `cd showcase/products/${project.slug} && npm install && npm run dev`;

  return `
    <article class="card" data-project="${escapeHtml(project.slug)}">
      <a class="shot" href="${project.desktop}" target="_blank" rel="noopener">
        <span class="shot-badge">${escapeHtml(project.badge)}</span>
        <img
          src="${project.image}"
          alt="${escapeHtml(project.title)} 复刻整页预览"
          loading="lazy"
          decoding="async"
        />
      </a>
      <div class="card-body">
        <div class="card-kicker">${escapeHtml(project.kicker)}</div>
        <h3>${escapeHtml(project.title)}</h3>
        <a class="source" href="${project.source}" target="_blank" rel="noopener">
          ${escapeHtml(project.sourceLabel)} ↗
        </a>
        <div class="status" data-tone="${project.tone === "review" ? "review" : "evidence"}">
          <span class="status-dot" aria-hidden="true"></span>
          <span>${escapeHtml(project.status)}</span>
        </div>
        <div class="tags">
          ${project.tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}
        </div>
        <div class="actions">
          <a class="btn primary" href="${project.desktop}" target="_blank" rel="noopener">桌面整页</a>
          ${secondary}
          ${extraMobile}
          <a class="btn" href="${project.source}" target="_blank" rel="noopener">查看原站</a>
        </div>
        <div class="command">${escapeHtml(command)}</div>
      </div>
    </article>
  `;
}

function sectionTemplate(group, items) {
  return `
    <section class="section" data-section="${group}">
      <div class="section-heading">
        <h2>${groupCopy[group].title}</h2>
        <p>${groupCopy[group].description}</p>
      </div>
      <div class="grid">
        ${items.map(cardTemplate).join("")}
      </div>
    </section>
  `;
}

function render(filter = "all") {
  const groups = filter === "all" ? ["recent", "archive"] : [filter];
  const visible = projects.filter((project) => groups.includes(project.group));

  gallery.innerHTML = groups
    .map((group) => sectionTemplate(group, visible.filter((project) => project.group === group)))
    .join("");

  resultCount.textContent = `显示 ${visible.length} 个项目`;
}

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    filterButtons.forEach((item) => item.classList.remove("is-active"));
    button.classList.add("is-active");
    render(button.dataset.filter);
  });
});

document.querySelector("#project-count").textContent = projects.length;
document.querySelector("#recent-count").textContent = projects.filter(
  (project) => project.group === "recent",
).length;

render();
