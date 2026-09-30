# M2-PROD-DETECT-2 发布形态验证记录（owner=ZCode，base=f79203eb）

- 机器：本机 win32（全部 CPU 路径）
- 构建/验证 venv：build=`G:/CODEX/New Manga.task-envs/m2ac5-build`（本 Task 扩为 packager+runtime closure）；回归=`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`
- 权重快照：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/`（repo 外，git 不追踪）

## AC1 构建链（ML 栈进 sidecar 闭包）

| 项 | 实测 |
|---|---|
| `requirements-build.txt` | pyinstaller==6.22.3 + PySide6_Essentials==6.11.2 + shiboken6==6.11.2 + **python-doctr==1.1.0 / torch==2.14.0 / torchvision==0.29.0 / transformers==5.17.0 / safetensors==0.8.0**（ML 五行与主 `requirements.txt` 逐字一致；头注释登记裁决 2） |
| `core_sidecar.spec` | EXCLUDED 撤去 torch/torchvision/doctr 三行（pandas/pytest/setuptools/distutils/pip 保持）；**hiddenimports 无需新增**（PyInstaller 经函数内 import 跟踪 + PYZ 归档已覆盖，见下） |
| build venv 更新 | `pip install -r packaging/m2ac5/requirements-build.txt` 全量成功（torch PyPI CPU wheels；doctr 传递依赖带入 opencv/scipy/shapely/h5py/onnx/pypdfium2——见 known limitations） |
| onedir 构建 | 最终 `-Force` 重建 **278 s**（首次试构建 262 s，exit=0） |
| warn 文件 | 29 行、13 个 missing module，**全部为平台条件性/可选噪音**（posix/grp/pwd/_winreg/readline/java 等 Windows 标准面），**0 个 torch/transformers/doctr/tokenizers/safetensors 相关**——「PyInstaller × transformers 动态 import」风险未出现 |
| 闭包 ML 栈核实 | `_internal/`：torch、transformers、tokenizers、safetensors、cv2、scipy、shapely、h5py、PIL 目录在位；`doctr` 为纯 Python 包进 **PYZ 归档**（`pyi-archive_viewer -r -l core_service.exe` 列出 doctr/doctr.models/… 全树；transformers 2320 条目） |
| spec `console=True` | FROZEN 未触碰（M2-RG1 AC2） |

## AC2 权重随包

- `build_sidecar.ps1` 新增 `Copy-MangaWeights`：构建后（含增量短路路径）把三文件从快照复制进 `<bundle>/models/detector/ogkalu-comic-text-and-bubble-detector/`，**逐文件 SHA-256 校验后复制**（脚本内 hardcode 三 pin + 来源注释；缺失/不匹配 throw，不静默跳过）；`-SkipWeights` 开关（默认带权重）。
- onedir 内三文件实测 sha256：`model.safetensors 037930a8…` / `config.json b6d70793…` / `preprocessor_config.json 7e9e2245…` —— 与 `detection_manga.py` pin 一致。
- **NSIS 安装后**（`%TEMP%/m2ac5-cleanstart/install/resources/core-sidecar/models/detector/...`）`model.safetensors` sha256 复核一致（重打包无损）。
- tauri.conf.json 零改动（整目录 resource 机制随包）；`apps/desktop/src-tauri/target/**` 为 gitignored（`apps/desktop/.gitignore` L1），权重永不入库（`git ls-files` 无任何 .safetensors/.pt/models-detector 文件）。
- docTR 权重不进包（裁决 3）。

## AC3 包内回退解析

- `src/bootstrap/core_assembly.py`：新增模块级 `_resolve_detector_weights_path(override, weights_name, db_path, *, bundled_in_release)`，装配段 manga/doctr 两分支改用（manga `bundled_in_release=True`，doctr `False`）。
- 查找顺序（裁决 4）：env override（原样，不探测）> data root 存在性探测 > frozen 包内存在性探测（`sys.frozen` + `Path(sys.executable).parent/models/detector/<name>`）> 默认 data root 路径。
- 语义分叉（裁决 3 × 裁决 4 的自洽组合）：**frozen + manga 全缺 = 安装损坏 → 装配时 fail-closed**（ValueError 列出全部已探测候选）；**frozen + doctr 全缺 = 设计内状态（权重不进包）→ 不 raise**，落默认路径，detect 时 PROVIDER_NOT_CONFIGURED+指引；**非 frozen 全缺 = 零变化**（装配成功、detect 时 NOT_CONFIGURED，与既有 `test_detector_assembly` 锁定行为逐字节一致）。
- 单测 `tests/providers/test_detector_weights_lookup.py`：**11/11 PASS**（monkeypatch `sys.frozen`/`sys.executable` 模拟 onedir，不真打包；矩阵=env 优先/data root 优先/仅包内/manga 全缺 fail-closed 含候选/doctr 全缺不 raise/非 frozen 零变化×3/装配级 wired 冒烟）。
- 既有面：`tests/providers/test_detector_assembly.py + test_detection_manga.py + tests/m2_acceptance/test_provider_fail_closed.py` = **37 passed**（零回归）。

## AC4 GATE 回归（M2-AC5 runner）

| 项 | 实测 |
|---|---|
| onedir | 5,550 文件 / **1,116,380,855 B**（基线 M2-PROD-DETECT-1：161 文件 / 99,308,142 B；+5,389 文件 / +1,017,072,713 B ≈ +970 MiB） |
| NSIS 安装包 | **460,184,382 B（438.9 MiB）**，sha256 `6c765ed3a7decdac…`（基线 27,924,371 B / 26.63 MiB；+432.3 MiB，符合裁决 1「数百 MiB」预期） |
| 构建时长 | PyInstaller onedir 278 s；tauri build（cargo release 68 s + NSIS 压缩 ≈4.5 min）共 ≈6 min |
| GATE | **25/25 PASS，GATE: PASS**（`raw/cleanstart-runner-stdout.log`；CS-E/I/L/P/A/R/Z 全系列；安装后 5,552 文件） |
| M2-AC5 raw | runner 重写 6 文件已 `git checkout --` 还原，专项 diff 为空 |

风险③（torch DLL 进 onedir 后启动变化）由 GATE 实测兜底：production 模式真实窗口 10 s 存活 + sidecar 全 reap，均 PASS。

## AC5 发布形态 detect 探针（`packaged-detect-probe.py`）

对 GATE 刚安装的环境（`%TEMP%/m2ac5-cleanstart/install`）执行，verdict=**PASS**（5/5 场景，结果 JSON 同目录）：

| 层 | 场景 | 实测 |
|---|---|---|
| L1 | PK-L1-frozen-startup-ping | 安装后 core_service.exe（purged PATH，stdio JSON-lines）core.ping → **EXIT=0，status=ready**（装配段 frozen 查找端到端） |
| L2 | PK-L2-counter-proof | 包内 models/ 树临时移走 → frozen 进程**启动即失败 exit=1**，stderr 含 `probed candidates`（装配时 fail-closed 反证包内权重确实被探测）；还原后 ping 恢复 EXIT=0 |
| L3 | PK-L3-real-inference | 合成漫画页（白底+双黑边气泡+文字，PIL）经生产 adapter 全链（validate→frame pixels→processor→model→post_process→三类过滤→冻结合并），weights_dir=**安装后包内权重**：**EXIT=0，text 候选=2（conf 0.94/0.93）**，冷启动 6,542 ms（含 engine 构建），**稳态 299 ms/页（298/302/298）**——与 M2-PROD-DETECT-1 venv 形态 315.6 ms/页同量级。ML 栈版本逐字一致（torch 2.14.0 / torchvision 0.29.0 / transformers 5.17.0 / safetensors 0.8.0 / python-doctr 1.1.0 / tokenizers 0.23.2） |
| L4 | PK-L4-doctr-starts-fail-closed-at-detect | `NEWMANGA_DETECTOR_BACKEND=doctr` 下 frozen 进程正常启动 EXIT=0（裁决 3：依赖就绪、NOT_CONFIGURED 留在 detect 时，装配不崩） |

**边界（如实登记）**：L3 推理在 frozen 进程**外**执行——frozen 命令面为 M2-IPC1 冻结（core.ping/ListBooks/core.shutdown），**不存在 detect RPC 触发路径**（契约释放时假设的「detect 命令」在代码中不存在；core_service.py 不在允许修改范围，本 Task 不扩命令面）。frozen 闭包完整性由三重证据背书：L1 启动（装配段+ML 闭包加载）、warn 文件零 ML missing、PYZ 归档清单（doctr/transformers 全树）。L2 反证提供包内权重解析的端到端因果证明。

## AC6 回归与纪律

| 套件 | 结果 | 口径 |
|---|---|---|
| pytest providers（主 venv，PYTHONPATH=src） | **286 passed + 1 failed** | 基数 275+1（既有环境性失败 `test_registry_readiness::test_no_model_runtime_is_installed_in_this_environment`，断言 venv 无 torch——base 同败）；+11 为本 Task 新增 |
| pytest m2_acceptance | **35 passed** | 基数 35 保持 |
| pytest core | **77 passed** | 基数 77 保持 |
| cargo test（apps/desktop/src-tauri） | **44 passed + 1 ignored, 0 failed** | 零影响 |
| vitest（frontend） | **31 passed（5 文件）** | 零影响 |
| `git diff --check f79203eb..HEAD` | **EXIT=0** | — |
| `git diff --check`（工作区） | **EXIT=0** | — |
| 禁改面专项 diff（apps/**、tauri.conf.json、run_clean_start_e2e.py、ports/**、两个 provider、requirements.txt、experiments/**） | **为空** | `git diff f79203eb --stat -- <paths>` 无输出 |

## 已知限制

1. **docTR 权重不进包**（裁决 3）：发布形态切回 doctr = 依赖就绪（doctr 在 PYZ）但 detect 时 fail-closed PROVIDER_NOT_CONFIGURED+指引；源码形态不受影响。运维可在 data root 放 `fast_base-688a8b34.pt` 或设 env 启用。
2. **权重随包冻结**：包内权重随安装包版本走；换权重需重装或走 data root 覆盖（裁决 4 优先级天然支持，无 UI）。
3. **无 UI 权重管理**：权重放置/更新无产品 UI，靠文档化路径约定。
4. **build venv 传递依赖**：python-doctr 把 opencv-python/scipy/shapely/h5py/onnx/pypdfium2 带进 build venv 与闭包（版本由 pip 解析，非手工 pin）；`pypdfium2` 因此进闭包（主 requirements 本有 5.13.0，实际装 5.13.0 同版本）。mobi 仍不进 venv（warn 面无 missing 留痕，延迟 import 边界同 base）。
5. **frozen 进程内无 detect RPC**（见 AC5 边界）：发布形态 UI 的 detect 链路经 host 的 pipeline 调用，其 frozen 端到端在 M2-IPC1 命令面扩展后才能进程内验证；本 Task 以四层证据链替代。
6. 安装包 438.9 MiB（裁决 1）：撤销方式 = revert spec/requirements-build.txt 改动（build venv 同步删 ML 行）即回 26.63 MiB 轻量包。
