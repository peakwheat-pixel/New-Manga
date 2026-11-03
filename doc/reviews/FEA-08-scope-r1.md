---
task_id: FEA-08
reviewer: ZCode CLI fresh session
reviewer_kind: agent
author: dsh-lead
base_commit: e36a7442bd5f704252e4b0af8c63ab4f790000e1
reviewed_head: 7ded8bd37fb9c8f35c3c86defc3c4329edeaf8e1
decision: changes_requested
counts:
  P0: 0
  P1: 3
  P2: 5
verdict: changes_requested
p0: 0
p1: 3
p2: 5
provenance:
  reviewer_session: ZCode CLI 独立 fresh session（未参与 FEA-08 起草、范围处置或实现）
  scope_draft: 'G:\CODEX\New Manga.workspace\FEA-08\FEA-08-scope-draft.md（SHA-256 e1cccebe038f3144199665012661d403dc46920078cc14ff3f066a1a89a36221）'
  task_card: doc/tasks/FEA-08.md @reviewed_head（git blob ff79464be2f1748bc9945172334c68b6954eee19）
  governance_check: 'tools/governance/check.ps1 → PASS (3 warnings, EXIT=0)'
---

# FEA-08 Scope Review r1

## Reviewer 与范围

- **Reviewer**：ZCode CLI 独立 fresh session；由 DSH 派发（scope-review-prompt）。本次只读审查，未参与 FEA-08 起草、范围处置，也不承担其实现。
- **被审对象**：`doc/tasks/FEA-08.md`（proposed）@ `7ded8bd37fb9c8f35c3c86defc3c4329edeaf8e1`，及 workspace 草案 `FEA-08-scope-draft.md`（hash 见 front matter）。行号按被审 head 实测。
- **审查边界**：范围充分性、AC 可判定性、契约/治理一致性、安全与数据边界、三个待决项；不审未编写的实现，不替 DSH 做路径/数值终裁。不得为放行降低既有判据。

## 结论

**Decision: `changes_requested` — P0 0 / P1 3 / P2 5。FEA-08 当前不可置 ready。** 主题范围本身合格：与提案 S3 FEA-08 行交付物一致（隔离原型+能力矩阵/技术报告），OUT 正确排除生产实现，allowed_paths 无 `src/**`/`apps/**`/`experiments/**`，不越界 FEA-09/10/12，"不触真实库/用户文件/AppData"方向正确——**无需缩减范围**。阻断点是三处 P1：AC1 缺 H4 核心判别断言（同一已验证句柄/中途替换不混合/内存映射写）；AC2 的"不永久删除"无可判定操作且回收站作为用户级全局资源的安全处置未写入冻结载体；原型/报告/临时数据路径在提案 §15.4、草案与治理规则间三处口径不一致加 depends_on 指向不存在的 Task ID。全部为文字级最小修订，处置后可置 ready。

## Findings

### F08R1-001 (P1) AC1 未承载 H4 核心判别语义

Task `:52`（草案 `:23`）AC-1 现文只要求"正常读取 digest 一致；外部替换/删除被检测；不可保证时返回 unavailable"。提案 `:465` 的 H4 冻结语义是"稳定读取期间禁止与之冲突的写/替换（通过句柄共享模式验证），计算 digest 并**从同一已验证流解码**，杜绝 check 后按路径另开文件"；H 表 `:794` 边界枚举含**内存映射写**。按现文，一个"检测到替换但读取流混入新内容"或"check 后按路径另开文件"的原型也能通过 AC1，H4 命题未被证明。

**最小修订**（AC1 增加三条可判定断言）：
1. digest 必须取自打开时验证过的同一句柄/流：读取前后以句柄级身份（volume serial + file index）与 size/mtime 比对，一致才成立；
2. 读取中途外部替换/写入的运行结果只能是 unavailable 或完整旧 digest，**不得出现混合/部分新内容的 digest 假成功**；
3. 能力矩阵场景纳入"内存映射写"（H 表 `:794` 明列），不可证则该项标 LIMITED/UNAVAILABLE。

