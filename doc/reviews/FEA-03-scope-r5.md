---
document_id: FEA-03-scope-r5
kind: independent_scope_review
reviewer: fea03-scope-reviewer
reviewer_kind: subagent
reviewer_source: "同一独立席位续任（DSH Agent Teams durable teammate `fea03-scope-reviewer`，fresh 独立上下文，由 Team Lead `lead` 派发；未参与 FEA-03 起草、v1–v6 范围冻结、UNFREEZE 载体或 v6 处置起草）"
reviewer_independent: true
reviewed_by_implementer: false
author: dsh
base_commit: 666a51214
reviewed_head: 666a51214
reviewed_head_full: 666a512141406c54da887db89abaaef2610e6ec3
repository: G:/CODEX/New Manga
scope: "FEA-03 范围冻结 v6 独立复核（r4 P1×2/P2×12 逐项 disposition）；C-13 v6/UNFREEZE 已在 r3 单独批准、本轮确认 pin 未变（8faf1e80…），不重审契约字节"
decision: approved
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 12
checkps1: "Governance check: PASS (2 warnings)，EXIT=0"
verifypins: "PIN AUDIT: PASS (all 15)；C13 = 8faf1e805eac（未变）；FEA01 = 0370c18932b1（未变）"
captured_at: 2026-11-02T00:14:00+08:00
captured_by: fea03-scope-reviewer
---

# Review：FEA-03 范围冻结 v6（base/reviewed_head = `666a51214`）

**结论：`approved`（P0 × 0 / P1 × 0 / P2 × 12）。**

r4 的 2 条 P1 已闭环：
1. **R4-P1-01（revisionIds 统一）**：R-RECEIPT-2、R-APPLY-2、AC4、AC15、R-LEGACY-2、V8/V20/V21 均为 `revisionIds`/复数语义；逐行 grep 未发现“同 revisionId / 1 revision”单数残留（唯一的 `revisionId` 出现在映射值 `{regionId: revisionId}`、`BaseRevisionId` 与 `current_revision_id`，均非残留）。
2. **R4-P1-02（intent 崩溃窗口）**：v6 的 R-APPLY-3 覆盖了 r4 指出的五点——`current_revision_id == expectedRevisionIds[regionId]` 守卫、apply 失败 `finally` 清 intent、receipt 写失败 fail-closed、intent 改 per-Region `contentDigests`、页尺寸来源（`pages.width/height`，`schema.py:186-194`）与 `PAGE_SIZE_UNAVAILABLE` fail-closed。

P2 × 12 记录在案（不阻断本次范围冻结 approval；其中 P2-01/04/05/07/08 属文档/指针精度，建议在 ready/集成提交中顺带修正）：来源 2 仍引 C-13 v5 pin；approval/元数据残留；AC13 的 `tests/infrastructure` 未收窄；契约 deferral 表把导出 Task 写成 FEA-06/07（应为 `FEA-14-EXPORT`）且新增了未入 AC 的“可查询未保存草稿状态”承诺；R-JOURNAL-1 未含 `commitIntent`；R-RECEIPT-1 与 R-RECEIPT-2 的 digest 字段单复数不一致；`expectedRevisionIds` 语义未写明；receipt 写原子性/不可解析恢复分支未定义；V20 的“current 不匹配”分支期望不准确；receipt 清理窗口未定义；“追加校验回调且不改端口签名”的机制未说明；closeout/载体残留。

本报告只审范围冻结，不评价实现、不构成实现验收或 Gate 关闭。

---

## 0. 复核对象、方法与环境

**被审 head `666a51214`**（parent `fe2fbb113`，即 r4 被审提交；main 线性，工作区 clean）。v6 提交共 5 个文档变更（+269/−27）：

1. `doc/tasks/FEA-03.md`（v6 卡，**+33/−24 行**）
2. `doc/checkpoints/GOAL-PROGRESS-2026-11-01.md`（+2/−1：§3B 范围复核行更新到 r4/r5）
3. `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`（v6/r5 指针）
4. `doc/reviews/FEA-03-scope-r4.md`（+230，r4 报告入库）

