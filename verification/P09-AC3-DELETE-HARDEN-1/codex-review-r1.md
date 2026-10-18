---
task_id: P09-AC3-DELETE-HARDEN-1
reviewer: Codex
author: dsh
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
reviewed_head: 4824ed5d4872a6dc519ca6e671bfa6485bd47d9a
decision: changes_requested
---

# Review：P09-AC3-DELETE-HARDEN-1

## 范围与依据

- 固定区间：a04e4ea78d5b33a0f91efcdc06b396391c4b165e..4824ed5d4872a6dc519ca6e671bfa6485bd47d9a。
- git rev-parse 对固定 head 的解析与给定值完全一致。实际 checkout HEAD 是 d807012ad62d50bfaeb11dcf21995dca430e44e，不等于固定 reviewed head；target 到当前 HEAD 只改了 doc/REBASELINE_PLAN.md、doc/STATUS.md、本 Task 文件，相关实现文件没有后续差异。实现审查以固定 head 内容为准；当前 Task 的 pins 与指针则按用户要求核对磁盘现状。
- base..head 实际包含 48 个提交；其中 git log --grep=P09 命中 18 个。Task 中“共 18 个提交”只对应 P09 标记提交数，不是整个固定区间总数。区间累积差异为 320 files / 48,529 insertions / 861 deletions，含区间内其他工作；本 Review 聚焦本 Task 对应实现、测试、证据和上位 AC，不将这些统计冒充为本 Task 独有 diff。
- 依据：本 Task 的 AC1–AC12、测试要求表及 11 个 Canonical Evidence pin；上位 Task P09-AC3-DELETE-1、R3 Review、T2 full-suite triage、P09.md；M2-C1 冻结契约；固定区间内真实代码与测试。
- 本次只新增本 Review 文件；未更改代码、历史 pin 或用户未提交文件。测试结束时未发现 m2rc1-desktop、core_service、host_bridge 进程。

## Architecture

回收站命令已从 Tauri production 路由到 Core dispatcher 和 Service；Rust 错误类型也能以结构化 JSON 错误投影到前端。永久删除的核心清理仍有数据安全与恢复问题：译图阅读生成的随机 preview 没有进入删除清单，且生命周期来源路径不匹配；拒绝删除的 preview 仍被当作清理成功。另有盘符相对路径可绕过 helper 的绝对路径判断。回收站 IPC 命令不在冻结契约内，且本 Task 明文禁止新增未冻结命令。

## Standards（可选视角）

发现的硬性范围冲突：本 Task doc/tasks/P09-AC3-DELETE-HARDEN-1.md:63 写明“不新增未冻结的 IPC 命令”；M2-C1 doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:1224 写明“仅冻结项目级单条与批量永久删除 IPC 契约，不授权本轮 runtime 实现”。当前实现加入 library_list_recycle_bin_books，但 M2-C1 命令目录没有该命令。具体影响见 F-001。

## Spec（可选视角）

- AC4 的要求是译图 preview 真正进入可回收生命周期；现有测试只断言 lifecycle 行及 artifact/revision ID，真实删除仍留有随机 key/catalog row。见 F-002。
- AC5 要求拒绝路径替换及越界删除；静态 junction 用例有判别力，但盘符相对路径可绕过，且调用方忽略拒绝返回值。见 F-003、F-004。
- AC7 的九条关联查询与 verify_all.py 完全同步，且主 verifier 对真实样本 Book 执行并断言九类 DB 行为 0；但派生目录只打印文件数/字节数，没有 orphan 扫描或清理断言，R3 此部分仍未闭合。见 F-005。
- AC11 的上位 delivery_head 正确补齐且 AC3 delete 子条件仍为 BLOCKED；但 P09.md 的 AC3 状态仍写“完成”，AC3 matrix pin 与磁盘 SHA 不一致。见 F-006。
- AC12 当前全量测试输出与 Task 描述同为 9 failures，但其中两项 Transformers 检测失败是 API 不兼容异常，不能一概称为环境缺失/反转；证据文件也记录在更早的 HEAD。见 F-007。

## Findings

