# DeepSeek R1

session: session-89d9de3e-714e-4a87-b0b0-b60526ec5eae；exit0；web_visibility=unverified

**changes_requested**

固定基准：
- `diff_base`: `3d0a36ac04d30eba0906e70218ef9491c5b9ffbc`
- `reviewed head`: `3879cb93632a2498babc9586c431266ad6265fe8`，实测 `HEAD` 与之一致
- 交付/EV commit：`c9d6b19514c7e3ea2b21dc40c37bf705729c69d7`
- canonical cwd：`G:/CODEX/New Manga`

核心判断：五根整体保护、精确来源绑定、共享 scanner 收口、不新增 CLI 通用 broad 开关的方向正确，范围总体克制；未发现 P0。但设计仍有 1 个 P1 规格矛盾和 1 个 P1 激活来源缺口，批准前应修订；这不影响“另冻实现 Task”的总体方向，但不建议现在批准。

## P0

未发现会直接扩大删除权限、缩小五根保护或绕过全部失败关闭的 P0。

## P1

1. **12 个“保全诊断”没有冻结承载方式和计数，且与模型矛盾**
   - `design.md` 要求逐 record 新增 `DECL_BROAD_ROOT_PRESERVED` 可审计诊断，并转换为保全诊断。
   - 但 `ProtectionIndex` 只有 `errors`/`warnings` 两个计数容器；`model-proof.json` 的 `modeled_after_counts.warnings` 仍是 `254`，我的当前内存模拟也是 `warnings=254`。
   - 如果诊断进 `warnings`，after 应为 `266`；如果进 `errors`，错误仍是 `24`，与 `24→12` 矛盾；如果是独立 `diagnostics` 列表，设计没有定义其 schema、序列化、消费者行为。
   - 这会让实现者要么丢掉逐 record 诊断，要么无法满足模型/验收计数。建议明确推荐 `add_warning`，并同步更新模型 after 计数、T01/T12/T16 的断言。

2. **“存在但未被 Git 跟踪”的 policy 会被加载，绕开固定 commit 审查**
   - 设计只规定：policy 不存在且未安装时保持旧行为；已 tracked 但丢失时 fatal。
   - 但没有规定 `tools/governance/broad-root-preservation.json` **存在但 untracked** 时拒绝。当前实现路径会读取并验证它。
   - 这不会直接扩大删除权：六条绑定仍须匹配原行/错误对，且只会增加保护；但它允许一个未经固定 commit 独审的本地 JSON 激活保全收口，违反 T18 的固定 commit 发布语义。
   - 建议：policy 文件存在时要求 `git ls-files -z -- <path>` 精确包含它；否则 `POLICY_UNTRACKED` fatal。T14/T18 增加该负例。

## P2

1. **相邻路径断言应写“无新增根命中”，不能写 `evaluate(repo)==[]`**
   - `G:/CODEX/New Manga` 主仓库自身已有既有保护命中；我的严格空命中检查在该项返回 false，但 `root_delta` 恰为五根，不包含该路径。
   - 模型文字是 `MODEL_NO_NEW_ROOT_HIT_NOT_DELETE_PERMISSION`，语义成立；但 T11/T16 应明确断言“新旧根集合差集不含相邻路径”，否则未来测试会误判。

2. **`scanned` 计数快照和原子性需写明**
   - 收口阶段必须在 `scan_repo_declarations` 计算 `scanned["declarations"/"errors"/"warnings"]` 之前完成，否则返回计数与 index 不一致。
   - `_register_protective` 若中途异常，设计只要求“原子”，未写回滚/两阶段提交。建议实现时先构造全部 pending Declaration，再一次性登记；T01/T12 增加部分失败断言。

3. **非 Git fixture 的“未安装 policy 保持旧行为”未闭合**
   - 设计允许用 `git ls-files` 判断，且 Git 失败 fatal；若旧 fixture 没有 `.git`，会 fatal 而不是保持旧行为。T14 应明确 fixture 必须是 Git 仓库，或提供受控的“无 Git policy 检查”fixture 方式。

