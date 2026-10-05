# M2-SFX-GATE-T3 · Gate 定义冻结文档（G1-G8 合同级权威定义）

- Task：[doc/tasks/M2-SFX-GATE-T3.md](../../doc/tasks/M2-SFX-GATE-T3.md) AC1 ｜ Owner：ZCode ｜ 日期：2026-10-05
- 分支 `agent/zcode/M2-SFX-GATE-T3`（base_commit=`87ca8724`，release=`f858edd3` 仅 Task 合同入库）｜ worktree：`G:/CODEX/New Manga.worktrees/M2-SFX-GATE-T3-zcode`
- 版本：**v1.0-frozen**（本文档 commit 即冻结时点；变更规则见 §5）

## 0. 冻结声明

1. 本文档是 T3 正式评测（AC4）与门判定（AC5）的**唯一门定义事实源**。AC4 评测执行开始后，本文档不得修改；AC5 逐门判定只能引用本文档 v1.0 的门定义。
2. 阈值、数据构成、口径在本节签署的版本内为合同值；评测执行中发现的口径缺口按 §5 变更登记规则处置，禁止原地改写。
3. 本文档为零 src 交付：仅 `verification/M2-SFX-GATE-T3/gate-definition.md` 一个文件；生产 pin（`src/infrastructure/providers/detection_sfx.py:108/110-112`）与全部 src/tests/contracts 零触碰。
4. 门判定纪律（沿 V1/V2 合同口径顺延至正式门）：统计功效低（考卷 5 框、KO 56 框量级），**禁用「显著」**；0 也如实；**FAIL 如实判定即为本 Task 成功（Gate 不是橡皮图章，Task 合同风险③）**。

## 1. 定义输入（全部经本 worktree 在位验证）

| # | 输入 | 路径 | 权威数字摘录 |
|---|---|---|---|
| ① | T0 技术事实 | `verification/M2-SFX-FINETUNE-PREFLIGHT/preflight-report.md`（主仓库，本分支已含） | 路线 A′ 定案（§2）；导出链→生产通道 EXIT=0、names 逐字零漂移（§5）；显存 batch=8（§4）；许可备案=用户裁决降权不阻断（§6） |
| ② | V1 实测 | `verification/M2-SFX-TRAIN-V1/train-v1-report.md` | BJ 考卷 0/5（严格）；KO 0/56；GT ⊂ chiqui7 候选池循环性定性（§4 DSH r1 C1）；T4 条件清单（§7.2） |
| ③ | V2 实测 | `verification/M2-SFX-TRAIN-V2/train-v2-report.md` | 三方同链路评测：v2a 4/5（P 0.80）/v2b 5/5（P 1.0）/chiqui7 复跑 5/5（P 0.8333）；KO 长条页三方 0/56 结构性发现（§4.4）；P2-1 整改=同链路独立复跑基线口径（§4.1）；v2b license:other 未审计（§6） |
| ④ | KO 口径提案 | `verification/M2-KO-TILE-CALIB/calib-report.md` + `ko-caliber-proposal.md` | 四组矩阵：letterbox 双权重双 conf 全 0/56（零输出，GT 无关事实）vs tile ov128 chiqui7 56/56（同源复现，P 0.8235）/v2b 35/56（P 0.3465）；GT 同源性/循环性限制五点（§1/提案 §3）；冻结参数（提案 §3.1-3.4） |
| ⑤ | R3 成果 | `verification/M2-SFX-ANNOTATE-R3/stage-r3-report.md` | BJ 正集 8 页 18 框（train 6 页 13 框+考卷 5 框不动）；train-v3 指纹 `d57353b1db87749fbf20da4a4f2b555c60266db41fc69a594110bd7658c328de`；own-manga 418 自蒸馏框归因分层（§6 DSH P3-4）；R3-MISS 立项（BJ32-37 六页 miss 补画） |

