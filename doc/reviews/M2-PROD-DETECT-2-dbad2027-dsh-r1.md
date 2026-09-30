## Verdict
**changes_requested**（存在 2×P1；无 P0，无伪造迹象——L2 traceback 行号 `core_assembly.py:623/791`、GATE 25 条 PASS、NSIS `6c765ed3…`、438.87 MiB、体积/文件数均与落盘证据逐项对得上，证据是真实产物而非编造。但两处 P1 落在「AC 判定口径」与「AC1 核心风险结论的证据载体」上，须闭合后才能作为集成依据。）

## 逐项核对表

| 项 | 结论 | 依据 |
|---|---|---|
| A① 体积如实且与裁决 1 一致 | **成立** | onedir 1,116,380,855B/5,550 文件、NSIS 460,184,382B（438.9 MiB）、基线 99,308,142B/161 与 27,924,371B，均见 release-notes.md:39-41 与 Handoff:19；NSIS 后缀 `6c765ed3a7decdac5e583…`（cleanstart-runner-stdout.log:4）、tauri 构建 438.87 MiB（tauri-build-console.log:292）、cargo 1m08s（:286）三者互证 |
| A② ML 五行逐字一致 + 裁决 2 登记 | **成立** | requirements-build.txt:37-41 与 requirements.txt:16-18,28,29 逐字相同（torch==2.14.0/torchvision==0.29.0/python-doctr==1.1.0/transformers==5.17.0/safetensors==0.8.0）；头注释 8-19 行显式登记裁决 2「minimal packager → packager + runtime closure」 |
| A③ 只带 manga 权重、docTR 切回语义 | **基本成立（带 R4/R6 条件）** | build_sidecar.ps1:52-92 只复制 manga 三文件、无 doctr 复制路径；core_assembly.py:801-812 走 `bundled_in_release=False`；但「发布形态切回 doctr = detect 期 NOT_CONFIGURED」在 frozen 进程内无执行证据（探针 run_l4 只验启动） |
| A④ 查找顺序 | **成立（分叉见 R6）** | core_assembly.py:608-628：override（原样）→ data root `exists()` → frozen `Path(sys.executable).resolve().parent/models/detector/<name>` `exists()` → 默认路径；错误消息 `" | ".join(probed)`（:622-627）列两个候选 |
| B spec/构建链最小性 | **spec 侧成立；warn 面与「零 hiddenimports」的论证不成立** | console=True 未动（core_sidecar.spec:95-100）、EXCLUDED 仅撤 torch/torchvision/doctr 且 pandas/pytest/setuptools/distutils/pip 保持（:52-65）、hiddenimports 仍 `[]`（:76）；但 warn 证据载体错位（R1）、transformers 进闭包机制解释错误（R3）；无「放宽排除掩盖真问题」的痕迹 |
| C 装配解析语义 | **非 frozen 零变化严格成立；两 backend 失败时点分叉未在契约层追认，且错误非 typed** | 非 frozen：唯一路径返回式与旧式 `Path(db_path).resolve().parent/...` 同构（core_assembly.py:608-614,628），`bundle_candidate.exists()` 只在 `sys.frozen` 分支内调用（:615-619）→ 无多余 fs 探测、无 raise，逐字节等价；分叉见 R6，untyped 见 R5 |
| D 测试真实性 | **成立（细节见 R11）** | tests/providers/test_detector_weights_lookup.py 共 11 个测试（:54,:82,:102,:127,:145,:165,:186,:210,:226,:245,:266），frozen 用 `monkeypatch.setattr(sys,"frozen",True)` + `sys.executable` 模拟（:34-38），不真打包；装配级冒烟走生产 `assemble_production_core`（:269-295，且该函数确为 Qt-free，core_service.py:79-88）；无 mock 冒充 |
| E GATE 与探针证据自洽 | **成立（L4 声称除外，见 R4）** | cleanstart-runner-stdout.log 逐条计数 = 25 PASS（CS-E1..3/I1..2/L1..3/P1..3/A1×2,A2..A5/R1..R4/Z1..Z4），`GATE: PASS`（:47），安装后 5,552 文件（:12）；diff 中 `verification/M2-AC5/**` 零出现 → raw 还原声称静态成立；探针 results JSON 5 场景与 l1/l2/l3/l4 日志逐项对齐（results:5-66 vs raw/l1:3-4、l2:2-10、l3-inference.log:2、l4:3-4）；L2 反证逻辑有效（权重在位=EXIT=0、移走后唯一 raise 点在 in-bundle 分支 → 因果成立） |
| F AC5 边界披露的诚实性与定性 | **披露诚实；但 AC5 只能判 PARTIAL** | 见下 F 三条裁定（packaged-detect-probe.py:16-36,369-388；results:67；release-notes:49-58,79） |
| G 权重治理 | **成立（直接 hash dump 缺失，由 L3 传递证明）** | build_sidecar.ps1:70-74 三值与 detection_manga.py:85-93 逐字相同（`037930a8…`/`b6d70793…`/`7e9e2245…`）；权重只存在于 `apps/desktop/src-tauri/target/**`（glob 三处），被 apps/desktop/.gitignore:1 覆盖，diff 无任何权重文件；「安装后一致」由 L3 通过 provider 内部三文件 pin 校验后 EXIT=0 传递成立 |
| H 范围纪律 | **成立** | diff 19 文件全落允许路径（doc/tasks、doc/handoffs、packaging/m2ac5 三件、src/bootstrap/core_assembly.py、tests/**、verification/M2-PROD-DETECT-2/**）；`tauri.conf.json`、`run_clean_start_e2e.py`、`ports/**`、两 provider、`requirements.txt`、`experiments/**`、`verification/M2-AC5/**`、`apps/**` 在 diff 中零出现 |

---

## Findings

**R1 [P1]｜verification/M2-PROD-DETECT-2/release-notes.md:15（配合 raw/build-sidecar-console.log:45/180/317/383）｜AC1「warn 13 missing、0 ML 相关」所依据的 warn 文件不覆盖 ML 闭包，且被已提交日志部分反证。**
机制：spec 四入口共用一个 workpath，PyInstaller 的 `CONF['warnfile']` 固定为 `warn-core_sidecar.txt`（PyInstaller/building/build_main.py:1153、:1064-1090），每次 Analysis 覆盖写同一文件；日志显示四次写入（:45 host_bridge、:180 core_service、:317 acceptance_bridge、:383 catalog_loader），**留存的 29 行/13 项来自最后一次 catalog_loader Analysis（:366 起）**——该闭包不含 ML 栈，故「29 行、13 个 missing、全为 posix/grp/pwd/_winreg/readline/java 类平台面」与本次改动前的归档件 `verification/M2-RG1/raw/rg1-warn-warn-core_sidecar.txt`（29 行、13 项、同名单）逐项吻合；同一文件在 M2-RG1 记为「11 条」、本 Task 记为「13 个」，口径变化亦未说明。而承载 ML 的 core_service Analysis 在已提交 console log 中确有 ML 相关告警：`:119/:256`（`torch.utils.tensorboard` 子模块收集失败 → 必然伴随 `missing module named tensorboard`）、`:156-157/:293-294`（`Hidden import "torchvision.image"/"torchvision._C" not found!`）、`:159/:296`（`scipy.special._cdflib`）。**建议**：按 Analysis 分别归档 warn 文件（或写入前改名），对 ML-bearing Analysis 的 missing 逐条分类（区分 `missing module`、hook 的 hidden-import 软告警、编译扩展/DLL），把「风险未出现、hiddenimports 无需新增」的结论改挂在该文件上；在补证前不要把「0 ML 相关」作为 AC1 PASS 依据。

**R2 [P1]｜doc/tasks/M2-PROD-DETECT-2.md:49（配合 packaged-detect-probe.py:16-36,174-228,369-388）｜AC5 勾选 PASS 的口径高于证据强度：「发布形态 detect 端到端可用」既未验证、在当前命令面下也不可达。**
frozen 命令面确认只有 `core.ping`/`ListBooks`/`core.shutdown`（core_service.py:266/278/324），无 detect RPC；manga provider 的 torch/transformers 是首次 detect 才 import（detection_manga.py:182-184、:275、:286），因此 **L1 启动 EXIT=0 不触及任何 ML import**；L3 在 build venv 内以 src 代码 + 安装后包内权重推理（probe:174-228、320-366），frozen 进程从未加载 torch。故三重背书（L1 启动 + warn 零 ML missing + PYZ 清单）至多支撑「闭包内已**收集** ML 运行时」，不能支撑「发布形态 detect 端到端可用」；更弱的是 warn 面本身已被 R1 削弱，且 transformers 模型类经 `_LazyModule` 动态解析，`RTDetrImageProcessor/RTDetrV2ForObjectDetection` 所属子模块是否被收集无任何证据。**建议**：AC5 改判 **PARTIAL**（子项 NOT_RUN：frozen 进程内 ML import/detect），并把「进程内 detect 验证」登记为依赖 M2-IPC1 命令面扩展的后续 slice；若 Codex 认定 AC5 原意仅为「安装后环境内跑一次真实推理」，须在 Task/Handoff 显式写明该解释，避免集成方把「运行时已随包」误读为「发布形态 detect 已验收」。

**R3 [P2]｜packaging/m2ac5/core_sidecar.spec:27-33、:76（配合 Handoff:16、release-notes:12）｜「doctr/transformers 经函数内 import 跟踪进 PYZ」的机制解释不成立：transformers 进闭包是 torch 内部可选 import 的偶然结果。**
静态核查：src 内可被 modulegraph 跟踪的 ML import 只有 `import torch`（src/infrastructure/devices/manager.py:202）与 `from doctr.models import detection_predictor`（detection_docstr… detection_doctr.py:226）；transformers 在 src 内只以字符串形式出现（detection_manga.py:286 经 `_lazy_import`→`importlib.import_module(module_name)`，:429-431，modulegraph 不解析 CALL）。全 site-packages 穷举后，除 transformers 自身外唯一静态 import transformers 的位置是 torch 的两处函数内 import：`torch/onnx/_internal/exporter/_input_observer.py:873`、`torch/testing/_internal/common_distributed.py:281`（这正是 `hook-transformers` 被执行、transformers 进入 graph 的来源）。后果：一旦 torch/依赖版本变化丢掉这两处可选 import，闭包会**静默**失去 transformers（构建仍绿），发布形态 detect 在 MLA 栈上退化为 `PROVIDER_DEPENDENCY_MISSING`；而它是本 Task 的核心承诺。**建议**：spec 允许的范围内显式 `hiddenimports=["transformers"]`（必要时含 `transformers.models.rt_detr`），或加构建期闭包断言（PYZ 清单包含 transformers 与 rt_detr），并修正文档中的机制表述。

**R4 [P2]｜verification/M2-PROD-DETECT-2/packaged-detect-probe.py:30-36 vs :369-388｜L4 docstring 声称「+ venv 侧 detect 断言 typed PROVIDER_NOT_CONFIGURED」，实现里没有任何 detect。**
`run_l4` 只做 frozen 启动 ping 判定；Task:49 的 doctr 子句（切回 fail-closed NOT_CONFIGURED）在发布形态零执行证据（现有覆盖仅为解析路径单测 tests:186-202 与非 frozen 的 m2_acceptance 用例）。**建议**：补一处 doctr detect 断言（可复用 L3 driver 换 backend），或把「仅启动验证、detect 语义由单测覆盖」写入 docstring/Task 措辞，不保留越界的声称。

**R5 [P2]｜src/bootstrap/core_assembly.py:621-627（证据 raw/l2-frozen-weights-absent.log:4-11）｜装配期 fail-closed 用裸 `ValueError`（非 typed），且「权重目录缺失=整个 core_service 启动失败」这一产品级后果未登记。**
AC3 字面要求「全缺→typed 错误含候选列表」，仓内 typed 错误在 ports/providers/errors（如 `ProviderNotConfigured`），此处为未捕获裸异常并触发 `[PYI-…] Failed to execute script`（l2:11）。爆炸半径是整机：包内 `models/` 缺失（AV 隔离、半成品安装、误用 `-SkipWeights` 产物）会让书架/阅读等一切功能都不可启动，与 M2-PROD-DETECT-1/M2-AC3「装配不崩、detect 期 typed fail-closed」的既有承诺方向相反（裁决 4 允许 fail-closed，但后果未列「已知限制」）。**建议**：至少登记该后果；更优改为 typed provider 错误，并评估把 manga 的装配期 raise 降级为 detect 期 NOT_CONFIGURED（与 doctr 对齐）是否更符合产品纪律。

**R6 [P2]｜src/bootstrap/core_assembly.py:618-628、:791-812 vs doc/tasks/M2-PROD-DETECT-2.md:40（裁决 4）与 :47（AC3「两 backend 同样语义」）｜`bundled_in_release` 语义分叉属未追认的裁决级分叉。**
裁决 4 原文给的是单一末级回退「默认 data root 路径（fail-closed 报错列候选）」，裁决 3 又要求 doctr 保持 detect 期 NOT_CONFIGURED；实现选择「权归属决定缺失语义」：manga 冻结全缺=装配期 raise，doctr=不 raise（tests:165-202）。**裁定：接受该分叉**——理由成立（doctr 不 raise 是裁决 3 的必要条件，manga 全缺确实等于安装损坏），release-notes:31 与 Handoff:64② 亦已披露待审议；但它使 AC3「同样语义」字面落空，且只在 verification/Handoff 层登记、契约与裁决登记未追认。**建议**：Codex 在裁决登记/Task 中显式追认，AC3 改为「同一查找顺序 + 按 bundled 语义分叉」；同时修 build_sidecar.ps1:35-37 的 `-SkipWeights` 注释（现写「fails closed NOT_CONFIGURED at run time」，实际 manga 冻结态是装配期崩溃）。

**R7 [P2]｜raw/build-sidecar-console.log:1,:411 vs Handoff:34｜构件与 delivery_head 无绑定，Handoff「被测 commit @1cf731ca」与日志 `HEAD=44e70f66` 不一致。**
构建发生在 claim commit 的脏工作树（日志两处记录 `HEAD=44e70f66…`，即实现尚未提交），而交付头是 1cf731ca。AC1/AC4 的产物无法字节级归属到被审 commit。**建议**：Handoff/验收表按实际写「构建时 HEAD=44e70f66（工作树含未提交实现）、交付头 1cf731ca」，或重跑构建绑定 delivery_head；同类绑定缺失（NSIS sha256 ↔ commit）在 NOT_VERIFIED 一并列出。

**R8 [P3]｜packaging/m2ac5/README.md:18-30、:92｜允许面内的构建文档未同步，现与交付自相矛盾。**
仍写固定版本仅 pyinstaller/PySide6/shiboken6、「pypdfium2/mobi **不进**构建 venv」、安装包「26.62 MiB」，且 §2 步骤未提权重复制与 `-SkipWeights`。**建议**：更新或显式登记不更新理由（该文件在允许范围「如需」内）。

**R9 [P3]｜packaging/m2ac5/requirements-build.txt:30-33 vs release-notes.md:78｜同一交付内两处口径冲突。**
文件注释称 pypdfium2 故意不进 build venv；已知限制 4 说 pypdfium2 随 doctr 传递依赖进入闭包（版本同 5.13.0）。**建议**：改为「mobi 不进；pypdfium2 由 doctr 传递依赖带入」，并注明传递依赖不手工 pin 的风险。

**R10 [P4]｜packaging/m2ac5/build_sidecar.ps1:57｜权重源硬编码本机绝对路径，可复现性受限。**
新鲜 checkout/其他机器必须依赖 repo 外快照（Handoff:63 已披露）。**建议**：加 `-WeightsSource` 参数（默认现值），并在注释中说明与 pin 的一致性约束。

**R11 [P4]｜tests/providers/test_detector_weights_lookup.py:65,:235,:284-294｜三处判别力/耦合瑕疵（不影响 11/11 计数与真实性）。**
:65 设了 `NEWMANGA_DETECTOR_WEIGHTS` 却把 override 作为参数传入，未覆盖装配段的 env 读取路径；:235-242 构造 `stray` 但从不落盘，断言偏弱；:284-294 靠 `__closure__` 反射取 detector，耦合 handler 实现。**建议**：补一条「仅设 env、不传参」的装配级用例；`stray` 落盘后再断言。

**R12 [P4]｜verification/M2-PROD-DETECT-2/packaged-detect-probe.py:369-388 + results:58-65｜场景命名与层数表述易误读。**
`PK-L4-doctr-starts-fail-closed-at-detect` 实际只验「启动」；「5/5」=L1/L2/L2-recovery/L3/L4 四层五场景，与「四层证据」并列时口径含混。**建议**：场景改名（如 `...-starts-without-assembly-error`）、在 Task/Handoff 明示 5 = 4 层 5 场景。

---

## NOT_VERIFIED（静态不可复现，须集成方运行时复跑）
1. **pytest 三套件**：providers `286+1`（含新增 11）、m2_acceptance `35`、core `77`；既有环境性失败 `test_registry_readiness::test_no_model_runtime_is_installed_in_this_environment` 的「既有」属性需对 base 复现（release-notes:64、Handoff:38-44）。
2. **GATE 25/25**：我静态计数与 CS 系列逐条对齐（cleanstart-runner-stdout.log:3-43），但 runner 实跑、NSIS `6c765ed3…` 与安装目录 5,552 文件需复跑；`run_clean_start_e2e.py` 未改已由 diff 静态确认。
3. **探针 5/5 与 L3 真实推理**（EXIT=0、候选=2、299ms/页）：需 build venv + 安装目录复跑；我仅完成 results↔raw 日志↔脚本逻辑的对齐。
4. **warn 文件真实内容与 ML 分类**（未入库，`target/pyinstaller-work/` 为 gitignored；M2-RG1 有归档先例）：须按 Analysis 分别导出并逐条分类（R1）。
5. **PYZ 归档清单**（doctr 全树、transformers 2320 条目）：无入库日志，须 `pyi-archive_viewer -r -l core_service.exe` 复跑，并额外确认 `transformers.models.rt_detr` 子模块在列（R2/R3）。
6. **权重三文件在 onedir 与 NSIS 安装后的 sha256 dump**：无直接证据文件；「安装后与 pin 一致」目前由 L3 经 provider 内部 pin 校验通过而传递成立，建议补一次显式 `Get-FileHash` 记录。
7. **`git diff --check` 双 EXIT=0、禁改面专项 diff 空、权重零 tracked、`.gitignore` 面**：我以 diff 文件清单与 glob 静态验证到「零出现/仅 target 下有权重」，git 层结论须执行确认。
8. **frozen 进程内 ML import / transformers LazyModule 子模块解析 / 进程内 detect**：当前命令面（core_service.py:266/278/324）结构性不可达，须待 M2-IPC1 命令面扩展后另立验证。

---

## 集成方闭合清单（按优先级）
- **P1-1（R1）**：按 Analysis 分别归档 warn 文件并分类；把 AC1「0 ML 相关」结论重建在 core_service Analysis 的正确载体上；同步 release-notes/Task 措辞。
- **P1-2（R2）**：AC5 改判 **PARTIAL**，列明 NOT_RUN 子项（frozen 内 ML import/detect）与后续 slice 依赖；若维持 PASS，须由 Codex 以契约解释落字（不得由 Owner 单方口径）。
- **P2-1（R3）**：spec 显式 hiddenimports 或构建期闭包断言（含 `transformers.models.rt_detr`）；修正 Handoff/release-notes 的机制句。
- **P2-2（R4）**：补 doctr detect 断言，或下调 L4 docstring/AC5 的 doctr 表述。
- **P2-3（R5/R6）**：裁决层追认 `bundled_in_release` 分叉 + 登记「冻结形态包内权重缺失=启动失败」；修 `-SkipWeights` 注释；评估 ValueError→typed 错误。
- **P2-4（R7）**：Handoff/验收表如实写构建时 HEAD=44e70f66（或重跑绑定 1cf731ca）。
- **P3**：README（R8）、requirements-build.txt 注释（R9）；**P4**：R10-R12 可后置。
- 复核顺序建议：上表 NOT_VERIFIED 1→2→3→4/5→6→7。

## 推荐下一步
把 R1（warn 证据载体）与 R2（AC5 改判 PARTIAL）作为两条硬条件转交 Owner 返修，P2-1/R3 的显式 hiddenimports 一并随返修落地；返修后再由本 Reviewer 以相同锚（1cf731ca/80f7a0cb + 新增返修 tip）做 r2 定点复审，闭合后交 Codex 集成。
