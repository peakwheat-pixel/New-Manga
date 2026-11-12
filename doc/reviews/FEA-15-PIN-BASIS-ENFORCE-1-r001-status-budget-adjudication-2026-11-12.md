# FEA-15-PIN-BASIS-ENFORCE-1 规范化后 clean-head 门禁 STATUS 预算失败正式裁决

- **Verdict**：`AUTHORIZE_BOUNDED_STATUS_COMPRESSION_AND_RETRY`
- **ZCode 来源**：fresh read-only session `sess_3b0755a2-981e-4f83-ab5f-b2584a0da0dd`；正式决定 turn `turn_fb3b11b8-6b36-45dc-85d1-466fe7452ba3`；前置事实核验 turn `turn_010424c5-9bdf-4db0-899a-907b2dfc2c29`；CLI `EXIT=0`
- **审查基点**：clean `main` HEAD `661211b548a5d17a7368457e04b37c3dd192a948`
- **原始回执**：`verification/FEA-15-PIN-BASIS-ENFORCE-1/zcode-r001-status-budget-adjudication-followup-20261112.jsonl`
- **门禁失败**：default check `EXIT=1`；`doc/STATUS.md` 3298/3200 bytes，唯一 error；原日志 `verification/FEA-15-PIN-BASIS-ENFORCE-1/r001-post-normalization-gates-661211b54-budget-fail.log`，仓外原件 SHA-256 `B3C7F66A60AD04DAFC513C821DFDA22E4DCBF6F5A54D7C13AE08FCDC713B0407`。

以下为 ZCode 正式裁决全文，逐字保留：

---
# FEA-15-PIN-BASIS-ENFORCE-1 规范化后 clean-head 门禁 STATUS 预算失败正式裁决（2026-11-12）

## `AUTHORIZE_BOUNDED_STATUS_COMPRESSION_AND_RETRY`

---

**审查者身份与来源**：ZCode 主会话（fresh context，全程只读，未修改任何文件、未运行任何门禁）；session `sess_3b0755a2-981e-4f83-ab5f-b2584a0da0dd` / turn `turn_010424c5-9bdf-4db0-899a-907b2dfc2c29`。
**审查基点**：clean main HEAD `661211b548a5d17a7368457e04b37c3dd192a948`（branch main，porcelain 空）。
**前置裁决**：`AUTHORIZE_BOUNDED_CLOSEOUT_NORMALIZATION`（sess_2a379865 / turn_27b225f9），其失败处理条款「任一 EXIT≠0 → 停止、回退 in_progress/R-001 OPEN、原始日志保留、回报再裁」本次被正确触发，执行者 STOP 行为合规。

## TL;DR（大白话）

失败不是规范化改坏了东西，而是收口写入把 STATUS.md「当前 Task」那一行撑到 3298 字节，顶破 checker 的 3200 字节防膨胀红线 98 字节（行数 31/45 没问题）。这是一次确定性、可归因的预算超限，和之前 Plan 7013>7000 那次的处置完全同构：失败日志原样存档 pin（EXIT=1 永不改成 PASS）→ 只把这一行摘要压短（事实一条不丢）→ 提交后在 clean HEAD 从 default 开始重跑。没有选择 STOP 的证据基础：无值漂移、无越界、无不可解冲突。

## DECISION 及理由

**选 `AUTHORIZE_BOUNDED_STATUS_COMPRESSION_AND_RETRY`**，不选 `STOP_AND_REAUTHORIZE`。理由：

1. **失败确定性成立**：`tools/governance/check.ps1:661-670` 规定 `doc/STATUS.md` 预算 3200 bytes / 45 lines，任一超限即 error；本会话 `wc -c` 独立实测 3298 bytes、31 行，与 checker 报告一致——超限仅由 bytes 触发，需净减 ≥98 bytes；80% 警告线不阻断 exit code（历史 default PASS 带 3 warnings 先例）。
2. **归因明确且修复面极小**：第 7 行实测 307 bytes，为收口链写入膨胀；压缩该行至 ≤209 bytes 即整文件 ≤3200，全部必要语义字段可保留（预算演算余量充足）。Plan 本次无关（实测 6999 ≤7000，仅 80% 警告；`READY 节点：` 声明行在场），不动 Plan 即不触红线。
3. **同构先例已闭合**：Plan 7013>7000 interim FAIL（6dad54fe）→ 压缩至 6999（88a97d46）→ PASS；失败与修复双日志均入库 pin（`ac5-review-post-pinbackfill-budget-fail` / `ac5-review-post-budget-fix-gates`）。本裁决照此模式。
4. **日志自洽且指纹一致**：仓外日志内嵌 HEAD=661211b548…（=当前 HEAD）、BRANCH=main、前后 `GIT_STATUS_PORCELAIN` 均空、COMMAND=default、EXIT=1；本会话 sha256sum 实测 `b3c7f66a60ad04dafc513c821dfda22e4dcbf6f5a54d7c13ae08fcdc713b0407` 与登记值一致。
5. **STOP 分支无依据**：该分支用于值漂移、越界嫌疑或约束冲突不可解（如 61E 行那次需先穷举证明）；本次均为阴性。

