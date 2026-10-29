# 独立审查报告 · V11R-B-1 / V11R-B-3

**审查者**：reviewer（独立、只读，未参与实现）
**审查基准**：已全读 `FUSION_SPEC.md`、`DESIGN_SYSTEM.md`、`V11R_AVALONIA_CONTRACT.md`、`V11R_SCREEN_SPECS.md`、`V11R-B-1.md`、`V11R-B-3.md`
**审查方式**：把两个交付 commit 用 `git archive` 提取到 `%TEMP%` 阅读（未改动任何 worktree 文件、未 commit、未 push、**未运行任何构建/测试** → 两条分支的 build/test log **均未由我重跑**，只做日志与代码的一致性抽查）。
**被审对象（pin）**：B-1 = `35f4dfd29`；B-3 = `b265e306b`（实现 `4317624b1`）。

> ⚠️ 审查期间两个分支都在动：`V11R-UI-SHELL` 的 HEAD 已从 `35f4dfd29` 前进到 `16449bfa0`（B-2 Console WIP `b4a75d724` + merge main `b12aaa819`），工作树有未提交 B-2 改动；`V11R-UI-STUDIO` 的 HEAD 已是 `c452c28c8`（post-delivery 修了 `queued` 符号 + merge main）。本报告按用户指定的 pin 审查，并标注"pin 之后已修"的项。

---

## 一、分支结论

| 分支 | 结论 | 一句话理由 |
|---|---|---|
| **V11R-B-1**（`35f4dfd29`） | **PASS_WITH_ISSUES** | 外壳/Library 主体真实可用、令牌纪律好、诚实降级到位；但证据目录 135 个文件中 **57 个是其他 11 个任务的字节级复制品**（P1），且"滚动保留"证据是同义反复、C# 层裸设计值绕过 conformance 扫描。 |
| **V11R-B-3**（`b265e306b`） | **FAIL（需返修后复审）** | 读链/降级/写门禁诚实且测试扎实，但**画布 Region 的鼠标选中与 hover 链路在实现层被自己关掉**（P1 用户可见），且证据把未实现的"Modal 默认焦点=取消"写死成 JSON 字段、把从未渲染的 hover 写进 `region-badges.json`（P1 证据不可信）；AC4（C#/样式表裸间距）、AC5（焦点管理）实际未达成。 |

---

## 二、问题清单

### 2.1 V11R-B-1（`35f4dfd29`）

