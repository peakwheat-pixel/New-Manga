---
id: M2-RG1
title: M2 Release Gate（Windows 本机口径）：cold start metrics / Windows matrix / console policy / packaged dependency closure
kind: acceptance
status: done
release_state: M2_RG1_RELEASE_GATE_RELEASED
approval: approved_by_user_2026-09-29_local_machine_ruling
execution_approval: approved_by_user_2026-09-29_local_machine_ruling
suggested_owner: ZCode
owner: ZCode
claimed_by: ZCode
claimed_at: 2026-09-29
reviewer: DeepSeek Harness
integrator: Codex（编排会话代行，保持 Owner≠Integrator）
depends_on: [M2-AC5]
base_commit: 875eb818abc74a498c84026016dd1a1c72e0ad50
branch: agent/zcode/M2-RG1-release-gate
worktree: G:/CODEX/New Manga.worktrees/M2-RG1-zcode
delivery_head: e752ba39c2cd2e566105ff00ec3150f50a09e0e3
review: doc/reviews/M2-RG1-a1100d75-dsh-r1.md（approved_with_conditions：0×P0、1×P1、3×P2、8×P3；r1 返修已闭合全部必闭项，见 Handoff r1 返修节）；doc/reviews/M2-RG1-6b6366fc-dsh-r2.md（changes_requested：P1-1(N)/P2-1(N) 必闭 + P3-1..8(N) 落字；r1 P1-1/P2-1 判定"真闭"，产品与 Gate 结论 25/25 成立——r2 返修见 Handoff r2 返修节）
integration_commit: b796bed3cb3d79b2d4208b29f3e53c956a018dee
dispatch_state: INTEGRATED
delivery_ledger: claim=33280f5e -> ac2-fix=29c71024 -> gate-v1=a1100d75 -> bookkeeping=b38a646c -> [r1 import e218cc65 by integrator] -> r1-rework=05a8f93a/6b6366fc -> [r2 import c1177e5d by integrator] -> r2-closure=e752ba39 (delivery_head) / 8e0100ba (owner branch tip)；Owner branch/worktree 保留于 8e0100ba
---

# M2-RG1 — M2 Release Gate（Windows 本机口径）

## 来源与目标

来源：[Rebaseline Plan](../REBASELINE_PLAN.md) M2 Acceptance Backlog 第 6 行（"M2 Release Gate | backlog"）与 Acceptance Backlog 表行 "Cold-start metrics, target Windows support matrix, GUI console policy and packaged dependency closure | DEFERRED | Decide and verify in a future M2 Release Gate/D08; do not inherit the Legacy results."

**用户裁决（2026-09-29，存档原文）**："把本机视为干净widows环境。若本机通过，则视为pass"——据此解除"真干净机覆盖"前置：本机（Windows 11 x64，build 26200）即为验证基座；本机全项通过 ⇒ 本 Release Gate PASS。该裁决按 D08"范围删减、阈值豁免先形成用户可审查的文档决定"的要求以此 Task 文件与 release evidence 固化。

**目标**：对 [M2-AC5](M2-AC5.md) 交付的分发形态（NSIS installer + onedir 四入口自包含 sidecar）执行 Release Gate 四项：**cold start metrics、Windows support matrix、GUI console policy、packaged dependency closure**——每项做出**可审查的裁决（decision）**并给出**机器可验证证据**。可测对象已由 M2-AC5 就位；本 Task 是 M2 新架构首个正式发布验收 Gate（Legacy T3.2.1 PyInstaller Gate 已按 REBASELINE 撤销，不继承其结果）。

**形态：实现+验收混合（同 M2-AC5 先例）**。console policy 现状已在释放侦察中实证 FAIL（见 AC2 证据），故预授权有界修复；修复仅为达成 Gate 裁决所必需的最小改动。

## Acceptance Criteria

### AC1 构建锚定（可复现发布候选）

