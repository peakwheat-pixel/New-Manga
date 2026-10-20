# SEARCHABLE-PDF-CJK-1 独立 Review（ZCode）

- **Reviewer**: ZCode（非作者；实现者为 DSH）
- **日期**: 2026-10-20
- **范围**: `agent/dsh/SEARCHABLE-PDF-CJK-1`，`d1a5556cc..8593f81c6`（3 commits，+551/−1）
- **对象**: `src/infrastructure/export/qt_free.py`（`_embedded_font` 候选列表 2→4）、`tests/export/test_searchable_cjk_font.py`（5 测试）、`tests/export/test_searchable_font_cost.py`（2 测试）、`verification/SEARCHABLE-PDF-CJK-1/` 7 份证据
- **结论**: **approve_with_conditions**（2 项条件，见 F-1/F-2；均为小改，不需要返工架构）

## TL;DR

核心修复正确且足够：coverage-first 判据下加入 `malgun.ttf` 使纯韩文页命中韩文字体，ja/zh/latin 仍选 `msyh.ttc`，无回归（本机复跑 `tests/export` 11 passed；字体选择独立实测确认）。作者对第一版 skip 教训的处置、「判断被标记为判断」、AC3 标 PARTIAL，都是诚实的。333 字节极差经我独立复算闭合（≈83.5 B/页的页级元数据，与图像内容无关）。「不做子集化」的判断我**接受**。

两项条件：

1. **F-1（P2）**：AC4 守护测试只测 1/3 页，任务书「测试要求」明文「多页测试至少 5 页」；5 页数据只有一次性手工证据，且模块 docstring 自己写着「1, 3 and 5 times」而代码是 `for pages in (1, 3)`。
2. **F-2（P2）**：AC1 证据索引声称「真实韩漫页 600×18401 导出后 `text='안녕하세요 세계'` 可提取」，但 7 份已入库证据无一承载该实测；测试套件中也没有韩文的 compose→提取端到端（唯一端到端 `test_the_pdf_still_has_a_text_layer` 用的是日文）。任务书「真实页、四种语言各一条」未在韩文上满足。

另有一项必须修正的**证据口径**（F-5）：「子集化能降到约 10–50 KB」只在单页 5–9 字符场景成立；产品导出单位是整章，按我实测的字形分布应在 ~130 KB–870 KB。这个数字已被写进未来 Task 的建议 AC，照抄会把未来验收钉在错误预期上。

## 验证方法（本 Review 独立执行的）

1. 复跑 `python -m pytest tests/export -q` → **11 passed**（11.17s）。
2. **内存复放 AC4**（不落盘）：合成 1350×1920 噪声页（`os.urandom`，避免图像可压缩性干扰），`_compose_pdf` 同页 1/3/5 次，另测 5 页 50 个不同字符 vs 6 个字符。
3. **字体选择实测**：`_embedded_font("안녕 こんにちは")`、`_embedded_font("안녕하세요")`、`_embedded_font("안녕 你好")`。
4. **字形分布实测**：解析 `malgun.ttf` 的 `loca`/`glyf`，统计全部 11,172 个谚文音节字形大小。
5. 源码通读（`qt_free.py` 全文、两个测试全文、7 份证据全文、r40/r41 裁定与任务文档）。

未做分回滚实跑（避免改仓库文件）；「缺陷下 3 failed / 2 passed」经逻辑推演确认（见 §3.2）。

## §3.1 修复本身

**改动足够吗？——足够。** 判据是 `all(ord(char) in cmap for char in text if not char.isspace())`（qt_free.py:140），首个**全覆盖**者胜出，顺序只在多字体同时覆盖时决定赢家。实测确认：

