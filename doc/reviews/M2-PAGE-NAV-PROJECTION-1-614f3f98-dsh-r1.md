# M2-PAGE-NAV-PROJECTION-1 r1 独立 Review

VERDICT: approve_with_conditions

说明（证据可得性）：本 worktree 的 `pwsh` 因沙箱 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)` 完全不可用，且无审批通道可升级，因此**无法执行任何 git/测试命令**。本 Review 全部基于只读文件工具（read/grep/glob）核验源码、契约、测试与已有 raw 日志；涉及 commit 文件清单/工作区洁净度的项已在“可核验性受限”清单中如实标注，未凭推断代替证据。以下所有行号均为当前工作树实测。

---

## 逐条发现

### PR-01（P2）桥接用例的「typed 透传」声称无对应断言
- 文件：`apps/desktop/src-tauri/src/library_bridge.rs:812-843`
- 事实：用例名 `page_nav_mock_channel_round_trip_and_typed_pass_through`（:813），但函数体只 `set_domain_result(Ok({chapters/pages...}))` 并断言投影字段（:822-842），**没有任何 `Err(LibraryError)` 分支断言**；而同类先例 `page_resolve_mock_channel_round_trip_and_typed_rejection`（:780-810）结尾明确断言 `PAGE_NOT_FOUND`/`category`/`retryable`（:800-809）。
- 声称：Handoff:22 写「桥接用例 `page_nav_mock_channel_round_trip_and_typed_pass_through`（投影形状 + 包装对象 + **typed 透传**，沿 PR-01 返修先例）」——「typed 透传」这一证据项不存在。
- 处置：在 :843 前补 `channel.set_domain_result(Err(LibraryError::new("INVALID_REQUEST","validation",false,Some(...))))` + `unwrap_err()` 断言（推荐，与 :800-809 对齐）；或把手递该条降级为「投影形状 + 包装对象」。影响有限（Mock 的 `Err` 透传是 `clone()` 直通），但这是**证据声称与事实不符**。

### PR-02（P3）契约 §5 表两处交叉引用方向写反（AC1 落字质量）
- 文件：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:123` 与 `:138`
- 事实：§5 表中原 PROPOSAL 组合行在 **:123**（上方），新增冻结行 `ListChapters` 在 **:138**（下方）。但 :123 写「`ListChapters` 已转冻结为 wire `list_chapters`（见**上方** `ListChapters` 行…）」；:138 写「**下方**原 PROPOSAL 组合行中的 `ListChapters` 转本行冻结」。两处「上/下」互换。
- 影响：AC1 明确要求「rev 1.8 三处落字」，而 §5 表内部导航指错；读者按 :123 的「上方」找不到冻结行（正确指向是其下方 :138）。
- 处置：:123 改「见下方 `ListChapters` 行」，:138 改「上方原 PROPOSAL 组合行」。语义与实现均无误，属纯文档缺陷（若按 AC1 严格口径可升级 P2）。

### PR-03（P3）dispatch 中 resolve 分支注释被错位到导航分支之上
- 文件：`src/bootstrap/core_service.py:1493-1495`（受影响分支 :1496-1546，失去注释的分支 :1548）
- 事实：注释 `# M2-PAGE-RESOURCE-RESOLVE-1: page -> servable resource key. Read face of the display image; publishes the immutable managed original into the derived read-only root…` 现在紧贴 `if command in ("list_chapters", "list_chapter_pages"):`（:1496），而真正实现该语义的 `if command == "resolve_page_resource":`（:1548）上方**无注释**。新增导航分支时被插在注释与原分支之间。
- 影响：在契约关键 dispatch 函数里把「publishes…into the derived read-only root」（有副作用）的语义挂到只读导航分支上，误导后续读者/维护者；行为无影响。
- 处置：将 :1493-1495 三行下移到 :1548 之前，导航分支只保留 :1497-1499 的自身注释。

