# FILE_IDENTITY_CHANGED 定位（第一轮）：口径契约与实际缺口

- head: `ac434d911`
- 前提更正：这**不是 flaky、不是并发**，是这两个测试**第一次真正执行**时的真实失败
  （见 `correction-skip-vs-pass.md`）

## 契约（identity.py:3-9，原文）

> The same physical file must present one identity everywhere: scanner facts,
> the grant scope, the Windows handle probe, the strict read lease and the
> import scope check. **Raw NTFS file indices are 64-bit unsigned and can exceed
> SQLite INTEGER / the wire's representable range, so every producer and every
> comparator calls `normalize_identity` — never the raw `st_ino`.**

归一化规则（`identity.py:16/20/27`）：

```python
_VOLUME_MASK = 0xFFFFFFFF          # 与 Windows dwVolumeSerialNumber 一致（32 位）
_FILE_MASK   = (1 << 53) - 1       # C-17 N/G 整数族，53 位可精确表示
def normalize_identity(volume_serial, file_id):
    return (int(volume_serial) & _VOLUME_MASK, int(file_id) & _FILE_MASK)
```

## 比较点（scanner.py:163-171）—— 这一侧是对的

```python
dev, ino, size = _stat_folder_entry(path, root)
expected_volume = facts.volume_serial
if os.name == "nt":
    dev &= 0xffffffff
    expected_volume &= 0xffffffff
if dev != expected_volume or ino != facts.file_id or size != facts.size:
    raise SourceImportError("FILE_IDENTITY_CHANGED", "granted folder member identity drifted")
```

`_stat_folder_entry`（`scanner.py:81-100`）尾部：

```python
from application.importing.referenced.identity import normalize_identity
return normalize_identity(info.st_dev, info.st_ino) + (size,)
```

⇒ `dev` / `ino` **已 normalize**（再 `&= 0xffffffff` 是冗余但无害）。

## 所以缺口在「producer」侧，不是 comparator

`facts` 来自 `resolved.folder_entries`，其生产链：

```
source_read_refs.py:210   folder_entries=scope[4],
source_read_refs.py:286   folder_entries=grant.folder_entries,
source_read_refs.py:1080  return GrantFacts(*numbers, raw["sha256"])
```

**`GrantFacts(*numbers, ...)` 里的 `numbers` 是否经过 `normalize_identity`，是本轮尚未确认的关键点。**

## 另一处未 normalize 的强候选：Host 侧的 FileIndex 计算

`HostIssuer.cs:591-596`（Windows 侧 probe）：

```csharp
if (!GetFileInformationByHandle(handle, out var info)) { ... }
return (info.VolumeSerialNumber, ((ulong)info.FileIndexHigh << 32) | info.FileIndexLow);
```

⇒ **Host 返回的是完整 64 位 FileIndex，没有 `& ((1<<53)-1)`**。

而 `identity.py` 的契约要求「every producer … calls normalize_identity」。
如果这条路径把未 mask 的 64 位值写进 grant scope（经 IPC 进入 `resolved.folder_entries`），
比较时 `ino`（已 mask 53 位）就会与 `facts.file_id`（未 mask）不等
⇒ **`FILE_IDENTITY_CHANGED`**。

**注意**：FileIndex 恰好 ≤ 2^53 时两者相同 —— 这解释了为什么是**偶发**失败：
NTFS 的 file index 通常是递增的小数值，但跨卷/跨时间可能超过 53 位。
在 `test.ps1` 下跑了更多测试、创建了更多临时文件，命中超过 2^53 的 index 的概率随之上升。

> 这一条是**假设**，需要下一轮用实测数据验证：把注册时记录的 `file_id` 与导入时
> `_stat_folder_entry` 的值取出来对比，看是否只在高位不同。

## 验证计划（下一轮）

1. 在 `GrantIssuerTests` 的失败点上抓取两侧的实际数值（Host 写入的 `file_id`、
   Python `st_ino` 原始值与 mask 后值）；
2. 判定是「Host 未 mask」还是「`source_read_refs.py:1080` 的 `GrantFacts(*numbers)` 未 mask」；
3. 修法方向（两种，取决于上一步结论）：
   - **A**：在 Host 侧 IPC 序列化前 mask（与契约一致，"every producer normalize"）；
   - **B**：在 core 侧反序列化 grant scope 时 mask（防御式，接受未规范输入）；
   - 契约文本要求 A；B 可作为纵深防御。

## 本轮不做修改的原因

`identity.py` 的契约把 `normalize_identity` 规定为**唯一口径**，而当前至少有一处
producer 可能违反。改哪一侧取决于实测数据（A 还是 B），**不能靠猜**。
本会话已有 6 次「用自己的推断代替验证」的错误记录，这一轮先取证。
