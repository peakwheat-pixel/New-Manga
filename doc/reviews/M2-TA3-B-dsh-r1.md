## Verdict
**changes_requested**（0×P0、0×P1、7×P2；全部为文档/计划级修正，不需重跑冒烟，最长修复项是 1 个 region 的 Paddle 端到端探针）

阶段一的四件交付**事实层基本站得住**：范围零越界、C4/C1 引用数字逐条可对、tag 矩阵算术自洽、TA3-A 超集成立、`engine_factory` 注入点在 `src` 中真实存在（所以"零改 src 绕行"方向可行）、发现 3 的前提（`engine.ocr(image_bytes)` 直传）在 `ocr_local.py:184` 实测成立。但 **AC1 的 GT 设计存在一处逻辑空转（G3）与两处代表性缺口未披露**，**AC4 的两份操作手册有 4 条照抄即不可执行/会 fail-closed 的步骤**，均落在 Task 明名的交付面上，故要求先闭合再集成。

## 逐项核对表

| 项 | 结论 | 依据 |
|---|---|---|
| **A 阈值提案合理性** | **部分成立**：ja 锚定链与 ko"无基线初版猜测"披露如实、inpaint 无数值 Gate 的定性属实、用户裁决点 D/O/T/I/R 五组齐全；但 ja G1 的"论文锚定"与实测子集文本类型不一致（R2）、ko 侧同类代表性缺口未设裁决点（R2）、SFX Gate 无最小 n（R13）、5 分制锚点未分维（R12） | quality-thresholds.md:74-79/100-102/112-116/123-126；cases.json:4192(J46=end_card_and_credits)、4247(J47=dense_multilingual_credits) |
| **B GT 三分设计** | **G3 定义空转**：G2 只覆盖 BJ01-BJ12 + K01-K10，与 G1（J46/J47/K11/K19）零重叠 → 交集恒为空；G1 的两个 ja case 是 end-card/多语言 credits 页而非对白页，CER 中位数在混合来源下的可比性已被"分 G1/全量两档"部分处理，但**混合来源池的偏差方向未披露** | quality-thresholds.md:62-68；cases.json:4185-4294 |
| **C OCR 冒烟证据** | **证据物齐（脚本+两 JSON+结果 md），但缺 raw 日志与版本清单**；三发现定性总体如实，唯发现 3 的**机制表述超出观测**（R10），且生产缺口只登记为"候选"——考虑到该缺口会让用户从 Settings UI 选 PaddleOCR 时静默产出空 OCR，登记强度够但**必须同时给出立即释放的小 Task 建议 + 阶段二第 0 步真跑验证** | ocr-smoke-results.md:32-36；ocr-smoke-paddleocr.json:10-13；ocr-local.py:182-185 |
| **D case 选取代表性** | **矩阵算术全部复核正确**（12 项 tags 计数逐项与 cases.json 一致）、TA3-A 5 case 超集成立、K03/K06 空 tags、BJ09/BJ12 重复理由均核实；不足：ja 10 中 5 页为 title/credits/end-card 类未披露（R3）、taxonomy 16 项中 4 项在**全池**为 0 未登记（R3）、`native_ocr_gt` 用路径 heuristic 而非目录权威字段（R9）、BJ05"唯一覆盖页"表述越界（R17） | cases.json:11-28/4664-4683/4734-4753/4942-5008/5224-5238；select_cases.py:117-121 |
| **E 阶段二计划可执行性** | **设计骨架与 runner 对接正确**（复用 assemble→Run1 PAGE_SELECTION→Run2 REGION→export、13 步与阈值文档逐条对应、engine_factory 注入点真实存在）；但 4 处不可直接执行：(a) 配置注入 API 不存在 + env-var 凭证通路不存在（R4）、(b) "已内建默认 base_url"不成立、缺写 profile 步骤（R5）、wrapper 只解决输入侧、输出形状未对齐会 fail-closed（R6）、未处理 `max_regions=40` 截断（R7） | phase2-plan.md:36/53-58/70-97；core_assembly.py:536-571/690-701/517-532；runtime.py:562-592；dependencies.py:130-138；openai_client.py:174-221；run_smoke.py:325-328 |
| **F 范围纪律** | **静态可核部分全部通过**：`review-input.diff` 仅 10 个文件，全部落在 `doc/tasks`、`doc/handoffs`、`experiments/M2-TA3-B/**`、`verification/M2-TA3-B/**`；无 `src/**`/`requirements.txt`/`packaging/**`/`apps/**`/TA3-A 产物；无二进制/权重文件。注意 `verification/M2-TA3-B/release-c4039415.md` **不在 diff 内**（归属需集成方确认），且 Task frontmatter `base_commit=c4039415` 与 Handoff/diff base `53fdfcc6` 双口径并存（R18） | review-input.diff（`^diff --git` 10 行清单）；glob 权重后缀 0 命中 |

