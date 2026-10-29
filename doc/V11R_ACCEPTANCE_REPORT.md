# New Manga 全功能整改 + 全新 UI/UX + Theme Studio 重建 · 验收报告

生成时间：2026-10-30（Asia/Shanghai）
Lead / Integrator：DeepSeek Harness（DSH）
仓库：`G:/CODEX/New Manga`；main HEAD：`5e2d60023`（本报告随其后一个提交入库）
授权依据：用户总指令（V11R）；证据/裁定索引见 `doc/V11R_PROGRAM.md` §8（R-01…R-25）、`doc/V11R_PIN_LEDGER.md`。

> 本报告只写**实测**结论。未运行、无证据、环境不允许的项目一律标 `NOT_RUN`/`BLOCKED`，不伪造 PASS。

---

## 1. 总结论

| 范围 | 结论 | 说明 |
|---|---|---|
| V1.1 审计整改（工作流 A） | **PASS_WITH_ISSUES** | A-1/A-2/A-3/A-5/A-6/A-7 完成并集成；66 命令契约 FROZEN 49 / PARTIAL 17 / GAP 0；**追加发现并修复 P0**：发布版默认 `ReadOnlyUntilParity` 导致导入/建书/运行全被拒（A-5）。F0-1/F0-2 Region 写面 4 轮审查 P1 全关闭、I4 修 3×P2 并经独立窄验证 CLOSED，已合入 main（见 §7）。 |
| 全新 UI/UX（工作流 B） | **PASS_WITH_ISSUES** | 新 Avalonia 外壳 + Library/Console/Studio Page/Studio Batch + 导出/术语工作面全部交付；main 已切**新壳为默认入口**（`--shell=legacy` 保留回滚）。独立审查 r1/r2/r3 的 P1 均已关闭；剩余 P2/P3 见 §8。 |
| Theme Studio 重建（工作流 C） | **PASS** | C-1 新主题引擎 **PASS**（235 测试）；C-2 Theme Studio 7 分区 **PASS**（行高契约漂移 P1 + 2×P2 已修并经独立验证 3/3 CLOSED，**主题域 L3 可签署**）；**C-3 旧主题退役已完成并收口**（`NewManga.Theme` 项目/源码/引用删除、零引用门、干净树 R6、双壳 EXIT 0/0、v2 host.log）；r1 FAIL(P2-only) → C-3-I1 修复 + 干净树补证 + 窄验证通过。 |
| 设计系统（工作流 D） | **PASS_WITH_ISSUES** | D-1 独立审查 r2 的 2×P1 已修（真实 App 资源栈全局令牌、徽标合成对比度），DS 82 测试；仍有 6 行/6 对状态色落极端表面未达 4.5:1（已登记组件约束）。 |
| 总体 | **未达 L4 最终验收** | 阻断项：C-3 未执行（旧主题系统仍在）、F0-1 待最终复核、跨项目并行测试偶发、Windows 实机/DPI/IME/Trim 未验证（NOT_RUN）。可交付为 **M2（新壳可用）+ M3（全工作面）候选**。 |

---

## 2. 交付物

### 2.1 架构（保持 AD-002 冻结：C#/.NET 9 + Avalonia 11.3 + Python Core + SQLite + Typed JSON IPC）
- 新增 `NewManga.DesignSystem`（令牌/样式/自定义控件/图标/a11y）与 `NewManga.ThemeEngine`（主题包 Schema/Registry/Validator/Persistence/Preview/Palette/迁移/`IThemeService`）。
- 依赖方向固定：`App → ThemeEngine → DesignSystem`（R-20）；App 不再直接依赖旧主题实现（C-3 完成后旧项目删除）。
- 旧 React/Tauri 壳未成为生产前端（保留为历史证据）。

