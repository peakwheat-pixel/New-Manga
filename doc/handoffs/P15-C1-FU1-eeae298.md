---
task_id: P15-C1-FU1
author: Codex
recipient: DeepSeek Harness
base_commit: 82ce23bd50e4c53c3e546a392f4e984e7102a097
delivery_head: eeae29831b4f20b7ddf0e93897d3b99e806b8ccf
status: in_review
---

# Handoff：P15-C1-FU1-eeae298

## 交付结果

交付状态为 `in_review`，尚待非作者独立 Review；本 Handoff 不表示已被接受或批准。

| AC | 结果 | 对照 |
|---|---|---|
| AC1 | 已写入 | `TestNetworkProfile` 的 `provider_profile_id` 必需；缺省/非法时 `INVALID_REQUEST`；目标恒为 Provider Profile 的 endpoint，经请求指定 Network Profile 路由。 |
| AC2 | 已写入 | §5.2 明确禁止自选公网 URL、loopback、假目标、把 Proxy 主机冒充 Provider TLS/HTTP 目标及伪造阶段结果。 |
| AC3 | 已写入 | §5.2 给出 Direct/System/HTTP/HTTPS/SOCKS5 × Proxy/DNS/TCP/TLS/HTTP/ProviderAuth 矩阵、目标来源、判定和 `NotRunReason` 规则。 |
| AC4 | 已写入 | §5.2 沿用既有敏感字段排除与 §9 封闭失败投影；未放宽 Secret、路径、引用边界。 |
| AC5 | 已写入 | §2 声明 rev 2.6→2.7 和请求形状兼容影响；不改 G21/G22/G24 或 P10 冻结语义。 |
| AC6 | 已写入 | 本 Handoff、Canonical Evidence 与决策映射均在仓库；测试表全部 `NOT_RUN`。 |

实际修改：

- `doc/contracts/P15_SETTINGS_IPC_CONTRACT.md`：§2、§5.2、§10、§11。
- `verification/P15-C1-FU1/decision-map.md`：逐项裁决→条文→来源映射及 `NOT_RUN` 测试表。
- `doc/tasks/P15-C1-FU1.md`：交接元数据与 Canonical Evidence 在后续文档提交回填。

交付提交 `eeae29831b4f20b7ddf0e93897d3b99e806b8ccf`（基于 `82ce23bd50e4c53c3e546a392f4e984e7102a097`）。提交范围为契约与决策映射；后续只提交 Handoff/Task 交接元数据。没有修改 `src/**`、`apps/**`、Schema、依赖、`STATUS` 或 `REBASELINE_PLAN`。

## 验证证据

设计类测试按 Task 要求全部 `NOT_RUN`，没有用静态阅读冒充产品测试。具体原因与裁决来源映射见 `verification/P15-C1-FU1/decision-map.md`。

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1–AC5 设计类验证 | 按 Task 对照契约语义 | 设计文档；`eeae29831b4f20b7ddf0e93897d3b99e806b8ccf` | `NOT_RUN` | `verification/P15-C1-FU1/decision-map.md`（说明原因） |
| AC5 协议/runtime 兼容测试 | 无；本交付未实现 handler | 无 runtime；`eeae29831b4f20b7ddf0e93897d3b99e806b8ccf` | `NOT_RUN` | `verification/P15-C1-FU1/decision-map.md`（说明原因） |
| AC6 磁盘字节 SHA-256 证据采集 | `Get-FileHash -Algorithm SHA256`（提交后读取） | PowerShell / linked worktree；source commit `eeae29831b4f20b7ddf0e93897d3b99e806b8ccf` | 已记录；这不是产品测试 | `doc/tasks/P15-C1-FU1.md` Canonical Evidence 表 |

## 接收方式

- 仓库：`G:/CODEX/New Manga`。
- Owner 分支/worktree：`codex/P15-C1-FU1` / `G:/CODEX/New Manga.workspace/worktrees/P15-C1-FU1`。
- 基线：`82ce23bd50e4c53c3e546a392f4e984e7102a097`；契约交付 head：`eeae29831b4f20b7ddf0e93897d3b99e806b8ccf`。
- 复现方式：只读查看上述固定提交的文档差异；无需启动应用、Core 或测试服务。
- 没有运行时依赖、Schema 或依赖清单变更。
- 未自行发起独立 Review。建议由 DeepSeek Harness 以非作者身份按下方指令执行；Reviewer worktree 尚未创建，待 Codex 创建。

