## Verdict

**approved_with_conditions**（0×P0/P1；1×P2、5×P3、3×P4）

- 代码面（`src/infrastructure/providers/ocr_local.py` 单文件）：输入侧 bytes→BGR ndarray、默认构造 `enable_mkldnn=False`、3.x 双形状解析（含 numpy box 物化、`rec_boxes` xyxy→4 点）、错误码/字段零变化，**静态核对全部成立**，且与 TA3-B R6 已端到端验证的 wrapper 映射逐条同构；fail-closed 语义未放宽。
- 证据面：唯一 P2 是 AC4「先红后绿」的 pytest 判别性证书未以 artefact 入库（09 协作协议 §6-12 / Q-009 ①②），DSH 已用 diff 中的修前代码独立复算出「10 failed / 7 passed」与该断言自洽，因此属证据包装缺陷而非事实缺陷。
- 按 handoff 自述 Gate「DSH 0×P0/P1/P2」，R1 需在 merge 前关闭（§集成方闭合清单 第 2 条给出一条命令级补救）；其余 P3/P4 可随集成修正 commit 或另立登记项处置。
- 沙箱无 shell（`pwsh` 返回 `SetNamedSecurityInfoW failed`），本次为**纯静态** Review，所有运行项转 NOT_VERIFIED 交集成方。

---

## 逐项核对表

