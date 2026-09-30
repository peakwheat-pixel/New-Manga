---
task_id: M2-PROD-DETECT-2
author: ZCode
recipient: Codex（integrator）；reviewer=DeepSeek Harness（非作者，r2 定点复审）
base_commit: f79203eb
delivery_head: dbad2027（r1 review-fix 主体；证据 commit 紧随其后，见提交列表）
status: review_fix_delivered
supersedes: doc/handoffs/M2-PROD-DETECT-2-1cf731ca.md（r1 交付记录，保留为历史证据）
review_fix_of: verification/M2-PROD-DETECT-2/raw-r1（r1 时点证据已整体归档于此）
---

# Handoff：M2-PROD-DETECT-2 r1 review-fix（DSH r1 changes_requested → R1-R12 处置）

## 交付结果

DSH r1 review（`G:/CODEX/New Manga.task-envs/M2-PROD-DETECT-2/dsh-review-r1.md`，verdict=changes_requested，2×P1+5×P2+P3/P4）的全部 12 项处置完毕；acting Codex 三条裁决（Task 内「裁决⑤⑥⑦」）落地。前一任 Owner（同角色 ZCode）因额度熔断留下的 R5/R6 半成品（core_assembly 装配降级 + 测试增强，两个未提交改动）经完整性核验（装配段全分支覆盖、`bundled_in_release` 代码引用零残留）后补完，随本返修一并交付。

**核心语义变化（裁决⑤）**：权重缺失失败语义统一——manga frozen 全缺不再装配期 raise，改为 stderr 一行警告（含全部 probed candidates）+ 正常装配，detect 期 typed `PROVIDER_NOT_CONFIGURED`（与 doctr 完全对称）；「语义分叉」消解。

**AC 判定变化（裁决⑥）**：AC5 由 PASS 改判 **PARTIAL**——frozen 命令面（core.ping/ListBooks/core.shutdown，M2-IPC1 冻结）无 detect RPC，端到端 frozen detect 结构性不可达；NOT_RUN 子项=「frozen 进程内 ML import/detect」，登记后续 slice「M2-IPC1 命令面扩展 + frozen 进程内 detect 验证」。本 Task 可验收结论收窄为「**运行时+权重随包就绪 + 闭包外等价推理验证**」。

## R1-R12 逐条处置表