### F08R1-002 (P1) AC2"不永久删除"缺判定操作；回收站全局资源处置未入冻结载体

Task `:53`（草案 `:24`）AC-2 判"证明失败路径不永久删除"，但没有给出判定操作；回收站是 per-volume 的用户级全局资源（无测试隔离区），草案只禁"改变回收站设置"，未覆盖：
1. **判定操作缺位**：应明确 = 失败/取消/中断后目标仍在原路径（保留），或成功回收时存在于回收站且可还原（还原后 digest 与回收前一致）；
2. **清空类 API 未禁止**：`SHEmptyRecycleBin` 等一旦误调会清空用户真实回收站，须明文禁止，并禁止对任何非合成路径发起回收；
3. **合成 fixture 的回收站条目处置未写入冻结载体**："临时树清理"目前只存在于 workspace 派发 prompt 一句话，不是 Task 卡 AC；测试后条目应还原并删除（数量/结果入日志），或显式登记保留；
4. 提案 `:512` 的"路径被替换、结果未知"分支与 `:514`"崩溃恢复先核对 OS receipt/文件事实，不能盲目重发"未进入 AC2 判据。

**最小修订**：把上述四点写入 AC2；"模拟中断"的恢复判据 = receipt + 文件系统事实核对，不得重发 destructive 操作。

### F08R1-003 (P1) 路径口径三处不一致 + depends_on 非存在 Task ID

1. **原型位置**：提案 `:929`（§15.4 FEA-08 行）= "`experiments/` 内 DSH 指定路径"（Git 内；`experiments/` 现存 20+ M2 线实验目录，是既有实践）vs 草案/Task `:58` = workspace 非 Git（hash 登记）；
2. **报告位置**：提案 `:929` = "`doc/design/` 对应报告" vs 草案 `:59` = `doc/research/FEA-08-source-capability.md`；
3. **临时数据**：提案 `:929` = `workspace/tasks/FEA-08/`（治理规则分类表亦无 `tasks/` 类目）vs 草案 = workspace 根级 `FEA-08/`（治理分类表同样无根级形式，但 FEA-02-CORE/03/04/06-RESIDUAL-1/2/07 均已如此，属 FEA 线系列实践）；
4. **depends_on**（Task `:11-12`）：`FEA-00`、`FEA-01` 在 `doc/tasks/` 无同名卡（实际前置 Task 为 `FEA-01-FREEZE-1`，done；FEA-00 是方案切片非 Task），违反模板"depends_on 必须是已存在 Task ID"。

**最小修订**：DSH 一句话裁定统一口径并在 Task 卡登记与提案 `:929` 的有意偏差及理由（如：原型不进 Git 以控制仓库体积；报告归 research；临时数据延续 FEA 线 workspace 根级实践）；depends_on 改为 `FEA-01-FREEZE-1`，FEA-00 以"依据"引用保留、不入 depends_on。

### F08R1-004 (P2) Task 卡 ADJ-001 引用路径错误

Task `:33` 引用 `doc/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md`，实际位置为 `doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md`（AGENTS.md 引用正确）。改为 contracts/ 路径。

### F08R1-005 (P2) H5 负向分支枚举未对齐提案 :512/:513

草案已覆盖失败/取消/部分失败/中断/占用/权限，补齐提案明列的：不可回收（卷/策略）、网络盘限制、**路径被替换**、**结果未知**、目录不可回收则保留（**不得改调永久 rmdir**）。能力矩阵失败分支按此枚举登记。

### F08R1-006 (P2) 能力矩阵结构：证据类型标注 + 二维维度

