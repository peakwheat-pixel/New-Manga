# GOV-PIN-LINEAGE-1 释放裁定（r26）

- 日期：2026-10-20
- 裁定者：Codex（Lead / Architect / Integrator）
- checkout：`G:\CODEX\New Manga`
- branch：`antigravity/P09-AC3-DELETE-HARDEN-1`
- 当前 HEAD / 建议 `base_commit`：`08935b198094507f8029f5ddfcfc96c33c0cf08e`
- 对象：`doc/tasks/GOV-PIN-LINEAGE-1.md`
- 本文件是本轮唯一写入；本轮不更新 Task、Plan、STATUS 或 checker，也不执行 Git 写命令。

## 裁定摘要

1. **角色选方案 A：DSH Owner，Antigravity Reviewer。** 这不违反 r25 §3.5 的核心意图：DSH 不得成为唯一 Reviewer；由未生成清单、未实现 checker 的 Antigravity 独立审查 registry 分类、实现和固定交付 head，制作者与审查者分离。r25 推荐的「Antigravity Owner + ZCode Reviewer」是优先组合，不是排斥其他可验证独立性的硬性规定；本轮实测 ZCode 没有可用 headless CLI，不能为满足原首选而等待不确定恢复。DSH Owner 的依据是已完成清单和调查；它不得审查自己的 registry/checker。Antigravity 的本轮探测成功证据见 `verification/GOV-PIN-LINEAGE-1/reviewer-availability.md`。Codex 仍做集成 Gate，不替代指定的独立 Review。
2. **准予按本裁定范围释放为 `ready`，但当前仓库状态仍是 `proposed`。** r25 所要求的依赖、回归清单、预算、角色可用性已核实；`GOV-SOURCE-RECORDS-1` 在 REBASELINE_PLAN 中为 `done`，依赖满足。正式改成 `ready` 前，Codex 仍须按 §4 将 DAG / STATUS / Task 元数据登记一致，并建立隔离 linked worktree 后冻结其真实路径。此轮明确授权只允许产出本文件，所以不执行上述元数据和 worktree 操作；不得将本报告描述成 Task 已实际转为 ready。
3. **必须使用隔离 linked worktree。** `check.ps1` 是被全局治理检查使用的基础设施，直接原地改动会同时改变所有 Task 的判断，且当前主 checkout 有大量既存 dirty/untracked 内容。建议以本裁定列出的当前完整 HEAD 为基线，建立 Task 专属 branch/worktree，在该处改动、测试和 Review；Review 固定 delivery head 后由 Codex 集成并做集成后验证。不要在既存主 checkout 原地实施。
4. **19 个 pin-only Task 必须先做基线 blob 核验，再改 checker。** “改后看哪些变绿再解释”顺序不接受。AC2 的“blob 不符仍报 error”是必要保护，但不能证明受影响的 19 个目标原本都是有效历史 pin。先对这 19 个 Task 的每条相关证据 pin，逐一确认 commit 可解析、commit:path 可取、blob SHA 与原 pinned SHA 一致，并保存逐项结果；任一不符或无法解析都先调查并维持 FAIL，不得靠新语义消除。然后实现 checker，做前后错误矩阵；实际转绿集合必须与已核实集合相符，所有其他失败仍按原规则保留。
5. **这不是最后一项可证实的治理债，也不能据此宣布全仓治理债清零。** 已知 23 条 `MISSING_FILE` 仍待单独诊断；83 个 FAIL 中另有非 pin-only 错误，本 Task 不解决这些问题。Plan 仍有 `RUST-ENV-BASELINE-1` 的 proposed 节点；它本身不自动等于治理债。当前证据不足以声称不存在其他未发现债务。完成本 Task 后应以当前 Plan、STATUS 和可复核 Gate 结果做有界盘点，再决定是否关闭治理债线，不扩大到无目标全仓清理。

## 3.1 角色与 r25 §3.5

选择 **A（DSH Owner + Antigravity Reviewer）**，但加上明确的独立性和工作顺序约束：

- DSH 可利用已经完成的 inventory / scope 工作，承担实施、测试、逐项核验与 registry 交付。
- Antigravity 不得参与该 checker / registry 的编写；Review 必须独立读取原始 inventory、pinned blob、实现 diff、确定性夹具和错误矩阵，并绑定固定 `delivery_head`。
- Antigravity Review 至少核验：69 条 `TIME_BASED + LINE_ENDING` blob 结果、19 个 pin-only Task 的前置核验、23 项排除项的诊断边界、工作区漂移诊断与错误语义、六种确定性用例、既有门禁回归。
- DSH 的职责类别偏测试/分析，但没有项目规则禁止其担任 Owner；这里不让 DSH 担任其自身清单的 Reviewer。若实际派发发现 DSH 无法承担 checker 实现，保持 Task 在 `ready` / 未认领状态，由 Codex 重新裁定 Owner，不得把 Reviewer 同时变成 Owner 或以自审替代独立审查。