生产代码契约（本 worktree 实测 grep 核验，行号与各报告引用一致）：
`src/infrastructure/providers/detection_sfx.py:108` `SFX_HF_REVISION="7f5f5c04…"`；`:110-112` `SFX_WEIGHTS_SHA256="d87389af4350954143a216bcfe40fd2ad93312cb136534e6073c9c740d98b646"`；`:118` `SFX_CONF_THRESHOLD=0.5`；`:121` `SFX_NMS_IOU=0.7`；`:137` `SFX_CLASS_MAP={0:bubble,1:panel,2:sfx,3:text}`；`:138` `SFX_CLASS_ID=2`。

## 2. 门目录与门数登记理由

| 门 | 名称 | 类型 | 一句话 |
|---|---|---|---|
| G1 | BJ 毛笔竖排召回门 | **硬 Gate** | vol05 组考卷原始 5 框严格口径召回+精度双下限，扩展集 directional |
| G2 | KO 长条页门（tile 冻结口径，双 GT） | **硬 Gate**（口径合规+非派生切片不回退） | 派生 56 框=采集一致性属性（directional），非派生切片=模型质量属性（硬判据载体） |
| G3 | 数据集健全性与考卷完整性门 | **硬 Gate（先决）** | 六项断言全零违例，任何一项 FAIL 则本轮全部评测数字不作门判定 |
| G4 | 考卷覆盖门 | directional | 形态×页×held-out 覆盖矩阵登记，考卷重划提案留给用户/编排裁决 |
| G5 | 生产序列契约门 | **硬 Gate** | ONNX→SHA 门→`_build_engine`→names/imgsz/输出张量五项断言 |
| G6 | 合成-真实域差与标签噪声归因门 | directional | 评测差值按「样本量/域差/标签噪声/GT 循环性」四层归因登记，无 PASS/FAIL |
| G7 | 端到端损害门 | **硬 Gate** | 新权重进程内替换后 SFX→翻译链路冒烟零新增故障，输入差异 directional 登记 |
| G8 | 部署门 | **硬 Gate**（checklist 全项） | ONNX/sha/来源/许可审计清单，v2b license:other 审计在本门结算 |

**门数=8、编号连续的理由（合同裁量点登记，Task:63「G1-G8 具体门数可按 preflight 事实增删」）**：提案语境仅锁定三门编号语义——G1=BJ 门（`verification/M2-SFX-TRAIN-V2/train-v2-report.md` §7.1.1「G1 BJ 门的质量可达性」）、G7=端到端损害门（`doc/STATUS.md:14` 前情段「G1-G8 含 G7 端到端损害门」+`verification/M2-SFX-ANNOTATE-R1/stage2-report.md:29`）、G8=部署门（Task 合同 AC1 原文引 STATUS「含端到端损害门 G7/部署门 G8」）。G2-G6 无提案编号绑定；本定义按 ①-⑤ 输入材料的实测事实填充为五门（KO 口径提案 AC3→G2；V1/V2/R3 三轮全部以「门」级断言出现的数据健全性检查→G3；R3 §6.2 考卷重划提案→G4；T0 AC4+V1/V2 AC3 冒烟链→G5；V1 §6 DSH P3-3+R3 §6 P3-4+KO-TILE 限制段→G6），恰好 8 门、每门均有在盘实测材料支撑，**无需增删**。注意：`doc/STATUS.md:14` 中「G2 50 行 GT」属 TA3-B2 OCR 线（`doc/handoffs/M2-TA3-B2-3c8801b7.md:71`），与 SFX Gate 门编号无关，不作为本 G2 语义来源。

## 3. 通用评测口径（全门公共底座，逐门不再重复）

