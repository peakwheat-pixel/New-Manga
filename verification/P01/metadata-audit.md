# P01 台账元数据与 Review 载体取证

## 基线与判定边界

- Task=`P01`；冻结 base=`826bea12a132c5af2ac0cd1244d00e9170093c71`；恢复时分支 `agent/codex/P01-metadata-audit`、worktree `G:/CODEX/New Manga.worktrees/P01-metadata-audit-codex`、HEAD=`714138de3da06013e3ea35395e0c11b3d15fc371`、clean、common-dir=`G:/CODEX/New Manga/.git`。base 为 HEAD 祖先；Reality Check=`RESUME_SAFE`。核验细节见[RESUME](RESUME.md)。
- 根 `main` checkout 保持原有24项 modified/untracked；本 Task 未复制、stage、stash、覆盖或清理这些内容。
- Git 对象核验均在 P01 worktree 进行。`git cat-file -t`、`git merge-base --is-ancestor` 用于核实对象和祖先关系；Review 与 Handoff 指纹为版本化 carrier 的 SHA-256 / Git blob OID。
- P01 只修复有来源证据的 frontmatter 元数据；来源 Task 状态、Review 结论、产品决策与产品代码/测试均不在本次修正范围。

## Acceptance Criteria 结果

| AC | 结果 | 证据摘要 |
|---|---|---|
| AC1 固定检查点 | PASS | 恢复点、branch/HEAD/dirty/common-dir 与 base 祖先核验均一致；root 24项原有 dirty/untracked 保持。 |
| AC2 GC2 元数据 | PASS | `cea610ed…` 是当前 HEAD 祖先上的真实 merge commit；Task、Plan、Handoff、11轮 Review 链及集成后记录一致。仅修正 Task `integration_commit`。 |
| AC3 DETECT3 元数据 | PASS | 错误 SHA 对象查询 EXIT=128；实际 merge `8fe5199c…` 是 HEAD 祖先，且集成修正 `7314ad20` 与证据提交 `69a6e4e1` 均在该 merge 的第二父链。仅修正 Task `integration_commit`。 |
| AC4 ANNOTATE-R2 Review carrier | PASS / 独立原件 `NOT_VERIFIED` | 已追踪 Task、Handoff、Owner 报告、数据摘要与 `doc/reviews/`；没有可核验的 R2 独立报告/fixed reviewed head。没有据此宣称 Review 从未发生。 |
| AC5 SYNTH Review / 元数据冲突 | PASS / 独立原件 `NOT_VERIFIED` | Codex closeout、真实 integration commit、Plan 与 Handoff 足以证明重复字段中的 `null` 陈旧；已合并为唯一完整 SHA。Task 仍为 `in_review`，独立 Review 原件/fixed head/decision/hash 仍 `NOT_VERIFIED`。 |
| AC6 产品裁决保护 | PASS | 记录 R2 challenge 空集/T2 release 交用户裁决；保留 SYNTH 人工登录前置与来源 Task `in_review` 文本，不代用户决定、不冒称已正式 Review。 |
| AC7 最终 Review 与 Integration Gate | PENDING | 尚待固定最终 head、真实派发 DeepSeek Harness 非作者 Review、Codex 范围/指纹/空白与集成后 Gate。 |

## AC2 — M2-DERIVED-GC-2

**允许字段修正依据充分。** 源 Task 在 P01 base 的 blob=`bad659fd7a79c56e4f2c153eb26a5f21248126c9`，`integration_commit: null`；P01 worktree 中只把该字段改为 `cea610ed3f3349f1d76361d151815445e991f7d7`，不修改 `status: done` 或其他字段。修正后 Task SHA-256=`1823c834b9d24409703fc6200bf1abb19dc6ef81e46497f607e343c2f82ac4ea`，Git blob=`c4414f5697b9d88df97cabd4cc0f34336cf743ed`。

