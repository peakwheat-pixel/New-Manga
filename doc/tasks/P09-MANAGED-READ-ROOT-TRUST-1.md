---
id: P09-MANAGED-READ-ROOT-TRUST-1
title: 托管文件读取/导出路径的 root 可信性（R5b P2 转交）
kind: security-hardening
status: in_review
approval: user_released_20261021
suggested_owner: DeepSeek Harness
owner: p09-root-trust
reviewer: Codex
depends_on: [P09-AC3-DELETE-HARDEN-1]
base_commit: b8a1e519703f13af73b320dded117004b4bb189a
branch: dsh/P09-MANAGED-READ-ROOT-TRUST-1
worktree: G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1
integration_commit: null
delivery_head: 56aee75ae8fa88913655f27c019345224414096d
canonical_evidence_status: pending
resource_closeout_status: pending
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
      （`logs/ac1-after-fix.txt`；修复前 exit 1，`logs/ac1-before-fix.txt`）。
- [x] **AC2**：**合法读取不回归**（含链接合法使用场景；链接策略取舍见上节并记录链接合法使用结论）。
      **结果 MET**：8 处测试均含「换 root 前合法读取成功」断言；8 个套件逐套件 base/current 计数一致
      （core 564、storage 87、m2_resource_channel 106、security 29→40、library 63、reading_export 141、
      export 13、m2_acceptance 37），runner exit 0；链接策略与结论见
      `verification/P09-MANAGED-READ-ROOT-TRUST-1/DESIGN-expected-identity.md` 第四节、`SITE-MATRIX.md`。
- [x] **AC3**：**8 处逐个**有测试或探针，**不接受「模式相同所以一起算」**。
      **结果 MET**：`ac3-discrimination.py` exit 0；同一测试文件在 base 源码快照上 8/8 site 测试
      FAIL、当前 8/8 PASS（`logs/ac3-discrimination.txt`）；逐处映射 `SITE-MATRIX.md`。
- [x] **AC4**：不引入新依赖或契约变更。
      **结果 MET**：`logs/ac4-change-files.txt` 只含 4 个实现/测试文件 + 本 Task 文档/证据；
      无 `pyproject/requirements/package.json/Cargo.*`、无 `doc/contracts/**`、无 Schema/ACL 变更。
- [x] **AC5**：`P09-AC3-DELETE-HARDEN-1` 的 9 个探针**不回归**。
      **结果 MET**：`ac5-run-delete-probes.py` exit 0；9/9 与基线一致（`logs/ac5-delete-probes.txt`；
      仅改路径常量的副本 diff：`ac5-delete-probes/PATH-ADAPTATION.diff`）。

## 测试要求

