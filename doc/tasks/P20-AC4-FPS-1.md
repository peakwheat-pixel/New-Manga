---
id: P20-AC4-FPS-1
title: P20 AC4 帧率与帧时间测量（默认关闭的前端 requestAnimationFrame 采样钩子）
kind: feature
governance_version: 2
status: closed_with_limitations
approval: user_ruling_20261018_ac4_fps_measurement
blocked_by: null
suggested_owner: ZCode
owner: ZCode
reviewer: Codex
depends_on: [P20]
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
branch: null
worktree: G:/CODEX/New Manga
integration_commit: 16b99524794a7ff2132a19753ce6a7fcd53fc244
delivery_head: 16b99524794a7ff2132a19753ce6a7fcd53fc244
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/P20-AC4-FPS-1
---

# P20-AC4-FPS-1：AC4 帧率与帧时间测量

## 来源与依据

`P20` 的 AC4 原文要求"单页/Webtoon 长图滚动**稳定 60 FPS**；缩放平移无可见撕裂"。此前实测只完成交互延迟部分（20/20 样本有效、`avg = 36.0 ms ≤ 50 ms`，`p95 = max = 62.4 ms` 超限如实保留），**FPS 与撕裂因无测量手段被标为 NOT_MEASURED**（证据 `verification/P20/ac4-20261018-0720/**`）。

用户 2026-10-18 裁决**全采纳**以下四项，本 Task 据此成立：

1. **达标口径**：帧时间 **avg ≤ 50 ms** 视为 AC4 帧率部分达标；不再要求"稳定 60 FPS"的严格表述。
2. **p95 如实记录**：p95 帧时间（当前记录值 **77.5 ms**）必须原样如实报告，**不得**为达标而删改样本或只报 avg。
3. **批准实现默认关闭的前端 `requestAnimationFrame` 采样钩子**，用于测量 FPS 与帧时间尖峰。
4. **撕裂只记为限制（limitation）**，不做客观验证；不得以静态推理代替实测，也不得声称"已验证无撕裂"。

## Acceptance Criteria

- [ ] AC1：**默认关闭的采样钩子**——前端新增 `requestAnimationFrame` 采样钩子，**默认关闭**；仅在显式开启（如查询参数 / 全局开关 / 环境变量，具体形式由 Owner 冻结并在 Task 记录）时采集。关闭态必须**不注册 rAF 回调、不分配采样数组**，并有可复核的证据（代码路径或测试）证明零开销，不得以"提前 return"掩盖已注册的常驻回调。
- [ ] AC2：**结构化产物**——开启后按帧记录帧间隔（frame time, ms）与瞬时 FPS，可导出为 CSV/JSON 到**调用方指定**的 OutDir。严禁写入用户真实数据目录 `%APPDATA%\com.newmanga.m2rc1.desktop`；严禁默认落盘。
- [ ] AC3：**真实桌面测量（单页 + Webtoon 长图滚动）**——在真实交互式桌面对隔离样例执行滚动测量，产出样本级 CSV + 汇总（`avg` / `max` / `p95` / 样本数 / 丢弃样本数与理由）。**达标判定按用户口径：`avg ≤ 50 ms`。**
- [ ] AC4：**p95 如实记录**——`p95` 与 `max` 必须如实列入报告，即使超出 50 ms。若 p95 超限，**不得**在本 Task 内通过调阈值或改写口径消解；只能如实登记并把冷路径优化另立 Task（由 Coordinator 决定是否立项）。
- [ ] AC5：**撕裂只记 limitation**——AC4 原文的"缩放平移无可见撕裂"不在本 Task 做客观验证；报告须显式写明该子项为 `NOT_VERIFIED_BY_RULING`（用户裁决只记限制），不得写成 PASS。
- [ ] AC6：**不回归**——钩子关闭时产品行为与性能特征不变；前端既有测试全绿（`npm test`）；AC4 既有延迟结论（`avg = 36.0 ms`、20/20 有效）不得退化或被覆盖，须给出重跑对照或说明复用依据。
- [ ] AC7：**不回归 P20 其他 AC**——不改动 AC2 冷启动、AC3 内存、AC5 降级、AC6 自愈、AC7 发布 Gate 的任何实现或阈值。

## 允许修改范围

- `apps/desktop/frontend/**`：采样钩子本体、其单元测试，以及**最小必要的**开启/导出接线（不得改变既有 UI 行为）。
- `verification/P20-AC4-FPS-1/**`：测量脚本、原始样本、汇总报告、命令 stdout/stderr/exit。
- 本 Task、`doc/handoffs/P20-AC4-FPS-1-zcode.md`。

