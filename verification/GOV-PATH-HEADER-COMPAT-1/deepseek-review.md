## Review: GOV-PATH-HEADER-COMPAT-1

```yaml
task_id: GOV-PATH-HEADER-COMPAT-1
reviewer: DeepSeek (independent, read-only)
base_commit: 93c4eb2ca（要求值；完整 SHA 未能解析，见 V-1）
reviewed_head: 1a958d770299e57a1dad44feaae5ad4f630c298e（声明值；未能本机复核）
decision: changes_requested
```

### 结论先行

**不批准本 head 集成。** 代码静态切片未发现 P0/P1 级缺陷，但本次审查的强制门禁（HEAD 一致性、测试重跑、`git diff --check`、12 条 pin 的原始字节 SHA256、同快照新旧 guard 对比）**全部无法执行**：本会话 `pwsh` 在沙箱初始化阶段连续两次失败，未运行任何 Git/Python 命令。按"不能假装 PASS"原则，只能给出 `changes_requested`（验证阻断型，非代码缺陷判定）。工作树/分支继续保留。

### Architecture

静态读取 `tools/governance/clean_workspace.py` L1259–1281 与 L1289–1379：

- `_exact_column` 与 `_duplicate_identity_columns` 各自仅新增一处**完全相同**的归一化：先 `strip().lower()`，再把与字面量 `path（仓库相对路径或绝对路径）` **完全相等**的单元映射为 `"path"`。是精确相等，不是前缀/包含/子串匹配，无法泛化出任意中文别名。
- 该归一化同时进入重复列检测，因此 `path`+alias、alias+`path`、alias+alias 均计为 `path x2`，走 `TABLE_DUPLICATE_IDENTITY_COLUMN` 并 `continue`，不会静默取首列。
- 未知标签（`path（任意文本）`、`path (relative path)`、`路径`、`note`）不匹配字面量 → 返回 `None` → 仍走 `TABLE_SCHEMA_INCOMPLETE`；行宽不符仍由 `parse_table_block` 抛 `TABLE_ROW_ARITY`；`source_path`/`destination_path`/`disposition` 未受影响（测试第 5 例专门断言）；资源清单分支逻辑未改，JSON/disposition/不可读/模糊环境路径的处理点未触碰。
- 改动量确为两函数各 +2 行级，无新依赖、无 Schema/API 变更，未触及历史 Task/证据/pin 或例外清单（就可见内容而言）。

### Verification（仅基于已落盘证据的静态核对，非重跑）

| 证据 | 观察 | 状态 |
|---|---|---|
| `new-tests.log` | `Ran 5 tests` / `OK` | 与声明一致，未复跑 |
| `declaration-tests.log` | `Ran 29 tests` / `OK` | 与声明一致，未复跑 |
| `hardening-tests.log` | `Ran 80 tests` / `OK`（含双 replay 15×REJECT、deleted 0、violations 0） | 与声明一致，未复跑 |
| `baseline-discriminator.log` | `Ran 5 tests` / `FAILED (failures=5)` | 符合旧 guard 抓不到新 fixture 的预期；**未见 EXIT 行**，exit=1 未直接取证 |
| `real-comparison.json` | `errors 77→32`、`protected_roots 1280→1690`、`remaining_errors` 列表在案 | 数值与报告一致；绝对根数为快照值，按用户说明不作当前固定值 |
| `incident-replay-*.json` / `replay-*-executed.log` | 各 15 REJECT、`deleted: 0`、`violations: 0` | 与声明一致；真实资源删除无法独立确认 |
| 12 条 evidence pin | **SHA256 未计算** | **未验证**（需 `Path.read_bytes()` 与 `git show <commit>:<path>`，shell 不可用） |
| `git diff --check base..head` | 未执行 | **未验证** |

关键缺口：lints/测试的 exit code、`reviewed_head` 是否确为 `1a958d77…`、base 是否解析为 `93c4eb2c…` 全无本机证据。另外 EV-12 指向 `9ea78f1a`、其余指向 `9f59537f`，与 `delivery_head` 三者关系只能在 Git 可用时核对。

### Findings

**P1（阻断，环境）— 命令行通道不可用，强制门禁未执行。**
两次调用均在同一处失败：

```text
SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.workspace\worktrees\GOV-PATH-HEADER-COMPAT-1)
EXIT: 无（工具在进程启动前的沙箱 ACL 授权阶段失败，非命令退出码）
```

已按"同一失败限 2 次"停止，未尝试改 ACL/配置，未做第三次重试。因此 `git rev-parse`、`git status`、`git diff base..head`、`git diff --check`、python unittest 均未产生任何输出。**本 head 的集成门禁实质处于未审计状态**，需在 shell 可用的环境重做（或由可执行环境的 Reviewer/Owner 补证）。

**P2（文档，需集成前修正）— Task 副本 `allowed_paths` 被字符串替换污染。**
`doc/tasks/GOV-PATH-HEADER-COMPAT-1.md` L27 现为：

```text
doc/REe7cbcada6d1a5c01f9c55e888e30c3efba20e1ffLINE_PLAN.md
```

这是把 `REBASELINE_PLAN.md` 中的 `BASE` 误替换成 base commit 的结果。该条目指向不存在的路径，若被用于作用域/存在性校验会削弱治理元数据。请修正为 `doc/REBASELINE_PLAN.md`，并确认它是 head 内提交还是工作树未提交副本（本次无法用 `git status` 区分）。

**P2（元数据一致性）— `base_commit` 双值。**
Task frontmatter 记 `e7cbcada6d1a…`，而本次审查基线为 `93c4eb2ca…`。若前者是 Task 创建时基线、后者是实际 diff 基线，应在 Task 中显式写明二者关系，避免后续审计误用范围。

### 对批准范围的表态

- 本 Review **不批准** GOV-PATH-HEADER-COMPAT-1 的 `1a958d77…` 集成（原因：门禁未执行，非代码否决）。
- 更不批准清理、父收敛 Task done、或"只有 main"的任何结论；剩余 32 errors 从静态代码路径看仍以 error 形式 fail-closed，但该结论同样待实跑确认。
- 工作树 `GOV-PATH-HEADER-COMPAT-1` 与分支 `codex/gov-path-header-compat-1` 必须保留。本次未修改任何文件、租约、分支或 Git 引用，未调用 apply，未联网，未派发子任务。

### 推荐下一步

在 shell 可用、且不改动仓库/ACL 的前提下重开独立 Review：先 `git rev-parse HEAD` 确认 `1a958d77…`，再跑 `python -B -m unittest discover -s tools/governance/tests -p test_path_header_compat.py`（预期 5/0skip exit0）、既有 29 声明回归、`git diff --check 93c4eb2ca..1a958d77`，并用 `Path.read_bytes()` 与 `git show` 原始 bytes 复算 12 条 pin 的 SHA256；同时修正上述两处 Task 文档 P2。全部通过后方可转为 approved。
