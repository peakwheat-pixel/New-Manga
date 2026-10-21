---
id: P09-MANAGED-READ-ROOT-TRUST-1
title: 托管文件读取/导出路径的 root 可信性（R5b P2 转交）
kind: security-hardening
status: done
approval: user_released_20261021
suggested_owner: DeepSeek Harness
owner: p09-root-trust
reviewer: Codex
depends_on: [P09-AC3-DELETE-HARDEN-1]
base_commit: b8a1e519703f13af73b320dded117004b4bb189a
branch: dsh/P09-MANAGED-READ-ROOT-TRUST-1
worktree: G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1
integration_commit: 155f7d3f29ae2c81ba40efa06a87ed32ba984eae
delivery_head: 2a0ff8819dceff0849a2ea783ba202769e18078b
previous_delivery_head: 56aee75ae8fa88913655f27c019345224414096d
review_round: 2  # 第 1 轮 Codex changes_requested（R-001/R-002/R-003 + 建议 R-004/R-005）已返修
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/P09-MANAGED-READ-ROOT-TRUST-1
allowed_paths:
  - src/bootstrap/core_service.py
  - src/bootstrap/core_assembly.py
  - src/infrastructure/resource_channel/handle_resolver.py
  - tests/security
  - verification/P09-MANAGED-READ-ROOT-TRUST-1
  - doc/tasks/P09-MANAGED-READ-ROOT-TRUST-1.md
  - doc/handoffs
created: 2026-10-19
---

# P09-MANAGED-READ-ROOT-TRUST-1

## 来源

由 `P09-AC3-DELETE-HARDEN-1` 的 R5b 复审转出（用户裁决路线 B）。**删除路径加固不含读取路径**，本 Task 单独处理。

- 草案：`verification/P20-CLOSE-BOUND-HARDEN-2/r5b-p2-read-path-draft.md`
- 前序交付：`verification/P09-AC3-DELETE-HARDEN-1/HANDOFF.md`
- 原始复现：R5b findings 第 3/4 项、R6 findings（P2 `handle_resolver`）；coordinator 输出见
  `G:/CODEX/New Manga.workspace/agent-output/coordinator/codex-r5b-result.md`、`codex-r6-result.md`
  （仓外原始输入，按 sha256 pin，见 Canonical Evidence）。

## 设计答案（第一交付物，实施前冻结）

**「期望身份」从哪来？** —— 见 `verification/P09-MANAGED-READ-ROOT-TRUST-1/DESIGN-expected-identity.md`（本 Task 第一交付物）。

摘要：

> **期望身份 = 装配时对配置根实际打开的那一个句柄所携带的对象身份
> `(volume_serial, file_index)` + 该句柄报告的规范路径（`GetFinalPathNameByHandleW`）；
> 配置根的 `os.path.abspath` 词法路径另存，作为把数据库相对引用折算成「根下相对段」的
> 名字侧基准。每次读取先按词法基准冻结期望，再重新打开配置根并比对对象身份，随后在
> 已验对象下打开目标、要求句柄规范路径 == 快照规范根 + 词法相对段，最后通过同一句柄读取。**

关键性质：快照在**任何业务读取之前**取得；对象身份不随名字解析改变；竞态只能改变「名字现在指向谁」，
改变不了快照里的对象；校验与使用是同一个句柄（不再有「检查后按名字再打开一次」的窗口）。

第 8 处 `resolve_namespace_identity` 的局部版本：词法 `expected = os.path.abspath(str(path))`
在任何文件系统访问前固定 → 单次打开 → 规范路径/身份只来自该句柄 → `final == expected` 才接受。
既有「盘符根起任一 reparse 即拒绝」策略保留（derived/GC 域契约，不放宽）。

## 范围（8 处，逐处验收）

Task 表行号来自 R5b 审计时（`34fe1069f`）；base `b8a1e51` 实际行号如下（修改前）。

| # | 位置（base 实际行号） | 复现者 |
|---|---|---|
| 1 | `src/bootstrap/core_service.py:518-537` `assemble_production_core.read_original_page`（Task 表 464–467） | R5b |
| 2 | `src/bootstrap/core_service.py:2070-2075` `handle_resolve_page_resource`（Task 表 1923–1926） | R5b |
| 3 | `src/bootstrap/core_service.py:2636-2643` `_checked_managed_path`（+ `_reader_sha256` 2645-2650；Task 表 2490–2493） | R5b（AC1 原始复现点） |
| 4 | `src/bootstrap/core_service.py:2679-2694` `_is_protected_export_target`（Task 表 2533–2542） | R5b |
| 5 | `src/bootstrap/core_assembly.py:207-233` `_ManagedPageCatalog.image_state`（Task 表 227–230） | R5b |
| 6 | `src/bootstrap/core_assembly.py:235-242` `_ManagedPageCatalog._uri_within`（Task 表 236–239） | R5b |
| 7 | `src/bootstrap/core_assembly.py:262-288` `_ManagedPageImageSource._page_image`（Task 表 270–273） | R5b |
| 8 | `src/infrastructure/resource_channel/handle_resolver.py:602-620` `resolve_namespace_identity` | R5b 与 R6 各自独立复现 |

