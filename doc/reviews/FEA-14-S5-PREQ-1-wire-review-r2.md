---
task_id: FEA-14-S5-PREQ-1
reviewer: fresh 独立上下文子 agent（续接 r1；未参与本卡写作/实现）
reviewer_kind: subagent
author: dsh
base_commit: b7aaccfbc
reviewed_head: 5459c9220
decision: approved
---

# Review：FEA-14-S5-PREQ-1 AC2/AC3 处置后复核（wire r2）

## 0. 审查对象、环境与字节锚

- 仓库 `G:\CODEX\New Manga`，`main`；**HEAD = `5459c92201a7138b971fc39b95642cbe0d69dc00`**。审查开始 `2026-11-10T09:46:01+08:00`、结束 `09:52:23+08:00` 两次实测 `git status --short` 均 **clean**（本报告写入前；报告本身是审查后唯一新增 untracked 文件）。
- 被审增量：`b7aaccfbc..5459c9220`，**单提交 13 文件**（`git diff --name-status`）：
  - 契约/卡面：`doc/plan/FEA-C07_API_INVENTORY.md`（35/1）、`doc/plan/FEA-CONTRACT-FROZEN-C07.md`（21/7）、`doc/plan/FEA-CONTRACT-FROZEN-C01b.md`（9/0）、`doc/plan/FEA-CONTRACT-FROZEN-C09.md`（9/0）、`doc/tasks/FEA-14-S5-PREQ-1.md`（6/2）
  - 复核/载体：`doc/reviews/FEA-14-S5-PREQ-1-wire-r1.md`（125/0，新增 §8）、`doc/reviews/CONTRACT-UNFREEZE-2026-11-10-C07.md`（60/0）、`doc/reviews/ADJ-2026-11-10-FEA14-NEW-DATA-CATEGORIES.md`（77/0）、`doc/reviews/FEA-14-S5-PREQ-1-wire-review-r1.md`（120/0，r1 报告入库）
  - 证据：`verification/FEA-14-S5-PREQ-1/ddl-v10-plan.md`（4/3）、`verification/FEA-14-S5-PREQ-1/logs/{api-inventory,gates-check,gates-pins}.log`
- 被审字节锚（工作树 SHA-256）：
  - inventory `5673b1c4b53e69ec36f1897ea5bb0ba8eeedbf437320381ee1b2a04448bf2aa6`
  - frozen C07 `c3f9eee2341c9f7c59d3440b3e44defbdd7fd37b0c226e1e772e6ab110aaa725`
  - frozen C01b `754c099b7a01abc28c94c6bd0f07d076fdb98c60cb8471b5908c2bebc0082961`
  - frozen C09 `2908f2e4c0cc14a8c8648cd65896b0c297097c4268aae25a5b1562ca797800b1`
  - card `869d7ac0f171ad1e4d5219bf0f5810bb640f6d38078e5976883f686bcfa089d3`
  - wire-r1 `30e6bbd61b508cbfc74df16e1de1d35db435c9229721e8b7ca48de3fd63f0397`
  - UNFREEZE `0e0da4388e98f60e554b2da2786218d6df25451a7b772f074a979c1e33d7f743`
  - NEW-DATA ADJ `37ddba96abbb850dea37d5aec708ecb5125b700b962ece1ef94c70cbd128bad7`
