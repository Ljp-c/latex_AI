#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
xrd_analysis.py
===============

【注意】本脚本包含 pseudo-Voigt 峰拟合、Scherrer 晶粒尺寸、Spurr–Myers 半定量
和四方晶格参数最小二乘等**后续课程内容**，本次作业二**不使用**。作业二只使用
make_origin_ready.py（txt 格式转换）和 plot_xrd_multi.py（多曲线 + PDF 卡片绘图）。

TiO2 系列样品 XRD 数据的批量处理、峰拟合与论文图件生成。

功能
----
1. 读取仪器导出的原始 txt（或 make_origin_ready.py 生成的 ready/ 数据）；
2. ALS 扣背底 + Savitzky-Golay 平滑 + pseudo-Voigt 峰拟合；
3. 计算 FWHM、Scherrer 表观晶粒尺寸、Spurr-Myers 金红石相含量；
4. 用最小二乘（含零点偏移）精修四方晶系晶格参数 a、c；
5. 生成论文用多曲线 + PDF 卡片图、局部放大图、晶粒尺寸/相含量图；
6. 输出 CSV/JSON 以及可直接 \input 的 LaTeX 表格。

用法
----
    python .\脚本\xrd_analysis.py
    python .\脚本\xrd_analysis.py --no-figures
    python .\脚本\xrd_analysis.py --dpi 600

依赖：numpy、scipy、matplotlib（仅标准科学计算栈，无需额外安装）。
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
from scipy import sparse
from scipy.optimize import curve_fit, least_squares
from scipy.signal import savgol_filter
from scipy.sparse.linalg import spsolve

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import AutoMinorLocator, MultipleLocator

# ---------------------------------------------------------------------------
# 路径与常量
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
READY_DIR = ROOT / "资料" / "原数据" / "ready"
NORM_DIR = ROOT / "资料" / "原数据" / "ready_norm"
OUT_DIR = ROOT / "资料" / "处理后数据" / "分析结果"
PDF_DIR = ROOT / "资料" / "处理后数据" / "PDF卡片"
FIG_DIR = ROOT / "课程论文" / "assets" / "xrd"
TAB_DIR = ROOT / "课程论文" / "content" / "tables"

LAMBDA_CUKA = 1.54056  # Å
K_SCHERRER = 0.9
SPURR_CONST = 1.26  # Spurr & Myers (1957) 的锐钛矿/金红石经验常数

SAMPLES = [200, 300, 400, 500, 600, 700, 800, 900]
QUANT_SAMPLES = [300, 400, 500, 600, 700, 800, 900]  # 200 °C 仅为宽包，不纳入定量

# ---------------------------------------------------------------------------
# PDF 卡片数据（PDF 21-1272 锐钛矿；PDF 21-1276 金红石）
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PdfPeak:
    h: int
    k: int
    l: int
    two_theta: float
    intensity: float

    @property
    def hkl(self) -> str:
        return f"({self.h}{self.k}{self.l})"


ANATASE_PDF: Tuple[PdfPeak, ...] = (
    PdfPeak(1, 0, 1, 25.28, 100),
    PdfPeak(1, 0, 3, 36.95, 10),
    PdfPeak(0, 0, 4, 37.80, 20),
    PdfPeak(1, 1, 2, 38.58, 10),
    PdfPeak(2, 0, 0, 48.05, 35),
    PdfPeak(1, 0, 5, 53.89, 20),
    PdfPeak(2, 1, 1, 55.06, 20),
    PdfPeak(2, 1, 3, 62.12, 4),
    PdfPeak(2, 0, 4, 62.69, 14),
    PdfPeak(1, 1, 6, 68.76, 6),
    PdfPeak(2, 2, 0, 70.31, 6),
    PdfPeak(1, 0, 7, 74.03, 2),
    PdfPeak(2, 1, 5, 75.03, 10),
    PdfPeak(3, 0, 1, 76.02, 4),
)

RUTILE_PDF: Tuple[PdfPeak, ...] = (
    PdfPeak(1, 1, 0, 27.45, 100),
    PdfPeak(1, 0, 1, 36.09, 50),
    PdfPeak(2, 0, 0, 39.19, 8),
    PdfPeak(1, 1, 1, 41.23, 25),
    PdfPeak(2, 1, 0, 44.05, 10),
    PdfPeak(2, 1, 1, 54.32, 60),
    PdfPeak(2, 2, 0, 56.64, 20),
    PdfPeak(0, 0, 2, 62.75, 10),
    PdfPeak(3, 1, 0, 64.04, 10),
    PdfPeak(3, 0, 1, 69.01, 20),
    PdfPeak(1, 1, 2, 69.79, 12),
)

PDF_CARDS = {
    "anatase": ("Anatase TiO$_2$", "PDF 21-1272", ANATASE_PDF),
    "rutile": ("Rutile TiO$_2$", "PDF 21-1276", RUTILE_PDF),
}