- `cea610ed3f3349f1d76361d151815445e991f7d7`：`git cat-file -t`=`commit`；parents=`554a9845fe0372436c89179568f15a4b73242eef`、`0fadc330a6daa42de6c78be52feaae26ce6724ea`；`git merge-base --is-ancestor <sha> HEAD` EXIT=0。
- Task 的收口记录（`doc/tasks/M2-DERIVED-GC-2.md`）与 Plan（`doc/REBASELINE_PLAN.md` §P01前置/历史集成记录）均把最终合并记作 `done @merge cea610ed`；Task AC6 记录 merge 和集成后验证完成。该值与当前 HEAD 的 Git merge 对象一致。
- Handoff `doc/handoffs/M2-DERIVED-GC-2-363265b1.md` SHA-256=`60773c8195eab7a88b76c8d3be157204e77da3b4705e75a708ea342253e401cd`，blob=`9d31ac659548533769b54f97d1045d074ef597a3`：固定代码实体 `363265b1`、Owner 终 tip `0fadc330`、Codex r11 后交 Codex 集成。Task 与 Handoff 都保留真实旧状态/边界。
- 独立于作者的 Codex r11 carrier `doc/reviews/M2-DERIVED-GC-2-258ca6fe-codex-r11.md`：`reviewed_head=258ca6fe45ae75e4165b6ba5624e0c3a1bb7669e`、`evidence_tip=dc0bb4841908e0c3746b5bb623e190920d2cd61c`、`decision=approve`、0 findings；SHA-256=`3e2fb4b0b9526fa46a780f29b510f7e8004cf6b21b360538e1f00fca776e9776`，blob=`d33ef2909b08ed4433ad14f57722673d4659a9f8`。Task/Handoff 记录完整 11 轮 Review 收敛，r11 后再集成。
- Plan 与 STATUS 集成记录确认 merge 后 pytest 1941 passed + 1 skipped、cargo 62 passed + 1 ignored、vitest 140 passed；packaged 证据绑定交付第十轮，并登记 runner 的 CS-L1 既有 FAIL/debt。这里仅引用已归档历史证据，不声称 P01 重跑这些产品测试。

## AC3 — M2-PROD-DETECT-3

**允许字段修正依据充分。** 源 Task 在 P01 base 的 blob=`7ca47ad98b5d9a6efc666ea749215eeb063888b1`，字段值为 `8fe5199c44b06e679a2f0e6ee47767032217eb47`；对象查询 EXIT=128。Task 把集成记录写为 `merge=8fe5199c`，但该 SHA 不是 Git 对象。P01 worktree 中只将字段改为真实 merge `8fe5199c6d05d144052141ad02ed054bbaa90645`，不改 `status: done`、交付 head 或其他审计/产品字段。修正后 Task SHA-256=`445b992e1921a4dc6ff115b61aa6b1a341732c0b8c50906f15be442c1f1ae796`，blob=`58d4433d57a1c929109457f5950e8c3c6ad33db7`。

- 实际 merge `8fe5199c6d05d144052141ad02ed054bbaa90645` 是 commit，parents=`c63bee0e…` 和 `0a470407…`，为当前 HEAD 祖先（EXIT=0）。`7314ad20`（集成修正/重建输入）与 `69a6e4e1`（重建后证据）均为该 merge 第二父链祖先（各 EXIT=0）。
- Handoff `doc/handoffs/M2-PROD-DETECT-3-983a50d5.md` SHA-256=`8728341a796c9e0b9bd07545d3dbc56af3189ec7322d1a63554086c1200c5d9a`，blob=`1f9a1e48187896ccb6e7b9dd50b5755398aa2e74`：`base_commit=46f079e8`、交付证据 `69a6e4e1`、集成修正 `7314ad20` 与重建验证链均有明确记录。
- DSH r1 carrier `doc/reviews/M2-PROD-DETECT-3-7314ad20-dsh-r1.md`：Task/Handoff 记录 `approved_with_conditions`，其条件在集成修正、重建与集成轮证据中逐项闭合；SHA-256=`4fad67d23f458b05c1402ca68659126c6aa6b06090b21692f435e90d42edf898`，blob=`b29be12bc05def3ebb255faa0303b9532a1ebe69`。Task/Plan 记录集成后 pytest 437 passed + 1 skipped、cargo 44 passed + 1 ignored，且产品状态 `done`。P01 不重跑产品 Gate。

## AC4 — M2-SFX-ANNOTATE-R2 Review carrier

