# P02 范围契约独立审查 r1

- Timestamp: 2026-10-09T03:05:30Z
- Reviewer: `/root/p02_scope_review`（与 Codex 作者不同；只读审查）
- Baseline: `241ff3b70b6fc0490ea238efd486cc707f849031`
- Reviewed artifact: `doc/tasks/P02.md`，审查时 SHA-256=`5E6B4612998F2279AD2EFEDC8BE1FBB68B7CE296371CDFFE663CC8DB6BC83841`
- Decision: `changes_requested`
- Findings: P0/P1=0，P2=2，P3=1

## Findings

### P02-SCOPE-R1-01 — AC4 可跳过核心判别并关闭 Task（P2）

AC4 允许 retype/undo/restore 无法准备时记 `NOT_RUN`，但未声明这是否阻止 `done`。这样可能在默认 300ms 配置下“写后立即刷新”缺口尚未被判别时关闭 P02。既有 `WorkbenchPage.test.tsx` 用例在 `regionDebounceMs=0` 运行，`M2-REGION-DEBOUNCE-1` 已记录该验证缺口。

建议将三种操作设为必要覆盖，并明确任一路径未验证即 `BLOCKED`、不能满足 AC4。

### P02-SCOPE-R1-02 — 未映射 token 可能跳过可计算的对比度（P2）

AC6 把 token 未映射、CSS fallback 和动态底色无法确定混为 `UNMAPPED/NOT_VERIFIABLE`。实际 WebView computed 前景/背景有时仍可确定并计算 ratio；例如 `RegionInspector.tsx` 存在可计算的固定前景/背景。无 token 映射不应跳过颜色测量。

建议分别记录 token mapping 和 contrast result；实际前景/背景可确定时必须计算。仅实际合成底色不可确定时才允许 `NOT_VERIFIABLE` 并写明原因。

### P02-SCOPE-R1-03 — 构建命令与路径禁令文字冲突（P3）

测试计划要求 npm 与 Cargo 构建，但禁止路径同时覆盖其标准生成目录 `frontend/dist`、`src-tauri/target`。这会让执行者无法判断允许何种临时输出。

建议为隔离、可重建且不入库的构建输出写出明确例外，并保持生产源码、配置与发布产物只读。

## Review 覆盖和局限

审查核对了 Task 中 AC、路径边界、真实/Mock 证据划分、来源契约、现有 debounce 实现与构建计划。未发现需要新增依赖或修改生产源码才能完成 harness 的证据。此审查不是 DSH 对实现的正式 Review；真实 WebView2 驱动/交互、构建及测试仍 `NOT_RUN`。

## 修订处置

Codex 已在本工作副本将 AC4 改为三项均须判别、未覆盖阻止 `done`；AC6 拆分 token mapping 与 contrast result 并强制对可确定颜色计算；为可重建 task-local 构建输出添加例外和保护要求。该修订仍待独立 r2 复核，当前 Task 不得据此视为 ready。