| ID | 优先级 | 状态 | 位置 file:line | 说明（含可核对的原文） |
|---|---|---|---|---|
| F-001 | P1 | open | apps/desktop/src-tauri/src/main.rs:75,1601,1801；src/bootstrap/core_service.py:3144；doc/tasks/P09-AC3-DELETE-HARDEN-1.md:63；doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:1224 | 路由事实成立：PRODUCTION_COMMANDS 含 "library_list_recycle_bin_books"，production generate_handler! 注册 handler，command_allowlist 从 production 列表派生，测试白名单也列出它；Core 有 if command == "ListRecycleBinBooks" 分支并调用 Service。但冻结契约中无 ListRecycleBinBooks 命令，且 Task 禁止范围原文为“不新增未冻结的 IPC 命令”；M2-C1 原文为“仅冻结项目级单条与批量永久删除 IPC 契约，不授权本轮 runtime 实现”。因此命令虽可达，仍属未冻结 IPC 越界；AC1 不能整体 PASS。 |
| F-002 | P1 | open | src/bootstrap/core_assembly.py:390；src/bootstrap/core_service.py:1834,1940-1950,3917,3984；src/infrastructure/resource_channel/render_preview.py:125-150；tests/core/test_p09_ac4_translated_preview.py:140-154 | 标识符修复确实在真实阅读链路：production reader catalog 将 revision.managed_path 转为绝对路径（translated = self._storage.absolute_path(revision.managed_path)）；真实 handle_get_reader_projection 用 page_id、translated_artifact_id、translated_revision_id 查到行，再调用 publish(..., origin=...)。但之后把绝对路径存入 managed_rel_path=page.translated_path，而 retired GC 用 if revision["managed_path"] != candidate.managed_rel_path: return None 作字面相等比较；相对 managed path 与绝对路径不等，候选被保护而不删除。并且 retired collector 只取 retired=1，reader 生成的 preview-<uuid> 没有在删除链路中 retire/纳入 manifest；启动 collect_orphans() 不处理仍有 catalog row 的 live 文件。测试只断言 preview_lifecycle 行、artifact_id == "a1"、artifact_revision_id == "ar1"，没有删除后回收断言。故真实链路仍会泄漏 preview；不是最初的 ID 查找问题，而是其后的路径、retirement、manifest 清理缺口。 |
| F-003 | P1 | open | src/infrastructure/sqlite/library.py:1237-1269；src/application/resource_channel/dto.py:97-110；tests/storage/test_preview_unlink_reparse.py:42-88 | helper 对普通相对路径逐段 lstat()，拒绝 . / ..、绝对路径及 reparse point；Windows 上注入 previews/link junction、目标为普通文件的测试实际通过，能捕获静态父目录 junction 回归。但 helper 仅用 Path(normalised).is_absolute()；Windows 的 C:outside.png 等盘符相对形式 is_absolute() 为 False。以 G 盘根目录拼接不同盘符形式会保留如 C:outside.png 的 drive-relative 路径，后续 is_file()/unlink() 可访问 root 外的每盘当前目录。共享 validate_rel_path() 明确以 rel_path[1] == ':' 拒绝盘符路径，但 helper 未调用它；当前测试只拒绝绝对路径与 ../，未覆盖盘符相对输入。 |
| F-004 | P1 | open | src/infrastructure/sqlite/library.py:1114-1122,1180-1187 | unlink_preview_without_following() 的契约是“Returns True when a plain file was actually removed”，遇到 junction 会返回 False；调用方却不检查返回值，随后无条件 catalog.remove(res_id)。all_deleted 仍为 True 时后续删除 cleanup manifest 并返回成功。于是被安全拒绝的文件仍留在磁盘，但 catalog/manifest 重试线索被清掉，无法重试且可能向上层报告完成。junction 单测只测 helper，没有测永久删除调用方结果与 retry 状态。 |
| F-005 | P1 | open | verification/P09-AC3-DELETE-1/verify_all.py:212-254,399-405；verification/P09-AC3-DELETE-HARDEN-1/ac7-verify-query-check.py:19-63 | 独立 AST 比对结果是两份查询字典 9/9 完全相同：books、chapters、reading_progress、book_tags、media_artifacts、pages、regions、region_revisions、artifact_revisions。主 verifier 对真实创建的 book1.book_id 执行查询并 assert rows == 0，比 mock 有判别力。残留缺口是 R3 R-008 明确要求的 orphan 检查：主 verifier 只调用 count_directory_metrics() 并打印 Managed storage after / Derived storage after 数量，没有对派生文件 orphan 或预期清理结果作断言；AC7 schema probe 使用空 "probe-book"，在 queries_ok=... 后不论结果直接打印 done。因此查询同步修正成立，但 R3 的“没有 orphan 扫描或断言”未完全闭合，AC7 只能 PARTIAL。 |
| F-006 | P2 | open | doc/tasks/P09.md:59,128；verification/P09/evidence/AC3-source-hashes.json | AC3 delete 子条件仍明确为 BLOCKED，符合硬约束；但同一 P09.md:59 状态栏仍写 AC3 | 完成，与“故 AC3 的 delete 子条件仍为 BLOCKED，不得据此判为 PASS”并列，状态仍矛盾。Canonical Evidence 的 AC3-MATRIX 期望 SHA 为 6c2018642ae5aa4e930a88fa62d1885264e479b5dc9e4693e7401f266afcfeac，本机 CRLF 磁盘字节实算为 56e40a827c20725cc1a66ddd527c521b84fcd059f624873732cfcecb814266e3。不得改写历史 pin；需追加证据/状态澄清。 |
| F-007 | P2 | open | verification/P09-AC3-DELETE-HARDEN-1/ac12-no-regression.md:6；当前全量 pytest 输出 | AC12 证据把六项 providers failures 整体定性为“环境反转”。本次全量 pytest 确认 9 failed / 2250 passed / 9 skipped；四项确属环境可用性反转（GPU/OCR 可用而测试要求不可用），另两项真实检测测试抛 AttributeError: module transformers has no attribute RTDetrV2ForObjectDetection，包装为 ProviderError: PROVIDER_FAILED，属于当前 Transformers 接口不兼容，不能定性为单纯“环境具备 GPU/OCR”。证据文件记录的 head 为 899b72b65d90c6c2f6c0835857ce0b4028b3d71d，早于固定 delivery head。当前结果没有证明这些 providers 失败由本 Task 引入，但也不足以接受“六项都是环境反转”或严格宣告零回归；应有锁定/隔离依赖或注入 provider 可用性的确定性替代验证。 |