| 级别 | 位置 | 问题 | 依据 | 建议修法 |
|---|---|---|---|---|
| **P1** | `verification/V11R-B-1/**`（共 135 个文件，其中 57 个与他任务字节相同） | 交付 commit 把**其他 11 个任务的证据整包复制**进本任务证据目录：如 `credential-ui/put-create.json` ≡ `verification/CREDENTIAL-UI-1/…`；`commands/run-binding-*.db`(+WAL 4.2MB) ≡ THEME-MACOS-1；`diagnostics/*` ≡ HOST-COMMAND-MIGRATION-1；`screenshots/*` 为 THEME-MACOS 主题截图。证据目录 42% 与本任务无关，含 4 个 SQLite 二进制。**复现**：`git -C <wt> ls-tree -r 35f4dfd29` 后用 blob hash 与其他任务比对（我实测：identical 57 / unique 78；来源分布 SETTINGS-PROFILE-UI-1 ×9、CREDENTIAL-UI-1 ×7、PDF-EXPORT-UI-1 ×6、READER-SELECTOR-UI-1 ×5…） | AC7「证据：verification/V11R-B-1/」；协作协议证据归属 | 删除全部外任务文件（尤其 `*.db`/`*.db-wal`），重生成证据并单独 evidence commit；复查 `git add -A` 是否又扫入 |
| P2 | `Shell/V2/ShellState.cs:301`（`SetScroll`）+ `V2ShellUiTests.cs:202,218` | **"切换空间保留滚动"没有生产者**：`SetScroll` 全仓库只有测试在调用；`LibraryView.axaml.cs` / `LibraryViewModel` 均不写回/恢复 `ScrollViewer.Offset`。测试先手动 `SetScroll(…,320)` 再断言仍是 `320` —— **同义反复**，不证明行为。真正保留下沉为"视图实例未销毁"（隐式、未断言） | SCREEN_SPECS §0「不重置滚动与选择」；AC2；契约 §6.1「各空间滚动与筛选」 | 在 Library/Studio 的 ScrollViewer 上订阅 `ScrollChanged` 写回 `SpaceViewState`，`OnActivated` 恢复；测试断言**真实 ScrollViewer.Offset** 跨 Ctrl+1/2/3 往返保持 |
| P2 | `ViewModels/V2/Shell/AppShellViewModel.cs:307-311`、`Library/LibraryViewModel.cs:400-403,829-841,450` | **C# 层裸设计值**且注释自承是为"让 XAML 没有魔法值"：`PaletteWidth=560`、`ConfirmWidth=480`、`SearchBoxWidth=220`、`SortBoxWidth=120`、断点 `1400/1200`、面板 `360/340/300`、卡片 `272/240/200`、间距 `12/8`、`IsCompact = width < 1200`。`V2ConformanceTests.cs:57-69,79-105` **只扫 `.axaml`**，且不扫 `Margin/Padding/Spacing/BorderThickness/Opacity/Brushes`；`CornerRadius` 正则 `"([4-9]|\d\d+)` 漏 `"0,0,4,4"` 这种 4 值写法 | 契约 §2.2「组件 **XAML/C#** 中禁止裸色值/裸字号/**裸间距**」+ §2.4 未登记；AC4 | 迁到 `Nm.Size.*/Nm.Padding.*/Nm.Space.*`；把断点提为常量并入 §2.4 或改 spec；conformance 扫描扩到 C#（排除 tests）并补上述模式 |
| P2 | 同上 | **响应式断点三套**：spec 为 1600/1280（FUSION §6），B-1 用 1400/1200，B-3 用 1600/1400/1280。1280–1599 下 B-1 的 Library 详情栏按 1200 判定，与"≥1280 三列/胶片条 56"的口径错位 | FUSION_SPEC §6；SCREEN_SPECS §1 验收「1600/1280/1024 三档」 | 统一断点常量（建议 `Nm.Size.Breakpoint.*`），或由 Lead 在 DECISION_LOG 裁定后同步 spec |
| P2 | `Views/V2/Library/LibraryView.axaml:117-126` | **loading 态没有骨架，但界面文案声称有骨架**：只渲染"正在读取书架…"两行文字，同时显示"骨架保持书卡网格布局，不使用整页 spinner"。既没有占位书卡，也没保留网格几何 | DESIGN_SYSTEM §7 硬规则 1「loading（骨架保持布局）」、§9.8 | 渲染 N 个 96–140px 占位卡（同 `ItemWidth/ItemHeight`），删除自证文案；补 loading 截图 |
| P2 | `ViewModels/V2/Library/ImportDockViewModel.cs:139,159`（及类注释 `:12-13`） | 无章节时通知用户「"新建章节"为能力待接入」，但实现早已走真实 `CreateChapterAsync`（D-11、测试 `ImportDock_WithoutChapter_*` 通过）。**对用户低报能力**，与 DEVIATIONS D-11 自相矛盾 | AC1 诚实性（反向：不得把已接能力说成未接）；D-11 | 改为「请先新建章节（走 Core CreateChapter）」并同步类注释；`NOT_WIRED.md` 复核 |
| P2 | `Shell/V2/**`（缺失 `IWorkspaceView`） | 契约 §6.1 定义的 `IWorkspaceView{Space,CreateContent,OnActivated(ShellState),OnDeactivated(ShellState)}` **在两个分支中都不存在**（B-1 属其写域却没定义；B-3 只能自造 `Activate/Deactivate`，并在 `StudioWorkspaceView.axaml.cs:17-20` 注明"接口不在本分支"）。导致 scroll/filter/焦点恢复没有挂载点，直接造成上一条 P2 | 契约 §6.1；§1.2 写权 `Shell/V2/**` = ui-shell | ui-shell 补 `Shell/V2/IWorkspaceView.cs`；`AppShellViewModel.SwitchSpace/SetStudioMode` 调用 OnDeactivated→OnActivated；两工作面实现 |
| P2 | `verification/V11R-B-1/AC_COVERAGE.md` vs `V2ShellUiTests.cs:165-187,173` | **证据强度夸大**：AC_COVERAGE 写「1600 四列 / 1280 三列断言」，实际 1600 用例**没有** `ColumnCount` 断言（只在 `:484` 断 1280=3）；TopBand 用 `Bounds.Height >= 32` 而规格是 36（32 也通过） | AC7/证据可信度 | 补 `Assert.Equal(4, ColumnCount)`、`Assert.Equal(36, topBand.Bounds.Height)` 或改证据措辞 |
| P3 | `Shell/V2/Statuses.cs:28` | pin 处 `queued` 用 `◦`，冻结源是 `DESIGN_SYSTEM §2.2` + `tokens.json stateSymbols.queued="·"`；`DEVIATIONS.md D-8` 还把事实说反（称"契约是 ◦ / tokens.json 是 ·"）。**pin 之后已修**（`b4a75d724` 改为 `·`），但塞在 B-2 提交里、D-8 未更新 | DESIGN_SYSTEM §2.2；契约 §2.3 | 单独 fix commit + 更新 D-8 + 重生成 conformance/证据 |
| P3 | 交付可追溯性 | 审查期间工作树出现 B-2 未提交改动、证据 `verification/V11R-B-1/NOT_WIRED.md` 在 `35f4dfd29..16449bfa0` 的 merge 中被修改（第 9 行）→ **交付证据未冻结** | 契约 §7 证据与 commit 对应 | Lead 要求 B-1 冻结 pin；后续任务另开分支，证据改动必须新 commit |
| P3 | `Shell/V2/ShellCommands.cs:49-50`；`Views/V2/Shell/AttentionMenu.axaml:16`；`ScopeSelector.axaml` | 死代码/误导：未引用的 `NotWiredCreateChapter` 常量；隐藏的假计数 `Text="4" IsVisible="False"`；"作用域**选择器**"实为只读 Flyout（FUSION §2.3 称选择器），未进 NOT_WIRED | 契约 §6.2；§9.6 | 清理；若要保留只读语义，在 NOT_WIRED 记「作用域切换待 B-4」 |
| P3 | `Shell/V2/AppShellV2.axaml.cs:44-51` | 主题管理器：构造时若未注入则 `new + Initialize()`，若注入则**不 Initialize**，只 `SetAppearance` → 两条路径行为不一致 | 契约 §4 行为约束 | 统一：注入也调用 `Initialize()`（幂等）并在测试中断言 |
| P3 | `Views/V2/Shell/TopBand.axaml:55-64` | 顶带同时有"主题"（打开 C-2 占位）与"深色/浅色"立即切换，两个主题入口语义重叠，与 `Ctrl+,` 三个入口并存 | DESIGN_SYSTEM §6.2 TopBand | 保留一个主入口 + 一个快速切外观，或合并 |