**未改**：源码、schema、C-13 契约字节、冻结记录、UNFREEZE 载体、TASK_LEDGER。`verify_pins` 15/15 PASS（C13 `8faf1e805eac`、FEA01 `0370c18932b1` 均与 r4 相同）；`check.ps1` PASS（2 warnings）。

**对照材料（只读）**：v6 卡全文；C-13 冻结记录与 v6 契约；`doc/contracts/V11R_REGION_WRITE_CONTRACT.md:146-150`、`:233`；`src/application/editing/{ports.py,service.py}`；`src/infrastructure/sqlite/{schema.py,regions.py}`；`src/domain/regions/entities.py`；方案 §12.1 `:645-646`（FEA-06/07）与 `:707`/`:953`（FEA-14-EXPORT）；r1–r4 报告。

**未执行**：未运行 `pytest`/`dotnet test`（无实现可测）；未做运行时崩溃/并发实测；未逐字节重审 C-04b/C-08/C-05（本卡不改）。范围冻结阶段以 static review 为准。

---

## 1. r4 findings 逐项 disposition 核验（14 条）

状态：**closed** / **partial** / **open**。

| r4 ID | r4 问题（摘要） | v6 处置（证据） | 核验结论 | r5 关联 |
|---|---|---|---|---|
| R4-P1-01 | receipt/AC 单复数未同步 | R-RECEIPT-2（`:85`）`revisionIds`/`contentDigests`；R-APPLY-2（`:93`）`revisionIds`；AC4（`:132`）“不新增 revision、返回同 revisionIds”；AC15（`:143`）复数；R-LEGACY-2（`:103`）receipt + journal intent；V8/V20/V21（`:166`/`:178-179`）复数 | **closed**（逐行 grep 无“同 revisionId / 1 revision”残留；映射值 `{regionId: revisionId}` 与 `BaseRevisionId` 属正常语义） | 残留见 R5-P2-06 |
| R4-P1-02 | intent 崩溃窗口四点 | R-APPLY-3（`:94`）：`current_revision_id == expectedRevisionIds[regionId]` 守卫；apply 失败 `finally` 清 intent；receipt 写失败 fail-closed；`contentDigests: {regionId: digest}`；页尺寸 `pages.width/height` + `PAGE_SIZE_UNAVAILABLE` fail-closed；`revision_by_id` 读方法 | **closed**（五点均已写入）；语义/原子性细节残留见 R5-P2-07/08 | R5-P2-07 / R5-P2-08 |
| R4-P2-01 | 来源 2 仍引 C-13 v5 pin | 来源 2（`:51`）**未改**，仍“C-13 冻结 v5（pin `d2cb8de4…`）” | **open** | R5-P2-01 |
| R4-P2-02 | 元数据/写权/AC2 层级 | approval（`:7`）改为 `dsh_ruling_2026-11-01_GOAL_Q1_Q11`；review_appointment（`:21`）→ r1…r4；AC14（`:142`）→ r5；来源 5（`:54`）→ r4；来源 4（`:53`）仍“v3 处置 Q-11”；`tests/core` 两文件仍写权（`:41-42`）；AC2/V3 未改（`:130`/`:161`） | **partial** | R5-P2-02 |
| R4-P2-03 | AC13 基线（tests/domain/基础设施过宽） | AC13（`:141`）已移除 `tests/domain` 并注明“由本卡新建，不计入基线”；`tests/infrastructure` 仍整目录；skip/失败裁定未写 | **partial** | R5-P2-03 |
| R4-P2-04 | `rg` 命令未排除定义 | R-LEGACY-3（`:104`）在原 `rg` 命令后再接 `rg -v` 级联，排除定义行与 tests/ 行 | **closed**（排除定义与 tests 的行级过滤已写入；`tests/` 过滤在 src/apps 范围内为冗余但无害） | — |
| R4-P2-05 | C-13 `:94` deferral 未登记 | 新增“契约 deferral 登记”表（`:185-192`），含 C-13 `:94`、SC-D02、SC-D11、SC-D12 四行 | **partial**：登记已加，但 C-13 `:94` 的“导出实现 Task（FEA-06/07）”**归属错误**（FEA-06=Fluent 界面、FEA-07=运行期切换；导出应为 `FEA-14-EXPORT`，见方案 `:645-646`、`:707`/`:953`）；另“只在 journal/草稿层提供可查询的未保存草稿状态”未进交付项映射/AC | R5-P2-04 |
| R4-P2-06 | V24 .NET 命令 / V22/V23 注入方式 | V10（`:168`）注入方式与 CRASH-C 时点；V22（`:180`）chmod/ACL/挂载只读；V23（`:181`）两进程+脚本化 spawn；V24（`:182`）`dotnet test …NewManga.ApplicationCore.Tests.csproj` | **closed** | — |
| R4-P2-07 | Q-9 digest 超集口径 | R-DIGEST-1（`:99`）加注“SC-D12 公式的分组超集（额外 `manual_edited`），属收紧而非放宽，不改 SC-D12 语义” | **closed** | — |
| R4-P2-08 | 扩展 seam vs 铁律 2 张力 | R-APPLY-1（`:92`）改为“在 `commit_region_batch` 的 `BEGIN IMMEDIATE` 内追加校验回调；不改既有端口签名、不触铁律 2 冻结面” | **closed**（解释已写）；回调注入机制仍可读性不足 | R5-P2-11 |
| R4-P2-09 | 重放/过期 precedence | R-APPLY-2（`:93`）“token 过期检查先于 receipt 命中”；AC4（`:132`）与 V21（`:179`）同步 | **closed** | — |
| R4-P2-10 | receipt 7 天清理后 `EDIT_TOKEN_REUSED` 窗口 | R-RECEIPT-3（`:86`）/AC15（`:143`）未改 | **open** | R5-P2-10 |
| R4-P2-11 | journal intent 一致性 | “DB 去重”措辞已改（R-RECEIPT-2/R-APPLY-2/R-LEGACY-2）；V 矩阵标题改 V1–V25（`:155`）且 V20–V25 顺序归位（`:178-183`）；**R-JOURNAL-1（`:79`）内容定义仍未含 `commitIntent`**；AC5/V10 未覆盖“intent 落盘、事务未提交”的恢复分支 | **partial** | R5-P2-05 / R5-P2-09 |
| R4-P2-12 | GOAL/closeout/载体残留 | GOAL §3B（`:58`）已更新 r1…r4→v6、r5 待审；closeout 增 v6 行（`:223`）；C-13 载体未改（§4/§5 仍“复核通过后更新”）、§1A③ LF sha 未补；closeout 称“处置 r4 P2×12”但多项 P2 仍有残留 | **partial** | R5-P2-12 |

