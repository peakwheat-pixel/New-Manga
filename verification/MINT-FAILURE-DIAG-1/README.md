# MINT-FAILURE-DIAG-1 证据

基线 `8ca6a36ff`。目标：让 `SOURCE_ENTRY_MISSING` 可诊断（保留原始异常），并据此拿到真实原因。

## 1. 改动（最小，错误码语义不变）

| 文件 | 改动 |
|---|---|
| `src/NewManga.Host/Sources/SourceSecurity.cs` | `SourceAccessException(string code, Exception? inner = null)`：新增**可选** inner；新增 `OriginalExceptionType`；**重写 `Message => Code`** |
| `src/NewManga.Host/Sources/SourceReadCoordinator.cs` | `MapMintFailure` 的**每个**分支都把 `error` 作为 inner 传入（含 `_ =>` 兜底） |
| `tests/NewManga.Host.Tests/MapMintFailureDiagnosticsTests.cs` | 新增 3 个 Fact |

**为什么重写 `Message => Code`**：`Exception(string, Exception)` 会把 `" ---> inner message"` 追加到 `Message`，
那会**静默改变**既有断言与冻结错误词汇依赖的文本。重写后 `Message` 与改动前逐字相同，原始信息只经
`InnerException` / `OriginalExceptionType` / `Exception.ToString()` 暴露。

## 2. 判别测试

| 测试 | 断言 |
|---|---|
| `UnlistedException_KeepsSourceEntryMissingCode` | `InvalidOperationException` → `Code == "SOURCE_ENTRY_MISSING"`，且 `Message` **逐字等于** code |
| `UnlistedException_OriginalTypeIsObservable` | 同上 → `InnerException` 非空、`OriginalExceptionType == nameof(InvalidOperationException)` |
| `EnumeratedExceptions_KeepTheirOwnCodes_AndCarryTheOrigin` | `FileNotFound/UnauthorizedAccess` → `SOURCE_ENTRY_MISSING`；`IOException` → `FILE_IDENTITY_CHANGED`；`ArgumentException` → `SOURCE_ACCESS_DENIED`；**且每个都带原始类型** |

**判别力**：把 `MapMintFailure` 里两个 `SOURCE_ENTRY_MISSING` 分支的 `, error` 去掉 → **2 failed / 1 passed**；
恢复 → **3 passed**。

**我自己犯的一个错（已登记在测试注释里）**：最初用 `PathTooLongException` 当"走兜底"的探针，
但它**继承自 `IOException`**，实际映射到 `FILE_IDENTITY_CHANGED` ⇒ 测试红。
改用 `InvalidOperationException` 后才真正覆盖兜底分支。这说明**兜底分支比直觉难触发**。

## 3. ★ 本卡的真正产出：拿到真实原因

改动后重跑 `Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain_NewKeyOldDigestConserved`：

```
NewManga.Host.Sources.SourceAccessException : SOURCE_ENTRY_MISSING
---- System.UnauthorizedAccessException : Access to the path
     'G:\CODEX\New Manga.workspace\FEA-11\fixtures\r4a-production-09056d4bffc7404f9956736cc2555a49' is denied.
```

**关键**：被拒绝的路径是 **fixture 的 root 目录**（`r4a-production-<guid>`），**不是** `source-v2.zip`。
即某处把**目录**当成了容器路径传给 `DescribeContainer`，`FileStream` 打开目录 → `UnauthorizedAccessException`
→（修复前被兜底）`SOURCE_ENTRY_MISSING`。

**⇒ `FEA11-ENTRY-MISSING-1` 的 blocked 已解除**：原因不再是"未知"，而是"目录被当容器"。
下一步应定位**谁**把这个目录传进去（`Fea11Residual4AIpcTests` 的 `IssueAsync` 调用链），
但那属**另一张卡**，本卡（诊断能力）已完成。

## 4. 未做

- 未修那个把目录当容器的调用点（属 `FEA11-ENTRY-MISSING-1` 后续）。
- 未跑无夹具三项目全量（本卡改了产品代码 `SourceAccessException`/`MapMintFailure`，
  会影响 Host 测试面，需在下一轮或本卡收口时补跑 —— **如实标注：本卡未跑全量**）。
