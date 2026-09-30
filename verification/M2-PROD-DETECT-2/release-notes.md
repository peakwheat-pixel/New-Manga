# M2-PROD-DETECT-2 发布形态验证记录（owner=ZCode，base=f79203eb）

> 本文件为 **r1 review-fix 重跑版**：DSH r1 review（changes_requested，R1-R12）处置后的全量证据重跑，构建/验证绑定返修 commit `dbad2027`（构建时 `HEAD=dbad2027a196e6d4ae933dc9401037809bd668f2`，工作树=返修 commit 已提交，见 `raw/build-sidecar-console.log`）。r1 时点证据整体归档于 `raw-r1/`（git mv，review 锚点不失效）。逐项处置见 `doc/handoffs/M2-PROD-DETECT-2-dbad2027.md` 的 R1-R12 处置表。

- 机器：本机 win32（全部 CPU 路径）
- 构建/验证 venv：build=`G:/CODEX/New Manga.task-envs/m2ac5-build`（packager+runtime closure）；回归=`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`
- 权重快照：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/`（repo 外，git 不追踪；`build_sidecar.ps1 -WeightsSource` 参数化，默认即此路径）

## AC1 构建链（ML 栈进 sidecar 闭包；r1 review-fix：warn 载体重建 + hiddenimports 双保险）

| 项 | 实测（@dbad2027 全量重建） |
|---|---|
| `requirements-build.txt` | pyinstaller==6.22.3 + PySide6_Essentials==6.11.2 + shiboken6==6.11.2 + **python-doctr==1.1.0 / torch==2.14.0 / torchvision==0.29.0 / transformers==5.17.0 / safetensors==0.8.0**（ML 五行与主 `requirements.txt` 逐字一致；头注释登记裁决 2；pypdfium2/mobi 注释按 R9 改写） |
| `core_sidecar.spec` | EXCLUDED 撤 torch/torchvision/doctr 三行（pandas/pytest/setuptools/distutils/pip 保持）；**R3：`hiddenimports=["transformers","transformers.models.rt_detr"]`（core_service 入口）+ `_assert_ml_closure` 构建期闭包断言**；`console=True` FROZEN 未触碰 |
| 构建期闭包断言（R3） | **真实执行**：`closure assertion: core_service PYZ carries transformers, transformers.models.rt_detr (8572 pure modules)`（`raw/build-sidecar-console.log`）；若缺即 `SystemExit` fail build |
| PYZ 清单复核（R3） | `pyi-archive_viewer -r -l core_service.exe`（`raw/pyz-core-service-listing.txt`）：transformers 2320 条、**`transformers.models.rt_detr` 11 条**（含 modeling_rt_detr）+ `transformers.models.rt_detr_v2` 全家、doctr 170 条。机制句更正（R3）：r1 所述「lazy-import 跟踪进 PYZ」不成立——transformers 原系 torch 内部两处可选 import 的偶然带入，现由 hiddenimports 显式保证 |
| onedir 构建 | `-Force` 全量重建 **353 s**，exit=0；构建日志含四条 `warn-archive:` 行（R1）与一条 `closure assertion:` 行 |
| **warn 文件（R1 载体重建）** | **r1 的「29 行/13 missing 全平台噪音 0 ML」结论作废**——该文件实为共享 warn 文件被最后一次 catalog_loader（无 ML）Analysis 覆盖的残留。本次按 Analysis 归档四文件（`warn/warn-{host_bridge,core_service,acceptance_bridge,catalog_loader}.txt`，host_bridge/catalog_loader 各 29 行，core_service/acceptance_bridge 各 979 行）。core_service Analysis：**958 missing 全部归入 12 桶**（平台条件 58/multiprocessing 探测 10/torch 可选加速后端 72/torch 分布式 30/**bundled 库 attribute 探测面 320**/torch 可选集成 13/doctr 可选 io 2/transformers 可选生态 180/scipy 可选后端 94/notebook-viz-pandas 50/io-net 序列化 128/mobi 边界 1），**unclassified=0**；**detect 链硬依赖（torch/torchvision/transformers+rt_detr+rt_detr_v2/safetensors/tokenizers/numpy/cv2/PIL/doctr/h5py/shapely/scipy）零 missing**。hidden-import 软告警（console :119/:257 tensorboard、:157-158/:294-295 torchvision.image/_C、:160/:297 scipy.special._cdflib）逐条论证见 `warn/CLASSIFICATION.md` |
| spec `console=True` | FROZEN 未触碰（M2-RG1 AC2） |

## AC2 权重随包

- `build_sidecar.ps1` `Copy-MangaWeights`：构建后（含增量短路路径）把三文件从快照复制进 `<bundle>/models/detector/ogkalu-comic-text-and-bubble-detector/`，**逐文件 SHA-256 校验后复制**（缺失/不匹配 throw）；`-SkipWeights`（注释已按 R5/R6 新语义修正：stderr 警告+detect 期 typed NOT_CONFIGURED，非装配期崩溃）；**R10：`-WeightsSource` 参数**（默认 C4 快照路径，只重定位来源、不放宽 pin 校验）。
- onedir 内三文件 sha256（本次构建日志 `build_sidecar: manga weights bundled (3 files, sha256 verified)` 校验通过）：`model.safetensors 037930a8…` / `config.json b6d70793…` / `preprocessor_config.json 7e9e2245…` —— 与 `detection_manga.py` pin 一致。
- **NSIS 安装后复核**（`%TEMP%/m2ac5-cleanstart/install/resources/core-sidecar/models/detector/...`）：三文件 `Get-FileHash` 实测 `037930a8…`/`b6d70793…`/`7e9e2245…` 与 pin 逐字一致（重打包无损，显式 hash 证据补齐 r1 NOT_VERIFIED#6）。
- tauri.conf.json 零改动（整目录 resource 机制随包）；`apps/desktop/src-tauri/target/**` 为 gitignored（`apps/desktop/.gitignore` L1），权重永不入库（`git ls-files` 零 .safetensors/.pt/models-detector/ogkalu 权重文件命中；fast_base 字样命中 9 条均为 M2-DOCTR-QUAL 文档文件名）。
- docTR 权重不进包（裁决 3）。

## AC3 包内回退解析（r1 review-fix：失败语义统一，裁决⑤）

- `src/bootstrap/core_assembly.py`：模块级 `_resolve_detector_weights_path(override, weights_name, db_path)`（**`bundled_in_release` 参数已删**），装配段 manga/doctr 两分支共用同一 lookup。
- 查找顺序（裁决 4）：env override（原样，不探测）> data root 存在性探测 > frozen 包内存在性探测（`sys.frozen` + `Path(sys.executable).parent/models/detector/<name>`）> 默认 data root 路径。
- **失败语义统一（R5/R6，裁决⑤）**：manga 与 doctr 的 frozen 全缺走**同一形状**——stderr 一行警告（weights name + 全部 probed candidates + NOT_CONFIGURED 指引）+ 装配成功 + detect 期 typed `PROVIDER_NOT_CONFIGURED`。r1 前的「manga 装配期 raise ValueError」已消除（装配期崩溃爆炸半径=整机，违背 M2-AC3「装配不崩、失败留在该步」）；**非 frozen 全缺 = 零变化**（装配成功、无输出、detect 时 NOT_CONFIGURED）。
- 单测 `tests/providers/test_detector_weights_lookup.py`：**14/14 PASS**（矩阵=env 优先（两形态）/空 override 落穿/data root 优先/仅包内命中/doctr 文件探测/frozen 全缺参数化×2（manga+doctr，断言 stderr 含 probed candidates）/包内命中零警告/非 frozen 零变化×3（含 stray 落盘反证）/装配级 wired 冒烟/**装配级 env-only（R11）**/**装配级全缺降级+警告**）。monkeypatch `sys.frozen`/`sys.executable` 模拟 onedir，不真打包。
- 既有面：`test_detector_assembly.py + test_detection_manga.py + tests/m2_acceptance/test_provider_fail_closed.py` 零回归（含在 289/35/77 口径内）。

