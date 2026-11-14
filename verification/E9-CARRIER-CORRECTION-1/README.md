# E9-CARRIER-CORRECTION-1：更正载体假设 + 新约束

基线 `52bdf9343`。上一轮 `E9-PATH-CARRIER-STUDY-1` 暗示需要 **schema 迁移**。本轮核实**推翻该前提**。

## 1. ★ 更正：C# journal **不是 SQLite 表**，是 DPAPI 加密 JSON 文件

```csharp
private void Write(JournalEntry entry)
{
    var payload = JsonSerializer.SerializeToUtf8Bytes(entry);
    var protectedBytes = Protect(payload);        // DPAPI
    var path = PathOf(entry.OperationId);         // 每 operation 一个文件
}
private JournalEntry Read(string operationId) { ... var payload = Unprotect(body[magic.Length..]); ... }
```

**⇒ 加字段无需 schema 迁移**；`System.Text.Json` 默认对缺失字段留 null，旧文件可反序列化。

`schema.py:798` 的 `source_operations` 表是 **Python Core 侧**的另一份记录（上一轮曾误称
`source_operation_journal`），与 C# journal 文件是两套东西。

**上一轮"需要 schema 迁移"的判断是错的，此处更正。**

## 2. 新约束：`Authorize()` 的调用方**不知道容器路径**

全仓 `_operations.Authorize(...)` 只有 **1 个**调用点：`HostOperationOrchestrator.cs:301`（retry-failed 流程）。
其上下文只有 `entry`（无路径）、`minted.Authorization`（无路径）、`roots`（**正是错的 registry root**）。

真正知道路径的是 `SourceReadCoordinator.IssueLockedAsync` 的 `sourcePath`（grant 发行链），
与 `Authorize()` 写 journal 是**两条不同的链**。

⇒ 加字段容易，**难在"哪个写入点能拿到真实容器路径"**。

## 3. 待裁决的设计问题

1. 操作开始时（plan 创建那刻）是否已知容器路径？已知则记入 journal；
2. 若只有 Core 的 scan target 知道，是否扩 Core 返回（成本回到方案 B）；
3. 若都拿不到，是否接受"非 folder 恢复永久 typed 拒绝"并在产品上限制该能力。

**不能用局部补丁糊过去。**

## 4. 未做

- 未改任何代码；未确认 `StartOperation` 时刻的可用信息。
- 带 opt-in 三类基线仍 **12 passed / 1 failed**；条件 3 仍不判 MET。