## Findings

**R1 [P2]｜verification/M2-TA3-B/quality-thresholds.md:66（§2.2）｜G3 双源交叉恒为空集，条款不可执行**
G3 定义为"G1 与 G2 同时可用的 region"，但同表把 G2 限定为"BJ01-BJ12（无文本 GT）、webtoon K01-K10"，G1 为 J46/J47/K11/K19 —— 两个集合互斥，交集永不存在。
建议：二选一——①把 G2 预填扩展到 G1 四个 case 的同一 region（同 crop 双源对照，量小且正是"最高可信度"想做的事）；②删除 G3，并在 §2.2 显式写"本批无独立交叉源，G1/G2 互为旁证"。

**R2 [P2]｜quality-thresholds.md:74-77 + :100-102（§2.3/§2.6 O-3）｜ja G1 的论文锚与实测子集文本类型不匹配；ko 侧同类缺口未设裁决点**
J46（E20P06）= `japanese_end_card_and_credits`、J47（E20P07）= `dense_multilingual_credits`（cases.json:4192/4247），**不是**竖排对白页；manga-ocr 论文锚（Manga109）指向对白气泡。O-3 只写了"P&C 圆体风格 vs BJ 印刷漫字形"，未披露"credits/end-card 页 vs 对白页"和"多语言 credits 文本"两点。同构问题在 ko 侧（G1=K11/K19 全是 P&C kr，而 ko 生产域是 webtoon 手写体）完全没有对应裁决点。
建议：把 O-3 扩写为 ja/ko 两侧共享的代表性裁决点，并在 §2.3 明写"G1 子集结论只对 P&C 风格排版/credits 文本成立，不得外推到对白/竖排/手写体"。

**R3 [P2]｜case-selection.json:39-448 + doc/handoffs/M2-TA3-B-b057ec69.md:64｜ja 子集的文本类型分布未披露，tag 矩阵被读成"全覆盖"**
ja 10 中 BJ04/BJ05/BJ08 的 `text_type=title_and_credits`（cases.json:4671/4741/4949），加 J46/J47 共 **5/10 是标题/版权/结束卡类**，只有 BJ02/BJ03/BJ06/BJ10/BJ11 是故事页；"ja 10＝日漫竖排对白核心"的表述会高估对白覆盖。另：taxonomy 16 项中 `curved_text/overlapping_text/unusual_balloon/extreme_size` 只出现在 taxonomy 定义（cases.json:19-27），**全池零 case**，manifest 未登记该缺口。
建议：manifest 增 `text_type` 分布字段 + "池内不可得 tag（4 项）"登记；handoff/回填表把 ja 子集表述改为"5 故事页 + 5 标题/版权页"。

**R4 [P2]｜verification/M2-TA3-B/phase2-plan.md:66-84（§3 选项 (a)）｜配置注入 API 不存在；"key 只经环境变量"在生产凭证通路上无实现**
① `core.settings.update({...})` 无此对象：`CoreServices`（core_assembly.py:536-571）没有 `settings` 字段；真实路径是 provider profile 存储（`ProviderProfileStore.update_profile`，ports/providers/profiles.py:88 / json_profile_stores.py:162）+ `pipeline_defaults.save_provider_binding`（该 API 存在，pipeline_defaults.py:62）。② 唯一凭证 resolver 是 Windows vault（core_assembly.py:517-532），`assemble_core_services`（:690-701）**没有** credential_store/resolver 注入参数，鉴权走 `credential_ref`→resolver（openai_client.py:174-175/207-221）——"`TA3B_TRANSLATE_API_KEY` 环境变量"没有现成通路。
建议：手册补写"runner 内需 re-register `openai-compatible-translation` 并传入自定义 `credential_resolver`（读 env）"或"用 vault 写 credential"的二选一具体步骤；否则二选一解锁后第一步就会卡住。

