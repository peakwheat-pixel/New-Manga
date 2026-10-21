---
id: GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1
title: 剩余模板与NUL五项只读身份核验
kind: research
governance_version: 3
status: in_review
approval: user_auto_continue_next_task_20261022
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [GOV-BROAD-ROOT-PRESERVATION-IMPL-1]
base_commit: 951b7c61f2d09e842fc170290a1327e6780acbc0
branch: codex/gov-residual-template-nul-identity-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1
integration_commit: null
delivery_head: 69f53e0548979fda90675cdc1229d0f8ac2acb75
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1
allowed_paths:
  - verification/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1
  - doc/tasks/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1.md
  - doc/handoffs/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
  - verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md
---

# GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1

## 冻结来源、范围与目标

用户“自动继续下一步任务”（2026-10-22），来源已done实现Handoff、当前STATUS/Plan和父checkpoint；依赖R4 d5d21ff9f、集成a3bba87ce，当前基线951b7c61f。Owner Codex，Reviewer DeepSeek Harness非作者。只读当前12中的2模板错误（同一旧Review）和3含NUL文件，读取已引用32矩阵对应项及必要scanner/规则；交付精确原字节身份、语义/归属/引用与保护、保全解释选项和最小后续设计边界。研究完成不等于修复。

禁止改旧Review/NUL/历史源、旧Task/source pin/69例外/scanner/共享契约/Schema/依赖或产品代码；7历史运行身份保留BLOCKED，不猜TEMP/APPDATA，不扩大历史扫描。不执行apply/删除/迁移/归档/GC/prune/push/reset/stash/ACL/安装/Legacy。只写allowed_paths。原作者dirty/untracked/ignored原地保留。DeepSeek严格纯只读/内存，禁止fixture/权限探针/任何项目或TMP写入；不能枚举则NOT_RUN，不能绕过权限。

## Acceptance Criteria

- [x] **AC1** 五项完整code/file/locator/message与当前12、多重集匹配；原raw SHA/编码/NUL位置/行定位、tracked/HEAD blob或untracked归属事实明确，不猜修复。 <<MET>>
- [x] **AC2** 有界核实语义、来源链与当前引用/保护，给出保持原字节和旧pin的解释选项；未知与最小裁决、7历史身份保留，禁止把研究当例外配置或删除授权。 <<MET>>
- [x] **AC3** 同canonical数据前后12完整身份不变、旧保护集合不减、四个源文件raw不变；所有EV raw/blob/pin与实际注册、check/diff实测，NOT_RUN分列。 <<MET>>
- [ ] **AC4** 固定head DeepSeek独审通过，Codex正常集成/复验、资源原位保留核销，Task/STATUS/Plan/Handoff/恢复点一致。 <<PARTIAL: 待审集成>>

## 测试计划与限制

