# P02 R10 Review erratum — 针对 exact HEAD `92dc7361194f1db8fdf7aff3a15a3d234ae56678`

审查对象与状态不变：HEAD `92dc7361194f1db8fdf7aff3a15a3d234ae56678`、tree `73511f7ba03d6b2215f4dad9c5a3c7f442471a6f`、parent/base `083d2b47f7051c2dedd0d9ae4346ae1affab6c1b`；审查 worktree 仍 clean（`git status --porcelain=v1 -uall` 空，EXIT=0），HEAD/tree 未变，未修改候选或任何项目文件，未新增审查范围。

## E-1 路径状态计数更正（原报告 §1 表、§5 表）

- 复核命令：`git diff --name-status 083d2b47f7051c2dedd0d9ae4346ae1affab6c1b 92dc7361194f1db8fdf7aff3a15a3d234ae56678` → **EXIT=0**。
- 实际状态：**2 added + 5 modified**（共 7 路径，`+152 / −21`）。
  - `A`：`codex-checkpoint-p02-preflight-r4-condition-closure.md`、`codex-checkpoint-p02-smoke-admission-r1.md`
  - `M`：`codex-scratch-build-process-isolation-scope-delta-r1.md`、`codex-scratch-build-preflight-r2.md`、`codex-scratch-build-preflight-observations-r2.json`、`codex-checkpoint-p02-preflight-r4-start.md`、`codex-preflight-r4-validation.md`
- 原报告中的 **“3 A + 4 M” 作废**，更正为 **2 A + 5 M**。路径集合、范围结论（全部落在 `verification/P02/**`，无产品代码/Schema/IPC/依赖/用户数据改动）不变。

## E-2 撤回原 O-3

- 依据归档的 r9 正式响应 `verification/P02/dsh-review-p02-preflight-r4.response.md`：`:5`/`:50` 明确 **P0/P1/P2 = 0/0/0、P3 = 6、NOTE = 1**；`:57-91` 为 **C-01..C-06 六项，全部标注 P3**。
- 因此 r10 的 C-01..C-06 与 r9 正式响应**同编号、一一对应，六项即六个 P3**；不存在 `P3-01..P3-05` 编号组，也**不需要任何 crosswalk**。
- **原 O-3 整条撤回**（其依据是一份早于归档正式响应的过程稿 `dsh-review-p02-preflight-r4.stdout.md`，不作为 r9 正式记录）；原 §8 中“补编号映射”的建议一并作废。入库 r9 附件时应入库正式响应 `-r4.response.md`（17211 bytes），而非过程稿 `-r4.stdout.md`（14802 bytes）。

## E-3 连带更正（同一错源，仅限原 O-2 的证据锚点）

- 原 O-2 对 “one note” 内容的描述取自过程稿，作废。归档正式响应的 note 为 **`NOTE-01`**（`:93-94`）：r9 审查侧无法独立核对 **source commit pins 的期望尺寸/哈希来源表**。
- 更正后 **O-2 仍为非阻断观察**：候选文档（如 `codex-checkpoint-p02-preflight-r4-condition-closure.md:6`）引用 “one note” 而未点名/处置；建议入库 r9 附件时引用 `NOTE-01` 原文。附注：该 pin 源表在 r10 可核——我以 `codex-scratch-build-preflight-inputs-r1.tsv` 与 `observations-r2.json` 的 20 条逐项比对，**0 处不符**，故 `NOTE-01` 的实质关切已可复算闭合。

## 更正后的观察项清单

`O-1`（授权锚点措辞）、`O-2`（note 未点名，锚点更正为 `NOTE-01`）、`O-4`（r9/r10 review packet 入库）、`O-5`（observations JSON 就地修订标记）；**`O-3` 撤回**。全部仍为**非阻断观察**，不构成 r10 候选的 Review 条件。

## 最终 decision 与阻断状态

- **最终 decision：仍为 `APPROVED`**（针对 exact HEAD `92dc7361…` / tree `73511f7b…`）。两处更正均不触及条件闭合的实质判定：**C-01..C-06 全部 CLOSED** 的结论不变；本轮独立复算的数字（7 路径集合、根 manifest 203/203 与其 digest、20/14/6 计数、12/12 `mapping_domain`、config canonical 2609 B / `9af44513…`、20 pins 0 drift）不受影响。
- **未产生新的阻断**：P0 / P1 / P2 / P3 = **0 / 0 / 0 / 0**。
- 状态分离不变：① process-isolation 方案/设计 Review = 前序已通过（本轮不重审）；② 本 r10 文档条件闭合 Review = **APPROVED**；③ Smoke admission = **`NOT_ADMITTED`**（本 erratum 不构成 admission）；④ Build Gate = **`BLOCKED`**、build = `NOT_AUTHORIZED / NOT_RUN`、**Hard Build Barrier 有效未解除**；⑤ 产品验收与 AC1–AC7 = **`BLOCKED / NOT_RUN`**，无 AC 通过。
