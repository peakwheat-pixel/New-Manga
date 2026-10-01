---
task_id: M2-DETECT-WEBTOON-TILING
author: ZCode
recipient: DeepSeek Harness（review，非作者）→ 编排会话代行 Codex（集成）
base_commit: f99a6c55
delivery_head: 29a7f5b5
status: delivered  # 待 DSH review；review 通过后由集成方合并（集成次序 TILING → BACKFILL → SFX-UI）
---

# Handoff：M2-DETECT-WEBTOON-TILING（webtoon 长条漫 ogkalu tiling 检测修复）

## 交付结果

- **delivery_head = `29a7f5b5`**（implement 单 commit：实现+测试+qualification 全部落盘；本 Handoff 与 Task 回填为后续文档 commit）。
- 变更路径（与允许修改面逐项对照）：
  - `src/infrastructure/providers/detection_manga.py`（+369/-4）：tiling 路径唯一实现文件；
  - `tests/providers/test_detection_manga.py`（+452）：新增 32 个测试函数（collected 45 条）；
  - `experiments/M2-DETECT-WEBTOON-TILING/qualify_tiling.py`（新增）：AC3 qualification 脚本；
  - `verification/M2-DETECT-WEBTOON-TILING/qualification-results.json` + `qualification-report.md`（新增）：AC3 raw 数据与报告。
- **AC1 tiling 路径**（全部落在 detection_manga.py 单文件，契约零变更）：
  - **触发条件**：`height/max(width,1) > 4.0`（严格大于，边界不触发）。Owner 选型留痕：DIAG 实测 webtoon 页 h/w = 30.7（K02）/ 40.8（K04）/ 90.0（K01），普通页 h/w ≤ 1.41（BJ02 2946×4167、K19 1200×1660），阈值 4.0 两侧余量 ~20×，见 `TILING_TRIGGER_RATIO` 常量注释。不触发页走**零 diff 的原 `_detect_text_boxes`**（函数本体逐字节未动，diff 仅新增函数与 detect() 分支编排）。
  - **参数配置化**：env 通道 `NEWMANGA_DETECTOR_TILING_TRIGGER_RATIO / _TILE_SIZE / _OVERLAP / _NMS_IOU`（命名沿 `NEWMANGA_SFX_CONF_THRESHOLD` 先例），默认=DIAG 冻结值 4.0/1024/128/0.5。**选型留痕：env 而非 settings**——settings 通道需动 `bootstrap/core_assembly.py`（禁改面），env 读取内聚在 provider 文件内；非法值 fail-fast（`ValueError` 消息含 env 变量名，解析错误与范围错误同语义；overlap 对**生效 tile_size** 联合校验，自定义小 tile 必须自带 overlap）。读取时机=detect 内（engine 校验之后），fail-closed 顺序不变。
  - **实现**：`_tiling_tiles`（2D 重叠网格，DIAG 精确步进：K01 690×62133 → 70 块、原点 0..61824 步 896、尾块 309px=DIAG 逐值一致）→ `_pad_tile`（右/下常量灰 114 pad 到方形=DIAG 惯例）→ `_tile_inference`（逐块生产推理序列，**复用同一 engine/session，不逐块重建**；target=padded 尺寸=DIAG）→ 复用共享纯过滤 `_text_boxes_from_results`（**块内 clip 到块界**=任务书要求；DIAG 以"pad 带中心点丢弃"实现，其 pad 带实测 0 检出，两种处理在 DIAG 数据下数值等价）→ `+块原点` 回映 → `_greedy_nms`（置信度序贪心，**IoU 严格大于阈值删除、恰好等于保留**=DIAG 语义）。输出=绝对页坐标 text_boxes 进冻结生产合并——DetectionRequest/Response 与 MERGE_* 输入零变更。
  - provenance：detect options 新增 `tiling=on/off`、`tiling_tiles`、`text_boxes_pre_merge`（审计可见；dict 取键式既有断言不受影响）。
