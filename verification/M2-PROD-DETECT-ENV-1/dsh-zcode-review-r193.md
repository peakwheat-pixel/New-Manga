# M2-PROD-DETECT-ENV-1 独立 Review（r193）

**Reviewer**：ZCode · **日期**：2026-10-20 · **对象**：`verification/M2-PROD-DETECT-ENV-1/environment-restoration.md`（commit 9464003cd）+ Task `doc/tasks/M2-PROD-DETECT-ENV-1.md`

## 结论：**approve_with_conditions**

核心证伪（「离线」是误判）**成立**，且有本 Review 的独立第三方佐证；修复方案（隔离 venv + 显式 `--index-url`）与结果（442 passed / 0 failed）**采信**——本机沙箱拦截了 python/pwsh/git 执行，pytest 复跑**未执行（NOT_RUN，如实登记，不以静态走读冒充）**，但静态证据链（dist-info、pyc 物证、类存在性、权重字节数）与作者证据互洽。三条条件全部是**文档表述级修正**（1×P2 + 2×P3），不涉及代码、环境或重跑。

---

## 0. 本 Review 的独立验证通道（先声明口径）

本会话沙箱**拒绝执行**：venv `python.exe`、`python -m`、`python -c`、`pwsh`、`git`、任何仓库外路径的可执行文件。因此 §六 的两条复跑命令登记 NOT_RUN（见 §8）。

已完成的独立验证（不依赖作者证据）：

| # | 验证 | 结果 |
|---|---|---|
| V1 | `C:\Users\49745\AppData\Roaming\pip\pip.ini` | `[global] index-url = https://pypi.tuna.tsinghua.edu.cn/simple` |
| V2 | webReader 抓 `https://pypi.org/simple/transformers/` | 200，版本列表至 **5.20.2，含 5.17.0** |
| V3 | webReader 抓 `https://pypi.tuna.tsinghua.edu.cn/simple/transformers/` | 200，**页面非空**，版本列表至 **5.5.0**（无 5.6+） |
| V4 | webReader 抓 tuna `/pypi/transformers/json` | `info.version: "4.43.4"`、`last_serial: 24429835`、releases 无 5.x 段 |
| V5 | venv `pyvenv.cfg` | `include-system-site-packages = true`、base=`C:\Python314` 3.14.6 |
| V6 | venv site-packages dist-info | `transformers-5.17.0` + `huggingface_hub-1.33.0` + `tokenizers-0.23.3` + `pip-26.1.2`（无 torch——证实「不重装、复用全局」） |
| V7 | 用户 site dist-info | `transformers-4.48.3`、`torch-2.11.0+cu128`、`torchvision-0.26.0+cu128`、`safetensors-0.8.0`（与证据 §二 表格逐项一致） |
| V8 | venv 内 `models/rt_detr_v2/modeling_rt_detr_v2.py` 存在 + `auto/modeling_auto.py` 引用 `RTDetrV2ForObjectDetection` + 对应 `__pycache__/*.cpython-314.pyc` 已生成 | V2 类在 5.17.0 中存在；**pyc 是该 venv 确已 import 并执行过 V2 模块的物证** |
| V9 | 权重目录三文件字节数 | 2,320 / 171,543,900 / 470 B，与证据 §三 逐字节一致 |
| V10 | 321 个 `doc/tasks/*.md` 表头扫描（精确 `^\| resource \|` + 宽松大小写/空格两模式） | **0 命中**（详见 §6） |

---

## 1. §3.1 证伪是否成立

### Q1 网络诊断方法是否足够 —— **成立**

「网络通、镜像坏」的结论方向正确。逐个竞争解释：

