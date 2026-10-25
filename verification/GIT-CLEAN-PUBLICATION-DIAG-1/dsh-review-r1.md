---
task_id: GIT-CLEAN-PUBLICATION-DIAG-1
reviewer: DeepSeek Harness
author: Codex
base_commit: e34a90d001cce1fa966aec7d2b032bb5ad1cf148
reviewed_head: fed1a9cf3295e5e05f7ffd363ac1075bd22e90b1
decision: approved
---

# Review：GIT-CLEAN-PUBLICATION-DIAG-1

2026-10-24 / DeepSeek Harness（独立 Reviewer，非作者）。本 Review 只对上述 `reviewed_head` 有效。`base_commit` 是父候选 root commit；`reviewed_head` 是**诊断仓库**在父候选之上的 +1 commit（`sandbox.py` 局部诊断字段 + 一个新 mock 测试），**不是父候选升级、不是 main 集成、不是产品修复**。父 Task `GIT-CLEAN-PUBLICATION-1` 的 DSH r1 `blocked` 不因本 Review 改变。

## 范围与依据

- 需求/AC：`doc/tasks/GIT-CLEAN-PUBLICATION-DIAG-1.md`（kind=research，`in_review`；AC1/AC2/AC4 标 MET，AC3 PARTIAL）；`verification/GIT-CLEAN-PUBLICATION-DIAG-1/APPOINTMENT.md`（`APPOINTED_PENDING_EXECUTION`，本 Review 执行后关闭该待办）；`RESULT.md`、`HANDOFF.md`、Task 的 Canonical Evidence `DIAG-01..53`。
- 被审对象（固定）：
  - 诊断仓库 `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-DIAG-1/source`，branch `codex/git-clean-publication-diag-1`，HEAD `fed1a9cf3295e5e05f7ffd363ac1075bd22e90b1`（parent `e34a90d…`，无 remote）；
  - 证据：DIAG task-env（`rust-default-parallel-r*`、`registry-isolated-1..4`、`core-r2-source-pins*`、`grant-mock*`、`grant-patch-provenance`、`packaged-*`、`evidence-helper-tests*`、`governance-final-*`、`DIAGNOSTIC_FREEZE.json`）；补包 `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/review-package-r2/`（`PACKAGE_MANIFEST.json` 62 文件）；父 Task 更新的 52 项 SOURCE_PIN。
  - 父候选 `source-export-r4`（`e34a90d`）与源 main（`349e61faf`）作为只读对照。
- 未覆盖：安装包/签名、真实模型、真实 GUI、完整产品审计；真实多 channel 持续饱和压力；真实「旧机器」icacls 错误码（历史 UNKNOWN）。以上均不在本 Task 可宣称范围。
- 只读约束：本 Review 未修改诊断仓库、父候选、源仓、证据、Task 状态或远端；未运行真实 `icacls`/未改 ACL；未重跑 Core 全套（同条件上限 2 次已用满）或任何失败测试；唯一写入为本文件。
- 视角状态：Architecture `executed`、Verification `executed`；Standards/Spec 未单独执行（`doc/templates/REVIEW.md` 已取消双轴强制）。证据收集派出 3 名只读子核查（源码差分/mock、并发/Core DB、补包/packaged），命令与原始输出已汇入本文件并经 Reviewer 独立重算交叉复核。

## Architecture

**结论：本诊断在结构、边界与归属上成立；它产出了一个可审的失败证据链与一个有界的诊断补丁，但没有（也不应）证明产品并发安全或 Core 环境缺陷。** 批准的是**诊断交付**，不是父候选可发布。

