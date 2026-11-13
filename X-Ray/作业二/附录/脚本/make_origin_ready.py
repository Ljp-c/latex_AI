#!/usr/bin/env python3
"""把仪器导出的 XRD txt 整理成 Origin 可直接导入的规整格式。

输入：GBK 编码，9 行元数据表头 + 定宽数据（020.0200 119）
输出：ready/<文件名>，制表符分隔，3 行表头 + 两列数据：
      第 1 行 列名(Long Name)  第 2 行 单位(Units)  第 3 行 备注(Comments)

3 行表头都是两个字段，Origin 的自动识别会把它们正确当成
列名 / 单位 / 备注，不会再像原来那样把元数据当数据读进去。

用法：
    python make_origin_ready.py 资料\原数据            # 处理该目录，输出到它的 ready/
    python make_origin_ready.py 资料\原数据 --norm     # 归一化到最强峰=100，输出到 ready_norm/
    python make_origin_ready.py 资料\原数据\200.txt -n # 只处理单个文件
    不带路径时处理当前工作目录
"""

import re
import sys
from pathlib import Path

ENCODING = "gbk"
DATA_RE = re.compile(r"^\s*(\d{1,3}\.\d{4})\s+(\d+)\s*$")


def parse(text: str):
    """拆出元数据和 (2θ, 强度) 数据行。"""
    meta: dict[str, str] = {}
    rows: list[tuple[float, int]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        match = DATA_RE.match(line)
        if match:
            rows.append((float(match.group(1)), int(match.group(2))))
        elif ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
        elif "=" in line:
            key, value = line.split("=", 1)
            meta[key.strip()] = value.strip()
    return meta, rows


def build(meta: dict[str, str], rows: list[tuple[float, int]], name: str, normalize: bool = False) -> str:
    lam = meta.get("波长", "?")
    step = meta.get("步宽", "?")
    start = meta.get("起始角", "?")
    end = meta.get("终止角", "?")
    date = meta.get("实验日期", "?")

    peak_angle, peak = max(rows, key=lambda row: row[1])
    if normalize:
        long_name, units = "2θ\tI/I0", "°\t%"
        body = [f"{angle:.4f}\t{count / peak * 100:.2f}" for angle, count in rows]
    else:
        long_name, units = "2θ\tIntensity", "°\tcounts"
        body = [f"{angle:.4f}\t{count}" for angle, count in rows]

    header = [
        long_name,
        units,
        # 备注里不用 Å：GBK 编不出来，Origin 默认按 GBK 读会出乱码
        f"λ={lam} A; step {step}°; {start}-{end}°; {date}; Imax={peak} @ {peak_angle:.2f}°"
        f"\tsample {Path(name).stem}",
    ]
    return "\r\n".join(header + body) + "\r\n"


def main() -> int:
    base = Path.cwd()
    args = sys.argv[1:]
    normalize = any(a.lower() in ("-n", "--norm", "--normalize") for a in args)

    roots, files = [], []
    for arg in (a for a in args if not a.startswith("-")):
        path = Path(arg)
        path = path if path.is_absolute() else base / path
        (roots if path.is_dir() else files).append(path)

    if roots or files:
        for path in roots + files:
            if not path.exists():
                print(f"路径不存在：{path}")
                return 1
        anchor = roots[0] if roots else files[0].parent
        targets = [t for root in roots for t in sorted(root.glob("*.txt"))] + files
    else:
        anchor = base
        targets = sorted(anchor.glob("*.txt"))

    targets = [t for t in targets if t.is_file()]
    if not targets:
        print(f"没有找到 .txt 文件（查找目录：{anchor}）")
        return 1

    out_dir = anchor / ("ready_norm" if normalize else "ready")
    out_dir.mkdir(exist_ok=True)

    for src in targets:

        meta, rows = parse(src.read_bytes().decode(ENCODING))
        if not rows:
            print(f"跳过（没有识别到数据行）：{src.name}")
            continue

        dest = out_dir / src.name
        dest.write_bytes(build(meta, rows, src.name, normalize).encode(ENCODING))
        print(f"{src.name:<10} {len(rows):>5} 行  λ={meta.get('波长', '?'):<8} -> {out_dir.name}/{src.name}")

    print(f"\n完成，共 {len(targets)} 个文件，输出目录：{out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