**R5 [P2]｜phase2-plan.md:88-97（§3(b) 步骤 4）｜"生产 provider 已内建默认 base_url/模型"不成立，手册缺写 profile 步骤**
`sakura_config` 的默认值**未被 registry 使用**：runtime.py:583-588 显式读 settings 里的 `base_url/model`（注释亦明说不用隐式默认），空 profile 会让 endpoint requirement 未满足（dependencies.py:132-133 "no base_url configured"）→ readiness fail-closed。
建议：手册加一步"写入 sakura profile：base_url=`http://127.0.0.1:8080/v1`、model=`sakura`"并给出真实写入 API，再执行 `save_provider_binding("translate","sakura-local")`。

**R6 [P2]｜phase2-plan.md:36（§2.2 绕行 1）vs src/infrastructure/providers/ocr_local.py:183-241｜wrapper 只修输入侧，输出契约未对齐 → ko OCR 会 fail-closed**
`_parse_paddle_output` 只接受 3.x 之前的 `[[box,(text,score)],…]` 嵌套（docstring 亦如此声明），而 3.x 的返回形状是 `res.rec_texts/rec_scores`（冒烟脚本自己就是按 3.x 形状解析：ocr_smoke.py:107-113、JSON:10-13）。wrapper 直接转调真 engine → adapter 抛 `ProviderInvalidOutput`，ko 侧 CER 无法产出（是 fail-closed，不是静默，但仍阻塞 Gate）。
建议：计划中写明"wrapper 需把 3.x 结果映射回 legacy 形状（或改用 `predict()` + runner 内输出适配）"，并把"1 个真实 region 端到端跑通 ko OCR"列为阶段二第 0 步验证项。

**R7 [P2]｜phase2-plan.md:24-33（§2.1 扩展表）｜未处理 run_smoke.py:325-328 的 `max_regions=40` 截断，直接影响 CER 分母与"全量"档 Gate 口径**
K01 为 690×62133 长条漫，region 数远超 40；run_smoke 只记 `truncated: true`，而成品口径（quality-thresholds.md:14/78-79）说的是"全量（G1+G2）"。
建议：明确 run_qualification.py 的 region 策略（提升上限 / 分层抽样并登记种子 / 取消截断），并在 §2.4 写明"CER 分母 = 全部检出 region（或明示抽样集）"，避免阶段二报告口径漂移。

**R8 [P3]｜quality-thresholds.md:64（§2.2 G1 备注）｜"已验证：ep04/ep20 语言包各 472 个 SVG"无证据物**
本交付 diff 内无该审计记录，phase2-plan 第 3 步才做 G1 提取；仓库内 TA2C 审计只记录 ep04 ZIP **615 成员**（doc/reviews/M2-TA2C-2c12ba1e-dsh-r1.md:49），与 472 的计数口径关系未说明。
建议：补 ZIP 成员清单/计数记录（或改措辞为"待阶段二第 3 步验证"）。

**R9 [P3]｜experiments/M2-TA3-B/select_cases.py:117-121｜`native_ocr_gt` 用路径 heuristic 而非 cases.json 权威字段**
`"peppercarrot" in str(page_path)` 会把 **J48-J52**（`ground_truth_available=no_text_transcription_in_svg`，cases.json:5313 等）也标成 native GT，当前选取下结论正确但生成器脆弱。
建议：改从 `ground_truth_available` 派生，保留三分（`partial_svg_text_layer`/`svg_text_layer_present_unaligned`/`none`），顺带消除"K11/K19 是 unaligned 而非 partial"这一差异的丢失。