1. **诊断补丁的架构边界干净。** `src/infrastructure/plugins/sandbox.py` 的 6 行改动只在 `_grant` 的非零返回路径构造 `SandboxError` 后附加 `returncode`/`stderr` 两个属性；异常类型、`str(error)`、用户可见消息、成功缓存（`self._grants.granted.add(key)`）、失败不缓存、`OSError` 传播路径均与父候选相同；未改 IPC/Schema/协议/依赖。`tests/infrastructure/test_grant_diagnostics.py` 用 `unittest.mock.patch('infrastructure.plugins.sandbox.subprocess.run')` 替换真实调用，不可能执行 `icacls`；覆盖失败诊断、成功缓存、启动 `OSError` 三条路径。覆盖边界（只到 `_grant` 原语，不覆盖 `PluginService→PLUGIN_HOOK_UNAVAILABLE` 端到端）已在 RESULT 明示。
2. **诊断仓库与父候选/源仓的归属清晰。** `fed1a9c` 单父 `e34a90d`、仅 1 个 branch、无 remote、对象库 2 commits；父候选与源 main 均不含 `fed` 对象（不可由 push 传播）。工作树 `git status` 的 75 个 ` M` 经 `git diff HEAD`、`git diff --cached`、`hash-object` 全等证实为 **stat 缓存假象**（内容=HEAD）；索引 `stat` 记录 size = 实际 size + 行数、且 index mtime 早于工作树文件，证明是一次 CRLF 检出遗留，不是语义改动。未发现诊断行为污染父候选/源仓。
3. **证据架构可信且可独立复现。** 我独立重算：Task Canonical `DIAG-01..53` **53/53 MATCH**；`DIAGNOSTIC_FREEZE.json` **42/42 MATCH**；`review-package-r2` **62/62 pinned MATCH**（物理 63 文件 = 62 pinned + 外挂自指纹 `PACKAGE_MANIFEST.json`，由 DIAG-53/父 SUP-38 pin）；packaged bundle **6614/6614** 与构建输入 **733/733** SHA 匹配；父 Task 新增 52 项 pin **52/52 MATCH**（含我的父 Review `a14f1438…`）；诊断仓库 `HEAD`/parent/remote/refs 与声明一致。补包采用「原文件复制 + 事后 EXIT envelope」而非篡改原始日志：19 个 envelope 均标注 `RETROSPECTIVE_ENVELOPE_FROM_EXISTING_CHECKS_NOT_ORIGINAL_RUN_HEADER`、`venv=UNRECORDED`、`EXIT=… (reported by original checks; not a rerun)`，且 **19/19 envelope body SHA = 对应 raw log SHA**（原件未被改写）；EXIT 分布 12×0 / 3×1 / 4×101，失败原样保留。
4. **诚实边界逐项成立。** mock 的 `returncode=5` 只用于测试，`grant-patch-provenance.json` 明写「returncode=5 is mocked, not historical icacls evidence」；RESULT/HANDOFF 明确「r2 真实 icacls 错误码仍 UNKNOWN」「权限不足是静态推断」；packaged 验证的是 **e34 未改 packaged 源码**，非 `fed` 诊断补丁的发布版本；154 filtered 明确不视为通过；产品并发饱和风险明确未排除。
5. **保留的架构性缺口（不阻塞本次诊断结论，见 Findings）**：冻结证据的**生成器版本**未随包冻结（`r1/r2/isolated-1..4` 六份 RUN_HEADER 无 `tracked_changes` 字段，而最终 `diagnose.py` 会写该字段）；`DIAGNOSTIC_FREEZE` 未登记 3 个 `library.db` 二进制；`governance-final-*` 4 件晚于 freeze 且未被任何表登记；首轮 `packaged-tests` 元数据的 `head` 字段错记为 `fed`（已披露 + probe + 补跑修正）。

## Verification