### 2.2 V11R-B-3（`b265e306b`）

| 级别 | 位置 | 问题 | 依据 | 建议修法 |
|---|---|---|---|---|
| **P1** | `Views/V2/Studio/Controls/StudioRegionOverlay.cs:105`（`IsHitTestVisible = false`）→ `:58-64` 的 `PointerEntered/PointerExited/PointerPressed`、`:134` 的 `hovered => HoverRegion` | **画布 Region 的鼠标选中与 hover 在实现层被关闭**：父级 Canvas 设 `IsHitTestVisible=false` 后整棵子树不参与命中测试（虽注释写"hit-testable only on the region boxes themselves"，实现相反）。RegionBox 的 3 个指针处理器成为死代码；`HoverRegion` 无产品调用者。**用户后果**：在 Studio Page 模式里**鼠标点画布上的 Region 无反应（被 `StudioCanvasViewport.cs:278-290` 解释为拖拽平移）**，hover 永不高亮；只能靠 `J/K`（还需焦点在画布列）或 HUD。`.hovered` 样式（`StudioTheme.axaml:180-183`）永不激活 | SCREEN_SPECS §3「Region 覆盖…选中描边/hover 半亮」；FUSION §4；AC1 | overlay 保持可命中但自身 `Background=null`（空区不拦截），仅 Box 命中；Box `PointerPressed` 设 `e.Handled=true` 阻止平移；补 headless 指针测试（对 Box 发 PointerPressed 断言 `SelectedRegion` 变化 + hovered class），并在 README 去掉未实现的 hover 断言 |
| **P1** | `verification/V11R-B-3/leave-modal.json` 的 `modal_default_focus:"取消"` + `V2StudioPageTests.cs:443` 写死 `writer.WriteString("modal_default_focus","取消")`；`StudioLeaveModal.cs` 全文无 `Focus()` | **证据把未实现的行为写成事实**：全分支无任何 `Focus()` 调用（grep 0 命中），无焦点陷阱、无关闭回焦；Modal 内三个出口按钮无法用键盘到达（Tab 在 Studio 被 HUD/模式切换消费）。JSON 字段是**字面量常量、零断言**，README §2/§5 亦据此声称"默认焦点=取消" | DESIGN_SYSTEM §6.2 Modal「默认焦点在取消」、§8「浮层打开焦点入首项、Tab 循环、关闭回焦」；AC5 | 实现 `CancelButton.Focus()`（Loaded 优先级）+ 焦点陷阱 + Esc=取消 + 关闭回焦；测试断言 `FocusManager.GetFocusedElement()` 后再写 JSON，**禁止**写死字段；删除或改错该证据文件 |
| P2 | `Views/V2/Studio/Controls/StudioLeaveModal.cs:42` | **保存失败的错误文案不可见**：`Foreground = Brushes.Transparent` 是本地值，优先级高于 `meta` 样式 → `LeaveError` 显示为透明文字（用户看不到"保存失败：CODE"），与 README「保存失败留在 Modal 并就地报错」矛盾 | DESIGN_SYSTEM §7「错误必须可从发生位置定位」 | 删除本地 Foreground，改用 DS 样式类（如 `studio-banner-error` 内的 `Nm.Color.Status.Failed`），加断言（渲染帧像素或样式解析） |
| P2 | `ViewModels/V2/Studio/StudioSelection.cs:157-173` + `V2StudioMathTests.cs:223-228` | **显式多选被 Region 遮蔽**：已框选 2 页时 `SelectionSummary` 仍返回"当前 Region"；测试**把该行为断言成规范**（`:225`），再手动 `CurrentRegionId=null` 才得到"选中 2 页"（`:227-228`）。`context-retention.json` 的 `multi_page_scope:2` 因而与 UI 作用域文案冲突 | FUSION §1 硬规则 1「Batch 框选 3 页，切 Page 后作用域仍是这 3 页」；§2.3 作用域后缀；§9.6「看不出作用域的操作」 | 引入显式 `ScopeKind`（Chapter/SelectedPages/Page/Region）并让显式多选优先；B-4 批量动作统一消费同一枚举；更新测试断言为"选中 2 页" |
| P2 | `Views/V2/Studio/StudioTheme.axaml`（`Padding` 裸值 :90,117,124,131,136,148,155,165,171,198,204,215,267,285,310；`Width="480"` :328；`Width/Height="8"` :288-289）+ C# 几何常量 `StudioPageWorkspace.cs:66,137,213,280`、`StudioInspectorPanel.cs:66,109,416`、`StudioWorkspaceView.axaml.cs:54,195`、大量 `new Thickness(...)` | **AC4 在 B-3 不成立**：样式表与 C# 都有裸间距/裸尺寸；且 B-3 **没有等价 conformance 扫描测试**（只有 `build.log 0 warning`，与裸值无关）。`verification/V11R-B-3/design-system-usage.md` 内容损坏（6 处 `System.Object[]`），无法核对 README 宣称的"40 token / 10 DS Classes / 51 本地类"（我手工计数 ≈38 token、58 个样式选择器，数量级相符但证据不可审计） | 契约 §2.2 硬规则 + AC4 | 样式/几何迁 `Nm.Size.*/Nm.Padding.*/Nm.Space.*`；新增 Studio conformance 测试（XAML + C#）；修生成器（`string.Join` over `object[]` → `Select(x=>x.ToString())`）后重生成该 md |
| P2 | `StudioPageWorkspace.cs`（无 loading 骨架）；`states.json`/README | AC3 六态只落地 5 态：empty/error/partial 有三图，"loading"仅 `PageImageNote` 文本，**无 loading 截图/无断言**；idle 亦无断言 | DESIGN_SYSTEM §7；AC3 | 胶片条/检查器占位骨架 + `IsLoading` 断言 + `state-loading.png` |
| P2 | `Views/V2/Studio/Controls/StudioPageWorkspace.cs:174-202`（host banner + error banner + 中心错误卡）；`:186-190` 纵向 StackPanel 里的重试按钮被拉满整行 | **同一错误三重复呈现**（见 `state-error.png`：两条同样的"Host 未就绪(Failed)"横幅 + 一张"页面读取失败/重试"卡），且重试按钮渲染成整行宽的强调色条，视觉噪音 | DESIGN_SYSTEM §7、§9（层级只用明度+描边、避免冗余装箱） | 合并为 1 个就地错误块（错误码→摘要→建议动作→重试）；host 未就绪只留一条 banner |
| P2 | `ViewModels/V2/Studio/StudioPageViewModel.cs:748-838,878-953` | **错误路径不完备**：`LoadAsync` 只 `catch (OperationCanceledException)`；`LoadPageCoreAsync` 用 `Task.WhenAll(...).Result`。Host 抛出的 `InvalidOperationException`/`SidecarException`（App 其他 VM 都按这两类捕获，见 `LibraryViewModel.cs:525`）会逸出到 async 视图调用（可能未观察异常/崩溃），error 态实际只能由"返回 null/Host 未就绪"触发 | AC3「error 可就地 + 可重试」 | 捕获同两类异常 → `LoadState=Error/Partial` + `ErrorText`；`WhenAll` 改 try 包裹并按"哪一路失败"给 partial 原因 |
| P2 | 全分支无 `.Focus()`；`StudioKeyboard.cs:18-21` 在 Studio 内把 Tab 交给 HUD/模式切换（`StudioWorkspaceView.axaml.cs:156-161`）；检查器/胶片条/Modal 无焦点可达路径 | **AC5「键盘可达」不成立**：Tab 被占用后没有替代焦点遍历，键盘用户无法到达检查器五个页签、胶片条、Modal 出口 | DESIGN_SYSTEM §8；AC5 | Tab 仅在"画布/HUD 上下文"接管（有 Region 且焦点在画布列时），其他区域恢复系统 Tab；或提供 `F6`/方向键焦点环替代并写进 spec（需 Lead 裁决） |
| P2 | `V2StudioMathTests.cs:110-113` | 测试断言 `Assert.Equal("◦", StudioStates.Glyph(Queued))` 并注释为"frozen contract vocabulary" → **测试把违规固化为规范**。`DESIGN_SYSTEM §2.2` + `tokens.json` 均为 `·`；pin 之后已由 `5da974cd1` 修正（代码+测试同步），但 pin 版本不满足 | DESIGN_SYSTEM §2.2 / tokens.json；契约 §2.3 | 已在分支修；需重跑并重生成证据（当前 `verification/V11R-B-3` 仍是 `◦` 时代产物） |
| P3 | `ViewModels/V2/Studio/StudioPageViewModel.cs:984-1020` | `RequestSelectPage` 与 `SelectPageAsync` 的"未保存守卫"逻辑重复；`SelectPageAsync` 忽略 `LoadPageCoreAsync` 返回值恒 `return true`（`:1018-1019`），`MovePageAsync` 同样忽略，失败时调用方无法感知 | 可维护性 | 合并成一个守卫入口，返回真实加载结果 |
| P3 | `StudioPageViewModel.cs:1639-1644`（`BuildGate` 仅在构造/Load 时重建，不订阅 Host 状态） | Host `Starting→Ready` 后写门仍为禁用，直到下次 `LoadAsync`；只读切换同理 | AC1 降级准确性 | 订阅 `IHostController` 快照变更刷新 gate（或每次写前重算） |
| P3 | `StudioUi.cs:227-232`（`Hairline()` 未使用且返回 `Opacity=0.0` 的 Separator）；`StudioWorkspaceView.axaml.cs:45-46`（空函数体 + "Temporary Nm.* token shim" 遗留注释）；`StudioHudRing.cs:63`（`ReOcrRegion` 映射到 `StudioCommand.CreateRegion`） | 死代码/错误映射/误导注释 | 可维护性、契约对齐 | 删除/修正 |
| P3 | `region-badges.json` `states:"selected + hover + locked + failed"`；`wired-writes.json` `"ac":"AC2"` | 证据字段不准确：hover 从未渲染也从未断言（测试只设 `IsLocked/HasFailed`，`V2StudioPageTests.cs:629-648`）；AC 标号错写 | 证据可信度 | 修正证据字段并补 hover 断言（依赖 P1 修复） |
| P3 | `StudioHudRing.cs:58-65`（HUD glyph = T/Y/H/R/U/O/L/D）、`StudioInspectorPanel.cs:45-49`（页签用 文/样/修/锁/史）、`:272,490` 与 `:102` 硬编码 `▮`/`✗` | **图标体系完全缺失**：用无意义字母/汉字占位代替 1.25px stroke 图标；DEVIATIONS/NOT_WIRED 未登记该视觉偏差（只登记了能力缺失）；`▮` 符号在 3 处硬编码，违反"UI 不得自造符号"的单一来源要求 | DESIGN_SYSTEM §5（图标 1.25 stroke、禁 emoji/彩色）、§2.2（符号单一来源） | 在 DEVIATIONS 登记"图标集待 DS 交付"；把 `▮/✗` 收敛到 `StudioStates`；DS 上收后替换 |