- **代理**：`pip.ini` 无 proxy 配置。即便存在系统级代理，「经代理可达」同样证伪「离线」——不改变结论方向。
- **缓存命中**：B1 原记录「pip 缓存 transformers 相关 wheel 为 0 个」，download 之前无缓存可用。更关键的是 **V2/V3/V4：本 Review 用第三方抓取通道（完全不经本机网络栈）独立确认两个索引服务在线且对该包有真实内容**——「服务端存在」不是本机网络层的幻觉。
- **TLS 拦截**：拦截代理要伪造 simple 页必须提供真实版本列表（V2/V3 内容与 pypi 生态一致）；且即便如此也不改变「不是离线」。

### Q2 「pip index 与 pip download 走不同索引」解释是否完整 —— **前提核实，机制需修正（→条件 C1）**

- **前提成立**：V1 证实用户级 `pip.ini` 把默认索引指向 tuna，仓库内无 `pip.ini`。`pip index versions` 走镜像、`pip download --index-url https://pypi.org/simple` 走官方——路径分叉的解释成立。配置藏在用户层 pip.ini 也解释了为什么命令行表面看不出「实际查询的是谁」。
- **但机制表述与实测不符**：V3/V4 显示 tuna 对 transformers 的 `/simple/` 页**并非空**（列出 0.1→5.5.0），JSON API 元数据水位停在 **4.43.4**（2024-08），5.x 文件段只到 5.5.0——即镜像不是「对该包返回空版本列表」，而是**5.x 段同步滞后且不完整（缺 5.17.0），且元数据（4.43.4）与文件（5.5.0）两个水位互不一致**。`from versions: none` 的精确触发器本 Review 无法复现（pip 不可执行），不排除候选过滤（requires-python / wheel 标签 / pip 26 行为）等替代解释。**这不影响修复结论**（5.17.0 确实只在 pypi.org，V2），但 L6「镜像仍异常」的现在时表述会把「镜像对该包空」当作事实传播——这正是本 Task 教训的镜像版。

### Q3 当初为什么写出「离线」—— 错误链重构（作者最想听的）

从错误信息到结论，错在五步，其中第 1 步是根因：

1. **错误语义读反（根因）**：pip 的「网络不可达」与「索引无匹配」报错文案完全不同——前者是 `Retrying (…) / Connection error / Could not fetch URL`，后者是 `No matching distribution found / from versions: none`。**能报出 `from versions: none` 本身就证明请求到达了某个索引并拿到了应答**——错误文本自带反证，被读成了「连不上」。这是对错误信息的误读，不是证据不足。
2. **配置层遮蔽**：`index-url` 藏在用户级 `pip.ini`（V1），命令行不可见。镜像的行为被当成了「网络的行为」——诊断时没有问「pip 实际查询的是谁」（`pip config list` 一次即出）。
3. **强断言零验证**：「本机离线」是全局强断言，一次 TCP/DNS 探测（秒级、零依赖）即可证伪。blocked_reason 只记了结论，没记「排除了什么、如何重验」——留下了八轮无人能核的死角。
4. **锚定传播**：blocked_reason 一旦写入就成为后续每一轮的输入，被当既成事实复述而无人重验。组织缺陷：**长阻塞没有强制重验机制**——八轮里任何一轮重跑一次探测都能解开。
5. **确认偏误闭合**：「pip index 失败 + 缓存 0 wheel」两个信号都指向「装不了」，与「离线」自洽，于是没人问「装不了还有哪些别的原因」——镜像坏、requires-python 过滤、版本不存在。讽刺的是最后一条还被作者后来的核实推翻了（5.17.0 存在，V2 佐证）。

**教训落点（建议进证据或协作协议）**：环境类 blocked_reason 必须记录**原始错误文本 + 当时实际查询的索引/端点 + 重验条件**；阻塞超过 N 轮必须重验根因而非复述理由。

---

## 2. §3.2 `--system-site-packages` 是否正确选择

### Q1 —— **可接受**

