---
id: P09-MANAGED-READ-ROOT-TRUST-1
title: 托管文件读取/导出路径的 root 可信性（R5b P2 转交）
kind: security-hardening
status: in_progress
approval: user_released_20261021
suggested_owner: DeepSeek Harness
owner: p09-root-trust
reviewer: Codex
depends_on: [P09-AC3-DELETE-HARDEN-1]
base_commit: b8a1e519703f13af73b320dded117004b4bb189a
branch: dsh/P09-MANAGED-READ-ROOT-TRUST-1
worktree: G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1
integration_commit: null
delivery_head: null
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

- [ ] **AC1**：R5b 的复现（祖先 junction → 读出 `outside bytes`）**被拒绝**。
      证据：`verification/P09-MANAGED-READ-ROOT-TRUST-1/ac1-r5b-repro.py` 的 base-vs-current 差分
      （base 读出 `OUTSIDE`；当前拒绝）+ `tests/security/test_p09_managed_read_root_trust.py` 对应测试。
- [ ] **AC2**：**合法读取不回归**（含链接合法使用场景；链接策略取舍见上节并记录链接合法使用结论）。
      证据：8 处各自的「换 root 前合法读取成功」断言 + `tests/core`、`tests/storage`、
      `tests/m2_resource_channel`、`tests/security`、`tests/library`、`tests/reading_export`、
      `tests/export`、`tests/m2_acceptance` 套件结果（命令与 exit code 记录在 Handoff/证据）。
- [ ] **AC3**：**8 处逐个**有测试或探针，**不接受「模式相同所以一起算」**。
      证据：`verification/P09-MANAGED-READ-ROOT-TRUST-1/site-matrix.md` 逐处映射表 + 每条测试名。
- [ ] **AC4**：不引入新依赖或契约变更。
      证据：`git diff --stat b8a1e5197..<head>` 与依赖/契约/Schema 文件零差异的检查记录。
- [ ] **AC5**：`P09-AC3-DELETE-HARDEN-1` 的 9 个探针**不回归**。
      证据：`verification/P09-MANAGED-READ-ROOT-TRUST-1/ac5-delete-probes/`（9 个探针的仅改路径常量副本、
      与原始文件的 diff、逐项 `injection_fired`/`outside_survived` 结果表）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac1-r5b-repro.py` | Windows、Python 3.14、worktree | NOT_RUN | 待填 |
| AC1/AC3 | `C:/Python314/python.exe -m pytest tests/security/test_p09_managed_read_root_trust.py -q` | 同上 | NOT_RUN | 待填 |
| AC2 | 逐套件 `python -m pytest <suite> -q`（core/storage/m2_resource_channel/security/library/reading_export/export/m2_acceptance） | 同上 | NOT_RUN | 待填 |
| AC5 | `C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac5-run-delete-probes.ps1` | 同上 | NOT_RUN | 待填 |
| AC4 | `git diff --stat b8a1e519703f13af73b320dded117004b4bb189a..HEAD` | 同上 | NOT_RUN | 待填 |

## 允许修改范围

`allowed_paths` 见 frontmatter。本 Task 唯一新增产品代码载体为
`src/infrastructure/resource_channel/handle_resolver.py` 中的读取原语
（`ManagedRootTrust`）；其余 7 处为同文件的调用点改造。**新增路径
`src/infrastructure/resource_channel/handle_resolver.py` 已在既有 allowed_paths 内。**

## 依赖、风险与阻塞

- 硬依赖：`P09-AC3-DELETE-HARDEN-1`（已完成/已交付，删除路径不动）。
- 残余风险见设计文档第六节（路径/URI 交接窗口、硬链接、内部链接 fail-closed、root 被搬走后读取拒绝）。
- 无阻塞。

## 交付与运行记录

- 设计：已冻结，`verification/P09-MANAGED-READ-ROOT-TRUST-1/DESIGN-expected-identity.md`
  （commit：本 Task 首次设计提交）。
- Handoff：交付时创建 `doc/handoffs/P09-MANAGED-READ-ROOT-TRUST-1-<short-head>.md`。
- Review：尚无（不得自造）。
- 实际测试：见「测试要求」表，交付时回填命令与 exit code。

## Canonical Evidence

进入 `in_review` 前逐项填写（当前 pending）。仓库内文件 pin commit；仓外原始输入 pin SHA-256。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class |
|---|---|---|---|---|---|
| — | — | 待交付时填写 | — | — | — |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | `G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1` | PRESERVE_REFERENCED | 本路径 | — | 本 Task 交付；删除须 Codex 按 Worktree Safety Inventory 另行授权 |
| temp（探针临时目录） | `%TEMP%/p09-*` | NOT_APPLICABLE | — | — | 探针自建自清，不触碰用户数据 |
| agent-output | 无（本 Task 不在仓外新建 agent-output） | NOT_APPLICABLE | — | — | 证据全部在 `verification/P09-MANAGED-READ-ROOT-TRUST-1/` |

## Closeout Record

- Closeout date / Codex：待关闭时填写（本 Task 只到 `in_review`，不关闭）。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：0（本 Task 不执行清理）。
- 未关闭项及保留原因：交付时填写。
- 当前指针清理：不适用（Owner 不改 STATUS/Plan 指针）。
