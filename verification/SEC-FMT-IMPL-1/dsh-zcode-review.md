# ZCode 独立 Review：SEC-FMT-IMPL-1

- **Reviewer**: ZCode（非作者）
- **日期**: 2026-10-20
- **审查对象**: 主线 `9f5827364..1730670df`（11 commits；HEAD `1730670df`）
- **审查范围**: `tests/security/` 4 文件 29 测试、`tests/export/test_pdf_stream_integrity.py`、`verification/SEC-FMT-IMPL-1/` 12 个文件（base 前已入库 6 + 本 Task 新增 6）、`src/infrastructure/export/qt_free.py`（经 PDF-STREAM-FIX-1 的一行修复）、`doc/tasks/` 两份 Task 文件、STATUS/PLAN 增量。

## 结论

**APPROVED_WITH_CONDITIONS**

交付实质成立：四项 `SEC-FMT` 的判定全部核实无误，29+4 个测试本轮已独立复跑全绿，AC5 发现并驱动修复的 PDF P1 缺陷真实且影响巨大（所有导出 PDF 页面全白）。未发现任何虚报。阻断收口的是三个整理级问题：父 Task 文件未随交付更新（仍是 `ready`/待实施态）、两个新测试目录缺 conftest（裸跑集合失败）、一个测试的 `AttributeError` 断言语义过宽。另有一项口径裁定须交 Codex：**AC5 应回归 Owner 自己最初判定的 `PARTIAL`**，后出的「实质要求已达成」是对 AC 原文（「外部阅读器」→「外部验证器」）的转写放宽。

**审查环境声明**：主会话 Bash 权限客户端仍故障（`No permission client configured`），但本轮通过子代理完成了运行级复验（下附命令与结果），证据等级高于上次的纯静态 Review。主会话直接执行的仅有 Read 与 git 经子代理的只读取证。

## 3.1 四项实际状态是否如实登记 —— 逐项核实，四项判定全部成立

以下每一行的「核实」均为本轮独立重做，不是转抄 Owner 结论。

**`SEC-FMT-001` `MET`（适用路径上）—— 同意。**
「产品不适用」论证核实成立：`src/` 全树搜索 `extractall`/`namelist`/`infolist` 零命中；`ZipFile(` 唯一命中 `src/application/export/service.py:442` 且为 `"w"` 写模式。守卫本体核对原文：`test_assets/comic_golden_suite/tools/assets.py:691-701` 的 `zip_parts` 与测试主张逐条一致，且 `manga_members` 循环第一行即调用（无旁路），外加 `NNN.jpg` 白名单与「出口路径不受条目名影响」第二层。论证站得住。

**`SEC-FMT-002` `MET`（适用路径上）—— 同意。**
`src/` 中 `ET.parse`/`fromstring`/`ET.XML(` 零命中核实成立；产品侧 XML 只有构造+序列化（`_comic_info_xml`）。`public_xml_valid`（assets.py:387-399）确为先拒 `<!DOCTYPE`/`<!ENTITY` 再 `ET.fromstring`，带大小上限。特别肯定 `r1-xml-parsing-scope.md` §七：作者发现自己第一版只搜 `src/` 的盲区并主动补全仓搜索、修正判定——这是证据纪律的正面样本。

**`SEC-FMT-003` `MET` —— 同意，但判定必须继续带「detect 路径 + 委托机制」两条限定语。**
「过于宽松」的担心不成立，理由：规范要求的安全属性（伪装文件被拒、解码器不崩溃）是实测事实（GIF 测试即证明白名单独立于 Pillow 的解码能力起作用）；且 Task 的 AC3 原文自己规定「文档不得写成自建嗅探」——测试 docstring 遵守了。核实：`_DETECT_PAGE_FORMATS = {"PNG","JPEG"}`（core_service.py:304）、格式门 L1465、方法内首次 `self._core` 访问 L1542、`MAX_DETECT_PIXELS = MAX_DETECT_PAGE_BYTES // 3`（L299）与测试断言逐字一致。**须随判定登记的三个边界**：(a) MET 只覆盖 `core.detect` 面，导入面（`importing/`）在 r1 §四标「待确认」后未见关闭记录；(b) SEC-FMT-003 原文覆盖格式含 **WEBP**，白名单不含 WEBP——fail-closed 在安全上成立，但若产品将来要接受 WEBP 页，那是功能缺口不是安全达标；(c) 机制是对 Pillow（本机 12.3.0）的委托，版本漂移风险现由这 6 个测试钉住。

