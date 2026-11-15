# CAPTURE-VAR-OVERWRITE-INCIDENT-1：**我覆盖了既有证据，已回退**（事故登记）

基线 `34a01cefc`。

## 1. 我做了什么

按上一轮自己提的计划"扫一遍剩余的 capture 变量"，我执行了：

```powershell
$env:NEWMANGA_CAPTURE_RESIDUAL3_PNGS="1"
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj `
  --filter "FullyQualifiedName~FluentResidual3VisualEvidenceTests"
```

测试通过（1 passed / 0 failed / 0 skipped / 2 s），**但 `git status` 显示**：

```
M verification/FEA-06-RESIDUAL-3/visuals/05-workbench-batch-matrix.png
M verification/FEA-06-RESIDUAL-3/visuals/07-reader-single.png
M verification/FEA-06-RESIDUAL-3/visuals/08-reader-double.png
M verification/FEA-06-RESIDUAL-3/visuals/09-reader-webtoon.png
M verification/FEA-06-RESIDUAL-3/visuals/inventory.md
```

**⇒ 我覆盖了 `FEA-06-RESIDUAL-3` 的 5 个既有证据文件（4 张 PNG + 1 个 inventory.md）。**

## 2. 已回退

```powershell
git checkout -- verification/FEA-06-RESIDUAL-3
```

**回退后验证**：
- `git status --short` → **无输出**
- `git status --short verification/FEA-06-RESIDUAL-3` → **无输出**
- `git diff --stat HEAD -- verification/FEA-06-RESIDUAL-3` → **无输出**

**⇒ 既有证据已恢复到 HEAD 的原字节，零残留。**

## 3. 为什么会发生

`FluentResidual3VisualEvidenceTests:95` 的注释其实写得很清楚：

> `NEWMANGA_CAPTURE_RESIDUAL3_PNGS=1` 才写 9 张图 + inventory 到**本卡证据目录**

**"本卡证据目录"** —— 那个"本卡"是 **`FEA-06-RESIDUAL-3`**，不是我的。

**我读到了这句话，但没有把它当回事。** 我把它理解成"它会写到某个目录"，
而没有问"**那个目录里有东西吗？我会覆盖吗？**"

## 4. ★ 这是同一个错误的第 14 次

| # | 错误 | 类型 |
|---|---|---|
| 3 | 只搜 `git grep`，漏 gitignore | **搜索范围不完整** |
| 7 | 只搜 `*.axaml`，漏 C# 构建 UI | **搜索范围不完整** |
| 11 | 说"做尽"但没 grep 现成能力 | **搜索范围不完整** |
| 12 | 计划写新测试，其实一条 env 变量就够 | **搜索范围不完整** |
| **13** | **写到 `FEA-06-RESIDUAL-1/png/` 后才发现该先查** | **先做后验** |
| **14** | **跑 capture 变量前没查写盘目标，覆盖了既有证据** | **先做后验** |

**⇒ 13 与 14 是同一天、连续两轮的同一个错误。**
**上一轮我刚写完"写入别人的目录前应先确认那里有什么"，下一轮就违反了它。**

## 5. 我原本应该怎么做

**跑任何 `NEWMANGA_CAPTURE_*` 之前**：

1. 读该测试的写盘路径（`FluentResidual3VisualEvidenceTests:95` 附近有 `output` 变量）；
2. `git status` + `ls` 该目录，确认**是否有未提交改动 / 是否受版本控制**；
3. 若受版本控制且已有内容 ⇒ **先确认能否安全重写**，或**改用临时目录**；
4. 跑完立刻 `git status`，**先看有没有意外改动，再看产出**。

**我这次是第 4 步才做，而且是在测试通过、以为一切正常之后。**

## 6. 影响评估

| 项 | 影响 |
|---|---|
| 既有证据字节 | **已恢复，零影响** |
| 证据 pin（sha256） | 未变（工作树与 HEAD 一致） |
| 门禁 | 未变（回退后跑过 check/pins/inventory） |
| `FEA-06-RESIDUAL-3` 卡片结论 | 不受影响（它的 PNG 内容被临时改过又恢复） |

**⇒ 实质零损害。但过程违规，必须登记。**
