# 《纳米材料制备实验》课程论文 · 工程说明

本目录是本课程论文的完整可复现工程：正文（LaTeX）、插图（由原始数据重绘）、分析脚本与定量结果表。

## 1. 目录结构

```text
课程论文/
├─ main.tex                  # 主文件（ctexart + twocolumn，标题条与模板同版式）
├─ ref.bib                   # 参考文献（biblatex gb7714-2015，10 条）
├─ builtin/                  # 模板内建宏（封面、页眉、标题、摘要等）
├─ config/configure.tex      # 题目、关键词、作者信息
├─ content/
│  ├─ abstract.tex           # 摘要
│  ├─ body.tex               # 汇总各节
│  └─ body/                  # 01 引言、02 方法、03 结果、04 结论、05 致谢
├─ figures/                  # 图 1—图 10（pdf 矢量 + png 预览）
├─ analysis/
│  ├─ data/                  # 解压后的原始数据（运行 extract_data.ps1 生成，不入库）
│  ├─ scripts/               # 数据处理与作图脚本（含 extract_data.ps1）
│  └─ outputs/               # 中间结果 CSV、分割校验图
├─ complie.bat / complie.sh  # 一键编译（xelatex + biber）
└─ 交付/                     # 最终 PDF（按提交要求命名）
```

## 1.1 复现步骤

```bat
cd 课程论文\analysis\scripts
powershell -ExecutionPolicy Bypass -File extract_data.ps1   :: 从各实验 zip 解压数据
python xrd.py && python raman.py && python uvvis.py
python sem.py && python eds.py && python fig1_flow.py
cd ..\..
complie.bat main.tex
```

（脚本只依赖 numpy、matplotlib、scipy、opencv-python、scikit-image。）

## 2. 编译方法

```bat
cd 课程论文
complie.bat main.tex
```

等价命令（本机 TeX Live 位于 `E:\latex_AI\TexLive\bin\windows`）：

```bat
xelatex -interaction=nonstopmode main.tex
biber main
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

> 注意：本机用户名含中文，biber 需把 `TMP`/`TEMP` 指向纯 ASCII 目录（如 `E:\latex_AI\.texbuild`），否则会报 `Can't call method "binmode"`。

## 3. 图表与脚本对应关系

| 图/表 | 生成脚本 | 关键输出 |
|---|---|---|
| 图 1 工艺流程图 | `fig1_flow.py` | `figures/fig1_flow.pdf` |
| 图 2 XRD 堆叠图 | `xrd.py` | `figures/fig2_xrd_stack.*` |
| 图 3 晶粒尺寸/金红石含量 | `xrd.py` | `fig3_xrd_quant.*`、`outputs/xrd_peaks.csv` |
| 图 4 四组重复性 | `xrd.py` | `fig4_xrd_groups.*` |
| 图 5 拉曼谱 | `raman.py` | `fig5_raman.*`、`outputs/raman_peaks.csv` |
| 图 6 SEM 形貌 | `sem.py` | `fig6_sem.*` |
| 图 7 粒径分布 | `sem.py` | `fig7_sem_hist.*`、`outputs/sem_sizes.csv` |
| 图 8 EDS 谱 | `eds.py` | `fig8_eds.*`、`outputs/eds_ratio.csv` |
| 图 9 吸收光谱 | `uvvis.py` | `fig9_uvvis.*` |
| 图 10 Tauc 曲线 | `uvvis.py` | `fig10_tauc.*`、`outputs/uvvis_eg.csv` |

运行顺序：`xrd.py` → `raman.py` → `uvvis.py` → `sem.py` → `eds.py` → `fig1_flow.py`（均只需 Python 3 + numpy/matplotlib/scipy/opencv/scikit-image）。

## 4. 数据来源与取舍

| 数据 | 来源 | 说明 |
|---|---|---|
| XRD 温度序列 | 第六组（主）、第一/三/五组（对比） | 统一截取 20°—80°；同一温度存在重复文件时取非补零命名者 |
| 拉曼 | 九组共享谱库中文件名含 TiO$_2$ 与温度标识者 | 仅使用 100—1000 cm$^{-1}$ 且信噪比可辨的 6 条谱 |
| SEM | 第五组 `200/300/500/700/900` 与 `spin` 样品 | 标尺由元数据 `PixelSize` 换算 |
| EDS | 第五组 `500.txt`、`900.txt` | 仅作定性成分确认（计数率低，未定量） |
| UV-Vis | 第四组 `tio2-400…800` | 900 ℃ 数据基线未归零，已剔除 |

## 5. 已知局限（论文 3.6 节已讨论）

- Scherrer 公式未扣除仪器宽化与应变，晶粒尺寸为表观下限；
- 金红石含量用单对衍射峰直接对比法，未做 Rietveld 精修；
- SEM 粒径为半自动分割统计（`outputs/sem_overlay_*.png` 可核查），对粘连颗粒存在 ±10%—15% 误差；
- Tauc 线性区选择带有主观性，$E_g$ 不确定度约 ±0.05 eV。

## 6. 自查记录

- 正文（不含摘要/图表题注/参考文献）中文约 5100 字，满足 ≥3000 字要求；
- 与课程讲义原文的 13 字连续片段重合率为 0%（`analysis/scripts/overlap_check.py`）；
- 参考文献 10 条，正文按 `[n]` 顺序引用，题录均可核实。
