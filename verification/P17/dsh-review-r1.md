# P17 独立 Review（R1）

| 项 | 值 |
|---|---|
| Task | P17（阅读器 Reader，四页第四页；设计基线 §4） |
| Owner | antigravity |
| Reviewer | dsh（epoch 6；独立于 Owner，`route-agent.py` 机器排除 Owner） |
| 交付 | `55b9ff3f8`（feat）；HEAD 同（工作树 clean） |
| 基线 | `536962909` |
| 结论 | **approved**（含 1 项需在 closeout 修正的**状态词法缺陷**，见 §3） |

## 1. 独立验证且成立的部分

| # | 验证项 | 方法 | 结果 |
|---|---|---|---|
| V1 | **范围与页面边界（核心）** | `git diff --name-only 536962909..HEAD` | **PASS**。改动**只在** `apps/desktop/frontend/src/reader/**`（10 文件）+ `src/shell/AppShell.tsx` + Task/Handoff/verification；**未触碰** Tauri/Rust、Python Core、契约、Schema、依赖 ✓ |
| V2 | **导出面板未实现（冻结边界）** | 源码检索 + Owner 的 `boundary_audit.txt` | **PASS**。`ExportDialog` / `StartExport` / `cancel_export` / `get_export_*` / `open_folder` / `reveal` 在 `src/reader/**` **0 命中**；且有**测试**断言渲染结果 `not.toContain("library_start_export")` |
| V3 | **无发明 wire** | 检索 `invoke(` / `library_` | **PASS**。仅调用 `library_get_reader_projection`、`library_save_reading_progress`（+ 既有 `resolve_page_resource` 路径）；常量以测试钉死 |
| V4 | **页图经 §10 资源通道** | 读 `ReaderPageImage.tsx` | **PASS**。`resolvePageResource(page.page_id)` → `{resource_id, revision}` → `resourceClient.fetchAll(issued.url, issued.size)` → `URL.createObjectURL(blob)`；**不构造、不持有任何文件系统路径** |
| V5 | **路径零泄露** | 前端检索 `output_path|source_path|sourcePath|absolutePath` | **PASS**（**0 命中**） |
| V6 | **§6.3 红线（AC2）** | 读实现 + 测试 | **PASS**。缺失译图以 **`resource_ref: null`** 呈现（测试显式覆盖 `resource_ref: null // missing translation`）；`beginning` 不改进度、`original`/`translated` 独立进度键、`elapsed_seconds_delta` 缺失不重发 —— 均有行为证据（`behavioral_evidence.md` 逐条）与单测 |
| V7 | 事件→重查快照 | 读 client/页面 | **PASS**。订阅 `core:ReadingProgressChanged` 后重新 `GetReaderProjection`（测试断言调用次数增加） |
| V8 | 证据真实性与 pin | 逐个 `Get-FileHash` | **PASS**。8 条证据的 sha256 **全部与磁盘匹配**；日志真实：vitest **193 passed**、`vite build` exit 0、pytest **407 passed**、cargo source/packaged 均 ok |
| V9 | **如实限定** | 读 Handoff | **PASS**。**GUI e2e 明确 `NOT_RUN`**，并写明"**绝不以单测通过表述为 e2e 通过**"（无头 Windows 无法取得 WebView2 窗口句柄 `0x80070578`）——完全符合我 AC5 的要求 |

## 2. 结论：approved

严格落在设计 §4 与既定边界内：只做前端、只调用已冻结的两条阅读器命令、页图经资源通道、无路径泄露、事件后重查快照、缺失译图为 null；**明确未实现导出面板**（含独立审计文件与测试断言）；证据充分且如实声明 GUI e2e 未运行。

## 3. 需在 closeout 修正的状态词法缺陷（非实现缺陷）

Task front matter 使用了**不在合法状态集合内**的值：

- `status: ready_for_review` → 合法值应为 `in_review`（或终态）；治理检查器会按未知状态处理；
- `canonical_evidence_status: ready_for_review` → 应为 `complete`；
- `delivery_head: pending` → 应为分支实际 HEAD `55b9ff3f8`（**BL-15**）。

**裁定**：属**状态词法缺陷**（与 P12 的 `review_ready` 同类），**不要求 Owner 返修**；由 Coordinator 在 closeout 按真实值修正并记录。
**另**：8 条证据行的 `commit` 列为 `pending` —— 检查器**显式接受**该值（回退校验 sha256，且 8/8 匹配），故非缺陷；closeout 将填入**真实交付提交**，使 **BL-17** 的 `git cat-file -e <sha>:<path>` 包含性校验成为可用证据。

## 4. 集成预告

本 Task 只改 `apps/desktop/frontend/src/**`（含 `shell/AppShell.tsx`）。**P14 亦在飞且可能同时修改 `AppShell.tsx`（页面路由）** → 合并时**预期在该文件冲突**；按既有方法论：叠加式可用并集，**但**若含路由表/计数类内容必须按**合并后真实值**统一；**每次合并后重跑全套**（vitest + build + Rust + pytest）。