- [x] Owner worktree 从 `base_commit` 干净构建：先 `packaging/m2ac5/build_sidecar.ps1`（fresh-checkout 约束），后 Tauri NSIS bundle；构建日志带 shell 头 + 固定 HEAD + EXIT 入库。（实测：三步全 EXIT=0；顺序=sidecar→frontend install/build→tauri build）
- [x] 记录并锚定：installer sha256、sidecar 全清单 hash（沿用 M2-AC5 的清单格式）、工具链版本（pyinstaller/PySide6/tauri CLI/rustc/NSIS）；本机 OS 版本快照（Windows 11 x64 build 26200）。（实测：pre-fix build1=`def5b92b…`；**修复后 Gate 锚定=`d222073b…`**；清单 161 文件、首文件 sha256 与 M2-AC5 runA 一致；tauri-cli 2.12.0/pyinstaller 6.22.3/PySide6 6.11.2/rustc 1.98.1）
- [x] 后续所有 gate 运行绑定该 installer sha256（gate.json 记录），被测物与 release candidate 一一对应。（实测：rg1-gate.json 与 rg1-m2ac5-cleanstart-gate.json 均记录 `d222073b…`）

### AC2 GUI console policy —— 裁决 + 验证（现状 FAIL，授权有界修复）

**裁决（frozen）**：packaged 产品正常运行（静默安装 → 冷启动 → 核心 workflow → 干净退出）期间，除应用主窗口外**零可见控制台窗口**。

**现状实证（释放侦察，2026-09-29）**：
- `target/release/m2rc1-desktop.exe` PE OptionalHeader Subsystem=**3（CONSOLE）**（python 解析 e_lfanew→Subsystem 字段实测）；main.rs 无 `windows_subsystem` 属性——安装态双击即弹应用自身控制台。
- 全仓 `grep creation_flags|CREATE_NO_WINDOW` 零命中；`packaging/m2ac5/core_sidecar.spec:91` `console=True`——production 分派（main.rs:410-462）派生 `host_bridge.exe`+`core_service.exe`（ac1 模式再加 `acceptance_bridge.exe`）时各自弹控制台。

- [x] 机器可验证判据（gate runner 实现）：① installed `m2rc1-desktop.exe` PE Subsystem=2（GUI）；② 运行期 EnumWindows 观测：类名 `ConsoleWindowClass` **或 `CASCADIA_HOSTING_WINDOW_CLASS`**（r1 P2-1 加固：Windows Terminal 委托窗口属主为 WindowsTerminal.exe，pid 归属失效时按标题启发归属并写明边界），窗口标题或属主进程涉及 `m2rc1-desktop`/四 frozen 入口 exe 的顶层可见窗口数=0（app 运行中与退出后各采样）；**阳性对照 RG1-CW0**（r1 P2-1）：以 `powershell` 为载体、`CREATE_NEW_CONSOLE(0x10)` 故意不加 CREATE_NO_WINDOW spawn console 子进程，断言命中 ≥1——证明检测器能看见红（载体注记：`cmd` 载体在本机 ConPTY 继承环境下退出码 125 无窗口，故用 powershell）；③ dev 模式行为零变化（cfg_attr 仅 release 生效；`CREATE_NO_WINDOW` 仅按 `cfg(windows)` 门控，故 Windows debug 构建下 sidecar 控制台窗口亦不再出现，stdio 管道语义不变——r1 P3-8 注）。（实测 v2：①=2；② CW0 命中 1（CASCADIA_HOSTING_WINDOW_CLASS，属主 WindowsTerminal.exe pid 25252，标题=powershell.exe 路径）；CW1 三轮命中 0、app 全程存活、sidecar pid 快照入库；CW2 三轮命中 0；注册表 `HKCU:\Console\%%Startup` 双 null=Win11 默认委托与 CASCADIA 实证互证；③ 静态源审计全过——cfg_attr 门控/cfg(windows) 门控/spec 参数冻结）
- [x] **授权的有界修复**（仅此，不得扩大）：（commit 29c71024；diff 见 raw/rg1-console-policy-fix.diff）
  - `apps/desktop/src-tauri/src/main.rs` 顶部加 `#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]`；
  - `core_bridge.rs` / `ac1_bridge.rs` / `library_bridge.rs` 的 **Command 构建段**加 `creation_flags(CREATE_NO_WINDOW=0x08000000)`（`#[cfg(windows)]` 门控）；不改协议、不改参数语义、不改其他任何逻辑；
  - **`packaging/m2ac5/core_sidecar.spec` 的 `console=True` 参数值禁改**（stdio JSON 协议依赖管道；PyInstaller windowed 模式会改变 stdout 语义）——如注释需同步可改注释。（实测：仅注释同步，参数值未改）