1. **匹配算法**：box IoU≥0.5、pred conf 降序贪心、每 GT 至多一预测（`experiments/M2-SFX-TRAIN-V2/eval_v2.py:68-97` `match_gt` 逐字先例，`IOU_MATCH=0.5` `:47`）；T3 评测脚本零复刻引用或独立实现须过复算核验（KO-TILE §5 `recompute_matrix.py` 先例）。
2. **conf 双口径**：主口径 conf≥0.50（生产冻结 `SFX_CONF_THRESHOLD=0.5`，`detection_sfx.py:118`，精度优先）；宽松 conf≥0.20 **仅诊断**，不作任何硬 Gate 判据（KO-TILE 提案 §3.4 实证理由：chiqui7 tile 0.2 档召回零增益纯增误检 68→84；v2b precision 崩至 0.2019——以 0.2 评门会奖励高误检配置）。
3. **基线口径（对全部对照数字）**：chiqui7 现役权重经生产 pin sha 自检后**同链路独立复跑**（`eval_v2.py:129-131` sha 断言 + `:197-201` `provider.detect` 真调用；P2-1 整改模式，V2 §4.1）；预标注引用口径（V1 蓝本）**永久退役**，其历史数字（chiqui7 56/56、5/5 预标注口径）不得出现在任何门的对照列。
4. **进程内重指纪律（零 src）**：候选权重经 `SFX_WEIGHTS_SHA256` 进程内运行时重指进生产序列，运行前须先证 SHA 门对外来权重正确拒跑（`PROVIDER_FAILED`），finally 恢复原 pin（先例：`eval_v2.py:179`、`tile_calib.py:374/381-382/443-444`）；src/env/registry 零改动。
5. **GT 循环性总登记（适用于一切含 chiqui7 派生 GT 的门）**：BJ 考卷 GT 与 KO 派生 GT 均源自 chiqui7 扫描候选（R2/R1 判定链 confirm），故 chiqui7 对这类 GT 的召回=「GT ⊂ 候选池」的数学必然（V1 §4 DSH r1 C1、KO-TILE §1 限制①），**只能作自洽上界/采集一致性参照，不得解释为独立性能**；跨模型中立的唯一 KO 考题=AC3 非派生切片（G2-B）。全部 GT=ai-consensus（`human_review=false`），「标注质量」与「模型质量」两层误差必须分开归因（R1 stage2-report §0、R3 §0）。
6. **输出纪律**：逐框明细+汇总矩阵落 `verification/M2-SFX-GATE-T3/raw/`；每门判定须给出可复算的数字来源；directional 门的产出是登记表而非 PASS/FAIL。

## 4. 逐门定义

### G1 · BJ 毛笔竖排召回门【硬 Gate】

- **定义**：候选权重在生产整页 letterbox 序列下，对 densho810/vol05 组 BJ 考卷（竖排毛笔假名主攻形态）的召回与精度同时达到替换候选资格下限。语义=「不差于现役的多命中、不多于现役的误检」。
- **评测数据**：①**主判据数据**=vol05 组考卷原始 5 框：pre-bj17（2 框 R2-BJ17-B00/B01）+pre-bj18（3 框 R2-BJ18-B00/B01/B02），坐标逐位=R2 出厂（R3 §5.3「考卷 5 框不动」断言）；排除留痕 R2-BJ17-B02（仲裁 delete）。②**directional 扩展集**=AC2 R3-MISS 补画后 BJ 域全部 complete 页（R3 时点 8 页 18 框+补画转正页），按 train-v4 重切后 split 归属分列：challenge 侧（含 vol05 组转正扩展框）=泛化考题，train 侧=记忆性指标（只登记，不作判据）。
- **口径**：整页 letterbox 生产序列原样（`SfxDetectionProvider.detect`：letterbox 1024/类无关 NMS 0.7 `detection_sfx.py:121`/sfx 类过滤 `:138`）；主口径 conf≥0.50；通用口径 §3 全条适用。
- **阈值（冻结）**：主判据同时满足 ①严格 conf≥0.50 召回 **≥4/5（80%）**；②precision **≥ chiqui7 同链路独立复跑同口径 precision**（V2 参考值 0.8333＝6 pred 5 匹配；以 T3 评测当轮复跑实测值为判据值）。
- **判定规则**：**硬 Gate**——两条件同时成立=PASS；任一不成立=FAIL（如实判定）。扩展集数字、宽松口径数字、vs 基线差值全部 directional 记录，不影响 G1 判定。原始 5 框子集为不变判据集——AC2 扩展不改变阈值分母。
- **阈值依据**：①召回线 4/5——V2 实测两版均达线（v2a 4/5、v2b 5/5，V2 §4.2），V1 为 0/5，门可达性已证（V2 §7.1.1「从『未证』升级为『directional 已证、待正式 Gate 定量』」）；5 框上 1 框差=20%，满召回硬线会令统计噪声直接决定门判，4/5 为「主攻形态多数命中」的最低合同化。②精度线=基线同值——「不多于现役误检」的切换语义（chiqui7 唯一误检=曾被仲裁 delete 的气泡框，与判定链自洽）；v2a 型 4/5+1 误检（P 0.80）据此 FAIL。
- **已知限制**：①考卷 GT 源自 chiqui7 整页 letterbox 扫描候选——基线 5/5（IoU≈1.0 级）是自洽上界非独立性能（§3.5）；新权重数字不受此循环性影响（绝对量）。②5 框功效低，判据对单框波动敏感，PASS/FAIL 结论禁用「显著」表述。③train 侧 BJ 正集仅 6 页 13 框（R3 §5.2），扩展集 train 侧数字是记忆性指标。④BJ32-37 补画页若产框转正入 challenge，扩展部分无既有判定链先例（AI 直接标注首例），其 GT 质量归因登记在 G6。

