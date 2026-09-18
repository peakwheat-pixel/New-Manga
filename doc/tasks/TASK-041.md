---
id: TASK-041
title: MOBI 导入路线（用户已批准 MOBI 解析依赖）
kind: implementation
status: in_review
approval: approved_by_user
suggested_owner: DeepSeek Harness
owner: ZCode
reviewer: Codex
depends_on: [TASK-023]
base_commit: 904fca185c9900c0b2df297529a58ece831dc0a0
branch: agent/zcode/TASK-041-mobi-import
worktree: G:/CODEX/New Manga.worktrees/TASK-041-zcode
integration_commit: null
---

# TASK-041：MOBI 导入路线（承接 TASK-023 遗留 `BLOCKED`）

**READY（2026-09-18 用户批准"两项都批准"——本项为 MOBI 解析依赖）**：Owner=`ZCode`、Reviewer=`Codex`（**非作者**）、base=`904fca1`、branch/worktree 见顶部元数据。开工前把 `status` 改为 `in_progress`。

**改派说明（2026-09-18，经用户确认"适合交给 ZCode"）**：Owner 由 `DeepSeek Harness` 改为 `ZCode`（属"独立 Feature/长任务实现"职责面；原 `agent/deepseek/TASK-041-mobi-import` 分支与 worktree **无任何提交**，已按命名约定移除并重建为 `agent/zcode/**`）。Reviewer 保持 `Codex`（非作者）。

## 来源

[TASK-023 Handoff](../handoffs/TASK-023-7fa9118.md) 第 25/52 行登记的遗留：

> pypdfium2 仅覆盖 PDF（U-2 批准范围）；**MOBI 无批准解析依赖 → 非 PDF 载荷一律 typed `UNSUPPORTED_FORMAT`**；MOBI 光栅化 **BLOCKED**，解锁条件＝用户批准 MOBI 解析依赖。

用户已批准该依赖。**Codex 选定的依赖**：`mobi==0.4.1`（PyPI 实测存在；纯 Python、无编译扩展、无网络调用）。**注意其上游自 2016 年后基本未更新** → 必须放在**适配器端口之后**，便于日后替换（见 AC ⑤）。

## 目标与范围界定（重要，避免过度承诺）

**本 Task 只做"从 MOBI 容器中提取内嵌页面图像"** —— 漫画类 MOBI/AZW3 的常见形态就是"每页一张图"。**不承诺**对**可重排文本型** MOBI 做 HTML → 页面栅格化：那需要 HTML 渲染引擎（本 venv 的 `PySide6_Essentials` **不含 QtWebEngine**），属另一个量级的依赖与裁决。

- 能提取到内嵌页面图像 → 按既有 **Managed Copy** 纪律落地为 Page（复用 TASK-023 的文档导入用例路径）。
- **只含可重排文本、没有可用页面图像**的 MOBI → **typed fail-closed**（明确 reason，例如"reflowable text-only MOBI 不在批准范围"），**不伪造页面、不静默降级为纯文本**。若你认为产品必须支持后者，**先停下交 Codex 裁决**。

## Acceptance Criteria

- [x] **AC ①（依赖与留证）**：`requirements.txt` **仅新增 `mobi==0.4.1`**（不得顺带升级/新增其他项）；给出**安装前后各一次全仓对照**与 venv 变更记录；确认该包**不发起网络请求**（可静态核对其导入面）。
- [x] **AC ②（解析→带图页面）**：对真实/合成 MOBI 样本提取内嵌页面图像，经 Managed Copy 落地为 Page，排序/来源/重复策略与既有文档导入一致（复用 TASK-023 的用例路径，不另造一套）。
- [x] **AC ③（fail-closed 矩阵）**：下列输入一律**可诊断失败**且**不留下部分导入的脏数据**（事务/清理语义与 PDF 路径一致）：依赖缺失（readiness = `missing_dependency`）、非 MOBI 载荷、**加密/DRM 保护**、截断/畸形容器、文本型无页面图像、以及图像解码失败的页。
- [x] **AC ④（不回归 PDF）**：TASK-023 的 PDF 路径与全部既有用例**逐项不变**（`tests/import_formats/**`、`tests/library/**` 通过数不减少）；MOBI 的新用例**不得**改动 PDF 断言。
- [x] **AC ⑤（可替换性）**：解析器位于**端口/适配器**之后（`application/importing/documents/ports.py` 已有先例），`requirements.txt` 之外**不得**让 `mobi` 类型泄漏进 application 层；Handoff 说明"若上游停更如何替换"。
- [x] **AC ⑥（判别力 + 回归）**：新增用例对**修前代码**失败（放 base `904fca1` 的 `src` 上跑一次并留证）；全仓串跑 **≥5 次**逐次记录（**同一 shell + 同一 venv**，退出码 + passed/skipped 分列）。
- [ ] **AC ⑦** 交付 Handoff、取证，经**非作者** Review（Review 模板、四轴、passed/skipped 分列）与 Codex 集成后才能 done；并在 STATUS 记录 TASK-023 遗留项①关闭。