## 实测结果（只读）

- 两历史源 `raw SHA`、base blob SHA、status 全部一致；六条 `global_line`、`row_verbatim`、`row_raw_sha256` 全部精确；每条恰好两个对应错误；根集合恰 5 个；`source_keep` 为 4 个 `PRESERVE_REFERENCED` + 2 个 `PRESERVE_UNKNOWN`。
- 现有 parser 对广域行只登记错误、不会登记 `Declaration`，因此 `source_keep`/lexical/real 只能由 policy + pending Declaration 核，不能用现有 `index.declarations` 核；这与设计的收口阶段一致。
- 当前实际 guard：`declarations=2474`、`protected_roots=1804`、`errors=24`、`warnings=254`；24 个错误 identity 与“12 个 removed + 12 个 remaining”完整并集逐项一致，且 24 个均唯一。
- 内存模拟：`2467/1797 → 2479/1802` 是模型快照；当前实测为 `2474/1804 → 2486/1809`，新增恰 `12` Declaration、`5` 根，旧保护集合为子集，剩余错误恰为模型列出的 12 项。`SIMULATION 24→12` **不等于**当前真实 24 已消解。
- 15 项覆盖：12 项 root/future-descendant、ancestor、lexical-prefix sibling 均符合；repo-sibling 按“无新增根”语义成立，按“空 hits”语义不成立，原因见 P2-1。
- 7 份 EV：path 存在、commit `c9d6b195...` 可取、current raw SHA = committed SHA-256 = pin，7/7 全匹配；实际 `parse_markdown_declarations` 得到 `EVIDENCE_PIN=7`、`errors=0`。
- 7 个只读输入：raw SHA、base blob SHA、status、base..HEAD 内容全部未变；`runtime broad-root-preservation.json` 磁盘不存在、未被跟踪；`tools` 在 base..HEAD 和 worktree 均无 diff。
- `99` branches、`137` worktrees；不是“只剩 main”。r212/父 blocked 未被本设计触碰。
- `git diff --check 3d0a36...HEAD` exit 0；`pwsh -NoProfile -File tools/governance/check.ps1` exit 0，PASS，2 个 warning（14 个非终态 Task、STATUS 预算 80%）。
- PowerShell 有 ConstrainedLanguage 非核心类型告警输出到 stderr，但上述命令均 exit 0；未用复杂 PowerShell 逻辑替代 Python。

## 未测 / 不能据此批准的内容

- T01–T18 全部仍是 `PLANNED / NOT_RUN`；本次只做了只读扫描与内存模拟。
- `109` 回归、clean/remove 双 15 事故回放均未跑；它们是未来实施 Gate，不是本设计已通过证据。
- policy loader、严格 schema、漂移/错误对/realpath 负例、三个 CLI 真实行为均未实现；模型不是 loader、绑定器或 CLI。
- 产品/构建测试 NOT_RUN；未执行任何真实资源操作、清理、迁移、GC、prune、push、ACL 或 Legacy 运行。

## 实现门槛

修订 P1/P2 后，才建议另冻 `GOV-BROAD-ROOT-PRESERVATION-IMPL-1`。实施至少须冻结：

- 运行 policy schema、诊断承载方式、tracked 校验、原子登记/回滚和 `scanned` 计数。
- 真实 `24→12` 恰为指定 12 条；其余 12 条 identity 不变；旧保护不减少且新增五根/12 来源。
- 三个消费者共同生效；`remove_worktrees` 不得只依赖名称映射，必须有 path `evaluate`。
- T01–T18 正反例、109 回归、双 15 回放、真实 EV/check/diff、固定 commit 独审和 Codex main 复验。
- 继续禁止 CLI 通用 broad 开关、跳过源文件/整 Review、清理/迁移/GC/prune/push、修改旧 pin/69 例外/其它消费者。

**结论：设计方向可保留，但当前不批准；请 Codex 先修订上述 P1/P2，重新固定 head 后由 DeepSeek 复审。设计批准本身也不等于工具实现授权或资源清理授权。**
