# GOV-RESOURCE-MANIFEST-JSON-1 集成裁定与 closeout 建议（r9）

日期：2026-10-19（Asia/Shanghai）

## 2. 裁定：选 A，接纳 `a2ca297f1` 为最终 delivery/integration source head

接纳理由：`a2ca297f1b5775a0d5fb5fc8efcc2281bc4013c2` 相对 `7d09143d6df73d6c12a9769beaf19cfd70cc313c` 只新增 Review 报告，并修正测试驱动写入非法 JSON 字符串的方式；没有改 `tools/governance/check.ps1` 或 schema。Review 的 `reviewed_head` 仍如实填写 `7d09143d6df73d6c12a9769beaf19cfd70cc313c`，Task 的 `delivery_head` 填 `a2ca297f1b5775a0d5fb5fc8efcc2281bc4013c2`。不得把两者改写成相同 head，也不要求为这项仅测试驱动的变更重做代码 Review；集成后应在最终集成树上重跑离线套件和治理检查。

closeout 应明确写：`reviewed_head=7d09143d6df73d6c12a9769beaf19cfd70cc313c`，`delivery_head=a2ca297f1b5775a0d5fb5fc8efcc2281bc4013c2`，`integration_commit=<实际生成的 --no-ff merge commit 完整 hash>`。说明 Review 与 delivery/integration head 不同；两者之间的唯一实现差异是用例 19 的测试驱动修正，Review 报告本身于 `a2ca297f1` 落盘。`integration_commit` 不是 `a2ca297f1`，也不是预演得到的 tree hash；merge 后用 `git rev-parse HEAD` 记录实际 merge commit。

## 3.1 集成命令与基线核验

当前现场核实值与请求中列出的主 checkout HEAD 不同：主 checkout 实际 branch 为 `antigravity/P09-AC3-DELETE-HARDEN-1`，HEAD=`bb3abad16fc16aa7fc263718e182304a7fd84344`；`688d866d9b614de32ce1f511040a208ab6e9f32e` 是其祖先。目标 worktree branch `GOV-RESOURCE-MANIFEST-JSON-1` 的 HEAD 为 `a2ca297f1b5775a0d5fb5fc8efcc2281bc4013c2`，以 `c131b1ae114d00c17e734a51f38263d92fe6f198` 为分叉基线；相对实际主线有 **9 个提交**不在主分支。

只读 `git merge-tree --write-tree bb3abad16fc16aa7fc263718e182304a7fd84344 a2ca297f1b5775a0d5fb5fc8efcc2281bc4013c2` 成功，返回 tree `168d19a08162f8a6932470f7436e0c082c0a2db8`，未见文本冲突。GOV-PLAN-BUDGET-1 已在主线：Plan 标为 `done`，`c131b1ae...` 集成提交在主线祖先链中；无需再次集成该 Task。

**本轮没有执行 Git 写操作。** 当前主 checkout 有 1,235 条 porcelain 状态行，目标 worktree 有 33 条；两边均有既存未跟踪内容。不得直接在此状态下运行以下命令，也不得 stash、清理、移动或覆盖这些文件。待文件所有者完成逐项核实并安全保存，且主 checkout 状态允许切换/合并后，在主 checkout 执行：

```powershell
Set-Location 'G:\CODEX\New Manga'
git switch antigravity/P09-AC3-DELETE-HARDEN-1
git merge --no-ff --no-edit GOV-RESOURCE-MANIFEST-JSON-1
git rev-parse HEAD
```

无冲突预期依据是上述只读 merge-tree 预演；遇到新冲突或未跟踪文件覆盖提示即停止并保留现场。合并完成后，`integration_commit` 填最后一条命令输出的完整 hash。

## 3.2 Task 终态、Canonical Evidence 与 Resource Manifest

### 终态与字段

目标终态建议为 **`done`**，因为 AC1–AC5 已由 Review 批准，r8 对 AC4 的计数语义作了 Codex 裁定，r2 报告确认 P1 已修复；目前仍缺的是集成与可追溯 closeout，不是已知产品限制。当前 Task 仍是 `in_progress`，在 merge、集成后验证、AC4 证据更新和资源清单闭环前不得提前置 `done`。若无法补出 AC4 的可复核证据或集成检查失败，则暂留 `in_progress`；只有明确决定放弃未满足 AC 时才使用 `closed_with_limitations`，不建议用它替代尚未完成的常规 closeout。