## AC1–AC12 逐项独立结论

| AC | 结论 | 独立证据与判断 |
|---|---|---|
| AC1 | PARTIAL | 回收站命令在 PRODUCTION_COMMANDS、allowlist 派生面、production generate_handler! 和 Core dispatcher 均存在且可达；服务从软删除集合读取。但这新增了 M2-C1 未冻结的 IPC command，冲突于本 Task :63 禁止范围。 |
| AC2 | PASS | pipeline_run_targets 的 run_target_id 是主键；删除时设 target_id = 'detached:' || run_target_id，并将 page_id 清空。当前生产 Page ID 由 UUID 生成，detached: 不与正常生产 page ID 形状碰撞；未发现删除后依赖该 target_id 反查 page 的路径。pipeline_stage_states 的 16-byte randomblob 后缀在数学上并非绝对唯一，但碰撞概率可忽略；不是严格无碰撞证明。 |
| AC3 | PASS | Rust PermanentlyDeleteBooksErrorView 是 Serialize 结构，其 per-item items 是顶层字段。Tauri 2.12.0 的 InvokeError 持有 serde_json::Value，泛型 From<T: Serialize> 序列化结构体并经 invoke error callback 传给 JS 为对象；源码位置为 Cargo registry tauri-2.12.0/src/ipc/mod.rs:224,240、src/ipc/command.rs:262 和 ipc/protocol.rs 的 error callback。Tauri 的错误形状并非一律对象：Result<_, String> 仍会给字符串；本命令返回 typed error view，不是 String。client.ts:394-400 的 carrier.items !== undefined ? { items: carrier.items } 因此会把真实 top-level items 送入 LibraryClientError.details.items。details 本身不是 Rust JSON 字段；本命令的前端取值成立，mock 形状与真实投影一致。未运行完整 WebView E2E。 |
| AC4 | PARTIAL | _resolve_preview_origin_for_page 的 ID 查找修正在 production reader catalog 链路成立；preview 确实写入生命周期行。但绝对 translated_path 被存作 managed_rel_path，retired-source 比较会拒绝；随机 reader preview 也未进入删除 manifest/retire 流程。现有测试只证明写入行，不证明 GC 能删除。 |
| AC5 | PARTIAL | 逐段 lstat() 与静态父 junction 测试真实有效，本机三项 storage 测试全通过；但盘符相对路径绕过绝对路径拒绝，且永久删除调用方忽略 helper 的 False，清理失败后仍移除 catalog/manifest。 |
| AC6 | PASS | strip_run_json_locators 递归处理 dict/list，仅删除 locator key；测试断言 status、book_title 等历史快照保留。stage-state suffix 是概率唯一，不是形式上的绝对唯一；真实 target_id 生产值为 UUID，无实际碰撞证据。 |
| AC7 | PARTIAL | 独立 AST 比对确认九条查询与 verify_all.py 实际一致；主 verifier 用真实 book_id 并断言 9 类关系行清零。仍缺派生目录 orphan 扫描和清理结果断言，R3 R-008 未完全关闭。 |
| AC8 | PASS | cleanup_book_files 不再递归 os.walk；仅对 manifest targets 的祖先目录执行有界 rmdir，非空目录保留。 |
| AC9 | PASS | Rust phase 投影只允许 preflight、cleanup，其他字符串降级 unknown，非字符串为 None；与 code 的闭集映射模式一致。指定 Rust 单测通过。 |
| AC10 | PASS | 真实 schema 版本硬编码测试由 v4 更新到 v5；tests/packaging 与 tests/diagnostics 共 84 项通过。 |
| AC11 | PARTIAL | 上位 P09-AC3-DELETE-1.md 的 delivery_head 与 R3 reviewed_head 都是 a04e4ea78d5b33a0f91efcdc06b396391c4b165e；P09 AC3 delete 子条件仍为 BLOCKED，没有翻为 PASS。但 P09.md 仍将 AC3 总状态写为“完成”，并有失效的 AC3 matrix SHA pin。 |
| AC12 | PARTIAL | 固定代码的完整 pytest 运行得到 9 failed / 2250 passed / 9 skipped；Task 说明的三项 workbench 既有失败与当前结果一致。providers 六项中四项属 GPU/OCR 环境可用性反转，两项是 Transformers API 不兼容异常。没有同一依赖环境的前后基线，不能把全部失败都记为环境反转或无条件宣告零回归。 |

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 固定 head | git rev-parse 4824ed5d4872a6dc519ca6e671bfa6485bd47d9a | Windows PowerShell；仓库工作区 | PASS，输出精确等于给定 SHA | 本 Review 范围核对 |
| 固定提交数量 | git rev-list --count base..head；git log --grep=P09 base..head | 固定区间 | 48 个总提交；18 个 P09 命中 | 本 Review 范围核对 |
| Core / storage / pipeline | python -m pytest tests/core tests/storage tests/m2_resource_channel tests/pipeline -q | Windows；PowerShell；当前 python PATH 环境；固定区间代码未在当前 HEAD 后续更改 | PASS：841 passed, 1 warning，exit 0 | 本次实际运行输出；未单独保存原始 stdout 文件 |
| Packaging / diagnostics | python -m pytest tests/packaging tests/diagnostics -q | 同上 | PASS：84 passed，exit 0 | 本次实际运行输出；未单独保存原始 stdout 文件 |
| Rust phase 测试 | 根目录原命令 cargo test --bin m2rc1-desktop permanently_delete_error_phase 找不到 Cargo.toml；转到 apps/desktop/src-tauri 后运行同一测试 | Windows；Rust crate apps/desktop/src-tauri | PASS：1 passed, 160 filtered out；根目录尝试 exit 101，crate 内 exit 0 | 本次实际运行输出 |
| 前端类型与单测 | apps/desktop/frontend 下 npx tsc --noEmit；npx vitest run | Windows；PowerShell | PASS：tsc exit 0；Vitest 32 files / 327 tests passed | 本次实际运行输出 |
| Governance | pwsh -NoProfile -File tools/governance/check.ps1 | 当前仓库工作区 | PASS，2 个预算告警（STATUS 与 REBASELINE_PLAN 达 80%） | 本次实际运行输出 |
| 全量 Python suite（额外复核） | python -m pytest tests -q -rf --tb=line | 当前 Windows 环境；固定区间相关代码与当前 HEAD 一致 | FAIL：9 failed, 2250 passed, 9 skipped, 2 warnings；failure 明细见 AC12 | 本次实际运行输出；用于 AC12 判别，不替代专项测试 |
| junction 判别测试 | python -m pytest tests/storage/test_preview_unlink_reparse.py -q -vv | Windows；实际创建 junction 的隔离测试目录 | PASS：3 passed；父目录 junction 中的保护文件保持存在 | 本次实际运行输出 |
| AC7 查询同步 | AST 解析 verify_all.py 的 db_scope_queries 与 ac7-verify-query-check.py 的 queries，逐项比较 SQL 字符串 | 固定区间代码 | PASS：9/9 字典相同，键为 books、chapters、reading_progress、book_tags、media_artifacts、pages、regions、region_revisions、artifact_revisions | 本次独立比对；另静态检查主 verifier 对真实 book1.book_id 每项 assert rows == 0 |