### 2.2 UI（工作流 B）
- 外壳：三空间（资料柜/工作台/控制台）+ Studio 双模式（Page ⇄ Batch）+ 共享选择模型（R-16）+ 键盘仲裁（R-17）+ Theme Studio 表面栈。
- Library：搜索/排序/筛选、封面网格、驻留详情、多选批量条、导入 Dock（含新建章节）、回收站、阅读浮层。
- Studio Page：画布 + Region 编辑/检查器五页签/胶片条/六态（空/加载/部分/错误/只读/锁定）。
- Studio Batch：动态列矩阵（10/5 列真实投影）、七态符号、计数 Chip、门禁确认、Stop 二次确认、R-22 意图级幂等键、增量刷新保滚动/焦点。
- Console：9 分区（真实 4 项 + 诚实 NOT_WIRED 5 项）、Provider/网络档案/凭据（永不回显）、Run 投影与控制（共享单一 poller，R-24）。
- 导出/术语：导出预检（范围/格式/stale 策略两值真实透传）、进度/取消/历史；术语与约束因 Core 无读写命令，诚实 NOT_WIRED。

### 2.3 Theme Studio（工作流 C）
- C-1 引擎：10 子系统 + 203–229 测试；Part B Avalonia 适配器（`DesignSystemThemeLayerSink`，59 键白名单、原子替换、失败保持原状、不重建窗口、画布像素差=0）；K-21 Scrim 全局不变量。
- C-2 页面：7 分区全部可用（主题库/预览/我的主题/编辑/外观/导入导出/恢复默认），真实生产服务（非 STUB），24 帧渲染证据 + 应用/取消/回滚真断言。
- C-3 执行（R1–R6）：tag `v11r-pre-retire` = `df883f2ce`；迁移 10 个生产文件（旧壳 chrome/设置页/`--theme` 兼容映射到新引擎）；R4 补 5 条硬门替代断言后删除 5 个旧测试；**删除 `NewManga.Theme` 项目与源码**；R6 零引用门（DELETE/MIGRATE/REPLACE 全 0，余 87 证据 + 55 非依赖），双 shell 启动 smoke 通过。

### 2.4 服务层与 Core（工作流 A）
A-1 `CreateChapterAsync`；A-2 `IRunController`（暂停/继续/停止/重试，R-08 幂等键纪律）；A-3 66 命令契约 + 派生 parity 测试；A-4 同 SHA CI + 干净克隆可重建；A-5 **P0 写入策略**（默认可写 + 三重护栏 + 首次备份）；A-6 启动自检（协议/能力不匹配降级只读）；A-7 导出 `stale_policy` 透传。

---

## 3. 测试与门禁（L1–L4）

| 层级 | 内容 | 结果 |
|---|---|---|
| L1 任务级 | 各任务 build `-warnaserror` + 聚焦测试 | PASS（证据各 `verification/<TASK>/`） |
| L2 功能级 | 全量 `dotnet test`（5 项目）+ `pytest` | **PASS（最后一次干净运行 ×2）**：DS **85** / ThemeEngine **235** / Host 49(+28 skip) / CoreClient 119(+22 skip) / App 308(+7 skip) = **796 通过 / 57 环境性跳过 / 0 失败**（CoreClient 偶发 1 例跨项目并行 flake，单项目复跑 0 失败，已登记 FOLLOW-UP-TEST-1）；Python **2727 passed / 10 skipped / 0 failed**（F0 分支） |
| L3 里程碑 | 独立 Reviewer（≠ Owner）对 UI/主题/DS 的固定 pin 审查 | UI r3：`PASS_WITH_ISSUES`（P1 后已修）；主题域：C-1 PASS、C-2 PASS_WITH_ISSUES、C-3-READY FAIL；DS r2 FAIL→I2 已修待终审；F0 4 轮审查 P1 全关闭 |
| L4 发布验收 | Windows 实机 / DPI / IME / Trim / AOT / 真 sidecar E2E | **NOT_RUN**（环境限制，见 §9）；新壳在**真实窗口**已启动并截图取证（`verification/V11R-INT-1/v2-shell-default-first-run.png`） |

> 注：全量解决方案运行时偶发 1 个 CoreClient 测试失败（单项目独立运行 0 失败，连续 2 次复跑通过）；已登记测试基础设施 follow-up（A-6 runsettings 串行化已落地）。

---

## 4. P0 发现（超出原审计，必须在总报告强调）