**第 8 处的复现细节**（R6）：在 `_lstat_reparse_walk(path)` 之后、`path.resolve()` 时注入祖先 junction →
函数接受并返回 `outside\derived`，外部字节可读。

**根因**：把句柄的最终路径与「已被重定向后的 `resolved` 名字」比对 —— **拿被污染的值验证自己**。

## 与删除路径的本质差异（决定了这不是接线）

| | 删除（已完成）| 读取（本 Task）|
|---|---|---|
| 手段 | 句柄 disposition，一次打开即可 | 句柄需保持打开并持续读，窗口更长 |
| 现有基建 | `win_unlink.unlink_by_handle` | **无** —— 新增读取原语 |
| 修法性质 | 接线 | **新设计** |

## 链接策略（AC2 取舍，已冻结）

- **配置根之上（祖先）或根本身是 reparse**：**允许**，当且仅当对象身份仍等于启动快照
  （保留「数据目录迁移后留 junction」「data root 是链接」两种合法部署）。
- **配置根之下（managed 布局内部）任何 reparse 段**：**拒绝**（与 `remove_managed` 删除路径既有语义一致）。
- **「任一祖先 reparse 即拒绝」未采用**：会破坏上两类合法部署，且对象身份快照已提供更强判据。
- `resolve_namespace_identity` 的既有「盘符根起拒绝 reparse」策略保留，不因本 Task 放宽。

## 禁止范围

不改 IPC 契约、Schema、ACL、依赖；**不改删除路径**（`win_unlink.py`、`managed_storage.remove_managed`、
`render_preview.py`、`tile_cache_sweep.py`、`backup.py` 均不动）；不采用「任一祖先段是 reparse 就拒绝」
作为默认方案（已在上节显式记录取舍）；不扩大范围；不执行任何真实删除/移动/清理；不 push/merge；
不修改主仓库或其他 Task/草稿。

## Acceptance Criteria

- [x] **AC1**：R5b 的复现（祖先 junction → 读出 `outside bytes`）**被拒绝**。
      **结果 MET**：`ac1-r5b-repro.py` 在同一 driver 上对 base 快照 = VULNERABLE（读到 `OUTSIDE`）、
      当前 = SAFE（`P16WireError`，outside bytes 未读出）；调用 exit 0
      （返修后重跑 `logs/ac1-after-fix.txt`；修复前 exit 1，`logs/ac1-before-fix.txt`）。
- [x] **AC2**：**合法读取不回归**（含链接合法使用场景；链接策略取舍见上节并记录链接合法使用结论）。
      **结果 MET**：8 处测试均含「换 root 前合法读取成功」断言；8 个套件逐套件 base/current 计数一致
      （core 564、storage 87、m2_resource_channel 106、security 29→**43**、library 63、reading_export 141、
      export 13、m2_acceptance 37），runner exit 0；**R-003：每份 `logs/suite-*.log` 均含执行头
      （shell/os/python/cwd/command）与日志内 `EXIT=<code>`**；链接策略与结论见
      `verification/P09-MANAGED-READ-ROOT-TRUST-1/DESIGN-expected-identity.md` 第四节、`SITE-MATRIX.md`。
- [x] **AC3**：**8 处逐个**有测试或探针，**不接受「模式相同所以一起算」**。
      **结果 MET**：`ac3-discrimination.py` exit 0；**以 pytest 退出码为门槛**（base exit=1、current exit=0），
      `-v` 解析真实结果集合，同一测试文件在 base 源码快照上 8/8 site 测试 FAILED、当前 8/8 PASSED
      （`logs/ac3-discrimination.txt`）；R-001/R-002 补充测试 base FAILED → current PASSED；
      逐处映射 `SITE-MATRIX.md`。
- [x] **AC4**：不引入新依赖或契约变更。
      **结果 MET**：`logs/ac4-change-files.txt`（base..`2a0ff8819`）中 `src/`+`tests/` 只含 4 个
      实现/测试文件；全量 diff 无 `pyproject/requirements/package.json/Cargo.*`、无
      `doc/contracts/**`、无 Schema/ACL 变更。
