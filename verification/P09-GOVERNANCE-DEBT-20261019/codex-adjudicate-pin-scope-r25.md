# Pin 失配 92 项范围裁定（r25）

日期：2026-10-20  
裁定者：Codex（Lead / Architect / Integrator）  
对象：`GOV-PIN-LINEAGE-1` proposed Task 及其扫描发现  
性质：范围与语义裁定；本文件不释放 Task，也不授权代码或历史 Task 修改

## 1. 结论摘要

1. **核心缺陷在检查器的校验对象，不在 63 个历史 pin。** `Canonical Evidence` pin 是 `(path, commit, sha256)` 三元组；历史证据应以该 commit 中该路径的 Git blob 为准。当前 `check.ps1` 对工作区文件计算 hash 并与 pin 比较，忽略 pin commit，因而把后续合法演进误报为 `Evidence SHA-256 不匹配`。
2. **不逐项改 63 个 pin，也不把 lineage 注记散写入 28 个历史 Task。** 原 pin 保持原样。将 `GOV-PIN-LINEAGE-1` 重定范围为：修正检查器的历史 blob 校验语义、用 63 项清单验证分类/结果，并在该 Task 的 evidence 目录保留一份完整、可追溯的 lineage registry。registry 按 63 条逐项记录来源 Task、evidence_id、path、pinned commit、pinned SHA、该 commit 的 blob SHA、后续相关提交、当前工作区状态及结论。Task 文件无需复制重复说明。
3. **6 项 `LINE_ENDING` 不需重算，也不需再改 `.gitattributes`。** 如所报逐字节诊断真实可复现，则工作区 CRLF 与 pin commit 的 LF blob 是同一文本的检出转换；检查 pinned blob 后原 pin 应匹配。把工作区 hash 写回 pin 会把表示转换当成新证据，且破坏历史记录。纳入 checker 回归验证，不另开 EOL follow-up。
4. **23 项 `MISSING_FILE` 暂不归因，也不纳入修复范围。** inventory 对这些行的 `exists_at_pinned_commit` 为 `null`，所以现有清单并未证明路径写错、证据在仓外或 pin commit 中存在。该 Task 文件在当前 checkout 确实存在，ID 与 evidence path 一致；此事实本身不能证明证据目录的历史位置。先独立解析每条 pin 的 Git commit/blob、Task 声明路径、仓库路径和 workspace 归档/引用记录，再决定是否另立诊断 Task。不得猜测或改写路径。
5. **采用检查器修复，不采用“所有历史 Task 永久红”选项，也不批量改 63 个 Task。** 这是对报告核心问题的明确裁定。按 pin commit 验 blob 可从一个校验路径修正全局语义；registry 负责让本次 63 项调查可审计。不得引入依赖 Task 散文注记的隐式豁免。

## 2. 依据与边界

本裁定读取并交叉核对：`pin-inventory-and-scope.md`、`pin-inventory.json`、`doc/tasks/GOV-PIN-LINEAGE-1.md`、`doc/tasks/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION.md`、`tools/governance/check.ps1`、`doc/09_COLLABORATION.md` §4.1、当前 `STATUS` / `REBASELINE_PLAN`，以及本轮可见的 r20–r24 裁定材料。扫描报告给出的计数为 313 个 Task、1214 个带 commit + SHA 的 pin、92 个当前磁盘不匹配项；三类分别为 63 `TIME_BASED`、6 `LINE_ENDING`、23 `MISSING_FILE`。这些是扫描结果，不等于 92 个无效历史证据。

`check.ps1` 在约 313–315 行解析 Canonical Evidence 表、验证路径/commit/SHA 格式并对 `Resolve-LocalPath` 得到的当前文件执行 `Get-FileHash`。该 hash 与表中 SHA 不等时无条件 `Add-Error 'Evidence SHA-256 不匹配'`。该分支没有读取 `$commit` 对应的 Git blob。故其当前检查实际回答“工作区此路径的现时字节是否等于 pin”，不是“pin 所声明的提交是否包含该证据字节”。对历史 pin，这不是 §4.1 所表达的核验。

r20 §2.2 保留原 pin、不覆盖 SHA 的历史保真原则仍成立；本次修正的是它依赖的 lineage 处理方式：无需在 28 个 Task 文件中重复登记每次后续演进，统一 registry 即可提供集中索引与审计链。r21–r24 提出的 7 项是未完成扫描时的估算，不再作为数量边界。新的 63 项仍须逐条核对 pinned commit 的 blob；不能只信分类器的 `TIME_BASED` 标签。

