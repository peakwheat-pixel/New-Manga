VERDICT: approve

说明（证据可得性）：本会话同样无法执行 git/测试命令，全部结论基于只读文件核对（read/grep/glob）+ 已有 raw 日志只读核对；`14f4b1e6`/`4f8568e3` 的精确文件清单、工作区洁净度无法独立证实（见文末）。

## 逐项判定表（r2 @`14f4b1e6`）

| 项 | 级 | 判定 | 证据 |
|---|---|---|---|
| PR-01 | P2 | **fixed** | `library_bridge.rs:844-856` 新增 Err 分支：`set_domain_result(Err(LibraryError::new("INVALID_REQUEST","validation",false,…)))` + `unwrap_err()` 断言 `code/category/!retryable` 三字段，与 page-resolve 先例 `:800-809` 同构；注释 :844-846 明示 PR-01 由来。 |
| PR-02 | P3 | **fixed** | 契约 `:123` 已改「见**下方** `ListChapters` 行」、`:138` 已改「**上方**原 PROPOSAL 组合行」；方向互换后与表内实际位置（:123 上、:138 下）一致。 |
| PR-03 | P3 | **fixed** | `core_service.py:1545-1547` 三行 resolve 语义注释（publishes…derived read-only root）已下移紧贴 `:1548 if command == "resolve_page_resource":`；导航分支 `:1493-1496` 只保留自身只读语义注释。 |
| PR-04 | P3 | **fixed** | `main.rs:966` 已改 `fifteen production … + the page navigation projections`；`:987-988` 已改 `all 22 commands across the three surfaces (15 production + 4 probe-only + 3 ac1)`；与 `build.rs:37-43`（twenty-two/fifteen）自洽（N-02 为残余精度项）。 |
| PR-05 | P3 | **fixed** | `commandSurface.test.ts:40-49` 数组 8 项（+`list_chapters`/`list_chapter_pages`）；`:211-220` `toEqual` 精确钉 8 项；`:125-130` 补两命令 handler；`:247-256` production 逐个 allow + probe 全 deny；`:10-17` docstring 自述补 rev 1.8（N-03 为残余精度项）。 |
| PR-06 | P3 | **fixed** | `WorkbenchPage.tsx:248/:287` 两 effect 在发起时先 `setChapters([])`/`setPages([])` 再置 busy（与 error 三态互斥兼容，无「no chapters」闪烁，见关键点清单）；测试 `WorkbenchPage.test.tsx:919-947` 双书 fixture 断言切书后 `page-nav-list` 收起 + `chapter-tile-ch-a` 不可见——**但该用例不能隔离新增的清空行**，见 N-01。 |
| PR-07 | P4 | **fixed** | `main.rs:1639-1643` 注记链在 2→3 与 4→5 之间补入 `M2-RC4-DOMAIN-COMMANDS: 3 -> 4 (… DSH r1 PR-07 retro-note)`，与 `core_service.py:135-158` 权威链逐条对齐。 |
| PR-8 | P4 | **fixed** | `WorkbenchPage.test.tsx:949-976` 用延迟 promise 挂住 book-a 回包，切 book-b 后再 resolve；删 `isCurrent()`（:254）会让 `ch-a` 重新出现，`:971` 变红 → 真实判别。 |
| PR-09 | P4 | **fixed** | `PageListPanel.test.tsx:91-109` 用例改名、删除恒真 `expect(onPageIdChange).not.toHaveBeenCalled()`、`:2` 导入仅 `describe/expect/it`（无未用 `vi`）；`:92-95` 明示接线判别力归属集成层。 |
| PR-10 | P4 | **fixed** | `test_page_nav_projection.py:48-49` 已改「two pages … imported one per call (distinct colors so the second import is not dropped by source-hash dedup)」，与 `:66-71` 的逐页 `for` 循环一致。 |
| PR-11 | P4 | **deferred-accepted** | `main.rs:1126-1152` 依旧自引用 `PAGE_NAV_PRODUCTION_ONLY_COMMANDS`；defer 可接受（P4、历代先例共有）。但 r1 所述反向推演不成立：`:1011-1038` 有精确 15 元 vec pin、`:1150-1151` 有绝对 7/6 长度 pin，「删成单成员」会被捕获——残余缺口比 r1 描述更窄，登记独立技术债即可。 |

## 新发现

