---
task_id: T1.1.1
reviewer: Codex
author: ZCode
base_commit: 1fa5f893649ec3c9f13f0823aca838548d863393
reviewed_head: 4a1ed6ca2778301da983f9f9159210a2fcca6985
decision: changes_requested
---

# T1.1.1 非作者 Review

## 范围与依据

审查对象为 `1fa5f89...4a1ed6c` 的完整 diff。被审 worktree
`G:\CODEX\New Manga.worktrees\T1.1.1-production-text-detector` 在审查开始时
clean，HEAD 为 `4a1ed6c`，分支为
`agent/zcode/T1.1.1-production-text-detector`。提交顺序为：

- `865074f`：docTR adapter、bootstrap detector 装配、测试和验证脚本；
- `6273816`：作者验证、真实素材 CPU 证据和 Handoff；
- `4a1ed6c`：GPU 证据和素材脚本修订。

审查读取了实际生产 diff、受影响 handler/port/domain 调用链、Task acceptance
criteria、Release Gate 评估文档、作者 Handoff、作者验证记录和新增测试；没有把
聊天摘要作为代码证据。

## Standards

- 变更路径在声明范围内；没有修改 SQLite Schema、`src/ports/detection/ports.py`、
  QML、Settings、Roadmap 或 STATUS。
- `src/bootstrap/app.py` 的新增内容限于 detector import、权重路径解析和构造注入；
  Region 写入仍通过 `RegionEditingService.create_region`。
- lazy import、缺权重 fail-closed、SHA 检查和无运行时下载的边界符合仓库的可选
  重依赖和源文件保护方向。
- 但依赖 pin、几何边界和冻结 merge policy 的实现违反 T1.1.1 已登记的硬性
  acceptance，见 R-001～R-004。

## Spec

已实现且经运行核对：docTR `fast_base` 真实推理、raw BGRA/rgb24 转 RGB、
`page-global` candidate、缺权重 typed failure、无静默 fallback、22 项 seam
测试、CPU/GPU Python 3.12 专项、真实 production bootstrap 的 detect→SQLite
路径和源文件保护。

未满足或实现错误：

1. merge policy 的水平阈值声明为 8px，但实现使用垂直 tolerance；
2. padding 没有 page-boundary clipping，候选可落在页外；
3. `torch` 没有固定版本，CPU/GPU 作者环境甚至是不同 minor 版本；
4. compliance re-check 只引用评估阶段网络证据，作者记录明确写明未重复核实，
   且本交付没有入库的权重/训练数据/再分发条款证据。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R-001 | **BLOCKING** | `src/infrastructure/providers/detection_doctr.py:345,358-360` | `MERGE_HORIZONTAL_TOLERANCE_PX = 8.0` 已声明，但 `h_near` 比较的是垂直 `tolerance`。当 median height 为 20px 时，14px 水平间隙仍会合并，违反冻结的 8px policy。 | `cluster_words_into_blocks([(0,0,10,20),(22,0,32,20)], [0.9,0.9])` 与 gap 14 均返回 1 block；gap 12 已超过 8px 仍合并。 | 使用冻结的水平常量，并补充 8px 边界两侧的判别测试。 | open / changes requested |