## 3. 3.1 范围、产物与预算

### 范围裁定

`GOV-PIN-LINEAGE-1` 的范围不是“63 处逐 Task 文案补注”，也不是“92 项全部修复”。范围调整为：

- 对清单内 63 个 `TIME_BASED` pin 验证 pinned commit 中路径存在且 blob SHA 与原 SHA 相符；检查后续提交记录和当前工作区状态，生成单一 `pin-lineage-registry`，保留每条可审计事实。不得覆盖原 pin。
- 对 6 个 `LINE_ENDING` pin 验证 pinned blob SHA。另以 LF normalization 复核所报诊断作为解释性材料；不按工作区 CRLF hash 重钉，不在本 Task 改 `.gitattributes`。
- 修正 checker：对有有效 Git commit 的仓库内 pin，以 `git cat-file` / 等效安全只读接口取得 `commit:path` blob 并计算 SHA-256。原 SHA 与 blob 相符时，该历史 pin 通过；工作区文件缺失或 hash 不同应报告单独的工作区漂移诊断（warning/info），不得将其冒充 pinned evidence 不匹配。若 commit 不存在、路径不在该 commit、blob 取出失败、或 blob SHA 与 pin 不符，继续报 error。对仓外/原始输入类 pin 按其明确来源规则校验，不能静默套用仓库 blob 语义。
- 回归覆盖：上述 69 条已归类项（63 + 6），至少包括 blob 匹配但工作区修改、LF/CRLF 转换、commit 缺失、commit 中路径缺失、pin SHA 与 blob 不符、原有工作区一致情形；再运行既有治理 checker 夹具，证明 v3 AC、manifest 等无关门禁不被绕过。
- 对 23 个 `MISSING_FILE` 只记录为排除项及待诊断问题，不修改其路径、pin、Task、证据或 workspace 文件。初步诊断至少判明 pin commit 是否存在、`commit:path` 是否存在及其 blob hash；仓外位置只有在找到可核实来源记录时才可认定。

### 单一 registry 的规模

63 条 registry 可采用 JSON/CSV 数据文件加一页简短说明，建议作为 `verification/GOV-PIN-LINEAGE-1/pin-lineage-registry.json` 与同目录摘要。若每条保留约 8–12 个短字段，JSON 预计约 20–40 KB；摘要约 2–5 KB。实际大小以交付物为准。28 个 Task 文件预计 **0 字节增量**，因为不逐个追加重复段落；`GOV-PIN-LINEAGE-1.md` 本身更新 AC/范围，增量约 2–4 KB；`check.ps1` 增量预计约 1–3 KB，需按真实 diff 核定。Plan 与 STATUS 的 Task 节点只需短状态说明，预计合计小于 1 KB；不应复制 63 条明细到权威状态文件。

这些只是规划估算，不是行数或文件体积预算事实。`GOV-PLAN-BUDGET-1` 已完成，仍须遵循它记录的预算治理：释放前以真实 diff 更新计划估算；交付后用实际统计复核，若超过冻结预算先停下并提交变更裁定。不得因本裁定直接改 Plan/STATUS；Task 仍 proposed，需完成依赖、状态及生命周期 Gate 后由 Codex另行冻结/释放。

## 4. 3.2 LINE_ENDING 裁定

6 项并入 `GOV-PIN-LINEAGE-1` 的 checker 验证样本，不作为重算或 EOL 文件改动工作。报告中的 6 组字节数与 LF normalization 相同是有力分类证据，但须在 Task 执行时对 pin commit 中原 blob 与工作区文件重新验证，并确认 inventory 中 pinned SHA 对应哪一方字节。若 pinned blob SHA 不等于原 SHA，则该项分类不成立，应作为异常逐项查因，不能强行按 EOL 结案。

`GOV-EOL-PIN-1` 已 done；不应在已 done Task 内追加新工作，也不需要为这 6 项再建单独 FU。`.gitattributes` 只影响检出/归一化行为，并不能替代对历史 pin 所指 blob 的核验。checker 改为 blob 校验后，历史 LF pin 在 CRLF 工作区也有稳定解释。此结论不授权本 Task 修改 `.gitattributes`。

## 5. 3.3 MISSING_FILE 诊断裁定

现有 Task 文件路径为 `doc/tasks/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION.md`；frontmatter 的 `evidence_dir` 是 `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION`。23 条清单路径都以该目录为前缀，文件名包括 `zcode-owner-preflight-r1.json` 等。报告给出的 `exists_at_pinned_commit: null` 表示尚无该检查结果；`later_commits: []` 也不能证明未在 workspace 中保存或 pin commit 中不存在。

