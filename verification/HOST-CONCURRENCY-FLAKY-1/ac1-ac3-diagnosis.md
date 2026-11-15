# HOST-CONCURRENCY-FLAKY-1 AC1/AC3 诊断：`SOURCE_REGISTRY_BUSY` 的根因

- head: `25e8f5492`
- 方法：读源码（`SourceAccessRegistry.cs`），不猜

## AC1：并发路径已澄清

### 锁的作用域与命名

`SourceAccessRegistry` 构造（`L26-35`）：

```csharp
public SourceAccessRegistry(string dataRoot, ISecretProtector? protector = null)
{
    var normalized = SourceSecurity.Normalize(dataRoot);
    _directory = Path.Combine(normalized, "host", "source-access");
    var digest = Convert.ToHexString(
        SHA256.HashData(Encoding.UTF8.GetBytes(normalized.ToUpperInvariant())))
        .ToLowerInvariant()[..16];
    _lockName = "NewManga.Host.SourceAccessRegistry." + digest;
}
```

⇒ **`_lockName` 由 `dataRoot` 的 SHA256 派生，每个 dataRoot 唯一。**

`HostFixture.CreateOptions`（测试侧）：

```csharp
dataRoot = NewDataRoot(testName);
MutexName = mutexName ?? @"Local\NewManga.Host.Test." + Guid.NewGuid().ToString("N")[..12],
```

⇒ **`dataRoot` per-test 唯一 ⇒ `_lockName` 也 per-test 唯一。**
**所以不是跨测试抢同一把锁。**

### 锁的实际实现（`Locked<T>`，`L334-358`）

```csharp
Mutex mutex;
try { mutex = new Mutex(false, "Global\\" + _lockName); }
catch (UnauthorizedAccessException) { mutex = new Mutex(false, "Local\\" + _lockName); }
using (mutex)
{
    var acquired = false;
    try
    {
        try { acquired = mutex.WaitOne(0); }                    // ← ① 零超时
        catch (AbandonedMutexException) { acquired = true; }
        if (!acquired) throw new SourceAccessException("SOURCE_REGISTRY_BUSY");   // ← :346
        SourceSecurity.RejectReparseAncestors(_directory);
        FileStream fileLock;
        try { fileLock = new FileStream(
            Path.Combine(_directory, "registry.v1.lock"),
            FileMode.OpenOrCreate, FileAccess.ReadWrite, FileShare.None); }        // ← ② 独占文件锁
        catch (IOException) { throw new SourceAccessException("SOURCE_REGISTRY_BUSY"); }
        using (fileLock) return action();
    }
    ...
    finally { if (acquired) mutex.ReleaseMutex(); }
}
```

## AC3：根因判定 = 「锁粒度不足」+「零超时」

**两个独立缺陷，都在同一段代码里：**

### 缺陷 1：`mutex.WaitOne(0)` 零超时、不重试

拿到锁失败**立即**抛 `SOURCE_REGISTRY_BUSY`，没有任何等待/重试。

⇒ **同一进程内**只要有另一个线程在极短窗口内持有同名 mutex，
本次调用就直接失败。对于一个「每次操作都重新加载」的 registry（`L16` 注释），
这是**必然发生**的竞争窗口。

### 缺陷 2：`FileShare.None` 的独占文件锁同样零重试

即使 mutex 拿到了，`registry.v1.lock` 以 `FileShare.None` 打开，
失败也立即 `SOURCE_REGISTRY_BUSY`。

### 缺陷 3（与 `Generation` 相关）：`:71` 的乐观并发

```csharp
if (entry.Generation != expectedGeneration) throw new SourceAccessException("SOURCE_REGISTRY_BUSY");
```

调用方在**同一逻辑操作内**若先读后写、期间状态被别人改过，也会得到 BUSY —— 同样是**无重试**。

## 为什么偏偏是 `Fea11WatchHostRuntimeTests` 暴露

测试 `Ready_ArmsWatcher_RealFileEventProducesHint_DisposeDisarms` 的行为是：

1. 测试线程：`SourceAccessRegistry.Register(...)` 注册 source；
2. `HostRuntime` 启动后，**后台 watcher 线程**在文件事件到达时也要访问 registry；
3. 两条路径在同一 dataRoot 上竞争同一把 mutex / 文件锁；
4. 因为 `WaitOne(0)` 不等，**任一方立即失败**。

⇒ `SOURCE_REGISTRY_BUSY` 是**同进程内并发访问**的必然结果，不是环境噪声。

## `FILE_IDENTITY_CHANGED` 的关联

`scanner.py:170` 的 `"granted folder member identity drifted"`。
两个 `GrantIssuerTests` 也走 grant/import 路径，同样会读写 registry；
它们在 `test.ps1` 下与其它 30 个新执行的测试并行，
更可能与自己的 watcher/后台任务撞在同一 dataRoot 上，导致 identity 校验读到中间态。

**这一条需要 AC2（受控复现）才能确认到代码级**，本轮只记录关联性。

## 修复方向（供 AC4 范围冻结参考，本轮不实施）

| 方案 | 做法 | 评价 |
|---|---|---|
| **A（推荐）** | `WaitOne(0)` → `WaitOne(boundedTimeout)`（如 5s），`FileShare.None` 失败改为有界重试 | 最小改动，符合「BUSY 表示真的忙」的语义 |
| B | 在 `HostRuntime` 内对 registry 访问串行化（单线程调度） | 改动大，需重构调用方 |
| C | 把 `SOURCE_REGISTRY_BUSY` 变成可重试错误，让调用方重试 | 分散到多个调用点，易漏 |

**A 的关键**：`SOURCE_REGISTRY_BUSY` 的语义应是「**在合理等待后仍然忙**」，
而不是「**这一次抢占失败了**」。当前实现把「瞬时竞争」和「真的忙」混为一谈。

## 本轮结论

- **AC1 完成**：锁名 per-dataRoot 唯一；不是跨测试抢锁；是**同进程内竞争 + 零超时**。
- **AC3 部分完成**：`SOURCE_REGISTRY_BUSY` 根因明确为「零超时 + 无重试」；
  `FILE_IDENTITY_CHANGED` 的机制关联已指出，但需 AC2 受控复现确认。
- **不改产品代码**：修并发语义属产品行为变更，需范围冻结（AC4）。