## 禁止范围

- 不修改 IPC / 共享契约 / Schema / ACL / 依赖版本。
- **不得默认开启钩子**；不得让钩子进入生产默认路径。
- **不得指标操纵**：不得丢弃尖峰样本、不得只报 avg 不报 p95、不得以调阈值或改写口径消解超限。用户已裁决的 `avg ≤ 50 ms` 口径不得由 Agent 更改。
- 不触碰 P09-AC3-DELETE-1 在制品、`apps/desktop/src-tauri/**`（属 P20-CLOSE-BOUND-HARDEN-1 范围）、用户 20 个具名 dirty 文件。
- 不得 `git add -A` / `git add .` / `git commit -a`；禁止 `reset --hard` / `clean` / `push` / `stash` / 删除文件。
- GUI 验证的隔离根**必须**放 `%TEMP%` 新建目录，**禁止**放 `apps/desktop/src-tauri/target/**`；收尾确保 `m2rc1-desktop` / `core_service` / `host_bridge` 全退。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 钩子默认关闭与零开销 | 前端单元测试：默认态不注册 rAF、不分配数组；开启态注册并按帧采样 | Vite/Vitest | **PASS**（r1 后累计含 rAF spy 0 注册、无实例无数组、默认渲染无面板；r2 增可见性监听仅 start() 时注册） | `apps/desktop/frontend/src/perf/*.test.ts`；`verification/P20-AC4-FPS-1/npm-test-20261018-r2.log` |
| AC6 既有前端测试 | `npm test`（隔离根，不得被管道包裹） | 前端依赖已安装 | **PASS**（32 files / 324 tests passed，exit 0；基线全数保留） | `verification/P20-AC4-FPS-1/npm-test-20261018-r2.log` |
| AC3 单页滚动帧时间 | 真实交互桌面直跑测量脚本，导出 CSV | release/ dev 前端 + WebView2 可用；唯一隔离根 | **NOT_RUN**（Owner 范围外；脚本已交付，由 Coordinator 执行） | `verification/P20-AC4-FPS-1/run-ac4-fps.ps1`；产物待 `run-*/` |
| AC3 Webtoon 长图滚动帧时间 | 同上，Webtoon 模式长图滚动 | 同上 | **NOT_RUN**（同上） | 同上 |
| AC5 撕裂 | **不执行**（用户裁决只记 limitation） | — | NOT_VERIFIED_BY_RULING | 脚本 `fps-metadata.txt` 固定声明 + `MEASUREMENT-GUIDE.md` |

## 依赖、风险与阻塞

- 依赖：`P20` 已授权激活；AC4 延迟证据位于 `verification/P20/ac4-20261018-0720/**`。
- 风险一：本机 CDP 远程调试端口**无法开启**（`WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port` 被阻断），因此**不能**用 CDP 做帧采样；必须走前端钩子 + 文件导出。
- 风险二：真实桌面测量必须由 Coordinator 在交互式桌面执行 —— Owner 只交付钩子、测试与测量脚本；若 Owner 试图自行做窗口级验证将失败（见 P20 系列既往记录）。
- 风险三：`p95` 很可能仍超 50 ms（已记录 77.5 ms）。按用户裁决，**这不阻断达标判定**，但必须如实记录并保留为 limitation。

## 交付与运行记录

- Handoff：`doc/handoffs/P20-AC4-FPS-1-zcode.md`（r3 返修 delivery_head = `16b995247`）。
- Review：r1 `codex-review-r1.md` 结论 `changes_requested`（五项 finding 全处置）；r2 `codex-review-r2.md` 结论 `changes_requested`（四项处置）；r3 `codex-review-r3.md` 结论 `changes_requested`（两项处置见下，含用户 DIR-4 豁免授权），待 Codex 第四轮独立复审（Owner 不审自己的变更）。
- 实际测试：见上表（AC1/AC6 PASS；AC3 NOT_RUN 属 Coordinator；AC5 NOT_VERIFIED_BY_RULING）。
- 2026-10-18 Coordinator（dsh, epoch 8）按用户 T4 裁决建立本 Task 并冻结范围。
- **2026-10-18 Owner（ZCode）交付**：
  - 开启方式冻结为三通道任一显式开启（默认全关）：构建期 `VITE_M2_FPS_SAMPLING=1` / 查询参数 `?m2_fps=1` / localStorage `m2rc1_fps_sampling=1`；注意 Tauri v2 编译期嵌入 dist，测量构建需重编译 debug exe（`-BuildExe`，须避开 P20-CLOSE-BOUND-HARDEN-1 对 `src-tauri/target` 的并行使用）。
  - `npm test` 32 files / 319 tests passed（exit 0）+ `npx tsc --noEmit` exit 0；新增 22 用例含默认关闭零开销证明（rAF spy 0 注册、无 recorder 实例即无采样数组、默认 DOM 无面板）。
  - 排除规则仅两类且逐样本留痕（`raf_gap_ge_1000ms` / `non_positive_delta`），尖峰样本一律保留在 CSV；`avg ≤ 50 ms` 口径为常量、不可配置；p95（nearest-rank）与 max 恒如实报告。
  - 导出落盘只经保存对话框（调用方选 OutDir）或 UIA 抓取写 OutDir；代码无路径写入；不触碰 `%APPDATA%\com.newmanga.m2rc1.desktop`；无默认落盘。
  - 测量脚本 `verification/P20-AC4-FPS-1/run-ac4-fps.ps1` + `MEASUREMENT-GUIDE.md`：%TEMP% 隔离根、SAMPLING_NOT_ENABLED fail-fast、独立复算汇总、收尾全退 `m2rc1-desktop`/`core_service`/`host_bridge`。