**计数**：closed 7、partial 5、open 2（共 14）。

---

## 2. 逐项核查（对应派发清单 1–4）

### 2.1 R4-P1-01（revisionIds 语义统一）

- 逐行 grep `revisionId`：卡内 4 处非复数出现——`:84` 映射值 `{regionId: revisionId}`、`:90` `BaseRevisionId`、`:93` 的 `revisionIds` 文本、`:94` 的 `{regionId: revisionId}` 与 `expectedRevisionIds`；**没有**“同 revisionId / 1 revision”的验收残留。
- R-RECEIPT-2、R-APPLY-2、AC4、AC15、R-LEGACY-2、V8/V20/V21 均已改为 `revisionIds`/复数；AC4 相应改为“不新增 revision、返回同 revisionIds”。**R4-P1-01 闭环。**
- 尾项（P2）：R-RECEIPT-1（`:84`）字段仍是 `contentDigest`（单值），而 R-RECEIPT-2（`:85`）比较 `contentDigests`、R-APPLY-3（`:94`）intent 用 per-region `contentDigests` → 见 R5-P2-06。

### 2.2 R4-P1-02（intent 崩溃窗口）

逐点核验 v6 R-APPLY-3（`:94`）：

1. **守卫** ✅ 已写 `regions.current_revision_id == expectedRevisionIds[regionId]`。**但语义需写明**：该守卫只在 `expectedRevisionIds` = “apply 将写入的新 revision ids（在写 intent 之前预生成）”时正确；若被读成 base ids 则逻辑反转。当前实现支持预生成（`service.py:398-409` 的 `_build_revision` 在事务前用 `_new_id()` 生成 `region_revision_id`，`commit_region_batch` 接受调用方提供的 `RegionRevision`）→ 建议加一句说明（R5-P2-07）。
2. **apply 失败 finally 清 intent** ✅ 已写（stale/protection/DB）。
3. **receipt 写失败 fail-closed** ✅ 已写（进程不得继续写，重启由 intent 恢复）。
4. **per-Region `contentDigests`** ✅ 已写（intent 字段改为 `{regionId: digest}`）。
5. **页尺寸来源与 fail-closed** ✅ 已写（`pages.width/height`，`schema.py:186-194`；取不到 → `PAGE_SIZE_UNAVAILABLE` fail-closed）——与 r4 更正后的结论一致。

