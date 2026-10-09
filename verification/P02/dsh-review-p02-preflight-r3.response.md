# P02 非提权宿主 Preflight R3 exact-head Review（独立非作者 Reviewer 报告）

## 1. Decision

**`APPROVED`** — N-01 / N-02 / N-03 全部闭合；该 documentation/evidence-only 修复可由 Codex 集成。
**P0 / P1 / P2 / P3 = `0 / 0 / 0 / 3`**（3 项均为新增非阻断 P3，无需集成前闭合）。

## 2. 审查对象与 checkout 校验（本人独立执行）

| 项 | 固定值 | 实测 | 结论 |
|---|---|---|---|
| HEAD | `c36435aec5042143b816c01aa6da2ff3e80ba154` | 同 | ✅ |
| tree | `cba4d7f25bf8d68827b41449d0cfbde62539fd7f` | 同 | ✅ |
| parent | `9a96b5ae0695f56da9f19bfaf0771adda7999ea7` | 同 | ✅ |
| task base / live main | `6855c113e6a44320d9555777900cfb78a218d383` | `merge-base` 同 | ✅ |
| 工作区洁净 | clean | `git status --porcelain -uall`=0，stash=0 | ✅ |

branch=`codex/P02-process-isolation`，git-common-dir=`G:/CODEX/New Manga/.git`，live root=`main@6855c113`。审查全程只读；未修改/暂存/提交/删除任何文件，未创建 stash。

**35 条 base-relative 变更路径**：4×`doc/**`（M）+ 31×`verification/P02/**`（A）；rename=0、delete=0、`+701/-5`。落在 `doc/` 与 `verification/P02/` 之外=0；匹配 `package.json / Cargo / *.ts / *.tsx / *.py / *.rs / *.toml / *.lock / contracts/ / schema / tests/` 的路径=**0** → 确认无产品源码、测试、契约、IPC、Schema、依赖、用户数据或 Owner allowlist 改动。

## 3. 独立复算（全部在 exact target `c36435ae` 现场执行）

| 检查 | 作者记录口径 | 我的独立结果 |
|---|---|---|
| route validator | EXIT=0 / 196 nodes（@`9a96b5ae`） | **EXIT=0，196 nodes 全 PASS，`live HEAD=c36435ae`**（fresh exact-target） |
| `git diff --check 6855c113..HEAD` | EXIT=0 | **EXIT=0** |
| Markdown 相对链接 | 19 files / 772 targets / 10 基线已缺 / 0 新增缺失（@`9a96b5ae`） | **20 files / 772 targets / 10 base-existing missing / 0 new missing** |
| root protected manifest | 203/203，mismatch 0，staged=0 | **manifest 203 vs live 203；missing/extra/status/kind/size/sha256 = 0/0/0/0/0；staged=0** |
| canonical entries SHA-256 | `3a54fa97…0e2`（36,985 B） | 按 manifest 自带 recipe 逐字复跑：**36,985 bytes / `3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`** |
| 状态分布 | `4×" M" + 199×"??"` | **manifest 与 live 均为 4×`" M"` + 199×`"??"`** |
| candidate ∩ root dirty | overlap=0 | **overlap=0**（35 候选路径） |
| 路径 union 包含性 | 24/26 口径已记 | **80cf5651(24) / 7d8951c2(26) / c36435ae(35) 三处 outside-union 均为 0** |

**commit / tree / parent / 路径数逐项核对**（全部与记录一致）：`561f4105`=14、`cd3e86d6`=22、`80cf5651`=24（tree `234cd26f…`）、`b14c7d27`=26、`7d8951c2`=26（tree `1340c528…`，parent `b14c7d27`）、`6ffba27b`=33（tree `313f8d8c…`）、`ed0fb8a2`=34、`6f47d481`=34（tree `5f9d94b9…`，parent `ed0fb8a2`）、`9a96b5ae`=34（tree `d6e1bab4…`）、`c36435ae`=35。

**N-01 关键事实独立复核**：以 `scope-frozen.md:6` 的 R1 freeze 清单（13 路径）减去 r7 逐条枚举（实测 **27 条**，与记录一致），差集**恰为**记录所列 6 条（`inputs-r1.tsv`、`wsb-version-r1.{stdout,stderr}.txt`、`wsb-list-raw-r1.{stdout,stderr}.txt`、`non-elevated-preflight-start.md`），且 6 条在 `561f4105`→`7d8951c2` 区间 **blob 逐字节相同**（逐一 `rev-parse` 比对）。r7 的 27 条中有 7 条在 `7d8951c2` 尚不存在（r2-review checkpoint + 6 件 r2 packet）→ 20+6=26 与受审 HEAD 路径数自洽。