| AC / Appointment Gate | 实际结果 | 判定 |
|---|---|---|
| Gate-1 精确 head | 诊断仓库 HEAD=`fed1a9cf3295e5e05f7ffd363ac1075bd22e90b1`；`rev-list --parents -n 1` = `fed`+`e34` 单父；`show-ref` 仅 1 branch；`remote -v` 空 | **PASS** |
| Gate-2 源码差分恰两文件 | `diff e34a90d fed1a9c --stat` = `sandbox.py +5/-1`、`test_grant_diagnostics.py +35`，2 files / +40/−1；无删除、无模式变更、无第三文件 | **PASS** |
| Gate-3 mock 证据 SHA 绑定 | `grant-patch-provenance.files[]` 的 SHA-256 = fed HEAD blob 内容 SHA-256 = 工作树 SHA-256（`b9c9cc8d…`、`a0cf6d66…`）；`grant-mock-fixed-head` head=fed、`tracked_changes=""`、2 passed、EXIT=0 | **PASS** |
| Gate-4 默认并发 = 父 e34 baseline | `rust-default-parallel-r2`：cwd=诊断 source、head=e34、argv 无 `--test-threads`、`unset=[RUST_TEST_THREADS,M2RC1_PACKAGED]`、`running 154 tests`、`151 passed / 2 failed / 1 ignored / 12 filtered`、EXIT=101、10.62s；失败为 `ac4_unreaped_…`（panic@9150）与 `ac1_consecutive_lock_timeouts_…`（panic@9278）；51 条 `capacity (32)` 告警；`r1` 为 frontendDist 缺失编译失败、未跑测试 | **PASS** |
| Gate-5 isolated 不冒充 | 4 个 `registry-isolated-*` 均 `running 1 test` / `1 passed` / `165 filtered out` / EXIT=0，argv=`--exact --nocapture`；RESULT/HANDOFF 明确「非全套通过，不计 PASS」；四个单测耗时合计 11.53s > r2 全套 10.62s，反向佐证并发非串行 | **PASS** |
| Gate-6 Core 不盲跑 | 诊断环境无 core-tests 全套产物、无 pytest basetemp；父 Task 两次全量（19:26/19:32）未改写；本 Task 仅 helper 3 passed 与 grant-mock 2 passed 两次有界 pytest | **PASS** |
| Gate-7 mock 值不冒充历史 | RESULT §R-002、HANDOFF「风险与遗留」、provenance note 三处均明确 mock≠历史；无任何文档称旧机器真实错误码已获取 | **PASS** |
| Gate-8 packaged 先冻结后执行 | `packaged-sidecar-frozen.json` 6614 文件、`frozen_utc=12:41:22` 早于首测 `12:42:20`；`packaged-tests-fixed-head` head=e34、M2RC1_PACKAGED=1、unset 源码解释器/RUST_TEST_THREADS、`12 passed / 0 failed / 154 filtered`、EXIT=0；`postcheck` 6614 文件前后不变且 `frozen_sha256` 对应；`packaged-build-inputs` 733 输入 SHA + Python 3.12.3/PyInstaller 6.22.3；首轮 head 错记 fed 已用 `packaged-source-head-probe`（actual=e34）与补跑修正 | **PASS** |
| AC1 默认并发复现与风险区分 | 复现成立（151/2/1/12，exit 101）；静态裁定区分「测试共享污染（已证实）」与「真实产品饱和风险（未排除）」；明确不得用改线程局部/放宽 MAX 刷绿；父 150/3 与本轮 151/2 的失败集合差异支持共享污染解释 | **MET** |
| AC2 DB 冻结与 `_grant` 补丁 | 3 DB 344064B，SHA 与 DIAG-50..52、DIAG-08、父包 manifest 三处一致；`plugin_events` 原文：opt0/opt1 各 1 条 `before_export`、opt2 另有 `after_export`，均为 `{"code":"PLUGIN_HOOK_UNAVAILABLE","detail":"cannot grant sandbox access to python.exe"}`；原 DB hash 未变；补丁+mock 2 passed 并绑定 fed | **MET** |
| AC3 冻结包/EXIT/串行披露 | 补包 62 文件 + 338 禁止 ID 摘要（169 行去重 338）+ 旧 checks/log 全量 + `checks-r4-clarified.json`；19 个 RETROSPECTIVE envelope 全部带标注与 EXIT，并包含原 log 原文；旧 raw log SHA 与父包一致；r2/r3 串行各 152/1/1/12、r4 才 153/0/1/12 已明示 | **PARTIAL（接受）**：旧日志未采集的 venv/环境字段不可追溯，已如实标 `UNRECORDED`；冻结清单未登记 3 个 DB、生成器版本未冻结（见 R-01/R-02） |
| AC4 packaged 真实结果 | 12 passed / 0 failed / 0 ignored / 154 filtered、EXIT=0；无模型（`weights=NOT_BUNDLED`、`SkipWeights`、日志 `detector weights not found` 走 fail-closed）；未声明安装包/GUI/release 通过 | **MET（仅本验证项）** |
| 治理检查 | 独立运行 `check.ps1 -TaskPath doc/tasks/GIT-CLEAN-PUBLICATION-DIAG-1.md` → `Governance check: PASS (3 warnings)`、exit 0，与 `governance-final-*` 一致；STATUS/REBASELINE_PLAN 当前指针为 DIAG-1 `in_review`、父 Task `in_review`/r1 blocked | **PASS（带告警）** |

