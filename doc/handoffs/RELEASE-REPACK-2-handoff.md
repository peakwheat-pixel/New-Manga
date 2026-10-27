# RELEASE-REPACK-2 Handoff（第二次重打包 + 8 页全链复验 + UPGRADE 文档）

- Task: `doc/tasks/RELEASE-REPACK-2.md`（team task-41）
- Branch: `task/RELEASE-REPACK-2`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-2`
- Base: 卡面 `2980608e0`；实际基于 Lead 指定的当前 HEAD **`0f4b836a5`**
- Delivery head: 见任务卡 Canonical Evidence 的 commit 列
- 未 push；未改 Core 语义/Host 契约/旧壳；未碰真实用户数据。

## 1. 交付摘要

| AC | 结论 | 证据 |
|---|---|---|
| AC1 重打包 | **MET** | 新 base `091a201d…3bf45a` / 新 models `c5531930…5c027b`（均 399,492B；bundle 195,375,520 / 868,862,035B）；对照 RELEASE-REPACK-1 `ed499bd7…` / `9fcb9e87…`；torch-free 闭包断言（858 pure modules）、0 shadowing ICU |
| AC2 同构建全链 | **MET** | 新 models 构建 + identity 绑定：run `completed` 86.43s；translate 22/22、segment/mask_refine/inpaint/render 22/22 completed；0 `PROVIDER_NOT_CONFIGURED`；页 4–8 completed(0 region)；每步耗时见表 |
| AC3 并发 | **MET** | 同构建 wire 探针并发 `GetTaskProjection` 658 次 → 0 stuck running / 0 regionless INVALID_INPUT；源码 `repro_scheduler.py scheduler projection-fresh` PASS（0/0） |
| AC4 发布件+文档 | **MET** | base zip 102,981,645B / models zip 724,989,976B；install-verify ×2 幂等 + install-smoke（console=0、exit 0、sidecar 随包、license byte-identical、卸载幂等）；`VERSION.json.sidecar_build` 正确；**UPGRADE.md 已补**构建识别章节；packaging README §2.1 更新 |
| AC5 门禁 | **MET** | test.ps1 **177/177**；pytest 实测 **3F/2772P/9S**（基线 4F/2760P/9S，0 新增）；check.ps1 PASS；64-hex pin；本 Handoff |

## 2. 代码/脚本/文档改动

| 文件 | 改动 |
|---|---|
| `apps/desktop-avalonia/docs/UPGRADE.md` | 新增「构建识别（RELEASE-REPACK-2 起）」：`VERSION.json.sidecar_build` 字段说明、RELEASE-REPACK-2 新旧 sha、identity experimental 声明、覆盖升级说明 |
| `packaging/m2ac5/README.md` | §2.1 更新为 RELEASE-REPACK-2 新构建表 + 同构建证据；旧 §2.1 降为 §2.2 历史 |
| `verification/RELEASE-REPACK-2/tools/run_full_chain_probe.py`（新增） | AC2/AC3 真实 wire 探针：identity 绑定 StartRun、并发 GetTaskProjection 轮询、DB step_runs 统计、每步耗时 |
| `verification/RELEASE-REPACK-2/tools/README.md`（新增） | 探针/AC3 复现说明 |
| `doc/tasks/RELEASE-REPACK-2.md`、`verification/RELEASE-REPACK-2/**` | AC/证据/Resource Manifest 收口 |

未改：`src/**`、Host 契约、旧壳、任何 Python Core 语义；未覆盖旧包。

## 3. 复现

```powershell
# AC1（约 2 分钟，两个配置）
pwsh -File packaging/m2ac5/build_sidecar.ps1 -Force -SkipWeights   # base
pwsh -File packaging/m2ac5/build_sidecar.ps1 -Force                # models
# AC2/AC3（新 models bundle；真实 wire）
python verification/RELEASE-REPACK-2/tools/run_full_chain_probe.py `
  --sidecar G:\CODEX\New Manga.workspace\task-envs\RELEASE-REPACK-2\sidecar-models\core-sidecar `
  --out G:\CODEX\New Manga.workspace\task-envs\RELEASE-REPACK-2\full-chain-run.json
# AC3 源码拓扑
$env:NEWMANGA_EVIDENCE_DIR='...\RELEASE-REPACK-2\ac3-repro'
python verification/RUN-STORE-CACHE-RACE-FIX-1/tools/repro_scheduler.py scheduler projection-fresh
# AC4
pwsh -File apps/desktop-avalonia/scripts/package.ps1 -OutputRoot <out> -SidecarDir <base-bundle>
pwsh -File apps/desktop-avalonia/scripts/package.ps1 -OutputRoot <out> -SidecarDir <models-bundle> -WithModels
pwsh -File apps/desktop-avalonia/scripts/install-verify.ps1 -PackageDir <stage> -InstallDir <dir> -Out <json>
pwsh -File apps/desktop-avalonia/scripts/install-smoke.ps1  -PackageDir <stage> -InstallDir <dir2> -Out <json>
```

## 4. 关键结果速查

- 新旧 sha：base `091a201d…` / models `c5531930…`（上一版 `ed499bd7…` / `9fcb9e87…`；原始冻结 `2b36bfeb…`）。
- 8 页全链：terminal=`completed` 86.43s；render 22/22；0 `PROVIDER_NOT_CONFIGURED`；每步耗时
  detect 4.40s / ocr 5.58s / color 5.25s / term_extract 1.35s / translate 1.16s / segment 8.54s /
  mask_refine 15.99s / inpaint 29.76s / render 13.85s。
- 并发：658 次 projection-fresh 轮询，stuck=0、regionless=0。
- 包：base 102,981,645B、models 724,989,976B；console=0、license 一致、安装/卸载幂等。

## 5. 遗留 / NOT_RUN

1. **identity 是 EXPERIMENTAL 占位**（输入=输出），不是真实翻译能力；产品翻译质量需真实 provider +
   后续打包复验。UPGRADE.md 已明确声明，不得作为产品翻译宣传。
2. 旧包未动（RELEASE-REPACK-1/out、FINAL-VALIDATION out）；新包在 `task-envs/RELEASE-REPACK-2/out/`。
3. `doc/STATUS.md`/`REBASELINE_PLAN.md`/`TASK_LEDGER.md` 指针由 DSH 收口。
4. 需独立 Review（Owner 不得自审）；并发 NS-WIRE-B2 只改 C# registry，与本 Task 无文件冲突。