遗留（P2，不构成 P1）：
- `expectedRevisionIds` 语义未写明（R5-P2-07）。
- receipt 写原子性（temp+fsync+replace）与“intent+receipt 都在但 receipt 不完整/不可解析”的恢复分支未定义；r4 的“写失败 fail-closed”覆盖不了“写中崩溃”（R5-P2-08）。
- V20（`:178`）“current 不匹配”分支的期望“同 revisionIds”不成立（该分支=事务未提交，没有 revisionIds），应拆两支（R5-P2-09）。
- R-JOURNAL-1 未把 `commitIntent` 纳入内容定义；AC5/V10 未加“intent 落盘、事务未提交”的恢复断言（R5-P2-05）。

### 2.3 P2 清单核验（派发清单第 3 项）

| 派发项 | 核验结果 | 证据 |
|---|---|---|
| AC13 基线收窄（tests/domain 新建不计基线） | ⚠ 部分：`tests/domain` 已排除；`tests/infrastructure` 仍整目录 | 卡 `:141` |
| `rg` 排除定义与 tests | ✅ | 卡 `:104` |
| V10/V22/V23 注入方式 | ✅ | 卡 `:168`/`:180-181` |
| V24 的 .NET 命令 | ✅ | 卡 `:182` |
| Q-9 digest 超集口径 | ✅ | 卡 `:99` |
| 重放/过期 precedence | ✅ | 卡 `:93`/`:132`/`:179` |
| replay 与 receipt 清理窗口 | ❌ 未定义 | 卡 `:86`/`:143` 未改 |
| “扩展 seam 不改既有端口签名”说明 | ⚠ 已写但机制可读性不足 | 卡 `:92` |
| C-13 `:94` 导出/删除 preflight deferral（deferral 表） | ⚠ 已登记但导出 Task 归属错误（FEA-06/07 → 应为 FEA-14-EXPORT） | 卡 `:189`；方案 `:645-646`/`:707`/`:953` |
| 来源 5 列到 r4 | ✅ | 卡 `:54` |
| approval/appointment 更新 | ⚠ appointment→r1…r4 ✅；approval 改为 `GOAL_Q1_Q11` 语义不明 | 卡 `:7`/`:21` |
| V 矩阵标题 V1–V25 | ✅ | 卡 `:155`，V20–V25 顺序归位 |

### 2.4 新问题（重点核查）

1. **`commitIntent` 在 R-JOURNAL-1 中的位置**：R-JOURNAL-1（`:79`）仍写“内容 = 11 字段 + `status`/`savedAt`”，未含 `commitIntent`；intent 写 journal 后与内容定义不一致（R5-P2-05）。
2. **intent 与 journal 原子性**：intent 复用 journal 写路径（R-JOURNAL-2）可继承原子性，但卡未明说；且 AC5/V10 只覆盖 journal 的 tmp/rename 崩溃，未覆盖“intent 已落盘、SQLite 事务未提交/已提交未写 receipt”的恢复断言（R5-P2-05）。
3. **V25 顺序**：已归位到 V24 之后（`:183`），标题改 V1–V25 ✅。
4. **deferral 表与禁止范围**：表中“只在 journal/草稿层提供可查询的未保存草稿状态”是新能力，未进交付项映射/AC，属范围外承诺；禁止范围本身无冲突（不触 C-04b、不接线），但 deferral 归属的 FEA-06/07 指错（R5-P2-04）。
5. **receipt 字段单复数**：R-RECEIPT-1 `contentDigest` vs R-RECEIPT-2 `contentDigests`（R5-P2-06）。
6. **receipt 原子性/不可解析恢复**（R5-P2-08）。
7. **V20 分支期望**（R5-P2-09）。
8. **approval 语义**：`dsh_ruling_2026-11-01_GOAL_Q1_Q11` 可读成“Q1 与 Q11”而非“Q1…Q11”；建议写全或注明范围（R5-P2-02）。