# 用于晶格参数精修的反射。只取分离较好、强度足够的峰，避免重叠峰把峰位带偏。
ANATASE_LATTICE_REFS = [
    ("101", 1, 0, 1),
    ("004", 0, 0, 4),
    ("200", 2, 0, 0),
    ("204", 2, 0, 4),
    ("116", 1, 1, 6),
    ("220", 2, 2, 0),
    ("215", 2, 1, 5),
]
RUTILE_LATTICE_REFS = [
    ("110", 1, 1, 0),
    ("101", 1, 0, 1),
    ("200", 2, 0, 0),
    ("111", 1, 1, 1),
    ("210", 2, 1, 0),
    ("220", 2, 2, 0),
    ("002", 0, 0, 2),
    ("310", 3, 1, 0),
    ("301", 3, 0, 1),
]

# ---------------------------------------------------------------------------
# 数据读取与背景处理
# ---------------------------------------------------------------------------


def load_xy(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """读取 make_origin_ready.py 生成的 3 行表头、Tab 分隔两列数据。"""
    rows: List[Tuple[float, float]] = []
    with open(path, encoding="gbk") as fh:
        for i, raw in enumerate(fh):
            if i < 3:
                continue
            line = raw.strip()
            if not line:
                continue
            parts = re.split(r"\t+|\s+", line)
            if len(parts) < 2:
                continue
            try:
                x, y = float(parts[0]), float(parts[1])
            except ValueError:
                continue
            rows.append((x, y))
    if len(rows) < 10:
        raise ValueError(f"{path} 中没有识别到足够的数据行（{len(rows)} 行）")
    arr = np.asarray(rows, dtype=float)
    order = np.argsort(arr[:, 0])
    arr = arr[order]
    return arr[:, 0], arr[:, 1]


def als_baseline(y: np.ndarray, lam: float = 1e6, p: float = 5e-4, niter: int = 15) -> np.ndarray:
    """Asymmetric least squares 背景估计（Eilers & Boelens）。"""
    y = np.asarray(y, dtype=float)
    n = y.size
    d = sparse.diags([1.0, -2.0, 1.0], [0, -1, -2], shape=(n, n - 2), dtype=float)
    w = np.ones(n, dtype=float)
    for _ in range(niter):
        w_mat = sparse.spdiags(w, 0, n, n)
        z_mat = (w_mat + lam * d.dot(d.T)).tocsc()
        z = spsolve(z_mat, w * y)
        w = p * (y > z) + (1.0 - p) * (y < z)
    return z


def smooth_signal(y: np.ndarray, window: int = 11, poly: int = 3) -> np.ndarray:
    if window % 2 == 0:
        window += 1
    if window >= len(y):
        return y.copy()
    return savgol_filter(y, window, poly)


def robust_noise(y: np.ndarray) -> float:
    med = np.median(y)
    return float(1.4826 * np.median(np.abs(y - med)))


# ---------------------------------------------------------------------------
# 峰拟合
# ---------------------------------------------------------------------------


def pseudo_voigt(
    x: np.ndarray,
    x0: float,
    amp: float,
    fwhm: float,
    eta: float,
    bg0: float,
    bg1: float,
) -> np.ndarray:
    gauss = np.exp(-4.0 * math.log(2.0) * ((x - x0) / fwhm) ** 2)
    lorentz = 1.0 / (1.0 + 4.0 * ((x - x0) / fwhm) ** 2)
    return bg0 + bg1 * (x - x0) + amp * (eta * lorentz + (1.0 - eta) * gauss)


def pv_area(amp: float, fwhm: float, eta: float) -> float:
    return amp * fwhm * (eta * math.pi / 2.0 + (1.0 - eta) * math.sqrt(math.pi / (4.0 * math.log(2.0))))


@dataclass
class PeakFit:
    hkl: str
    two_theta: float
    fwhm: float
    area: float
    amplitude: float
    eta: float
    two_theta_err: float
    fwhm_err: float


def fit_peak(
    x: np.ndarray,
    y: np.ndarray,
    center: float,
    half_window: float,
    noise: float,
    max_signal: float,
) -> Optional[PeakFit]:
    mask = (x >= center - half_window) & (x <= center + half_window)
    xx, yy = x[mask], y[mask]
    if xx.size < 8:
        return None
    y_min, y_max = float(np.min(yy)), float(np.max(yy))
    span = max(y_max - y_min, 1e-6)
    p0 = [center, span, 0.3, 0.5, y_min, 0.0]
    lower = [center - 0.55, 0.0, 0.03, 0.0, -1e6, -1e5]
    upper = [center + 0.55, span * 20.0 + 1e-6, 3.0, 1.0, 1e6, 1e5]
    try:
        popt, pcov = curve_fit(pseudo_voigt, xx, yy, p0=p0, bounds=(lower, upper), maxfev=80000)
    except (RuntimeError, ValueError):
        return None
    x0, amp, fwhm, eta, _, _ = popt
    if not np.all(np.isfinite(popt)):
        return None
    if amp < max(2.5 * noise, 0.002 * max_signal):
        return None
    if abs(x0 - center) > 0.5:
        return None
    if not (0.03 < fwhm < 3.0):
        return None
    perr = np.sqrt(np.diag(pcov)) if pcov is not None else np.full(6, np.nan)
    return PeakFit(
        hkl="",
        two_theta=float(x0),
        fwhm=float(fwhm),
        area=float(pv_area(amp, fwhm, eta)),
        amplitude=float(amp),
        eta=float(eta),
        two_theta_err=float(perr[0]),
        fwhm_err=float(perr[2]),
    )


def fit_phase_peaks(
    x: np.ndarray,
    y_fit: np.ndarray,
    peaks: Iterable[PdfPeak],
    noise: float,
    max_signal: float,
    half_window: float = 0.9,
) -> Dict[str, PeakFit]:
    fits: Dict[str, PeakFit] = {}
    for peak in peaks:
        fit = fit_peak(x, y_fit, peak.two_theta, half_window, noise, max_signal)
        if fit is not None:
            fit.hkl = peak.hkl
            fits[f"{peak.h}{peak.k}{peak.l}"] = fit
    return fits


# ---------------------------------------------------------------------------
# 物理量计算
# ---------------------------------------------------------------------------


def scherrer_size(two_theta: float, fwhm_deg: float, k: float = K_SCHERRER, lam: float = LAMBDA_CUKA) -> float:
    """Scherrer 表观晶粒尺寸（nm）。fwhm 为仪器展宽未校正的实测半高宽。"""
    beta = math.radians(fwhm_deg)
    theta = math.radians(two_theta / 2.0)
    return k * lam / (beta * math.cos(theta)) / 10.0


def spurr_myers(area_anatase: float, area_rutile: float) -> float:
    """返回金红石质量分数（%）。Spurr & Myers, Anal. Chem. 1957, 29, 760."""
    if area_anatase <= 0 or area_rutile <= 0:
        return 0.0 if area_rutile <= 0 else 100.0
    w_a = 1.0 / (1.0 + SPURR_CONST * area_rutile / area_anatase)
    return float(100.0 * (1.0 - w_a))


def tetragonal_d(a: float, c: float, h: int, k: int, l: int) -> float:
    return 1.0 / math.sqrt((h * h + k * k) / (a * a) + (l * l) / (c * c))


def calc_two_theta(a: float, c: float, h: int, k: int, l: int, offset: float) -> float:
    d = tetragonal_d(a, c, h, k, l)
    return 2.0 * math.degrees(math.asin(LAMBDA_CUKA / (2.0 * d))) + offset


def fit_lattice(
    fits: Dict[str, PeakFit],
    refs: Sequence[Tuple[str, int, int, int]],
    p0: Sequence[float],
) -> Optional[dict]:
    observed = [(h, k, l, fits[key].two_theta) for key, h, k, l in refs if key in fits]
    if len(observed) < 4:
        return None

    def residual(p: Sequence[float]) -> np.ndarray:
        a, c, offset = p
        return np.array([calc_two_theta(a, c, h, k, l, offset) - tt for h, k, l, tt in observed])

    try:
        result = least_squares(
            residual,
            x0=list(p0),
            bounds=([2.0, 2.0, -1.0], [10.0, 20.0, 1.0]),
        )
    except ValueError:
        return None
    a, c, offset = (float(v) for v in result.x)
    rms = float(np.sqrt(np.mean(residual(result.x) ** 2)))
    return {
        "a": a,
        "c": c,
        "c_over_a": c / a,
        "volume": a * a * c,
        "zero_offset": offset,
        "rms": rms,
        "n_peaks": len(observed),
        "peaks": [f"{h}{k}{l}" for h, k, l, _ in observed],
    }


# ---------------------------------------------------------------------------
# 汇总分析
# ---------------------------------------------------------------------------


def analyze_sample(temperature: int) -> dict:
    x, y = load_xy(READY_DIR / f"{temperature}.txt")
    background = als_baseline(y)
    y_sub = y - background
    y_fit = smooth_signal(y_sub, window=11, poly=3)
    noise = robust_noise(y_fit)
    max_signal = float(np.max(y_fit))

    anatase_fits = fit_phase_peaks(x, y_fit, ANATASE_PDF, noise, max_signal, half_window=1.0)
    rutile_fits = fit_phase_peaks(x, y_fit, RUTILE_PDF, noise, max_signal, half_window=0.9)

    a101 = anatase_fits.get("101")
    r110 = rutile_fits.get("110")

    result = {
        "temperature": temperature,
        "sample": str(temperature),
        "max_counts": float(np.max(y)),
        "noise": noise,
        "phase": "低结晶度锐钛矿（宽包）" if temperature == 200 else "",
        "main_peak": None,
        "main_two_theta": None,
        "main_fwhm": None,
        "main_d_nm": None,
        "main_d_err_nm": None,
        "rutile_pct": 0.0,
        "rutile_note": "",
        "anatase_fits": anatase_fits,
        "rutile_fits": rutile_fits,
    }

    if temperature == 200:
        result["rutile_note"] = "峰形为宽包，未做定量"
        return result

    if a101 is not None and r110 is not None:
        rutile_pct = spurr_myers(a101.area, r110.area)
        result["rutile_pct"] = rutile_pct
        result["rutile_note"] = "Spurr–Myers 半定量"
    elif r110 is not None and a101 is None:
        result["rutile_pct"] = 100.0
        result["rutile_note"] = "仅检出金红石"
    else:
        result["rutile_pct"] = 0.0
        result["rutile_note"] = "未检出金红石（<2%）"

    # 主峰：优先取两者中积分强度更大的一个
    if a101 is not None and (r110 is None or a101.area >= r110.area):
        main = a101
        main_label = "A(101)"
    elif r110 is not None:
        main = r110
        main_label = "R(110)"
    else:
        main = None
        main_label = "—"

    if main is not None:
        d_nm = scherrer_size(main.two_theta, main.fwhm)
        # 由 FWHM 误差传播到 D
        d_err = d_nm * (main.fwhm_err / main.fwhm) if main.fwhm > 0 else np.nan
        result["main_peak"] = main_label
        result["main_two_theta"] = main.two_theta
        result["main_fwhm"] = main.fwhm
        result["main_d_nm"] = d_nm
        result["main_d_err_nm"] = d_err

    rp = result["rutile_pct"]
    if rp >= 98.0:
        result["phase"] = "金红石"
    elif rp >= 40.0:
        result["phase"] = "锐钛矿+金红石"
    elif rp >= 10.0:
        result["phase"] = "锐钛矿+少量金红石"
    elif rp >= 2.0:
        result["phase"] = "锐钛矿+微量金红石"
    else:
        result["phase"] = "锐钛矿"
    return result


def analyze_all() -> List[dict]:
    results = []
    for t in SAMPLES:
        try:
            results.append(analyze_sample(t))
        except Exception as exc:  # noqa: BLE001 - 单个样品失败不应中断整批
            print(f"[警告] {t} °C 处理失败：{exc}")
    return results


# ---------------------------------------------------------------------------
# 输出 CSV / JSON
# ---------------------------------------------------------------------------


def ensure_dirs() -> None:
    for path in (OUT_DIR, PDF_DIR, FIG_DIR, TAB_DIR):
        path.mkdir(parents=True, exist_ok=True)


def write_pdf_card_files() -> None:
    for key, (_, card, peaks) in PDF_CARDS.items():
        path = PDF_DIR / f"{key}_{card.replace('PDF ', '').strip()}.txt"
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("2theta_deg\trelative_intensity_pct\thkl\n")
            for p in peaks:
                fh.write(f"{p.two_theta:.2f}\t{p.intensity:.0f}\t{p.hkl}\n")


def write_csvs(results: List[dict]) -> None:
    peak_path = OUT_DIR / "peak_parameters.csv"
    with open(peak_path, "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "sample",
                "temperature_C",
                "phase",
                "hkl",
                "two_theta_deg",
                "fwhm_deg",
                "area",
                "amplitude",
                "eta",
                "two_theta_err",
                "fwhm_err",
                "scherrer_D_nm",
            ]
        )
        for r in results:
            for phase, fits in (("anatase", r["anatase_fits"]), ("rutile", r["rutile_fits"])):
                for fit in fits.values():
                    d_nm = scherrer_size(fit.two_theta, fit.fwhm)
                    writer.writerow(
                        [
                            r["sample"],
                            r["temperature"],
                            phase,
                            fit.hkl,
                            f"{fit.two_theta:.4f}",
                            f"{fit.fwhm:.4f}",
                            f"{fit.area:.3f}",
                            f"{fit.amplitude:.2f}",
                            f"{fit.eta:.3f}",
                            f"{fit.two_theta_err:.4f}",
                            f"{fit.fwhm_err:.4f}",
                            f"{d_nm:.2f}",
                        ]
                    )

    summary_path = OUT_DIR / "sample_summary.csv"
    with open(summary_path, "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "sample",
                "temperature_C",
                "phase",
                "main_peak",
                "main_two_theta_deg",
                "main_fwhm_deg",
                "scherrer_D_nm",
                "scherrer_D_err_nm",
                "rutile_pct",
                "rutile_note",
            ]
        )
        for r in results:
            writer.writerow(
                [
                    r["sample"],
                    r["temperature"],
                    r["phase"],
                    r["main_peak"] or "—",
                    "" if r["main_two_theta"] is None else f"{r['main_two_theta']:.4f}",
                    "" if r["main_fwhm"] is None else f"{r['main_fwhm']:.4f}",
                    "" if r["main_d_nm"] is None else f"{r['main_d_nm']:.2f}",
                    "" if r["main_d_err_nm"] is None else f"{r['main_d_err_nm']:.2f}",
                    f"{r['rutile_pct']:.1f}",
                    r["rutile_note"],
                ]
            )

    phase_path = OUT_DIR / "phase_fraction.csv"
    with open(phase_path, "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["sample", "temperature_C", "rutile_pct", "method", "note"])
        for r in results:
            writer.writerow(
                [
                    r["sample"],
                    r["temperature"],
                    f"{r['rutile_pct']:.1f}",
                    "Spurr–Myers" if r["rutile_pct"] not in (0.0, 100.0) else "—",
                    r["rutile_note"],
                ]
            )


def write_lattice_csv(results: List[dict]) -> List[dict]:
    rows: List[dict] = []
    for r in results:
        t = r["temperature"]
        if t < 400:
            continue
        rutile_pct = r["rutile_pct"]
        # 只精修主相，避免把弱峰/重叠峰得到的不可靠晶格参数写进论文
        if rutile_pct < 50.0 and r["anatase_fits"]:
            lat = fit_lattice(r["anatase_fits"], ANATASE_LATTICE_REFS, [3.785, 9.514, 0.0])
            if lat is not None:
                lat.update({"sample": r["sample"], "temperature_C": t, "phase": "anatase"})
                rows.append(lat)
        if rutile_pct >= 50.0 and r["rutile_fits"]:
            lat = fit_lattice(r["rutile_fits"], RUTILE_LATTICE_REFS, [4.593, 2.959, 0.0])
            if lat is not None:
                lat.update({"sample": r["sample"], "temperature_C": t, "phase": "rutile"})
                rows.append(lat)

    path = OUT_DIR / "lattice_parameters.csv"
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "sample",
                "temperature_C",
                "phase",
                "a_A",
                "c_A",
                "c_over_a",
                "volume_A3",
                "zero_offset_deg",
                "rms_deg",
                "n_peaks",
                "peaks_used",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row["sample"],
                    row["temperature_C"],
                    row["phase"],
                    f"{row['a']:.5f}",
                    f"{row['c']:.5f}",
                    f"{row['c_over_a']:.4f}",
                    f"{row['volume']:.3f}",
                    f"{row['zero_offset']:+.4f}",
                    f"{row['rms']:.4f}",
                    row["n_peaks"],
                    " ".join(row["peaks"]),
                ]
            )
    return rows