planned：Python -B读取原字节/JSON和必要Git只读查询、调用当前scan_repo_declarations同canonical数据并比较完整error/protected多重集；pwsh -NoProfile -File tools/governance/check.ps1；git diff --check。非实现，不创建合成fixture、不跑产品构建或旧127回归；NOT_RUN需注明与本只读研究无关。任何解码只在内存，不回写NUL源，不生成会被scanner当作新坏Markdown的副本。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-1|AC1/AC2/AC3/AC4|verification/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1/.gitattributes|69f53e0548979fda90675cdc1229d0f8ac2acb75|705fd4d6451a31d36b3df7de96f83f30ac976c9b4a6d1e51671d8e2f33e2d0da|CANONICAL|
|EV-2|AC1/AC2/AC3/AC4|verification/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1/audit_identity.py|69f53e0548979fda90675cdc1229d0f8ac2acb75|cafc14ded50cf7dd04aad41b14bcc2515e477bdb9cbdbf3aa0439ff2eb2aa8ff|CANONICAL|
|EV-3|AC1/AC2/AC3/AC4|verification/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1/checkpoint.md|69f53e0548979fda90675cdc1229d0f8ac2acb75|dbdd0102434cd932a08f2b12bd745ff9746c9dae1da52ed1619124d6325448a6|CANONICAL|
|EV-4|AC1/AC2/AC3/AC4|verification/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1/deepseek-review-r1.md|69f53e0548979fda90675cdc1229d0f8ac2acb75|1a09d06dbabd1af53fed4d9878af5c952ad6fb76f12586f7ef0d9dd84d99dbbb|CANONICAL|
|EV-5|AC1/AC2/AC3/AC4|verification/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1/execution.json|69f53e0548979fda90675cdc1229d0f8ac2acb75|43bec31ed755c6a4fc8922a24dd21122508e0ac385045a9f55913bbab0b5cf5a|CANONICAL|
|EV-6|AC1/AC2/AC3/AC4|verification/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1/preservation-validation.json|69f53e0548979fda90675cdc1229d0f8ac2acb75|5e00844c2828cd618c6eb57236b9a944cdb35e0271c998428865f084a12dbc97|CANONICAL|
|EV-7|AC1/AC2/AC3/AC4|verification/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1/report.md|69f53e0548979fda90675cdc1229d0f8ac2acb75|ada56aed897b03d262d610a480d36d876684d7475078ffb3b31000298ead06ef|CANONICAL|
|EV-8|AC1/AC2/AC3/AC4|verification/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1/source-facts.json|69f53e0548979fda90675cdc1229d0f8ac2acb75|f4821be6b0766d899b69980d7351f7e2b519f39b6247f33ab0fd2e6e861a708c|CANONICAL|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1 | doc/tasks/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1.md | 冻结后创建，原位保留，不删除 |
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1 | doc/tasks/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1.md | 只读运行日志/会话材料保留，无fixture/清理 |
| env/build/model | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无新建 |
| source-evidence | G:/CODEX/New Manga/verification/P09-GOVERNANCE-DEBT-20261019/codex-closeout-p19-view-r12.md | PRESERVE_REFERENCED | G:/CODEX/New Manga/verification/P09-GOVERNANCE-DEBT-20261019/codex-closeout-p19-view-r12.md | verification/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1/source-facts.json | 本研究有界只读来源，原字节/原路径保留；不覆盖旧pin，不删除/归档 |
| source-evidence | G:/CODEX/New Manga/verification/P14/owner-initiated-dsh-self-review-r1.md | PRESERVE_REFERENCED | G:/CODEX/New Manga/verification/P14/owner-initiated-dsh-self-review-r1.md | verification/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1/source-facts.json | 本研究有界只读来源，原字节/原路径保留；不覆盖旧pin，不删除/归档 |
| source-evidence | G:/CODEX/New Manga/verification/P14/owner-initiated-dsh-self-review-r2.md | PRESERVE_REFERENCED | G:/CODEX/New Manga/verification/P14/owner-initiated-dsh-self-review-r2.md | verification/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1/source-facts.json | 本研究有界只读来源，原字节/原路径保留；不覆盖旧pin，不删除/归档 |
| source-evidence | G:/CODEX/New Manga/verification/P22/codex-p22-task-r4-malformed-snapshot-7ebd7d40.md | PRESERVE_UNKNOWN | G:/CODEX/New Manga/verification/P22/codex-p22-task-r4-malformed-snapshot-7ebd7d40.md | verification/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1/source-facts.json | 本研究有界只读来源，原字节/原路径保留；不覆盖旧pin，不删除/归档 |

## 运行与恢复

冻结时main951b7c61f，common G:/CODEX/New Manga/.git；Codex epoch9有效，无并发主控接管。当前100heads/138WT，任务资源创建后预计101/139，新增资源按r212原位保留，父blocked且尚未只剩main。新branch/worktree为冻结分配路径，创建后补实际base/HEAD。不得用worktree缺未跟踪源替代canonical事实；只将本Task新增证据镜像到main供check/真实注册，旧源不镜像改写。

现场补核：五错误涉及四个源文件；实际冻结branch base/WT HEAD为cc72f6a822f0c7823a50996d9e43674147bc7b4a（包含范围冻结metadata），Task来源base951b7c61f。共同Git目录核实同一.git。已实际101heads/139WT；当前只读scanner12，旧基线protected1865，记录于本Task agent-output/baseline.json。NUL源均严格UTF-8，P14两个SOURCE_PIN在旧Task文字存在但当前scanner未实际保护文件，不推断无引用；P22 Task明确记录malformed snapshot与rawSHA。为本研究保全四源，在本Task新Manifest逐项登记原位保留，不改旧pin/源字节/解析器。

交付ec8631131，实际branch/review diff base cc72f6a822f0c7823a50996d9e43674147bc7b4a；本Task7EV完整raw/blob/pin，研究不改生产代码。baseline12完整身份未变、protected1865→1869（仅新增四源，EV登记前快照），实际原作者文件全raw不变。执行记录execution.json（UTF8，EXIT0）；初次子进程stdout GBK编码失败已改调用环境，不修改源或审计逻辑。7历史身份保留，当前101/139，下一固定head DeepSeek纯只读独审；本研究源/Handoff见对应路径。

R1 approved b8ab6317e（P0/P1=0）；非阻断P2为报告raw/blob换行叙述不准，现改为磁盘原字节等于HEAD blob，与原source-facts一致；仅报告/恢复点/R1 Review落盘/EV重签，审计脚本与原四源/工具不变。新交付69f53e054，当前8EV；固定新head交R2有界纯只读复核后才集成。