---

## 3. Findings（r5）

| 编号 | 级别 | 位置 | 问题 | 建议 | 状态 |
|---|---|---|---|---|---|
| R5-P2-01 | P2 | 卡 `:51`（来源 2） | 来源仍写“C-13 冻结 v5（pin `d2cb8de4…`）”；v6 实际 pin 为 `8faf1e80…`（r4-P2-01 未处置） | 改为 C-13 冻结 v6 + pin `8faf1e80…`，链接 UNFREEZE 载体与 r3 复核 | open |
| R5-P2-02 | P2 | 卡 `:7`（approval）、`:21`（review_appointment）、`:53`（来源 4）、`:41-42`（tests/core 写权）、`:130`/`:161`（AC2/V3） | ①approval 写成 `GOAL_Q1_Q11`，语义可读成“Q1 与 Q11”；②来源 4 仍“v3 处置 Q-11”；③`tests/core` 两个基线文件仍授予写权；④AC2/V3 未写 flush 断言层级（Core seam 五类原因 vs 真实 UI 触发） | approval 写全或注明 Q1…Q11；来源 4 改“v3/v4/v5 处置 Q-11”；`tests/core` 两文件从写权移除或写明 DSH 批准例外；AC2 注明 Core seam 断言 + UI 接线归 FEA-04/06 | open |
| R5-P2-03 | P2 | 卡 `:141`（AC13） | `tests/domain` 已排除 ✓，但基线仍含整个 `tests/infrastructure`（plugin 打包/沙箱等无关项）；未写基线“实现前”如何取得、skip/失败如何裁定 | 收窄 `tests/infrastructure` 到相关文件（或注明排除清单）；基线逐文件 outcome + skip 原因 + 无关失败裁定写入 Handoff | open |
| R5-P2-04 | P2 | 卡 `:189`（deferral 表） | ①C-13 `:94` 的“导出实现 Task（FEA-06/07）”指错：FEA-06 = Fluent 独立界面、FEA-07 = 运行期切换/窗口（方案 `:645-646`），导出任务是 `FEA-14-EXPORT`（方案 `:707`/`:953`）；②“只在 journal/草稿层提供可查询的未保存草稿状态”是新能力，未进交付项映射/AC | 把 deferral 归属改为 `FEA-14-EXPORT`（删除侧仍需 C-04b UNFREEZE）；把“未保存草稿状态查询”要么加入交付项映射/AC，要么删去该承诺；在 ready 前修正 | open |
| R5-P2-05 | P2 | 卡 `:79`（R-JOURNAL-1）、`:133`/`:168`（AC5/V10）、`:178`（V20） | intent 写 journal，但 R-JOURNAL-1 内容定义仍为“11 字段 + status/savedAt”；AC5/V10 未覆盖“intent 已落盘、SQLite 事务未提交/已提交未写 receipt”的恢复分支 | R-JOURNAL-1 内容加 `commitIntent`（或其 key 位置/生命周期）；AC5/V10 增 intent 崩溃点，V20 明确两恢复分支 | open |
| R5-P2-06 | P2 | 卡 `:84`（R-RECEIPT-1）、`:85`（R-RECEIPT-2）、`:94`（R-APPLY-3） | R-RECEIPT-1 仍是单值 `contentDigest`，与 R-RECEIPT-2 的 `contentDigests`、intent 的 per-Region `contentDigests` 不一致；恢复“补 receipt”需要 combined digest 的定义 | 三处统一为 per-Region `contentDigests`（或定义 combined digest 的计算与比较对象），并同步 R-RECEIPT-2/AC15 | open |
| R5-P2-07 | P2 | 卡 `:94`（R-APPLY-3） | `expectedRevisionIds` 语义未写明是“apply 预生成的新 revision ids”还是“expected base ids”；`current_revision_id == expectedRevisionIds[regionId]` 仅在前者语义下正确 | 加一句：新 revision id 在写 intent 前预生成（`service.py:398-409` 现有的 `_build_revision` 做法），intent 存这些 id，事务用同一 ids；恢复用 `==` 判断已提交、`!=` 判断未提交 | open |
| R5-P2-08 | P2 | 卡 `:94`（R-APPLY-3）、`:86`（R-RECEIPT-3） | receipt 写原子性未定义（是否 temp+fsync+replace）；恢复分支“intent+receipt 都在 → 清 intent”未定义 receipt 不完整/不可解析时按缺失处理；r4 的“写失败 fail-closed”不覆盖“写中崩溃” | 写明 receipt 原子写（与 journal 同模式）；恢复时 receipt 解析失败按“缺失”走 intent 分支；补“写中崩溃”恢复断言 | open |
| R5-P2-09 | P2 | 卡 `:178`（V20） | V20 三场景合并成一条期望“同 revisionIds；intent 清；无第二 revision”；其中“current 不匹配”= 事务未提交，没有 revisionIds 可返回 | 拆两支：receipt/intent 命中 → 同 revisionIds、无第二 revision；current 不匹配 → 清 intent、视为未提交（重放按正常 apply 或 stale 处理） | open |
| R5-P2-10 | P2 | 卡 `:86`（R-RECEIPT-3）、`:143`（AC15） | receipt 7 天未活动清理后，同 token 不同内容的 `EDIT_TOKEN_REUSED` 不再可判（receipt 已删）；AC15 该断言隐含时间窗口但卡未定义 | 定义幂等窗口（receipt 保留至 Draft 清理，或明确 7 天后只保证同内容幂等），并写明清理后不同内容重放的行为 | open |
| R5-P2-11 | P2 | 卡 `:92`（R-APPLY-1）、`:94`（R-APPLY-3） | “在 `commit_region_batch` 内追加校验回调；不改既有端口签名”机制自相矛盾：回调如何取得 per-apply expected digest 未说明；同段 `revision_by_id` 属新增端口方法（属扩展而非“不改”） | 写明回调注入方式（可选参数/适配器内部比较/新方法）并与 C-13 铁律 2 口径对齐；若新增方法，明确“不改既有签名”的含义 | open |
| R5-P2-12 | P2 | 卡 `:223`（closeout）、C-13 载体 `:45-58`、GOAL `:58` | ①closeout v6 称“处置 r4 P2×12”，但 P2-01/03/10/11/12 仍有残留，未列范围；②C-13 载体 §4/§5 仍写“复核通过后更新记录”（记录已在 v5 更新）；§1A③ LF blob sha 未补；③review_appointment 未列 r5（本轮 Review 完成后应补） | closeout 列 P2 处置范围（或注明“余项见 r5”）；载体补时序说明与 LF sha；r5 approved 后 review_appointment 增 r5 | open |