| 输入 | 选中字体（按返回字节判定） |
|---|---|
| `안녕하세요`（纯 ko） | malgun，13,459,196 B |
| `안녕 こんにちは`（ko+ja 假名） | malgun，13,459,196 B |
| `こんにちは世界` / `你好世界` / `hello` | msyh（19,583,608 B，测试窗口断言） |
| `안녕 你好`（ko+zh 混排） | `ValueError` fail-closed —— 与 r40「混排 fail-closed」裁定一致 |

**有没有回归？——没有。** msyh 列首且覆盖 ja/zh/latin，这三个语种的赢家不变（`test_the_existing_languages_are_unchanged` + 11 passed + 上表实测双重确认）。ko+zh 混排的 fail-closed 是范围裁定内的预期行为，不是回归。

**malgunbd（粗体）加得对吗？——正确性无问题，但注意它几乎不可达。** 顺序保证只要 `malgun.ttf` 存在就永远轮不到 `malgunbd.ttf`（两者 cmap 覆盖相同，见任务文档实测表）；它只在「malgun.ttf 缺失而 malgunbd.ttf 存在」的机器上兜底。「没区分字重」在此设计下**不是缺陷**：文本层是 `3 Tr` 隐形渲染（qt_free.py:96），仅供提取/搜索，粗细无用户可见影响；`widths` 从实际选中的字体读取（qt_free.py:147），与该字体自洽。无害，保留合理。

## §3.2 测试有效性

**残留 skip？** `test_searchable_cjk_font.py` 的 5 个测试**无任何 skip**——第一版的缺陷触发 skip 已删净，docstring 把教训写清楚了（「the skip fired precisely because the defect was present」），这个反省和处置是对的。`test_searchable_font_cost.py:27` 有 `pytest.importorskip("pymupdf")`——这是**依赖守卫**（触发条件是环境缺库，不是被检缺陷），性质不同、可接受；但若 CI 不装 pymupdf，AC4 的守护会静默消失，建议 CI 依赖清单钉住 pymupdf（F-4）。`_find_page` 找不到页时用 `pytest.fail` 而非 skip——正确。

**宽松断言？** `test_korean_text_embeds` 的 `len(raw) > 10_000` 单看是弱的，但同函数后续有 `chars` 去重数、`glyphs` 等长、`widths > 0` 三重强断言，组合判别力足够。`test_korean_does_not_fall_back_to_a_font_without_hangul`（同文本选不同字体）+ `test_a_character_nobody_covers_still_fails_closed`（异常守卫）把「谓词退化成『文件存在』」和「异常消失」两个逃逸路径都钉住了。

**15,000,000 阈值可靠吗？——在当前候选集内判别充分，但它是大小代理而非身份断言。** 候选集四者的返回字节：msyh 重建 face ≈19.58 MB、malgun 13.46 MB、malgunbd ≈12.6 MB、arial 1.05 MB——唯一 >15 MB 的是 msyh，所以「>15M」当前**等价于**「选了 msyh」，恰好防住本 Task 引入的唯一回归方向（malgun 抢赢 CJK 表意文字）。弱点：若未来候选加入 simsun（18.3 MB）/msjh（21.4 MB）这类同量级字体，断言会静默放行换字体。建议升级为字节同一性断言（F-3）：`_embedded_font(text)[0] == _load_ttf(font_dir / "msyh.ttc")[0]`（TTC face 重建是确定性的，此断言可行）。

**分回滚声称（缺陷下 3 failed / 2 passed）**：逻辑推演确认。缺陷下 `_embedded_font("안녕…")` 必抛 ValueError，三个韩文测试（`test_korean_text_embeds`、`test_korean_and_japanese_together`、`test_korean_does_not_fall_back…`）全部直接失败；`test_the_existing_languages_are_unchanged` 与 fail-closed 测试不受影响。与作者实测一致。

## §3.3 AC4 测量

