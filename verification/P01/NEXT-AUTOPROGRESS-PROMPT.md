请从 `G:/CODEX/New Manga` 继续自动推进已授权的项目路线图，默认用简体中文；直到全部已授权工作完成，或遇到必须由我决定的产品问题/外部不可逆操作。优先读取当前仓库的 `AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/STATUS.md`、`doc/09_COLLABORATION.md`、当前Task与对应RESUME；以Live Git、权威项目文件和实际证据为准，不根据聊天推断完成，不重做已完成审计。按项目协作协议使用非作者Agent/Skill Review并跟踪实际交付；Qoder已退出，绝不分配。

## 当前恢复检查点：P01 R1修订 candidate（C4后）

- 先核验root `main` 与P01 worktree的branch、HEAD、dirty/staged、worktree登记、common-dir；记录`RESUME_SAFE`或`DRIFT_DETECTED`。root原有24项dirty/raw evidence必须保持不动，不得stage/stash/reset/clean。
- P01 TaskStatus=`blocked`，ExecutionState=`ACTIVE`；branch=`agent/codex/P01-metadata-audit`；worktree=`G:/CODEX/New Manga.worktrees/P01-metadata-audit-codex`；base=`826bea12a132c5af2ac0cd1244d00e9170093c71`。R1 reviewed_head=`6f24006c21281df485375674d20a1d3b7b48ca63`、decision=`blocked`，正式报告=`doc/reviews/P01-6f24006c-dsh-r1.md`，SHA-256=`9d30def7e8d683b79b4265c808199523ea9aa375489fce556f477d5c506ab9ff`，session=`session-28701f2e-5276-4696-8036-11fb9a4b0445`。
- 上一已提交checkpoint C4=`aaa27767f1ca8cd5014cda0796033b3f9268cf90`；其fixed-head日志=`verification/P01/ac7-r1-blocked-checkpoint.log`，结果PASS。当前Live HEAD应仍为C4，但worktree有R1修订中的P01文档改动（精确列表见`verification/P01/RESUME.md`），staged=0；绝不丢弃/覆盖它们。R1原始报告及R1/C3证据保持只读。
- R1修订内容已在当前worktree写入：更正R2实际`status: in_review`并登记已有`STATE_CONFLICT`（未修改R2来源Task）；区分SYNTH来源Task=`in_review`与Handoff=`r4-docfix-delivered`；更正Task/Handoff测试commit绑定；把`verify_plan.py`产品路径及治理文档空白检查改为P01 frozen base到`HEAD`范围。工作树route validator和`git diff --check`目前EXIT=0，但这不是fixed-head Gate结果。
- 下一步先核对`verification/P01/RESUME.md`的Live状态与当前diff/allowed paths，只stage清单中的P01路径，staged `git diff --check`通过后提交R1修订checkpoint，Task仍保持`blocked`。新commit后运行并记录base..HEAD allowed-path、`git diff --check <base>..<head>`、路线图校验器、R2源Task只读和root保护检查，记录UTC、shell、解释器、head与EXIT；全部通过后才将P01恢复`in_review`，固定精确reviewed_head并保持不可变，使用已安装`dsh-dispatch` Skill派发DeepSeek Harness非作者R2，保存完整原始carrier。Review如仍blocked则如实记录并恢复真实审查能力；不得伪造批准。通过新Review后由Codex按`base_commit..reviewed_head`执行Integration Gate，AC/范围/证据及集成后检查满足后才标`done`并更新真实integration commit。
- 不重复P01 AC2–AC6已完成的来源Task审计：GC2/DETECT3/SYNTH元数据证据和R2/SYNTH `NOT_VERIFIED`边界见`verification/P01/metadata-audit.md`。不重做P03/P08。

## P01完成后的自动推进

从权威`REBASELINE_PLAN.md`选取依赖已满足、范围已冻结的下一项候选，正式创建/更新Task、状态、Owner/Reviewer（必须不同）、base/branch/worktree/allowed_paths、测试证据和Gate；需要外部Agent时实际dispatch并跟踪，不把建议当派发。遵守P08确认的产品范围和所有用户决策；日常实现/任务分配不询问我。更新Task、Plan、Status、依赖图、ROADMAP和Task-local RESUME。每项按AC、测试、独立Review和Codex Integration Gate逐一收口后继续下一项。保护用户数据、人工修改、Lock、current/pinned Revision、secret和其他Agent dirty；不push、不发布、不部署、不删除。只有必须由我作产品裁决、具体外部不可逆动作待确认，或全部已授权工作完成时暂停，并一次性列明问题及影响范围。
