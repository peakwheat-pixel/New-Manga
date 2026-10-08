---
id: M2-PACKAGED-AC1-DLL-DIAG
title: 新架构安装态 AC1 QtGui DLL 加载失败只读诊断
kind: research
status: in_progress
approval: user_authorized_release_20261008
suggested_owner: DeepSeek Harness
owner: DeepSeek Harness
reviewer: Codex（非作者）
integrator: Codex
depends_on: [M2-DERIVED-GC-2]
related_blocked_task: M2-RUNNER-SNAPSHOT-DEBT
base_commit: 9063c317937b86bed1f6ff3e2f2c5d224dc10553
branch: agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG
worktree: G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh
integration_commit: null
---

# M2-PACKAGED-AC1-DLL-DIAG：安装态 AC1 DLL 诊断

2026-10-08 用户明确授权单独释放。TaskStatus=in_progress，ExecutionState=ACTIVE；
2026-10-08 用户授权自动调用外部Agent，Codex已串行登记DSH认领；即将真实CLI派发，诊断测试当前NOT_RUN。

## 来源、依赖与冻结输入

- M2-DERIVED-GC-2 done@cea610ed，祖先关系已实测。它是唯一硬依赖。
- M2-RUNNER-SNAPSHOT-DEBT仍blocked，不作为done依赖；仅消费其已固定失败证据。
- 主线诊断base=9063c317937b86bed1f6ff3e2f2c5d224dc10553；原构建source_head=cfb5d2eecc4d8ab7a3159cdbb1d5812547bb5cd2。
- 原runner Owner证据HEAD=15cd788f10e83f6a1a215e71538bfa175b435785；
  G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex只读，不在那里执行会写输出的命令。
- verification/M2-RUNNER-SNAPSHOT-DEBT/build-fingerprint.json、result-summary.json、
  raw/packaged/cleanstart-ac1-run1-stdout.log、raw/packaged/cleanstart-gate.json、
  raw/sidecar-build.log、raw/sidecar-weights-retry.log、raw/nsis-build.log。
- 原installer实际路径/哈希见本Task input-manifest.json。SHA256=
  1cecca95d25439fca682cbe4336123d3b3352db229dd58c4e7d724b4d6c6ccb8；589904619 bytes。
  释放前已重新实测匹配；开始诊断时再次检查，ignored二进制变化/缺失记DRIFT/BLOCKED，不能猜旧产物。
- 事实：packaged CS-L1 PASS；完整26项=20 PASS/1 FAIL/5 NOT_RUN；
  acceptance_bridge在bootstrap/acceptance_bridge.py:173导入PySide6.QtGui时报ImportError。
  具体失败DLL/导出符号/搜索路径原因及单次退出时间线UNKNOWN，不能以QtGui模块名推断DLL缺失。
- 只读追踪src/bootstrap/acceptance_bridge.py装配、packaging/m2ac5/core_sidecar.spec、
  build_sidecar.ps1、实际入口和新架构Tauri packaged AC1调用链；已有路径先复用。
  Qt在此只是新架构验收sidecar的依赖，不开启Legacy PySide6/QML UI诊断或修复。

## 目标与 Acceptance Criteria

最小可复核诊断：区分失败DLL/依赖/导出符号/搜索路径/构建环境原因，证据不足保留UNKNOWN；
给出另行冻结的最小修复范围建议，本Task不实施修复。

- [ ] AC1 Reality Check：实际base/head/branch/common-dir/clean、输入hash、环境/工具版本；
      planned与executed分开，原始shell/命令/EXIT日志入本Task目录。
- [ ] AC2 原失败与有界复现：使用hash匹配的二进制，在自有隔离lab复现同一导入失败，
      或明确无法复现/工具不可用的BLOCKED/NOT_RUN；记录调用方式、purged PATH、退出与时间线。
      主线未合并旧Task runner修复，禁止直接用当前checkout旧快照runner混淆诊断。
- [ ] AC3 DLL/closure矩阵：每个候选写实际文件路径/hash/依赖关系、加载观测、证据、
      PROVEN/REJECTED/UNKNOWN；文件存在不等于能加载，静态依赖扫描不等于运行验证。
      只追踪与QtGui导入直接相关的闭包，不进行全仓架构审计。
- [ ] AC4 环境差量与最小范围：原PowerShell5 PyInstaller成功、weights步骤失败，PS7只恢复hash/copy；
      与既有PASS构建只比较有固定head/hash的证据，未取得对照记UNKNOWN。
      给出根因置信度、最小拟议修复allowed_paths和后续fresh/full Gate，未授权修复不启动。
- [ ] AC5 交付固定报告/矩阵、原始日志、Handoff，产品/历史证据零diff；Codex非作者Review、
      文档集成验证后才done。诊断done不等于旧Task解除阻塞或完整packaged PASS。

## allowed_paths

