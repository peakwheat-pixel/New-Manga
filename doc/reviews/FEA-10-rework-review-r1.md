---
task_id: FEA-10
reviewer: DSH 独立子 agent（父会话 session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4 派发；全新只读上下文，未参与实现/返修/证据生成）
reviewer_kind: subagent
author: DSH（rework r1 实现/集成）；前序 Codex/ZCode/DSH
base_commit: a92934585088fe75ce8ec53452a67c0a72496d31
reviewed_head: ed60c1d2293234d326ecf8d265a8ca4e711fd026
decision: changes_requested
---

# Review：FEA-10 rework r1（新 head 独立实现 Review）

## 0. 审查者身份与来源

- 身份：DeepSeek Harness 主会话（`session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4`）派发的**独立子 agent**，全新只读上下文；本会话未参与 FEA-10 的 r1/r2 实现、rework r1 返修或任何证据生成。
- 审查对象：`reviewed_head=ed60c1d2293234d326ecf8d265a8ca4e711fd026`（rework r1；前序 r2 交付 `a9293458`、阶段提交 `25ba7cb2`）；审查 diff `a9293458..ed60c1d2`，并在必要处回看 `aa7bcd6..ed60c1d2`。
- 对照输入：`doc/tasks/FEA-10.md`（AC1–AC10、rework 记录、Canonical Evidence）、`doc/reviews/FEA-10-impl-r1.md`、`doc/reviews/FEA-10-rework-r1.md`、`doc/reviews/ADJ-2026-11-04-FEA-10-R2.md`、C-08（`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md`）、C-13/C-05/C-04b、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev 2.12 §5.5、`doc/handoffs/FEA-10-handoff.md`、`verification/FEA-10/**`。
- 只读约束：未修改生产代码/测试/证据/契约，未 commit/push。唯一写入是本文件；测试与探针只在 `G:/CODEX/New Manga.workspace/FEA-10/fixtures/review2-*` 下创建，TEMP/TMP 亦指向该 workspace，未写系统 AppData。审查开始和结束时 `git status --porcelain` 均为空，HEAD 保持 `ed60c1d2`。

## 1. 结论

**changes_requested（不可 approved / 不可 closeout）。**

rework r1 中四项主要修复都有真实代码与可复跑证据：

- R-001 的合法 settings 面不再使 Prepare 失败；冻结 `typeset` 键（`stroke_enabled`/`auto_font_size`）和 `providers`/`network` 段均可 Prepare。
- R-002 的 `provider_id`/`provider_profile_id`/`id` 三形状在 freeze 后均可 plan（`available=True`、OCR 已 committed 后 `status=pending`）。
- R-003 的未注册/未 typed fallback 现在稳定抛 `RUN_SNAPSHOT_INCOMPLETE`，不再泄漏 `TypeError`。
- R-004 的 Host 默认 `{"ocr":"manga-ocr"}` 注入已接到 `RunPayloads.PrepareRun`，生产注册表的 `local-manga-ocr-onnx` typed 快照可 Prepare/Accept；新增 C# 单测与真实 IPC 均通过。

但本轮**新增了一个 P1 安全/AC2 缺陷**：为处理 R-014 的 glossary 误拒而收窄认证材料键扫描后，嵌套在非执行 settings 段（甚至任意未知段）中的 `headers`/`authorization`/`signing_key`/`bearer` 可以绕过扫描，进入 `settingsSnapshot` 并随 Accept 持久化到 `pipeline_runs.settings_snapshot_json`；嵌套 `token` 虽被 `_redact` 从 snapshot 去掉，但仍原样出现在 `PreparedRun.overrides`（及启用 wire evidence 时的 `core-service.ndjson`）。同时“非执行段过滤”实际只是跳过校验，并未从 snapshot 移除，文档描述与实现不符。

另有 **1 个 P1 证据缺陷**：R-009 没有真正修复——Canonical Evidence 行的 commit 与 sha256 互斥错配，`DELIVERY-MANIFEST` 的 `head` 仍是 `3e01fae8`、Task 卡哈希与当前树不一致，handoff 仍保留 r2 的 `3 warnings`；rework record 却声称 manifest 已随 rework head 重新生成。若按“前序 findings 未真正修复必须给 P0/P1”的口径，该 P2 证据项在本轮升为 P1。