**333 字节该不该解释？——该，现在也解释掉了。** 我用合成噪声页独立复放：overhead = 12,408,209 / 12,408,385 / 12,408,543——与作者真实页数据（…210/…385/…543）仅差 1 字节，证明该常数与图像内容完全无关。逐页增量 83.5 B/页，构成可算：每页页对象的 `/Font << /F0 N 0 R >>` 资源字典 ≈22 B + 每页 BT/ET 文本 content 压缩后 ≈60 B + `startxref`/xref 偏移的十进制位数增长。作者「可由页面对象与 xref 解释」的猜测**方向与量级都对**，本 Review 已将其从猜测变为复算。

**同一页重复 N 次是否掩盖「不同页不同字体」？——不掩盖，因为「每页各自选字体」这个情况在架构上不存在。** `_embedded_font` 在 qt_free.py:43 对**全文档所有页所有 region 的文本 join 后调用一次**，在页循环（L73）之前——一次调用、一个字体、要么全覆盖要么 ValueError。作者的理解（全文档一次）**正确**。重复同页 vs 异页异字符的真实差异我实测了：5 页 50 个不同字符 vs 同 5 页 6 个字符，overhead 仅 +474 B（≈11 B/distinct 字符，来自 CIDToGIDMap +2 B/字符、ToUnicode bfchar ~20 B/字符、W 数组，压缩后）——远小于 333 B 的页级噪音，不构成字体级成本。唯一被同页重复略过的是整章 distinct 字符集更大带来的映射表增量，量级 <1 KB/百字符，不影响「常数开销」结论。

（但注意 F-1：守护测试只到 3 页，且 docstring 与实现不一致。）

## §3.4 AC3 的处置

**「判断」被恰当标记了吗？——是。** `ac3-subsetting-feasibility.md` §五 原文明确写「这句『高于……在当前阶段的价值』是一个判断，不是事实。所以它应该被 review，而不是被当作结论」，§八 列了五项「明确未做」。标记与边界都诚实。

**PARTIAL 标对了吗？——对，维持 PARTIAL。** 按 r41 §2 定稿口径，AC3 的证据分支是齐的（实测体积、未子集化声明、非许可的技术理由+原型依据）；但「体积实际下降」未发生、且决策本身是待审判断——PARTIAL 是诚实标注，不应升 MET。

**本 Review 对该判断的裁定：接受「不在本 Task 顺手做子集化」。** 理由与作者一致且经 r41 §3 背书：它改变产品输出格式、需要跨阅读器验证（本机无桌面阅读器是已登记的限制 V3）、需要一个字体子集→嵌入→提取→字形正确的完整往返测试——这不是修 bug 的旁边能顺手完成并自信验收的。独立立项的建议正确。

**「10–50 KB」的声称可靠吗？——不足以按当前措辞支撑；单页成立，整章差一到两个数量级。这是 AC3 证据里真正的空洞。** 我实测 `malgun.ttf`：全部 11,172 个谚文音节字形**均非空**，大小 110–886 B，均值/中位 426 B。含 loca/hmtx/cmap/表目录等配套（固定 ~1.1 KB + ~12 B/字形）的子集估算：

| distinct 字符数 | 子集字体估算 | 对应场景 |
|---:|---:|---|
| 6 | ~3.7 KB | 原型测的单页（`안녕하세요`） |
| 50 | ~22.9 KB | — |
| 100 | ~44.7 KB | — |
| 500 | ~219 KB | 整章漫画的量级 |
| 2,000 | ~873 KB | 长册/多册 |

结论分两半：

- 对**原型实际测的场景**（一页 5–9 个字符），「10–50 KB」成立且**偏保守**（真实约 4–6 KB）——作者的自我怀疑（loca/hmtx/cmap/表目录成本）方向对，但那些配套是 ~1 KB 固定 + ~12 B/字形，量级上**不是**主要误差源。
- 真正的洞是**外推场景**：产品导出单位是**章**（`ExportRequest.pages` 是整章页列表），一册几百页的 distinct 字符是数百到上千，子集会是 **~130 KB–870 KB**。`ac3-subsetting-feasibility.md` §六 把「体积与预期量级相符（约 10–50 KB）」写进了未来 Task 的建议 AC——照抄会把未来验收钉在错误预期上。「四个数量级」的说法对单页成立，对整章是 1.5–2.5 个数量级（12.4 MB → ~0.2–0.9 MB）——收益仍然巨大，「值得独立立项」的结论不变，但数字口径必须修正（F-5）。

