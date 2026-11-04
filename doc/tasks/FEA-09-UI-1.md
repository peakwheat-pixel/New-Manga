---
id: FEA-09-UI-1
title: 引用源导入最小 UI/适配接线（V2 ImportDock：plan 预览、密码、取消、进度）
kind: implementation
governance_version: 3
status: in_review
approval: **RELEASE APPROVED（2026-11-04，DSH）**：scope 冻结 + Appointment——owner=ZCode（新 headless 会话）、reviewer=Codex（全新上下文）、base_commit `19a71b396`（释放 commit）；范围/AC/门禁见 `doc/reviews/FEA-09-UI-1-appointment.md`
suggested_owner: zcode
owner: zcode→codex（ZCode 额度 429 后按用户授权由全新 Codex 会话完成返修；DSH 集成）
reviewer: codex（r1 P1=5/P2=2 → 返修；r2 P1=1/P2=4 → 处置；r3 P2=3 → 处置；r4 待全新上下文 Codex 复审，reviewed_head 见 r4 报告）
depends_on:
  - FEA-09-PREREQ-1
  - FEA-09
base_commit: 19a71b396eb177627f872d829c59dd7e440ebbbe
branch: main
worktree: G:\CODEX\New Manga
integration_commit: null
delivery_head: b14e04dafbb14b94a59cfcb935f01ecd4e5a636b（r2/r3 返修集成提交；提交后仅文档指针更新）
canonical_evidence_status: complete（返回修证据与 Canonical Evidence 表已登记；commit pin 随 DSH 提交回填）
resource_closeout_status: pending
evidence_dir: verification/FEA-09-UI-1
allowed_paths:
  - doc/tasks/FEA-09-UI-1.md
  - doc/handoffs/FEA-09-UI-1-*.md
  - doc/reviews/FEA-09-UI-1-*.md
  - verification/FEA-09-UI-1/**
  - apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/ImportDockView.axaml
  - apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/ImportDockView.axaml.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ImportDockViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/ImportExportContracts.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/SourceImportModels.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/**
out_of_scope:
  - Core/Host 契约、wire、持久化与授权实现（FEA-09 / FEA-09-PREREQ-1 写域）
  - 其它页面/组件/设计基线与 Fluent 视觉重设计（FEA-14 系列/设计基线 v1.1）
  - 真实用户数据/真实外部卷/真实取消/回收站
  - 以 fake controller 或进程内断言冒充真实 IPC/UI 证据
  - push
---

# FEA-09-UI-1：引用源导入最小 UI/适配接线

> 来源：`doc/reviews/FEA-09-scope-r1.md` §2.3/R1-005（提案 `:1040` 要求「每项用隔离数据断言 Core→Host→UI 结果」；现有 V2 `ImportDock` 只有旧 `ImportPages` 路径、无密码/plan 确认/运行中取消入口；`ImportExportUiTests` 使用 fake controller 不能作为真实 IPC 证据）。本 Task 是 FEA-09 的**协同交付**切片，不替 FEA-09 决定 Core/Host 语义。
> **历史说明**：本卡首版为 scope 草案（已由 DSH 2026-11-04 冻结并 Appointment，见 `doc/reviews/FEA-09-UI-1-appointment.md`）；当前状态以 frontmatter 为准。

## 来源与目标

- FEA-09 交付 Core/Host 的引用源读取、导入 plan/receipt、授权与取消语义；本 Task 只做**最小 UI/适配接线**：让真实 V2 用户路径可达并产出可观察证据。
- 目标：在现有 `ImportDock`（V2 Library）上接线——导入预览（plan）确认、加密项目密码输入（短期安全引用）、运行中取消、逐项进度与成功/失败/跳过汇总；消费 FEA-09 冻结的命令面，不新增业务真值。
- 约束：Avalonia UI 不直接访问数据库、任意 OS 路径或模型；只经 Host/IPC adapter；不改变 Current V2 既有行为（旧 `ImportPages` 路径保留）。

## 范围（草案）

1. `ImportDockViewModel`/`ImportDockView` 接线 FEA-09 的 plan/receipt/取消/进度命令（真实 Host 命令，不经 fake controller）。
2. 密码输入：仅经短期安全引用传递；UI 不持久化、不写日志、不出现在错误文案；取消/失败清理引用。
3. 取消与重试：运行中取消入口；已提交/未提交结果按 FEA-09 冻结的提交单元展示；重试不重复提交。
4. 汇总：按当前项目显示进度与成功/失败/跳过/待处理逐项原因；不支持/损坏/加密（含 AES ZIP typed unsupported）逐项可读。
5. 可访问性/键盘：新交互沿用既有 V2 控件与 Fluent 语义，不新增设计令牌/组件变体；超出即停等 DSH 裁决（设计基线 v1.1 或 OUT）。

## Acceptance Criteria（scope 冻结；Owner 交付自评——待 Codex 独立 Review + DSH 集成验证）

- [x] **AC-1**：plan 预览经真实 Host IPC 生成并可确认/取消；确认前源变化时 UI 呈现拒绝或更新预览，不静默提交。 <<MET>>
- [x] **AC-2**：密码重试路径经真实 IPC 走通（支持的加密子格式），密码不出现在日志/快照/错误文案/证据；AES ZIP 显示 typed unsupported。 <<MET>>
- [x] **AC-3**：运行中取消可触发；已提交项目保留、未提交不出现；重试不重复提交；汇总计数与 FEA-09 receipt 一致。 <<MET>>
- [x] **AC-4**：以隔离 fixture + 真实 production adapter 断言 UI 可观察结果（非 fake controller、非进程内替代）；证据含 UI 状态/原因/计数。 <<MET>>
- [x] **AC-5**：不改变旧 managed 导入路径行为；旧 FEA-06 四 PNG 不变；无真实用户数据；全量测试不减少；未 push。 <<MET>>

## 允许修改范围

见 frontmatter `allowed_paths`。`apps/desktop-avalonia/src/NewManga.App/Services/` 仅在 FEA-09 冻结的命令适配所需文件内改动（实施时由 DSH 指定精确文件，不与 FEA-09 重叠写）。共享组合根（`App.axaml`/`App.axaml.cs`/`NewManga.App.csproj`/`NewManga.sln`）仍仅 DSH 单点提交。

## 禁止范围

Core/Host 契约与实现、Schema、授权、wire、持久化；其它页面；设计基线；真实用户数据/外部卷/回收站；以 fake/进程内证据替代真实 IPC/UI；push。

## 测试要求（下表为首版历史记录，当前返修见末节）

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC-1…AC-4 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo`；`dotnet test … -c Release --no-build`；`NEWMANGA_FEA09_IPC=1 NEWMANGA_BUILD_PYTHON=<python> dotnet test tests/NewManga.Host.Tests -c Release --no-build --filter "FullyQualifiedName~Fea09UiImportIpcTests"`；headless：`--filter "FullyQualifiedName~ReferencedImportUiTests"` | 主工作树；隔离 fixture（workspace `FEA-09-UI-1/ipc-*` + 冻结 FEA-09 fixture）；不碰真实 AppData | build **0/0**；全量 **1313/0/63**；真实 IPC **5/5**；VM **13/13** | `verification/FEA-09-UI-1/logs/gates.json`、`ipc/ui-import-ipc.json`、`ipc/ui-import-ipc.wire.ndjson`、`AC-MATRIX.md` |
| AC-5 | 同全量基准（Appointment 1300/0）；旧四 PNG hash 对照；`git diff --name-only` 对照 allowed_paths；`verify_pins` 17/17；`check.ps1` | 同上 | 1313/0（≥基准）；PNG **4/4 UNCHANGED**；diff 全部 allowed_paths 内；pins **17/17**；check **FAIL 1 error**（READY DAG 滞后，PLAN 同步属 DSH 集成步骤；3 既有 warning） | 同上 |

## 依赖、风险与阻塞

- `depends_on`：FEA-09-PREREQ-1（契约）、FEA-09（Core/Host 命令）。二者为已登记 Task；本卡在 FEA-09 交付前只可做只读准备，不得实施。
- 风险：①FEA-09 命令面未冻结前接线会返工；②UI 证据易被 fake/进程内测试冒充——必须真实 production adapter；③密码输入与日志安全需独立负测；④与 FEA-09 写域重叠（App/Services）必须由 DSH 指定单一写者。
- 阻塞解除：FEA-09 scope-r2 approved + PREREQ-1 done 后本卡提交 scope review。

## Canonical Evidence

（工作树 SHA-256；commit 列在紧随其后的文档提交回填）

| evidence_id | 证据说明 | 仓库路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-001 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/AC-MATRIX.md` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `86e71c73a402dba560d64925560a4d82a3d2ca6d90baf67f72b7c279a3eb9421` | CANONICAL |
| EV-002 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/ipc/production-ui-import-ipc.json` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `a1da1ecf54e809641b3fbb42a8aaaf3a455114a4b502aa44b9c9f8f484c7d16f` | CANONICAL |
| EV-003 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/ipc/production-ui-import-ipc.wire.ndjson` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `79eabd23b3acea0a2988c39c8f8d7f360558bfced9f99e4e9f8bdf2307249e6c` | CANONICAL |
| EV-004 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/ipc/ui-import-ipc.json` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `c616c25b22521d6b04b41c978b28f81ac3d3313f8279458307716a47cd6e290e` | CANONICAL |
| EV-005 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/ipc/ui-import-ipc.wire.ndjson` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `9b125edd05f96fe449d91691bd0980870f0db6f8e3e3d30419b933f49917e421` | CANONICAL |
| EV-006 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/dsh-integration.json` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `cec8e91c26bc59b5bf1dc6db12f0250f47946c00cad69d6d1b746b44c853999e` | CANONICAL |
| EV-007 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/dsh-scope-diff.txt` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `fe51190dec3bebfec7691b29b931ccd7a807de43ebecf69b2e774b181cd9c713` | CANONICAL |
| EV-008 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/dsh/build.log` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `c64d07b3ef5930ee7cff111c3d6bcfa47bb1f6f25ea7529ff33de0e0b52ed21c` | CANONICAL |
| EV-009 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/dsh/full-test.log` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `d538d93f02b132ce747989db0b67b8a8775c8ea8791bf3a02cfbcdbfeebf9a05` | CANONICAL |
| EV-010 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/dsh/ipc-test.log` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `9f585e0df486e2d09677e4e627af6a351db03c43e5396d0cab087df10aa4a07b` | CANONICAL |
| EV-011 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/dsh/trx/dsh-full-NewManga.App.Tests.trx` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `ea938fb62663fea4659397cdd5e5784431943a2449e3c4811db66a624ac5ff15` | CANONICAL |
| EV-012 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/dsh/trx/dsh-full-NewManga.Appearance.Tests.trx` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `dfaad33fbb50dc1860c3ae4ff50fb4afffc4ffcf767286461fbd9da3ec3dd3c5` | CANONICAL |
| EV-013 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/dsh/trx/dsh-full-NewManga.ApplicationCore.Tests.trx` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `8beaa6ec2ddd63b95cb0b1bb418c9b7457a784512fbd0cc847ef2689b96bb4be` | CANONICAL |
| EV-014 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/dsh/trx/dsh-full-NewManga.CoreClient.Tests.trx` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `3eb19966525ac91b09adcce6ba3c3f8b16df4e73b5d12eaa29386a2227d1f8d1` | CANONICAL |
| EV-015 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/dsh/trx/dsh-full-NewManga.DesignSystem.Tests.trx` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `cacfef0c656dfad3431604e25931356a69937cd936213ecb03f2430d57743745` | CANONICAL |
| EV-016 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/dsh/trx/dsh-full-NewManga.Host.Tests.trx` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `56435422541e040c96232661576bbb15bd483e30efcfc5cf232acebaede1e800` | CANONICAL |
| EV-017 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/dsh/trx/dsh-full-NewManga.Presentation.Avalonia.Tests.trx` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `09d9c0e2017b52b434415fb07777464f20c3f8d442dd73f02bdf3393a28a5b3f` | CANONICAL |
| EV-018 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/dsh/trx/dsh-full-NewManga.ThemeEngine.Tests.trx` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `11501e7db0ea2077d905efd87d50aa851dbedae45b8c6d0d37157de53a1b33e5` | CANONICAL |
| EV-019 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/dsh/trx/dsh-ipc.trx` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `cb9608803e14401ca013056c540731757f5e52db08498b4f86a280e50ca7592b` | CANONICAL |
| EV-020 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/gates.json` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `020ed3ee8dfea67855f4aae742d1eb7145e330bc4e1b60ff398ddbf9a6ce9569` | CANONICAL |
| EV-021 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/repair-api.log` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `f5a23d415a32c51b6691a96b2a7fb7c4534646e9502ec21b5647f3e20348f852` | CANONICAL |
| EV-022 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/repair-build-initial.log` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `8a281d7de093d1f8e020e9f67a68d33148521bdbae2054847f29312051edee5b` | CANONICAL |
| EV-023 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/repair-build.log` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `395f602828a4b759fdcccda5e9dd476f5ad82afb63d68b4134a4dcef6d57bfc3` | CANONICAL |
| EV-024 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/repair-fea09-restore.json` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `d81bcf9da8e328e31d00c51659464558aed192c0925bad25faaaddd885c59531` | CANONICAL |
| EV-025 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/repair-full-inventory.json` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `02f0317c519942676295efb23ce18399f83e9be704fc629c38382bfc9bcc0b5d` | CANONICAL |
| EV-026 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/repair-full.log` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `d56504fe24bf03fd9f747195e6183c64a1e053501cf45340f47a74979a96e348` | CANONICAL |
| EV-027 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/repair-governance.log` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `d6f42ff9c343d164471566c3314ff84bcbb43a6462124ef8cae67a6098c1bdf3` | CANONICAL |
| EV-028 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/repair-ipc.log` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `40833e4c504a06686c2ca9b5cd56c1ff8584661ba0410ce4d920a7859c58b320` | CANONICAL |
| EV-029 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/repair-password-audit.json` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `eba126b2a2465f2af5bcfff954b0c6e9804e5ad82f432277eeb062a4834842a4` | CANONICAL |
| EV-030 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/repair-pins.log` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `fa4b978d09a934466f0816073ef2fbdf0bc6fd150fe3b9ec045d02466ba2a34c` | CANONICAL |
| EV-031 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/repair-scope-diff.json` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `c5eefec626b0a9ce2b29faaceae0f7b8ab3e2028a5682bc81c3d468b25b130ae` | CANONICAL |
| EV-032 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/repair-vm.log` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `db58720205555268d61279e276d5906f05ea446a0bb2f568a7b1183a637423cb` | CANONICAL |
| EV-033 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/test-results/repair-full_net9.0_20261104093436.trx` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `206b2e02c1e21b8493b613680a93944e29c72793b9da309d401230451185bbe6` | CANONICAL |
| EV-034 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/test-results/repair-full_net9.0_20261104093437.trx` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `7175680b2e594f7ba750207147fd7b9932ae7cdcee8ff8db5d48c351661b1c54` | CANONICAL |
| EV-035 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/test-results/repair-full_net9.0_20261104093438.trx` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `f7b1c4955e3b7804fbccdbea74c7f293ae6806c967fbefd39ed3cf12357e672f` | CANONICAL |
| EV-036 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/test-results/repair-full_net9.0_20261104093439.trx` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `85bd052baf6a24cae328ad819622335a3db7bfab9240774eec6f01fdff53ffb9` | CANONICAL |
| EV-037 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/test-results/repair-full_net9.0_20261104093440.trx` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `e9f475be87371a2ff67149aecd65f3ae9ae8360a0071b2aadfe34e85f2d6585c` | CANONICAL |
| EV-038 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/test-results/repair-full_net9.0_20261104093441.trx` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `1dfe0604cc3a730a52705481d50fe7f117c29ea5f4dc1249a082ff87ad4429cb` | CANONICAL |
| EV-039 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/test-results/repair-full_net9.0_20261104093513.trx` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `da46d4b6e033cf0c93f4226ad54cc9a82dfdfbe1c3d3048b6520e1a96129c178` | CANONICAL |
| EV-040 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/logs/test-results/repair-full_net9.0_20261104093703.trx` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `cedf9c52189b49fcf70709d794762a8d6ebb88791467abc4ca4801b77674a4d8` | CANONICAL |
| EV-041 | FEA-09-UI-1 证据文件 | `verification/FEA-09-UI-1/repair-checkpoint.md` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `a7932523da6ec52813308f844b8ec4c78adbc2b454360f2f77fca6b6e3d43ec8` | CANONICAL |
| EV-042 | FEA-09-UI-1 证据文件 | `doc/handoffs/FEA-09-UI-1-rework-dsh-7f4f4d3cd.md` | b14e04dafbb14b94a59cfcb935f01ecd4e5a636b | `9d1fa5ea1dd340335f0f7bef485fbd6335453a645cb0ab5e5bad920d28e9fdad` | CANONICAL |


## Closeout Record

- Owner 首版：ZCode（Appointment 2026-11-04）；Review r1：Codex changes_requested（P1=5/P2=2）；返修：Codex 全新上下文（用户授权故障转移）；集成/门禁：DSH。
- 当前：r1–r3 findings 全部处置，DSH 门禁全绿，Task `in_review`；等全新上下文 Codex Review r4。
- 未提交/未 push：工作树；由 DSH 提交后回填 commit。
- 已知事项：见 AC-MATRIX「限制」。

## 变更记录

| 日期 | 变更 | 依据 |
|---|---|---|
| 2026-11-03 | 建立 scope 草案（proposed）：最小 UI/适配接线，作为 FEA-09 的 UI 证据协同切片 | `doc/reviews/FEA-09-scope-r1.md` R1-005；提案 `:1040`；现有 ImportDock 现状 |
| 2026-11-04 | ZCode 认领（in_progress）；实现交付（工作树）：新增 `Services/SourceImportModels.cs`（UI 模型+payload+`SourceImportCoordinator` 生产编排：register→issue→plan / 密码 DPAPI secret_ref→重签 Secret-G→重 plan→start / receipt 轮询+终态清理 / cancel）；`IHostController`+`HostController`+`NullHostController` 增 4 方法（Plan/Start/GetReceipt/Cancel，typed 不抛）；`ImportDockViewModel`+`ImportDockView.axaml` 引用导入面（plan 预览/密码框/确认/取消/重试/进度，旧路径零改动）；`FakeHostController` 补 scripted 面；Host.Tests 引用 App；新测试 `ReferencedImportUiTests`（13）+`Fea09UiImportIpcTests`（5，真实 stdio）；证据 4 件。**HostCommandDispatcher/Registry 零改动**（source 命令 pass-through 已由 FEA-09 交付，核实无缺口）。Task → in_review | 本卡 Appointment；`verification/FEA-09-UI-1/**`；Handoff |
| 2026-11-04 | **DSH 复核返修 r1**：IHostController 改动撤回 → 独立 `ISourceImportController`；`generate_api_inventory.py --check` PASS（C-07 冻结面未变）；DSH 复跑 build 0/0、全量 1313/0/63、真实 IPC 5/5、pins 17/17；证据补 DSH 集成日志/范围 diff | DSH 集成；`doc/reviews/FEA-09-UI-1-appointment.md` |



| 日期 | 变更 | 依据 |
|---|---|---|
| 2026-11-03 | 建立 scope 草案（proposed）：最小 UI/适配接线，作为 FEA-09 的 UI 证据协同切片 | `doc/reviews/FEA-09-scope-r1.md` R1-005；提案 `:1040`；现有 ImportDock 现状 |
## Release / Appointment（2026-11-04，DSH）

- 用户指令释放本 Task；范围冻结与 Appointment 见 `doc/reviews/FEA-09-UI-1-appointment.md`。
- Owner：**ZCode**（新 headless 会话；认领后 Task → `in_progress`）；Reviewer：**Codex**（全新上下文，实现完成后独立 Review）；DSH Integrator。
- base_commit：`19a71b396eb177627f872d829c59dd7e440ebbbe`。
- 精确 allowed_paths 已冻结（见 frontmatter）：仅 App 层 ImportDock/Services、CoreClient command adapter 既有 source 命令 pass-through、App/Host 测试、本 Task 文档与 evidence。
- AC-1…AC-5 冻结；验证门禁：`dotnet build`、`dotnet test`（基准 1300/0）、真实 IPC（`NEWMANGA_FEA09_IPC=1`）、`check.ps1`、`verify_pins.ps1`（17/17）、范围 diff；证据 `verification/FEA-09-UI-1/`。
- 禁止：改 C-05/C-15/C-16 冻结字节、改 FEA-08/FEA-09 closeout 文件、fake/进程内冒充真实 IPC、push。发现需扩围 → 停并写「待裁决」交 DSH。
- 完成路径：实现 + 测试 + Evidence + Handoff → `in_review` → Codex 独立 Review → DSH 集成验证 → `done`。
## 返修 r1（2026-11-04，DSH 复核 / ZCode 执行）

- **触发**：Owner 首版把 4 个方法加进 `IHostController` → `tools/generate_api_inventory.py --check` FAIL（C-07 FROZEN 清单 54 方法基线被改），需要 C-07 UNFREEZE，超出本 Task 授权。
- **返修**：改为**独立接口** `ISourceImportController`（`Services/SourceImportModels.cs`；4 个 typed 方法），`HostController`/`NullHostController`/测试 fake 同时实现；`ImportDockViewModel` 通过 `controller as ISourceImportController` 能力探测（缺失=typed unavailable，旧 managed 路径不变）；`IHostController.cs` 恢复 HEAD 原字节。
- **结果**：`python tools/generate_api_inventory.py --check` **PASS**（C-07 冻结面未变）；build 0/0；全量 .NET/真实 IPC/门禁结果见 `verification/FEA-09-UI-1/logs/dsh-integration.log`。
- **C-07 待办撤销**：不再需要 UNFREEZE 载体；本 Task 未改任何冻结契约字节。
- 文档同步：Handoff / AC-MATRIX 中“IHostController +4 / C-07 UNFREEZE”描述作废，以本节为准。
## Implementation Review r1 处置（DSH，2026-11-04）

| ID | 级别 | DSH 处置 | 状态 |
|---|---|---|---|
| R1 | P1 | 接受：token 创建即登记清理上下文；所有未 accepted 出口统一 Delete+Revoke；补失败负测 | 返修中 |
| R2 | P1 | 接受：receipt 暂时失败保持运行中状态，可恢复轮询/取消；终态才释放 | 返修中 |
| R3 | P1 | 接受 + **DSH 接缝裁决**：folder 交 Host `IssueAsync` 枚举（App 不递归/排序/授权）；最小改动不可行则入口 typed unavailable 并如实登记 | 返修中 |
| R4 | P1 | 接受：补真实 `HostController`+`ImportDockViewModel`→IPC 闭环（普通/AES/单加密源重试/取消守恒/源变化拒绝） | 返修中 |
| R5 | P1 | 接受：>1 加密源 App 层 typed 拒绝，逐源独立确认/token；不扩 Core wire | 返修中 |
| R6 | P2 | 接受：绑定并显示每项 CountsText；补测试 | 返修中 |
| R7 | P2 | 接受：分别显示 skipped_pages/skipped_sources；补整源跳过测试 | 返修中 |

## 返修 r2 完成（Codex 实现 + DSH 集成，2026-11-04）

- **状态：返修完成，DSH 门禁全绿，Task → `in_review`，等全新上下文 Codex 复审。**
- 实现者：Codex 全新上下文（ZCode 429 额度不可用，按用户授权故障转移；返修者不得自审）。
- 修复：R1 token/Secret-G 异常清理；R2 receipt 暂时失败保持可取消运行态；R3 folder 改交 Host `IssueAsync`/EnumerateFolder（App 不递归/排序/授权）；R4 新增真实 `HostController`+`ImportDockViewModel`+Python stdio 闭环；R5 >1 加密源 typed 拒绝；R6 绑定 CountsText；R7 skipped_pages/skipped_sources 分别显示。
- DSH 集成复跑：build 0/0；全量 .NET **1317 passed / 0 failed / 74 skipped**；真实 IPC **16/16**（11 production + 5 下层）；`generate_api_inventory.py --check` PASS（C-07 未变，无 UNFREEZE）；`check.ps1` PASS（3 warnings）；pins **17/17**；范围全部 allowed_paths；FEA-09 canonical 证据复跑污染已恢复。
- 证据：`verification/FEA-09-UI-1/AC-MATRIX.md`、`ipc/production-ui-import-ipc.*`、`logs/gates.json`、`logs/dsh-integration.json`；Handoff `doc/handoffs/FEA-09-UI-1-rework-dsh-7f4f4d3cd.md`。
- 限制：多加密源逐源确认；folder 交 Host；FEA-09 证据可被常规测试复跑重写（既有债务候选）；UI 证据为控件级。


## 返修 r1 与 DSH 集成（2026-11-04）

- R1–R7 已按 `doc/reviews/FEA-09-UI-1-impl-r1-adjudication.md` 全部修复；实现：Codex 全新上下文（ZCode 429 不可用，用户授权故障转移）。
- DSH 复跑门禁：build 0/0；全量 .NET **1317/0/74**；真实 IPC **16/16**（11 production HostController+VM+HostRuntime+Python stdio + 5 下层）；C-07 inventory `--check` **PASS**；check.ps1 PASS（3 warnings）；pins **17/17**；范围合规；FEA-09 canonical 证据污染已恢复。
- 证据：`verification/FEA-09-UI-1/AC-MATRIX.md`、`ipc/production-ui-import-ipc.*`、`logs/gates.json`、`logs/dsh-integration.json`；Handoff：`doc/handoffs/FEA-09-UI-1-rework-dsh-7f4f4d3cd.md`。
- 限制：多加密源逐源确认；folder 交 Host EnumerateFolder；FEA-09 证据复跑重写为既有债务候选。
- 下一步：全新上下文 Codex 复审（r2）；approved 后 DSH 集成 → done。

## Review r2 处置与复跑（DSH，2026-11-04）

- r2 结论：changes_requested P0=0/P1=1/P2=4（N1 门禁原始记录、N2 Grid 行定义、N3 Registry 审计覆盖、N4 源变化负测关联、N5 Task 字段过期）。
- 处置：N1 补 DSH 成功原始日志+TRX（`logs/dsh/**`）；N2 receipt Grid `RowDefinitions="Auto,Auto"`；N3 改为扫描 Registry 原始 opaque 字节并收窄声明；N4 仅对本次 confirm 新增帧断言 `FILE_IDENTITY_CHANGED`；N5 更新 delivery_head/proposed 历史说明。
- 复跑：build 0/0；全量 .NET **1317/0/74**；真实 IPC **16/16**；C-07 `--check` PASS；check.ps1 PASS；pins 17/17。
- 下一步：全新上下文 Codex Review r3；approved 后 DSH 集成 closeout。

## Review r3 处置（DSH，2026-11-04）

- r3：changes_requested P0=0/P1=0/P2=3。
- N1：按 8 个测试项目分别运行并保存唯一 TRX（`logs/dsh/trx/dsh-full-<project>.trx`），日志带命令头/CWD/EXIT；IPC 日志/TRX 同。
- N4：E 改为逐文件 offset 只断言本次 confirm 追加帧 `FILE_IDENTITY_CHANGED` + receipt 行同码 + 0 页，去掉 Snapshot.LastError 兜底。
- N5：固定 delivery_head/EV commit/Closeout 当前状态（紧随本次代码提交的文档提交）。
- 复跑：build EXIT=0；8 项目合计 **1317/0/74**；IPC **16/16** EXIT=0；C-07/check/pins 全绿。