### G2 · KO 长条页门（tile_ov128 冻结口径，双 GT）【硬 Gate】

- **定义**：KO 长条页（宽≤690、aspect>1:20 量级）在**冻结 tile 口径**下的评测，按双 GT 属性分离：chiqui7 派生 56 框标「**采集一致性**」属性（directional），本轮 AC3 非派生切片标「**模型质量**」属性（硬判据载体）——防采集一致性冒充模型质量（KO-TILE 限制⑤「T3 采信前置」的裁决落地，用户裁决=按推荐释放含此前置子项）。
- **评测数据**：①**KO-A 派生 GT**：pre-k01/k02/k08/k09 四页 **56 框**（27/3/2/24），页尺寸 690×51971～100480（aspect 1:75～1:146）与 600×18401（1:31），来源 R2 final manifest（KO-TILE §1）。②**KO-B 非派生切片**：AC3 产物——两 AI 独立看整页画 SFX 框（任务书零既有坐标，隔离纪律实证）、比对仲裁后的 GT 切片（预期每页数个至十余个）+与派生 GT 56 框的交集/差集统计。
- **口径（冻结，逐字=KO-TILE 提案 §3）**：tile 宽=页宽原生无缩放、高 1024、重叠 128（步长 896）、末尾补 `page_h-1024` 锚点；tile 内=生产序列本体逐字（`dsfx._letterbox`/`dsfx._sfx_boxes` 函数本体，零第二实现）；页级合并=跨 tile IoU 0.5 conf 降序贪心 NMS（R1 `_dedup_boxes` 逐字）；主口径 conf≥0.50；**letterbox 整页对照口径并行跑**（每权重每 conf 一组，复现零输出结构性事实）。
- **阈值（冻结）**：硬性判据两条——①**口径合规**：冻结参数逐字复刻断言通过（tile 数/步长/锚点/合并阈值与提案 §3.1-3.3 一致）；②**KO-B 相对不回退**：非派生切片 tile 口径下候选权重 recall ≥ chiqui7 基线同切片同口径 recall。KO-A 差值、precision、宽松口径、letterbox 对照、交集/差集统计全部 directional。
- **判定规则**：**硬 Gate**（①+②）——两条件同时成立=PASS；任一不成立=FAIL。**KO-B 切片若为 0 框（AC2/AC3 极端产出），G2 判 INDETERMINATE 如实登记（不判 PASS）**；AC3 隔离纪律实证（任务书无泄漏）失败则 KO-B 数据作废、G2 降为 FAIL-数据无效并如实登记。
- **阈值依据**：KO-TILE §0/§2——letterbox 双权重双 conf 全 0/56（n_pred=0 零输出，GT 无关绝对事实）vs tile 56/56（同源复现）/35/56；「在序列口径实验完成前任何权重都无法通过沿用整页序列的 KO 门」（V2 §7.1.3）；v2b tile 35/56+P 0.3465 双差已裁「不入切换候选」（KO-TILE §6.5）——G2 硬线即把该裁量合同化。
- **已知限制**：①KO-A 56/56 基线是同源复现（pred conf 与 GT conf 逐位相同的确定性必然，KO-TILE §1 限制①），其 precision 0.8235≈1−代审拒绝率，非独立误检率；新权重 vs 该上界的差值无法区分「模型差」与「GT 偏」——此不可分离性正是双 GT 属性分离的原因。②ov128 与 GT 采集相位一致是「GT 在 ov128 网格上采集的必然相位」，三相位 56/44/45 证明相位强调制（限制②），T4 落地复测偏离 56/56 先查相位。③非派生切片产量与质量依赖 AI 直接标注（首例），GT 误差归 G6 登记；其与派生 GT 差集可能大——这正是要度量的对象（Task 风险④）。④GT 页集仅 690/600 宽，宽≠690/600 的 KO 页 tile 参数化未覆盖（KO-TILE §9）。

