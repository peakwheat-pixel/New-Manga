# CONTRACT-UNFREEZE-2026-11-07-C15：C-15 v1.5（Registry 文件损坏与「根身份当前不可用」分离）

> 载体用途：按 [C-15 冻结记录](../plan/FEA-CONTRACT-FROZEN-C15.md) 的 UNFREEZE 流程提出 C-15 v1.5 字节修订；须经独立上下文 fresh subagent 做 **byte-level 复核** + DSH 重新冻结后方可视为最终字节。
> 触发：用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；`FEA-11-L-S1-REGISTRY-RESILIENCE-1` 权威 scope review `doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-scope-r1.md`（**READY-WITH-UNFREEZE**：仅 C-15 §5 单条，1 pin；C-16/C-17 零改）；Codex 裁决输入不可用（product limit）→ 按用户授权故障转移 ZCode（记录见卡）；DSH 裁决 D-1…D-9（`doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1.md`）。
> 顺序约束：本载体 + C-15 + 冻结记录 + 矩阵为 UNFREEZE 提交；A 实现另卡（`FEA-11-L-S1-REGISTRY-RESILIENCE-1`，depends PREREQ）；B（恢复/重授权）另卡。

## 1. 背景与目标

现状：`SourceAccessRegistry.Load()` 在读取时对每个条目的每个 root 做 `SourceSecurity.Identity()` 严格比对，任一不符即复制 `registry.v1.dat.corrupt-*` 并抛 `SOURCE_REGISTRY_UNAVAILABLE`（`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs:119-138`）。这是 C-15 v1.1 §5 的**冻结字面**（`doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` §5：「magic/version/长度/DPAPI/JSON/**roots identity 任一不合法** = 损坏」）。结果：用户移动/删除/替换一个引用源根 → 整库 source 线不可用（导入/注册/撤销/重置/C-17 apply/watcher 全部阻断）。

目标（最小）：把「**文件字节损坏**」与「**根身份当前不可用/不匹配**」拆开——文件级损坏仍整库 fail-closed；根级不可用不再使 registry 不可读（`List` 可用、其余根不受影响），授权期逐请求重核验该根 identity，不可用 → 该请求 typed 拒绝且零写；**缺失根永不等于「无授权」**；不自动重建/重授权。恢复/撤销语义不变。

## 2. 提议修订（C-15 v1.5）

### A. 头部与日期
- 状态行 → `FROZEN v1.5（2026-11-07 重冻；v1.0 2026-11-03、v1.1 2026-11-04 历史）` + 载体/冻结记录链接；日期行补 v1.5。

### B. §5 状态机
- **文件级损坏**（magic/version/长度/DPAPI/JSON 任一不合法）：保持 = 损坏、fail-closed、不创建空文件/不覆盖、复制 `registry.v1.dat.corrupt-<utc>`、所有 source 操作 `SOURCE_REGISTRY_UNAVAILABLE`。
- **根身份当前不可用/不匹配**（新增拆分）：根不存在、路径不可读、卷/文件 identity 与登记不符 → **不再判定为文件损坏**；registry 文件仍合法可读；该根条目以「当前不可用」参与读取（`List` 可用、其余根不受影响）；`Authorize` 逐请求对请求路径所属根重新核验 identity，不可用/不匹配 → 该请求 typed 拒绝（**沿用既有 `SOURCE_REGISTRY_UNAVAILABLE`，零新错误码**）、零写；缺失根 ≠ 无授权；不自动重建 identity、不自动重授权。
- 恢复：文件级损坏恢复不变（显式 `source_reset_registry {confirm:true}`）；根级恢复由显式用户操作完成，不得自动。
- 撤销：不变（generation+1、`revoked_at`、C-16 ACK 语义）。

### C. §9
- 冻结条件追加 ⑤（v1.5 独立 byte-level 复核 approved、C-16/C-17 与其余 17 pins 零改动、错误码/TTL/撤销/ACL/加密边界零改动）。
- 变更记录追加 v1.5 行。

### D. 冻结记录/矩阵
- `doc/plan/FEA-CONTRACT-FROZEN-C15.md`：pin → v1.5 最终字节 sha256；v1.5 重冻记录（历史 pin 保留）。
- `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`：C-15 行 → `FROZEN v1.5`（2026-11-07）。
- `verify_pins.ps1` 不改；18/18（C15 新值、其余 17 不变）。

## 3. 兼容与影响

- **旧 Host × 新语义**：旧实现仍整库 fail-closed（行为不变）；新实现放宽到条目级（受 A 卡控制）。
- **新 Host × 旧 Core / 旧契约读者**：错误码不变、wire 不变、无 schema/依赖变化；`SOURCE_REGISTRY_UNAVAILABLE` 语义收窄为「文件级损坏或该请求所属根当前不可用」。
- **安全**：文件级损坏仍整库 fail-closed；根级不可用只影响该根相关请求；身份校验从 `Load` 移到 `Authorize`（A 卡实现必须补，只删不补会让被替换根重新获得授权能力——本载体明确禁止）。
- **恢复路径**今日不存在（App 无调用）：B 卡接线，不因本契约自动可用。

## 4. 风险与回退

- 风险：①1/18 pin 重签须独立复核；②实现若只删 `Load` 校验而不补 `Authorize` 校验 → 安全回退（A 卡 AC 强制）；③错误码复用可能被误解为「文件损坏」（登记 limitation/词表另案）。
- 回退：恢复 C-15 v1.1 字节（sha `d8c0a3bcfc21…`）与冻结记录/矩阵；A 卡不释放。

## 5. 独立复核要求

- Reviewer：未参与起草/前轮复核的 fresh subagent；只读最终字节；记录 session/reviewed_head。
- 核对：①本载体 §2 逐项落地；②仅 C-15/冻结记录/矩阵变化（`git diff --name-only`），C-16/C-17 及 src/apps/tools/tests 零 diff；③无新错误码/wire/能力/schema/依赖；④pin 可复算、18/18、其余 17 不变；⑤语义无放宽（缺失根 ≠ 无授权；不自动重建/重授权；恢复/撤销不变）。
- 通过标准：approved（可含非阻断 P3）；随后 DSH 提交 UNFREEZE 并重跑 pins；未通过 → 返修后窄面复审。

## 6. 复核结果（独立 byte-level）

- **r1（`doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1-r1.md`）**：`changes_requested`，**P0=0 / P1=2 / P2=5 / P3=9**；C-15 v1.5 条款字节语义合格（安全语义无 P1；文件级损坏仍整库 fail-closed、根级不可用 List 可用/Authorize 逐请求/零写/缺失根≠无授权/不自动重建；pin `f9e376a0…` 可复算、18/18）。两 P1 均为簿记/门禁：P1-A 冻结矩阵 C-15 行未更新；P1-B `check.ps1` 未过（台账/PREREQ 未登记 DAG）。
- **处置（2026-11-07）**：①矩阵 C-15 行 → `FROZEN v1.5`（2026-11-07）已修；②台账重建（529 Task/11 非终态）与 PLAN READY/DAG 登记（PREREQ-1/A/L-S4-A）已修，`check.ps1`（默认 + `-TaskPath`）PASS；③P2：A 卡工作树改动属 Lead 释放编辑（单独提交）；`check.log`/`EV.md` 已刷新（EV 逐文件 sha256）；④跨契约错误码语义（C-15 复用 `SOURCE_REGISTRY_UNAVAILABLE` 与 C-16 `:174`/C-06 `:44` 的码义不自洽）登记为 limitation，词表细化另案，不改本批字节；⑤派生状态（根「当前不可用」的对外呈现字段）为 A 卡实现细节，契约不新增字段（不改变 C-15 字节）；⑥AC-T4 措辞已补「契约就绪 ≠ 实现/产品可用」。
- **r2 窄面复核（`doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1-r2.md`）**：**`approved`，P0=0/P1=0/P2=0/P3=15（非阻断）**；P1-A/P1-B 关闭；C-15 字节未变（`f9e376a0…`）；pins 18/18、其余 17 项零 diff、EV 7/7、diff 归一化一致、无安全放宽。
- **C-15 字节未变**（`f9e376a0…`）→ 仅记录/门禁/证据修复；r2 通过后提交 UNFREEZE 并重冻。

## 7. 证据

- `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1/pre-post.sha256`
- `changed-lines.diff`、`other-17-pins.txt`
- `carrier.md`、`EV.md`
- `logs/pins.log`、`logs/check.log`、`logs/check-taskpath.log`
