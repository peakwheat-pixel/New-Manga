# FEA-09 DSH 集成检查点 — Phase C/D 阶段提交（2026-11-03 21:45）

- 阶段 commit：`995d80ca54fbd8dad8a27ae19ab69c7ef45813d8`（实现署名 Codex/ZCode；DSH 集成修复与提交）。
- 起点：`f9a2fa8e0`；Phase A `d3d7cd564`（ZCode）、Phase B `ceae03edb`（ZCode）、Phase C/D 工作树（Codex，Node 通路）+ DSH 6 项集成修复。
- Task 仍 `in_progress`；`canonical_evidence_status: pending`、`resource_closeout_status: pending`；不宣称 Phase C/D 完成或 AC 全 MET。
- 剩余（按 Handoff/EV 与 Task AC）：生产 rendition 读取接线、密码完整链路、真实 IPC/V2 证据、AC-1…AC-10 部分验证、独立 impl Review、最终 DSH 集成验证。

## DSH 实际验证（本机主环境）

| 验证 | 结果 |
|---|---|
| `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | EXIT 0；0 warning / 0 error |
| `dotnet test …NewManga.sln --no-build --settings …runsettings --nologo` | EXIT 0；**1298 passed / 0 failed / 57 skipped**（基线 1292/0/57，+6 新增） |
| `python -m pytest tests/fea09 tests/import_formats tests/storage -q` | EXIT 0；**245 passed** |
| `python -m pytest tests/fea09 -q` | EXIT 0；**92 passed** |
| `python -m pytest tests/core/test_architecture.py tests/core/test_bootstrap.py tests/core/test_core_service.py -q` | EXIT 0 |
| `dotnet test Host.Tests --filter SourceRegistryTests` | EXIT 0；2 passed |
| `pwsh tools\governance\check.ps1 -TaskPath doc\tasks\FEA-09.md` | EXIT 0；PASS(3) |
| `pwsh tools\governance\verify_pins.ps1` | EXIT 0；17/17 PASS |
| 旧 FEA-06 四 PNG | 4/4 与基线一致（Codex 日志 `fea06-png-audit.json`） |
| allowed_paths 对照 | 全部工作树变更在写域内；无冻结契约/共享组合根/UI/依赖改动 |

原始日志：`G:\CODEX\New Manga.workspace\FEA-09\dotnet-dsh-full-r2.log`、`python-fea09-after-fix.log`、`python-core-fix-verify.log`、`dotnet-host-registry-test.log`、`dotnet-build-after-fix.log`；仓库内：`verification/FEA-09/logs/`。

## DSH 集成修复清单

1. `src/application/importing/referenced/scanner.py`：删除 application→infrastructure 动态 import，改为 `install_verified_reader` 注入；`src/infrastructure/resource_channel/source_strict_read.py` 提供 `read_verified_bytes`；`src/bootstrap/core_assembly.py`、`tests/fea09/conftest.py` 注入。
2. `tests/core/test_bootstrap.py`：fake `MigrationRunner` 接受 C-15 新增 `validate` 参数。
3. `tests/core/test_core_service.py`：capability/E2E 断言同步 C-16 `source.read/1`。
4. `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceSecurity.cs`：`SetOwner(当前用户)` 后再校验 owner（修复 repo 证据目录继承 Administrators owner 的误拒）。
5. `tests/fea09/test_referenced_flow.py`：撤销边界测试按 Phase C 双次验证（读前+提交前）修正触发计数。
6. Handoff/EV/Task 指针：本检查点与 commit 记录。

## 明确未完成/未验证

- 生产 rendition 读取（`handle_resolve_page_resource` 对 referenced 的完整接线）与密码完整链路（DPAPI 秘密文件→导入解密→清理）在契约层已实现方向，但**未完成生产端到端**。
- 真实 Host IPC + 现有 V2 生产 adapter 的端到端证据未完成（AC-6 BLOCKED）。
- AC-1…AC-10 仍按 Codex Handoff 标 PARTIAL/BLOCKED；不得据此宣称完成。
- 独立 impl Review 未进行；DSH 集成验证仅是阶段验证。
