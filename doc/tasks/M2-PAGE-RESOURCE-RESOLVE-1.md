---
id: M2-PAGE-RESOURCE-RESOLVE-1
title: 页→资源解析 wire 命令 resolve_page_resource（Workbench 页图自动加载第一刀）
kind: feature
status: ready
approval: user_2026-10-07_autonomous_mode_continuation（STATUS 授权：RC-4 后继续最新证据下下一最高优先任务）
suggested_owner: Codex Executor
owner: Codex Executor（ZCode 代行）
reviewer: DeepSeek Harness（非作者）
integrator: Codex
depends_on: [M2-RC4-DOMAIN-COMMANDS, M2-WORKBENCH-REACT-1]
base_commit: 2fe446c5
branch: zcode/page-resource-resolve-1
worktree: G:/CODEX/New Manga.worktrees/PAGE-RESOLVE-1
integration_commit: null
---

# M2-PAGE-RESOURCE-RESOLVE-1

## 来源与目标

STATUS Planned next 主路径候选①「production 页导航/资源投影」的最薄纵切。侦察实证（2026-10-07，Explore 全仓盘点）：WorkbenchPage 五区数据源已全走真实 IPC（列表/regions/Inspector/写通道），唯一硬缺口=**页图加载需手输 resource id/revision**——`workbench/pageImage.ts` 明文登记「page→resource catalogization 不在生产面，仅 acceptance bridge 播种」。本 Task 打通 page_id → 可 issue 的资源目录键，页图自动加载。

## 范围（冻结）

### 契约（M2-C1 rev 1.6 → 1.7）
- §5 命令目录新增 `ResolvePageResource`：request `{page_id}` → response `{resource_id, revision}`，页面无资源且无法解析时 fail-closed `PAGE_NOT_FOUND`；复用既有资源通道语义（opaque URL/chunk/TTL/§10 大媒体保护均不变）。
- envelope protocol minor 4→5（惯例：bump=commands added，RC-4 先例）。

### Core（src/bootstrap/core_service.py）
- DTO + handler + dispatch 分支；`PROTOCOL_MINOR=5`。
- handler 语义：page_id → Page（repository）→ 经 `read_original_page` 同款 storage 缝解析 managed 原图 → 查 ResourceCatalogStore：已目录化则幂等返回既有键；未目录化则发布进 derived 只读根并登记（RC-4 preview 同款发布路径，`render_preview.py` 先例）→ 返回目录键；page 不存在 → `PAGE_NOT_FOUND`。
- pytest：dispatch 级用例（未目录化首解析、幂等二次解析同键、PAGE_NOT_FOUND、protocol minor 5）。

### Rust（apps/desktop/src-tauri）
- `library_bridge.rs` trait 方法 + stdio 方法映射；`main.rs` `#[tauri::command] resolve_page_resource` + `PRODUCTION_COMMANDS` 追加（12→13）+ 生产-only 分组 + **len 单测 pin 更新**；`capabilities/m2rc1-commands.json` permission 同步。
- cargo 测试：allowlist pin 断言更新 + 新命令桥接用例。

### 前端（apps/desktop/frontend）
- client 封装 `resolvePageResource`（wire 名常量钉死，snake_case 先例）；`commandSurface.test.ts` 数组同步。
- `WorkbenchPage` 页图 effect 改为：pageId 变化 → `resolve_page_resource` → `loadPageImageUrl`；手输 resource id/revision 输入框**保留**但降级为调试后备（解析成功时自动填充/覆盖为解析结果；解析 PAGE_NOT_FOUND 时保留手输路径并显示错误）。
- vitest：client 用例 + WorkbenchPage interactive mock 加新命令 + 自动加载用例（含 fail-closed 呈现）；build EXIT=0。

### 明确不做
- `list_chapters`/`list_pages` 投影命令与页导航列表升级（PageListPanel 手输 page_id 保留）。
- Reader 页、四页导航结构、TaskProgressPanel 数据线、导入/Run 命令族。
- Legacy src/ui/QML 零接触；Schema/ports 业务语义不改（wire 加法）。

## 验收 Gate

1. AC1 契约：M2-C1 rev 1.7 修订落字（命令目录+DTO+minor bump+Revision history）。
2. AC2 Core：focused pytest 全绿，新用例覆盖幂等/fail-closed/minor 5。
3. AC3 Rust：cargo 测试全绿（13 命令 pin）。
4. AC4 前端：vitest 全绿 + `npm run build` EXIT=0；页图自动加载路径有测试钉住。
5. AC5 回归：pytest 全量等量递增（1862 基线+新增）；cargo、vitest 基线不变量保持。
6. 非作者 Review（DSH）通过。

## 完成定义

AC 全过 + Review 通过 + 集成 merge main + STATUS/PLAN 收口。
