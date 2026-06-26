# Perfect Web Clone v4 — 指导思想与交付战略

> **这份文档怎么读：** 它按**变化速度分层**。越上面越稳定（是框架的世界观），越下面越易变
> （是当下的战线）。每次遇到新问题，写进**第 3 层**，并蒸馏出它教会的原则；若是新原则，升到
> **第 0 层**；若是新决策，记进**第 2 层（只增不改）**。这样它才是"指导思想"，而不是杂物抽屉。

---

## ★ 北极星（一句话）

> **每一个要求，都必须先变成一个确定性的、带证据的门禁（gate），然后才去满足它——
> 绝不靠"我觉得还原得挺好"。**

整个框架——以及本文件每一个决策——都是这句话的产物。下面四根支柱是它的展开。

---

## 第 0 层 · 指导思想（几乎不变）

### 支柱 1 — 门禁化一切（Gate everything）
每个要求都翻译成一个**确定性的 pass/fail + 证据**的门禁，判断绝不靠肉眼或"子 Agent 的自觉"。
> *教训来源：* v3 的交付被技术审挂掉，正是因为"代码干净"全靠子 Agent 自觉、从没被测过——
> 残留 70 处 shopify、225KB 内联 CSS 没人拦。门禁化就是不让"自觉"成为质量的依赖项。

### 支柱 2 — 解耦 clean 与 fidelity（Decouple into two layers）
"**干净**"在上游用我们自己的词汇 / design token **出生**；"**保真**"在下游用 SSIM 对基准图
**度量**。两个目标分属不同层，**永不在同一产物上打架**。
> *教训来源：* v3 把保真和干净压在同一份"真实 HTML+critical CSS"上，于是最快的保真方式就是
> 粘原始 Shopify 标记，干净只能事后清、永远清不净。解耦从根上解决这个矛盾。

### 支柱 3 — 闭环必然收敛（Convergence by construction）
渲染是**多对一**的：无数份不同的干净源能渲染出同一张像素图，所以"渲染像素相同的干净源"
**可证明存在**。于是 `生成 → 度量 → 修最差区 → 再度量` 是一个**有目标的封闭搜索**，必然收敛——
开放式合成被降级成封闭式搜索。
> *推论：* 不需要一个完美的一次性逆变器，只需要一个会朝着已知靶心收敛的循环。

### 支柱 4 — 确定性的手，唯一的脑（LLM-free hands, one brain）
Layer 0–3 与所有门禁是**纯 Python，从不调模型**：抓取、分段、组装、构建、截图、扫描、度量、
打分。Claude Code 只在**一个地方**当脑——拿着「一个 gate 失败 + 定位到的区域 + 出问题的节点」，
决定**怎么修这一个组件**。判断的表面积被压到最小、最高价值的那一点。

### 一条铁律（贯穿四柱）
**残留长尾（bespoke JS / WebGL / canvas）永远显式标注，绝不静默丢弃。** 门禁化的反面不是
"假装全过了"，而是诚实地报告哪条没过、差多少。

---

## 第 1 层 · 交付契约（项目周期内稳定）

**交付载体**：用户在自己的 Claude Code / Codex 里当 **skill** 跑（最佳质量、成本仅订阅费）。
交付物 = **skill（`skill/SKILL.md`）+ `pwc4` MCP 服务器 + 非程序员可照做的安装/使用说明**。
不是逐页代做。**产出** = 粘贴 URL → 干净 standalone 的 Vite+React+Tailwind 项目（本地 `dist/`，
**默认不部署**）。

### 九个验收门禁（定义稳定；右栏现状随时变）

| # | 门禁 | 标准 | 现状 |
|---|---|---|---|
| R1 | 指纹 `fingerprint_gate` | `dist/` 内 0 处 `shopify`/`template--…__`/`original.css` 等 | ✅ 0 |
| R2 | 干净代码 `cleanliness_gate` | 无内联裸 CSS dump；一段一组件；可读可改 | ✅ |
| R3 | 体积 `weight_gate` | **代码** ≈50–80KB gz（内容图与代码分开计） | ✅ 82KB |
| R4 | 像素级 `fidelity_gate` | 各断点 × 关键态 SSIM ≥ τ | ⚠️ 0.30* |
| R5 | 明显更优 `comparison_gate` | 与旧 repo 并排「明显更好」 | ✅ M1 |
| R6 | sticky 跟随滚动 | 滚动态截图里 sticky 仍被钉住 | 待修 |
| R7 | footer 完整 | footer 区域 SSIM ≥ τ | 待修 |
| R8 | reviews 真组件 | 评论重建为数据驱动组件，非静态 PNG | 待修 |
| R9 | 视频在 | 每个源 `<video>`/embed 本地化且可播 | 待修 |