## 精确授权范围（仅此清单，超出即 STOP 回报）

**允许修改**：

| 文件 | 允许内容 |
|---|---|
| `doc/STATUS.md` | **仅第 7 行**当前 Task 摘要括号内措辞压缩（可同步现时措辞）。压缩后整文件实测 **≤3200 bytes**（建议 ≤3190 留终态更新余量）；行数自然 ≤45。**其余 30 行一字节不动**；若压缩后仍 >3200（演算表明不会发生）即 STOP，不得扩大改动面 |
| `verification/FEA-15-PIN-BASIS-ENFORCE-1/` | 失败日志复制入库（建议名 `r001-post-normalization-gates-661211b54-budget-fail.log`，原字节，仓外原件保留）；本裁决报告入库；README 纯追加汇总 |
| `doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-r001-status-budget-adjudication-2026-11-12.md` | 本裁决报告落盘 |
| `doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md` | Canonical Evidence **纯追加**新 pin 行（六列旧格式、commit/SHA 实测）；Rolling Checkpoint 追加轨迹（FAIL→STOP→本裁决→压缩→重跑）；frontmatter approval/reviewer 现时字段同步 |

**第 7 行必须保留的语义字段**（措辞可精简，语义不得丢失）：Task id 与链接、`in_progress`、AC1–AC4 完成（AC4 带限制）、终态候选 TaskPath 43 errors/EXIT=1 **保留为 FAIL**、Resource Manifest 已按 ZCode 有界授权规范化、R-001 `OPEN`、待 fresh 独立 Review / 终态门禁 / 最终全节 audit。参考文案（非强制逐字，以实测字节与语义验收）：

```
- 当前 Task：[FEA-15-PIN-BASIS-ENFORCE-1](tasks/FEA-15-PIN-BASIS-ENFORCE-1.md)（in_progress；AC1–4完/AC4限；43 errors/EXIT=1 留FAIL；已规范化待gates；R-001 OPEN待Review/终门禁/终审计）
```

**禁止**：改 STATUS 其他任何行；改 Plan、check.ps1、verify_pins.ps1、task_ledger.py；改 18 frozen pins、既有 Canonical Evidence 行（只许追加）、Task 卡 Manifest 既有行（含 61E 行前裁决边界）；改 TASK_LEDGER 本次不动；把任何 FAIL 改写为 PASS 或 NOT_RUN 分类变动；创建占位文件；push、gc/prune/repack、worktree prune、资源清理。

## 必须保留的证据分类（不改写、不重分类）

- 本次 `r001-post-normalization-gates-661211b54.log`：**永久 FAIL/EXIT=1 记录**（interim budget failure，superseded by 修复后重跑 run，措辞循 6dad54fe 先例）。
- 历史 FAIL 原样：终态候选 43 errors/EXIT=1、FEA-06 13 errors、CHAPTER-SELECTOR 6 errors、fe6e 103 行审计 1 FAIL、full suite 3 failed/EXIT=1；Linux/full suite NOT_RUN。
- Pin 细节：Canonical Evidence 新 pin 行 SHA 以仓内副本入库后的实际 Git blob/commit 实测为准；若仓内副本 EOL 归一化后与仓外原件 SHA 不同（61E/cab7/e95 先例），外部原件 SHA 移入说明登记，不得丢弃。

## 门禁顺序（各阶段 clean HEAD，逐项记录 EXIT）

