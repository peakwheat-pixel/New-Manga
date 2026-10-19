# AC1 核验结果：r25 的核心假设不成立

**产出**: 2026-10-20 · **执行**: AC1 第 2 步（r26 §3.3 强制，**改 checker 之前**）

## 一、结论先行

**r25 §1 的核心假设是错的。**

> `Canonical Evidence` pin 是 `(path, commit, sha256)` 三元组；历史证据应以该 commit 中
> 该路径的 **Git blob** 为准。当前 `check.ps1` 对**工作区文件**计算 hash 并与 pin 比较，
> **忽略了 pin 的 `commit` 字段**。

**「忽略 commit 字段」这句是对的。但由此推出的「所以 pin 应该是 blob hash」不成立。**

实测：19 个 pin-only Task 的 **300 个 pin** 中——

| 分类 | 数量 | 含义 |
|---|---:|---|
| **`PIN_MATCHES_WORKTREE_NOT_BLOB`** | **187** | **pin 是按工作区字节算的**（当时工作区 CRLF，blob LF） |
| **`CONTENT_DIFFERS`** | **40** | pin 既不匹配工作区也不匹配 blob |
| `LINE_ENDING_ONLY` | 2 | 内容相同，仅行尾 |
| `PIN_VALID` | 71 | pin 与 blob 相符 |

**若按 r25 的裁定改成 blob 校验：**

> **会制造 187 个新失败，而不是修复 19 个。**

## 二、为什么 r26 的顺序救了这件事

我原本倾向的顺序是「先改 checker，再看哪 19 个转绿」。r26 否决了：

> 「改后看哪些变绿再解释」顺序**不接受**。
> 19 个 pin-only Task **必须先做基线 blob 核验，再改 checker**。

**如果按我的顺序：**

1. 改 checker 验 blob →
2. **187 个当前通过的 pin 突然变红** →
3. 我会看到「修完之后失败变多了」，然后**开始解释**（「这些是历史 pin，需要再补」）→
4. **把一个错误的设计包装成「已知代价」**

**r26 的顺序让我在动手前就知道这个设计是错的。**

## 三、187 个「工作区 pin」是怎么产生的

`core.autocrlf=true` 让工作区是 CRLF、Git blob 是 LF。

**若 Owner 在提交后用工作区文件算 hash**，得到的就是 CRLF 字节的 hash——
而 blob 是 LF 字节。**两者不同，但都不是错。**

**实测印证**：这 187 个 pin 中，`pin == sha256(当前工作区文件)`，且工作区内容与 blob
**正文完全相同**（仅行尾不同）。

**所以这 187 个 pin 既不是「blob 正确」也不是「损坏」，而是「按工作区算的」。**

## 四、40 个 `CONTENT_DIFFERS` 才是真问题

这 40 个 pin **既不匹配工作区、也不匹配 blob**。示例：

| Task | evidence_id | 路径 |
|---|---|---|
| `ENV-BUNDLE-1` | `S04` | `apps/desktop/src-tauri/src/main.rs` |
| `ENV-BUNDLE-1` | `S05` | `apps/desktop/src-tauri/src/library_bridge.rs` |
| `HOST-CORE-1` | `HOSTCORE-C1-PIN` | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` |
| `SEC-FIX-PATH-ECHO-1` | — | `src/bootstrap/core_service.py` |

**这些才是当前 FAIL 的来源**（19 个 Task 当前的 FAIL 行数与这 40 个的分布一致）。

**它们可能的原因**：
- pin 是在另一个分支/worktree 上按当时的文件算的，而该文件在那个 commit 中不同
- pin 是手写/抄录错误
- 该 commit 中文件确实与 pin 声称的不同

**需要逐项诊断，不能一概而论。**

## 五、这对 `GOV-PIN-LINEAGE-1` 意味着什么

**r25/r26 授权的方案是「改 checker 验 blob」。按实测，这个方案会让 187 个 pin 变红。**

所以：

| 原定方案 | 实测结果 |
|---|---|
| 修 1 处 checker → 19 个 Task 转绿 | **→ 187 个新 FAIL，19 个不会转绿** |

**本 Task 不能按原方案实施。**

## 六、我看到的三条可能出路（交 Codex 裁定）

### 出路 A：把 pin 语义**显式化**，而不是改变默认

不猜「pin 应该是什么」，而是让 Task **声明**它用的是哪种 pin：

- `sha256_basis: blob` —— pin 是 commit 中 blob 的 hash
- `sha256_basis: worktree` —— pin 是提交时工作区字节的 hash（187 个属于这类）

检查器按声明的 basis 校验。**未声明时按现状（工作区）校验**，不改变任何现有绿灯。

**优点**：不产生新失败，语义清楚，可渐进迁移。
**缺点**：要给 187 个 pin 补声明（或给整个 Task 补一处 frontmatter 声明）。

### 出路 B：双向校验，只报「两者都不符」

检查器同时算 blob hash 与工作区 hash：

- 匹配任一 → **PASS**
- 两者都不匹配 → **FAIL**（这 40 个）

**优点**：改动最小，不产生新失败，且能抓出真问题（40 个）。
**缺点**：无法区分「按工作区算的历史 pin」与「按 blob 算的历史 pin」，
语义仍然模糊。**但这恰恰与现状一致——现状本来就是模糊的。**

### 出路 C：先诊断 40 个，再定方案

40 个 `CONTENT_DIFFERS` 是唯一确定的故障。
**先查清它们，再决定 pin 语义该怎么定。**

**我倾向 C 然后 B**：先弄清真问题，再用最小改动抓它。

## 七、明确未做

- **未修改 `tools/governance/check.ps1`。** r26 的强制顺序要求核验在前，核验发现了问题，
  因此没有进入第 4 步。
- 未修改任何 Task 文件、Plan、STATUS。
- 未重算或覆盖任何 pin。

## 八、产物

| 文件 | 内容 |
|---|---|
| `ac1-pin-only-verification.json` | 300 个 pin 的逐项核验（commit 可解析性、路径存在性、blob SHA） |
| `ac1-mismatch-diagnosis.json` | 229 个不符 pin 的逐项诊断（分类、blob/工作区/disk 三个 hash） |
| 本文件 | 结论与出路 |

**这两个 JSON 就是 r26 要求的「逐条输入键、原 SHA、commit、path、blob SHA」明细。**
