# AGPL-RELEASE-1 实施报告（models 包 AGPL-3.0 声明落地 + AGPL 全文随包 + 重打包验证）

- Task：`doc/tasks/AGPL-RELEASE-1.md`（shared task-2；Owner `region-workbench-owner`，Reviewer `dsh`）
- Branch / Worktree：`task/AGPL-RELEASE-1` / `G:/CODEX/New Manga.workspace/worktrees/AGPL-RELEASE-1`
- 基线：worktree 起点 `7f0d1daef`（任务卡登记 base `d8aadc0de`；REGION-WORKBENCH-1 已先集成）
- 输入包（只读）：`task-envs/RELEASE-REPACK-5/out/`（base 103,374,546 B / models 725,382,787 B）
- 未 push；未改产品源码/Core/旧壳/冻结契约；未改 `LICENSE`（GPL-3.0 原文保留）；未覆盖 REPACK-5 out。

## 1. 交付摘要

| AC | 结论 | 关键证据 |
|---|---|---|
| AC1 权重与许可事实表 | **MET** | `verification/AGPL-RELEASE-1/weights-licenses.json`：models 包 10 个文件（4 权重 + 6 配置/词表）逐项 字节/sha256/许可证结论；`yolo11s-seg` 一手依据 = **ONNX 自身 metadata_props**（`author=Ultralytics`、`license=AGPL-3.0 License (https://ultralytics.com/license)`、`version=8.4.172`）+ Ultralytics 官方许可页 + Ultralytics 仓库 LICENSE（与 GNU 官方 AGPL-3.0 全文**逐字节一致**，sha `0d96a4ff…`）；RT-DETR/MangaOCR 保留 [待核实]（不阻断） |
| AC2 声明修正 | **MET** | `NOTICE.md`、`THIRD_PARTY_LICENSES.md`、`apps/desktop-avalonia/docs/LICENSE_AUDIT.md` 三处按变体给出结论：models（含权重）= **AGPL-3.0**；base（无权重）= **GPL-3.0-or-later**；删除「模型权重不随包」矛盾表述；包内副本逐字节一致（见 AC4） |
| AC3 AGPL 全文随包 | **MET** | 新增仓库根 `LICENSE-AGPL-3.0.txt`（34,523 B，sha256 `0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0`，来源 https://www.gnu.org/licenses/agpl-3.0.txt，抓取日期 2026-10-28）；`package.ps1` 许可文件组扩为 4 个（`LICENSE`/`LICENSE-AGPL-3.0.txt`/`NOTICE.md`/`THIRD_PARTY_LICENSES.md`），复制后 SHA-256 校验，base 与 models **都随包** |
| AC4 重打包验证 | **MET** | 重打 base + models 到 `task-envs/AGPL-RELEASE-1/out`：zip 字节/sha256 见 §3；包内 5 个许可文件（含 `LICENSE_AUDIT.md`）在 **zip 条目流**与 staging 两处均与仓库源逐字节一致；`VERSION.json` 记录 `license` 与 `license_files`；`package-manifest.json` 含 4 项许可 hash；大小与 REPACK-5 相当（各 +0.11 MB / +1 file） |
| AC5 回归与门禁 | **MET** | `extract-command-surface.py --check` PASS（66）；`scripts/test.ps1` 隔离复跑 **PASS**（见 `test/summary.json` / `logs/test-ps1-console.log`）；`check.ps1 -TaskPath` PASS（见 `check-governance.json`）；Canonical Evidence 全部 64-hex pin + Handoff |

## 2. AC1 权重与许可事实表（来源：`weights-licenses.json`）

models 包 `app/core-sidecar/models/` 共 10 个文件、合计 673,486,515 B（642.3 MiB）：