## 下一任务建议（必填）

- **Task ID / 标题**：`P15-C1-FU1` 独立 Review（当前 Task 的审查 Gate，不是新产品 Task）。
- **推荐 Agent / Reviewer**：DeepSeek Harness；Owner 为 Codex，满足非作者 Review。
- **推荐原因与前置依赖**：本 Task 已交付 `in_review`；P15-CORE-1C 六阶段实现仍须等待本 Task 关闭。审查 AC1–AC6、阶段矩阵、A1 边界、兼容说明与证据 pin 后，再由 Codex 集成验证/决定关闭。
- **Recovery point**：仓库 `G:/CODEX/New Manga`；Owner branch/worktree `codex/P15-C1-FU1` / `G:/CODEX/New Manga.workspace/worktrees/P15-C1-FU1`；固定 base=`82ce23bd50e4c53c3e546a392f4e984e7102a097`、delivery head=`eeae29831b4f20b7ddf0e93897d3b99e806b8ccf`。Reviewer 独立 worktree 未创建，待 Codex 创建；Review 必须先固定实际 reviewed head。
- **允许修改路径**：Reviewer 只读代码/契约；Review 报告写入 `verification/P15-C1-FU1/**`。
- **禁止范围与新增授权条件**：不得改 `src/**`、`apps/**`、Schema、依赖、G21/G22/G24、P10、`STATUS` 或 `REBASELINE_PLAN`；发现契约缺口时只写 Review finding，修订须退回 Task Owner。
- **交付物**：固定 base/reviewed head 的独立 Review 报告；按 AC 和安全/兼容边界逐项记结果；修订需要新 delivery head 和新 Handoff。
- **验证命令、环境与完成 Gate**：无产品测试命令（设计任务测试表继续 `NOT_RUN`）；Review 在隔离 linked worktree 静态核对 AC1–AC6、来源映射、Canonical Evidence 磁盘字节 hash 和范围；报告记录未覆盖项。无未解决 P0/P1 且证据/范围成立后交 Codex 集成验证；在 Review、验证与集成完成前 Task 不得标 `done`。
- **可直接转发给 Agent 的指令**：

  > 请以非作者 Reviewer 身份审查 `P15-C1-FU1`。仓库为 `G:/CODEX/New Manga`；Owner 工作区为 `G:/CODEX/New Manga.workspace/worktrees/P15-C1-FU1`、branch `codex/P15-C1-FU1`，base=`82ce23bd50e4c53c3e546a392f4e984e7102a097`，契约 delivery head=`eeae29831b4f20b7ddf0e93897d3b99e806b8ccf`。先由 Codex 建立隔离 Reviewer worktree，并在 Review 开始前固定实际 reviewed head。只读核对 `doc/contracts/P15_SETTINGS_IPC_CONTRACT.md` §2/§5.2/§10/§11、`doc/tasks/P15-C1-FU1.md`、`doc/handoffs/P15-C1-FU1-eeae298.md` 与 `verification/P15-C1-FU1/decision-map.md`；报告写入 `verification/P15-C1-FU1/**`。逐项审查 A1 必填参数/唯一目标、三项禁止规则、五模式六阶段目标与状态、§9 脱敏、rev 2.6→2.7 兼容影响、Canonical Evidence disk-byte pins 和修改范围。不得实现产品代码，不得把 `NOT_RUN` 提升为 PASS；保留全部产品/协议/安全测试 `NOT_RUN`。报告须含 findings、验证边界与固定 base/head。无 review 报告前不得视为接受或批准。

## 风险与遗留

- rev 2.6→2.7 是未实现 command 的预发布契约修订；rev 2.6 草案缺少 `provider_profile_id` 的调用形状会被 rev 2.7 拒绝。§2 已明确该兼容影响，没有声称通用 minor 必填性变化向后兼容。
- 产品、协议、网络与安全测试均 `NOT_RUN`，符合设计类 Task 口径；后续实现/Review 不得据此声称 runtime 通过。
- P15-CORE-1C 仍需等待 P15-C1-FU1 经独立 Review 与 Codex 集成关闭。
- 本 Task 未删除、移动或覆盖其他 worktree/用户 dirty。
