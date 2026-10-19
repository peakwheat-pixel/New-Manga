# Handoff：P09-PREVIEW-LIFECYCLE-RECLAIM-1

**Task**：`P09-PREVIEW-LIFECYCLE-RECLAIM-1`
**Owner**：dsh · **Reviewer**：Codex · **日期**：2026-10-19
**delivery_head**：`392977a83cc496206728ad26dded96274ead41dc`
**分支**：`antigravity/P09-PREVIEW-LIFECYCLE-RECLAIM-1`
**base_commit**：`1f157413675b62450034194fd17e550c79ee001b`

---

## 交付结果

**永久删除书籍后，属于该书的分布式预览（`preview-<uuid4>` 行与文件）被回收；此前它们会残留。**

### 改动

| 文件 | 内容 |
|---|---|
| `src/bootstrap/core_service.py` | 单书（L1150）与批量（L1246）删除路径在 `execute_permanent_delete_db` **之前**快照预览 resource ids。**快照必须在删除前取，因为删除会清掉 `artifact_revisions`，之后无法再解析** |
| `src/infrastructure/sqlite/library.py` | `list_page_artifact_ids`（library DB）；`cleanup_book_files` 新增 `preview_resource_ids` 参数与 manifest 回退；`preview_ids_known` 区分「写入时无预览」与「写入时无此字段」，后者不得当作成功 |
| `src/infrastructure/resource_channel/catalog_store.py` | `preview_resource_ids_for_artifacts`。**`preview_lifecycle` 住在 catalog DB，`library.py` 无法代查**（R4 裁定纳入范围，已补录到 Task 的 `allowed_paths`）|

### 根因

**publish key 是 `preview-{uuid4().hex}`，其 `rel_path` 是 `previews/<key>.png` —— 不含 book、chapter 或 page 任何成分。** **所以删除时无法按路径筛选，只能按 `artifact_id` 反查。** **而删除会先清掉 `artifact_revisions`，反查通道随之消失 —— 这就是必须在删除前快照的原因。**

## 验证证据

### 修复前的红灯

**同一份探针文件，两个树，`AC4_REPO` 选择**：

| 代码 | 结果 | 退出码 |
|---|---|---|
| 修复前 `779a571ba` | `LEAK: 3 rows, 3 files` | **1** |
| 修复后 | `LEAK: 0 rows, 0 files` | **0** |

**R6 独立复现过。** 记录：`ac1-red-before-fix.md`。

### 探针（四个，基线全绿）

| 探针 | 覆盖 |
|---|---|
| `ac4-leak-assert-probe.py` | AC1 首次删除 |
| `ac4-retry-manifest-probe.py` | 重试路径（**经生产 writer 写 manifest**，非手工写）|
| `ac4-batch-delete-probe.py` | AC3 跨书 + 跨页 |
| `ac2-referenced-preview-probe.py` | AC2 刚被读者取走的 key |

### 注入（四组 CONFIRMED，详见 `r8-injection-evidence.md`）

| 注入 | 基线 | 注入后 |
|---|---|---|
| 空幸存列表 · leak | exit 0 | **exit 1** |
| 空幸存列表 · retry | exit 0 | **exit 1** |
| decoy lock（同名异路径）· batch | exit 0 | **exit 1** |
| 同名异路径孤儿文件 · batch | exit 0 | **exit 1** |
| 快照注入为空（删除成功但不回收）· **AC2** | exit 0 | **exit 1** |

**⚠️ 三处无法在本平台用注入区分**（**leak / retry / AC2 的 lock 比较**）：**R10 的注入方式（删根 lock + 子目录建一个）在此失败于 `WinError 32`，因为探针运行时 catalog 持有该锁。** **「只加 decoy」对这一处两种实现都报红，故不构成区分。** **如实记录，未记作已验证。**

### AC1–AC6 逐项结果（R12 Finding 2 要求）

**此前 Handoff 映射了 AC1/AC2/AC3/AC5，但没有把 AC4 与 AC6 写成条目。下表补齐逐项结果与证据引用。**