- **2026-10-18 Owner（ZCode）r1 返修交付**（Review `changes_requested`，五项 finding 全处置；实现 commit `4c54f3dd1`）：
  - **FPS-R1-01（P1）**：runner 启动前把 `NEWMANGA_DATA_ROOT`/`M2RC1_DERIVED_ROOT`/`M2RC1_MANAGED_ROOT`/`M2RC2_CATALOG_DB` 全部钉到新建 `%TEMP%` 隔离根并读回校验，任一缺失或越界即拒绝启动（exit 7）；dev 模式经 `-DevSrcRoot` 显式设置并核对 `M2RC1_SRC_ROOT`，不传时要求 packaged sidecar 存在（否则 app 必 panic，同样拒绝）；真实 `%APPDATA%\com.newmanga.m2rc1.desktop` 启动前/收尾后逐文件 sha256 快照比对，任何变化判 FAIL。**实测**：`-SmokeTest` 启动 exe 12 s，AppData 24 文件前后 UNCHANGED，写入（`catalog/catalog.sqlite`、`library.db`、`derived/.preview-lifecycle.lock`、`managed/temp`）全部落在隔离根，exit 0。
  - **FPS-R1-02（P1）**：只记录并清理本轮 app PID 及其后代（Win32_Process PPID 链，启动后与每轮 capture 前刷新；结束时补扫孤儿），Stop-Process 前按进程名家族白名单复核防 PID 复用；既有同名进程登记 `NOT_OURS` 不触碰；清理统一进 `try/finally`（覆盖正常/失败/人工中止），收尾复查全退、残留即 FAIL。
  - **FPS-R1-03（P1）**：失败累积制——CSV/JSON 缺失、capture 失败、kept=0、`avg>50ms`、AppData 变化、进程残留任一即非零退出（6）；只有全部请求 phase 完整且 avg 判定通过才 exit 0。退出码表见 MEASUREMENT-GUIDE。
  - **FPS-R1-04（P2）**：面板导出改走 `window.showSaveFilePicker()` 显式 Save As（目标由调用方选；取消即 AbortError 不写任何位置；无 picker 环境明示用 Show/Copy）；删除 Blob+anchor.download 静默下载路径（不再可能写 WebView2 默认下载目录）；前端仍不接触绝对路径。
  - **FPS-R1-05（P2）**：`>=1s` gap 仅在与采样的 hidden 区间（visibilitychange 跟踪，可注入源）相交时排除（reason=`raf_gap_ge_1000ms_while_hidden`）；前台停顿保留在 kept 统计；summary/标题/JSON 增加 `allMaxMs` 与 `excludedMaxMs`，runner 复算同步输出 `all_max_ms`/`excluded_max_ms`——被排除停顿不可能隐身于 PASS。
  - 验证：`npm test` 32 files / **324** tests passed（exit 0）+ `npx tsc --noEmit` exit 0；`-SafetySelfCheck` 6 项 PASS exit 0（首跑曾抓出 iso 前缀判定缺陷并修复——自检有效性实证）；`-SmokeTest` 见上。AC3 真实桌面测量仍归 Coordinator（NOT_RUN）。