### PR-04（P3）`main.rs` 两处冻结面计数注释仍为陈旧值 13/20
- 文件：`apps/desktop/src-tauri/src/main.rs:965-967`、`:985-989`
- 事实：:966 仍写「thirteen production」，:987 仍写「all **20** commands across the three surfaces (**13** production + 4 probe-only + 3 ac1)」。实际生产面 15、三面并集 22。同一次交付已把 `build.rs:37` 更新为「twenty-two commands…（fifteen production…）」。
- 影响：同一命令面的三视图（constants / generate_handler! / build.rs）注释不再互相印证，`app_acl_manifest_is_generated_and_enforced`（:970）的说明与实测面不符。测试逻辑本身正确（遍历 allowlist，无硬编码数字）。
- 处置：:966 改 fifteen、:987 改 22/15；建议顺带把「resource-channel, IPC1, settings, retype, RC-4 and the page resolve」补上「+ the page navigation projections」。

### PR-05（P3）前端命令面镜像 `commandSurface.test.ts` 未随命令面扩员，镜像已失真
- 文件：`apps/desktop/frontend/src/resourceChannel/commandSurface.test.ts:35-45`、`:199-207`
- 事实：`DOMAIN_PRODUCTION_ONLY_COMMANDS`（:38-45）为 6 项，且 :200-207 用 `toEqual` 把该 6 项**精确钉死**；新增的 `list_chapters`/`list_chapter_pages` 未纳入。该文件 docstring（:7-8）自称「reproduces the hardened host semantics pinned by the Rust suite (main.rs `command_allowlist` + capabilities/m2rc1-commands.json)」，因此在 `makeSurfaceInvoke("production")` 里这两个新命令会被判为 `unavailable on production surface`（:65-70）。
- 影响：JS 侧「同一面」的第 4 个手工镜像与 Rust 面（15 生产命令 / 6 个生产-only 族）失同步；任何后续用该 fixture 验证导航 client 的用例会假失败，且该镜像不再能作为漂移哨兵。契约 `§5.3:181` 明确写有「前端 commandSurface pin 与 Rust unit test 同时更新」的宿主同步纪律（虽该句语境为 settings 通道，属最近先例）。
- 处置：把两命令加入 `DOMAIN_PRODUCTION_ONLY_COMMANDS`，并补一条 production-allow / probe-deny 断言（或至少修正 :7-8 的自述范围）。

### PR-06（P3）切书时旧书章节行仍可点击，悬空 `selectedChapterId` 可被重新引入
- 文件：`apps/desktop/frontend/src/workbench/WorkbenchPage.tsx:233-265`（配合 `PageListPanel.tsx:123-154`）
- 事实：章节 effect 在 :235 首行 `setSelectedChapterId(null)`（重置正确），但**未清空 `setChapters([])`**（对比 :236-240 收起分支与 :273-275 页分支都清了数据）。切书瞬间渲染仍是旧书 `chapters` 行（:125-137 先渲染列表，:138 才渲染 busy 提示），这些行在 B 书数据返回前的窗口内可点击（`onSelectChapter`，:130）。
- 后果：点击后 `selectedChapterId` 被置为 A 书章节；B 书章节到达后 `setChapters` 覆盖列表，但 `selectedChapterId` 仍为 A 书章节 → `page-nav-list`（:155）继续渲染并拉取 A 书章节的页，界面出现「B 书章节列表 + A 书页码列表」的跨书不一致——正是 Handoff:52 设计裁定 3 声称要避免的「旧书章节 id 在新书列表中悬空」。
- 测试判别力：`WorkbenchPage.test.tsx` 的两个新用例（:827、:870）只注入**单本** `book-1`，且 `onListChapters` 为同步 `Promise.resolve`，既无跨书切换也无迟到窗口，故该路径完全未钉（删除 :235 的 `setSelectedChapterId(null)` 亦不会变红）。
- 处置：切书分支改为 `setChapters([]); setChaptersBusy(true); setChaptersError(null);`（与页分支对称）；补一条「两本书 A→B 切换后 `page-nav-list` 收起」的用例。严重度 P3（无数据风险、无 Core 写路径、需加载窗口内点击）。