Owner只允许写：
- doc/tasks/M2-PACKAGED-AC1-DLL-DIAG.md（状态/运行记录，不自行扩大范围）
- verification/M2-PACKAGED-AC1-DLL-DIAG/**（报告、矩阵、最小诊断探针/日志、自有隔离fixture）
- doc/handoffs/M2-PACKAGED-AC1-DLL-DIAG-*.md
Reviewer Codex只写doc/reviews/M2-PACKAGED-AC1-DLL-DIAG-*.md；Codex治理可维护Plan/STATUS/索引。
共享接口/Schema/依赖修改授权：无。

## 禁止范围与停止条件

src/**、apps/**、tests/**、packaging/**、依赖/Schema/wire/ACL/模型/构建spec脚本全部只读；
不改现有runner阈值或历史raw，不删用户/Managed Copy/他人文件，不reset/clean/stash，
不改系统PATH/安装开发Qt绕过Gate，不升级/重装共享task-env，不部署/推送/合并main。
允许将固定输入复制/解包到本Task独占隔离lab并只写其中的fixture；只终止本Task创建的进程。
临时诊断环境对照必须独立子进程、记录原环境与差量，不能替代原purged PATH验收或宣称Gate修好。
输入漂移、越界需求、沙箱无法执行时记录BLOCKED/UNKNOWN交Codex，禁止自行补生产修复。

## 验证计划（全部planned，释放阶段诊断NOT_RUN）

PowerShell；可用解释器候选G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe，
开始时实测；只读构建环境m2ac5-build，不能把旧版本记录当本次验证。
逐步先读固定日志/spec与调用链，再hash验证并隔离复制/解包，用现有工具做最小DLL加载对照；
工具不具备则明确NOT_RUN，不为诊断安装新共享依赖。具体探针/运行命令由DSH创建后记录，
本释放不编造尚未存在命令或诊断PASS。

~~~powershell
Set-Location 'G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh'
git status --short --branch
git rev-parse HEAD
git rev-parse --path-format=absolute --git-common-dir
git diff --check
# 诊断后核对固定base与交付head（且检查所有变更均在allowed_paths）：
git diff 9063c317937b86bed1f6ff3e2f2c5d224dc10553 HEAD -- src apps tests packaging
~~~

报告=verification/M2-PACKAGED-AC1-DLL-DIAG/REPORT.md；候选矩阵/原始日志也在该目录。
使用doc/templates/HANDOFF.md和REVIEW.md；Handoff在固定delivery_head后追加，避免自引用。
AC逐项记录PASS/FAIL/BLOCKED/NOT_RUN和证据；UNKNOWN不可填为根因确认。

## 释放与下一步

allocated初始HEAD=9063c317937b86bed1f6ff3e2f2c5d224dc10553，本Task worktree已创建并实测clean/common-dir正确。
实际release commit与同步HEAD由Codex提交后写入主仓库
G:/CODEX/New Manga/verification/M2-PACKAGED-AC1-DLL-DIAG/release.md及DSH_INSTRUCTION.md，
DSH启动前读取该实际恢复点，不猜自身提交hash、不追随main后续纯治理HEAD。
认领需按协作协议由Codex串行登记再由Owner在本分支ready→in_progress；只读分析并不允许另开修复。
下一接收者=DSH；交付后Reviewer=Codex；诊断/修复范围需另行批准，旧runner debt继续blocked。

## 自动派发认领（Codex串行登记）

DSH通路探测CLI EXIT0，返回“收到”；版本0.1.7-rc.2。用户明确授权自动调用外部Agent。
Codex登记ready→in_progress；Owner=DSH。原release4330b792之后仅恢复文档和本认领治理变更，
Owner将clean fast-forward到本认领提交，再执行真实DSH；实际start_head写入主仓库dispatch.md，
冻结诊断输入source_head与installer SHA不变。不得跟随未冻结生产差量。

## 运行记录（DSH Owner，2026-10-08，status=in_progress 不变）

- 本会话 start_head 期望=`24e0ec6e5c6d64a35daad006565919818616b317`；**git 未实测**（shell NOT_RUN）。
- 执行限制：`pwsh` 每次启动前置失败 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(<worktree>)`；
  `danger-full-access` 升级被拒（无审批通道）。故 AC1/AC2 = NOT_RUN，仅用只读文件工具。
- 静态结论：PyInstaller `-Force` 全量构建成功（COLLECT+5 exe+ML/SFX 闭包断言），EXIT=1 出现在
  其后的 `Copy-MangaWeights`（`Get-FileHash` CommandNotFound）；PS7 无 `-Force` 重试走增量短路只补 weights（EXIT=0）。
- 闭包静态事实：`_internal/PySide6/{Qt6Core,Qt6Gui}.dll`、`pyside6.abi3.dll`、`shiboken6/shiboken6.abi3.dll`、
  MSVC/CRT 均存在；`icuin*`、`d3dcompiler_47.dll`、`opengl32sw.dll` 未见（影响 UNKNOWN）。
  失败点在 `src/bootstrap/acceptance_bridge.py:173` import 语句，早于 `QGuiApplication` 构造。
- 判定：根因类别高置信="QtGui 依赖链 Win32 126 未解析模块"；**具体 DLL/符号 UNKNOWN**；安装态 `_internal`
  完整性 UNKNOWN（无清单证据）。未实施修复，未解除 runner debt，未自审，未置 done。
- 交付（**未提交**，delivery_head 未固定）：`verification/M2-PACKAGED-AC1-DLL-DIAG/{REPORT.md,dll-closure-matrix.json,
  raw/exec-20261008-dsh-notrun.log,probe/**}`、`doc/handoffs/M2-PACKAGED-AC1-DLL-DIAG-20261008-dsh.md`。
  probe 由 Codex 实跑后非作者审查。
