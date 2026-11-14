# FEA11-ENTRY-MISSING-1 证据：`SOURCE_ENTRY_MISSING` 归因（部分）

基线 `414e3e8d1`。对象：`Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain_NewKeyOldDigestConserved`。

## 1. 失败形态

```
NewManga.Host.Sources.SourceAccessException : SOURCE_ENTRY_MISSING
  at NewManga.Host.Sources.SourceReadCoordinator.DescribeContainer(String path, Int64 maxBytes)
     line 382
```

## 2. 抛出点（代码事实）

`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs`：

```csharp
private static JsonObject DescribeContainer(string path, long maxBytes)
{
    SourceSecurity.RejectReparseAncestors(path);
    FileStream stream;
    try { stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read); }
    catch (Exception error) when (error is not OutOfMemoryException)
    {
        throw MapMintFailure(error);          // <-- line 382
    }
    ...
}

public static SourceAccessException MapMintFailure(Exception error) => error switch
{
    FileNotFoundException or DirectoryNotFoundException or UnauthorizedAccessException =>
        new SourceAccessException("SOURCE_ENTRY_MISSING"),
    IOException => new SourceAccessException("FILE_IDENTITY_CHANGED"),
    ArgumentException or NotSupportedException => new SourceAccessException("SOURCE_ACCESS_DENIED"),
    _ => new SourceAccessException("SOURCE_ENTRY_MISSING"),      // <-- 兜底
};
```

⇒ 失败发生在 **`FileStream` 打开**，且**内层异常类型被 `MapMintFailure` 丢弃**。

**★ 诊断性缺陷（P3）**：`_ => SOURCE_ENTRY_MISSING` 兜底 + 不保留 inner exception，
使"文件不存在 / 无权限 / 被占用 / 其它"在错误码上**不可区分**，排障只能靠猜。

## 3. 已排除：种子与路径

手动按 fixture 的相同参数跑种子（路径含 `FEA-11`）：

```
FEA11_IPC_SEED_OK {"schema_version": 14}
ipc-seed-receipt.json  830 B
library.db          626688 B
source-v1.zip          358 B
source-v2.zip          358 B      <-- new_zip 确实创建
new_zip : ...\FEA-11\fixtures\probe-<guid>\source-v2.zip
```

⇒ **`new_zip` 文件存在**，路径也是绝对路径；`schema_version=14` 与 `CoreSchema.Current` 一致。

## 4. 因此，剩余可能（未定论）

1. **文件被占用**（`FileShare.Read` 与另一持有者冲突）→ 会映射成 `IOException`→`FILE_IDENTITY_CHANGED`，
   但实测是 `SOURCE_ENTRY_MISSING`，所以**不太可能是占用**；
2. **`UnauthorizedAccessException`**（路径在 workspace 下，可能受 ACL 影响）；
3. **`PathTooLongException` / 其它** → 走 `_ =>` 兜底。

**要定论必须先拿到内层异常类型**，而这被 `MapMintFailure` 丢弃了。

## 5. 建议（未实施）

1. **产品侧（P3 改进）**：`MapMintFailure` 保留 `innerException`，或在兜底分支用 `SOURCE_ENTRY_MISSING`
   但把原始类型写进 message/诊断，使"文件不存在"与"其它"可区分 —— 这是**诊断性**改动，不改错误码对外语义；
2. **测试侧**：本次失败在 `DescribeContainer` 的 `FileStream` 打开处，需在测试里先断言
   `File.Exists(newZip)` 并打印路径，把"文件不存在"从"其它"里分离出来；
3. 在拿到内层异常前，**不得**声称这是产品缺陷或测试缺陷。

## 6. 本卡边界

- 已排除：种子未生成 `new_zip`、路径非绝对、schema 版本不符。
- 未定论：`FileStream` 打开的具体失败原因（被兜底掩盖）。
- 带 opt-in 三类基线仍 **12 passed / 1 failed**。
- 条件 3 仍不判 MET。