**N-01（P3）PR-06 判别用例对新增的「立即清空」无判别力** — `apps/desktop/frontend/src/workbench/WorkbenchPage.test.tsx:919-947`（对照 `WorkbenchPage.tsx:248/:287`）
反向推演：删掉 `:248 setChapters([])`（或 `:287 setPages([])`）后本用例仍绿。原因：`onListChapters` 对 book-b 返回 `Promise.resolve`，而 `click` helper（`:112-123`）在 `act` 内 `await nextTurn()`（8 个 microtask）已足以让 book-b 回包落地——同一时序在 PR-8 用例 `:964-965`「click 后立刻断言 ch-b 存在」被直接证明。因此 `:942 chapter-tile-ch-a toBeNull` 由**回包覆盖**保证，而非清空；`:940 page-nav-list toBeNull` 由**既有的** `setSelectedChapterId(null)`（r1 时已正确）保证。即 r1 PR-06 的真正回归点（加载窗口内旧章行可点击）在测试里从未被复现。
建议：仿 `:949` 手法把 book-b 也设为 pending，切书后断言「`chapter-tile-ch-a` 不可见且 `chapters-busy` 仍在」，再 resolve book-b。非阻断（功能修复本身正确）。

**N-02（P4）`main.rs` ACL 文档注释只改了数字，未补 probe 面** — `apps/desktop/src-tauri/src/main.rs:965-968`
该注释自称 app manifest 声明「exactly the live commands (fifteen production … plus three M2-AC1 acceptance)」，仍缺 4 条 probe-only（15+3≠22），与同一测试内 `:987-988` 的 `22 = 15+4+3` 及 `:991-995` 三面清扫范围不自洽。属 1.7 遗留（r1 PR-04 仅要求数字），非本返修引入。

**N-03（P4）`commandSurface.test.ts` 自述与 mock 允许面不全一致** — `apps/desktop/frontend/src/resourceChannel/commandSurface.test.ts:11-12`、`:56-62`
docstring 与 `makeSurfaceInvoke` 内联注释都称 IPC1 pair（`core_ping`/`library_list_books`）、resolve 与 nav 同在生产 arm，但 `:63-68` 的 `available` 只有 `PRODUCTION_COMMANDS`(3)+settings+DOMAIN，**不含 IPC1 pair**（mock 下会被判 deny，只是无用例触发）；且 `:56-62` 内联注释仍写「region command face (retype/read/revision/history/restore/rerender)」，未随 PR-05 补 `resolve_page_resource`/`list_chapters`/`list_chapter_pages`（PR-05 只更新了头部 docstring 与 `:207-209`）。IPC1 部分属既有，非返修引入。

**N-04（P4）`WorkbenchPage.tsx` 悬挂注释残句** — `apps/desktop/frontend/src/workbench/WorkbenchPage.tsx:310-312`
`:310` 以「catalog key and feed the existing image loader automatically…」开头，缺首行（以小写续句起头），紧贴 `:313` 的 resolve effect。纯注释瑕疵，疑似 614f3f98 交付即存在、r1 未列；本返修未触及该行区间，仅登记。

**N-05（P4）`PageListPanel.test.tsx` 新用例名声称的高亮无断言** — `apps/desktop/frontend/src/workbench/PageListPanel.test.tsx:91-109`
改名后为「…with the current-page highlight…」，但只传 `pageId: "p-1"` 让 `tileStyle(true)` 生效，未断言选中态（`PageListPanel.tsx:163` 的高亮样式全仓无判别用例；把 `tileStyle(selected)` 恒为 false 无测试变红）。等于用一个未验证声称替换了 PR-09 的旧未验证声称，建议改名为「renders page tiles for the selected chapter」或补一条背景/选中断言。

## 核对过、未发现问题的关键点

