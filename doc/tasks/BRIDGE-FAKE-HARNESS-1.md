---
id: BRIDGE-FAKE-HARNESS-1
title: 冻结 bridge 假 sidecar 夹具并补两处调用点的 poison 动态证据（E-7 #2 / bridge 侧）
kind: governance
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - BRIDGE-ID-FAILCLOSED-1
approval: DSH 裁决 2026-11-16（承接 BRIDGE-ID-FAILCLOSED-1 的 F-01）；Codex 裁决 §4 把夹具方案冻结派给 DSH
base_commit: 6f6fdda13
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/BRIDGE-FAKE-HARNESS-1
allowed_paths:
  - doc/tasks/BRIDGE-FAKE-HARNESS-1.md
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/**
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/BRIDGE-FAKE-HARNESS-1/**
---

# BRIDGE-FAKE-HARNESS-1：bridge 假夹具 + 调用点 poison 动态证据

## 为什么单独立卡

`BRIDGE-ID-FAILCLOSED-1` 实施了 Codex 裁决的 §3.1（parser 严格化）与 §3.2（生产调用点 poison），
但 r1 复核（`APPROVED_WITH_LIMITATIONS`，0/1/3/3）以**变异测试**确认：

> 删掉 `SendAsync` 里的 `_process.Poison();` 后，全量仍 **222 passed / EXIT 0**（**存活**）。

即 **poison 接线没有任何测试覆盖** —— 11 条测试都直接调静态 `ParseResponse`，不经过 `SendAsync` 的 catch。
而裁决 §3.2 原话是「**不能只改 parser 就宣布会话安全**」。

## DSH 裁决（2026-11-16）：F-01 另立卡承接

复核给出两条路：(a) 本卡关闭前补动态测试；(b) DSH 明确裁决另立卡并在卡面登记。

**选 (b)**，理由：

1. 障碍是真实且结构性的 —— 裁决 §4 自己指出：
   > Bridge fake 不能直接假定 core fake 的 Python 启动参数可复用：当前 `HostBridgeOptions` 只暴露
   > `ExecutablePath`，没有 `Arguments`。DSH 应冻结能通过现有启动方式运行的测试夹具方案，
   > **不为测试扩大生产公共 API**。
2. core 侧的同类缺口（host-control 的 poison 分支）**也**卡在夹具上 —— 两边共用同一个瓶颈，
   合并到一张卡处理比各自硬塞更合理；
3. 本卡的核心成果（parser 严格化 + 测试迁移）**已独立验证有判别力** —— 复核实测：
   收紧 raw ⇒ RED；`kind` 判断顺序反 ⇒ 5 红。

**但**：本卡**不得**宣称「bridge 侧会话安全」，`E-7 #2` **继续开放**。见本卡未关闭项。

## 范围

### 1. 冻结 bridge 假 sidecar 夹具（这是本卡的主要难点）

约束（裁决 §4）：**不得为测试扩大生产公共 API**。可选方向：

| 方案 | 优点 | 代价 |
|---|---|---|
| A. `.cmd`/`.bat` 包装脚本，`ExecutablePath` 指向它，内部转调 `python -u fake.py <scenario>` | 不改生产 API；沿用 core 侧内联 python 模式 | 平台相关（Windows only） |
| B. 小型 .NET 控制台假 bridge（测试项目内或独立 csproj） | 跨平台；无 python 依赖 | 需新增 csproj / 构建产物管理 |
| C. 测试内 `Process.Start` 直接起 python 并用 `ExecutablePath` 指向 python，把脚本路径塞进 `AdditionalArguments` | **不可行** —— `HostBridgeOptions` 没有 `Arguments` | — |

**A 或 B 二选一**，需在实施时记录选择理由。

### 2. 补两处调用点的 poison 动态证据

- **bridge**：`SendAsync` 收到无/非法/错 id 帧 ⇒ 立即 `MalformedResponse`；**即使后面紧跟正确 id 帧也不重同步成功**；
  下一调用在**写请求之前**因 poisoned/restart required 失败。检查假服务端收到的请求数（不能只匹配消息里 "poisoned" 一词）。
- **core**：`SendHostControlAsync` 的「无 id 耗尽 ⇒ poison」分支（`E7-2-DYNAMIC-EVIDENCE-1` 因全量 flaky 撤回的那条）。

### 3. 变异验证（本卡的验收方式）

两处接线分别改 no-op ⇒ **必须有测试变红**。这是本卡的核心判据：
**不接受"测试通过但没有判别力"**。

## 目标（一个可观察结果）

两处 `Poison` 接线各自被一条经**生产调用链**的测试覆盖；把任一接线改 no-op 会产生**至少一条红测试**。

## Acceptance Criteria

- [ ] **AC1 夹具冻结**：选定方案（A 或 B）并记录理由；能通过 `HostBridgeClient.StartAsync` 的握手。
- [ ] **AC2 bridge poison 动态证据**：真实 `StartAsync` → `SendAsync` 链上，坏帧 ⇒ 首调 `MalformedResponse`、
      次调 `RequestTimeout`（poisoned 快路径），且**请求计数**证明次调未写入。
- [ ] **AC3 core host-control poison 动态证据**：`SendHostControlAsync` + `idless-only` ⇒ 首调 `MalformedResponse`、次调 `RequestTimeout`。
- [ ] **AC4 变异判别力**：两处接线各自改 no-op ⇒ 至少一条测试变红（**必须 `--no-incremental` 强制重建**）。
- [ ] **AC5 不回归**：全量 0 failed；四件套 PASS。
- [ ] **AC6 独立复核**：固定 head 交独立上下文 Review。

## 禁止范围

- **不得为测试扩大生产公共 API**（裁决 §4）；
- 不得修改 `ParseResponse` 的判据（那是 `BRIDGE-ID-FAILCLOSED-1` 的范围）；
- 不得用「只匹配消息里含 poisoned」的弱断言（裁决 §4 明确禁止）；
- **变异验证必须 `dotnet build --no-incremental` 强制重建** —— r1 复核发现：从备份恢复源文件会保留旧
  时间戳，增量构建可能跳过重编译，导致测试跑的是上一次变异的 DLL（它首测因此误判过一次）。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| bridge 动态 | 新增测试 | 首调 MalformedResponse / 次调 RequestTimeout |
| core host-control 动态 | 新增测试 | 同上 |
| 变异 | 两处接线各改 no-op + `--no-incremental` | 至少一条红 |
| 全量 | `dotnet test …NewManga.CoreClient.Tests.csproj` | 0 failed |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |
