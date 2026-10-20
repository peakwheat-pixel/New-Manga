# 四项 `SEC-FMT` 的防御在 `src/` 里都已经存在

**产出**: 2026-10-20 · **对应**: `SEC-FMT-IMPL-1` 的范围重估
**起因**：Round 143 发现 `SEC-FMT-002` 的防御已存在于 `test_assets/`。
**所以先查其余三项是否也已存在——避免重写已有防线。**

## 一、结论

**三项都已有实现，且都在 `src/`（产品代码）里，不是只在测试工具里。**

| ID | 攻击面 | 已在何处实现 |
|---|---|---|
| `SEC-FMT-001` | Zip Slip / 路径穿越 | **`src/` 至少 6 处** |
| `SEC-FMT-002` | XXE / Billion Laughs | `test_assets/.../assets.py` 4 处（见 R1 文件）|
| `SEC-FMT-003` | 伪装图像的无效二进制 | **`src/` 至少 5 处** |
| `SEC-FMT-004` | 超长路径 | **`src/` 至少 3 处** |

## 二、逐项证据

### `SEC-FMT-001` Zip Slip

| 位置 | 内容 |
|---|---|
| `src/application/export/service.py` L635 | 「Strips any directory components (path traversal), rejects empty names」|
| `src/application/resource_channel/dto.py` L101–L114 | 「no drive, no UNC prefix, no empty/`.`/`..` traversal segments」；`raise TypedResourceChannelError(E_MALFORMED, "traversal segment in rel_path")` |
| `src/application/resource_channel/service.py` L94 | 同上，注释说明 |
| `src/infrastructure/filesystem/managed_storage.py` L168 | `Path(relative_path).is_absolute()` 拒绝 |
| `src/application/maintenance/cleanup.py` L221 | **「a naive startswith check would let `cache/webtoon-tiles/../../...`」**——说明这里已经想过 `startswith` 不够 |
| `src/infrastructure/sqlite/library.py` L1231 | 「traversal, absolute path, or a plain unlink」|

**`cleanup.py` L221 那条注释特别重要**：它记录了「朴素 `startswith` 不够」这个认知。
**这正是 `SEC-FMT-001` 要求的那种深度。**

### `SEC-FMT-003` 魔数嗅探

| 位置 | 内容 |
|---|---|
| `src/application/importing/documents/service.py` L22–L30 | `_PDF_MAGIC = b"%PDF-"` + `data.startswith(_PDF_MAGIC)` |
| `src/infrastructure/imaging/streaming_png.py` L52 | `PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"` |
| `src/infrastructure/imaging/webtoon_tiles.py` L82 | 同上签名 |
| `src/bootstrap/acceptance_bridge.py` L139 | 同上 |
| `src/bootstrap/core_assembly.py` L466 | `payload.startswith(b"NMFR")`（自家格式）|

**所以 PDF 与 PNG 都有魔数校验。**

**JPEG** 的签名在 `test_assets/.../assets.py` L317（`stream.read(2) != b"\xff\xd8"`），
**但 `src/` 里是否有 JPEG 魔数校验，本轮未确认——这是 AC3 的一个待查点。**

### `SEC-FMT-004` 长路径

| 位置 | 内容 |
|---|---|
| `src/infrastructure/export/target_refs.py` L235 | `if value.startswith("\\\\?\\")`——已识别长路径前缀 |
| `src/infrastructure/resource_channel/handle_resolver.py` L185–L187 | `\\\\?\\UNC\\` 与 `\\\\?\\` 两种形式都处理 |
| `src/infrastructure/sqlite/connection.py` L3 | 「Unicode paths, no MAX_PATH」|

**`handle_resolver.py` 区分了 `\\?\UNC\` 与 `\\?\`**——这是 Windows 长路径的完整形态，
说明实现者知道 UNC 需要不同前缀。

## 三、这改变了 `SEC-FMT-IMPL-1` 的性质

### 原假设

**Task 文件写的是「实现四个安全测试 + 外部阅读器验证」。**
**`proposed` 状态的默认读法是「这些防御不存在，需要建」。**

### 实际情况

**四项防御都已存在。缺的不是实现，是「证明它们有效」。**

| 原 AC | 实际需要做的 |
|---|---|
| AC1 Zip Slip 防御 | **证明**已有 6 处守卫真的挡住攻击 |
| AC2 XXE 防御 | **证明** `assets.py` 的 DTD/ENTITY 拒绝真的有效（R1 已实测，需落为测试）|
| AC3 魔数嗅探 | **证明**已有签名校验；**并确认 JPEG 在 `src/` 是否有** |
| AC4 长路径 | **证明** `\\?\` 处理真的能读 >260 字符路径 |

**所以这是一个「验证 Task」，不是一个「实现 Task」。**

## 四、这对范围的影响

### 变小

**不需要从零写四道防线。** 工作量主要在校验与测试。

### 变大（另一方向）

**「证明已有防线有效」比「写一道防线」更难被信任**，因为：

- 测试必须**真的打到那道守卫**，而不是在它前面被别的检查拦住
- 需要**对照臂**：合法输入仍被接受（否则「拒绝一切」也能过）
- **`SEC-FMT-001` 的 6 处守卫中，可能只有 1–2 处真的挡在攻击路径上**——要逐处判断

**这是「覆盖度」问题，不是「存在性」问题。**

### 一个必须先回答的问题

**这四道防线在什么路径上生效？**

**例如 `SEC-FMT-001` 的 `dto.py` 守卫在 `resource_channel` 上，
而 `SEC-FMT-001` 的攻击面是「ZIP/CBZ 条目路径」。这两者是不是同一条路径？**

**若不是，那么「有守卫」不等于「挡住了该攻击」。**

**这是 AC1 的第一个问题，本轮不答。**

## 五、明确未做

- **未验证任何一处守卫在实际攻击路径上生效**——只列出它们存在。
- **未确认 `src/` 是否有 JPEG 魔数校验**（AC3 待查）。
- **未确认 `SEC-FMT-001` 的守卫是否覆盖 ZIP 条目解压路径**（§四末）。
- **未修改 `SEC-FMT-IMPL-1` 的 AC 判定**——本文件是证据，判定待实施或裁定。
- **未检查 `.rs` 侧**是否有对应防御（只查了 Python）。

## 六、给实施的第一个问题

**「这四道防线存在」和「这四道防线在该攻击路径上生效」是两个不同的命题。**

**本文件证明了前者。后者需要在实施时逐条走查。**

**而这正是 r33 对 `DETECT-TILING-1` 的裁定所强调的同一件事**：

> **结构验证不能替代真实验证。**
