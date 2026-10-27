# RELEASE-REPACK-1 报告：sidecar 重打包与同构建复验

- Task: `doc/tasks/RELEASE-REPACK-1.md`（team task-36）；Branch/Worktree: `task/RELEASE-REPACK-1` /
  `G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-1`
- Base: 卡面 `97de0fa99`；按 Lead 指示基于当前仓库 HEAD **`ae7fe3334`** 开分支（含 CORE-PIPELINE-FIX-1、
  RUN-BINDING-FIX-1、GRANT-ISSUER-1）。未 push；未改 Core 语义/Host 契约/旧壳；未碰真实用户数据。
- 构建机：PyInstaller 6.22.3，build venv `G:/CODEX/New Manga.task-envs/m2ac5-build`，`build_sidecar.ps1` HEAD=`ae7fe3334`。

## 0. 结论

| AC | 判定 | 要点 |
|---|---|---|
| AC1 重打包 | **MET** | base/models 两配置均用 **当前 src/** 重打，新旧 sha256 对照成立（见 §1）；闭包断言 torch-free（857 pure modules + onnxruntime DirectML，无 torch）；0 shadowing ICU；python runtime 随包。**未复用旧 exe** |
| AC2 同构建复验 | **MET** | 新 models 构建 + Host 命令面 + BOOK-FIXTURE 8 页：**ocr 3/3 completed、color 3/3 completed、term_extract 3/3 completed**（0 条 `PROVIDER_NOT_CONFIGURED`）；**页 4–8 completed(0 region)**（region_counts 0）；translate 3/3 仍 `PROVIDER_NOT_CONFIGURED`（如实记录，TRANSLATE-PROVIDER-1 不在本 Task 范围）；run 终态 `completed_with_failures`，5.58s |
| AC3 发布件 | **MET** | base zip 98.2MB / models zip 691.4MB 重打；install-verify（安装×2 幂等、卸载×2 幂等、license byte-identical、residue 0）+ install-smoke（真启动窗口、**console_window_count=0**、exit 0、sidecar 随包：base 195,366,432B / models 868,852,947B、models_bundled 正确）两包全绿 |
| AC4 元数据 | **MET（README 范围受限，见 §4）** | 新增 `VERSION.json.sidecar_build`（core_service sha256/bytes/built-at/repo HEAD/variant/models_bundled，`package.ps1` 自动生成，两包实测值正确）；`packaging/m2ac5/README.md` 增补「Current frozen build」章节（新旧 sha、bundle 字节、torch-free 断言）；闭包依赖集合未变（CORE-PIPELINE-FIX-1 仅 Python 模块增删），NOTICE/THIRD_PARTY_LICENSES 无需变更（license 哈希与仓库根 byte-identical 已由 package/install-verify 断言） |
| AC5 门禁 | **MET** | `test.ps1` **177/177 passed**；pytest **3F/2753P/9S**（基线一致，0 新增）；`check.ps1 -TaskPath` PASS；64-hex pin；Handoff |

## 1. AC1 新旧 sha256/大小对照

| 构建 | core_service sha256 | bytes | 说明 |
|---|---|---|---|
| **旧（冻结）** | `2b36bfebcf09ea118537a0bc77a6c7c9a47c8845d7a853bc60d56ed004ec519b` | 399492 | FINAL-VALIDATION 包旧构建（CORE-PIPELINE-FIX-1 之前） |
| **新 base**（`-SkipWeights`） | `ed499bd7859574a7a615ee1581610ff2b3ed829c870276938b762ff147d9cd7d` | 399492 | 当前 src 重打；bundle 195,366,432B（无 models） |
| **新 models**（默认权重） | `9fcb9e8750ff7a52bc7ab5467f261ca689114a059874f9223054022ac41331dd` | 399492 | 当前 src 重打；bundle 868,852,947B（detector+ocr+sfx 权重 sha 校验通过） |

- 新旧 sha256 不同；exe 字节数相同属 PyInstaller bootloader 固定，差异在 PYZ/entry 内容。
- base 与 models 的 core_service.exe 也不同（build_sidecar 把 variant 注入 entry/资源），两包 VERSION.json 分别记录。
- 证据：`sidecar-hashes.json`、`build-base.log`、`build-models.log`。

## 2. AC2 同构建 8 页 Run（Host 命令面）

驱动方式：真实 `HostRuntime` + `HostCommandDispatcher`（`library_list_books` → `list_chapters` →
`list_chapter_pages` → `library_start_run` → 轮询 `library_get_run_snapshot` → `library_get_task_projection`
→ 逐页 `list_regions`），侧车 = **新 models 构建**，数据根 = BOOK-FIXTURE 私有副本（locks/catalog 清理）。
run=`run-457dbf2a7f9c44d5b59607db56690b29`，timeline pending→running(0.5s)→completed_with_failures(5.58s)。

| 页 | 区域数 | 任务状态 | 步骤 |
|---|---|---|---|
| 1 (f52f2772) | 13 | failed | detect/ocr/**color**/term_extract **completed**；translate failed `PROVIDER_NOT_CONFIGURED` |
| 2 (4f8a2414) | 6 | failed | 同上 |
| 3 (a607fc4c) | 7 | failed | 同上 |
| 4–8 | **0/0/0/0/0** | **completed** | detect completed（0 region ⇒ 空检测语义生效） |

