---
task_id: FEA-08
reviewer: ZCode CLI fresh session
reviewer_kind: agent
author: dsh-lead
base_commit: 7ded8bd37fb9c8f35c3c86defc3c4329edeaf8e1
reviewed_head: 2870a9fa52b73fdf344cc723e59957d76d60e395
decision: approved
counts:
  P0: 0
  P1: 0
  P2: 2
verdict: approved
p0: 0
p1: 0
p2: 2
provenance:
  reviewer_session: ZCode CLI 独立 fresh session（未参与 FEA-08 起草、r1 处置或修订；修订者=DSH）
  task_card: doc/tasks/FEA-08.md @reviewed_head（git blob 1a9079143dc68aca8b0168412d0bfb95c7e8626b）
  revision_diff: '7ded8bd37..2870a9fa5（cd5692f1b 最小修订 + 2870a9fa5 收录 scope-r1/修订记录/scope-r2 派发；diff 实测=4 文件，Task 卡 60 行，无夹带范围扩大）'
  scope_draft: 'G:\CODEX\New Manga.workspace\FEA-08\FEA-08-scope-draft.md（SHA-256 e1cccebe038f3144199665012661d403dc46920078cc14ff3f066a1a89a36221，与 r1 报告登记一致，未变；修订全部落在 Task 卡）'
  governance_check: 'tools/governance/check.ps1 → PASS (3 warnings, EXIT=0)'
---

# FEA-08 Scope Review r2

## Reviewer 与范围

- **Reviewer**：ZCode CLI 独立 fresh session；由 DSH 派发（scope-r2 prompt）。本次只读审查 + 唯一写入本报告；未参与 FEA-08 起草、r1 findings 处置或 Task 卡修订（修订者=DSH），不承担其实现。
- **被审对象**：`doc/tasks/FEA-08.md`（proposed）@ `2870a9fa52b73fdf344cc723e59957d76d60e395`（blob `1a907914…`）；修订 diff = `7ded8bd37..2870a9fa5` 实测复核。行号按被审 head 实测。
- **审查边界**：r1 八条 findings 的闭环真实性、AC 可判定性、路径口径/依赖/ADJ-001 引用、三个待决项裁决、可否置 ready；不审未编写的实现，不替 DSH 做终裁，不为放行降低既有判据。

## 结论

**Decision: `approved` — P0 0 / P1 0 / P2 2。FEA-08 可置 `ready`。** r1 三项 P1（AC1 判别断言、AC2 判定操作与回收站全局资源处置、路径口径三处不一致 + depends_on 非存在 ID）与五项 P2 全部实质闭环：修订逐字落入 Task 卡且与 r1 最小修订建议一一对应，diff 无夹带范围扩大或判据弱化。两项 P2 均为程序性/派发前置事项（派发 prompt AC 摘要未同步、置 ready 时元数据收敛），不构成放行阻断；条件见「置 ready 条件」。

## r1 findings 逐条闭环核验（核验点 1）