| 场景/AC | 命令/步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac1-r5b-repro.py` | Windows、Python 3.14.6、worktree | **exit 0**；base=VULNERABLE、current=SAFE（修复前 exit 1、双 VULNERABLE） | `logs/ac1-after-fix.txt`、`logs/ac1-before-fix.txt` |
| AC1/AC3 | `C:/Python314/python.exe -m pytest tests/security/test_p09_managed_read_root_trust.py -q` | 同上 | **11 passed** | `logs/suite-security.log`（该 suite 40 = 29 旧 + 11 新） |
| AC3 | `C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac3-discrimination.py` | 同上（内部取 base 源码快照） | **exit 0**；8/8 site 测试 base FAIL、current PASS | `logs/ac3-discrimination.txt`、`SITE-MATRIX.md` |
| AC2 | `pwsh -NoProfile -File verification/P09-MANAGED-READ-ROOT-TRUST-1/run-suites.ps1` | 同上 | **exit 0**；core 564 / storage 87 / m2_resource_channel 106 / security 40 / library 63 / reading_export 141 / export 13 / m2_acceptance 37 | `logs/summary.txt`、`logs/suite-*.log`、`logs/baseline/` |
| AC5 | `C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac5-run-delete-probes.py` | 同上 | **exit 0**；9/9 与基线一致 | `logs/ac5-delete-probes.txt`、`.json` |
| AC4 | `git diff --name-only b8a1e5197..56aee75ae`（记录于 `logs/ac4-change-files.txt`） | 同上 | 仅 4 个实现/测试文件 + 本 Task 文档/证据；无依赖/契约/Schema/ACL 变更 | `logs/ac4-change-files.txt`、`AC-RESULTS.md` |

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

## 交付与运行记录

- **设计（第一交付物）**：`verification/P09-MANAGED-READ-ROOT-TRUST-1/DESIGN-expected-identity.md`
  —— commit `a5147eed8`（先于产品代码提交；Task `in_progress` 同提交）。
- **实现 head**：`56aee75ae8fa88913655f27c019345224414096d`（3 个源文件 + 11 个测试）。
- **证据提交**：`82b23bac8a961daa5169be5dc5acd3a7b41f1215`（`verification/P09-MANAGED-READ-ROOT-TRUST-1/` +
  Handoff）。
- **Handoff**：`doc/handoffs/P09-MANAGED-READ-ROOT-TRUST-1-56aee75.md`（commit `82b23bac8`）。
- **Review**：尚无（Owner 不得自造 Review；等待 Codex 独立 Review）。
- **实际测试**：见「测试要求」表；全部命令与 exit code 已记录，本文件不含任何未运行项被写成 PASS。

## Canonical Evidence

仓库内文件 pin 提交 `82b23bac8a961daa5169be5dc5acd3a7b41f1215`（除设计文档 pin 其自身提交
`a5147eed8`）；仓外原始输入 pin SHA-256。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC1 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/logs/ac1-before-fix.txt` | `82b23bac8` | `89886379C15DD3B1DE1A29DC2EFDE62F5D8707167E3C7B4DC4A6807AECC5694F` | CANONICAL |
| EV-02 | AC1 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/logs/ac1-after-fix.txt` | `82b23bac8` | `0B9E957446C79462C38C4DF4C9201C38B55BC16EB13BFADDFB300A94128155A9` | CANONICAL |
| EV-03 | AC1 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/ac1-r5b-repro.py` | `82b23bac8` | `BBF488E84916BB968E27B562ACE721FB304E1B8083BA91B0E1E506FC362C2B24` | CANONICAL |
| EV-04 | AC3 | `tests/security/test_p09_managed_read_root_trust.py` | `82b23bac8` | `8635C40CEEDB51261122420AB2A73674CAE15314DC7EB7EA7A4DFD1BC982B25D` | CANONICAL |
| EV-05 | AC3 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/ac3-discrimination.py` | `82b23bac8` | `A15C015B691107E6A0D48DA308376B3261836BF6A5FFC4696D95DB22972D691C` | CANONICAL |
| EV-06 | AC3 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/logs/ac3-discrimination.txt` | `82b23bac8` | `DC4945AB821EA82E5B3E6A4180AF1824EC57497B00452CD5049DEACE5F57E38D` | CANONICAL |
| EV-07 | AC3 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/SITE-MATRIX.md` | `82b23bac8` | `166B62103C27B39DC96EE3AF97F39052A9577E41F65A67778F94D104DEAA6E28` | CANONICAL |
| EV-08 | AC2 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/logs/summary.txt` | `82b23bac8` | `D508D2562ADE5F895812CF0DE3E602C054F36806B502CCB91D777C4A1F278115` | CANONICAL |
| EV-09 | AC2 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/logs/baseline/baseline-core.log` | `82b23bac8` | `B70F50E311E3458C4F19C39037EAEEECA5088449AE157140782053E55DD3D1C9` | CANONICAL |
| EV-10 | AC4 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/logs/ac4-change-files.txt` | `82b23bac8` | `97A5E982000A79003700A6FF2F8C3FB75658CA5A3CC02407DCEA57C0366C81FA` | CANONICAL |
| EV-11 | AC5 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/logs/ac5-delete-probes.txt` | `82b23bac8` | `6E04762BA908699BB152C98760FD60F3ED5A411ABD394E58EBF9F1DC9DEE4AE0` | CANONICAL |
| EV-12 | AC5 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/ac5-delete-probes/PATH-ADAPTATION.diff` | `82b23bac8` | `29A2256658DF016DBBC6B089AEA1F404924F897C57F3BFB6F27CBDED615A055A` | CANONICAL |
| EV-13 | AC1–AC5 汇总 | `verification/P09-MANAGED-READ-ROOT-TRUST-1/AC-RESULTS.md` | `82b23bac8` | `0BD708B2805A3836DA613A6B66599DE8AC0D29F1019BFE18E11CAAB8561621BA` | CANONICAL |
| EV-14 | 设计（第一交付物） | `verification/P09-MANAGED-READ-ROOT-TRUST-1/DESIGN-expected-identity.md` | `a5147eed8` | `A75AF59E447025CC0927532E56857412DFC29536F3DEA9A21755FC91ACEA27AE` | CANONICAL |
| EV-15 | 交付 Handoff | `doc/handoffs/P09-MANAGED-READ-ROOT-TRUST-1-56aee75.md` | `82b23bac8` | `72714B63C72FBC7D61C34994483F1A017985F6ABE7D2D031BF41E7C077D36CB6` | CANONICAL |
| SP-01 | 来源（R5b 原始复现） | `G:/CODEX/New Manga.workspace/agent-output/coordinator/codex-r5b-result.md` | — | `B8D7CA7A1988FFB9C755AB53E48EFC9D884171E1C42877B00CD56E6CD0AC23AD` | SOURCE_PIN |
| SP-02 | 来源（R6 原始复现） | `G:/CODEX/New Manga.workspace/agent-output/coordinator/codex-r6-result.md` | — | `E0C5BE3E203FAEFFD47943C0D558B9BD72C547776BA8112F27DF14CF7529E424` | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | `G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1` | PRESERVE_REFERENCED | 本路径 | — | 本 Task 交付；删除须 Codex 按 Worktree Safety Inventory 另行授权 |
| temp（探针临时目录） | `%TEMP%/p09-ac1-*`、`%TEMP%/p09-ac3-*`（`git archive` 解出的 base 源码 + driver） | NOT_APPLICABLE | — | — | 探针自建自清（`finally: shutil.rmtree`）；不触碰用户数据/仓库 |
| scratch（AC5 探针夹具） | `verification/P09-MANAGED-READ-ROOT-TRUST-1/_scratch/` | NOT_APPLICABLE | — | — | `ac5-run-delete-probes.py` 前后清理（先 `os.rmdir` 移除 junction 再删目录）；证据目录中无残留 |
| agent-output | 无（本 Task 不在仓外新建 agent-output；只读引用 SP-01/SP-02） | NOT_APPLICABLE | — | — | 证据全部在 `verification/P09-MANAGED-READ-ROOT-TRUST-1/` |

## Closeout Record

- Closeout date / Codex：待关闭时填写（本 Task 只到 `in_review`，不关闭）。
- canonical_evidence_status：`pending`（等待 Codex Review/收口确认）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：0（本 Task 不执行清理）。
- 未关闭项及保留原因：残余风险四项见设计文档第六节；Rust/前端/packaging 未运行（不在 AC 范围）。
- 当前指针清理：不适用（Owner 不改 STATUS/Plan 指针）。