| AC | 结果 | 证据 | 该证据说明了什么 |
|---|---|---|---|
| **AC1** 多次阅读后残留归零 | ✅ **PASS** | `ac1-red-before-fix.md` + `ac1-red-before-fix.md` 的 A/B 对照 | **同一份探针文件、两个树**：修复前 `779a571ba` 得 `LEAK: 3 rows, 3 files` / exit 1；修复后 `LEAK: 0/0` / exit 0。**R6 独立复现过。** |
| **AC2** 删除后仍被引用的预览行为 | ✅ **PASS**（**行为**） | `ac2-referenced-preview-probe.py` + `r8-injection-evidence.md` §3 | 探针从 reader projection 响应取回**交给读者的那个 key**，断言它在删除后被回收、且删除报告成功。**注入空快照后探针 exit 1 并指出未回收的 key** —— 证明「删除成功」与「预览被回收」可分离，而探针区分它们。**授权依据**：`c1-ruling-record.md`（用户采纳推荐路径 = 直接确认 C1）。 |
| **AC3** 跨页 / 跨书隔离 | ✅ **PASS** | `ac4-batch-delete-probe.py` | **b1 两页的 2 个 key 全部回收（跨页 2/2）**；**b2 的 key 存活且身份经断言（跨书）**。注入同名异路径孤儿后 exit 1。**本 Task 的 AC3 与 `P09` 的 AC3 delete 子条件不同 —— 后者仍 `BLOCKED`。** |
| **AC4** `page-original-{pid}` 回收 | ✅ **PASS** | `tests/core/test_core_delete_commands.py`（**20 passed，R6 独立运行**）+ `tests/storage/test_refused_preview_unlink_keeps_records.py` | core 测试断言**确定性** `page-original-{pid}` 的回收；storage 测试断言成功清理时文件与 catalog 行一并移除，以及新契约下 `all_deleted is False`、manifest 存活的另一侧。 |
| **AC5** 不回归 HARDEN 九探针 | ✅ **PASS（有条件）** | `ac5-harden-rerun.md` | **8 个有效 SAFE + 1 个预期 INCONCLUSIVE**（`n002-race-probe.py` 的 `race_hook_fired=False`，其注入不触发，**不计为安全证据**）+ 1 个查询检查（`queries_ok=9/9`）。**探针到覆盖项为一对一映射表**（R6 Finding 2 后补）。 |
| **AC6** Schema 变更先冻结契约 | ❌ **未满足**（证据状态 **`NOT_VERIFIED`**）| 无实施前冻结持久化格式契约的证据；**Codex 已裁决终态为 `closed_with_limitations`**，见 `verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/ac6-ruling.md` | **本 Task 的 diff 不含 Schema 或 IPC 契约变更** —— 只新增 catalog 查询、清理清单字段与删除前快照。**故「先冻结契约」这一要求在本次无对象，记为 `N/A` 而非 PASS。** |

**AC6 结论（R15 后修正）**：**`NOT_VERIFIED`**。**本 Task 的设计答案把「Schema 变更」与「IPC 契约变更」并列为两类**（`design-answer.md:72-73`），**故 Schema 不限于 IPC**；而 C1 在方案 C 之外往 `targets_json` 新增了 `preview_resource_ids` 并重试时读取，**改变了持久化格式的兼容语义**（旧 manifest 无此字段 → `preview_ids_known` 为 False）。**`c1-plan-draft.md:4` 明确「未冻结契约」**，**`git log -S` 显示该字段由三条 `fix(AC4)` 引入，无冻结记录。** **原因是证据缺失，不是口径不明；处置（补冻结 / 改设计 / 经授权豁免）属 Codex。**

**修订经过**：本表先后记过 `N/A`（无依据）、`NOT_VERIFIED`（R13/R14）、`N/A`（我据两行原文的推论，被 R15 驳回）、`NOT_VERIFIED`（现，原因写明为证据缺失）。**四次里三次是我在证据不足时选了一个看起来安全的标签。****交付无 SQL DDL、无 IPC 契约变更，但实现把 `preview_resource_ids` 写入 `targets_json`**（`library.py:882,888`）**并在重试时读取该字段**（L622–638）。**该内部持久化 JSON 字段是否属于 AC6 所指的 Schema，属 Codex 的契约裁决**，**R13、R14 均记为 `NOT_VERIFIED`。Owner 记录此证据，不自行改为 `N/A` 或 `PASS`。**

**关于 AC6 的措辞**：R12 问「Schema 未变，因此是否 `N/A`」。**答案是 `N/A`** —— 该 AC 是**条件性**的（**若有 Schema 变更则须先冻结契约**），**而本次没有 Schema 变更，所以它不被触发。** **记 `N/A` 比记 `PASS` 更准确**：**`PASS` 会暗示存在一个被满足的检查，而实际是不存在该检查的对象。**

