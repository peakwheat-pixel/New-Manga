# NIGHT SHIFT 2026-11-01 晨报（DSH 自主夜班）

**一句话结论**：夜班进行中——主线 SAFETY-6 已 done 并集成 main；新架构线 FEA-00 r7 独立 Review 为 `changes_requested`（2×P1），方案待修订；当前离线可推进项 = REALUSE-DATA-SAFETY-7（SAFETY-6 Review 的 3 条 P2）。

## 主线到哪

| 项 | 状态 | 证据 |
|---|---|---|
| REALUSE-DATA-SAFETY-6 | **done**（AC1/AC2/AC3 MET；Review approved；P2×3 open） | 集成 `011b19bbf`；证据 `verification/REALUSE-DATA-SAFETY-6/`；Review `doc/reviews/REALUSE-DATA-SAFETY-6-review.md` |
| 集成验证 | 通过 | build 0 警告/0 错误；test 394 通过 / 0 失败 / 7 跳过（401）；check.ps1 PASS |
| REALUSE-DATA-SAFETY-7 | **ready → 夜班执行中**（R-001 并发 NRE / R-002 pin / R-003 日志） | worktree `G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-7`，分支 `task/REALUSE-DATA-SAFETY-7`，base `29d06c462` |

## 新架构到哪

| 项 | 状态 | 证据 |
|---|---|---|
| FEA-00 方案 r3 | `changes_requested`（0 P0 / 2 P1 / 6 P2） | `doc/reviews/FEA-00-dsh-r7.md`、`doc/reviews/FEA-00-dsh-r7-appointment.md` |
| P1 卡点 | R7-01 未同步 AD-003/ADJ-001；R7-02 删除流程未吸收 PD-01–PD-10 | 同上 |
| 契约清单草案 | 已建，C-01→a/b/c、C-04→a/b/c；**全部未冻结** | `doc/plan/FEA-01_CONTRACT_DRAFT.md` |
| FLUENT 文档 | 已入库（修复 AD-003 失效引用） | `6cab0b083` |
| 下一步 | 转 Codex 修订 → 新 hash 独立复审 | — |

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
   - **A（推荐）**：起草 per-scheme 例外登记（与 R-14 同构），不整体豁免
   - B：完全豁免

## 明早推荐第一步

**先裁决 1 与 2**（各回一个字母即可），我按裁决开实施 Task；新架构线等 Codex 修订完成后我会自动进入复审，不需要你介入。

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