- **2026-10-18 Owner（ZCode）r2 返修交付**（Review r2 `changes_requested`，四项全处置；实现 commit `de5c06a4d`；前端零改动——r2 四项 finding 全在 runner）：
  - **FPS-R1-02（P1 阻断）**：窗口查找重写为 `Find-WindowByTitleForPid`——枚举**全部**同标题顶层窗口，只返回 `ProcessId` 等于本轮 app PID 的那个；**不存在「取首个同标题窗口」回退**，异进程同标题窗口登记 `NOT_OURS_WINDOW`（每 pid 一次）且永不点击/滚动/杀灭。测量路径在窗口就绪后经 `Assert-OurWindow` 二次校验（不匹配即 exit 2）；`WINDOW_BOUND pid=...` 日志固定绑定证据；滚动注入期间 app 退出即 `SCROLL_ABORT` FAIL。**P1 验证（两层）**：① `-SafetySelfCheck` 干扰窗口注入三连 PASS——decoy（pwsh WinForms 同标题窗）对其自身 PID 可查得（阳性对照）、对任意异 PID 返回 null（无首匹回退）、审计轨迹登记 `NOT_OURS_WINDOW`；② 实机组合——持久 decoy（pid=48468）在场跑 `-SmokeTest`：登记 NOT_OURS_WINDOW 48468 → 绑定本轮窗口（`window_pid=29896 app_pid=29896` 一致）→ 11 后代全退 → AppData UNCHANGED → exit 0 → **decoy 全程存活未被触碰**（验证后自行清理）。
  - **FPS-R1-01（PARTIAL）**：`Get-TreeManifest` 把目录枚举错误（`ENUM_FAIL`）与单文件哈希错误（`HASH_FAIL`）记入 manifest 错误表——**快照不完整即 fail closed**：基线不完整拒绝启动（exit 7，不启动 exe）、终末快照不完整 FAIL（exit 6）；`Compare-Manifests` 加 UNREADABLE 守卫（同路径前后均不可读 → 比较为 NOT-unchanged，r1 漏报路径闭合）。**故障注入**（`-SafetySelfCheck`）：独占锁定文件 → `HASH_FAIL` 入表 PASS；同路径双侧 UNREADABLE → 拒绝为 unchanged PASS；枚举注入在本 Owner 令牌下因持 **ENABLED `SeBackupPrivilege`**（Windows 设计 bypass 读类 DACL）诚实降级为 PASS-by-channel（missing-directory 探针证明喂 `ENUM_FAIL` 的 `-ErrorVariable` 通道存活），无特权令牌（Coordinator/Reviewer 正常终端）走完整 deny-ACL 注入路径。注入开发过程自身抓出两个真实缺陷并修复（`Get-FileHash` 非终止错误须 `-ErrorAction Stop` 才进 catch、icacls `(OI)(CI)` 为 inherit-only 不作用于目录本对象）——两次中间 FAIL 留档为注入有效性实证。
  - **FPS-R1-03（PARTIAL）**：① JSON artifact——`Show CSV`/`Show JSON` 按钮失败即 FAIL 且**不把 textarea 残留写成 artifact**；CSV 抓取校验表头+行结构；JSON 抓取后**解析并校验确为本轮数据**（`meta.task='P20-AC4-FPS-1'`、`summary.totalSamples`/`excludedCount`、`samples[]` 长度 vs CSV 行数、首/末样本 `frameTsMs` vs CSV 首末行 `frame_ts_ms`）——上一轮残留 payload 无法通过。② SmokeTest false-pass 三处闭合——窗口缺失（`SMOKE_NO_WINDOW`）、启动早退（`SMOKE_APP_EXITED_EARLY`/`..._DURING_SETTLE`）、隔离根无写入（`ISO_EMPTY`）全部进 failure list（exit 6），不再是仅记录。
  - **smell（非阻断）**：`T` → `Write-Trace`（日志职责）、`F` → `Find-UiaByName`（UIA 查找职责），全调用点同步。
  - 验证：语法 PSParser 0 错；`-SafetySelfCheck` **12 项断言** PASS exit 0（`selfcheck-20261018-180541/`）；decoy 组合 `-SmokeTest` PASS exit 0（`smoke-20261018-180626/`）；`npm test` 未重跑（前端零改动，基线 324 tests 仍有效——r2 Review 复核同口径）。AC3 真实桌面测量仍归 Coordinator（NOT_RUN）。
