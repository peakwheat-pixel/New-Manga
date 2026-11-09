# FEA-13-COV-2 证据索引

- Task：`FEA-13-COV-2`（覆盖清单二期；FEA-13 片 2）
- Base：`892cb99df`；依赖 `FEA-13-BK2-1`（done）
- 依据：`ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT`（D2/D3）+ `FEA-13-scope-r1.md` §7 片 2 + `FEA-13-COV-2-sc01-decision.md`（SC-B01 ④ 单列）
- 证据批次：`fea-13-cov-2-r2`

## 实现口径

| 类别 | 入包规则 | 包内位置 |
|---|---|---|
| `settings` | `<data_root>/settings/` 三个 JSON（存在才入） | `extras/settings/<name>` |
| `drafts` | `<data_root>/drafts/**`，**排除 `.lock/` 与 `*.tmp`**；空目录合法（0 文件） | `extras/drafts/<rel>` |
| `plugins` | `<data_root>/plugins/**`；空目录合法 | `extras/plugins/<rel>` |
| `trash-manifest` | `<managed_root>/trash-manifest.json`（存在才入） | `extras/trash-manifest/trash-manifest.json` |
| 排除项 | `catalog`（可从 library.db 重建）、`derived`（可重建缓存）、`external_source_files`（data root 之外）、`os_credential_vault`（OS 托管） | 不入包，manifest `excluded_categories` 逐项带 reason |

- manifest：`included_categories`（存在的类别根，**含空根**）/ `empty_categories`（存在但 0 文件）/ `skipped_categories`（成功包恒 `[]`）/ `excluded_categories` / `extras`（每项 `category/relative_path/sha256/size_bytes`）/ `extras_total_bytes`。
- **空目录语义（R-001 修复）**：干净关机的 `<data_root>/drafts/` 为空是正常状态；空类别根计入 `included_categories` 且不产出成员，**绝不**导致 `BACKUP_CREATE_FAILED`。仅「收集/读取过程发生错误」才失败。
- `verified=true`：read-back 校验通过 + extras 成员 sha256/size + **类别声明交叉校验**（`included_categories == extras ∪ empty_categories`，`skipped_categories` 为空）。
- 未知 extras 类别（更新版本的包）→ `BACKUP_FORMAT_UNSUPPORTED`（前向兼容，不伪装 corrupt）。
- restore：**不写回** extras（延迟到片 4），report 含 `deferred_categories`。
- 安全边界：extras 收集跳过 `is_symlink()`（不把 data root 外内容读入包）；额外 ACL/符号链接回归登记 UNKNOWN。

## 判别证据

| AC | 结果 | 证据 |
|---|---|---|
| AC1 类别入包（含空目录） | 4 类全部入包；空 `drafts`/`plugins` 仍计入 `included_categories`（`empty_categories`）且不失败；每项 sha256+size 与包内字节一致 | `logs/pytest-backup-suite.log`（74 passed） |
| AC2 排除项 | `catalog`/`derived` 不在包内；`excluded_categories` 四项均有 reason | 同上 |
| AC3 verified 语义 | 收集/读取错误 → `BACKUP_CREATE_FAILED` 且无包产出；空目录不失败；类别声明不一致 → `BACKUP_CORRUPT` | 同上（新增 4 例） |
| AC4 restore 延迟写回 | restore 后 settings/drafts/plugins/trash-manifest 字节不变；`deferred_categories` = 4 类 | 同上 |
| AC5 变异判别 | ①禁用 extras sha 校验（同长篡改）→ **1 failed / 3 passed**；②**restore 写回 extras（真实变异）→ 1 failed / 7 passed**；复原后 8 passed | `logs/mutation-extras-sha.log`、`logs/mutation-writeback.log` |
| AC6 门禁 | `check.ps1` 默认 + `-TaskPath` PASS；pins 18/18 | 卡/Handoff |

## 命令

```powershell
python -m pytest tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_format.py tests/storage/test_nmbak_coverage.py tests/storage/test_backup_restore.py tests/core/test_core_backup_wire.py tests/infrastructure/test_nmbak_startup_backup.py -q
```

## 残余 / 未覆盖

- **SC-B01 ④「源引用/授权元数据入包」**：写域在 Host 侧，不在本片；按 `doc/reviews/FEA-13-COV-2-sc01-decision.md` 单列 `FEA-13-SRC-6`（proposed）。
- **真实 Windows ACL 不可读目录 / 真实符号链接**：CI 无法稳定构造，`UNKNOWN`；代码已跳过 symlink。
- **性能/IO**：`_verify_package` 逐成员 `archive.read` 且 create read-back 再跑一次；restore `extractall` 解出永不写回的 extras（双倍 temp IO）→ 登记，优化归片 5。
- `tests/storage` 全量未跑（环境 >10 分钟），备份面 6 文件 74 passed 覆盖改动面。
