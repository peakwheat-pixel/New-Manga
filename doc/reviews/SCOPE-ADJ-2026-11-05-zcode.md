# SCOPE-ADJ-2026-11-05（ZCode 裁决记录）

> 背景：用户 2026-11-05 明确「裁决交给 codex 或 zcode」。Codex 额度耗尽（两次 `category: limit` 失败）后由 ZCode 承接；ZCode 对 4 份 scope review 的歧义点给出逐项裁决。本文件为由 Lead 转录的裁决摘要（ZCode 原始输出见会话记录；卡内引用本文件与 scope review）。
> 基线：`main@604a2d343`（scope review 时点）。

## A. FEA-11-MATCH-1（可冻结）
- A1 解码约定：接受，卡内冻结（EXIF 转置归一化、W/H=转置后、orientation 恒 1、params canonical 对象哈希，修复 `scanner.py:545-555` 双重编码）。
- A2 旧 pixel 缺失但 W/H 存在：接受 `changed → missing_old`；窄批 `tests/fea11/test_source_scan.py` 1–2 行。
- A3 写域：否决扩 `service.py` / `ports.py`+`core_assembly.py`（PDF raster 另卡；`service.py` 登记 L-M3）。
- A4 reason 映射：接受（加密→encrypted；解码失败/预算超限→unsupported；content_digest 缺失→missing_evidence）。
- A5 counterpart-less 重复成员：接受归 `missing`/`added`，totals 变化登记。
- A6 PDF pixel profile OUT + L-M1；W1 窄批；W2/W3 不扩。

## B. FEA-12-UI（可冻结；整卡释放依赖 CORE 重冻/closeout）
- Q1 C-07：接受独立 `ITrashController` 替代 additive；冻结记录显式写明「满足 ADJ :41 additive 意图、无需 UNFREEZE」；`generate_api_inventory.py --check` PASS + pins 18/18 作门禁；`IHostController.cs`/C-07 清单列入禁止清单。
- Q2 首版只做单本彻底删除（批量 OUT/L1；`is_whole_library` 不过滤 `deleted_at` 的死路依据）。
- Q3 数据源 `ListTrash`（`ListRecycleBinBooks` 冻结面不动；不显示总数、cursor 不持久化）。
- Q4 书架侧「移入回收站」入口属本卡（否则回收站永空）。
- Q5 Fluent 仅文案诚实化；Q6 软删撤销（复用 RestoreFromTrash）；Q7 独立 TrashViewModel（允许并入，路径由 Owner 定）；Q8 本卡 L2 headless+真实 IPC，真机 L3 OUT/L10。
- 附加核实：ADJ :41 为预期口径非唯一机制，B1 不违背保护意图。

## C. FEA-11-AC4-GAPS-1（需修改后冻结）
- C1 纳入 AC4（G4–G11 漂移矩阵 + 全表零写精确比较集）；只做 L-5 三项则卡面必须写「AC11-4 仍 PARTIAL、G4–G11 转 limitation」，禁止以 done 推 MET。
- C2 same-op 第二响应=返回原 receipt（accepted=true）；「仅一个成功」改为「恰好一次业务提交」；typed 冲突仅 different-op；跨实例 same-op replay Out。
- C3 双分支都测：plan 自带过期 migrate revision → `STALE_BASE_REVISION`；现实漂移 → `SOURCE_PLAN_STALE(cause=manual)`。
- C4 AC2-c 要求 wire 级 `SOURCE_SYNC_STORAGE_FAILED` 证据；增列 `tests/fea11/test_source_sync_storage.py`。
- C5 AC1-c 必需（两个独立 registry/stack → 同一文件 DB），登记 L1「非生产装配 seam 防御证据」。
- C6 不允许 `service.py` 行为修复，严格 test-only；从 allowed_paths 移除 `service.py`/`source_sync.py`。
- C7 0 C# diff 时 .NET `NOT_RUN` + 理由可接受，禁止写 PASS。
- C8 depends_on 统一为 `FEA-11`。
- 补充：G12 拒绝审计=C-17 §6.2 明文禁止非缺口；AC11-4 口径=本卡纳入 AC4 后为完整收口卡，全 AC 交付+Review 通过即 MET（L1–L4 limitation）。

## D. FEA-11-SCAN-1（需修改后冻结；方案 A=Host 侧只读周期触发切片）
- D1 方案 A + L-A limitation；冷启动全源枚举另立 `FEA-11-SCAN-2`（proposed，不释放）。
- D2 不要求用户可见状态条。
- D3 C-09 SC-B08 仅约束自动备份调度；窄裁定写入 Appointment/卡内说明，不改 C-09 字节。
- D4 enabled=true、interval=900s；env `NEWMANGA_SOURCE_SCAN_INTERVAL_SECONDS` [60,86400] 非法回落+WARN；不加 settings section。
- D5 状态面 in-process 属性（`HostRuntime.SourceScanStatus`），不新增 wire 命令。
- D6 watcher 另立 `FEA-11-WATCH-1`（proposed）；AC11-1 done 后仍 PARTIAL（仅闭合定时扫描半边）。
- D7 可冻结：allowed_paths 换 Host 侧（删 5 个 Python 草案项，加 4 新 C# + 4 改 C#）；AC-S1…S6 按 scope §3；零契约/schema/依赖改动，18 pins 不受影响。

## 落卡结果
- `doc/tasks/FEA-11-MATCH-1.md`、`FEA-11-AC4-GAPS-1.md`、`FEA-11-SCAN-1.md`（重写）；`doc/tasks/FEA-12-UI.md`（新建）；占位 `FEA-11-SCAN-2.md`、`FEA-11-WATCH-1.md`。
- 均 `status: proposed`（未被 Lead 释放前不得实施）；Lead 已确认 scribe 的路径澄清（`ISourceImportController` 替代 `IHostController`、`LibraryViewModel.cs`/`FakeHostController.cs` 补充、FEA-12-UI 的 App/Services 路径解释与 `LibraryView.axaml(.cs)` 补充）。
- 释放顺序建议（ZCode）：先 `FEA-11-AC4-GAPS-1`（test-only）→ `FEA-11-MATCH-1` → `FEA-11-SCAN-1` → `FEA-12-UI`（依赖 CORE 重冻/closeout）。
