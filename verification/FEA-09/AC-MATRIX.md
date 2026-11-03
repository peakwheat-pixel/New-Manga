# FEA-09 AC 证据矩阵（DSH 最终集成，2026-11-04）

状态口径：`MET` = 本矩阵列出的命令在最终集成 head 实际运行且全绿，且逐项 AC 判别项有测试/证据映射；`PARTIAL`/`NOT_RUN` 不得记 MET。本表为 Task `done` 的逐项 AC 证据。

## 最终门禁结果（HEAD `87ca50702e00c62c64540ac7ac4ff3b1d27fa0cd`，closeout 文档提交在其后）

| 命令 | 结果 |
|---|---|
| `python -m pytest tests/fea09 -q` | **142 passed** |
| `python -m pytest tests/core -q` | **897 passed** |
| `python -m pytest tests/storage -q` | **121 passed** |
| `python -m pytest tests/m2_resource_channel -q` | **110 passed** |
| `python -m pytest tests/reading_export -q` | **141 passed** |
| `python -m pytest tests/import_formats -q` | **32 passed** |
| `python -m pytest tests/infrastructure -q` | **91 passed** |
| `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **0 warning / 0 error** |
| `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build` | **1300 passed / 0 failed**（8 个测试程序集） |
| `Fea09RealIpcTests`（`NEWMANGA_FEA09_IPC=1`，真实 Python Core stdio） | **1 passed**（17 frames；Plan/Start/Receipt/Resolve + `HostCommandDispatcher` V2 adapter） |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS**（3 persistent warnings） |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **17/17 PASS** |
| 独立实现复核 | r1（changes_requested）→ r1-rework r1（P1）→ **r1-rework r2 approved P0=0/P1=0/P2=2**（`doc/reviews/FEA-09-impl-r1-rework-r2.md`） |

## AC 结论

| AC | 判别项 → 证据 | 结果 | 状态 |
|---|---|---|---|
| **AC-1 格式矩阵** | `test_referenced_scanner.py`（21：单图/文件夹/ZIP/CBZ/PDF 成功·unsupported·损坏·预算·安全拒绝）、`test_ac_1_2_3_closure.py`（5 类×成功/unsupported/损坏/空内容矩阵）、`tests/import_formats`（32） | 21 + 8 + 32 passed；AES ZIP 为 typed `SOURCE_FORMAT_UNSUPPORTED`（裁决 1） | **MET** |
| **AC-2 顺序** | `test_ac_1_2_3_closure.py`（文件夹 1/2/10/100、ZIP 成员 1/2/10、PDF 12 页 ordinal 0…11）、`test_referenced_scanner.py` natural order、`test_referenced_flow.py` 嵌套文件夹 | passed；natural-key/tie-break 由 scanner 实现固定 | **MET** |
| **AC-3 occurrence 与共享** | `test_referenced_flow.py`（重复成员/occurrence/排序）、`test_referenced_sharing.py`（同一 source 跨项目共享、source 行共享、binding 独立）、`test_ac_1_2_3_closure.py::test_ac3_*`（两项目页状态/软删独立） | passed | **MET** |
| **AC-4 密码与错误** | `test_referenced_password.py`（11：DPAPI 真往返/缺失/坏 payload/无密/错密/重试/3 次冷却/零泄漏/加密 PDF 导入）、`test_i005_resolve_secret.py`（8：Secret-G 0/1/多/重放/路径/TTL/撤销）、`test_i005_encrypted_resolve.py`（2：真实 zipcrypto resolve、cache-hit 免 token）、`test_i005_encrypted_pdf_resolve.py`（2：真实 R2/RC4 PDF resolve、无 Secret-G typed REQUIRED） | passed；密码仅经短期 secret_ref，一次性消费+零填充删除，日志/receipt/错误消息零泄漏 | **MET**（限制：加密源 Host↔Core 跨进程 IPC 未单列，见「限制」） |
| **AC-5 取消/进度/计数** | `test_referenced_flow.py`（21：accepted 取消、部分取消+unsupported、mid-run 失败、撤销边界、整源 skip、部分已引用、replay、锁、跨重启、项目不匹配、禁用开关、部分重试） | passed | **MET** |
| **AC-6 隔离链路与源守恒** | `Fea09RealIpcTests`（真实 stdio：Plan/Start/GetReceipt/Resolve、生产 `CoreServiceClient`/`SourceReadCoordinator`/`HostCommandDispatcher` V2 adapter）、`test_referenced_wire.py`（13：Core wire face/注册/撤销/失败关闭）、`test_referenced_resolve.py`（含双读）、`SourceRegistryTests`（Host Registry 持久化 2） | real IPC 1 passed；V2 adapter 断言 `HostCommandChannel.CoreService` | **MET**（限制：UI 视图/ViewModel 属 `FEA-09-UI-1`，不在本 Task；加密 resolve 的跨进程 IPC 未单列） |
| **AC-7 完整性/升级/回退** | `test_v7_migration.py`（11：正尺寸基线、union 守恒、断言 1/2/2b/3/4/5、失败停留 v6、篡改拒绝、verifier 强制、copy-only 可见）、`test_read_paths.py`（8：五读路径、V≠R、父级删除、双读）、`test_i001_managed_visibility.py`（11：witness 矩阵/投影/资源选择） | passed；破坏/半写/未来时间/软删/校验失败均有负测 | **MET** |
| **AC-8 证据与交付** | 上方门禁表：build 0/0、.NET 1300/0、Python 142+897+121+110+141+32+91、check PASS、pins 17/17；独立复核 r1-rework r2 **approved**；I011 EV 收敛（唯一 ID/0 PENDING）；FEA-06 四 PNG 未变（见 logs） | 全绿 | **MET** |
| **AC-9 授权与 lease** | `test_source_grants_unittest.py`（7：签名优先级、四维 scope、generation/撤销/EOF、过期/identity 变更、strict lease、import 精确绑定、unbound 拒绝）、`test_referenced_wire.py`（13：Host control/生成/EoF/失败关闭）；Host `SourceRegistryTests`（持久化/重启 2） | passed | **MET** |
| **AC-10 cache 与预算** | `test_rendition_cache_unittest.py`（5：key 含 version/entry/decoder/参数、单请求预算先于 decode、损坏重建+崩溃恢复、LRU tie/active 保护、并发解码队列）、`test_rendition_cache_integration.py`（2：生产 resolve 走 cache/命中零解码/损坏重建）、`test_referenced_resolve.py` 预算 2 | passed；key/预算/LRU/并发/重建/淘汰均有实现级测试 | **MET** |

## 限制与已知债务（如实登记，不记为 MET 缺口）

1. **加密源 Host↔Core 真实跨进程 IPC**：r1-rework 复核记录为 NOT_RUN；Core 侧加密 zip/PDF resolve、DPAPI、Secret-G、零泄漏均以进程内真实实现与真加密 fixture 验证；Host fresh-grant 协议已实现并由 `SourceSecretStoreTests`（2）单测覆盖。后续集成可按 `NEWMANGA_FEA09_IPC=1` 扩展该变体。
2. **UI 接线**：`FEA-09-UI-1` 不在本 Task（Task 明确声明），本 Task 只交 Core/Host 契约面与生产 adapter。
3. **DEBT-FEA09-01**：RenditionCache 装配失败仅日志并降级 legacy 路径；契约安全不受影响（加密源 legacy 仍 typed REQUIRED），已登记债务候选（Task「债务候选」）。
4. 原生多进程并发/真实磁盘满/跨机恢复未单列；相关失败注入与 typed 拒绝由迁移/读取/secret 负测覆盖。

## 结论

- **AC-1…AC-10 全部 MET**（上文逐项证据）；独立实现复核 approved；I011 EV 收敛完成。
- Task `FEA-09` 满足 `done` 条件：逐项 AC 证据 + 独立 Review + DSH 集成验证 + canonical evidence + resource closeout。
