# -*- coding: utf-8 -*-
"""把 11 个 MinerU markdown 中的图片排成 A4 横向图册（仅图 + 章节标签）"""
import os, re, html, argparse

ROOT = r"E:\latex_AI\波谱分析"
IMGDIR = os.path.join(ROOT, "images")
IMG_RE = re.compile(r'^\s*!\[[^\]]*\]\((https?://[^)]+)\)\s*$')
ORDER = [("第一章_绪论", "第一章 绪论"), ("第二节_波谱解析的主要内容", "第一章 第二节 波谱解析的主要内容"),
         ("第二章_紫外光谱-1", "第二章 紫外光谱 ①基本原理"), ("第二章_紫外光谱-2", "第二章 紫外光谱 ②结构与关系"),
         ("第二章_紫外光谱-3", "第二章 紫外光谱 ③应用与实例"), ("第三章_红外光谱-1", "第三章 红外光谱 ①基本原理"),
         ("第三章_红外光谱-2", "第三章 红外光谱 ②特征基团"), ("第三章_红外光谱-3", "第三章 红外光谱 ③解析实例"),
         ("第四章_氢核磁共振谱-1", "第四章 氢谱 ①基本理论"), ("第四章_氢核磁共振谱-2", "第四章 氢谱 ②主要参数"),
         ("第四章_氢核磁共振谱-3", "第四章 氢谱 ③测定技术"), ("第四章_氢核磁共振谱-4", "第四章 氢谱 ④结构鉴定应用")]


def collect(minpx):
    fs = [f for f in os.listdir(ROOT) if f.startswith("MinerU_markdown_") and f.endswith(".md")]
    out = []
    for key, title in ORDER:
        cand = [f for f in fs if key in f]
        if not cand:
            continue
        p = os.path.join(ROOT, cand[0])
        cells, sec, idx = [], title, 0
        recent = []
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                s = line.strip()
                if not s:
                    continue
                m = IMG_RE.match(line)
                if not m:
                    if s.startswith("<table") or s.startswith("<img") or s.startswith("$$"):
                        continue
                    t = re.sub(r'^#+\s*', '', s)
                    t = re.sub(r'[$\\{}]', '', t).strip()
                    if t:
                        recent.append(t[:70])
                        recent = recent[-2:]
                    continue
                b = os.path.basename(m.group(1).split("?")[0])
                fp = os.path.join(IMGDIR, b)
                if not os.path.isfile(fp):
                    continue
                idx += 1
                cap = " ／ ".join(recent) if recent else sec
                cells.append((fp, cap[-96:], idx))
        out.append((title, cells))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-page", type=int, default=6)
    ap.add_argument("--out", default=os.path.join(ROOT, "PPT图册.html"))
    a = ap.parse_args()
    data = collect(0)
    cols = {4: 4, 6: 3, 8: 4, 9: 3}.get(a.per_page, 3)
    rows_per_page = a.per_page // cols
    maxh = {4: 62, 6: 47, 8: 40, 9: 34}.get(a.per_page, 45)

    parts = [f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>波谱分析 PPT 图册</title><style>
@page {{ size:A4 landscape; margin:7mm 7mm 6mm 7mm; }}
*{{box-sizing:border-box}}
body{{font-family:"Microsoft YaHei";margin:0;font-size:7pt;color:#111}}
.sec{{page-break-before:always;page-break-after:avoid;background:#1f3864;color:#fff;
     font-size:11pt;font-weight:700;padding:1.2mm 3mm;margin:0 0 2mm 0;letter-spacing:.5pt}}
.sec.first{{page-break-before:auto}}
.grid{{display:grid;grid-template-columns:repeat({cols},1fr);gap:2mm}}
.cell{{border:0.4pt solid #9aa3b2;padding:1mm;display:flex;flex-direction:column;
      page-break-inside:avoid;break-inside:avoid;height:{maxh + 14}mm}}
.imgbox{{flex:1;display:flex;align-items:center;justify-content:center;overflow:hidden}}
.imgbox img{{max-width:100%;max-height:{maxh}mm;object-fit:contain}}
.cap{{font-size:5.4pt;color:#333;margin-top:0.8mm;line-height:1.15;
     height:12mm;overflow:hidden;border-top:0.3pt solid #ccd}}
.cap b{{color:#1f3864}}
.cap{{font-size:5.2pt;color:#222;margin-top:0.8mm;line-height:1.15;
     height:13mm;overflow:hidden;border-top:0.3pt solid #ccd}}
</style></head><body>"""]
    total = 0
    for si, (title, cells) in enumerate(data):
        cls = "sec first" if si == 0 else "sec"
        parts.append(f'<div class="{cls}">{html.escape(title)}　<span style="font-size:7.5pt;font-weight:400">（{len(cells)} 图）</span></div>')
        parts.append('<div class="grid">')
        for fp, sec, idx in cells:
            total += 1
            parts.append(
                f'<div class="cell"><div class="imgbox"><img src="{html.escape(fp)}"></div>'
                f'<div class="cap"><b>#{idx}</b> {html.escape(sec)}</div></div>')
        parts.append("</div>")
    parts.append("</body></html>")
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    print(f"图片 {total} 张，{a.per_page}/页 → 理论 {-(-total // a.per_page) + len(data)} 页左右")
    print("写出:", a.out)


if __name__ == "__main__":
    main()