| r1 ID | 级别 | 核验结果 | 证据（Task 卡 @2870a9fa5） |
|---|---|---|---|
| F08R1-001 AC1 缺 H4 判别断言 | P1 | **FIXED** | `:59-62` AC-1 三断言逐字落地：①digest 取自打开时验证过的同一句柄/流，读取前后以句柄级身份（volume serial + file index）与 size/mtime 比对；②中途替换/写入只能是 unavailable 或完整旧 digest，不得混合/部分新内容假成功，杜绝 check 后按路径另开文件（=提案 `:465` 冻结语义）；③矩阵场景含内存映射写（H 表 `:794` 明列），不可证则 LIMITED/UNAVAILABLE。 |
| F08R1-002 AC2 判定操作缺位/回收站全局处置未入卡 | P1 | **FIXED** | `:63` AC-2：判定操作=原路径保留，或回收站存在且还原后 digest 与回收前一致；`:50` OUT 明文禁止 `SHEmptyRecycleBin` 等清空类 API + 仅合成路径（含"对非合成路径发起回收"禁止，`:49`）；fixture 回收站条目测试后还原并删除（数量/结果入日志）或显式登记保留——已从派发 prompt 上收到 Task 卡；`:63` 末句 receipt + 文件系统事实核对、不重发 destructive（=提案 `:514`）。四点全落。 |
| F08R1-003 路径口径三处不一致 + depends_on | P1 | **FIXED** | `:34-38` 新增「路径口径裁定（有意偏差登记）」段：prototype\ 非 Git / doc/research/ / tmp\ 三点偏差 + 理由，与提案 `:929` 的偏差有登记有理由；`:11-12` depends_on=`FEA-01-FREEZE-1`（实测存在于 `doc/tasks/` 且 `done`），FEA-00 仅作依据引用（`:39`）。 |
| F08R1-004 ADJ-001 引用路径 | P2 | **FIXED** | `:31` = `doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md`。 |
| F08R1-005 H5 负向分支未对齐 :512/:513 | P2 | **FIXED** | `:63` 覆盖提案 `:512-:514` 分支：不可回收卷/策略、网络盘限制、路径被替换、结果未知、目录不可回收则保留且不得改调永久 rmdir——与 r1 要求的枚举逐项对应。 |
| F08R1-006 矩阵证据类型 + 二维结构 | P2 | **FIXED** | `:65` AC-4：二维 = 卷类型（NTFS 本地/USB/SMB/…）× 输入类别（单图/文件夹/ZIP/CBZ/PDF）逐项"现状/需新增"（=提案 `:929` 出口定义）；每项标注 measured/mocked/inferred，mock/推断不得记 PASS、上限 LIMITED(mocked)。 |
| F08R1-007 H6 判据锚点 | P2 | **FIXED** | `:64` AC-3 按 `:457/:469`：二分精确匹配/候选 + 附判定 digest 类型；图片强 digest/文件夹成员身份+digest/容器成员内容 digest+规范解码像素 digest、尺寸、方向、唯一性；重复成员名独立 occurrence；感知 hash/OCR 仅候选；GIF 仅首帧；PDF 记录页码与渲染参数。逐项与提案原文核对一致。 |
| F08R1-008 治理卫生三项 | P2 | **PARTIAL（非阻断）** | ②G-CONTRACT 提案快照说明：**FIXED**——`:31` 写明"提案内 'OPEN' 为冻结时快照，字节不动"；①派发 prompt 同步：**PARTIAL**——路径部分已同步（prototype\、doc/research/），但 AC 判据摘要仍为 r1 前旧口径（见 F08R2-001）；③base_commit/reviewer 收敛：**未到期**——base_commit 已刷至 `7ded8bd37`，r2 批准后须再刷至最终冻结 head（F08R2-002）。 |

无掩盖、无降级：全部修订为加强判据方向，未见任何一处比 r1 被审版本更弱的表述。

## 核验点详述

### 2. AC 判定充分性