---

## 三、已核实正确的关键点

### V11R-B-1
1. **单一键盘注册表**：`KeyMap.cs:87-97` 启动断言、`:99-130` 冲突检测、`:43-44` 作用域判定；`Tab` 只在 `SpaceId.Studio` 注册（`ShellCommands.cs:64`）；单测覆盖全量快捷键与冲突（`V2ShellCoreTests.cs` 中 `KeyMap` 组 5 条）。
2. **IME 让位**：`AppShellViewModel.cs:655-663` + `:1149-1164` 输入框聚焦时字母/方括号/空格让位，Ctrl/F/Esc 仍生效；有专门测试（`V2ShellUiTests.cs:262-282`），且 `AppShellV2.axaml.cs:114-122` 从真实焦点推导 `textInputFocused`。
3. **Esc 逐级**：`AppShellViewModel.cs:795-870` 顺序为 Confirm→Palette→Jump→Help→Reader→ThemeStudio→Recycle→CreateBook→多选→页→章→书→浮层；测试覆盖 Modal/回收站两级（`:411-416`）。
4. **导入诚实**：`ImportDockViewModel.cs:314-359` 每文件一次真实 `ImportFilesAsync`，行状态来自真实 `outcome`（导入/跳过重复/失败+错误码），文件夹明确标注"聚合结果"；测试断言调用数 3→4、目标章节、重试只跑失败行（`:317-349`）。
5. **危险动作不假成功**：`LibraryViewModel.cs:1100-1110` 回收站确认 `CanConfirm:false` + 原因，确认按钮禁用；测试断言确认被拒后只出提示、不写数据（`:390-419`）。
6. **新建章节真实调用**：`LibraryViewModel.cs:773-823` 走 `CreateChapterAsync`，失败带 typed code，成功后刷新并选中；测试断言 host 调用与请求体（`:353-387`）→ 关闭审计 F011。
7. **令牌纪律（XAML 侧）**：V2 全部 `.axaml` 无裸色值/裸字号/裸尺寸/`CornerRadius>3`/阴影/渐变/模糊（我逐文件正则扫描 + `conformance/v2-tokens-and-classes.json`：23 文件 / 48 个 `Nm.*` 键 / 34 个 Classes）；`V2LocalStyles.axaml` 全量 `{DynamicResource}`（仅 `Padding="0"`、`MinHeight="0"`、`Padding="4,1"` 三个例外）。
8. **架构边界**：生产代码无 DB/文件/进程/HTTP 直连（grep：`System.IO.File`/`Directory.`/`Sqlite`/`Process` 仅出现在测试证据写入），全部经 `IHostController`。