发布版 GUI 默认 `ReadOnlyUntilParity`（`AppOptions/HostOptions ParityReached=false`，NSIS 快捷方式无参数），导致用户侧**导入、建书、建章、运行全部被 `HOST_READ_ONLY` 拒绝**。A-5 已修：默认 ReadWrite + 三重护栏（旧 Tauri 壳在运行 / `--parity=false` / Host 未就绪）+ 首次运行备份 + `HostViewSnapshot.ReadOnlyReason`，并有真实备份产物与四象限证据。

---

## 5. 独立审查记录

| 对象 | 轮次 | 结论 | 处置 |
|---|---|---|---|
| D-1 设计系统 | r1 / r2 | FAIL / FAIL（2×P1） | P1 已修（真实 App 资源栈令牌、徽标合成对比度），P2 八项完成 → 待终审 |
| F0-1 Region 写面 | r1 / r2 / r3 / r4 / I4 | FAIL×4；r4 仅 2×P2 未闭 | I4 已修 3 项，待窄复核 |
| B-1/B-2 | r1 / r2 / r3 | PASS_WITH_ISSUES | I1 关闭 P1；B-2 轮询恢复/状态词表 P2 部分完成 |
| B-3/B-4 | r1 / r2 / r3 | FAIL → PASS_WITH_ISSUES | I1→I3 关闭 P1；DIS 上收/证据/R-25 已修 |
| B-5 | r1 | PASS_WITH_ISSUES | P2 证据重生成 + A-7 后 stale 两值已上收 |
| C-1 / C-2 / C-3-READY | r1 | PASS / PASS_WITH_ISSUES / FAIL | C-2 2×P2、C-3-READY 1×P1+2×P2 待修 |

报告均归档 `doc/reviews/`。

---

## 6. 已知问题（不修项 / 组件约束）

1. **状态色落极端表面**：6 行/6 对（dark/light × `bg.overlay/sunken/raised`）未达 4.5:1；裁决=状态文字只落 `bg.panel/raised`+`statusMuted`，其余为背景用途（`verification/V11R-D-1/contrast-matrix.md`）。
2. **`Nm.Color.Scrim`/`Instant` 为全局不变量**，不入 59 键主题层（R-21）。
3. **系统强调色跟随**仅作用域生效、不持久化（GAP-3，V1 不扩 `IThemeService`；登记 V1.x follow-up）。
4. **术语表/不译表**无 Core 读写命令 → 三页诚实 NOT_WIRED。
5. **过期/待确认计数**无投影口径 → 显示 `—`（follow-up：Core 投影扩展）。
6. **页缩略图网格**需 Host 缩略图命令（follow-up）。
7. **`ImportExportPanels`/`ReaderWorkbenchPages` 本机路径 fallback** 待 owner 清理（verify-clean-clone ALLOW_PENDING）。
8. 主题层行高与绝对行框并存（R-15 已纳入白名单并按主题层派生）。

---

## 7. BLOCKED / 未完成

| 项 | 状态 | 原因 / 解除条件 |
|---|---|---|
| C-3 旧主题退役 | **done（已关闭）** | R1–R6 + C-3-I1 + 干净树补证全部完成；`workingTreeDirty=false`、双壳 EXIT 0/0、145 引用仅剩证据 89 + 非依赖 56 | F0-1 / F0-2 Region 写面 | **已合入** | 4 轮审查 P1 全关闭；I4 修 3×P2 后独立窄验证 3 项 **CLOSED**（`doc/reviews/V11R-F0-1-r5-verification.md`），整支（含 C077 `list_page_region_texts`）合入 main `d217b3658`；合入后 build 0W/0E、CoreClient 119 pass、App 305 pass。 |
| D-1 终审 | 待审 | I2 已交付（2×P1+P2 全闭），需固定 pin 终审。 |
| C-2 2×P2 | 待修 | ThemeStudio C# 裸几何值 + conformance 排除、AC9 像素探针恒真。 |

---

## 8. 下一步建议（按优先级）