单独诊断时按每行记录：Task 声明路径、pin commit 对象是否可解析、commit 中路径是否存在、blob SHA 与 pin SHA 是否相等、当前仓库路径状态、Task Handoff/Canonical Evidence/历史 manifest 的交叉引用、可能的 workspace 来源及其来源证据。只有来源链足以确认时才能区分“路径错前缀”“仓外保留”“历史对象缺失”或“pin 本身错误”。

此诊断是单独发现，不是 `GOV-PIN-LINEAGE-1` 的修复范围；不回写该 P02 Task，不重建证据、不从 workspace 复制、不搬移/删除文件。若路径在 pin commit 中存在而只是工作区当前缺失，新的 checker 应区分“历史 pin 仍有效”和“本地检出缺文件”；若 pin commit 中也没有路径，则维持 error 并交由独立诊断决定是否立项。当前不得宣称历史遗留可忽略，也不得宣称 23 项已证实为路径整体失效。

## 6. 3.4 `GOV-PIN-LINEAGE-1` Acceptance Criteria 替换文本

以下文本建议整体替换原 Task 的 Acceptance Criteria；在 Codex 正式更新 Task、Plan/STATUS 和冻结范围前，它是本裁定的释放建议，不是对 Task 文件的直接修改。

```markdown
- [ ] **AC1 — 冻结并核验 pin 清单**：以 `verification/GOV-PIN-LINEAGE-1/pin-inventory.json` 为输入，逐条核验 63 个 `TIME_BASED` 与 6 个 `LINE_ENDING` pin 的 `pinned_commit:path` Git blob。记录 Task、evidence_id、path、commit、原 pinned SHA、blob SHA、后续相关提交、工作区状态和逐项结论至唯一 lineage registry。原 evidence_id、commit、SHA 均不得覆盖。若任一条与分类不符，保留原始行并记录重新分类依据，不静默改清单。
- [ ] **AC2 — 修正历史 pin 校验语义**：`tools/governance/check.ps1` 对有有效 Git commit 的仓库内 pin，以该 commit 中该路径的 blob SHA-256 与 pinned SHA 比较；不得用当前工作区 SHA 代替历史 blob SHA。pin commit/blob 缺失或 blob SHA 不符仍报 error。工作区文件缺失或与 pinned blob 不同须用独立 warning/info 诊断表达，不得误报为 `Evidence SHA-256 不匹配`。仓外/原始输入按既有明确规则校验，不因本改动获得豁免。
- [ ] **AC3 — 处理 6 项行尾样本**：对 6 个 `LINE_ENDING` pin 验证 pinned blob SHA 与原 SHA 相符，并复核 LF normalization 诊断；不重算或覆盖任何 pin，不修改 `.gitattributes`。无法复现的项作为未解释异常报告，不得计为通过。
- [ ] **AC4 — 保留 23 项诊断边界**：逐项记录 `MISSING_FILE` 的 commit 可解析性、commit 中路径/blob 状态及 hash 对照，并核对 Task/Handoff/manifest 中的来源引用；只有来源链支持时才判为前缀错误或仓外证据。不得改写 P02 Task、重建/复制/移动/删除证据，不把未查明项算作已解决。
- [ ] **AC5 — 回归保护既有门禁**：为历史 blob 匹配但工作区修改、LF/CRLF、commit 缺失、commit 路径缺失、blob hash 不符、工作区与 pin 一致等情况建立确定性用例；运行 checker 自身既有夹具和相关 Task-scoped 检查，证明 v3 AC gate、Resource Manifest 与路径/状态错误仍按原规则失败或通过。记录命令、环境、stdout/stderr、exit code 和完整结果；不得仅用全仓 PASS 代替分类用例。
- [ ] **AC6 — 交付 registry 与独立 Review**：提交单一机器可读 lineage registry 和摘要、最小 checker diff、测试证据、Handoff；registry 覆盖 63+6 条，保留逐项来源和结论。由未编写该 checker/registry 的 Reviewer 对固定 delivery head 独立核对原 pin 未被重算、分类可复现、checker 不存在绕过路径。Codex 完成集成后验证与资源 closeout 前，Task 不得标记 `done`。
```

AC 冻结时还要为 AC5 列出具体既有夹具和受影响 Task 清单，并遵循项目 Task 模板。不要保留原 AC4 的“a/b/c 三选一”：此裁定已选择按 Git blob 验证，并要求区分工作区漂移。