最终 frontmatter 建议：`canonical_evidence_status: complete`、`resource_closeout_status: complete`；在所需证据和资源行均落盘前，两项保持 `pending`。Task 字段分别记录 `delivery_head=a2ca297f1...`、`integration_commit=<merge commit>`；Review 文件记录 `reviewed_head=7d09143d...`。

### Canonical Evidence 建议行

Review 文件本身可作为当前独立 Review Gate 的 canonical evidence。AC4 源 JSON 应登记为 `SOURCE_PIN`。现有两份 Task evidence 中，`ac1-ac5-manifest-support.md` 描述早期 16 个用例和旧版 P1 状态；`ac4-brace-and-counts.md` 的结论仍写 `BLOCKED`，与 r8 后来的裁定冲突。它们可保留为历史输入，但不能冒充完整、最新的 AC1–AC5 canonical evidence。先由负责 closeout 的人把 AC4 证据与 r8 对齐，并用最终实际 evidence commit/hash 替换下表中的待填项；不要伪填 SHA 或把未提交文件登记成 canonical。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| `GOVRM-REVIEW-R2` | AC1–AC3、AC5 / 独立 Review | `doc/reviews/GOV-RESOURCE-MANIFEST-JSON-1-7d09143d6-antigravity-r2.md` | `a2ca297f1b5775a0d5fb5fc8efcc2281bc4013c2` | `CADDDB6162B5B3915F10923FAA4F4ABB96A7FED3438832371D3C3677B5F97B35` | `CANONICAL` |
| `GOVRM-P19-JSON-SOURCE` | AC2、AC4 / 原始输入 pin | `verification/P19-UI-FIX-1/resource-manifest.json` | `5dd4b2af0a0c1da00d49d7267ddac11d718cd94c` | `B0772D93AB8ED9182497A43E0761F0D4CCC5560768F806BA86EB8048905C4DC2` | `SOURCE_PIN` |
| `GOVRM-AC1-AC5-RECONCILED` | AC1–AC5 / 集成后复核结果，须覆盖 case 19 修正及 r8 的 AC4 判定 | `verification/GOV-RESOURCE-MANIFEST-JSON-1/ac1-ac5-manifest-support.md`（更新后） | 待产生的实际 evidence commit | 待对更新后文件计算 SHA-256 | `CANONICAL` |
| `GOVRM-AC4-RECONCILED` | AC4 / 花括号保真、7 项资源与 4 个 count 声明值保留；说明 `moved=6` 是资源数组外的日志改名动作 | `verification/GOV-RESOURCE-MANIFEST-JSON-1/ac4-brace-and-counts.md`（更新后） | 待产生的实际 evidence commit | 待对更新后文件计算 SHA-256 | `CANONICAL` |
| `GOVRM-HANDOFF-V2` | 交付 Gate / Handoff | `doc/handoffs/GOV-RESOURCE-MANIFEST-JSON-1-7d09143d6.md` | `f0fbd512607149adfa42e55af72d1661c31e75c0` | `E68FB8BF10F924D32E4B663E0449D9A72AB757E38275664B3121E9069AD89933` | `CANONICAL` |

`ac1-ac5-manifest-support.md` 早期文件 SHA-256 为 `012A889DD62E739B748119482E073FBACA28D725EC379EA3E03D21DB834F5982`（含文件提交 `eab5531b03d7150fa2ad6151b4626f586fe77279`）；`ac4-brace-and-counts.md` 当前 SHA-256 为 `E4590E75E29D8C2928E5F33F27CA5A91C5D96A3AC33085E70ACDD576BEEE4B7F`（含文件提交 `7da0d9a07745c9aefbcbb11e67e822c4169eb165`）。因内容结论已过时，这两组值只用于识别历史文件，不建议登记为当前 AC canonical evidence。

