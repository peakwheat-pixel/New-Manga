---
task_id: FEA-15-PIN-EOL-GOV-1
reviewer: ZCode CLI (`sess_1ff7ce49-fa46-4cb8-b7a7-d2efcb347fdc`)
reviewer_kind: agent
author: Codex
base_commit: 4173961dfe1b65256cb06d7628cc813b0603caa3
reviewed_head: 996f9768985ee121767bd750d24b1cdfe74dd186
decision: approved
---

# Review：FEA-15-PIN-EOL-GOV-1

> 本报告依据 ZCode 独立只读 CLI 会话的完整响应整理；reviewer、reviewed head、decision 与 finding 保持原结论。ZCode session：`sess_1ff7ce49-fa46-4cb8-b7a7-d2efcb347fdc`；未复用释放裁决会话 `sess_abdb4288-4a4f-49c1-8097-6edbb6e3866f`，未参与实现或返修。

## 范围与依据

- 固定审查范围：`4173961dfe1b65256cb06d7628cc813b0603caa3` → `996f9768985ee121767bd750d24b1cdfe74dd186`。ZCode 报告实测 10 commits、24 files、`+144,778/-10`；提交涉及路径均在 Task `allowed_paths` 内。
- 当前 pinbackfill HEAD `96b79ca356a43e00f8a55d47b4a89771e377e022` 仅用于读取 Task 生命周期与证据指针，不计入 AC1–AC3 交付 head。
- 依据：Task 卡、`doc/09_COLLABORATION.md` §4/§4.4/§6、`doc/templates/REVIEW.md`、`verification/FEA-15-PIN-EOL-GOV-1/README.md`、FEA-15-ACCEPT-1 r1/r2 Review 与 DIAG-ACL-1 释放裁决。

## Architecture

**PASS。** ZCode 逐提交检查触及范围：无 `.gitattributes`、governance checker / `verify_pins` / `task_ledger` 语义、冻结契约、源代码、Schema、依赖的修改；无历史证据删除或改写、无 push。新脚本只在当前 Task 的 `verification/FEA-15-PIN-EOL-GOV-1/` 下。

18 条 FROZEN 记录与 `verify_pins.ps1` 的 18 项映射未被改动。ZCode 读 `check.ps1` r194 后确认当前双基准语义为：先比较工作区 SHA；不匹配时再比较记录 commit 的 blob SHA；任一匹配即通过。跨 checkout 主 worktree 的改动集合与 Task 自有文档和证据相符；未触碰用户源文件、未 renormalize、未清理或迁移资源。

## Verification

**PASS（附本人门禁复跑 NOT_RUN）。**

| 项 | 结果与依据 |
|---|---|
| AC1 全集 | **支持 MET**。清单总数 5,350 行：584 Task cards、5,332 Task rows、18 frozen records；basis 分类合计自洽（BLOB 327、WORKTREE 3,451、MIXED 999、INCONSISTENT 160、UNPINNED 293、UNRESOLVED_COMMIT 68、EXTERNAL_UNAVAILABLE 47、MISSING 3、COMPOSITE_PATH 2）。584 卡由排除 README 索引后的 tracked Task 路径独立复算。 |
| AC2 checkout 矩阵 | **支持 MET**。4 种样本 × 3 个 checkout = 12 条观察，均有 HEAD、时点、命令 EXIT、pin 与 head-blob 结果；head-blob 12/12 PASS，pin 结果 7 PASS / 5 FAIL，与 README/checkpoint 一致。失败值保留为 FAIL。 |
| AC3 策略分析 | **支持 MET**。分析区分事实、推论、未知/反证、4 个未选候选项和暂停门槛；覆盖 FEA-08、r194、renormalize 与历史 pin 处置，没有选择或实施策略。 |
| Canonical Evidence / manifest | ZCode 复算工作区哈希均与卡面匹配，提交包含性也成立；manifest 与 Handoff 哈希匹配。工作区和 blob 口径的差异见 R-001。 |
| Review 自行执行的检查 | `git diff` 范围检查、SHA-256 双口径复算、Task 卡数与 matrix 结构复算、r194 语义核对、18 条 frozen 文件 / 映射核对、gate 日志 HEAD/EXIT 记录核对：ZCode 均报告 PASS。 |
| 门禁由 ZCode 亲自复跑 | **NOT_RUN**。ZCode `--mode plan` 环境拦截 `pwsh` 与带参数 `python` 命令；它没有声称亲自运行 `check.ps1`、`verify_pins.ps1` 或 API inventory。其判断依据是已提交日志和独立结构核查。 |
| 产品测试、Linux fresh clone、renormalize simulation | **NOT_RUN**，符合 Task 只读范围；不得将其记作 PASS。 |

调用方后续在 HEAD `96b79ca356a43e00f8a55d47b4a89771e377e022` 实际复跑四项门禁，全部 EXIT 0；该结果不是 ZCode Review 的亲跑结果。复跑详情在 Task closeout 和后续证据中记录。

## Findings

| ID | 级别 | 位置 | 触发与影响 | 建议 | 状态 |
|---|---|---|---|---|---|
| R-001 | P2 | Task Canonical Evidence 与 Resource Manifest 的 SHA-256 pin | 当前新增 pin 未明示字节基准。独立复算：`pin-inventory.json` 工作区 `1b369d621867d6a55aa866b22a2ea7160e188b2dd89efb1e69521a7a14c38ab5`、blob `214157a769cc5b7ac5c93084c4f0598fc8af086f1c859975ef803afd33efed18`；`checkout-matrix.json` 工作区 `e826f597cf606f92be6307f5ad8a4c2e3695892edb45e04a93e81bea19f61e6a`、blob `e1ce420139c9e3fe9adff885de9128f77a8ec1e59af45e2bc881f21944b81f9e`；`gate-final.log` 工作区 `3f7869327f6713693af95fbc95e57699ff1f579b2f4881dcca314322d4c4aa45`、blob `0223770509f371ed0c352ce1041b167f9829cc5c41695098f20c5fe96e9337b6`；`resource-manifest.json` 工作区 `fd2f4aebf0099563a82a43dcfa976678772d63b4256843e086c2a6e41e125820`、blob `c615b7a16c8310bcbac3aede482e23aa458bf91af176560fd2565b0f7fb17c8d`。四组在 LF/blob 检出下不等于工作区 pin；`candidate-policy-analysis.md` 工作区与 blob 同为 `53f7f39eba91649d52a448fabf5ed678ca463d437a2bba7aa5e8990ccc96c05d`。现行 r194 双基准仍接受这些 pin，Task 未要求改为 blob 基准，故不阻断；但与 AC3 候选 1「新条目声明基准」存在治理自洽缺口。 | 由集成裁决接受为非阻断遗留，并纳入后续 pin 口径裁定；无需扩展本只读 Task。 | open（不阻断） |

除 R-001 外，在审查范围内未发现问题。首版 README 索引计数错误、初次 gate 失败、长路径恢复、补充 checkout 降级等均保留并如实说明，未改写为 PASS。

## 结论与复审

- **decision: approved**；Architecture PASS、Verification PASS；0 P0 / 0 P1；R-001 为 open P2，不阻断。固定交付 head `996f9768985ee121767bd750d24b1cdfe74dd186` 可进入集成裁决。
- ZCode 提醒：当前 pinbackfill head `96b79ca35…` 的最终门禁未写入仓库；集成前再跑默认与 `-TaskPath` 检查。调用方随后已在该 head 实际复跑，全部四项 EXIT 0。
- 限制：Review 通过不等于 Task 已 `done`；R-001 仍需由集成裁决记录处置，资源 Manifest 仍待 closeout。
