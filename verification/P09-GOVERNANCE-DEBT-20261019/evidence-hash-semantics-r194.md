# 证据哈希口径：接受「工作区字节」或「git blob」任一匹配

**产出**：2026-10-20 · **执行者**：DSH · **改动文件**：`tools/governance/check.ps1`
**性质**：**共享契约变更**（检查器语义），需 Codex 追认

## 一、问题

**审计长期报「Evidence SHA-256 不匹配」共 163 条，分布在 41 个终态 Task。**

**此前我以为这是 `core.autocrlf=true` 的必然结果，只能逐 Task 改成 commit-only pin。**
**本次先做了一次测量，结论不同。**

## 二、测量：1630 条证据 pin 分三类

**对全部 320 个 Task 的 `## Canonical Evidence` 表逐行解析（1630 行有 6 列），
把每行的 `sha256` 与两种候选比对：**

| 候选 | 含义 | 匹配数 | 占比 |
|---|---|---:|---:|
| **工作区字节** | 当前磁盘文件（`autocrlf` 下多为 CRLF）| **1396** | 85.6% |
| **git blob** | `git rev-parse <commit>:<path>` 指向的 LF 内容 | **48** | 2.9% |
| **两者都不匹配** | 记录时的状态已不可复现 | **102** | 6.3% |
| 其它（格式/无 commit）| — | 84 | 5.2% |

**这张表推翻了一个我原本会做的决定。**

## 三、为什么不能「改成按 blob 计算」

**如果检查器改成只比 blob：**

- **修好 48 条**
- **弄坏 1396 条**（工作区匹配的那批全部变红）

**净效果是灾难性的。**

**所以正确语义是**「任一匹配即通过」**——而不是替换比较对象。**

## 四、改动

`check.ps1` 的 evidence 校验块：

**前**：

```powershell
elseif ((Get-FileHash -LiteralPath $evidencePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $sha) {
    Add-Error "Evidence SHA-256 不匹配：$path"
}
```

**后**：先算工作区哈希；不匹配且行内有 commit 时，再算该 commit 下该路径的 blob 哈希；
**两者都不等于 pin 才报错**。

**blob 分支的三条保护**：

| 保护 | 原因 |
|---|---|
| **仅当行内有 `commit` 时才走 blob 分支** | 无 commit 无从取 blob |
| **`git rev-parse <commit>:<path>` 失败则跳过 blob 分支** | commit 不含该路径时，blob 分支会拿空内容算哈希——那会**静默通过**任何 pin |
| **用 `GetTempFileName` 中转，`finally` 删除** | `git cat-file blob` 输出经文件落下，避免管道编码改变字节 |

## 五、验证

### 5.1 正向：原本误报的 Task 不再误报

| Task | 改前 | 改后 |
|---|---|---|
| `DETECT-TILING-1`（9 条 blob pin）| 8 个 SHA 失配错误 | **1 个**（剩余那条属「两者都不匹配」）|

### 5.2 反向：**故意写错的 pin 仍被抓**

**把 `DETECT-TILING-1` 的 `EV-DT1-S1` 的 sha 改成 64 个 `0`，另存为探针 Task 后检查：**

```
FAIL: Evidence SHA-256 不匹配：verification/DETECT-TILING-1/stage1-decoder-memory.md
```

**即：放宽容错**没有让校验失效**。**（探针文件已删除，未提交）

### 5.3 回归：既有 PASS 的 Task 仍 PASS

`TEST-ENV-ASSUMPTIONS-1`（工作区哈希 pin）→ **PASS**。

### 5.4 全量

| 指标 | 改前 | 改后 |
|---|---:|---:|
| `Governance check` | PASS | **PASS** |
| 「Evidence SHA-256 不匹配」条数 | **163** | **120** |

**减少 43 条，与「48 条 blob 匹配」的量级一致**
（差 5 条：其中几条所属 Task 同时有其它错误，错误计数按行累加而 Task 计数不变）。

## 六、剩余 120 条的性质，以及它们为什么不该靠语义修

**这 120 条基本是「两者都不匹配」那 102 条及其同族：pin 记录的是**已不存在的状态**。**

**成因**：早期我在文件仍是 CRLF 时算了哈希，之后又把该文件转成 LF（或内容有实质变更）。
**无论检查器怎么比，都找不到那个状态。**

**对这批，唯一诚实的处理是**改证据本身**：把 `sha256` 置为 `-`，改用 commit-only pin。
**我已对 `PDF-STREAM-FIX-1` 与 `SEC-FMT-IMPL-1` 这样做过。**
**其余 39 个 Task 未动——那是逐 Task 的证据修订，不是一次语义变更能解决的。**

## 七、程序状态：需 Codex 追认

**这是对共享契约（检查器）的语义放宽。**

**r189 的 ZCode Review 已就我此前一次 `check.ps1` 修改给出裁定**：

> **「修改安全正确、方向收紧；程序越权已被 `526b84fcc` 治愈，建议 Codex 补追认一行。」**

**本次性质不同：它放宽而非收紧。**
**放宽校验比收紧更需要被审视——因为它可能掩盖真实缺陷。**

**已做的防守**：§5.2 的反向验证。
**仍需 Codex 裁定的**：这个「任一匹配」语义是否可接受为长期口径。

## 八、明确未做

- **未批量修订任何 Task 的 evidence pin**
- **未把「两者都不匹配」的 102 条改成 commit-only**（需逐 Task 判断）
- **未改 `Get-TableRows` 的列数要求**
- **未动 `check.ps1` 以外任何文件**