本 Review 的测试 stdout 未额外写入日志文件；表中记录了命令、环境、退出结果和可复核汇总。完整 cargo test 未运行；遵照用户给定的环境说明，不把缺少 M2RC1_PYTHON / sidecar 的全量 Rust 失败计作本次回归。未运行 GUI/WebView 集成流程。

## 证据 pin 复核

以下 SHA-256 均用 Windows Get-FileHash -Algorithm SHA256 对磁盘字节实算（CRLF 检出）；commit 用 git cat-file -e <commit>^{commit} 验证，并用 git cat-file -e <commit>:<path> 确认该提交包含对应路径。11 项均通过两项 commit 检查。

| evidence_id | path | Task 期望 SHA-256 | 磁盘 SHA-256 | commit | commit / path |
|---|---|---|---|---|---|
| AC12-REGRESSION | verification/P09-AC3-DELETE-HARDEN-1/ac12-no-regression.md | d65675c91251aaa110af478e67593e4cf8159ed5177449a9c59deb5134a34a94 | d65675c91251aaa110af478e67593e4cf8159ed5177449a9c59deb5134a34a94 | a5221281919dc28cce1fbdec3a9325110251df03 | PASS / PASS |
| AC7-QUERY-CHECK | verification/P09-AC3-DELETE-HARDEN-1/ac7-verify-query-check.py | b409672408c0cf79f9a1f74bb64dc6828496bc65a990d786c7119487422e8afc | b409672408c0cf79f9a1f74bb64dc6828496bc65a990d786c7119487422e8afc | 034d7e3f0a01237ba264615203e59ba3161afe38 | PASS / PASS |
| AC1-DISPATCHER-TEST | tests/core/test_p09_ac1_recycle_bin_route.py | d2dbffc7a13b656cd5e79e03b140caae7c85a2da3d07847ebb512af4fc4ff8de | d2dbffc7a13b656cd5e79e03b140caae7c85a2da3d07847ebb512af4fc4ff8de | 899b72b65d90c6c2f6c0835857ce0b4028b3d71d | PASS / PASS |
| AC4-ORIGIN-TEST | tests/core/test_p09_ac4_translated_preview.py | 5b5e644a8fff89f064acf329e0b0fba5da07158efd643256e1a7dff63b1a523f | 5b5e644a8fff89f064acf329e0b0fba5da07158efd643256e1a7dff63b1a523f | bbf5d13258fdef184fe00745e9c59e207e13be3e | PASS / PASS |
| AC5-REPARSE-TEST | tests/storage/test_preview_unlink_reparse.py | 9fd3a1c7680ce472461dbf450c832ddbdf25e88c2e4dbbb8b32681a189c49e1e | 9fd3a1c7680ce472461dbf450c832ddbdf25e88c2e4dbbb8b32681a189c49e1e | 41fbf2d2e536ad8997750c060749de738a586a45 | PASS / PASS |
| AC2-AC6-AC8-IMPL | src/infrastructure/sqlite/library.py | 6e4babac2ab5f3864743e58c456a5ade17099593972fbaab3ce0d5d25b46c01c | 6e4babac2ab5f3864743e58c456a5ade17099593972fbaab3ce0d5d25b46c01c | 98629ba369f44ea125c039c081ec7a0a8c3d4f33 | PASS / PASS |
| AC1-AC4-CORE-IMPL | src/bootstrap/core_service.py | 5faa0346bc1cde4cc8c6a0c9732264fa77e991a5fb1686ba5c95214ab24eae2e | 5faa0346bc1cde4cc8c6a0c9732264fa77e991a5fb1686ba5c95214ab24eae2e | 5edf207b8b2fce124c5f0da79e6dc701ee6fcdb0 | PASS / PASS |
| AC9-AC1-RUST-IMPL | apps/desktop/src-tauri/src/library_bridge.rs | 6026b952f24cbffd5741caed68d5f24999b795431b65bc16abd9a21f4b21bc18 | 6026b952f24cbffd5741caed68d5f24999b795431b65bc16abd9a21f4b21bc18 | 899b72b65d90c6c2f6c0835857ce0b4028b3d71d | PASS / PASS |
| AC1-UI-IMPL | apps/desktop/frontend/src/recycleBin/RecycleBinPage.tsx | 4c81aa15c0b4a61f56a275dec042571002d688c3316edec99921c9ff244c8a3e | 4c81aa15c0b4a61f56a275dec042571002d688c3316edec99921c9ff244c8a3e | 393e5e7e118c87893926fd33d6975aafe3a9cfc7 | PASS / PASS |
| AC3-CLIENT-IMPL | apps/desktop/frontend/src/library/client.ts | 06ca08658a9d733f58e7993430f4de7316395df84b518828aa2abcea0bfb4e7f | 06ca08658a9d733f58e7993430f4de7316395df84b518828aa2abcea0bfb4e7f | c66fa6e9ea48a4f46c3186dc569131cbe364d9af | PASS / PASS |
| AC7-VERIFY-SCRIPT | verification/P09-AC3-DELETE-1/verify_all.py | 510f7820b5efb1a6cdb0e72dd4c226c19ffd38d11e1c79f83e2f77455547d923 | 510f7820b5efb1a6cdb0e72dd4c226c19ffd38d11e1c79f83e2f77455547d923 | 034d7e3f0a01237ba264615203e59ba3161afe38 | PASS / PASS |