**边界核对**：未把 isolated 说成默认并发通过；未把 mock `returncode=5` 说成历史 icacls；未把 packaged e34 说成 fed 发布版；未把 154 filtered 说成 PASS；未声称产品并发安全、Core 缺陷已排除或真实 ACL 已修改。父 Task AC4 仍 BLOCKED、AC5 PARTIAL，Task 文件与 STATUS 指针一致。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R-01 | P2 | 诊断证据与 `DIAG-02` `diagnose.py:50-55` | 冻结的 `diagnose.py` 会在 RUN_HEADER 写 `tracked_changes`，但 `rust-default-parallel-r1/r2`、`registry-isolated-1..4` 六份 RUN_HEADER/json 均无该字段 → 这六份证据由**早期未冻结**的运行器版本生成，无法用冻结脚本逐字节复现。不影响已核对的 argv/head/unset/计数真实性（均已独立交叉验证），但属 AC3「可追溯」范围的缺口 | `rust-default-parallel-r2.json` 无 `tracked_changes`；`grant-mock-fixed-head.json` / `evidence-helper-tests.json` / `packaged-tests-fixed-head.json` 有该字段；冻结 `diagnose.py` 的 `run()` 含该字段 | 补登当时版本或其 SHA，或在 DIAG-02/RESULT 书面声明「六份早期证据由前一版本运行器生成，差异仅缺 `tracked_changes` 字段」 | open |
| R-02 | P2 | `DIAGNOSTIC_FREEZE.json`（42 条）vs Task `DIAG-50..52` | freeze 只登记 `core-r2-source-pins.json`（DIAG-08），未登记 3 个 `library.db` 二进制 → 冻结清单本身不能自证 AC2 的 DB 字节；实际完整性由 Task 表、DIAG-08、父包 manifest 三处同 hash 佐证 | 3 DB SHA `cafc7f9a…`/`56c79f8c…`/`768e32e2…` 在 Task 表、pins、`review-package-r2/core-db/` 三处一致；freeze `files[]` 无 `.db` | 把 3 个 DB 纳入 `DIAGNOSTIC_FREEZE`，或在 RESULT 明确「DB 字节由 PACKAGE_MANIFEST 覆盖、freeze 只覆盖指向它的 pins」 | open |
| R-03 | P2 | `packaged-tests.json` / `packaged-tests.log` RUN_HEADER | 首轮 packaged 的机器元数据 `head` 错记为 `fed`（实际 cwd=`packaged-source`，e34）；虽已用 `packaged-source-head-probe.json`（actual_head=e34）与 fixed-head 补跑 + postcheck 修正并披露，但原文件保留错误字段，自动化读者可能误用 | `packaged-tests.json: head="fed1a9cf…"`, cwd=`packaged-source/...`；`packaged-source-head-probe.json: actual_head="e34a90d…", runner_source_repository_head="fed1a9cf…"` | 在 RESULT 明确「首轮 `packaged-tests.json/log` 的 `head` 字段不可作为绑定依据，绑定以 probe + fixed-head 为准」，或另存 `packaged-tests-first-attempt-INVALID-HEAD.json` 标注 | open |
| R-04 | P3 | `governance-final-GIT-CLEAN-PUBLICATION-{1,DIAG-1}.{json,log}` | 4 件（20:45:33/34）晚于 `DIAGNOSTIC_FREEZE`（20:44:59），既不在 freeze 也不在 Canonical Evidence；文档未声称其被冻结，属未 pin 辅助产物 | 文件 mtime 晚于 freeze；42 条与 53 条证据表均无这 4 件 | 在 RESULT/Task 注明为「未冻结辅助产物」，或补 freeze（需新的冻结快照，不得覆盖旧包） | open |
| R-05 | P3 | `core-r2-source-pins.json` 的 `companions` | 原 basetemp 的 `library.db-wal`/`-shm` mtime=20:13:27，晚于主 DB 19:32:24，说明冻结前有进程以 WAL 模式打开过；WAL=0B、主 DB hash 与三源一致 → `readonly` 描述中「WAL 复制前后均为 0 bytes」的「前」应改为「冻结时观测」，避免暗示从未被打开 | 原路径 `-wal` 0B/`-shm` 32768B 且 mtime 20:13:27；主 DB hash 未变 | 修改措辞为「冻结时观测 WAL 为 0B；更早的打开痕迹见 mtime」 | open |
| R-06 | P3 | `RESULT.md:41`（R-009 段） | 75 个 `git status` M 的成因描述不完整：只说 global autocrlf 影响、已设 false；实测索引 stat size = 实际 size + 行数（183882 vs 180392、359 vs 348），是 CRLF 检出遗留的 stat 缓存假象 | 75/75 条 stat size 不一致、delta ∈ {11,3490}；`git diff HEAD` 空、`hash-object` 全等 | 在 RESULT 补一句「索引记录 CRLF 检出 stat、工作树现为 LF 且与 HEAD 字节一致，故 M 为假阳性」 | open |
| R-07 | P3 | 六次 Rust 运行的 `CARGO_TARGET_DIR` | 均指向父 Task 的 `cargo-target` 缓存；日志显示仍从诊断 source 重新编译 crate、测试数据/TEMP 隔离 → 不构成串行冒充或结果复用，但「隔离数据环境」应限定为「数据/TEMP 隔离，构建缓存共享」 | 6 份 json `env_overrides.CARGO_TARGET_DIR` 指向父 `cargo-target`；`Compiling m2rc1-desktop v0.1.0 (…DIAG-1\source\…)` | 在 RESULT/HANDOFF 的「隔离数据环境」处注明构建缓存共享 | open |
| R-08 | P3 | `rust-default-parallel-r2` 证据 | 未记录 `tracked_changes` 与 `git diff --exit-code HEAD` 断言输出；只能由时间线间接证明（`sandbox.py` 修改 20:31:44 晚于 r2 结束约 20:31:25） | `diagnose.py:138` 有该断言但未写日志；r2 json 无 `tracked_changes` | 未来运行器把断言结果写入 RUN_HEADER；本 Task 以时间线 + 现工作树 `git diff HEAD` 为空作补证 | open |
| R-09 | P3 | 全部旧 raw log | AC3 的历史环境字段（`venv`、部分 env）不可追溯，已如实标 `UNRECORDED`；这是客观限制，不是可补造项 | 19 个 envelope 均 `venv=UNRECORDED`、`env_completeness` 声明只含原元数据 | 接受为已知限制；若需严格环境追溯，另授权以新变量运行（不重跑已超限的 Core 失败） | open |
| R-10 | P3 | `test_grant_diagnostics.py` | mock 只证到 `_grant` 原语 fail-closed，未覆盖 `PluginService → PLUGIN_HOOK_UNAVAILABLE` 端到端；未断言 icacls argv 内容；OSError 仍原样抛出（补丁未改） | 测试文件 35 行；`service.py:372-378` 仍 `str(error)` → `PLUGIN_HOOK_UNAVAILABLE` | 在 RESULT 覆盖边界处保留说明；如后续要端到端证据，另释测试 Task（不得修改旧 head 证据） | open |
| R-11 | P3 | `packaged-build.json` 的 `env_overrides.M2RC1_SRC_ROOT` | 该字段记录为诊断 `source/src`（fed 副本），但 `build_sidecar.ps1` 以 `$PSScriptRoot\..\..` 定位 repoRoot、`core_sidecar.spec` 以 spec 位置解析 `SRC_ROOT=REPO_ROOT/src`（= `packaged-source` e34），**不读取该变量**；实际 PyInstaller 输入只见 `packaged-source\src`，733 输入 SHA 全部对应 e34 → 无源码污染，但该 env 字段易被误读为「用 fed 源码打包」 | `packaged-build.json` env 字段；`packaged-build.log` 的 module search path；`packaged-build-inputs.json` 733/733 SHA 对应 e34 | 在 RESULT/注释中明示「该变量被 spec 忽略，实际输入以 `packaged-source` 与 733 输入 SHA 为准」 | open |
| R-12 | P3 | `review-package-r2/` 内 `checkpoint.md`、`RESULT.md`、`HANDOFF.md` | 包内三份文档是 20:33:55 冻结版，父仓 `verification/GIT-CLEAN-PUBLICATION-1/` 同名文件已于 20:37:55 更新；若复审把包内三文档当作父 Task 最新 RESULT/HANDOFF 读取，会缺少后续披露（包内哈希自洽，manifest 也未声明等价当前版） | 包内与父目录同名文件 SHA/内容差异；`PACKAGE_MANIFEST` 无「派生于当前父文档」声明 | 在 `PACKAGE_MANIFEST`/RESULT 注明「包内三文档为冻结时快照，最新披露以父目录为准；包仅作旧 checks/log + envelope + 禁止 ID 的冻结容器」 | open |
| R-13 | P3 | `freeze_review.py::verify()` | 验证器会拒绝缺失 log 引用、逐项校验 manifest SHA、检查 envelope 含 `EXIT=`/`RETROSPECTIVE_ENVELOPE`，但**不**重算 envelope 内部 `raw_sha256`/`metadata_sha256`，也不校验 envelope body==raw log；声明本身未夸大（只声明 manifest 层），本次已由独立重算补齐（19/19 body SHA = raw SHA） | `freeze_review.py:83-91`；本次独立校验 19/19 body SHA 等于 raw log SHA | 可选：在 `verify()` 增加 envelope 内部 pin 与 body 校验；不阻塞本 Task | open |

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 53 项 Canonical Evidence SHA | 脚本解析 Task 表格 + `Get-FileHash`/Python `hashlib` 逐项 | Win11 / DSH；主仓 `349e61faf`（工作区 dirty 不变） | **53/53 MATCH，0 missing** | 本文件；`doc/tasks/GIT-CLEAN-PUBLICATION-DIAG-1.md` |
| 诊断仓库 head/隔离 | `git rev-parse`、`rev-list --parents -n 1`、`show-ref`、`remote -v`、`count-objects`、`diff e34..fed` | 诊断 source | HEAD=fed、parent=e34、1 ref、无 remote、差分恰两文件 | 本文件；`git` 输出 |
| 75 个 worktree M | `git status --porcelain`、`git diff HEAD --stat`、`git diff --cached --stat`、`git hash-object` 全量、`ls-files --debug` | 诊断 source | 内容全等 HEAD；`git diff HEAD` 空；stat 缓存假象；index mtime 未被写 | 本文件；子核查 task-4 |
| mock 源码 SHA-256 绑定 | `git rev-parse HEAD:<path>`、`git cat-file blob \| Get-FileHash`、`Get-FileHash` worktree | 诊断 source fed | `b9c9cc8d…`（sandbox.py）、`a0cf6d66…`（test）三处相等；`grant-mock-fixed-head` 2 passed/exit0 | 本文件；`grant-patch-provenance.json` |
| 默认并发 r1/r2 | 读 RUN_HEADER/json/log；统计 ok/FAILED/ignored、capacity 告警、`running N tests` | 诊断 source e34 | r1=编译失败未跑测试；r2=151/2/1/12、exit101、51 条 capacity(32)、154 tests、10.62s | `rust-default-parallel-r1/r2.json/log` |
| 4× isolated 对照 | 读 4 份 json/log；核 argv/结果 | 诊断 source e34 | 4/4 `running 1 test`、`1 passed`、exit0、`--exact --nocapture` | `registry-isolated-1..4.*` |
| Core r2 DB SOURCE_PIN | `sqlite3` immutable 只读查 3 副本 `plugin_events`；对比原路径/父包 hash | 父 r2 basetemp（b1e6935） | 3 DB 344064B、SHA 三处一致；plugin_error 原文一致（opt2 另有 after_export）；原 DB 未变 | `core-r2-source-pins.json`；`review-package-r2/core-db/` |
| 冻结包 62 文件 | Python 脚本逐项 SHA-256+bytes；核对 338 ID 去重、disposition pin、旧 checks/log 覆盖 | `review-package-r2` | **62/62 pinned MATCH**（包目录物理 63 文件：62 pinned + `PACKAGE_MANIFEST.json` 自身，由 DIAG-53/父 SUP-38 外挂 pin；338 ID = 169 outer + 169 embedded、交集 0；`checks-r4-clarified.json` 派生自 `65733bec…`） | `PACKAGE_MANIFEST.json`；`forbidden-object-fingerprints.json` |
| 19 个 EXIT envelope | 逐文件检查标注/EXIT/名称对应；对 body 求 SHA 与 raw log 比对 | `review-package-r2/log-envelopes/` | 19/19 带 `RETROSPECTIVE_ENVELOPE…`、`venv=UNRECORDED` 与 `EXIT=`；19/19 **body SHA = 对应 raw log SHA**（原件未被改写）；EXIT 分布 12×0 / 3×1 / 4×101 | envelope 头尾；`PACKAGE_MANIFEST` |
| DIAGNOSTIC_FREEZE 42 文件 | Python 脚本逐项 SHA-256+bytes | DIAG task-env | **42/42 MATCH**；头部 `parent=e34`、`diagnostic_head=fed`、`source_main=349` | `DIAGNOSTIC_FREEZE.json` |
| packaged 冻结/测试/postcheck | 读 `packaged-sidecar-frozen/json/log`、`packaged-tests*.json/log`、`postcheck`、`build-inputs`、`head-probe`；独立重算 6614 bundle 与 733 输入 | packaged-source（e34） | 6614 文件冻结（1,121,604,514 B，12:41:22）早于测试（12:42:20）；**6614/6614 SHA 匹配、前后不变**；**733/733 输入 SHA 匹配**；12/0/154 exit0；首轮 head 错记 fed 已披露修正；build 从零构建（SkipWeights） | 对应 json/log；`packaged-build.log` |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GIT-CLEAN-PUBLICATION-DIAG-1.md` | 主仓 `349e61faf` | `PASS (3 warnings)`、exit 0；与 `governance-final-*` 一致 | 命令输出；`governance-final-*.json` |
| 父 Task 52 项 pin | 脚本逐项 SHA-256 | 主仓/workspace | **52/52 MATCH**（含父 Review `a14f1438…`） | `doc/tasks/GIT-CLEAN-PUBLICATION-1.md` |
| 安装包/签名/真实模型/GUI/产品审计 | 未运行 | — | NOT_RUN（Task 明确不在此范围；SkipWeights 无模型 Gate） | RESULT/HANDOFF |

## 结论与复审

**decision: approved（仅批准本诊断交付）。**

理由：
1. Appointment 的 8 项 Gate（精确 head、差分恰两文件、mock SHA 绑定、默认并发=父 e34 baseline、isolated 不冒充、Core 不盲跑、mock 值不冒充历史、packaged 先冻结后执行）**逐项通过**。
2. 证据真实性：53 项 Canonical、42 项 freeze、62 项补包、52 项父 Task pin 全部由 Reviewer 独立重算匹配；核心数字（151/2/1/12、12/0/154、771/3 不重跑、6614 文件冻结）与原始日志/字节一致；未发现虚报、伪造、选择性披露或把 filtered/ignored 当 PASS。
3. 边界诚实：产品并发饱和风险明确「未排除」、旧 icacls 错误码明确「UNKNOWN」、mock 值明确「非历史」、packaged 明确「e34 非 fed 发布版」、旧日志环境明确「UNRECORDED」。
4. 诊断结论可用：R-001 已把「默认套件存在共享状态干扰（已证实）」与「真实产品并发安全（未排除）」分开，并给出不应通过改线程局部/放宽 MAX 刷绿的正确约束；R-002 用 3 个原始 DB 的 `plugin_error` 把 Core 失败归因钉在 AppContainer 无法为系统 Python 授 ACL 的环境边界上（仍为高置信静态推断，不是已解除的缺陷）。
5. AC3 PARTIAL 作为**已知限制接受**：旧日志未采集的环境字段不可追溯，禁止补造；补包用明确标注的 retrospective envelope + 原文件保留已是最优处置。R-01/R-02 属该限制的延伸缺口，列入后续补齐建议，不推翻诊断结论。

**不构成授权的结论：** 本 Review 不改变父 Task `GIT-CLEAN-PUBLICATION-1` 的 `in_review` / r1 `blocked` / AC4 BLOCKED；不批准 push、默认分支/远端变更、产品 release、安装包或真实模型验收；不授权把 `fed` 诊断补丁集成到父候选或 main；不解除「不传播」裁决。

**后续（不属于本 Review 批准范围）：**
- 测试隔离修复与真实多 channel 饱和压力验证：需另冻范围、固定新 head、重新 Appointment；不得以 isolated 通过代替默认套件绿灯。
- Core 新环境诊断（V2–V5 变量）：需另授权，不修改真实 ACL、不重跑已达上限的全套失败。
- 若父 Task 要以新 head 复审，必须重新 Appointment，并把 DIAG 证据（DIAG-50..52、`review-package-r2/PACKAGE_MANIFEST.json`）以交叉引用方式纳入父证据链。
- R-01/R-02/R-03 建议在任何父候选升级或发布准备前补齐；R-04–R-13 为文档/口径改进（其中 R-11/R-12 建议由 Owner 在 RESULT/PACKAGE_MANIFEST 补一句说明即可，不改证据字节）。

**剩余风险：** 真实产品并发饱和下的公平性/资源上限/回收时限仍未证明（本 Task 明确不宣称）；旧机器真实 icacls 错误码 UNKNOWN；旧日志环境不可追溯；诊断补丁只在本地 `fed` head，未集成、未发布。