- **无 OCR/color 的 `PROVIDER_NOT_CONFIGURED`**（旧构建在 color 处 `PROVIDER_FAILED`、OCR 未配置；现已修复）。
- translate 仍缺口：3 条 `PROVIDER_NOT_CONFIGURED`（如实记录；TRANSLATE-PROVIDER-1 由 route-research 并行推进）。
- 证据：`run-smoke.json`（含 page_ids/region_counts/每页 steps/timeline）。临时 harness 未入库（allowed_paths 不含
  `tests/**`），Handoff 记录复现字段；证据 JSON 由真实 Host 命令面运行产生。

## 3. AC3 发布件与 smoke

| 包 | zip 大小/sha256 | 安装 | 卸载 | sidecar 随包 | console | 许可证 |
|---|---|---|---|---|---|---|
| base | 102,975,176B / `e9997898…5675ea` | ×2 幂等 | ×2 幂等 | 1954 files / 195,366,432B | **0** | byte-identical |
| models | 724,983,494B / `4cbd0566…0942c7` | ×2 幂等 | ×2 幂等 | 1964 files / 868,852,947B + models | **0** | byte-identical |

install-smoke：`window_handle_found=true`、`exit_code=0`、`residual_processes=0`、`install_dir_after=false`。
证据：`smoke/install-{verify,smoke}-{base,models}.json`、`packages/*.json`。

## 4. AC4 元数据 / 范围说明

- `VERSION.json.sidecar_build`：两包实测与 sidecar 字节一致（base `ed499b…9cd7d` / models `9fcb9e…31dd`）。
- `packaging/m2ac5/README.md`：新增 §2.1 Current frozen build（新旧 sha、bundle 大小、torch-free 断言说明）。
- **README 安装说明**：仓库无根 README；安装说明以包内 `docs/UPGRADE.md`/`MANUAL_VERIFY.md` 承载，但本卡
  `allowed_paths` 不含 `apps/desktop-avalonia/docs/**`，故未改该文件（避免越界）；已在 `packaging/m2ac5/README.md`
  同步构建/发布信息，并把 `VERSION.json.sidecar_build` 作为安装排查字段。建议 DSH 后续单独授权该 docs 修改
  （或在下个打包 Task 覆盖）。
- NOTICE/THIRD_PARTY_LICENSES：闭包依赖集合与旧构建相同（仅 Python 模块内容变化），无需更新；包内 license
  与仓库根 byte-identical 已断言。

## 5. AC5 门禁

| 门 | 结果 |
|---|---|
| `scripts/test.ps1` | **177/177 passed, 0 skipped**（CoreClient 56 / Host 46 / App 75） |
| pytest | **3 failed, 2753 passed, 9 skipped**（基线一致，0 新增） |
| `check.ps1 -TaskPath` | PASS（既有 WARN 除外） |

## 6. 遗留 / NOT_RUN

1. **translate 仍缺口**：3/3 `PROVIDER_NOT_CONFIGURED`，需 TRANSLATE-PROVIDER-1（route-research 在途）合入后
   重新打包/复验，才能闭环 Run→Export。
2. `docs/UPGRADE.md` 未改（allowed_paths 限制，见 §4）；`doc/STATUS.md`/PLAN/LEDGER 指针由 DSH 收口更新。
3. 旧包（FINAL-VALIDATION `out/`）保留未动，仅新增 `task-envs/RELEASE-REPACK-1/out/` 新包，避免覆盖他人在途引用。
4. 临时 AC2 harness 未入库（见 §2），复现步骤见 Handoff；如要求 CI 化，需 DSH 授权 `tests/**` 或新增 `scripts/**` 工程。
5. 需独立 Review（Owner 不得自审）。
