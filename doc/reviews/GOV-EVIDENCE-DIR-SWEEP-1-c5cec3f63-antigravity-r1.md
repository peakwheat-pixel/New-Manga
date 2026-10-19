---
task_id: GOV-EVIDENCE-DIR-SWEEP-1
reviewer: Antigravity
reviewed_head: c5cec3f63
verdict: APPROVED
conversation_id: 4fad67e9-d36b-4569-ac93-366a48a57ac2
note: 5 个 REGISTER 均有内容依据且被 Closeout 引用；NOT_APPLICABLE 区分成立；加表错误修正彻底
---
# Task GOV-EVIDENCE-DIR-SWEEP-1 只读 Review 报告

- **审查对象**：`Task GOV-EVIDENCE-DIR-SWEEP-1`
- **被审 Head / Commit**：`c5cec3f63`（及 Handoff pin 修复 `23336a1a7`，涉及交付提交 `24fcfae13`）
- **审查类型**：只读审计（未修改任何文件）
- **总体结论**：`APPROVED`

---

## 一、三项核心问题核对结论

### 1. 五个 `REGISTER` 判定是否都有内容依据（核心核对）

**结论**：**全部 5 个文件判定为 `REGISTER` 理由充分、依据扎实；0 个应当 `ARCHIVE`。**
交付方对文件内容（包括两份失败日志的 `EXIT_CODE=101`）的描述**完全准确**。

#### 实际读取到的内容摘要与证据价值核对：

