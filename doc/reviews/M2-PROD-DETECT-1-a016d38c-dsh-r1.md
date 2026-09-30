## Verdict

**approved_with_conditions**

无 P0/P1：契约零修订、禁改路径零触碰、三文件 hash pin 与 C4 证据全量一致、fail-closed 四纪律同款复刻、C4 推理序列未引入额外变换。存在 2 项 P2（证据口径/交付记账，均可在集成前以文档+登记闭合）与 8 项 P3/P4（测试守卫强度、可诊断性、可复现性微瑕）。建议由 Owner 在**本 Task 允许路径内**出一轮 review-fix（含两处口径更正与冻结守卫测试收紧），再由 acting Codex 复跑 NOT_VERIFIED 清单后集成。

---

## 逐项核对表

| 项 | 结论 | 依据（文件:行） |
|---|---|---|
| A. 契约零修订 / MERGE_* 复用 | **PASS（守卫强度见 R3）** | review-input.diff 仅 11 文件，无 `src/ports/**`、`detection_doctr.py`、`experiments/**`、`apps/**`、spec；`detection_manga.py:54-60` import 四个 MERGE_* + `cluster_words_into_blocks`，`:109-114` 仅引用不复制；但测试断言为值相等非身份（`test_detection_manga.py:78-87`） |
| B. fail-closed 四纪律同款 | **PASS** | ①`:248-271` 零依赖探测（目录+三文件，缺=ProviderNotConfigured）；②`:274-282` 逐文件 sha256 → `ProviderError`=`PROVIDER_FAILED`（`errors.py:30`），三 pin 与 `M2-DOCTR-QUAL-C4-19d1772e.md:41-43` 全量 hex 逐字一致；③`:157` `manga-<n>` 匿名 label；④`:404-405` 退化框丢弃、空页零候选；懒加载 `:410-418`，模块顶层仅 stdlib+ports |
| C. 加载/推理序列与 C4 一致 | **PASS** | `:285-290` vs `eval_detection_manga.py:126-128`（同本地目录，production 加 `local_files_only=True`+hash 前置）；`:339-346` vs eval `:149-156` 同序同 `target_sizes`；conf 0.5 冻结（`:97`）与 `results-formal-…seg05.json:25` 一致；三类过滤 `:382-386` ≡ eval `:159-164`；clip 写法差异经逐例推演对 keep/skip 与保留坐标**等价**；text 框→同一 `cluster_words_into_blocks(page_size=…)`，RegionCandidate 块级粒度与 docTR word→block 消费对齐 |
| D. 装配最小改动 / backend 语义 | **PASS（R7 为唯一例外）** | `core_assembly.py` 仅 `:61-66` import 段与 `:688-739` 装配段；doctr 分支 `:720-734` 原路径，mock 分支 `:679-686` 未动；未知 backend `:735-739` ValueError；默认 manga 已登记代理裁决（`release-c8eefb4b.md:19`、Task `:29`）；唯一语义差＝空串 env（R7） |
| E. 测试质量与真实性 | **PASS（R3/R4/R8）** | 27 项计数与内容吻合：缺目录/缺文件/缺 torch/缺 transformers/hash 错/空输出/bubble 丢弃全覆盖（`test_detection_manga.py:135-198`、`:209-274`）；real 测试 `:18-37` module-skip 显式原因、`device="cpu"`（无 GPU 可跑）；`test_detector_assembly.py` 仅加 `:69-72` 显式 `backend=doctr`，落点测试语义不变；单测显式 `provider._engine=(object(),object())`+monkeypatch 且 docstring 声明不跑模型（`:4-6`），无 mock 冒充真实推理；real 为真权重推理 |
| F. 证据自洽 | **PASS（R1/R2/R4）** | `cleanstart-gate.json` 顶层 25 条 scenario 全 `status: PASS` + `verdict: PASS`（逐条点数一致）；体积 99,286,538→99,308,142=+21,604 B/+0 文件与 Task/handoff/envelope 三处一致；CPU 均值算术自洽（1578/5=315.6，`envelope.md:27-34`）；C4 基线 38.89s/511/conf 0.5/classes[1,2] 与 JSON `:62-63`、`:25-29` 相符；样本范围（n=5/K01/690px）已在 `:55` 标注 |
| G. 范围纪律 | **PASS** | diff 11 文件全在 Task `:44-51` 允许清单（detection_manga 新增 / core_assembly 装配段 / requirements 追加 `:19-29` / 3 个 tests/providers / Task+Handoff+verification×3）；`packaging/**` 零改动（允许但非必需）；无越界文件 |
| H. Owner 自报两项 | **D 成立且处置得当** | ①`test_registry_readiness.py:190-196` 断言 venv 无 torch/numpy，而 base `requirements.txt:16-18` 已含 torch/doctr（T1.1.1 起）→ 主 venv 必失败，与 base 同 venv 复现的解释可信，另立 slice 合理；②review-input.diff 中 `verification/M2-AC5/**` 零出现，raw 6 文件在本 Task diff 内字节未变，「已 `git checkout --` 还原」与静态证据自洽（git 层复跑见 NOT_VERIFIED） |