| R-002 | **BLOCKING** | `src/infrastructure/providers/detection_doctr.py:365-378` | 每个 block 四边无条件加 `MERGE_PAD_PX`，没有按 page width/height 裁剪；page-global candidate 可落在负坐标或超过页面边界，随后直接进入 Region persistence。Task AC 明确要求覆盖 boundary clipping。 | `cluster_words_into_blocks([(0,0,1,1)], [0.9])` 返回 `[(-6,-6),(7,-6),(7,7),(-6,7)]`。 | 在 adapter 输出阶段按页面尺寸裁剪，并测试四条边及裁剪后的有效 bbox。 | open / changes requested |
| R-003 | **BLOCKING** | `requirements.txt:5-9`; Handoff §1/§4 | `requirements.txt` 只 pin `python-doctr==1.1.0`；torch 仍为 docTR 的 `>=2.0,<3.0` 传递范围。作者 CPU venv 为 torch 2.14.0，GPU venv 为 torch 2.11.0+cu128，不能复现一个固定 torch 发布组合。 | `pip show`/metadata：`python-doctr` requires `torch<3.0.0,>=2.0.0`; 两个作者 venv 的 torch minor 版本不同。 | 由 Codex 明确 CPU/GPU packaging choice，固定兼容的 torch/torchvision 版本或明确同版本 CPU/CUDA wheel 方案，并更新安装/验证证据。 | open / changes requested |
| R-004 | **BLOCKING** | `verification/T1.1.1/author-verification.md:178-185`; Handoff §4 | T1.1.1 要求完成 license、训练数据/数据集和权重再分发条款的 compliance re-check；作者文档写明“未重复核实网络源”，交付目录也没有对应的可复核 license/compliance artefact。 | `verification/T1.1.1` 只有作者摘要、结果 JSON 和脚本；没有 docTR LICENSE、权重许可/来源条款或训练数据条款的入库复核记录。 | 在允许的 verification/Handoff 范围补充来源 URL、抓取日期、版本/SHA、权重许可和训练数据/再分发结论；无法确认的条目保持 BLOCKED。 | open / changes requested |
| R-005 | IMPORTANT | `src/bootstrap/app.py:687-699`; `verification/T1.1.1/scripts/fetch_doctr_weights.py:43-47` | 生产默认查找 `<data root>/models/detector/fast_base-688a8b34.pt`，但 sanctioned fetch 脚本默认写入 `%USERPROFILE%\\.cache\\doctr\\models`。不设置 `NEWMANGA_DETECTOR_WEIGHTS` 时，按文档执行 fetch 后生产路径仍会 fail-closed。 | 对照默认路径与脚本默认 `--dest`；作者真实推理使用的是 cache 路径，不是 bootstrap 默认 data-root 路径。 | 统一默认安装路径，或在 Handoff 明确并验证 `--dest <data-root>\\models\\detector` 的生产安装命令。 | open / changes requested |
| R-006 | IMPORTANT | `tests/providers/test_detection_doctr.py:104-110` | 冻结常量测试只断言水平常量、padding 和 SHA 前缀，没有断言 `MERGE_VERTICAL_FACTOR`、`MERGE_MIN_TOLERANCE_PX`，也没有边界/水平阈值 mutation。当前 R-001/R-002 正是该测试缺口暴露的问题。 | 现有 41 项专项虽通过，但 `gap=12/14` 和 edge padding 的判别测试缺失。 | 修复 R-001/R-002 时补齐垂直、水平、padding、boundary 的最小判别测试。 | open / changes requested |

没有发现超出声明范围的生产文件修改；没有发现第二条 Region 写入路径。

## Findings disposition

- R-001～R-004：**MERGE_BLOCKED / 必须修订后重新提交新 delivery HEAD**；不能在
  当前 head 上批准或集成。
- R-005～R-006：随同下一次修订处理；在 R-001～R-004 关闭前不单独放行。
- 没有 `DEFER` 可替代上述 blocker 的裁决；没有新增正式 Roadmap Task。

## Verification

以下均为 Codex 在 reviewed head 上 fresh 执行，shell 为 PowerShell，除特别说明外
`PYTHONPATH=src`。

