---
task: P09-MANAGED-READ-ROOT-TRUST-1-REVIEW
reviewer: Codex
author: dsh-p09-root-trust
base_commit: b8a1e519703f13af73b320dded117004b4bb189a
reviewed_head: cb767e1b7c82fe02bb966894a8d2cf85d26376b6
implementation_head: 56aee75ae
decision: changes_requested
review_mode: read_only
---

## 1. 结论

- **A — 设计成立。** `ManagedRootTrust.capture()` 在装配时从同一根目录句柄固定 `(volume_serial, file_index)` 与 `GetFinalPathNameByHandle` 规范路径，并保存纯词法绝对根。读取时先冻结引用，再核验根句柄和目标句柄；实际字节读取使用已核验的句柄。根之上/根本身的 reparse 在身份未变时允许，根下 reparse 拒绝；没有采用“任一祖先 reparse 即拒绝”。通用 guard 可复用，第 8 处保留独立的 namespace 规则。
- **B — 部分成立。** 八处都有独立代码改造和对应测试名；没有“模式相同所以一起算”。但第 5/6 处丢失了文件类型检查；第 3 处测试没有覆盖导出 hash 和惰性 provider，AC3 脚本也没有可靠断言每项当前测试实际通过。
- **C — 部分成立。** 作者日志中的 AC1 记录是 base `VULNERABLE`、current `SAFE`；AC5 记录 9/9 与基线一致，并正确保留 `n002-race` 为 `INCONCLUSIVE`。AC2 有目录替换回归，且回归套件日志不满足仓库的完整日志要求。硬链接、同名替换和校验后按路径重新打开的窗口均有披露，没有被本 Review 当作已修复。
- **D — 范围与 pins 成立。** `b8a1e519..56aee75` 共 6 个文件；实现提交 `56aee75` 只改 3 个源文件和测试。未发现删除路径、IPC、Schema、ACL 或依赖改动。15 个仓库内 Canonical Evidence 行的工作区字节 SHA-256 均匹配；其路径在所 pin 的 commit 中存在。8 个文本 pin 的 blob hash 与工作区 hash 不同，但在 `core.autocrlf=true` 下仅为 CRLF/LF 差异，换行归一化后匹配 blob。SP-01、SP-02 的实际文件 hash 也匹配。

## 2. Findings

1. **R-001 — P2：`verify_existing()` 接受目录，导致第 5/6 处行为回归。**  
   在 [`handle_resolver.py`](<G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1/src/infrastructure/resource_channel/handle_resolver.py:753>)，目标句柄只拒绝 reparse 和规范路径不匹配，没有拒绝 `FILE_ATTRIBUTE_DIRECTORY`；[`core_assembly.py`](<G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1/src/bootstrap/core_assembly.py:226>) 的 `image_state()`、`_uri_within()` 又移除了原有 `is_file()` 检查。若图片路径被同名目录替换，状态会是 `"ok"`，且会返回目录的 `file://` URI，违反 Task AC2 的合法文件准入语义。  
   **最小修正：** 在已打开的目标句柄上拒绝目录，并增加目录替换测试，断言 `image_state == "invalid"` 且 URI 为空。

2. **R-002 — P2：AC3 没有稳健证明第 3 处全部子路径通过。**  
   [`test_p09_managed_read_root_trust.py`](<G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1/tests/security/test_p09_managed_read_root_trust.py:209>) 的 site3 测 `_checked_managed_path()` 和 `_reader_sha256()`，没有覆盖 `_verified_managed_sha256()`、`_read_verified_managed()` 或导出时实际执行的惰性 provider。另，[`ac3-discrimination.py`](<G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1/verification/P09-MANAGED-READ-ROOT-TRUST-1/ac3-discrimination.py:108>) 解析了 `current_passed` 却未使用；第 122–124 行把“未出现在失败集合”直接判为 PASS，也不以 pytest exit code 作门槛。日志中的 8/8 结果因此不能证明这些精确测试均实际通过。  
   **最小修正：** 对导出 hash 和惰性 provider 增加重定向后拒绝测试；AC3 runner 要求列出的每个测试出现在实际通过/失败集合中，并检查 pytest 退出码。

3. **R-003 — P2：AC2 定向测试日志不符合证据纪律。**  
   [`suite-security.log`](<G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1/verification/P09-MANAGED-READ-ROOT-TRUST-1/logs/suite-security.log>) 等 suite 日志记录了 `N passed`，但没有 shell/venv 执行头和日志内 `EXIT`。`summary.txt` 有 `exit=0` 和结果尾行，但缺执行头。违反 `doc/09_COLLABORATION.md` §6.12①；按该规则，这些日志不能作为合格的 `N passed` 证据。  
   **最小修正：** 重新运行并逐次保存含 shell、解释器路径、命令和 `EXIT` 的日志。