### G3 · 数据集健全性与考卷完整性门【硬 Gate · 先决】

- **定义**：本轮评测所依据的数据集（train-v4 重切产物）与考卷的完整性断言——**先决门**：任何一项 FAIL，则本轮全部评测数字不作门判定（先决失效，G1/G2/G7 判 INDETERMINATE-先决失效如实登记）。
- **评测数据**：train-v4 全量 manifest+dataset 树（AC2 产物）；考卷 vol05 组定义（Task 禁止范围——本轮零改动）。
- **口径**：断言清单（全部沿 V1/V2/R3 三轮已实证的既有口径，零新造）：①组隔离违例=0（每 group 单 split）；②challenge 仅 densho810/vol05 组；③考卷原始 5 框坐标逐位=R2 final 出厂；④`dataset.yaml` names 双通道（字面行解析+pyyaml 独立解析）逐字=`SFX_CLASS_MAP`（`detection_sfx.py:137`）；⑤重切指纹按 `experiments/M2-SFX-DATA-INFRA/sfx_data_infra/splits.py:160` 算法可复现且 lock/summary 一致（seed=20261004，`splits.py:31`）；⑥考卷零重叠：own-manga/新增页与考卷页组名/样本 id/页图 sha256 三层零交集。
- **阈值（冻结）**：六项断言**全部零违例**。
- **判定规则**：**硬 Gate**——6/6=PASS；任何一项违例=FAIL 且触发先决失效语义。判定输出=逐项断言数字表。
- **阈值依据**：V1 §1（组隔离 0 违例双口径复算）、V2 §1.1/§1.2（指纹 `345deeb7…`、考卷零重叠三层断言）、R3 §5.3（指纹 `d57353b1…`、考卷 5 框逐位不动）——三轮全部 PASS 的既有门级断言，正式门原样收编。
- **已知限制**：①③两项目标值随 AC2 重切产物在 T3 当轮产出，断言本体（算法/口径）已冻结，目标值以 R2 出厂+R3 登记值为对照。

### G4 · 考卷覆盖门【directional】

- **定义**：登记考卷+扩展集对 BJ 主攻形态与新回填形态的覆盖充分性，产出「形态×页×held-out 状态」覆盖矩阵；考卷是否随正集扩容重划=**用户/编排裁决项，本门只登记缺口不执行重划**（R3 §6.2 提案语义顺延）。
- **评测数据**：BJ 域全部 complete 页（R3 时点 8 页 18 框）+AC2 补画转正页；train-v4 split 归属。
- **口径**：形态标注沿 R3 §5.2 对照表（竖排毛笔假名/斜置粗毛笔片假名/手术室潦草拟声/竖排字块/竖排拟声等）；held-out=challenge 侧。
- **阈值（冻结）**：无 PASS/FAIL（directional 门）。**登记义务**：矩阵必须逐形态给出「有无独立考题」结论；已知缺口=R3 §6.2「考卷对新回填形态（pre-bj16 回填 3 框、pre-bj28/29 新形态）零覆盖」必须原样入表。
- **判定规则**：directional 记录；产出结论仅供 G1 判读外推边界与 T4/后续轮考卷重划裁决引用。
- **阈值依据**：R3 §6.2 + V1 §7.1（challenge 复用 vol05 组、指纹与判定链可溯源）。
- **已知限制**：矩阵的「形态」分类为人工/AI 归类，非受控词表；覆盖判断不改变 G1 硬判据集。