## AC4 GATE 回归（M2-AC5 runner）

| 项 | 实测（@dbad2027） |
|---|---|
| onedir | 5,550 文件 / **1,116,381,295 B**（r1：1,116,380,855 B / 5,550——hiddenimports 增量 +440 B；基线 M2-PROD-DETECT-1：161 文件 / 99,308,142 B） |
| NSIS 安装包 | **460,175,852 B（438.86 MiB）**，sha256 **`ed4015845fcc092d7944f65e67d2575d9c4331e76b1677c133daf32ae55772b0`**（r1：460,184,382 B / `6c765ed3…`；基线 27,924,371 B） |
| 构建时长 | PyInstaller onedir 353 s；tauri build 516 s（cargo release 20.6 s + makensis ≈7 min） |
| GATE | **25/25 PASS，GATE: PASS**（`raw/cleanstart-runner-stdout.log`；CS-E2 绑定新 NSIS sha256 `ed401584…`；安装后 5,552 文件） |
| M2-AC5 raw | runner 重写 6 文件已 `git checkout --` 还原，专项 diff 为空 |

风险③（torch DLL 进 onedir 后启动变化）由 GATE 实测兜底：production 模式真实窗口 10 s 存活 + sidecar 全 reap，均 PASS。

## AC5 发布形态 detect 探针（判定 **PARTIAL**，裁决⑥；4 层 6 场景，R12 口径）

对 GATE 刚安装的环境（`%TEMP%/m2ac5-cleanstart/install`）执行，verdict=**PASS（6/6 场景，4 层）**：

