# FEA-13-RESTORE-4 证据索引

- Task：`FEA-13-RESTORE-4`（merge restore + staging/commit marker + L-5 维护锁；FEA-13 片 4）
- Base：`0dc4ff85f`；依赖片 1–3（done）
- 依据：`FEA-13-scope-r1.md` §7 片 4 + 冲突模型裁决 `doc/reviews/ADJ-2026-11-09-FEA13-RESTORE-MODEL.md`
- 证据批次：`fea-13-restore-4`

## 实现口径

| 项 | 实现 |
|---|---|
| 预览 `restore.plan`（库内能力） | `plan_restore`：只读 `ATTACH` 备份 DB，对比 7 张表（books/chapters/pages/media_artifacts/artifact_revisions/regions/region_revisions）+ managed 文件；逐项 `add/noop/conflict/keep`；**零写**（测试用 DB 行/managed 字节/包 sha256 快照比较） |
| 默认 `defer` | 只应用 `add`；`conflict`/`keep` 保留 live 现值并逐项列出；不整库覆盖 |
| `UseBackup` | 指定项先 `_preserve_row` 到 `restore-undo/<backup_id>/rows/<table>/<key>.json`，成功才覆盖；缺 undo 区 → 该项 fail-closed（不覆盖） |
| `overwrite` | 保留既有整库覆盖行为（显式 mode） |
| staging + marker | `<backups>/.restore-staging-<id>/library.db`（复制 + sha256 校验）；marker `<backups>/.restore-<id>.json`：`staging` → apply → `committed`；apply 崩溃时 marker 保持 `staging`、live 库不变（已测） |
| L-5 维护锁 | `_restore_maintenance_active` 期间，除 `backup.list/create/delete` 外所有命令返回 `RESTORE_IN_PROGRESS`（conflict、retryable）；commit/失败后释放 |
| wire | `backup.restore` 增加可选 `mode`（`overwrite` 默认 / `defer` / `use_backup`）与 `entries`；非法 mode → `INVALID_REQUEST` |

## 判别证据

| AC | 结果 | 证据 |
|---|---|---|
| AC1 只读预览 | 预览前后 DB 行/managed 字节/包 sha256 全等；分类正确 | `logs/pytest-restore-suite.log`（91 passed） |
| AC2 默认 defer | defer 后 live 值不变、冲突逐项在报告 | 同上 |
| AC3 UseBackup 保全 | 覆盖前 undo JSON 保存旧值；无 undo 区 → 该项失败且不覆盖 | 同上 |
| AC4 过期/非法输入 | 非法 mode → `INVALID_REQUEST`；`RESTORE_PLAN_STALE` 已注册（过期检测在包 sha 对比处由调用方传入，本片有码字未有端到端用例 → **PARTIAL，登记**） | 同上 |
| AC5 marker/L-5 | apply 崩溃 → marker=`staging`、live 不变、锁释放；L-5 期间写命令 fail-closed、备份命令豁免 | 同上 |
| AC6 门禁 | 91 passed；`dotnet build` 0/0；`check.ps1`/pins 见卡与 Handoff | `logs/pytest-restore-suite.log`、`logs/build.log` |
| 变异判别 | ①defer 也应用冲突 → **1 failed / 3 passed**；②关闭 L-5 → **1 failed / 3 passed**；复原后 8 passed | `logs/mutation-defer-overwrites.log`、`logs/mutation-no-lock.log` |

## 命令

```powershell
python -m pytest tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_format.py tests/storage/test_nmbak_coverage.py tests/storage/test_nmbak_identity.py tests/storage/test_nmbak_merge_restore.py tests/storage/test_backup_restore.py tests/core/test_core_backup_wire.py tests/core/test_core_restore_plan.py tests/infrastructure/test_nmbak_startup_backup.py -q
dotnet build apps/desktop-avalonia/NewManga.sln -c Debug --nologo
```

## 残余 / 未覆盖

- **AC4 端到端**：`RESTORE_PLAN_STALE` 已注册但未接端到端用例（预览→换包→应用路径）。登记后续。
- **managed 文件的 apply**：本片 `apply_restore` 对 managed 项一律 deferred（需要 staging 复制语义），真正写回归后续切片；`UseBackup` 对 managed 项同样 deferred。
- **真实进程 kill 崩溃注入**：以 monkeypatch 抛错模拟 apply 崩溃（marker=`staging`、live 不变）；真实 kill 注入登记为部署态验证。
- **region 字段级自动合并**、跨机恢复、UI 冲突面板：裁决 §3 后续。
- wire 文档（V11R `backup.restore` 行）未同步 `mode/entries` 字段（按需后续）。