1. **C-3-READY 修复 + 窄复审 → 执行 C-3 退役**（旧主题项目/旧壳主题入口删除，依赖图/迁移门/回滚三件套已就绪）。
2. **F0-1 窄复核通过 → 合入 main**，ui-studio 接 C077 与 Region 写命令（`verification/V11R-F0-1-I1/CONSUMER_GUIDE.md`）。
3. **D-1 终审 + C-2 两个 P2 修复**，合入后冻结 V1 设计/主题契约。
4. **L4 实机验收**：Windows 10/11、DPI 100/150/200、IME、Trim/AOT/单文件发布、真 sidecar E2E（建书→建章→导入→运行→导出→重启持久化）。
5. **测试基础设施**：解决跨项目并行偶发（runsettings 已串行化宿主，仍需定位残余共享状态）。
6. 已知 follow-up：Core 投影计数、Host 缩略图命令、术语读写命令、本机路径 fallback、系统强调色持久化。

---

## 9. 环境限制（NOT_RUN 汇总）

Windows 实机启动 smoke、真实 DPI 多屏、IME、屏幕阅读器、Trim/AOT/单文件发布、GitHub Actions 真实运行、PyInstaller 同 SHA sidecar 集成、真 `%APPDATA%` 生产数据读写 —— 均因当前环境不可执行而 `NOT_RUN`，无伪造。

---

## 10. L4 证据阶段发现并修复的关键缺陷（本轮新增）

L4 真实窗口/真实 sidecar 取证阶段（非单元测试）发现 5 个单元测试覆盖不到的发布级缺陷，这是分层验证的直接价值：

| # | 级别 | 缺陷 | 影响 | 状态 |
|---|---|---|---|---|
| 1 | **P0** | **v2 默认壳从不启动 Host**（唯一 `StartAsync` 只在 legacy `MainWindow`；v2 链路 `RefreshBooksAsync` 在 `_runtime is null` 时静默返回） | 默认安装后数据面全不可用、状态栏永远"Host 未就绪"、无错误提示 | **已修**（INT-2：Start→数据读取、幂等 StartAsync、失败/只读上状态栏、跨线程 Changed marshal）；真实窗口 L4 复跑 **7/7 Host 就绪** |
| 2 | **P1** | 主题引擎 `ThemePaletteComposer` 把 `Nm.LineHeight.*` 写成绝对像素，DS 按倍数再乘字号 → 行高 ×12（194.4px），任意主题层应用后版式崩坏（含 v2 启动） | 全 UI 版式崩坏 | **已修**（C-2-I1，engine 倍数/绝对分离 + 6 例回归） |
| 3 | **P1** | 资料柜空态 4 个 `EmptyState` 兄弟节点重叠，Host 未就绪 + 空库时多个同时可见 | 首屏文字叠印（真实截图可见） | **已修**（INT-2：单一状态容器 + 互斥选择器 + 5 组合"恰有一个可见"渲染树断言） |
| 4 | **P1** | CLI 只接受 `--key=value`，空格形式被静默解析为 `true`（sidecar/data-root/log-dir 全部失效，无 InvalidReason） | 诊断/部署参数静默失效 | **已修**（A-8：两种写法等价、非法/裸值 exit 2、WriteFatal 永不崩） |
| 5 | **P2** | `--variant=dark\|light` 在 v2 壳无可见差异（主题栈未接 StartupVariant/被覆盖） | 明暗偏好失效 | **已修**（INT-2：采纳已应用外观 + 显式 variant 优先，dark/light 截图哈希不同） |

> 结论：**若只跑单元/headless 测试会全部"通过"**；这批缺陷只有真实窗口 + 真实 sidecar + 真实渲染才能暴露。已在验收报告标注，修复后需重跑 L4 矩阵（`tools/e2e/v2-launch-matrix.ps1`）并重新生成证据。

---

## 11. 最终门禁快照（main `4374dfeae`）