### Resource Manifest 建议行

保留现有 33 条 worktree 未跟踪状态，不删除/迁移。worktree 含 9 个尚未集成的独有提交，也含与本 Task 无关的未知未跟踪文件；这使 `PRESERVE_UNKNOWN` 比 `DELETE_SAFE` 合适。测试 fixture 与工具源码是交付物，应保留。下表 hash 为当前文件 SHA-256；路径按仓库相对路径或实际 worktree 路径记录。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task worktree | `G:\CODEX\New Manga\.agents\worktrees\GOV-RESOURCE-MANIFEST-JSON-1` | `PRESERVE_UNKNOWN` | 原路径 | `HEAD=a2ca297f1b5775a0d5fb5fc8efcc2281bc4013c2; git status --porcelain=33 行` | 9 个独有提交尚待集成；worktree 有 33 条未跟踪状态（含未知用户文件）；不清理、不删除，移除前须更新 Worktree Safety Inventory 并逐项核实 |
| test fixtures | `tools/governance/tests/fixtures/resource-manifest/cases.json` | `PRESERVE_REFERENCED` | 原路径 | `SHA-256=6DF62BBEE8BFCBA0880DCD1B5305426FA907CC7A0F6086A24815017AAEE734A9` | 被测试驱动引用；保留 |
| test runner | `tools/governance/tests/run-resource-manifest-cases.py` | `PRESERVE_REFERENCED` | 原路径 | `SHA-256=61B7418875F7EBFE5E5F883D5106F377C0C1D7FA4805772EDB4CCA90E0942D3B` | AC5 测试入口；保留 |
| schema / checker | `tools/governance/resource-manifest.schema.json`; `tools/governance/check.ps1` | `PRESERVE_REFERENCED` | 原路径 | 集成后以 Git commit 固定版本 | Task 交付代码；保留 |
| task-env | `New Manga.workspace/task-env/GOV-RESOURCE-MANIFEST-JSON-1/` | `NOT_APPLICABLE` | 无 | task 专属目录检查：不存在 | 仅在 closeout 时复核仍不存在后登记 |
| agent-output | `New Manga.workspace/agent-output/dsh/GOV-RESOURCE-MANIFEST-JSON-1/` | `NOT_APPLICABLE` | 无 | task 专属目录检查：不存在 | 仅在 closeout 时复核仍不存在后登记 |
| exchange | `New Manga.workspace/exchange/GOV-RESOURCE-MANIFEST-JSON-1/` | `NOT_APPLICABLE` | 无 | task 专属目录检查：不存在 | 仅在 closeout 时复核仍不存在后登记 |
| temp output | runner 使用的系统临时目录 | `NOT_APPLICABLE` | 无 | Review 报告称清理后 `tempdir=True` | 集成后复跑确认无残留；否则逐项记录并保留未知项 |

以上 `NOT_APPLICABLE` 以当前核查的 Task 专属路径为限，不代表整个 workspace 的同名目录均不存在。集成 closeout 时需确认目录约定和实际路径，再填实际结果；不确定项保持 `PRESERVE_UNKNOWN`。

## 3.3 Plan / STATUS 与 P19 后继 Task

### Plan / STATUS

当前 `doc/REBASELINE_PLAN.md` 为 **2,496 bytes、36 行、32 条 DAG 数据行**；其中已有 `GOV-RESOURCE-MANIFEST-JSON-1|GOV-PLAN-BUDGET-1|ready` 登记。与 r7 的旧快照“35 行”不同，当前文件已含注册行，不应再次新增重复节点。closeout 时把该行改为终态，例如：

```markdown
|GOV-RESOURCE-MANIFEST-JSON-1|GOV-PLAN-BUDGET-1|done（integration `<merge-commit>`；reviewed `7d09143d6`，delivery `a2ca297f1`）|
```

这是原行更新，不增加 DAG 行。最终字节数会随实际 merge hash 和文字长度变化，应在更新后重新测量。`doc/STATUS.md` 当前没有该 Task 的权威指针；终态时在“当前权威指针”中增加明确的终态引用（Task 文件及 delivery/review/integration hashes），保持现有当前 Active Task 指针不变，并按协议运行指定 Task 检查。当前主 checkout 的 STATUS 仍显示 GOV-PLAN-BUDGET-1 已完成；不需为它新增行。