### G5 · 生产序列契约门【硬 Gate】

- **定义**：候选权重导出物可进入生产 `detection_sfx.py` 推理通道且契约面零漂移——T4 替换的链路可行性前提。
- **评测数据**：每个候选权重（v2a/v2b 及 T3 轮如重训则含新产物）的 best.onnx 导出物。
- **口径**：`YOLO.export(format="onnx", imgsz=1024)` → 生产 `_build_engine` → `SfxDetectionProvider.detect` 全链（T0 §5 `export_smoke.py` 模式）；进程内重指纪律（§3.4）。
- **阈值（冻结，五项断言）**：①SHA 门先证在位：外来 onnx 按生产 pin 加载被 `PROVIDER_FAILED` 正确拒跑；②进程内重指全链冒烟 **EXIT=0**，零 src、生产 pin 逐字节零改动；③names metadata 逐字=`{0: 'bubble', 1: 'panel', 2: 'sfx', 3: 'text'}`；④imgsz=`metadata_parsed` 且 =1024；⑤输出张量形 `(1, 40, N)`（4 xywh+4 cls+32 mask）。
- **判定规则**：**硬 Gate**——5/5=PASS；任何一项不成立=FAIL（该权重丧失替换候选资格）。
- **阈值依据**：T0 §5（AC4 EXIT=0、类面零漂移）、V1 §3、V2 §3（两版 sha_gate.fired 先证+EXIT=0）——三轮全过，正式门原样收编。
- **已知限制**：NMS 解析链注入（T0 `nms_chain_probe.py`）仅进程内验证，非持久化测试；门语义由断言链单次运行产出，须留 raw JSON/console。

### G6 · 合成-真实域差与标签噪声归因门【directional】

- **定义**：把 G1/G2 的评测差值按「样本量 / 合成-真实域差 / 标签噪声 / GT 循环性」四层归因登记，产出归因登记表——**无 PASS/FAIL**；本门存在的理由=V1 §6 DSH r1 P3-3「样本量不足为首要瓶颈」是方向性假设、并列解释未排除，正式门必须把归因强度与判定数字分离。
- **评测数据**：G1/G2 全部逐框明细+训练数据构成（train-v4：synthetic 324/own-manga 558 partial 140+pseudo 418/BJ real 正集 8 页 18 框）。
- **口径**：每条评测差值至少标注一层归因并给出证据行；禁用「显著」；归因分层义务清单（冻结）——①own-manga 418 自蒸馏框不可与 BJ 正集同权（R3 §6 DSH P3-4：densho810 64 pseudo 不入 train vs own-manga 418 pseudo 带框入 train 的处置不对称）；②KO 长条页 6 页训练侧标签噪声（DSH P3-7）与 v2b tile 双差的方向性（KO-TILE §2）；③BJ 扩展 train 侧数字=记忆性（G1 限制③）；④chiqui7 循环性条目只入「GT 循环性」层（§3.5）。
- **阈值（冻结）**：无数值阈值；登记完备性要求=四层逐层有结论（含「本层数据不足无法归因」的如实结论）。
- **判定规则**：directional 记录。
- **阈值依据**：V1 §6、V2 §6（own-manga 框坐标=chiqui7 模型输出未手工收紧）、R3 §6、KO-TILE §9（v2b 噪声方向性非定量归因）。
- **已知限制**：归因为登记性推断，无消融实验支撑（V1/V2 均未做配比消融）；四层间可能混杂（如样本量与域差耦合）。

### G7 · 端到端损害门【硬 Gate】