**R10 [P3]｜ocr-smoke-results.md:36 / experiments/M2-TA3-B/ocr_smoke.py:112-116｜发现 3 的机制表述超出观测**
注释称 3.x "ignored 并静默复用上一次输入"，但 seam 探针是在一次成功 ndarray 推理**之后**仍返回 `EMPTY_RESULT`（JSON:10-13），与"复用上一次输入"不相容。
建议：正文只陈述观测（bytes → 空结果且无异常），机制标为假设；修复 Task 用"连续 2 个不同 region 走 bytes 路径"判定是"空"还是"错位复用"（后者严重度显著更高：静默错误文本）。

**R11 [P3]｜quality-thresholds.md:43（§1）vs :179（§6）｜0-region case 的 SKIP 豁免与"四件齐"存在内部矛盾**
§1 说 region_count=0 不判 FAIL 且 OCR/translate 自动 SKIP；§6 却要求每 case"detect/OCR/translate/export 四件齐"→ 该 case 必然让全链 Gate FAIL。
建议：§6 增"`attribution=data:no-regions-detected` 时四件齐不适用"的豁免条款。

**R12 [P3]｜quality-thresholds.md:123-126（§3.2）｜5 分制锚点未按维度定义**
现只有一组整体锚（5=出版级…1=不可用），而闸门用三维均值的"中位数 ≥3.5 且 ≥3 占比 ≥80%"，对"锚点施于单维还是均值"解释敏感。
建议：每维度补一行维内锚，或明写"锚点对每个维度独立适用，region 分=三维均值"。

**R13 [P3]｜quality-thresholds.md:112-116 + :135（§3.1/T-2）｜SFX Gate 无最小 n，且示例 case 含未选中页**
`non-fail ≥70%` 未设 n 下限；同文自述 SFX region 可能"不足 15 条"，而示例中的 **J38 不在 20 case 选取内**。
建议：设最小 n（n≥15 才判 Gate，否则只登记分布）+ 把示例改为选中的 BJ06/BJ10。

**R14 [P4]｜.gitignore:7-8｜"`.gitignore` 护栏"表述强于实际规则**
护栏只有 `*.safetensors`，未见 `*.pt`/`*.onnx`/`*.pdmodel`/`*.gguf`。
建议：补规则，或把 AC5 措辞改为"权重全部落在仓库外路径（task-envs/HF/paddlex 缓存）"。

**R15 [P4]｜quality-thresholds.md:165 vs phase2-plan.md:32｜"抽样种子登记"与固定名单不一致**
§5 说抽样（种子登记），计划写死 `--rerun-check BJ02,K01,K11`。
建议：统一为"固定 3 case（理由：覆盖 ja/ko/P&C）"或改为带种子的抽样。

**R16 [P4]｜phase2-plan.md:53-58（§2.4 方案 A）｜缺依赖冲突检查**
冒烟已实测 numpy 2.5.3→2.3.5（ocr-smoke-results.md:16）；再叠生产 requirements + PySide6 + docTR 存在 torch/numpy/opencv 版本冲突面，当前只做 import 自检。
建议：第 1 步加 `pip check` + torch/numpy/opencv/docTR 版本对照记录。

**R17 [P4]｜case-selection.json:60（BJ05 selected_reason）｜"rotated_text 唯一覆盖页"越界**
BJ01（cases.json:4465-4470）与 BJ09（:5022-5026）tags 与 BJ05（:4744-4749）**完全相同**，"唯一"只在"已选中 20 case"内成立；且 BJ01 排除理由（封面 credits 页）同样适用于 BJ09（排除表却写"与 BJ05 tags 重复"）。
建议：改为"选中集内唯一 rotated_text"，并补一句三页同 tag 中为何选 BJ05。

**R18 [P4]｜doc/tasks/M2-TA3-B.md:13 vs doc/handoffs/M2-TA3-B-b057ec69.md:5｜base 双口径**
Task frontmatter `base_commit=c4039415`，Handoff/diff base=`53fdfcc6`（AC5 自检也用 53fdfcc6）。
建议：frontmatter 增 `branch_base: 53fdfcc6` 或统一口径，避免集成方用错 diff 范围。

