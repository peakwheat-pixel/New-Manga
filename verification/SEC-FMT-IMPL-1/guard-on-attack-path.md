# 守卫是否在攻击路径上：逐项答案

**产出**: 2026-10-20 · **对应**: `SEC-FMT-IMPL-1` 的第一个实质问题
**上一轮留下的问题**：

> `SEC-FMT-001` 的守卫在 `resource_channel` 上，而攻击面是「ZIP/CBZ 条目路径」。
> **这两者是同一条路径吗？若不是，「有守卫」不等于「挡住了该攻击」。**

## 一、`SEC-FMT-001` Zip Slip：答案是「产品路径不适用，测试侧完整实现」

### 1.1 `src/` 只创建 ZIP，从不解压

**全文搜索 `extractall` / `namelist(` / `infolist(` / `ZipFile(...) as ...`:**

**唯一命中**：

```python
src/application/export/service.py L442:
    with zipfile.ZipFile(temp, "w", compression=compression, ...) as archive:
```

**`"w"` 模式。只写。**

**`namelist()` / `infolist()` / `extractall()` 在产品代码里零命中。**

**所以 Zip Slip 在产品路径上不适用**——产品不会把任何 ZIP 条目写到文件系统。

### 1.2 `test_assets/.../assets.py` 有完整实现

**而校验工具侧有真正的解压路径，且有完整守卫。**

**`zip_parts`（L691–L701）**：

```python
def zip_parts(info: zipfile.ZipInfo) -> tuple[str, ...]:
    name = info.filename
    path = PurePosixPath(name)
    clean_name = name[:-1] if info.is_dir() and name.endswith("/") else name
    if (
        not clean_name or "\\" in name or "\x00" in name or ":" in name
        or path.is_absolute() or PureWindowsPath(name).drive
        or any(part in {"", ".", ".."} for part in clean_name.split("/"))
    ):
        raise ValueError(f"unsafe path in ZIP archive: {name!r}")
    return path.parts
```

**它拒绝**：

| 攻击形态 | 被哪一条挡住 |
|---|---|
| `../../Windows/System32/evil.dll` | `any(part == "..")` |
| `/etc/passwd`、`C:\Windows\...` | `path.is_absolute()` / `PureWindowsPath(name).drive` |
| `..\..\evil`（反斜杠）| `"\\" in name` |
| `C:evil`（驱动器相对）| `":" in name` |
| `foo/./bar` | `any(part == ".")` |
| `evil\0.png`（NUL 截断）| `"\x00" in name` |

### 1.3 而且它在正确的调用位置

`manga_members` 的**第一行**就是 `parts = zip_parts(info)`（L708）：

```python
for info in archive.infolist():
    parts = zip_parts(info)      # L708 - every entry goes through this
    if info.is_dir():
        continue
```

**所以每个条目都被检查，没有旁路。**

### 1.4 第二层防御：白名单而非黑名单

**即使 `zip_parts` 被绕过，写入路径也不是从条目名拼出来的。**

**`manga_members` 只接受匹配极窄模式的名字**：

```python
if part == "images" and tail[0] == title and len(tail) == 2:
    name = tail[1]
    if re.fullmatch(r"\d{3,}\.jpg", name):     # 只接受 NNN.jpg
```

**而 `copy_zip_member` 的 `destination` 由调用者给定**（`local_dir(case)` + 已知结构），
**不使用 `info.filename` 拼路径。**

**所以这是双层防御：入口白名单 + 出口路径不受输入影响。**

**比单纯的「校验条目名」更强。**

## 二、`SEC-FMT-002` XXE：产品路径不适用，测试侧已实现

**见 `r1-xml-parsing-scope.md`。**

**`src/` 只写 XML（`ET.Element` + `tostring`），不解析。**
**`assets.py` 4 处解析，全部先拒绝 `<!DOCTYPE` / `<!ENTITY`。**

**Round 143 已实测**：XXE 与 Billion Laughs 均被拒，合法 XML 通过。

