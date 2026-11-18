import re, glob, os
tot = 0
for p in sorted(glob.glob(r"E:\latex_AI\纳米材料制备与表征\课程论文\content\body\*.tex")) + [r"E:\latex_AI\纳米材料制备与表征\课程论文\content\abstract.tex"]:
    t = open(p, encoding="utf-8").read()
    t = re.sub(r"\\begin\{(table|tabular|figure)\*?\}.*?\\end\{\1\*?\}", "", t, flags=re.S)
    t = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})?", "", t)
    n = len(re.findall(r"[\u4e00-\u9fff]", t))
    print(os.path.basename(p), n)
    tot += n
print("TOTAL CJK", tot)
