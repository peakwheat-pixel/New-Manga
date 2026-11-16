---
id: FEA-14-FONT-1
title: FEA-14 切片 FONT-1：Core 字体库（安装/列举/预览/删除 + 内置字体）
kind: implementation
governance_version: 3
status: closed_with_limitations
approval: **DSH 2026-11-10 冻结**（`ADJ-2026-11-10-FEA14-S5-SCOPE` §2.1/§2.2；PREQ-1 wire 预冻结 FONT P1–P4；侦察 `recon.md` §2.3）
suggested_owner: dsh
owner: dsh
reviewer: r5 独立复核 approved（`doc/reviews/FEA-14-FONT-1-r5.md`，P0/P1/P2=0；P3=2 登记）
depends_on:
  - FEA-14-S5-PREQ-1
base_commit: 24637d1b4
branch: null
worktree: null
integration_commit: 8e39bb72c
delivery_head: 8e39bb72c
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-14-FONT-1
allowed_paths:
  - doc/tasks/FEA-14-FONT-1.md
  - doc/reviews/FEA-14-FONT-1-*.md
  - doc/reviews/CONTRACT-UNFREEZE-*.md
  - doc/handoffs/FEA-14-FONT-1-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/plan/FEA-C07_API_INVENTORY.md
  - doc/plan/FEA-CONTRACT-FROZEN-C07.md
  - verification/FEA-14-FONT-1/**
  - src/application/fonts/service.py
  - src/application/fonts/ports.py
  - src/infrastructure/sqlite/schema.py
  - src/infrastructure/sqlite/fonts.py
  - src/bootstrap/core_assembly.py
  - src/bootstrap/core_service.py
  - apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs
  - tests/storage/test_fonts.py
  - tests/storage/test_reading_preferences.py
  - tests/core/test_v9_migration.py
  - tests/fea09/test_v7_migration.py
  - tests/fea11/test_source_gate_unify.py
  - tests/core/test_font_wire.py
out_of_scope:
  - 不随包分发商业/系统字体（许可证红线；内置字体仅限已授权开源字体，缺省不随包）
  - 不改冻结契约字节（C-07 统计节按实现落地更新，pin 重算须记录）
  - 不实现字体渲染管线（渲染仍用 Avalonia/系统字体；本卡只做字体库数据面）
  - 不修改 FEA-15 正式验收声明
---

# FEA-14-FONT-1：Core 字体库

## 背景

FEA-14 S5 FONT 切片（FEA-00 §12.2/§15.6）需要字体库数据面：安装/列举/预览/删除用户字体与内置字体元数据。PREQ-1 已预冻结 FONT wire P1–P4（`GetFontsAsync`/`InstallFontAsync`/`DeleteFontAsync`/`GetFontCatalogAsync` 等，具体以 `FEA-14-S5-PREQ-1-wire-r1.md` §8 为准）。侦察确认现有字体消费仅 `FontFamily.Name`（Avalonia 首族），无数据面。

## Scope 冻结（2026-11-10，DSH）

1. Core：字体库 service + schema v11（`user_fonts` 表：id/display_name/family/weight/style/path/sha256/installed_at；内置字体元数据只读种子，不随包依赖）。
2. 字体安装：从用户选择的字体文件复制到 data root `fonts/`（受管路径 + sha256 校验 + 拒绝越界）；删除受管文件与行。
3. Host：P1–P4 四条命令（additive；旧签名不变），按 C-07 冻结记录流程更新 inventory 并重算 pin。
4. 许可证：内置字体仅当已确认许可兼容；默认不随包（缺省空列表），文档记录边界。
5. 证据：pytest 定向/全量、App.Tests、check/pins/API inventory。

## Acceptance Criteria

- [x] **AC1 字体安装**：合法字体文件 → 复制到受管 `fonts/`、行记录（family/subfamily/format/sha256；**weight/style/display_name 不在本卡**——需 fontTools 解析，登记 limitation）；重复安装同 sha256 幂等；越界/非字体文件拒绝（typed，魔数与扩展名必须一致）。 <<MET>>
- [x] **AC2 删除**：删除行（soft delete）+ **删除受管副本**；不存在/已删 → typed `FONT_NOT_FOUND`；不触碰用户源文件。 <<MET>>
- [x] **AC3 列举/目录**：列举已安装字体（排除 deleted；**wire P1 保持 PREQ `{}` 形状、不做 family/weight 过滤——过滤留 FONT-2**）；**内置条目缺省为空（PREQ：不随包任何字体）**；数据与磁盘一致（refresh）。 <<MET>>
- [x] **AC4 迁移无损**：schema v11 additive；既有用户数据行不受影响。 <<MET>>
- [x] **AC5 契约/门禁**：P1–P4 按 PREQ §8 形状；`generate_api_inventory.py --check` EXIT 0；`verify_pins` 18/18（C-07 pin 更新记录）。 <<MET>>
- [x] **AC6 证据**：定向 pytest/App.Tests 通过；`verification/FEA-14-FONT-1/` 日志含 EXIT；NOT_RUN（真实字体渲染/随包字体）如实登记。 <<MET>>


## r1 处置记录（2026-11-10，对 `40c252904` 的 changes_requested）

- **R1-001（P2，已修）**：`_font_format` 改为**魔数与扩展名必须一致**（任意内容改 `.ttf` 不再通过）；补 PNG/伪装 `.ttf` 拒绝测试；AC1 口径同步（weight/style 不在本卡，登记 limitation）。
- **R1-002（P2，已修）**：`delete_asset` 删除受管副本 + 不存在/已删 → typed `FONT_NOT_FOUND`；wire handler 映射 `not_found`；测试更新（源文件保留、受管副本删除、二次删除 typed）。
- **R1-003（P2，已修/口径）**：`list_assets` 排除 deleted 并支持 family 过滤；内置条目缺省空（PREQ 不随包）；weight 过滤登记 limitation。
- **R1-004（P2，已修）**：allowed_paths 补 UNFREEZE 载体与 4 个 v11 适配测试（`test_reading_preferences.py`/`test_v9_migration.py`/`test_v7_migration.py`/`test_source_gate_unify.py`）。
- **R1-005/R1-006/R1-007（P3）**：Host P2 DTO 空 Format/Sha256 登记（P2 wire 仅回 asset_id/family/subfamily）；补边界测试（伪装格式/删除 typed/list deleted）；base 校准 `24637d1b4`、新增 v11 回归日志 `regression-v11.log`。


## r2 处置记录（2026-11-10，对 `133498d33` 的 changes_requested）

- **R2-001（P2，口径修正）**：wire P1 保持 PREQ §8 的 `{}` 形状，**不增加 family/weight 过滤**（过滤留 FONT-2）；AC3/README 口径同步（service 层保留 `family` 参数供内部/测试）。
- **R2-002（P3，已修）**：删除受管副本失败不再静默——`FONT_DELETE_FAILED` typed 错误（行已软删，调用方可重试/上报）。
- **R2-003/R2-004（P3，登记）**：Host P2 import 返回空 Format/Sha256/Size（PREQ P2 仅回 asset_id/family/subfamily/status；UI 可 import 后 List 刷新）；边界测试（>50MB/>200/并发/refresh sha mismatch）登记。


## r3 处置记录（2026-11-10，对 `0b0733322` 的 changes_requested）

- **R3-001（P2，已修）**：删除改为**先删受管副本、成功后再 soft_delete**——失败时 row 保持 active，可重试；测试补「失败后 row 仍 active、retry 成功」。
- **R3-002（P3，已修）**：wire 删除错误按 code 映射类别——`FONT_NOT_FOUND` → `not_found`；`FONT_DELETE_FAILED` → `write` + retryable。
- **R3-003（P3，已修）**：日志 HEAD/Canonical 行数说明修正（Canonical 实际 5 行 EV-FN-001..005）。


## r4 处置记录（2026-11-10，对 `2bec370e7` 的 changes_requested）

- **R4-001（P2，已修）**：`FONT_DELETE_FAILED` 的 category 由未登记的 `write` 改为既有 taxonomy **`internal`**；卡面「+ retryable」措辞删除（retryable 由 code 表达）。
- **R4-002（P3，登记）**：wire 级 `FONT_DELETE_FAILED` 负例未补（wire P1 不回 managed_path，测试无法定位受管文件；storage 层已覆盖失败/重试）；登记。
- **R4-003（P3，登记）**：pytest-font.log/App 全量日志 HEAD 为生成时工作树；Canonical 5 行正确。


## r5 复核与收口（2026-11-10）

- r5：**approved**（P0/P1/P2=0，P3=2），报告 `doc/reviews/FEA-14-FONT-1-r5.md`。
- R5-001（P3，已处理）：r3 历史记录标注「已被 R4-001 修正」，`write`/`retryable` 措辞作废。
- R5-002（P3，登记）：pytest/App 日志 HEAD 为生成时工作树；Canonical 5 行正确；wire 失败负例留 FONT-2。

## 证据计划（L2）

`verification/FEA-14-FONT-1/`：`logs/`（pytest 定向/全量、App.Tests、门禁、API inventory、pins）、字体 fixture 清单与 sha256、NOT_RUN、复现命令。

## 风险与回退

| 风险 | 处置 |
|---|---|
| 商业/系统字体随包（许可证） | 默认不随包；内置条目需授权记录，否则空 |
| 越界写入（路径注入） | 受管路径校验 + 只复制到 `fonts/` + sha256 |
| 删除误伤用户源文件 | 只删受管副本；源文件只读 |
| schema 迁移风险 | v11 additive + pre_migration 备份 + 失败即停 |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| temp | `G:\CODEX\New Manga.workspace\FEA-14-FONT-1\`（字体 fixture/数据根） | NOT_APPLICABLE | — | — | 仓外，不提交 |
| user-data | `C:/Users/49745/AppData/Roaming/com.newmanga.desktop` | PRESERVE_USER_DATA | — | — | 只读；测试用隔离根 |
| build | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 复用现有环境 |
| worktree | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 主树实现 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-FN-001 | FONT-1 | `verification/FEA-14-FONT-1/logs/dotnet-app-tests.log` | `-` | `fd837f5fe5af02719c261db4f2e5043619eb95e3da21917c727cec1571b5696a` | CANONICAL |
| EV-FN-002 | FONT-1 | `verification/FEA-14-FONT-1/logs/pins-api.log` | `-` | `9d798a9b0a0637abe5ddc41b74f2915997cb933ef4be16fa9da064531336b5e6` | CANONICAL |
| EV-FN-003 | FONT-1 | `verification/FEA-14-FONT-1/logs/pytest-font.log` | `-` | `6321dedf6973a44d8e1f818e3758e4cb0e02f804a855a5513db5a1b159680c9b` | CANONICAL |
| EV-FN-004 | FONT-1 | `verification/FEA-14-FONT-1/logs/regression-v11.log` | `-` | `9934a4a4e67b8cc4435fbd0fd63a9232ced1e3ecd40d8dcb70d0e354fa081d37` | CANONICAL |
| EV-FN-005 | FONT-1 | `verification/FEA-14-FONT-1/README.md` | `-` | `56581d3f17faae7cec09ed8ecb9f26a8e6fad66acb726529474a0007706fd29e` | CANONICAL |

## Closeout Record

- 结论：**完成（带 limitation）**（2026-11-10）。r1–r4 changes_requested（严格格式/删除语义/list 过滤/删除顺序/category）→ **r5 approved**（P0/P1/P2=0，P3=2 登记）。
- 交付：schema **v11** `font_assets` + `FontLibraryService`（导入/软删+受管删除/refresh，严格魔数+扩展名、≤50MB/≤200、sha256、typed 错误）+ wire P1–P4 + Host 三层 4 方法 + C-07 UNFREEZE v1.4（65/72，pin `8d92a32f…`）；定向 8 passed、v11 回归 1235、App 874/0/11、pins 18/18。
- **Limitation**：FONT-2 范围（字体渲染消费、Fluent 设置页字体 UI、字体家族/字重元数据解析需 fontTools、内置字体需授权记录——**不随包任何字体**）；wire 级 FONT_DELETE_FAILED 负例未补（storage 已覆盖）；大文件/并发/占用文件未压测；日志 HEAD 为生成时工作树。
- 零未授权契约字节（C-07 仅统计节，UNFREEZE v1.4 记录在案）；未 push。
