---
task_id: P09-FU2
title: 导入侧 IPC 接线实现
reviewer: dsh（项目权威 Reviewer，`.orchestrator/tasks/P09-FU2-role.json`；role_exclusion 已排除 owner=codex）
owner: codex
base_commit: 9fe6ac5cd116474de1006b4ab4b1e5341b71cf41
declared_delivery_head: cac219fe79e0d741259d92dae12d896e9d357c6c
reviewed_head: 73b52e86aebbbab3854b870990d8de513d3e7ee1
review_worktree: G:/CODEX/New Manga.workspace/worktrees/P09-FU2-IMPORT-IPC-RUNTIME
date: 2026-10-16
mode: 只读审查 + 独立 Git/测试日志/安全断言复核；未修改被审分支或主仓任何文件
object_binding: VERIFIED
severity: Core wire 实现 + 安全 Gate（消除 P18 实测的 UNKNOWN_COMMAND）
decision: approved
---

# P09-FU2 独立 Review（R1）

## 0. 复核结果（未采信自述）

| 项 | 方式 | 结果 |
|---|---|---|
| 变更范围 | `git diff --name-only 9fe6ac5c..HEAD` | **22 个路径，全部在契约 §12 授权内** |
| **只读复用面未被触碰** | 过滤 `src/application/importing/`、`src/application/library/`、`src/infrastructure/sqlite/` | **空** ✅ |
| **冻结契约完好** | 过滤 `M2-C1_TYPED_IPC_CONTRACT`、`P11_LONG_TASK` | **空** ✅ |
| 越界路径 | 反向过滤授权集合 | **空** ✅ |
| worktree / 主仓 | `git status` | worktree **clean**；主仓 **19 项 dirty 未变** |
| 完整测试集 | 独立读原始日志 | `tests/core`：**377 passed / 0 failed / exit 0** |
| 既有测试改动性质 | 读 `test_core_detect.py`/`test_core_service.py`/`test_p13_run_runtime.py` diff | **仅协议版本断言** `{major:2,minor:1}`→`{major:2,minor:2}`、`(2,1)`→`(2,2)`；**未削弱断言** |

## 1. AC 逐项结论

| AC | 判定 | 依据 |
|---|---|---|
| **AC1 命令已识别** | **接受** | 原始 stdio 实测：`ImportPages` 响应 `result` 含 `sources`/`pages`、`serve_exit_code=0` —— **不再是 `UNKNOWN_COMMAND`**，P18 的运行时缺口已消除 |
| **AC2 引用校验（安全 Gate）** | **接受（重点）** | 见 §2 |
| AC3 接入既有 importer | **接受** | 图片与 PDF 两条既有 importer 均已接线，**importer 文件未被修改**（只读面过滤为空）；Managed Copy、真实尺寸、页序、源文件不变均有断言 |
| AC4 `user-source` 只读 scope | **接受** | `test_user_source_is_core_only_and_read_only`；契约要求"未放宽既有前端 scope allowlist 与 §10.1/§10.2"已核对 |
| AC5 `ImportReport` 序列化 | **接受** | `import-report-sample.json` + 用例断言源 hash、逐 Page hash、真实 `width/height`、`source_order`/`sort_order`、`duplicate`、`side_effects` |
| AC6 覆盖 | **接受** | 13 个测试函数覆盖重复（`skip`/`import_as_new`）、中断、Unicode 自然序、损坏图片、损坏与加密 PDF |
| AC7 范围锁定 | **接受** | 见 §0 三项过滤，全部为空 |
| AC8 可复核性 | **接受** | `host-issuer-and-test-seam.md` 明确 **host issuer 仍待独立 Task**，并说明注入 seam 不是 issuer、不暴露为 JSON-RPC 命令 |
| AC9 Review + 集成 | **Review 由本文件闭合；集成由 Coordinator 执行** | Task 保持 `in_review` |

## 2. AC2 安全 Gate 的独立复核（本 Review 的核心）

**覆盖超出契约要求**：契约 §10.4 要求 6 类拒绝，实测覆盖 **12 项**，每项用例名均带 `have_zero_side_effects`：

