# URAT LaTeX 模板构建原理与规律

## 1. 总体结构与入口
- 模板入口是 [URAT/main.tex](URAT/main.tex)。它负责：加载宏包、引入内建模块、读取配置、并按固定顺序拼装封面、目录、摘要、正文与附录。
- 文档类使用 `ctexart`（12pt、A4），天然支持中文排版；引用方案用 `biblatex` + `biber`，样式是 `gb7714-2015`。

## 2. 文件职责与模块分层
**核心逻辑层（builtin）**
- [URAT/builtin/config.tex](URAT/builtin/config.tex) 定义元数据宏（如 `\doctitle`、`\mucprojectid`），并保存到内部变量。
- [URAT/builtin/cover.tex](URAT/builtin/cover.tex) 使用内部变量排版封面。
- [URAT/builtin/header.tex](URAT/builtin/header.tex) 统一设置页眉页脚、章节标题格式、段落与行距。
- [URAT/builtin/abstract.tex](URAT/builtin/abstract.tex) 封装摘要与关键词环境，并写入目录。

**用户配置层（config）**
- [URAT/config/configure.tex](URAT/config/configure.tex) 仅负责填写元数据，不改模板逻辑。

**内容层（content）**
- [URAT/content/abstract.tex](URAT/content/abstract.tex) 摘要与英文摘要正文。
- [URAT/content/body.tex](URAT/content/body.tex) 正文结构与章节。
- [URAT/content/attach.tex](URAT/content/attach.tex) 附录、致谢、参考文献。

**资源层（assets）**
- [URAT/assets](URAT/assets) 存放 Logo 等图片资源。

**编译层（scripts）**
- [URAT/complie.bat](URAT/complie.bat) / [URAT/complie.sh](URAT/complie.sh) 负责检测编译器、重复编译、处理参考文献与清理中间文件。

## 3. 文档拼装流程（主线）
`main.tex` 的拼装顺序是固定的：

```text
加载宏包 -> 载入 builtin 模块 -> 调用 \setupHeader
-> 读取 config/configure.tex
-> \begin{document}
-> \makecover
-> \tableofcontents
-> content/abstract.tex
-> content/body.tex
-> content/attach.tex
```

这说明模板是“先定义结构与宏，后注入数据与内容”的流水线。

## 4. 元数据机制：定义-赋值-渲染
模板采用三层元数据流：

1. **定义变量**：在 [URAT/builtin/config.tex](URAT/builtin/config.tex) 用 `\def` 与 `\makeatletter` 创建内部变量。
2. **用户赋值**：在 [URAT/config/configure.tex](URAT/config/configure.tex) 调用 `\doctitle{...}` 等命令写入值。
3. **渲染输出**：
   - 封面在 [URAT/builtin/cover.tex](URAT/builtin/cover.tex) 读取 `\varmucprojectid` 等内部变量。
   - 摘要在 [URAT/builtin/abstract.tex](URAT/builtin/abstract.tex) 读取 `\muckeywords` 与 `\mucenglishkeywords`。

这个模式的规律是：**所有可配置内容都通过“宏命令”传值，而不是直接改模板文件**。

## 5. 版式与标题控制
- [URAT/builtin/header.tex](URAT/builtin/header.tex) 统一设置页眉：使用 `fancyhdr`，居中显示固定标题，页脚显示页码。
- `\setupHeader` 还设置：
  - `\baselinestretch` 行距系数为 1.25
  - `\parindent` 首行缩进 2em
  - `\titleformat` 与 `\titlespacing` 控制章节标题样式与间距
- [URAT/main.tex](URAT/main.tex) 中额外细化 `\subsection` 与 `\subsubsection` 的标题样式，并配置 enumerate 的编号样式。

## 6. 摘要与目录的封装方式
- [URAT/builtin/abstract.tex](URAT/builtin/abstract.tex) 定义 `textarea` 环境：
  - `\phantomsection` + `\addcontentsline` 将非编号段落写入目录
  - 使用 `\obeylines` 保留换行
  - 自动切换为 `\songti\sihao` 字号
- `MUCAbstract` 与 `MUCENAbstract` 是 `textarea` 的特化包装，结束时自动插入关键词。

**规律**：需要进入目录但不使用 `\section` 的内容，统一用 `textarea` 包裹。

## 7. 正文组织方式
- 正文内容集中在 [URAT/content/body.tex](URAT/content/body.tex)。
- [URAT/main.tex](URAT/main.tex) 在正文前调用 `\par`、`\indent`、`\obeylines`，使正文更接近“纯文本输入”的体验。

## 8. 附录、致谢与参考文献
- [URAT/content/attach.tex](URAT/content/attach.tex) 用 `textarea` 生成“附录”“致谢”等目录项。
- 参考文献使用 `\printbibliography`，并在前面用 `\addcontentsline` 手动插入目录。

## 9. 参考文献与编译策略
- 引用样式：`biblatex` + `gb7714-2015`。
- 编译脚本根据源文件判断编译器：
  - 发现 `ctex`/`xeCJK`/`fontspec` 则使用 `xelatex`
  - 发现 `luatex` 则使用 `lualatex`
  - 否则使用 `pdflatex`
- 先编译一次，再运行 `biber`/`bibtex`，最后再编译两次确保交叉引用更新。
- [URAT/complie.bat](URAT/complie.bat) 会将临时文件放入 `.tmp` 目录，并做清理。

## 10. 模板规律总结（可迁移原则）
1. **分层原则**：布局逻辑在 builtin，配置在 config，内容在 content。
2. **宏驱动原则**：所有可变信息通过宏传值，模板本身不直接写死数据。
3. **目录控制原则**：非编号章节进入目录统一使用 `\phantomsection + \addcontentsline`。
4. **中英文摘要对称原则**：摘要环境统一封装、统一字号、自动挂载关键词。
5. **可编译原则**：脚本自动检测编译器、自动运行文献工具、自动清理。

## 11. 使用与扩展建议
**最小使用流程**
1. 修改 [URAT/config/configure.tex](URAT/config/configure.tex) 中的元数据。
2. 编辑 [URAT/content/abstract.tex](URAT/content/abstract.tex) 与 [URAT/content/body.tex](URAT/content/body.tex)。
3. 使用 [URAT/complie.bat](URAT/complie.bat) 或 [URAT/complie.sh](URAT/complie.sh) 编译。

**扩展方法**
- 新增封面字段：在 [URAT/builtin/config.tex](URAT/builtin/config.tex) 定义新宏，在 [URAT/builtin/cover.tex](URAT/builtin/cover.tex) 渲染，并在 [URAT/config/configure.tex](URAT/config/configure.tex) 赋值。
- 新增非编号章节：复用 `textarea` 环境，确保目录条目一致。
- 更换引用样式：修改 [URAT/main.tex](URAT/main.tex) 中 `biblatex` 的 `style` 参数。

## 12. 给下一篇文章建模板时的抽取清单
- 文章标题层级结构（一级、二级、三级）
- 是否有摘要、关键词、英文摘要
- 参考文献样式要求与引用规范
- 是否有附录、致谢、图表目录
- 章节编号是否需要特殊格式
- 字号与行距要求

确认这些信息后，可快速生成一份与文章结构一致的最小模板。