### V11R-B-3
1. **真实读链**：`StudioPageViewModel.cs:748-953`（`LoadReaderBook→ListChapterPages→LoadPageRegions+ReadPageImage→LoadRegionRevisions`）；测试断言 host 侧调用集合（`V2StudioPageTests.cs:66-69`）并断言页面图确实解码（`:90`）。
2. **几何正确**：百分比→页面像素→渲染缩放有独立纯逻辑测试（`V2StudioMathTests.cs:16-88`），且断言渲染位置 `Canvas.GetLeft == 120*0.86`（`:95-96`）；我目视 `page-mode-1600x1000.png`，Region 框与页面面板对位一致。
3. **写面诚实收敛**：仅 3 条已接入命令（`StudioCapabilities.cs:48-53`），其余 15 条 F0-1 命令 + 4 把锁 + pin + 成品/分屏 全部 `IsEnabled=false` + tooltip"能力待接入"；测试断言 **零写调用**（`:292-298`）与 `not-wired.json write_calls:0`。
4. **读面缺失不伪造**：`NotWiredRegionTextSource/FlagSource` 返回 `null`（`StudioCapabilities.cs:135-150`），四级文本显示"能力待接入"+"—"，无假文本；锁/失败角标默认不出现并在测试中验证"产品路径不发明角标"（`:653-658`）。
5. **未保存 Modal 三出口**：`StudioPageViewModel.cs:1560-1623`（取消保留编辑 / 放弃丢弃并继续导航 / 保存走 set_region_type 后继续），测试三路径齐全（`:396-431`）。
6. **主题切换不影响页面像素**：真实渲染裁剪 + 逐像素 diff（`V2StudioPageTests.cs:676-767`）；`theme-canvas-before/after.png` 为同一 blob（diffPixels=0 必然成立，方法本身有效），而 `theme-window-before/after.png` 字节不同 → **证明主题确实切换了**，不是空操作。
7. **Batch 诚实占位**：不画矩阵/进度，"开始处理"禁用 + NOT_WIRED + 说明（`StudioWorkspaceViewModel.cs:59-65`、`StudioWorkspaceView.axaml.cs:191-221`）。
8. **架构边界**：不直连 DB/文件（同上 grep），不修改 `AppShellV2/ShellState/KeyMap/MainWindow`（实现 commit 仅动 Studio 目录 + tests + evidence）。