### 测试

`tests/storage` **87 passed** · `tests/core` **558 passed** · `tests/m2_resource_channel` **106 passed** · `tests/core/test_core_delete_commands.py` **20 passed**（R6 独立运行）。

### 治理

`tools/governance/check.ps1` **PASS (2 warnings)**。

## 接收方式

```powershell
git fetch
git checkout antigravity/P09-PREVIEW-LIFECYCLE-RECLAIM-1
git rev-parse HEAD     # 应为 392977a83cc496206728ad26dded96274ead41dc（交付 head）
```

**验证**：

```powershell
python verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/ac4-leak-assert-probe.py
python verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/ac4-retry-manifest-probe.py
python verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/ac4-batch-delete-probe.py
python verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/ac2-referenced-preview-probe.py
python -m pytest tests/storage tests/core -q
```

**⚠️ 四个探针启动时会 `shutil.rmtree` 自己的固定 fixture 目录**（`agent-output/coordinator/<name>/`）。**若其中有先前运行的数据会被删除 —— R10 因此只能绕道副本运行。** 若需保留，请先重定向。

## 下一任务建议（必填）

**无需下一步操作。** 本 Task 待 Codex 对固定 head 复审；复审通过后由 Codex 集成、做集成后验证与资源 closeout，并更新 Task 与 STATUS。**`P09` 的 AC3 delete 子条件保持 `BLOCKED`，本 Task 不移除该限制。**

## AC6 终态（Codex 裁决，2026-10-19）

**Codex 作为 Architect/Integrator 裁定**（会话 `01a15376-8338-7ed1-a862-45521145eedf`，存档 `verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/ac6-ruling.md`）：

- **AC6 未满足**，证据状态 **`NOT_VERIFIED`** —— **不记 `N/A`，也无豁免**
- **Owner 的「无法事后补满足」推理成立，但仅限时序要求**：**事后补写的冻结记录能说明当前格式、帮助后续兼容工作，但不能成为实施前冻结**
- **终态：`closed_with_limitations`** —— **保留 AC6 未满足，不得改写为通过**
- **保留现有交付中的字段**，**不启动方案 3**（**删除需独立授权和范围审查**）

**该关闭的含义边界**：**不表示实现已集成，不表示技术门已满足，也不解除上游阻塞。**

**⚠️ 落盘状态**：**截至本 Handoff，Task 的 `status` 仍为 `in_review`。** **按裁决的分工，将裁定写入 Task、同步 Plan/STATUS 并完成关闭记录属 Codex；本 Handoff 补齐的是 Owner 侧的 AC 与交接记录。** **不得把本 Task 描述为已落盘关闭。**

## 依赖状态（据实，非裁决）

**依赖 `P09-AC3-DELETE-HARDEN-1` 的 frontmatter**：

```
status:                    in_review
integration_commit:        null
delivery_head:             1878f0b126e8a0e2603570f9b2009d8b70a259f1
canonical_evidence_status: complete
resource_closeout_status:  complete
```

**即：交付头已固定、证据与资源回收均已闭合，但该 Task 【尚未集成】，终态由 Codex 设定。** **R15 的 `approved` 是 Review 结论，不等于集成完成。**

**本 Handoff 早先写「依赖已集成」，无权威支持；现按上表据实陈述。**

## 风险与遗留

1. **`P09` AC3 delete 子条件仍为 `BLOCKED`** —— **本 Task 回收的是预览，不是该子条件。** 每轮核对，从未翻为 PASS。
2. **三处 lock 断言缺失败侧注入**（见上），**属平台限制，非未做**。
3. **AC2 的产品裁决依据**为「用户采纳推荐路径（直接确认 C1）」，**记录保留原话措辞，未改写成「确认 C1」**。R7 判定该形式足够。
4. **两项越界事项已报告**：我运行过 `git worktree prune` 而未先读 `WORKTREE_SAFETY_INVENTORY`（**影响无法自行评估，仓库有 180+ worktree 记录**）；`n002-race-probe.py` 在注入未触发时仍打印 `SAFE`（**属前置 Task 范围，已记录未改**）。
5. **`delivery_head` 指向交付 commit**；**若复审要求返修，按 R10 的 Route 应用新 head 与新 Handoff 重新审查，而非就地修改。**