### PR-07（P4）真实 sidecar 用例的 minor 注记链漏掉 RC-4 的 3→4
- 文件：`apps/desktop/src-tauri/src/main.rs:1635-1645`
- 事实：注记链写 `…1.1 -> 2 … 2 -> 3 … ; M2-PAGE-RESOURCE-RESOLVE-1: 4 -> 5 …; M2-PAGE-NAV-PROJECTION-1: 5 -> 6`，其中 3→4（RC-4 三条命令）缺条目（属 1.7 交付遗留，本次又续写该链）。`core_service.py:135-158` 的权威注记链是完整的。
- 处置：在 2→3 与 4→5 之间补「M2-RC4-DOMAIN-COMMANDS: 3 -> 4」。

### PR-8（P4）导航两个读取 effect 的迟到回包守卫无测试钉住
- 文件：`apps/desktop/frontend/src/workbench/WorkbenchPage.tsx:243`、`:279`（守卫 `isCurrent()`）
- 事实：守卫结构（`signal.cancelled` + `requestId === xxxReadRef.current`）与既有先例一致、实现无误；但 resolve 链有专门判别用例（`WorkbenchPage.test.tsx:792-825`「drops a stale page-resource resolve…」使用延迟 promise），导航两个 effect **没有**对应延迟回包用例。反向推演：删除 `if (!isCurrent()) return;`（:249、:285 等）后全部 134 条 vitest 仍绿。
- 处置：仿 :792 追加一条「切书后 A 书 chapters 迟到返回被丢弃」的用例；或接受该守卫为「沿先例的防御性代码」并在 Handoff 中不宣称其可测。

### PR-09（P4）`PageListPanel.test.tsx` 的「回调接线」用例并未验证接线
- 文件：`apps/desktop/frontend/src/workbench/PageListPanel.test.tsx:91-108`
- 事实：用例名「renders page tiles **feeding onPageIdChange** once a chapter is selected」，但 `renderToString` 不触发事件，唯一相关断言是 `expect(onPageIdChange).not.toHaveBeenCalled()`（:107，恒真）。`onClick={() => onPageIdChange(page.page_id)}`（`PageListPanel.tsx:162`）若被删除，该用例仍绿。
- 缓解事实：接线在集成层被真实覆盖——`WorkbenchPage.test.tsx:858` 点击 `page-tile-p-nav-1` 并断言 `resolve_page_resource`/输入框/`resourceReads`（:859-864），删除接线会变红。故「三级下钻有测试钉住」（Task AC4）成立。
- 处置：用例改名（如「…renders page tiles and leaves the wiring to the injected callback」）或在 `renderPanel` 里直接调用产出的 props 回调；`Handoff:33` 的「回调接线」表述建议限定为集成层。

### PR-10（P4）新 Core 测试文件 docstring 与 seed 实现不符
- 文件：`tests/core/test_page_nav_projection.py:47-49` 与 `:66-71`
- 事实：docstring 写「two pages in the second chapter **imported in one call**」，实现是 `for` 循环内**逐页**调用 `core.importer.import_files("chapter-2", [ImportSource(...)])`（两次调用）。
- 处置：改为「imported one per call（不同颜色，避免 source_hash 去重）」。

### PR-11（P4，继承性）生产-only 族的算术 pin 对被测常量自引用
- 文件：`apps/desktop/src-tauri/src/main.rs:1065-1078`、`:1108-1121`、`:1132-1151`
- 事实：负向断言与长度等式都遍历/引用 `PAGE_NAV_PRODUCTION_ONLY_COMMANDS` 自身。反向推演：把该常量删成 `["list_chapter_pages"]`（不放回 `PRODUCTION_COMMANDS`）时，`list_chapters` 会静默进入 probe/ac1 面，而 `probe.len()` 期望式（15−11+4=8）与实得 8 仍相等，`production_surface_is_exactly_fifteen_commands` 照旧通过（因为 `PRODUCTION_COMMANDS` 未被改）→ 无独立断言钉住该常量的成员集合。
- 说明：该结构弱点为 IPC1/SETTINGS/RETYPE/RC4/RESOLVE 各代先例共有，非本 Task 引入；此处记录以便后续统一加固（例如新增 `assert_eq!(PAGE_NAV_PRODUCTION_ONLY_COMMANDS, &["list_chapters","list_chapter_pages"])` 或断言 `PRODUCTION_COMMANDS` ⊇ 各族并集且两两不相交）。

