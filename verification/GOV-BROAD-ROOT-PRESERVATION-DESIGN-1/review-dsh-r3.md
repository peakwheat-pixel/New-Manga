# DeepSeek R3：设计及metadata批准

session: session-89d9de3e-714e-4a87-b0b0-b60526ec5eae；exit0；web_visibility=unverified

**approved（仅设计/自有 metadata）**

固定基准：
- 原 `diff_base`: `3d0a36ac04d30eba0906e70218ef9491c5b9ffbc`
- R2 reviewed head: `1670b34ec39bd72c5b663d42193faea96836e22a`
- R3 reviewed head: `232e3a5896644446acf3c4e0a0d5edc1a9490616`
- 设计交付 source: `e33a51b4df4856b9bdfe2dd8e57b84f1c395a797`
- EV-10 commit: `9cfae1352ca97a53cf5b037f7d66d4bb502a3fea`

## R1/R2 发现关闭

- **R1 P1 诊断承载/计数**：已关闭。设计明确 12 条 `DECL_BROAD_ROOT_PRESERVED` warnings；R2 模型 `warnings 254→266`，15 覆盖与内存模拟已复核。
- **R1 P1 untracked policy**：已关闭。untracked 存在=`POLICY_UNTRACKED` fatal；tracked 丢失=`MISSING`；Git 失败、非 Git scanner、读取失败均 fatal；直接 `ProtectionIndex`/model 不触发 policy。
- **R1 P2 相邻断言**：已关闭。只断言新增五根无命中，不要求 `evaluate(repo)==[]`。
- **R1 P2 原子/计数**：已关闭。`new_index/new_scanned` 隔离、两阶段发布、异常丢弃暂存、最终统计前收口；注入测试仍为未来 NOT_RUN。
- **R1 P2 非 Git fixture**：已关闭。旧行为仅限有效 Git RepoFixture；nonGit 继续 fatal。
- **R2 P2 Handoff 旧 delivery**：已关闭。Handoff 顶部 `delivery_head` 和下一 Task 建议均为 `e33a51b4...`，Handoff 内已无 `c9d6b195...`。

无剩余 P0/P1/P2。

## 本次 R3 实测

- `R2..HEAD` 仅 3 个文件变化：
  - `doc/handoffs/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1.md`：仅下一 Task 的 delivery 由 `c9d6b195...` 改为 `e33a51b4...`，1 行删除/1 行新增。
  - `doc/tasks/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1.md`：新增 EV-10 行和 R3 运行记录，3 行新增。
  - `verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/review-dsh-r2.md`：新增保存 R2 Review。
- 设计、模型、六绑定、两历史源、7 个只读输入、tools 均无 R2..HEAD diff；7 个输入 raw/base/status 全部一致；runtime policy 仍不存在。
- 10 份 EV：10/10 path 可取、commit 可取、current raw SHA = committed SHA = pin；10/10 tracked 且 status clean。原 EV-1..EV-9 的 path/commit/pin 与 R2 完全一致；EV-10 指向 `review-dsh-r2.md`，commit 前缀为 `9cfae1352`。
- 实际 `parse_markdown_declarations` 注册结果：`EVIDENCE_PIN=10`、`errors=0`。
- 当前真实 guard：`errors=24`，错误码分布与 R2 一致；`declarations=2477`、`protected_roots=1807`（较 R2 的 2476/1806 增加 EV-10 一项），仅作当前计数，不是模型计数。
- `99` heads、`137` worktrees；未变成“只剩 main”。父 blocked/r212 保留。
- `git diff --check 3d0a36...HEAD` exit 0；`check.ps1` exit 0，PASS，2 个 warning（14 个非终态 Task、STATUS 预算 80%）。
- PowerShell 仍有 ConstrainedLanguage 非核心类型 stderr 告警，但命令均 exit 0；未作为实现测试证据。

## 沿用与本次新核

- **沿用 R2 已核**：设计正文、模型 `warnings 254→266`、15 项覆盖、六绑定语义、7 输入保全、正式 24 错误主体。
- **本次 R3 新核**：Handoff metadata、R2..HEAD 范围、10 EV 注册与 pin、EV-10 对应 `9cfae`、原 9 EV 未变、7 输入未变、当前 24、99/137、`diff --check` 与 governance check。
- **未重算**：未重读设计正文、未重算 15 模型；按任务要求不重复历史/资源盘点。

## 未测与边界

- T01–T18、109 回归、clean/remove 双 15 回放均 **NOT_RUN**，是未来实施 Gate。
- policy loader/schema、漂移/错误对/realpath 负例、原子异常注入、三个 CLI 真实行为均未实现。
- 产品/构建测试 NOT_RUN；无任何真实清理、迁移、GC、prune、push、ACL 或 Legacy 运行。
- `SIMULATION 24→12` 仍不等于当前真实 24 已消解；当前正式仍 24 errors。
- 本批准仅覆盖固定 base/R3 head 的设计与自有 metadata，**不批准工具实现、runtime policy 发布、资源清理或父 Task 解除 blocked**。

**下一步建议：Codex 核销本 R3 独审，按 Handoff 另冻 `GOV-BROAD-ROOT-PRESERVATION-IMPL-1`；实施前仍须 T01–T18、109、双 15、真实 24→12、三入口和固定 head 全部 Gate。**
