## P04 提案修订 · 第二轮只读审查（static only）

**审查对象**：`codex/P04-scope-freeze` @ `af67d5019fa3fb83ed2c1765dd2548cdba743a80`，base `88579622d85ff6d0dfd509c6f21931bd91d0881b`
**HEAD 确认**（只读 Git 元数据）：`.git/refs/heads/codex/P04-scope-freeze` → `af67d501…`；`.git/worktrees/P04-scope-freeze/logs/HEAD:4` 记录 `018023e8 → af67d501`，消息 `docs: address P04 proposal review findings`。

---

# Verdict: approve

第一轮 P1-1 与 P2-1/P2-2/P2-3、P3-1..P3-6 均已实质关闭；P04 仍为 `proposed`，隔离前提与阻止释放条件在 Task/Plan/STATUS/Index 间一致。仅余 1 条非阻断 P3（reviewed head 未绑定恢复/校验记录），不影响批准。

---

## 第一轮 finding 逐项关闭确认

| 编号 | 结论 | 证据（固定 head 内） |
|---|---|---|
| P1-1 sidecar bundle / provenance / build gate | **closed** | `doc/tasks/P04.md:14-16` 新增结构化 `blocked_by`（P02 Build Gate: PASS + Codex-provisioned 隔离 checkout + provenance-bound bundle）；`:61-63` 前提栏要求隔离 checkout、sidecar 源码/脚本 commit、input pins、SHA-256、`CARGO_TARGET_DIR` 用 Gate 指定 scratch 路径；`:70` 明确 bundle 由 Codex 在隔离 checkout 按 P02 授权 `build_sidecar.ps1` + 冻结 inputs 生成、记录 SHA-256、**Owner 不得自行运行 sidecar build**、禁止复用 root ignored output，并如实标注 `build.rs` 缺目录即 panic、当前 worktree 无该目录。`REBASELINE_PLAN.md:75`、`STATUS.md:3`、`00_INDEX.md:3` 同步。 |
| P2-1 AC1 字面精确断言 | **closed** | `doc/tasks/P04.md:35`：强制 `assert_eq!(PAGE_NAV_PRODUCTION_ONLY_COMMANDS, &["list_chapters", "list_chapter_pages"]);`，明文"不得从该常量自身派生期望"，且 probe/M2-AC1 面检查针对"这两个字面命令"。 |
| P2-2 AC2 FAIL / blocked / follow-up 无循环 | **closed** | `doc/tasks/P04.md:36` 区分行为 `PASS` / `FAIL` 与阻断；`:37` 规定错配时只落 `verification/P04/**`、**不提交失败测试、不改生产行为**、P04 置 `blocked`（previous=`in_progress`）、Codex 建独立修复 Task 且"明确其不依赖 P04=`done`，避免依赖环"、修复集成后恢复 P04 补/启用回归测试并复跑 AC2、修复与复测前不得 done、无法确定性构造则同样 blocked + 另立 seam Task。AC4 的集成条件因此不再互锁。 |
| P2-3 checkpoint 与恢复指针 | **closed（主体）** | 新增 `verification/P04/proposal-review-checkpoint-018023e8.md:7,13,14,15`：绑定 reviewed HEAD `018023e8`、列出变更路径集、记录 route validator / `git diff --check` / 直链检查结果与 DSH verdict；`proposal-amendment-checkpoint-20261010.md:15-16,24-27` 记录修订项与"发布/运行 Cargo 前"的下一步；`doc/tasks/P04.md:78` 区分"初始提案 checkpoint（历史快照）"与"最新恢复点"。残余见下方 P3。 |
| P3-1 M2-AC1 术语 | **closed** | `doc/tasks/P04.md:35` 已写作 "probe/M2-AC1 面"。 |
| P3-2 protocol 旁录与 PROPOSAL 限制 | **closed** | `doc/tasks/P04.md:36` 末句：字段"只在 sidecar 边界旁录到 `verification/P04/**`，该记录本身不代表 PASS，也不冻结合同中的 PROPOSAL 语义"；`:71` 再次限定为诊断证据、不提升 `request_id` 语义。 |
| P3-3 stderr / availability 临时工件未签入 | **closed（静态）** | `verification/P04/` 现无 `dsh-availability-probe.*`，亦无 R1 的 `dsh-proposal-review.stderr.log`；`proposal-review-checkpoint-018023e8.md:9,13` 明示 DSH dispatch artifacts 不属 reviewed commit、变更路径集仅 5 个文档；`proposal-amendment-checkpoint-20261010.md:9,26` 明确只入库 prompt/output/exit/session，"never the stderr trace"。 |
| P3-4 显式 `--bin m2rc1-desktop` | **closed** | `doc/tasks/P04.md:61-63` 三条命令均含 `--bin m2rc1-desktop`。 |
| P3-5 `#[cfg(test)]` 限定 | **closed** | `doc/tasks/P04.md:43`："仅 `#[cfg(test)]` 范围内的测试、helper 或同步设施；生产代码零改动"。 |
| P3-6 机器可读 `blocked_by` | **closed** | `doc/tasks/P04.md:14-16`；`:70` 显式回指该字段；`REBASELINE_PLAN.md:75` 启动条件列同步。 |