- **AC2 测试（先红后绿）**：红态实证=实现前 `test_detection_manga.py` 73 collected 中 **44 failed / 29 passed**（全部失败因 tiling 符号不存在：`AttributeError: _tiling_config` 等）；绿态 **73 passed 全绿**。新增覆盖：触发判定（K01/K02/K04 触发、BJ02 不触发、h/w==ratio 边界不触发、width=0 防御、ratio 可配）；env fail-fast 矩阵（14 条 parametrize：非数字/零/负/超域/overlap≥tile）；块几何（K01 70 块 DIAG 逐值、单块页、整除无空尾块、2D 网格、全覆盖无洞）；坐标回映（+原点）；跨块 NMS（重叠带重复删低 conf、IoU 恰 0.5 保留、keeper 恒为高 conf、disjoint 不删）；块内 clip；bubble 跨块累计；共享纯过滤 NaN typed（DSH r1 R9 语义贯通）；普通页**必走**原路径+tiled 分支禁入（双向哨兵）；长条页缺权重仍 `PROVIDER_NOT_CONFIGURED`（fail-closed 顺序不变）；无权重 typed 缺失（既有 TestFailClosedEngine 未动全过）。**既有测试零修改**：三套件 `tests/providers tests/core tests/m2_acceptance` = **575 passed + 1 skipped 0 failed**（基线 530+1skipped + 新增 45；解释器 `T1.1.1-impl-py312`）。
- **AC3 qualification**（DIAG 冻结口径逐条，真权重 pin 一致、CPU，数据=[qualification-results.json](../../verification/M2-DETECT-WEBTOON-TILING/qualification-results.json)、报告=[qualification-report.md](../../verification/M2-DETECT-WEBTOON-TILING/qualification-report.md)）：
  - **Gate PASS**：五张 `webtoon_long_strip` 生产 `provider.detect` region 数>0 —— K01=**180**（合并前 193 框，**与 DIAG 块级实验逐值一致**）/20 104ms（≤25s）；K02=**93**（97）/5 968ms（≤10s）；K04=**113**（117）/9 271ms（≤15s）；K05=**62**（64）/14 277ms；K08=**60**（61）/16 252ms（K05/K08 无预算项，数字如实登记=发布形态输入）。三张预算页全部预算内。
  - **阈值曲线（0.5 vs 0.4）**：K01 193→214 框（region 180→191）；K02 97→103（93→97）；K04 117→120（113→115）；K05 64→65（62→62）；K08 61→65（60→62）。0.5 生产点 conf_max 0.9666–0.9725；贴阈敏感性=DIAG 预警形态，无爆炸；**conf 生产默认 0.5 不变**（0.4 仅为曲线数据）。
  - **690×690 原生尺度对照**（K01，tile 690/overlap 128）：111 块（≈70×1.6×）→ **198 框 / 177 region**，31 887ms——与 1024² 的 193/180 同量级（+2.6%），分辨率假设验证成立（恢复源于消除整页重缩放，非特定 tile 尺寸）。
  - **K19**（无字页）：0 candidates、`tiling=off`——正确行为；F4（handler 把空成功判 `INVALID_INPUT`）口径**不修只登记**（相邻发现，与 DIAG 定案一致）。
  - **BJ02 对照**：region=5、`tiling=off`——与 DIAG 探针逐值一致（`matches_diag_probe=true`），普通页零变化。
- **AC4 文档**：模块+函数级 docstring（触发/参数/回映/NMS 语义、普通页零变化承诺、env fail-fast、pad 惯例出处）已随实现落盘；本 Handoff + Task 回填=文档 commit；**发布形态影响评估：无新依赖（纯标准库 os + 既有 numpy/torch 调用）→ 闭包/GATE 不涉及，登记确认**。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC2 红 | `pytest tests/providers/test_detection_manga.py`（实现前） | T1.1.1-impl-py312 @ base f99a6c55+测试 | 44 failed / 29 passed（AttributeError 缺 tiling 符号） | 会话记录（未落盘，红态为符号缺失的机械失败） |
| AC2 绿+基线 | `PYTHONPATH=src pytest tests/providers tests/core tests/m2_acceptance -q` | 同上 @ 29a7f5b5 | **575 passed 1 skipped 0 failed**（基线 530+1sk+45） | 会话记录 |
| AC3 Gate+延迟+曲线+690 对照+K19+BJ02 | `python experiments/M2-DETECT-WEBTOON-TILING/qualify_tiling.py --output verification/M2-DETECT-WEBTOON-TILING/qualification-results.json` | T1.1.1-impl-py312（torch 2.14.0+cpu）@ 29a7f5b5 | **GATE PASS**（5/5 + controls 全 true） | qualification-results.json / qualification-report.md |
| 自检 | `git status --porcelain`、`git diff --check` | 29a7f5b5 | 仅 4 个允许面路径；diff --check EXIT=0；禁改面零触碰 | 会话记录 |

未运行：GPU 形态（CPU 单环境=DIAG 同口径）、逐框精度（无 ground truth，DIAG 已声明）。

## 接收方式