AC4 明文「不以升级全局 Python 环境作为默认操作」；本场景只缺 transformers 一个包，却要为此重装数 GB 的 cu128 torch 栈（完全独立 venv 的代价），成本收益不成比例。写入面 = venv 自身（V5/V6），全局零触碰。语义上的代价（该 venv = 「全局栈 + transformers 覆盖层」）已被证据 L5「只修了本机」如实声明。

### Q2 venv 是否稳定解析到 5.17.0 —— **静态核实通过，动态复跑 NOT_RUN**

- V6：5.17.0 装在 venv site；V7：4.48.3 与 torch 栈全在**用户 site**。
- CPython venv 语义（`include-system-site-packages=true`）保证顺序：venv site → 系统 site → 用户 site；作者自报的 sys.path #6/#7 与此一致。
- **间接物证**：venv 内 `models/rt_detr_v2/__pycache__/*.cpython-314.pyc` 已生成（V8）——只有用该 venv 解释器实际 import 过 5.17.0 的 V2 模块才会产生。若解析到 4.48.3，AC3 不可能绿（4.48.3 无 V2 类，AttributeError 必现）。
- sys.path 动态打印未执行（python 被拦）——如实登记。

### Q3 污染方向 —— **写入不污染，读方向有两个陷阱（→条件 C3）**

venv 内 `pip install` 落 venv 自身 site-packages，不写全局/用户 site（venv 标准行为）。但值得在证据里登记两个读方向陷阱：(a) 在该 venv 内 `pip uninstall/降级 transformers` 只作用于 venv 副本，之后会**露出全局 4.48.3（版本闪回）**；(b) 依赖解析「看得见」整个全局栈，未来装新包时其依赖可能被全局旧版满足而不在 venv 内落副本。

---

## 3. §3.3 版本基线口径

### Q1 判定正确

逐行核对 `requirements.txt`：L9-12 确实明写 GPU (CUDA) wheels 是单独打包决定（T3.2.1）、在 one-off venv 中验证过 **torch 2.11.0+cu128 / RTX 5070 Ti**、且「NOT part of requirements.txt」；L17-18 的 `torch==2.14.0` / `torchvision==0.29.0` 是 CPU 支持口径。引用行号准确。V7 独立复核本机用户 site 就是 2.11.0+cu128。「不是偏离」的判定成立——CPU 基线与 GPU 实测基线是两个在案口径，不能混读。

### Q2 torchvision —— 同一逻辑适用

同一打包决定、同一 one-off venv 记录覆盖两者；证据表也已并排列出。适用。

### Q3 「一致」与「不一致」并列 —— 不会误读

表格判定列明确分流（「一致」/「见下」），「见下」有行号级依据段落承接。可选改进（非条件）：判定列直接写「GPU 变体（L9-12 在案）」可让表格自包含。

---

## 4. §3.4 AC3 的通过是否真实

### Q1 断言强度 —— **够用于本 Task 的验收目的**

`test_real_detection_returns_block_candidates`（tests/providers/test_detection_manga_real.py:98-125）不是仅「没抛异常」：断言了 provider 元数据（id/type/model/coordinate_space）、**候选存在性（≥1）**、每个候选的 reading_order 递增、标签序号、**置信度 ∈ [0,1]**、**polygon 四点且全部落在页内**、provenance 计数一致。加上 `test_real_blank_page_yields_zero_candidates`（:127-142，空白页**必须零候选**）构成双向判别。

它确实不断言「框落在三个手画气泡附近」——检出**位置**正确性不在单测口径，且测试 docstring 自己明示了这个限制并指向 envelope §AC3 的真实页实测记录（K01 页 2 框，scores 0.941/0.938）。该口径继承自 M2-PROD-DETECT-1 已审设计；本 Task 是环境恢复，无新增断言义务。

### Q2 排除「别的原因」—— **成立**