**时间戳 / 元数据**：r3-start `00:49:36`（commit `00:49:48`）、r2-review `00:47:07`（commit `00:47:25`）、r3-delivery `00:53:45`（commit `00:53:48`）；r2 session `completed_at=2026-10-09T16:47:07.737Z` = `00:47:07 +08`，与 r2-review 时间戳精确一致；`reviewed_head=7d8951c2` / `reviewed_tree=1340c528…` / `reviewed_parent=b14c7d27` / `task_base=6855c113` 全部核对通过；`exit_code=0`、`mount_exit_code=0`、`stderr_bytes=0`、`raw_jsonl_committed=false`（符合 r7:101）。

**PASS 用词审计**：新增行含 `PASS` 共 37 行，逐条确认仅限「宿主只读实测项」（root manifest、非提权判定、WSB identity/version/list、clone 不存在、架构/虚拟化、资源阈值、HostFolder 存在性、20 文件 pins）、历史 Stage A Gate 既有陈述、以及 Reviewer 对「无虚假 PASS」的声明。`source commit pins=MATCH_PREDICTED / CHECKOUT_NOT_RUN` 未被改写为 PASS。**无任何 PASS 暗示 Windows Feature / Smoke / Build / AC 成功。**

## 4. N-01 / N-02 / N-03 Disposition

| ID | 来源与要求 | 判定 | 独立依据 |
|---|---|---|---|
| **N-01**（R2 P3）允许集口径与 6 条延续路径 | **CLOSED** | `codex-preflight-r2-validation.md:5/:30` 明确写为「original R1 frozen scope ∪ r7」、列明 6 条、锚定 `80cf5651`=24 与 `7d8951c2`=26；`codex-checkpoint-p02-preflight-r2-review.md:7`、`codex-checkpoint-p02-preflight-r3-start.md:8`、`codex-checkpoint-p02-preflight-r3-delivery.md:6`、`codex-checkpoint-p02-preflight-r2-delivery.md:5/:+Post-review` 同步登记。审计轨迹与 union 包含性均独立复现（见 §3）。 |
| **N-02**（R2 P3）exact-head 验证留痕 | **CLOSED** | `codex-checkpoint-p02-preflight-r2-review.md:8` 登记 DSH 在 `7d8951c2` 的独立复跑（route EXIT=0/196、diff EXIT=0、15 files/766 targets/10/0、root 203/203、overlap=0），与 `dsh-review-p02-preflight-r2.response.md:35/:22` 原文一致；`codex-preflight-r2-validation.md:31` 二次登记并链接；`:34-41` 另记 author-side R3 final candidate（`6f47d481`）复跑。上述数字我全部复算通过。 |
| **N-03**（R2 P3）start checkpoint 时间线 | **CLOSED** | `non-elevated-preflight-start.md:3` 保留原 `2026-10-09 15:58 UTC / 23:58 +08` 与 `PREFLIGHT_SCOPE_FROZEN / READY_TO_RUN`；`:10` 完成句改标为「交付时追记：在该范围冻结 checkpoint 之后…」。R3 diff 证实**仅该一行**被改写（另仅补文件尾 LF），采集窗口与冻结时间先后自洽。 |

**结论：N-01、N-02、N-03 均已完全且准确闭合。** 该 documentation/evidence 修复**可以集成**。

## 5. Findings

