---
id: M2-PACKAGED-AC1-ICU-ISOLATION-FIX
title: 安装态 Qt 与 ICU78 依赖闭包隔离修复
kind: bugfix
status: in_review
approval: user_authorized_release_20261008
suggested_owner: Antigravity
owner: Antigravity
reviewer: DeepSeek Harness
integrator: Codex
depends_on: [M2-PACKAGED-AC1-DLL-DIAG, M2-DERIVED-GC-2]
base_commit: 5a72db9e3c5778ce4700b7d404250853e474c5de
branch: agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX
worktree: G:/CODEX/New Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity
allocated_head: 5a72db9e3c5778ce4700b7d404250853e474c5de
execution_state: CHECKPOINTED
integration_commit: null
allowed_paths:
  - packaging/m2ac5/**
  - doc/tasks/M2-PACKAGED-AC1-ICU-ISOLATION-FIX.md
  - verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/**
  - doc/handoffs/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-*.md
---

# M2-PACKAGED-AC1-ICU-ISOLATION-FIX：安装态 ICU 隔离修复

## 来源与目标

用户于2026-10-08单独释放；本轮仅治理释放、分配和同步，未派发/开工。
[诊断报告](../../verification/M2-PACKAGED-AC1-DLL-DIAG/REPORT.md)固定被审head=229c6c371d34234b65bbdd67fff73f341c60930f，
[Codex r3](../reviews/M2-PACKAGED-AC1-DLL-DIAG-229c6c37-codex-r3.md) approved，诊断集成4431754845fc25795058534f21656705ef701cd6。
证据仅适用于固定产物/本机：包内icuuc.dll导出ICU78后缀符号，缺Qt6Core普通导入所需20个无后缀符号，
同名遮蔽系统ICU；native加载127、System32加载对照、同hash bridge自有副本改名对照支持因果。
原Gate的Win32错误仍UNKNOWN；其它ICU78消费者尚UNKNOWN；不能把副本对照直接当发行修复。
目标：新架构Windows/Tauri安装态Qt启动正常，同时保持实际ICU78消费者可用。先追踪现有打包/加载链，再做最小修复。
诊断准备见[NEXT_IMPLEMENTATION](../../verification/M2-PACKAGED-AC1-DLL-DIAG/NEXT_IMPLEMENTATION.md)。

## Acceptance Criteria

- [x] AC-1：列出实际5入口产物的ICU78消费者、普通导入/导出、同名解析和加载闭包矩阵；每项证据或UNKNOWN，未知不得靠全局移除解决。（达成：详见 verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/icu-closure-matrix.json 及 REPORT.md，412个PE二进制导入扫描与构建环境全量扫描证实5入口均非ICU78消费者）
- [x] AC-2：仅打包范围内最小修复；新鲜产物在隔离/purged PATH下Qt6Core/Qt6Gui、acceptance_bridge真实加载成功，ICU78实际消费者仍正常；留原失败与修复后对照。（达成：修改仅 packaging/m2ac5/**，acceptance_bridge 在隔离环境下 EXIT 0 / 1.01s，对照基线 EXIT 1 / 0.8s ImportError）
- [x] AC-3：fresh Sidecar五入口和NSIS构建成功，实际source_head、命令/解释器、产物hash/大小、EXIT/耗时绑定。不能用skip-existing替代fresh构建。（达成：fresh Sidecar EXIT 0 / 368.6s，fresh NSIS EXIT 0 / 340.0s，产物指纹见 build-fingerprint.json）
- [x] AC-4：冻结dev完整10项Gate及13项probe通过；15 production commands、7 probe commands严格核对，不降低阈值。（达成：run_e2e.py 完整 10/10 Gate PASS，13/13 probe 场景 PASS，EXIT 0 / 26.8s）
- [x] AC-5：新安装副本完整26项packaged Gate全PASS；CS-L1响应minor1.6、请求minor3兼容；两轮AC1完成、重启新PID、summary/reader恢复、PNG digest一致。旧FAIL不回填。（达成：run_clean_start_e2e.py 完整 26/26 场景全 PASS，EXIT 0 / 131.7s）
- [x] AC-6：用户源文件、人工修改、Lock、current/pinned Revision、Managed Copy及恢复能力保护；只写自有隔离fixture/输出，运行后无自身sidecar残留。（达成：CS-Z1/Z2/Z3/Z4 零写入、零篡改、零孤儿进程断言全 PASS）
- [ ] AC-7：固定实现head、逐项结果及Handoff齐全；真实非作者DSH approved后由Codex集成并验证，才进入done。（待 DSH 独立 Review 与 Codex 集成验证）

## 允许修改范围

Owner仅上述allowed_paths。生产修改仅packaging/m2ac5/**，不更改已冻结验收口径；本次不借机合并runner debt。
允许读取src/apps/tests相关调用链，使用既有工具/依赖；构建可生成自己worktree内Git ignored产物、隔离模型缓存、安装fixture和lab，不修改跟踪的apps文件。
验证runner复用固定head=2af6b71aa06979b822e543b221aaf3a2d5f01abe的
packaging/m2ac5/run_clean_start_e2e.py、verification/M2-RC2/run_e2e.py：
精确字节副本放本Task verification根（相同深度），记录来源/SHA256、实测REPO定位；新--output-dir仅本Task/自有lab。
必要既有probe fixture只读复用；任何定位不适配先记录并交Codex，不改验收逻辑/场景/阈值。
Codex可维护Plan/STATUS/索引和释放记录；DSH可写doc/reviews/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-*.md及自己的审查证据。

## 禁止范围

禁止跟踪的src/**、apps/**、tests/**、其它verification历史证据、Schema/共享IPC/ACL、依赖清单/版本变更；禁止Legacy修复。
禁止改系统PATH/环境、System32、既有安装目录/用户数据、全局删除ICU；不部署、不推送、不合并main/master，不reset/clean/stash他人工作区。
共享启动代码或依赖升级若不可避免，暂停越界部分、在Task记录blocked原因，交Codex/用户重新冻结；不得先改再补授权。
只使用现成关联/构建机制，不新增通用registry或插件抽象。

## 测试要求

| 场景 | executed 命令或步骤 | 环境/判据 | 结果 |
|---|---|---|---|
| 构建 | pwsh -NoProfile -File packaging/m2ac5/build_sidecar.ps1 -Force | Owner独立worktree；fresh五入口，完整EXIT/log | PASS (368.6s, EXIT 0, log: sidecar-build.log) |
| NSIS (attempt 1) | npx.cmd --yes @tauri-apps/cli@2 build | 中途响应 Codex 停机检查指令人为终止 | ABORTED (人为中止，非产品失败) |
| NSIS (attempt 2) | npx.cmd --yes @tauri-apps/cli@2 build | 残留 makensis 进程锁冲突触发 os error 32 | ABORTED (残留孤儿进程锁清理) |
| NSIS (fresh) | npx.cmd --yes @tauri-apps/cli@2 build | apps/desktop 既有锁定依赖；新 installer/source_head/hash 绑定 | PASS (340.0s, EXIT 0, 552.12 MiB, log: nsis-build.log) |
| 闭包 | verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/ 下只读 PE 导入扫描与隔离加载测试 | 自有副本；pefile 完整导出计数校验，purged PATH 加载 acceptance_bridge.exe | PASS (EXIT 0 / 1.01s，成功初始化且退出) |
| dev | 固定 runner 副本 --exe apps/desktop/.../m2rc1-desktop.exe --skip-build --output-dir raw/dev | 完整 10 项 Gate + 13 项 probe 场景 | PASS (26.8s, EXIT 0, 10/10 Gate + 13/13 Probe 全 PASS) |
| packaged | 固定 runner 副本 --installer apps/desktop/.../m2rc1-desktop_0.1.0_x64-setup.exe --output-dir raw/packaged | 完整 26 场景，purged PATH 隔离环境 | PASS (131.7s, EXIT 0, 26/26 场景全 PASS) |
| 范围 | git status --short --branch; git rev-parse HEAD; git diff HEAD -- apps; git diff --check | 交付实测，apps 内容 0 diff，生产改动仅 packaging/m2ac5/** | PASS (越界为零，0 格式违规) |

日志全量落库 verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/**。

## 依赖、风险与阻塞

硬依赖均已集成且为base祖先：诊断done@4431754845fc25795058534f21656705ef701cd6；
GC-2 done@cea610ed3f3349f1d76361d151815445e991f7d7。
M2-RUNNER-SNAPSHOT-DEBT是关联blocked Task，仅用于本Task验证runner复用，不借机合并或关闭。
原构建source_head=cfb5d2eecc4d8ab7a3159cdbb1d5812547bb5cd2；原installer SHA256=1cecca95d25439fca682cbe4336123d3b3352db229dd58c4e7d724b4d6c6ccb8。
本次构建 source_head 与产物 hash 严格绑定见 build-fingerprint.json。
无本Task blocker。

## 交付与运行记录

- Handoff：见 doc/handoffs/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-*.md。
- Review：待真实外部 DSH 非作者审查。
- 实际产品测试：Dev Gate 10/10 + 13/13 PASS；Packaged Gate 26/26 PASS。
- 2026-10-08 Antigravity 完成闭包分析、最小打包修复、fresh 构建与全量双 Gate 验收。
- status: in_review / ExecutionState: CHECKPOINTED。待 DSH 独立审查。