- [x] 修复后重建 → 重装 → 复测 AC2 三判据全过；若修复引入回归（三层基线跌破）停下登记，不得用放宽断言换绿。（实测：重建 EXIT=0（raw/rg1-tauri-build-run2-fix.log）；三层基线全绿不回退）

### AC3 Cold start metrics —— 测录（无阈值）

**裁决（frozen）**：本 Gate **只测录、不设阈值**——冷启动阈值属用户产品裁决，Backlog 行仅要求 "cold-start metrics"。

- [x] 安装态（净化 PATH + `APPDATA=<lab>`）测量并落 gate.json + raw 日志，每项 ≥3 次采样（报 min/median/max）：
  - ① app 冷启动：`CreateProcess(installed exe)` → 首个可见顶层窗口（EnumWindows by pid, IsWindowVisible）耗时 ms；（实测 v2：46.9 / 49.9 / 160.2 ms，n=3；r2 P1-1(N) 更正：app 轮不 pin `NEWMANGA_DATA_ROOT`——app 轮的零触碰由 APPDATA 逐轮 pin + host 侧 `packaged_user_root()`（main.rs:315-319,366-367）派生并显式下传 data root（main.rs:446-452、library_bridge.rs:149-151）保证；`NEWMANGA_DATA_ROOT` 仅在 core/ac1/seed/DC1b/DC3 探针内显式 pin）
  - ② core ready：安装态 `core_service.exe` stdio probe spawn → `ready` 应答耗时 ms；（实测 v2：237.6 / 247.6 / 251.4 ms，n=3）
  - ③ ac1 handshake：安装态 `acceptance_bridge.exe` spawn → ready 耗时 ms。（实测 v2：267.2 / 267.6 / 268.5 ms，n=3；probe 按该 bridge 冻结契约 pin `M2AC1_TEST_MODE=1`）
  - v1（r1 前）数值 46.0/48.2/157.1、239.1/240.5/240.9、266.5/268.2/280.1 ms 存档于 `raw/rg1-gate-run1.json`，仅作对照不作判据。
- [x] 环境快照（PATH 净化条目数、APPDATA lab 路径、采样轮次）随数值入库；NOT_RUN 项（如有）如实标注原因。（实测：净化移除 11 条/保留 45 条；逐轮新 lab APPDATA（每轮均冷启动口径）；无 NOT_RUN）

### AC4 Packaged dependency closure —— 安装态闭环

- [x] 安装态**四入口** stdio 往返全部成功：`core_service.exe`（**DC1a**：先经 acceptance_bridge `seed_fixture`（M2AC1_TEST_MODE=1）向 lab data root 写入真实书目 → **DC1b**：core.ping ready + ListBooks envelope 断言 ≥1 行、含全部 8 个必需键——r1 P3-5 消除空列表恒真断言；实测 v2 books_count=1 + shutdown）、`host_bridge.exe`（资源通道握手）、`acceptance_bridge.exe`（ac1 handshake）、`catalog_loader.exe`（lab 数据根真实 seed + SQLite 读回）。（实测 v2：RG1-DC1a/DC1b/DC2/DC3/DC4 全 PASS；host_bridge 额外做 issue/resolve/revoke；catalog_loader CLI 参数从 worktree 源确认后 seed 2 行 + sqlite3 读回）
- [x] PyInstaller warn 文件（4 入口，`build_sidecar.ps1` 产物）入库并逐类审查：缺 load-time-critical 模块=FAIL；仅条件导入/可选模块=逐条披露。（实测：PyInstaller 6.22 产出**一份合并** warn-core_sidecar.txt 覆盖 4 入口（布局与释放侦察预期不同，已披露）；missing 共 11 条全部为条件/可选导入、0 条 load-time-critical；逐条清单见 gate.json）
- [x] 复用 M2-AC5 clean-start runner（25 场景）作为回归基线并在本 installer 上全 PASS；其证据按 **"运行 → 搬运（改名 `rg1-m2ac5-*` 入 `verification/M2-RG1/raw/`）→ `git restore verification/M2-AC5/`"** 处理——M2-AC5 raw 在本 Task worktree 中**不得提交**（runner 写死 `verification/M2-AC5/raw/` 绝对路径，属 M2-AC5 P3-9(b) 已知行为，披露即可）。（实测：25/25 PASS @ `d222073b…`（v2 复跑确认）；M2-AC5 目录 restore 后零变更）