| 文件（相对 `models/`） | 字节 | sha256 | 类型 | 许可结论 |
|---|---|---|---|---|
| `detector/yolo11s-seg.onnx` | 40,824,255 | `944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d` | 权重 | **AGPL-3.0（Ultralytics YOLO11s-seg）已核实** |
| `detector/rtdetr-v2-fixed.onnx` | 171,618,071 | `c7fb5af1a8982416b56955e621c1b10397730807956998066e2fbc132c77bbc3` | 权重 | Apache-2.0（HF 模型卡）[待核实；不阻断] |
| `ocr/manga-ocr-onnx/encoder_model.onnx` | 343,454,249 | `15fa8155fe9bc1a7d25d9bb353debaa4def033d0174e907dbd2dd6d995def85f` | 权重 | 上游 MangaOCR [待核实；不阻断] |
| `ocr/manga-ocr-onnx/decoder_model.onnx` | 117,480,262 | `ef7765261e9d1cdc34d89356986c2bbc2a082897f753a89605ae80fdfa61f5e8` | 权重 | 同上 [待核实；不阻断] |
| `ocr/manga-ocr-onnx/{config,generation_config,preprocessor_config,special_tokens_map,tokenizer_config}.json` + `vocab.txt` | 132–77,161 | 见 `weights-licenses.json` | 配置/词表（非权重） | 随上游 MangaOCR [待核实；不阻断] |

**yolo11s-seg = AGPL-3.0 的一手依据（记录 URL / 抓取日期 / sha256）**：
1. **文件自身**：ONNX `metadata_props` = `{description: "Ultralytics YOLO11s-seg model trained on …", author: "Ultralytics", license: "AGPL-3.0 License (https://ultralytics.com/license)", version: "8.4.172", docs: "https://docs.ultralytics.com", task: "segment"}`（用 build venv 的 onnx 1.23.2 读取，记录于 `weights-licenses.json`）。
2. **Ultralytics 官方许可页** `https://www.ultralytics.com/license`（2026-10-28 抓取，398,454 B，sha256 见 JSON；页面原文含 “AGPL-3.0 and Enterprise licensing options for YOLO models and applications.”）。
3. **Ultralytics 仓库 LICENSE** `https://raw.githubusercontent.com/ultralytics/ultralytics/main/LICENSE`（2026-10-28 抓取，34,523 B，sha256 `0d96a4ff…`，与 GNU 官方 AGPL-3.0 全文**逐字节一致**）。
4. GNU 官方全文 `https://www.gnu.org/licenses/agpl-3.0.txt`（34,523 B，sha256 `0d96a4ff…`；即随包 `LICENSE-AGPL-3.0.txt`）。

## 3. AC4 重打包结果

| 变体 | 包名 | 文件 | zip 字节 | zip sha256 | 与 REPACK-5 字节差 |
|---|---|---|---|---|---|
| base | `NewManga-0.1.0-win-x64.zip` | 1,968 | **103,492,048** | `722fc62b53a4488dff8e3043b419a720cb59c3e4c790a9c8d19511efb627e8ef` | +117,502 B（+0.11 MB，+1 文件） |
| models | `NewManga-0.1.0-win-x64-models.zip` | 1,978 | **725,499,708** | `480d06323ce482214955582dc86696bfdd8023e9227100941fd6b8873b237f67` | +116,921 B（+0.11 MB，+1 文件） |

包内许可文件（zip 条目流 SHA-256 **等于**仓库源；staging 副本同值；base 与 models 各一套）：

| 文件 | 字节 | sha256（= 仓库源） | base | models |
|---|---|---|---|---|
| `LICENSE-AGPL-3.0.txt` | 34,523 | `0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0` | ✔ | ✔ |
| `NOTICE.md` | 3,411 | `dc36e35f854916b87855f8ad66295d6fd935bfceefb770b4725381c000ecc53c` | ✔ | ✔ |
| `THIRD_PARTY_LICENSES.md` | 4,769 | `ee5393685aa9f098ea590e39ce93d0934bbbfe02ffcf3795a4227e49fab2618c` | ✔ | ✔ |
| `LICENSE`（GPL-3.0 原文，未改） | 34,906 | `cde3a5c4c116f8cde7ba83ee7a4a885bc591164195b6123bfcbcdc3a52f9a88c` | ✔ | ✔ |
| `LICENSE_AUDIT.md`（源 `apps/desktop-avalonia/docs/`） | 1,958 | `7a0db863dfa8396584d18063c649ac49babd904f67b5a3ee7cbb58f9e7bfeaeb` | ✔ | ✔ |

