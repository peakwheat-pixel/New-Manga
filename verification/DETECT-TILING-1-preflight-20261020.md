# 释放前复核：`DETECT-TILING-1` **不能立即释放**（样本缺失）

**产出**: 2026-10-20 · **性质**: 释放前 Gate 核对 · **结论**: **AC4 的前提不成立**

## 一、r34 要求的两项释放前复核

r34 §「释放前 Gate」要求：

> 释放前先复核 dirty 工作区基线，并确认**真实页样本可用**及解码内存策略可行。

**本轮逐项核对结果：一项通过，一项失败。**

| 复核项 | 结果 |
|---|---|
| dirty 工作区基线 | **已复核**（1237 项，绝大多数是他人未提交内容与 `.orchestrator/` 等；本轮只写了自己声明的文件）|
| **真实页样本可用** | **不使用** —— **样本已丢失** |
| 解码内存策略可行 | 未验证（依赖样本）|

## 二、样本确实丢失了

### 2.1 记录里有什么

`verification/P18/raw/ja/probe-summary.json` 记录了两个关键事实：

```json
"path": "G:\\CODEX\\New Manga.workspace\\test-materials\\objects\\sha256\\9b\\9bbd38763fde...",
"sha256": "9bbd38763fde3a45e0dc3af61647ee8097f1345653dce99c32759a58c6c499e1",
"width": 2946,
"height": 4167
```

和失败信息：

```
core.detect page exceeds the pixel limit (2946x4167 = 12275982 px > 11184810 px)
```

### 2.2 那个路径现在不存在

```
=== sample exists: False
  NOT FOUND - the real page sample is gone
```

**实测 `Test-Path` 返回 False。**

### 2.3 磁盘上也没有替代

`verification/P18/raw/**` 里只有：

- `probe-summary.json`、`request-sequence.json`、`sidecar-*.log`
- `data/library.db`（311 KB）、`data/catalog/catalog.sqlite`（24 KB）

**没有任何 `.png` / `.jpg` / `.jpeg`。**

**所以那张 2946×4167 的真实页，连同它所在的 content-addressed store，
在 `New Manga.workspace\test-materials\` 下已经不存在了。**

## 三、这对 `DETECT-TILING-1` 意味着什么

### AC4 的前提不成立

```
- [ ] AC4：用被拒的那一页（2946×4167 = 12,275,982 px）实测通过…
      同时用一张正常页做对照…
```

**这一页没有了。**

**而 AC4（原始 `ARCH-DOC-REBASELINE` AC4）明确要求「不重新获取 Manga109」**
——那是素材许可约束，不是可以绕过的。

**所以 AC4 目前有两种可能的改法**（需 Codex 裁定，不由交付方定）：

| 改法 | 说明 | 代价 |
|---|---|---|
| **A. 用等价合成页替代** | 生成一张同样尺寸（2946×4167）的合成图（纯色/噪声/平铺文字），只验证**像素与内存行为**，不验证检测质量 | **诚实但有边界**：能证明分块与内存有界，**不能证明真实漫画页的检测质量** |
| **B. 立一个新的素材 Task** | 寻找已许可的等价高分辨率页 | 成本高，且可能违反「不重新获取」的既有裁决 |
| **C. 降低 AC4** | 只要求「超限页被正确拒绝或分块」，不要求真实页 | **最省但最弱** |

**我倾向 A**，因为 `DETECT-TILING-1` 的技术目标（有界解码 + 分块坐标 + 边界去重）
**与图像内容无关**——它只需要「一张超限的合法 PNG/JPEG」。

**但「真实漫画页的检测质量」这件事会被留在 P18 那边，仍需真实素材。**

### 这个发现同时解释了 P18 的一个旧问题

**P18 AC5 一直 BLOCKED，而它的阻塞清单里没写「样本丢失」。**

**现在多了一条**：即使 `core.detect` 的分块做完了，
**P18 的端到端实验切片也需要真实 JA/KO 素材**，而那些素材同样在
`test-materials` 里，**同样可能已丢失。**

**这一条值得单独核实**——但本轮没做。

## 四、因此本轮不释放 Task

**r34 的释放 Gate 有一条没过。**

**所以 `DETECT-TILING-1` 保持 `status: proposed`。**

**我没有：**
- 改 `status` 为 `ready`
- 分配 Owner
- 派发实施

## 五、建议的下一步（按推荐自行裁决）

1. **先核实 `test-materials` 的整体状态**：还有哪些 P18/P19 依赖的素材仍在？
   这不是 `DETECT-TILING-1` 的事，但**它决定了很多其它 Task 的可行性**。
2. **若 `test-materials` 大面积缺失**，应立一个「素材盘点」Task，
   而不是让每个 Task 各自发现自己的样本没了。
3. **`DETECT-TILING-1` 的 AC4 改为合成页**（方案 A），把「真实漫画页质量」明确留在 P18。

## 六、明确未做

- 未修改 `DETECT-TILING-1.md`（它是刚登记的 proposed，等裁定后再改）。
- 未重新获取任何素材（受 AC4 约束）。
- 未释放、未派发。
