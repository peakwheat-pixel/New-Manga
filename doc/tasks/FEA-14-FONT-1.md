---
id: FEA-14-FONT-1
title: FEA-14 切片 FONT-1：Core 字体库（安装/列举/预览/删除 + 内置字体）
kind: implementation
governance_version: 3
status: in_review
approval: **DSH 2026-11-10 冻结**（`ADJ-2026-11-10-FEA14-S5-SCOPE` §2.1/§2.2；PREQ-1 wire 预冻结 FONT P1–P4；侦察 `recon.md` §2.3）
suggested_owner: dsh
owner: dsh
reviewer: null
depends_on:
  - FEA-14-S5-PREQ-1
base_commit: bd6aa5246
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-14-FONT-1
allowed_paths:
  - doc/tasks/FEA-14-FONT-1.md
  - doc/reviews/FEA-14-FONT-1-*.md
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

- [x] **AC1 字体安装**：合法字体文件 → 复制到受管 `fonts/`、行记录（family/weight/style/sha256）；重复安装同 sha256 幂等；越界/非字体文件拒绝（typed）。 <<MET>>
- [x] **AC2 删除**：删除行 + 受管文件；不存在 → typed 错误；不触碰用户源文件。 <<MET>>
- [x] **AC3 列举/目录**：列举返回已安装字体（含内置条目，缺省空）；目录查询按 family/weight 过滤；数据与磁盘一致。 <<MET>>
- [x] **AC4 迁移无损**：schema v11 additive；既有用户数据行不受影响。 <<MET>>
- [x] **AC5 契约/门禁**：P1–P4 按 PREQ §8 形状；`generate_api_inventory.py --check` EXIT 0；`verify_pins` 18/18（C-07 pin 更新记录）。 <<MET>>
- [x] **AC6 证据**：定向 pytest/App.Tests 通过；`verification/FEA-14-FONT-1/` 日志含 EXIT；NOT_RUN（真实字体渲染/随包字体）如实登记。 <<MET>>

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
| user-data | `%APPDATA%\com.newmanga.desktop` | NOT_APPLICABLE | — | — | 只读；测试用隔离根 |
| build | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 复用现有环境 |
| worktree | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 主树实现 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-FN-001 | FONT-1 | `verification/FEA-14-FONT-1/logs/dotnet-app-tests.log` | `-` | `fd837f5fe5af02719c261db4f2e5043619eb95e3da21917c727cec1571b5696a` | CANONICAL |
| EV-FN-002 | FONT-1 | `verification/FEA-14-FONT-1/logs/pins-api.log` | `-` | `9d798a9b0a0637abe5ddc41b74f2915997cb933ef4be16fa9da064531336b5e6` | CANONICAL |
| EV-FN-003 | FONT-1 | `verification/FEA-14-FONT-1/logs/pytest-font.log` | `-` | `2fdfb7359e36fea2284dc29ddaae41977171a306627afb9e265538bf8fcfcb55` | CANONICAL |
| EV-FN-004 | FONT-1 | `verification/FEA-14-FONT-1/README.md` | `-` | `ad3fb403d6401dc35c1542fdd06713d43542366bef919196496da5f7eb5d6b20` | CANONICAL |

## Closeout Record

- 未开始（2026-11-10 scope 冻结，`ready`）。
