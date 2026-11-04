# FEA-10 实施验收矩阵（Owner，2026-11-04；r2 刷新）

实现基线 `aa7bcd6161be5df07e2b8bf546600fec04af038f`（r1）/ 起点 `25ba7cb2e`（r2 阶段 commit），`main` 主工作树；无 commit/push。以下是 Owner 验证，不是独立 Review 或 DSH 集成结论。**r2 + DSH rework r1 后：AC1–AC8、AC10 MET（R-001…R-004 已修复并加回归）；AC9 待独立 Review 与 closeout。**

| AC | Owner 结论（r2） | 实际证据及边界 |
|---|---|---|
| AC1 | MET（r1 保持） | `test_prepared_run.py`：Prepare 无 INSERT/UPDATE/DELETE/BEGIN、无 Run；四元组独立 SHA-256 向量；Accept 在既有 store.accept 的 BEGIN IMMEDIATE 内重读校验，拒绝零写；Host 临时候选身份/代次/过期；真实 IPC。 |
| AC2 | **MET（r2）** | 二选一口径（DSH ADJ §2.2）：mock-local（`mock-local-v1`）与 openai-compatible 家族（`openai-compatible-v1`）typed 完整快照（`execution`+`execution_digest` 闭环）；其余类型/未注册/缺 model/白名单外 options → Prepare `RUN_SNAPSHOT_INCOMPLETE`（`test_prepared_run.py` 3 条新测试）；敏感面：secret 不入 prepared 序列化、`credential_ref` 仅 opaque 引用、overrides 带 `token` 键拒绝；StartRun 对 unsupported binding 兼容不回归。日志 `python-main-r2.log` 1047 passed。 |
| AC3 | **MET（r2，按 ADJ §2.1 口径限定）** | 三文件窄改落地：preview 与 send 共用 `freeze_request`（同一 builder、同一冻结 config），`payloadDigestSend` 取自实际发送冻结字节；可确定请求四路一致（r1 transport 拦截测试保持绿）；上游 OCR 依赖步骤 preview=`requires_upstream_output` 不制造正文，Accept 后 provider config/settings/defaults 漂移下 send 仍发冻结 endpoint/model（`test_snapshot_retry.py::test_upstream_dependent_step_...`）；wire/契约零改动，providers 559 passed/4 skipped。**不宣称未来输出正文可预览**（DSH 裁决明示口径）。 |
| AC4 | **MET（r2）** | r1 两分支保持（同键原 Run、异键失败子集+`source_run_id`+上下文重读冻结）；r2 补：凭据不可解析→plan BLOCKED(PROVIDER_UNAVAILABLE)+vault 恢复 resume 解除；冻结 model≠live model→BLOCKED+复原解除；retry 换 provider→新 Run（`source_run_id`→旧 run、新 binding 冻结）且旧 run 快照字节不变（`test_snapshot_retry.py` 3 条新测试）。 |
| AC5 | MET（seam 层，r1 保持） | `fault-matrix.log`：17 项测试，覆盖 10 类故障、三处零变化、成功计数不增；成功 live/revision/Run receipt 单事务。source lease/Binding generation 为注入 seam，非 Windows 系统级源故障验收。 |
| AC6 | **MET（r2）** | 新增 `test_control_terminal.py`（4 passed）：pause/stop 请求持久化≠状态改变（status 仍 running、`*_requested` 位落库）；projection 只报 Core 持久 status（请求期 'running'，调度器 unit 边界兑现后才 'paused'/'cancelled'）；四终态共同不变量（processing=0/waiting=0）+completed（failed=0/blocked=0）/completed_with_failures（failed>0/blocked=0）附加判据+非法组合（终态标签+waiting 页）拒绝；同 DataRoot/DB 重开 Core 复读 PAUSED 与请求位。C# RunMonitor 无第二真值（只投影 Core 查询），既有 .NET 回归+真实 IPC 覆盖。 |
| AC7 | MET（r1 保持） | prepared receipt 丢 ACK/重启找回/异 fingerprint/request_id 非键；`restart-core` 两进程同库；真实 stdio Core 重启重放（IPC 1 passed）。 |
| AC8 | MET（已执行链路，r2 复验） | production assembly Prepare→Accept→transport→commit；真实 IPC 复跑通过（restart_core 适配后）；build 0/0；.NET 全量 1344/0/75 与基线一致；主套件/逐文件/providers 回归见 r2 日志。仅固定响应 transport fixture。 |
| AC9 | BLOCKED | pins 17/17、FEA-09 零 diff（重写文件已 checkout 恢复）、范围 0 域外（`test_control_terminal.py` 按 r2 授权入卡）、check PASS（4 warnings）。**独立实现 Review、DSH 集成、commit pins 未做**（归 DSH）。 |
| AC10 | MET（产品/代码边界） | 无新依赖/Schema/未冻结 wire/共享组合根改动；三文件窄改在 DSH 批准条款内且不动已发布传输语义（providers 回归等量）；fixtures 合成数据；r2 全程 TEMP/TMP 指向 workspace fixtures。 |

