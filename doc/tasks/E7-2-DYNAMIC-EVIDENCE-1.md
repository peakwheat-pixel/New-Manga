---
id: E7-2-DYNAMIC-EVIDENCE-1
title: 假 core_service 夹具 —— 在生产调用链上动态验证 E-7 #2 与 R-002（一个夹具解两个结）
kind: governance
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - E7-2-FAILCLOSED-1
  - R002-RESYNC-1
approval: 用户 2026-11-15「全部授权」；Codex 裁决 2026-11-16 §5.3 要求「真实调用链的动态证据」
base_commit: bed4023ab
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/E7-2-DYNAMIC-EVIDENCE-1
allowed_paths:
  - doc/tasks/E7-2-DYNAMIC-EVIDENCE-1.md
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/FakeCoreServiceIntegrationTests.cs
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/E7-2-DYNAMIC-EVIDENCE-1/**
---

# E7-2-DYNAMIC-EVIDENCE-1：假 core_service 夹具

## 为什么要做

两个纠缠多轮的缺口，根子是同一个：**没有能在真实生产调用链上跑的假 sidecar**。

| 缺口 | 出处 |
|---|---|
| 裁决 §5.3 要求「在真正的 `SendAsync` / `SendHostControlAsync` 路径上有确定性假 sidecar 测试」 | `E7-2-FAILCLOSED-1` 未关闭项 1 |
| 「4 条测试只直接调 `internal static` helper，没有任何测试证明两个调用点真的在用它」 | `R002-RESYNC-1` r1 的 P2-F1 |

**一个夹具解两个结。**

## 方案

内联 Python 假 `core_service`（测试运行时写入临时文件，**不改 `.csproj`、不提交二进制夹具**）：

```python
if cmd == "core.ping":        # 握手：status=ready + protocol_version.major=2
    emit({... "status": "ready", "protocol_version": {"major": 2, "minor": 3}, ...})
elif scenario == "mismatch-then-match":   # 先错 id 帧，再正确帧
elif scenario == "missing-then-match":    # 先无 id 帧，再正确帧
elif scenario == "idless-only":           # 只有无 id 帧（应 poison）
```

场景通过**命令行参数**传递（`CoreServiceOptions` 没有 `Environment` 字段，无法走环境变量）。

`PythonPath()` 用 `where.exe python` 解析**绝对路径** —— `SidecarProcess` 用 `File.Exists` 校验，
传 `"python"` 会被判 `SidecarExeMissing`（这是本轮第一次跑时的实际失败）。

## 三条测试

| 测试 | 验证 |
|---|---|
| `ProductionSendAsync_ResynchronisesWhenFirstFrameBelongsToAnotherRequest` | **R-002 在生产链上生效**：错 id 帧被丢弃，调用方拿到真正属于自己的 `{"ok":true}`（不是错帧的 `{"stolen":true}`） |
| `ProductionSendAsync_DiscardsIdlessFrame_ThenSucceedsOnTheMatchingOne` | **E-7 #2 fail-closed 生效**：无 id 帧被丢弃，随后匹配帧成功 |
| `ProductionSendAsync_PoisonsChannel_WhenOnlyIdlessFramesArrive` | **E-7 #2 的失败路径**：只有无 id 帧 ⇒ `MalformedResponse` + 下一次调用立即 `poisoned` |

三条都经过 `CoreServiceClient.StartAsync`（含 `core.ping` 握手）→ 因此**证明的是生产调用点**，
不是 helper 单独的行为。

## 目标（一个可观察结果）

三条测试通过；全量 **213 passed / 0 failed / 30 skipped** 不退化。

## Acceptance Criteria

- [ ] **AC1 完成握手**：假 sidecar 能让 `CoreServiceClient.StartAsync` 通过（`core.ping` ready + 协议主版本匹配）。
- [ ] **AC2 R-002 动态证据**：错 id 帧在生产链上被丢弃、调用方拿到匹配帧。
- [ ] **AC3 E-7 #2 动态证据（成功路径）**：无 id 帧被丢弃、随后匹配帧成功。
- [ ] **AC4 E-7 #2 动态证据（失败路径）**：只有无 id 帧 ⇒ `MalformedResponse` + 后续调用 poison。
- [ ] **AC5 不改 csproj / 不留二进制夹具**：Python 脚本内联在测试里、运行时写临时文件。
- [ ] **AC6 不回归**：全量 **213 / 0 / 30**；四件套 PASS。

## 允许修改范围

见 frontmatter `allowed_paths`：只新增一个测试文件。

## 禁止范围

- 不得修改既有测试来「配合」新夹具；
- 不得为通过而在产品代码里加测试专用开关；
- 不得提交任何二进制夹具或 `.csproj` 改动。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 假夹具 | `--filter FullyQualifiedName~FakeCoreServiceIntegrationTests` | 3 passed |
| 全量 | `dotnet test …NewManga.CoreClient.Tests.csproj` | 213 / 0 / 30 |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## 证据

测试日志与全量日志写入 `verification/E7-2-DYNAMIC-EVIDENCE-1/`。
