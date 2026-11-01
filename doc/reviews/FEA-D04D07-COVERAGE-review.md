---
document_id: FEA-D04D07-COVERAGE
kind: independent_review
task_id: task-33（AC8 D04–D07 完整覆盖检查复核）
round: 1
scope: D04–D07 四包逐项覆盖验证 + §6 保留限制 + 结论边界
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: 44667d836
reviewed_head_full: 44667d83608977b92b722a667fbb21114c2a5bca
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 44667d836）"
reviewed_documents:
  - doc/plan/D04-D07-COVERAGE-CHECK-2026-11-01.md（90 行，blob sha256 1adbe4ec…）
  - 13 份冻结契约 + 冻结记录（C-01b/C-02/C-03/C-04b/C-05/C-06/C-07/C-08/C-09/C-11/C-12/C-13/C-14）
  - 依据：方案 `:767`/`:768`/`:769`/`:770`、FEA-01 `:57`/`:58`、ADJ-001 §9 `:128`
reviewed_sha256:
  doc/plan/D04-D07-COVERAGE-CHECK-2026-11-01.md: 1adbe4ec96c433516c3fb82952dac320d1fd7838ca1174917c832807d7b3b216
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 2
p2_count: 3
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
verifypins: "PASS (all 13)，EXIT=0，本次实跑"
captured_at: 2026-11-01T11:38:00+08:00
captured_by: c01b-reviewer
---

# 独立复核：D04–D07 完整覆盖检查（AC8）

**本报告不是** Gate 关闭裁定。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 2** / P2 × 3）。**

**四包的条款级覆盖基本成立**：D04 **6/6**、D05 **5/5**、D06 **6/6**（含我重点怀疑的 SC-R06——它不是复述 M2-C1，确有 Run 侧不变量）、D07 **前 6 项 6/6**。但有两处**具体漏项/误判**必须先补，否则「D04–D07 全覆盖」这一结论不能直接支撑 Gate 关闭：

1. **D07 第 7 项「独占写锁与 pin」被写成 ✅，实际只覆盖「迁移 + 备份 pin」**：`SC-17` 原文限定「任何**迁移**」使用独占维护锁；C-09 的恢复路径（`SC-B02`/`SC-B09`）**没有**要求「整库恢复持独占维护锁、停写者/Run/lease」（方案 `:530` 明文要求）。除非写明「整库恢复按迁移处理」，否则该行应为「部分」。
2. **§6 的「保留限制」漏了至少 4 条冻结契约已登记的 L 项**：C-14 **L-3**（`scope.entry` 与 `EntryId` 对齐待确认）、C-13 **L-1** / C-04b **L-1**（protectionDigest 编辑层不接入删除 preflight；book 级聚合对「计数不变而分布变」不敏感）、C-08 **L-1/L-2**（preparedDigest 逐字段 wire 编码、防抖/过期值）、C-09 **L-3**（settings 路径实现未核）。P1-2。

| 包 | 逐项核对 | 结论 |
|---|---|---|
| **D04**（方案 `:767` 六项） | 6/6 ✅（SC-D04/D05、SC-D01/D12、SC-D06/D07、SC-D08、SC-D09/D10、SC-D11，逐条实核内容） | 成立 |
| **D05**（方案 `:768` 五项） | 5/5 ✅（但第 2 项把 **SC-31** 列为 lease 载体是**误引**——SC-31 是原文件删除流程；lease 是 SC-25/29） | 成立（附 P2-1） |
| **D06**（FEA-01 `:57` 六项） | 6/6 ✅（SC-R06 有 3 条 Run 侧不变量 + 验证，非复述；SC-R07/R08/R09 见下） | 成立 |
| **D07**（FEA-01 `:58` 七项） | 1–6 ✅；**第 7 项 ⚠**（见 P1-1） | 部分 |

---

## 2. 四包逐项核对（哪几行成立、哪几行不成立）

### 2.1 D04 —— **6/6 成立**