## r2 核心日志（`logs/*-r2.log`）

- `python-main-r2.log`：1047 passed、EXIT=0（隔离根 `G:/CODEX/New Manga.workspace/FEA-10/fixtures/r2-gates-*/`）。
- `provider-regressions-r2.log`：559 passed / 4 skipped、EXIT=0。
- `python-files-validated-r2.log`：卡中 20 文件 248 passed、EXIT=0。
- `dotnet-build-r2.log`：0 warning/0 error、EXIT=0；`dotnet-tests-r2.log`：1344/0/75、EXIT=0。
- `ipc-r2.log`：真实 IPC 1 passed、EXIT=0（r2 语义收紧后的适配结果；首次失败历史在 r1 `real-ipc.log`，本 log 仅保留通过运行）。
- `governance-r2.log`：PASS（4 warnings）、EXIT=0；`pins-r2.log`：17/17、EXIT=0；`scope-r2.log` + 脚本刷新的 `scope.log`：0 域外、FEA-09 EMPTY。

## r1 核心日志（历史保留）

- `logs/python-isolated.log`：1036 passed；`logs/python-files-validated.log`：204 passed；`logs/provider-regressions-second.log`：559/4；`logs/fea10-fallback-final.log`：33 passed；`logs/canonical-commit.log`；`logs/fault-matrix.log`：17 passed；`logs/restart-core.log`；`logs/dotnet-final-*.log`；`logs/ipc-final.log`；`logs/pins-final.log`；`logs/governance-*.log`；`logs/scope.log`（r2 由脚本刷新为当前状态，r1 数字以本文件记录为准）。

## r1 核心日志（原始记录，历史保留）

- `logs/python-isolated.log`：指定 `tests/fea10 tests/core tests/pipeline -q` 全量，TEMP/TMP 指向 workspace fixtures。
- `logs/python-files-validated.log`：Task 列出的 14 个逐文件回归，204 passed。
- `logs/provider-regressions-second.log`：扩大 provider 回归，559 passed / 4 skipped（既有 optional dependency/环境门径）。
- `logs/fea10-fallback-final.log`：33 passed；`logs/canonical-commit.log`：真实 production Prepare/Accept/transport/commit 定向 1 passed。
- `logs/fault-matrix.log`：17 passed（逐项名称可见）；`logs/restart-core.log`：stop/start 均 EXIT=0。
- `logs/dotnet-final-tests.log`：1344 passed / 0 failed / 75 skipped、EXIT=0；`logs/dotnet-final-build.log`：0 warning / 0 error、EXIT=0；`logs/ipc-final.log`：真实 IPC 1 passed、EXIT=0（含新候选同 fingerprint 同键重放及 Core 重启）。
- `logs/pins-final.log`、`logs/governance-initial.log`，以及最终 `logs/governance-final.log`。

## r1 需求/契约落地问题（历史保留；四项均已在 ADJ-2026-11-04-FEA-10-R2 裁决并由 r2 落地）

1. 未来 OCR 输出精确预览 → 裁决 §2.1.3 口径限定（`requires_upstream_output` + Accept 后隔离证明），r2 已落地。
2. 三文件窄改 → 裁决 §2.1.2 批准，r2 已落地（`freeze_request`/`complete_frozen`/`request_digest`）。
3. provider 版本快照/blocked/新配置确认 → 裁决 §2.2/§2.3 口径，r2 已落地（typed 快照二选一 + 凭据/版本阻挡 + retry 差异新 Run）。
4. 治理指针 → DSH 已在 r1 复核后对账修复（check PASS）。

## r1 执行偏差与 NOT_RUN（历史保留）

- 早期既有回归继承系统 `TEMP/TMP=C:/Users/49745/AppData/Local/Temp`，在其中生成了测试临时材料；这不符合本 Task 的目录约束。未使用真实应用库、未额外扫描/清理系统 TEMP。最终全量已将 TEMP/TMP 重定向 `G:/CODEX/New Manga.workspace/FEA-10/fixtures/<suite-uuid>/`。早期材料保留，由 DSH 决定后续处理。
- 曾在 .NET 全量 testhost 尚未结束时启动 build，因 DLL 被占用而 EXIT=1（`dotnet-build-final.log`）；等待测试结束后 build 0 warning/0 error。失败日志保留，不作 canonical 成功证据。
- r1 未运行：独立实现 Review、DSH 集成/push、真实模型质量/外网 provider、Windows 系统级 source lease 故障、原生 UI 端到端、完整 provider/非法终态/重连专项矩阵（其中终态/控制矩阵已由 r2 补齐）。
- 初始失败和中间日志均保留，以便诊断；最终通过不改写失败历史。