1. [`verification/EXPORT-REVEAL-1/post-merge-packaged-capture-error.log`](file:///G:/CODEX/New%20Manga/verification/EXPORT-REVEAL-1/post-merge-packaged-capture-error.log)
   - **实际内容摘要**：共 7 行。编译 `m2rc1-desktop v0.1.0`（8.74s），运行 `unittests src\main.rs` 时报错 `error: Unrecognized option: 'A'`，提示 `error: test failed, to rerun pass '--bin m2rc1-desktop'`，末尾为 `EXIT_CODE=101`。
   - **内容核对**：交付方描述完全一致。
   - **判定依据**：**不应归档**。此日志是 EXPORT-REVEAL-1 合并后进行 packaged 测试首次运行失败的真实排错日志，对应 Task [EXPORT-REVEAL-1.md](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L111) Closeout 第 111 行“逐次日志已归档”的现场事实，证明测试非一次性伪造，具有排查留存价值，与纠正参数后通过的 `post-merge-packaged.log` 共同构成完整验证链。

2. [`verification/EXPORT-REVEAL-1/pytest-core.log`](file:///G:/CODEX/New%20Manga/verification/EXPORT-REVEAL-1/pytest-core.log)
   - **实际内容摘要**：共 15 行。pytest 运行 `tests/core/` 测试，包含 1 条关于 `Image.Image.getdata` 的弃用警告，末尾明确总结：`405 passed, 1 warning in 32.00s`，`EXIT_CODE=0`。
   - **内容核对**：交付方描述完全一致。
   - **判定依据**：**不应归档**。在 [EXPORT-REVEAL-1.md](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L108) Closeout 第 108 行中明确引用了合并前交付事实：“Core `tests/core/**` 405 passed”，该文件即为此处引用的真实原始数据依据；与已登记的合并后测试 `post-merge-python.log` 分属不同阶段。存在现行文档事实引用，必须登记保留。

3. [`verification/EXPORT-REVEAL-1/rust-packaged.log`](file:///G:/CODEX/New%20Manga/verification/EXPORT-REVEAL-1/rust-packaged.log)
   - **实际内容摘要**：共 41 行。编译产生 2 条 warning，运行 8 项 `packaged_sidecar_tests` 测试全部通过，汇总：`test result: ok. 8 passed; 0 failed; 0 ignored; 0 measured; 83 filtered out; finished in 11.65s`，`EXIT_CODE=0`。
   - **内容核对**：交付方描述完全一致。
   - **判定依据**：**不应归档**。在 [EXPORT-REVEAL-1.md](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L108) Closeout 第 108 行中明确引用了合并前交付数据：“packaged sidecar 8 passed”，是合并前 packaged 测试原始事实依据（合并后版本为 9 passed，记录在 `post-merge-packaged.log`）。存在现行文字引用，必须登记保留。

4. [`verification/EXPORT-REVEAL-1/rust-source.log`](file:///G:/CODEX/New%20Manga/verification/EXPORT-REVEAL-1/rust-source.log)
   - **实际内容摘要**：共 115 行。编译产生 2 条 warning，运行 83 项单元测试，82 项通过，1 项忽略（`tests::perf_chunk_request_digest_cost ... ignored`），8 项过滤，汇总：`test result: ok. 82 passed; 0 failed; 1 ignored; 0 measured; 8 filtered out; finished in 5.08s`，`EXIT_CODE=0`。
   - **内容核对**：交付方描述完全一致。
   - **判定依据**：**不应归档**。在 [EXPORT-REVEAL-1.md](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L108) Closeout 第 108 行中明确引用了合并前交付数据：“Rust source 82 passed / 1 ignored”，该文件是合并前 source 测试原始事实依据（合并后版本为 86 passed，记录在 `post-merge-source.log`）。存在现行文字引用，必须登记保留。

5. [`verification/P15/cargo-test-unfiltered-first-run.log`](file:///G:/CODEX/New%20Manga/verification/P15/cargo-test-unfiltered-first-run.log)
   - **实际内容摘要**：共 468 行。完整记录了编译与测试执行过程。运行 108 tests，其中 95 项通过，12 项失败（全部是 `packaged_sidecar_tests` 中的环境变量/sidecar fail-closed 门卫断言 `"" == "1"` 失败），1 项 ignored，汇总：`test result: FAILED. 95 passed; 12 failed; 1 ignored`，`EXIT_CODE=101`。
   - **内容核对**：交付方描述完全一致。
   - **判定依据**：**绝不应归档**。在 [P15.md](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L115) Closeout Record 第 115 行原文中明确字面点名：“**证据诚实性（正向记录）**：Owner 保留未过滤首跑的失败日志并**如实命名为 `cargo-test-unfiltered-first-run.log`（exit 101）**，说明其为 `packaged_sidecar_tests.rs:23` 的 `M2RC1_PACKAGED=1` **环境门卫 fail-closed**...”。此文件不仅有现行强引用，而且是工程治理中表扬“诚实保留失败事实”的核心物证，归档移动会导致审计依据凭空消失。

---

### 2. AC4 标记 `NOT_APPLICABLE` 是否恰当

**结论**：**区分完全成立，标记恰当且符合逻辑。**

1. **语义层面**：
   - AC4 的标题定义是 `**AC4 执行移动（仅 ARCHIVE 项）**`。该条款在结构上是一个**条件型动作**（Conditional AC），其执行对象严格限定为 `ARCHIVE` 候选集。
   - 前置步骤 AC2/AC3 基于文件内容与现行引用严格审计后，得出 `ARCHIVE` 候选集为空集（0 个项）。对空集合执行移动，其结果自然是“无动作产生”，本条款在此前置结果下已逻辑闭环。
2. **「不需要」vs「做不到」的区分**：
   - `BLOCKED`（如 `EXPORT-REVEAL-1` AC4-③）：目标是明确需要达成的交付物（打开真实 GUI 资源管理器），但在本环境下由于外部客观阻塞（Windows headless 无头环境报 `0x80070578` 且缺少真实导出路径）而“**想做却做不到**”。
   - `NOT_APPLICABLE`（本 Task AC4）：目标是“移动被判定为冗余归档的文件”。但在内容审计后确认全部 5 个文件均有现行引用与证据价值，根本不属于归档范畴，因此“**客观上不需要移动任何文件**”。
   - 将“不需要做”标记为 `BLOCKED` 反而是虚假的，会向后续审计传递“本该移动却因故障卡住”的误导信号。因此 `[x] <<NOT_APPLICABLE: 逐文件判定结果为 0 个 ARCHIVE，无文件需移动>>` 是准确且诚实的表述。

---

### 3. 错误加表修正是否彻底

**结论**：**修正彻底，结构完整，无交叉污染。**

1. **表位置核验**：
   - 在 [`doc/tasks/EXPORT-REVEAL-1.md`](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L131-L134) 中，补列的 4 行确实完整位于 `## Canonical Evidence` 表内，置于 `## Resource Manifest` 标题之前。
   - 在 [`doc/tasks/P15.md`](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L98) 中，补列的 1 行（`E9`）确实完整位于 `## Canonical Evidence` 表内，置于 `## Resource Manifest` 标题之前。
2. **`Resource Manifest` 纯净性**：
   - 两个 Task 的 `Resource Manifest` 表均未被污染，原有结构原封不动（`EXPORT-REVEAL-1` 仅保留 1 行 worktree 登记；`P15` 仅保留 1 行 worktree 登记）。
3. **表格结构完整性**：
   - 两个 Task 的 `Canonical Evidence` 表格均严格包含完整的 6 列：
     `| evidence_id | AC/Gate | path | commit | sha256 | class |`，无缺列或错位问题。

---

## 二、治理检查实测结果

执行用户指定的治理检查命令，实测输出如下：

### 1. 本 Task 检查
```powershell
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-EVIDENCE-DIR-SWEEP-1.md
```
- **结果**：`Governance check: PASS (1 warnings)`
  - 1 warning 为既有的 `doc/STATUS.md 已达到预算的 80%`，无任何 FAIL。

### 2. 全局检查
```powershell
pwsh -NoProfile -File tools/governance/check.ps1
```
- **结果**：`Governance check: PASS (1 warnings)`（指向当前 STATUS 节点 P20，PASS）。

### 3. `EXPORT-REVEAL-1.md` 检查
```powershell
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/EXPORT-REVEAL-1.md
```
- **结果**：`Governance check: FAIL (2 errors, 1 warnings)`
  - 错误数从修复前的 **7 errors 下降至 2 errors**。
  - 剩余 2 个错误为：
    1. `FAIL: Evidence SHA-256 不匹配：doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（契约时间性演进失配，归属于 `GOV-PIN-LINEAGE-1`）
    2. `FAIL: DONE 不能保留未完成 Acceptance Criteria；范围未完成时使用 closed_with_limitations。`（真实情况 AC4-③ `BLOCKED`）
  - 原有的 `evidence_dir 含未登记文件` 错误已彻底消除，剩余错误与本次改动完全无关。

### 4. `P15.md` 检查
```powershell
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P15.md
```
- **结果**：`Governance check: FAIL (2 errors, 1 warnings)`
  - 错误数从修复前的 **4 errors 下降至 2 errors**。
  - 剩余 2 个错误为：
    1. `FAIL: Evidence SHA-256 不匹配：apps/desktop/frontend/src/settings/SettingsPage.test.tsx`（后续提交改动测试，归属于 `GOV-PIN-LINEAGE-1`）
    2. `FAIL: Resource manifest 不存在：verification/P15/resource-manifest.json`（缺失外部 manifest 文件，归属于 `GOV-P15-MANIFEST-1`）
  - 原有的 `evidence_dir 含未登记文件` 错误已彻底消除，剩余错误与本次改动完全无关。

---

## 三、最终评审结论与推荐下一步

- **评审裁定**：`APPROVED`
- **推荐下一步**：
  建议将本审查结论通知 **Codex**，由 Codex 执行治理合流：
  1. 在 `doc/tasks/GOV-EVIDENCE-DIR-SWEEP-1.md` 中记录 Review 结论，将 AC5 标记完成；
  2. 推进 Task `GOV-EVIDENCE-DIR-SWEEP-1` 状态至 `approved` / `done`；
  3. 后续按 Plan 推进处理剩余既有治理缺陷的独立任务（如 `GOV-PIN-LINEAGE-1` 与 `GOV-P15-MANIFEST-1`）。
