# M2-QUAL-DETERM-CALIB：reading_order 对齐译文相似度校准报告（F5）

- Task：[M2-QUAL-DETERM-CALIB](../../doc/tasks/M2-QUAL-DETERM-CALIB.md) · 分支 `agent/zcode/M2-QUAL-DETERM-CALIB` · 日期 2026-10-01
- 生成方式：`experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py`（stdlib，确定性）——本报告与 `calibration.json` 均为脚本产物
- 数据源（只读）：`verification/M2-TA3-B/phase2/summaries/qual-K11{,.rerun}.json、qual-BJ02{,.rerun}.json`（各 run 的 translate_details × regions，Run2 后 DB 译文）
- 证据强度：**directional evidence only: n=2 calibration cases from the first quality run (M2-TA3-B2), remote DeepSeek provider, 2026-10-01; not a production determinism conclusion**
- 口径修订来源：M2-QUAL-DETERM-CALIB + 用户裁决 2026-10-01（全部进行）

## 1. 方法（Gate 定义）

1. **对齐键 = reading_order**（方法学事实，TA3-B2 r1 R1 登记：region_id 每 run 重新生成，同 bbox 两轮 uuid 不同；region_id 只用于把 translate_details 关联到本 run 的 regions[].reading_order）。两次 run 的 reading_order 集合不一致时脚本 fail-closed 退出。**对齐假设交叉校验（dsh r1 R1）**：逐 reading_order 断言两 run 的 bbox 逐字段一致（region 几何跨 run 再生稳定——K11 13/13、BJ02 5/5 实测一致），不一致视为对齐假设被破坏（同集合置换无法被键集合相等检查发现），fail-closed 退出；translate_details 覆盖 regions[]亦为 fail-closed（缺失 region 的 reading_order 列表落盘于 FATAL 消息）。
2. **相似度 = 1 − Levenshtein/max_len（字符级，stdlib）**；Levenshtein 与归一化复刻自项目既有 `experiments/M2-TA3-B/measure_cer.py`（不跨目录 import，M2-TA3-B 在本 Task 禁改面）。
3. **双口径**：`raw`（译文原串，复现 quality-report F5 的 K11 "7/11 非空对浮动"观察）与 `normalized`（quality-thresholds §0 归一化：去全部空白、…≡...、casefold——与项目 CER 同口径，换行/空格级差异不计入翻译不稳定）。**Gate 口径 = normalized**，raw 作附报。空对判定基准统一为 normalize 后空串（dsh r1 R6），status 与 similarity 不会在仅空白差异上互相矛盾。
4. **空译文对规则（登记口径，非临时约定）**：双方空 → 相似度 1.0（`empty_both`，两次 run 行为一致：都无译文）；单方空 → 相似度 0.0（`empty_one_side`，run 级行为变化=最大不稳定）。实测数据中仅出现前者（K11 ro=9 OCR 空文本、ro=13 SFX SKIP，两次 run 双侧均空）。**覆盖前置（dsh r1 R2）**：非空对 n≥1 方可判定，否则 **NO_DATA**——全空跑（如 provider 整体失效返回空译文）在相似度口径下会平凡 PASS（全部 empty_both=1.0），翻译覆盖度由 §7 translate 评分 Gate 兜底，相似度 Gate 不对覆盖度负责；region_count=0 的 case（如 K01 两侧均 0 region）贡献 0 对，按同一 NO_DATA 口径豁免、不阻断整体 Gate 但单独登记（dsh r1 R3，与 R11 零 region 豁免同口径）。
5. **语义边界（绑定表述）**：本 Gate 度量的是**翻译稳定性**（同输入同模型重跑下译文的词汇级一致性），**不是渲染/导出复现性**。K11 export 字节差异的根因在 Run1 层（未逐层隔离），不在本度量范围内；「export 字节逐位一致」对 mock/deterministic provider 场景仍然有效并继续执行（BJ02 Run1 渲染产物两次逐位一致为上界参照）。

## 2. 实测分布

