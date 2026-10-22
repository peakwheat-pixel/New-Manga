---
task_id: GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1
author: DeepSeek Harness
base_commit: 345c86857f6ea80153ead49271e84ff234a4963f
reviewed_head: e6f400101d39e466d44278f08163ed1e4c1c234a
decision: approved
---

## 结论

**approved**

- `reviewed_head = e6f400101d39e466d44278f08163ed1e4c1c234a`
- `diff_base = 345c86857f6ea80153ead49271e84ff234a4963f`
- `delivery = a4fd609b43db745f789251467907cbf69208d2e3`
- canonical main：`ec136c64f2fc994602de145bc47907976bf58222`

R1 的两个 P2 已实质闭合：validation 计数已改为明确快照并标注 `registered_evidence_pins_at_measurement=7`；broad active Gate、`DEPENDENCY_INACTIVE`、line227 第 7 个 real 目标末检已写入设计。未发现 P0/P1。批准仅设计 metadata；未来实现 Task 仍需另冻，不批准任何运行实现/例外、原件修改、真实清理、父 done、r212 解除或 push。

## P0 / P1 / P2

- **P0：0。**
- **P1：0。**
- **P2（实现 Task 需冻结的匹配键）**：broad Gate 的“12 条对应保全 Declaration”不能按来源文件统计。当前 `idx.declarations` 中来自两历史源的声明共有 **83 条**（含其它旧 Manifest 行），远多于 12。实现必须按 12 条 `DECL_BROAD_ROOT_PRESERVED` warning 的 `file/locator/role/root` 与 Declaration 的 `source_file/locator/normalized/real/keep` 精确对应，不能只数来源文件或 count。设计文字“对应”方向正确，但建议实现 Task 明确冻结该匹配键，避免把 83 当作 12 或只核 warning 数。
- **说明（非 P2）**：`validation.json` 的 `counts_snapshot 2582/1889`、`snapshot_protected_count 1889`、`registered_evidence_pins_at_measurement 7` 是 R2 最终 pin 前的快照；当前实际为 **2583/1890 / 12 errors / 272 warnings**（8 EV 已计入）。measurement_basis 已明确，不能把 1882/1889 当实时或把 Owner 1882 全集合比较当 Reviewer 独立重建。

## Architecture

- **broad active Gate 可落地**：前序 broad fatal 原样返回；自己的 policy absent+untracked 为 no-op；自己的 policy enabled 时必须 broad 存在且 tracked、无 broad policy fatal、12 条 broad warning 对应 12 条保全 Declaration、五广域根保护均在，否则只加 `DEPENDENCY_INACTIVE`，保留全部输入错误（如 24→25，不是 19）。
- 设计明确 total error 数不硬编码为 12；12→7 只是当前 canonical 验收快照，其它债务原样保留。
- **末检**：重新 resolve 原 line227 声明的 `normalized` 并等于冻结 `real_normalized`，同时保留 lexical/real 保护；它是第 7 个实目标复检对象，不是第 7 条新增 Declaration，仍为 `+6 Declaration / +4 warning`。T15/T18 已明确。
- tracking 仅覆盖配置/facts/四源；两个 reference 目录只查存在性/目录类型/real；broad 策略原字节/tracking 也纳入发布末检。
- 模板 1 binding（R25/R26、fence 117..239、line227 保留）、3 个 NUL/C0 空 parse binding、2 个 reference guard；只移 5 个完整错误，新增 6 Declaration +4 warning；不泛化整文件/围栏忽略，不剥离/转码 NUL，不接管 P22。
- 当前 6 个 guard 根均已保护，新增 protected 根为 0；旧保护子集、七历史身份、r212 与五广域根保持。

## Verification

**本轮实际只读执行**

- `validate_design.py`：**exit 0**，`DESIGN_DATA_ASSERTIONS_PASSED`。
- 重新计算 canonical sample SHA：`3f4cae13b0848ed105b5ba59c7538c8456c991b1403596ca64b68b63381e4b7d`，与 Task/Handoff/validation 一致。
- `design_raw_sha256`：当前 design.md 为 `02d1e9e55ad0021d55481883c7067a2536c294ef03a7628ee3caeb4b1bf2f9b0`，与 specimen 绑定一致。
- 8 EV 逐项 `raw = blob = pin` 全部成立；Task 实际 `EVIDENCE_PIN 8 / errors 0`（12 declarations）。
- 当前 canonical scan：**12 errors / 2583 declarations / 1890 protected roots / 272 warnings**；R25/R26/R27/R28/R32 与旧矩阵完整 identity 匹配，其余 7 项保持。
- broad 证据：`DECL_BROAD_ROOT_PRESERVED` warning **12 条**、五广域根全部 exact 受保护、broad policy tracked 且无 broad fatal；但来源文件声明共 83 条，故 Gate 必须按 warning/Declaration 身份匹配（见 P2）。
- 模板 P09 内存 parse：1 declaration / 2 errors / 2 warnings；line227 worktree 存在且 exact 受保护。
- P14/P22 三源 NUL/C0：P14 `[286]`，P22 `[12330,20486]`；各自空 parse 0/0/0；与有效 source facts 一致。
- 六个 guard 根（四源 + 两个参考目录）均 exact 受保护；两个目录存在。
- 运行 policy 路径 **不存在**；`tools/**` 在 `345c..e6f` diff 为空；WT `status --porcelain` 为空。
- canonical `check.ps1`：**PASS（2 个既有 warning）**。
- `git diff --check 345c…e6f`：**exit 0**。

**沿用 R1 已执行**

- 四源 raw SHA、五完整错误、P14 `SOURCE_PIN` 未实际登记、P22 untracked/作者 unknown、模板围栏/行/line227、7 历史身份；本轮不重复全部研究。
- R1 的 1882 全保护集合比较仍属 Owner baseline，**Reviewer 未独立重建**；本轮只确认当前 12、8 EV、6 guard 与 1890 快照。

**NOT_RUN**

- 未来 `_apply_historical_evidence_interpretation`、实际 `12→7`、`+6 Declaration/+4 warning`、T01–T18：**PLANNED_NOT_RUN**，本轮不实施、不跑矩阵。
- 产品构建、旧 127 回归、fixture、全 102 heads/140 WT 盘点、进程/句柄、真实 apply/cleanup：**NOT_RUN**；不据此授权删除。
- 未创建任何 temp/fixture/探针，未改 ACL，未执行 Git mutation。

## 范围与下一步

- 本批准仅设计契约与 metadata；不批准实现、运行例外、NUL 修改、P22 接管、旧 source/pin 修改、真实清理、父 done、r212 解除或 push。
- 可继续 Codex 正常 merge/main 复核并 done；建议实现 Task 冻结 P2 中的 broad/Declaration 匹配键，并显式覆盖 broad absent/no-op 的 `DEPENDENCY_INACTIVE`。102/140 全部原位保留；设计通过不自动实施 T01–T18。