- **定义**：新权重经生产序列进程内替换后，SFX→翻译链路无链路级退化——「损害」操作化为**链路故障面**（异常/契约违例/语义破坏），不含检测质量差异（那是 G1/G2 的对象，框集变化本身是新权重的目的）。
- **评测数据**：≥1 合成 manga 页+≥1 真实页（BJ17 页先例：`verification/M2-SFX-TRAIN-V1/raw/bj17-demo.json`）；候选权重+chiqui7 基线双侧。
- **口径**：沿 T0/V2 冒烟方式**零 src**——进程内重指（§3.4）→`SfxDetectionProvider.detect`→SFX 产物按现役语义流入翻译链入口（SFX mask/policy/translate 入口既有链路，`M2-SFX-TRANSLATE-ENTRY` 产物，只读调用）；同页同参下基线权重对照跑一遍。
- **阈值（冻结，三项硬判据）**：①全链 EXIT=0（无未捕获异常）；②`DetectionResult` 及下游输入契约合法（`class_filter=sfx`、`coordinate_space=page-global`，**fail-closed 语义保持**：0 候选=合法空输入非异常，T0 §5 先例）；③vs 基线同链对照：下游错误/异常/超时**新增数=0**。
- **判定规则**：**硬 Gate**——三条件同时成立=PASS；任一不成立=FAIL。SFX 输入框集差异（数量/conf 分布/位置）directional 如实登记，不作 PASS/FAIL。
- **阈值依据**：Task 合同 AC1 原文「端到端损害门（新权重经生产序列替换后 SFX→翻译链路无退化，进程内重指沿 T0/V2 冒烟方式零 src）」；T0 §5 + V2 §3 冒烟链先例。
- **已知限制**：冒烟页样本量极小（≥2 页），链路级结论不外推为全量质量结论；「无退化」不覆盖性能/时延回归（T4 部署面另行测量，KO tile 化成本登记见 KO-TILE §7）；翻译链下游若因非 SFX 原因故障，须分离归因后重跑。

### G8 · 部署门【硬 Gate · checklist】

- **定义**：候选权重作为生产替换物的部署审计清单——ONNX/sha/来源/许可四面逐项结算；**v2b 基座 `license: other` 未审计在本门结算**（Task 合同 AC1 原文）。
- **评测数据**：候选权重 best.onnx+训练产物链（基座 .pt→run log→导出物）；基座许可证据快照（v2b：`verification/M2-SFX-TRAIN-V2/raw/b-base-{readme-snapshot.md,args.yaml,snapshot-metadata.json}`）。
- **口径**：checklist 逐项出具证据（路径+值），参照 V1 §7.2 / V2 §7.2 的 T4 材料清单权威化：
  1. **产物 sha**：best.onnx sha256 登记且盘上复算一致（v2a=`27d162e9…` / v2b=`944e8114…` 参考）；
  2. **来源链可溯源**：基座 .pt sha256（v2a=`1caa81c0…` AGPL / v2b=`1f0fd609…` other）→训练 log `TRAIN_RESULT_JSON`→导出物 sha，全链无断点；
  3. **metadata 契约**：引用 G5 结果（names/imgsz/张量形）；
  4. **许可结算**：v2a 基座 AGPL-3.0——用户 2026-10-04 许可降权备案覆盖沿 T0 §6；**v2b 基座 `license: other` 审计执行并出具 PASS/FAIL**（含 Manga109-s 衍生声明核验：「does not include or grant rights to the original Manga109-s images or MangaSeg annotations」）——**审计 FAIL 则该权重不得列为切换候选**；衍生权重 gitignored 未入库未分发声明；
  5. **pin 替换语义**：`SFX_WEIGHTS_SHA256`（`detection_sfx.py:110-112`，现值 d87389af…）单值替换方案+`SFX_HF_REPO`/`SFX_HF_REVISION`（`:108`，现指 chiqui7@7f5f5c04）来源字段处置方案（HF 发布通道 or 本地发布通道登记，V2 §7.2.3）；
  6. **回退语义**：恢复 d87389af 值+旧权重文件在位（chiqui7 权重随包 NSIS 通道不变，V2 §7.2.6）；
  7. **训练数据许可备案引用**：own-manga=用户自有（2026-10-04 备案）、densho810 报告义务（2026-11-02 窗口）、HF webtoon/P&C 沿二次裁决备案。
