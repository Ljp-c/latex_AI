"""Count Chinese characters in the essay body (excluding figures, tables, captions)."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
FILES = [
    "content/abstract.tex",
    "content/ch1-intro.tex",
    "content/ch2-mechanism.tex",
    "content/ch3-choice.tex",
    "content/ch4-single-vs-combined.tex",
    "content/ch5-limits.tex",
    "content/ch6-conclusion.tex",
]

CJK = re.compile(r"[\u4e00-\u9fff]")
FLOAT_ENV = re.compile(
    r"\\begin\{(figure|table)\}.*?\\end\{\1\}", re.S
)
CAPTION = re.compile(r"\\caption\{[^{}]*\}", re.S)


def strip_latex(text: str, keep_floats: bool = False) -> str:
    text = re.sub(r"(?<!\\)%.*", "", text)
    if not keep_floats:
        text = FLOAT_ENV.sub("", text)
        text = CAPTION.sub("", text)
    text = re.sub(r"\\(cite|ref|label)\{[^{}]*\}", "", text)
    text = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?", "", text)
    text = re.sub(r"[{}$^_&]", "", text)
    return text


def main() -> None:
    total = 0
    total_full = 0
    for rel in FILES:
        path = ROOT / rel
        if not path.exists():
            print(f"missing: {rel}")
            continue
        raw = path.read_text(encoding="utf-8")
        body = strip_latex(raw)
        count = len(CJK.findall(body))
        full_count = len(CJK.findall(strip_latex(raw, keep_floats=True)))
        total += count
        total_full += full_count
        print(f"{rel:35s} {count:5d}  (with floats: {full_count:5d})")
    print("-" * 60)
    print(f"{'TOTAL (CJK, body only)':35s} {total:5d}")
    print(f"{'TOTAL (CJK, incl. floats)':35s} {total_full:5d}")
    print("target: 800-1800; recommended: 1500-1650 (body only)")


if __name__ == "__main__":
    main()
