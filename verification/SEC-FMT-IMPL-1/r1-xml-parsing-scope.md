# R1 的答案：本项目**写** XML，但**不解析** XML

**产出**: 2026-10-20 · **对应**: `SEC-FMT-IMPL-1` 的风险 R1
**问题**（Task 自己写的）：
> 本项目是否真的解析 XML（CBZ 的 `ComicInfo.xml`）？
> **若不解析，本项记为 `NOT_APPLICABLE` 并给出代码证据。**

## 一、代码证据

### 唯一的 XML 代码：只构造，不解析

`src/application/export/service.py` L692–L708：

```python
def _comic_info_xml(request: ExportRequest) -> str:
    import xml.etree.ElementTree as ET

    book = request.book_metadata or {}
    chapter = request.chapter_metadata or {}
    root = ET.Element("ComicInfo")                    # 构造
    for key, value in (...):
        if value:
            ET.SubElement(root, key).text = str(value)  # 构造
    pages = ET.SubElement(root, "Pages")              # 构造
    for index, _page in enumerate(request.pages):
        ET.SubElement(pages, "Page", Image=str(index), Type="Story")
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(root, encoding="unicode")
                                                       # 序列化，仍不解析
```

**用到的 API**：`ET.Element`、`ET.SubElement`、`ET.tostring` —— **全部是构造/序列化。**

### 解析 API 零命中

**在 `src/**` 全文搜索**：

```
ET.parse | ET.fromstring | ET.XML( | parse(...xml
```

**结果：零命中。**

### 出口也确认了这一点

`archive.writestr("ComicInfo.xml", _comic_info_xml(request).encode("utf-8"))`
（同一文件 L466）

**`writestr` 是写，不是读。**

**测试那边**（`test_p16_reader_export.py` L578）：

```python
assert b"<Series>Test Manga</Series>" in archive.read("ComicInfo.xml")
```

**这是测试在读自己刚写的字节，不是产品在读外部 XML。**

## 二、结论：`SEC-FMT-002` 当前 `NOT_APPLICABLE`

**`SEC-FMT-002` 的攻击面是**：

> 包含畸形超深嵌套实体的 XML 描述文件（Billion Laughs / XXE 攻击）

**而本项目的 XML 相关操作**：

| 操作 | 方向 | 是否受 XXE 影响 |
|---|---|---|
| 生成 `ComicInfo.xml` | **写** | **否**——写不会被实体扩展攻击 |
| 读取 `ComicInfo.xml` | **不存在** | **不适用** |

**所以：本项目当前没有可被 `SEC-FMT-002` 攻击的代码路径。**

**判定：`NOT_APPLICABLE`**，理由是**代码证据**（不是「没听说过」）。

## 三、但这个 `NOT_APPLICABLE` 有明确的有效期

**它不是永久的。**

**`ComicInfo.xml` 是 CBZ 的标准元数据文件。若将来要实现「导入 CBZ 时读取原有元数据」，
就会引入解析路径，而那时 `SEC-FMT-002` 立即适用。**

**所以本文件不是「这一项可以永久跳过」，而是「在当前代码状态下不适用」。**

**这一条必须写进 `SEC-FMT-IMPL-1` 的 AC2 判定里**，否则将来加了解析路径，
不会有人回头找这个 `NOT_APPLICABLE` 来推翻它。

## 四、对它三项的影响

**R1 的答案顺带确认了另外三项确实**有**对象**：

| ID | 是否有代码路径 | 依据 |
|---|---|---|
| `SEC-FMT-001` Zip Slip | **是** | `import zipfile` 在 `src/application/export/service.py` L32；CBZ/ZIP 是导出格式 |
| **`SEC-FMT-002` XXE** | **否** | 本文件 §一 |
| `SEC-FMT-003` 魔数嗅探 | **是** | `core.detect` 有 Pillow 白名单（detect 面）；**导入面待确认** |
| `SEC-FMT-004` 长路径 | **是** | 文件系统路径操作存在 |

**所以 `SEC-FMT-IMPL-1` 的范围从 4 项变成 3 项 + 1 项 `NOT_APPLICABLE`。**

## 五、一个必须提出的问题：这是不是「用不适用来缩小范围」

**我意识到这个文件可能被读成「找到了一个跳过的理由」。**

**所以要说清楚**：

- **这不是我选的攻击面**——`SEC-FMT-002` 针对的是 XML 解析
- **项目里确实没有 XML 解析**——这是查出来的，不是解释出来的
- **证据是可复算的**：搜索 `ET.parse`，任何人都会得到零命中
- **而且我记录了它的有效期**（§三）

