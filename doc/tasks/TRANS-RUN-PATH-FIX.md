---
id: TRANS-RUN-PATH-FIX
title: 自动翻译运行路径收口：修 library_start_run 的 INVALID_REQUEST + RunBindingDefaults 扩展
kind: implementation
governance_version: 3
status: closed_with_limitations
disposition: "L1-T-B（2026-11-14 DSH 释放）；依据 MAINT-1-AUTO-TRANSLATE-FEASIBILITY §7 T-B 与 REAL-TRANSLATE-PROVIDER-1 §7.2 遗留"
approval: DSH 2026-11-14 释放（零冻结契约改动；依赖 T-A 已 closed）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - TRANS-BINDING-BRIDGE
base_commit: f8a6185f9
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 652d7e7d0
delivery_head: 652d7e7d0
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/TRANS-RUN-PATH-FIX
allowed_paths:
  - doc/tasks/TRANS-RUN-PATH-FIX.md
  - doc/reviews/TRANS-RUN-PATH-FIX-*.md
  - verification/TRANS-RUN-PATH-FIX/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/**
  - apps/desktop-avalonia/src/NewManga.Host/**
  - apps/desktop-avalonia/tests/**
  - src/bootstrap/**
  - src/application/**
  - src/infrastructure/**
  - tests/**
out_of_scope:
  - 冻结契约字节（C-01b…C-17、M2-C1、ADJ-001）；不得新增 wire 命令或 IHostController 成员
  - schema/DDL 变更、依赖变更、远端写操作
  - doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/TASK_LEDGER.md（DSH 维护）
---

# TRANS-RUN-PATH-FIX：自动翻译运行路径收口

## 来源

- 评估 §7 T-B：`TRANS-RUN-PATH-FIX`。
- 遗留缺陷：`verification/REAL-TRANSLATE-PROVIDER-1/REPORT.md:75,80` 记录「隔离根 + REPACK-2 models sidecar 下，Host `library_start_run` 返回 `INVALID_REQUEST`；Core 直连同 payload 可接受」——**未定位**。
- `RunBindingDefaults.DefaultJson = {"ocr":"manga-ocr"}`（`apps/desktop-avalonia/src/NewManga.CoreClient/Commands/RunBindingDefaults.cs:23`）默认不注入 translate。

## Acceptance Criteria

- [x] **AC1 先诊断后修**：定位 `library_start_run` 的 `INVALID_REQUEST` 根因（Host dispatcher 的 payload 形状 vs Core 期望），给出**证据**（文件:行 + 复现步骤 + 实际/期望形状差异）。**不得**在未定位前盲改。 <<MET>>
- [x] **AC2 修复**：按 AC1 的诊断修复；若根因在 Core 侧，改动须最小且不改冻结契约；若确认是 Host 侧传参错误，修 Host。 <<MET>>
- [x] **AC3 RunBindingDefaults 扩展**：默认绑定改为「ocr +（存在 translate 配置时）translate」，且**用户显式 overrides 永远优先**（保持 `RunBindingDefaults.cs:9-15` 既有语义）。 <<MET>>
- [x] **AC4 不新增契约面**：无新 wire 命令、无新 `IHostController` 成员；`generate_api_inventory --check` 维持 `1/80/6=87`；`verify_pins` 18/18。 <<MET>>
- [x] **AC5 判别测试**：至少一条覆盖「默认绑定含 translate」与「显式 override 优先」；若 AC1 的根因可测，补一条回归测试。 <<MET>>
- [x] **AC6 门禁**：`check.ps1`（默认 + 本卡 TaskPath）、`verify_pins`、`generate_api_inventory --check`、受影响 `dotnet test` 与 pytest 全绿。 <<MET>>
- [x] **AC7 若根因不可修**：允许 `closed_with_limitations`，但**必须**给出「不可修的客观原因 + 已排除的假设 + 下一步需要的条件」，不得用「未定位」收尾。 <<NOT_APPLICABLE: 根因已定位并修复可诊断性，未触发该分支>>

## 测试要求

C#：`dotnet test`（CoreClient / Host / App 受影响项目）；Python：定向 + 全量 `pytest` 不得新增 failed。

## 风险

- AC1 的根因可能不在 Host 而在 Core 的 payload 校验；**先取证**，不要按假设改。
- `RunBindingDefaults` 有环境变量覆盖口 `NEWMANGA_RUN_PROVIDER_BINDINGS`，改动须保留它。
- 若发现必须新增 wire 命令才能修，**停下回卡报 DSH**。

## 证据计划

`verification/TRANS-RUN-PATH-FIX/README.md` + `logs/`（诊断证据、测试与门禁原始输出）。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-1 | AC1-AC6 | verification/TRANS-RUN-PATH-FIX/README.md | 652d7e7d0 | a89fc63637aa35f217acf69127245f79f40fafc2bc9b0b88c78a458798c733ff | canonical |
| EV-2 | AC1-AC6 | verification/TRANS-RUN-PATH-FIX/logs/gates.log | c9cb3eeab | 7874f48e6d5b0be63dc8542ef6abb38f8838c2f08ca93236e77fb2c9355585ba | canonical |
| EV-3 | AC1-AC6 | verification/TRANS-RUN-PATH-FIX/logs/pytest-full.log | c9cb3eeab | be371538b845f7363bed36409ccac14badfd3338e50103cbf72e605972cfc0e7 | canonical |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | `G:\CODEX\New Manga`（main） | NOT_APPLICABLE | - | - | 复用主工作树 |
| evidence（仓库） | `verification/TRANS-RUN-PATH-FIX/**` | NOT_APPLICABLE | 仓库内 | `verification/TRANS-RUN-PATH-FIX/EV`（见 Canonical Evidence） | 诊断/门禁原始输出已保留 |

## Closeout Record

- **收口（2026-11-14，DSH）**：`closed_with_limitations`。AC1–AC6 `MET`；AC7 `NOT_APPLICABLE`（根因已定位，未触发该分支）。独立复核 `approved`（`TRANS-RUN-PATH-FIX-r1.md`）。
- **复核修正了三处记录层引用（已采纳）**：折叠点实为 `core_service.py:6821-6822`（非 6810-6811）、文案 `:6837`；生产抛点实为 `sqlite/pipeline.py:847-848`（`store.py:420-421` 是内存孪生，同 code 同 detail）；AC2 代码落在 `c9cb3eeab`（非 `652d7e7d0`）。
- **limitation（已登记）**：
  1. **用户仍看到通用文案**：章节无 active page 时终端仍显示 `INVALID_REQUEST / Run request is invalid`；精确原因只在 stderr。可读文案需 Host 前置探测（`list_chapter_pages`），已转入 **T-C**。
  2. **Host 默认 translate 值来自环境变量**（`NEWMANGA_RUN_TRANSLATE_PROVIDER`）而非当前翻译 binding；T-C 须改为从 binding 取值、环境变量仅兜底。
  3. **诊断探针脚本与原始输出未入库**（复核用等价脚本独立重放成功）。
- **交付**：`c9cb3eeab`（诊断）+ `652d7e7d0`（stderr 可诊断性 + RunBindingDefaults）。pytest **3564/0/10**；CoreClient 182/0/26、App 915/0/11、Host 321/0/74（无 env）；四件套绿。

## 交付记录与 DSH 裁决（2026-11-14）

### 诊断（`c9cb3eeab`）—— 推翻了既有记录

- **根因**：`INVALID_REQUEST` **不是** Host 传参错位。Core 把 `EMPTY_TARGET_SELECTION`（目标集为空）**折叠**成冻结的 `INVALID_REQUEST` 并配通用文案（`core_service.py:6810-6811`，文案 `:6826`），真实异常来自 `src/application/tasks/store.py:413-421`（`PipelineError: 'EMPTY_TARGET_SELECTION: scope expands to no active pages'`），精确原因从不离开进程。
- **「同 payload 可接受」的真相**：直连探针是 `translate_untranslated` + **book scope**，Host/App 是 `translate_all` + **chapter scope**（`WorkbenchViewModel.cs:14,172-176`）⇒ 章节无 active page 时 book scope 能展开到别章页面，chapter scope 必拒。
- **已排除**：打包/仓库 Core 版本漂移（envelope 逐字节相同）、Host payload 形状错位、协议 minor 不匹配、`provider_profiles` 在 minor 3 被拒。

### 修复（`652d7e7d0`）

- **AC2**：折叠前把精确原因写 stderr（`[core.run] <Cmd> refused: <CODE>: <detail>`），Host 本就捕获 Core stderr；**wire 字节零变更**。
- **AC3**：默认仍 `{"ocr":"manga-ocr"}`；有 translate 配置（`NEWMANGA_RUN_TRANSLATE_PROVIDER` 或显式入参）时追加 `translate`；**显式 `overrides.provider_bindings` 永远优先**；`NEWMANGA_RUN_PROVIDER_BINDINGS` 关闭口保留；无配置时默认 JSON 逐字节不变。
- **实测**：pytest **3564/0/10**（+2）；CoreClient 182/0/26、Host 351/0/44、App 915/0/11；四件套绿；`--check` 1/80/6=87。

### DSH 裁决

- **R-1 接受 AC2 只修「可诊断性」，不判 PARTIAL**。根因是**数据前置条件**（本章无可处理页面）而非传参 bug；要改用户可见错误码必须动冻结错误面（UNFREEZE），要改行为必须让 Host 先探测页面（产品决策）。实施者选了唯一零契约、零行为变更的动作，并把能力边界写进 README §3 —— 这是正确的最小动作。**但「用户仍看到通用文案」必须作为产品债登记**（见 R-3）。
- **R-2 接受 AC3 的当前解释（环境变量兜底），但加约束**。T-A 的镜像已把全局 `provider_bindings.translate` 写进 Core，默认注入在多数场景冗余，此处不做 P15 反查是合理的。**约束**：T-C 必须让 Host 默认值来自**当前翻译 binding**，环境变量只作兜底 —— 否则用户「在 UI 选了 profile A、Host 注入 B」会静默错配。
- **R-3 两条产品债转入 T-C**：① 章节无 active page 时用户只看到 `INVALID_REQUEST / Run request is invalid` —— T-C 须加 Host 前置探测（`list_chapter_pages`）并给可读文案；② Host 默认 translate 值须来自当前 binding，环境变量兜底。
- **R-4 一次自曝的坑已记录**：把 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 指向 0.1.1 发布 sidecar 跑**全部** .NET 测试会激活期望 models sidecar 的 fixture（CoreClient 1 红、App 6 红），撤掉后全绿；本卡两条 dispatcher 用例在该 sidecar 上单独跑 4/0/0。复核者须避免这个假红。