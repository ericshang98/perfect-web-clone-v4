# 复刻过程全记录 — everswap.com (2026-06-30)

目的：真复刻 https://everswap.com，**全程记录每一步**，标出哪一步没达到标准，反推架构优化点。
驱动方式：pwc4 MCP server 本会话掉线 → 直接用 `.venv` 跑 `core/` 确定性模块（与 MCP 背后同一套代码）；"大脑"部分（逐 section 写 JSX）由子代理完成。

每个 Phase 记三件事：**标准是什么 / 实际发生 / 是否达标 + 架构优化建议**。

---

## Phase 0 — 框定任务
- 目标 URL：https://everswap.com（DeFi 站，title "EverSwap - Trade, Lend, Borrow."）
- 范围：整页克隆，默认本地 dist，不部署。
- 预探：HTTP 200，44KB HTML，仅 1 个 `<script>`，无 `#root/#app/#__next` 挂载点 → 初判偏静态落地页（待 extract 确认）。

---

## Phase 1 — 抓取 (Layer 0 ground truth)
**标准**：抓全 DOM + 计算样式 + 资产 + 参考 raster；触发懒加载、关弹窗；参考 raster 必须是"网站真实长相"。

**实际**：
- source_id `everswap.com-1782793167-835ba6`，title 正确（非软-404）。
- DOM 有真实内容：438 元素、958 字文案（"DeFi at Peak"/"Scroll to start"/"One Pool — Swap. Lend. Borrow."/"EverSwap unifies trading, lending, and borrowing…"/"Made for EVERyone"）。4 图 / 5 字体 / 1 CSS。脚本 0/2 下载。
- **但参考 raster 几乎全空**：全页截图 13275px 高，只有顶部一屏 hero（绿山+蓝天+极小 logo+左侧竖字）画出来了，下面 ~12000px 全白。
- **"Scroll to start" + opacity:0 元素=0** → everswap 是**滚动编排动画站**（内容靠滚动逐屏揭示/位移，静止态被 transform 推到屏外）。

**❌ 没达标 — 3 个架构缺口：**
1. **滚动编排站 = 空 raster**：单张静态截图无法表达"随滚动揭示"的站。与 oryzo 同类天花板。ground truth 本身失真 → 下游 fidelity 无意义。
   - 架构建议：capture 阶段需识别 scroll-driven 站（探测 GSAP ScrollTrigger / Lenis / `data-scroll` / pin），并**按滚动位置分段截多张 raster**（state = scroll@0%,25%,50%…），而不是一张全页图。
2. **height 指标自相矛盾**：summary `page_height=900`，实际 raster 13275px。指标不可信。
   - 架构建议：page_height 应取实际 `scrollHeight`，并与 raster 高度做一致性断言。
3. **0/2 脚本捕获**：与审计"无交互层"一致；滚动动画逻辑完全丢失。
   - 架构建议：至少识别驱动动画的脚本/库并登记为 residual，别静默丢。

---

## Phase 2 — section plan
**标准**：按真实 `#main` 子节点切段，每段带数值 bounds。
**实际**：8 段（section/section-2..6/footer/navigation），名字全是泛化占位名；**bounds 8/8 全空**。
**❌ 没达标**：bounds 仍未落数（第 3 个站复现）。泛化命名说明切段对这类非语义结构站只能给占位名。

## Phase 3 — assemble shell
**标准**：写共享文件 + 注入去重全局 cleaned CSS，sections 渲染时已带样式。
**实际**：shell 建成（App.jsx 按序 import 8 段；main.jsx；index.css）。全局 theme CSS = `public/theme.css`(22KB) + index.html `<link>`，字体已本地化。
**🟡 部分达标 + 文档过时**：机制 OK，但 SKILL.md 写的是"注入 index.css"，实际是 public/theme.css（commit 36f2f54 改的）。**文档与实现不一致，需更新。**

