---
id: FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1
title: C-15 v1.5 UNFREEZE（Registry 文件损坏与「根身份当前不可用」分离）
kind: contract
governance_version: 3
status: done
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；`FEA-11-L-S1-REGISTRY-RESILIENCE-1` 权威 scope review `doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-scope-r1.md`（fresh subagent `976c9d16-…`，**READY-WITH-UNFREEZE**：仅 C-15 §5 单条，1 pin；C-16/C-17 零改）；Codex 裁决输入因额度不可用 → 按用户授权故障转移 ZCode（结果见卡「裁决依据」）；DSH 裁决 D-1…D-9（见下）
suggested_owner: dsh
owner: dsh
reviewer: 独立上下文 fresh subagent（byte-level；未参与起草）：r1 `94eab07b-7235-422e-b1f0-569c603e4cf7`（changes_requested P0=0/P1=2/P2=5/P3=9）/ r2 `ccdae3ad-6ff7-4236-b59c-0b46b7ef9043`（**approved** P0=0/P1=0/P2=0/P3=15 非阻断）；报告 `…-PREREQ-1-r1/r2.md`；载体 §6
depends_on:
  - FEA-11-RUN-GRANT-2B-PREREQ-1
base_commit: d782c52a4
branch: null
worktree: null
integration_commit: ae8c2de07
delivery_head: ae8c2de07
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1.md
  - doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1-*.md
  - doc/handoffs/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1-*.md
  - doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C15.md
  - doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C15.md
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
  - verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1/**
out_of_scope:
  - 生产代码/测试（src/**、apps/**、tests/**）——A 实现卡另起
  - C-16/C-17/C-06/C-01b 及其余 17 份冻结契约字节
  - wire/错误码闭集/能力/schema/依赖；UI/恢复流程（B 卡）；真实用户数据；push
---

# FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1：C-15 v1.5 UNFREEZE

> **状态：`ready`（契约前置；只起草 + 独立 byte-level 复核 + 重冻；不实现）。**
> 来源：`FEA-11-L-S1-REGISTRY-RESILIENCE-1` scope review：现状把「roots identity 任一不合法」并入文件损坏 → 单根缺失/替换使整库 `SOURCE_REGISTRY_UNAVAILABLE`（C-15 v1.1 §5 冻结字面）。需把「文件字节损坏」与「根身份当前不可用」分离（1 pin）。

## 裁决依据（2026-11-07）

- 权威 scope review：`doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-scope-r1.md` → **READY-WITH-UNFREEZE**，仅 C-15 §5 单条、1 pin；C-16/C-17 零改动；影响面含导入/注册/撤销/重置/C-17 apply/watcher；恢复路径今天不存在（B 卡）。
- Codex 裁决输入：**不可用（product limit）**；按用户授权故障转移 **ZCode**（`subagent_zcode` 结果见本卡「ZCode 裁决记录」；如 ZCode 亦不可用则 DSH 直接裁决并记录）。
- **DSH 裁决**：
  - **D-1** 批准 C-15 §5 单条 UNFREEZE（v1.5；1/18 pins 重签；C-16/C-17 零字节）。
  - **D-2** 错误码保持现状：根身份当前不可用时的授权拒绝仍返回既有 `SOURCE_REGISTRY_UNAVAILABLE`（零可观察漂移；AC-S2-5 不变；码义收窄登记 limitation）。
  - **D-3** 拆卡：A（读取韧性，本轮释放，零 wire）；B（恢复/重授权 UI，依赖 L-S4）；C（`.corrupt-*` 无界复制）登记 limitation。
  - **D-4** A 不含 App 自动重注册（不得把缺失/替换根自动恢复授权）。
  - **D-5** `.corrupt-*` 复制策略不并入本卡。
  - **D-6** A 的 allowed_paths 文件级冻结（含新测试文件 `SourceRegistryResilienceTests.cs`）；`SourceScanScheduler.cs`/`HostRuntime.cs`/`SourceWatcher.cs` 明确 Out（需要时走 scope 修订）。
  - **D-7** A 须有 1 条 gated 真机 IPC（混合 registry：有效根 + 缺失根）。
  - **D-8** 冻结前先修台账（已 `task_ledger.py --write`）。
  - **D-9** A 交付复跑 `Fea11RunGrantIpcTests`/`Fea11ScanIpcTests`（skip/warning 分布会变）。

## In（本卡变更点，冻结）

### I-1 载体
`doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C15.md`：触发/授权/缺口/逐项修订/兼容/回退/复核要求/结果。

### I-2 C-15 v1.5（`doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md`）
- 头部状态 → `FROZEN v1.5（2026-11-07 重冻；v1.0/v1.1 历史）` + 载体/冻结记录链接；日期行补 v1.5。
- §5 状态机拆分：
  - **文件级损坏**（magic/version/长度/DPAPI/JSON **任一不合法**）仍 = 损坏：fail-closed、不创建空文件、不覆盖、复制 `registry.v1.dat.corrupt-<utc>`、所有 source 操作 `SOURCE_REGISTRY_UNAVAILABLE`（**保持**）。
  - **根身份当前不可用 / 不匹配**（根不存在、路径不可读、卷/文件 identity 与登记不符）**不再判定为文件损坏**：registry 文件仍合法可读；该根的条目以「不可用」状态参与读取（`List` 可用、其余根不受影响）；**授权期逐请求校验**（`Authorize` 对请求路径所属根重新核验 identity）：不可用/不匹配 → 该请求 typed 拒绝（沿用 `SOURCE_REGISTRY_UNAVAILABLE`，零新码），零写；**缺失根永不等于「无授权」**；不得自动重建 identity/自动重授权。
  - 恢复：仍由 `source_reset_registry {confirm:true}` 处理**文件级损坏**；根级恢复（重授权/重定位）由显式用户操作（B 卡接线），不得自动。
  - 撤销：不变（generation+1、持久化 `revoked_at`、C-16 ACK 语义不变）。
- §9 冻结条件追加 v1.5 条；变更记录追加 v1.5 行。

### I-3 冻结记录与矩阵
- `doc/plan/FEA-CONTRACT-FROZEN-C15.md`：pin → v1.5 最终字节 sha256；v1.5 重冻记录（历史 pin 保留）。
- `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`：C-15 行 → `FROZEN v1.5`（2026-11-07）。
- `verify_pins.ps1` 不改；18/18（C15 新值、其余 17 不变）。

### I-4 证据
`verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1/**`：pre/post sha、changed-lines.diff、other-17-pins、pins/check 日志、carrier。

## Out

- 生产实现（A 卡）；C-16/C-17 及其余契约；wire/错误码/能力/schema/依赖；UI/恢复流程（B 卡）；push。

## Acceptance Criteria（v3）

- [x] **AC-T1 契约增量最小**：C-15 v1.5 仅含 I-2 拆分（文件级损坏 vs 根级不可用 + 授权期校验 + 恢复/撤销不变）；C-16/C-17 及其余 17 契约逐字节不变；无新错误码/wire/能力/schema。 <<MET>>
- [x] **AC-T2 独立 byte-level 复核 approved**：fresh subagent 复核最终字节（diff 逐行、语义无放宽、17 项不变、pin 可复算）；P0/P1=0；session/reviewed_head 入载体。 <<MET>>
- [x] **AC-T3 重冻与 pins**：FROZEN-C15 更新；矩阵更新；`verify_pins` **18/18**（C15 新值、其余 17 原值）；`check.ps1`（默认 + `-TaskPath`）PASS。 <<MET>>
- [x] **AC-T4 载体与不夸大**：载体含触发/授权/变更点/兼容/回退/复核要求/结果；明写「契约就绪 ≠ 实现/产品可用」；未改 Run wire/schema/依赖。 <<MET>>

## 独立复核要求（byte-level）

- Reviewer：未参与起草/前轮复核的 fresh subagent；只读最终字节；记录 session/reviewed_head。
- 核对：I-2 逐项落地；C-16/C-17 及其余 17 契约零字节；无新错误码/wire/minor/schema/依赖；pin 可复算 18/18；载体/卡不夸大。
- 通过标准 approved（可含非阻断 P3）；随后 DSH 提交 UNFREEZE 并重跑 pins。

## ZCode 裁决记录

- **已记录（ZCode，2026-11-07，subagent_zcode 只读）**：对 D-1…D-9 **全部无异议、无翻案**；确认 C-15 §5 必须 UNFREEZE（1 份/1 pin）、C-16/C-17 零改动、零契约折中不存在；错误码保持现状（D-2）成立；同意 A/B/C 拆分（A 本轮、B 依赖 L-S4、C limitation）；补充 limitation 应同时引用 C-16 :174 与 C-06 :44 的码义不自洽。建议 A 的 Owner 可为 ZCode（Host 单文件窄改）；本卡经 DSH 裁决采用既有 Host 实现 Owner。

## Review 处置（DSH，2026-11-07；append-only）

- r1 `changes_requested`（P0=0/P1=2/P2=5/P3=9）：P1-A 矩阵行、P1-B check 台账/DAG；DSH 处置：矩阵 C-15 行 → FROZEN v1.5、台账重建（529/11）、PLAN READY/DAG 登记、EV.md/日志刷新、错误码跨契约语义登记 limitation、派生状态不新增契约字段、AC-T4 措辞补齐。
- **r2 `approved`（P0=0/P1=0/P2=0/P3=15 非阻断；session `ccdae3ad-…`，reviewed_head `821b309a0`）**：P1 全关闭；C-15 字节未变（`f9e376a0…`）；pins 18/18、其余 17 零 diff、EV 7/7、diff 归一化一致、无安全放宽。
- 剩余 P3 登记接受（记录/引用/措辞级；C-15 字节不再改动以保持 pin）。

## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-T3/T4 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1/carrier.md | ae8c2de07 | 080cb6c9dfea0ba0eb39254a3af5b09c872b954dc7390696bbaae97293e4bd78 | CANONICAL |
| EV-02 | AC-T3/T4 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1/changed-lines.diff | ae8c2de07 | a872d7d1f96978b54254ca077cc47fbe8c00fce330d78becdb4aaefebee4690f | CANONICAL |
| EV-03 | AC-T3/T4 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1/EV.md | ae8c2de07 | 0e157cadb74c4530f9b1489e15bdcea999765329c04feabf5f44ffc1f217653d | CANONICAL |
| EV-04 | AC-T3/T4 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1/logs/check-taskpath.log | ae8c2de07 | 046d00987d38cc32e3b52c8d992d0f746c133ff04b4241dbb4eebf2f4c18dc42 | CANONICAL |
| EV-05 | AC-T3/T4 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1/logs/check.log | ae8c2de07 | 27430a9761cfc512af676a0678f3ea88c1dcb487ebc6a1d0ef2b28e9469510c0 | CANONICAL |
| EV-06 | AC-T3/T4 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1/logs/pins.log | ae8c2de07 | 584e7ad029873e0b7bdce5a1d5884725f1a93537b5a49e872c9b9eba6408323e | CANONICAL |
| EV-07 | AC-T3/T4 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1/other-17-pins.txt | ae8c2de07 | 01c4d04358f466b3683c999e9b1424d259924c2b84fef8ad34ed22a11004dc57 | CANONICAL |
| EV-08 | AC-T3/T4 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1/pre-post.sha256 | ae8c2de07 | 80c72a4f0c3b22b013d68ac67e10c3310ab7b94791fafd3c0848d3804b27e46b | CANONICAL |
| EV-09 | AC-T2 | doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C15.md | ae8c2de07 | 080cb6c9dfea0ba0eb39254a3af5b09c872b954dc7390696bbaae97293e4bd78 | CANONICAL |
| EV-10 | AC-T2 | doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1-r1.md | ae8c2de07 | e12b46c822b03f619741321ba6c07b9dadd7ff2b98960cc1dc026e1200853fbb | CANONICAL |
| EV-11 | AC-T2 | doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1-r2.md | ae8c2de07 | dfa041ea222f2a482866b94dc08cec5dde33afe98ad7548641aaa199aee02304 | CANONICAL |

> 证据树其余文件（changed-lines.diff、other-17-pins.txt、pre-post.sha256、carrier.md、logs 3）的逐文件 sha256 见 EV.md；本表只列 closeout 层关键项。

## Resource Manifest

| resource_type | 资源 | disposition | 目标 | 完整性 | 引用/进程检查结果 |
|---|---|---|---|---|---|
| 无删除/移动/归档 | - | NOT_APPLICABLE | - | - | 本卡仅改契约/冻结记录/矩阵/载体/证据；仓内 0 删除/0 移动/0 归档；仓外隔离根 `G:/CODEX/New Manga.workspace/FEA-11-L-S1-REGISTRY-RESILIENCE-1/` 保留（无独有产品数据） |

## Closeout Record（2026-11-07）

- **状态**：`done`；delivery/integration = `ae8c2de07`（C-15 v1.5 + FROZEN-C15 + 矩阵 + 载体 + r1/r2 报告 + 证据 + PREREQ 卡）。
- **AC 判定**：AC-T1…AC-T4 **全 MET**。
- **Review 处置**：r1 changes_requested → 处置 → **r2 approved（P0=0/P1=0/P2=0/P3=15 非阻断）**。
- **门禁数字（before → after）**：pins **18/18 → 18/18**（C15 `d8c0a3bc…`→`f9e376a0…`；其余 17 项实测 UNCHANGED）；`check.ps1`（默认 + `-TaskPath`）PASS(3 warnings)；C-15 变更 +7/−4 行（§5 拆分 + §9 记录）；C-16/C-17 零字节；全量 pytest/.NET **NOT_RUN**（契约-only；由 A/L-S4 实现卡门禁实跑）。
- **limitations / follow-up**：A（读取韧性）与 B（恢复/重授权）实现未交付；错误码复用 `SOURCE_REGISTRY_UNAVAILABLE` 的跨契约码义不自洽登记 limitation；`.corrupt-*` 无界复制（C）登记；契约就绪 ≠ 实现/产品可用。
- **push**：Lead 统一 push（PRE/POST/AHEAD 记录见状态文件）。