## 7. 3.5 Owner / Reviewer 裁定

**Antigravity 可用性：当前证据不足以宣告可用或不可用。** 当前 `STATUS` 显示 ZCode 遇 429 限流；本 checkout 在 `antigravity/P09-AC3-DELETE-HARDEN-1`，说明 Antigravity 近期承担过工作，但不能推断其当前负载、会话是否仍运行或能否承接。释放前应按协作协议核验 Agent 当前状态、工作量和能力。项目故障转移顺序是 **ZCode → Antigravity**；Qoder 已退出。若 AG 确认不可用，依序评估 ZCode；若两者均不可用，则保持 proposed，不分配 Owner。不得跳到 Qoder 或仅凭旧建议假定 AG 已认领。

**DSH 不宜作为本 Task 的唯一 Reviewer。** 清单由 DSH 制作；虽然扫描并不等同于 checker 实现，DSH 审查自己的分类、阈值和证据挑选仍存在自我复核风险。此前由 DSH 承担多个治理 Owner 也是负载轮换理由。优先建议：Antigravity 做 Owner，ZCode 做独立 Reviewer（各自确认可用，Reviewer 不参与实现）；但若工作负载或角色分工不合适，Codex 应在释放时指定一名未参与清单生成和 checker 实现的合格 reviewer，并书面说明独立性。不要让同一 agent 同时 Owner/Reviewer。若无法找到独立 Reviewer，Task 不释放。DSH 可提供扫描方法说明或作为咨询者，其结果仍须独立抽查/复算。

## 8. 3.6 是否“大扫除”

不对 1214 个 pin 做无差别重算或全仓改写。92 是检查器按“当前磁盘 hash 对原 pin”得到的差异集合，不是已证实的 92 个损坏 pin。63 项 TIME_BASED 在 pinned commit blob 校验相符时属于健康的历史 pin；改写 63 份 Task 会制造无必要的维护噪音，甚至把历史语义伪装成当前文件语义。正确主修复是 checker 校验 `commit:path` blob，辅以单份 registry 记录清单结论。

该修复也不能把所有工作区差异吞掉：区分两件事——**历史 pin 有效性**（commit 中 blob 与 SHA 是否一致）和**工作区可用性/现态**（当前路径是否存在、是否仍与历史字节相同）。第一项决定历史 pin 是否有效；第二项可作为独立诊断信息交给 Review，不得反过来篡改 pin。commit 缺失、commit 中路径缺失或 blob SHA 不匹配均应继续 FAIL。对仓外来源继续按其声明的 source/hash 校验。

因此答案是：**改检查器校验语义（1 个实现点）+ 建一份 63 项 lineage registry；不改 63 个 Task，不将历史 Task 永久标红。** 6 项作为回归样本一起解决其“工作区转换造成误报”的同类校验问题；23 项留待诊断。

## 9. 工作状态与写入记录

本轮只创建本文件。未调用 `coordinator-lease.py`，未执行任何 Git 写命令，未修改 `doc/**`、`tools/**`、`src/**`、`tests/**`、`.gitattributes`、`verification/GOV-PIN-LINEAGE-1/` 或任何既有文件。

写入前：`git status --porcelain` 1237 行，SHA-256（UTF-8，LF join 并含末尾 LF）为 `bfd3153657299ab8ac4c809cb7784778338320cd6e07a5d6b0949e118c539ba7`；目标文件不存在。此前 dirty/untracked 内容均属既有工作区状态。

写入后：`git status --porcelain` 为 1238 行，状态文本 SHA-256（UTF-8，LF join 并含末尾 LF）为 `b4c9a0f5a1d6832c199552888e8b906fa30e49f1b1f4726b67b6578716797686`。与写入前逐项对比，唯一新增项为 `?? verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-pin-scope-r25.md`；原 1237 行全部保留，原 `.qoder-credits/report.json` 修改仍在。

## 10. 下一步建议

当前 `GOV-P15-MANIFEST-1` Task 与 REBASELINE_PLAN 均为 `done`（integration_commit `7b1cb6a78346b42bb7c23de9bf924117b7c68a21`），故 r24 中“待 closeout”的前置事项已被当前权威状态取代。推荐 Codex 依据本裁定更新 `GOV-PIN-LINEAGE-1` 的范围与 AC，核实 `GOV-SOURCE-RECORDS-1` 依赖、checker 回归清单、真实预算和独立 Reviewer 可用性，再冻结 base/branch/worktree/allowed paths 并决定是否释放。该文件本身不释放 Task，也不授权立即实施。