---

## 四、UNVERIFIED（只读环境无法确认）与建议验证

| 项 | 原因 | 建议验证方法 |
|---|---|---|
| 两条 workflow 的 build/test log 真实性 | 纪律要求不写 bin/obj，未重跑 | 由 Lead 在集成机上 `dotnet build NewManga.sln -warnaserror` + `dotnet test NewManga.sln --no-build` 重跑并 diff 计数（B-1 预期 App 178/2；B-3 预期 App 166/2、V2Studio 21/21） |
| **B-3 的 Tab/Esc 键盘测试为何能通过** | `HudRing_TabCycles`（`V2StudioPageTests.cs:451-503`）在 1600 宽下按实现应先"收起检查器"（`StudioKeyboard.cs:79-100`，`InspectorExpanded` 默认 true），却直接断言 `SelectedRegion==null`。Avalonia headless 的 tunnel/bubble 与 `KeyboardNavigationHandler` 顺序无法静态确定 | 单跑该测试并加断言：第一次 Esc 后断言 `InspectorExpanded==false && SelectedRegion!=null`，第二次 Esc 才清选区；若失败说明该测试原本靠未声明的前提通过 |
| B-3 画布点击选中（P1）的运行期表现 | 由 `IsHitTestVisible=false` 静态确定不可用 | 用 `Avalonia.Headless` 对 `RegionBox` 发 `PointerPressed` 断言选中；或真实窗口点击录像 |
| 真实 Core E2E（空库→建书→建章→导入 2 页→重启可见） | 两分支 README 均标 NOT RUN（无 sidecar） | INT-1 用 `V11R-F0-1`/sidecar 环境补 E2E；不要把 FakeHostController 断言当 E2E 证据 |
| 100/150/200% DPI | 双方均未验证（headless 无 DPI 模拟） | 真实桌面三档缩放跑 `01/11/12` 与 Studio 三档截图 |
| 截图内容代表性 | 页面图为 SkiaSharp 合成 fixture（已诚实标注"fixture art"），非真实漫画 | 用真实漫画页（不同尺寸/长图）重截，验证 `Uniform` 缩放与叠加层对位 |
| `theme-canvas-*` 方法外推 | 只裁剪页面图区域（排除 2px 描边与底部带），且测试把 overlay/HUD `Opacity=0` | 证据里注明裁剪范围与遮罩处理；C-2 再做整窗主题验收 |

