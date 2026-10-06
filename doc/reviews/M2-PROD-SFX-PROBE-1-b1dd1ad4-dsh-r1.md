# M2-PROD-SFX-PROBE-1 非作者独立 Review（DeepSeek Harness，只读静态）

## 1. 终判

**approved_with_conditions**（0×P0 / 1×P1 / 3×P2 / 5×P3 / 若干 P4）

- 交付主体成立：第五 frozen 入口 `sfx_detect_probe.exe` 的 additive 选型、冻结粒度核实、GATE 25/25、回归 1835=1823+12、安装后环境 frozen 进程内 DML 真实推理（EXIT=0/候选=1/三键 dml·dml·null）均为**真实、可复算、与 raw 证据互证**，无 P0、无功能面阻塞。
- 但证据文档中有一处**可证伪的定量错误陈述**（"v2b 锚点逐位一致"，P1）：实测 `0.9046692252159119` 与锚点 `0.9046694040298462` 并不逐位相等（Δ≈1.79e-7），且构建面存在一处**被 raw 证据直接推翻的技术声明**（"探针 entry 不拉 torch/transformers"，P2）。
- 上述两项均为**局部文本/断言面**可闭合（返回面在 Task 允许路径内：`doc/tasks/M2-PROD-SFX-PROBE-1.md`、`verification/M2-PROD-SFX-PROBE-1/**`、`doc/handoffs/**`、`packaging/m2ac5/**`），不要求重跑构建/探针，故判 approved_with_conditions 而非 changes_requested。
- 返修条件：**C1**（锚点比较更正，P1）、**C2**（探针闭合面归属更正 + 增量归属/更优替代取舍登记，P2-1/P2-2）、**C3**（runner 判定面补 `frozen=true` 与权重 pin 断言，P2-3）、**C4**（文档/元数据顺笔：README 五入口、`base_commit`、range `diff --check` 实证、GATE 场景枚举、results JSON 可追溯字段）。

方法与边界：全程只读，未执行任何 shell/git/构建命令，未写任何文件。独立证据源=worktree reflog（`G:\CODEX\New Manga\.git\worktrees\M2-PROD-SFX-PROBE-1-zcode\logs\HEAD`，只读）+ 仓库内源文件 + 交付 raw 证据；所有关键数字均由 raw 逐行重算，不采信文档转述。

---

## 2. 分级发现

### P0（阻塞集成）
无。

### P1（必须返修）

**P1-1 「与 v2b 锚点逐位一致」为错误陈述（3 处）**
- 证据：锚点 `experiments/M2-SFX-T4-SWITCH/v2b-k07-r123-anchor.json:14` = `0.9046694040298462`；探针实测 `verification/M2-PROD-SFX-PROBE-1/raw/sp-l2-real-page.log:4` 与 `packaged-sfx-detect-probe-results.json:44` = `0.9046692252159119`。二者差 `1.788e-7`，**不是逐位一致**；且该 Task 自己的回归测试只用 `abs=1e-3` 容差比较（`tests/providers/test_detection_sfx.py:975` `best.confidence == pytest.approx(expected[0]["conf"], abs=1e-3)`），并不主张位级相等。反例先例：M2-SFX-T4-SWITCH 的冻结探针 `best_sfx_conf=0.9046694040298462`（`verification/M2-SFX-T4-SWITCH/raw/frozen-v2b-probe-results.json:17`）与锚点**确实**逐位相等——该处 CPU 形态，本 Task 为 DML 形态，末位浮点漂移是 GPU-EP-1 已登记的既有事实（`doc/tasks/M2-SFX-GPU-EP-1.md:7,71`：`max|Δconf|≤2e-06`，本观测 1.79e-7 在窗口内）。
- 位置：`doc/tasks/M2-PROD-SFX-PROBE-1.md:73`、`verification/M2-PROD-SFX-PROBE-1/deploy-record.md:34`、`doc/handoffs/M2-PROD-SFX-PROBE-1-zcode-20261004.md:14`（`:32` 为弱化版本）。
- 影响：把 DML↔CPU 的**有限漂移**错报为**位级可复现**，会污染后续 STATUS/Release Gate 的确定性口径；AC2 实质证据（候选>0、三键、权重 pin）不受影响。

### P2（应返修）