---

## 我核对过、未发现问题的关键点

**AC 与证据链（对 raw 日志只读核对，未重跑）**
- 五份 raw 日志 `HEAD` 行全部自述 `614f3f98e4416456e7134ca5a0fbc0f192832bb2`；`.git/worktrees/PAGE-NAV-1/logs/HEAD` reflog 确认 `428cd92c → 614f3f98`（feat）+`614f3f98 → 68a09251`（docs/logs），与 Handoff:8「交付 head 614f3f98、68a09251 为文档与日志入库」一致。
- AC2 focused `422 passed`（命令 `tests/core tests/editing tests/rendering tests/m2_resource_channel`，`focused-pytest-1.log:4,21`）＝ PAGE-RESOLVE 基线 417（`verification/M2-PAGE-RESOURCE-RESOLVE-1/raw/focused-pytest-1.log:21`）+5，逐项自洽。
- AC5 full `1876 passed, 1 skipped, EXIT=0`（`full-pytest-1.log:399-400`）＝ 基线 1871+1sk（PAGE-RESOLVE `full-pytest-1.log:400`）+5。
- AC3 cargo `running 56 tests` → `55 passed; 0 failed; 1 ignored; EXIT=0`（`cargo-test-1.log:17,75,77`）＝ 基线 54+1ign（PAGE-RESOLVE `cargo-test-1.log:75`）+1 新桥接用例；日志内含 `page_nav_mock_channel_round_trip_and_typed_pass_through`、`production_surface_is_exactly_fifteen_commands`、`production_only_commands_stay_off_both_frozen_test_surfaces`、`app_acl_manifest_is_generated_and_enforced` 全 ok（:35,38,40,50），且 `Compiling m2rc1-desktop`（:4）成功 ⇒ 该 HEAD 下 trait 三实现同步可编译。
- AC4 vitest `134 passed / 12 files / EXIT=0`（`vitest-run-1.log:22-27`）＝ 基线 124（PAGE-RESOLVE `vitest-run-1.log:23`）+10，分文件 10（client）/5（PageListPanel）/29（WorkbenchPage）与 Handoff:45「+3/+5/+2」一致；`frontend-build-1.log` `EXIT=0`。
- 基线数字来自上一 Task 自身的 raw 日志（已读），未重跑测试。

**契约 rev 1.8 一致性（除 PR-02 指代方向外）**
- 三处落字齐备且语义一致：头部增量块 `:1`、Revision history `1.8` 七点 `:13`、§5 表 `ListChapters :138` / `ListChapterPages :139`、状态行 `:9`、原 PROPOSAL 组合行注记 `:123`（`CreateChapter`/`DeleteChapter` 保持 PROPOSAL）。DTO 字段集（`chapter_id,title,chapter_number,sort_order`；`page_id,source_filename,sort_order`）三处与实现四侧一致。
- 排序语义：`sort_order` 升序在契约三处一致；repository 确为 `ORDER BY sort_order`（`src/infrastructure/sqlite/library.py:190`、`:363`），Core 透传不重排。
- 零新错误码：`core_service.py:1505-1517` 复用 `E_INVALID_REQUEST`(validation)/`E_UNKNOWN`(internal)；全仓未新增 wire 错误码字面量；`PAGE_NAV_MALFORMED` 仅存在于前端 client 与其测试（非 wire、不在 Core 错误码表），与 Handoff:51 一致。
- minor bump：`PROTOCOL_MINOR = 6`（:159），注记链完整（0→1→2→3→「1.5 不 bump」→4→5→6，:135-158）；`test_page_nav_projection.py:75`、`test_core_service.py:154,240`、`test_core_service_settings.py:69-80`、`test_core_service_retype.py:132-141`（已改名为 `test_protocol_minor_bumped_to_six_with_page_nav_surface`）、`test_core_detect.py:56,604-616`、`test_page_resource_resolve.py:88-94` 全部同步为 6；真实 sidecar 断言 `main.rs:1645`。Handoff:19 列出的 5 个同步文件逐一命中。
- rev 1.7 及更早内容未被改写（1.8 为新增块 + §5 两行 + 一行注记 + 状态行）；§5.2「UI-local actions」`:167` 未改，与 1.8 声称「§5.2 边界不变」一致；§11「Tauri command names」行未加注记，与 1.7 先例（亦未加）一致，不构成矛盾。
- `GetReaderProjection` 行 `:141` 未被改动，与「冻结不变」一致。

