---
id: FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1
title: C-15 v1.5 UNFREEZE（Registry 文件损坏与「根身份当前不可用」分离）
kind: contract
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；`FEA-11-L-S1-REGISTRY-RESILIENCE-1` 权威 scope review `doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-scope-r1.md`（fresh subagent `976c9d16-…`，**READY-WITH-UNFREEZE**：仅 C-15 §5 单条，1 pin；C-16/C-17 零改）；Codex 裁决输入因额度不可用 → 按用户授权故障转移 ZCode（结果见卡「裁决依据」）；DSH 裁决 D-1…D-9（见下）
suggested_owner: dsh
owner: dsh
reviewer: 独立上下文 fresh subagent（byte-level；不得参与本 UNFREEZE 起草；session 见 `doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1-r1.md` 与载体）
depends_on:
  - FEA-11-RUN-GRANT-2B-PREREQ-1
base_commit: d782c52a4
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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
