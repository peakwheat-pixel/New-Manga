# FILE_IDENTITY_CHANGED 根因铁证：Host 侧 producer 违反 `normalize_identity` 契约

- head: `4b1198443`
- 前序：`file-identity-diagnosis.md`（契约缺口）、`st-ino-measured.md`（物理条件实测）

## 完整链路（每一环都有代码）

### 环 1：Host 写入**未 mask 的 64 位** FileIndex

`apps/desktop-avalonia/src/NewManga.CoreClient/Issuer/HostIssuer.cs:558-566`：

```csharp
if (!GetFileInformationByHandle(handle, out var info))
{
    throw new HostIssuerException("REF_SCOPE_DENIED", "cannot read import source identity");
}

ulong index = ((ulong)info.FileIndexHigh << 32) | info.FileIndexLow;   // ← 完整 64 位
var size = ((long)info.FileSizeHigh << 32) | info.FileSizeLow;
var reparse = (info.FileAttributes & 0x400) != 0;
return (info.VolumeSerialNumber, index, size, reparse);                // ← 未 mask
```

`info.VolumeSerialNumber` 本身是 `uint`（32 位），天然合规；
**`index` 是完整 64 位，没有任何 53 位截断。**

### 环 2：core 原样透传，不做归一化

`src/infrastructure/resource_channel/source_read_refs.py:1060-1080`：

```python
@staticmethod
def _facts(raw) -> GrantFacts:
    if not isinstance(raw, dict) or set(raw) != {
        "volume_serial", "file_id", "size", "sha256"
    }:
        raise SourceImportError("SOURCE_ACCESS_DENIED", "source-read grant facts are malformed")
    numbers = (raw["volume_serial"], raw["file_id"], raw["size"])      # ← 直接用 raw
    if any(isinstance(value, bool) or not isinstance(value, int) or value < 0
           for value in numbers):
        raise SourceImportError("SOURCE_ACCESS_DENIED", "source-read grant facts are malformed")
    if not isinstance(raw["sha256"], str) or not _SHA256.fullmatch(raw["sha256"]):
        raise SourceImportError("SOURCE_ACCESS_DENIED", "source-read grant facts are malformed")
    return GrantFacts(*numbers, raw["sha256"])                          # ← 未 mask
```

**该文件里 `normalize_identity` 一次都没出现**（已 grep 确认）。

### 环 3：比较端用**mask 后的 53 位**

`src/application/importing/referenced/scanner.py:81-100`（`_stat_folder_entry` 尾部）：

```python
from application.importing.referenced.identity import normalize_identity
return normalize_identity(info.st_dev, info.st_ino) + (size,)
```

`identity.py:16/20/27`：

```python
_VOLUME_MASK = 0xFFFFFFFF
_FILE_MASK   = (1 << 53) - 1
def normalize_identity(volume_serial, file_id):
    return (int(volume_serial) & _VOLUME_MASK, int(file_id) & _FILE_MASK)
```

`scanner.py:163-171`：

```python
dev, ino, size = _stat_folder_entry(path, root)
expected_volume = facts.volume_serial
if os.name == "nt":
    dev &= 0xffffffff
    expected_volume &= 0xffffffff
if dev != expected_volume or ino != facts.file_id or size != facts.size:
    raise SourceImportError("FILE_IDENTITY_CHANGED", "granted folder member identity drifted")
```

### 结论：`ino`（mask 后）对比 `facts.file_id`（未 mask）

**只要 FileIndex > 2^53，两者必然不等** —— 而 `st-ino-measured.md` 已实测
`%TEMP%` 下新建文件 6/6 超过 2^53。

## 这违反了哪条契约

`src/application/importing/referenced/identity.py:3-9` 原文：

> The same physical file must present one identity everywhere: scanner facts,
> the grant scope, the Windows handle probe, the strict read lease and the
> import scope check. Raw NTFS file indices are 64-bit unsigned and can exceed
> SQLite INTEGER / the wire's representable range, so **every producer and every
> comparator calls `normalize_identity` — never the raw `st_ino`.**

契约明确点名了 **"the Windows handle probe"** 和 **"the grant scope"** 都是 producer，
都必须 `normalize_identity`。`HostIssuer.cs:563` 是 Windows handle probe 的实现，
**它就是那个违约的 producer**。

## 影响面（不只是测试）

任何用户**新导入**的源文件，其 NTFS FileIndex 大概率 > 2^53（实测 6/7），
所以「新建/下载的文件夹 → 导入」这条**正常用户路径**会稳定报
`FILE_IDENTITY_CHANGED`（"Import source reference was rejected"）。

这是本会话发现的**第一个可能直接影响真实用户**的缺陷
（此前修的 `CommandWiring*` / `RunBindingFix*` 都是测试期望过时）。

## 修法（契约要求的方向）

**Host 侧 producer 必须与 comparator 同口径**：

```csharp
// HostIssuer.cs:563
const ulong FileIdMask = (1UL << 53) - 1;
ulong index = (((ulong)info.FileIndexHigh << 32) | info.FileIndexLow) & FileIdMask;
```

同时需要检查 `DirectoryIdentity`（`HostIssuer.cs:596`）是否也被同一套比较逻辑使用 ——
若目录 identity 也走 `normalize_identity` 比较，则同样要 mask。

**单一事实来源问题**：`_VOLUME_MASK` / `_FILE_MASK` 目前只定义在 Python 侧
（`identity.py`），C# 侧若复制常量就产生第二份真相。
**下一轮必须先确认项目里是否已有跨语言共享的常量定义**（如生成的协议文件），
没有的话要在 Task 中明确记录「常量以 `identity.py` 为准，C# 侧镜像并在注释里指向它」。

## 本轮不改代码的原因

`HostIssuer.cs` 属于 `apps/desktop-avalonia/src/NewManga.CoreClient/`，
而本卡的 `allowed_paths` 只授权了 `apps/desktop-avalonia/src/NewManga.Host/Sources/**`。

**这是模型层（CoreClient/Issuer）的改动，超出了本卡范围。**
按治理规则，需要先扩展 `allowed_paths` 或另立卡。
本轮已把根因定到行，下一轮做范围决策。