| case | 对数 | 非空对 | 口径 | 相同对 | 浮动对 | min | median | P10 | Gate 判定 |
|---|---|---|---|---|---|---|---|---|---|
| K11 | 13 | 11 | raw(全部) | 6 | 7 | 0.75 | 0.9474 | 0.75 | — |
| K11 | 13 | 11 | normalized(全部，Gate 口径) | 8 | 5 | 0.75 | 1.0 | 0.75 | **PASS** |
| BJ02 | 5 | 5 | raw(全部) | 4 | 1 | 0.75 | 1.0 | 0.85 | — |
| BJ02 | 5 | 5 | normalized(全部，Gate 口径) | 4 | 1 | 0.75 | 1.0 | 0.85 | **PASS** |
| 合并（K11+BJ02） | 18 | 16 | raw(非空) | 8 | 8 | 0.75 | 0.9737 | 0.75 | — |
| 合并（K11+BJ02） | 18 | 16 | normalized(非空) | 10 | 6 | 0.75 | 1.0 | 0.75 | — |

关键读数：**浮动对（normalized，Gate 口径）K11 n=5、min=0.75、median=0.75；BJ02 n=1（min=median=0.75）；合并 n=6、min=0.75、median=0.75**——实测浮动幅度全部落在 [0.75, 0.875]，是 min 阈值（0.7）的锚。全部对口径：K11 raw 浮动 7/11 非空对（复现 quality-report F5 已登记的 7/11 观察；normalized 降为 5/11——ro=5 换行位移、ro=10 空格差异被 §0 归一化吸收，浮动对全部为 1 编辑差）；**BJ02（该样本两次 Run1 渲染产物逐位相同=上界参照）Run2 译文仍有 1 对浮动**（`所谓强大`→`所谓强啊`，similarity 0.75）——Run1 渲染逐位与 Run2 译文浮动是两个独立层，与 quality-report §5 机制结论一致。

## 3. 逐对清单（normalized < 1.0 标 **浮动**）

### K11（ko，n=13）

| reading_order | type | 译文（首跑） | 译文（复跑） | sim(raw) | sim(normalized) |
|---|---|---|---|---|---|
| 1 | speech | 胡萝卜？ | 小萝卜？ | 0.7500 | 0.7500 **浮动** |
| 2 | speech | 小萝卜！ | 胡萝卜！ | 0.7500 | 0.7500 **浮动** |
| 3 | speech | 胡萝卜？ | 胡萝卜？ | 1.0000 | 1.0000 |
| 4 | speech | 胡萝卜？！ | 胡萝卜？！ | 1.0000 | 1.0000 |
| 5 | speech | 本以为\n没必要做到\n这种地步 | 本以为\n没必要\n做到这种地步 | 0.8571 | 1.0000 |
| 6 | speech | 胡萝卜？！！！ | 小萝卜？！！！ | 0.8571 | 0.8571 **浮动** |
| 7 | speech | 咦？床底下也有\n你？ | 咦？床底下也有\n你？ | 1.0000 | 1.0000 |
| 8 | speech | 胡萝卜！ | 小萝卜！ | 0.7500 | 0.7500 **浮动** |
| 9 | speech | (空) | (空) | 1.0000 | 1.0000 |
| 10 | speech | 咔咯咔咯咔咯\n咔咯沙沙沙沙\n沙沙沙沙 | 咔咯咔咯咔咯\n咔咯沙沙 沙沙\n沙沙沙沙 | 0.9474 | 1.0000 |
| 11 | speech | 哦 我的\n泰阳！！ | 哦 我的\n泰阳阳！！ | 0.9000 | 0.8750 **浮动** |
| 12 | speech | 咕噜噜 | 咕噜噜 | 1.0000 | 1.0000 |
| 13 | sfx | (空) | (空) | 1.0000 | 1.0000 |

### BJ02（ja，n=5）

| reading_order | type | 译文（首跑） | 译文（复跑） | sim(raw) | sim(normalized) |
|---|---|---|---|---|---|
| 1 | speech | 别说得那么冠冕堂皇 | 别说得那么冠冕堂皇 | 1.0000 | 1.0000 |
| 2 | speech | 一定要做手术…… | 一定要做手术…… | 1.0000 | 1.0000 |
| 3 | speech | 所谓正确，就是软弱 | 所谓正确，就是软弱 | 1.0000 | 1.0000 |
| 4 | speech | 所谓强大 | 所谓强啊 | 0.7500 | 0.7500 **浮动** |
| 5 | speech | 就是说不行 | 就是说不行 | 1.0000 | 1.0000 |

