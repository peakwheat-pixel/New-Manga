# RELEASE-REPACK-2 报告：第二次 sidecar 重打包与 8 页全链复验

- Task: `doc/tasks/RELEASE-REPACK-2.md`（team task-41）；Branch/Worktree: `task/RELEASE-REPACK-2` /
  `G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-2`
- Base: 卡面 `2980608e0`；按 Lead 指示基于当前仓库 HEAD **`0f4b836a5`** 开分支（含 TRANSLATE-PROVIDER-1、
  RUN-STORE-CACHE-RACE-FIX-1）。未 push；未改 Core 语义/Host 契约/旧壳；未碰真实用户数据。
- 构建机：PyInstaller 6.22.3，build venv `G:/CODEX/New Manga.task-envs/m2ac5-build`，`build_sidecar.ps1` HEAD=`0f4b836a5`。

## 0. 结论

| AC | 判定 | 要点 |
|---|---|---|
| AC1 重打包 | **MET** | base/models 均用当前 `src/` 重打，新旧 sha256 对照成立（见 §1）；torch-free 闭包断言；0 shadowing ICU；python runtime 随包 |
| AC2 同构建全链 | **MET** | 新 models 构建 + identity 绑定（`provider_bindings={ocr:manga-ocr, translate:identity-translation}`）：run **terminal=completed**、86.43s；translate **22/22**、segment/mask_refine/inpaint/**render 22/22** completed；步数 detect 8、ocr/color/term_extract 各 26、下游各 22；**0 条 PROVIDER_NOT_CONFIGURED**；页 4–8 completed(0 region)；每步耗时见 §2 |
| AC3 projection-fresh 并发 | **MET** | 同一新构建 wire 探针并发轮询 `GetTaskProjection` **658 次@100ms** → **stuck_running=0、regionless INVALID_INPUT=0**；另 `repro_scheduler.py scheduler projection-fresh`（源码拓扑）**PASS**（0/0） |
| AC4 发布件与文档 | **MET** | base zip 102,981,645B / models zip 724,989,976B；install-verify 安装×2/卸载×2 幂等、license byte-identical；install-smoke **console=0**、exit 0、sidecar 随包字节与 bundle 一致；`VERSION.json.sidecar_build` 两包正确；**`apps/desktop-avalonia/docs/UPGRADE.md` 已补安装/构建识别说明**（本次 allowed_paths 含） |
| AC5 门禁 | **MET** | `test.ps1` **177/177**（见 §5）；pytest 基线 4F/2760P/9S 无新增；`check.ps1 -TaskPath` PASS；64-hex pin；Handoff |

## 1. AC1 新旧 sha256/大小对照

| 构建 | core_service sha256 | bytes | bundle |
|---|---|---|---|
| RELEASE-REPACK-1 base（对照） | `ed499bd7859574a7a615ee1581610ff2b3ed829c870276938b762ff147d9cd7d` | 399492 | 195,366,432 |
| RELEASE-REPACK-1 models（对照） | `9fcb9e8750ff7a52bc7ab5467f261ca689114a059874f9223054022ac41331dd` | 399492 | 868,852,947 |
| **RELEASE-REPACK-2 base（新）** | **`091a201da8a044c1830e7cb8d541b012cf458c8c5b7d392624de913fa93bf45a`** | 399492 | 195,375,520 |
| **RELEASE-REPACK-2 models（新）** | **`c55319306e3022f325c1879deaa96a476dc105b206fa7135c6ae312a2a5c027b`** | 399492 | 868,862,035 |

- 相对上一版打包（RELEASE-REPACK-1）sha256 均变化；原始冻结 `2b36bfeb…` 亦不同（见 sidecar-hashes.json）。
- 构建日志含 `closure assertion: core_service carries ONNX Runtime ... (858 pure modules, torch-free)`、
  `0 shadowing ICU binaries`、`bundle_python_runtime: OK`（详见 `build-base.log` / `build-models.log`）。

## 2. AC2 同构建 8 页全链（identity 绑定）

驱动：`verification/RELEASE-REPACK-2/tools/run_full_chain_probe.py`（真实 wire 协议、真实 exe、BOOK-FIXTURE 私有副本）。
run=`run-236e8cfe1b764fdcbc1fc17854b22ebf`，**terminal=`completed`，86,430.7ms**。

| step_type | 完成数 | 状态 |
|---|---|---|
| detect | 8 | completed |
| ocr | 26 | completed |
| color | 26 | completed |
| term_extract | 26 | completed |
| translate | **22** | completed（identity-experimental） |
| segment | **22** | completed |
| mask_refine | **22** | completed |
| inpaint | **22** | completed |
| render | **22** | completed |

**0 条 `PROVIDER_NOT_CONFIGURED`**；页 4–8：仅 detect completed（0 region）→ task completed；页 1–3 全链 9 步完成。
每步墙钟耗时（从 `CurrentPageStepChanged` 事件流推导，§2 表）：

| detect | ocr | color | term_extract | translate | segment | mask_refine | inpaint | render |
|---|---|---|---|---|---|---|---|---|
| 4.40s | 5.58s | 5.25s | 1.35s | 1.16s | 8.54s | 15.99s | 29.76s | 13.85s |

说明：identity = 输入输出相同的 **EXPERIMENTAL 占位**，仅用于链路验证，不代表产品翻译质量。

## 3. AC3 projection-fresh 并发

- **同构建 wire 探针**：同一 run 期间第二线程每 100ms 调 `GetTaskProjection`，共 **658 次**；
  终态后查 run DB：`step_runs` 中 `status='running'` = **0**，`error_code='INVALID_INPUT' AND region_id IS NULL` = **0**，
  `PROVIDER_NOT_CONFIGURED` = **0**（与 AC2 同一证据 `full-chain-run.json`）。
- **源码拓扑回归**：`verification/RUN-STORE-CACHE-RACE-FIX-1/tools/repro_scheduler.py scheduler projection-fresh`
  → `RESULT {"verdict":"PASS","stuck_running":0,"regionless_invalid_input":0,...}`（`ac3-repro.log`、`ac3/*.json`）。

## 4. AC4 发布件与文档

| 包 | zip 大小/sha256 | 安装 | 卸载 | sidecar 随包 | console | 许可证 |
|---|---|---|---|---|---|---|
| base | 102,981,645B / `f42af3da…f79c893` | ×2 幂等 | ×2 幂等 | 1955 files / 195,375,520B | **0** | byte-identical |
| models | 724,989,976B / `ffb23b25…668aa29` | ×2 幂等 | ×2 幂等 | 1965 files / 868,862,035B + models | **0** | byte-identical |

- `VERSION.json.sidecar_build` 实测：base `091a201d…3bf45a` / models `c5531930…5c027b`，repo_head=`0f4b836a5`，
  variant/models_bundled 正确（`packages/VERSION-*.json`）。
- **UPGRADE.md 已更新**：新增「构建识别」章节（sidecar_build 字段说明 + RELEASE-REPACK-2 新旧 sha、
  identity experimental 声明、覆盖升级说明）。`packaging/m2ac5/README.md` §2.1 同步新表。
- install-smoke：`window_handle_found=true`、`exit_code=0`、`residual_processes=0`、`install_dir_after=false`。

## 5. AC5 门禁

| 门 | 结果 |
|---|---|
| `scripts/test.ps1` | **177/177 passed, 0 skipped** |
| pytest | **实测 3F/2772P/9S**（基线 4F/2760P/9S；失败集合为已知 flaky 子集、0 新增；通过数随 main 新增测试上升） |
| `check.ps1 -TaskPath` | PASS |

## 6. 遗留 / NOT_RUN

1. identity 为 **EXPERIMENTAL 占位**，不是真实翻译能力；产品翻译需后续真实 provider。
2. AC2 探针为本 Task `verification/RELEASE-REPACK-2/tools/` 入库脚本（与上次不同，本次 allowed_paths 可放）；未改 `tests/**`。
3. 旧包（`task-envs/RELEASE-REPACK-1/out/`、FINAL-VALIDATION out/）保留未动；新包在 `task-envs/RELEASE-REPACK-2/out/`。
4. `doc/STATUS.md`/`REBASELINE_PLAN.md`/`TASK_LEDGER.md` 指针由 DSH 收口（本 Task 未改）。
5. 需独立 Review（Owner 不得自审）。