- **阈值（冻结）**：7 项全部出具证据且无未决项=PASS；第 4 项对**拟切换候选权重**的审计结论必须为 PASS（FAIL 即丧失候选资格并在 T4 终稿如实名）；非候选权重的审计 FAIL 只登记。
- **判定规则**：**硬 Gate**（对候选资格）；checklist 产出即 T4 材料终稿的部署章节输入。
- **阈值依据**：T0 §6+§7.4（pin 更新属 src 变更留 T4）、V2 §6（v2b license:other 未审计「上生产面前须补审计」）、V2 §7.2（切换语义六点）。
- **已知限制**：许可审计为文档证据链审计（快照+上游声明），非法律意见；AGPL 衍生权重的合规义务（公开对应源或购 Enterprise License，T0 §6）持续适用；densho810 义务窗口晚于 T3，部署时点核查归 T4。

## 5. 变更登记规则（冻结机制）

1. **冻结时点**：本文档 v1.0 随本 commit 进入 Git 即冻结；AC4 评测执行开始后**不得修改**已判定门定义。
2. **评测执行前的变更**：在本文件追加「变更登记」段（§6 版本表新行：版本号/日期/变更门/理由/影响范围），由 Owner 提交、Reviewer（DSH，非作者）确认后生效；禁止覆盖旧文本。
3. **评测执行后的变更**：仅允许追加新版本段且**原判定与原定义双轨保留**（新版本只对未判定门生效；已出数字的门定义回溯变更=无效），并在 Task 与 Handoff 显式登记。
4. **门判定引用规则**：AC5 判定文档须逐门标注「依据 gate-definition v1.0 §4.Gx」；引用非冻结版本定义的判定无效。
5. 本文档零 src：变更只发生在本文件与 Task/Handoff；生产代码/契约面任何改动都超出本 Task 授权范围（Task 禁止范围）。

## 6. 版本表

| 版本 | 日期 | 变更 | commit |
|---|---|---|---|
| v1.0-frozen | 2026-10-05 | 初版：G1-G8 合同级定义冻结（G1/G7/G8 对齐提案语境，G2-G6 权威化新定，门数登记理由 §2） | gatedef(GATE-T3) |

## 7. 证据索引

| 类别 | 路径 |
|---|---|
| 生产契约 | `src/infrastructure/providers/detection_sfx.py:108/110-112/118/121/137/138`（本 worktree grep 实测，行号与 ①-⑤ 报告引用一致） |
| 定义输入 ①-⑤ | §1 表全部路径（本 worktree 在位验证：`ls verification/M2-SFX-TRAIN-V{1,2}/ verification/M2-KO-TILE-CALIB/ verification/M2-SFX-ANNOTATE-R3/` 实测） |
| 匹配/重指先例 | `experiments/M2-SFX-TRAIN-V2/eval_v2.py:47/68-97/129-131/179/197-201`；`experiments/M2-KO-TILE-CALIB/tile_calib.py:374/381-382/443-444` |
| 指纹算法/seed | `experiments/M2-SFX-DATA-INFRA/sfx_data_infra/splits.py:31/160`（本 worktree grep/sed 直验；R3 报告记 `:30` 系彼 worktree 行号偏移，语义同一常量） |
| V2 评测 raw | `verification/M2-SFX-TRAIN-V2/raw/eval-{v2a,v2b,chiqui7-rerun,comparison}.json`（ls 实测在位） |
| KO 矩阵 raw | `verification/M2-KO-TILE-CALIB/eval-matrix.json` + `raw/`（ls 实测在位） |
| v2b 许可快照 | `verification/M2-SFX-TRAIN-V2/raw/b-base-{readme-snapshot.md,args.yaml,snapshot-metadata.json}`（ls 实测在位） |