**P2-1 spec/设计登记称探针 entry "不拉 torch/transformers"与构建事实相反，且 +64.76 MiB 的归属被误标**
- 证据（构建分析面归属确凿）：`verification/M2-PROD-SFX-PROBE-1/raw/build-sidecar.log:440` 起为 `Analyzing .../entry_sfx_detect_probe.py` 的分析区间，其中 `:456` `hook-cv2`、`:459` `hook-torch`、`:480` `hook-torchvision`、`:501` `hook-transformers`、`:522` torch DLL 搜索目录，随后 `:527-529` 建 `PYZ-04`、`:532` `sfx_detect_probe.pkg`；归档警告文件 `apps/.../pyinstaller-work/core_sidecar/warn-archive/warn-sfx_detect_probe.txt` 满含 `torch.*`/`transformers.*`/`doctr.*`/`scipy.*`（如 `:22,40,403,446`），而 `warn-catalog_loader.txt` 同类搜索**零命中**（证明不是"所有入口都这样"）。
- 机理（可解释，非随机）：`src/bootstrap/sfx_detect_probe.py:65-70` → `detection_sfx` → `detection_manga.py:82` → `detection_doctr`，后者函数体内存在**静态** `from doctr.models import detection_predictor`（`src/infrastructure/providers/detection_doctr.py:226`），modulegraph 会跟进函数体内的 import，于是 doctr→torch→（torch 内部可选 import 拉入）transformers 整链进入该 entry 的 PYZ。
- 被推翻的声明：`packaging/m2ac5/core_sidecar.spec:77-83`（"It needs ONLY the onnxruntime stack (no torch/transformers)"）、`doc/tasks/M2-PROD-SFX-PROBE-1.md:57`（"**不**拉 torch/transformers"）、`verification/.../deploy-record.md:50`（"8455 modules onnxruntime 面"、"onnxruntime 目录与基线一致（无 ML 闭包膨胀）"）。
- 事实口径：8455 ≈ core_service 的 8584 pure modules，`sfx_detect_probe.exe` 67,901,644 B ≈ core_service 68.5 MB（`deploy-record.md:50`），说明增量是**第二份 torch/transformers/doctr 闭包**，而非 onnxruntime 面；"onnxruntime 目录不变"只说明共享 `_internal` 未膨胀，不能推出 PYZ 未膨胀。
- 影响：spec 是全仓**闭包完整性**的唯一权威文件，其注释为假会误导后续"瘦身/断言加固"判断；同时掩盖了真实成本结构。

**P2-2 更优替代（零增量方案）未做取舍披露**
- 文档只给出"回退=revert spec 第五行"（`deploy-record.md:50`）与"如需收窄=瘦身探针 import 面/共享 PYZ 方案，属新 slice 裁量"（`doc/handoffs/...:67`），**未评估**：在既有 `core_service.exe` 上加一次性 CLI 模式（如 `core_service.exe --sfx-detect-probe`）——按本 Task 自己确立的冻结口径（AC1①：冻结面是 stdio 命令面，非 CLI 入口参数，`doc/tasks/M2-PROD-SFX-PROBE-1.md:45-46`），该方案同为"非 IPC 命令面"路径且**新增 0 B**（复用既有 PYZ），也能满足"frozen 进程内跑一次生产 provider"。
- 影响：+64.72 MiB 的接受缺少"成本-替代"论证；评审要点 D 所指的取舍披露不完整。

**P2-3 runner 未断言"frozen 进程内"这一核心属性；SP-L2 也未断言权重 pin**
- `verification/M2-PROD-SFX-PROBE-1/packaged-sfx-detect-probe.py`：SP-L1 判据（`:291-298`）与 SP-L2 判据（`:347-355`）均**不检查** `payload["python"]["frozen"] is True`（该字段在 JSON 里已记录，见 `raw/sp-l2-real-page.log:4` `"frozen": true`）；SP-L2 亦无权重 sha 断言（仅 SP-L1 `:282,295` 有 `weights_sha256_matches_pin`）。即 AC2 的核心命题"frozen 进程内"目前是**记录面**而非**判定面**，一旦探针被误指向非 frozen 形态（或 json 字段回归消失），SP-L2 仍会 PASS。
- 影响：断言面窄于声明面（本仓库对同类问题在 M2-SFX-T4-SWITCH 评审中曾明确要求"把 `bool(sfx_labels)` 并入判据"），建议补两行判据。