**Core**
- 两 handler 位于 `handle_resolve_page_resource`（:988）之前（:937、:963），与 Handoff:58 提示一致；只读投影，非空字符串校验（:945-949、:971-975），`chapter_number/title/source_filename/sort_order` 逐字段取自已排序的 repository 行。
- fail-soft 边界正确：未知父 id 由 repository 返回空集 → `{"chapters": []}` / `{"pages": []}`（:950-961、:976-986）；仅 payload 校验抛 `RegionRequestError` → `INVALID_REQUEST`；`Exception` → `UNKNOWN` internal+固定安全短句（:1521-1536，符合 §8 message 约束）。
- **不加新查询方法**：`ports.py:30,58` 的 `list_chapters`/`list_pages` 与 sqlite 实现均为既有；`src/application`、`src/infrastructure`、`src/ui` 内**无任何** `M2-PAGE-NAV` 标记（grep 全仓确认），`self._core.repository` 即既有 repository。
- `PROTOCOL_MINOR` bump 注记补 5→6 且带契约指针（:155-158）。

**Rust**
- trait 声明 `:178,:180`；Stdio `round_trip` 真实 wire 名与 payload（`{book_id}`/`{chapter_id}`，:454-463）；Mock `:598-604`；测试用 `SequencedRerenderLibrary`（`self.inner.`，:1855-1860）与 `Arc<SequencedRerenderLibrary>`（`(**self).`，:1896-1901）两个 impl 均补转发；编译成功为同步的运行时保证。
- `command_allowlist` 过滤器纳入 `PAGE_NAV_PRODUCTION_ONLY_COMMANDS`（:147）；`PRODUCTION_COMMANDS` 13→15（:53-77，新组 `:133-134`）；probe/ac1 分支字面清单**未变**（:826-847），生产分支按序注册两命令（:853-869）。
- 冻结面断言：`production_surface_is_exactly_fifteen_commands` 精确 vec（:1011-1038，含 13→15 注释）；probe/ac1 负向各加新组（:1065-1067、:1108-1110）且算术 pin 同步加 `- PAGE_NAV_…len()`（:1076、:1119）；负向清扫 chain 纳入新组且注释改 SIX（:1124-1151）；probe/ac1 形状仍钉 7/6（:1149-1150）。
- ACL 三面：`capabilities/m2rc1-commands.json:22-23` 有 `allow-list-chapters`/`allow-list-chapter-pages`；`build.rs:85-86` 声明且注释已更新为「twenty-two/fifteen」（:37-43）；生成物 `gen/schemas/acl-manifests.json`、`capabilities.json`、`desktop-schema.json`、`windows-schema.json` 四件均含新命令，`permissions/autogenerated/list_chapters.toml`、`list_chapter_pages.toml` 各含 allow/deny 两条（共 22 件 toml = 22 命令）。`.gitignore` 未忽略 `gen/`/`permissions/`（生成物可入库）。
- 两个 `#[tauri::command]`（:371-395）只读：无轮换、无 TTL、无写路径，`CORE_UNAVAILABLE` 与 `error.code` 映射与 `resolve_page_resource`（:356-367）同款；`library_bridge` trait docstring 注明 fail-soft 空列表语义（:174-177）。