| 项 | 处置 | how（文件:位置） |
|---|---|---|
| R1[P1] warn 载体重建 | closed | `core_sidecar.spec` `_archive_warn_file`（每 Analysis 后 copy 到 `warn-archive/warn-<entry>.txt`，构建日志含 `warn-archive:` 行）；四文件入库 `verification/M2-PROD-DETECT-2/warn/`；`warn/classify_warn.py` + `warn/CLASSIFICATION.md` 逐条分类（958 missing 全归桶 12 类；**detect 链硬依赖零 missing**；hidden-import 软告警 3 类各自论证）；release-notes §AC1 重建结论；Task AC1 措辞同步。r1「13 missing 0 ML」结论作废（载体是无 ML 的 catalog_loader Analysis） |
| R2[P1] AC5 口径 | closed（PARTIAL，裁决⑥） | Task AC5 判定改 PARTIAL + NOT_RUN 子项 + 后续 slice 登记（Task「遗留与边界」）；probe results JSON `boundary_note` 同步；release-notes §AC5 收窄表述 |
| R3[P2] transformers 机制 | closed | `core_sidecar.spec` `ML_HIDDENIMPORTS=["transformers","transformers.models.rt_detr"]`（core_service 入口）+ `_assert_ml_closure`（Analysis 后断言两者进 `a.pure`，缺即 `SystemExit` fail build；本次构建日志实测输出 `closure assertion: core_service PYZ carries transformers, transformers.models.rt_detr (8572 pure modules)`）+ 构建后 PYZ 清单复核（`raw/pyz-core-service-listing.txt`：transformers 2320 条、`transformers.models.rt_detr` 11 条、rt_detr_v2 全家、doctr 170 条）；Handoff r1「lazy-import 跟踪进 PYZ」机制句由本文件更正 |
| R4[P2] doctr detect 断言 | closed | `packaged-detect-probe.py` `run_l4` 新增 (b)：闭包外 doctr detect（build venv driver，`DoctrDetectionProvider` + 包内不存在的 `fast_base-688a8b34.pt` 候选）断言 typed `ProviderNotConfigured`（`error_code=PROVIDER_NOT_CONFIGURED`），场景 `PK-L4-doctr-detect-fail-closed-typed`；L4(a) docstring 明示「frozen 启动验证 only，detect 语义由单测+闭包外探针覆盖」 |
| R5[P2] 裸 ValueError | closed（裁决⑤，前任半成品完成） | `core_assembly.py` `_resolve_detector_weights_path`：删 `bundled_in_release` 参数与 `raise ValueError`，frozen 全缺 → `print(..., file=sys.stderr)` 一行警告（weights name + probed candidates + NOT_CONFIGURED 指引）→ 返回默认路径；装配不崩。「权重目录缺失=整机不可启动」后果随装配期 raise 一并消除（Task 遗留与边界登记） |
| R6[P2] 语义分叉追认 | closed（裁决⑤） | 分叉消解（两 backend 同一 lookup 同一失败形状）；Task「r1 review 处置裁决」节 + 裁决 4 文本追加追认注记；AC3 措辞改「同一查找顺序 + 失败语义统一（detect 期）+ 装配期 stderr 警告」；`build_sidecar.ps1` `-SkipWeights` 注释修正（stderr 警告 + detect 期 typed NOT_CONFIGURED，非装配期崩溃） |
| R7[P2] 证据重绑定 | closed | 全部代码/spec 改动完成后重新构建：构建时 `HEAD=dbad2027a196e6d4ae933dc9401037809bd668f2`（构建日志 `build_sidecar: git HEAD=dbad2027…`），构建时工作树=返修 commit 已提交（干净）；新 NSIS sha256/onedir 字节文件数绑定该 tip（见下表）；r1 时点证据整体归档 `raw-r1/`（git mv，保留 review 锚点） |
| R8[P3] README | closed | `packaging/m2ac5/README.md` §1（ML 栈五行+裁决 2 定位翻转+权重随包+体积口径+mobi/pypdfium2）与 §2.b/2.c（权重复制、`-SkipWeights`/`-WeightsSource`、新体积口径指向 release-notes） |
| R9[P3] requirements 注释 | closed | `requirements-build.txt` pypdfium2/mobi 段改写：「mobi 不进（lazy import）」；「pypdfium2 由 doctr 传递依赖带入（不手工 pin，pip 解析），风险登记（ML 升级后复核闭包）」 |
| R10[P4] -WeightsSource | closed | `build_sidecar.ps1` param 新增 `[string]$WeightsSource = "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector"`，`Copy-MangaWeights` 参数化，两条调用路径（增量短路+全量）均传参；注释明示「只重定位来源，不放宽 pin 校验」 |
| R11[P4] 测试增强 | closed（前任半成品保留+核验） | env-only 装配级用例 `test_assembly_reads_env_override_without_explicit_argument`；`test_non_frozen_never_probes_a_bundle_layout` stray 真实落盘（fake interpreter 于 tmp_path，不触碰真 venv）；`__closure__` 反射收敛为 `_wired_detector` helper（与 `test_detector_assembly.py` 同技术）；计数如实 11→14（manga/doctr 全缺两测合并参数化 2 例 + 3 新测） |
| R12[P4] 场景命名/层数 | closed | `PK-L4-doctr-starts-fail-closed-at-detect` → `PK-L4-doctr-starts-without-assembly-error`；probe docstring/Task/Handoff 明示「6 场景 = 4 层（L2 反证+恢复、L4 启动+闭包外 detect）」 |
| L2 反证改写 | closed | `run_l2` 断言改「移权重 → EXIT=0 status=ready + stderr 含 `probed candidates`；还原 → ready 且警告消失」；场景改名 `PK-L2-weights-absent-assembles-with-warning`；results JSON/raw 日志同步 |

## 新构建三数字（R7，绑定 dbad2027）

| 项 | r1（1cf731ca 时点，已归档 raw-r1） | **r1 review-fix（dbad2027）** |
|---|---|---|
| onedir | 1,116,380,855 B / 5,550 文件 / 构建 278s | **1,116,381,295 B / 5,550 文件 / 构建 353s**（hiddenimports 增量 +440 B，符合「略涨」预期） |
| NSIS | 460,184,382 B / sha256 `6c765ed3…` | **460,175,852 B（438.86 MiB）/ sha256 `ed4015845fcc092d7944f65e67d2575d9c4331e76b1677c133daf32ae55772b0`** / tauri 构建 516s（cargo release 20.6s + makensis） |
| warn 面（AC1 载体重建） | r1 引用的 29 行/13 missing 实为 catalog_loader Analysis（无 ML），结论作废 | **core_service Analysis 979 行 / 958 missing 全归桶；detect 链硬依赖（torch/torchvision/transformers+rt_detr+rt_detr_v2/safetensors/tokenizers/numpy/cv2/PIL/doctr/h5py/shapely/scipy）零 missing**；软告警：torch.utils.tensorboard 收集失败（console :119/:257）、torchvision.image/_C 与 scipy.special._cdflib hidden-import（:157-160/:294-297）——逐一论证见 warn/CLASSIFICATION.md |

