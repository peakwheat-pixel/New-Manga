# M2-PAGE-RESOURCE-RESOLVE-1 Handoff（Owner→Reviewer/Integrator）

- Owner: Codex Executor（ZCode 代行，持续自治授权）
- Reviewer: DeepSeek Harness（非作者）
- Integrator: Codex
- Task: [M2-PAGE-RESOURCE-RESOLVE-1](../tasks/M2-PAGE-RESOURCE-RESOLVE-1.md)（release `bf00865b`，base `2fe446c5`）
- Branch/worktree: `zcode/page-resource-resolve-1` @ `G:/CODEX/New Manga.worktrees/PAGE-RESOLVE-1`
- Delivery head: `61c71952`（commits：`f46dd28e` Core 层 → `61c71952` Rust/React/契约层）

## 交付内容（一句话）

新 wire 命令 `resolve_page_resource`：page_id → 页显示图的可 issue 资源目录键 `{resource_id, revision}`；Core 首次解析把不可变 managed 原图逐字节发布进 derived 只读根（RC-4 preview 同款通道）并登记目录（确定性键 `page-original-{page_id}`，后续解析幂等返回同键）；React Workbench 页图随之自动加载，手输 resource id/revision 降级为调试后备。契约 M2-C1 rev 1.6→1.7，协议 minor 4→5。

## 逐层交付

### Core（`f46dd28e`）
- `src/bootstrap/core_service.py`：`PROTOCOL_MINOR=5`（含完整 bump 注记链）；新错误码 `E_PAGE_NOT_FOUND="PAGE_NOT_FOUND"`（not_found；与 region 面 `TARGET_NOT_FOUND` 族区分）；`_ORIGINAL_SUFFIXES` 白名单（png/jpg/jpeg/webp/bmp/gif，fail-closed）；`handle_resolve_page_resource`（payload 校验→`RegionLookupError`：page 不存在/无 managed_original_ref/文件缺失；`read_original_page` 同款 Managed Copy 根逃逸检查→`RuntimeError`→`E_UNKNOWN`；publisher 未配置→`RuntimeError`→`E_UNKNOWN`）；dispatch 分支（OSError→`ARTIFACT_WRITE_FAILED` internal retryable，stderr 记录发布失败）。
- `src/infrastructure/resource_channel/render_preview.py`：`lookup(resource_id)`（目录读）；`publish_original(managed_file, resource_id, suffix)`（确定性键发布，temp+fsync+os.replace+逃逸检查与 preview 同款，revision 恒 `"original"`）。
- 测试 `tests/core/test_page_resource_resolve.py`（4 用例）：minor 5 ping、首解析发布+字节保真+目录行（scope `derived-read-only`、rel_path 精确）+幂等二次解析同键、未知页 `PAGE_NOT_FOUND` fail-closed、payload 校验三形态 `INVALID_REQUEST`。
- 协议 pin 同步：`test_core_service.py`（两处 minor 5）、`test_core_service_settings.py`、`test_core_detect.py`（PROTOCOL_VERSION 常量+用例改名 minor_5）、`test_core_service_retype.py`（bump 断言 1,5）。

### Rust（`61c71952`）
- `library_bridge.rs`：trait 方法 + stdio 实现（`round_trip("resolve_page_resource", {page_id})`）+ `MockLibraryChannel` 实现（复用 domain_result）。
- `main.rs`：`PRODUCTION_COMMANDS` 12→13（含 `resolve_page_resource`）；新生产-only 组 `PAGE_RESOLVE_PRODUCTION_ONLY_COMMANDS`；`command_allowlist` 过滤器扩员；`#[tauri::command] fn resolve_page_resource`（**不走 preview 轮换**——稳定目录键不得被 per-page revoke 删除，函数注释注明裁定）；`generate_handler!` 生产分支注册；`production_surface_is_exactly_thirteen_commands`（改名+扩 vec）；probe/ac1 算术 pin 加 `- PAGE_RESOLVE...len()`；`app_acl_manifest` 文档注释 thirteen；真实 sidecar round-trip 测试 minor 4→5（consequence sync）；`SequencedRerenderLibrary`/`Arc<>` 两个测试 impl 补转发。
- `build.rs`：app-manifest 声明加 `resolve_page_resource`。
- `capabilities/m2rc1-commands.json`：`allow-resolve-page-resource` permission + description 更新。
- cargo：**53 passed + 1 ignored**（RC-4 基线等量）。