---

## Findings

**R1 [P2]｜verification/M2-PROD-DETECT-1/envelope.md:46-51 + doc/handoff…:21 + doc/task…:41,70｜AC6「构建通过（含新依赖）」措辞与证据不符，且未点明发布形态下检测器不可用。** `build_sidecar.ps1:12-13,18` 显示 build venv 是 pyinstaller-only（`packaging/m2ac5/requirements-build.txt`），handoff 亦写「build venv 未动」；+21.6 KB/+0 文件正说明 transformers/torch **不进闭包**（懒加载 + spec EXCLUDED）。因此发布包内默认 manga backend 的 detect 必然 `PROVIDER_DEPENDENCY_MISSING`（docTR 在 base 同样如此，非本 Task 回归，release note `:21` 已把分发优化后置）。但 Task `:25` 的「一个可观察的交付结果：应用…detect 链路产出真实 Region」只在源码 venv 成立。**建议**：①AC6/envelope/handoff 措辞改为「构建不回退 + ML 栈不进闭包（发布形态需外部运行时）」；②把「发布形态检测器运行时/权重分发」显式登记为后续 slice。

**R2 [P2]｜verification/M2-PROD-DETECT-1/envelope.md:39-40｜CPU/GPU 对比混合口径，4.1× 未经说明。** C4 的 38.89s/511=76.1 ms 是**整轮 eval 循环**（含 PIL 解码、merge、计分、12 张 preview 落盘，见 `eval_detection_manga.py:283-474`），而 315.6 ms 是 adapter 单页 `detect()`（envelope `:56` 自述不含 handler）。二者不同域，且该差异方向上下压了 GPU 侧数字，使比值偏保守。**建议**：在 GPU 对照处补一句口径注（「C4 为整轮 eval 口径，含解码/计分/预览，非纯推理」），或引用 C4 侧纯推理数字；76.1 ms 与 4.1× 只作量级参考。

**R3 [P3]｜tests/providers/test_detection_manga.py:78-87、:344-350（并涉 Task:84 / handoff:19）｜冻结守卫弱于声称。** `MERGE_POLICY_CONSTANTS == (detection_doctr.MERGE_*, …)` 是 **float 值相等**：即使 detection_manga 复制了字面量该断言仍通过，故「测试断言对象身份/防复制」不成立；`test_sha256_pins_match_the_c4_weights_manifest` 又只比 sha256 前缀。生产侧「import 未复制」我已由源码静态确认成立。**建议**：改为四组 `detection_manga.MERGE_PAD_PX is detection_doctr.MERGE_PAD_PX`（模块属性同对象，复制即 False），pin 断言写全量 hex；`MERGE_POLICY_CONSTANTS` 若仅供测试可注明或移入测试。

**R4 [P3]｜tests/providers/test_detection_manga_real.py:49-50｜docstring 引用不实的实测数字。** 称「the pinned model detected 3/3 text boxes at conf >= 0.93 **in the AC3 gate run**」，但 envelope §AC3（`:18`）记录的是 `K01_R001` = **2** 个 text box（0.941/0.938）+ 2 bubble。测试本身只断言 `>=1`（未伪造结果），但引用来源错位。**建议**：改为引用 envelope 实际记录，或补一条合成页实测数据再引用。

**R5 [P3]｜src/infrastructure/providers/detection_manga.py:248-257｜配置迁移时的可诊断性。** manga 分支把 `NEWMANGA_DETECTOR_WEIGHTS` 当**目录**；升级用户/脚本若仍将其指向 docTR 的 `.pt` 文件，错误只说 `directory … is missing`，不含 backend 指引（与设计决策「错误消息带配置指引」的目标有落差）。**建议**：消息追加一句「若该变量指向 docTR `.pt`，请设 `NEWMANGA_DETECTOR_BACKEND=doctr`」。

**R6 [P3]｜verification/T1.1.1/scripts/fetch_doctr_weights.py（对照物）vs 本 Task｜缺 sanctioned 的权重获取+校验路径。** docTR 有带 `--dest`/校验的 fetch 脚本并对齐 bootstrap 默认路径；manga 快照只有手交里一条外部 task-env 路径，三文件 pin 仅存在于代码。集成方/运维无法从仓库文档化地取得并自校验快照。**建议**：后续 slice 补 `fetch/verify` 脚本（或 Task 内登记安装 SOP 与 `NEW_MANGA_MANGA_WEIGHTS` 之外的部署约定）。

**R7 [P4]｜src/bootstrap/core_assembly.py:704-730｜doctr 分支唯一语义差异（空串 env）。** 原实现 `Path(os.environ.get("NEWMANGA_DETECTOR_WEIGHTS", str(default)))` 在 env=`""` 时得 `Path("")`（cwd），新实现 `override if override else default` 回落默认路径；两者都 fail-closed，但 handoff/注释「逐字节保留 / 行为零变化」在空串边界不严格成立。**建议**：注释登记该差异，或保持 `os.environ.get(..., str(default))` 原语义。

