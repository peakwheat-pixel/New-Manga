---
task_id: GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1
author: DeepSeek Harness
base_commit: cc72f6a822f0c7823a50996d9e43674147bc7b4a
reviewed_head: b8ab6317ec873b34819e09d09ec53dda4f75915b
decision: approved
---

## 结论

**approved**

- `reviewed_head = b8ab6317ec873b34819e09d09ec53dda4f75915b`
- `diff_base = cc72f6a822f0c7823a50996d9e43674147bc7b4a`
- `delivery/source = ec86311318975ffe1ac909fc1e5dd4e832ae1617`
- Task 来源 base：`951b7c61f`

本 Task 为纯只读研究，未改生产工具、旧 source/pin/69 例外或 runtime 行为；R1 未发现 P0/P1。批准范围仅研究结论与 metadata；不批准任何解析器/例外实现、原字节修改、真实 cleanup、父 Task done 或 r212 解除。

## Architecture

- 研究边界正确：只读当前 12 中 R25/R26/R27/R28/R32，四源原字节/路径/归属事实与旧 32 矩阵一致；新增 Task Manifest 四行用于原位保全，不生成运行例外。
- 两模板错误仍保留为错误，未泛化忽略整个 P09 Review 或 117..239 围栏；同围栏 line 227 的精确 worktree 保护仍存在。
- 三份 NUL 源保持原始字节：P14 两文件各 1 个 NUL（offset 286），P22 原文件 2 个 NUL（12330/20486）另有非空白 C0；未去 NUL、未转码、未提交/接管 P22 untracked 快照。
- P14 旧 `SOURCE_PIN` 字样保留但断表未实际登记；本 Task 仅在自己的 Manifest 补四源保护，不改旧 P14/P22 Task 与旧 pin。
- 7 个历史运行身份保持 remaining；101 heads/139 WT 未作任何资源操作（未完整枚举，Owner 证据）。

## Verification

**五项身份**

- 当前 canonical scan 为 **12 errors**；R25/R26/R27/R28/R32 与 `matrix.json` 的 `code/file/locator/message` 完整一致，五元多重集匹配。
- 其余 7 项保持原身份：P19 三条、ENV-BUNDLE-1-FU1 一条、P19-UI-FIX-1 三条。
- 四源 raw SHA 与旧矩阵/source-facts 一致：
  - P09 `dcc528c1dd803961…`
  - P14 r1 `df4de2411355fe05…`
  - P14 r2 `122b34494203dbd8…`
  - P22 `7ebd7d40e7334c94…`
- P14 两文件各 `nul_offsets=[286]`、严格 UTF-8；P22 `nul_offsets=[12330,20486]`，共 6 个非空白 C0（含 0x0b/0x0c/0x08），严格 UTF-8。
- 三源内存独立 `parse_markdown_declarations` 均为 **0 Declaration / 0 error / 0 warning**；实际 `read_text` 均 `FILE_UNREADABLE`。
- P09 内存解析：1 条 line 227 worktree 保护、2 errors（line 7/8）、2 warnings；line 227 在全 index 中仍受保护。两模板行位于 fence 117..239 内的物理行 228/229，scanner locator 7/8。
- P14.md 独立解析对 P14 两文件 **0 Declaration / 0 error**（1 warning）；其 line 133/134 `SOURCE_PIN` 仅为字面记录，未实际注册。新 Task Manifest 四行实际注册：P09/P14 r1/P14 r2 为 `PRESERVE_REFERENCED`，P22 为 `PRESERVE_UNKNOWN`（均另有 destination pin）。
- P22 `git ls-files` 为空、`HEAD:path` 不存在，确为 untracked；实际作者 unknown，未接管或提交。

**保全与计数**

- 实时 scan：`2567 declarations / 1876 protected roots / 12 errors / 270 warnings`。
- `source-facts.json` 的 `2560/1869` 和 `preservation-validation.json` 的 `1865→1869` 是 **7 EV 登记前快照**；7 EV 后实时为 `2567/1876`，未把旧快照当实时。
- 新增 `EVIDENCE_PIN` 7 个（实时 1746 包含它们）；四源新增保护实际存在，current 12 完整身份未变。
- 未发现 P09 同文件 line 227 保护被新 Manifest 覆盖/移除；新 Manifest 是保护整源，不是忽略围栏。

**EV / 检查**

- EV-1…EV-7 逐项 `raw = blob = pin` 全部成立；Task 实际 `EVIDENCE_PIN 7 / errors 0`（19 declarations）。
- `audit_identity.py` 实际以 `python -B … G:/CODEX/New Manga` 运行：**exit 0**，stdout JSON 断言通过，未写文件。
- canonical `check.ps1`（默认及 `-TaskPath`）：**PASS（2 个既有 warning）**。
- `git diff --check cc72…b8ab`：**exit 0**。
- `git diff --name-only` 对 `tools/**`、两旧历史源：**空**；WT `status --porcelain` 为空，Task/EV 均 tracked。

## Owner 证据 / 我的执行 / NOT_RUN

- **Owner 证据**：`source-facts.json`、`preservation-validation.json`、`execution.json`、`report.md`、7 EV pins；`execution.json` 记录 audit/governance/diff 三条 exit 0 及 raw log hash。
- **我实际执行**：canonical 当前 scan、矩阵/current 12 对比、四源 SHA/NUL/严格 UTF8、P09/P14/P22 内存 parse、`read_text` 拒绝、新 Manifest 实际注册、EV raw/blob/pin、Task 7 EVIDENCE_PIN、`audit_identity.py`、`check.ps1`、`git diff --check`。
- **NOT_RUN（合理）**：产品构建、旧 127 回归、fixture、process/file handle 全量证明、101 heads/139 WT 完整盘点、旧保护 1865 全集合的独立重建；这些不授权删除或 cleanup。
- 本 Task 不涉及旧六探针目录，本轮未触碰其 ACL/内容；旧任务资源继续保留。

## P0 / P1 / P2

- **P0：0。**
- **P1：0。**
- **P2（叙述修正，不阻塞）**：`report.md` 第 7 行称 P09 “磁盘 CRLF 与 blob LF 不同”，但 `source-facts.json` 明确 `disk_equals_head_blob: true`、`lf_normalized_equals_head_blob: true`，即磁盘字节与 HEAD blob 一致。raw SHA 与身份结论不受影响；建议改为“磁盘与 HEAD blob 一致”，如修改 report 则需重签 EV-6/对应 head。

## 范围与下一步

- 批准仅覆盖本只读研究及 metadata；不批准解析器/例外实现、原字节修改、NUL 清除、P22 接管、真实清理/迁移/删除、父 Task done 或 push。
- 可继续 Codex 正常 merge/main 复核 done；建议在 main 复核时顺手修正上述 P2 叙述（不影响当前 raw/pin/保全结论）。之后再按 Handoff 建议，单独冻结 `GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1` 做精确历史证据解释设计，不把设计当作实现或删除授权。