\* 全页 SSIM 0.30 的根因均可解释、可修，非「复刻错了」——见第 3 层。

**范围边界（客户原话）**：视觉保真是第一优先；**交互行为（手风琴、变体切换、倒计时）由客户
自己后期手搓**。因此工具对 R6–R9 只负责**所截关键态的视觉还原**，不负责完整的行为等价。

### 里程碑 → 付款（固定价 $4,000）
- **M1（40%）= 已完成**：单 URL「明显更好」已过、定金已到账。
- **M2（30%）= 端到端跑通**：4 个 URL 都过 `fingerprint` ∧ `weight` ∧ `fidelity ≥ τ`。
- **M3（30%，验收）**：每个 URL 并排判定「明显更好」。

**4 个验收 URL**：`reelshort.com/es` · `livora.co/…` · `kojeva.com/…` · `trykojiva.com/brush`

---

## 第 2 层 · 决策记录（判例 · 只增不改）

### 2026-06-26 — 子 Agent 分段路线扶正为默认主路径；IR→codegen 搁置
- **决策**：默认主路径 = `extract_page → get_section_plan（按 #main 子节点）→ 每段一个子 Agent
  自转干净 JSX + 局部 CSS → assemble_project → build_project → 门禁`。IR→codegen（`build_ir`/
  `run_recognizers`/`generate_code`）从 SKILL 主路径移除，保留代码、标注为长期演进。
- **证据**：真实页面 DOM ~4.6MB，过不了 MCP 上下文 → `build_ir` 不可用；`generate_code` 当前
  输出空壳。而子 Agent 路线实测拿到 **0 指纹 + 82KB gz**——证明「干净」不依赖 IR 层。
- **它是哪条原则的应用**：支柱 1（门禁化）。我们拿真站去测 IR 路径这个"门禁"——能不能在真实
  页面上同时产出 clean + fidelity？没过，于是换路。不是拍脑袋，是门禁判的。
- **对 `architecture.md` 的影响**：标注 Layer 1–3 当前由「分段 + 子 Agent 自转」承担；门禁
  （Layer 4）与可行性论证（§1）不变。

---

## 第 3 层 · 状态与路线图（日志 · 随时变）

### 当前战线
**Plan 1 已完成并通过 live 验收**（branch `feat/capture-completeness`，8 commits，TDD，full suite
231 passed + pagerie live 验收绿）。SSIM 0.30 三大根因里，**①②已在抓取层修掉**：
- ① 品牌字体：`PagerieFont-Roman.otf` + `panolight.otf` 现已被抓取本地化（之前 0）；
- ② 订阅弹窗：dismissal 强化（newsletter/dialog + 兜底 display:none）；
- 图片完整性：pagerie 抓取 **21 → 115 张**（FOUND 118 / DOWNLOADED 115，门禁 ≥80）。

剩余核心未完成 = **R4 像素级实测复跑（确认 SSIM 提升）+ R6–R9 四个硬伤 + Plans 2–4**；
根因 ③（累计纵向缩放敏感）随字体到位应自然收敛，待复跑确认。4 个验收 URL 仍需正式跑通门禁。

### 路线图（TDD 子计划 + 2 个 pipeline 洞，按收益排序）
1. **Plan 1 — 抓取完整性** ✅ **已完成**（2026-06-26）。懒加载图/`srcset`/`{width}` 模板 + 主题相对
   字体 + 关弹窗 + **静态 HTML 图片兜底抓取**（新增 Task 8：noscript/JS-gated 商品图）。纯 Python +
   单测 + live 验收。计划文件：`docs/superpowers/plans/2026-06-26-pwc4-capture-completeness.md`。
2. **Plan 2 — `assemble_project` 默认注入去重后的全局 cleaned CSS**（待写）。现在只写 `@tailwind`
   三层，纯 MCP 跑出来是无样式空白页。
3. **Plan 3 — 按 `#main` 真实子节点分段取代 chunker**（待写）；同时修订 SKILL 的 Phase 顺序
   （实测必须先 assemble 建壳再填段）。
4. **Plan 4 — 修 `check_weight` 崩溃 bug + 拆 code/asset 重量预算**（待写）。
- **洞 A**：段 `bounds` 全为空 → 自动自愈无法定位，只能人工。抓取时记录每段 bounds。
- **洞 B**：子 Agent 对 `display:none` 捕获态策略不统一 → 统一为「揭开隐藏/懒加载内容」。

### 执行节奏
Plan 1 →（补写并执行）Plan 2→3→4 + 两个洞 → 每轮在 4 个 URL 重跑门禁累积 M2 → 生成 before/after
并排图进入 M3 验收。
