# AC1 / AC2 — 引用格式修复，以及它暴露出的既有债务

**Task**: P19-UI-MANIFEST-VIEW-1 · **性质**: 单节文本修正 + 意外发现

## 结论摘要

- **AC1 达成**：`P19-UI-FIX-1` 的 Resource Manifest 引用改为检查器可解析的仓库相对路径；
  原错误 `Resource Manifest 引用必须位于 verification/**：resource-manifest.json` **消失**。
- **但净错误数变差：4 → 10。** 引用可解析后，检查器开始读取那份 JSON，于是暴露出
  **6 个此前不可见的 destination 债务**。
- **源 JSON 未被修改**：sha256 改前改后均为
  `b0772d93ab8ed9182497a43e0761f0d4ccc5560768f806ba86eb8048905c4dc2`。

## 改了什么

只改 `doc/tasks/P19-UI-FIX-1.md` 的 `## Resource Manifest` 节开头一句：

```diff
- 见 [`resource-manifest.json`](../../verification/P19-UI-FIX-1/resource-manifest.json)。worktree、构建产物、...
+ 外部清单：`verification/P19-UI-FIX-1/resource-manifest.json`。worktree、构建产物、...
```

原散文的**处置事实逐字保留**：worktree / 构建产物 / 隔离数据 / 源数据均保留、删除 0 项、
6 个旧运行日志仅在证据目录内改名以防覆盖、`build_sidecar.ps1 -Force` 清理的 PyInstaller 缓存已在资源清单与 Handoff 登记。
节字节数 353 → 332（只减了链接语法与措辞）。

## 改后的完整错误清单

改前（4 条）：

```
FAIL: Evidence SHA-256 不匹配：verification/P19-UI-FIX-1/frontend-npm-test-final.log
FAIL: Evidence SHA-256 不匹配：verification/P19-UI-FIX-1/frontend-npm-build-final.log
FAIL: DONE evidence_dir 含未登记文件：（8 个 04-settings-*/app-err-* 文件，合并为 1 条）
FAIL: Resource Manifest 引用必须位于 verification/**：resource-manifest.json
```

改后（10 条）：

```
FAIL: Evidence SHA-256 不匹配：verification/P19-UI-FIX-1/frontend-npm-test-final.log
FAIL: Evidence SHA-256 不匹配：verification/P19-UI-FIX-1/frontend-npm-build-final.log
FAIL: Evidence SHA-256 不匹配：verification/P19/import-no-response-r4.md
FAIL: DONE evidence_dir 含未登记文件：（同上）
FAIL: Resource 最终路径未验证：Same ignored target/dist locations in this worktree
FAIL: Resource 最终路径未验证：apps/desktop/src-tauri/target/p19-ui-fix-1-isolation-20261017
FAIL: Resource 最终路径未验证：Same source location
FAIL: Resource 最终路径未验证：Same shared build environment
FAIL: Resource 最终路径未验证：Same local cache location
FAIL: Resource 最终路径未验证：Same main-repository paths
```

注：`verification/P19/import-no-response-r4.md` 的 SHA 不匹配是本 worktree 的环境差异
（该文件由主 checkout 镜像而来，换行可能与 blob 不同），不是本 Task 造成的。

## 6 个 destination 错误是什么

`verification/P19-UI-FIX-1/resource-manifest.json` 的 7 个资源项中，有 6 个的
`destination_path` 是**散文而非路径**：

| # | resource_type | destination_path |
|---|---|---|
| 2 | generated-build-artifacts | `Same ignored target/dist locations in this worktree` |
| 3 | isolated-user-data-copy | `apps/desktop/src-tauri/target/p19-ui-fix-1-isolation-20261017`（真实但不存在） |
| 4 | user-data-source | `Same source location` |
| 5 | sidecar-build-environment | `Same shared build environment` |
| 6 | pyinstaller-cache | `Same local cache location` |
| 7 | read-only-baseline-evidence | `Same main-repository paths` |

检查器对 `MIGRATE / ARCHIVE / PRESERVE_*` 会 `Resolve-LocalPath` + `Test-Path`，散文与
不存在的路径都会失败。

**这与 Round 22 的发现同源**：当时我把这份 JSON 转成表格，错误从 4 涨到 8，原因正是这些
destination。当时我回退了。现在引用格式修好，同一批债务以另一种形式浮现。

## 为什么本 Task 无法修好它

1. 本 Task 的 `allowed_paths` 只有 `doc/tasks/P19-UI-FIX-1.md` 与
   `verification/P19-UI-MANIFEST-VIEW-1/`——**不含**源 JSON，也**不含** `tools/governance/`。
2. 改 JSON 的 destination 会篡改一份 Codex 出具、内容准确的记录（`Same source location`
   的语义确实是「与 source 相同」）。
3. 让检查器容忍散文 destination 属于**检查器行为变更**，需要独立 Task 与 Review。

## 我的判断（交 Codex 裁定）

`Same source location` 这类值**不是路径，而是「与 source_path 相同」的指针**。检查器把它当路径
`Test-Path` 必然失败——这不是数据缺陷，而是**检查器对该语义没有表达能力**。

合理的修法是给检查器加一条规则：当 `destination_path` 恰好等于某个「同源」标记
（`Same ...` / 空 / `-`）时，解析为 `source_path` 再做校验，或直接跳过并记 note。
这与 Round 29 处理 `closeout_counts` 口径问题同型——都是「真实数据比检查器模型更丰富」。

**但这是检查器变更，不在本 Task 授权内。**