- **AC-1 → H4**：三条断言各自可证伪（句柄级身份比对是 Windows `GetFileInformationByHandle` 可得的具体量；"混合 digest 假成功"有明确失败形态；内存映射写为具名场景），组合后覆盖 H 表 `:794` 的核心命题"不能证明则标受限/不可用，不能静默使用不稳定 bytes"。场景枚举（替换/重命名/删除/断连/共享写/内存映射写）在目标段 `:43` 完整冻结，AC-1 断言③把 H 表明列的内存映射写钉入矩阵，其余场景经目标段 + AC-4 卷类型维度合读可判定——足以支撑 H4 结论，不再要求加码。
- **AC-2 → "绝非永久删除"**：判定操作双向覆盖（失败/取消/中断 → 原路径保留；成功 → 回收站存在且还原后 digest 与回收前一致），使"不永久删除"从口号变为可执行检查。部分失败场景未在判定操作中逐字枚举，但判定操作按文件粒度适用（成功项走回收站分支、失败项走保留分支），目标段 `:44` 已列"部分失败"——可判定，无需修订。unknown 分支（"结果未知"）明列 `:63`；恢复路径 receipt+文件系统事实核对、不重发 destructive 与提案 `:514` 崩溃恢复语义对齐。合成 fixture 条目处置已入冻结载体（Task 卡），消除了"仅存于派发 prompt"的 r1 缺陷。
- **AC-3 → H6**：判定口径与 `:457/:469` 逐项锚定（见 F08R1-007 行），H 表 `:796` 场景清单（PDF 重生成、ZIP 重编码/重复名、GIF/色彩/方向、密码格式→"加密格式"）在目标段 `:45` 全数在列；"只给候选"边界保留。
- **AC-4**：二维矩阵 + measured/mocked/inferred 口径使 OUT"无证据的 PASS"条款有了机械落点（mock ≤ LIMITED(mocked)）；"无生产代码改动"判据 = 实施 diff 仅落 allowed_paths（`git diff --name-only` 对照；allowed_paths 无 `src/**`/`apps/**`/`experiments/**`）。

### 3. 路径口径、依赖与引用

- **偏差登记可接受**：三点偏差（原型非 Git / 报告归 research / 临时数据 workspace 根级）均有理由且与既有实践吻合——`doc/research/` 现存 11+ 份 DIAG/M2 线研究报告（研究类归 research 是仓库既有实践）；FEA-02-CORE/03/04/06/07 均用 workspace 根级目录（r1 已核实）；原型不入 Git 与 AD-003 `:128`"允许隔离原型与技术调研"（未限定位置）不冲突。偏差+理由已写入 Task 卡冻结载体，提案 `:929` 字节不动、以登记代替改写，处置方式正确。
- **depends_on**：仅 `FEA-01-FREEZE-1`（存在、done）；符合模板"depends_on 必须是已存在 Task ID"。FEA-00（方案文档）以依据引用保留，不再冒充 Task。
- **ADJ-001 路径**：`doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md` 正确。

### 4. 三个待决项裁决（核验点 4）

| 待决项 | Task 卡裁决 | 与 r1 建议一致性 | 冻结载体 |
|---|---|---|---|
| 隔离测试 SQLite | **否**——"测试 SQLite/DB 文件行为不在本卡范围（Source DDL 未冻，耦合未冻结 schema 会污染结论）"（`:55`） | 一致（r1：四表 DDL 未冻，避免与未冻结 schema 耦合；AD-003 `:128` 边界背书） | BLOCKED 段 ✓ |
| 无硬件卷 mock/LIMITED | 接受——BLOCKED `:54` LIMITED/UNAVAILABLE 交产品裁决 + AC-4 "mock 不得 PASS（上限 LIMITED(mocked)）" | 一致（含 r1 要求的执行口径） | BLOCKED + AC-4 ✓ |
| H6 加密格式 fixture | 二选一：最小新依赖（登记许可+不进生产闭包，示例 pyzipper MIT）或预生成 fixture+SHA-256 | 一致（r1 两选项原样；"技术报告含依赖/许可"承载采用方式披露） | AC-4 ✓ |

三项均已从"待决定"改为带出处的确认项（`:71-74`）。

### 越界复核（沿用 r1 边界）

OUT 排除生产 Source/导入实现、Host Registry/grant、Core schema/DB、UI 集成；allowed_paths 仅 `doc/tasks|research|handoffs|reviews/FEA-08-*` + `verification/FEA-08/**`；AC-4 "无生产代码改动"；不触 FEA-09/10/11/12 范围——修订未改变任何边界，越界结论维持 r1（无越界）。