原型方法本身（glyf/loca/cmap 解析 + 复合字形递归、只统计字节不重建表）对**数量级估算**是足够的；作者已在 §八 如实声明「只统计了字节，未重建表」。

## §3.5 硬编码字体 = 环境假设？

**是环境假设，但不是本 Task 引入的新类别。** 既有设计本来就硬编码 `msyh.ttc`——它只在中文 Windows 预装；一台 en-US Windows 既没有 msyh 也没有 malgun，ja/zh/ko 全部 fail。本 Task 把可用的机器范围从「中文 Windows」扩到「中文或韩文 Windows」，fail-closed 语义全程未动。r41 §4 也已明示「不得据此推定其他机器安装了微软雅黑或其他字体」——裁定者对此知情。

**fail-closed 是对的。** 抛 `ValueError` 好过嵌入缺字字体产出「看起来成功、提取出 boxes/乱码」的 PDF（`test_korean_does_not_fall_back…` 的 docstring 把这个更坏结局说得很清楚），且该行为有测试钉住。

**产品期望的错误呈现——当前不达标，但不在本 Task 范围。** `"no installed embeddable font covers searchable PDF text"` 不指明缺哪种文字、哪些字符、用户该装什么。作为内部异常可以；作为用户可见错误不可操作。错误如何冒泡到 React UI（可读消息、指明缺谚文/建议安装含谚文的字体、或降级为纯图片导出的选项）属于导出错误呈现的集成层设计，应由 Codex 立项，不应在本 Task 顺手做。

**硬编码 vs 探测——当下硬编码是正确的最小改动；长期应登记候选 Task。** 硬编码：零新依赖、确定性、可测试、失败语义清晰。探测（扫描 `%WINDIR%\Fonts` 全目录解析 ttf/ttc cmap）：能覆盖 Noto Sans KR/Dotum/Batang 等非微软字体，健壮性更好，代价是一次性几百 ms 到数秒的解析（可缓存），是合理的后续演进。另一条路是随包附带许可清洁的开源 CJK 字体（体积 +40 MB 量级 + 许可审查，需独立立项；随包不算 AC6 禁的「网络下载」，但须 Codex 冻结范围）。**建议登记后续候选，不阻塞本交付。**

**一个测试可移植性的代价要说破**：`test_korean_text_embeds` 等在无 malgun 的机器上会**红**——作者 docstring 明示这是有意的（「the test fails and says the font inventory needs looking at」）。这与删 skip 的立场一致，方向正确；代价是 CI 必须固定在有这些字体的 runner 上，否则韩文测试预期失败。这是上述环境假设的直接后果，记录在案即可（N-4）。

## 发现清单