**独立 Review 原件=`NOT_VERIFIED`，不等于断言其从未发生。** 源 Task SHA-256=`525a37a24ab9c7f5ce7c613e574d13a0c1e34359e2d0c2f53e63ef56582b12fe`，blob=`8e6b27de853dc24e108ef98a3866a0057c209e3e`；`review_events: []`。Task 后续段落有 `approved_with_conditions` 的嵌入式结论文字，但没有 Review 文件/会话原件链接或 fixed reviewed head。

- Handoff `doc/handoffs/M2-SFX-ANNOTATE-R2-zcode-20261004.md` SHA-256=`0baa9fc65b4247ef7ae97b79e9e5140d50e0c5aa07fa0fa5355dfa5ece3c7182`，blob=`bbefef967c660129fb99a0b4915b5a1c219d3d4d`：frontmatter 记录 base=`99eab8b6`、delivery=`cb055135`、`status=in_review`；正文要求 DSH 报告落到该 Task 的 verification 目录，但现存交接只有摘要，没有原始报告、精确 reviewed head、DSH transcript/退出码或报告 SHA。
- `verification/M2-SFX-ANNOTATE-R2/stage-r2-report.md` 是 Owner 自核而非 Reviewer 报告：开头明确独立 Review 待审。SHA-256=`e624c7cfed247f149fc7aad57d244fc2010966c9bdd0c4661dfeee26d1005508`，blob=`09cefe93311092c793ea39d183f7cccaae5c4c94`。`stage-r2-final-summary.json` 是数据摘要，不是 Review：SHA-256=`38ea3b95fc2f0089d1dbcc028f285120bd264754d08acadfe0320bf47b9000b2`，blob=`6a1d2a5809c5c636dc74877e9a8a9fe20baed33f`。
- `git ls-tree -r --name-only HEAD -- verification/M2-SFX-ANNOTATE-R2` 仅有上述两项；`doc/reviews/` 未找到 R2 专属报告。R3 的 DSH 报告和 R1 的 DSH verdict summary 均不是 R2 Review carrier。
- Task `status: done`、`integration_commit: 84f952b3` 及其历史关闭提交保留不动。Task 与 Owner 报告中的 challenge 空集、T2 是否释放均明确留待用户/编排裁决；P01 不追加解释为批准或释放建议。

## AC5 / AC6 — M2-SFX-SYNTH-BG-AUTO

### 可核验的 integration 字段与仍未核验的 Review

- P01 base 源 Task 的 SHA-256=`5da2f3ad99e441324d388dbcd576337ce3befde0773e295c10dc2715c20ab307`，blob=`9f475861360f07e78b2c5ca2fd9dd493b102b413`；frontmatter 有短值 `integration_commit: 913ca3a9` 与重复 `integration_commit: null`。Merge `913ca3a9f9c9a83c43d9a03af4bc80b54cc1cc66` 为真实 commit、parents=`d1af32e4…`/`8c77c90f…`，且为当前 HEAD 祖先（EXIT=0）。
- Codex governance closeout `72ac895eebacfe84bbd93493ddebb1db1eb515fb` 的 Task tree 已记录 `integration_commit: 913ca3a9`，但重复 `null` 仍在；Plan 的 Task 表将 SYNTH 标为 2026-10-04 done，后续集成/真实冒烟提交为 `3a0ce5f705c842a5073128a59ab5f853e6522844`。这些证据足以证明重复 `null` 陈旧，不足以让 P01 改 Task status 或审核结论。
- P01 只保留一条完整字段 `integration_commit: 913ca3a9f9c9a83c43d9a03af4bc80b54cc1cc66`，删除重复 `null`；保留 `status: in_review（代码集成 done @merge；真实冒烟 manual 待用户登录后代跑）`。修正后 Task SHA-256=`e30b536ddf625ac601f9264058cf0b960cbc12db57a9f1803d8ea2f861627f3d`，blob=`a9720c761253dfaad2d5e8847f6ca5a3d36168ac`。
- SYNTH Handoff `doc/handoffs/M2-SFX-SYNTH-BG-AUTO-zcode-delivery-20261004.md` SHA-256=`a9f996b653a1bfde82a821e14908a1159a89cc31990e4e63e1928940a4aa5b36`，blob=`08841688ef2e82a3265226bdf8c727415611411f`。Handoff 文本提到 DSH r1–r4 结论与修订，但当前 tracked `doc/reviews/` 未找到 SYNTH 专属报告；没有可核验的原始报告、精确 fixed `reviewed_head`、decision 原文或报告 hash。因此 SYNTH 独立 Review carrier=`NOT_VERIFIED`，不补造批准。