### P3（应返修）

**P3-1 `packaging/m2ac5/README.md` §3 仍写"四个 frozen 入口"且表内无第五入口**
- `packaging/m2ac5/README.md:117-127`（标题"四个 frozen 入口"、表仅 4 行；另 `:35` "其余 sidecar 入口（host_bridge / core_service / catalog_loader）"）。该文件在 Task 允许面（`packaging/m2ac5/**`）内，且正是 AC1 引用的 catalog_loader 先例出处（`:127`）。Task 仅登记了 `main.rs:378-379` 过时注释（`:78`、`deploy-record.md:14`），**未登记 README** 同类过时。

**P3-2 `deploy-record.md:79` 对 SP-L2 断言面的描述与代码不符**
- §7 称"SP-L2 断言只要求**三键在场**+候选>0"；代码 SP-L2 只检查 `device`/`sfx_ep` 非空（`packaged-sfx-detect-probe.py:347-355`），**没有** `sfx_ep_fallback` 键在场检查（SP-L1 `:266-271` 才有）。探针本体恒写三键（`src/bootstrap/sfx_detect_probe.py:287-289`），故实际风险低，但文字与代码不一致。

**P3-3 AC4 的 `git diff --check` 证据口径空转 + trailing whitespace 豁免叙述与交付内容矛盾**
- `deploy-record.md:55` 引"`git diff --check` EXIT=0（提交完成后工作区口径）"——提交后工作区无未暂存改动，该命令恒 EXIT=0，**不构成对交付内容的检查**；同时该段声明"全链 `git diff --check d298ecd0..HEAD` 对证据 log 报出的 trailing whitespace…"沿 GPU-EP-1 先例豁免。但我在本 Task 全部变更文件上以 `[ \t]+\r?$` 检索（`src/bootstrap/sfx_detect_probe.py`、`tests/core/test_sfx_detect_probe.py`、`packaging/m2ac5/**`、`verification/M2-PROD-SFX-PROBE-1/**` 含 `raw/**`、Task/Handoff 文档）**零命中**；对照组 GPU-EP-1 raw 有两文件 16 处命中（方法有效性已验证）。即：**本 Task 的 range check 本应干净**，"豁免"叙述与实际不符（更可能是从先例复制的模板句）。
- 另注：M2-AC5 对同类问题的自有口径是**规范化证据日志以满足整树 `diff --check` EXIT=0 硬 gate**（`verification/M2-AC5/raw/README.md:11-14`），与"豁免"是两套口径；且先例的"22 处"数字在仓库内无 raw 可核（仅 `doc/tasks/M2-SFX-GPU-EP-1.md:61` 提及 `4fa38540` 为 docs 提交本身）。
- 建议：重跑并原样落盘 `git diff --check d298ecd0..HEAD` 的真实输出（预期为空），删掉误导性豁免段。

**P3-4 Task frontmatter `base_commit` 与实际不符**
- `doc/tasks/M2-PROD-SFX-PROBE-1.md:11` = `72807d30`；实际 worktree base = `d298ecd0`（reflog 首行 `G:\CODEX\New Manga\.git\worktrees\M2-PROD-SFX-PROBE-1-zcode\logs\HEAD:1-3`；`doc/handoffs/...:5`、`deploy-record.md:4` 亦为 `d298ecd0`）。`72807d30` 是 STATUS 记录的 2026-10-04 释放基点（`doc/STATUS.md:14`），属"释放时预记 vs 实际检出点"漂移，应更正并注明。

**P3-5 证据可追溯性缺口（results JSON）**
- `packaged-sfx-detect-probe-results.json` 无 installer sha256 / 构建 HEAD；`build_venv_note` 为空（`:5`，runner 有 `--build-venv-note` 通道，Handoff 又记载 `m2ac5-build` venv+pyinstaller 6.22.3），因此探针证据无法**程序化**绑定到被测安装包（该绑定只存在于 `raw/m2ac5-gate-artifacts-thisrun/cleanstart-gate.json:4` 与 `raw/bundle-sizes.log:2`）。
- 另：JSON 的 `page.sha256 = b3b7c4a6…` 是**解码后 rgb24 缓冲**的哈希（`src/bootstrap/sfx_detect_probe.py:265`），与锚点的**文件级** `frame_sha256 = 28dab503…`（`experiments/M2-SFX-T4-SWITCH/v2b-k07-r123-anchor.json:9`，`extract_v2b_anchor.py:99` `sha256_file(FRAME)`）不同域；`deploy-record.md:31` 的"页 sha256 b3b7c4a6…"未标注域，读者与锚点对账会直接看到"不一致"。建议标注为像素缓冲哈希并同时记录文件哈希。