## Phase 4 — 逐 section 写组件（大脑）
**标准（SKILL 原文）**：子代理从"DOM 子树 + 计算样式 + **css_rules** + geometry + 内容 + **asset refs**"写干净 JSX；绝不粘原始标记。
**实际**：`get_section_data` 对 8 段**只返回 `raw_html` + name/tag/classes/section_type**——**没有 css_rules、没有 images/assets、没有 bounds、没有 computed styles**。
**❌ 最严重的架构-文档断层**：工具根本不给"干净写作"所需的数据。子代理只能①粘 HTML（违反 clean）或②靠 class 猜全局 CSS。这解释了为何能跑通的 dorro/pagerie 走的是另一条路（cleaned `dangerouslySetInnerHTML` + 全局 union CSS），而非 SKILL 描述的"从 css_rules 写本地样式"。
**另两个 Phase-4 缺口**：
- 抓到的 HTML 带**动画冻结 inline 样式**（`opacity:0`/`display:none !important`/`blur`/`translate3d`）——hero 标题"EverSwap"是 display:none。无任何 flag 区分"动画临时态" vs "故意隐藏"。直接粘 = 内容隐形。
- hero 主视觉（山脉）是 **canvas/JS 绘制**，不是可本地化资产（只抓到 favicon+ogimage 4 张）。

## Phase 5 — build（硬 gate）
**实际**：`npm run build` rc=0，dist 产出（js 167KB/gz 50KB，css 5.6KB，theme.css 22KB）。**✓ 达标**。

## Phase 6 — gates
- **fingerprint**：total=0，**✓**（非 shopify 站，且清洗干净）。
- **weight**：ok=false，238KB > 120 预算。但拆分：**代码 js49+css6≈55KB 在 50–80KB 目标内**；超标全在 assets 180KB（ogimage 124KB + 5 字体）。**❌ 单一合并预算误判**（审计 #6：应分"代码预算"与"内容图预算"）。
- **fidelity**：**无法运行/无意义**——Phase-1 参考 raster 几乎全空 + bounds 空。指标对这站等于零信息。

## Phase 7 — deliver（实物）
**实际**：克隆页渲染出全部**文字内容**，但视觉**破碎**——文字极小极淡、布局被 `position:static` 拍平、山脉主视觉缺失、底部残留几个绿块。height 19436px。
**❌ 视觉没达标**：去动画化无法重建"活在 JS 动画层里的设计"。**确认天花板：canvas + 滚动编排站，内容可抓、长相不可复刻。**

---

## 总判定
everswap 属于**最难一类**（canvas 主视觉 + 滚动编排布局，同 oryzo）。流程结果：
- build ✓ / fingerprint ✓ / 代码体积 ✓
- **视觉 fidelity ✗（本质性）**：参考 raster 本身就是空的，设计在 JS 里，静态拼不出。

## 反推的架构优化清单（按价值排序）
1. **【capture】站点类型预分类 + 前置告知天花板**：clone 前先分类（静态 / Shopify店 / SPA内容 / 滚动编排 / WebGL-canvas），对滚动/canvas 站**提前告诉用户"只能静态骨架、长相还原不了"**，别承诺 pixel-perfect。
2. **【capture】滚动站多态 raster**：识别 GSAP/Lenis/pin，按 scroll@0/25/50/75/100% 截多张，而非一张全页空白图。
3. **【get_section_data】必须补齐 css_rules + 解析后的图片 src + bounds + computed styles** —— 否则 SKILL 描述的"干净写作"recipe 在工具层根本不成立（最大断层）。
4. **【section数据】动画态归一化**：剥离/标记 `opacity:0 / display:none / transform / blur` 等临时 inline 样式，并给 `hidden_reason` flag。
5. **【plan】bounds 落数**（3 个站连续全空）——解锁 self-heal 定位 + 逐段 fidelity。
6. **【weight gate】拆分预算**：代码预算 vs 内容图预算，别用单一合并值误判图重站。
7. **【height 指标】**取真实 scrollHeight 并与 raster 高度断言一致。
8. **【文档】**SKILL.md 全局 CSS 落点（index.css→public/theme.css）等已与实现脱节，需同步。
9. **【capture】canvas/WebGL 主视觉**至少登记为 residual（截一张静态帧当占位图也行），别静默丢主视觉。