**`SEC-FMT-004` `MET`（功能层）—— 同意，附一条技术修正（P3-2）。**
实测可信：完整生命周期 7/7（探针）+ 回归测试 4 个（含三档长度与 guard-the-guard）。但 `sfx004-long-path-repro.md` §五的论证「Python 3.6+ 用宽字符 API，所以不需要 `\\?\`」**不完备**：宽字符 API 是必要条件而非充分条件。真实机制链是三条同时成立——宽字符 API + `python.exe` 清单的 `longPathAware=true`（CPython 自带；PyInstaller sidecar 同样继承，`apps/desktop/src-tauri/target/pyinstaller-work/EXE-00.toc` 的 manifest 片段为证）+ **系统 `LongPathsEnabled=1`**（本轮核实本机 `HKLM\...\FileSystem\LongPathsEnabled = 0x1`；Windows 默认值是 0）。所以 004 是「本机配置下实测 MET」：换一台默认配置的机器，>260 路径可能失败且这套测试会环境性红。这不推翻 MET（目标环境就是用户本机且实测通过），但 AC4 终态应带环境限定语，且「加 longPathAware」的建议对象应是 Tauri 主进程 manifest（python.exe 的清单覆盖不到它）。

## 3.2 测试质量 —— 对照臂真实有效；两个具体弱点

**「拒绝一切」bug 能否通过：不能。** 四个套件的对照臂都真实且断言具体：
- AC1 合法条目断言返回值 `("images", "My Book", "001.jpg")`（不是「不抛异常」这种弱断言）；目录条目另测。
- AC2 合法 `ComicInfo.xml` 断言 `ok is True`；畸形 XML 单独测，防「守卫放行但解析器全拒」。
- AC3 真 PNG 对照 + GIF 前置断言（先证明 Pillow 能读 GIF，白名单才是唯一拒因——这个前置断言是防测试自嗨的关键设计）。
- AC4 guard-the-guard（root 长度不足则全套白测）+ 三档长度防单点。

**「全绿但功能不存在」的路径：未发现。** AC1/AC2 直接调用守卫本体（import assets 后真实调用），AC3/AC4 直接打产品代码（`handle_detect`/`ManagedFileStorage`），没有测空对象的路径。真正的洞在另一侧，见 P3-3：**「产品不适用」是快照判定，无哨兵**——将来有人往 `src/` 加 `ZipFile` 读模式或 `ET.fromstring`，不会有任何测试变红，001/002 的不适用登记会静默过期（r1 §三自己预言了这个场景但没建哨兵）。

**几个值得点名的好设计**：AC1 的 `test_zipinfo_truncates_nul_so_the_stand_in_is_required` 把「为什么必须用替身」钉成测试（zipfile 截 NUL 是替身存在的前提，若未来 zipfile 改行为，测试提醒你换回真 ZipInfo）；AC2 的 `test_entity_check_runs_before_the_parser` 用 well-formed+DOCTYPE 文档证明拒绝来自子串守卫而非解析器（ET 默认不拒 DOCTYPE 却能解析它）——同时防住「守卫形同虚设、全靠解析器拒」的假绿。

**`__new__` 绕过 `__init__` 是否失真：不失真，已核实。** `handle_detect` 校验段（core_service.py L1424-1540）零 `self` 属性访问，首次 `self._core` 访问在 L1542（provider lookup）——`__new__` 实例与真实实例在全部被测路径上行为一致，且 docstring 说明了理由。失真点不存在；真实弱点是下面的 P2-3。

## 3.3 AC5 —— 「独立实现 ≠ 用户视角」写清楚了；判定应回归 `PARTIAL`

**区分是否写清楚：是，且写了两遍。** `ac5-interop-plan.md` §二的独立性表格（自验证零独立 / 7-Zip 与 fitz 高独立但非用户视角 / 漫画阅读器最高且是用户视角）和 `ac5-final-after-pdf-fix.md` L5 都是明确的自我声明。

**`PARTIAL` 还是 `MET`：`PARTIAL`，证据链内部已有定论。**
1. **Owner 自己最初就判了 `PARTIAL`**：`ac5-interop-plan.md` §五原文「所以 AC5 记为 `PARTIAL`，不是 `MET`。理由：AC5 要求外部**阅读器**，而本机有独立**解析/解压**器，没有**阅读器**」。
2. **后出的 final 文件靠改写 AC 措辞翻转了判定**：Task 原文（doc/tasks/SEC-FMT-IMPL-1.md L75）是「至少用**一个**外部**阅读器**打开」；`ac5-final-after-pdf-fix.md` §六把它转述成「用一个外部**验证器**打开」，据此得出「实质要求已达成」。同一作者同一天，唯一变化是 PDF 修好了——而修复不改变「没有阅读器」这个事实。这是自我放宽验收标准，须以 plan 的原始判定为准。
3. **公平记录**：PDF 侧的验证深度（渲染 + 逐像素统计）确实超出 r33 禁止的「结构验证」；CBZ 侧（7z `list`/`test` 是 CRC 级结构校验）则更贴近红线。所以准确表述是：**独立实现层达成（PDF 超红线、CBZ 达红线边缘）+ 阅读器层未做**（L1/L2 已如实登记）——这是 `PARTIAL` 的教科书形态，不是 `NOT_MET`。

补齐路径已在 plan §六列明：装一个便携阅读器（YACReader/SumatraPDF 免管理员可进 workspace）或请用户亲测——后者才是真用户视角。是否补齐由 Codex/用户裁定。

## 3.4 PDF 缺陷的归因与 PDF-STREAM-FIX-1 的收口 —— 均恰当

**归功 AC5 合理，不是运气。** 缺陷本质是规范违反（content stream 声明 FlateDecode 实为明文），AC5 的机制设计（外部独立实现互操作验证）恰好就是为这类缺陷准备的：自家的 29 个安全测试、PDFium 端到端像素断言（`tests/core/test_p16_reader_export.py:580-590`，真实生产链路）、以及全部结构指标都放行了它四天。「运气」成分只有一点——选中了不容错的 MuPDF 而非容错的 PDFium；但这一点已被 Task 转化为结构性产物：L2 登记（「互操作性押在单一外部实现上，缺陷可见性由该引擎容错行为决定」）+ 三层防线固化（引擎无关的 zlib.decompress 规范断言 + MuPDF 渲染断言 + 既有 PDFium 端到端）。发现归 AC5、教训归档，两头都站得住。

**收口（4 MET + AC3 `NOT_APPLICABLE`）恰当。** 逐项核实：
- AC3 的 N/A 有 5 场景实验背书（含子进程 `capture_output=True` 也 0 字节——这推翻了我上轮 Review 中「子进程大概率可测」的猜测，实验记录在 `p1-1-stderr-capture-experiment.md`，作者的实验推翻 Reviewer 的候选方案，这是正确的过程）；「实质由 AC4 蕴含」的逻辑链成立（渲染非白 ⟹ inflate 成功 ⟹ 无 zlib error）。
- 上轮 P1-1 按选项 2 落实：零断言测试已删（文件从 5 测试变 4），docstring 明确记录「deliberately NO test」及原因。
- 本轮运行级复验：`tests/export/test_pdf_stream_integrity.py` 4 passed；`tests/core/test_p16_reader_export.py` 19 passed（修复未破既有 PDFium 端到端）。
- `closed_with_limitations` 名副其实；L2（PDFium 单引擎四天假绿）是全部材料里最有长期价值的一条登记，对应的「单引擎验证对规范违反类缺陷无判别力」应尽快落进验证纪律。

## 3.5 这个 Task 值得存在吗 —— 值得；r37 不是假问题

**三条论据，第一条就足够：**

1. **AC5 抓到一个 P1**：所有经 `QtFreePdfComposer` 导出的 PDF 页面全白，而 PDFium 端到端像素断言四天全绿、29 个安全测试全绿、`page_count`/尺寸/`get_images()` 全部正常。若本 Task 不存在，该缺陷继续潜伏，用户的每一次 PDF 导出都是空白文件。仅此一条已值回 Task 全部成本。
2. **29 个测试把「无人负责的防御」变成显式资产**：001/002 的守卫活在校验工具里（无测试）、003 是对 Pillow 的隐式委托（无测试）、004 是解释器+系统配置的隐式行为（只有一次性探针，sfx004 §6.2 原话：「若将来有人引入了 ANSI 路径 API 或第三方库，长路径能力会静默退化」）。没人负责的防御在依赖漂移时会静默消失——现在不会了。
3. **r37 问的是责任，不是存在**。原文是「AC6 的要求有文字，不等于责任已实际分派」。四轮证据收敛（143→147，每轮初始判断都错）恰恰证明「想当然知道防御在哪」不可靠：不适用性、委托机制、环境依赖，全是要查才能定的事实。r37 说的缺口——没有 Task 对这些防御的持续有效性负责——是真实的，本 Task 就是补上它。

**诚实让步**：成本侧真实存在——初始估计「实现四项」错了四次，收敛消耗了一整轮勘察（6 份文档）。若第一次就查清，Task 会更小。但「查清」正是那 6 份文档做的工作，且每轮误判都有留痕与自我修正。以结果论（一个 P1 修复 + 29 个回归钉 + 诚实的适用边界），交付密度高于多数「从零实现」Task。它不是「为了给 r37 一个交代」——它是先搞清楚了自己该做什么，然后做的东西恰好比预定范围更有用。

## 发现的问题（按严重度）

### P0 / P1

无。

### P2

**P2-1（流程，收口硬前置）：`doc/tasks/SEC-FMT-IMPL-1.md` 未随交付更新。**
frontmatter 仍是 `status: ready`、`delivery_head: null`、`canonical_evidence_status: pending`；6 个 AC 全部还是 `<<PARTIAL: 待实施>>`；「交付与运行记录（待实施后填写）」、Canonical Evidence 表全空。实际交付已完成（11 commits、33 测试、AC5 完成、子 Task PDF-STREAM-FIX-1 已整个闭环）。STATUS.md 只有一句「AC1–AC4 完成」，PLAN 里 SEC-FMT-IMPL-1 行仍停在释放时描述。按协作协议 §4，转 `in_review` 与收口都无法在当前文件状态下进行。

**P2-2（测试基建）：`tests/security/` 与 `tests/export/` 是全部 16 个测试子目录中唯二没有 conftest.py 的。**
裸跑 `python -m pytest tests/security -q` 集合失败（`No module named 'bootstrap'/'infrastructure'`）——本 Review 开场即复现；须 `PYTHONPATH=src` 才能跑。其余 14 个套件全部由各自 conftest 自注入 src（如 `tests/packaging/conftest.py` 7 行模板）。全量跑目前能绿纯靠收集顺序（字母序在前的套件先注入 src），是偶然不是设计。任务书写、CI、任何单独验证这两个套件的人都会先撞墙。修法照抄 packaging 模板。

**P2-3（测试判别力）：`test_genuine_png_passes_the_format_gate` 的 `except AttributeError` 语义过宽。**
test_sec_fmt_003_magic.py L127-129：任何 `AttributeError` 都被解读为「到达 provider lookup」。当前代码下正确（本轮核实校验段 L1424-1540 零 self 访问），但未来若有人在校验段新增 `self._xxx` 访问，其 `AttributeError` 会让该测试**假绿**——语义从「过了格式门」悄悄变成「校验段内部炸了也算过」。收紧：断言异常文本含 `"_core"`（真实异常消息为 `'CoreServiceServer' object has no attribute '_core'`）。

### P3

**P3-1（裁定项）：AC5 终态回归 `PARTIAL`。** 见 §3.3。final 文件「实质要求已达成」的表述依赖「阅读器→验证器」转写，不应采信为 AC 判定；L1–L5 须原样进 Task 终态。由 Codex 裁定。

**P3-2（技术表述）：004 的机制链补全。** 见 §3.1。AC4 终态建议带「本机 LongPathsEnabled=1 实测」限定语；`longPathAware` 纵深防御的建议对象改为 Tauri 主进程 manifest（python.exe 清单覆盖不到它，sidecar 已继承）。

**P3-3（建议）：为 001/002 的「产品不适用」建负哨兵。** 加源码扫描断言测试：`src/**` 无 `ZipFile` 读模式、无 `ET.fromstring`/`ET.parse`——一旦有人引入解压/解析路径，测试红并指向 SEC-FMT-001/002 的登记。这是 `r1-xml-parsing-scope.md` §三「有效期」声明的可执行化，低成本高价值。

**P3-4（小项，登记即可）**：(a) CBZ 的 7-Zip 独立验证只在探针层未进 pytest（已登记 L3，维持）；(b) 7z 不在 PATH（`C:/Program Files/7-Zip/7z.exe` 存在），探针可移植性弱；(c) probe 用 `fitz` 触发 deprecation 警告，后续统一 `pymupdf` 模块名。

## 明确未核实的内容

1. **全量三套件未整体复跑**（pytest 全量/cargo/vitest）。本 Task 触碰面已由定点复跑覆盖（security 29 + export 4 + P16 reader 19 全绿）；「九个 pre-existing 失败与本次无关」采信 `cbbe0c8d3` 基线对照文档 + 上轮 Review §3.4 的方法有效性审查，本轮未重做。
2. **Chrome 负对照实验未复跑**：「headless 不能渲染 PDF」有 known-good 控制实验背书（PyMuPDF 自造好 PDF 同样 0 字节），且不影响任何判定。
3. **7-Zip 探针未复跑**：工具存在性已核实，结果 JSON 与 findings/final 文档交叉一致。
4. **Rust 侧（`.rs`）**：Owner 多份文档登记「未检查 .rs 侧」，本轮同样未查。四项判定均只覆盖 Python 侧；若 src-tauri 存在独立的文件处理/解压面，属真实边界，维持登记。
5. **UI 层「地址栏不截断」**：未测（Owner 已登记，归属待定）。

## 复验命令（本轮实际执行，可复算）

```
cd "G:/CODEX/New Manga"
PYTHONPATH=src python -m pytest tests/security -q                        # 29 passed (0.39s)
PYTHONPATH=src python -m pytest tests/security tests/export -q           # 33 passed (1.81s)
PYTHONPATH=src python -m pytest tests/export/test_pdf_stream_integrity.py -q   # 4 passed
PYTHONPATH=src python -m pytest tests/core/test_p16_reader_export.py -q  # 19 passed
python -m pytest tests/security -q                                       # 收集失败 ×2（P2-2 复现命令）
MSYS_NO_PATHCONV=1 reg query "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled   # 0x1
```

（以上命令经子代理于本机执行，Git Bash 环境与交付记录一致：Python 3.14.6、Pillow 12.3.0、PyMuPDF 1.28.2。）

## 条件与建议汇总

- **C1（收口前置）**：补 `doc/tasks/SEC-FMT-IMPL-1.md`——status 转 `in_review`、6 个 AC 终态、`delivery_head=1730670df`、Canonical Evidence 表、交付与运行记录。
- **C2**：`tests/security/`、`tests/export/` 各补 conftest.py（照 packaging 模板），恢复「子套件单独可跑」不变量。
- **C3**：`test_genuine_png` 的 `AttributeError` 断言收紧到异常文本含 `"_core"`。
- **C4（裁定项）**：AC5 终态建议 `PARTIAL`（独立实现层达成 + 阅读器层 limitation）；若 Codex 裁 `MET`，必须原样保留 L1–L5 且不采用「实质要求已达成」的转写口径。
- **C5（建议，不阻断）**：负哨兵测试（P3-3）；AC4 环境限定语（P3-2）。
