# CRASHPOINT-FAIL-NATURE-1：`CrashPoint_Park/Recover` 在全量运行中 fail 是**设计使然**，不是缺陷

基线 `95dde85d8`。本卡**只做性质澄清**，**不改代码、不改测试、不加 skip**。

## 1. 为什么把 fail 改成 skip 是**错的**

纪律明确写着：**"不得新增 skip/xfail"**。

把 2 个 fail 转成 skip 属于**新增 skip**，即便理由是"它们需要外部驱动"。
**而且**转成 skip 会**降低**可见性：现在每次跑全量都会看到"2 failed"，提醒读者去确认驱动是否仍 PASS；
改成 skip 后就变成"看不见"，这**降低**而不是提高保障。

**⇒ 不做。** 保持 fail 可见，并把性质写清。

## 2. 这 2 个测试的真实性质

```csharp
[Fea11IpcFact]
public async Task CrashPoint_Park()
{
    var state = Environment.GetEnvironmentVariable("NEWMANGA_FEA11_CRASH_STATE");
    Assert.False(string.IsNullOrWhiteSpace(state), "NEWMANGA_FEA11_CRASH_STATE is required");
    ...
```

- 它们**不是普通测试**，而是**两阶段驱动的一半**：`CrashPoint_Park` **永不自行结束**
  （文件注释原文："This test never self-terminates on purpose: only the kill ends it"），
  它 block 等**外部驱动器 kill 整棵进程树**；`CrashPoint_Recover` 再由**新进程**读状态文件恢复。
- **必须由** `verification/FEA-11-HOST-AUTH-3/tools/crash-ack.ps1` 编排（park → kill → recover → 幂等）。
- 单独放进 `dotnet test` 全量时，**没有驱动设 `NEWMANGA_FEA11_CRASH_STATE`**，
  所以它们在第一行 `Assert.False(string.IsNullOrWhiteSpace(state), ...)` 就失败 ——
  **这是"前置条件缺失"的诚实失败，不是产品缺陷**。

## 3. 它们确实被覆盖（实测证据）

`crash-ack.ps1` 实测（`E9-FILE-ROOT-RECOVERY-1` 之后）：

```
CRASH_POINT=PASS acknowledge_once=1 gates_open=True rows_unchanged=True
  second_call_idempotent=True commit_digest_match=True distinct_host_pid=True
  distinct_core_session=True fresh_grant=True source_sha256_unchanged=True sidecar_proven_dead=1
EXIT=0
```

**10 项 CHECK 全 1**，证据归档在
`verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-0a1d9d2eb425495fad533910d0ef414a/`。

**⇒ 这 2 个 fail 对应的能力是真实存在并且被验证过的**，只是**验证入口不是 `dotnet test`，而是驱动脚本**。

## 4. 全量测试的正确读法

```
全量 Host.Tests（NEWMANGA_FEA11_IPC=1 + NEWMANGA_BUILD_PYTHON）：
2 failed / 353 passed / 50 skipped / 405
```

**这 2 个 failed 必须读作**："2 个需要外部驱动的两阶段测试，在当前入口下缺少前置条件"，
**不能读作**"2 个产品缺陷"，**也不能**为了好看而转成 skip。

## 5. 结论

| 项 | 结论 |
|---|---|
| 是否改测试 | **否**（改动会触碰纪律红线，且降低可见性） |
| 是否新增 skip | **否** |
| 这 2 个 fail 的性质 | **设计使然：两阶段驱动的一半，缺少外部驱动的前置条件** |
| 是否已被覆盖 | **是** —— `crash-ack.ps1` 的 `CRASH_POINT=PASS`，10 项 CHECK 全 1 |
| 建议 | 保持可见；在本文件与矩阵文档里固定这个读法，防止后人误当缺陷或误转 skip |