- 只读纪律：仅写本文件；未改源码/契约/卡面/证据，未 commit/push；临时校验脚本与日志仅写仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-S5-PREQ-1-r2\`。

## 1. 结论

**`approved`。**

| 计数 | 值 |
|---|---|
| P0 | **0** |
| P1 | **0**（r1 的 P1/R-001 已关闭） |
| P2 | **0** |
| P3 | **6**（文档精度/证据措辞/待回填类残余，不阻断） |

r1 的 5 个 P1/P2 finding（R-001…R-005）**全部 CLOSED**；r1 P3 项中 R-006/R-007/R-009/R-010 CLOSED，R-008 为 **PARTIAL**（其残余即 R2-002，P3、不阻断）。交付提交 13 文件全部落在 16 条 allowed_paths 内且工作树 clean；C01b/C09 冻结记录 append-only 锚点（9/0，契约草案零改动、pins 不变）；prompt_templates 载体矛盾消除且 DDL 计划同步；fonts/ 与 SC-11 优先级已写明。剩余 6 项 P3 均为可随收口一并处理的文字/证据精度问题（§3）。

## 2. r1 findings 关闭判定

| r1 ID | r1 级别 | 判定 | 依据（本审查实测/代码） |
|---|---|---|---|
| R-001 | P1 | **CLOSED** | wire-r1 §8（`:86-118`）新增 25 行 per-command 映射：P1–P25 顺序、Host command id、Core wire、`minor=3`、request/response keys 均齐；脚本校验：25/25、无重复 Host id/Core wire、与现有 registry 字符串及 88 个既有 CoreCommand 无碰撞、与 §2–§6 主表及 inventory 计划节（25 行）名称/返回类型/切片逐条一致（0 issues）。§1.4（`:12`）已改为同时锁「名称/返回类型/语义/Host id/Core wire/minor/payload 键」；§1.2（`:10`）行号改为 `:43`。残余 P3 见 R2-004 |
| R-002 | P2 | **CLOSED** | `git status --short` 审查开始/结束均 clean；提交 `5459c9220` 的 13 个文件按卡面 allowed_paths（`:21-36`）逐项 pattern 匹配 **OUT=0**；`ADJ-…NEW-DATA-CATEGORIES.md` 已在 allowed（`:26`），`CONTRACT-UNFREEZE-*.md` 与两份 C01b/C09 冻结记录也在 allowed（`:27,31,32`）。残余 P3（AC6 证据措辞）见 R2-005 |
| R-003 | P2 | **CLOSED** | `FEA-CONTRACT-FROZEN-C01b.md:85-92`、`FEA-CONTRACT-FROZEN-C09.md:110-117` 新增 append-only errata 节，引用本 ADJ 与 S5 范围 ADJ；两份文件 diff 均 **9 增 / 0 删**（纯追加）；C01b/C09 **契约草案零改动**（pins 仍 `3c9f5af7…` / `dc51226b…`，verify_pins 验证）；18 pins 计数不变。残余 P3（"18 pins 不变"措辞）见 R2-003 |
| R-004 | P2 | **CLOSED** | `ADJ-…NEW-DATA-CATEGORIES.md:20-27` 统一 `prompt_templates` 载体为 `library.db`（仅用户自建），内置模板不落库；§3 表（`:48-52`）同口径；DDL 计划 `verification/FEA-14-S5-PREQ-1/ddl-v10-plan.md:37-45` 已同步（去掉「条件性/二选一」，表只存用户自建、内置为代码常量，删除条件说明）。残余 P3（AC4/scope 文档旧条件句）见 R2-001 |
| R-005 | P2 | **CLOSED** | `ADJ-…NEW-DATA-CATEGORIES.md:31-36` 明确优先级：用户导入字体资产（数据根 `fonts/` + `font_assets` 条目）属 SC-10b 默认包含；SC-11「独立可选项」保留为备份预览显式排除（排除后不覆盖 verified，SC-13）；外部原文件默认不包含、不随包字体；不修改 SC-10a/SC-11 字节。`FEA-CONTRACT-FROZEN-C01b.md:92` 同步该澄清；C-01b/C-09 字节与 pins 不变。残余 P3（外部原始字体文件边界）见 R2-006 |
| R-006（r1 P3） | P3 | **CLOSED** | inventory `:3` 与 `:104` 链接均改为 `../reviews/CONTRACT-UNFREEZE-2026-11-10-C07.md`；`doc/plan/reviews/` 不存在，已无 `](reviews/` 断链 |
| R-007（r1 P3） | P3 | **CLOSED** | 卡 AC2 `:65` 与 wire `:10` 均改为 `FEA-CONTRACT-FROZEN-C07.md:43`（实际第 43 行为「实现注意」）；活跃文档中不再有 `:42` 引用（仅历史 FEA-05 review 与 r1 报告保留旧文，非现行） |
| R-008（r1 P3） | P3 | **PARTIAL（P3，不阻断；残余记入 R2-002）** | 冻结记录新增 v1.2 记录（`：52-61`，含任务/载体/变更/pin/复核/不构成），但新增节编号为 `## 5.`，与文件原有 `## 5. 变更记录`（`:85-91`）**编号重复/顺序错位**（新 §5 位于 §4 与 §1A 之间，原 §5 仍在其后）；原 §5 变更表也未补 v1.2 行（同一问题在 §3 以 R2-002 跟踪，避免重复计数） |
| R-009（r1 P3） | P3 | **CLOSED** | `verification/FEA-14-S5-PREQ-1/logs/` 已提交 3 份日志：`api-inventory.log`（1/54/6=61、`OK: rendered counts match`、EXIT=0）、`gates-check.log`（默认+TaskPath PASS、EXIT=0）、`gates-pins.log`（18/18，C07 `5673b1c4b53e`、EXIT=0）；均记录 `HEAD=b7aaccfbc…`（提交前父提交，见 R2-005 的 provenance 说明） |
| R-010（r1 P3） | P3 | **CLOSED** | inventory 状态行（`:3`）改为「正式成员表与脚本 stdout 一一对应；『S5 计划追加』节属人工预冻结、不计入统计，实现卡落地时并入正式表并重算」；计划节（`:102-104`）同口径。既有 stdout/doc 成员顺序差异仍存在（集合相等；本卡未引入），记为背景观察，不阻断 |

## 3. R2 Findings（均为 P3，不阻断）

| ID | 级别 | 位置 | 事实与影响 | 建议 |
|---|---|---|---|---|
| R2-001 | P3 | `verification/FEA-14-S5-PREQ-1/settings-storage-shape.md:68`；`doc/reviews/ADJ-2026-11-10-FEA14-S5-SCOPE.md:70`；`ADJ-…NEW-DATA-CATEGORIES.md:29` vs `ddl-v10-plan.md:41` | **旧条件句未同步**：AC4 形状文档仍写「提示词模板正文若落库则见 DDL 计划，若落设置则只登记 `ai` section 的引用键」；S5 范围 ADJ §2.6 仍写「AI（`prompt_templates` 若落库；否则 settings section）」——与 R-004「统一落库、不使用二选一」不一致。另 ADJ errata `:29` 说「`builtin` 列可保留…默认为 0」，但 DDL 计划 `:41` 的表已无 `builtin` 列，措辞不一致。影响：实现卡（尤其 AI-1）可能读旧条件产生分歧 | 同步 AC4 形状文档与范围 ADJ（改「统一落库」或加 superseded 注记）；ADJ 与 DDL 计划就 `builtin` 列取舍统一措辞（保留列则写入 DDL，或删除「列可保留」句） |
| R2-002 | P3 | `doc/plan/FEA-CONTRACT-FROZEN-C07.md:52-61`（新 §5）与 `:85-91`（原 §5） | **冻结记录 §5 重复编号（R-008 残余）**：新增 `## 5. v1.2 UNFREEZE 变更记录` 位于 §4 与 §1A 之间，原 `## 5. 变更记录` 仍在文件后部，形成两个 §5 且顺序错位；原 §5 表未补 v1.2 行。影响：记录结构不符合该文件自身 v1.0/v1.1 的 §5 变更表惯例，读者可能漏读 | 二者合并：在**原 §5 变更表**追加 2026-11-10 v1.2 行（新/旧 pin、载体、r1→r2、范围），并把新节重编号（如 §5A）或删除重复节；不影响 pin 值 |
| R2-003 | P3 | `doc/plan/FEA-CONTRACT-FROZEN-C01b.md:87`；`doc/plan/FEA-CONTRACT-FROZEN-C09.md:112` | **「18 pins 不变」措辞不精确**：两处 errata 锚点写「18 pins 不变」，但同一提交中 C-07 pin 已因 AC2 从 `3fdb44e4…` 重算为 `5673b1c4…`；按字面可读成全部 18 pin 值未变。影响：仅措辞精度，无 pin 错误（verify_pins 18/18、C01b/C09 值确实未变） | 改为「本 errata 不改 18 pins 计数；C-01b/C-09 pin 不变；C-07 pin 变更见 AC2 UNFREEZE」 |
| R2-004 | P3 | `doc/reviews/FEA-14-S5-PREQ-1-wire-r1.md:86-118`（§8）；`HostCommandRegistry.cs:237-367` | **§8 的计划值未经验证**：全部 25 条 `minor=3` 是计划假设（既有 Core 命令存在 minor 3/7/8/10/11/13 多种）；未给出 Host channel（app vs host-control）与 payload 值类型/校验约束；新 Host command id/域（`fonts_*`/`editing_*`/`ai_*` 等）需要实现卡扩 `HostCommandRegistry`/`HostCommandDomain` 与冻结命令快照，本包未列步骤；§8 本身未被 C-07 pin 覆盖（wire-r1 非冻结文档），与「预冻结」措辞存在轻微落差。影响：实现卡仍需验证/记录 minor 与 payload，已在 §8 约定「不得静默改」 | 实现卡把「minor/通道/payload 校验」列为必做并回填证据；或由 DSH 在载体/卡面注明 §8 为计划值、pin 只覆盖 inventory 计划节，避免「已冻结」误解 |
| R2-005 | P3 | 卡 `:69`（AC6）；`verification/FEA-14-S5-PREQ-1/logs/*.log`（HEAD 行） | **AC6 证据在交付 head 上为恒真**：改为「`git status --short` 的全部改动（含 untracked）⊆ allowed_paths」，而交付 head 工作树 clean → 该断言空转；日志也未记录交付区间 diff，且日志记录的 `HEAD=b7aaccfbc` 为提交前父提交（自然，但无法直接证明 commit `5459c9220` 的内容）。本审查已独立验证提交 13 文件 ⊆ allowed_paths | AC6 证据改为交付区间（`git diff --name-only b7aaccfbc..5459c9220`）并落日志；日志可在提交后重生成或记录「父 HEAD + 提交哈希」 |
| R2-006 | P3 | `ADJ-…NEW-DATA-CATEGORIES.md:31-36`；`doc/plan/FEA-CONTRACT-FROZEN-C01b.md:92` | **SC-11 解释的边界可再明确一句**：优先级已写清且不改 SC-11 字节；但「外部原文件」聚焦漫画原文件，用户导入字体的**外部原始字体文件**（导入源）与库内 `fonts/` 副本的备份取舍未一句话点明；另把 SC-11「独立可选项」落到「预览可排除」属解释性口径，若 DSH 采用严格 opt-in 读法则应走 UNFREEZE。影响：实现 FONT-1 时可能对导入源文件是否入包产生分歧 | 在 errata §2 R-005 边界补「导入源文件默认不入包（同 SC-10a 口径）；仅库内 `fonts/` 副本默认包含」；并注明 SC-11 解释属 DSH 裁决（如严格读法则另走 UNFREEZE） |

## 4. AC 逐项（本审查复核 AC2/AC3，AC1/AC4/AC5 仅交叉引用）

| AC | 状态 | 依据 |
|---|---|---|
| AC1 七切片裁决 | MET（已提交，未重审） | `ADJ-2026-11-10-FEA14-S5-SCOPE.md` + `FEA-15` append-only 注记 |
| AC2 共用 wire + 一次 UNFREEZE | **MET（r2 approved；载体 §5 r2 记录/冻结 §1B 待回填）** | §8 25/25 一致且无缺列；inventory 旧签名/统计零改动、`--check` 61 EXIT 0；pin 重算 `5673b1c4…` 三方一致、18/18；UNFREEZE 要素齐备；r1 处置记录已在载体 §5，r2 结论由本报告给出 |
| AC3 新数据类别 errata | **MET** | C01b/C09 冻结记录 append-only 锚点（9/0×2）、契约草案零改动、pins 不变；四类数据 backup/cleanup/restore 语义在 ADJ 中覆盖；prompt_templates 统一落库、内置不落库不备份；0 pin 成立 |
| AC4 设置存储形状 | MET（原状，未重审） | `settings-storage-shape.md`；R2-001 指出其 `:68` 为旧条件句，建议同步 |
| AC5 DDL v10 计划 | MET（已按 R-004 同步） | `ddl-v10-plan.md:37-45` 已改为统一落库；`builtin` 措辞见 R2-001 |
| AC6 门禁与零改动 | **MET（本审查重验范围）** | 提交 13 文件 ⊆ allowed_paths（OUT=0）；`git status` clean；check 默认+TaskPath PASS、pins 18/18；无 src/apps/DDL diff；AC6 证据措辞见 R2-005 |

## 5. 门禁实测（命令 + 时点 + EXIT）

| # | 命令 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `python tools/generate_api_inventory.py --check` | 09:48:23 | `OK: rendered counts match FEA-C07 doc`；**1/54/6 = 61** | **0** |
| 2 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 09:48:35 | **PIN AUDIT: PASS (all 18)**；C07=`5673b1c4b53e`；C01b `3c9f5af7`、C09 `dc51226b` 及其余 15 项与 r1 逐项相同 | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/check.ps1` | 09:48:36 → 09:48:38 | PASS（3 warnings：11 非终态 / STATUS 3133 B·30 L 80% / PLAN 6791 B·63 L 80%） | **0** |
| 3b | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-14-S5-PREQ-1.md` | 09:48:36 → 09:48:38 | PASS（同上） | **0** |
| 4 | `Get-FileHash doc/plan/FEA-C07_API_INVENTORY.md -Algorithm SHA256` | 09:47 前后 | `5673b1c4b53e69ec36f1897ea5bb0ba8eeedbf437320381ee1b2a04448bf2aa6` = frozen §1/载体 §1 新 pin；旧 pin `3fdb44e4…` 与 r1 锚 `c67c40e7…` 均保留 | — |
| 5 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 09:46:01 / 09:52:23 | 同一 HEAD `5459c9220…`；工作树两次均 clean | — |

仓外校验日志：`G:\CODEX\New Manga.workspace\temp\FEA-14-S5-PREQ-1-r2\`（`gate1-inventory.log`、`gate2-pins.log`、`gate3-check-default.log`、`gate4-check-taskpath.log`、`check_wire_r2.log`、`check_returns.py` 输出）。
补充脚本校验（EXIT 0）：§8 25/25、无重复、无碰撞、逐条与 inventory/主表一致；提交 13 文件 scope OUT=0；C01b/C09 9/0 append-only。

## 6. 范围与越界

- 交付提交 13 文件全部映射进卡面 16 条 allowed_paths：**OUT=0**；禁止目录（`doc/plan` 之外、`doc/contracts/**`、`tools/governance/**`、`doc/tasks/FEA-13*`）命中 0。
- 无 `src/**`/`apps/**`/`schema.py`/DDL diff；C-01b/C-09 **契约草案零改动**（pins 不变）；C-07 契约内容仅 inventory 文档新增计划节 + 状态行（35/1，唯一删除=状态行旧文），旧 54 成员表/统计逐行不变。
- 结论：**无越界**。本审查写域仅本文件。

## 7. 证据复核

| 证据 | 本审查核对 | 判定 |
|---|---|---|
| `logs/api-inventory.log` | 重跑 `--check` → EXIT 0、1/54/6=61、`OK`；日志同 | 可复现 |
| `logs/gates-pins.log` | 重跑 → 18/18、C07 `5673b1c4`；日志同 | 可复现 |
| `logs/gates-check.log` | 重跑默认+TaskPath → PASS/EXIT 0；日志同 | 可复现 |
| `wire-r1 §8` | 解析 25 行并与 inventory/主表/registry/CoreCommand 交叉比对，0 issues | 通过 |
| `frozen C01b/C09` | diff 9/0×2；pins 未变；引用 ADJ 存在 | 通过 |
| `frozen C07` | §1 新 pin 与实算一致；旧 pin/r1 锚保留；§1B 记「复核进行中」；§5 见 R2-002 | 通过（P3 结构问题） |
| 日志 HEAD | 记录 `b7aaccfbc`（提交前父提交）；提交后本审查重跑验证交付字节 | 可接受（R2-005） |

## 8. NOT_RUN（不得标 PASS）

- 25 条计划命令的**实现/行为** = NOT_RUN（无代码，计划态）。
- Core 侧 per-command `minor`/payload 校验/通道（app vs host-control）与 `HostCommandRegistry`/`HostCommandDomain`/冻结命令快照的注册 = NOT_RUN（未实现；§8 为计划值）。
- 真实备份/恢复/清理行为（fonts/bookmarks/markers/templates）= NOT_RUN（仅文档与既有常量核对：`cleanup.py:41`、SC-B01a 文本）。
- `prompt_templates` 最终落库实现（AI-1）= NOT_RUN；settings 分支已由 R-004 裁决取消，未实现验证。
- AC4 形状文档的同步（R2-001）未做 = NOT_RUN（待 Lead 处理）。
- 双口径 pin（`git cat-file blob` LF SHA-256）记录 = NOT_RUN（本审查按仓库既有 worktree pin 口径验证，与 §1A 建议的双口径一致但未额外登记 LF 值）。

## 9. 待回填（approved 后的收口动作，不阻断本结论）

1. 在 `CONTRACT-UNFREEZE-2026-11-10-C07.md` §5 追加 **r2 approved** 记录（本报告路径/结论/字节锚），并在 `FEA-CONTRACT-FROZEN-C07.md` §1B 回填 approved 与复核字节；随后才可视为 UNFREEZE 生效。
2. 卡面 AC2/AC3 勾选为 `<<MET>>` 并引用本 r2 报告；`ADJ-2026-11-10-FEA14-NEW-DATA-CATEGORIES.md` 的 `status: in_progress` 按项目惯例更新。
3. 随收口处理 R2-001…R2-006（建议在本次 closeout 提交前完成，避免残留旧条件句/重复 §5/证据措辞）。
4. STATUS/PLAN/TASK_LEDGER 的 PREQ 状态与 `delivery_head`/`canonical_evidence_status` 由 Lead 按生命周期刷新。

## 10. 审查者声明

本报告由未参与本卡写作的独立上下文子 agent 出具（与 r1 同一审查上下文续接；r1 报告为本审查者上一轮产出，不构成对实现的参与）。只读审查，唯一写入为本文件；所有 PASS 均基于本次实测或逐行静态核对，未实测项已在 §8 记 NOT_RUN；被审字节以 §0 SHA-256 锚定。