- `VERSION.json`：base `license=GPL-3.0-or-later`、`bundled_weights_license="none (no model weights in this variant)"`；models `license=AGPL-3.0`、`bundled_weights_license="AGPL-3.0 (Ultralytics YOLO11s-seg: app/core-sidecar/models/detector/yolo11s-seg.onnx)"`；两者 `license_files` 均含 4 个许可文件；`sidecar_build` 记录 `core_service_sha256=bde2d866…` 与 `repo_head`。
- `package-manifest.json`：base/models 的 `licenses` 均含 4 项许可文件 hash；`files[]` 含 `LICENSE_AUDIT.md` 等全部随包文件（逐文件 sha256）。
- 变体事实：base `models/` 目录**不存在**；models 的 `detector/yolo11s-seg.onnx` 在包内实测 40,824,255 B / `944e8114…18d`，与 REPACK-5 完全一致（模型权重未被改动）。
- 校验细节：`package-check.json` 的 `variants.*.license_files_in_zip[*].byte_identical` 全为 `true`，且 `checks.every_license_zip_entry_byte_identical=true`。

## 4. AC2/AC3 文件变更

| 文件 | 变更 |
|---|---|
| `NOTICE.md` | 明确 base/models 两个变体的整体许可（GPL-3.0-or-later / AGPL-3.0）；写明 models 含 Ultralytics YOLO11s-seg 权重（含字节/sha256）→ 整体 AGPL-3.0；删除模糊条件句；第三方登记表加 YOLO11s-seg 行；许可见证组加入 `LICENSE-AGPL-3.0.txt` |
| `THIRD_PARTY_LICENSES.md` | §3 由「不随仓库分发」的待决列表改为 **models 变体随包清单**（路径/字节/sha256/许可结论）；YOLO11s-seg 一手依据三条；明确 models=AGPL-3.0 / base=GPL-3.0-or-later；§5 Gate 勾选 AGPL 落地项 |
| `apps/desktop-avalonia/docs/LICENSE_AUDIT.md` | 按变体给出两套正确结论（base:GPL-3.0-or-later 无权重；models:AGPL-3.0 含 YOLO11s-seg）；删除「模型权重不随包」「依赖清单未包含 AGPL」矛盾表述；列随包 4 许可文件与校验方式 |
| `LICENSE-AGPL-3.0.txt`（新增） | GNU AGPL-3.0 官方全文（未改动），sha256 `0d96a4ff…` |
| `apps/desktop-avalonia/scripts/package.ps1` | 许可文件组 3→4（新增 `LICENSE-AGPL-3.0.txt`），复制后 SHA-256 校验、缺失即失败；`VERSION.json` 新增 `license` / `license_files` / `bundled_weights_license` 三字段；既有打包/复制/zip 逻辑不动 |

## 5. AC5 回归与门禁

