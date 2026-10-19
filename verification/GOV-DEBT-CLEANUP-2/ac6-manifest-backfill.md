# AC6 — 七个 DONE Task 的 Manifest 事实补录

**Task**: GOV-DEBT-CLEANUP-2 · **AC**: AC6 · **性质**: 补表 + 一处 frontmatter 更正

**事实来源**: `verification/P09-GOVERNANCE-DEBT-20261019/missing-manifest-resource-facts.md`（实测）。

## 结果概览

| Task | 处理 | 治理效果 |
|---|---|---|
| `FEAT-CREATE-1` | 新增 Resource Manifest 表（4 行） | 错误 2 → **1** |
| `FEAT-CREATE-2` | 新增表（4 行）+ **frontmatter `worktree: null` 更正为实测路径** | 错误 2 → **1** |
| `FEAT-CREATE-3` | 新增表（4 行） | 错误 2 → **1** |
| `FEAT-CREATE-4` | 新增表（4 行） | 错误 2 → **1** |
| `FEAT-IMPORT-MULTI-1` | 新增表（4 行） | 错误 5 → **4** |
| `P19-UI-FIX-2` | 新增表（4 行） | 错误 2 → **1** |
| `P19-UI-FIX-1` | **保留原状，未表格化** | 仍为 4（见下） |

## `FEAT-CREATE-2` 的 frontmatter 更正

原值 `worktree: null` 与实测矛盾——`New.Manga.workspace/worktrees/FEAT-CREATE-2` 真实存在且已在 Git 注册。
已更正为：

```
worktree: G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-2
```

这是 AC6 明确要求的更正。本 Task 未改动该 worktree 的任何内容。

## `P19-UI-FIX-1` 为何保留原状（重要取舍）

该 Task **本来就有**一份由 Codex 于 2026-10-17 生成的
`verification/P19-UI-FIX-1/resource-manifest.json`（4027 字节，7 个资源项 + closeout 计数），
其 Task 正文的 `## Resource Manifest` 节以散文形式引用它。检查器只认表格，所以报「必须逐项填写」。

我尝试过把它转成表格，实测结果：**Manifest 错误消除，但新增 4 个「Resource 最终路径未验证」错误**
（错误数 4 → 8）。原因核实如下：

| 原始 destination 表述 | 实际情况 |
|---|---|
| `apps/desktop/src-tauri/target/{core-sidecar,debug/resources,debug/m2rc1-desktop.exe}` | 花括号简写，非可解析路径（父目录存在） |
| `%APPDATA%/com.newmanga.m2rc1.desktop/{catalog,data,derived}` | 环境变量 + 花括号简写（目录存在） |
| `apps/desktop/src-tauri/target/p19-ui-fix-1-isolation-20261017` | **实际不存在** |
| `C:/Users/49745/AppData/Local/pyinstaller` | **实际不存在**（JSON 自述该 cache 已被清除重建） |
| `G:/CODEX/New Manga/verification/P19/{d-run-v2,import-no-response-r4.md}` | 花括号简写（两者都存在） |

**结论**：这些是原始记录的真实表述。为了迁就检查器而把它们改写成「能通过校验的路径」，
会篡改一份由他人（Codex）出具、且内容准确的资源清单——尤其两个路径确实已不存在，
强行填一个存在的路径等于伪造资源状态。因此我回退了这次改造，保留原始散文 + JSON。

**这不是「放弃修复」，而是记录了一条明确的债务**：该 Task 的清单格式与检查器不兼容，
且转换会引入更多错误。格式转换的授权与判据应由 Codex 裁定。

## 诚实边界

- 新增的 6 张表里，`sha256/manifest` 列填的是**该 Task 文件自身的 sha256**（真实的 64-hex 可复核值），
  不是资源的完整性证明。资源本身的状态记录在 `reference/process check` 列。
- `PRESERVE_UNKNOWN` 是保守标注，不表示已确认可清理。
- 本 Task 未删除、移动、归档任何资源，未改动任何 worktree 内容。
- `P19-UI-FIX-1` 的治理错误仍为 4，属已知且已说明的债务。