### P4（备注）

- P4-1 `apps/desktop/src-tauri/src/main.rs:374-379` 注释仍列四入口，且 `run_clean_start_e2e.py:805-807` CS-Z3 进程残留名单不含 `sfx_detect_probe.exe`（本 Task GATE 不启动第五入口，故无影响；若未来场景启动则须补名单）。main.rs 过时注释已如实登记（`deploy-record.md:14`），保持 src-tauri 零 diff 的处理合理。
- P4-2 `raw/probe-runner.log:5` 显示 `cleared env names (0): []`——"全 `NEWMANGA_*` 清除"实际是"宿主本就无该类变量"，证据强度更高但表述易被误读为"曾存在并被剔除"，建议改为"零 NEWMANGA_*/M2RC1_* 干预（clear 数=0）"。
- P4-3 SP-L3 探针信封发 `minor: 0`（`packaged-sfx-detect-probe.py:169-178`），而冻结面为 1.3（`raw/sp-l3-core-service-ping.log:3`）；服务端只校验 major（`src/bootstrap/core_service.py:765-780`）故可用，但作为"既有命令面冒烟"用 `minor:3` 更贴冻结形态。
- P4-4 `deploy-record.md:40` 对 25/25 的场景枚举写作 "E1-E3/I1-I2/L1-L3/P1-P3/A1-A3/Z1-Z4"（按此计仅 18），漏了实际存在的 CS-A4/CS-A5（`raw/gate-clean-start-e2e.log:30-31` 与 `thisrun/cleanstart-gate.json:188,204`）；25/25 判定本身正确。
- P4-5 runner 自带一份 `SFX_WEIGHTS_SHA256` 常量（`packaged-sfx-detect-probe.py:79-81`），未改用探针 JSON 的 `weights.expected_sha256`（`raw/sp-l2-real-page.log:4`）；作为独立 pin 可接受（失效即 FAIL，方向安全），但 pin 迁移时需两处同步。
- P4-6 `deploy-record.md:36` 的"dev 冒烟 n=1/conf=0.9047/793ms 与 frozen 互证"无 raw 落盘（仅实现 commit message），建议补日志或删该对账句。
- P4-7 spec 的探针断言以 `SFX_PROBE_ENTRY` 字符串为键（`core_sidecar.spec:89,294-295`），若 ENTRIES 行被改名而常量未改，断言会静默不执行；`build_sidecar.ps1:209-213` 的名称 sanity gate 是有效兜底，可接受。
- P4-8 SP-L2 的"真实页身份"仅靠路径锚定（`raw/sp-l2-real-page.log:1,4`），建议并记文件 sha256（同 P3-5）。

---

## 3. AC1–AC5 逐条判定