注：所有实测浮动对均为 **1 次编辑差**（单字替换或插入，如 `胡萝卜？`→`小萝卜？`、`所谓强大`→`所谓强啊`），无结构性语义漂移样本——这是 n=2 校准的核心局限（见 §6）。

## 4. Gate 阈值建议（AC2）

**建议 Gate（normalized 口径）：`median ≥ 0.95` 且 `min ≥ 0.7`**（同 case 两次 run 全部对齐对，含空对规则）。

推理链（全部锚定实测分布，非拍脑袋）：

1. **min ≥ 0.7**：实测最坏浮动对 = 0.75（4 字译文单字替换，K11 ro=1/2/8 与 BJ02 ro=4）。同输入同模型重跑必须 PASS → 阈值须 ≤0.75；取 0.75 − 0.05 = **0.70**，**0.05 为绝对值余量**（dsh r1 R4，与 thresholds 写法统一——不是「一个字符」：4 字锚串上 1 编辑差=0.25，0.05 仅为其 1/5；对 20 字译文 1 编辑差才恰为 0.05）。反向锚：40% 字符替换的合成漂移相似度 ≈0.5635（min 0.5）→ FAIL；3 字及以下译文的单字浮动（2/3≈0.667）也会 FAIL——fail-closed 方向，见 §6 局限。
2. **median ≥ 0.95**：实测 median = 1.0（同输入同模型重跑下多数 region 译文逐位相同）。0.95 的语义 = 允许少量采样浮动存在、但多数 region 浮动（系统性漂移，如 prompt/provider 变更）即 FAIL。18 对分布下的精确边界（以实测浮动幅度 [0.75, 0.875] 计，**在本校准样本的译文长度分布下**——浮动串长 4–16 字，dsh r1 R5）：浮动 ≤8 对（<50%）时 median 恒=1.0（PASS）；浮动 ≥9 对（≥50%）时 median ≤(0.875+1)/2=0.9375 <0.95（恒 FAIL）——即约半数 region 浮动即触发 median gate。该边界不外推到显著更长的译文：长译文 1 编辑差相似度更高（20 字串 1 编辑=0.95），median 腿对低幅系统性漂移的分辨力随译文长度下降（§6 局限）。
3. **判别力合成对照（无自然 FAIL 样本的替代证据）**：对实测译文施加确定性字符扰动（seed=20261001，非 FAIL 实证、仅演示阈值判别力）。三个探针各演示一个维度：**single_char_ge4**（实测量级浮动：每串 1 编辑差）逐对全部 ≥0.75 → min gate 不触发（阈值容纳实测浮动幅度），但因探针强制全部对浮动，median=0.857 → 完整 gate FAIL（即「全部 region 系统性浮动」被 median leg 抓住）；**drift_40/drift_70**（漂移代理）min 跌破 0.70 → min gate 抓住结构性漂移：

| 合成对照 | n | min | median | min-gate(≥0.70) | 完整 gate | 演示结论 |
|---|---|---|---|---|---|---|
| single_char_ge4 | 15 | 0.75 | 0.8571 | **PASS** | **FAIL** | 实测浮动量级逐对 PASS；全 region 浮动 → median leg FAIL |
| drift_40 | 16 | 0.5 | 0.5635 | **FAIL** | **FAIL** | ~40% 字符替换（漂移代理）→ min leg FAIL |
| drift_70 | 16 | 0.2 | 0.2857 | **FAIL** | **FAIL** | 严重漂移 → 双维度 FAIL |

与实测分布合起来的判别力闭环：实测「少数对浮动」（K11 5/13、BJ02 1/5）→ 完整 gate PASS（同输入重跑必须 PASS 的要求满足）；「全部对 1 编辑浮动」（系统性轻微变化）→ median leg FAIL；「结构性漂移」→ min leg FAIL。

4. **对实测分布的判定**：K11 → **PASS**；BJ02 → **PASS**（上界参照：其 Run1 渲染产物逐位一致）。即：已知的「同输入同模型重跑」在该 Gate 下 PASS；「明显漂移」（合成 40%+ 字符替换）FAIL。

## 5. 语义边界与双轨表述（绑定）

