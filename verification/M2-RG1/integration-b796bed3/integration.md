# M2-RG1 Integration Record — M2 Release Gate（Windows 本机口径）

- **Integration merge**：`b796bed3cb3d79b2d4208b29f3e53c956a018dee`（`--no-ff`，parents：main `79510a8b` + owner tip `8e0100ba`；冲突 2 处均为 add/add——`doc/tasks/M2-RG1.md`、`verification/M2-RG1/release-875eb818.md`，按"唯一 Task/证据文件冲突取 Owner 交付版"惯例以 `--theirs` 解决）
- **base**：`875eb818`；**release commit**：`79510a8b`；**Owner 交付链**：claim `33280f5e` → AC2 修复 `29c71024` → gate v1 `a1100d75` → bookkeeping `b38a646c` →（集成方导入 r1 `e218cc65`）→ r1 返修 `05a8f93a`/`6b6366fc` →（集成方导入 r2 `c1177e5d`）→ r2 收口 `e752ba39`（=delivery_head）/`8e0100ba`（=终 tip）。Owner branch/worktree 保留于 `8e0100ba`
- **Integrator**：编排会话代行 Codex（Owner=ZCode 子 agent，Owner≠Integrator 保持）

## 1. Review 链与条件闭合

| 轮次 | Session | Decision | 必闭项 | 闭合方式 |
|---|---|---|---|---|
| r1（[报告](../../doc/reviews/M2-RG1-a1100d75-dsh-r1.md)，SHA256 `943ba8f808…`，导入 `e218cc65`） | `session-1e36fc83` | approved_with_conditions（0×P0、1×P1、3×P2、8×P3） | P1-1 首跑日志引用不实；P2-1 检测器类名盲区；P2-2 diff-check 口径；P2-3 LOCALAPPDATA 论证 | Owner 返修 `05a8f93a`+`6b6366fc`：**gate v2 复跑 25/25**（新增 RG1-CW0 阳性对照真命中 `CASCADIA_HOSTING_WINDOW_CLASS`、DC1 拆 DC1a/DC1b seed 后 books_count=1）、P1-1 按"transcript 从未入库、仅文字披露"更正、LOCALAPPDATA 取证入库 |
| r2（[报告](../../doc/reviews/M2-RG1-6b6366fc-dsh-r2.md)，SHA256 `29116d9bd7…`，导入 `c1177e5d`） | `session-3cc0ef38` | changes_requested（r1 P1-1/P2-1 判"真闭"；新 P1-1(N)/P2-1(N) + 8×P3(N)） | P1-1(N) 7 处文档声称 round_env 已 pin `NEWMANGA_DATA_ROOT` 但代码无此行；P2-1(N) 审计范围未落终 tip 字面量 | Owner 纯文字收口 `e752ba39`+`8e0100ba`（采 DSH 方案 (a) 改文字为实、零代码新增、零重建、零重跑）：7 处统一为"APPDATA 逐轮 pin + host 侧派生显式下传；`NEWMANGA_DATA_ROOT` 仅探针内 pin，app 轮不 pin"；P2-1(N) 字面量落 `875eb818..e752ba39`（EXIT=0 原样贴入）；P3-1..8(N) 全部落字 |

## 2. 集成方终验（merge 前，@ `8e0100ba`）

1. `git diff --check 875eb818..8e0100ba` → **EXIT=0**
2. runner 代码事实自证：`timed_app_cold_start`（`run_release_gate.py:472-481`）确只 pin `APPDATA`+`WEBVIEW2_USER_DATA_FOLDER`，与改后措辞一致（P1-1(N) 方案 (a) 正确落地，提交 runner = 产生 v2 gate.json 的 runner）
3. `git status --porcelain` → 空（干净）
4. installer sha256 → `d222073becc50d59…`（与 gate 绑定一致，未重建）
5. name-status 45 文件全落两级允许路径、禁改路径（`src/**`/`requirements.txt`/contracts/frontend/`tauri.conf.json`/`run_clean_start_e2e.py`/spec console 参数/`verification/M2-AC5/**`）零命中；Handoff:57 的"残留"行经核实为 r2 更正叙事本身（描述旧声称→更正），非不实声明

## 3. 集成复跑（@ merge `b796bed3`，[raw 日志](../raw/i-integration-replay.log)）

| 命令 | 结果 | EXIT |
|---|---|---|
| `cargo test --bin m2rc1-desktop`（apps/desktop/src-tauri） | 38 passed / 0 failed / 1 ignored | 0 |
| `TASK-012-py312 python -m pytest tests/m2_acceptance -q`（解释器=`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`） | 35 passed | 0 |
| `npx vitest run`（apps/desktop/frontend） | 31 passed（5 files） | 0 |
| `git diff --check 875eb818..b796bed3` | 无输出 | 0 |

与 M2-AC5 收口基线（38+1 / 35 / 31）持平，无回退。首次复跑尝试因 shell 内 `cd ../..` 路径算术错误产生过一份含 command not found/usage 输出的日志，已用完整正确重跑整体覆盖（现文件为终版；该过程性日志未保留，特此披露）。

## 4. Gate 终态（关键数字，全部经 DSH 两轮独立复算）

- **GATE PASS 25/25**（v2；v1 23/23 存档 `raw/rg1-gate-run1.json`）：AC2 PE Subsystem=2（GUI）+ EnumWindows 双类名运行期观测 0 命中（CW1 三轮 app 存活、sidecar_pids_seen=2；CW2 退出后 0）+ **CW0 阳性对照命中 1**（检测器先证能红）；AC3 冷启动测录 app 46.9/49.9/160.2 ms、core ready 237.6/247.6/251.4 ms、ac1 handshake 267.2/267.6/268.5 ms（n=3，无阈值）；AC4 四入口安装态 stdio 闭环 + warn 11 条 missing 全条件导入 0 load-time-critical + M2-AC5 25 场景回归 25/25；AC5 Win11 x64 build 26200 已验证、Win10 NOT_RUN 三处披露；AC6 证据纪律与范围全过
- **用户裁决锚点**："把本机视为干净widows环境。若本机通过，则视为pass"（2026-09-29）——本机全项通过 ⇒ **M2 Release Gate PASS**

## 5. 遗留与候选登记

- Windows 10/其他 build 实机覆盖（AC5 冻结裁决候选）；NSIS 卸载链路与 per-user 注册表/快捷方式残留清理（r1 P3-6 候选）；CW0 属主镜像名入 gate.json hits[]（r2 P3-5(N) 若做 v3 取证）；bit-for-bit 可复现、fresh-checkout beforeBuildCommand 根治（承 M2-AC5 候选）
- Real docTR qualification：维持 BLOCKED（需用户受控权重/环境/质量阈值，释放权在用户）