---

## 五、跨分支发现

1. **两套选择模型，无一接线（最高集成风险）**
   `ShellState.Selection`（`ShellSelection`，含 `MultiPage`，`ShellState.cs:32-113`）与 `StudioSelection`（`StudioSelection.cs:33-182`，含 Book/Chapter/Page/Region/多选/Zoom/SurfaceMode/InspectorTab）**互不相识，无适配器**。而契约 §6.1 规定 `ShellState` 是唯一状态源。后果：FUSION §1 硬规则 1 在集成后必然不成立；两套作用域文案优先级还不同（`AppShellViewModel.ScopeText` 多选优先；`StudioSelection.SelectionSummary` Region 优先）→ 同一 selection 在两个顶带显示不同作用域。**建议**：INT-1 前由 DSH 裁决单一模型（建议 `ShellState.Selection` 为权威，Studio 侧改为投影/双向绑定），并把 `Zoom/Offset/SurfaceMode` 归入 `SpaceViewState`。
2. **`IWorkspaceView` 缺失（契约 §6.1 未落地）**：两分支均无该接口；B-3 明确写"接口不在本分支"。INT-1 必须新增并让 Library/Studio/Console 三个工作面实现，否则 §6.1 的 `OnActivated/OnDeactivated` 契约空洞。
3. **键盘注册会互相吃掉（实测风险）**
   shell 在 `AppShellV2` 用 **TopLevel tunnel** 统一拦截（`AppShellV2.axaml.cs:71,114-122`），且 `Tab`（`ShellCommands.cs:64`）与 `Esc`（`:79`）是全局/工位注册项 → 集成后 **Studio 的 `Tab`（HUD 环）与 `Esc`（Modal→检查器→选区逐级，`StudioKeyboard.cs:26-29,79-100`）将永远收不到**；B-3 的 `[ ]`/`+/-`/`0` 又未进 `KeyMap`（与 Library 的 `[`/`]` 翻页语义并存）。**建议**：`IWorkspaceView` 增加 `TryHandleKey`，shell 在 Studio 空间把 `Tab/Esc/J/K/[ ]` 先交工作面；或把 Studio 的这些键按 `StudioMode` 注册进 `KeyMap` 并删除 Studio 自带监听。
4. **重复实现清单（上收 DS 的候选）**
   状态符号表 ×2（`Statuses.cs:25-37` vs `StudioStateKind.cs:27-38`）+ Studio 内硬编码 `▮/✗`（`StudioInspectorPanel.cs:272,490`）；`ObservableObject` ×2（`Shell/V2/ObservableObject.cs` / `StudioObservable.cs`）；Modal ×2（`ConfirmModal` / `StudioLeaveModal`，焦点行为还不一致：前者聚焦取消、后者完全不聚焦）；证据写入器 ×2（`StudioEvidence` 落仓库 vs `V2ConformanceTests.EvidenceRoot` 落 `%TEMP%`）。DS 目前**没有任何自定义控件**（`NewManga.DesignSystem/` 只有 Themes/Styles/Generated，无 `Controls/StatusGlyph`），所以 D-3 降级本身合理，但 §3.2 的 M3 上收必须在 INT-1/DS 补齐：`StatusGlyph/StatusBadge/Kbd/EmptyState/AlertBanner/Modal/图标集/2px 焦点环`。