## DSH rework r1（2026-11-04，按 FEA-10-impl-r1 Review 处置）

- Review 结论 changes_requested（1 P0 + 3 P1 + 12 P2），报告 `doc/reviews/FEA-10-impl-r1.md`（reviewed_head `a9293458`）。
- 修复（DSH 实现；独立复查待新 head Review）：
  - R-001（P0）：settings replay 白名单改为「执行段强白名单 + 非执行段过滤」，补真实 `typeset` 键；合法用户设置不再使 Prepare 失败。
  - R-002（P1）：`run_binding_available` 接受 `provider_id`/`provider_profile_id`/`id` 三形状；freeze 规范化 `provider_id`。
  - R-003（P1）：未注册/未 typed fallback 在 freeze/validate 统一 fail-closed `RUN_SNAPSHOT_INCOMPLETE`（不再泄漏 TypeError）。
  - R-004（P1）：`RunPayloads.PrepareRun` 注入与 StartRun 相同的 Host 默认 provider_bindings；Core Prepare 继承 StartRun 的 `provider_profiles` 门径；本地 provider（manga-ocr/paddle/korean OCR）typed 快照，默认 `{"ocr":"manga-ocr"}` 可 Prepare。
  - R-005：本地 provider 版本漂移在 resolve 校验（typed local adapter）。
  - R-012：InMemory 适配器与 SQLite seam 的 pause/cancel 差异显式标注，等价 seam 由 AC5 故障注入覆盖（既有 pipeline 语义测试保持绿）。
  - R-008：真实 IPC 证据改写 workspace（不再污染 tracked 文件）。
  - R-009/R-010：check 警告数修正为 4；scope 基线说明见下。
  - R-014：认证材料键扫描限定 provider_bindings/设置浅层，glossary 词条 `token` 不再误拒。
  - 其余 P2（R-006/R-007/R-011/R-013/R-015/R-016）登记为非阻断债务，未在本次修复。
- 新回归：`test_prepared_run.py` +4（settings 过滤/合法键、glossary token、mapping 形状、untyped fallback、local typed 默认 binding）；Host 单测 `PreparedRunPayload_CarriesTheSameHostDefaultBindingsAsStartRun`。
- 门禁（DSH 实跑，`logs/dsh/dsh-rework-*.log`）：pytest 主套件 1051 passed、providers 559/4；build 0/0；.NET 全量与真实 IPC 结果见同日日志。
- scope 口径（R-010）：AC9 的「0 域外」指 **Owner 字节**；DSH 治理指针文件（PLAN/STATUS/ADJ/Handoff）为 Integrator 单点编辑，不属 Owner 写域；`git diff aa7bcd6..<head> -- doc/contracts verification/FEA-08 verification/FEA-09 组合根` 为空。

## DSH rework r2（2026-11-04，按 FEA-10-rework-review-r1 处置）

- Review（新 head `ed60c1d2`）changes_requested：P0=0、P1=2（RR-01/RR-02）、P2=6。报告 `doc/reviews/FEA-10-rework-review-r1.md`。
- RR-01（P1，已修复）：prepared 的 settings/overrides 现在**规范化到执行面**——非执行段从 `settingsSnapshot` 与持久化 Run 中移除（不是仅跳过校验）；认证材料扫描恢复为任意嵌套键拒绝（glossary 子树豁免）；执行段未知键仍 fail-closed；accept 时对当前配置过滤后比较，保持 stale 检测（`test_nested_authentication_material_cannot_enter_a_prepared_run` 等）。
- RR-02（P1，已修复）：Canonical Evidence commit 回填为包含证据的 rework/final 提交；DELIVERY-MANIFEST 在提交前生成并在清单中记录 `excluded_docs`（Task/Handoff/Review 属 DSH 指针文档，不参与字节清单）；handoff 的 warnings 计数修正为 4；rework 记录措辞修正。
- RR-03（P2）：pytest 日志按本轮实跑保存（`logs/dsh-rework2-*.log`）；此前日志的失败历史保留未改写，本表只引用实跑结果（1052 passed）。
- RR-04（P2，已修复）：`frozen_fallbacks` 非 Mapping 时统一 `RUN_SNAPSHOT_INCOMPLETE`。
- RR-05（P2，已修复）：本地 typed resolve 同时校验 provider_type 与 model；执行 validate 限定已知本地类型集合。
- RR-06（P2，已修复）：Core Prepare 拒绝非对象 `provider_bindings`（`INVALID_REQUEST`），不再落成 UNKNOWN。
- RR-07（P2，已修复）：tracked `ipc/real-ipc.txt` 稳定化为历史说明，无随机 DataRoot。
- RR-08（P2）：文档计数/测试名/R-005 口径已按本轮实跑校正；build 日志已保存（`logs/dsh-rework2-dotnet.log`）。