- **召回基线（只读核对，未重跑）**：五份 raw 日志 HEAD 行全部为 `14f4b1e6b05c7fc5cc1f947e1848a1ff411335d7`。数字与 Handoff 声称一致且与 PAGE-RESOLVE 基线自洽：focused `422 passed`（基线 417，+5，`focused-pytest-1.log:21`）；full `1876 passed, 1 skipped, EXIT=0`（基线 1871+1sk，+5，`full-pytest-1.log:399-400`）；cargo `running 56 tests` → `55 passed; 0 failed; 1 ignored; EXIT=0`（基线 54+1ign+1 新桥接用例，`cargo-test-1.log:17,33,39,40,48,75,77`，含 `page_nav_…`/`production_surface_is_exactly_fifteen_commands`/`production_only_commands_stay_off_both_frozen_test_surfaces`/`app_acl_manifest_is_generated_and_enforced` 全 ok，`Compiling m2rc1-desktop` :4）；vitest `136 passed / 12 files / EXIT=0`（基线 124/11 files，`WorkbenchPage.test.tsx` 27→31 = +4、`library/client.test.ts` 7→10 = +3、`PageListPanel.test.tsx` 5 = +5，`vitest-run-1.log:10,17,20,22-23`）；`frontend-build-1.log:13-14` `EXIT=0`。
- **契约 rev 1.8 三处落字自洽**：头部增量块 `:1`、状态行 `:9`、Revision history 七点 `:13`、§5 表 `:123`（转冻结注记）/`:138`（`ListChapters`）/`:139`（`ListChapterPages`）互相一致；DTO 字段集（`chapter_id/title/chapter_number/sort_order`、`page_id/source_filename/sort_order`）与 `core_service.py:950-961/:976-986` 的 handler 投影及 §5 行逐字段一致；「零新错误码 + fail-soft 空数组 + `INVALID_REQUEST` 复用」与 `core_service.py:945-949/:971-975,1502-1517` 一致；「按 `sort_order` 升序」由 repository 既有排序承载、未被本 Task 改写。
- **PR-02 方向修正未波及其他交叉引用**：全仓「上方/下方」grep 中，`:212/:214` 指向 1.5 条目（确在 §5.4 之前）仍正确；`getReaderProjection` 行 `:141` 未被改动。
- **PR-06 立即清空不破坏正常加载路径**：`setChapters([])`/`setPages([])` 与对应 busy 在**同一 effect 批次**提交（React 18.3.1 + `createRoot` 自动批处理，`package.json:14-15`），Panel 的 busy/error/empty 三态互斥（`PageListPanel.tsx:138-152`、`:169-183`），过渡态渲染 `chapters-busy`/`pages-busy` 而非 `…-empty`；错误路径 `WorkbenchPage.tsx:259-266/:298-305` 仍以 error 态呈现。反向风险（清空导致 busy/error 失真）不成立。
- **PR-05 镜像矩阵自洽**：`DOMAIN_PRODUCTION_ONLY_COMMANDS` 8 项精确 pin、production 8 命令逐个 `resolves`、probe 8 命令逐个 `rejects`，与 Rust 侧 `PRODUCTION_COMMANDS` 15 = 3+2+2+2+3+1+2、生产-only 族总长 12、probe/ac1 形状 7/6（`main.rs:1150-1151`）一致；Rust 侧注记链/ACL 面（`main.rs:75-76,134,826-869,1035-1036`、`build.rs:57-86`）三视图同步。
- **PR-07 注记链完整性**：`main.rs:1636-1648` 与 `core_service.py:135-158` 覆盖 0→1→2→3→「1.5 不 bump」→4→5→6，无缺条目；真实 sidecar 断言 minor 6（`:1648`）。
- **PR-10 与实现一致**：`_seed_core` 逐页 `import_files` 两次调用 + 不同颜色（`test_page_nav_projection.py:66-71`），文件共 5 用例（`:75/:84/:107/:125/:146`），与 Handoff 声称一致；`:116` 断言 `page-a.png/page-b.png` 顺序。
- **PR-11 修正（对 r1 的自我更正）**：`production_surface_is_exactly_fifteen_commands`（`:1019-1038`）以精确 vec 钉住 15 条生产命令含两新命令；`probe_surface_…`/`ac1_surface_…` 的算术式虽自引用族常量，但 `production_only_commands_stay_off_both_frozen_test_surfaces` 另有 **绝对** 7/6 长度 pin（`:1150-1151`）。r1 PR-11 的「删成单成员仍全绿」不可复现：该突变使 `command_allowlist(true,false).len()` 变 8，`:1150` 直接失败。故 defer 不仅可接受，且残余缺口比 r1 描述更窄。
- **可核验性受限**：本会话无 git/测试执行能力，故 (1) `14f4b1e6` 精确文件清单与是否零触碰允许范围外路径、(2) `4f8568e3` 内容（文档+日志入库）、(3) 工作区洁净度，均只能用文本旁证，未能独立证实；建议集成方按 r1 受限清单在合并前补 `git show --stat`。

推荐下一步：由 Codex（Integrator）在放行前执行受限项的 git 复核（`git show --stat 14f4b1e6` 与 `4f8568e3`、工作区洁净），通过后即可把 Task 置 done 并落地 `integration_commit`；N-01/N-05 建议作为同面测试加固项（可顺手在 PR-06 判别用例上补延迟 promise），N-02/N-03/N-04 为 P4 文档 nit，可并入下一次同面改动或技术债 Task，无需单独释放 Task。
