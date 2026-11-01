# FEA-03 验证命令记录

日期：2026-11-02（Asia/Shanghai）
仓库：G:\CODEX\New Manga.workspace\FEA-03
Branch：feat/fea-03
HEAD：b83bc7703a6224d54d13bd1aef9591a4edc3aeee
运行时：Windows；CPython 3.14；.NET SDK 10.0.401；Roslyn 5.9.0

## 测试与静态检查

| 命令 | 结果 | 说明 |
|---|---|---|
| python -m pytest tests/editing tests/domain tests/infrastructure tests/core/test_region_write_commands.py tests/core/test_region_batch_locking.py -q | BLOCKED，exit 1 | C:\Python314\python.exe: No module named pytest；没有收集或运行测试。 |
| dotnet test apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/NewManga.ApplicationCore.Tests.csproj | BLOCKED，exit 1 | restore 阶段失败：NuGet.targets(782,5) Value cannot be null. (Parameter 'path1')；两个项目均未进入测试执行。 |
| python -m compileall -q src/application/editing src/domain/drafts src/infrastructure/filesystem/draft_journal.py src/infrastructure/sqlite/regions.py tests/editing/test_draft_protection.py tests/domain/test_drafts.py tests/infrastructure/test_draft_journal.py | PASS，exit 0 | 修改的 Python 源与测试源语法编译通过。 |
| dotnet exec "C:\Program Files\dotnet\sdk\10.0.401\Roslyn\bincore\csc.dll" @C:\Users\49745\AppData\Local\Temp\fea03-csharp-compile\compile.rsp | PASS，exit 0 | DraftBuffer.cs 直接编译；有 response file 的 CS2023 提示。 |
| dotnet exec "C:\Program Files\dotnet\sdk\10.0.401\Roslyn\bincore\csc.dll" @C:\Users\49745\AppData\Local\Temp\fea03-csharp-compile\testcompile.rsp | PASS，exit 0 | C# 测试源直接编译；有手工引用目标框架导致的 CS1701 警告，不能替代 dotnet test。 |
| git diff --check | PASS，exit 0 | 无 whitespace errors。 |
| git diff -- src/application/editing/service.py src/infrastructure/sqlite/schema.py | PASS，空差异 | 旧保存服务与 schema 未改。 |

## 可复跑的补充手工 Smoke

| 命令 | 结果 | 说明 |
|---|---|---|
| python verification/FEA-03/component_sqlite_smoke.py | PASS，exit 0 | 真实 SQLite adapter 组件 smoke；不是 assemble_production_core 对象图。
| python verification/FEA-03/crash_probes.py | PASS，exit 0 | 真实子进程 CRASH-A/B/C 与 .lock 探针。

## production assembly 尝试

命令：python -c "import sys; sys.path.insert(0, 'src'); from bootstrap.core_service import assemble_production_core"

结果：BLOCKED，ModuleNotFoundError: No module named 'PIL'，发生于 core_assembly 导入 infrastructure/export/qt_free.py。D4 要求从 assemble_production_core 对象图执行 CORE V 测试；本环境未达到该验收入口。组件级 SQLite smoke 见 manual-smokes.md，不将其冒充 production assembly 测试。

## Pin

工作树直接运行 pwsh -NoProfile -File tools/governance/verify_pins.ps1：FAIL，15/15 mismatch。诊断为 Git 全局 core.autocrlf=true，冻结源在工作树被检出为 CRLF，而 pin 针对 HEAD 中的冻结字节。

将 HEAD 中的 frozen-record 和 contract source blob 复制到临时 fixture 后运行同一 verify_pins.ps1：PASS (all 15)，C-13 pin=8faf1e805eac。详情见 pins.md。