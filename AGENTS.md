# AGENTS.md — 本工作区代理（AI）规则

## ⛔ `notes/` 仓库：只读 · 禁止推送 · 仅允许拉取（重要，永久有效，2026-09-24 起）

`notes/` 是从 `https://git.smarttwig.cn/lanshuye/notes.git` 克隆的**他人仓库**（岚椿铧 的课程笔记），在本工作区仅作**只读参考**使用。

### 永远禁止
- 编辑、增删、移动、重命名、格式化 `notes/` 中的任何文件（包括 Markdown 正文与图片）；
- 在 `notes/` 中执行 `git add` / `git commit` / `git merge` / `git push` / `git rm` / `git clean` 等一切写操作；
- 删除或绕过 `notes/.git/hooks/` 下的保护钩子（`pre-commit`、`pre-merge-commit`、`pre-push`）；
- 使用 `--no-verify` 等参数绕过钩子。

### 唯一允许的操作
- `git -C notes pull`（或 `git fetch`）获取上游最新内容；已配置 `pull.rebase=true` 自动集成。

> 该规则已由 git hooks + 禁用推送 URL（`read-only://push-disabled`）强制执行，请勿尝试绕过。

---

**English:** The `notes/` folder is a READ-ONLY clone of a third party's repository.
Never modify, commit, or push anything inside it. The only allowed operation is `git pull`.
