# Repository Knowledge Base — New Manga

本目录是本仓库的派生知识层。事实优先级：Source / Tests / Git > 本目录内容。
所有权与刷新权限见 [doc/AI_COORDINATION.md](../doc/AI_COORDINATION.md)。

## Structure
- `repowiki/`: 轻量仓库结构地图与 import 依赖 PageRank 排名（零 LLM）。
  - `repo-map.json`: 机器可读的文件排名与语言统计。
  - `repo-map.txt`: 人/Agent 可读的高优先级导航地图。
- `codewiki/`: CodeWiki 深度架构与组件文档；当前包含 17 个同页双语模块页面、模块树、
  CodeWiki baseline metadata 和 policy freshness sidecar。页面默认采用简体中文 + English，
  不创建 `codewiki-zh` / `codewiki-en` 两套 Wiki。
- `Knowledge Refresh Owner = Codex`；刷新责任不改变项目既有主线 writer、branch/worktree 或 Git 权限。

## 全局命令（Windows 原生，任何 Git 项目可用）

工具链安装在 `%USERPROFILE%\.repo-knowledge\`，本项目不需要任何项目内脚本：

- `rk-init`: 创建 `wiki\` 脚手架（幂等，不覆盖已有内容）。
- `rk-map`: 刷新 RepoWiki 依赖地图（零 LLM）。
- `rk-wiki`: 生成 CodeWiki 深度文档（需 CodeWiki LLM 凭据，未配置时打印启用指引）。
- `rk-update`: 刷新 map + CodeWiki 增量更新（`--update --update-rung 0`）；缺少 CLI baseline 时拒绝隐式 full generation。
- `rk-status`: 只读状态：分支、HEAD、产物新鲜度、MCP 健康。
- `rk-verify`: 校验 venv、包装脚本、UTF-8、MCP stdio 握手、map JSON。

持久化双语规则位于 `%USERPROFILE%\.repo-knowledge\config\codewiki-instructions.md`。
`rk-wiki`、`rk-update` 和 MCP 写入流程必须使用同一规则；Web UI 只作为 preview/cache。

## Agent 接入（MCP / Shared Wiki）

ZCode / Codex / Qoder / Antigravity 的 MCP 配置均已指向全局
`%USERPROFILE%\.repo-knowledge\bin\codewiki-mcp.cmd`；DSH 无 MCP 客户端配置，
直接读本目录文件（Shared Wiki 模式）。所有 Agent 都只是本知识层的消费者，
刷新主知识基线须遵循 AI_COORDINATION.md 的交接流程。

## 注意事项

- CodeWiki 对 QML 不是一等支持：涉及 Screen / Component / signal / property /
  ViewModel binding 的结论必须直接读 `.qml` 与对应 Python/ViewModel/Service。
- `.repowikiignore` 控制 map 扫描范围（不影响 git）；`.qoder-credits\` 等
  canvas 产物已被排除。