- 失败签名是确定性的**属性缺失**（`AttributeError: no attribute RTDetrV2ForObjectDetection`）：4.48.3 早于 V2 类引入的 4.49；5.17.0 有该类（V8 静态核实定义与 auto 注册）。
- 同一权重（sha256 pin 同一）、同一代码、同一机器，唯一变量 = transformers 版本；`src/`、`tests/` 零改动（git 不可用，未能独立复核——采信作者声明，我读到的当前文件与证据引用的行号/内容一致）。
- 「跳过冒充通过」不成立：skip 条件是权重目录缺失或 torch 缺失（:18-37），两者均满足且作者报告「2 passed」非 skip。
- 局限：本 Review 未复跑（NOT_RUN）；442=440+2 的算术自洽，3 skipped 口径与已知环境 skip 面一致；354 个测试函数经参数化展开到 445 collected 属合理量级。

### Q3 「加载了但推理无意义仍通过」—— **可能性被逼到极窄，且剩余窄窗有既有 Gate 背书**

恒空输出会被用例 1 抓（≥1）；垃圾框输出大概率被用例 2 抓（空白页零候选）。剩余窄窗是「输出少量页内合法框但位置错位」——而权重经 `_build_engine` 的**完整 sha256 pin 校验**（见 §5）= 与 C4 qualification 完全同一快照，其检出质量已有 C4 Gate（三项 PASS）与 envelope 实测背书；「同一快照在这台机器上系统性语义劣化而结构不变」没有任何证据支持。AC3 证明的是**链路恢复**，不是检测质量重证——后者按 r42 口径本就无需重证。

---

## 5. §3.5 AC2 的离线与权重证据

### Q1 三个约束是否足以证明没有下载 —— **足够，实际是四层**

1. 加载源是**本地目录路径**（`str(weights_dir)`，非 repo id）——本地目录加载不进入 hub 解析路径（detection_manga.py:522-527）；
2. `from_pretrained(..., local_files_only=True)` **写在生产代码里**——这是关键层：AC3 测试走生产路径时**并不依赖**那两个环境变量，仅凭代码内参数即拒绝联网；
3. `HF_HUB_OFFLINE=1`；4. `TRANSFORMERS_OFFLINE=1`（作者手工构造时的额外约束）。

transformers 在「本地目录 + local_files_only」语义下不存在静默回退在线路径；若文件缺失会直接报错而非下载。声称成立。

### Q2 前 16 位 sha256 够不够 —— **形式上不够，实质上闭合（→条件 C2）**

- 「校验真的会跑吗」——**会，且是模型构建的必经之路**：`detection_manga.py:511-519` 在 `from_pretrained`（:522-527）**之前**对三文件逐一做**完整 64 位** sha256 校验，不匹配即 raise `ProviderError`（fail-closed，非 warning）。**因此 AC3 的 2 passed 本身蕴含三文件完整校验通过**——否则模型根本建不起来。
- 证据记录的三个前 16 位与代码 pin（:112-120）前缀逐一吻合（本 Review 核对）。
- 缺口仅在形式：证据 §三 没有写出上述蕴含关系，读者须自行读代码才能从「前 16 位」到达「同一快照」的结论。C2 要求补一句论证或抄录完整 hash。

---

## 6. §3.6 收口格式

### Q1 表头错误成因 —— **检查器设计分工使「全量 PASS」对 Task 表格零信息量**

- `check.ps1` **无参模式只审权威指针文档**（AGENTS.md、00_INDEX、AD-001、STATUS、PLAN）与全局哨兵（架构冲突标记、防膨胀预算等），**不逐个审历史 Task 文件**；只有 `-TaskPath` 才加载该 Task 做 front matter / Canonical Evidence / Resource Manifest / AC 门禁校验（check.ps1:244-247, 384-452）。
- 错误表头 `| resource | …` 因首列不匹配 `^(evidence_id|resource_type)$` 被当作**数据行**（:49），至少触发两个确定性错误：`Resource disposition 无效：DISPOSITION`（:431）与 `Resource manifest 不存在：sha256/manifest_path`（:443-445）。4 个错误的精确构成本 Review 未复现（pwsh 被拦），其中 ≥2 个可由机制确定解释。
- **是否系统性疏漏：是**——但缺陷在**收口工作流**而非检查器：模板（doc/templates/TASK.md:72）本有正确表头 `| resource_type | …`，三次同错说明建 Task 时手写表格而未复制模板、且收口时缺「每个新建/修改的 Task 必须跑一次 `-TaskPath`」的固定步骤。「全量 PASS」不构成 Task 文件合规的证据。

