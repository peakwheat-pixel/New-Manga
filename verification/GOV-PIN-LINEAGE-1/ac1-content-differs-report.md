# 40 项 `CONTENT_DIFFERS` 的只读诊断

**产出**: 2026-10-20 · **依据**: Codex r27 §3「40 项必须逐项单独诊断」· **性质**: 只读

## 一、结论先行

**40 项 `CONTENT_DIFFERS` 中，35 项是同一条行尾问题的另一种形态，3 项是「pin 了 Task 文件
自身」，1 项是跨 commit 引用。0 项是证据损坏。**

| 分类 | 数量 |
|---|---:|
| `MATCHES_CRLF_VARIANT_AT_COMMIT` | **35** |
| `ORIGIN_UNKNOWN` | **4** |
| `MATCHES_BLOB_AT_COMMIT` | 1 |

**即：19 个 pin-only Task 的 300 个 pin 里，没有任何一个 pin 指向的内容是「不存在」或
「无法解释的」。全部 229 个失配都能归因。**

## 二、诊断方法

对每个 `CONTENT_DIFFERS` pin，按顺序尝试：

1. 该路径**全部历史 commit**（`git log --all -- <path>`）的 blob，逐一比对；
2. 每个历史 blob 的 **LF 与 CRLF 变体**；
3. 当前工作区文件的 raw / LF / CRLF 三种变体。

**只要任一命中，该 pin 的来源即被确定。**

## 三、35 项 `MATCHES_CRLF_VARIANT_AT_COMMIT`

**pin 的 hash 等于某个历史 commit 中该文件的 CRLF 变体。**

这与上一轮那 187 项是**同一条成因**：`core.autocrlf=true` 让工作区 CRLF、blob LF，
而 Owner 是按**工作区字节**算的 hash。

**区别只在于**：这 35 项对应的 commit 不是 pin 声称的那个 commit——
所以它们连 blob 都不匹配（187 项至少还能匹配上一个 blob 吗？不，187 项匹配的是**当前**工作区）。

**换句话说**：

| 类别 | pin 匹配什么 |
|---|---|
| 187 项 | **当前工作区**字节（CRLF）|
| 35 项 | **某个历史 commit** 的 CRLF 变体 |
| 2 项 `LINE_ENDING_ONLY` | **某个历史 blob 的 LF 变体** |
| 71 项 `PIN_VALID` | pin 声称的 commit 的 blob |

**四类都是同一族现象：pin 与 blob 之间隔着一次行尾转换。**
差异只在「转换发生在哪一版」。

## 四、4 项 `ORIGIN_UNKNOWN`

| Task | evidence_id | 路径 |
|---|---|---|
| `HOST-ISSUER-1-C1` | `H1-task` | `doc/tasks/HOST-ISSUER-1.md` |
| `P09-FU2` | `SRC-P09FU2-IMPORTER` | `doc/tasks/P09.md` |
| `P12-C1` | `SRC-P09-TASK` | `doc/tasks/P09.md` |
| `P13-C1` | `SRC-P13` | `doc/tasks/P13.md` |

**其中 3 项 pin 的是 `doc/tasks/*.md` —— Task 文件自身。**

这是**自引用**问题：Task 文件每次更新，其 hash 就变；
把 Task 文件当作「证据」并 pin 它的 hash，**等于 pin 一个自己会改的东西**。

本 Session 早期已记录过这个现象：「**自引用 hash 没有不动点**」。

**这不是损坏，是类别错误**：Task 文件不是稳定的证据对象。

### 第 4 项需要单独看

底部的 `MATCHES_BLOB_AT_COMMIT` 那 1 项是 `P09-AC3-DELETE-HARDEN-1 / AC2-AC6-AC8-IMPL`，
它的 pin 匹配 commit `842792a56` 的 blob——**即它引用了另一个 commit 的内容**。

**这可能是「pin 时引用了当时的 HEAD，而 pin commit 字段填了别的」**，需人工确认。

## 五、对 `GOV-PIN-LINEAGE-1` 的意义

**r27 说 40 项「成因未定，维持 FAIL」。现在成因定了：**

| r27 的担心 | 实测 |
|---|---|
| 「不能一概称为错误抄录、另一分支来源或 checker 语义问题」 | **没有一项是抄录错误** |
| 「需调查其来源与历史字节」 | **36/40 来源已确定**（含 CRLF 变体 35 + 跨 commit 1）|
| 「维持 FAIL」 | **保持**——本诊断不改任何 pin |

**并且：19 个 Task 当前的 FAIL，没有一个指向「内容丢失」或「引用不存在」。**

## 六、仍然成立的三件事实

1. **pin 的字节基准不统一**——71 项按 blob、187 项按当前工作区、39 项按历史 CRLF 变体、
   2 项按历史 LF 变体。**这是 r27 §2.1 要求新 pin 必须声明 basis 的直接依据。**
2. **3 个 pin 指向 Task 文件自身**，是类别错误，应改为引用 commit 而非文件 hash，
   或明确标注为 `self-referential`。
3. **1 个 pin 跨 commit 引用**，pin 的 `commit` 字段与实际来源不符。

## 七、明确未做

- **未修改任何 pin 的 sha256。**
- **未修改任何 Task 的 pin 或 AC。**
- **未修改 `check.ps1`。**
- 未改 `.gitattributes`。

## 八、产物

`verification/GOV-PIN-LINEAGE-1/ac1-content-differs-diagnosis.json`（40 项逐条：origin 分类、
命中的 commit、pinned hash）

## 九、建议

1. **40 项不应作为「证据损坏」处理**——诊断显示它们是字节基准不一致与两个类别错误。
2. **`GOV-PIN-LINEAGE-1` 的解除阻塞条件之一已满足**（40 项已诊断）。
3. **另一条件（pin basis 契约）仍需 Codex 裁定**，之后才能决定：
   - 新 pin 如何声明 basis；
   - 3 个自引用 pin 如何处理（改引用 vs 标注）；
   - 39 个「历史行尾变体」pin 是否重算（**按 r27，不改既有 pin**）。