---

## Unresolved findings

### P3-1：reviewed head `af67d501` 未绑定任何恢复/校验记录，"最新恢复点"仍指向提交前状态

- 路径/行号：
  - `verification/P04/proposal-amendment-checkpoint-20261010.md:7`（`current HEAD` 仍写 `018023e8`；`:9` Working Tree 为"modified/new、no staged"的提交前形态）
  - `verification/P04/proposal-amendment-checkpoint-20261010.md:26`（Next Exact Step 仍是"validate 后 commit amended candidate，再请 DSH 复审新 head"）
  - `doc/tasks/P04.md:78`（把上述文件标为"最新恢复点"）
  - 反证：`.git/worktrees/P04-scope-freeze/logs/HEAD:4` 显示 `af67d501` 已提交；全仓检索 `af67d501` 仅命中 `verification/P04/dsh-proposal-review-r2.prompt.md:3` 与 `verification/P04/dsh-proposal-review-r2.stderr.log`（两者均为本会话派发工件），无任何已提交 checkpoint 记录该 HEAD、变更路径集或 route validator / `git diff --check` / link 结果。
- 影响：按 `P04.md:78` 恢复的人会认为当前 HEAD 仍是 `018023e8`、且"提交修订候选 + 路线校验"尚待执行；`af67d501` 通过路线 validator 这一结论在仓库内没有落盘证据（仅 R2 prompt 的口头声明），与仓库"未记录不记为已通过"的纪律不一致。不会诱发受禁操作，故非阻断。
- 最小修改：本轮 R2 落盘时新增一份 delivery checkpoint（或就地追加节），记录 `af67d501` 的 HEAD/tree、变更路径集、route validator / `git diff --check` / Markdown 链接结果，并把 `doc/tasks/P04.md:78` 的"最新恢复点"指向该文件；同时按 `proposal-amendment-checkpoint-20261010.md:26` 的口径处置 R2 派发工件（`dsh-proposal-review-r2.stdout.md` / `.exit` / `.session.txt` 入库，`dsh-proposal-review-r2.stderr.log` 不入库）。

**unresolved P0/P1/P2/P3 = 0/0/0/1**

---

## 其余审查点确认