## 磁盘 SHA-256 实算表

下表为当前磁盘字节 SHA-256（CRLF 检出）；对象均在固定区间中有改动。该表用于文件指纹复核，不替代 commit/blob pin。

| 关键文件 | 磁盘 SHA-256 |
|---|---|
| src/bootstrap/core_service.py | 5faa0346bc1cde4cc8c6a0c9732264fa77e991a5fb1686ba5c95214ab24eae2e |
| src/infrastructure/sqlite/library.py | 6e4babac2ab5f3864743e58c456a5ade17099593972fbaab3ce0d5d25b46c01c |
| apps/desktop/src-tauri/src/library_bridge.rs | 6026b952f24cbffd5741caed68d5f24999b795431b65bc16abd9a21f4b21bc18 |
| apps/desktop/src-tauri/src/main.rs | f8fd657c12e4ccdb3839b99f7eecfa4ccbfc1581d7a46e5aed2e98c300ab03c9 |
| apps/desktop/frontend/src/library/client.ts | 06ca08658a9d733f58e7993430f4de7316395df84b518828aa2abcea0bfb4e7f |
| apps/desktop/frontend/src/recycleBin/RecycleBinPage.tsx | 4c81aa15c0b4a61f56a275dec042571002d688c3316edec99921c9ff244c8a3e |
| tests/core/test_core_delete_commands.py | 449225ba85bbfc4933b5097b11b4b68da465d2f3a5066269be4d31f550f21147 |
| tests/core/test_p09_ac1_recycle_bin_route.py | d2dbffc7a13b656cd5e79e03b140caae7c85a2da3d07847ebb512af4fc4ff8de |
| tests/core/test_p09_ac4_translated_preview.py | 5b5e644a8fff89f064acf329e0b0fba5da07158efd643256e1a7dff63b1a523f |
| tests/storage/test_preview_unlink_reparse.py | 9fd3a1c7680ce472461dbf450c832ddbdf25e88c2e4dbbb8b32681a189c49e1e |
| tests/packaging/test_frozen_runtime_contract.py | 34db903ff6cd46737aa30bc076efb2f6e7ddbfe7c46c42a7faf931a178a5c72c |
| verification/P09-AC3-DELETE-1/verify_all.py | 510f7820b5efb1a6cdb0e72dd4c226c19ffd38d11e1c79f83e2f77455547d923 |
| verification/P09-AC3-DELETE-HARDEN-1/ac7-verify-query-check.py | b409672408c0cf79f9a1f74bb64dc6828496bc65a990d786c7119487422e8afc |
| verification/P09-AC3-DELETE-HARDEN-1/ac12-no-regression.md | d65675c91251aaa110af478e67593e4cf8159ed5177449a9c59deb5134a34a94 |
| doc/tasks/P09.md | b32f4daa1426aca83f3a7155e49622192cfb10139ba0f21b239552587eb54f47 |
| doc/tasks/P09-AC3-DELETE-1.md | 67c0c2d074b05f2010a4d3b576b2cc2d2c2e1a4ebf9d5eda74bdf1e9be1856ca |

