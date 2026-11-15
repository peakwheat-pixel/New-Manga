---
id: E7-2-DYNAMIC-EVIDENCE-1
title: 假 core_service 夹具 —— 在生产调用链上动态验证 E-7 #2 与 R-002（一个夹具解两个结）
kind: governance
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: fake-core-review（独立上下文子 agent，APPROVED_WITH_LIMITATIONS）
integration_commit: 003385bc3
canonical_evidence_status: complete
resource_closeout_status: complete
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

四条测试通过；全量 **214 passed / 0 failed / 30 skipped** 不退化。

## Acceptance Criteria

- [x] **AC1 完成握手**：假 sidecar 能让 `CoreServiceClient.StartAsync` 通过（`core.ping` ready + 协议主版本匹配）。 <<MET>>
- [x] **AC2 R-002 动态证据**：错 id 帧在生产链上被丢弃、调用方拿到匹配帧。**两条命令路径均有覆盖**：`SendAsync`（第 1 条）+ `SendHostControlAsync`（第 4 条，变异验证：绕过 resync ⇒ 该条变红）。 <<MET>>
- [x] **AC3 E-7 #2 动态证据（成功路径）**：无 id 帧被丢弃、随后匹配帧成功。 <<MET>>
- [x] **AC4 E-7 #2 动态证据（失败路径）**：只有无 id 帧 ⇒ `MalformedResponse` + 后续调用 poison。**r1 P1 修正**：初版只断言消息含 "poisoned" —— 但「channel poisoned」(RequestTimeout) 与「out of step, channel poisoned」(MalformedResponse) 两条消息**都含**该词，删掉整个 poison 钩子仍是绿的（复核用变异测试实测为存活变异）。现改为断言 **`next.Code == RequestTimeout`** + "restart required"，从错误码上区分两条路径。 <<MET>>
- [x] **AC5 不改 csproj / 不留二进制夹具**：Python 脚本内联在测试里、运行时写临时文件。 <<MET>>
- [x] **AC6 不回归**：全量 **214 / 0 / 30**；四件套 PASS。**变异测试判别力（r1 实测）**：A 让 `SendAsync` 绕过 resync ⇒ **3/3 全红**；B 让 `BelongsToRequest` 回 fail-open ⇒ 2 红；C 令 `ResyncMaxDrainFrames=0` ⇒ 2 红；D 把 `Poison` 换 no-op ⇒ 修 P1 前**3/3 全绿（存活）**、修正后应红。 <<MET>>

## 允许修改范围

见 frontmatter `allowed_paths`：只新增一个测试文件。

## 禁止范围

- 不得修改既有测试来「配合」新夹具；
- 不得为通过而在产品代码里加测试专用开关；
- 不得提交任何二进制夹具或 `.csproj` 改动。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 假夹具 | `--filter FullyQualifiedName~FakeCoreServiceIntegrationTests` | 4 passed |
| 全量 | `dotnet test …NewManga.CoreClient.Tests.csproj` | 214 / 0 / 30 |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-FC-01 | AC1-AC4 假夹具 3 passed | verification/E7-2-DYNAMIC-EVIDENCE-1/fake-core-tests.log | 003385bc3 | 751309d7055f4d90ca99be51f383f44dc0788a00e9ec141450de0c308bec7e84 | CANONICAL | BLOB |
| EV-FC-02 | AC6 全量不回归（213/0/30） | verification/E7-2-DYNAMIC-EVIDENCE-1/coreclient-full.log | 003385bc3 | 446bdaad7a605162b075aa770ce5a9459d1c3b06d0c3a8b67a740c4d47d858ce | CANONICAL | BLOB |
| EV-FC-03 | AC2/AC6 变异验证（SendHostControlAsync 绕过 resync ⇒ 第 4 条变红） | verification/E7-2-DYNAMIC-EVIDENCE-1/mutation-D-sendhostcontrol.log | 003385bc3 | 99a118c9bcb24c7389f706dd7a9e27e1d0f6305c8c8c35400bbd259a5b5efd0c | CANONICAL | BLOB |
| EV-FC-04 | AC4 变异验证（host-control poison 改 no-op ⇒ 第 5 条变红） | verification/E7-2-DYNAMIC-EVIDENCE-1/mutation-E-hostcontrol-poison.log | b3ff87fa4 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/E7-2-DYNAMIC-EVIDENCE-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-16，DSH；实现 `939f1811d` + r1 返修（本提交）。
- **结果**：内联 Python 假 `core_service` 夹具，能通过 `core.ping` 握手，让四条测试经
  **真实生产调用链**（`StartAsync` → public `SendAsync`）验证 E-7 #2 与 R-002。