| 行 | 声明 | 我实核的条款内容 | 判定 |
|---|---|---|---|
| 1 | edit token / journal | C-13 `SC-D04`：`{tokenId, DraftId, DraftSequence, SessionId, issuedAt, expiresAt}`，**幂等键**（同 `(DraftId, DraftSequence)` 返回同一结果）+ 过期码；`SC-D05`：draft journal 持久检查点、与 revision 表分离、重启恢复为 `active` 不自动提交 | ✅ |
| 2 | Draft / Protection 版本 | `SC-D01`：Draft 字段集（`DraftId`/`SessionId`/`DraftSequence` 等）；`SC-D12`：`protectionDigest` = 三锁 + manual 位 | ✅ |
| 3 | candidate-only prepare | `SC-D06`（`:89` 明文「任何同区域的新结果**先成为 `RegionCandidate`**，不得直接覆盖 `current_revision_id`」）+ `SC-D07`（prepare 只产出 `RegionCandidate`、live apply 才切换） | ✅（覆盖归属正确，不是只列编号） |
| 4 | 统一事务 live apply | `SC-D08`：全 Region 同一 SQLite 事务 + 乐观并发 `STALE_BASE_REVISION` + 读隔离 | ✅ |
| 5 | 锁定样式白名单 | `SC-D09`（三锁 × 三域）+ `SC-D10`（`TextStyle` 真实 6 个 snake_case 键） | ✅ |
| 6 | 旧非幂等写兼容 | `SC-D11`：统一去重键 + 过渡期客观判据 | ✅ |

### 2.2 D05 —— **5/5 成立，1 处误引（P2-1）**

| 行 | 声明 | 实核 | 判定 |
|---|---|---|---|
| 1 | 持久身份与授权分离 | C-06：`SourceAccessRegistry` 持久条目（`identityFacts` = 内容 digest + volume serial + file ID、`generation`）+ `source-read` grant 独立类型（不复用旧 grant） | ✅ |
| 2 | scope / version / lease | C-06 grant `scope{sourceId,version,entry,rendition}` ✓；**lease 的真实载体 = C-01b `SC-25`（稳定读取 lease + digest）+ `SC-29`（结果应用前重取 lease）**；**`SC-31` 是「原始文件删除独立流程」，不是 lease 载体** → **P2-1** | ✅（附误引） |
| 3 | 重定位 / 同步 | C-14 `SC-S01…S08`（三种操作区分、范围选择、失败回滚、diff 预览、sync plan、不连带删除、C-04b 接口）——小标题逐条对上 | ✅ |
| 4 | 容器页映射 | C-14 `SC-S09…S13`（locator≠身份、Page 绑定、稳定排序键、健康判定、原文件缺失） | ✅ |
| 5 | 缓存边界 / 资源上限 | C-06 `:64` per-request 预算 + C-01b `SC-02/03/20` + C-14 `SC-S14…S17`（淘汰/持久化/全局上限/通道隔离） | ✅ |

### 2.3 D06 —— **6/6 成立**（重点核了 SC-R06 是否只是复述）

| 行 | 声明 | 实核 | 判定 |
|---|---|---|---|
| 1 | preview 与发送同源 | `SC-R01`：`PrepareRun` 计算快照+摘要+`preparedDigest`，`AcceptRun` 校验 digest 后写入；拒绝 `RUN_STALE_PREVIEW` 零副作用 | ✅ |
| 2 | 不可变内容 pin | `SC-R02`：已接受 Run 的 `*_snapshot_json` 只增不改；执行期只读快照 | ✅ |
| 3 | 控制 pending 状态 | `SC-R06`：**不只是复述**——引用 M2-C1 `:213` 后，有「**Run 侧不变量（本契约新增）**」3 条：①控制请求已持久化 ≠ 状态已改变 ②UI 不得早于持久 `status` 显示 `paused`/`cancelled`（引 `:203`/P11 `:97`）③状态变更唯一权威 = Core 持久化；并有验证（`ControlResult.status` 仍可为 `running` → 到安全边界才 `paused`） | ✅ |
| 4 | 真实完成口径 | `SC-R07`：权威持久状态 + 共同不变量（终态且 `counts.processing=0 && counts.waiting=0`）+ 逐终态判据（用 M2-C1 §6.1 `:834` 的 `counts.{total,completed,failed,skipped,blocked,waiting,processing}`）+ 明文的三个否定 + 4 条验证（含重启后同一终态） | ✅ |
| 5 | retry 是否复用 | `SC-R08`：同键重放不重取快照（`:200`/`:201`）；新 Run 复用失败 Page 集合（`:206`）、**不复用冻结上下文**（`:202` fingerprint 不含 Revision/Lock/settings…）；源 Run 不变；对照 P11 | ✅ |
| 6 | 断线 receipt | `SC-R09`：同键重放找回原 Run（`:200`）；覆盖范围 = 三处带 `idempotency_key` 的操作（`:201`）；**`request_id` 不得作去重键**（引 `:138`）；`idempotency_key` 随 Run History 保留 | ✅ |

**旁证**：`SC-R03/R04/R05`（配置变化、候选存储、快照完整性）确为额外覆盖，不算在六项内也不影响判定 ✓。

### 2.4 D07 —— **前 6 项成立；第 7 项 ⚠ 部分**

| 行 | 声明 | 实核 | 判定 |
|---|---|---|---|
| 1 | 软删/恢复/TrashEntry 命令面 | C-09 `SC-B06`：`MoveToTrash`/`RestoreFromTrash`/`ListTrash`/`PurgeTrash` 4 命令 + `TRASH_ENTRY_NOT_FOUND(not_found)`/`TRASH_RESTORE_CONFLICT(conflict)`/`TRASH_RESTORE_LAYER_MISMATCH(conflict)` 3 码 + 不变量 + 验证 | ✅ |
| 2 | 三路径统一 ProtectionPolicy | `SC-B04`（三层边界）+ `SC-B04a`（共用判定函数；彻底删除=披露+专门确认非阻断；共享引用可安全拆分不阻断；非终态 Run→`BOOK_BUSY`）——r4 已实核与 ADJ-001 PD-01/PD-08 一致 | ✅ |
| 3 | 备份覆盖清单 | `SC-B01` + `SC-B01a`（完整归属表：含 settings 凭据/非凭据拆分、catalog 判定不纳入理由=可重建、backup/1 只读、backup/2 产物） | ✅ |
| 4 | `backup/2` | `SC-B07`（版本协商、legacy adapter 只读不写回、写端只写 v2、命名统一 `format:"nmbak"+version:2`） | ✅ |
| 5 | `DatabaseId` | C-01b `SC-18`（引用不复写；C-09 `SC-B03` 引用） | ✅ |
| 6 | 自动备份调度归属 | `SC-B08`（归 Core、单 scheduler、手动不重置自动、保留策略、失败语义、DatabaseId 不匹配不恢复） | ✅ |
| 7 | **独占写锁与 pin** | **pin ✅**：C-01b `SC-13`「DB 快照 → pin 文件集合 → 复制校验 → 原子发布 → 标 verified → 释放 pin」；**独占写锁 ⚠**：`SC-17` 原文「任何**迁移**使用独占维护锁…」——**C-09 的恢复路径 `SC-B02`/`SC-B09` 没有要求独占维护锁**，而方案 `:530` 明文要求「灾难恢复整库模式：独占维护锁，停所有应用写者/Run/lease，先 verified pre-restore 包，再在新数据根验证并切换入口」 | **⚠ 部分（P1-1）** |

**「引用是否足够算覆盖」的回答**：引用 C-01b 冻结条款本身是合法的（C-14 引 C-01b SC-26/27/34 也被判通过）；**但必须写明「整库恢复按迁移处理、持 SC-17 锁」**，否则读者只能得出「独占锁只覆盖迁移」的结论——而恢复是 D07 的核心业务面之一。**不需要改冻结契约**：只要在覆盖表该行注明这一前提（或把该行改「部分」并把差距登记为 L-5），或由 DSH 在 AC9 裁定里明文认定「整库恢复 = 迁移」即可。

---

## 3. 漏项清单

1. **P1-1（D07 行 7）**：见 2.4 —— 「独占写锁」对恢复路径没有落点；需补映射前提或改「部分」+ 登记 L-5。
2. **P1-2（§6 登记不全）**：见 §4 —— 至少漏 C-14 L-3、C-13 L-1/C-04b L-1；建议并补 C-08 L-1/L-2、C-09 L-3；另 L-2 对 C-08 块② 的描述不全（漏 `RUN_*` 3 码 + §8「Proposed（未观察）」小节）。
3. **P2-1（D05 行 2 误引）**：`SC-31` 不是 lease 载体（是原始文件删除流程）；lease 载体应写 **`SC-25` + `SC-29`**。
4. **P2-2（声明来源两版清单未对齐）**：方案 `:770` 的 D07 必须冻结内容是「统一三路径、**profile/catalog 归属**、DatabaseId、backup/2、**旧包**、**独占升级/格式 Gate**」，与 FEA-01 `:58` 的七项不是同一张清单；本表只对 FEA-01 对齐。实际覆盖情况：旧包 → `SC-B07` legacy adapter ✓、格式 Gate → C-01b `SC-38` ✓、profile/catalog 归属 → `SC-B01a` ✓——**但表内没有这些行、也没有注明来源差异**。建议加一张「方案 `:770` ↔ FEA-01 `:58` ↔ 承载」crosswalk（或注明以 FEA-01 为准并解释与方案的差异）。
5. **P2-3（结论边界措辞）**：§5 `:67`「**`G-DELETE-CONTRACT` 的契约侧条件已满足**——但关闭须待本文件经独立复核 `approved`」——加两道前置是恰当的做法 ✓；但「已满足」是绝对表述，建议改为「**在 §6 保留限制下**，D04–D07 的**条款级**承载已完成；契约侧条件的最终判定由 AC9 裁定」。这样不会在 §6 尚不完整时被读成「无条件满足」。