| AC | 判定 | 一句话理由 |
|---|---|---|
| **AC1 命令面扩展** | **PASS** | additive 判定链成立：M2-C1 冻结面=React↔Tauri↔Core transport-neutral 消息边界（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:17`、§11 `:381` "Runtime serialization library, Tauri command names…NOT_IN_SCOPE"），M2-IPC1 冻结面=`core_service.exe` stdio 命令面（`src/bootstrap/core_service.py:120` `PROTOCOL_MINOR=3`，全文无 `sfx_detect_probe` 命令/分发表改动），catalog_loader"独立 frozen 入口、产品命令面零扩展"先例有文可依（`packaging/m2ac5/README.md:127`），GATE CS-I1 确为 at-least 语义（`run_clean_start_e2e.py:66-71`、`:231-234` 仅按名单 `is_file()`），第五入口不触碰任何 25 场景断言；AC1③ 不适用（无 rev bump、`doc/contracts` 无 probe 字样）。唯一保留：静态会话无法执行 git 复核 `contracts/**`/`src-tauri/**` 零 diff（且仓内无 `contracts/` 树），该结论由源码面+reflog+集成 Gate 承接。 |
| **AC2 frozen 进程内真实运行** | **PASS（判定面成立，附 C1/C3）** | 安装后环境（GATE 安装态、purged PATH、零 `NEWMANGA_*` 干预）实测：EXIT=0、候选=1、`elapsed_ms=696`、三键 `device=dml`/`sfx_ep=dml`/`sfx_ep_fallback=null`，`weights.resolved_from=bundle_probe` 且 `sha256=944e8114…`=生产 pin（`raw/sp-l2-real-page.log:4`；`packaged-sfx-detect-probe-results.json:38-53`），并与 SP-L1 合成页（候选=4、1846ms、同三键）互证；"候选=0 不得静默 PASS"**真在 runner 代码里**（`:350` `(result.get("n_candidates") or 0) > 0` → 候选=0 即 FAIL；SP-L1 候选=0 则落 `synthetic_zero_candidates_note` 记录面，符合设计登记）。扣分项：锚点比较措辞错误（P1-1）、`frozen` 与权重 pin 未进判据（P2-3）。 |
| **AC3 既有面零破坏** | **PASS（附 C2/C4）** | GATE `run_clean_start_e2e.py` PASS 25/25 EXIT=0（`raw/gate-clean-start-e2e.log:47`；场景 id 逐条重算=25，含 CS-A4/A5，`thisrun/cleanstart-gate.json:12` verdict=PASS），installer sha256 `3ffa03f5…` 在 GATE CS-E2（`gate-clean-start-e2e.log:4`）、`bundle-sizes.log:2`、`deploy-record.md:46` 三处一致并与本 Task 包相符；M2-AC5 落点按 GPU-EP-1 先例（`verification/M2-SFX-GPU-EP-1/deploy-record.md:284-293`）快照 6 文件+逐文件 sha256（`raw/m2ac5-gate-artifacts/`，12 条目）后还原——现 `verification/M2-AC5/raw/cleanstart-gate.json:4` 仍为 M2-AC5 时代 `5410e29e…`，与快照一致，历史证据未被跨 Task 改写；包体积 Δ 计算正确（580,540,551−512,675,022=+67,865,529 B=+64.72 MiB，`bundle-sizes.log` vs `verification/M2-SFX-GPU-EP-1/raw/bundle-sizes.log:8`）。扣分项：增量归属误标（P2-1）、更优替代未披露（P2-2）、豁免叙述不实（P3-3）。 |
| **AC4 回归与纪律** | **PASS** | 全量 `1835 passed + 1 skipped + 1 failed`（`raw/pytest-full-regression.log:399`），唯一失败为既有 `tests/m2_test_assets/test_catalog.py::test_manifest_has_unique_cases_and_exact_taxonomy`（`:381-390`，`assert 122 == 97`）；基线 `1823` 有独立出处=GPU-EP-1 末轮 `1 failed, 1823 passed, 1 skipped`（`verification/M2-SFX-GPU-EP-1/raw/pytest-full-regression-r2run.log:399`，其 Iteration Gate 亦按 1823 记账），新增 12=文件内恰好 12 个 `def test_`（`tests/core/test_sfx_detect_probe.py`），**1835=1823+12 逐项吻合**；权重/页图零入库（`src/tests/packaging/verification/doc/experiments` 下 `*.onnx/*.png` 全树零命中）；探针/runner 未进 GATE 场景集（`SIDECAR_EXES` 仍 4 项）。扣分项：`diff --check` 证据口径空转与豁免叙述不实（P3-3）、`base_commit` 元数据不符（P3-4）。 |
| **AC5 文档** | **PARTIAL** | 载体齐全且范围正确：results JSON+`raw/**`、deploy-record、Task 回填、Handoff 均在位；**PROD-DETECT-2 AC5 NOT_RUN 的 sfx slice 闭合声明**与历史原文逐字对应（`deploy-record.md:63` 引用 `verification/M2-PROD-DETECT-2/packaged-detect-probe-results.json:83` 的 boundary_note），并明确"manga slice 属另一缺口未覆盖、历史文件不改写"——诚实登记达标。判 PARTIAL 的唯一原因：同一批 AC5 文档内含 P1-1 的**可证伪错误陈述**（3 处"逐位一致"）与 P3-1/P3-4 的过时/不一致登记，须随 C1/C4 更正后再封存。 |

---

## 4. 残留风险与集成建议

**4.1 闭合语义的精确边界（最重要，建议写进 STATUS/集成记录）**
- 本 Task 证明的是：**随包发布的 frozen PyInstaller 入口进程内**（同一 onedir、同一 in-bundle v2b 权重、同一 `SfxDetectionProvider` 类，`src/bootstrap/core_assembly.py:976` 装配同一类）能跑通生产 detect 并给出三键 — 这是 NOT_RUN 缺口"frozen 闭包内 ML import/detect 结构性不可达"的**闭包面**闭合。
- 它**不是**"产品 sidecar `core_service.exe` 进程内 detect 可达"的闭合，也不是 manga slice 的闭合；`M2-PROD-DETECT-2` 历史 boundary_note 的字面条件是"until the frozen command surface extends"，而本 Task 刻意**未**扩命令面（改用独立入口先例，`deploy-record.md:63` 已如实说明路径差异）。GPU-EP-1 当时的登记结论是"需命令面扩展"（`verification/M2-SFX-GPU-EP-1/deploy-record.md:299-302`）。
- 建议：由 Codex 在集成轮以**明确措辞**登记"依据 catalog_loader 先例，NOT_RUN 的 sfx slice 以独立 frozen 入口（非命令面扩展）闭合；core_service 进程内 detect 与 manga slice 维持 NOT_RUN"，避免后续把"命令面扩展"当作既定收敛条件。

**4.2 数值确定性口径**
DML 与 CPU 的末位漂移是既有事实（本观测 Δconf≈1.79e-7 ≤ GPU-EP-1 的 2e-6 门）。修正 C1 时应把"逐位一致"替换为："与 v2b 锚点 `0.9046694040298462` 同源同页、差 1.79e-7，落在 GPU-EP-1 登记的 GPU↔CPU 漂移窗口（≤2e-06）内；回归测试容差 `abs=1e-3`"。**不要**把"位级可复现"写进任何未来证据。

**4.3 包体积决策**
+64.72 MiB 的数字登记诚实，但驱动因素是**第二份 torch/transformers/doctr 闭包**（P2-1），不是 onnxruntime。建议在 C2 里显式给出三选一并记录选择理由：(a) 接受（当前）；(b) 一次性 CLI 模式挂在既有 `core_service.exe` 上（0 B，需论证不触碰冻结入口行为）；(c) 瘦身探针 import 面（避免 `detection_manga→detection_doctr` 的静态 doctr import）/共享 PYZ。若选 (a)，同时把 spec 注释改成事实口径，避免后续维护者按"只有 onnxruntime"做断言优化。

**4.4 静态审查未覆盖、需集成 Gate 复核的项**
- `git diff --check d298ecd0..HEAD` 的真实输出与 `--name-status`（确认 `contracts/**`、`apps/desktop/src-tauri/**`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、GATE runner 场景集零 diff）。
- base `d298ecd0` 处的 pytest 通过数（本次以 GPU-EP-1 末轮 1823 反推，未见 base 点直接日志）。
- M2-AC5 快照文件与当前文件的逐字节相等（本次以"当前文件仍持 M2-AC5 时代 installer sha `5410e29e`"作内容一致性旁证，`.sha256` 旁车文件在静态会话中无法重算）。

**4.5 低优先级集成顺手项**
`packaging/m2ac5/README.md` §3 五入口更新（P3-1）；`main.rs:378-379` 注释与 CS-Z3 名单（P4-1，可留待 src-tauri 下次开面）；results JSON 增记 installer sha256/build HEAD/`build_venv_note`（P3-5）；`deploy-record.md:40` 场景枚举补 CS-A4/A5（P4-4）。

**4.6 建议的下一步**
1) 由 ZCode 按 C1–C4 在本 Task 允许面内返修（预计仅文档 + runner 判据 + spec 注释，无需重建包：C3 的 runner 判据变更不改变已实测结论，可在同一证据目录补一行说明；若要重跑 runner，用既有安装态即可，不必重跑 GATE/tauri build）；
2) 返修后由**集成方**复核 range `diff --check`/`--name-status`、M2-AC5 还原与 base 点回归数，再把 DETECT-2 的 sfx slice 闭合按 4.1 的精确措辞写入 STATUS；
3) `doc/reviews/M2-PROD-SFX-PROBE-1-dsh-r1.md` 可由集成/编排方按模板把本报告原样落盘（本会话为只读，未写文件）。