---

## 4. 验证记录（实际执行）

| 场景 | 命令/步骤 | 环境/commit | 结果 | 证据/备注 |
|---|---|---|---|---|
| HEAD 与工作区 | `git rev-parse HEAD`；`git status --porcelain` | `666a51214`，main | PASS（clean） | `666a512141406c54da887db89abaaef2610e6ec3` |
| v6 提交范围 | `git show --name-status`；`git diff --stat fe2fbb113..HEAD` | `666a51214` | 5 文件（卡/GOAL/STATUS/PLAN/r4 报告） | 无源码/schema/契约字节/冻结记录改动 |
| pin 与检查器 | `verify_pins.ps1`；`check.ps1`；`Get-FileHash` C-13 | `666a51214` | 15/15 PASS；C13 `8faf1e80…` 未变；FEA01 `0370c189…` 未变 | PASS（2 warnings） |
| revisionIds 残留 grep | `revisionId` / `1 revision` 全卡扫描 | `666a51214` | 无“同 revisionId / 1 revision”验收残留；仅映射值/BaseRevisionId/current_revision_id | R4-P1-01 closed |
| intent 五要素 | 读 R-APPLY-3（`:94`）逐项对照 r4-P1-02 | `666a51214` | 守卫/finally 清 intent/fail-closed/per-region digest/页尺寸均写入 | R4-P1-02 closed；细节 R5-P2-07/08 |
| r4-P2 清单 | 逐项 grep 读卡 | `666a51214` | 7 closed / 5 partial / 2 open | 见 §1 |
| deferral 归属核对 | 方案 `:645-646`、`:707`、`:953` | `666a51214` | FEA-06/07 非导出；导出为 FEA-14-EXPORT | R5-P2-04 |
| receipt 字段一致性 | 读 R-RECEIPT-1/2 与 R-APPLY-3 | `666a51214` | `contentDigest` vs `contentDigests` 不一致 | R5-P2-06 |
| 运行 pytest / dotnet test | — | — | **NOT_RUN** | 无实现可测；范围冻结阶段 |
| 崩溃/并发实跑 | — | — | **NOT_RUN** | 无实现 |
| C-04b/C-08/C-05 正文 | — | — | **NOT_RUN** | 非本卡写域 |