**React**
- `LIST_CHAPTERS_COMMAND/LIST_CHAPTER_PAGES_COMMAND` 常量（`client.ts:39-40`）被 `client.test.ts:121-122` 钉死；`listChapters/listChapterPages` 包装形状校验 → `PAGE_NAV_MALFORMED`（:107-112、:134-139），wire typed 码经 `:114-120`/`:141-147` 原样透传（`client.test.ts:169-179` 证明 `CORE_UNAVAILABLE` 不被 fallback 吞掉）。
- 下钻状态机：`onSelectBook`/`onSelectChapter` toggle（:473-479）；切书 effect 首行重置章节选择（:235）；收起（null）分支清 rows/busy/error（:236-240、:272-276）；计数守卫 `chapterReadRef/pageNavReadRef` + `signal.cancelled`（:242-243、:278-279）；错误呈现三态互斥（`PageListPanel.tsx:138-152`、`:169-183`）；当前页高亮 `page.page_id === pageId.trim()`（:163）；`page_id` 手输框保留（:86-99）且仍驱动既有 resolve→image 链。
- 测试判别力（反向推演）：删 repository `ORDER BY sort_order` → 逆序插入 seed 使 `test_list_chapters_returns_sorted_projection` 红；删校验分支/改未知父为报错/改 `PROTOCOL_MINOR` → 对应 Core 用例红；删 page tile `onClick` → `WorkbenchPage.test.tsx:858-864` 红；删 toggle → `:888-898` 红；删前端常量值 → `client.test.ts:121-122` 红。

**边界**
- Legacy：`src/ui` 无任何 wire 命令或 `M2-PAGE-NAV` 标记（其 `list_chapters` 调用是既有 Qt ViewModel 对应用服务的进程内调用，与 wire 名同名属历史事实）；`PageListPanel` 仅映射既有 QML 面板命名。
- Schema/ports：`src/application`、`src/infrastructure`、`src/domain` 零改动标记 ⇒ wire 加法，未改业务语义；两 handler 未新增 port/查询方法。
- 用户数据：Core 两 handler 与 Rust 两命令均为纯读（无 UPDATE/INSERT/文件发布），React 无写路径 ⇒ 源文件、人工修改、Lock、Revision 未被触碰；`§5.2` 纯 UI 动作边界未被突破。

## 可核验性受限（本会话无法独立证实，请集成方用 git 复核）
1. `614f3f98` 的**精确文件清单**（是否只含本 Task 允许路径、是否零触碰 `src/ui`）——我只做了文本级旁证（无 wire 引用、无任务标记）。
2. `gen/schemas/` 四件与 `permissions/autogenerated/` 两新 toml **是否确实随 614f3f98 入库**（Handoff:26 的 numstat 说法）。注意这些 toml 由 tauri-build 生成，即便未入库，`cargo test` 也会重新生成并通过——raw 日志无法证明入库；`app_acl_manifest_is_generated_and_enforced` 通过仅证明 `acl-manifests.json` 在该 HEAD 下含新命令。
3. `base_commit: 8e8e724b` 与 worktree 起点 `428cd92c` 的关系（Handoff:6 区分 release/base，log 自洽，但无法独立验证）。
4. 工作区是否洁净（无未提交残留）；以及 `68a09251` 是否仅含文档与 raw 日志。

## 放行条件（conditions）
- **C1**：修正 PR-02（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:123/:138` 交叉引用方向）——AC1 落字质量项。
- **C2**：处理 PR-01——在 `library_bridge.rs:812-843` 补 typed 失败断言，或把手递「typed 透传」声称改为「投影形状 + 包装对象」。
- 建议（非阻断，随下次同面改动一并处理）：PR-03 注释归属、PR-04 陈旧计数注释、PR-05 前端命令面镜像同步、PR-06 切书清列表 + 跨书用例；PR-07–PR-11 为 nit/继承项。

---

推荐下一步：由 Codex（Integrator）在放行前先执行上述受限项的 git 复核——`git show --stat 614f3f98` 与 `git show --stat 68a09251`（核对文件范围、生成物入库与 `src/ui` 零接触）——并确认工作区洁净；随后把 C1/C2 作为 r2 返修项回派原作者（Task 保持 `in_review`，`integration_commit` 维持 `null`）。
