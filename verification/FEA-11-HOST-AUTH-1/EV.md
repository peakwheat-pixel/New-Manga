# FEA-11-HOST-AUTH-1 EV（证据索引）

生成：2026-11-05（DSH closeout；`closed_with_limitations`；终态裁决人 = Codex，用户 2026-11-05 委托）。
`canonical_evidence_status: complete`；`resource_closeout_status: complete`。

- 任务卡：`doc/tasks/FEA-11-HOST-AUTH-1.md`
- delivery head：`cbd561b432f73bce3308d68366f79f408cee000a`（r8 reviewed head）
- base：`7ab9eea87062a44d5b08edbd507538f21443e000`
- 终态裁决：`doc/reviews/FEA-11-HOST-AUTH-1-codex-adjudication-2026-11-05.md`（DECISION: A）
- 最终复审：`doc/reviews/FEA-11-HOST-AUTH-1-r8.md`（approved，P0/P1/P2=0，P3=5；AC3 PARTIAL；10 项 limitation）
- 变更文件清单：`verification/FEA-11-HOST-AUTH-1/changed-files.txt`
- 门禁：`verification/FEA-11-HOST-AUTH-1/logs/gates.log`（含 closure 记录）

## AC → 证据

| ID | AC | 证据 | 状态 |
|---|---|---|---|
| EV-AC1 | AC1 canonical-json/1 + sha256（跨实现向量，含 non-BMP） | `CanonicalJson.cs` + `CanonicalJsonTests.cs`（5/5）；r8 §AC 判定 | MET |
| EV-AC2 | AC2 HostAuthorization 六字段 + operation_id 注入 | `HostAuthorizationMinter.cs` + `HostAuthorizationMinterTests.cs`（6/6）；`Fea11HostAuthTests`（注入断言） | MET |
| EV-AC3 | AC3 Registry durable→journal 顺序 + typed 失败 + retry + capability 门 | `HostOperationOrchestrator.cs` + `Fea11HostAuthTests.cs`（24/24，19 方法）；ACK 重发/崩溃点矩阵/真实 e2e 未自动化 | PARTIAL（保留，见 limitation 1–10） |
| EV-AC4 | AC4 FEA-11 r3 复审接受本卡为 P0-1 闭合路径（或产品方接受 Core-only limitation） | `doc/reviews/FEA-11-r3.md:38`（r8 口径：MET 路径层） | MET（路径层） |
| EV-R8 | 最终独立复审 | `doc/reviews/FEA-11-HOST-AUTH-1-r8.md` | approved |
| EV-CODEX-ADJ | 终态裁决（用户委托 Codex） | `doc/reviews/FEA-11-HOST-AUTH-1-codex-adjudication-2026-11-05.md` | DECISION A |
| EV-GATES | 门禁日志（r1–r8 + closure） | `verification/FEA-11-HOST-AUTH-1/logs/gates.log` | 见日志 |
| EV-FILES | 交付变更文件清单 | `verification/FEA-11-HOST-AUTH-1/changed-files.txt` | 23 files |

## 门禁口径（重要，不可合并为无波动 PASS）

- 全量 .NET **1395 passed / 0 failed / 78 skipped**：来源 = r8 Reviewer 独立运行（reviewed head `cbd561b4`）。本类 closeout 未重跑全量 .NET；C#/apps 自 `cbd561b4` 到 closeout head 零 diff（`closure gate` 记录 `apps diff lines: 0`）。
- Host.Tests：r6 时代记录为 `105/0/49`；r8 head 记录为 `107/0/49`（`Fea11HostAuthTests 24/24（19 方法）`）。两个数字属不同 head，保留原始出处。
- IPC：r8 Reviewer 首次 `2/3`（`ScanWithAHostIssuedGrant_WorksEndToEnd` flake，未捕获详情）→ 单独 `1/1` → 随后 `5×3/3`；Core 直连套件，**非 HostRuntime e2e**。该 flake 与本卡 limitation 1/2 相关，保留原始记录。
- pytest：r8 时点 fea11 40 passed / 全量 3051 passed·10 skipped；closeout head（含 FEA-11-LINEAGE-1 r2 在途改动）fea11 62 passed；全量 pytest 由 LINEAGE-1 r2 证据 `verification/FEA-11-LINEAGE-1/logs/gates-r2.log` 记录（3073/10），不冒充本卡独立证据。
- 治理：closeout head `check.ps1` PASS（2 warnings：非终态计数、PLAN 80% 预算）；`verify_pins.ps1` 18/18 PASS。

## Limitation（10 项，原文见 r8；closeout 不改写）

1. HostRuntime→Core 真实 sidecar + dispatcher 接线 e2e 未自动化（IPC 为 Core 直连）。
2. ACK 重发/崩溃点矩阵（C-17 §3.3）未自动化。
3. retry 仅为 Host 编排 API（dispatcher 无冻结 retry 命令，UI/命令面不可达）。
4. Host 侧 plan 有效性预检未实现（依赖 Core `take_confirmed` 事务内 fail-closed）。
5. ACK/recovery 前 receipt 核对与 CommitReceipt canonical 重算未实现。
6. Host 输入规则精度未收口。
7. Registry scope/多 registry 原子性/Begin 与 Authorize 顺序崩溃窗口。
8. 分类精度：黑名单含未产出码、typed 歧义分支用例。
9. `source.read/1` 缺失时 capability item reason 语义。
10. R7-P2-01 用例 2 判别力残留 / R8-P3 文档指针 / 证据残留。

**附注（Codex 裁决要求补充，不改写上述 10 项）**：ACK/recovery 当前从 journal 读取原 authorization（`SourceOperationCoordinator.cs` ACK/recovery 路径），而 C-17 要求 ACK/recovery 使用 fresh grant/authorization；Core 侧仍有摘要/基线/identity/live grants 校验，未见 P0/P1 绕过。该行为缺口映射到 limitation 1/2/5（Host 流程完整性）与 10（文档/证据），属已接受 limitation；若后续要真正闭合，需新授权卡。