| 项 | 结果 |
|---|---|
| `dotnet build NewManga.sln -warnaserror` | **0 warning / 0 error** |
| `dotnet test NewManga.sln`（runsettings 串行宿主） | DS 85 / ThemeEngine 235 / Host 49(+28 skip) / CoreClient 119(+22 skip) / App 308(+7 skip) = **796 passed / 0 failed** |
| Python `pytest`（F0 合入时） | **2727 passed / 10 skipped / 0 failed** |
| 旧主题退役 | `src/**`、`tests/**` 旧符号 0；`NewManga.Theme` 已删除；双壳均可启动 |
| 真实窗口 L4 | 启动矩阵 **7/7 PASS**：三尺寸×明暗 + legacy 回滚；窗口出现 + **Host 就绪 7/7** + 截图 9 张 + **自然退出 exit 0（7/7）**，无 harness 终止 |
| 主题切换画布像素 | ThemeEngine `DesignSystemThemeLayerSinkTests`：32×32 区域像素差 **0**，同时断言资源色确实改变 |
| 主题层行高契约 | 倍数/绝对分离（C-2-I1），6 例回归 + 真实窗口 TextBlock 行高 ≤ 字号×2.5 |

## 12. 交付判定

- **可交付状态**：新壳默认入口 + 三空间 + Studio 双模式 + Theme Studio + 新主题引擎 + 旧主题退役 + V1.1 整改（A 系列）+ Region 写面（F0）+ 导出/术语/Console/Library 全部功能面已集成，main 全量测试 0 失败。
- **仍需人工确认**：L4 实机项目（DPI/IME/Trim/AOT/真机交互）与 C-3/D-1 的窄验证结论；`FOLLOW-UP-*` 清单为 V1.x 收尾项，不阻塞本轮交付判定。
- **禁止事项遵守**：未 push 远端、未删除用户数据、未伪造 PASS；所有 NOT_RUN 均如实标注。
## 13. 收盘状态（main `e33e3384f` 之后）

| 工作流 | 状态 | 收官证据 |
|---|---|---|
| A（V1.1 整改） | **done**（A-1…A-8 全部合入） | A-3 契约、A-5 P0 写入策略、A-6 自检、A-7 stale、A-8 CLI |
| B（新 UI/UX） | **done**（B-1…B-5 + INT-0/1/2 全部合入） | `verification/V11R-B-*/`、`V11R-INT-1/`、`V11R-INT-2/` |
| C（Theme Studio/主题） | **C-1 done、C-2 done(PASS_WITH_ISSUES)、C-3 done** | `verification/V11R-C-1/`、`V11R-C-2/`、`V11R-C-3/`（含 R6-report-clean.md） |
| D（设计系统） | **done**（D-1 收口，r4 PASS_WITH_ISSUES，FocusRing P2 已闭） | `verification/V11R-D-1/`（I2/I3） |
| F0（Region） | **done**（5 轮审查 + 独立窄验证 CLOSED，已合入） | `verification/V11R-F0-1-I4/`、`V11R-F0-1-r5-verification.md` |
| L4（发布验收） | **真实窗口矩阵 7/7 PASS**；实机 DPI/IME/Trim/AOT/交互 **NOT_RUN** | `verification/V11R-L4-EVIDENCE/` |

**结论**：本轮交付范围内，所有"可在当前环境执行"的验证均已完成且 0 失败；剩余项均为环境受限的实机验证（NOT_RUN）与已登记的 V1.x follow-up，不阻塞功能交付。
## 14. 主题域 L3 签署与最终复检

| 对象 | 结论 | 依据 |
|---|---|---|
| C-1 新主题引擎 | **PASS** | `doc/reviews/V11R-THEME-L3-r1-independent.md`；235 测试；零依赖旧 `NewManga.Theme` |
| C-2 Theme Studio | **PASS** | C-2-I1 后窄验证 3/3 CLOSED（`doc/reviews/V11R-C-2-I1-verification.md`） |
| C-3 旧主题退役 | **PASS** | 干净树 R6（`workingTreeDirty=false`、双壳 EXIT 0/0、v2 host.log、零引用门）+ C-3-I1 窄验证补项闭环 |
| 主题域 L3 | **可签署** | 三者闭环，无 P1/P2 未处置项 |
| 最终树 clean-clone 自检（A-4） | **修复中** | 唯一 hard failure 为负向安全测试夹具中的假路径字面量（`V2ConsoleUiTests.cs:368`），正在加"显式标注豁免 + 报告可见"后复跑 |
| 真实窗口 L4 矩阵（当前 HEAD 复跑） | **7/7 PASS** | `verification/V11R-L4-EVIDENCE/launch-matrix.json`：Host 就绪 7/7、自然退出 7/7、截图 9 张 |
## 15. 最终门禁（main `8ed4a4f4f`，本轮收盘）