## 允许修改范围

- `requirements.txt`（**仅** `mobi==0.4.1`）
- `src/application/importing/documents/**`
- `src/infrastructure/importing.py`（如确需拆包须在 Handoff 说明理由）
- `src/bootstrap/app.py`（仅当需要装配新解析器时）
- `tests/import_formats/**`、`tests/library/**`
- `doc/tasks/TASK-041.md`、`doc/handoffs/TASK-041-*.md`、`verification/TASK-041/**`、`doc/STATUS.md`（仅登记关闭关系）

## 禁止范围

- 不得修改 Schema/migration、pipeline seam 本体、路由判定、`AGENTS.md`、其他 Task；不得新增除 `mobi` 之外的依赖。
- 不得放宽/删除既有断言，不得新增 `skip`/`xfail`（依赖缺失走 readiness + typed 失败，**不是** skip）。
- 不得为"让 MOBI 看起来能用"而伪造页面或静默降级（AC-FALLBACK-001 / AC-OPTIONAL-002 口径）。
- 不处理超大 webtoon 解码（由 [TASK-042](TASK-042.md) 承接）。

## 测试要求

- `python -m pytest tests/import_formats tests/library -q -p no:cacheprovider -rs`
- 全仓 `python -m pytest -q -p no:cacheprovider -rs -rf`（≥5 次逐次记录）
- 样本：自制/授权的多页 MOBI、DRM 样本（若可得，否则以加密标志的合成容器替代并说明）、截断样本、文本型样本。

## 依赖、风险与阻塞

硬依赖：TASK-023（已 `done`，文档导入用例与 Managed Copy 纪律）。用户已批准 `mobi` 依赖。

风险：
- **上游停更**：`mobi` 0.4.1 较老 → AC ⑤ 的端口隔离是主要缓解；若样本上不可用，**先回报**再讨论替代（不得自行换包）。
- **可重排文本型 MOBI 的期望管理**：本 Task 明确不支持渲染；若产品需要，须另立裁决（可能牵出 QtWebEngine 级别的依赖）。

## 交付与运行记录

- Handoff：[TASK-041-3230f45](../handoffs/TASK-041-3230f45.md)。Review：尚无（待 Codex，非作者）。证据：[verification/TASK-041/](../../verification/TASK-041/)。
- **最近状态（当前，唯一）**：2026-09-18 ZCode 实现交付 `in_review`。开工先 `git merge master`（实际实现基线 `6ea3dd3`，含 TASK-043 的 `Format_BGR888` 修复；任务书 `base=904fca1` 已被取代，判别力对两锚点均留证）；实现 head=`3230f45`。**范围执行口径**：只做 picture-MOBI 内嵌页面图像提取（`MobiDocumentRaster` lazy import `mobi`，application 层零泄漏）；text-only/DRM/截断/坏页/依赖缺失全部 typed fail-closed 且无脏数据（9 例矩阵）；PDF 断言零改动；`requirements.txt` 仅 +`mobi==0.4.1`（装前/装后全仓 819 passed/0 skipped 一致，@`6ea3dd3` 同 venv 同代码状态对照；3 个纯 Python 传递依赖如实声明）；**MOBI 解码走 `QImage.loadFromData`（Qt 自解码 JPEG/PNG），不产生裸 BGR 缓冲，故无第二份颜色映射——`Format_BGR888` 仍是 pdfium 路径的唯一权威实现**（Handoff「Format_BGR888 复用口径」节）。证据（同口径：PowerShell + `TASK-012-py312` + `PYTHONDONTWRITEBYTECODE=1` + `-p no:cacheprovider`）：定向 `tests/import_formats tests/library` **65 passed/0 skipped** exit 0；判别力修前两锚点 **ImportError exit=2**、修后 9 passed；全仓 ×5 **每次 828 passed/0 skipped** exit 0（=基线 819+9 新例；唯一 warning 为 `mobi` 包自身 `imghdr` 弃用告警，已登记为上游停更实证）。AC ⑦ 待 Codex Review 与集成；STATUS 登记 TASK-023 遗留①随集成关闭。