## Findings（本轮新增）

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| F08R2-001 | P2 | `G:\CODEX\New Manga.workspace\FEA-08\implementation-dispatch-prompt.md`（AC 摘要段） | 派发 prompt 路径已同步（prototype\、doc/research/），但 AC 摘要仍为 r1 前旧简化口径：无同一句柄/流+句柄级身份断言、无"混合 digest 假成功"禁止、无内存映射写场景、无清空类 API 禁止、无 fixture 还原处置、无 measured/mocked/inferred 与 mock≤LIMITED 口径。虽有"以 Task 卡冻结 AC 为准"声明，摘要与冻结判据不一致会误导实现者优先级。 | 该文件 08:38 版（2249 B）与本 Task 卡 `:59-65` 逐条比对（本次审查实测） | 派发实施前把 AC 摘要同步为冻结 AC 判据（或直接改为"见 Task 卡 AC-1…AC-4"指针式引用） | open（r1 008① 的延续义务） |
| F08R2-002 | P2 | `doc/tasks/FEA-08.md:13` | 置 ready 程序性收敛未完成：base_commit 现为 `7ded8bd37`（r1 收录 head），本报告批准落 commit 后冻结 head 将再次前移；reviewer 字段仍为"待 scope-r2 + impl Review appointment" | `git diff 7ded8bd37..2870a9fa5 -- doc/tasks/FEA-08.md` front matter 段 | 置 ready 时把 base_commit 刷新到最终冻结 head；impl Review 经 DSH Appointment 后更新 reviewer 字段（FEA-07-scope-r1 P2-2 先例） | open（r1 008③ 的到期执行） |

## 治理与实跑

- `git rev-parse HEAD` = `2870a9fa52b73fdf344cc723e59957d76d60e395`；`git status --short` 起始为空（本报告为本次唯一写入）。当前 checkout 在 `main`，非 linked worktree；未创建/删除/移动 worktree，未改源码/Task/证据，未 push。
- `git diff 7ded8bd37..2870a9fa5`：仅 `doc/TASK_LEDGER.md`（+FEA-08 追踪计数）、`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md`（追加）、`doc/reviews/FEA-08-scope-r1.md`（收录）、`doc/tasks/FEA-08.md`（60 行最小修订）——与"按 scope-r1 最小修订 + 收录"宣称一致，无夹带。
- `pwsh -NoProfile -File tools/governance/check.ps1`：**PASS（3 warnings，EXIT=0）**——9 个非终态 Task、STATUS/PLAN 预算 80% 均为已知存量，与本卡无关。
- workspace `FEA-08/`：scope-draft（hash 与 r1 登记一致，未变）、scope-review-prompt、implementation-dispatch-prompt（见 F08R2-001）、两个 raw log。草案 AC 与 Task 卡 AC 不同步属预期（草案为历史输入，hash 固定；修订载体是 Task 卡）。
- 依据锚点均经实测：提案 `:457/:465/:469/:512-:514/:647/:794-:796/:929`、AD-003 `:128`（G-CONTRACT CLOSED 边界：允许隔离原型与技术调研、禁止释放 FEA-09/11/12/13 实现）、STATUS（当前 Task=FEA-08 proposed；G-CONTRACT/G-DELETE-CONTRACT 均 CLOSED 2026-11-01）。

## 置 ready 条件与下一步建议

**FEA-08 可置 `ready`。** 程序（对 DSH）：

1. 收录本报告与 Task 卡 approval 字段更新（`scope-r2 approved（ZCode，P0=0/P1=0/P2=2）`）时，把 base_commit 刷新到该冻结 commit（F08R2-002）。
2. 同步 `workspace\FEA-08\implementation-dispatch-prompt.md` 的 AC 摘要与冻结 AC 一致（F08R2-001），再派发实施（Owner=codex，与提案 S3 行一致；STATUS 记录 Codex 备用位）。
3. impl Review 由 DSH 另行 Appointment（上下文独立），完成后更新 reviewer 字段。

无需缩减或扩大范围。
