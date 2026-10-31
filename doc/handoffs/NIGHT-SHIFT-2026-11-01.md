# NIGHT SHIFT 2026-11-01 晨报（DSH 自主夜班）

**一句话结论**：SAFETY 线（6→12）全部收尾、17 条 P2 零悬挂；新架构四份契约中 **C-01b/C-02/C-03 已 `approved`**、C-11 待 r3 极窄面；冻结只差你回 `R`（AD-002 口径）与 U-04/U-05 三个选择。

## 主线到哪

| 项 | 状态 | 证据 |
|---|---|---|
| REALUSE-DATA-SAFETY-6 | **done**（AC1/AC2/AC3 MET；Review approved；P2×3 open） | 集成 `011b19bbf`；证据 `verification/REALUSE-DATA-SAFETY-6/`；Review `doc/reviews/REALUSE-DATA-SAFETY-6-review.md` |
| 集成验证 | 通过 | build 0 警告/0 错误；test 394 通过 / 0 失败 / 7 跳过（401）；check.ps1 PASS |
| REALUSE-DATA-SAFETY-7 → **11** | **全部 `done`**：7（`aaed145e9`）/ 8（`84b9f4319`）/ 9（`9aa6758b6`）/ 10（`8b15adbfe`）/ 11（`a1b82ffb9`） | 各 `doc/reviews/REALUSE-DATA-SAFETY-*-review.md`；证据 `verification/REALUSE-DATA-SAFETY-*/` |
| REALUSE-DATA-SAFETY-12（收尾审计） | **done**：14 条 → 复核修正为 **17 条 P2**（当轮 5 + 转后续 12、0 悬挂） | `verification/REALUSE-DATA-SAFETY-12/safety-line-audit.md`；Review `doc/reviews/REALUSE-DATA-SAFETY-12-review.md` |
| 当前 Task | **FEA-GOV-4**（C-02/C-03/C-11 三份草案独立复核；C-02 复核中） | `doc/tasks/FEA-GOV-4.md` |

## 新架构到哪

| 项 | 状态 | 证据 |
|---|---|---|
| FEA-00 方案 r4 | **`approved`**（0 P0 / 0 P1 / 9 P2） | `doc/reviews/FEA-00-dsh-r8.md`、`doc/reviews/FEA-00-dsh-r8-appointment.md`；方案 `74a772167`，sha256 `8895aebe…` |
| r7 的 2×P1 | 均已实质处置（R7-01 权威层同步、R7-02 PD-01–PD-10 全部落位） | r8 §3 |
| r7 的 6×P2 | 全部有处置（R7-05/07/08 无残留） | 同上 |
| 契约清单草案 | 已吸收 r8；C-04c 已由 r4 §9.1 覆盖；G-01/G-03 关闭 | `doc/plan/FEA-01_CONTRACT_DRAFT.md` |
| **C-01b 存储契约草案** | **v5，r5 独立复核 `approved`（P0×0 / P1×0 / P2×3 非阻断）**；r1→r5 共处置 P0×1、P1×3、P2×20；条款 SC-01…SC-39 覆盖 AD-003 §3.1–§3.8 全部 38 单元 | `doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md`；报告 `doc/reviews/FEA-C01b-r{1..5}.md` |
| **C-07 端口清单** | 由代码生成：54 成员（`IReaderProgressSink` 1 + `IHostController` 47 + `IRunController` 6） | `doc/plan/FEA-C07_API_INVENTORY.md` |
| **C-02 V11R 修订单** | V-01…V-08 逐条（项目/写权/令牌组/状态/例外/DS/ThemeEngine/UI 结构）；U-04 落点为 V-05（Fluent per-scheme 例外） | `doc/plan/FEA-C02_V11R_AMENDMENT_DRAFT.md` |
| **C-03 外观持久化** | `presentation-settings.json` 单点写者 + 10 行字段迁移矩阵 + 动效三态/三类；U-05a/U-05b 待裁决 | `doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md` |
| **C-11 候选表口径** | §12.1 主表 + §15.6 补充列合并引用；L1–L4 等级；H1–H4b Gate 判据；FEA-04b 硬前置 | `doc/plan/FEA-C11_TASK_TABLE_ALIGNMENT_DRAFT.md` |
| 冻结前置 | ① C-01b r5 `approved` ✅；② AD-003 `G-REVIEW` → **`SATISFIED`**（FEA-GOV-1）✅；③ AD-002 责任表口径 **待你回 `R`**（FEA-GOV-2 提案 v3 `approved`，推荐 D 零字节）⏳；④ `check.ps1` PASS ✅ | `doc/AD-003_...md` §5；`doc/reviews/FEA-GOV-1-ad003-review.md`；`doc/plan/FEA-AD002_AMENDMENT_PROPOSAL.md` |
| **C-01b 冻结包** | `approved`（r3，0 P0/0 P1/3 P2）；四份条件核对 + 11 步四阶段序列 + 回退表 + UNFREEZE 载体 | `doc/plan/FEA-CONTRACT_FREEZE_PACKAGE.md` |
| **C-02 复核** | **`approved`**（r2，0 P0/0 P1/3 P2 非阻断；r1 的 4 P1 全部处置） | `doc/reviews/FEA-GOV-4-c02-r2.md` |
| **C-03 复核** | **`approved`**（r2，0 P0/0 P1/3 P2；写者上移 Appearance coordinator） | `doc/reviews/FEA-GOV-4-c03-r2.md` |
| **C-11 复核** | r1 `changes_requested`（2 P1）→ 已修，r2 复核中 | `doc/reviews/FEA-GOV-4-c11-review.md` |
| **C-04b 草案** | 删除协议字段/码表（`PreviewPermanentDeleteBooks` + `inventory_digest` + 6 码表），未复核 | `doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md` |