- [x] **AC5**：`P09-AC3-DELETE-HARDEN-1` 的 9 个探针**不回归**。
      **结果 MET**：`ac5-run-delete-probes.py` exit 0；9/9 与基线一致（返修后重跑
      `logs/ac5-delete-probes.txt`；仅改路径常量的副本 diff：`ac5-delete-probes/PATH-ADAPTATION.diff`）。

## 测试要求

| 场景/AC | 命令/步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac1-r5b-repro.py` | Windows、Python 3.14.6、worktree、scratch=`New Manga.workspace/temp/...` | **exit 0**；base=VULNERABLE、current=SAFE（修复前 exit 1、双 VULNERABLE） | `logs/ac1-after-fix.txt`、`logs/ac1-before-fix.txt` |
| AC1/AC3 | `C:/Python314/python.exe -m pytest tests/security/test_p09_managed_read_root_trust.py -q` | 同上 | **14 passed**（该 suite 43 = 29 旧 + 14 本 Task） | `logs/suite-security.log` |
| AC3 | `C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac3-discrimination.py` | 同上（内部取 base 源码快照；`-v` + 退出码门槛） | **exit 0**；base exit=1、current exit=0；8/8 site + 3 条 R-001/R-002 测试均 FAILED→PASSED | `logs/ac3-discrimination.txt`、`SITE-MATRIX.md` |
| AC2 | `pwsh -NoProfile -File verification/P09-MANAGED-READ-ROOT-TRUST-1/run-suites.ps1` | 同上；每份日志含执行头+`EXIT` | **exit 0**；core 564 / storage 87 / m2_resource_channel 106 / security 43 / library 63 / reading_export 141 / export 13 / m2_acceptance 37 | `logs/summary.txt`、`logs/suite-*.log`、`logs/baseline/`（历史） |
| AC5 | `C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac5-run-delete-probes.py` | 同上 | **exit 0**；9/9 与基线一致 | `logs/ac5-delete-probes.txt`、`.json` |
| AC4 | `git diff --name-only b8a1e5197..2a0ff8819 -- src tests`（记录于 `logs/ac4-change-files.txt`） | 同上 | 仅 3 个源文件 + 1 个测试文件；全量列表无依赖/契约/Schema/ACL 变更 | `logs/ac4-change-files.txt`、`AC-RESULTS.md` |

**未运行**：Rust、React/前端、packaging 测试（变更面只在 Python Core 读取路径；不属于 AC1–AC5 范围）。

## 允许修改范围

`allowed_paths` 见 frontmatter。本 Task 唯一新增产品代码载体为
`src/infrastructure/resource_channel/handle_resolver.py` 中的读取原语
（`ManagedRootTrust`）；其余 7 处为同文件的调用点改造。**新增路径
`src/infrastructure/resource_channel/handle_resolver.py` 已在既有 allowed_paths 内。**
`tests/security/`、`verification/P09-MANAGED-READ-ROOT-TRUST-1/`、本 Task 与 `doc/handoffs/`
均在 frontmatter `allowed_paths` 内。

## 依赖、风险与阻塞

- 硬依赖：`P09-AC3-DELETE-HARDEN-1`（已完成/已交付，删除路径不动；AC5 9/9 零回归）。
- 残余风险见设计文档第六节（路径/URI 交接窗口、硬链接、同名替换、内部链接 fail-closed、
  root 被搬走后读取拒绝）。
- 无阻塞。

## Review 返修记录

| 轮次 | 结论 | 说明 |
|---|---|---|
| 第 1 轮（对 `56aee75ae`） | `changes_requested` | R-001 目录准入回归、R-002 AC3 覆盖/断言不足、R-003 AC2 日志证据纪律（P2）；R-004 scratch 位置、R-005 重复收敛（P3 建议） |
| 第 2 轮（对 `2a0ff8819`） | 待 Codex Review | 全部 5 条已逐条返修：目录在**已打开句柄**上拒绝；site3 增导出 hash + 惰性 provider 测试；`ac3-discrimination.py` 以真实结果集合 + pytest 退出码为门槛；8 份 suite 日志加执行头 + `EXIT`；ac1/ac3 scratch 移到 `New Manga.workspace/temp/...`；重复收敛。证据见 `AC-RESULTS.md` 文末「Review 返修对照」与 `doc/handoffs/P09-MANAGED-READ-ROOT-TRUST-1-2a0ff88.md` |

## 交付与运行记录

- **设计（第一交付物）**：`verification/P09-MANAGED-READ-ROOT-TRUST-1/DESIGN-expected-identity.md`
  —— 首版 commit `a5147eed8`（先于产品代码提交；Task `in_progress` 同提交）；返修轮补充
  R-001 目录拒绝（见证据提交）。
- **实现 head（返修后，当前）**：`2a0ff8819dceff0849a2ea783ba202769e18078b`
  （3 个源文件 + 14 个测试）。
- **历史实现 head（已被 Review 替换）**：`56aee75ae8fa88913655f27c019345224414096d`（11 个测试）。
- **证据提交（返修后）**：`d305c584540f2979f149618de2d3947f4abcbf28`。
- **历史证据提交**：`82b23bac8a961daa5169be5dc5acd3a7b41f1215`。
- **Handoff（返修轮）**：`doc/handoffs/P09-MANAGED-READ-ROOT-TRUST-1-2a0ff88.md`；
  历史 Handoff `doc/handoffs/P09-MANAGED-READ-ROOT-TRUST-1-56aee75.md` 保留为 HISTORICAL。
- **Review**：Codex 第 1 轮独立 Review 结论 `changes_requested`（R-001/R-002/R-003 + 建议
  R-004/R-005），本轮已逐条返修；**尚无第 2 轮 Review**（Owner 不得自造 Review）。
- **实际测试**：见「测试要求」表；全部命令与 exit code 已记录，本文件不含任何未运行项被写成 PASS。

## Canonical Evidence

仓库内文件 pin 证据提交 `d305c584540f2979f149618de2d3947f4abcbf28`；仓外原始输入 pin SHA-256。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC1 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/logs/ac1-before-fix.txt` | `d305c5845` | `89886379C15DD3B1DE1A29DC2EFDE62F5D8707167E3C7B4DC4A6807AECC5694F` | CANONICAL |
| EV-02 | AC1 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/logs/ac1-after-fix.txt` | `d305c5845` | `37E635968529D5C4C9BB1B0630F01558BEE9034708B3BAF799E15A17E7CA48EC` | CANONICAL |
| EV-03 | AC1 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/ac1-r5b-repro.py` | `d305c5845` | `7A2AD52C77E83DB0B1253E0C0191B6AF89BE55C208A24FB3F45297B86EC35590` | CANONICAL |
| EV-04 | AC3 | `tests/security/test_p09_managed_read_root_trust.py` | `d305c5845` | `2C3FEC921BE7EE24ED86FC22B94B8F5A5EC77680AA575D00C8B8F733A056E1C8` | CANONICAL |
| EV-05 | AC3 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/ac3-discrimination.py` | `d305c5845` | `D774CDEF109CB4CA3DEF4ADEE92301EFC39F588D2BF63906F6FAFAB79D8842DA` | CANONICAL |
| EV-06 | AC3 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/logs/ac3-discrimination.txt` | `d305c5845` | `42C8E95C57B0C563262B6F9521B675535842DD9DBD48CEA0D4FE42B92BC001AB` | CANONICAL |
| EV-07 | AC3 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/SITE-MATRIX.md` | `d305c5845` | `4FDC11ADB8B66E3D054E2133E04249F88C10D3435CE9B772780296DB6C684B92` | CANONICAL |
| EV-08 | AC2 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/logs/summary.txt` | `d305c5845` | `F9DA9A0803690E1CEDC168EFF061218908A7229B16E60FD184A401C401977809` | CANONICAL |
| EV-09 | AC2 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/logs/suite-security.log`（带头+EXIT） | `d305c5845` | `5E77C66655824D09986E1EDCF7C47D700CA7AE8E4314D59ABAA9AD831B135250` | CANONICAL |
| EV-10 | AC2 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/logs/suite-core.log`（带头+EXIT） | `d305c5845` | `AD1EF2252B6832D6FC7150C2C990D303C56E9B7BC7BA56FB99E9BC92071801A3` | CANONICAL |
| EV-11 | AC2 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/logs/baseline/baseline-core.log`（历史基线） | `d305c5845` | `B70F50E311E3458C4F19C39037EAEEECA5088449AE157140782053E55DD3D1C9` | CANONICAL |
| EV-12 | AC4 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/logs/ac4-change-files.txt` | `d305c5845` | `1EFDBD87FF279438C9C013E65DD6EB1CE0A302B050C77309C16B458DF6214EA1` | CANONICAL |
| EV-13 | AC5 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/logs/ac5-delete-probes.txt` | `d305c5845` | `6E04762BA908699BB152C98760FD60F3ED5A411ABD394E58EBF9F1DC9DEE4AE0` | CANONICAL |
| EV-14 | AC5 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/ac5-delete-probes/PATH-ADAPTATION.diff` | `d305c5845` | `29A2256658DF016DBBC6B089AEA1F404924F897C57F3BFB6F27CBDED615A055A` | CANONICAL |
| EV-15 | AC1–AC5 汇总 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/AC-RESULTS.md` | `d305c5845` | `1BD235CC6E281EB10593802FFB081BCB94722A48DE52C98AE1FA17E7EB420AA1` | CANONICAL |
| EV-16 | 设计（第一交付物） | `verification/P09-MANAGED-READ-ROOT-TRUST-1/DESIGN-expected-identity.md` | `d305c5845` | `58576C08B86B07790474A2388F19CB7DB3E404713AFBBC5732DC487F3FDC0314` | CANONICAL |
| EV-17 | 交付 Handoff（返修轮） | `doc/handoffs/P09-MANAGED-READ-ROOT-TRUST-1-2a0ff88.md` | `d305c5845` | `598B568AC0EBC7ADE9C56CCB05031ED3C4C3E4CD2D7247900FED4F5B2B23797D` | CANONICAL |
| EV-18 | 证据工具（日志合规） | `verification/P09-MANAGED-READ-ROOT-TRUST-1/run-suites.ps1` | `d305c5845` | `417295293C5DF76EA5385148FE31ACD342F323EA4EDBA6FCFA09A34567BC275A` | CANONICAL |
| SP-01 | 来源（R5b 原始复现） | `G:/CODEX/New Manga.workspace/agent-output/coordinator/codex-r5b-result.md` | — | `B8D7CA7A1988FFB9C755AB53E48EFC9D884171E1C42877B00CD56E6CD0AC23AD` | SOURCE_PIN |
| SP-02 | 来源（R6 原始复现） | `G:/CODEX/New Manga.workspace/agent-output/coordinator/codex-r6-result.md` | — | `E0C5BE3E203FAEFFD47943C0D558B9BD72C547776BA8112F27DF14CF7529E424` | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | `G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1` | PRESERVE_REFERENCED | 本路径 | — | 本 Task 交付；删除须 Codex 按 Worktree Safety Inventory 另行授权 |
| temp（探针 scratch） | `G:/CODEX/New Manga.workspace/temp/P09-MANAGED-READ-ROOT-TRUST-1/`（ac1/ac3 的 base 源码快照与 driver，R-004） | NOT_APPLICABLE | — | — | 探针自建自清（`finally: shutil.rmtree`）；不写仓库、不用系统 `%TEMP%` |
| scratch（AC5 探针夹具） | `verification/P09-MANAGED-READ-ROOT-TRUST-1/_scratch/` | NOT_APPLICABLE | — | — | `ac5-run-delete-probes.py` 前后清理（先 `os.rmdir` 移除 junction 再删目录）；证据目录中无残留 |
| agent-output | 无（本 Task 不在仓外新建 agent-output；只读引用 SP-01/SP-02） | NOT_APPLICABLE | — | — | 证据全部在 `verification/P09-MANAGED-READ-ROOT-TRUST-1/` |

## Closeout Record

- Closeout date / Codex：2026-10-21；Codex R2 `approved_with_conditions`（唯一条件为归档使用实际 HEAD，已满足）；合并提交 `155f7d3f29ae2c81ba40efa06a87ed32ba984eae`（integration_commit）。
- canonical_evidence_status：`complete`（EV-01..EV-18、SP-01/02 已核）。
- resource_closeout_status：`complete`（worktree PRESERVE_REFERENCED；scratch NOT_APPLICABLE）。
- 删除、迁移、归档数量/字节数：0（本 Task 不执行清理）。
- 未关闭项及保留原因：残余风险四项见设计文档第六节；Rust/前端/packaging 未运行（不在 AC 范围）。
- 当前指针清理：不适用（Owner 不改 STATUS/Plan 指针）；STATUS 已由 Lead 切到 WORKSPACE。
- Review 归档：`doc/reviews/P09-MANAGED-READ-ROOT-TRUST-1-cb767e1b7-codex-r1.md`、`doc/reviews/P09-MANAGED-READ-ROOT-TRUST-1-9f5560bc1-codex-r2.md`。

## 释放记录（2026-10-21，用户授权）

- 用户裁决：释放（"1释放"）。Owner：`dsh-p09-root-trust`（DSH teammate）；Reviewer：Codex。
- Base：`b8a1e519703f13af73b320dded117004b4bb189a`；worktree：`G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1`；分支：`dsh/P09-MANAGED-READ-ROOT-TRUST-1`。
- 首交付物：**"期望身份"来源设计答案**（竞态前固定、不随后续解析变化），再实施 8 处修复；不得扩大到删除路径/契约/Schema/依赖。