4. **R-004 — P3：AC1/AC3 脚本把临时目录放在系统 `%TEMP%`。**  
   `ac1-r5b-repro.py` 与 `ac3-discrimination.py` 使用未指定 `dir` 的 `tempfile.mkdtemp()`；Task Resource Manifest 也记录了 `%TEMP%/p09-ac1-*`、`%TEMP%/p09-ac3-*`。这不符合 [`AGENTS.md`](<G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1/AGENTS.md:44>) 和 `doc/WORKSPACE_GOVERNANCE.md` 的临时产物位置规则。  
   **最小修正：** 将脚本 scratch 放到 `New Manga.workspace/temp/P09-MANAGED-READ-ROOT-TRUST-1/`。

5. **R-005 — P3 判断项：possible Duplicated Code。**  
   [`core_assembly.py`](<G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1/src/bootstrap/core_assembly.py:190>) 和同文件第 291 行重复 `_trust()` 的懒捕获逻辑；`core_service.py` 第 2701、2731 行重复摘要读取与错误映射形状。属于维护性判断，不影响本次安全结论；可在后续复用现有 helper 时收敛。

## 3. 逐处 8/8 判定表

| 位置 | 设计是否到位 | 测试是否有判别力 | 结论 |
|---|---|---|---|
| `core_service.py` `read_original_page` | 是，调用 `read_bytes()` | site1 覆盖合法读取与祖先重定向拒绝；日志声称 base FAIL/current PASS | 通过 |
| `core_service.py` `handle_resolve_page_resource` | 是，读取已核验字节后交给私有临时文件 | site2 检查未发布 outside bytes | 通过 |
| `core_service.py` `_checked_managed_path`、`_reader_sha256`、导出 hash/provider | 代码路径均使用 guard | site3 未覆盖导出 hash/provider；AC3 runner 的 PASS 判定不严格 | 部分 |
| `core_service.py` `_is_protected_export_target` | 是，托管侧用冻结词法路径 | site4 检查真实托管文件仍受保护、outside mirror 不受保护 | 通过 |
| `core_assembly.py` `image_state` | reparse/规范路径检查到位，但未拒绝目录 | site5 仅测祖先重定向，未测目录替换 | 部分 |
| `core_assembly.py` `_uri_within` | 身份检查到位；仍有向消费者交付路径的窗口 | site6 测重定向前后 URI，但未测目录替换或交接竞态 | 部分 |
| `core_assembly.py` `_page_image` | 是，`read_bytes()` 后用 `QImage.fromData()` 解码 | site7 覆盖已重定向祖先拒绝 | 通过 |
| `handle_resolver.py` `resolve_namespace_identity` | 是，文件系统访问前固定词法 expected，保留既有严格 reparse 策略 | site8 在 walk 后、open 前注入 junction | 通过 |

## 4. 残余风险是否可接受

硬链接、同名目录替换，以及验证后把规范路径交给 QML/preview publisher 按名字重新打开的窗口，都已在设计文档中披露；当前实现没有消除这些风险。它们只有在信任边界明确排除“能写入托管根或其父目录的攻击者”时，才可作为本 Task 的范围限制接受。若威胁模型包含这类并发写入者，路径交接仍可能读到外部字节，需要另行采用句柄相对访问或传递已核验字节；不得将这些路径描述成已完全修复。

## 5. 运行证据

| 只读命令 / 检查 | 结果 |
|---|---|
| `git status --short --branch`（指定 worktree） | exit 0，worktree clean |
| `git diff --stat b8a1e519..56aee75ae`、`git show --stat 56aee75ae` | exit 0；分别为 6 个文件、实现提交 4 个文件 |
| `git diff --check b8a1e519 56aee75ae` | exit 0；无空白错误 |
| `git diff --name-only ... --` 删除路径、Schema、ACL、IPC、依赖相关路径 | exit 0；无命中 |
| Canonical Evidence / Source Pin 字节重算与 `git cat-file` 核对 | exit 0；EV-01–EV-15、SP-01、SP-02 的工作区 SHA 均匹配 |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P09-MANAGED-READ-ROOT-TRUST-1.md` | **exit 1**，6 errors / 4 warnings。Task 自身没有专属 FAIL；非终态 Task 台账计数、缺失 archive 引用、DAG 未登记 P09 均为该 worktree 的 base 差异：主仓当前 `STATUS`/`REBASELINE_PLAN` 已列 P09，主仓有未跟踪 Task/archive 内容，而此分支快照没有。另有 lifecycle v1 提示，属非阻断 warning。 |
| AC1、AC3、AC5 探针及 pytest 套件 | **NOT_RUN**。为遵守“不修改任何文件”；已检查提交内日志和脚本，但未把 DSH 日志当作独立复跑。 |

**建议下一步：** 由 Owner 修正目录准入、补齐 site3 导出路径测试并收紧 AC3 runner；重新生成符合证据纪律的 AC2 日志后，以新 head 重新提交 Review。