### React（`61c71952`）
- `library/client.ts`：wire 名常量 `RESOLVE_PAGE_RESOURCE_COMMAND="resolve_page_resource"`（钉死防漂移）；`resolvePageResource(pageId)`（result 形状校验→`PAGE_RESOURCE_MALFORMED`；typed code 透传）。
- `library/types.ts`：`PageResourceResolve`。
- `workbench/WorkbenchPage.tsx`：resolve effect（pageId 非空→resolve→成功填充 `resourceId`/`resourceRevision`（手输框自动填充=调试可见）、失败显示 typed code）；`onPageIdChange` 清空手输值（跨页不泄漏）；Resource section 加 `resource-resolve-busy`/`resource-resolve-error` 显示。手输路径完整保留（解析失败时兜底 previews 等资源）。
- `WorkbenchPage.test.tsx`：interactive mock 默认 `resolve_page_resource` 抛 `PAGE_NOT_FOUND`（保持既有用例手输/preview 流的历史时序零扰动）；两个新用例（自动解析喂图：断言 invoke 参数/输入框自动填充/页图 blob/资源读 URL；typed 失败呈现+手输兜底可用）。vitest **120 passed**（118+2），`npm run build` EXIT=0。
- `resourceChannel/commandSurface.test.ts`：production-only 数组与冻结断言加 `resolve_page_resource`；surface mock 加 handler。probe deny 断言覆盖新命令。

### 契约（`61c71952`）
- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev 1.7：头部增量块、Revision history 条目（八点：请求/响应、storage 缝、发布语义、确定性键与幂等、新错误码、minor bump、Rust 13 命令与 host 不轮换裁定、§5.2 边界不变）、§5 表新增 `ResolvePageResource` 行。

## 验收对照

| AC | 状态 | 证据 |
|---|---|---|
| AC1 契约 rev 1.7 | DONE | 契约三处落字（见上）；`61c71952` |
| AC2 Core focused | DONE | tests/core 228 passed；focused 四目录 **412 passed**（RC-4 基线 408+4 新）；新用例 4 个覆盖幂等/fail-closed/minor 5 |
| AC3 Rust | DONE | cargo **53 passed + 1 ignored**（等量）；13 命令 pin 断言 |
| AC4 前端 | DONE | vitest **120 passed**（118+2）+ build EXIT=0；自动加载与失败呈现有测试钉住 |
| AC5 全量回归 | DONE | worktree 全量 pytest **1866 passed + 1 skipped + 0 failed**（main 基线 1862+1sk+0 failed 等量递增 +4 新 Core 用例）；raw 日志 `verification/M2-PAGE-RESOURCE-RESOLVE-1/raw/full-pytest-1.log`（HEAD 绑定 61c71952，含 handoff 的 1d9605b3 不含后续提交） |

## 设计裁定（集成方/Reviewer 请特别核验）

1. **确定性资源键 vs preview 随机键**：managed 原图不可变 → `page-original-{page_id}` 恒定；幂等=目录查找命中即返回（不重发布、不校验文件存在性——目录权威原则 F-03，与 RC-4 revoke-previous 的键删除语义互斥：host 端该命令不进 preview 轮换）。
2. **发布失败（OSError）**：本命令核心功能即发布，失败不可静默降级（与 rerender 的 `preview_error` 降级不同——preview 是附带品），映射 `ARTIFACT_WRITE_FAILED` internal retryable。
3. **`PAGE_NOT_FOUND` 新码**：Task 冻结承诺；region 面的 `TARGET_NOT_FOUND` 语义是"region 不存在"，混用会把错误码语义绑到 message 文本上。
4. **resolve effect 与手输的优先级**：resolve 成功覆盖手输值（产品语义：pageId 是权威输入）；resolve 失败不清理手输（调试后备语义）。
5. **suffix 白名单**：managed_original_ref 受控于导入面，白名单是纵深防御非信任替代；白名单外 → `E_UNKNOWN`（数据态异常，非请求错误）。

## 已知登记项

- fresh worktree 首次 cargo 前跑了 `packaging/m2ac5/build_sidecar.ps1`（HEAD=f46dd28e 构建 OK，闭包断言/权重 sha256 全过）——M2-AC5 如实登记先例。
- 契约 §5 表 `ListChapters`/`GetReaderProjection` 等仍为 PROPOSAL（本 Task 明确不做，见 Task 冻结范围）。
- vitest 的 `resourceReads` 现含 `page-original-*` 自动读（新用例断言）；既有用例的断言为子串式，零扰动。

## Review 输入

- Task: doc/tasks/M2-PAGE-RESOURCE-RESOLVE-1.md（含冻结范围）
- Contract: doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md（rev 1.7 三处）
- Diff: `git diff 2fe446c5..61c71952`（13 文件，+628/-49 预期口径）
- Raw: verification/M2-PAGE-RESOURCE-RESOLVE-1/raw/full-pytest-1.log