## 验证证据（全部重跑 @dbad2027）

| 验证 | 结果 | 日志/产物 |
|---|---|---|
| 构建期闭包断言（R3） | **真实执行**：`closure assertion: core_service PYZ carries transformers, transformers.models.rt_detr (8572 pure modules)` | raw/build-sidecar-console.log |
| PYZ 清单复核 | transformers 2320 条 / `transformers.models.rt_detr` 11 条（含 modeling_rt_detr）+ rt_detr_v2 全家 / doctr 170 条 | raw/pyz-core-service-listing.txt |
| warn 逐条分类（R1） | 958 missing / 12 桶 / 硬依赖零 missing / unclassified=0 | warn/warn-*.txt（4 文件）+ warn/CLASSIFICATION.md |
| GATE（M2-AC5 runner） | **25/25 PASS，GATE: PASS**（CS-E2 绑定新 NSIS sha256 `ed401584…`；安装后 5,552 文件） | raw/cleanstart-runner-stdout.log |
| 发布形态探针 | **6/6 PASS（4 层 6 场景）**：L1 启动 ready；L2 移权重→stderr 警告含 probed candidates+装配 ready、还原→警告消失；L3 真实推理 EXIT=0、候选=2、稳态 288ms/页（冷启动 17,478ms 本轮含冷缓存）；L4 doctr 启动 EXIT=0 + 闭包外 typed PROVIDER_NOT_CONFIGURED（provider_id=local-doctr） | packaged-detect-probe-results.json + raw/l*.log |
| pytest providers | **289 passed + 1 failed**（既有环境性失败 `test_registry_readiness::test_no_model_runtime_is_installed_in_this_environment` 保持；基数 275+1 + 本 Task 14） | raw/pytest-three-suites-tail.log |
| pytest m2_acceptance / core | **35 / 77 passed**（基数保持） | 同上 |
| cargo test | **44 passed + 1 ignored, 0 failed**（本轮零 Rust 触碰，实测同上轮） | 本表 |
| vitest | **31 passed（5 文件）**（本轮零前端触碰，实测同上轮） | 本表 |
| M2-AC5 raw 还原 | runner 重写文件 `git checkout --` 还原，专项 diff 为空 | git status |
| 权重治理 | onedir 内三文件 sha256 与 pin 一致（Copy-MangaWeights 校验 + L3 provider 内 pin 校验传递 NSIS 安装态）；`git ls-files` 零权重 | build-sidecar-console.log + release-notes §AC2 |

未运行项：真干净 Windows 覆盖（M2 Release Gate 口径冻结 NOT_RUN）；**frozen 进程内 ML import/detect（AC5 NOT_RUN 子项，裁决⑥，待 M2-IPC1 命令面扩展）**——不伪造。

## 提交列表（branch `agent/zcode/M2-PROD-DETECT-2`，未 push）

- `e0e367c1`（上轮 tip：claim 44e70f66 → implement 1cf731ca → handoff 80f7a0cb → hygiene fb943798 → sync e0e367c1）
- `dbad2027` review-fix 主体（R1-R12 处置 + 前任熔断遗留半成品的完成；构建输入与本表数字的被测 commit）
- 证据 commit（本 Handoff、release-notes 更新、warn/ 四文件+分类、probe results、raw 重跑日志、raw-r1 归档、Task 测试表实测回填）
- task record commit（Task frontmatter delivery_head → 证据 commit sha；status 保持 in_review）

## 接收方式（r2 定点复审）

