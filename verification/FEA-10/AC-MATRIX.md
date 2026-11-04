# FEA-10 实施验收矩阵（Owner，2026-11-04）

实现基线 `aa7bcd6161be5df07e2b8bf546600fec04af038f`，`main` 主工作树；无 commit/push。以下是 Owner 验证，不是独立 Review 或 DSH 集成结论。**当前交付未满足全部 AC，不可关闭 Task。**

| AC | Owner 结论 | 实际证据及边界 |
|---|---|---|
| AC1 | MET | `test_prepared_run.py`：Prepare 无 INSERT/UPDATE/DELETE/BEGIN、无 Run；四元组独立 SHA-256 向量；Accept 在既有 store.accept 的 BEGIN IMMEDIATE 内重读校验，拒绝零写；Host 临时候选身份/代次/过期；真实 IPC。 |
| AC2 | PARTIAL | Prepared 路径设置字段白名单、认证键拒绝；远程 OpenAI-compatible provider 的 typed config/network/options 快照与安全 endpoint 检查已实现。**其他 provider 类型仍可只保存 ID，未冻结本地模型/实现版本及所有运行参数**；不宣称全部 provider 可重放。Prepared 白名单外设置 fail-closed；未扩 wire/Schema。 |
| AC3 | PARTIAL | 已有源文本的 `retranslate_region`：预览与实际 transport endpoint/model/body 三者摘要同值；不与四元组摘要混同。邻页内容/revision/content digest 入目标快照，接受前邻页变化 stale、接受后不变。**依赖上游 OCR 的请求正文尚不存在，预览明确标 requires_upstream_output，尚未达成所有命令的精确正文预览。** |
| AC4 | PARTIAL | retry 同键原 Run、异键失败 Page 子集/新上下文/source_run_id；历史不改，P13 durable retry 回归通过。**凭据/本地模型版本不可用统一 blocked、新配置差异确认的完整生产 adapter 流程未完成**。仅远程 typed config 具备已接受后配置隔离。 |
| AC5 | MET（seam 层） | `fault-matrix.log`：17 项测试，覆盖 10 类故障（manual/final、pause/cancel 分列）、live text/current/revision 三处零变化、成功 Step receipt/完成页计数不增；candidate retained/abandoned 可诊断。成功 live/revision/Run receipt 一个事务；编辑层 3 Region apply 成功/第三项 stale 全回滚；真实 token sequence 拒绝。source lease/Binding generation 使用注入 seam，**不是 Windows 系统级源故障或重定位验收**。编辑 candidate 与 pipeline candidate 不混用。 |
| AC6 | PARTIAL | 控制 pending 保留 Core status；取消/abandon 清掉 waiting，终态判定校验 processing/waiting 与 failed/blocked 约束；现有 RunMonitor/RunStateStore 无第二真值。**本次未新增完整非法投影组合、UI 断线重连与所有终态重启计数的专门矩阵**；现有相关回归通过，不以此替代所缺验证。 |
| AC7 | MET | 新增 prepared receipt 丢 ACK/过期前置查键、相同 wire request_id 不同 key 两操作、Control restart 同库重开；P13 StartRun/Retry durable 回归；`restart-core.log` 两个独立 Python 进程同 DataRoot/DB，`--stop` 后 `--start` 找回同 run_id。真实 stdio Core 重启重放。 |
| AC8 | MET（已执行链路） | production assembly 的 Prepare→Accept→translate provider transport→commit 测试；真实 C# Host-side CoreServiceClient↔Python stdio；Release build/全量 .NET/pytest/逐文件回归见日志。仅固定响应 transport fixture，不证明真实模型质量；新增 App typed adapter 未作原生 UI 点击验收。 |
| AC9 | BLOCKED | `verify_pins.ps1` 17/17；FEA-09 重写文件已恢复；范围检查纳入 untracked。**check.ps1 因 PLAN 的 READY 节点与 DSH 已写 Task 状态不一致失败**，PLAN/STATUS 不在 Owner 写域；独立实现 Review、DSH 集成、commit evidence pin 待 DSH。 |
| AC10 | MET（产品/代码边界） | 无新依赖、Schema、未冻结命令或共享组合根修改；三处 request builder 边界文件保持只读，复用现有 builder。测试 fixtures 为合成数据。环境偏差另见下文，不隐瞒为完全符合运行限制。 |