| 命令 | 结果 | 证据 |
|---|---|---|
| `python apps/desktop-avalonia/scripts/extract-command-surface.py --check` | **PASS：66 commands**（零漂移） | `logs/extract-command-surface.log` |
| `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence-test` | 隔离复跑（产品代码零改动）：**PASS 258/258 passed, 0 skipped**（coreclient 61 / host 60 / app 137） | `test/summary.json`、`logs/test-ps1-console.log` |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/AGPL-RELEASE-1.md` | **PASS**（无阻断 error） | `check-governance.json`（原始日志在 task-env `logs/check-governance.log`） |
| 打包两次（base/models） | exit 0，见 §3 | `logs/package-*.log`、`logs/publish-*.log`、`packages/*` |

## 6. 风险与遗留

1. **RT-DETR / MangaOCR 许可仍 [待核实]**：无内嵌许可元数据、上游模型卡未在本任务抓取；AC1 明确「不作为本卡阻断」。下次发行 Gate 前需补一手结论（若其中出现非 AGPL 兼容许可，models 声明结论不受影响，但仍须在 THIRD_PARTY 表补全）。
2. **AGPL 义务的发行侧执行**：本任务落地「声明 + 全文随包 + 校验」；发行页需同时提供对应源码获取方式（仓库/发行页），属发布流程，不在本卡代码范围（NOTICE 已写明）。
3. **重打包环境**：`package.ps1` 的 GPU probe 依赖 `G:/CODEX/New Manga.task-envs/m2ac5-build/Scripts/python.exe`（存在），VERSION.json 的 devices 字段与 REPACK-5 同源；base/models zip 大小 +0.11MB 属许可文件与 NOTICE/VERSION 文本增量，无异常膨胀/缺失。
4. **`LICENSE`（GPL-3.0）原文未改**；`LICENSE-AGPL-3.0.txt` 与 GNU 官方逐字节一致（34,523 B）。
5. 本卡不改 `doc/STATUS.md`/`PLAN`/`LEDGER`（由 DSH 统一更新）。

## 7. 复现命令

```powershell
# AC1 证据重建（读取只读的 REPACK-5 models 包）
python <task-env>/build_weights_licenses.py

# AC2/AC3：确认许可文件组 + AGPL 全文
Get-FileHash LICENSE,LICENSE-AGPL-3.0.txt,NOTICE.md,THIRD_PARTY_LICENSES.md -Algorithm SHA256

# AC4：重打两包（输出只写自己的 task-env；REPACK-5 out 只读）
$sidecar = 'G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-5/out/NewManga-0.1.0-win-x64-models/app/core-sidecar'
pwsh -NoProfile -File apps/desktop-avalonia/scripts/package.ps1 -OutputRoot <task-env>/out -SidecarDir $sidecar
pwsh -NoProfile -File apps/desktop-avalonia/scripts/package.ps1 -OutputRoot <task-env>/out -SidecarDir $sidecar -WithModels
pwsh -NoProfile -File <task-env>/verify_packages.ps1

# AC5
python apps/desktop-avalonia/scripts/extract-command-surface.py --check
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence-test
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/AGPL-RELEASE-1.md
```

## 8. 证据索引（`verification/AGPL-RELEASE-1/`）

| 路径 | 内容 |
|---|---|
| `weights-licenses.json` | AC1 权重事实表 + 一手许可来源（URL/抓取时间/字节/sha256）+ ONNX metadata_props + REPACK-5 输入摘要 |
| `package-check.json` | AC4 两变体 zip 字节/sha256、zip 条目流与 staging 双重复核的 5 许可文件 hash、VERSION/manifest 许可字段、权重存在性、REPACK-5 大小对比 |
| `packages/package-summary-{base,models}.json` | `package.ps1` 产物摘要（zip/字节/许可 hash/模型字节） |
| `packages/VERSION-{base,models}.json` | 两变体随包 VERSION.json 副本（含 license 声明） |
| `logs/package-{base,models}.log`、`logs/publish-{base,models}.log` | 两次打包与 dotnet publish 原始日志 |
| `logs/extract-command-surface.log` | 命令面 `--check` PASS |
| `logs/test-ps1-console.log`、`test/summary.json` | 隔离复跑门禁日志/汇总 |
| `check-governance.json` | `check.ps1 -TaskPath` PASS 记录（原始日志在 task-env `logs/check-governance.log`） |
| `REPORT.md` | 本报告 |