| 类别 | 拒绝码 |
|---|---|
| 契约要求的 6 类 | `REF_MALFORMED` / `REF_SIGNATURE_INVALID` / `REF_EXPIRED` / `REF_UNKNOWN_ID` / `REF_REVOKED` / `REF_ALREADY_CONSUMED` |
| **额外**（超出要求，值得肯定） | `REF_SCOPE_DENIED`（host session 不符）、`REF_NOT_FOUND`、**`REF_REPARSE_POINT`**（Windows 符号链接/重解析点逃逸）、**`FILE_IDENTITY_CHANGED`**、**`FILE_SIZE_CHANGED`**（TOCTOU 身份/尺寸漂移） |

**关键安全断言（我逐条确认存在）**：

1. **`test_request_path_fallback_is_rejected_as_malformed_reference`** —— 直接证明**裸路径字符串不会被当作授权**（契约 §10.4 的核心禁止项）✅
2. **`test_invalid_second_reference_prevents_first_source_import`** —— 证明**原子性**：后续引用无效时，前面的来源也不得被导入 ✅
3. **`test_directory_grant_rejects_an_outside_child_before_import`** —— 目录 grant 不得越出直接子项（路径逃逸）✅
4. **`test_corrupt_sources_are_rejected_without_managed_or_library_writes`** / **`test_encrypted_pdf_is_rejected_before_any_managed_copy_or_page`** —— 拒绝发生在**任何托管拷贝或 Page 写入之前** ✅

**结论：AC2 达到"可证伪的负向断言"标准**，且在 Windows 安全细节（reparse point、文件身份/尺寸漂移）上**超出**契约最低要求。

## 3. Findings

| id | 级别 | 内容 | 处置 |
|---|---|---|---|
| **F1** | **P3（流程，同类第 9 次）** | `delivery_head` 申报 `cac219fe`（实现提交），实际 HEAD=`73b52e86`（证据提交） | closeout 冻结实际 HEAD；BL-7 再次确认 |
| **F2** | **P2（后续依赖）** | **Tauri host issuer 仍未实现**（契约与授权均明确排除）；测试使用**注入 seam**。真实产品中"用户选择来源 → host 签发 → 注册受信 grant"链路尚不存在 | 须由独立 Task 实现（含 HMAC key 与 host session 生命周期/撤销）；**P12/P19 的真实端到端在它完成前仍无法验证** |
| **F3** | P2（验证边界） | 本 Task 证明的是 **Core 侧**能力；P18 实测的 JA/KO 端到端仍受阻于**检测像素上限**与 **KO detector 权重缺失**（另有登记） | 该两项仍待解阻；本 Task 未声称端到端已通 |
| F4 | P3（继承限制） | P09 的**项目级永久删除**验收仍受限（`AC-IMPORT-002`） | 保持登记，不随本实现消失 |
| F5 | P4 | 既有测试文件的协议版本断言随 minor 1→2 更新 | 必要副作用；已在 §0 确认无削弱 |

**无 P0/P1 finding。**

## 4. 条件

- **C1**：Coordinator 集成时冻结实际被审 head `73b52e86aebbbab3854b870990d8de513d3e7ee1`。
- **C2**：**host issuer Task 应在 P12/P19 的真实端到端验证前完成**（F2）。
- **C3**：P09-FU2 可标 `done`（AC1–AC8 闭合 + 本 Review + 集成）；但 **F3 的检测像素上限与 KO 权重**、**F4 的项目级永久删除**仍是独立登记项，不得据此宣称产品级导入/端到端已完成。
- 实现本身无需返修。

## 5. 能力边界

- 本 Review 覆盖范围合规、`UNKNOWN_COMMAND` 消除的实测证据、AC2 安全断言的独立复核与既有测试改动性质；**未重跑** 377 用例（原始日志已核验 exit 0）。
- 所有 Git / 日志 / 代码 / 安全断言结论均由 Reviewer 在 live 环境实际执行。
- Reviewer 未修改被审分支、主仓或任何证据文件；未 push。