### Q2 有没有第四处 —— **核实通过，没有**

321 个 `doc/tasks/*.md`（作者口径 320，差 1 不影响结论）中：精确模式 `^\| resource \|` **0 命中**；宽松模式（大小写、空格容忍）**0 命中**。95 个文件带标准表头 `^\| resource_type \|`，97 个文件含 `Resource Manifest` 段——差 2 个为无表格形态（非错误表头；错误表头已被上述两模式全量排除）。

---

## 7. 条件（全部文档级，零代码/环境改动；本轮 Review 不改文件，由作者返修）

| # | 级别 | 条件 | 落点 |
|---|---|---|---|
| **C1** | **P2** | 把「镜像对该包返回空版本列表 / from versions: none」的机制表述修正为：「tuna 对 transformers 的 5.x 段同步滞后不完整（simple 页至 5.5.0、JSON API 元数据水位 4.43.4、缺 5.17.0），元数据与文件两个水位互不一致；`from versions: none` 的精确触发器未复现，不排除 requires-python/候选过滤等替代解释」。防止「镜像空」成为下一个被复述八轮的既成事实。 | `environment-restoration.md` §一/§七-L6 + Task Closeout Record 对应句 |
| **C2** | **P3** | 证据 §三补一句蕴含论证：「AC3 通过 ⟹ `_build_engine` 的三文件完整 sha256 pin 校验通过（校验在 from_pretrained 之前、fail 即 raise），故权重与受测代码为同一快照」，或直接抄录三个完整 64 hex。 | `environment-restoration.md` §三 |
| **C3** | **P3** | 补一行 venv 使用警示：(a) 在该 venv 内 uninstall/降级 transformers 会露出全局 4.48.3；(b) 该 venv 的依赖解析「看得见」全局栈，新装包的依赖可能被全局旧版满足。 | `environment-restoration.md` §六 |

---

## 8. NOT_RUN 清单（如实登记，均因本会话沙箱拒绝执行，非静默跳过）

| 项 | 请求方期望 | 状态 |
|---|---|---|
| venv `pytest tests/providers -q` | 442 passed, 3 skipped | **NOT_RUN**（venv python.exe 与 `python -m` 均被拦截） |
| 全局 `pytest tests/providers -q` | 2 failed | **NOT_RUN**（同上） |
| `pip index versions` / `pip download` 复现 | 复现镜像空候选 | **NOT_RUN**（pip 不可执行；已用 V1-V4 第三方通道部分替代） |
| venv `sys.path` 动态打印 | 顺序 #6/#7 | **NOT_RUN**（静态核实替代，见 §2 Q2） |
| `check.ps1 -TaskPath` 复现 4 错 | 4 errors | **NOT_RUN**（pwsh 被拦截；机制静态走读已闭合） |
| `git status`/`cat-file` 核零改动与 evidence commit 可达 | — | **NOT_RUN**（git 被拦截；「零改动」采信作者声明 + 文件内容与证据引用一致性） |

## 9. 结论重述

**approve_with_conditions（C1 P2 + C2/C3 P3）**。「离线」证伪成立且方向正确（本 Review 另以第三方抓取双索引 + JSON API + pip.ini 独立佐证）；修复落点、版本口径判定、AC3/AC2 的实质闭合均核实通过；唯一需要返修的是镜像机制的表述精度（C1）与两处证据形式缺口（C2/C3）。