- 复审锚：r1 报告（`G:/CODEX/New Manga.task-envs/M2-PROD-DETECT-2/dsh-review-r1.md`，锚 1cf731ca/80f7a0cb）+ 返修 tip（见上提交列表）。r1 时点证据在 `verification/M2-PROD-DETECT-2/raw-r1/`（原样保留，行号引用不失效）；返修新证据在 `raw/`、`warn/`、`packaged-detect-probe-results.json`。
- 复现构建：`powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1 -Force`（观察 `closure assertion` 与 `warn-archive:` 输出）→ `cd apps/desktop/src-tauri && npx --yes @tauri-apps/cli@2 build` → `python packaging/m2ac5/run_clean_start_e2e.py` → `python verification/M2-PROD-DETECT-2/packaged-detect-probe.py --install-dir %TEMP%/m2ac5-cleanstart/install`。
- pytest：主 venv `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`，`PYTHONPATH=src`，`pytest tests/providers tests/m2_acceptance tests/core`。
- 重点核查建议（r2）：①warn 分类桶与硬依赖反证（R1 载体）；②L2 降级断言与新装配语义一致性（R5/R6）；③AC5 PARTIAL 判定与 NOT_RUN 子项登记（R2/裁决⑥）；④新 NSIS/onedir 数字与 raw 日志绑定（R7）。

## 下一任务建议（必填）

- Task ID / 标题：无需新立 Task——本返修进入 DSH r2 定点复审；通过后 Codex 集成。**另：裁决⑥登记的后续 slice「M2-IPC1 命令面扩展 + frozen 进程内 detect 验证」待 Codex 释放契约范围（core_service 命令面扩展须 Codex 先立契约）后另行注册。**
- 推荐 Agent / Reviewer：DSH（非作者 r2 复审）；集成=编排会话代行 Codex。
- Recovery point：仓库 `G:/CODEX/New Manga`，worktree `G:/CODEX/New Manga.worktrees/M2-PROD-DETECT-2-zcode`，branch `agent/zcode/M2-PROD-DETECT-2`，base `f79203eb`，返修主体 `dbad2027`。
- 禁止范围不变：`apps/**`、`tauri.conf.json`、`run_clean_start_e2e.py`、`ports/**`、两个 detection provider、`requirements.txt`、`experiments/**`；spec `console=True` FROZEN；权重永不入库。
- 可直接转发给 Agent 的指令：`「你是 DSH reviewer（非作者）。在 worktree G:/CODEX/New Manga.worktrees/M2-PROD-DETECT-2-zcode（branch agent/zcode/M2-PROD-DETECT-2）对 M2-PROD-DETECT-2 做 r2 定点复审：先读 doc/tasks/M2-PROD-DETECT-2.md（含 r1 处置裁决⑤⑥⑦）与 doc/handoffs/M2-PROD-DETECT-2-dbad2027.md 的 R1-R12 处置表，对照你在 G:/CODEX/New Manga.task-envs/M2-PROD-DETECT-2/dsh-review-r1.md 的 12 项 findings 逐项核销；重点①warn 分类载体（verification/M2-PROD-DETECT-2/warn/）②AC5 PARTIAL（裁决⑥）③L2 降级断言④新构建数字绑定 dbad2027；r1 证据已归档 raw-r1/。报告写 verification/M2-PROD-DETECT-2/review-r2-dsh.md。」`

## 风险与遗留

- 已知限制（在 r1 基础上更新）：①docTR 权重不进包（裁决 3；发布形态切回=frozen stderr 警告 + detect 期 typed NOT_CONFIGURED+指引，与 manga 同形状）；②权重随包冻结（换权重=重装或 data root 覆盖，无 UI）；③无 UI 权重管理；④build venv 传递依赖（pypdfium2 由 doctr 传递带入、pip 解析非手工 pin，风险登记——R9）；⑤frozen 进程内无 detect RPC（AC5 PARTIAL 的结构性原因，裁决⑥，待 M2-IPC1）；⑥装配期 stderr 警告语义（裁决⑤）：包内权重全缺时应用照常启动，detect 期 typed fail-closed。
- 用户选择点：安装包体积维持数百 MiB 级（裁决 1，可撤销）；裁决⑤改变了 r1 前的「frozen 全缺=装配期崩溃」行为——若产品反而需要「安装损坏快速可见」，revert 装配段即回 fail-fast（Task 裁决⑤已登记撤销方式）。
- 破坏性操作：无（无迁移、无宿主 %APPDATA% 写入——GATE CS-Z4 实测 PASS）。
- 关联：M2-PROD-DETECT-1（done @056617e4）；M2-DOCTR-QUAL-C4（权重快照）；M2-RG1（console=True 冻结）；后续 slice M2-IPC1（frozen 命令面扩展）。
- 回退方法：revert `dbad2027` + 证据 commit 即回 r1 交付态（1cf731ca 语义）。
