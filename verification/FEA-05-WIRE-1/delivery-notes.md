# FEA-05-WIRE-1 交付说明（DSH 代实现）

日期：2026-11-02
实现者：DSH（Codex 本地命令通道不可用，按目标故障转移规则由 DSH 实施；实现复核须独立上下文）
范围：doc/tasks/FEA-05-WIRE-1.md v5.2（r7 approved）

## 改动清单

| 文件 | 改动 |
|---|---|
| doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md | 新建：头部（PENDING/v1.0/变更记录）+ 五节（范围/清册/请求响应/错误码逐码表/兼容性/实现指针） |
| doc/contracts/V11R_COMMAND_CONTRACT_V1.md | §8 追加 C078–C083 六行（7 列与 C067 同形）+ 段落说明 + 约束句 |
| src/bootstrap/core_service.py | 导入 DraftError；白名单 + _dispatch_draft_command（6 命令，真实签名）；_draft_error_envelope + 冻结词表 category/retryable；_require_str/_require_int/_require_mapping；handler 分支（Region 分支前） |
| 	ests/core/test_draft_commands.py | 新建：9 项（6 命令成功映射 + 非法 payload + 未知命令 + 错误信封） |

## 测试结果

| 命令 | 结果 |
|---|---|
| python -m pytest tests/core tests/domain -q | **897 passed, 1 warning, exit 0** |
| python -m pytest tests/core/test_draft_commands.py -q | **9 passed** |
| dotnet test .../NewManga.CoreClient.Tests --filter "CommandContractV11RTests|RegionWriteCommandTests" | **80 passed, 0 failed**（§8 六行可解析、未进已冻结集合、Region 不变式不受影响） |
| python -c "ast.parse(...)" | AST OK |

## 设计说明

- 命令名下划线（drafts_open 等），与 §8 解析器 ^[a-z][a-z0-9_]*$ 一致。
- _dispatch_draft_command 返回 result dict；DraftError 由调用处转 _draft_error_envelope（冻结 M2-C1 信封，category 仅用冻结词表，bench: LOCK_CHANGED/PAGE_SIZE_UNAVAILABLE/DRAFT_JOURNAL_UNWRITABLE/INTERNAL 为 retryable）。
- 未接 IHostController/CoreClient registry（W-6，归 FEA-05-PORT-1）。
- 未改 src/application/editing/**、src/domain/drafts/**、schema、UI。

## 已知限制

- C081 响应 { "<region_id>": "<region_revision_id>" } 按 pply_candidates 真实返回值；receipt 元数据不在 wire 返回。
- drafts_status 按 payload 二选一（draftId/sessionId），两者都给或都不给 → DRAFT_INVALID。
- Python 测试用 fake 服务（不依赖 SQLite/assembly），真实集成由后续 FEA-05-PORT-1 的端到端覆盖。

## impl-r1 处置（DSH，2026-11-02）

| finding | 处置 |
|---|---|
| P1-01 C081 多包一层 | _dispatch_draft_command 直接 eturn drafts.apply_candidates(...)（裸映射 {region_id: revision_id}）；测试断言同步 |
| P1-02 §3 逐码表错 | 从 drafts.py 实际 17 码重写：DRAFT_FLUSH_TRIGGER_INVALID/DRAFT_NOT_FOUND/DRAFT_CANDIDATE_NOT_FOUND/DRAFT_OWNER_CHANGED/EDIT_TOKEN_REUSED/STALE_BASE_REVISION/DRAFT_APPLY_FAILED 已入表；删除不存在的 3 码；_DRAFT_ERROR_CATEGORY 同步 17 码 |
| P1-03 主契约 12 处表格被改坏 | git checkout be9265b34 -- doc/contracts/V11R_COMMAND_CONTRACT_V1.md 恢复，再精确追加 §8.2 与 §10（不改其它行） |
| P1-04 §10/§8 标题 | §8 标题扩为「C067–C077 … 与 C078–C083 Draft 命令面」；§10 追加 FEA-05 行（去重后单 §10） |
| P1-05 AC4 覆盖 | 新增 	est_each_command_rejects_invalid_payload（8 组非法 payload）与 	est_drafts_dispatch_is_registered_and_typed（dispatcher 注册）；测试 9 → 11 项 |
| P2-02 retryable | 保留 LOCK_CHANGED=true（W-4 已冻「锁冲突 true」；impl-r1 建议再裁，记为 P2 接受遗留） |

回归：pytest tests/core tests/domain -q → **899 passed, exit 0**；dotnet test CoreClient.Tests --filter "CommandContractV11RTests|RegionWriteCommandTests" → **80 passed, 0 failed**。
