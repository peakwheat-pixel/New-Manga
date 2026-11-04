# FEA-10-PREREQ-1 Appointment（DSH，2026-11-04）

状态：**RELEASE APPROVED — scope frozen；Task `ready`；实施待 Codex 额度恢复后认领；不 push**
Task：`doc/tasks/FEA-10-PREREQ-1.md`（proposed → ready）
依据：Codex 2026-11-04 下一 Task 裁决（FEA-10 首选）+ DSH 补定 C-08 块②硬前置（`doc/reviews/ADJ-2026-11-04-NEXT-TASK.md`）；C-08 冻结记录 §3；scope review r5 **approved**（`doc/reviews/FEA-10-scope-r5.md`，P0/P1=0，残留 P2 非阻断）。

## 1. 范围（冻结）

- 仅 C-08 块②协议注册：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev 2.12 增量（PrepareRun/AcceptRun、3 码、§8 未观察、retryable/taxonomy 例外、wire 2.12 登记）；host `allowedRunErrorCodes` 白名单/unknown 降级与负向对照；客户端 registry/错误投影映射与测试。
- **不实现** PrepareRun/AcceptRun 运行逻辑、候选存储、提交 seam（归 FEA-10）；不改冻结契约字节；不 push；不碰删除线/C-04b 语义。

## 2. 文件级写域

见 Task frontmatter `allowed_paths`（M2-C1 文档、`Wire/CoreProtocol.cs`、`HostCommandDispatcher/Registry`、`HostRuntime.cs`、`HostRuntimeIntegrationTests.cs`、`WireTests.cs`、新 `Fea10PrereqProjectionTests.cs`、本 Task/Review/Handoff/evidence）。

## 3. 角色

| 角色 | Agent | 说明 |
|---|---|---|
| Owner（实现） | **Codex**（新实现会话；额度 13:31 恢复后认领） | 只写 allowed_paths；不得自审 |
| Reviewer（实现 Review） | DSH 派发的**全新上下文**（Codex/ZCode；未参与实现/返修） | 只读 reviewed_head；报告归档 |
| Integrator / 裁决 | DSH | 提交、门禁、集成、closeout |

## 4. AC 与门禁

- AC1 M2-C1 rev 2.12 字节增量 + wire 2.12 登记（文档 rev 与 Core `PROTOCOL_MINOR` 分离）；AC2 host 白名单（未注册→unknown、保留 code、不作 UI 分支依据）；AC3 负向对照；AC4 既有 Run 回归/check/pins 17/17/C-05/C-15/C-16 字节未改；AC5 证据+独立 Review+Handoff+EV/Resource Manifest。
- 门禁：`dotnet build apps/desktop-avalonia/NewManga.sln -c Release`；CoreClient/Host 定向测试（`CoreProtocolTests|AsciiWireTests`、`Fea10PrereqProjectionTests`）；`dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build`；`check.ps1`；`verify_pins.ps1`；范围 diff。证据 `verification/FEA-10-PREREQ-1/logs/`（含 EXIT）。
- 完成定义：实现 + 测试 + 证据 + Handoff → `in_review` → 独立实现 Review → DSH 集成 → `done`；FEA-10 以本 Task done 为硬前置。

## 5. 当前阻塞

- Codex 额度上限（13:31 后恢复）、ZCode HTTP 429：r6 scope review 未完成；本卡实施也待 Codex 恢复后认领。恢复后先完成 FEA-10 scope r6（fresh context），再派本卡实现。
