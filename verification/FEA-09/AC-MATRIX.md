# FEA-09 AC 证据矩阵（DSH 集成，2026-11-03 22:30）

状态口径：`PASS` = 本矩阵命令实际运行且全绿；`PARTIAL` = 已有实现/部分测试，但仍缺本 Task AC 要求的判别项；`NOT_RUN` = 未执行。**本矩阵不把 PARTIAL 当 MET。**

| AC | 覆盖测试/证据 | 实际结果 | 状态 | 缺口 |
|---|---|---|---|---|
| AC-1 格式矩阵 | `tests/fea09/test_referenced_scanner.py`（21）、`tests/import_formats/` | 21 passed（scanner）；import_formats 见 `pytest tests/fea09 tests/import_formats tests/storage` 245 passed | PARTIAL | 五类 fixture 的成功/unsupported/损坏/空内容矩阵未逐项对表；AES ZIP typed unsupported 仅扫描层断言，缺逐 fixture SHA-256 表 |
| AC-2 顺序 | `test_referenced_scanner.py`、`test_referenced_flow.py`（自然序 001/002/010/dup） | 同上 | PARTIAL | PDF 数值页码/文件夹 1/2/10/100 稳定 tie-break 的完整回归未单列 |
| AC-3 occurrence/共享 | `test_referenced_flow.py`（21，occurrence）+ `test_referenced_sharing.py`（1，跨项目共享同一源/source 行共享、binding 独立） | passed | PARTIAL | 两项目阅读进度/人工修改/处理结果独立回归未写 |
| AC-4 密码 | `test_referenced_password.py`（10） | 10 passed | PARTIAL | 生产 secret 文件 → 导入解密 → 删除链路已接线（`read_secret`）；真实 DPAPI 产品路径与日志扫描未跑；AES 仅 typed unsupported |
| AC-5 取消/进度/计数 | `test_referenced_flow.py`（21，含 accepted 取消/部分取消/失败/计数/跨重启/自然键） | passed | PARTIAL | 丢 ACK/异常/解码中取消的扩展场景未单列；Host 可观察进度的真实 IPC 未验 |
| AC-6 隔离与 V2 | `test_referenced_resolve.py`（7，含 Core wire face/双读）；Host `SourceRegistryTests` 2；**`Fea09RealIpcTests` 真实 stdio**（Plan/Start/Receipt/Resolve + `HostCommandDispatcher` V2 adapter，17 frames） | real IPC 1 passed；组件 9 passed | PARTIAL | 真实 Host IPC 与生产 V2 command adapter 已过；UI 视图/ViewModel 归 FEA-09-UI-1；其余 AC 行为未逐一 IPC 化 |
| AC-7 完整性/迁移/回退 | `test_v7_migration.py`（9）、`test_read_paths.py`（8）、`test_referenced_resolve.py`（7，含双读 managed+referenced resolve）、flow `test_disabled_flag_rejects_new_imports` | passed | PARTIAL | 缺文件/磁盘满/中断不切入口负测未单列；迁移双集合已测 |
| AC-8 证据与交付 | `dotnet build` 0/0；`.NET` 全量 **1298/0/58**（含真实 IPC 测试默认跳过）；`pytest tests/fea09` **100**；`check.ps1` PASS；`verify_pins` 17/17；FEA-06 四 PNG 未变 | 全绿 | PARTIAL | 独立 impl Review 未 Appointment/进行；最终 DSH 集成验证未完成 |
| AC-9 授权/lease | `test_source_grants_unittest.py`（5）、`test_referenced_wire.py`（13，含 Host 命令/脱敏/撤销） | 18 passed | PARTIAL | Registry 重启/根替换/跨根 reparse 的原生组合未全跑；Host 侧 Revoke ACK/EOF 竞态未集成测 |
| AC-10 cache/预算 | `test_rendition_cache_unittest.py`（5）、`test_referenced_resolve.py`（cache 行/预算 2） | 7 passed | PARTIAL | LRU/总字节上限/并发解码上限/崩溃恢复/通道隔离未接线验证（当前仅 row 写入 + 单请求预算） |

## 复现命令

```text
python -m pytest tests/fea09 -q                      # 98 passed
python -m pytest tests/fea09 tests/import_formats tests/storage -q   # 245 passed
python -m pytest tests/core/test_architecture.py tests/core/test_bootstrap.py tests/core/test_core_service.py -q
dotnet build apps/desktop-avalonia/NewManga.sln --nologo          # 0 warning / 0 error
dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings --nologo  # 1298 passed / 0 failed / 57 skipped
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-09.md   # PASS (3 warnings)
pwsh -NoProfile -File tools/governance/verify_pins.ps1                            # 17/17 PASS
```

## 结论

- 无 AC 达到 MET；AC-6/AC-8 仍有关键缺口（真实 IPC/V2、独立 Review）。
- 下一步优先级：① Host↔Core 真实 IPC resolve/import 端到端证据；② 双读与回退开关集成断言；③ AC-1…AC-5 逐项 fixture 表补齐；④ 独立 impl Review。