- 本 Gate（相似度）适用于 **remote/随机采样翻译 provider** 的确定性验收；度量翻译稳定性，不度量渲染/导出复现性。
- **mock/deterministic provider 场景维持 export 字节逐位一致**（TA3-A 框架原口径不变）；BJ02 两次 Run1 渲染产物逐位相同是该口径的实际先例与相似度度量的上界参照（Run1 渲染逐位 ≠ Run2 译文逐位——BJ02 自身 Run2 译文仍有浮动对）。
- K11 export 哈希不一致（Run1 层根因未逐层隔离）**不**由本 Gate 解释或修复；Run1 层确定性属后续独立问题（§6 局限）。

## 6. 局限登记（AC4）

1. **n=2 case 校准**：仅 K11（ko 13 region）与 BJ02（ja 5 region）一组重跑对；阈值 0.70/0.95 锚定在 18 对实测分布上，样本量不支持外推生产结论；后续 qualification run 应同时落盘逐对相似度以滚动校准。
2. **无自然 FAIL 样本**：实测浮动全部为 1 编辑差（无结构性漂移），判别力只能用合成对照演示（§4.3），不是漂移场景的实证。
3. **极短译文粒度边界（长度相关悬崖，dsh r1 R4）**：min 阈值对编辑数的容忍度与译文长度强相关——同一「多 1 编辑」在 4 字串上跌 0.25、在 20 字串上只跌 0.05：3 字译文单字浮动（≈0.667）会被 min≥0.70 判 FAIL（fail-closed 方向可接受，但会把「良性的单字采样差」误报为漂移）；4 字反例（实测锚串）：2 次编辑即 2/4=0.5 → FAIL，即 0.05 的绝对值余量在锚长度上容不下第二个编辑差；实测最短浮动串为 4 字。
4. **Run1 层相似度未测**：K11 export 差异根因在 Run1（批量翻译/inpaint/render，未逐层隔离，scratch db 已清理）；本 Gate 只覆盖 Run2 后 DB 译文层的稳定性。
5. **归一化口径依赖**：normalized 口径吸收换行/空格差异（K11 浮动 7→5）；若产品语义认为换行位置也是译文的一部分，应引用 raw 口径附报。
6. **覆盖前置与全空跑盲点（dsh r1 R2/R3）**：空对规则下全空跑（两次 run 译文全空，如 provider 整体失效）相似度全部 1.0、可平凡 PASS 相似度 Gate——故 Gate 定义加非空对 n≥1 的覆盖前置（否则 NO_DATA）；翻译覆盖度（该译的没译）由 §7 translate 评分 Gate 兜底，相似度 Gate 不对覆盖度负责；region_count=0 的 case（本次校准集中的 K01 两侧均 0 region）贡献 0 对、按 NO_DATA 豁免，不阻断整体 Gate 但须单独登记——**ko webtoon 家族因此未被本次校准覆盖**（K11=ko P&C、BJ02=ja BJ）。
7. **median 腿分辨力随译文长度下降（dsh r1 R5）**：§4.2 的「浮动 ≥9 对恒 FAIL」边界以实测浮动幅度 [0.75, 0.875]（串长 4–16 字）为条件；更长译文上 1 编辑差的相似度更高（20 字串=0.95≥阈值），「全部 region 低幅浮动」的场景 median 腿可能 PASS——结构性漂移仍由 min 腿兜底，但 median 腿不是长度无关的系统性漂移检测器。
8. **词面口径的固有误报方向（dsh r1 R8）**：字符级相似度度量的是词面一致，不是语义等价——语义等价的合法重译（同义改写/整段重译）会被判低相似度 FAIL，而 remote 采样漂移的主形态恰是同义改写；即本 Gate 在「假 FAIL」（保守）方向系统性偏置，不会漏报词面漂移但会误报合法重译。未加同义改写代理探针：词面框架内无法可靠构造语义等价改写的确定性代理（任何字面扰动都改变词面），该维度的验证需语义度量（如回译/向量相似度），属后续独立工作、此处仅登记。

> **声明**：directional evidence only: n=2 calibration cases from the first quality run (M2-TA3-B2), remote DeepSeek provider, 2026-10-01; not a production determinism conclusion。