---

## 4. §6 四条保留限制核对

| 现列 | 是否如实 | 是否真的不阻断 | 评价 |
|---|---|---|---|
| **L-1** 四张表 DDL 未冻结 | ✅ 属实（AD-003 `:117`；C-14 记录 §5 L-1；G-CONTRACT 关闭裁定边界） | ✅ 不阻断 D04–D07 **语义**覆盖（D05 五项不含 DDL） | 保留 ✓ |
| **L-2** M2-C1 字节修订（`TRASH_*`、`PrepareRun`/`AcceptRun`、`allowedRunErrorCodes`）未做 | 基本属实，但**不完整**：C-08 块② 还含 `RUN_STALE_PREVIEW`/`RUN_PREVIEW_EXPIRED`/`RUN_SNAPSHOT_INCOMPLETE` 3 码 + §8「Proposed（未观察）」小节 + `:1119`/`:1122` 例外；C-09 侧还有 `SC-B06` 3 码 | ✅ 属**释放前置**，不阻断覆盖 | 补全描述（P2） |
| **L-3** 旧口径残留（C-13 `:203`、冻结记录、GATE-CLOSURE-RULING、ADJ-001 `:128`） | ✅ 属实（C-09 记录 §5 L-1 已列同一清单） | ✅ 不阻断（由下次裁定/errata 更正） | 保留 ✓ |
| **L-4** C-04b pending operation 披露字段未加入 | ✅ 属实（C-14 L-2；属 C-04b UNFREEZE） | ✅ 不阻断（当前行为=不披露，与现网一致） | 保留 ✓ |
| **第 5 条（漏）** | — | — | **C-14 L-3**：`scope.entry` 与 `EntryId` 对齐规则待 C-06 侧/协议 Task 确认——直接影响 D05 行 1/2 的「身份 ↔ 授权定位键」映射，应登记；**C-13 L-1 / C-04b L-1**：`protectionDigest` 是编辑层摘要、不接入删除 preflight；book 级聚合对「计数不变而分布变」不敏感——影响 D07 行 2/3 的删除保护检测，应登记；**C-08 L-1/L-2**：preparedDigest 逐字段 wire 编码留块②、防抖/过期是建议值；**C-09 L-3**：settings 路径实现未核（本 checkout 无 `src/`） |

---

## 5. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具，`reviewer_kind: subagent`，独立上下文。
- 未参与覆盖表的编写（作者 = DSH），未参与任何契约起草/冻结；本轮逐条对照方案 `:767`–`:770`、FEA-01 `:57`/`:58`、各契约实际条款文本与各冻结记录 §5，未按表内「✅」转述判定。
- 我出具过 C-01b…C-14 的多轮复核（如实披露）；本轮按「该行承载是否真的覆盖声明」标准核，未因此前批准过某契约而放宽。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`。

---

## 6. 治理（本次实跑）

- `check.ps1`：PASS（3 warnings），EXIT=0。
- `verify_pins.ps1`：PASS (all 13)，EXIT=0（13 份冻结契约 pin 全部一致）。
- 未 push（`origin/main..HEAD` = 239）；工作树干净；覆盖表 blob `1adbe4ec…`。

---

## 7. NOT_RUN

- 未运行程序/pytest；全部为文档、git 历史与脚本输出比对。
- 未核 C-02/C-03/C-05/C-07/C-11/C-12 的内容（与 D04–D07 无关，只确认 pin）。
- 未核实现代码（`src/` 不在本 checkout）；未核 M2-C1 字节修订的实际执行情况（属释放前置）。
- 未核 C-09 与 C-14 之外**未冻结**文档（如 C-10）与 D04–D07 的关系。

—— 报告结束（`verdict: changes_requested`；D04 6/6、D05 5/5、D06 6/6 成立；D07 前 6 项成立、第 7 项需补映射前提；§6 漏 4 条 L 项；P1×2 + P2×3）。
