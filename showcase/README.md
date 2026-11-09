# Perfect Web Clone v4 · Showcase

这个目录是 Harness 的复刻合集。Harness 是一整套给 Agent 的工作流：Agent 是脑，`pwc4` 的确定性工具是手。接上之后，对 Agent 说 `复刻 <url>`，它会抓取、分段、写成干净的 Vite + React + Tailwind 页面，再按区块度量并修补。

开源介绍、对照图和每一条视频的入口都在仓库根目录的 `README.md`。视频文件在 `videos/`，由真实整页截图滚出来。左右对照只在原站和复刻都有可用光栅时才做。

## 接入

仓库根目录的 `README.md` 写了 Python 安装。`.mcp.json` 注册名为 `pwc4` 的 stdio 服务。流程合同在 `skill/SKILL.md`。

## 跑某一个克隆

克隆用绝对路径 `/assets/...`，必须在它自己的目录当服务器根：

```bash
cd products/reelshort
npm install
npm run preview
```

`cineshader` 和 `oryzo-pixel` 是单文件，直接打开 `index.html`。

## 这份合集里有什么

17 个站点，20 个可运行构建。四份 v4 交付账（ReelShort 0.931、Livora 0.748、Kojeva 0.762、TryKojiva 0.7204）记在 `../delivery/four-reference-sites.md`。那份账用的视觉阈值是 0.72。仓库默认视觉门是 0.97。终端状态是 `ready_for_user_review` 或 `failed_with_residuals`。

获奖站点里，vshslv 有原站 / 复刻并排。Infinite Passerella、ORYZO、CineShader、Everswap 的奖项写在页面上。WebGL 原站没有画实的那一帧，不做假对照。

本目录只做展示，不部署这些克隆。
