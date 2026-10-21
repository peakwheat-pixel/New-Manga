---
id: GOV-BROAD-ROOT-PRESERVATION-IMPL-1
title: 五个广域根整体保护的精确运行策略实现
kind: governance-hardening
governance_version: 3
status: in_review
approval: user_next_step_20261021_scoped_reviewed_design_implementation
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [GOV-BROAD-ROOT-PRESERVATION-DESIGN-1]
base_commit: 40343a8b2efe85cb6927f278be9e1e16fa439726
branch: codex/gov-broad-root-preservation-impl-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-BROAD-ROOT-PRESERVATION-IMPL-1
integration_commit: null
delivery_head: 528940a007ffc53ae7278a3ea007fa80d4a65f6d
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1
allowed_paths:
  - tools/governance/clean_workspace.py
  - tools/governance/broad-root-preservation.json
  - verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1
  - doc/tasks/GOV-BROAD-ROOT-PRESERVATION-IMPL-1.md
  - doc/handoffs/GOV-BROAD-ROOT-PRESERVATION-IMPL-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
  - verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md
---

# GOV-BROAD-ROOT-PRESERVATION-IMPL-1

## 冻结范围与授权

用户“下一步”启动已独审设计的实现；依赖设计done、R3 232e3a589/source e33a51b4d。只改共享scanner收口与新增运行策略，自己的新测试复用旧RepoFixture（只读）。严格按设计schema与T01-T18；通用路径/身份/Markdown/JSON拒绝、69例外、三个消费者原实现不改。用户5广域根继续整体保护，旧两Task/原SHA/pin不变；父blocked/r212禁令不解除。

单独Task分支/worktree隔离，当前99/137，创建后预计100/138且按禁令保留。main治理权威由epoch9 gate串行维护；不复制租约。候选真实审计必须以canonical main数据（含未跟踪源）为准；仅可镜像本Task新增policy及自有证据到main，先track供候选tracked检查，main旧guard在合并前仍24，不能声称已集成。工作树自身历史文件换行或缺未跟踪源不用于替代canonical真值。

## Acceptance Criteria

- [x] **AC1** 运行策略严格schema/六记录五根/裁决与源raw/行/role/错误对/realpath精确验证，tracked存在条件，未知/漂移fatal；旧源与69例外不变。 <<MET>>
- [x] **AC2** 隔离index/scanned原子发布，新增12Declaration/5根/12warnings，恰24→12且其它12完整身份/旧保护保全；EVIDENCE_PIN/prose/JSON/直连不继承许可，三入口共用。 <<MET>>
- [ ] **AC3** T01-T18实际正反/异常注入/三入口覆盖，29+80回归0skip及双15REJECT/0deleted/0violations，独立固定head DeepSeek Review。 <<PARTIAL: 127测试和双15回放已通过，固定head独审待完成>>
- [ ] **AC4** Codex main集成复验、实际EV注册/raw-blob-pin、check/diff/Handoff/资源原位核销完整，正式其它12继续fail-closed，100/138（创建后）全部保留。 <<PARTIAL: 独审集成后才核销>>

## 测试边界与禁止

