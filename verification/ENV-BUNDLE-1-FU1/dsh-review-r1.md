# ENV-BUNDLE-1-FU1 独立 Review（R1）

| 项 | 值 |
|---|---|
| Task | ENV-BUNDLE-1-FU1（packaged 驱动验收，闭环 ENV-BUNDLE-1 AC4 严格口径） |
| Owner | codex |
| Reviewer | dsh（epoch 6；独立于 Owner） |
| 交付 commit | 实现 `cffa9666f`；I1 返修 `dca85f71f`；记录 `77f760e5f` |
| 集成 commit | `b474c09b219ffd0d5c72a02f6705012dfa595996` |
| 基线 | `3bf2604dc9e8ef6be47bd80897e4df05cae077b3` |
| 结论 | **approved**（交付内容成立）；Task 状态 **`closed_with_limitations`**（AC3 受阻，已转 [HOST-TTL-BOUNDARY-1](../HOST-TTL-BOUNDARY-1.md)） |

## 1. 独立验证做了什么（可复现）

| # | 验证项 | 命令 / 方法 | 结果 |
|---|---|---|---|
| V1 | **AC2 packaged 六项（I1 前）** | 在同 worktree/commit、`M2RC1_PACKAGED=1`、`M2RC1_SRC_ROOT`/`M2RC1_PYTHON` unset 下复跑全量六项 | **4 passed / 2 failed（exit 101，111.59 s）** —— 失败项 `rc4_commands_round_trip_typed_errors`、`retype_pair_empty_page_and_typed_rejection`，均为 `CORE_UNAVAILABLE: production core startup ping timed out` → **判定 AC2 不可稳定复现，发出 I1** |
| V2 | 该失败项隔离复跑（第 1 次） | 只跑 retype 单项 | 0 passed / 1 failed（35.03 s） |
| V3 | 该失败项隔离复跑（第 2 次，负载下降） | 同上 | **1 passed / 0 failed（13.58 s）** → 证明是**负载相关假阴性**而非确定性缺陷 |
| V4 | **AC2 packaged 六项（I1 后）** | 同 V1，新默认 120 s，**在 P12/agy 仍运行的负载下** | **6 passed / 0 failed（exit 0）**；日志打印 `PACKAGED_STARTUP_TIMEOUT_SECS=120` 共 6 次 |
| V5 | I1 改动范围 | `git diff 151d14b95..HEAD` | **仅** `packaged_sidecar_tests.rs` 的启动 deadline 参数化（默认 120、断言 >0、真实 startup ping 仍强制、六项断言未改）；**未触任何产品代码** |
| V6 | 交付范围（全量） | `git diff --name-only 3bf2604dc..HEAD` | 仅 `main.rs`（+3 行 `#[cfg(test)]` 模块声明）、新增 `packaged_sidecar_tests.rs`、Task/Handoff/verification；**无产品语义、契约、Schema、依赖改动** |
| V7 | 主仓保护 | 主仓 HEAD + `git status --porcelain --untracked-files=no` | **tracked dirty 恒为 19（用户原有）**；owner 另附 status/diff 指纹前后一致证据 |
| V8 | AC4 产物刷新 | 主仓 `core_service.exe` 字节数/SHA/协议 | **68,604,146 B / protocol 1.6 → 68,717,156 B / SHA `896bd562…` / protocol 2.3**，刷新后隔离 smoke 通过 |
| V9 | 我复跑产生的副作用 | `git diff`/`--numstat` 证明零内容差异后逐项恢复 | 27 个 CRLF 纯行尾文件（两次复跑各恢复一次），工作树回到 clean |

## 2. 逐 AC 判定

| AC | 判定 | 依据 |
|---|---|---|
| AC1 前置与来源固定 | **PASS** | V8 + AC1 manifest；bundle 68,717,156 B / SHA `896bd562…` / protocol 2.3；未使用主仓旧 bundle 作为被测对象 |
| AC2 packaged 驱动验收（核心） | **PASS（I1 后）** | V1/V3 证明原验收**负载敏感**；V4 在相同负载下 6/6 通过；且新测试**断言** `M2RC1_PACKAGED=1` 与 `SRC_ROOT`/`PYTHON` unset，并在每次启动前打印 frozen exe 的**绝对路径 + 字节数 + SHA-256**——驱动对象可核验，不可混淆为 source-backed 结果 |
| AC3 packaged HostControl E2E | **BLOCKED（成立）** | 真实 frozen Core 上 `OpenHostSession` 成功，`RegisterImportSource` 返回 `REF_EXPIRED`。Owner 如实标 BLOCKED，未改产品代码 |
| AC4 主仓产物对齐 | **PASS** | V8；前后对比与统计归档 |
| AC5 不越界 | **PASS** | V5/V6；27 个行尾副作用已恢复且未入库 |
| AC6 主仓保护 | **PASS** | V7 |
| AC7 固定交付 | **PASS** | Handoff + 固定 commit + 31 行 Canonical Evidence（治理检查接受其 commit/sha pin） |

## 3. 关键结论：AC2 的 I1 已收敛

- 问题**不是伪造**：Owner 单次运行确为 6/6（机器空闲，8.73 s），证据真实。
- 问题**是验收 Gate 本身脆弱**：测试夹具对 68.7 MB 的 frozen PyInstaller `core_service.exe` 只给 30 s 启动 ping 死线；
  本项目是多 Agent 并行编排，机器经常满载 → **随机假阴性**。我给出三次反例（V1/V2/V3）后才发出 I1。
- I1 修复**未弱化任何断言**：仅把死线参数化并给出 120 s 默认；V4 在同一负载条件下 6/6 通过。
- **I1 CONVERGED，无需 I2。**

## 4. 移交与新增风险（已登记）

1. **[HOST-TTL-BOUNDARY-1](../HOST-TTL-BOUNDARY-1.md) 已释放**（Coordinator 只读复核确认）：host 把 import grant TTL 取在 Core 验证窗口的**精确上限**
   （`host_issuer.rs:152` = `unix_seconds() + 300.0`；Core `import_source_refs.py:153` 拒绝 `expires_at > now + 300`），
   即**零裕量的单点边界**，任何负向时钟偏差都必然失败 → 间歇 `REF_EXPIRED`。
   两侧时钟域**相同**（`core_assembly.py:1260` 用默认 `clock=time.time`），故不是域错配。
   **影响**：`library_import_file` / `library_import_folder`（`main.rs:409-458`，**P12 导入 UI 将要调用的命令**）正走这条路径。
2. **生产启动死线风险（只报告，未修）**：Owner 依本 Review 第 3 项要求调查并给出 `文件:行` 证据——
   生产 Host 启动同样传入 **30 s** 启动 ping（`main.rs:840` packaged、`main.rs:848` source-backed），
   失败会经 `.expect(...)` **panic**；`library_bridge.rs:617/626/633` 只接受调用方期限、无宽松默认。
   故打包应用在并发负载下存在同类冷启动误判风险。**本次未复现、未改产品代码**，已登记 `.orchestrator/BACKLOG.md`（BL-13）交 Coordinator 决定产品期限与失败处理。

## 5. 未覆盖（如实继承，不得声称）

- 既有 source-backed 全套 77 项测试、NSIS installer、GUI 安装验收 **均未运行**（`NOT_RUN`）。
- AC3 的真实端到端在修复前**不可声明通过**。
- 本 Review 未验证打包应用在真实安装布局下的启动行为。