**如果将来有人加了 XML 解析，这个 `NOT_APPLICABLE` 就是错的，而本文件写明了它会在那时变错。**

## 七、全仓搜索的结果：我的结论需要修正

**上一版只搜了 `src/**`，我指出了这个缺口并补上。结果改变了判定。**

### 7.1 产品代码（`src/`）：确实只写不读

**零命中确认。** `src/application/export/service.py` 只有 `ET.Element` / `SubElement` / `tostring`。

### 7.2 但全仓有 XML 解析，并且在 `test_assets/`

`test_assets/comic_golden_suite/tools/assets.py` 有 **4 处 `ET.fromstring`**。

**而它已经实现了 `SEC-FMT-002` 要求的防御**——四处都是同一模式：

```python
if b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
    return False, "DTD/entity declarations are not accepted"
root = ET.fromstring(xml)
```

**即：先拒绝含 DTD/实体声明的 XML，再交给解析器。**

**四处位置**：L394（`public_xml_valid`）、L512（annotation 校验）、
L735（archive annotation）、L783（archive member）。

**而且每一处都有大小上限**（`MAX_PUBLIC_XML_BYTES`、`MAX_ANNOTATION_BYTES`），
**L731/L507 还先看文件大小再读**，防的是「先读进内存再判断」这条路径。

### 7.3 判定修正

| 范围 | 解析 XML？ | `SEC-FMT-002` 防御 |
|---|---|---|
| **`src/`（产品代码）** | **否** | 不适用 |
| **`test_assets/.../assets.py`** | **是** | **已实现**（DTD/ENTITY 拒绝 + 大小上限）|
| `experiments/M2-TA3-B/extract_svg_gt.py` | 是 | **未实现**（但这是实验脚本，不在交付路径）|
| `.agents/worktrees/**` | 是 | **按定义就是各 worktree 的副本，不重复计入** |

**所以 `SEC-FMT-002` 的正确判定不是 `NOT_APPLICABLE`，而是：**

| 对象 | 判定 |
|---|---|
| `src/` 产品路径 | `NOT_APPLICABLE`（无解析）|
| `test_assets/` 校验工具 | **`MET`（已实现，需补测试证明它真的挡住）** |
| `experiments/` | `NOT_APPLICABLE`（不在交付路径）|

**上一版只写「不适用」是不完整的**——它漏掉了已实现的那一半。

### 7.4 因此 AC2 的实际工作变成了「证明」而不是「实现」

**`assets.py` 的防御**：

- ✅ 拒绝 `<!DOCTYPE`（挡 XXE 的外部实体声明）
- ✅ 拒绝 `<!ENTITY`（挡 Billion Laughs 的实体定义）
- ✅ 有大小上限（挡「先读爆内存」）
- ❓ **但没有测试证明这些守卫真的被走到**

**所以 AC2 从「实现防御」改为「验证已有的防御」**：

1. 构造含 `<!DOCTYPE ... SYSTEM "http://...">` 的 XML，断言被拒
2. 构造 Billion Laughs（嵌套 `<!ENTITY>`）的 XML，断言被拒
3. 构造超过 `MAX_ANNOTATION_BYTES` 的 XML，断言被拒
4. **对照组**：合法的 `ComicInfo.xml` 仍能被解析（否则「拒绝一切」也能过前三条）

**这比原先估计的工作量小，但性质不同——它是「证明已有防线有效」，不是「从零建防线」。**

## 八、这个发现改变了什么

**我原本准备把 `SEC-FMT-002` 记为 `NOT_APPLICABLE` 并写一段「它有有效期」。**

**那个说法在 `src/` 范围内是对的，但它掩盖了一个事实：项目里已经有人实现过这个防御。**

**如果我只搜 `src/`，我会得出「不需要做」；**
**搜了全仓，我得出「已经做了，需要证明它有效」。**

**后者才是真实状态。**

**而差别的来源只是一条命令的搜索范围。**

## 九、明确未做

- **未修改 `SEC-FMT-IMPL-1` 的 AC2 判定**——本文件是证据。
- **未证明 `assets.py` 的守卫真的被走到**（AC2 的工作）。
- **未检查 `experiments/` 是否在交付路径**（假设不在，但未核实）。
- **未检查 TS/React 侧是否解析 XML**——`DOMParser` 等模式已搜索，零命中。
