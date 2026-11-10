---
id: FEA-15-ACCEPT-1
title: FEA-15 集成正式验收（A1–A7 执行与缺口披露）
kind: acceptance
governance_version: 3
status: in_review
approval: **DSH 2026-11-10 冻结**；2026-11-10 用户授权接续，ZCode 独立会话裁决改派 Codex 并在 main 主树串行执行（见 `verification/FEA-15-ACCEPT-1/appointment.md`）
suggested_owner: codex
owner: codex
reviewer: ZCode 独立会话 sess_88acf941-2220-4c42-a4bf-ca95923a8cfe（r1；r2 待复审）
depends_on:
  - FEA-14-AI-1
base_commit: 164ebabcfa90b92fc46c07238280960fc01f7423
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: 6ad10aacf886a3c2b98ff3434070edf6b31dbf36
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/FEA-15-ACCEPT-1
allowed_paths:
  - doc/tasks/FEA-15-ACCEPT-1.md
  - doc/reviews/FEA-15-ACCEPT-1-*.md
  - doc/handoffs/FEA-15-ACCEPT-1-*.md
  - doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/FEA-15-ACCEPT-1/**
out_of_scope:
  - 不修改生产源码/测试（发现问题转诊断/修复卡，不在验收卡内顺手修）
  - 不新建安装包打包管线（若无安装包产物，A2 记 NOT_RUN + 打包缺口登记，不伪造通过）
  - 不改冻结契约字节；不 push
  - 不修改 FEA-14 已收口卡的历史证据
---

# FEA-15-ACCEPT-1：集成正式验收

## 背景

FEA-14 S5 七切片（SET/PREQ/EXPORT/READ/FONT/LIB/EDIT/AI 相关实现卡）已全部收口；`FEA-15-PREREQ-3` 已产出验收矩阵 `doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md`（准备版，非正式验收）。本卡执行 FEA-15 §S5 的正式验收：按 A1–A7 复用/重跑证据，对**依赖安装包、真实 UI 会话、真实旧库**的项如实登记 NOT_RUN 或执行，并给出可复核的验收结论与缺口清单。

## Scope 冻结（2026-11-10，DSH）

1. **A1 隔离干净构建**：在无 `bin/obj` 的干净 worktree 复核 Release 构建 0 错误 0 警告（重跑或复用 `FEA-15-PREREQ-3` 证据并核对 head）。
2. **A2 安装**：若存在可安装产物（安装包），执行安装→启动→四页面可达冒烟；若不存在，A2 = NOT_RUN + 明确打包缺口（不伪造）。
3. **A3 双 UI 回归**：legacy `MainWindow.Show()` 与 Fluent shell 两入口冒烟 + 关键路径测试；真实 UI 会话不可得时按测试层证据 + NOT_RUN 登记。
4. **A4 升级与回退**：旧库升级（FEA-13 迁移/备份/恢复证据）+ pre_restore 回退可执行性；真实用户库升级不可得时按 FEA-13/NEW-DB 证据 + NOT_RUN。
5. **A5 全量基线**：pytest + .NET 全量重跑（或复用 PREREQ-2 证据并核对 head）。
6. **A6 契约与 pin**：`verify_pins` 18/18、无未决 UNFREEZE。
7. **A7 FEA-14 汇总**：按冻结卡逐切片汇总（SET/PREQ/EXPORT/READ-1/READ-2/FONT-1/LIB-1/EDIT-1/AI-1 状态、limitation、NOT_RUN），并更新验收矩阵当前状态列。

## Acceptance Criteria

- [ ] **AC1 A1/A5/A6 复核**：干净构建、全量基线、18 pins 三项给出复核时点与 EXIT；与本卡 head 一致或说明差异。 <<PARTIAL: 构建和 pins PASS；pytest 与 .NET 全量 EXIT 1，部分失败根因仍待诊断>>
- [x] **AC2 A2 安装**：安装产物存在则实测安装/启动/四页可达；不存在则 NOT_RUN + 缺口登记（含缺失的打包交付物）。 <<MET>>
- [x] **AC3 A3/A4 真实层**：双入口冒烟与旧库升级/回退的真实层证据；不可得项 NOT_RUN 并给出可用替代证据（App/Host 测试层、FEA-13 五片）。 <<MET>>
- [x] **AC4 A7 汇总与矩阵**：七切片状态/limitation/NOT_RUN 汇总进 `FEA-15-INTEGRATION-ACCEPTANCE.md`，矩阵状态列更新。 <<MET>>
- [ ] **AC5 结论与门禁**：验收结论（通过/带 limitation/不通过）+ `check.ps1`（默认 + `-TaskPath`）+ pins；diff ⊆ allowed_paths。 <<PARTIAL: 验收结论和最终审查由 ZCode 独立会话裁决；最终门禁待固定交付 head 后复核>>
- [x] **AC6 证据**：`verification/FEA-15-ACCEPT-1/` 日志含 EXIT/时点；NOT_RUN 如实登记。 <<MET>>

## 证据计划（L2）

`verification/FEA-15-ACCEPT-1/`：`logs/`（构建、全量基线、pins/api、真实层冒烟或缺口说明）、NOT_RUN、复现命令。

## 风险与回退

| 风险 | 处置 |
|---|---|
| 无安装包/真实 UI 不可得 | A2/A3 记 NOT_RUN + 缺口清单，不伪造通过 |
| 真实用户库不可得 | A4 按 FEA-13/NEW-DB 证据 + NOT_RUN |
| 验收发现缺陷 | 只登记，另开诊断/修复卡，不在验收卡内改生产代码 |
| 基线漂移 | 全量基线以本卡 head 重跑为准，记录命令/时点/EXIT |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| temp | `G:\CODEX\New Manga.workspace\FEA-15-ACCEPT-1\`（隔离根） | PRESERVE_UNKNOWN | — | — | 仓外测试数据、源码档案/对照夹具（含解包失败副本）和专用 Python venv 暂保留；另有 FEA-11 测试硬编码共享 fixtures，候选清单见 `verification/FEA-15-ACCEPT-1/fixture-observation.log`，归属未证明，不清理 |
| user-data | `%APPDATA%\com.newmanga.desktop` | NOT_APPLICABLE | — | — | 只读；不写真实用户数据 |
| build | `G:\CODEX\New Manga.workspace\FEA-15-ACCEPT-1\clean-tree\apps\desktop-avalonia` | PRESERVE_REFERENCED | — | — | Release 构建产物，暂供复核 |
| worktree | `G:\CODEX\New Manga.workspace\FEA-15-ACCEPT-1\clean-tree` | PRESERVE_REFERENCED | — | — | detached `d63d735a712dbe47100db2e72b4d59a73dfd1f62`；主树为任务写入树，不执行清理 |
| runtime ACL | `C:\Python314\python.exe`、`C:\Python314` | PRESERVE_UNKNOWN | — | `verification/FEA-15-ACCEPT-1/python-acl-observation.log` | 插件测试会尝试授予 AppContainer 权限；无运行前 ACL 快照，新增项与归属不明，不擅自撤销 |
| AppContainer profile | 当前用户 profile（测试涉及的插件 profile） | PRESERVE_UNKNOWN | — | — | 测试可创建或复用；无事前清单，不推断新增项，不清理 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC1/A1 | `verification/FEA-15-ACCEPT-1/build.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `afb50adff42c1417c0a1a15cec693b15204d7b7d7d4d1417ea0c2bd8abf9ae90` | CANONICAL |
| EV-02 | AC1/A5、AC6 | `verification/FEA-15-ACCEPT-1/pytest-full-retry.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `3f2fe9639e3f349af6f57cd4c4d54da536f655a3b7ed44306cb70136435ccb0b` | CANONICAL |
| EV-03 | AC1/A5、AC3 | `verification/FEA-15-ACCEPT-1/dotnet-full.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `593aac3963b8c2e5fbb857ceab0f1ee6e82fa2d29cf6931d45240029a0f42c70` | CANONICAL |
| EV-04 | AC1/A6、AC2、AC3、AC5、AC6 | `verification/FEA-15-ACCEPT-1/README.md` | `e0bfd4c6ea8d18020b71be9215cccdace6247cfe` | `e4405800496b0004990c81d2b98051e89ec9feb3cdca3c2899e510add4368a1d` | CANONICAL |
| EV-05 | AC2、AC3、AC4 | `doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md` | `b7344445e3abc520c4d03fcb642b97880fe47738` | `e60dfcaf686fa4955c870c5ea64d0f31ff8e5bf7b9b93350f55b79d4ea773ddb` | CANONICAL |

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| SRC-01 | supporting | `verification/FEA-15-ACCEPT-1/appointment.md` | `d63d735a712dbe47100db2e72b4d59a73dfd1f62` | `c612cd90459e3a763fed72ce404c79fe0194d26c2fa39edd978b1a62a04ea734` | SOURCE_PIN |
| SRC-02 | supporting | `verification/FEA-15-ACCEPT-1/checkpoint.md` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `f41211d4ad72f0704e322d631166a30ffffdf72d29193e612ab1c98c253c918b` | SOURCE_PIN |
| SRC-03 | supporting | `verification/FEA-15-ACCEPT-1/desktop-fixture.log` | `b7344445e3abc520c4d03fcb642b97880fe47738` | `4563351238439f26e562d1bd4eaa1307cbb4aaf0f0a5f42a32b3fe4d892a9f23` | SOURCE_PIN |
| SRC-04 | supporting | `verification/FEA-15-ACCEPT-1/dotnet-host-control.log` | `b7344445e3abc520c4d03fcb642b97880fe47738` | `0ce018b15aa1413d02eeaf27b04afe3758ccb2d94bd8bdd882d3fcf29b5530ec` | SOURCE_PIN |
| SRC-05 | supporting | `verification/FEA-15-ACCEPT-1/dotnet-repo-root-control.log` | `b7344445e3abc520c4d03fcb642b97880fe47738` | `350714949785ccc0ebe86abbca6e3e5620a8f22191681f66cf5e7b16b5b66b3c` | SOURCE_PIN |
| SRC-06 | supporting | `verification/FEA-15-ACCEPT-1/environment.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `48c63a11f745fb2f0a19c1bd9724ef73c54d2177d3957cf7804e6d96533249e5` | SOURCE_PIN |
| SRC-07 | supporting | `verification/FEA-15-ACCEPT-1/fixture-observation.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `f54409a15d7b09d01eff581862fb65a78365ec7b4b469e0013f6419a377e48ab` | SOURCE_PIN |
| SRC-08 | supporting | `verification/FEA-15-ACCEPT-1/gates-control.log` | `b7344445e3abc520c4d03fcb642b97880fe47738` | `d285e23e58a2e199ee496ee1d06ae8868beec6785af7bad64415a3638c7b4d5c` | SOURCE_PIN |
| SRC-09 | supporting | `verification/FEA-15-ACCEPT-1/gates-post.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `ecf9ddec5e642729f549f825517031160d6f94bf3b51f87d0f90deb47dd85155` | SOURCE_PIN |
| SRC-10 | supporting | `verification/FEA-15-ACCEPT-1/gates.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `c679bae936f129da2ca0f040b1a283439ec63521f48dfed48538155addd55204` | SOURCE_PIN |
| SRC-11 | supporting | `verification/FEA-15-ACCEPT-1/plugin-control.log` | `b7344445e3abc520c4d03fcb642b97880fe47738` | `86422c6a9f385699d2614067b0600dcf9740244fe98750a48bfcf8d80e55232e` | SOURCE_PIN |
| SRC-12 | supporting | `verification/FEA-15-ACCEPT-1/plugin-fixture.log` | `b7344445e3abc520c4d03fcb642b97880fe47738` | `1e31fb17a31330689f7203e831a1007c1fa849e9555b93b5d06ce060e9f439ed` | SOURCE_PIN |
| SRC-13 | supporting | `verification/FEA-15-ACCEPT-1/pytest-collect.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `d003d929526724852521fbf066bfb350f4e66c0a204ae22fec191a73dbca47d4` | SOURCE_PIN |
| SRC-14 | supporting | `verification/FEA-15-ACCEPT-1/pytest-full.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `6b35d5b03fd0de2a21cbae7498bf6c544812fc9e162b4cac636ab899a564df70` | SOURCE_PIN |
| SRC-15 | supporting | `verification/FEA-15-ACCEPT-1/pytest-main-targeted.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `cb03bae893412b20c44325963bc98c83186f64f99b83f2508f150ef73a7eb59e` | SOURCE_PIN |
| SRC-16 | supporting | `verification/FEA-15-ACCEPT-1/python-acl-observation.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `4ef940a1bb3dfd567f7cf2be23679d344c578db6989c620b3a288fbfbbe8a385` | SOURCE_PIN |
| SRC-17 | supporting | `verification/FEA-15-ACCEPT-1/source-fixture.log` | `b7344445e3abc520c4d03fcb642b97880fe47738` | `3a57402b7e2df428f7a26f178a323739c96e958c35602e8b3c1dfae2dce53035` | SOURCE_PIN |
| SRC-18 | supporting | `verification/FEA-15-ACCEPT-1/ui-process-smoke.log` | `b7344445e3abc520c4d03fcb642b97880fe47738` | `2d884177ccba432dc5c9e33e4a06a6212ff2f022c76b0ce600ebbec67804eedf` | SOURCE_PIN |
| SRC-19 | supporting | `verification/FEA-15-ACCEPT-1/v7-repro-2.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `8e0abc01bec34b3e38cc3a9e6117d34f443529552d60405ca2860c271779a6e6` | SOURCE_PIN |
| SRC-20 | supporting | `verification/FEA-15-ACCEPT-1/v7-repro.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `3a1ec6a9963c803310368015b8df9010c18001346e3809ab430918d25566d1a4` | SOURCE_PIN |
| SRC-21 | supporting | `verification/FEA-15-ACCEPT-1/v7-v14-probe.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `bf1413267cffabc37b9f58e19526ae1e2ff4c0b98df9278f8c619d3e2cfe9dd7` | SOURCE_PIN |
| SRC-22 | supporting | `verification/FEA-15-ACCEPT-1/zcode-evidence-decision.log` | `b7344445e3abc520c4d03fcb642b97880fe47738` | `43dd07630a3ab0ba2a675778a361b02df50e9bf644f004eb3ceb2e0082a6aa2e` | SOURCE_PIN |
| SRC-23 | supporting | `verification/FEA-15-ACCEPT-1/zcode-second-decision-raw.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `b3a9c528617876ab3675407fecccc1bc50bda175842e0597eea27363385e0986` | SOURCE_PIN |
| SRC-24 | supporting | `verification/FEA-15-ACCEPT-1/zcode-serial-decision-raw.log` | `8cad6d68c1e455c087a20346c9b1c0217bef129e` | `a614b38f124c83557ff548d99a4e74c25dbd6fefe7857c3ec633a7fdbdd4fa4b` | SOURCE_PIN |

## Closeout Record

- 2026-11-10 scope 冻结（`ready`）。未开始。
- 2026-11-10 Codex 认领（`in_progress`），ZCode 独立会话 `sess_2a802094-24f6-4254-9bfa-33cad3a6bf4e` 裁决；主树串行，执行基线 `164ebabcfa90b92fc46c07238280960fc01f7423`。冻结范围不变。
- 2026-11-10 验证进行中：隔离 Release 构建 0 警告/0 错误 EXIT 0；pytest 全量 3515 passed/16 failed/12 skipped EXIT 1；.NET 八项目中 App 与 Host 失败、整体 EXIT 1。日志、隔离限制与 NOT_RUN 见 `verification/FEA-15-ACCEPT-1/README.md`；失败及下一步已交 ZCode 独立会话裁决，未作验收通过结论。
- 2026-11-10 补充证据：四项 App 仓库定位对照 4/4；Host 两项对照 1/1，ACL 异常仍存；专用 venv 插件对照 6 passed/10 failed；legacy/Fluent 仅隐藏进程级 EXIT 0，可见窗口与页面交互 NOT_RUN。现有结论为全量基线未满足、归因部分未定，最终验收结论待上下文独立 Review 与 ZCode 裁决。
- r1 P3-4：Handoff 对变更路径的概括句已由 r1 使用 `git diff --name-status` 核实；报告及具体范围见 `doc/reviews/FEA-15-ACCEPT-1-r1.md`。
- r1（独立 ZCode `sess_88acf941-2220-4c42-a4bf-ca95923a8cfe`，reviewed head `e55a23dc9b7c701e31360a9e41b9fc4a88d0bf30`）approved 附条件；P2-2/P3-1/2/3 已修正，P2-1 跨 checkout hash 风险已登记、治理修复待另行释放；条件与新 head 须经 r2 独立复核，未集成。
