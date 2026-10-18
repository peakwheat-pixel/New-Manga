---
id: P20-AC4-FPS-1
title: P20 AC4 帧率与帧时间测量（默认关闭的前端 requestAnimationFrame 采样钩子）
kind: feature
governance_version: 2
status: in_review
approval: user_ruling_20261018_ac4_fps_measurement
blocked_by: null
suggested_owner: ZCode
owner: ZCode
reviewer: Codex
depends_on: [P20]
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
branch: null
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: 4c54f3dd1
canonical_evidence_status: pending
resource_closeout_status: pending
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

- Handoff：`doc/handoffs/P20-AC4-FPS-1-zcode.md`（r1 返修 delivery_head = `4c54f3dd1`）。
- Review：r1 `codex-review-r1.md` 结论 `changes_requested`（五项 finding 全处置见上）；r2 待 Codex 独立复审（Owner 不审自己的变更）。
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

## Canonical Evidence

r1 返修交付 head 已固定（`4c54f3dd1`，r0 原始交付为 `011293151`）；下表为 Owner 侧登记，`CANONICAL` 定级与最终裁决由 Codex Review 后确认。真实桌面测量产物（`run-*/`）在 Coordinator 执行后由 Review 阶段补登。r1 证据按磁盘真实字节实算（本轮写入文件为 LF 行尾；`011293151` 时为 CRLF 检出字节）。

| evidence_id | AC/Gate | path | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EVID-FPS-HOOK | AC1, AC2, AC4 | apps/desktop/frontend/src/perf/fpsRecorder.ts | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | 6435b9f9d01b71277e0a352701c14e15c27ac746c47697f18c723227185ce3e8 | SOURCE_PIN |
| EVID-FPS-PANEL | AC2 | apps/desktop/frontend/src/perf/FpsRecorderPanel.tsx | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | 527f2999d5157facc3bba8702ee105dcdf2441587abff60409e4c719b01b86a6 | SOURCE_PIN |
| EVID-FPS-TESTS-RECORDER | AC1, AC2, AC4 | apps/desktop/frontend/src/perf/fpsRecorder.test.ts | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | 9595256a211ff5d0a96a4bd7f9aadf403941f59797dcd8d1b3f087583066a0ca | SOURCE_PIN |
| EVID-FPS-TESTS-PANEL | AC1, AC2, AC6 | apps/desktop/frontend/src/perf/FpsRecorderPanel.test.tsx | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | fe6e7739ec4c067cd5653a3a74662b23f7b119970357feef3120268a5cbc0ac8 | SOURCE_PIN |
| EVID-FPS-WIRING | AC1, AC6 | apps/desktop/frontend/src/main.tsx | 01129315100928751546c9608456868f5085fa8c | b8f79fdc6746a250515af97970e6c3067f4bab10218c582b677490b57e6be050 | SOURCE_PIN |
| EVID-FPS-NPMTEST | AC1, AC6 | verification/P20-AC4-FPS-1/npm-test-20261018.log | 01129315100928751546c9608456868f5085fa8c | f14e86b5491f0e8012a89c717a931f1b84c5283931cbf2fd26093ab13188e355 | SOURCE_PIN |
| EVID-FPS-NPMTEST-R2 | AC1, AC6 | verification/P20-AC4-FPS-1/npm-test-20261018-r2.log | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | 110a8eaffe6010f4c1e9a48d081d1d25bc7161e6cb5da933693a49eb21f56ae4 | SOURCE_PIN |
| EVID-FPS-RUNNER | AC3 | verification/P20-AC4-FPS-1/run-ac4-fps.ps1 | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | a73cbcb6fe550b872a4a6c2bd41e87074905f915c840274b58039935ac2319fc | SOURCE_PIN |
| EVID-FPS-GUIDE | AC3, AC5 | verification/P20-AC4-FPS-1/MEASUREMENT-GUIDE.md | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | 2856f9df5cebfae9d9b22717bd5d27bd1e78afe8a12b381b8c37631f115a3b93 | SOURCE_PIN |
| EVID-FPS-REVIEW-R1 | Review | verification/P20-AC4-FPS-1/codex-review-r1.md | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | 5ef026d9f300ea0a501c001b878e31f1c46337f68952c2a64c56607a28bd037f | SOURCE_PIN |
| EVID-FPS-SELFCHECK | AC3 (runner 隔离自检) | verification/P20-AC4-FPS-1/selfcheck-20261018-173828/fps-trace.log | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | f4a88496237617069a5dd41fb6850eeec84556cd96ab25e7cddb6741d0501491 | SOURCE_PIN |
| EVID-FPS-SMOKE | AC3 (runner 隔离冒烟) | verification/P20-AC4-FPS-1/smoke-20261018-173917/fps-trace.log | 4c54f3dd10e5e7168500e96687b67097ccae2c00 | a7dd5a9378e57ab6d612592f128f6bcf8a7b9324a27304504aea52a3d64ea4c9 | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| 不新建 worktree | 复用 `G:/CODEX/New Manga` | `NOT_APPLICABLE` | 不适用 | 不适用 | 未创建、未删除资源。 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- `canonical_evidence_status`：`pending`。
- `resource_closeout_status`：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待 Owner 交付和 Review。
- 当前指针清理：待 Task 激活或关闭时由 Codex 同步 STATUS/Plan。