r25 §3.5 拒绝的是 DSH 成为**唯一 Reviewer**，理由是其制作了分类清单。方案 A 保留了这个拒绝的实质约束，并未与其原意冲突。它没有采用 r25 首选配对，是因为 ZCode 本机不可用；已有 Antigravity 实测能力证据，足以支持由它承担独立 Review。

## 3.2 释放状态、范围与基线

### 是否具备释放条件

依赖、输入清单、具体回归用例、预算和 Reviewer 可用性均已就绪。Plan 已列 `GOV-PIN-LINEAGE-1` 为 `proposed`，其依赖 `GOV-SOURCE-RECORDS-1` 为 `done`。因此技术前置条件满足，裁定**允许释放**。

但本轮只授权写指定裁定文件，不能代替必需的 Plan、STATUS 和 Task 生命周期登记。故结论是“批准按此冻结后转 ready”，不是声称当前 frontmatter 已经 ready。正式释放时还需依协作协议 §4 将状态和允许范围落入权威文件，并以 checker 验证当前指针。

### 冻结建议

- `base_commit`：`08935b198094507f8029f5ddfcfc96c33c0cf08e`。Task 现值 `d124977bf` 已落后于当前 HEAD，不应继续作为新释放基线。
- `branch`：Task 专属实现分支，建议 `dsh/GOV-PIN-LINEAGE-1`；创建后记录实际 branch。
- `worktree`：必须独立 linked worktree，放在 `G:\CODEX\New Manga.workspace\GOV-PIN-LINEAGE-1\worktree` 或按当前 workspace 治理规则确定的 Task 子目录；创建后将真实路径写入 Task。该路径是建议位置，不是已创建事实。
- `allowed_paths`：
  - `tools/governance/check.ps1`
  - `tools/governance/tests/`
  - `verification/GOV-PIN-LINEAGE-1/`
  - `doc/tasks/GOV-PIN-LINEAGE-1.md`
  - `doc/handoffs/GOV-PIN-LINEAGE-1-handoff.md`
  - `doc/reviews/GOV-PIN-LINEAGE-1-review.md`

Task 自身的 AC/状态和新 Handoff 可在上述范围内记录；Reviewer 仅写 Review。Plan、STATUS、`.gitattributes`、P02 Task/证据、其他 Task 文件及其它治理工具不在 Owner 修改范围。Codex 需要的 Plan / STATUS 生命周期登记属于本次释放/集成操作，不是 Owner 扩权。

### 隔离要求

本次改动影响全局检查结果，隔离 worktree 是释放条件，不是可选优化。Owner 在固定基线上实现并在隔离环境运行测试；Antigravity 对固定交付 head 审查。Review 通过后由 Codex 按项目集成流程接收，在集成后的实际 HEAD 上复跑相关治理检查，再更新 integration/closeout 字段。当前 checkout 中的 dirty/untracked 内容全部按既有用户数据处理，不能清理或带入 Task diff。

## 3.3 AC 判断与执行顺序

r25 §3.4 的六条 AC 与 r25 范围意图一致：不改写历史 pin，以 `commit:path` blob 判定 pin 有效性，把工作区漂移作为独立诊断，保留 commit/path/blob 失效时的 FAIL，并登记 63 + 6 条 registry、23 条排除诊断及独立 Review。释放时应在 AC1 / AC5 明写下列先决顺序，避免验收只验证最终 checker 行为：

1. 冻结 69 条输入记录和来源，不覆盖 inventory 中的原 evidence_id、commit、SHA。
2. **修改 checker 之前**，核对 19 个 pin-only Task 涉及的每个 pin：commit 存在、该 commit 内路径存在、blob SHA 与原 pin 完全相符。记录全量逐项表及异常。异常不是“先修 checker”的理由。
3. 核验 63 条 `TIME_BASED` 与 6 条 `LINE_ENDING` 的 pinned blob。63 + 6 = 69 条，每条结果自动提取是合理的；人工逐行复制/计算不是要求。脚本可以调用 `git cat-file` 取 blob 并计算 SHA-256，但需要保留逐条输入键、原 SHA、commit、path、blob SHA、命令/运行结果和结论，能复跑且有摘要完整性记录。任何 commit / path / hash 异常都不得由分类标签掩盖。数字“69”是 69 个 pin 项，不是 69 个 Task 或 69 次人工操作。
4. 再改 checker。由固定夹具证明工作区历史漂移、行尾转换、失效 commit、失效路径、错误 pinned SHA 与工作区一致六类行为；运行既有 `run-resource-manifest-cases.py` 与 `test_ac_gate.py`。
5. 修改前后对照全局 / 相关 Task 错误矩阵。预期最多 19 个 pin-only Task 消除该项错误；由于仍有其他错误的 64 个 Task 不应被期待整体变绿。超出预期的错误消失、无关门禁变化、或核验集合和转绿集合不一致，都应停下调查，不得记 PASS。
6. Review 和 Codex 集成验证通过后才允许 closeout。

因此 AC1 所写的 69 项逐条核验是合理且应保留的工作量：核验可自动化为一次确定性批处理，人工成本主要是审查异常与来源，不应被描述成 69 次手工 hash。需把批处理输出作为逐项证据，而不是只交一个总数或分类汇总。