5. **`queued` 符号契约冲突（已裁决、未统一落地）**：pin 时两分支都是 `◦`，main `b12aaa819` 已把契约改为 `·`（与 DESIGN_SYSTEM §2.2 / tokens.json 一致）；studio `5da974cd1`、shell `b4a75d724` 已改，但 **两支的 devitation/证据未同步重生成**（B-1 D-8 仍写反、B-3 证据仍是 `◦` 时期产物）。合并前必须统一并重冻结证据。
6. **MainWindow/外壳接线**：`V2WorkspaceHost.axaml:14` 仍挂 `StudioPendingView` → 集成必须替换为 `StudioWorkspaceView` 并删除 pending 视图；`MainWindow.axaml` 仍属 INT-1，两分支都没动（符合契约）。
7. **DS 上收与主题引擎**：两支都只用 `{DynamicResource Nm.*}`（B-1 XAML 全清、B-3 样式表大部分清），但 DS 缺 `Nm.Size.*` 之外的断点/图标/命令面板宽度等语义，导致两边都在 C# 里造数字（见各支 P2）。建议 DS 增补：断点、图标、CommandPalette/Modal 宽度、HUD slot 之外的语义尺寸。
8. **证据落盘约定不一致**：一个（B-1）依赖 `NEWMANGA_EVIDENCE_DIR` 环境变量、默认 `%TEMP%`；另一个（B-3）默认解析仓库根 → 同为 L3 证据，复现方式不同，容易"证据写在临时目录却声称已提交"。建议统一到 `verification/<TASK-ID>/` 且测试失败时不得写半成品。

---

## 六、最终判断

### 是否可合入 main：**否（两条分支均不满足合入条件）**

- **V11R-B-1**：合入前必须完成 ①清理 `verification/V11R-B-1/` 57 个外任务证据与二进制 DB 并重新提交证据；②补 `IWorkspaceView`（本任务写域）；③把"滚动保留"变成真实实现+真实断言（或降级为显式偏差说明）；④处理 C# 裸设计值与断点统一；⑤`queued` 单独 fix commit + 更新 D-8（分支已改，需落在独立提交并重生成证据）。以上多为**卫生/证据/契约补齐**类，返修面清楚。
- **V11R-B-3**：合入前必须完成 ①修复画布 Region 命中（P1 用户可见：鼠标点选 Region 不可用）；②Modal 焦点实现 + 删除写死的证据字段（P1 证据不可信）；③修复透明错误文案；④AC4（C#/样式表裸间距）与 AC5（焦点可达）补齐，或由 Lead 在 DEVIATIONS 里**明确登记为遗留并写清用户后果**；⑤重跑并重生成全部证据（含 `queued=·`、`design-system-usage.md` 修复）。其中 ①② 属阻塞项。
- **另需 Lead 处置的流程问题**：审查期间 B-1 分支 HEAD 前进到 `16449bfa0` 且工作树含 B-2 未提交改动、证据文件被后续 merge 修改 → B-1 的交付 pin 需重新冻结；建议 Lead 对每个被审分支执行"交付后冻结（只接受新 commit 的返修）"。

### 是否达到 L3 里程碑：**否**

L3 = 整屏组完成 + 独立审查通过 + 集成验证（SCREEN_SPECS §7）。当前：
- 已交付：B-1（Shell+Library）、B-3（Studio Page，含 P1）。
- 未交付/未集成：**B-2 Console 9 分区**（审查时 B-1 分支刚起 WIP）、**B-4 Batch**（仅 NOT_WIRED 占位）、**C-2 Theme Studio**（占位）、**INT-1**（MainWindow 承载 `AppShellV2` + 三空间真实接线 + `IWorkspaceView` + 双选择模型归一 + 键盘路由仲裁）。
- 因此 L3 的两个前提（跨空间上下文保留的**负向验证**、Batch↔Page 共享 selection 的**真实作用域**）目前都无法成立；建议状态：**L2 未闭合，L3 未进入**。下一步应把本报告作为返修输入，并在 B-2/B-4 交付后发起一次真正的 "整屏组 L3" 审查（届时需要真实 Core E2E + DPI 三档 + 键盘/焦点可达矩阵）。

### 推荐下一步（基于当前仓库状态）

1. **DSH/Lead**：要求 ui-studio 立即修复两个 P1（Region 命中 + Modal 焦点/证据），并在同一个 fix commit 里重生成 `verification/V11R-B-3`；要求 ui-shell 清理证据目录（保留 78 个本任务文件）+ 单独提交 `queued=·` 修正 + 补 `IWorkspaceView`；两项均**另开返修 commit，不再混入 B-2 分支**。
2. **DSH/Lead**：在 B-2/B-4 交付后冻结三个分支，先做一次"接线预演"（`IWorkspaceView` + 单一 selection + 键盘仲裁），再发起 INT-1；在此之前不要合并 UI 分支到 main（避免把两套 selection 半接线状态带进主线）。
3. 无需我进一步操作：我只读审查完成，未修改任何文件；如需复核修复后的分支，请重新派发 pin。