| # | 级别 | 内容 | 处置 |
|---|---|---|---|
| F-1 | **P2（条件）** | AC4 守护测试 `test_searchable_font_cost.py:94` 只测 `(1, 3)` 页；任务书「测试要求」明文「多页测试至少 5 页」；模块 docstring 写「1, 3 and 5 times」与实现不一致。5 页数据只有一次性手工证据，不是回归守护 | 改 `for pages in (1, 3, 5)`（+ 调整断言覆盖三组），一行级改动 |
| F-2 | **P2（条件）** | AC1 证据索引声称「真实韩漫页 600×18401 导出后 `text='안녕하세요 세계'` 可提取」，但 7 份入库证据无一承载该实测；测试套件中韩文无 compose→提取端到端（唯一端到端 `test_the_pdf_still_has_a_text_layer` 用日文）；任务书「真实页、四语各一条」在 ko 上未满足 | 补一个 ko 真实页端到端测试（模式照抄 text_layer 测试，用 `韩漫_KO` 素材），或把该实测落成证据文件并让 AC1 索引指向它 |
| F-3 | P3（建议） | `>15_000_000` 是大小代理断言：当前候选集内判别充分，未来加入 simsun/msjh 等同量级候选会静默失效 | 升级为字节同一性断言（与 `_load_ttf(font_dir/"msyh.ttc")[0]` 比较） |
| F-4 | P3（建议） | `importorskip("pymupdf")` 在 CI 缺库时静默吞掉 AC4 两个守护测试 | CI 依赖钉 pymupdf |
| F-5 | **P3（须修正措辞）** | 「子集化能降到约 10–50 KB」只在单页 5–9 字符场景成立；整章（数百–上千 distinct 字符）实测估算 ~130 KB–870 KB。该数字已被写进 `ac3-subsetting-feasibility.md` §六 的未来 Task 建议 AC | 未来立项引用时改为按 distinct 字符数缩放的口径（~426 B/字形 + ~12 B 映射 + ~1.1 KB 固定）；本 Task 内不需要改代码 |
| N-1 | 观察 | 333 B 极差已由本 Review 独立闭合：83.5 B/页（/Font 资源字典 ~22 B + 压缩后 BT/ET content ~60 B + 偏移位数），合成页复现值与真实页仅差 1 B | 无需行动 |
| N-2 | 观察 | 字体选择实测：纯 ko 与 ko+ja 均选 malgun；ko+zh 混排 fail-closed，与 r40 裁定一致 | 无需行动 |
| N-3 | 观察 | `malgunbd.ttf` 因顺序设计几乎不可达（仅 malgun 缺失时兜底），无害；不可见文本层的字重差异无用户可见影响 | 无需行动 |
| N-4 | 观察 | 韩文测试在无 malgun 的机器上预期红（作者明示有意）；CI runner 需固定字体清单 | 登记，随 §3.5 的字体发现候选 Task 一并考虑 |
| N-5 | 观察 | cost 测试把临时 PDF 写进 `test_assets/comic_golden_suite/日漫_JA/...` 源目录旁再删（finally 清理）；进程被杀会残留 `_ac4_*.pdf` 在资产树 | 可选：改写到临时目录 |
| N-6 | 观察 | 任务 frontmatter 仍 `status: proposed`、owner/delivery_head 空——交付生命周期未收口（AC 表已打 MET 与之矛盾） | 归 Codex 按协作协议 §4 收口，不在本 Review 范围 |

## AC 逐项核验

| AC | 作者标注 | 本 Review 核验 |
|---|---|---|
| AC1 韩文可用 | MET | 修复正确（实测 malgun 命中）；但**证据落地有缺口**（F-2），条件闭合后成立 |
| AC2 纯语种页可提取 | MET | font 级四语覆盖 + ja 端到端；ko 端到端缺（并入 F-2） |
| AC3 体积与子集化 | PARTIAL | **维持 PARTIAL**；判断被接受；「10–50 KB」口径须修正（F-5），不影响「不做」的决定 |
| AC4 开销不随页数增长 | MET | 结论成立（独立复现，常数 12.4 MB，83.5 B/页）；守护测试页数不足（F-1） |
| AC5 不回归 | MET | 确认：11 passed + 字体赢家不变实测 |
| AC6 无外部字体下载 | MET | 确认：候选仅 `%WINDIR%\Fonts` 四文件，无网络调用 |

## 结论

**approve_with_conditions**。条件为 F-1、F-2（均为测试/证据小改，不动 `src/`），建议同时采纳 F-5 的措辞修正（只改未来立项建议的口径表述，可在下一份证据或由 Codex 收口时登记）。实现本身、fail-closed 语义、无回归性、以及作者对 skip 教训与「判断 vs 事实」的处理，都经得起独立复算——这份交付的诚实度是高的。