---

## 5. 边界声明、结论与复审

**边界声明**

- 本 Review 只审 v6 范围冻结与 r4 findings 的 disposition；C-13 v6/UNFREEZE 已在 r3 单独 approved，本轮只确认 pin 未变（`8faf1e80…`），不重审契约字节。不评价实现、不构成实现验收、不构成 Task 释放或 Gate 关闭。
- 未修改任何被审文件；未 commit、未 push；只新增本报告。未访问用户数据。
- `check.ps1`/`verify_pins.ps1` 的 PASS 是机械结果，不替代范围判定。

**关键结论**

- **`approved`（P0 × 0 / P1 × 0 / P2 × 12）。**
- R4-P1-01、R4-P1-02 均闭环：revisionIds 语义统一、intent 崩溃窗口五点齐备且可实现（`_build_revision` 预生成 revision id、`revision_by_id` 属写域、`pages.width/height` 可取）。
- r4 的 14 条 disposition：closed 7、partial 5、open 2；P2 残留 12 条（见 §3），均属指针/精度/覆盖收尾，不构成 P1。
- 本轮新发现的重点 P2：deferral 表导出 Task 归属错误（应为 `FEA-14-EXPORT`）、R-RECEIPT-1 与 R-RECEIPT-2 的 digest 字段单复数不一致、`expectedRevisionIds` 语义未写明、receipt 写原子性/不可解析恢复未定义、V20 “current 不匹配”分支期望不准确、R-JOURNAL-1 未含 `commitIntent`。

**建议在 ready/集成提交中顺带修正（不阻断本次 approval）**

1. P2-01：来源 2 改 C-13 v6 + pin `8faf1e80…`。
2. P2-04：deferral 导出归属改 `FEA-14-EXPORT`；删除未入 AC 的“可查询未保存草稿状态”承诺或补交付项。
3. P2-05：R-JOURNAL-1 内容定义加 `commitIntent`；AC5/V10 增 intent 崩溃点。
4. P2-06/07/08/09：统一 receipt 字段为 per-Region digests；写明 `expectedRevisionIds` = 预生成新 id；定义 receipt 原子写与不可解析恢复；V20 拆两恢复分支。
5. P2-02/03/10/11/12：approval/来源 4/tests-core 写权/AC2 层级、AC13 收窄、receipt 清理窗口、seam 机制说明、closeout/载体/r5 appointment 收尾。

**复审口径**：本报告 P0/P1=0，按派发要求写 `approved`；P2 残留由 DSH 在 ready/集成提交中处置并在实现 Handoff 中留痕。实现复核（`doc/reviews/FEA-03-r1.md`）仍不在本报告范围。

---

*Reviewer：`fea03-scope-reviewer`（DSH Agent Teams durable teammate，fresh 独立上下文，由 Team Lead `lead` 派发；未参与 FEA-03 的起草、v1–v6 范围冻结、UNFREEZE 载体或 v6 处置起草）。日期：2026-11-01/02。*