**R8 [P4]｜tests/providers/test_detection_manga.py:4-6、276-334｜单测并非完全「无重运行时」。** 这些用例经 `detect()` → `_frame_pixels`（`detection_manga.py:220`）需要 numpy；docstring 声称的 no heavy runtime 只在 numpy 由 torch/doctr 带入时成立，缺 numpy 的环境会 error 而非 skip。real 测试还硬编码 `C:/Windows/Fonts/msgothic.ttc`（缺字体是 error）。**建议**：`pytest.importorskip("numpy")`；字体缺失走 `pytest.skip` 显式原因。

**R9 [P4]｜src/infrastructure/providers/detection_manga.py:400-406｜NaN 几何未类型化。** clip 用 `min/max`，NaN 会穿过 `x1<=x0`（NaN 比较恒 False）形成 NaN polygon，与「退化框 skip / never coerced」的自述不完全一致（docTR 同款）。**建议**：加 `math.isfinite` 校验 → `ProviderInvalidOutput`。

**R10 [P4]｜doc/tasks/M2-PROD-DETECT-1.md:12,16（附 envelope:17、cleanstart-gate.json 末行）｜交付锚点记账不一致。** frontmatter `base_commit: c8eefb4b`（release base，见 `release-c8eefb4b.md:5`）与实际分支 base `2fee7d6e` 不同源；`delivery_head: 0b0c9bc7` 与本次 delivery_head `40d4ab64` 不一致；envelope 的 `params=42,733,137` 与 C4 记录的 safetensors `F32=42,861,209` 口径不同；gate json 无末尾换行。**建议**：集成记录统一 release base / branch base / delivery_head 三值并注明差异来源。

---

## NOT_VERIFIED

静态无法复现、须集成方运行时复跑：

1. **pytest 计数**：`test_detection_manga.py` 27 passed（我仅静态点数＝27）、`test_detection_manga_real.py` 2 passed/8.15s、providers+m2_acceptance 309 passed+1 既有环境性失败、`m2_acceptance` 35、`tests/core` 77、cargo 44+1 ignored、vitest 31。
2. **SHA-256 重算**：三权重文件的字节级 hash（我核对了 pin 值与 C4 handoff/报告/正式 JSON 的**全量字符串一致**，未计算 171,543,900 B 文件本身）。
3. **CPU 兼容门 EXIT=0 与 envelope 计时**：`ac3_cpu_gate.py`／`envelope_cpu.py` 位于仓库外 task-env，未入库、不可复跑；315.6 ms/页（n=5）与 0.4s/770 张量、42,733,137 params 均为自报。
4. **M2-AC5 clean-start GATE 25/25 复跑**（我只验证 gate json 顶层 25 条全 PASS + verdict PASS + log 一致）。
5. **sidecar 两次构建与体积**（99,286,538 / 99,308,142 B、161 文件、NSIS 27,924,371 B、pyinstaller 6.22.3）。
6. **git 层事实**：commit 链/ancestry（`2e1d3deb`→`d7faea39`→`0b0c9bc7`→`40d4ab64`）、`git diff --check` EXIT=0、禁改路径专项 diff 为空、`verification/M2-AC5/raw/` 6 文件字节还原（我以 review-input.diff 的 11 文件清单作静态替代）。
7. **环境可用性**：`transformers==5.17.0` / `safetensors==0.8.0` 可安装性与 `transformers.RTDetrV2ForObjectDetection`/`RTDetrImageProcessor` 导出面；本地快照目录与 `msgothic.ttc` 存在性。
8. **C4 GPU 基线**：76.1 ms 未复跑（仅核 JSON `elapsed_seconds=38.89`、`n_regions_evaluated=511`）。

---

## 集成方闭合清单（优先级序）

1. **（P2,R1）** 更正 AC6/envelope/handoff「含新依赖」措辞；在 Task/Handoff 明写「发布形态 ML 栈不进闭包」，并把检测器运行时/权重分发登记为后续 slice。
2. **（P2,R2）** 在 envelope GPU 对照处补口径注（C4=整轮 eval 口径）。
3. **（P3,R3）** 冻结守卫测试改 `is` 身份断言 + 全量 sha256 pin。
4. **（P3,R4）** real 测试 docstring 与 envelope §AC3 对齐。
5. **（P3,R5）** manga 缺配置消息追加 backend 指引。
6. **（P3,R6）** 登记 manga 权重 fetch/verify SOP（后续 slice）。
7. **（P4,R7-R10）** 空串 env 注释/numpy·字体 skip/NaN 校验/锚点记账。
8. **复跑 NOT_VERIFIED 全部运行时证据**，并把结果（含 base 上 `test_registry_readiness` 同失败复现）留痕于 Task 测试表。

## 推荐下一步

把 R1–R10 作为一轮 review-fix 交回 ZCode（限 detection_manga.py / core_assembly 装配段 / requirements 追加行 / tests/providers/** / Task·Handoff·verification 允许路径），回交后由 acting Codex 复跑 NOT_VERIFIED 清单并集成。