- **2026-10-18 Owner（ZCode）r3 返修交付**（Review r3 `changes_requested`，用户 DIR-4 豁免授权本轮；两项 finding 全处置；实现 commit `16b99524794a7ff2132a19753ce6a7fcd53fc244`；前端零改动——r3 两项 finding 全在 runner）：
  - **FPS-R1-02（P1 阻断：注入未绑定前台焦点）**：Windows 把 `WM_MOUSEWHEEL`/`SendKeys` 发给**前台（焦点）窗口**而非光标下窗口（操作者从终端按 Enter 后终端即前台）。新增 `Assert-ForegroundIsPid` 守卫：**每轮注入 tick 前**经 `GetForegroundWindow`+`GetWindowThreadProcessId` 校验前台窗口 PID == 本轮 app PID；不符时先做一次激活（`TryActivate`＝SW_RESTORE + `SetForegroundWindow` + BringWindowToTop，前台锁被拒时以合成 Alt 键解锁重试），激活后重验；仍不符即 **fail-closed**（`FOCUS_NOT_OURS`/`FOCUS_ACTIVATE_FAILED`/`FOCUS_NO_HWND` 进 failures → exit 6 非零），**绝不在焦点不明时注入任何输入**。keys 路径同时检查 `AppActivate` 返回值（false 即 `KEYS_ACTIVATE_FAILED`，不发按键）。M2Wheel/M2Focus 原语上移至脚本顶部统一加载（测量与自检共用）。
  - **FPS-R1-02-AUDIT（P2：窗口查找提前 return 漏登记）**：`Find-WindowByTitleForPid` 改为**全扫描后返回**——即使自有窗口先被枚举到，同一次调用也会把其后出现的异 PID 同标题窗口登记 `NOT_OURS_WINDOW`（不再提前返回）。
  - **补测（Review 修法 3，`-SafetySelfCheck` 新增焦点注入组，共 16 项断言）**：三窗口实弹场景——stub（本轮 app 替身，同标题）、decoy（异 PID **同标题**干扰窗）、outsider（异标题外部窗，**真实持有前台**，`fg_pid` 实证）。① 同一次查找同时返回 stub 并登记 decoy `NOT_OURS_WINDOW`（全扫描判别断言，不论 UIA 枚举顺序）；② 外部窗占前台时 guard 拒绝——**三窗口滚轮计数零新增**（WM_MOUSEWHEEL 逐窗 WndProc 计数实证外部窗口未收到任何输入），拒绝经 `Fail()` 进入 exit-6 机制（与测量路径共用同一函数）；③ `TryActivate` 把 stub 带到前台后前台 PID 校验通过；④ 注入 1 个滚轮事件**只落在 stub**（decoy 与 outsider 零接收）。
  - 验证：语法 PSParser 0 错；`-SafetySelfCheck` **16 项断言 PASS exit 0**（`selfcheck-20261018-194056/`；四轮中间 FAIL `…193652/…193804/…193857/…193957` 留档——自检先后抓出 `Start-Process -ArgumentList` 不自动加引号、Windows PowerShell 5.1 `Add-Type -TypeDefinition` 需显式 `-ReferencedAssemblies System.Windows.Forms`、C# 裸 `CenterScreen` 不存在、含空格标题参数被拆断四个真实缺陷，注入开发有效性实证）；`-SmokeTest` 回归 PASS exit 0（`smoke-20261018-194111/`）；decoy 组合 `-SmokeTest` PASS exit 0（decoy 登记后存活未触碰，`smoke-20261018-194147/`）。AC3 真实桌面测量仍归 Coordinator（NOT_RUN）。
  - **证据表勘误（本轮登记时发现）**：对全表 19 行按磁盘真实字节逐行复核，发现 4 处 r1/r0 期登记的 pin 为抄写失真（`EVID-FPS-TESTS-RECORDER`/`EVID-FPS-TESTS-PANEL`/`EVID-FPS-WIRING` 各 1-2 个字符错、`EVID-FPS-SMOKE` 长 65 字符）——**r3 Review「15/15 MATCH」结论与磁盘事实不符**。已全部按磁盘实算值修正（本轮新增 6 行复核全过）；勘误属登记修复，对应文件内容与 commit 归属未变。

## Canonical Evidence

r3 返修交付 head 已固定（`16b995247`；r2 返修 `de5c06a4d`、r1 返修 `4c54f3dd1`、r0 原始交付 `011293151` 留史）；R4 已批准并完成集成指针登记。真实桌面测量产物（`run-*/`）在 Coordinator 执行后由 Review 阶段补登。本表共 20 个 pin，哈希按文件磁盘真实字节计算；本轮 `git ls-files --eol` 显示 Task 与 R4 Review 均为 `w/lf`（尽管 `core.autocrlf=true`），因此以实测字节为准，不按预期行尾转换重算。