P0：**0**。P1：**2**（RR-01、RR-02）。P2：6 项（RR-03…RR-08）。AC1–AC8、AC10 的机制基本成立，但 **AC2 因 RR-01 不成立**；AC9 仍 BLOCKED。

## 2. Findings

> 级别定义沿用前序 Review：P0 阻断（交付不可用/AC 不能成立）；P1 必修（正确性/安全/冻结契约/证据正确性）；P2 非阻断（边界、可维护性、证据整洁）。所有 finding 状态为 open（本会话不修复）。

| ID | 级别 | 文件:行 | 问题与影响 | 依据 | 修复建议 |
|---|---|---|---|---|---|
| RR-01 | **P1** | `src/application/tasks/store.py:99-101, 213-242`；`src/infrastructure/sqlite/pipeline.py:1502-1522, 1596-1604`；`src/application/tasks/service.py:398, 407` | R-014 的修复把认证键扫描收窄为 `provider_bindings` 深扫、settings 段浅扫、其他 key 一层扫描；同时 R-001 对不在 `settings_fields` 的 section 直接 `continue`。结果：嵌套在未知/非执行 section 中的 `headers`/`authorization`/`signing_key`/`bearer` 不被拒绝，`_redact` 也不覆盖这些键，`headers` 会进入 `settingsSnapshot` 并随 Accept 持久化；嵌套 `token` 从 snapshot 被 `_redact` 去掉，却仍出现在 `prepare_run` 返回的原始 `overrides` 中。这直接违反 AC2 的敏感面要求。 | AC2「敏感认证材料不入普通快照/日志/错误/证据」；ADJ §2.2「token/password/secret 及其可逆编码不入快照、日志、错误、证据」；M2-C1 §5.5 `PreparedRun`/`redactedPayloadPreview` 安全边界（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:240, 253`）；C-08 SC-R05 | 恢复对认证键的递归拒绝，但为已知用户内容路径（如 `translate.glossary` 的 term/translation 值）建显式 allowlist；或彻底从 snapshot 中去掉非执行 section，并对 `overrides` 回显做同样的结构化过滤；补 `headers`/`authorization`/`signing_key`/`bearer` 嵌套用例与 glossary `token` 正向用例。 |
| RR-02 | **P1** | `doc/tasks/FEA-10.md:212`；`verification/FEA-10/DELIVERY-MANIFEST.json:2, 39, 64`；`doc/handoffs/FEA-10-handoff.md:130`；`doc/reviews/FEA-10-rework-r1.md:19` | R-009 未真正修复：①Canonical Evidence 行写 `commit=a9293458` + `sha256=77ac0450…`，但 `77ac…` 是 `ed60c1d2` 的 AC-MATRIX worktree 哈希，`a9293458` 的同一文件 worktree 哈希为 `7428c009…`，commit 与字节互斥；②`DELIVERY-MANIFEST` 的 `head=3e01fae8`（不是 rework head），Task 卡 manifest 哈希 `2615eca2…` 与当前树 `45221d6f…` 不一致；③handoff `:130` 仍写 `check PASS（3 warnings）`，本次实跑为 4；④rework record 声称 manifest “随 rework head 重新生成”不成立。 | AC9 证据/Handoff/EV；模板证据纪律；前序 R-009 的修复要求 | 以最终 rework head 为基线重新生成 manifest、changed-files、scope；把 Canonical Evidence 的 commit 改为 `ed60c1d2`（或 `pending`）并重算/回填正确 sha256；修正 handoff 的 3→4；在 Task 卡/AC-MATRIX 记录 manifest 生成时点与生成后编辑。 |
| RR-03 | P2 | `verification/FEA-10/logs/dsh-rework-pytest.log:15, 81-83`；`doc/reviews/FEA-10-rework-r1.md:30`；`doc/tasks/FEA-10.md:239`；`verification/FEA-10/AC-MATRIX.md:70` | 声称“pytest 主套件 1051 passed（+4 新回归，无 failed）”，但唯一保存的 rework pytest 日志是 `2 failed, 1049 passed`（两个 `tests/pipeline/test_pipeline.py` pause/stop 用例）。本会话独立重跑 `tests/fea10 tests/core tests/pipeline` 两次均为 **1051 passed**（说明最终 head 可通过），但该日志不是成功门禁的证据，且失败历史未在 record/卡中披露。 | AC9 证据纪律；前序 R-009/R-012 的证据要求 | 保存最终 head 的成功日志并保留失败历史说明；若失败可复现则修 test isolation/InMemory 适配器差异；不要把中间失败日志当作“无 failed”证据。 |
| RR-04 | P2 | `src/application/tasks/store.py:114-120`；`src/bootstrap/core_service.py:4716-4726` | R-003 报告路径已修，但 `for fallback in value.get("frozen_fallbacks", {}).values()` 未先校验容器类型；手工/损坏候选把 `frozen_fallbacks` 传成 list 时抛 `AttributeError`，Core 投影为 `UNKNOWN/internal`，仍违反冻结三错误码。 | AC2 的 fail-closed 错误码；C-08/M2-C1 §5.5 | 先断言 `frozen_fallbacks` 为 Mapping，每个 fallback 为含 `execution` 的 Mapping，否则 `RUN_SNAPSHOT_INCOMPLETE`；加损坏候选测试。 |
| RR-05 | P2 | `src/infrastructure/providers/registry.py:461-469`；`src/application/tasks/store.py:170-178` | 本地 typed provider 的 `resolve_for_run` 注释称 replay identity 是 `(provider_type, model, adapter_version)`，实际只比较 `model`；本会话探针仅改 live `provider_type` 时 `run_binding_available` 仍为 True。`validate_provider_execution` 的 local 分支还接受任意 `local-*`（除 4 个排除项），未限制到 `_LOCAL_TYPED_PROVIDER_TYPES`/已注册 provider。 | AC4「版本不可用→阻塞」；AC2 typed 快照完整性；ADJ §2.2 | 同时比较 `provider_type` 与 adapter version（或完整 execution digest），local 校验限制到 typed 集合；补 type-only drift 与未注册 `local-*` 负例。 |
| RR-06 | P2 | `apps/desktop-avalonia/src/NewManga.App/Services/RunContracts.cs:428-447`；`src/infrastructure/sqlite/pipeline.py:1597`；`src/bootstrap/core_service.py:4556, 4716-4726` | R-004 的 Host 默认注入对正常路径成立，但 `PrepareRunOverrides` 只在存在 `provider_bindings` key 时原样返回；值为 `null`/非对象时会原样写入 wire，而 StartRun 的 dispatcher 会以 `INVALID_ARGUMENTS` 拒绝。Core `prepare_run` 随后在 `_merge(..., None)` 抛 `AttributeError`，经 `except Exception` 变成 `UNKNOWN`，不是 `INVALID_REQUEST`/`RUN_SNAPSHOT_INCOMPLETE`。 | AC1/AC4 的错误码与 StartRun/Prepare 同源语义；R-004 的修复目标 | 在 C# 与 Core 两侧都校验 `overrides.provider_bindings` 为对象（或 null 视为缺省），非法形状返回 typed `INVALID_REQUEST`；补 null/字符串/数组用例。 |
| RR-07 | P2 | `tests/NewManga.Host.Tests/Fea10RunIpcTests.cs:72-74`；`verification/FEA-10/ipc/real-ipc.txt:1`；`tools/governance/check.ps1` warning | R-008 的“移到 workspace”已生效（本会话实跑 IPC 未产生 tracked 变更），但仓库仍 tracked 的 `verification/FEA-10/ipc/real-ipc.txt` 保留着旧随机 DataRoot；`check.ps1` 仍把它列为未登记过程文件。该证据不可复现且与“证据字节稳定”目标冲突。 | AC9 证据纪律；R-008 | 把旧文件移入 workspace/归档或列为 SOURCE_PIN 并说明来源；测试文档只引用 workspace 路径。 |
| RR-08 | P2 | `doc/reviews/FEA-10-rework-r1.md:14,22,30`；`verification/FEA-10/AC-MATRIX.md:64,69-70`；`doc/tasks/FEA-10.md:131`；`doc/handoffs/FEA-10-handoff.md:139` | 文档与证据计数/名称不一致：C# 单测实际名 `PreparedRunPayload_CarriesTheHostDefaultBindings`，记录写成 `...TheSameHostDefaultBindingsAsStartRun`；`test_prepared_run.py` 实际 15 passed，卡写 11；R-005 在 rework record 是“部分修复”、handoff 是“未修复”、AC-MATRIX 是“已实现”，三种口径；R-012 称“既有 pipeline 测试保持绿”，但 rework 日志显示 2 failed。 | AC9 证据陈述一致性；Review 处置如实性 | 统一 R-005 处置口径；按实际测试名/计数刷新卡、AC-MATRIX、handoff；对结果日志逐项引用，不写“无 failed”除非有对应日志。 |
| RR-09 | P2 | `verification/FEA-10/logs/dsh-rework-dotnet.log:1-188`；`doc/tasks/FEA-10.md:239` | 只有 `=== test ===` 的全量测试日志（1345 passed / 0 failed / 75 skipped，逐程序集求和一致）；rework 声称的 `build 0 warning/0 error` 没有对应的 `dsh-rework-build.log`。本会话只跑了定向 App 测试与真实 IPC（`--no-build`），未重跑全量 build/test。 | AC9 证据完整性；Task 验证矩阵 | 补存一份 rework build 日志（命令/EXIT/0 warning）或在卡中把 build 证据指向实际文件；不要把 test 日志当作 build 证据。 |

### RR-01 复现（本会话只读探针，workspace fixture）

```text
# 合法 sections（providers/network/reading/translation/typeset）全部存在时
R001 legal sections Prepare: OK sha256:ff65ea62e
R001 snapshot sections: ['network', 'ocr', 'providers', 'reading', 'translation', 'typeset']
# 嵌套 headers/authorization/signing_key/bearer（未知/非执行 section）
snapshot= {"ocr": {"script": "japanese"}, "unknown": {"nested": {"headers": "Bearer SECRET-A"}}}
accepted=True run providers={'nested': {'headers': 'Bearer SECRET-A'}}
persisted contains secret: True
# 嵌套 token：snapshot 被 _redact 去掉，但 overrides 原样回显
overrides= {"settings": {"unknown": {"nested": {"token": "SECRET-D"}}}}
secret in overrides: True
secret in settingsSnapshot: False
```

可见“非执行段”既没有被移除（`settingsSnapshot` 仍含 `providers`/`network`/`unknown`），也没有被强类型扫描；`headers` 这类不在 `_SENSITIVE_PARTS` 中的认证键会落盘。这是 R-014 修复引入的新缺陷，不是旧问题复现。

### RR-02 复现（只读哈希核对）

```text
# worktree CRLF 口径
a9293458 AC-MATRIX = 7428c009b94e58ce08a3938e93baf6511fba42f1502591253c753e230ffb41f7
ed60c1d2 AC-MATRIX = 77ac045019c9c30b1f5883bf90ba157f10609acc27c5ed3c4191a9b260ba9db6
Task 卡当前 = 45221d6f8bbad5d321f504d5b0655ca733f426726d830de72af48053fe000ff4
manifest 记录 = 2615eca2de202fd01f69a86db9385ca815e0665bd21db1c396844b325c43f622
manifest head = 3e01fae83738fcc0441882cb8b827202e4319c10
```

`EV-FEA10-OWNER` 行同时写 `commit=a9293458` 与 `sha256=77ac…`（rework 内容），两者不能同时成立；manifest 的 `head` 与 Task 卡哈希也停留在 rework 之前。

## 3. 逐 AC 独立判断

| AC | 卡上结论（rework） | 本会独立判断 | 理由 |
|---|---|---|---|
| AC1 | MET | **MET（机制）** | Prepare 零 DB/零执行、四元组 digest、Accept 在 `BEGIN IMMEDIATE` 内重读；本会话主套件与 `test_prepared_run.py` 通过。R-004 的默认 binding 注入让 Prepare 在真实默认路径可用。 |
| AC2 | MET | **NOT MET（因 RR-01）** | 合法 settings 面与 typed provider 快照已修；但嵌套认证键可进入 settingsSnapshot/持久化 Run（headers 等），且 `overrides` 回显未过滤；AC2 敏感面不成立。R-006 的 StartRun 兼容偏差仍登记债务（前序 P2）。 |
| AC3 | MET（ADJ §2.1 限定） | **MET（按限定口径）** | 三文件窄改未回退；preview/send 共用冻结 builder，`payloadDigestSend` 取实际发送字节；Accept 后配置漂移测试通过；主套件通过。 |
| AC4 | MET | **MET（附边界）** | R-002 三形状已修（本会话探针 `available=True`、OCR committed 后 `status=pending`）；凭据/版本阻塞与 retry 分支测试仍在。边界：本地 typed provider 的 version drift 仍仅比较 model（RR-05），R-005 仍为债务；本地 type-only drift 未测。 |
| AC5 | MET（seam 层） | **MET（seam 层，附边界）** | 故障矩阵与 candidate-only 提交未改动；R-012 的 InMemory/SQLite 差异已文档化，生产 seam 由 AC5 注入覆盖。边界：R-013（crash_restart 非 commit 断言）、R-015（source lease 错误码）仍为债务。 |
| AC6 | MET | **MET（Python/DB 层，附边界）** | 控制 pending/终态矩阵未改动，主套件通过。边界：R-007（`is_terminal` 无生产消费者、C# 无专项）仍为债务。 |
| AC7 | MET | **MET** | durable receipt、同键重放、异 fingerprint、`request_id` 非键、Core 重启重放；主套件与真实 IPC 通过。 |
| AC8 | MET | **MET（附边界）** | R-004 的 Host 默认注入已落地，新增 C# 单测 1 passed；真实 IPC 1 passed；日志显示 .NET 1345/0/75。边界：真实 IPC 只到 Prepare/Accept/重放，不执行 plan/commit；生产 assembly 的 Prepare/Accept/commit 由 Python 测试覆盖；RR-06 的 null override 仍可返回 UNKNOWN。 |
| AC9 | BLOCKED | **BLOCKED** | 冻结契约/FEA-08/09/组合根零 diff、pins 17/17、check PASS（4 warnings）；但 RR-02 的 Canonical Evidence/manifest/Handoff 仍不一致，RR-03 的失败日志与“1051 passed”陈述冲突；独立 Review 即本文件，尚未 approved，不能 closeout。 |
| AC10 | MET | **MET** | 未新增未冻结 Schema/wire/依赖；共享组合根零 diff；三文件窄改在 DSH 授权内；fixtures 合成数据。 |

## 4. 独立验证记录

| 场景 | 命令/步骤 | 结果 |
|---|---|---|
| 仓库状态 | `git rev-parse HEAD`；`git status --porcelain=v1` | HEAD `ed60c1d2`；工作树干净 |
| 范围/冻结 | `git diff --name-only aa7bcd6 ed60c1d2 -- doc/contracts verification/FEA-08 verification/FEA-09 <组合根>` | 空（冻结契约、FEA-08/09 证据、组合根未改） |
| Rework diff | `git diff --name-only a9293458 ed60c1d2` | 19 文件；含 DSH 治理指针 `doc/STATUS.md`，其余在 Task allowed_paths/证据目录内 |
| 治理 | `pwsh -NoProfile -File tools/governance/check.ps1` | EXIT=0；PASS（4 warnings，含 `ipc/real-ipc.txt` 未登记过程文件告警） |
| Pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | EXIT=0；17/17 PASS |
| 主套件 | `TEMP/TMP=<review2-fixture> C:/Python314/python.exe -m pytest tests/fea10 tests/core tests/pipeline -q -p no:cacheprovider` | EXIT=0；**1051 passed**（本会话重跑两次均通过） |
| providers | 同环境 `pytest tests/providers -q` | EXIT=0；559 passed / 4 skipped |
| FEA-10 专项 | `pytest tests/fea10/test_prepared_run.py tests/fea10/test_snapshot_retry.py -q`（主套件内含） | 全部通过；`test_prepared_run.py` 实际 15 passed（卡写 11） |
| R-001 探针 | 真实 settings sections + `prepare_run` | `providers`/`network`/`reading`/`translation`/`typeset` 合法时 Prepare OK；执行段未知键仍 `RUN_SNAPSHOT_INCOMPLETE` |
| R-002 探针 | 三种 binding 形状 + OCR committed + `prepare_run/accept/plan` | `provider_id` 已规范化；`run_binding_available=True`；`status=pending` |
| R-003 探针 | primary typed + `fallback: ['fea10-legacy']`（docTR-blob） | `PipelineError RUN_SNAPSHOT_INCOMPLETE`，无 `TypeError`；合法 typed fallback Prepare OK |
| R-004 探针 | 生产注册表 `{"ocr":"manga-ocr"}` | `execution.adapter_version=local:local-manga-ocr-onnx:v1`、`model=manga-ocr-base-onnx`；Accept/plan 成功 |
| RR-01 探针 | 嵌套 `headers`/`token` 覆盖 + Accept | `headers` 进入 `settingsSnapshot` 并持久化；嵌套 `token` 出现在 `overrides` |
| RR-05 探针 | 仅改 live `provider_type` / 再改 `model` | type-only drift 仍 `available=True`；model drift `False` |
| C# 默认注入 | `dotnet test ... App.Tests --filter PreparedRunPayload_CarriesTheHostDefaultBindings --no-build` | 1 passed，EXIT=0；工作树无变更 |
| 真实 IPC | `NEWMANGA_FEA10_IPC=1 ... dotnet test ... Host.Tests --filter Fea10RunIpcTests --no-build` | 1 passed，EXIT=0；未产生 tracked 证据变更（R-008 修复生效） |
| 证据核对 | 读 `dsh-rework-dotnet.log`/`dsh-rework-pytest.log`/`python-main-r2.log`；复算 AC-MATRIX/Task 卡/manifest 哈希 | .NET 日志 1345/0/75 与 1 IPC；pytest 日志 `2 failed, 1049 passed`；RR-02 哈希错配 |

### 4.1 证据真实性小结

- **真实通过**：`check.ps1` PASS（4 warnings）、pins 17/17、主套件 1051 passed（本会话）、providers 559/4、定向 C# 1 passed、真实 IPC 1 passed。
- **仅核对日志、未独立重跑**：全量 .NET `1345 passed / 0 failed / 75 skipped`（日志逐程序集求和一致）、rework build `0 warning/0 error`（无独立 build 日志，见 RR-09）。
- **不能支撑声明的证据**：`dsh-rework-pytest.log` 是失败运行（2 failed），却被 record/卡/AC-MATRIX 当作 `1051 passed、无 failed` 的证据；本会话重跑通过，说明最终 head 可通过，但证据文件与陈述不一致（RR-03）。
- **没有发现凭空编造测试结果**：失败日志、r1 失败历史、manifest 生成时点均可核；问题集中在“中间失败/旧哈希未刷新”和“声明超前于证据”。

## 5. NOT_RUN

- 全量 `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` 与全量 `dotnet test`：**未在本会话重跑**。只跑了定向 App 测试与真实 IPC（`--no-build`），并核对 DSH `dsh-rework-dotnet.log`；重跑全量可能重写 FEA-09 tracked 证据，超出本 Review 的只读边界。
- Windows 系统级 source lease/源故障、真实外网 provider/模型质量、原生 UI 端到端点击：**未跑**（沿用 Handoff 的 NOT_RUN 边界）。
- 825 个 fixture 目录逐个内容审计：**未做**；只核对 manifest/日志/抽样与本次探针 fixture。
- `verification/FEA-10/RESOURCE-MANIFEST.json` 的逐文件哈希重算：**未做**；只确认其为 PRESERVE_REFERENCED 记录并抽查。

## 6. 处置建议

1. **先修 RR-01（P1）**：恢复认证材料递归扫描并给 `translate.glossary` 等用户内容建精确 allowlist；同时从 snapshot 真正过滤非执行段、对 `overrides` 回显做同一过滤；补 `headers`/`authorization`/`signing_key`/`bearer`/`token` 嵌套与 glossary 正向回归。
2. **再修 RR-02（P1）**：以 `ed60c1d2` 为基线重生成 manifest/changed-files/scope，更新 Canonical Evidence commit+sha256（或置 pending），修正 handoff 的 warnings 数；重新保存成功 pytest 日志并保留失败历史（RR-03）。
3. RR-04/RR-05/RR-06 作为同一轮 hardening 处理：fallback 容器/本地 typed 身份/null override 都要回到冻结错误码；RR-07/RR-08/RR-09 属证据与文档整洁，随同刷新。
4. 修复后必须在**新 head** 重跑主套件/providers/.NET 全量/真实 IPC/check/pins/scope，并派全新上下文 Review；本文件不构成对 `ed60c1d2` 的批准。

## 7. 复审边界

- 本审查只对 `ed60c1d2` 有效；若 DSH 在修复中改动生产/测试/证据，须重新派独立 Review。
- 未覆盖：真实 Windows 源租约、原生 UI 点击、真实外网模型质量、825 个 fixture 的逐目录内容、全量 .NET 重跑；这些在 Handoff 已列为 NOT_RUN，本 Review 沿用该边界。
