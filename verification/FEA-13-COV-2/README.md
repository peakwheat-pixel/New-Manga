# FEA-13-COV-2 证据索引

- Task：`FEA-13-COV-2`（覆盖清单二期；FEA-13 片 2）
- Base：`892cb99df`；依赖 `FEA-13-BK2-1`（done）
- 依据：`ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT`（D2/D3）+ `FEA-13-scope-r1.md` §7 片 2
- 证据批次：`fea-13-cov-2`

## 实现口径

| 类别 | 入包规则 | 包内位置 |
|---|---|---|
| `settings` | `<data_root>/settings/` 三个 JSON（provider/network/binding，存在才入） | `extras/settings/<name>` |
| `drafts` | `<data_root>/drafts/**`（目录存在则入） | `extras/drafts/<rel>` |
| `plugins` | `<data_root>/plugins/**`（目录存在则入） | `extras/plugins/<rel>` |
| `trash-manifest` | `<managed_root>/trash-manifest.json`（存在才入） | `extras/trash-manifest/trash-manifest.json` |
| 排除项 | `catalog`（可从 library.db 重建）、`derived`（可重建缓存）、`external_source_files`（data root 之外）、`os_credential_vault`（OS 托管） | 不入包，manifest `excluded_categories` 逐项带 reason |

- manifest 新增：`included_categories` / `skipped_categories` / `excluded_categories` / `extras`（每项 `category/relative_path/sha256/size_bytes`）/ `extras_total_bytes`。
- `verified=true` 依赖 read-back 全量校验（含 extras 成员的 sha256+size）；某类别根存在但收集失败 → `BACKUP_CREATE_FAILED` 且不产出包。
- restore：**不写回** extras（延迟到片 4 的合并语义），report 增加 `deferred_categories`；`_verify_package` 校验 extras（同长篡改也能被 sha256 抓住）。

## 判别证据

| AC | 结果 | 证据 |
|---|---|---|
| AC1 类别入包 | 4 类全部入包，`extras` 每项 sha256+size 与包内字节一致；`included_categories` 排序正确 | `logs/pytest-backup-suite.log`（70 passed） |
| AC2 排除项 | `catalog`/`derived` 不在包内；`excluded_categories` 四项均有 reason | 同上 |
| AC3 verified 语义 | 收集抛错 → `BACKUP_CREATE_FAILED` 且包目录无新增 | 同上（monkeypatch 用例） |
| AC4 restore 延迟写回 | restore 后 settings/drafts/plugins/trash-manifest 字节不变；`deferred_categories` = 4 类 | 同上 |
| AC5 变异判别 | ①禁用 extras sha 校验（同长篡改）→ **1 failed / 3 passed**；②`deferred_categories` 清空 → **1 failed / 3 passed**；复原后 **4 passed** | `logs/mutation-extras-sha.log`、`logs/mutation-deferred.log` |
| AC6 门禁 | `check.ps1` 默认 + `-TaskPath` PASS；pins 18/18 | 卡/Handoff |

## 命令

```powershell
python -m pytest tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_format.py tests/storage/test_nmbak_coverage.py tests/storage/test_backup_restore.py tests/core/test_core_backup_wire.py tests/infrastructure/test_nmbak_startup_backup.py -q
```

## 说明

- 包体可能因 drafts/plugins 变大：manifest 记录 `extras_total_bytes`，大小/保留策略归片 5。
- `data_root` 默认由 `backup_root.parent` 推断（`<data_root>/backups`）；`core_assembly` 已显式传 `data_root`。
- 旧包（无 extras 字段）→ 按空处理（v1/v2 均兼容）。
- 未跑 `tests/storage` 全量（环境 >10 分钟），备份面 6 文件 70 passed 覆盖改动面。