### 对 check.ps1 已多次改动的额外保护

`check.ps1` 在本 Session 已经有三次修改历史（按用户提供事实：GOV-EOL-PIN-1、GOV-AC-GATE-1 两轮）。这不改变 Task 范围，但说明必须在隔离 worktree 对当前精确基线工作。要求：

- 记录 checker 相对本 Task 基线的最小 diff；不回滚或重排前序 Task 的有效变更。
- 把新增历史 blob 校验放在现有 Canonical Evidence 校验路径内，限定于明确含有有效仓库 commit 的仓内 pin；保留无 commit / 仓外来源原规则。
- 先保存改动前现有两个治理测试的结果，再运行改动后相同测试及六类新夹具；命令、环境、stdout/stderr、exit code 留档。
- 单独验证无关 v3 AC gate、Resource Manifest、路径和状态错误仍然能失败；不能只以全局 PASS 推断无回归。
- 对照固定输入和错误矩阵，确认 checker 的副作用仅是把历史 pin 有效性从工作区 hash 改为 pinned blob hash，并新增可见的漂移诊断。

## 3.4 19 个 Task 的损坏风险裁定

**不接受先改 checker、再解释转绿集合。** “blob 不符时保留 error 语义”只能保证一般失败路径，不能证明此处预期转绿的 19 个 Task 中没有坏 pin。新语义可能改变这 19 个 Task 的检查结果，因此先确认具体数据，再动共享 checker，才符合治理门禁应先证明被影响输入安全的顺序。

所需前置核验不是人工浏览 19 份 Task 的全部文字，而是从实测 pin-only 清单机器提取 pin 行，对每个三元组读取 pinned blob、独立计算 SHA-256 并匹配原 pin；由 Reviewer 抽查原始来源和报告。对任意缺失 commit、路径缺失、hash 不合、pin 项无法唯一映射或错误集合有歧义的 Task：

- 不得纳入“确认健康的 19 项”；
- 不得将其错误消失算作 checker 修复的成功；
- 维持 FAIL，记为异常并在独立来源下查清；
- 只有确认 blob 相符后，才允许该 pin 的错误在新语义下消失。

改后比较是第二道验证，不是替代改前核验。记录“实际变绿的 Task 集合”和“改前通过 blob 核验的 Task 集合”，二者必须逐项对应；超出集合的 Task 状态变化都要说明原因并回归相应门禁。

## 3.5 治理债是否清零

**不是。** 本 Task 只修复一种已识别的 Canonical Evidence pin 校验语义，不是全局治理债审计或清零授权。

当前已知的未闭合问题至少包括：23 条 `MISSING_FILE` 仍需按 r25 §5 做来源诊断；83 个失败 Task 中，19 个 pin-only 以外的 FAIL 仍含各自独立错误；Plan 中还有 `RUST-ENV-BASELINE-1` proposed 节点。后者是否属于治理债须按其实际范围判断，不能只按状态名归类。完成本 Task 只会关闭经此 Task 覆盖的 pin-lineage 范围，不能推论其余错误已经修复或不存在。

项目目前缺少一份能证明“所有已知与潜在治理债已清零”的封闭全集和审计方法。故应直答：**这不是可证明的最后一个治理 Task；也没有依据声称之后没有未发现的治理债。** 建议本 Task closeout 后做一次限定于当前 Plan 节点、已登记 backlog 与仍失败 checker 类别的只读债务盘点；逐项区分 active debt、accepted limitation、历史噪音和非治理工作，不以全仓追求全绿为目标，也不自动释放新 Task。

## 工作区状态记录

比较口径：`git status --porcelain=v1 --untracked-files=all`。

- 写入前：1593 行；状态文本（UTF-8、逐行 LF 并带末尾 LF）SHA-256：`b5b01118610c8fec1f1c4178c7189735ccfe7fa3acd2d9ba908fd4b598640ac1`。
- 写入前目标文件不存在。
- 写入后：1594 行；状态文本 SHA-256（UTF-8、逐行 LF 并带末尾 LF）为 `3ddeccda52fed0f680364369518511a2b7abba5d6bbc800e4a8b64f9e6e41c0f`。逐项对比写入前后状态，原 1593 行均保留，唯一新增项为 `?? verification/P09-GOVERNANCE-DEBT-20261019/codex-release-pinlineage-r26.md`。

## 下一步

Codex 按本裁定更新 Task 范围/AC 与真实基线，登记 Plan 和 STATUS，创建 Task 专属隔离 worktree 后，方可将 Task 正式改为 `ready` 并交 Owner 认领。DSH Owner 的下一步指令应包含：先在改 checker 前核验 19 个 pin-only Task 的全部 pinned blob；再完成 69 项 registry、checker 最小 diff、六类确定性夹具、既有测试回归、前后错误矩阵及 Handoff；固定 delivery head 后请求 Antigravity 独立 Review。任何前置 pin 异常先停下并报告，不覆盖 pin 或扩大范围。