- **仍保持 proposed**：`doc/tasks/P04.md:5` `status: proposed`，`:9-10` `owner/reviewer: null`；`REBASELINE_PLAN.md:75` = `proposed / 未释放`；`STATUS.md:3` 与 `00_INDEX.md:3` 均含 "P04 仍为 proposed"。
- **依赖与允许范围准确**：`depends_on` 仅含已 done 的 `M2-PAGE-NAV-PROJECTION-1`（`P04.md:12-13`；`M2-PAGE-NAV-PROJECTION-1.md:5` = done）；硬执行前提以 `blocked_by` 结构化表达并与 `:70` 一致。允许范围 `:42-46` 仅覆盖 Rust 测试代码、`#[cfg(test)]` 设施、`verification/P04/**`、本 Task 文档与 Codex 维护的共享状态文件；AC2 的 sidecar 旁录、AC3 的回归测试均落在该范围内，未授权改生产逻辑/契约/依赖/ACL。
- **Plan / STATUS / Index / Checkpoint 一致**：三处均引用 `proposal-amendment-checkpoint-20261010.md` 为最新恢复点、均声明 P04 proposed、均写明硬启动条件为 P02 Build Gate=`PASS` + 解除 Hard Build Barrier + Codex 在 P02 批准隔离 build/test checkout 固定 sidecar provenance、均写明当前 worktree 无 `target/core-sidecar/core-sidecar` 且不得复用 root ignored output、均写明"屏障解除前不得释放 P04 或运行 Cargo"。
- **sidecar 与 `CARGO_TARGET_DIR` 仅限 P02 批准隔离环境**：`CARGO_TARGET_DIR` 仅出现在 `P04.md:61-63`，每条均绑定"Codex provisioned 的 P02 批准隔离 checkout"与"Gate 指定的 scratch 路径"；bundle 生成为 Codex 在隔离 checkout 按 P02 授权流程执行（`:70`），Owner 被明令禁止自行运行 sidecar build。无任何条目允许在 P04 worktree 或 root 产出/复用 sidecar。
- **P04 仍被正确阻止释放**：`blocked_by` 两条 + `P04.md:54`（屏障未解除禁止 Cargo/Tauri 测试、Feature 查询/启用、scratch clone、Sandbox）+ `:65`（三项前置任一未满足不得要求 Owner 运行 Cargo）+ `:70`（保持 proposed、不创建 Owner 分支、不派发实施），与 `REBASELINE_PLAN.md:75`、`STATUS.md:3`、`00_INDEX.md:3` 一致。
- **无"未运行写成 PASS"**：`P04.md:61-63` 实际结果全部 `BLOCKED / NOT_RUN`；`proposal-amendment-checkpoint-20261010.md:20-21` 如实记录未运行与"static only"边界。

---

## 审查限制与边界

- 本审查为**固定 head 的静态只读检查**；未运行 Cargo/Tauri build 或 test、未启动 Sandbox、未查询/启用 Windows Sandbox Feature、未创建 scratch clone、未创建或派发任何 Task。
- 只读 `git` 命令在本机被 DSH 沙箱 ACL 拒绝（`SetNamedSecurityInfoW failed (Win32 5)`），故 HEAD/提交顺序由 `.git` worktree 元数据与 reflog 只读确认；**无法逐文件核对 `018023e8` / `af67d501` 的提交内容**，P3-3"未签入"结论基于文件存在性与 checkpoint 声明的静态一致性，而非 git 复核。
- 本轮 R2 的 `dsh-proposal-review-r2.stderr.log` 含审查推理文本，属派发链路实时写入的工作区工件，不应作为证据入库。
- **本结论仅批准 proposed Task 的契约（范围/AC/依赖/阻塞表达）**，不是 P04 实现 Review，不是 Build Gate，也不是产品验收或发布 Gate。

## 推荐下一步

由 Codex 在落盘本轮 R2 证据时一并执行上述 P3-1 最小修改（绑定 `af67d501` 的 delivery checkpoint + 更新 `doc/tasks/P04.md:78`），随后 P04 保持 `proposed` 直至 P02 Build Gate=`PASS`、Hard Build Barrier 解除且在 P02 批准隔离 checkout 中生成 provenance-bound sidecar bundle；在此之前不创建 Owner 分支、不派发实施、不运行 Cargo。除该文档绑定动作外，**无需下一步操作**。
