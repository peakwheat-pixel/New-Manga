---
id: FEA-13-SRC-6
title: SC-B01 ④ 源引用/授权元数据入包（包内加密段；Host staging 交接面）
kind: implementation
governance_version: 3
status: done
approval: **ZCode 独立裁决 2026-11-09（`doc/reviews/ADJ-2026-11-09-ZCODE-ARCH-ADJUDICATION.md`）**：单列立项（「必须包含」项，非不做）；**不阻塞 FEA-15 正式验收**（验收登记为已知 limitation）；排在 `FEA-11-HOST-AUTH-3` 之后（同域 SourceAccessRegistry/Host 授权）
suggested_owner: zcode（Host/C# 主责域）
owner: dsh
reviewer: null
depends_on:
  - FEA-13-COV-2
  - FEA-11-HOST-AUTH-3
base_commit: 1a8bb1235
branch: null
worktree: null
integration_commit: ef0618e57
delivery_head: ef0618e57
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-13-SRC-6
allowed_paths:
  - doc/tasks/FEA-13-SRC-6.md
  - doc/reviews/FEA-13-SRC-6-*.md
  - doc/handoffs/FEA-13-SRC-6-*.md
  - verification/FEA-13-SRC-6/**
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRestore.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - src/infrastructure/sqlite/nmbak.py
  - tests/storage/test_nmbak_source_access.py
  - tests/storage/test_nmbak_backup.py
  - tests/storage/test_nmbak_coverage.py
  - tests/core/test_core_backup_wire.py
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceAccessRestoreTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs
out_of_scope:
  - **实现范围以本卡冻结为准**（scope 冻结 2026-11-10，DSH）
  - 不实现跨机恢复（DPAPI CurrentUser：同机恢复有效，跨机须重授权；跨机负例只做 typed 拒绝断言）
  - **不改 C-06/C-09/C-17 契约字节与 18 pins**（C-09 SC-B01 已含「源引用与授权元数据…包内加密」，无需 UNFREEZE；如需扩条款另走 errata）
  - 不改 `SourceSecurity`/`DpapiSecretProtector` 的既有加解密语义、不改 registry.dat 内部格式版本
  - 不实现数据根迁移（`FEA-13-MIGRATE-6` 单列 blocked）
---

# FEA-13-SRC-6：SC-B01 ④ 源引用/授权元数据入包（占位）

## 裁决依据（ZCode 2026-11-09）

- C-09 SC-B01 的「必须包含」项，SC-B07 强制增量 ④ 已预留；明确不做需走契约 errata（成本高于实现）。
- 产品价值：AD-003 引用模型下，若 SourceAccessRegistry 不随包恢复，重装/恢复后用户须对全部源重新授权，备份恢复承诺落空。
- 时序：排在 `FEA-11-HOST-AUTH-3`（UNFREEZE）之后——两者同域（SourceAccessRegistry/Host 授权），先落恢复语义再叠备份打包。
- **同机恢复有效；跨机恢复须重授权**（DPAPI CurrentUser 绑定，不得写成通用跨机恢复）。

## 预估范围（待 scope review 冻结）

| 项 | 预估 |
|---|---|
| Host staging 交接面 | `SourceAccessRegistry` 导出 → 交给 Core 打包加密段 |
| Core 侧 | `nmbak` 包内新增加密段（`extras/source-access/…`）+ manifest 记录 |
| 恢复反向 | 解包 → Host 导入（冲突/过期处置） |
| 契约 | 若需 C-06/C-09 载体 → 另走 UNFREEZE/errata（不得直接改冻结字节） |
| 证据 | L2 正/负 fixture + 加密段不可读断言 + 恢复后授权可用 |

## Acceptance Criteria

- 待 scope review 冻结（当前仅占位；不得实施）。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-S6-001 | AC1–AC6 | `verification/FEA-13-SRC-6/logs/dotnet-host-tests.log` | `-` | `e62ea0bfb8ad1bfa562ed898ea44ece29574e421a22f59e0ce3727262f9edc36` | CANONICAL |
| EV-S6-002 | AC1–AC6 | `verification/FEA-13-SRC-6/logs/dotnet-NewManga.App.Tests.log` | `-` | `2fb8c34f6c11309b17888157a3b5e7b0ef51193f556849586a98b3def2f7ddbe` | CANONICAL |
| EV-S6-003 | AC1–AC6 | `verification/FEA-13-SRC-6/logs/dotnet-NewManga.Appearance.Tests.log` | `-` | `9ee274ab128abe8dbfa75b8dd80b9ad81c876ebb28ead546a98b500d955bde9b` | CANONICAL |
| EV-S6-004 | AC1–AC6 | `verification/FEA-13-SRC-6/logs/dotnet-NewManga.ApplicationCore.Tests.log` | `-` | `874026c3ac6adb545c80a81e48d1401e9ebe63caa1cdd947a486e874f385728d` | CANONICAL |
| EV-S6-005 | AC1–AC6 | `verification/FEA-13-SRC-6/logs/dotnet-NewManga.CoreClient.Tests.log` | `-` | `6e33b05eaf5ecc1d2278496af46aa1f654d65c2ae28519fc87eb97ee9637c0ba` | CANONICAL |
| EV-S6-006 | AC1–AC6 | `verification/FEA-13-SRC-6/logs/dotnet-NewManga.DesignSystem.Tests.log` | `-` | `a096304fe4374f36e1fd9d5644451fce40aeb510b675cd971497f14399f7a747` | CANONICAL |
| EV-S6-007 | AC1–AC6 | `verification/FEA-13-SRC-6/logs/dotnet-NewManga.Host.Tests.log` | `-` | `e4490082a341ddec826ca7d62f12a480c48c3cc382144f426e9bc82729bf4a5f` | CANONICAL |
| EV-S6-008 | AC1–AC6 | `verification/FEA-13-SRC-6/logs/dotnet-NewManga.Presentation.Avalonia.Tests.log` | `-` | `b60d0c593df30053433babcb917ea0715d3644a92a6347f71aeab7a807c40ae4` | CANONICAL |
| EV-S6-009 | AC1–AC6 | `verification/FEA-13-SRC-6/logs/dotnet-NewManga.ThemeEngine.Tests.log` | `-` | `a92899e3b748f10fbbc9502ad56110c48334d9f9434591b52a54dcb271bcfb60` | CANONICAL |
| EV-S6-010 | AC1–AC6 | `verification/FEA-13-SRC-6/logs/dotnet-restore-tests.log` | `-` | `d984c1c693177dd061a5801309d8cc17d5a5fbedbd61de959a768bb9b19f7c75` | CANONICAL |
| EV-S6-011 | AC1–AC6 | `verification/FEA-13-SRC-6/logs/gates-check.log` | `-` | `6e08222a4e826b2bcd09d3f873c1faedf306a367734020d392c6e21111c9b94d` | CANONICAL |
| EV-S6-012 | AC1–AC6 | `verification/FEA-13-SRC-6/logs/gates-pins.log` | `-` | `5a2c122ac64b243ea6d137fb9560905479955a4d6f7a35ef9d02975ebdd79881` | CANONICAL |
| EV-S6-013 | AC1–AC6 | `verification/FEA-13-SRC-6/logs/pytest-full.log` | `-` | `ee5a3b6e793fec6fa04a4d22c7d8a526bb07cd0660a1e08fc12c12545c22c28d` | CANONICAL |
| EV-S6-014 | AC1–AC6 | `verification/FEA-13-SRC-6/logs/pytest-nmbak-suite.log` | `-` | `f3c9ebe5c9f066a6ad8f82d82ed6d3aa69743a2927caf593c9315bb854b7cac7` | CANONICAL |
| EV-S6-015 | AC1–AC6 | `verification/FEA-13-SRC-6/logs/pytest-src6.log` | `-` | `004d2999857bf5a4e8169c2dfc9b869cd31092e44c7e4eae8731b4666b9e976f` | CANONICAL |
| EV-S6-016 | AC1–AC6 | `verification/FEA-13-SRC-6/mutations/MA-live-conflict-overwritten.log` | `-` | `9194b599649bad5be510cbe50c6a7011646dc7f5c3af323b0cd350ad5cddeb5d` | CANONICAL |
| EV-S6-017 | AC1–AC6 | `verification/FEA-13-SRC-6/mutations/MB-foreign-dpapi-masked.log` | `-` | `75975bd8e6c38ff054bab95743773828eef95bcf209d2a4f64c85ea50ff13dc7` | CANONICAL |
| EV-S6-018 | AC1–AC6 | `verification/FEA-13-SRC-6/mutations/MC-plaintext-segment.log` | `-` | `d8986603842332f9807446d45675180d848c3811d8bdda4f258b9e284d82d261` | CANONICAL |
| EV-S6-019 | AC1–AC6 | `verification/FEA-13-SRC-6/README.md` | `-` | `0fad4331428db62092fd22df0953ad33ffedfe31a88a614281bb152f1dae3a55` | CANONICAL |

## Scope 冻结（2026-11-10，DSH；依据 `doc/reviews/FEA-13-SRC-6-scope-r1.md` READY-TO-FREEZE）

**契约依据**：C-09 `SC-B01`/`SC-B01a`/`SC-B07 ④` 已要求「源引用与授权元数据…备份包内加密」→ **无需 UNFREEZE**；C-06/C-17 零字节、零新命令、零新错误码、零 DDL。

**交接面（四段，字节语义固定）**：

| 方向 | 产物 | 写入方 | 读取方 | 字节语义 |
|---|---|---|---|---|
| 导出 | `<DataRoot>/host/source-access/registry.v1.dat`（`NMSAR1` + DPAPI 密文） | Host `Save`（既有） | Core `nmbak`（**只读，不解密/不解析**） | 原字节 |
| 包内段 | `extras/source-access/registry.v1.dat` + manifest `extras` 项（sha256/size） | Core `nmbak` | restore/Host | 与源逐字节相同 |
| 恢复 handoff | `<backup_root>/restore-handoff/<backup_id>/source-access/registry.v1.dat` + `handoff.json` | Core `nmbak.restore`（DB/managed 成功后） | Host `SourceAccessRestore` | 原字节 + 摘要 |
| 导入 live | `<DataRoot>/host/source-access/registry.v1.dat` | Host `ImportRestoredSnapshot`（原子 Save） | Host | 合并后快照 |

**关键边界**：registry 不存在 = 合法空（不伪装 empty）；存在但读失败 = `BACKUP_CREATE_FAILED`；损坏但仍可读 = 入包（由 Host 导入时 typed 拒绝）；并发按 C-15 `:309` 原子替换；Host 导入只**新增缺失 registry_id**，不覆盖/不复活 live 条目；失败时 live **零写**；跨机/他用户 DPAPI = typed `SOURCE_ACCESS_DENIED` + `NOT_RUN` 真实跨机。

## Acceptance Criteria（6 条，依 scope r1 §3）

- [x] **AC1 入包段与加密不可读**：manifest extras 恰一项 `source-access/registry.v1.dat`（sha256/size 一致）；包内成员与源逐字节相同且以 `NMSAR1\0` 开头；字节中无明文 registry_id/locator/绝对路径；Core 代码库 `grep CryptProtectData\|CryptUnprotectData src/` = 0；创建前后源文件字节 + mtime 不变。 <<MET>>
- [x] **AC2 缺失/不可读/空边界**：(a) 读失败→`BACKUP_CREATE_FAILED` 无包、源不变；(b) 缺失→create 成功、无段、restore 后 live 不变（`not_present`）；(c) 空 entries（文件存在）→ 有成员、导入 `unchanged` 零写。 <<MET>>
- [x] **AC3 恢复后授权可用**：第二 DataRoot overwrite restore + handoff → Host 导入后 `List()` 含条目、`Authorize` 成功；重复导入 `Imported=0`+live 零写；空 live 首次导入恰好一次；导入拒绝不反向失败数据恢复。 <<MET>>
- [x] **AC4 revoked/代次/冲突**：live 新代次/revoked 不被包内旧代次覆盖；包内 revoked 导入为 revoked；`Reset(true)` + receipt 后启动 `TryImportPending` 不复活；read-only 模式零写。 <<MET>>
- [x] **AC5 跨机/版本/identity 负例**：DPAPI 不可解 → `rejected`/`SOURCE_ACCESS_DENIED`/`dpapi_unprotectable`；版本 `NMSAR2` → `registry_version_unsupported`（已测）；截断 → Host 边界 `handoff_corrupt`（registry 级 `registry_corrupt` 未单测）；identity 变更 → `SOURCE_REGISTRY_UNAVAILABLE`（未单测）；均 live 零写；真实跨机 `NOT_RUN`。 <<MET>>
- [x] **AC6 门禁/证据/变异**：定向 pytest/.NET 0 failed；`check.ps1`（默认 + `-TaskPath`）PASS；`verify_pins` 18/18；diff ⊆ 14 paths；证据含 README/日志/字节探针/正负例/≥3 变异日志（含 `EXIT=` 与复原绿）；0 契约/0 pin/0 DDL/0 新 wire/0 新码。 <<MET>>

## 证据计划（L2，依 scope r1 §4）

fixtures：`F-POS-DPAPI`（真实 DPAPI）、`F-POS-FAKE`（Passthrough/fake 密文）、`F-ABSENT`、`F-EMPTY`、`F-FOREIGN-DPAPI`（必败 protector）、`F-NMSAR2`、`F-CORRUPT`、`F-TAMPER`。证据：`verification/FEA-13-SRC-6/`（README AC 映射、pytest/dotnet/门禁日志、加密段字节探针、handoff/导入正负例、≥3 变异日志）。跨机 = `NOT_RUN` + 原因。

## 风险与回退

| 风险 | 处置 |
|---|---|
| DPAPI 跨机/他用户 | 只声明同机同用户；typed 拒绝 + `NOT_RUN` 真实跨机；FEA-15 登记 limitation |
| 旧二进制读新包 | 未知 extras 类别 → `BACKUP_FORMAT_UNSUPPORTED`（COV-2 既有前向兼容），发布说明写明 |
| registry 版本演进 | Core 只复制字节；Host 导入校验 `NMSAR1`/JSON `format_version` |
| merge restore | 本卡不创建 handoff（§5.4），不表现为静默成功 |
| 回退 | `git revert` 实现提交；无 schema/契约字节变更 |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（proposed 占位） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无 |
| build | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无构建 |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问真实数据 |

## Closeout Record

- 结论：**完成**（2 轮独立 Review：r1→r3；Core extras+handoff + Host 导入 + 变异 + 全量门禁）。
- 残余 limitation：真实跨机 DPAPI 恢复 = NOT_RUN（simulated 负例覆盖）；merge restore 不产生 handoff（C# 未暴露）；MA 变异不可判别（如实登记）。
- 未开始（proposed）。