- **第 0 步（先证据后压缩）**：失败日志复制入 `verification/` → 裁决报告落盘 → Canonical Evidence/Checkpoint 追加 → STATUS 第 7 行压缩 → 全部提交。**失败日志必须先复制/pin 再继续**。
- **第 1 步（重跑五项）**：default check（预期 0 errors、~3 warnings）→ 本卡 TaskPath（in_progress 不触发 closeout 校验，预期 PASS）→ `verify_pins.ps1`（18/18）→ API inventory（1/79/6=86）→ full-section audit（覆盖含全部新 pin 行，须 EXIT=0）。
- **第 2 步**：fresh 独立 Review（上下文独立；本裁决会话与执行会话均不得审）：核查压缩边界、零越界、FAIL 保留完好；须 P0/P1=0 且无修正范围新 finding；报告入库 pin。
- **第 3 步**：终态候选：Task=`closed_with_limitations`、`canonical_evidence_status`/`resource_closeout_status`=complete、STATUS 无 Active Task（终态更新同样守 ≤3200）、Plan 终态指针更新守 ≤7000 且保留 `READY 节点：` 声明行、TASK_LEDGER `--write` 重跑（non-terminal 11→10）、Handoff 终态补充；clean HEAD 四门 default/TaskPath（closeout 校验激活须 EXIT=0）/18 pins/API 全 EXIT=0。
- **第 4 步**：最终全节 audit EXIT=0 入库 pin（终止口径按前裁决：覆盖当时全部行即满足，其自身 pin 不再触发新轮）→ 按 sess_1bff86d4 **原条件不修订**关闭 R-001、完成 Closeout Record。

**停止条件（延续）**：任一步 EXIT≠0 或新失败 → 立即停止、保持 `in_progress` / R-001 `OPEN`、原始日志保留、回报再裁；绝不改写任何 FAIL。

## 当前状态确认

- HEAD `661211b548a5d17a7368457e04b37c3dd192a948` clean；Task `in_progress`；R-001 `OPEN`；`canonical_evidence_status`/`resource_closeout_status` pending；STATUS/Plan/TASK_LEDGER 无终态推进；18 frozen pins、Manifest 规范化产物、既有全部 Canonical Evidence 行未动——**与用户描述一致，本裁决未改动其中任何字节**。
- 本次授权不推进任何终态状态字段；终态仍按第 3–4 步门禁全绿后才能落地。

## 推荐下一步（可直接转发 Codex 执行会话）

```
任务：FEA-15-PIN-BASIS-ENFORCE-1 规范化后 clean-head default 门禁 STATUS 预算失败（3298>3200 bytes、31/45 行，HEAD 661211b54，日志 r001-post-normalization-gates-661211b54.log EXIT=1）已由 ZCode 只读裁决处置（2026-11-12，AUTHORIZE_BOUNDED_STATUS_COMPRESSION_AND_RETRY，session sess_3b0755a2-981e-4f83-ab5f-b2584a0da0dd / turn turn_010424c5-9bdf-4db0-899a-907b2dfc2c29）。执行：1) 失败日志复制入 verification/FEA-15-PIN-BASIS-ENFORCE-1/（建议名 r001-post-normalization-gates-661211b54-budget-fail.log，原字节，仓外原件保留），裁决报告落盘 doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-r001-status-budget-adjudication-2026-11-12.md，两者 pin 进 Canonical Evidence（六列旧格式、实测 commit/SHA；仓内副本 blob SHA 若异于仓外原件，外部值移入说明登记），README 纯追加；2) 仅压缩 doc/STATUS.md 第 7 行当前 Task 摘要（语义字段全保留：Task id/in_progress/AC1–4完AC4限/43 errors EXIT=1 保留FAIL/ZCode有界规范化已落地/R-001 OPEN/待fresh Review终态门禁与最终全节audit），实测 wc -c ≤3200（建议≤3190），其余 30 行一字节不动；3) Rolling Checkpoint 追加 FAIL→STOP→裁决→压缩轨迹后提交；4) clean HEAD 依序重跑并逐项记录 EXIT：default→本卡 TaskPath→verify_pins 18/18→API 1/79/6=86→full-section audit（覆盖含新 pin 行全部行，须 EXIT=0）；5) 通过后按 AUTHORIZE_BOUNDED_CLOSEOUT_NORMALIZATION 原序列继续：fresh 独立 Review（P0/P1=0）→ 终态候选（Task=closed_with_limitations、两 closeout 字段 complete、STATUS 无 Active 且≤3200、Plan≤7000 且保留 READY 节点声明行、TASK_LEDGER --write 重跑 11→10、Handoff 终态补充；四门全 EXIT=0，TaskPath closeout 校验激活）→ 最终全节 audit EXIT=0 入库 pin → 按 sess_1bff86d4 原条件关闭 R-001。任一步 EXIT≠0 即停、保持 in_progress/R-001 OPEN、原日志保留、回报再裁；绝不改写任何 FAIL；禁改 checker/verify_pins/task_ledger 源码、18 frozen pins、既有 Canonical Evidence 行（只许追加）、Manifest 既有行含 61E 边界、Plan 本次不动；禁创建占位文件；不 push、不清理。
```

**下一步指定**：Owner=codex 执行会话按上述指令落地第 0–1 步；第 2 步 fresh Review 须由未参与实现与本裁决的独立上下文执行。