## 待你拍板（可直接回 A/B/C）

1. **MA-11 旧库迁移策略**（SAFETY-6 AC3，涉及用户数据）
   - A：保持现状（旧壳仍可写旧根）——零风险但问题保留
   - **B（推荐）**：只读封存冲突入口 + 迁移旧根（需备份 + 授权）
   - C：阻断旧壳写入 + 明确提示，不迁移
   - 理由：真实数据根迁移是幂等空操作，真风险是旧壳并发写旧根。

2. **MA-20 安装脚本隔离**（部署流程）
   - **A（推荐）**：`install.ps1` 默认隔离根 + `install-verify.ps1` 改实测断言
   - B：保持真实根 + 二次确认
   - C：仅文档化，不改脚本（不推荐：当前 `data_root_untouched=$true` 是硬编码假断言）

3. **U-02 彻底删除是否解除 Lock/current/pinned**（FEA 契约方向）
   - **A（推荐）**：沿用 ADJ-001 冻结语义（用户显式彻底删除可解除；仅回收站到期 GC 拦截）
   - B：方案原提议（彻底删除一律拒绝）
   - 理由：与 `M2-C1 §5.11.2` 现行一致，避免双权威。

4. **U-03 首阶段浮窗与主窗同区域编辑**
   - A：只读镜像（简单）
   - **B（推荐）**：按 `(SessionId, RegionId)` draft owner + 字段分域并发

5. **U-04 Fluent 视觉是否豁免 V11R 圆角/阴影/模糊禁令**
   - **A（推荐）**：起草 per-scheme 例外登记（与 R-14 同构），不整体豁免（已落在 [C-02 V-05](plan/FEA-C02_V11R_AMENDMENT_DRAFT.md)：材质/层次/圆角三行，仅 `builtin.fluent` 生效且强制走令牌）
   - B：完全豁免

6. **AD-002 口径（FEA-GOV-2，C1–C4）** —— 冻结前置③
   - **回 `R`（推荐）** = C1=**D 零字节**（不改 AD-002，解释由 AD-003 §2 + C-01b SC-07/SC-01 承担）、C3=哨兵保持 `Managed Copy`、C2/C4 无需回答
   - 若你要正文同步：回 `C1=A`（纯追加，需接受 AD-003 §2:28/§7① 配方扩展 + 再修订/再 pin）或 `C1=B`（改 `:28`，破坏字节保留声明）

7. **U-05a 外观持久化是否纳动效三态/三类**（C-03）
   - **A（推荐）**：纳入 `motion.mode = auto/full/reduce` + 三类（navigation/feedback/decorative），旧 `ReducedMotion=true` 映射为 `reduce`
   - B：只保留布尔 `ReducedMotion`（Fluent 动效分级无法表达）