| ID | 严重度 | 路径:行 | 影响 | 要求闭合方式 |
|---|---|---|---|---|
| **R3-N-01** | **P3**（非阻断） | `doc/REBASELINE_PLAN.md:5`、`doc/tasks/P02.md:87` | 两处仍以现在进行时描述该修复（「当前按冻结 r8 scope 修复非阻断 N-01..N-03」、「当前修复并准备 R3 exact-head Review」），而同一 exact target tree 内 `codex-checkpoint-p02-preflight-r3-delivery.md:3` 已声明 `R3_REPAIR_FIXED / READY_FOR_EXACT_HEAD_REVIEW`。读者可能误以为修复仍在编辑中、review target 尚未固定。这 4 份 doc 最后触碰于 `ed0fb8a2`（R3 start，00:49:48），未在 `6f47d481`/`9a96b5ae` 交付时刷新。 | 可在下一次合法文档触碰或集成/post-FF 时改为「修复已固定于 `6f47d481` / `9a96b5ae`；待 R3 exact-head Review」。**不阻断集成。** |
| **R3-N-02** | **P3**（非阻断） | `doc/STATUS.md:3`、`doc/REBASELINE_PLAN.md:5`、`doc/00_INDEX.md:3` | 三份当前状态文档的恢复指针仍指向 `codex-checkpoint-p02-preflight-r2-start.md`（该 checkpoint 自述 `R2_SCOPE_FROZEN / REPAIR_IN_PROGRESS`，落后一代）；新 `r3-start`/`r3-delivery` 仅被 `scope-delta` r8（`:117`）引用，无法从当前状态文档直接抵达。指针标签本身未写错，属导航滞后。 | 下次触碰时加/前移一个指向 `codex-checkpoint-p02-preflight-r3-start.md`（或 r3-delivery）的恢复链接。**不阻断集成。** |
| **R3-N-03** | **P3**（非阻断） | `verification/P02/codex-preflight-r2-validation.md:40` | r8 §R3 acceptance 明确要求核验「exact candidate path set 在 R1 freeze ∪ r7/r8 允许集内」；作者侧仅对 24/26 快照记有 union 包含性（`:5`），R3 的 34-path 候选记录只写了路径数、root manifest 与 overlap，未重述 union 包含性。**事实成立**（我已独立确认 `80cf5651`/`7d8951c2`/`c36435ae` 三处 outside-union=0，`9a96b5ae` 的 34 集为其子集）。纯留痕完整性，无越界路径。 | 可选：补一句「34 paths ⊆ R1 freeze ∪ r7 ∪ r8」。**不阻断集成。** |

**非 finding 备注（不计数）**：`codex-preflight-r2-validation.md` 在同一 r2 命名文件内叠加三代记录（r2 快照 / r2 exact-head 与 N-01..N-03 / R3 candidate），且 `:26→:27`、`:33→:34` 两处标题前缺空行 —— CommonMark 下标题仍正确解析，属排版可读性；`codex-scratch-build-preflight-r1.md` 的 `PASS` 仅覆盖实测宿主项，source pins 已如实降级；`non-elevated-preflight-start.md` 仅新增文件尾 LF，属良性空白规范化，`git diff --check` 通过。

## 6. Gate 边界（保持，未由本 Review 改写）

Windows Sandbox Feature=`UNKNOWN`（本轮未查询）；full preflight=`BLOCKED / INCOMPLETE`；Smoke admission=`NOT_ADMITTED`；Smoke=`NOT_AUTHORIZED / NOT_RUN`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；P02 AC1–AC7=`BLOCKED / NOT_RUN`；Hard Build Barrier 有效。**本人本轮未运行**：Windows Feature 查询/变更、提权、`wsb`、Sandbox、clone、Smoke、Build、产品 runner/test、GUI、WebView（仅执行只读 Git/Python 文档校验）。

## 7. 集成建议

1. **可集成**：R3 documentation/evidence 修复满足 N-01..N-03 闭合与 r8 §R3 acceptance 的实质要求，建议 Codex（Integrator）对 exact reviewed HEAD `c36435ae` 执行本地 fast-forward。
2. **注意 review 包会改变 HEAD**：本报告的 R3 review packet（r8 `:116` 授权新增的 `verification/P02/dsh-review-p02-preflight-r3.*` 6 件）会形成新 commit，使 exact HEAD 偏离 `c36435ae`。若先行提交该包，则须对新的 exact HEAD 重新执行 post-FF 验证（route validator、`git diff --check`、目标 HEAD/tree/parent、root 203/203 manifest、路径交集）后再 FF；若以 `c36435ae` 直接 FF，则 review 包作为后续 commit 并同样补跑 post-FF 校验。
3. **post-FF 复跑基线值**（供 Integrator 对照本人本轮实测）：route EXIT=0/196 nodes；diff check EXIT=0；changed-Markdown 20 files/772 targets/10 base-existing missing/0 new；root manifest 203/203、mismatch 0/0/0/0/0、staged=0、canonical `3a54fa97…0e2`；candidate∩root=0；union outside=0。
4. R3-N-01/N-02/N-03 三项 P3 可在下一次合法文档触碰（集成时或 post-FF 状态刷新）一并登记，不影响本次集成。

**最终决定：`APPROVED`（P0/P1/P2/P3 = 0/0/0/3），N-01、N-02、N-03 全部闭合，该 documentation/evidence 修复可以集成。**