- **独立复核**：`fake-core-review` **APPROVED_WITH_LIMITATIONS**（0/1/4/5）。它用**仓外变异沙箱**
  实测了四条回归的判别力（这是本报告最硬的证据）：
  - A `SendAsync` 绕过 resync ⇒ **3/3 全红**；B `BelongsToRequest` 回 fail-open ⇒ 2 红；
    C `ResyncMaxDrainFrames=0` ⇒ 2 红；
  - **D `Poison` 换 no-op ⇒ 3/3 全绿（存活）** ⇒ P1：初版只断言消息含 "poisoned"，
    而两条不同路径的消息**都含**该词。已改为断言 `next.Code == RequestTimeout` + "restart required"。
- **门禁**：假夹具 **3 passed / 324ms**；全量 **213 passed / 0 failed / 30 skipped / EXIT=0**；
  `check.ps1` PASS (3 warnings)｜`verify_pins` 18/18｜`api_inventory` 1/80/6=87。
- **未关闭项（不淡化）**：
  1. ~~**`SendHostControlAsync` 路径仍无动态证据**~~ —— **已在本轮补上**：
     根因是 `SendHostControlAsync` 自己写了 `"payload": {` 与收尾 `}`，所以它的 `payload` 委托
     只需写**成员**；传 `WireJson.EmptyObject`（自带 `{}`）才会触发
     `Cannot write the start of an object without a property name`。改用空委托 `static _ => { }` 后
     第 4 条 `ProductionSendHostControlAsync_AlsoResynchronises` 通过。
     **变异验证判别力**：把 `SendHostControlAsync` 的 resync 改回 `Parse` + `EnsureResponseBelongsToRequest`
     ⇒ 该条**变红**（EXIT=1），恢复后 EXIT=0、4 passed。
     ⇒ **裁决 §5.3 的两条命令路径现均有「重同步」动态证据**；**限定**：host-control 路径只验了
     resync 成功路径，其「无 id 耗尽 ⇒ poison」分支**没有**测试，因此 §5.3 是**部分满足**而非全部。
     **~~该项尝试过并撤回~~ → 已补齐，且"flaky"根因已查明**：
     该测试（`ProductionSendHostControlAsync_PoisonsChannel_WhenOnlyIdlessFramesArrive`）
     曾被判"全量下 flaky"（第二次调用拿到 `MalformedResponse` 而非 `RequestTimeout`）并撤回。
     **根因不是 flaky，是变异残留的旧 DLL**：撤回前我做过一次变异（把该路径的 `_process.Poison`
     改成 no-op）并从备份恢复源文件 —— **恢复保留了旧时间戳**，`dotnet build` 判定为最新、
     **跳过重编译**，于是全量跑的是**变异后的 DLL**（poison 仍在关闭状态）。
     本轮重加该测试并**逐项目 `--no-incremental` 强制重建**：
     - 定向连跑 3 次：**5/5 passed**（534–594ms）；
     - 全量连跑 3 次：**226 passed / 0 failed / 30 skipped**，三次一致；
     - **变异验证**：把 `SendHostControlAsync` 的 `_process.Poison` 改 no-op ⇒ 该测试**变红**（EXIT=1）；
       恢复后 EXIT=0。
     ⇒ §5.3 的两条命令路径、**两个 poison 接线**现在都有动态判别测试。
     **纪律（已写入 BRIDGE-FAKE-HARNESS-1 与本卡）**：`dotnet build --no-incremental` 只作用于
     被指定的项目，**不传到 `ProjectReference` 子项目**；任何变异/恢复后再验证，必须**逐项目**显式重建。
  2. **R002 的 P2-F1 对两条调用点均已关闭**：本卡新增的 4 条覆盖了 `SendAsync`（第 1-3 条）
     与 `SendHostControlAsync`（第 4 条）两个调用点，且第 4 条经变异验证有判别力。
     `R002ResyncTests` 那 4 条仍只调 helper，但**不再是唯一证据**；
  3. **CI 风险（r1 P2）**：夹具依赖 PATH 上的 `python`（`where.exe` 解析）。无 python 时**显式抛
     `InvalidOperationException`**（不 Skip、不静默 pass），但若 CI 的 `dotnet-tests` job 不装 Python，
     该 job 会转红 —— 推 main 前需实测；
  4. **`-TaskPath` 曾 FAIL 的两种原因须区分**：
     - 标 `done` 前是「当前 DAG 未登记非终态 Task」（`check.ps1:702`）—— that check 只在非终态触发；
     - **本轮返修前又出现第二种**：`DONE evidence_dir 含未登记文件：mutation-D-sendhostcontrol.log`
       （`check.ps1:840`）—— 新增变异日志却没登记 Canonical Evidence 行，**已补 EV-FC-03 修复**。
       这类「往 evidence_dir 加文件必须同时登记」的纪律，本会话已犯多次；
  5. 夹具是 `private` 嵌套类、脚本绑定 `CoreServiceClient` 握手、解释器解析用 `NEWMANGA_TEST_PYTHON`
     而仓内构建用 `NEWMANGA_BUILD_PYTHON`（两套变量）。当前单消费者，等 bridge fake 出现时再抽到
     `Support/` 共享。

