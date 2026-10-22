<!-- 本文件由 Antigravity 出具、dsh 机械转录，未改动其正文。原始 JSON（含 conversation_id 6017310c-35c0-4a87-abea-297f8ed771e5）见 G:/CODEX/New Manga.workspace/agent-output/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/agy-review-run1.json 与 verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/raw/agy-review-run1.json -->
---
task_id: GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1
reviewer: antigravity
author: dsh
base_commit: 8e31aaa1dff113e5f95ca7db5ece0de00126059a
reviewed_head: 3264e0b61ea509ff1cd0db46be85567a0a0adb25
decision: approved
---

# 独立审查报告：GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1

## 1. 审查范围与依据

### 1.1 审查对象
- **代码仓库**：`G:/CODEX/New Manga`（分支 `main`）
- **基线提交（base_commit）**：[`8e31aaa1dff113e5f95ca7db5ece0de00126059a`](file:///G:/CODEX/New%20Manga)
- **交付提交**：[`d4ac5452514f54147cff2bfd087ecf36305db947`](file:///G:/CODEX/New%20Manga)（实现）+ [`3264e0b61ea509ff1cd0db46be85567a0a0adb25`](file:///G:/CODEX/New%20Manga)（证据回填）
- **审查指针（reviewed_head）**：[`3264e0b61ea509ff1cd0db46be85567a0a0adb25`](file:///G:/CODEX/New%20Manga)
- **任务定义与交接**：
  - 任务文件：[`doc/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md`](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md)
  - 交付文件：[`doc/handoffs/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md`](file:///G:/CODEX/New%20Manga/doc/handoffs/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md)
  - 上游取证矩阵：[`verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/matrix.md`](file:///G:/CODEX/New%20Manga/verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/matrix.md)
  - 交付证据：[`verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/`](file:///G:/CODEX/New%20Manga/verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/)

### 1.2 审查操作特征
- 本次审查为**严格只读模式**：未创建、修改或删除工作树中的任何跟踪与非跟踪文件；未执行任何 Git 写操作（commit / merge / reset / checkout / push）；未执行工作区清理命令（无 `--apply`）。
- 所有验证命令均在独立环境中只读执行或输出至仓外临时工作区 `G:/CODEX/New Manga.workspace/temp/agy-review/`。

---

## 2. Architecture 审查结论

### 2.1 解释层安全性与防旁路能力
1. **严格禁止环境变量与通配符展开**：
   - 在 [`tools/governance/clean_workspace.py`](file:///G:/CODEX/New%20Manga/tools/governance/clean_workspace.py#L1997-L2005) 的 `absolute()` 函数中，对 relative path 执行了强制断言：禁止反斜杠、禁止 `GLOB_RE`、禁止 `ENV_RE`、禁止空/当前/上级路径片段。
   - 对于 `RRI-04`（`%TEMP%/.tmp* created by Rust tempfile tests`），标记为 `NON_IDENTITY_RECORD`，代码中明确执行 `require("target_abs" not in b and "targets" not in b, ...)`，绝不进行路径拼接、解析或通配求值，直接映射为非身份记录，从根本上杜绝了通配符泄漏。
   - 对于 `RRI-06` 和 `RRI-07`（指向 `%APPDATA%/com.newmanga.m2rc1.desktop/{catalog,data,derived}`），Policy 显式固化为绝对路径目标数组，直接断言其必须为已存在的目录，不执行任何动态环境变量解析。
2. **错误匹配的强单义性（一对一强绑定）**：
   - 遍历 `bindings` 时，代码严格要求 `len(b["errors"]) == 1`，每个 Binding 只能绑定恰好一个声明错误；
   - 逐项校验 `error["file"] == origin`、`index.errors.count(error) == 1` 且 `error not in removed`；
   - 最终执行双向基数断言：`require(len(removed) == 7 and len(index.errors) == 7, "ERROR_MISMATCH", ...)`。如果仓库中出现第 8 个错误（无论是新增文件引入、还是历史声明未覆盖），或者 7 个错误未完全匹配，该解释层直接触发 `ERROR_MISMATCH` 并整体拒绝生效（Fail-Closed）。
3. **目标存在性双向防御契约**：
   - `ALREADY_ABSENT_PATH`（E1–E3）：使用 `os.path.lexists` 严格断言目标绝对不存在。一旦历史目标在磁盘被意外创建（哪怕是空目录或悬空符号链接），立即触发 `RESIDUAL_TARGET_PRESENT` 报错并恢复 Fatal。
   - `PRESERVE_ROOTS`（E6–E7）：使用 `os.path.isdir` 严格断言目标必须在磁盘真实存在且为目录。一旦用户数据目录缺失，立即触发 `RESIDUAL_TARGET_MISSING` 报错并恢复 Fatal。
4. **运行期一致性与防篡改校验（TOCTOU 防御）**：
   - Policy 必须受 Git 跟踪（`require(enabled, "POLICY_UNTRACKED")`）；
   - Canonical JSON 摘要通过硬编码常量 `RESIDUAL_RUNTIME_IDENTITY_DIGEST` 严格锁定；
   - 在扫描结束前再次执行 `policy_digest(read_bytes(RESIDUAL_RUNTIME_IDENTITY_POLICY)) == RESIDUAL_RUNTIME_IDENTITY_DIGEST`，且对全部 live targets 重新调用 `_resolve_identity` 检查，杜绝扫描并发篡改。

### 2.2 核心不变量保持
- 针对 6 项核心治理与历史文件执行 `git diff 8e31aaa1d..3264e0b61`，结果严格为空：
  - [`doc/tasks/P19.md`](file:///G:/CODEX/New%20Manga/doc/tasks/P19.md)
  - [`verification/ENV-BUNDLE-1-FU1/resource-manifest.json`](file:///G:/CODEX/New%20Manga/verification/ENV-BUNDLE-1-FU1/resource-manifest.json)
  - [`verification/P19-UI-FIX-1/resource-manifest.json`](file:///G:/CODEX/New%20Manga/verification/P19-UI-FIX-1/resource-manifest.json)
  - [`tools/governance/historical-evidence-interpretation.json`](file:///G:/CODEX/New%20Manga/tools/governance/historical-evidence-interpretation.json)
  - [`tools/governance/broad-root-preservation.json`](file:///G:/CODEX/New%20Manga/tools/governance/broad-root-preservation.json)
  - [`tools/governance/resource-manifest.schema.json`](file:///G:/CODEX/New%20Manga/tools/governance/resource-manifest.schema.json)
  - [`tools/governance/non-declaration-json-exceptions.json`](file:///G:/CODEX/New%20Manga/tools/governance/non-declaration-json-exceptions.json)
- 既有解析器规则与错误分类机制零修改；既有 STATUS-r212 清理禁令与所有保护根集合完全保持。

---

## 3. Verification 审查结论

### 3.1 AC 逐项核验表

| AC 项 | 状态 | 独立验证命令 / 证据 | 结论与比对 |
|---|---|---|---|
| **AC1**（Policy 文件与摘要锁定） | **PASS** | 验证常量 [`RESIDUAL_RUNTIME_IDENTITY_DIGEST`](file:///G:/CODEX/New%20Manga/tools/governance/clean_workspace.py#L1971-L1972) 与 [`tools/governance/residual-runtime-identity.json`](file:///G:/CODEX/New%20Manga/tools/governance/residual-runtime-identity.json) 的规范 JSON SHA-256 匹配；字段校验完整。 | **一致**。Canonical SHA-256 值为 `5a47481d9bee7752fab5270b1bf7b348a855bdd3e8445fcf05e78cf36fd51b88`，实测严格匹配。 |
| **AC2**（挂接位置与单义校验） | **PASS** | 检查 [`tools/governance/clean_workspace.py`](file:///G:/CODEX/New%20Manga/tools/governance/clean_workspace.py#L2302-L2303)，确认挂接在 `_apply_historical_evidence_interpretation` 之后；前置检查上游错误；Origin 与 Line 校验通过。 | **一致**。上游解释失败时主动阻断；逐项校验 raw SHA-256、byte length、line SHA-256 及唯一 error 匹配。 |
| **AC3**（四类身份落地） | **PASS** | 检查 E1–E3 映射为 `ALREADY_ABSENT` 非保护身份；E4/E5 不生成 Declaration；E6/E7 为 APPDATA 三个目录注册保护根。 | **一致**。E6/E7 成功注册 `catalog`、`data`、`derived`（对应 `PRESERVE_REFERENCED` 与 `PRESERVE_USER_DATA`）。 |
| **AC4**（Warning 替换与审计留痕） | **PASS** | 检查原 7 项 fatal 错误被替换为 `DECL_RESIDUAL_RUNTIME_PRESERVED` warning，包含完整 policy/id/kind/origin/sha/declared/provenance 元数据。 | **一致**。实测 warnings 恰好净增 7 条，内容包含可追溯 provenance。 |
| **AC5**（生产声明审计 7 项降为 0） | **PASS** | 运行 `clean_workspace.py --audit-declarations --out G:/CODEX/New Manga.workspace/temp/agy-review`。 | **一致**。Fatal errors 由 7 降为 0，EXIT CODE 为 0；原 1936 个保护根为新保护集合的严格真子集；APPDATA 目录被 `evaluate()` 正常命中；无通配泄漏。 |
| **AC6**（6 类负例 Fail-Closed） | **PASS** | 运行 [`tools/governance/tests/test_residual_runtime_identity.py`](file:///G:/CODEX/New%20Manga/tools/governance/tests/test_residual_runtime_identity.py)；覆盖 6 类负例场景。 | **一致**。12/12 单元与负例测试全部通过（14.68s），退出码 0。各负例均包含精准断言，非空测试。 |
| **AC7**（治理脚本与提交固定） | **PASS** | 运行 `pwsh -NoProfile -File tools/governance/check.ps1`；`git diff --check 8e31aaa1d..3264e0b61`。 | **一致**。Governance check: PASS (2 warnings)；git diff --check exit 0；delivery_head 固定为 `d4ac54525`。 |

### 3.2 保护集合只增不减与缺口补齐验证
- 读取 [`verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/protection-delta.json`](file:///G:/CODEX/New%20Manga/verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/protection-delta.json)：
  - `before`: 2639 declarations / 1936 protected roots / 7 errors / 285 warnings
  - `after`（交付提交 d4ac54525 时）：2648 declarations / 1939 protected roots / 0 errors / 292 warnings
  - `roots_dropped`: `[]`（无任何既有保护根被丢弃）
  - `roots_added`: 补齐了 APPDATA 用户数据目录的 3 个保护根：
    - `c:/users/49745/appdata/roaming/com.newmanga.m2rc1.desktop/catalog`
    - `c:/users/49745/appdata/roaming/com.newmanga.m2rc1.desktop/data`
    - `c:/users/49745/appdata/roaming/com.newmanga.m2rc1.desktop/derived`
  - 实机核验：确认上述 3 个目录在当前 Windows 宿主上真实存在且为目录。
- 独立复验声明审计（在 reviewed_head `3264e0b61` 上复跑）：
  - 声明计数：2655 declarations / 1945 protected roots / 0 errors / 292 warnings（EXIT 0）
  - 口径说明：commit `3264e0b61` 在 Task 中回填了 7 条 Canonical Evidence 表行（EV-01..EV-07），由扫描器作为合法的 `EVIDENCE_PIN` 纳入，因此声明数较 d4ac54525 净增 7 条，protected roots 净增 6 个，errors 保持为 0。这严格符合 r2 口径约定（以 7 项历史运行身份错误降为 0 为断言，而非机械绑定全仓绝对声明数）。

### 3.3 测试套件判别力与无伪造审查
- [`tools/governance/tests/test_residual_runtime_identity.py`](file:///G:/CODEX/New%20Manga/tools/governance/tests/test_residual_runtime_identity.py)：
  - `test_fixture_baseline_is_the_seven_errors_without_the_stage`：验证了在未加本 stage 前，复制真实 origin 的 fixture 真实重现了历史 7 项错误码（`DECL_DESTINATION_UNRESOLVED`, `DECL_ENV` x4, `DECL_RELATIVE_AMBIGUOUS`, `DECL_UNKNOWN_DISPOSITION`），证明 fixture 具有真实反映缺陷的能力。
  - 6 类负例覆盖：
    1. `test_wrong_digest_fails_closed` -> 抛出 `POLICY_DIGEST_MISMATCH`（错误总数 8）
    2. `test_origin_drift_fails_closed` -> 抛出 `SOURCE_DRIFT`（错误总数 8）
    3. `test_present_absent_target_fails_closed` -> 抛出 `RESIDUAL_TARGET_PRESENT`（错误总数 8）
    4. `test_missing_preserve_target_fails_closed` -> 抛出 `RESIDUAL_TARGET_MISSING`（错误总数 8）
    5. `test_unbound_error_blocks_the_stage` -> 抛出 `ERROR_MISMATCH`（错误总数 9，未绑定错误阻断阶段并保留原错误）
    6. `test_tampered_policy_body_fails_closed` -> 抛出 `POLICY_DIGEST_MISMATCH`（错误总数 8）
  - 所有负例断言均检查了具体的错误码及错误总数，无任何空断言或假测试。
- 防回归测试：
  - `python -B tools/governance/tests/test_path_header_compat.py`：5/5 OK
  - `python -B tools/governance/tests/test_ac_gate.py`：12/12 OK

### 3.4 未运行项真实性与日志一致性
- 核对 [`verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/verification-log.txt`](file:///G:/CODEX/New%20Manga/verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/verification-log.txt) 第 5 节：
  - 产品测试套件（pytest / vitest / cargo）：记录为 `NOT_RUN`（未改动产品代码与契约，合理）；
  - `clean_workspace.py --apply`：记录为 `NOT_RUN`（禁令生效，无删除授权，必须保持未运行，合理）；
  - linked worktree 内完整 audit：记录为 `NOT_RUN`（worktree 缺少主仓未跟踪的 P22 原件，属于已知特性，在主 checkout 完成验证，合理）；
  - 独立 Review：记录为 `PENDING`。
- 确认：**没有任何未运行项被虚假标记为 PASS**。

---

## 4. Findings 表

| ID | 级别 | 文件与行号 | 触发与影响 | 复现证据 | 建议处置 | 状态 |
|---|---|---|---|---|---|---|
| **OBS-01** | P2 (Observation) | `tools/governance/clean_workspace.py` (历史代码行 783, 2271 等) | 在 Python 3.14 下执行测试时触发较多 `ResourceWarning: unclosed file` 告警输出。 | 运行 `test_residual_runtime_identity.py` 时终端打印 `ResourceWarning`。 | 属于既有工具未包裹 `with` 语句的历史现象，不影响退出码与判别逻辑。后续维护治理工具时可统一添加 context manager。 | CLOSED (无需阻塞) |

*本次审查未发现任何 P0（阻断级）或 P1（严重级）缺陷。*

---

## 5. 结论与复审要求

### 5.1 审查决策
**决策：`approved`**

本交付严格遵循了上游 `GOV-RESIDUAL-RUNTIME-IDENTITY-1` 的研究取证结论，在未触碰任何历史原件字节、未修改既有解析规则、未发生任何真实资源操作的前提下，成功构建了高内聚、强防御的精确解释层。7 项历史运行身份错误已安全归零，真实 APPDATA 用户数据已纳入保护，不变量与负例判别力真实有效。

### 5.2 后续要求
- **集成复验与 Task 关闭**：
  - 依协作协议与 Task 规定，请 Owner（`dsh`）在 `main` 分支同点完成集成复验；
  - 复验通过后，在 [`doc/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md`](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md) 中勾选 AC1–AC7，补齐 Closeout Record，将状态置为 `done`；
  - 同步更新 [`doc/STATUS.md`](file:///G:/CODEX/New%20Manga/doc/STATUS.md)、[`doc/REBASELINE_PLAN.md`](file:///G:/CODEX/New%20Manga/doc/REBASELINE_PLAN.md) 与 [`doc/TASK_LEDGER.md`](file:///G:/CODEX/New%20Manga/doc/TASK_LEDGER.md)。
- **严正重申禁令**：
  - 本次 Approval 及声明错误归零**绝不构成解除 STATUS-r212 清理禁令的理由**，也**不构成任何删除、迁移、归档或 Git prune 的授权**。

---

## 6. 推荐下一步与可转发指令

### 推荐下一步
推进父任务 `GIT-MAINLINE-CONVERGENCE-1` 的下一阶段：执行 103 个本地分支与 141 个工作树的增量盘点与 A/B/C/D 治理分类，严禁执行破坏性操作。

### 可转发指令（下一节点）
```text
从 G:/CODEX/New Manga 当前 main 先读 doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/handoffs/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md 与 verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/matrix.md，核对 HEAD 与 epoch 10 租约。GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1 已经 Antigravity 独立审查 approved，声明审计的 7 项历史错误已降为 0 且 APPDATA 用户数据已受保护。下一步是推进 GIT-MAINLINE-CONVERGENCE-1 的收敛盘点：以 verification/GIT-MAINLINE-CONVERGENCE-1/branch-analysis.json 与 worktree-analysis.json 为基线复用既有证据，只补查新增 6 分支/6 工作树的变化；对 103 heads 逐项给出 A/B/C/D 分类与最小授权清单。不得在 r212 禁令下执行任何删除、归档、引用移除或 prune；真实处置必须另提具体对象、证据、影响与最小授权并等待用户裁决。
```