| evidence_id | AC/Gate | path | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EVID-FPS-HOOK | AC1, AC2, AC4 | apps/desktop/frontend/src/perf/fpsRecorder.ts | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | 6435b9f9d01b71277e0a352701c14e15c27ac746c47697f18c723227185ce3e8 | SOURCE_PIN |
| EVID-FPS-PANEL | AC2 | apps/desktop/frontend/src/perf/FpsRecorderPanel.tsx | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | 527f2999d5157facc3bba8702ee105dcdf2441587abff60409e4c719b01b86a6 | SOURCE_PIN |
| EVID-FPS-TESTS-RECORDER | AC1, AC2, AC4 | apps/desktop/frontend/src/perf/fpsRecorder.test.ts | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | 9595256a211ff5d0a96a4bd7f9aadf403941f59797dcd8d1b3f087583066a0ca | SOURCE_PIN |
| EVID-FPS-TESTS-PANEL | AC1, AC2, AC6 | apps/desktop/frontend/src/perf/FpsRecorderPanel.test.tsx | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | fe6e7739ec4c067cd5653a3a74662b23f7b119970357feef3120268a5cbc0ac8 | SOURCE_PIN |
| EVID-FPS-WIRING | AC1, AC6 | apps/desktop/frontend/src/main.tsx | 01129315100928751546c9608456868f5085fa8c | b8f79fdc6746a250515af97970e6c3067f4bab10218c582b677490b57e6be050 | SOURCE_PIN |
| EVID-FPS-NPMTEST | AC1, AC6 | verification/P20-AC4-FPS-1/npm-test-20261018.log | 01129315100928751546c9608456868f5085fa8c | f14e86b5491f0e8012a89c717a931f1b84c5283931cbf2fd26093ab13188e355 | SOURCE_PIN |
| EVID-FPS-NPMTEST-R2 | AC1, AC6 | verification/P20-AC4-FPS-1/npm-test-20261018-r2.log | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | 110a8eaffe6010f4c1e9a48d081d1d25bc7161e6cb5da933693a49eb21f56ae4 | SOURCE_PIN |
| EVID-FPS-RUNNER | AC3 | verification/P20-AC4-FPS-1/run-ac4-fps.ps1 | 16b99524794a7ff2132a19753ce6a7fcd53fc244 | f3a34cfe7a7a656d776194b1d49fe7f7e6d224e204eaf8dd78c3a6600742b35a | SOURCE_PIN |
| EVID-FPS-GUIDE | AC3, AC5 | verification/P20-AC4-FPS-1/MEASUREMENT-GUIDE.md | 16b99524794a7ff2132a19753ce6a7fcd53fc244 | 2a882f461c82c9aff22150d206b6c148d4e0d537e3c345e5d75d5fa5ebeaff3a | SOURCE_PIN |
| EVID-FPS-REVIEW-R1 | Review | verification/P20-AC4-FPS-1/codex-review-r1.md | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | 5ef026d9f300ea0a501c001b878e31f1c46337f68952c2a64c56607a28bd037f | SOURCE_PIN |
| EVID-FPS-REVIEW-R2 | Review (r2 finding 依据) | verification/P20-AC4-FPS-1/codex-review-r2.md | de5c06a4d572c849de7d7fed8e5027f92e0de156 | c84cb4cb2f9dc69995bceb0dc659663b5531538d0a0b7c63ab52da2e1221c6bb | SOURCE_PIN |
| EVID-FPS-REVIEW-R3 | Review (r3 finding 依据) | verification/P20-AC4-FPS-1/codex-review-r3.md | 16b99524794a7ff2132a19753ce6a7fcd53fc244 | 5924bece66e831d8788c85bf0aa8aee83a0fc58b32646922317c32bb1c8b5f47 | SOURCE_PIN |
| EVID-FPS-REVIEW-R4 | Review (approved；FPS-R1-02 闭合与集成裁决) | verification/P20-AC4-FPS-1/codex-review-r4.md | cf477fe1b7ab6e2105be5a733c606da1684707a9 | 2c26b91a96c551ae8c66a9cd3e17ce4faab701ddd50f0e8ef6af87dd7f83728a | SOURCE_PIN |
| EVID-FPS-SELFCHECK | AC3 (runner 隔离自检, r1) | verification/P20-AC4-FPS-1/selfcheck-20261018-173828/fps-trace.log | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | f4a88496237617069a5dd41fb6850eeec84556cd96ab25e7cddb6741d0501491 | SOURCE_PIN |
| EVID-FPS-SELFCHECK-R2 | AC3 (runner 自检 r2, 12 断言含故障注入+干扰窗口) | verification/P20-AC4-FPS-1/selfcheck-20261018-180541/fps-trace.log | de5c06a4d572c849de7d7fed8e5027f92e0de156 | 2adca517d384cfc6c920340c8ba6f5cfafe6c002f48bd40a60e11f0b4cf95292 | SOURCE_PIN |
| EVID-FPS-SELFCHECK-R3 | AC3 (runner 自检 r3, 16 断言含焦点注入组：外部占前台零输入+Fail→exit6+滚轮只落 stub) | verification/P20-AC4-FPS-1/selfcheck-20261018-194056/fps-trace.log | 16b99524794a7ff2132a19753ce6a7fcd53fc244 | 075a66a7702f429720a2b3208753276c768ab9e64a16db905cc1cb3f8ca23746 | SOURCE_PIN |
| EVID-FPS-SMOKE | AC3 (runner 隔离冒烟, r1) | verification/P20-AC4-FPS-1/smoke-20261018-173917/fps-trace.log | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | a7dd5a9378e57ab6d612592f128f6bcf8a7b9324a27304504aea52a3d64ea4c9 | SOURCE_PIN |
| EVID-FPS-SMOKE-R2 | AC3 (P1 实证：同标题 decoy 在场绑定本轮 PID) | verification/P20-AC4-FPS-1/smoke-20261018-180626/fps-trace.log | de5c06a4d572c849de7d7fed8e5027f92e0de156 | 34450559cec0d2eba74347de1cbf52f5185a6805a7f1f109d7fc1521ada407c1 | SOURCE_PIN |
| EVID-FPS-SMOKE-R3 | AC3 (r3 回归：decoy 在场 SmokeTest，登记 NOT_OURS 后存活未触碰) | verification/P20-AC4-FPS-1/smoke-20261018-194147/fps-trace.log | 16b99524794a7ff2132a19753ce6a7fcd53fc244 | fb7df1f2176d59fb51887c643a0e3fdce25a3f363907178410f21cfabd51bda3 | SOURCE_PIN |
| EVID-FPS-SMOKE-REG-R3 | AC3 (r3 回归：普通 SmokeTest，窗口绑定/AppData/全退) | verification/P20-AC4-FPS-1/smoke-20261018-194111/fps-trace.log | 16b99524794a7ff2132a19753ce6a7fcd53fc244 | 8b56cf627b8ea62ac733d5623c1145758eaf391639392e13f28f4020ea321950 | SOURCE_PIN |
| AC3-ac3-grabber.ps1 | AC3 | verification/P20-AC4-FPS-1/ac3-real-desktop/ac3-grabber.ps1 | 28a174aa9488a8e7a89ebe59cdd9fdd0addaefb5 | b00347ed47514911c480282791ff0542467d342b2bd1dd6a5069c6f3f8730b7d | SOURCE_PIN |
| AC3-AC3-REPORT.md | AC3 | verification/P20-AC4-FPS-1/ac3-real-desktop/AC3-REPORT.md | 28a174aa9488a8e7a89ebe59cdd9fdd0addaefb5 | 97c0c0e141f3b68876c58a968996dd530617b014fbed450b972735152a5bb578 | CANONICAL |
| AC3-capture-channel-note.md | AC3 | verification/P20-AC4-FPS-1/ac3-real-desktop/capture-channel-note.md | 28a174aa9488a8e7a89ebe59cdd9fdd0addaefb5 | 673616c7b381f7d2c26ba2997bf863e7354c4c3b0d2851923e3d8020ad3f27d8 | CANONICAL |
| AC3-fps-single-samples.csv | AC3 | verification/P20-AC4-FPS-1/ac3-real-desktop/fps-single-samples.csv | 28a174aa9488a8e7a89ebe59cdd9fdd0addaefb5 | f9a41f61292675b4e5664c4cecc5047edb8b72bd169c3a840f0026aa2086edf7 | CANONICAL |
| AC3-fps-single-summary.json | AC3 | verification/P20-AC4-FPS-1/ac3-real-desktop/fps-single-summary.json | 28a174aa9488a8e7a89ebe59cdd9fdd0addaefb5 | 9c318cc0f0347c33511177a1dad929e6dbc27ef646925b05fad2b19a62d133d8 | CANONICAL |
| AC3-fps-single-title-summary.txt | AC3 | verification/P20-AC4-FPS-1/ac3-real-desktop/fps-single-title-summary.txt | 28a174aa9488a8e7a89ebe59cdd9fdd0addaefb5 | 1d00f63b63e0e847b6972aa794e9fc13f830f003ad72fd90e361bbf009bc416b | CANONICAL |
| AC3-fps-webtoon-samples.csv | AC3 | verification/P20-AC4-FPS-1/ac3-real-desktop/fps-webtoon-samples.csv | 28a174aa9488a8e7a89ebe59cdd9fdd0addaefb5 | 0539fb098cc5c6b960cd101e71ced2a1538f7dbbd084269ff9270ebd561fd33a | CANONICAL |
| AC3-fps-webtoon-summary.json | AC3 | verification/P20-AC4-FPS-1/ac3-real-desktop/fps-webtoon-summary.json | 28a174aa9488a8e7a89ebe59cdd9fdd0addaefb5 | d022c634555b2d5f4f9f192fd4894e2985859af12042fd48ad0c7fe4b411c4f3 | CANONICAL |
| AC3-fps-webtoon-title-summary.txt | AC3 | verification/P20-AC4-FPS-1/ac3-real-desktop/fps-webtoon-title-summary.txt | 28a174aa9488a8e7a89ebe59cdd9fdd0addaefb5 | e45f9679cb1ea7ab3709d0283c59ffd033bbbe36e5cc2970e267e0b09623ab73 | CANONICAL |
| AC3-run1-appdata-after.txt | AC3 | verification/P20-AC4-FPS-1/ac3-real-desktop/run1-appdata-after.txt | 28a174aa9488a8e7a89ebe59cdd9fdd0addaefb5 | 16b1dda080293f09297c884a99b17ebd21a36e867ad74c04684b137773864279 | CANONICAL |
| AC3-run1-appdata-baseline.txt | AC3 | verification/P20-AC4-FPS-1/ac3-real-desktop/run1-appdata-baseline.txt | 28a174aa9488a8e7a89ebe59cdd9fdd0addaefb5 | 16b1dda080293f09297c884a99b17ebd21a36e867ad74c04684b137773864279 | CANONICAL |
| AC3-run1-single-trace.log | AC3 | verification/P20-AC4-FPS-1/ac3-real-desktop/run1-single-trace.log | 28a174aa9488a8e7a89ebe59cdd9fdd0addaefb5 | 73e4ff4cceaf74008ad208c267b54cd596f7218860ebec76dbdf1d5119538e39 | CANONICAL |
| AC3-run4-appdata-after.txt | AC3 | verification/P20-AC4-FPS-1/ac3-real-desktop/run4-appdata-after.txt | 28a174aa9488a8e7a89ebe59cdd9fdd0addaefb5 | 16b1dda080293f09297c884a99b17ebd21a36e867ad74c04684b137773864279 | CANONICAL |
| AC3-run4-appdata-baseline.txt | AC3 | verification/P20-AC4-FPS-1/ac3-real-desktop/run4-appdata-baseline.txt | 28a174aa9488a8e7a89ebe59cdd9fdd0addaefb5 | 16b1dda080293f09297c884a99b17ebd21a36e867ad74c04684b137773864279 | CANONICAL |
| AC3-run4-webtoon-trace.log | AC3 | verification/P20-AC4-FPS-1/ac3-real-desktop/run4-webtoon-trace.log | 28a174aa9488a8e7a89ebe59cdd9fdd0addaefb5 | 753bbaac6dd3a3cf39cb471799a40eafb505171bfe0193bb4fd73702f8f42c0f | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| 不新建 worktree | 复用 `G:/CODEX/New Manga` | `NOT_APPLICABLE` | 不适用 | 不适用 | 未创建、未删除资源。 |