## 三、`SEC-FMT-003` 魔数嗅探：产品路径有，但需确认覆盖

**`src/` 已有的**：

| 格式 | 位置 | 内容 |
|---|---|---|
| PDF | `importing/documents/service.py` L22–30 | `_PDF_MAGIC = b"%PDF-"` |
| PNG | `imaging/streaming_png.py` L52 等 3 处 | `PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"` |
| 自家格式 | `bootstrap/core_assembly.py` L466 | `NMFR` |

**JPEG 的签名校验**：**只在 `test_assets/.../assets.py` L317 找到**（`read(2) != b"\xff\xd8"`）。

**`src/` 里是否有 JPEG 魔数校验——`core_service.py` L1399 的注释说**：

> 「whitelist enforced fail-closed after the header sniff」

**说明 Pillow 的 `Image.open` 之前有 sniff，但需要确认它覆盖 JPEG。**

**这是 `SEC-FMT-003` 的待查点，本轮不答。**

## 四、`SEC-FMT-004` 长路径：产品路径有识别，但需确认转换

**`src/` 已有的识别**：

```python
src/infrastructure/export/target_refs.py L235:     if value.startswith("\\\\?\\"):
src/infrastructure/resource_channel/handle_resolver.py L185:  if path_text.startswith("\\\\?\\UNC\\"):
src/infrastructure/resource_channel/handle_resolver.py L187:  elif path_text.startswith("\\\\?\\"):
```

**但这些是「识别已有的 `\\?\` 前缀」，不是「在路径过长时主动加前缀」。**

**`SEC-FMT-004` 要求的是**：

> 路径适配器自动启用 Windows `\\?\` 长路径前缀

**「识别」与「启用」是两件事。**

**`src/infrastructure/sqlite/connection.py` L3 提到「no MAX_PATH」，但那是 SQLite 连接层。**

**所以 `SEC-FMT-004` 是否满足，本轮不确定——这是 AC4 的待查点。**

## 五、汇总：四项的真实状态

| ID | 产品路径（`src/`） | 测试/校验路径 | 判定 |
|---|---|---|---|
| `SEC-FMT-001` | **不适用**（只写不解压）| **完整实现**（`zip_parts` + 白名单 + 出口隔离）| **`MET`（在适用路径上）** |
| `SEC-FMT-002` | **不适用**（只写不解析）| **完整实现**（DTD/ENTITY 拒绝 + 大小上限）| **`MET`（在适用路径上）** |
| `SEC-FMT-003` | **部分**（PDF/PNG 有，JPEG 待确认）| JPEG 有 | **待查** |
| `SEC-FMT-004` | **识别有，主动启用待确认** | — | **待查** |

## 六、这改变了 `SEC-FMT-IMPL-1` 的范围（第二次）

**Round 144 说「四项都已实现，需证明有效」。**

**本轮进一步：001 和 002 是「产品不用、校验工具已实现且完整」。**

**所以真正需要工作的只剩两项**：

| 项 | 需要做什么 |
|---|---|
| **`SEC-FMT-003`** | 确认 `src/` 是否有 JPEG 魔数校验；若无，**这是真缺口** |
| **`SEC-FMT-004`** | 确认是否有「主动加 `\\?\` 前缀」的路径适配器；若无，**这是真缺口** |
| `SEC-FMT-001` | 补测试证明 `zip_parts` 真的挡住（工作量小）|
| `SEC-FMT-002` | 补测试证明 DTD 拒绝真的挡住（工作量小）|

**所以 `SEC-FMT-IMPL-1` 从「四项安全测试」实际收敛为「两项真缺口 + 两项补测试」。**

## 七、明确未做

- **未确认 `src/` 是否有 JPEG 魔数校验**（§三末）
- **未确认是否有主动添加 `\\?\` 前缀的适配器**（§四末）
- **未写任何测试**（本文件是范围判定）
- **未修改 `SEC-FMT-IMPL-1` 的 AC 判定**
- **未检查 `.rs` 侧**