### AC5 Windows support matrix —— 裁决 + 记录

**裁决（frozen）**：当前支持矩阵声明 = **"Windows 11 x64（本机 build 26200）已验证（本 Gate）；Windows 10 及其他 build 未验证（NOT_RUN，如实披露）"**。矩阵扩展（Win10 物理/虚拟机覆盖）登记为后续候选，不阻断本 Gate。

- [x] 本机环境快照入库：OS 名称/版本/build、架构、CPU/内存摘要。（实测：Windows 11 专业版 10.0.26200.9457 x64；Ryzen 9 7950X3D 16C/32T；33.98 GB）
- [x] Windows 10 / 其他版本 NOT_RUN 在 Task、Handoff、verification-results 三处如实标注（不得写成 N/A 或 PASS）。（实测：三处均标注 NOT_RUN）

### AC6 证据纪律与范围

- [x] 所有 raw 日志带 shell/解释器头 + 固定 HEAD + 每命令 EXIT；gate 汇总 JSON 机器可读。（实测：rg1-gate.json verdict=PASS **25/25（v2）**；r1 前 23/23 原样存档 `raw/rg1-gate-run1.json` 供 DSH r1 审计对照；例外披露：行尾空白/CR 规范化权威清单共 **10 份**（仅空白差异；r1 P3-3 统一，见 verification-results 披露 6）、M2-AC5 runner 产物为 runner 自有格式）
- [x] `git diff --name-status <base>..<delivery_head>` 对照两级允许路径（日志入库）；`git diff --check <base>..<delivery_head>` EXIT=0。（实测：4 个条件允许源文件 + spec 注释 + 新增 gate/evidence/doc；EXIT=0——r2 P2-1(N) 字面量口径：范围与 check 均以 `875eb818..e752ba39c2cd2e566105ff00ec3150f50a09e0e3`（内容修正 commit）为准，历史注记：区间在 `a1100d75` 时点（规范化前）EXIT=2，自 `b38a646c` 起恢复 EXIT=0；见 raw/rg1-final-scope-audit.log、raw/rg1-final-scope-audit-r2.log、raw/rg1-final-scope-audit-r3.log）
- [x] 三层基线不回退：`cargo test --bin m2rc1-desktop`（≥38 passed + 1 ignored）/ `pytest tests/m2_acceptance -q`（≥35）/ `npx vitest run`（≥31）全 EXIT=0；触碰 Rust spawn 段后 cargo 必须全绿。（实测：38+1 / 35 / 31 全 EXIT=0；r1 返修 P3-1 注释改动后 cargo 重跑 38+1 绿，raw/rg1-baseline-cargo-test-r2.log）
- [x] NSIS 卸载测试 NOT_RUN 如实披露（不在 Backlog 四项范围）；**`src/**` Python 零改动**（发现缺陷只记 FAIL/候选）。（实测：NOT_RUN 已披露于本表、Handoff、verification-results；src/** 零改动）

## 允许修改范围

**无条件允许**：
- `packaging/release-gate/**`（新增：gate runner 脚本 + README）
- `verification/M2-RG1/**`
- `doc/tasks/M2-RG1.md`、`doc/handoffs/M2-RG1-*.md`
- `doc/reviews/M2-RG1-*.md`（集成方导入——r2 P3-8(N) 补记）

**条件允许（仅当 AC2 现状 FAIL——释放侦察已实证成立，随 release 激活）**：
- `apps/desktop/src-tauri/src/main.rs`（仅顶部 `windows_subsystem` 属性）
- `apps/desktop/src-tauri/src/core_bridge.rs`、`apps/desktop/src-tauri/src/ac1_bridge.rs`、`apps/desktop/src-tauri/src/library_bridge.rs`（**仅** Command 构建段 `creation_flags`；AC2 冻结的修复形态）
- `packaging/m2ac5/core_sidecar.spec`（仅注释同步；`console=True` 参数值禁改）

**禁止**：`src/**`（Python）、`requirements.txt`、`doc/contracts/**`、`apps/desktop/frontend/**`、`packaging/m2ac5/run_clean_start_e2e.py`（M2-AC5 回归参照不得改）、`verification/M2-AC5/**`（不得提交）、`tauri.conf.json`（若证明必需，停下登记）、其他任何共享契约。

## 禁止范围

非目标：安装包 bit-for-bit 可复现（沿用 M2-AC5 候选登记）、NSIS 卸载链路、自动更新、代码签名、多语言/本地化、性能阈值设定（AC3 只测录）、Windows 10 实机覆盖（AC5 候选）。用户源文件、人工修改、Lock、current/pinned Revision 保护语义不在本 Task 触碰面。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | build_sidecar.ps1 + `npx tauri build`（worktree 内） | fresh worktree @ base | 全 EXIT=0；installer（修复后锚定）sha256=`d222073b…`；sidecar 清单 161 文件 | verification/M2-RG1/raw/rg1-build-sidecar.log、rg1-tauri-build-run1/run2-fix.log、rg1-sidecar-manifest-build1.txt、rg1-environment-record.log |
| AC2 | gate runner：PE subsystem 解析 + EnumWindows 运行期观测（双类名）+ CW0 阳性对照 | 安装态 | v2：Subsystem=2；CW0 命中 1（CASCADIA，WindowsTerminal pid 25252）；CW1/CW2 三轮命中 0；注册表双 null；静态源审计全过 | raw/rg1-gate.json（RG1-PE1/PE2/CW0/CW1/CW2 + environment）、rg1-console-policy-fix.diff |
| AC3 | gate runner：三类冷启动计时 ≥3 采样 | 安装态 + 净化 PATH | v2：app 46.9/49.9/160.2 ms；core ready 237.6/247.6/251.4 ms；ac1 267.2/267.6/268.5 ms（n=3）；v1 数值存档 rg1-gate-run1.json | raw/rg1-gate.json（timings）、rg1-gate-run.log、rg1-gate-run1.json |
| AC4 | 四入口 stdio 往返（DC1a seed → DC1b ≥1 行 8 键）+ warn 审查 + M2-AC5 25 场景回归 | 安装态 + lab 根 | v2：四入口全 PASS、DC1b books_count=1；warn 11 条全条件导入、0 load-time-critical；25/25 PASS @ 同 installer | raw/rg1-gate.json（RG1-DC1a/DC1b/DC2/DC3/DC4/W1）、rg1-warn-*.txt、rg1-m2ac5-cleanstart-gate.json |
| AC6 | 三层基线 + diff --check + name-status | worktree @ delivery head | cargo 38+1（r2 重跑）/ pytest 35 / vitest 31 全 EXIT=0；diff --check `875eb818..e752ba39c2cd2e566105ff00ec3150f50a09e0e3`（内容修正 commit，r2 P2-1(N) 字面量）EXIT=0（a1100d75 区间规范化前 EXIT=2 已注记）；name-status 全落允许路径 | raw/rg1-baseline-*.log、rg1-scope-audit.log、rg1-final-scope-audit.log、rg1-final-scope-audit-r2.log、rg1-final-scope-audit-r3.log |

## 产物与交接链接

- Handoff：`doc/handoffs/M2-RG1-a1100d75.md`（初交付版 + r1 返修节 + **r2 返修节**；r1 返修 delivery_head `05a8f93a7a96…`（仅历史），r2 后现行 delivery_head = 内容修正 commit `e752ba39c2cd…`，见 frontmatter 与 P2-1(N) 字面量口径）
- Release evidence：`verification/M2-RG1/release-875eb818.md`（已交付；汇总表 [verification-results.md](../verification/M2-RG1/verification-results.md)——r1 返修后为 v2 版）
- Review 报告：`doc/reviews/M2-RG1-a1100d75-dsh-r1.md`（DSH 非作者 r1，approved_with_conditions，集成方导入 @ e218cc65；r1 返修闭合清单见 Handoff r1 返修节）

## 已知阻塞

无。前置 M2-AC5 已 done；真干净机前置经用户裁决（2026-09-29）以本机口径解除。
