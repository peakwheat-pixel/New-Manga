# RELEASE-REPACK-1 Handoff（sidecar 重打包与同构建复验）

- Task: `doc/tasks/RELEASE-REPACK-1.md`（team task-36）
- Branch: `task/RELEASE-REPACK-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-1`
- Base: 卡面 `97de0fa99`；实际基于 Lead 指定的当前 HEAD **`ae7fe3334`**
- Delivery head: `dd3e7d68e`（实现+证据提交；任务卡 Canonical Evidence 的 pin 均指向它）
- 未 push；未改 Core 语义/Host 契约/旧壳；未碰真实用户数据。

## 1. 交付摘要

| AC | 结论 | 证据 |
|---|---|---|
| AC1 重打包 | **MET** | 旧 `2b36bfeb…4ec519b`（399,492B）→ 新 base `ed499bd7…d9cd7d` / 新 models `9fcb9e87…c41331dd`（均 399,492B，bundle 195,366,432 / 868,852,947B）；闭包 torch-free、0 shadowing ICU、python runtime 随包 |
| AC2 同构建复验 | **MET** | 新 models 构建 Host 命令面 8 页：ocr 3/3 completed、color 3/3 completed、term_extract 3/3 completed、页 4–8 completed(0 region)；translate 3/3 `PROVIDER_NOT_CONFIGURED`（如实）；run `completed_with_failures` 5.58s |
| AC3 发布件 | **MET** | base 98.2MB / models 691.4MB zip；install-verify ×2 幂等 + install-smoke（console=0、exit 0、sidecar 随包、license byte-identical、卸载幂等）两包全绿 |
| AC4 元数据 | **MET（README 受限）** | `VERSION.json.sidecar_build`（sha/bytes/built-at/HEAD/variant/models）+ `packaging/m2ac5/README.md` §2.1；闭包依赖不变 → NOTICE/THIRD_PARTY 无需改；`docs/UPGRADE.md` 因 allowed_paths 未含而保留原样（见 §4） |
| AC5 门禁 | **MET** | test.ps1 **177/177**；pytest **3F/2753P/9S**；check.ps1 PASS；64-hex pin；本 Handoff |

## 2. 代码/脚本改动

| 文件 | 改动 |
|---|---|
| `apps/desktop-avalonia/scripts/package.ps1` | 新增 §2b：打包时记录 `core_service.exe` sha256/bytes/built-at/repo HEAD/variant/models 到 `VERSION.json.sidecar_build`（防止旧构建冒充） |
| `packaging/m2ac5/README.md` | 新增 §2.1 Current frozen build：新旧 sha256、bundle 字节、torch-free 断言、VERSION.json 字段说明 |
| `doc/tasks/RELEASE-REPACK-1.md` | AC/证据/Resource Manifest 收口 |
| `verification/RELEASE-REPACK-1/**` | 全部证据 |

未改：`src/**`、Host 契约、旧壳、任何 Python Core 语义、`apps/desktop-avalonia/docs/**`（越界保护）。

## 3. 复现

```powershell
# AC1（约 92s，两配置）
python  # 无：直接
pwsh -File packaging/m2ac5/build_sidecar.ps1 -Force -SkipWeights   # base
pwsh -File packaging/m2ac5/build_sidecar.ps1 -Force                # models（默认权重）
# AC3
pwsh -File apps/desktop-avalonia/scripts/package.ps1 -OutputRoot <out> -SidecarDir <base-bundle>
pwsh -File apps/desktop-avalonia/scripts/package.ps1 -OutputRoot <out> -SidecarDir <models-bundle> -WithModels
pwsh -File apps/desktop-avalonia/scripts/install-verify.ps1 -PackageDir <stage> -InstallDir <dir> -Out <json>
pwsh -File apps/desktop-avalonia/scripts/install-smoke.ps1  -PackageDir <stage> -InstallDir <dir2> -Out <json>
# AC2：见 §4 临时 harness 说明
```

## 4. AC2 临时 harness（未入库）

`tests/NewManga.Host.Tests/ReleaseRepackRunSmoke.cs` 为一次性证据 harness（未被 commit，allowed_paths 不含 `tests/**`）：
- 环境：`NEWMANGA_CORECLIENT_SIDECAR_DIR=<新 models bundle>`、`NEWMANGA_RUN_SMOKE_ROOT=<BOOK-FIXTURE 私有副本>`、
  `NEWMANGA_RUN_SMOKE_OUT=<json>`、`NEWMANGA_EVIDENCE_DIR=<dir>`；
- 流程：`HostRuntime.StartAsync` → dispatcher 命令 `library_list_books`/`list_chapters`/`list_chapter_pages`/
  `library_start_run`/`library_get_run_snapshot`/`library_get_task_projection`/`list_regions`；
- 断言数据（run/region_counts/steps）已冻结在 `verification/RELEASE-REPACK-1/run-smoke.json`；
- 如要 CI 化：需 DSH 授权把 harness 放入 `apps/desktop-avalonia/tests/**` 或新增 `scripts/**` 工程。

## 5. 遗留 / NOT_RUN

1. **translate 缺口**：新构建上 3/3 `PROVIDER_NOT_CONFIGURED`，需 TRANSLATE-PROVIDER-1 合入后重新打包复验
   （Run→Export 闭环的前置仍未完成）。
2. `docs/UPGRADE.md`/`MANUAL_VERIFY.md` 未改（allowed_paths 不含 `apps/desktop-avalonia/docs/**`）；安装/升级说明
   的版本化补充建议下个打包 Task 或 DSH 授权后补。
3. 旧包（`task-envs/FINAL-VALIDATION-1/out/`）保留未动；新包在 `task-envs/RELEASE-REPACK-1/out/`（base/models zip +
   解压目录），未覆盖任何既有引用。
4. `doc/STATUS.md`/`REBASELINE_PLAN.md`/`TASK_LEDGER.md` 指针由 DSH 收口（本 Task 未改）。
5. 需独立 Review（Owner 不得自审）；并发 TRANSLATE-PROVIDER-1 只改 `src/providers`，与本 Task 无文件冲突。