1. 每项结论标注证据来源类型（measured/mocked/inferred）；**mock/推断不得记 PASS**，上限 LIMITED（标注 mocked）——这是 OUT"无证据的 PASS"条款的机械落点（H 表 `:794`"不能静默使用不稳定 bytes"）；
2. AC4 的"每卷/项"应展开为提案 `:929` 出口定义的二维结构：卷类型（NTFS 本地/USB/SMB/…）× 输入类别（单图/文件夹/ZIP/CBZ/PDF **五类逐项"现状/需新增"结论**）。

### F08R1-007 (P2) H6 判据锚点

匹配口径按提案 `:457`（未变独立图片=强 digest；文件夹=成员身份+digest；容器=成员内容 digest/规范解码像素 digest、尺寸、方向、唯一性对照；重复成员名保持独立 occurrence；感知 hash/OCR 只候选）与 `:469`（GIF 只取首帧；PDF 记录页码与渲染参数）；AC3 报告须按"精确匹配/候选"二分并附判定所用 digest 类型。

### F08R1-008 (P2) 治理卫生三项

- `workspace\FEA-08\implementation-dispatch-prompt.md` 已先行存在：proposed 卡不得实施，该 prompt 只能在 scope approved 后派发；本轮 P1 修订若改变 AC/路径，派发前须同步更新。
- 提案 `:647/:929/:939` 仍写 `G-CONTRACT: OPEN` 系冻结时快照；当前 G-CONTRACT/G-DELETE-CONTRACT 已 CLOSED（2026-11-01，AD-003 §5/STATUS），FEA-08 隔离原型本属"允许隔离原型与技术调研"范围，Task `:33` 已正确标注——提案字节不动，建议 DSH 处置记录说明一句，防后续 Review 误判漂移。
- 置 ready 时按 FEA-07-scope-r1 P2-2 先例收敛元数据：修订后刷新 base_commit 到最终冻结 head；impl reviewer 经 DSH Appointment 后更新 Task `:10` reviewer 字段。

## 待决项裁决建议

1. **隔离测试 SQLite：否（维持草案建议）。** H4/H5/H6 均为文件系统/OS 层能力验证；Source 四表 DDL 未冻（G-CONTRACT CLOSED 的明示边界，AD-003 §5），引入测试 SQLite 会把原型结论与未冻结 schema 耦合；DB 文件在可移动卷上的行为属部署配置/FEA-09+ 问题。建议在 BLOCKED 登记段加一句"测试 SQLite/DB 文件行为不在本卡范围"。
2. **无硬件卷 mock/LIMITED：接受（维持草案建议）。** 依据 H 表 `:794`"无需承诺所有文件系统"；执行上按 F08R1-006 的矩阵标注要求（mock ≤ LIMITED(mocked)，不得 PASS）。
3. **H6 Python 依赖：按草案（标准库 + 已有 Pillow/zipfile 优先）。** 事实补充：标准库 zipfile **不能写**加密 ZIP（仅能读 ZipCrypto）、Pillow 不能生成加密 PDF——加密格式 fixture 若需运行时生成，允许最小新依赖（如 pyzipper，MIT），条件 = 许可兼容登记进技术报告 + 不进生产闭包（原型不发布，不触发 AGPL 整体声明条款）；或改用预生成 fixture 文件（生成方式 + SHA-256 登记）。二选一均可，报告须写明采用方式。

## 范围与契约对照