## 核心日志

- `logs/python-isolated.log`：指定 `tests/fea10 tests/core tests/pipeline -q` 全量，TEMP/TMP 指向 workspace fixtures。
- `logs/python-files-validated.log`：Task 列出的 14 个逐文件回归，204 passed。
- `logs/provider-regressions-second.log`：扩大 provider 回归，559 passed / 4 skipped（既有 optional dependency/环境门径）。
- `logs/fea10-fallback-final.log`：33 passed；`logs/canonical-commit.log`：真实 production Prepare/Accept/transport/commit 定向 1 passed。
- `logs/fault-matrix.log`：17 passed（逐项名称可见）；`logs/restart-core.log`：stop/start 均 EXIT=0。
- `logs/dotnet-final-tests.log`：1344 passed / 0 failed / 75 skipped、EXIT=0；`logs/dotnet-final-build.log`：0 warning / 0 error、EXIT=0；`logs/ipc-final.log`：真实 IPC 1 passed、EXIT=0（含新候选同 fingerprint 同键重放及 Core 重启）。
- `logs/pins-final.log`、`logs/governance-initial.log`，以及最终 `logs/governance-final.log`、`logs/scope.log`。

## 需求/契约落地问题（交 DSH）

1. 完整翻译链的未来 OCR 输出与 Prepare 时的精确 HTTP 正文预览存在时序缺口。当前不制造 OCR 文本，不把 requires_upstream_output 当作预览=发送的通过证据。请明确逐步 Prepare 的范围，或批准完整 immutable request builder 工作；不自行增加命令/Schema。
2. request builder 的现有 `TranslationRequestPayload.payload_hash()` 仅包含领域 payload；`OpenAiCompatibleClient._build_payload()` 才含 model/messages/options，`config.url()` 才含 endpoint。本次在 handlers 只读复用它们、以拦截 transport 证实摘要边界；`protocol.py/translation_openai.py/openai_client.py` 未修改。若需要冻结后直接发送同一 HTTP 请求对象，须按卡中窄改条款由 DSH 明确批准这三文件变更。
3. 本地/其他 provider 的配置版本快照、不可用时 blocked、以及新配置确认流程仍有实现与验证缺口，不把“存了 provider ID”视作完整快照。
4. PLAN/STATUS/Appointment 仍有 ready/旧 blocked 文字，与已授权认领不一致；Owner 仅登记，未写域外修复。

## 执行偏差与 NOT_RUN

- 早期既有回归继承系统 `TEMP/TMP=C:/Users/49745/AppData/Local/Temp`，在其中生成了测试临时材料；这不符合本 Task 的目录约束。未使用真实应用库、未额外扫描/清理系统 TEMP。最终全量已将 TEMP/TMP 重定向 `G:/CODEX/New Manga.workspace/FEA-10/fixtures/<suite-uuid>/`。早期材料保留，由 DSH 决定后续处理。
- 曾在 .NET 全量 testhost 尚未结束时启动 build，因 DLL 被占用而 EXIT=1（`dotnet-build-final.log`）；等待测试结束后 build 0 warning/0 error。失败日志保留，不作 canonical 成功证据。
- 未运行：独立实现 Review、DSH 集成/push、真实模型质量/外网 provider、Windows 系统级 source lease 故障、原生 UI 端到端、完整 provider/非法终态/重连专项矩阵。
- 初始失败和中间日志均保留，以便诊断；最终通过不改写失败历史。