## NOT_VERIFIED
静态沙箱（`pwsh` 不可用：`SetNamedSecurityInfoW failed`）无法执行任何命令，以下由集成方复跑闭合：
1. `pip` 安装三包 EXIT=0 / 总耗时 166s / py3.12.3 / 版本清单与 numpy 降级（无 raw 日志与 `pip freeze`）。
2. 权重 424MB（HF 缓存）+ 171MB（`~/.paddlex/official_models`）的存在性与体积、以及"模型经 modelscope 下载走通"。
3. 20 case 的 SHA256 **实算**（manifest 值与 cases.json 逐条一致，但未做文件哈希复算）。
4. `select_cases.py` / `ocr_smoke.py` 的 EXIT=0 复跑（含"两命令 EXIT=0、JSON status=OK"）。
5. `git diff --check` EXIT=0、禁改面 `git diff --stat` 为空、权重零入库的 git 层结论（我仅能读到 `review-input.diff` 的 10 文件清单；字节级 diff 完整性、worktree porcelain 状态、`release-c4039415.md` 与 53fdfcc6/c4039415 的提交归属均未确认）。
6. PaddleOCR 3.x 在本环境 `ocr()` 的真实返回形状与 pdf 兼容行为（R6 的判定依赖实跑）。
7. Sakura `127.0.0.1:8080` 当前 reachability（文档自述 `unreachable`）。
8. 阶段二估时（TA3-A 单 case 2-5 分钟 → 20 case 1-2 小时）与 `max_regions=40` 对各 case 的实际截断情况（R7）。

## 集成方闭合清单
1. `git -C <worktree> status --porcelain` 应为空；`git log --oneline -3` 应为 `2beca0bb → b057ec69 → 53811c36`；`git diff --stat 53fdfcc6..2beca0bb` 应恰为 review-input.diff 的 10 文件（若多于 10 文件，diff 不完整，Review 结论需重跑）。
2. `git diff --check 53fdfcc6..2beca0bb`（期望 EXIT=0）；`git diff --stat 53fdfcc6..2beca0bb -- src/ packaging/ apps/ experiments/M2-TA3-A/ requirements.txt`（期望空）；`git diff --name-only 53fdfcc6..2beca0bb | Select-String -Pattern '\.(pt|safetensors|onnx|pdmodel|gguf)$'`（期望空）。
3. 复跑 `python experiments/M2-TA3-B/select_cases.py`（期望 EXIT=0、`verification_failures: []`、`total=20/ja=10/ko=10/ta3a_superset_included=true`），并对 20 个 `page_sha256` 做一次独立实算比对（我核对到 cases.json 侧值一致，未做文件哈希）。
4. 复跑两条 `ocr_smoke.py` 命令（命令见 ocr-smoke-results.md §5），确认 EXIT=0 与 JSON `status=OK`；补存 `python -V` + `pip freeze` 原始输出。
5. 就 R6 做一次 1 个真实 region 的最小端到端：`PaddleKoreanOcrProvider(engine_factory=<wrapper>)` → 若抛 `ProviderInvalidOutput`，则确认输出形状缺口成立，阶段二须先补映射。
6. 就 R4/R5 选定翻译方案后，先按实际 API 写出 profile 写入 + binding + 1-region 探针的最小脚本（不得写 `src/**`），失败即停。
7. R1/R2/R3/R8/R11/R12/R13 为纯文档修订，建议 Owner 一次性返修（可只改 `quality-thresholds.md` + `phase2-plan.md` + `case-selection.json` + Handoff 摘要），再交 r2 复核。
8. 采纳 R10 的判定后，同步更新"修复 Task 候选"的验收条件（当前只写了"输入契约适配"，应补"输出形状契约 + 顺序 region bytes 行为验证"）。

## 推荐下一步
让 Owner（ZCode）在**不重跑冒烟**的前提下做一次文档返修，优先闭合 R1/R2/R4/R5/R6/R7 六条 P2（GT 双源交叉定义、G1 代表性裁决点、translate 两选项的真实配置/凭证步骤、Paddle 输出形状与 region 上限口径），随后交 DSH 做 r2 复核；用户侧仍只需回答"翻译 endpoint 二选一"。