def write_json(results: List[dict], lattice_rows: List[dict]) -> None:
    payload = {
        "metadata": {
            "wavelength_A": LAMBDA_CUKA,
            "scherrer_K": K_SCHERRER,
            "spurr_myers_constant": SPURR_CONST,
            "pdf_cards": {
                "anatase": "PDF 21-1272",
                "rutile": "PDF 21-1276",
            },
            "notes": [
                "Scherrer 尺寸未扣除仪器展宽，为表观值。",
                "200 °C 样品仅呈宽包，未纳入定量趋势。",
                "金红石含量为 Spurr–Myers 半定量结果，误差约 ±5–10%。",
            ],
        },
        "samples": [
            {
                "sample": r["sample"],
                "temperature_C": r["temperature"],
                "phase": r["phase"],
                "main_peak": r["main_peak"],
                "main_two_theta_deg": r["main_two_theta"],
                "main_fwhm_deg": r["main_fwhm"],
                "scherrer_D_nm": r["main_d_nm"],
                "rutile_pct": r["rutile_pct"],
                "rutile_note": r["rutile_note"],
            }
            for r in results
        ],
        "lattice": lattice_rows,
    }
    with open(OUT_DIR / "summary.json", "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# LaTeX 表格
# ---------------------------------------------------------------------------


def fmt(value: Optional[float], digits: int = 2, dash: str = "---") -> str:
    if value is None or (isinstance(value, float) and not np.isfinite(value)):
        return dash
    return f"{value:.{digits}f}"


def write_latex_tables(results: List[dict], lattice_rows: List[dict]) -> None:
    # 表：主峰参数与晶粒尺寸
    lines = [
        "% 由 xrd_analysis.py 自动生成，请勿手工修改",
        r"\begin{tabular}{@{}cccccccc@{}}",
        r"\toprule",
        r"样品 & 温度/$^\circ$C & 主要物相 & 主峰 & $2\theta$/$^\circ$ & FWHM/$^\circ$ & $D$/nm & 金红石含量/\% \\",
        r"\midrule",
    ]
    for r in results:
        main_peak = r["main_peak"] or "---"
        tt = fmt(r["main_two_theta"], 2)
        fwhm = fmt(r["main_fwhm"], 2)
        d_nm = fmt(r["main_d_nm"], 1)
        rutile = "<2" if r["rutile_pct"] < 2.0 else f"{r['rutile_pct']:.0f}"
        if r["temperature"] == 200:
            tt = "25.4$^{*}$"
        lines.append(
            f"{r['sample']} & {r['temperature']} & {r['phase']} & {main_peak} & {tt} & {fwhm} & {d_nm} & {rutile} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"% $^{*}$ 200 $^\circ$C 样品仅见宽包，峰位为近似值，未做 FWHM/晶粒尺寸定量。",
    ]
    (TAB_DIR / "tab_peak.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # 表：晶格参数
    lines = [
        "% 由 xrd_analysis.py 自动生成，请勿手工修改",
        r"\begin{tabular}{@{}cccccccc@{}}",
        r"\toprule",
        r"样品 & 物相 & $a$/Å & $c$/Å & $c/a$ & $V$/Å$^3$ & $\Delta 2\theta$/$^\circ$ & RMS/$^\circ$ \\",
        r"\midrule",
    ]
    for row in lattice_rows:
        phase = "锐钛矿" if row["phase"] == "anatase" else "金红石"
        lines.append(
            f"{row['sample']} & {phase} & {row['a']:.4f} & {row['c']:.4f} & {row['c_over_a']:.4f} & "
            f"{row['volume']:.2f} & {row['zero_offset']:+.3f} & {row['rms']:.3f} \\\\"
        )
    lines += [
        r"\midrule",
        r"PDF 21-1272 & 锐钛矿 & 3.785 & 9.514 & 2.514 & 136.3 & --- & --- \\",
        r"PDF 21-1276 & 金红石 & 4.593 & 2.959 & 0.644 & 62.4 & --- & --- \\",
        r"\bottomrule",
        r"\end{tabular}",
        r"% $\Delta 2\theta$ 为最小二乘拟合得到的零点偏移；RMS 为峰位残差均方根。",
    ]
    (TAB_DIR / "tab_lattice.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # 表：PDF 卡片数据
    lines = [
        "% 由 xrd_analysis.py 自动生成，请勿手工修改",
        r"\begin{tabular}{@{}cccccc@{}}",
        r"\toprule",
        r"\multicolumn{3}{c}{锐钛矿 PDF 21-1272} & \multicolumn{3}{c}{金红石 PDF 21-1276} \\",
        r"\cmidrule(lr){1-3}\cmidrule(lr){4-6}",
        r"$2\theta$/$^\circ$ & $I/I_0$/\% & $hkl$ & $2\theta$/$^\circ$ & $I/I_0$/\% & $hkl$ \\",
        r"\midrule",
    ]
    n = max(len(ANATASE_PDF), len(RUTILE_PDF))
    for i in range(n):
        cols = []
        if i < len(ANATASE_PDF):
            p = ANATASE_PDF[i]
            cols += [f"{p.two_theta:.2f}", f"{p.intensity:.0f}", p.hkl]
        else:
            cols += ["", "", ""]
        if i < len(RUTILE_PDF):
            p = RUTILE_PDF[i]
            cols += [f"{p.two_theta:.2f}", f"{p.intensity:.0f}", p.hkl]
        else:
            cols += ["", "", ""]
        lines.append(" & ".join(cols) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (TAB_DIR / "tab_pdf.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# 图件
# ---------------------------------------------------------------------------


def setup_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 9,
            "legend.fontsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "axes.linewidth": 0.8,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.top": True,
            "ytick.right": True,
            "xtick.major.size": 3.5,
            "ytick.major.size": 3.5,
            "xtick.minor.size": 2.0,
            "ytick.minor.size": 2.0,
            "savefig.dpi": 600,
            "savefig.bbox": "tight",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def sample_colors() -> Dict[int, tuple]:
    cmap = plt.get_cmap("viridis")
    return {t: cmap(v) for t, v in zip(SAMPLES, np.linspace(0.12, 0.88, len(SAMPLES)))}


def load_normalized(temperature: int) -> Tuple[np.ndarray, np.ndarray]:
    return load_xy(NORM_DIR / f"{temperature}.txt")


def plot_fig1() -> None:
    colors = sample_colors()
    offset = 100.0
    fig = plt.figure(figsize=(7.2, 8.8))
    gs = GridSpec(3, 1, height_ratios=[2.4, 0.65, 1.1], hspace=0.08)
    ax = fig.add_subplot(gs[0])
    axpdf = fig.add_subplot(gs[1], sharex=ax)
    ax2 = fig.add_subplot(gs[2])

    # (a) full range
    handles = []
    for i, t in enumerate(SAMPLES):
        x, y = load_normalized(t)
        (line,) = ax.plot(x, y + i * offset, color=colors[t], lw=0.65, zorder=2, label=f"{t} $^\\circ$C")
        handles.append(line)

    ax.set_xlim(20, 80)
    ax.set_ylim(-5, len(SAMPLES) * offset + 18)
    ax.set_ylabel("Intensity (a.u.)")
    ax.set_yticks([])
    ax.tick_params(labelbottom=False)
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_minor_locator(MultipleLocator(2))
    ax.text(0.012, 0.985, "(a)", transform=ax.transAxes, fontsize=10, fontweight="bold", va="top")
    ax.legend(
        handles=handles,
        labels=[f"{t} $^\\circ$C" for t in SAMPLES],
        loc="upper left",
        bbox_to_anchor=(1.015, 1.0),
        frameon=False,
        fontsize=7.5,
        handlelength=1.2,
        labelspacing=0.32,
        borderaxespad=0.0,
    )

    # (b) PDF cards, aligned with the main panel
    y_anatase = 1.05
    y_rutile = 0.05
    stick_h = 0.72
    for p in ANATASE_PDF:
        axpdf.vlines(p.two_theta, y_anatase, y_anatase + p.intensity / 100.0 * stick_h, color="tab:green", linewidth=1.1)
    for p in RUTILE_PDF:
        axpdf.vlines(p.two_theta, y_rutile, y_rutile + p.intensity / 100.0 * stick_h, color="tab:red", linewidth=1.1)
    axpdf.axhline(1.0, color="0.75", lw=0.5, zorder=0)
    for hkl in ("(101)", "(004)", "(200)", "(211)"):
        p = next(q for q in ANATASE_PDF if q.hkl == hkl)
        axpdf.text(p.two_theta, y_anatase + p.intensity / 100.0 * stick_h + 0.04, hkl, color="tab:green", fontsize=6.2, ha="center", va="bottom")
    for hkl in ("(110)", "(101)", "(211)"):
        p = next(q for q in RUTILE_PDF if q.hkl == hkl)
        axpdf.text(p.two_theta, y_rutile + p.intensity / 100.0 * stick_h + 0.04, hkl, color="tab:red", fontsize=6.2, ha="center", va="bottom")
    axpdf.text(79.5, y_anatase + 0.50, "Anatase 21-1272", color="tab:green", fontsize=7.2, va="center", ha="right", bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    axpdf.text(79.5, y_rutile + 0.50, "Rutile 21-1276", color="tab:red", fontsize=7.2, va="center", ha="right", bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    axpdf.set_ylim(-0.05, 2.02)
    axpdf.set_yticks([])
    axpdf.set_xlabel(r"$2\theta$ (degree)")
    axpdf.xaxis.set_major_locator(MultipleLocator(10))
    axpdf.xaxis.set_minor_locator(MultipleLocator(2))
    axpdf.tick_params(axis="y", left=False, right=False)
    axpdf.text(0.012, 0.92, "(b)", transform=axpdf.transAxes, fontsize=10, fontweight="bold", va="top")

    # (c) zoom 23-30
    for i, t in enumerate(SAMPLES):
        x, y = load_normalized(t)
        mask = (x >= 23.0) & (x <= 30.0)
        ax2.plot(x[mask], y[mask] + i * offset, color=colors[t], lw=0.7, zorder=2)
    ax2.axvline(25.28, color="tab:green", ls="--", lw=0.8, alpha=0.65, zorder=1)
    ax2.axvline(27.45, color="tab:red", ls="--", lw=0.8, alpha=0.65, zorder=1)
    ax2.text(0.326, 0.96, "A(101)", transform=ax2.transAxes, color="tab:green", fontsize=7.5, ha="center", va="top", bbox=dict(facecolor="white", edgecolor="none", pad=0.6))
    ax2.text(0.636, 0.96, "R(110)", transform=ax2.transAxes, color="tab:red", fontsize=7.5, ha="center", va="top", bbox=dict(facecolor="white", edgecolor="none", pad=0.6))
    ax2.set_xlim(23, 30)
    ax2.set_ylim(-5, len(SAMPLES) * offset + 70)
    ax2.set_xlabel(r"$2\theta$ (degree)")
    ax2.set_ylabel("Intensity (a.u.)")
    ax2.xaxis.set_major_locator(MultipleLocator(1))
    ax2.xaxis.set_minor_locator(MultipleLocator(0.2))
    ax2.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax2.set_yticks([])
    ax2.text(0.012, 0.985, "(c)", transform=ax2.transAxes, fontsize=10, fontweight="bold", va="top")

    fig.savefig(FIG_DIR / "fig1_xrd_stack.png", dpi=600)
    fig.savefig(FIG_DIR / "fig1_xrd_stack.pdf")
    plt.close(fig)


def plot_fig2(results: List[dict]) -> None:
    anatase = [r for r in results if r["temperature"] in (300, 400, 500, 600, 700) and r["main_peak"] == "A(101)"]
    rutile = [r for r in results if r["temperature"] in (800, 900) and r["main_peak"] == "R(110)"]

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0))
    for ax, key, ylabel in zip(
        axes,
        ["main_fwhm", "main_d_nm"],
        ["FWHM ($^\\circ$)", "Crystallite size $D$ (nm)"],
    ):
        ax.axvspan(700, 800, color="0.90", zorder=0, lw=0)
        ax.plot(
            [r["temperature"] for r in anatase],
            [r[key] for r in anatase],
            "o-",
            color="tab:blue",
            ms=4.5,
            lw=1.0,
            label="Anatase A(101)",
            zorder=3,
        )
        ax.plot(
            [r["temperature"] for r in rutile],
            [r[key] for r in rutile],
            "s--",
            color="tab:red",
            ms=4.5,
            lw=1.0,
            label="Rutile R(110)",
            zorder=3,
        )
        if key == "main_d_nm":
            for r in anatase + rutile:
                if r[key] is not None:
                    ax.errorbar(
                        r["temperature"],
                        r[key],
                        yerr=r["main_d_err_nm"],
                        fmt="none",
                        ecolor="0.4",
                        elinewidth=0.7,
                        capsize=2,
                        zorder=2,
                    )
        ax.set_xlabel("Temperature ($^\\circ$C)")
        ax.set_ylabel(ylabel)
        ax.set_xlim(250, 950)
        ax.xaxis.set_major_locator(MultipleLocator(100))
        ax.xaxis.set_minor_locator(MultipleLocator(25))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax.legend(loc="best", frameon=False)
    axes[0].set_title("(a) Peak width", loc="left", fontsize=9)
    axes[1].set_title("(b) Apparent crystallite size", loc="left", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig2_size.png", dpi=600)
    fig.savefig(FIG_DIR / "fig2_size.pdf")
    plt.close(fig)


def plot_fig3(results: List[dict]) -> None:
    temps = [r["temperature"] for r in results]
    rutile = [r["rutile_pct"] for r in results]

    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    ax.axvspan(700, 800, color="0.90", zorder=0, lw=0)
    ax.axhline(2.0, color="0.5", ls=":", lw=0.8, zorder=1)
    ax.text(210, 3.0, "detection limit $\\approx$ 2%", fontsize=7, color="0.4", va="bottom")
    ax.plot(temps, rutile, "o-", color="tab:red", ms=4.5, lw=1.0, zorder=3)
    for r in results:
        if r["temperature"] in (700, 800, 900):
            ax.annotate(
                f"{r['rutile_pct']:.0f}%",
                (r["temperature"], r["rutile_pct"]),
                textcoords="offset points",
                xytext=(0, 6),
                ha="center",
                fontsize=7,
                color="tab:red",
            )
    ax.set_xlabel("Temperature ($^\\circ$C)")
    ax.set_ylabel("Rutile fraction (%)")
    ax.set_xlim(180, 930)
    ax.set_ylim(-3, 108)
    ax.xaxis.set_major_locator(MultipleLocator(100))
    ax.xaxis.set_minor_locator(MultipleLocator(25))
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig3_phase.png", dpi=600)
    fig.savefig(FIG_DIR / "fig3_phase.pdf")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="TiO2 XRD 数据分析与论文图件生成")
    parser.add_argument("--no-figures", action="store_true", help="只输出 CSV/JSON/表格，不生成图件")
    parser.add_argument("--dpi", type=int, default=600, help="PNG 图件分辨率（默认 600）")
    args = parser.parse_args()

    ensure_dirs()
    setup_matplotlib()
    if args.dpi != 600:
        plt.rcParams["savefig.dpi"] = args.dpi

    write_pdf_card_files()
    results = analyze_all()
    if not results:
        print("没有成功处理任何样品，请检查数据目录。")
        return 1
    write_csvs(results)
    lattice_rows = write_lattice_csv(results)
    write_json(results, lattice_rows)
    write_latex_tables(results, lattice_rows)

    if not args.no_figures:
        plot_fig1()
        plot_fig2(results)
        plot_fig3(results)

    print(f"处理完成：{len(results)} 个样品")
    print(f"输出目录：{OUT_DIR}")
    print(f"图件目录：{FIG_DIR}")
    print()
    print(f"{'样品':>4} {'温度':>5} {'物相':<18} {'主峰':>6} {'2θ':>7} {'FWHM':>6} {'D/nm':>7} {'金红石%':>8}")
    for r in results:
        tt = "—" if r["main_two_theta"] is None else f"{r['main_two_theta']:.2f}"
        fw = "—" if r["main_fwhm"] is None else f"{r['main_fwhm']:.2f}"
        dn = "—" if r["main_d_nm"] is None else f"{r['main_d_nm']:.1f}"
        print(
            f"{r['sample']:>4} {r['temperature']:>5} {r['phase']:<18} "
            f"{r['main_peak'] or '—':>6} {tt:>7} {fw:>6} {dn:>7} {r['rutile_pct']:>8.1f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