## 明早推荐第一步

**先裁决 1、2、6**（各回一个字母 / 一个 `R` 即可）。第 6 项是 C-01b 冻结的最后一关：回了 `R`，我就按 D 案落裁决记录并冻结 C-01b/C-02/C-03/C-11，然后释放第一个 FEA 实现候选 Task。第 3–5、7 项影响后续契约细节，晚点回也不阻塞。

---

## 夜班日志（追加）

### 01:26 启动
- goal 已 active（roundsStarted=1）；SAFETY-7 worktree 建立（`29d06c462`）。
- 开始 AC1（R-001 并发 NRE）实现。

### 02:00 SAFETY-7 AC1/AC2/AC3 完成，进入独立 Review
- **AC1（R-001）**：修复 `ReaderOverlayViewModel` 并发 NRE —— await 前局部固化 book/page/pageCount；`CloseAsync` 先等待在途保存、再执行一次权威重读。新增并发用例 **6/6**；全量 **395 通过 / 0 失败 / 7 跳过（402）**；**负向对照 1 failed（EXIT=1）**已真实复现。
- **AC2（R-002）**：`.gitattributes` 加 `verification/REALUSE-DATA-SAFETY-6/** text eol=lf`；强制 LF 检出；重算 11 条 pin（2 条更新）。因检查器"工作树不匹配→回退 commit blob"机制，SAFETY-6 的 4 条代码 pin 一并改为 blob(LF) 基准（否则 SAFETY-7 改代码后 SAFETY-6 pin 必红）。
- **AC3（R-003）**：日志格式含 `generated_at` / 完整命令 / `EXIT=` / 负向对照可复现步骤。
- 提交：`306ae09ae`（实现+证据）→ `8a343d76f`（pin+manifest）→ `58596949a`（manifest pin）；`check.ps1` **PASS (3 warnings)**。
- 独立 Review 已派发：task-4 / `safety7-reviewer` / reviewed_head `58596949a`。

### 02:10 SAFETY-7 完成并集成；SAFETY-8 已开
- **Review approved**（P0=0 / P1=0 / P2=5；AC1/AC2/AC3 全 MET）；Reviewer 独立复现负向对照 1 failed/EXIT=1；pin 复核 SAFETY-6 12/12、SAFETY-7 10/10。
- 集成：**`main@aaed145e9`**（merge `task/REALUSE-DATA-SAFETY-7`，Review 报告 `2a0528851`）。
- 5 条 P2 登记为 **REALUSE-DATA-SAFETY-8**（`ready`）：F-001 证据文档计数、F-002 负向配方可复现、F-003 日志 cwd/filtered、F-004 异常捕获限定、F-005 关闭期保存门禁。
- 新架构线：**Codex 修订任务已派发**（R7-01/R7-02 + 6 条 P2，`codex exec` 运行中）；完成后对**新 sha256** 派独立复审。

### 02:15 SAFETY-8 实现完成，进入独立 Review
- **AC1（F-001/F-002/F-003）**：`ac2-eol-pin.md` 重写为 12 条对照（5 条变化：3 代码 + 2 证据）；`ac1-negative-control.md` 改 post-delivery 配方并实测复现 **1 failed / EXIT=1**；`ac1-fix-tests.txt` 补 cwd + filtered 段。
- **AC2（F-004）**：core 加通用 catch（`Debug.WriteLine` + 「内部错误」可见状态）；`CloseAsync` 等待 catch 限定类型。
- **AC3（F-005）**：新增 `_isClosing` 门禁 + 循环等待；`GoToAsync` 在 closing 时忽略；新用例断言**恰好一次**权威重读。
- 提交：`60056d353` → `923f1d5db` → `231ff2ebe`；filtered **7/7**、全量 **396 通过 / 0 失败 / 7 跳过（403）**；`check.ps1` **PASS (3 warnings)**。
- 独立 Review 已派发：task-5 / `safety8-reviewer` / reviewed_head `231ff2ebe`。
- **FEA 线**：Codex 修订完成并已提交（`74a772167`，r4 方案 793 行，LF sha256 `8895aebe…`）；机械验收通过（"待权威记录" 0 次、`PreviewPermanentDeleteBooks`×3、`inventory_digest`×4、未落库会话引用已移除、只改一个文件）。**第 8 轮 Appointment 已建**（`doc/reviews/FEA-00-dsh-r8-appointment.md`），独立复审已派发（task-6 / `fea-reviewer-r8`）。