| 层 | 场景 | 实测 |
|---|---|---|
| L1 | PK-L1-frozen-startup-ping | 安装后 core_service.exe（purged PATH，stdio JSON-lines）core.ping → **EXIT=0，status=ready** |
| L2 | PK-L2-weights-absent-assembles-with-warning（**R5/R6 改写**） | 包内 models/ 树临时移走 → frozen 进程**照常装配 EXIT=0 status=ready**，stderr 一行警告含 `probed candidates`；还原 → ready 且**警告消失**（PK-L2-recovery-after-restore） |
| L3 | PK-L3-real-inference | 合成漫画页经生产 adapter 全链，weights_dir=**安装后包内权重**：**EXIT=0，text 候选=2**，冷启动 17,478 ms（本轮含磁盘冷缓存），**稳态 288 ms/页**（ML 版本逐字一致：torch 2.14.0 / torchvision 0.29.0 / transformers 5.17.0 / safetensors 0.8.0 / python-doctr 1.1.0 / tokenizers 0.23.2） |
| L4 | PK-L4-doctr-starts-without-assembly-error（**R12 改名**：仅 frozen 启动验证） | `NEWMANGA_DETECTOR_BACKEND=doctr` 下 frozen 进程正常启动 EXIT=0（装配不崩；警告状态见 raw 日志） |
| L4 | PK-L4-doctr-detect-fail-closed-typed（**R4 新增**） | 闭包外 detect 断言（build venv，生产 `DoctrDetectionProvider` + 包内不存在的 `fast_base-688a8b34.pt` 候选）：**typed `ProviderNotConfigured`（error_code=PROVIDER_NOT_CONFIGURED，provider_id=local-doctr）**——发布形态切回 doctr 的失败语义端到端实证 |

**边界（如实登记，R2/裁决⑥）**：**AC5 判定=PARTIAL**——可验收结论为「运行时+权重随包就绪 + 闭包外等价推理验证」。L3 推理与 L4(b) detect 断言在 frozen 进程**外**执行：frozen 命令面为 M2-IPC1 冻结（core.ping/ListBooks/core.shutdown），**不存在 detect RPC 触发路径**。**NOT_RUN 子项：frozen 进程内 ML import / detect**——待后续 slice「M2-IPC1 命令面扩展 + frozen 进程内 detect 验证」（须 Codex 释放契约范围）。frozen 闭包完整性证据链：L1 启动 + **warn 四文件分类（R1：硬依赖零 missing）** + **构建期闭包断言与 PYZ 清单（R3）** + L2 端到端探测反证。

## AC6 回归与纪律

| 套件 | 结果 | 口径 |
|---|---|---|
| pytest providers（主 venv，PYTHONPATH=src） | **289 passed + 1 failed** | 基数 275+1（既有环境性失败 `test_registry_readiness::test_no_model_runtime_is_installed_in_this_environment`，base 同败）；**+14 为本 Task（r1 review-fix 后口径：11→14）** |
| pytest m2_acceptance | **35 passed** | 基数 35 保持 |
| pytest core | **77 passed** | 基数 77 保持 |
| cargo test（apps/desktop/src-tauri） | **44 passed + 1 ignored, 0 failed** | 零影响（本轮零 Rust 触碰，实测复跑） |
| vitest（frontend） | **31 passed（5 文件）** | 零影响（本轮零前端触碰，实测复跑） |
| `git diff --check f79203eb..HEAD` | **EXIT=0** | — |
| 禁改面专项 diff（apps/**、tauri.conf.json、run_clean_start_e2e.py、ports/**、两个 provider、requirements.txt、experiments/**） | **为空**（tauri/cargo 重写的 gen/schemas、permissions/autogenerated 已 `git checkout --` 还原） | — |

## 已知限制

1. **docTR 权重不进包**（裁决 3）：发布形态切回 doctr = frozen stderr 警告（与 manga 同形状，裁决⑤）+ detect 时 fail-closed PROVIDER_NOT_CONFIGURED+指引（L4(b) typed 断言实证）；源码形态不受影响。运维可在 data root 放 `fast_base-688a8b34.pt` 或设 env 启用。
2. **权重随包冻结**：包内权重随安装包版本走；换权重需重装或走 data root 覆盖（裁决 4 优先级天然支持，无 UI）。
3. **无 UI 权重管理**：权重放置/更新无产品 UI，靠文档化路径约定。
4. **build venv 传递依赖**：python-doctr 把 opencv/scipy/shapely/h5py/onnx/pypdfium2 带进 build venv 与闭包（pip 解析，非手工 pin）；**R9 风险登记**：pypdfium2 版本可能随 doctr 升级漂移（现与主 requirements 同为 5.13.0），ML 版本升级后需复核闭包。mobi 不进 venv（lazy import，warn 面 1 条留痕）。
5. **frozen 进程内无 detect RPC**（AC5 PARTIAL 的结构性原因，裁决⑥）：发布形态 UI 的 detect 链路经 host pipeline 调用，frozen 端到端须待 M2-IPC1 命令面扩展；本 Task 以四层证据链替代，NOT_RUN 子项如实登记。
6. **装配期 stderr 警告语义（裁决⑤，r1 review-fix 产品行为变化）**：包内权重全缺（AV 隔离/半成品安装/`-SkipWeights` 产物）时应用照常启动（一行警告指明候选与放置方式），detect 期 typed fail-closed——「包内权重缺失」不再使整机不可启动。撤销=revert 装配段回 fail-fast。
7. 安装包 438.86 MiB（裁决 1）：撤销方式 = revert spec/requirements-build.txt 改动（build venv 同步删 ML 行）即回 26.63 MiB 轻量包。