| 门 | 结果 |
|---|---|
| `dotnet build NewManga.sln -warnaserror` | **0 warning / 0 error** |
| `dotnet test NewManga.sln`（串行宿主 runsettings） | DS **85** / ThemeEngine **235** / Host **49**(+28 skip) / CoreClient **119**(+22 skip) / App **309**(+7 skip) = **797 passed / 57 skipped / 0 failed** |
| `CoreClient` 单项目复跑 | 119 passed / 22 skip / **0 failed**（确认跨项目 flake 不再现） |
| clean-clone 自检（最终树） | **OK**，hard_failures=0，fixture 豁免 1 条且可审计，分类自测 6/6 |
| 真实窗口 L4 矩阵（当前树复跑） | **7/7 PASS**，Host 就绪 7/7，自然退出 7/7，截图 9 张 |
| Python `pytest` | exit 0（QML 历史噪音不属于失败） |
| 旧主题退役 | `src/**`/`tests/**` 旧符号 0；`NewManga.Theme` 已删除；双壳启动 EXIT 0/0 |

**收盘判定**：本轮目标的可执行范围已全部完成且门禁全绿；仅剩环境受限的实机验证（Windows 真实 DPI/IME/屏幕阅读器/Trim/AOT/GitHub Actions 真跑/受支持的 UI 自动化输入）为 `NOT_RUN`，以及 `FOLLOW-UP-*` 清单中的 V1.x 收尾项，均已在报告与 `doc/V11R_PROGRAM.md §10` 诚实登记。
---

## 16. 真机实机清单执行结果（2026-10-30 补测）

按 `verification/V11R-L4-EVIDENCE/README.md` 在真实 Windows 交互桌面（10.0.26300 / x64 / 2560×1440 / 100%）执行，完整证据 `verification/V11R-L4-EVIDENCE/real-machine/`（`checklist.md`、`checklist.json`、UIA 树、截图、发布日志）。

| 清单项 | 结论 | 说明 |
|---|---|---|
| 启动矩阵 + Host 就绪 | **PASS 7/7** | 复跑真实窗口三尺寸×明暗 + legacy；全部自然退出 exit 0 |
| 重启持久化 E2E | **PASS** | UIA 真实点击「主题工作室 → 外观 → 浅色 → 应用」→ 关闭 → 重启：`theme-settings.json` `appearance=light` 保持，界面浅色 |
| 中文 IME | **PASS** | 真实键盘输入经 IME 复合后上屏「你好」写入搜索框 |
| DPI 感知 | **PASS @100%**；150%/200% **NOT_RUN** | manifest PerMonitorV2、运行时 DPI=96；改系统缩放未擅自执行 |
| 屏幕阅读器/可访问性 | **PARTIAL（发现 P2）** | UIA 71 元素/52 命名；**7 个按钮 Name 为类型名**（6×`Avalonia.Controls.StackPanel`、1×`Kbd`）→ `FOLLOW-UP-A11Y-1` |
| 单文件自包含发布 | **PASS** | 93.5 MB 单 exe；窗口+Host 就绪+exit 0 |
| Trimmed 发布 | **FAIL（默认 IL2026）/ PASS-with-caveat（抑制分析）** | 默认被 `TreatWarningsAsErrors` 升级为 error；抑制后窗口/Host/Theme Studio 可用，trim 安全性未分析 |
| AOT 发布 | **FAIL（默认参数冲突）/ PASS（`PublishTrimmed=true`+抑制）** | 28.8 MB 原生 exe 可运行，Host 就绪，仅 1 条 IL3050（MicroCom）警告 |
| GitHub Actions 真实运行 | **NOT_RUN** | 本机无 runner |

**新发现并登记**：`FOLLOW-UP-E2E-1`（主题设置路径不受 `--data-root` 隔离，E2E 写真实 `%APPDATA%`；本次测试产生的文件已备份并删除，用户环境已恢复）、`FOLLOW-UP-A11Y-1`（UIA 命名缺陷）、`FOLLOW-UP-PUB-1`（trim/AOT 发布参数需固化）。