### 人工冒烟和产品裁决边界

- Versioned evidence commit `5907be5967ea01ce42ee2834e84837771abadc7f` 含 `verification/M2-SFX-SYNTH-BG-AUTO/smoke-run.log`（该 Git 对象内容 SHA-256=`90654cd070ead3437331b6bb110c6a2bc7f32d8f580c068b43c3dfd70a2c10ab`）和 `bg-index-smoke.json`（SHA-256=`d20afc4ec339c0a7ca28c119c29ada013bf6a8eb190e9c3080a68b00b9b033a4`）；后继 `3a0ce5f7` 将证据集成。Handoff §真实冒烟留证记录人工登录后由集成方生成两张图并 `EXIT=0`。这证明有版本化冒烟证据，但不替代独立 Review。
- 源 Task/Handoff 仍保留 `status=in_review` / manual-login 文本；Plan 与后续记录另称已 done/AC5 冒烟闭合。此处只登记 `STATE_CONFLICT`，不改 source status、登录前置、用户决定或 Review 结论，也不把人工冒烟提升为本次重跑。
- ANNOTATE-R2 challenge 空集和 T2 release 都仍是用户裁决；SYNTH 人工登录要求保持原文。本 Task 没有作产品取舍。

## 运行记录与剩余 Gate

| 检查 | 命令/证据 | 结果 |
|---|---|---|
| 恢复安全 | `git worktree list --porcelain`；`git rev-parse --path-format=absolute --git-common-dir`；`git status --short --branch`；`git merge-base --is-ancestor <base> <HEAD>` | EXIT=0；`RESUME_SAFE`，P01 clean，root 24 项未动。 |
| 对象/祖先 | `git cat-file -t <full SHA>`；`git merge-base --is-ancestor <commit> HEAD` | GC2、DETECT3、SYNTH merge 均为 commit 且为祖先；DETECT3 错误字段对象查询 EXIT=128。 |
| R2/SYNTH carrier inventory | `git ls-tree -r --name-only HEAD -- doc/reviews verification/M2-SFX-ANNOTATE-R2 verification/M2-SFX-SYNTH-BG-AUTO`；目标 `git log HEAD -- <path>` | 两个来源 Task 均未定位独立 Review 原件；SYNTH 的 versioned smoke evidence 存在。缺报告的 rg 无匹配是 EXIT=1，按 `NOT_VERIFIED` 记录，不扩展为全仓/外部不存在。 |
| 路线图状态/依赖验证器 | `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` | EXECUTED EXIT=0：196节点分类/依赖、105祖先记录、21规划节点、DAG、导航链接、P01 frozen-base零产品差量均PASS。校验器的状态分布/标签、P08节点计数及代码差量基线已按P01 Task scope note收窄更新。 |
| AC7 路径/空白预检 | P01 allowed-path gate；`git diff --check 826bea12a132c5af2ac0cd1244d00e9170093c71`；同一命令运行路线图校验器 | `verification/P01/ac7-preflight.log`，SHA-256=`75aa3a3db5d6893ba60387271a255ee45ac8d818dfedc5c44eb4d1fcf71d63c9`；Git blob=`6d6de83ff6b7ce38d78ffa8cabc62aa72162682f` | 16项均在Task允许路径，staged=0，diff-check EXIT=0，路线图验证器 EXIT=0。此为交付前预检；固定 delivery/final head 的复核、DSH Review 与 Integration Gate仍待执行。 |
| 产品代码/测试 | 本 Task 冻结为只读取证和少量 Task frontmatter 修正 | `NOT_RUN`；本 Task未修改产品/测试代码。 |
| 固定 head / allowed paths / diff-check / DSH Review / Integration Gate | P01 AC7 | `PENDING`；待交付 Handoff 后，以实际固定最终 head 派发 DeepSeek Harness 非作者 Review，再由 Codex核验并集成。 |