### P19 兼容视图后继 Task

**需要另立窄范围 Task，但本次暂不释放为 `ready`。** r7 §2.3 明确要求在本 Task 集成后，为 `P19-UI-FIX-1` 兼容视图和 Task 检查重跑单独释放 Task；Task 本身也明确禁止在本范围修改 P19 Task。当前 GOV Task 尚未集成，实际 `integration_commit` 未生成；目标 Task 的 base、branch/worktree 和冻结允许路径因此尚无可填的真实值。先完成本 Task 集成与 closeout，再由 Codex按模板创建后继 Task、登记 STATUS/Plan 和 `allowed_paths`，随后才能置 `ready`。禁止此时虚构 base/hash 或让 DSH 越过释放 Gate。

后继 Task 范围冻结建议：仅更新 `doc/tasks/P19-UI-FIX-1.md` 的 Resource Manifest 正文，使其唯一引用 `verification/P19-UI-FIX-1/resource-manifest.json`；不改 JSON 和其它历史证据；使用已集成 checker 执行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P19-UI-FIX-1.md`，将输出、环境、exit code 与 SHA 记入它自己的 evidence_dir。完整 `ready` frontmatter 必须等 integration commit 和 workspace 分配后填写真实 `base_commit`、branch、worktree、owner、reviewer、依赖与 `allowed_paths`；本轮不生成伪造的 ready Task 内容。

### DSH / Codex 执行顺序

1. DSH 不再改动已固定的 `a2ca297f1` delivery 分支；保留现有 Task worktree 与 33 条未跟踪状态，逐项辨明归属，不能自行清理或搬走。
2. Codex/文件所有者先处理主 checkout 1,235 条与 worktree 33 条状态：只对明确归属项做安全保存；更新 Worktree Safety Inventory。不能确认的保持原路径并记 `PRESERVE_UNKNOWN`。
3. 在主 checkout 的目标分支执行 §3.1 命令，保留 `--no-ff` merge commit；记录完整 integration hash 与合并父提交。
4. 在集成树执行 Task 指定的完整离线套件和 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-RESOURCE-MANIFEST-JSON-1.md`；另执行全局治理检查。记录命令、环境、逐例结果、stdout/stderr、exit code。任何失败如实保留，不标 PASS。
5. DSH 提供或核对 AC1–AC5 最新证据：明确 a2 用例 19 修复后的真实语法错误分支，按 r8 更新 AC4 结论（7 个 resource 和 4 个 closeout 声明值忠实保留；`moved=6` 属数组外日志改名计数；不生成 P19 解析视图，不改源 JSON）。为更新文件计算 SHA 并记录含文件 commit；Review 证据继续固定 `reviewed_head=7d09143d...`。
6. Codex 补齐 Canonical Evidence 与 Resource Manifest 表，复核引用/进程/未知用户文件；不删除或迁移任何资源。只有 AC 证据、集成验证及资源登记均闭环时，设两个 closeout status 为 `complete`，更新 Task 为 `done`、Plan 行与 STATUS 指针，并运行指定 Task 检查。
7. 完成后 Codex 才释放依赖 `GOV-RESOURCE-MANIFEST-JSON-1` 的 P19 兼容视图窄范围 Task；届时填入实际 integration base 与 workspace/agent 信息并明确 Reviewer。

## 本轮 Git 状态对比

动手前主 checkout `git status --porcelain`：**1,235 行**，SHA-256（UTF-8 状态文本）`1EC39ACEE7E3CD9EBD8390DC0B1A6417262476C3D53166FCCD53DFC9C31044FD`；主 branch/HEAD 为 `antigravity/P09-AC3-DELETE-HARDEN-1` / `bb3abad16fc16aa7fc263718e182304a7fd84344`。本轮未执行 Git 写命令，也未运行 merge 或测试。文件写入后应再核对：允许差异仅是新增本文件对应的一条状态；其余既存状态必须保留。