| # | 核对项 | 结果 | 依据（文件:行） |
|---|---|---|---|
| **A1** | AC1 诊断先行：双 region 连续 bytes 路径、机制判定 | **PASS（条件）** | 探针 `experiments/M2-OCR-PADDLE3X-1/diagnose_bytes_path.py:394-543` 逻辑自洽（T1/T2 判定矩阵、`STALE_REUSE` 显著告警、EXIT=0 表示"判定落盘即交付"）；`diagnosis.json:21-66` 两 region A/B 均 `raw_type=list`、`raw_len=0`、`empty=true`；`verdict=ALWAYS_EMPTY`、`wrong_text_risk=false`、`t2_matches_gt_a=null` 与代码一致 |
| **A2** | 「bytes 被上层先解码」类误判 | **PASS** | 探针把 bytes 直接交给 `engine_prod.ocr()`（`:203-204`），无中间层；修前生产代码同样是 `engine.ocr(request.image_bytes)` 直传（diff 中 `-182,9` hunk 可证），路径同源 |
| **A3** | ALWAYS_EMPTY 是否排除 stale-reuse（R10 结案强度） | **PASS（条件）** | `engine_prod = PaddleOCR(lang="korean")` 在两次 bytes 调用前**没有任何先前推理**（`:193-204`），故结构上不存在"可被复用的非空结果"；且 `t2` 若非空且≠GT_B 必判 `STALE_REUSE`（`:505-515`），跨构造复用 GT_A 也会被捕获。**该论据未写进报告**；机制证据（引擎日志原话）只在 `diagnosis.md:7` 散文中，未入 `diagnosis.json` → R4 |
| **A4** | 证据强度（2 region + 单页 + 单版本） | **PASS（条件）** | 覆盖 paddleocr 3.7.0/paddle 3.3.1 单环境单页；结论域已在 Task/handoff 限定。`engine_prod` 构造注释 `"mirrors ocr_local.py default path exactly"`（`diagnose_bytes_path.py:196`、`diagnosis.json:40`）在修复后已不成立（生产默认现为 `lang="korean", enable_mkldnn=False`）→ R4 |
| **B1** | 行为变化披露：engine 由收到 bytes 变为收到 ndarray | **PASS（条件）** | handoff「风险与遗留①」（`doc/handoffs/M2-OCR-PADDLE3X-1-15ef29ab.md:39`）明确登记 TA3-B2 wrapper 需一行适配；Task AC2 与纪律 §“engine_factory 注入路径保持”同口径。**消费者盘点**：worktree 内 `engine_factory` 使用者仅 `experiments/M2-TA3-B/paddle_e2e_probe.py:161`（禁改面、历史证据）与新增测试；生产 registry 注册的是裸类（`src/infrastructure/providers/runtime.py:522-536`）→ 无生产消费者破坏。**但 tests docstring:19-22 的「TA3-B2 runner wrapper keeps working」与事实不符**（该 wrapper 对 ndarray 做 `np.frombuffer`+`imdecode` 会抛裸 `ValueError`，见 `experiments/M2-TA3-B/paddle_e2e_probe.py:55-58`）→ R2。定级：P3，不构成 P2（已披露且无生产消费者） |
| **B2** | bytes→ndarray 实现与 fail-closed | **PASS** | `ocr_local.py:235-263`：`np.frombuffer`+`cv2.imdecode(IMREAD_COLOR)`，异常与 `None` 均转 typed `ProviderInputError`（error_code `INVALID_INPUT`，见 `src/ports/providers/errors.py:140-143`）。语义**收严**：修前非空乱码 bytes 在 3.x 下是"静默空结果"（无异常），现为 typed 拒绝；无任何静默路径新增 |
| **B3** | 探针顺序与 `enable_mkldnn=False` 默认构造 | **PASS（条件）** | `recognize` 顺序 script→bytes→`_engine_or_raise()`（paddleocr 探针）→解码（`:201-218`），"lazy 探针顺序不变"成立；`engine_class(lang="korean", enable_mkldnn=False)`（`:197`）仅默认路径，注入路径不变（`:193-198`）。numpy/cv2 确为 paddleocr 硬传递依赖（本地 `paddlex-3.7.2.dist-info/METADATA:35,102`：`numpy<2.4,>=1.24`、`opencv-contrib-python==4.10.0.84; extra == "ocr-core"`），docstring `:244` 断言属实。风险：mkldnn 关闭的性能影响未测未登记、2.x 对 `enable_mkldnn` kwarg 的接受性无实测 → R5 |
| **B4** | `provider_id`/`provider_type`/错误码零变化 | **PASS** | diff 未改 `OcrResult` 构造字段与 `_lazy_import`/错误类；新增失败均为既有 typed 类（`INVALID_INPUT`/`PROVIDER_DEPENDENCY_MISSING`）。（旁注：`_lazy_import` 产生的依赖错误不带 `provider_id`，为修前既有行为，非本次变化） |
| **C1** | 3.x 双形状识别 | **PASS** | `_paddle3x_payload`（`:266-280`）处理 dict 与 `.json` 对象两形态、`res` 键在/不在两形态；`"rec_texts" in body` 作为唯一判别键，legacy 2.x 列表不含该键 → 双形状不歧义。与真实 3.x 解析参考（`experiments/M2-TA3-B/paddle_e2e_probe.py:60-77`、`ocr_smoke.py:110-111`）键名/取值方式一致 |
| **C2** | `rec_polys` vs `rec_boxes` 优先级 | **PASS（备注）** | `:344-346` 为「键存在即用（含空数组），仅 `None` 才回退」；TA3-B 参考用真值 `or`（`paddle_e2e_probe.py:142`）。现实 3.x 下两键同源（同一 det 输出），`rec_polys` 空而 `rec_boxes` 非空未见于任何证据 → 未构成缺陷，仅登记口径差异 |
| **C3** | xyxy→4 点顺序/方向 + numpy 物化覆盖 | **PASS** | `_polygon_of:405-427` 先 `tolist()` 再判定，覆盖 list-of-arrays / 单 `Nx4` / 单 `Nx4x2` / dict `.json` 列表四形态；xyxy→`[(x1,y1),(x2,y1),(x2,y2),(x1,y2)]` 与 TA3-B 已验证映射逐字相同（`paddle_e2e_probe.py:93-95`）。端口契约只要求 `tuple[tuple[float,float],...]`（`src/ports/ocr/ports.py:70-77`），下游消费 `polygon` 处（`core_service.py:419`、`core_assembly.py:397`）均属检测侧候选，无绕向依赖；区域几何仅要求 ≥3 点（`src/domain/regions/entities.py:95`）→ 方向无载荷风险 |
| **C4** | scores/texts 数量不齐 | **PASS** | `:353` `index < len(scores)` 否则 `None`；texts 多于 polys 时 polygon 留 `()`（`:372-381`），不发明数值——与 `:335-341` docstring 口径一致，测试 `test_parse_paddle3x_missing_or_short_scores_yield_none_confidence` 覆盖 |
| **C5** | 不可识别输出仍 typed | **PASS（例外见 R3）** | 顶层非序列、page 非序列、item 畸形、text 非 str 均 `ProviderInvalidOutput`（`:296-332`、`:348-352`）；但 `texts/scores` 的 `or` 与 `_box_at` 的异常集合存在非 typed 逃逸窗口 → R3 |
| **D1** | 伪造 3.x 结构真实性 | **PASS** | `_paddle3x_page`（`tests/providers/test_ocr_local.py:113-130`）构造 `{"res": {rec_texts,rec_scores,rec_polys|rec_boxes}, "input_path": None}`，与 TA3-B 实测解析路径的键名/层级/`rec_polys→rec_boxes` 回退/xyxy 判别一致 |
| **D2** | 红态声称（10 failed）自洽性 | **PASS（独立复算）** | DSH 以 diff 中修前代码静态复算：失败 10 = 5×3.x 解析 + `engine_receives_ndarray` + `undecodable_bytes` + `mkldnn` kwarg + `factory_wins` + `missing_opencv`；通过 7 = legacy/顶层拒绝/非 str 文本/空 bytes/paddle 缺失/真实缺失探针 + …；与 `e2e-real-engine.md:46` 的「10 failed, 7 passed」一致。**但红态无 artefact 入库** → R1 |
| **D3** | skipif 语义 | **PASS** | `test_ocr_local.py:364-375`：`skipif(find_spec("paddleocr") is not None)` → 主 venv（无 paddle）**执行**、隔离 venv 跳过；故 handoff「ocr_local 17/17」与「全量 +1 skipped（基线既有 skip）」自洽，非本测试被 skip |
| **D4** | monkeypatch 断言入参类型 | **PASS** | `test_engine_receives_ndarray_not_bytes` 断言 `isinstance(..., np.ndarray)`、`shape==(8,12,3)`、`dtype==uint8`、`calls==1`；`test_undecodable_bytes_fail_typed` 断言 `engine.calls==0`（未触达引擎）——正是 AC2 的判别断言 |
| **D5** | 测试环境耦合 | **PASS（条件）** | `test_ocr_local.py:40` 为测试套件首次顶层 `import cv2`；cv2/numpy 不在 `requirements.txt`（由 `python-doctr` 传递，numpy 顶层导入已有先例 `tests/providers/test_detection_sfx.py:36`）→ R8（P4） |
| **E1** | 文件面 = 允许面 | **PASS** | 依 `review-input.diff` 的 12 个 `diff --git` 头逐一核对：`src/infrastructure/providers/ocr_local.py`（src 仅此一文件）、`tests/providers/test_ocr_local.py`、`experiments/M2-OCR-PADDLE3X-1/`（4）、`verification/M2-OCR-PADDLE3X-1/`（4）、`doc/tasks/M2-OCR-PADDLE3X-1.md`、`doc/handoffs/M2-OCR-PADDLE3X-1-15ef29ab.md` —— 与 Task「允许修改面」（`doc/tasks/M2-OCR-PADDLE3X-1.md:52-54`）逐项对应 |
| **E2** | 禁改面零出现 | **PASS** | `src/ports/**`、`src/bootstrap/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`experiments/M2-TA3-B|A/**`、`doc/STATUS.md` 在 12 文件清单中**零命中**（`STATUS.md` 仍未见本 Task，属集成期更新项） |
| **E3** | 基线元数据一致性 | **条件** | Task/handoff 记 `base_commit: 69137837`（`doc/tasks/...:12`；`doc/handoffs/...:5,14,47,54`），而本次 Review 对象给出的 base 为 `19adf0e0`（release）→ R6，需集成方以 git 事实校正 |

---

## Findings

级别口径：P0 阻断/数据损坏；P1 严重须修；P2 记录标准违反或判别性证据缺口（须处置后才可集成）；P3 低风险建议；P4 备注/登记。

| ID | 级别 | 文件:行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| **R1** | **P2** | `doc/handoffs/M2-OCR-PADDLE3X-1-15ef29ab.md:33-35`；`verification/M2-OCR-PADDLE3X-1/e2e-real-engine.md:44-47`；标准 `doc/09_COLLABORATION.md:176`（§6-12 / Q-009 ①②） | AC4「先红后绿」的**判别性证据未以 artefact 入库**：红态明确写「未入仓库，逐项断言见测试文件注释」，绿态与全量 507 只有散文，均无 EXIT 码与 venv/解释器头；按 Q-009 应记 `NOT_RUN`，不得以散文代替 | handoff :33-35、e2e-real-engine.md:46；DSH 以 diff 修前代码（`engine.ocr(request.image_bytes)`、legacy-only 解析、无 mkldnn kwarg）独立复算得 10 failed/7 passed，与该断言**自洽**，故实质风险低 | 关闭方式（择一）：①Owner 补一份命令级日志入库——`git checkout 15ef29ab -- tests/providers/test_ocr_local.py && git checkout 1885619b -- src/infrastructure/providers/ocr_local.py` 跑 `-q` 得红态，`git checkout 15ef29ab -- src/` 跑绿态，两份均带 EXIT 与 `T1.1.1-impl-py312/Scripts/python.exe` 头；②集成时由 Codex 复跑同口径并将 EXIT 记入 `integration.md`（沿用 TA3-B 先例） | open |
| **R2** | P3 | `tests/providers/test_ocr_local.py:19-22`；`src/infrastructure/providers/ocr_local.py:14-16` | 测试 docstring 断言「`engine_factory` injection path stays untouched (TA3-B2 runner wrapper keeps working)」——注入**机制**不变属实，但 TA3-B2 wrapper 的**输入约定**已变；该 wrapper 对 ndarray 执行 `np.frombuffer`+`cv2.imdecode` 会得到 None 并抛裸 `ValueError("cannot decode region crop bytes")`，与 handoff 风险① 自相矛盾，属口误级误导 | `experiments/M2-TA3-B/paddle_e2e_probe.py:55-58`（wrapper 假设 bytes）；handoff:39（已登记需一行适配） | 改测试 docstring 为「注入机制不变；wrapper 输入约定变化见 handoff 风险①」；并在 src 模块 docstring 的"engine 可注入"段（:14-16）补一句**注入 engine 的输入契约为 BGR ndarray**（该契约目前在代码侧无任何记录点） | open |
| **R3** | P3 | `src/infrastructure/providers/ocr_local.py:342-343`、`372-381` | 3.x 解析的 fail-closed 残留窗口：①`texts = body.get("rec_texts") or []`、`scores = ... or []` 对 len>1 的 numpy 数组触发 `ValueError: truth value of an array ... is ambiguous`（同一函数已在 `_box_at`/`_polygon_of` 显式支持 ndarray box，口径不自洽）；②`_box_at` 只捕获 `(TypeError, IndexError)`，dict 形 `rec_polys` 缺整数键会漏出裸 `KeyError`。两者都会绕过 typed `ProviderInvalidOutput` | 代码静态可判；可达性受限于「payload 经 `.json` 得 JSON 类型」→ 生产路径不可达，注入 engine 返回 ndarray 型 dict 时可达 | 改 `texts = body.get("rec_texts"); texts = [] if texts is None else texts`（scores 同理）；`_box_at` 异常集合补 `KeyError`（或把 body 映射整体包一层 `except (TypeError, ValueError, KeyError)` → `ProviderInvalidOutput`）。若判定不值得改，须在 integration.md 记录可达性分析与接受理由 | open |
| **R4** | P3 | `experiments/M2-OCR-PADDLE3X-1/diagnose_bytes_path.py:193-197`；`verification/M2-OCR-PADDLE3X-1/diagnosis.md:7,14`；`diagnosis.json:40` | 诊断证据两处强度折损：①机制结论的唯一直接证据（引擎日志原话）只在散文里，`diagnosis.json` 无日志字段，读者无法独立复核；②报告未写明「engine_prod 在两次 bytes 调用前无任何先前推理，故无可复用结果」这一**真正排除** stale-reuse 的论据（DSH 已独立确认成立），只说"第二次为空→条件不满足"；③构造注释「mirrors ocr_local.py default path exactly」在修复后已失真，复跑者易误读 | `diagnose_bytes_path.py:194-197`、`diagnosis.md:7,14`、`diagnosis.json:40` | diagnosis 报告补一句机制论据（无先前结果可复用）+ 探针增加 `log_tail`/stderr 捕获字段；同步构造注释为「修复前生产默认构造（修复后已加 `enable_mkldnn=False`，对 bytes 类型拒绝无影响）」 | open |
| **R5** | P3 | `src/infrastructure/providers/ocr_local.py:32-36`、`:197`；`doc/handoffs/M2-OCR-PADDLE3X-1-15ef29ab.md:39`（未运行 2.x） | `enable_mkldnn=False` 是**默认构造的全局性能面变化**（CPU 推理），handoff 五条风险/遗留均未登记性能项；docstring「The flag is accepted by 2.x as well」无实测（真 2.x 回归 Owner 已如实记为"未运行"），故"version-agnostic"断言当前只有单侧证据 | 代码 + handoff:39 | 把「mkldnn off 的性能对照口径」与「2.x 上 `enable_mkldnn` kwarg / ndarray 输入 / legacy 解析组合实测」登记为 D06/后续测量项（不阻塞本 Task）；docstring 可降级为「2.x 亦接受该参数（未实测）」 | open |
| **R6** | P3 | `doc/tasks/M2-OCR-PADDLE3X-1.md:12`；`doc/handoffs/M2-OCR-PADDLE3X-1-15ef29ab.md:5,14,47,54` | base 元数据不一致：交付文档记 `base=69137837`，本次 Review 对象给定 `base=19adf0e0（release）`；若 69137837 非本 diff 直接父，则 handoff「§接收方式① `git diff 69137837..15ef29ab -- src/` 仅 ocr_local.py」与 Recovery point 坐标会误导复现（不影响 diff 面本身：12 文件与允许面一致） | 沙箱无 shell，不可判定两者 git 关系（本次为静态 Review） | 集成方以 `git merge-base`/`git log --oneline --graph` 确认实际 base；若已 rebase 到 release，回填 `base_commit` 与 handoff 正文/recovery point | open |
| **R7** | P4 | 隔离 venv `G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Lib/site-packages/`（`opencv_python-5.0.0.93.dist-info` 与 `opencv_contrib_python-4.10.0.84.dist-info` 并存） | e2e 证据报 `opencv=5.0.0`，说明 `import cv2` 解析到 `opencv-python`（`python-doctr` 传递依赖）而非 paddlex 为 `ocr-core` pin 的 `opencv-contrib-python==4.10.0.84`；"与 paddleocr 官方闭包一致"的证据强度打折（所用 `imdecode/imencode/IMREAD_COLOR` 跨 4.x/5.x 稳定，风险低） | `diagnosis.json:14-19`、`paddle-fixed-e2e.json:23-26`；两个 dist-info 目录 | 需要时在干净 paddle 闭包复核一次，或在 e2e 文档加一条分布冲突注记 | open |
| **R8** | P4 | `tests/providers/test_ocr_local.py:40`；`requirements.txt`、`requirements-dev.txt:1` | 测试模块顶层 `import cv2`，而 cv2 未在 requirements 声明（靠 `python-doctr` 传递）；在最小测试环境中会 collection 失败（numpy 顶层导入已有先例） | `tests/providers/test_detection_sfx.py:36`（numpy 先例）；`requirements.txt:16`（python-doctr） | 二选一：在 dev 依赖注记中登记测试对 cv2 的间接依赖，或测试内改用 numpy/PIL 自造 PNG 字节 | open |
| **R9** | P4 | `doc/handoffs/M2-OCR-PADDLE3X-1-15ef29ab.md:61` vs 仓库惯例 `doc/reviews/**` | 交付物指定 review 报告落 `verification/M2-OCR-PADDLE3X-1/dsh-review-r1.*`，与仓库既有惯例（`doc/reviews/<TASK>-<head>-dsh-rN.md`，204/204 份 DSH/其他 Review 均在 `doc/reviews/`，STATUS 记"报告原字节入库"）不一致；而 `doc/reviews/**` **不在**本 Task 允许面内，Reviewer 无权自落 | glob `doc/reviews` 全量；`doc/STATUS.md:14,30`（原字节入库口径） | Codex 裁决并记录：惯例路径（`doc/reviews/M2-OCR-PADDLE3X-1-<reviewed_head>-dsh-r1.md`，原字节 + sha256）或按 handoff 落 `verification/` 路径；同时明确 Review 报告自身的允许面 | open |

---

## NOT_VERIFIED（集成方运行时项）

1. **主 venv 绿灯与基线不回退**：`507 passed + 1 skipped, 0 failed`（=`tests/providers tests/core tests/m2_acceptance`）与 490 基线口径未由 DSH 执行（无 shell）。需复跑并记 EXIT + 解释器头，并逐条说明唯一 skip 的来源。
2. **红态可复现性**：`10 failed, 7 passed`（修前 src + 新测试）——DSH 仅静态复算自洽（见 D2），未运行；与 R1 同一闭合项。
3. **真实引擎端到端**（隔离 venv，paddleocr 3.7.0 / paddle 3.3.1 / numpy 2.3.5 / opencv 5.0.0）：页面级 28 行、全部 polygon 非空、mean conf 0.4086、`status=OK`、诊断 `verdict=ALWAYS_EMPTY`、crop 等价矩阵 6/6 —— 证据文件字段与探针代码自洽、无内部矛盾，但未复跑。
4. **3.x `res` 缺 `rec_texts` 键的零检测页**：`_paddle3x_payload:278` 要求 `"rec_texts" in body`，否则回落 legacy 分支并抛 `ProviderInvalidOutput`。真实 e2e 的 crop 用例返回 0 行且未抛错，但**既可能**是"payload 带空 rec_texts"**也可能**是 `engine.ocr()` 返回空 list（`parse([])→()`）——两者不可区分。建议集成方用一张无文字图跑一次零注入 `recognize`，断言不抛错（fail-closed 语义下最坏只是把"无文字"变成 typed 失败）。
5. **git 事实面**：`19adf0e0` vs `69137837` 的真实关系、`git diff <base>..<head>` 是否恰为这 12 文件、禁改面是否为空、`git diff --check` EXIT=0、各 commit 与 `delivery_head=15ef29ab` / `tip=67e974a1` 的绑定。
6. **2.x 兼容**：`enable_mkldnn` kwarg 接受性、ndarray 输入、legacy 形状解析三者在真 2.x 上的组合行为（Owner 已如实登记"未运行"，环境无 paddleocr 2.x）。
7. **opencv 分布冲突下的等价性**：隔离 venv 同时存在 opencv-python 5.0.0.93 与 opencv-contrib-python 4.10.0.84（R7）；`cv2` API 稳定性未在该 venv 之外复核。
8. **readiness 面**：新增的 cv2/numpy **运行期**依赖未登记在 registry descriptor（`src/infrastructure/providers/runtime.py:527-530`，禁改面）；由于 `paddlex[ocr-core]` 硬 pin 二者，实际 READY 判定仍准确，是否需要补登记由 Codex 裁决（P4）。

---

## 集成方闭合清单

1. **git 事实**：解析 `19adf0e0`/`69137837`/`1885619b`/`15ef29ab`/`67e974a1` 关系，确认 merge-base 与 reviewed_head；`git diff <base>..<head> --name-only` 应为 12 文件、禁改面为空、`git diff --check` EXIT=0；按 R6 回填 Task/handoff 的 `base_commit` 与 recovery point。
2. **R1（P2，merge 前）**：复跑红/绿两份 pytest 并留 EXIT + venv 头（红态配方：`15ef29ab` 的 tests + `1885619b` 的 src；绿态：`15ef29ab`），入库或记入 `integration.md`；同时复跑三套件确认 `507+1sk 0 failed` 与基线不回退。
3. **真实引擎复核**：隔离 venv 复跑 `diagnose_bytes_path.py`（期望 `probe_verdict=ALWAYS_EMPTY`、EXIT=0）与 `paddle_fixed_e2e_probe.py`（期望 `status=OK`、EXIT=0），核对 crop 矩阵 6/6 与 `e2e-real-engine.md:29-46` 一致；顺带处理 R7 注记。
4. **R2/R3 处置**：R2 建议随集成修正 commit 一并改（1 行 docstring + 1 行契约注释）；R3 建议收紧（`is None` 显式判空 + `KeyError` 并入 typed 通道），若不改须在 `integration.md` 记录可达性分析与接受理由。
5. **R4/R5 登记**：diagnosis 报告补机制论据与日志 artefact；把「mkldnn off 性能对照」「2.x 兼容实测」「PP-OCRv5 det 孤立 crop 零框」「默认构造全预处理质量 conf 0.41 vs 精简 0.69」一并落到 D06/阶段二台账（后两项 Owner 已在 handoff 风险②③ 登记，确认落地即可）。
6. **R9 + Review 归档**：裁决 Review 报告路径（惯例 `doc/reviews/M2-OCR-PADDLE3X-1-<reviewed_head>-dsh-r1.md` 原字节 + sha256，或按 handoff 落 `verification/`），并处理 `doc/reviews/**` 不在允许面的口径；按 09 §6.1 记录 DSH session ID 与 `web_visibility`。
7. **TA3-B2 联动**（handoff 风险①）：确认 merge 顺序——若 TA3-B2 先合，则本修复合并前其 wrapper 的输入约定适配（"已是 ndarray 则跳过 decode"）必须到位，否则将抛裸 `ValueError`。
8. **收口**：Task frontmatter `status: in_review → done`、回填 `delivery_head`/`reviewed_head`/`evidence`；更新 `doc/STATUS.md` Live execution state 与 completion checkpoint；确认分支/worktree 保留、无未交付内容。

---

## 推荐下一步

由 Codex（编排会话代行）按闭合清单第 1、2 条先落 git 事实与红/绿 pytest artefact（关闭 R1），随后执行合并与集成复跑，并把 R2/R3 作为集成修正 commit 一并收口。