Python -B/PYTHONDONTWRITEBYTECODE=1/UTF8；TMP/TEMP仅本Taskworkspace/agent-output/test-temp，允许测试创建并自清其独占合成fixture（含隔离git init/fixture提交），禁止对真实资源执行apply/删除/迁移/归档/GC/prune/push/reset/stash/ACL/安装/Legacy。新增运行policy测试时必须tracked；无Git scanner继续fatal。只读旧29/80 tests和事故ledger，不运行会重写旧pin的历史探针。产品/构建NOT_RUN（治理工具）。发现范围外消费者缺陷只能记录，不夹带修。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-1|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/.gitattributes|2fdf5b75d17c23e838427b590069ec630dfff574|705fd4d6451a31d36b3df7de96f83f30ac976c9b4a6d1e51671d8e2f33e2d0da|CANONICAL|
|EV-2|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/candidate-audit.json|2fdf5b75d17c23e838427b590069ec630dfff574|92cb7968ece9eccec8e7c17d3a7f22e99b5e00a6f9f098053e9524de597953f6|CANONICAL|
|EV-3|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/candidate-audit.log|2fdf5b75d17c23e838427b590069ec630dfff574|6e158a7d60f2a77aff48388dd626418e4040af5b1319d54efb23f8e4df3c41f2|CANONICAL|
|EV-4|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/candidate-clean-refusal.json|2fdf5b75d17c23e838427b590069ec630dfff574|9a093834e7c0325d0c5953a1ac3f418dd12ba4ad509e237ba19fa80450817e89|CANONICAL|
|EV-5|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/candidate-clean_workspace.log|2fdf5b75d17c23e838427b590069ec630dfff574|bb781829d15d63ac1e6b27f06200bf0d2f0d81dec5daf2c02765a3deca3f370c|CANONICAL|
|EV-6|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/candidate-remove-refusal.json|2fdf5b75d17c23e838427b590069ec630dfff574|b71491fe09abad9174d9bc6c69932993cc87334331674bbb7ac5c53bb4625d20|CANONICAL|
|EV-7|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/candidate-remove_worktrees.log|2fdf5b75d17c23e838427b590069ec630dfff574|24534ff3ed761f32f1bbb6a73450044acb4eb657e00c41e945611ba7f2153b09|CANONICAL|
|EV-8|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/checkpoint.md|2fdf5b75d17c23e838427b590069ec630dfff574|c9d7d357917a34c6402101098f4c42a73384134c7f0bfc6187288f73615b7ab2|CANONICAL|
|EV-9|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/cli-execution.json|2fdf5b75d17c23e838427b590069ec630dfff574|981d650e6f914b91afa6dd1df8807e7f095b9cd0a5299c4017465629565608c1|CANONICAL|
|EV-10|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/declaration-tests-r2.log|2fdf5b75d17c23e838427b590069ec630dfff574|096a00bf6c7cbaffc513d6ff7a41ee888512a0cd386bb11dadbe30a4e712aa46|CANONICAL|
|EV-11|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/final-replay-clean_workspace.py.log|2fdf5b75d17c23e838427b590069ec630dfff574|50ea270e6be4d1d028126a2336fe167226a3e3660efbe2777680ad960bba9a43|CANONICAL|
|EV-12|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/final-replay-remove_worktrees.py.log|2fdf5b75d17c23e838427b590069ec630dfff574|70d9922a08fee33ed3993a1548554c1645048b255b0e19a0440b483c23cd0963|CANONICAL|
|EV-13|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/hardening-tests-r2.log|2fdf5b75d17c23e838427b590069ec630dfff574|e37aceacb71a57eaa9b97cb3af89f9d5cb85e794ff144e94fb05301bd700d1c7|CANONICAL|
|EV-14|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/incident-replay-clean.json|2fdf5b75d17c23e838427b590069ec630dfff574|ce80452a51e24fc6473e5a52fbd60351bd46c31a5678676505af8834d0497672|CANONICAL|
|EV-15|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/incident-replay-remove.json|2fdf5b75d17c23e838427b590069ec630dfff574|a882fec5fc4415d8393c1fec19be16303a4f5ed555d84c7d2f515435c3d973f7|CANONICAL|
|EV-16|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/new-tests-r3.log|2fdf5b75d17c23e838427b590069ec630dfff574|222ae2b7596a5ec5073eb570c49c2f256216f81190f8bd08c0c3a0c2571efb8f|CANONICAL|
|EV-17|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/report.md|2fdf5b75d17c23e838427b590069ec630dfff574|fe381d05c56b6b779d65accd7d6e88fa22ef383f8d8322476ce86f0c2ec2d1c4|CANONICAL|
|EV-18|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/runtime-proof.json|2fdf5b75d17c23e838427b590069ec630dfff574|15908a6378cf4a6cd7847d8fe0071366d8eae4b61d49dc9e0c0f5beb633bc046|CANONICAL|
|EV-19|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/test-execution.json|2fdf5b75d17c23e838427b590069ec630dfff574|0244822e8822a7a17e50791a0fe3f6cd71c4e854c18619fdbfdb0b8ef2da1574|CANONICAL|
|EV-20|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1/tests/test_broad_preservation.py|2fdf5b75d17c23e838427b590069ec630dfff574|2f8b1f4e0af9dad693e13f658dc80ee685a7d67487a3350830a5ecb17b98c555|CANONICAL|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/GOV-BROAD-ROOT-PRESERVATION-IMPL-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/GOV-BROAD-ROOT-PRESERVATION-IMPL-1 | doc/tasks/GOV-BROAD-ROOT-PRESERVATION-IMPL-1.md | Codex冻结后创建，原位保留，禁止移除 |
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-BROAD-ROOT-PRESERVATION-IMPL-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-BROAD-ROOT-PRESERVATION-IMPL-1 | doc/tasks/GOV-BROAD-ROOT-PRESERVATION-IMPL-1.md | 日志/候选/测试根保留，仅自有合成fixture允许自清 |
| other env/build | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无新建 |

## 交付记录

实现528940a00，证据2fdf5b75d，真实branch base f47c68969，Task来源base40343a8b2。candidate代码仅共享scanner收口和新增policy；127测试0skip、双15拒绝0删除0违规、真实canonical24→12/新增五根十二role及十二warning，详见report/runtime-proof。main只镜像新policy及自有证据供审查，旧guard未集成仍正式24；100/138全保留，独审前不得done。
