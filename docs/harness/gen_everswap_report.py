#!/usr/bin/env python3
"""Generate a single self-contained HTML report (embedded base64 images) of the
everswap clone result + architecture-optimization points. Chinese, non-technical-friendly."""
import base64, io
from pathlib import Path
from PIL import Image

ROOT = Path("/Users/eric/AI_development/perfect-web-clone-v4")
OUT = ROOT / "docs/everswap-clone-report.html"

def b64(path, max_w, crop_h=None, q=72):
    im = Image.open(path).convert("RGB")
    if crop_h:
        im = im.crop((0, 0, im.width, min(crop_h, im.height)))
    if im.width > max_w:
        im = im.resize((max_w, int(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=q)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

EVER_REF = b64(ROOT/"core/extractor/_sources/everswap.com-1782793167-835ba6/screenshots/primary_full.png", 300)
EVER_CLONE = b64(ROOT/"docs/everswap-clone-shot.png", 300)
DORRO = b64(ROOT/"docs/dorro-sidebyside.png", 880)
PAGERIE = b64(ROOT/"docs/pagerie-compare.png", 720)

CARDS = [
    ("P0","抓取阶段","站点类型预分类 + 提前告知天花板","复刻前先判断这是什么站（普通页 / 网店 / 滚动动画站 / WebGL站）。遇到滚动/canvas 站，<b>开工前就告诉用户「这类站只能还原内容、还原不了动效长相」</b>，不要承诺一模一样。"),
    ("P0","拿数据阶段","get_section_data 必须补齐样式数据","目前每段<b>只返回原始 HTML</b>，不给 css_rules、图片地址、坐标。导致「干净重写」这条路在工具层根本走不通——这是文档和实现最大的脱节，应优先补。"),
    ("P1","拿数据阶段","动画样式归一化","抓回的 HTML 里标题、文字常被动画临时样式（透明度0、display:none）冻成隐形。要自动剥离/标记这些临时态，否则直接用就是一片空白。"),
    ("P1","抓取阶段","滚动站多张参考图","对滚动动画站，按滚动进度截多张图（0%/25%/50%…），而不是一张几乎全白的全页图——否则「像不像」根本没法比。"),
    ("P1","切段阶段","bounds 坐标必须落数","连续 3 个站切出来的段坐标全是空的，导致自动修复定位和逐段打分全部失效。"),
    ("P2","体积检查","代码预算 / 图片预算分开","现在把图片算进代码预算，图多的站一律误报超标。应分两本账：代码 50–80KB，内容图另算。"),
    ("P2","抓取阶段","canvas/WebGL 主视觉别静默丢","主视觉是画布画的（如 everswap 的山脉）时，至少截一帧当占位图并登记，别当没看见。"),
    ("P3","指标","页面高度取真实值并自检","页面高度上报 900，实际 13275，自相矛盾。应取真实滚动高度并和截图高度对账。"),
    ("P3","文档","SKILL 文档与实现同步","文档说全局样式注入 index.css，实际已改到 public/theme.css 等多处脱节，需更新，免得误导。"),
]
PRIO = {"P0":"#dc2626","P1":"# ea580c".replace(" ",""),"P2":"#ca8a04","P3":"#0891b2"}

cards_html = "\n".join(
    f'''<div class="card"><div class="tag" style="background:{PRIO[p]}">{p}</div>
    <div class="phase">{ph}</div><h4>{t}</h4><p>{d}</p></div>''' for p,ph,t,d in CARDS)

HTML = f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EverSwap 复刻效果 + 架构优化报告</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;color:#1a2332;background:#f4f6f9;line-height:1.7}}
.wrap{{max-width:1080px;margin:0 auto;padding:48px 28px 80px}}
h1{{font-size:32px;letter-spacing:-.5px;margin-bottom:8px}}
.sub{{color:#5b6b7f;font-size:15px;margin-bottom:40px}}
h2{{font-size:22px;margin:48px 0 18px;padding-left:12px;border-left:5px solid #2563eb}}
.verdict{{background:#fff;border:1px solid #e3e8ef;border-radius:16px;padding:26px 30px;font-size:17px}}
.verdict b{{color:#dc2626}}
.grade{{display:flex;gap:18px;flex-wrap:wrap;margin:16px 0}}
.gbox{{flex:1;min-width:240px;background:#fff;border:1px solid #e3e8ef;border-radius:14px;padding:20px 22px}}
.gbox .h{{font-weight:700;font-size:16px;margin-bottom:6px;display:flex;align-items:center;gap:8px}}
.good .h{{color:#16a34a}} .bad .h{{color:#dc2626}}
.gbox p{{font-size:14px;color:#5b6b7f}}
.compare{{display:flex;gap:20px;flex-wrap:wrap;margin-top:18px}}
.shot{{background:#fff;border:1px solid #e3e8ef;border-radius:14px;padding:14px;text-align:center}}
.shot img{{max-width:100%;border-radius:8px;border:1px solid #eef1f5}}
.shot .lab{{font-weight:600;font-size:14px;margin-bottom:10px}}
.shot small{{display:block;color:#8595a8;margin-top:8px;font-size:12px}}
.tall img{{max-height:520px;width:auto}}
table{{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;font-size:14px;border:1px solid #e3e8ef}}
th,td{{padding:11px 14px;text-align:left;border-bottom:1px solid #eef1f5}}
th{{background:#f0f4f9;font-size:13px;color:#3b4a5e}}
.ok{{color:#16a34a;font-weight:700}} .no{{color:#dc2626;font-weight:700}} .mid{{color:#ca8a04;font-weight:700}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px;margin-top:8px}}
.card{{background:#fff;border:1px solid #e3e8ef;border-radius:14px;padding:18px 20px;position:relative}}
.card .tag{{position:absolute;top:16px;right:16px;color:#fff;font-size:12px;font-weight:700;padding:2px 9px;border-radius:20px}}
.card .phase{{font-size:12px;color:#8595a8;margin-bottom:4px}}
.card h4{{font-size:16px;margin-bottom:8px;padding-right:40px}}
.card p{{font-size:13.5px;color:#5b6b7f}}
.legend{{font-size:13px;color:#5b6b7f;margin:6px 0 18px}}
.legend b{{padding:1px 7px;border-radius:10px;color:#fff;margin-right:4px}}
footer{{margin-top:50px;color:#8595a8;font-size:13px;text-align:center}}
</style></head><body><div class="wrap">

<h1>EverSwap 复刻效果 + 架构优化报告</h1>
<div class="sub">复刻目标：everswap.com ｜ 日期：2026-06-30 ｜ 全流程实跑 + 逐阶段诊断</div>

<div class="verdict">
一句话结论：<b>这个站没能复刻出原样</b>。原因不是工具坏了，而是 EverSwap 属于<b>最难的一类站</b>——
主视觉（那座山）是用代码实时「画」出来的、整个页面布局靠滚动动画编排。
我们能把<b>所有文字内容</b>都抓下来，但它「动起来的样子」是静态网页复刻不了的。
（同类天花板：之前的 oryzo 也是这种。）
</div>

<h2>① 复刻效果：分场景看</h2>
<div class="grade">
  <div class="gbox good"><div class="h">✅ 擅长：网店 / 普通页面</div>
  <p>布局、产品图、配色、页脚都能对上，一眼是同一个站。这是主力场景，拿得出手。</p></div>
  <div class="gbox bad"><div class="h">⛔ 天花板：滚动动画 / WebGL 站</div>
  <p>内容抓得到，但动效编排和代码绘制的主视觉复刻不了。EverSwap、oryzo 都属此类。</p></div>
</div>

<h3 style="margin:24px 0 10px;font-size:16px">擅长场景实例（左=原站，右=复刻）</h3>
<div class="compare">
  <div class="shot"><div class="lab">Dorro 商品页（效果好）</div><img src="{DORRO}"><small>产品图 / 排版 / 页脚基本一致</small></div>
  <div class="shot"><div class="lab">Pagerie 首页（效果好）</div><img src="{PAGERIE}"><small>产品网格 / 摄影图 / 页脚复刻到位</small></div>
</div>

<h2>② 这次 EverSwap 的最终复刻效果</h2>
<div class="compare">
  <div class="shot tall"><div class="lab">原站（抓到的真实长相）</div><img src="{EVER_REF}"><small>只有顶部一屏山脉，下面全靠滚动动画才出现 → 抓到的就是大片空白</small></div>
  <div class="shot tall"><div class="lab">我们的复刻结果</div><img src="{EVER_CLONE}"><small>文字内容都在，但设计活在动画里，去掉动画后只剩碎片</small></div>
</div>
<p class="legend" style="margin-top:14px">两张都「空」，正好说明问题：原站静止时本身就是空的，设计全在滚动动画里——这不是没做好，是这类站的固有天花板。</p>

<h2>③ 全流程逐阶段：哪一步达标</h2>
<table>
<tr><th>阶段</th><th>结果</th><th>说明</th></tr>
<tr><td>抓取内容</td><td class="mid">部分</td><td>文字全抓到；但滚动站只截到一张几乎全白的图，主视觉（山）是代码画的没抓到</td></tr>
<tr><td>切分区块</td><td class="no">未达标</td><td>切了 8 段，但每段坐标全是空的（连续第 3 个站）</td></tr>
<tr><td>组装框架</td><td class="mid">基本可</td><td>框架建成、全局样式注入有效；但文档写的位置和实际已脱节</td></tr>
<tr><td>逐段写组件</td><td class="no">未达标</td><td>取数据只给原始 HTML，不给样式数据 → 「干净重写」走不通（最大问题）</td></tr>
<tr><td>构建打包</td><td class="ok">达标</td><td>npm build 通过，产物正常</td></tr>
<tr><td>指纹检查</td><td class="ok">达标</td><td>0 残留</td></tr>
<tr><td>体积检查</td><td class="no">误报</td><td>代码 ~55KB 本来达标，但图片被算进同一预算导致误报超标</td></tr>
<tr><td>像不像打分</td><td class="no">无法用</td><td>参考图本身是空的 + 坐标空 → 打分等于零信息</td></tr>
<tr><td>最终长相</td><td class="no">未达标</td><td>视觉破碎（本质性，受限于站点类型）</td></tr>
</table>

<h2>④ 架构优化点（按优先级）</h2>
<div class="legend">
<b style="background:#dc2626">P0</b>最该先修
<b style="background:#ea580c">P1</b>高
<b style="background:#ca8a04">P2</b>中
<b style="background:#0891b2">P3</b>收尾</div>
<div class="cards">{cards_html}</div>

<footer>perfect-web-clone-v4 ｜ 过程详录见 docs/clone-process-everswap.md</footer>
</div></body></html>"""

OUT.write_text(HTML, encoding="utf-8")
print("wrote", OUT, f"({OUT.stat().st_size//1024} KB)")