## 未验证或不能据此宣告通过的事项

- 没有用真实 WebView/Tauri invoke 运行永久删除 E2E；AC3 的形状结论来自本仓 Rust 返回类型、Tauri 2.12.0 invoke 序列化源码及前端 carrier 代码，不是 live GUI 观察。
- 没有真实运行 verify_all.py 全流程；AC7 查询同步来自逐项 AST 比较，实际 verify_all.py 的关联断言来自源码审查。派生文件 orphan 的端到端删除结果未验证，也没有当前 verifier 断言。
- 没有测试盘符相对目录输入、并发替换路径的 TOCTOU 情形，也没有测试永久删除遇到 junction 拒绝后 catalog/manifest 保留与可重试性。
- 没有在固定、可复现的 provider 依赖环境中运行 AC12 前后对照；当前 9 个全量失败只可作为当前环境结果，不能直接证明全部失败均为环境反转或零回归。
- 未运行完整 Rust suite；用户给定的 M2RC1_PYTHON / sidecar 环境限制不用于判定本次回归。
- 固定 head 与当前 checkout HEAD 不同；当前 Task 的 11 条 pin 已按磁盘实算并验证 commit，但 Task 文件本身是 target 之后的文档版本。

## 验证结论与复审

- Architecture：changes requested。F-001 是未冻结 IPC 范围冲突；F-002、F-003、F-004 是删除/清理链路缺口，涉及泄漏、越界删除与不可恢复清理失败。
- Verification：changes requested。AC4、AC5、AC7、AC11、AC12 仍为 PARTIAL；专项测试多数通过，但不能替代这些逐项证据缺口。
- 决策：changes_requested。当前固定 head 不可作为本 Task 的集成批准；修订后应固定新 head，并再次独立验证。P09 的 AC3 delete 子条件必须保持 BLOCKED，不可翻为 PASS。
- 建议下一步：由 Coordinator 先处理 AC1 未冻结命令的契约/范围授权，再安排 AC4 preview 退休与 manifest 清理、AC5 路径和失败重试闭环、AC7 orphan 验收及 AC11/AC12 证据修订；期间保留 P09 AC3 delete 子条件 BLOCKED。