| 场景 | 命令/环境 | 结果 | 证据 |
|---|---|---|---|
| 固定 head / clean | `git status --short --branch`; `git rev-parse HEAD` | **PASS**, clean，HEAD=`4a1ed6c` | worktree 状态现场输出 |
| 专项 A | `T1.1.1-impl-py312\Scripts\python.exe -m pytest tests/providers/test_detection_doctr.py tests/providers/test_detection_doctr_real.py tests/providers/test_detector_assembly.py tests/providers/test_detect_seam_t111.py -q -p no:cacheprovider` | **PASS**, `41 passed`, exit 0 | fresh run，docTR/torch/weights 可用 |
| 专项 D GPU | 同 A，`T1.1.1-gpu-py312`，`NEW_MANGA_DOCTR_DEVICE=cuda` | **PASS**, `41 passed`, exit 0 | fresh RTX 5070 Ti run |
| 实现 venv 全量 B | `T1.1.1-impl-py312\Scripts\python.exe -m pytest tests -q -p no:cacheprovider -rs` | **FAIL**, `1064 passed, 6 skipped, 2 failed, 1 warning`，exit 1 | 失败为既有环境证据 `test_no_model_runtime_is_installed_in_this_environment` 与导出 ViewModel 测试 |
| 基线依赖全量 C（被审 head） | `TASK-012-py312\Scripts\python.exe -m pytest tests -q -p no:cacheprovider -rs` | **FAIL**, `1039 passed, 10 skipped, 1 failed, 1 warning`，exit 1 | 失败为导出 ViewModel 测试；2 个 T1.1.1 模块和 2 个 torch rung 按环境 skip |
| 基线对照全量（1fa5f89） | 同 C，在 clean base worktree | **FAIL**, `1024 passed, 6 skipped, 1 failed, 1 warning`，exit 1 | 同一导出 ViewModel 失败，证明不是本 diff 引入；不能把全量写成 PASS |
| compileall | `T1.1.1-impl-py312\Scripts\python.exe -m compileall -q src tests` | **PASS**, exit 0 | fresh run |
| bootstrap smoke | `T1.1.1-impl-py312\Scripts\python.exe -m bootstrap.app --smoke-test --data-root <fresh-temp>` | **PASS**, exit 0 | fresh temp data root |
| diff check | `git diff --check -- src tests doc verification` | **PASS**, exit 0 | fresh run |
| 权重 hash | `sha256(fast_base-688a8b34.pt)` | **PASS**, `688a8b3489e9f5d0290c476c6272ec3b18de3ee646c8a0dc158203b1a9c62ace` | matches adapter constant |
| 真实 production path | `assemble_services` + valid local weight + `TRANSLATE_ALL` | **PASS（detect seam）**；detect 完成，1 个 machine Region 和 1 个 revision 持久化；后续 OCR 按现有未配置契约 typed `PROVIDER_NOT_CONFIGURED`；原始 PNG 与 managed copy byte-exact | Codex fresh PowerShell probe，exit 0 |

真实漫画 JSON、GPU JSON、专项测试和 bootstrap smoke 证明实现存在可运行路径，但
不能覆盖 R-001～R-004 的验收缺口。作者报告的 `1071 passed, 1 failed` 未在当前
review environment 重现；以本表 fresh evidence 为准。

## Acceptance 状态

| Acceptance | 状态 |
|---|---|
| docTR adapter / provider identity | PASS（但受 blocker 影响） |
| raw frame → RGB、page-global candidate | PASS |
| deterministic word-to-block policy | **FAIL**（R-001） |
| boundary clipping | **FAIL**（R-002） |
| pinned docTR / torch / weights / SHA | **FAIL**（R-003） |
| no runtime download / no silent fallback | PASS |
| 22 seam tests promoted | PASS，41 项专项 fresh green |
| real-page quality evidence | PASS as observation evidence; no product accuracy claim |
| license / dataset / redistribution re-check | **NOT VERIFIED**（R-004） |
| CPU/GPU Windows/Python 3.12 | PARTIAL: runtime runs, packaging/pin unresolved（R-003） |
| production bootstrap → detect → SQLite | PASS by Codex fresh probe |
| source protection | PASS by seam and production probe |
| full suite | FAIL in both reviewed and base controls; unrelated baseline failure recorded |
| compileall / bootstrap smoke / diff check | PASS |

## 结论与复审

`4a1ed6ca2778301da983f9f9159210a2fcca6985` **不能交 Codex 集成**。

决策：`CHANGES_REQUESTED`。ZCode 需要在新 delivery commit 中修复 R-001～R-004，
并同时补齐 R-005～R-006 的证据/测试；新 head 必须重新 Review，不能沿用本报告批准。

本轮没有 cherry-pick、没有 master 集成 commit、没有修改生产代码。Review 报告和
STATUS 登记是本轮唯一新增治理产物。