### 02:20 SAFETY-9 完成并集成；SAFETY-10 开卡
- **SAFETY-9 Review approved**（0 P0 / 0 P1 / 1 P2 R-101）；集成 `main@9aa6758b6`。
- R-101 → **REALUSE-DATA-SAFETY-10**：负向对照转录补全（执行位置/命令/cwd/host/`Expected: 3 / Actual: 5 @ :328`/恢复确认）。

### 02:50 FEA 契约线推进 + SAFETY-10 复审
- **FEA-00 r4 approved**（r8，0 P0 / 0 P1 / 9 P2）已集成并登记索引；契约清单草案吸收 r8。
- **C-01b 存储契约草案**（`doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md`）：AD-003 §3.1–§3.8 → SC-01…SC-37。
- **C-01b r1 独立复核 = changes_requested**（P0×1 / P1×7 / P2×6）：P0 = SC-01 验证列严于 AD-003 §3.2（会驱动删除既有 derived）。**v2 已修订提交**（`e7e43543b`）：SC-01 口径收窄、SC-03/08/19 重标状态、§3.8 补二进制（SC-38）/数据（SC-39）、[现行] 补文件:行证据、冻结条件补 AD-003 `G-REVIEW` 与 ADJ-001 `G-DELETE-CONTRACT`。待 r2。
- **SAFETY-10**：实现提交 `df944357e`（转录补全 + 修复 Codex 首轮 RV-001 pin / RV-002 表格行）；Codex 第二轮复审运行中（其 build/test 受沙箱 NuGet 限制，由 Lead 集成验证覆盖）。

### 03:0x SAFETY-11 落地 + C-01b v2 进入 r2
- **SAFETY-10 收口**：最终 Review（durable teammate）`approved`（0 P0 / 0 P1 / 1 P2），集成 `main@8b15adbfe`；R-102 开 SAFETY-11。
- **SAFETY-11（R-102）**：完整五步负向对照重跑（覆盖 pre-F-005 → build → **失败 EXIT=1**「Expected 3 / Actual 5 @ :328」→ 恢复 → **通过 EXIT=0**），全程原始日志写入 `verification/REALUSE-DATA-SAFETY-10/ac1-negative-control-full.txt`（217 行）；`ac1-discriminating.md` 引用已更新。实现 HEAD `0726dab70`，`check.ps1` PASS。**Review 审查中**（task-10 / `safety9-reviewer`）。
- **C-01b v2**：处置 r1 全部 findings（SC-01 口径、§3.8 补 2 行、状态重标、验证列补文件:行、冻结条件补 AD-003 `G-REVIEW`/ADJ-001 `G-DELETE-CONTRACT`），提交 `e7e43543b`（`cacd6239…`）。**r2 复核中**（`c01b-reviewer`）。
- **C-07 端口清单**：由代码生成 `doc/plan/FEA-C07_API_INVENTORY.md`（54 成员：IReaderProgressSink 1 + IHostController 47 + IRunController 6），提交 `063f35c01`。

### 04:0x SAFETY 线收尾 + C-01b v3
- **SAFETY-11 收口**：Review `approved`（0 P0/0 P1/2 P2），集成 `main@a1b82ffb9`；R-102-A/B 集成前已处置（`e2eb824e0`）。
- **SAFETY-12（收尾审计）**：`verification/REALUSE-DATA-SAFETY-12/safety-line-audit.md` 汇总 **14 条 P2**（当轮处置 4 + 转后续闭环 10、0 悬挂）；治理一致性核对 PASS。实现 `810eacf95`/`705b046d0`；**Review 审查中**（task-11）。
- **C-01b v3**：处置 r2（P0×0 / P1×1 / P2×8）——SC-10 拆分为 SC-10a [现行] + SC-10b [新增]（`settings/*.json`、`catalog.sqlite` 未入 `nmbak` 包）、SC-01 补判别、SC-03 拆分、SC-06/09/15/16 统一 [文档级约束]、SC-38 证据换真实载体、图例与四态判据、变更记录补记。提交 `89aa61849`（`deca1c1d…`）。**r3 复核中**（`c01b-reviewer`）。
- 上游补正：SAFETY-10 卡在 main 未同步 done → `6f23b8ce5`；并登记 `E-AC1-LOG-FULL` pin。

