# AI Coordination — 知识层与主控交接

本文件只管两件事：**谁负责刷新知识层**，以及**换主控时怎么交接**。

它不改变角色与集成权限。主线集成权仍按 [AGENTS.md](../AGENTS.md) 与
[协作协议](09_COLLABORATION.md) 执行：Codex 是唯一主线写入和合并责任人。
本文件与上述两份冲突时，以上述两份为准。

## 当前状态

```text
Knowledge Refresh Owner:  Codex
Bootstrap Agent:          Codex         # 2026-09-21 从 ZCode 接手（工具链由 ZCode 于同日重建为全局 Windows 原生）
Mainline Integrator:      Codex        # 不由本文件授予或变更
Knowledge Baseline HEAD:  ba5cc5cc09ecf7b946dc589286a748100b12cd22
Last Knowledge Refresh:   2026-09-21
Last Handover:            2026-09-21 ZCode -> Codex (知识层刷新 Owner 移交；见下方交接记录)
```

## 交接记录

### 2026-09-21 ZCode → Codex（Knowledge Refresh Owner）

移交前安全检查与验证（完整日志见 `verification/KNOWLEDGE-OWNER-HANDOVER-20260921/`）：

- Git：`master` @ `ba5cc5c`（"docs: conditionally release T1.1.1"）。未提交内容
  归原作者所有并原样保留：`experiments/TASK-017/README.md`（tracked 修改）、
  `.codewiki/`、`.qoder-credits/`、`.repowikiignore`、本文件与 `wiki/`（untracked）。
- STATUS / TASK：无 in_progress Task；T1.1.1 已由 Codex 条件性释放
  （`proposed`，suggested_owner=ZCode，待分配 owner/branch/worktree 后才 ready）。
- 测试：Git Bash + `TASK-012-py312` venv（Python 3.12.3）@ `ba5cc5c`：
  `1031 passed, 0 skipped`，EXIT=0（`full-suite-ba5cc5c-gitbash-py312.log`）。
  与 STATUS 记录的 PowerShell 口径 `1025 passed + 6 skipped` 的差值是 6 个
  OpenSSL 条件 skip：Git Bash 下 openssl 可用，skip 消除；两种口径 collected
  均为 1031。
- 知识层：`rk-verify` ALL CHECKS PASSED，EXIT=0（`rk-verify-ba5cc5c.log`）；
  `rk-map` 已刷至 `ba5cc5c`（src/tests 相对 `1fa5f89` 无变化，map 排名不变）；
  `wiki/codewiki/` 仍为空（无 CodeWiki LLM 配置，属已知状态）。
- 接管确认（交接流程第 6 步）：新任 Owner 需读 AGENTS → 本文件 → STATUS →
  当前 TASK → RepoWiki Map → CodeWiki Overview → `git status` 后确认接管。

## 两个权限是分开的

| 权限 | 归属 | 范围 |
|---|---|---|
| 主线集成 | Codex | 合并、`master` 写入、发布、任务释放与范围冻结 |
| 知识层刷新 | Knowledge Refresh Owner | 只写 `wiki/**` 与 `wiki/*/*.meta.json` |

Knowledge Refresh Owner **不**因此获得 `src/**`、`tests/**`、`doc/tasks/**` 写权限，
也不获得审核自己产出以外的任何审查权。

## 知识源

| 层 | 位置 | 产生方式 | 不负责 |
|---|---|---|---|
| 实现事实 | `src/**`、`tests/**`、Git | 提交 | — |
| 项目管理事实 | `AGENTS.md`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/tasks/**` | 人工 + Codex 集成 | 代码结构 |
| 快速导航 | `wiki/repowiki/repo-map.json` | `repowiki map`，零 LLM | 架构结论、任务、完成证据 |
| 深度知识库 | `wiki/codewiki/` | CodeWiki 分析 + 编写 | 任务状态、Git 事实、验收 |

事实优先级：Source / Tests / Git → AGENTS → STATUS / TASK → 设计契约 → CodeWiki / RepoWiki 派生结论。

## 刷新规则

`repowiki map` 便宜，合并、重要文件变化、Task 集成、阶段 checkpoint 后可刷。
CodeWiki 只在模块增删、架构或依赖变化、Service/Repository 边界变化、阶段完成、
Release、Rebaseline 时刷，默认增量（`--update`），不默认全量重建。

普通执行 Agent 可以读 `wiki/**`、可以调 CodeWiki MCP，但默认不刷主知识基线，
也不在自己的 worktree 里生成主 Wiki。

刷新命令为全局 Windows 原生命令（任何 Git 项目可用，无需项目内脚本）：
`rk-init` / `rk-map` / `rk-wiki` / `rk-update` / `rk-status` / `rk-verify`
（安装在 `%USERPROFILE%\.repo-knowledge\`，详见 [wiki/README.md](../wiki/README.md)）。
零 LLM 的 map 刷新用 `rk-map` 或 `rk-update`；深度文档用 `rk-wiki`
（需 CodeWiki LLM 配置）或由 Agent 经 CodeWiki MCP 以 IDE-driven 流程生成。

## 交接流程

换 Knowledge Refresh Owner 必须走完整流程，不允许一句聊天消息完成：

1. 现任 Owner 完成当前安全检查，记录 Git / STATUS / TASK 状态。
2. 提交或安全保存当前状态（不 push；无 push 授权）。
3. 跑测试，跑 `rk-verify`。
4. 刷新 `wiki/repowiki/`；必要时增量刷 `wiki/codewiki/`。
5. 更新本文件的 `Knowledge Refresh Owner`、`Knowledge Baseline HEAD`、
   `Last Knowledge Refresh`、`Last Handover`。
6. 新任 Owner 读 AGENTS → 本文件 → STATUS → 当前 TASK → RepoWiki Map →
   CodeWiki Overview → `git status`，确认接管。

接任者只需要仓库、上述文档和全局 `rk-*` 命令，**不需要重装知识层工具**。
环境搭建步骤见 [wiki/README.md](../wiki/README.md)；机器专用配置（venv 路径、
代理、登录态）不进 Git，换 Agent 不换知识。

## 已知限制

- **RepoWiki Map 的 Windows bug 已修复（2026-09-21）。** repowiki 0.4.2 曾在
  Windows 下产出 0 条边（分数退化 `1/816`，根因：import 解析候选为正斜杠而
  `known_paths` 为反斜杠），当时 `wiki/repowiki/` 只能由 WSL 侧产出。现在已在
  全局安装内修复（`core/scanner.py` 统一 `FileInfo.path` 为 posix 分隔符），
  Windows 原生 `rk-map` 实测 Top 排名与此前 WSL 产物一致（Top 50 内 49 档分数），
  本目录由 Windows 侧产出。工具升级时需复测此项。
- **CodeWiki 不是一等支持 QML。** 涉及 Screen / Component / signal / slot /
  property / objectName / ViewModel binding / Python bridge / UI Action 的结论，
  必须直接读 `.qml` 与对应 Python/ViewModel/Service。CodeWiki 没显示不等于不存在。
- **antigravity 在 `AGENTS.md` 中没有角色条目**（见 STATUS.md 治理行）。本文件不
  补这个缺口，需要 Codex/Owner 裁决。