| 来源 | 复核结果 |
|---|---|
| 提案 S3 `:647` FEA-08 行 | 交付物（隔离 workspace 原型、能力矩阵/技术报告、不触真实库）与 Owner=Codex 均一致；"G-CONTRACT: OPEN"表述已被 2026-11-01 CLOSED 取代（F08R1-008）。 |
| 提案 §15.4 `:929` | write_scopes/路径与草案不一致（F08R1-003①②③）；"五类输入逐项现状/需新增"应入矩阵结构（F08R1-006）。 |
| 提案 `:465`/`:794`（H4） | AC1 判别断言缺口 + 内存映射写未列（F08R1-001）。草案补充的"重命名"检测合理（对应 `:461` 场景），保留。 |
| 提案 `:512-:514`/`:795`（H5） | 判定操作、receipt 核对、失败分支枚举缺口（F08R1-002/005）。 |
| 提案 `:457`/`:469`/`:796`（H6） | 判据锚点补齐后可判定（F08R1-007）；"只给候选、不自动套用"与草案一致。 |
| AD-003 §3.2/§3.6/§3.7/§4 | H4 目标与"稳定读取 lease + digest 强验证"一致；H5 与"独立授权 + 回收站桥 + 失败不降级永久删除"一致；§4 未实现清单（SourceAccessRegistry/回收站桥/ZIP 解码器等）与 OUT 一致，不抢 FEA-09/11/12 范围。 |
| ADJ-001 §3 流程 D / PD 系列 | H5 原型只验证 API 行为与失败分支，不实现产品 D 流程、不动 Core trash/GC——不越界 FEA-12；receipt/不盲发语义应入 AC2（F08R1-002④）。 |
| 09_COLLABORATION §4/§4.3 | governance_version 3；AC `[ ]` + `<<PARTIAL: 待实施>>` 组合合法；allowed_paths 显式含 `verification/FEA-08/**`（evidence_dir）✓；depends_on 违反模板（F08R1-003④）。 |
| WORKSPACE_GOVERNANCE | workspace 根级 `FEA-08/` 与治理分类表不符但为 FEA 线系列实践（F08R1-003③），须 DSH 裁定登记。 |

**越界检查（复核点 1）**：OUT 排除生产 Source/导入实现、Host Registry/grant、Core schema/DB、UI 集成；allowed_paths 仅 doc/verification 路径；H4 原型纯文件系统层（无 Core 命令）、H6 只做 fixtures 可行性（不做 binding/同步）——未见越界 FEA-09/10/11/12。

## 验收与证据

- AC1–AC4 经 F08R1-001/002/006/007 修订后均可判定；现文 AC1/AC2 存在"PASS 定义不足、无法证伪"项（判定操作/判别断言缺位）。
- 证据安排齐备：`verification/FEA-08/**`（命令/EXIT/日志/矩阵）、报告 `doc/research/`、Handoff、原型 hash；默认零写入、opt-in 生成临时树并清理（派发 prompt 已有，须上收到 Task 卡，见 F08R1-002③）。
- 审查安排合规：scope Review（本报告）→ 实施 → 独立 impl Review（DSH Appointment）→ DSH 集成验证；Owner=codex 与提案一致。
- AC4"无生产代码改动"的判据应为：实施 diff 仅落 allowed_paths（`git diff --name-only` 对照）。

## 治理与实跑结果

- `git rev-parse HEAD` = `7ded8bd37fb9c8f35c3c86defc3c4329edeaf8e1`；`git status --short` 起始为空（本报告为本次唯一写入）。当前 checkout 在 `main`，非 linked worktree；未创建/删除/移动任何 worktree，未改源码/Task/证据，未 push。
- Task `:14` base_commit `e36a7442bd5f704252e4b0af8c63ab4f790000e1` 经 `git rev-parse` 验证为真实完整 hash（尾部 `0000e1` 非占位符）。
- `pwsh -NoProfile -File tools/governance/check.ps1`：**PASS（3 warnings，EXIT=0）**——9 个非终态 Task、STATUS/PLAN 预算 80% 均为已知存量，与本卡无关。
- 草案与 Task 卡 hash 见 front matter provenance；workspace `FEA-08/` 目录现存 scope-draft、scope-review-prompt、implementation-dispatch-prompt、空 log 四个文件。

## 冻结与实施建议

**FEA-08 现在不可置 ready。** DSH 处置三项 P1（AC1 三断言、AC2 四判定、路径/depends_on 裁定，全部文字级）并酌情采纳 P2 后，可直接置 ready——范围结构、隔离边界、安全方向本身合格，无需缩减。随后同步更新 `implementation-dispatch-prompt.md` 再派发（Codex 备用位已登记）；impl Review 由 DSH 另行 Appointment。
