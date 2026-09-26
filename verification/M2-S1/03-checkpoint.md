# M2-S1 Rolling Checkpoint（§5.2 格式）

```text
Timestamp            : 2026-09-26T10:35Z (+08:00 2026-09-26 18:35)
Agent                : DeepSeek Harness (M2-S1 Owner)
Task ID              : M2-S1 — Large-Media Resource Channel Feasibility Spike
TaskStatus           : in_review（初审 changes_requested 已修订并以新增 commit 重新提交；复审/集成未完成）
ExecutionState       : CHECKPOINTED
Branch               : agent/deepseek/M2-S1-resource-channel-spike
Worktree             : C:/Users/49745/.codex/worktrees/M2-S1-dsh-resource-channel（C: 独立 clone，非 linked worktree）
start commit         : 85a2aa7fd07a2dca843bf5cea3ec34070b63bdbc
current HEAD         : 见 `doc/handoffs/M2-S1-64c87d1.md` 的 `delivery_head`（= 修订 reviewed_head）；
                       Handoff 提交与后续记账提交的 SHA 记录在 `doc/tasks/M2-S1.md` 的交付与运行记录
                       与 `raw/21-revision-scope.log`（本文件不自引用自身 hash）
Working Tree         : 干净（修订交付提交后）；修订 Handoff 提交只新增/修改授权文档
Completed Steps      : 1) 固定点/clone 形态/Contract blob 核验
                       2) AS-IS 图片/tile 生产者与消费者、四类资源生命周期、Core/host seam 勘察
                       3) 合成 fixture 生成器与隔离探针 + runner
                       4) 原交付 A–E 执行（60/60 场景 PASS，exit 0），连续两次一致
                       5) 报告、Task AC 回填、Handoff 提交（4eaad684 / 7766a2bb，保留）
                       6) 读取 Codex 初审（changes_requested），新增 probe F 实测 R-001/R-002 边界
                       7) 修订报告/Task/证据，以新增 commit 重新提交（不 reset/amend）
Current Working Point: 提交修订 Handoff 并记录新 reviewed_head；随后交 Codex 复审
Next Exact Step      : Codex 在固定 base 85a2aa7、修订 reviewed_head 上重新执行非作者 Review，
                       报告路径 doc/reviews/M2-S1-<reviewed-head>.md
Tests Already Run    : probe_a..e 全部 exit 0（原交付，未重跑；命令与输出见 raw/00-run-all.log、
                       raw/10..14-*.log）；修订探针 probe_f exit 0（raw/15-probe-F-boundary.log）；
                       fixture 复现 10/10 hash 一致（raw/16-revision-fixture-reproducibility.log）
Tests Remaining      : 产品 pytest / GUI / IPC runtime（本 Task 范围不运行）；
                       研究报告 §8.2 记录的 12 项 NOT_RUN/UNVERIFIED
Current Errors       : 无。两个探针缺陷已修正（02-evidence-manifest.md §4）；两项 Review 修订已完成（§6）
Blockers             : 无 BLOCKED 实验。前置阻塞：用户对 7 项缺失阈值/USER_DECISION_REQUIRED 的决定
                       （研究报告 §7）、Tauri 资产协议（S1-B1）、TOCTOU 产品级防护（S1-B11）、
                       路径保密性（S1-B12）
Decisions            : 推荐路线 A（签名、可解码引用）为主、路线 B（流式，显式长度+摘要）为辅；
                       路线 A 附带强制限定「先打开再从句柄校验」与「引用不保密」；
                       不推荐命名 section；DuplicateHandle 仅在同用户对手被排除时可选；
                       维持 Contract §10 对 JSON/Base64 的禁止；未预选 Tauri command/序列化库
Open Questions       : 见研究报告 §7、§8.2、§12（阈值、asset protocol、ACL、TOCTOU 防护、引用保密性、
                       Core 重启/断线语义）
Evidence             : verification/M2-S1/**（探针、日志、结果 JSON、hash、delivery/revision scope log）；
                       doc/research/M2-S1_RESOURCE_CHANNEL_SPIKE.md；doc/handoffs/M2-S1-*.md
Confidence           : 高（对已运行的 68 个场景、3 条路线 + 1 对照，以及已实测的边界窗口）；
                       中（对未运行项明确标 NOT_RUN/UNVERIFIED）
Resume Safety        : RESUME_SAFE — base/branch 一致；touched 文件集合全部在授权写集合内；
                       无未提交的探针或证据；G: 主仓库与其他 worktree 未被写入；
                       历史提交 4eaad684/7766a2bb 与 Codex 初审均保留
```

## 接手时的 Reality Check（§5.2）

| 检查 | 记录值 | 结论 |
|---|---|---|
| checkpoint HEAD vs 当前 HEAD | checkpoint 不自引用 SHA；`doc/handoffs/M2-S1-*.md` 记录 base、delivery_head、handoff 提交 | 无漂移 |
| branch | `agent/deepseek/M2-S1-resource-channel-spike` | 一致 |
| worktree | `C:/Users/49745/.codex/worktrees/M2-S1-dsh-resource-channel`，`--git-common-dir` = 本地 `.git` | 一致（独立 clone） |
| 记录的文件集合 | 4 个授权写集合 | 一致 |
| TaskStatus | `in_review` | 符合 §4：初审 `changes_requested` → 修订后回到 `in_review` |
| 测试环境 | Windows 11 / Python 3.14.6 / PowerShell 7.6.6；lab 路径已随会话轮换 | 一致（记录在 `raw/16-…log`） |
| 历史保留 | `4eaad684`（原 delivery）、`7766a2bb`（原 Handoff）、Codex 初审 `f709e39` 均未改写 | 一致（未 reset/amend/merge） |

## 续作者必须遵守的边界

- 只授权写：`doc/tasks/M2-S1.md`、`doc/research/M2-S1_RESOURCE_CHANNEL_SPIKE.md`、
  `doc/handoffs/M2-S1-*.md`、`verification/M2-S1/**`。
- 禁止：`src/**`、`tests/**`、`packaging/**`、`src-tauri/**`、React/QML、Schema/migration、
  依赖或锁文件、`doc/contracts/**`、AD-001、治理导航（Plan/Status/Index/Roadmap/Task 索引）、
  M2-C1 的 Owner/Handoff/Review/evidence、其他 Task。
- Reviewer 报告路径固定为 `doc/reviews/M2-S1-<reviewed-head>.md`，只由非作者 Codex 编写；
  Owner 不写 Review、不 merge `master`。
- Codex 释放证据只在 `origin/master`（`git show origin/master:verification/M2-S1/release-85a2aa7.md`）；
  Owner 分支不 merge 治理提交，也不得创建/覆写这两个文件。