- 分支 `agent/zcode/M2-DETECT-WEBTOON-TILING` @ worktree `G:/CODEX/New Manga.worktrees/M2-DETECT-WEBTOON-TILING-zcode`，base=f99a6c55，delivery=29a7f5b5。
- 测试复现：`PYTHONPATH=src "G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" -m pytest tests/providers tests/core tests/m2_acceptance -q`
- qualification 复现：`PYTHONPATH=src <同 venv> experiments/M2-DETECT-WEBTOON-TILING/qualify_tiling.py`（真权重路径 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector`，CPU 约 2.5 分钟；重跑会覆盖输出 JSON，数字应逐值复现——单线程 CPU 推理）。
- 前置条件：无（无新依赖；权重由 provider 自校验 sha256 pin）。

## DSH review 指引（非作者 review）

建议优先核对面（按风险排序）：

1. **普通页零变化主张**（最高优先）：`git diff f99a6c55 29a7f5b5 -- src/infrastructure/providers/detection_manga.py` 中 `_detect_text_boxes` 函数本体应零 diff（仅 docstring 措辞更新）；detect() 分支在 `tiling=off` 时与原实现逐调用等价（新增 `_tiling_config()` 纯读取+比较）；BJ02 qualification 对照逐值一致（5 region）。
2. **NMS 语义与 DIAG 一致性**：`_greedy_nms` 严格大于删除/等于保留（DIAG 探针 `best_iou > iou_threshold` 同款）；置信度序贪心；kept 集合构造性 IoU≤阈值。
3. **clip 语义差异登记**：DIAG 用"pad 带中心点丢弃"，生产用"块内 clip"（共享纯过滤）——DIAG pad 带零检出下两者数值等价；review 请确认接受该等价论证（qualification K01 193 框逐值复现是其经验证据）。
4. **env fail-fast 完备性**：非数字/超域/overlap≥生效 tile 联合校验；错误消息含 env 名；`_tiling_config` 在 detect 内读取（engine 之后）的时机取舍。
5. **红绿证据**：红态 44/73 mechanical failure；测试几何（重叠带重复、clip 后去重、IoU=0.5 边界）可从测试常量直接复算。
6. **qualification 数字**：K01 合并前 193=DIAG 逐值；K05/K08 首次实测；曲线点与 690 对照在 JSON 可复核。

## 下一任务建议（必填）

- Task ID / 标题：无需新建——本 Task 进入 DSH review → 集成（集成次序 TILING → BACKFILL → SFX-UI，见批次 release commit f99a6c55）。
- 推荐 Agent / Reviewer：DeepSeek Harness（非作者 review，按上文指引）；集成=编排会话代行 Codex。
- Recovery point：仓库 `G:/CODEX/New Manga`，branch `agent/zcode/M2-DETECT-WEBTOON-TILING`，base f99a6c55 / delivery 29a7f5b5；worktree 已存在。
- 允许修改路径：review 意见落在本分支 `src/infrastructure/providers/detection_manga.py`、`tests/providers/test_detection_manga.py`、`verification/M2-DETECT-WEBTOON-TILING/**`、Task/Handoff。
- 禁止范围与新增授权条件：任务书禁改面不变（detection_sfx.py/detection_doctr.py/ports/bootstrap/contracts/packaging/apps/TA3-*|DIAG experiments/STATUS）；若 review 要求动 bootstrap 配置通道（env→settings），按任务书先在 Handoff 登记移交集成方。
- 交付物：本分支两个 commit（implement + 文档）。
- 验证命令、环境与完成 Gate：上文两条复现命令；Gate=DSH review 通过 + 三套件 0 failed + qualification GATE PASS 保持。
- 可直接转发给 Agent 的指令：「对 M2-DETECT-WEBTOON-TILING @ 29a7f5b5 执行非作者 review：按 doc/handoffs/M2-DETECT-WEBTOON-TILING-29a7f5b5.md §DSH review 指引逐条核对，产出 doc/templates/REVIEW.md 报告。」

## 风险与遗留

- **粒度登记（非缺陷）**：ogkalu tiling 框多为"气泡文本块"级（生产合并率仅 1.6%–7.2%），K01 region=180 远细于 docTR 同页 15（生产合并后口径）——两 provider 粒度差异属实，Gate 口径不受影响；粒度对下游 OCR/翻译成本的影响留产品观测。
- **F4 相邻发现（不修）**：无字页空成功被 handler 判 `INVALID_INPUT`（K19 复现 0 候选正确行为），口径修复属后续 slice。
- **延迟**：长条页最坏 ≈20s（K01，CPU）；块数随页高线性（K08 51 971px → 58 块 16.3s）。GPU/并发/降块策略=发布形态决策输入，本 Task 不做。
- 回退方法：分支整体不合并即回退；运行时可通过 `NEWMANGA_DETECTOR_TILING_TRIGGER_RATIO` 调高阈值规避（不建议无证据调整）。

## 实验附录（实验任务）

- 数据来源与许可：TA3-B 20-case 选择清单（`experiments/M2-TA3-B/case-selection.json`），页面 sha256 全部与 manifest 匹配；K01/K02/K04/K05/K08=韩漫 KO real_webtoon_cleaned_dataset，K19=Pepper&Carrot kr EP20（CC 授权族），BJ02=Black Jack vol01 p0053。
- 模型/权重：ogkalu/comic-text-and-bubble-detector @ 16e8a622，三文件 sha256 与生产 pin 全匹配（JSON `weights` 段）。
- Runtime/硬件：torch 2.14.0+cpu / transformers 5.17.0 / numpy 2.5.3 / Python 3.12，Windows，CPU 单线程推理。
- 网络策略：全程离线（`local_files_only=True` + 本地快照）。
- 参数：tile 1024 / overlap 128 / NMS IoU 0.5 / trigger 4.0 / conf 0.5（生产）与 0.4（曲线点）；690 对照组 tile 690。
- 运行次数：各 1 次（qualification 非 determinism gate 范围；DIAG 侧 193 已两次复现）。
- 原始结果：`verification/M2-DETECT-WEBTOON-TILING/qualification-results.json`。
- 失败样例：无（Gate 一次通过）。
- 限制：无 ground truth（精度不裁）；CPU 单环境；K05/K08 无 DIAG 前数据（本轮为首次实测）。