## Closeout Record

- Closeout date / Codex：2026-10-18 / Codex（实现集成与资源核销；Task 未关闭）。
- `canonical_evidence_status`：`complete`；20/20 pin 的磁盘 SHA-256 与 commit:path 已核验。
- `resource_closeout_status`：`complete`；仅复用仓库工作区，无新建 worktree、需迁移/归档/删除的派生产物；操作计数均为 0。
- `integration_commit`：`16b99524794a7ff2132a19753ce6a7fcd53fc244`（已批准交付实现，且为当前主线祖先）；`delivery_head` 同此提交。
- 未关闭项及保留原因：AC3 单页与 Webtoon 真实桌面测量仍为 `NOT_RUN`，留给 Coordinator；AC5 按用户裁决保持 `NOT_VERIFIED_BY_RULING`。Task 保持 `approved`，不得设为 `done`。
- 当前指针：STATUS/Plan 保留 P20-AC4-FPS-1 当前项，标明实现已批准集成、等待 Coordinator 的 AC3 实测；AC5 限制不变。
- Governance check：20/20 pin 独立校验 `PASS`；`check.ps1` 返回 `FAIL (1 errors, 3 warnings)`，唯一错误把“已集成的 `approved` + AC3/AC5 未完成”按 DONE 拦截。依用户裁决保留 `NOT_RUN` / `NOT_VERIFIED_BY_RULING`，不伪记完成。