### 04:1x SAFETY-12 收尾审计 + C-01b v2/v3
- **SAFETY-11 收口**：Review `approved`（0 P0/0 P1/2 P2），集成 `a1b82ffb9`；R-102-A/B 集成前已处置。
- **SAFETY-12**：`safety-line-audit.md` 汇总 P2 处置链；**Review 复核后修正**——漏列 SAFETY-6 的 3 条、计数改为 **17 = 当轮 5 + 转后续 12**、SAFETY-6 集成点改 merge `011b19bbf`、证据路径修正（在 SAFETY-7 目录）。`approved`（0 P0/0 P1/5 P2 已修正）。
- **C-01b v2/v3**：v2 处置 r1（P0×1：SC-01 不再严于 AD-003）、v3 处置 r2（P1×1：SC-10 拆 SC-10a/10b；`nmbak` 未打包 `settings/*.json`、`catalog.sqlite`）。

### 05:0x C-01b r3 → v4 → r4 → v5
- r3 `changes_requested`（1 P1：文档控制字段未随 v3 同步 + 6 P2）→ v4。
- r4 `changes_requested`（1 P1：依据行未链 r2/r3；+ 4 P2：SC-20/SC-30 证据标签错位、§5 行序）→ v5。

### 06:1x C-01b r5 `approved` + FEA-GOV-1 开
- **C-01b v5 第 5 轮极窄面复核 `approved`**（P0×0 / P1×0 / P2×3 非阻断已知限制：L-1 图例写法、L-2 依据链、L-3 变更记录归属）。覆盖 38/38、出处 40/40、无新增语义。**文本层面已达冻结前质量**。
- 冻结前置仍未满足：② AD-003 `G-REVIEW`（-> **FEA-GOV-1 已开并派发独立复核**）；③ 用户确认 AD-002 责任表/哨兵；④ `check.ps1` PASS。
- SAFETY 线：**SAFETY-6→11 全部 done + 12 收尾审计 done**；17 条 P2 全部闭合、0 悬挂。

### 06:3x AD-003 独立复核 `approved`（FEA-GOV-1）
- reviewer `c01b-reviewer`（独立上下文）对 AD-003 判 **`approved`**（P0×0 / P1×0 / P2×4 非阻断），六项判定 6 通过。
- 关键实证：AD-002 的 LF blob 去掉 `504797ba7` 追加的 5 行横幅后，SHA-256 与变更前 `1180cdba7` **完全相同** → AD-003 §7「只追加未改写」为真；§4 的 12 项"未实现"全部实测 0 命中。
- `G-REVIEW`：`ADDRESSED_PENDING_R2` → **`SATISFIED`**（并写明依据 2026-10-31 独立性裁决）。**C-01b 冻结前置② 解决**。
- 披露：reviewer 同时是 C-01b r1–r5 复核者（存在确认倾向），但结论均从 AD-003 原文 + 代码实测重新取证。

### 07:3x FEA-GOV-2 开卡（冻结前置③）
- 开 **FEA-GOV-2**：起草 AD-002 `:28` 责任表行 + `:9-10` 横幅的**最小修订提案**（不直接改 AD-002，等用户确认）；并给出冻结前置③的确认清单。

## SAFETY 线总结（供晨阅）

- SAFETY-6 → 11 六个 Task + SAFETY-12 收尾审计**全部 `done` 并已集成**；`main` 上 `check.ps1` PASS。
- **17 条 P2 全部闭合、0 悬挂**（当轮处置 5 + 转后续闭环 12）。
- 关键行为修复：并发 NRE（SAFETY-7）、closing 门禁与判别性断言（SAFETY-8/9）、异常可见化（SAFETY-8）、证据链格式（SAFETY-9/10/11）。
- 当前测试基线：**396 通过 / 0 失败 / 7 跳过（403）**。