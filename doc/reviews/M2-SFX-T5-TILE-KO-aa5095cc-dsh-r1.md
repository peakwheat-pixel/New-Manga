> 【集成轮落盘注记】本报告为 DSH r1（非作者，只读，静态）审查原文，由集成方自 headless 会话输出原样落盘（DSH 沙箱只读未落盘）；审查对象 head=aa5095cc，其后 Owner 返修 306f5040（P3-1 parity 硬断言硬化+P3-2 登记扩+P3-3 degenerate 负例+P4 errata）→ merge。集成 Gate 实测（shell）：src/tests 各仅 1 文件、contracts/apps/packaging 零 diff、16 文件全在允许路径、worktree clean、SFX 测试文件 70/70 绿（P3-3 新例含）。

# M2-SFX-T5-TILE-KO 非作者 r1 Review（DSH，只读）

## ① 前置声明（工具与采信口径）

- **shell 不可用**：本会话中 `pwsh` 在命令执行前即失败——`Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-SFX-T5-TILE-KO-zcode)`（连续 3 次，含 `echo` 探针）。因此**所有 git 命令均未运行**：`git status`、`git diff a3b0f537 -- contracts/ apps/`、`git log`、`pytest` 均无法复跑。
- 可用通道：`read` / `grep` / `glob`（含工作区外只读路径）。我用以下**替代证据**完成 git 面核对：
  - 分支 ref：`G:\CODEX\New Manga\.git\refs\heads\agent\zcode\M2-SFX-T5-TILE-KO` = `aa5095cc5ff7bf…`（tip 一致）；
  - worktree reflog：`G:\CODEX\New Manga\.git\worktrees\M2-SFX-T5-TILE-KO-zcode\logs\HEAD`，第 3–8 行可读到完整提交链（见 R8）。
- **base 对照代理**：无法 `git show a3b0f537`，改用主工作区 `G:\CODEX\New Manga\src\infrastructure\providers\detection_sfx.py`（802 行）作为 base 代理。该文件无任何 `SFX_TILE`/`sfx_route` 符号，且 `detect()`（`:306-357`）与 worktree 的 letterbox 分支同形，作为 base 代理成立；但主工作区可能已晚于 a3b0f537，属**代理性对照**（已在结论中标注）。
- **采信口径**：运行级声称按「作者声称 + 静态/证据一致性」采信；凡未独立复跑者明确标注（见 ③ 末表）。全程只读，未修改/创建任何文件；Handoff 指定的 review 落盘路径 `doc/reviews/M2-SFX-T5-TILE-KO-<head>-dsh-r1.md` 由我方**无法写入**，本报告全文在此输出，需 Owner/集成方代持久化。

---

## ② Verdict

# **approved_with_conditions**（0×P0 / 0×P1 / 0×P2 / 3×P3 / 4×P4）

核心判断：AC1–AC5 的**实现等价性、路由安全、typed 断言、逐位复现证据链、回归自洽、性能协议与纪律**在静态与入库证据两个层面均成立；未发现产品面正确性缺陷。条件均为「证据门硬化 + 登记补齐」性质，不阻断集成。

### P0（阻断）— 无

### P1（集成前必修）— 无

### P2（应修）— 无

### P3（条件项，建议随集成收口）

- **P3-1｜AC3 硬门未真正断言 bit parity（最重要）**
  位置：`experiments/M2-SFX-T5-TILE-KO/verify_tile_parity.py:420-435`。
  KO 段的硬断言是 `ok = total_matched == expect and total_gt == (56|135)`，随后 `assert ok`；而逐页 `bit_parity_vs_t3_raw`（`:399`、`:409`）与 `t3_matched`/`t3_n_pred`（`:407-408`）**只记录、不断言**。对照 BJ 段则有 `assert all(b["bit_parity_vs_t3_raw"] ...)`（`:478`）。
  含义：若预测框发生漂移但 matched 总数恰好不变，脚本仍会写 `"bit_reproduction": true` 并通过——字段名 `bit_reproduction` 实际度量的是「matched 总数复现」，不是「逐位」。
  本次交付**不受影响**：入库 `parity-v2b.json`/`parity-chiqui7.json` 全部 8 个 KO 页 `bit_parity_vs_t3_raw=true`，且我已逐页对 T3 raw 交叉核验（R4）。建议：KO 循环补 `assert all(p["bit_parity_vs_t3_raw"] for p in per_page)`，并把 `bit_reproduction` 更名或拆为 `matched_reproduction`/`preds_bit_equal` 两字段。若集成方要求「AC3 硬门逐字可执行」，本项应升级为 P2。

- **P3-2｜路由是「页面形状全局生效」，跨域成本未登记**
  位置：`src/infrastructure/providers/detection_sfx.py:265-266`（阈值）、`:297-306`（默认 `enabled=True`）、`:373-375`。
  判定只依赖页宽/纵横比，不绑定 KO 书域；任何宽 ≤690 且 aspect ≥8.0 的页（含非 KO 长条页）默认走 tile，代价约 20×（部署记录 §1：CPU 均值 10.46 s/页 vs letterbox 0.3–0.5 s/页）。已登记的限制只有「宽≠600/690 未逐宽重校」（`src:256-266`、deploy report §3①），**未登记**「跨书域长条页一律进入慢路径」这一部署面影响。建议在 Task/部署记录补一条 limitation。

- **P3-3｜运行期断言的覆盖边界与非退化分支**
  位置：`src:398-447`（`_assert_tile_caliber`）、`:394`（`_tile_ys` 每次调用）、`tests:1043-1055`。
  断言确实覆盖「非空/首锚点 0/相邻差=步长或页底锚点/末锚点覆盖页底/非退化」，且是 `raise` 语句、typed `ProviderInvalidOutput`（`src/ports/providers/errors.py:129-137`，非 `AssertionError`），`-O` 不可剥除——**R3 主张成立**。两点边界需登记：
  1. 步长/页底锚点均由**同一份运行时 cfg** 反推，故运行期门只能发现「序列构造漂移」，**无法**发现冻结常量本身的漂移；常量冻结实际由 `tests:1017-1024` 单测钉住。
  2. 「非退化」分支 `y + tile_h <= y`（`:442`）等价于 `tile_h <= 0`，而 `tile_h > 0` 已在 `_tile_config:331-332` 拦截，实际只对 `y < 0` 生效；且该分支**无单测**（`test_tile_caliber_assertion_rejects_broken_geometry` 是 5 次调用=4 个 raise 面 + 1 个通过面，deploy report 的「单测 5 面」按调用数成立，但 degenerate 面无覆盖）。建议补 1 例并注明常量冻结由单测承担。

### P4（nits / 记录性）

- **P4-1｜提交信息计数与证据不符**：reflog 中 `c9880955` 提交信息写「tile 单测 **22** 例先红后绿」（logs/HEAD:6），而盘上 tile 用例实为 **32** 个收集项（13 个函数，其中一个 ×20 参数化；与 Task「+32 用例」「1812=1780+32」一致）。建议在 Task 偏差登记补一行 errata（docs 为追加式证据，不重写历史）。
- **P4-2｜交付链首环之前多一个 doc-only commit**：reflog 显示 `a3b0f537 → 217f3383（cherry-pick: chore(T5-TILE-KO): Task 合同 base_commit 更新）→ c11a2a9d claim`（logs/HEAD:3-4），而 Task/Handoff 的「交付链」从 claim 起算。仅 Task 文档改动，非 src 漂移，建议记录一句。
- **P4-3｜陈旧类型注解（pre-existing）**：`_engine_or_raise` 签名 `-> tuple[Any, int]`（worktree `src:683`；base 代理 main 同址 `:361`）与 4 元组返回不符。T5 未引入，可留待后续清理。
- **P4-4｜`off` 不短路其他 tile env**：`_tile_config` 在 `off` 时仍解析 5 个几何/阈值变量（`:297-357`），故 `NEWMANGA_SFX_TILE=off` + `NEWMANGA_SFX_TILE_HEIGHT=abc` 仍会 fail-fast 阻断普通页。与「anywhere 非法即 ValueError」的文档口径自洽，登记即可。
- （附）复合 provider 中 tile 口径 typed 失败会被 `except ProviderError` 转为 `sfx_provider_status=degraded: PROVIDER_INVALID_OUTPUT`（`src:1037-1047`）——属既有「可选 sfx 检测器降级」设计且审计可见；「fail loudly」在 provider 级成立。

---

## ③ R1–R8 逐项结论

### R1 实现等价性（最重要）— **PASS**（静态逐字等价；未独立复跑）

对照蓝本 `experiments/M2-SFX-GATE-T3/eval_gate_t3.py`：

| 口径 | 蓝本 | 生产 | 判定 |
|---|---|---|---|
| 锚点 `tile_ys` | `:219-227`：`range(0, max(h-H,0)+1, H-ov)`；空则 `[0]`；`ys[-1]+H < h` 补 `h-H` | `src:378-395`：逐字同构（参数化 `tile_h/overlap`），仅追加 `_assert_tile_caliber` 调用 | **等价**（断言不改序列） |
| 页级 NMS | `dedup_boxes:195-216`：`sorted(key=conf, reverse=True)` 稳定贪心；`IoU >= 0.5` 丢弃后来者；`run_tile:440` 末排序 `(-conf, xyxy)` | `_tile_page_nms:450-469`：同排序、同 `>=` 判据、同 `(-conf, box)` 末排序 | **等价**（`reverse=True` 在 Python 保稳定；`_iou:966-974` 与蓝本局部 `iou` 代数同构，逐运算同序） |
| tile 内序列 | `run_tile:425-433`：`crop((0,y0,w,y1))` → `asarray` → `dsfx._letterbox` → `dsfx._sfx_boxes(page_w=w, page_h=th)` → `+y0` 平移 | `_detect_tiles:662-679`：`rgb[y0:y1, 0:page_w]` + `ascontiguousarray` → `_letterbox` → `_sfx_boxes(page_w=w, page_h=tile_h_px)` → `+y0` 平移 | **等价**（PIL crop 与 numpy 切片像素同值；`th == tile_h_px`） |

未发现稳定排序、坐标精度、锚点条件上的任何差异。语义差异候选仅两处，均已排除：numpy 切片 vs PIL crop（同一 uint8 像素源）、`_iou` 的退化分支写法（`ix1<=ix0` 与 `max(0,…)` 在非退化框上逐运算同值）。**局限**：未能在本机执行，等价性为源码级证明 + 作者运行证据的双证。

### R2 路由正确性与安全 — **PASS**

- 边界：`_routes_to_tile:373-375` 为 `page_w > cap → False` + `aspect >= floor`；即 **690 命中、691 不命中、aspect 恰 8.0 命中**。单测 `tests:1069-1077` 四点全钉（690/51971、600/18401、691 拒、690×3000 拒、690×5520=8.0 收、1100×1600 拒）。
- letterbox 原路径：以 base 代理 `main:306-357` 与 worktree `src:557-629` 逐行对照，新增仅 4 处——`tile_cfg = _tile_config()`（`:563`，位于 `_engine_or_raise` 之前）、`page_h/page_w`（`:567`）、`route` 判定（`:568-571`）、options 末尾追加 `("sfx_route", route)`（`:571`/`:626`）。letterbox 分支体（`:583-591`）与 base `:312-320` **逐字一致**，`RegionCandidate` 构造、`elapsed_ms`、其余 options 全同。`sfx_route` 只进 options 审计尾（`DetectionResult.options`），输出候选面零变化。
- fail-fast 时序：`_validate_request`（`:559`）→ `_tile_config`（`:563`）→ `_engine_or_raise`（`:564`），非法 env 先于权重解析；单测 `tests:1142-1155` 用「缺失权重路径」证明 ValueError 先于 `PROVIDER_NOT_CONFIGURED`（20 格）。
- off 开关：`enabled=False → route="letterbox"`（`:568-570`），单测 `tests:1080-1089` 钉住 600×4800 边界。

### R3 P3-2 断言闭合 — **PASS（含 P3-3 边界）**

typed：`ProviderInvalidOutput(ProviderError)`（`ports/providers/errors.py:129-137`），是 `raise` 语句，**`python -O` 不可剥除**；`_tile_ys` 每次调用即断言（`src:394`）。断言面 = 非空（`:412-418`）/首锚点 0（`:419-424`）/相邻差=step 或 bottom_anchor（`:425-434`）/末锚点覆盖页底（`:435-441`）/非退化（`:442-447`），与 Task/部署记录声称逐条对应。覆盖边界见 P3-3。

### R4 AC3 逐位复现证据 — **PASS**（聚合与逐页均与 T3 raw 独立对上）

- T3 矩阵锚点：`verification/M2-SFX-GATE-T3/eval-matrix.json` chiqui7 ko-tile `56/56`、ko-npd `41/135`（`:154-163`、`:200-209`）；v2b ko-tile `35/56`、ko-npd `48/135`（`:478-487`、`:524-533`）；两侧 letterbox 对照 `0/56`、`0/135`。
- 逐页数字独立核对（parity ↔ T3 raw ↔ 矩阵）：
  - v2b ko-tile `14/27 + 17/24 + 2/2 + 2/3 = 35/56`，n_pred 合计 **101**＝矩阵 n_pred 101；ko-npd `14/35 + 26/42 + 5/48 + 3/10 = 48/135`，n_pred 101（T3 raw `eval-v2b-ko-tile.json:421-422/2564-2565/5377-5378/6850-6851`，`eval-v2b-ko-npd.json:426-427/2667-2668/5848-5849/7584-7585`）。
  - chiqui7 ko-tile `27/27 + 24/24 + 2/2 + 3/3 = 56/56`，n_pred 合计 **68**＝矩阵 68；ko-npd `19/35 + 18/42 + 2/48 + 2/10 = 41/135`，n_pred 68（`eval-chiqui7-ko-tile.json:484-485/2399-2400/4525-4526/5584-5585`，`eval-chiqui7-ko-npd.json:489-490/2388-2389/4702-4703/5970-5971`）。
- `bit_parity_vs_t3_raw`：8 个 KO 页全 `true`，且每页 `t3_matched == matched`、`t3_n_pred == n_pred`（parity-v2b.json:13-20 等 / parity-chiqui7.json 同理）。**精度口径如实**：比较发生在 T3 写盘精度（xyxy round 0.1 px、conf round 4），非 IEEE bit 级；脚本 docstring、汇总 `caliber`、部署记录均显式声明「写盘精度 + match_gt 全精度 matched 复算」。属如实披露，非夸大。
- BJ letterbox 零变化：T3 raw `eval-chiqui7-bj-exam.json:57-84`（pre-bj17 3 框）、`:190-217`（pre-bj18 3 框）、matched 2+3=5＝矩阵 `5/5 n_pred 6`；parity-summary `:59-85` 记 `sfx_route=letterbox`、`n_pred=3/3`、`bit_parity=true`，且 `:478` 有断言。
- 重指/恢复纪律：sha 先验断言（`verify_tile_parity.py:337-342`）→ `pin_backup` 捕获（`:354`）→ chiqui7 窗口 `:373-374`/`:447`，两处均 `try/finally` 恢复（`:443-444`、`:483-484`）；v2b 生产 pin 全程原样。与 tile_calib/eval_gate_t3 先例一致。
- 证据弱化项见 **P3-1**（KO 段 bit flag 未进硬断言）。

### R5 AC4 契约与测试 — **PASS（git 级零 diff 未独立验证）**

- 契约/应用面：全仓 grep `SFX_TILE|_detect_tiles|_routes_to_tile|NEWMANGA_SFX_TILE|sfx_route` 仅命中 `src/infrastructure/providers/detection_sfx.py`、`tests/providers/test_detection_sfx.py`、`experiments/M2-SFX-T5-TILE-KO/*.py`；`contracts/**`、`apps/**` 零命中，与「RegionCandidate 输出面不变、唯一 src 文件」静态自洽。**`git diff a3b0f537 -- contracts/ apps/` 未运行**（无 shell），属作者声称 + 静态一致。
- 先红：`raw/test-red-before-impl.log:12` = `ImportError: cannot import name 'SFX_TILE_HEIGHT' from …`（collection error）。红证据真实性：符号确实后来才存在，log 内部自洽；**但「先于 impl 提交」的时序无法独立验证**（无 shell/时间锚）。
- 后绿：`raw/test-green-after-impl.log` = `70 passed in 2.89s`；tile 段（`tests:987-1220`）13 个函数、其中 `test_tile_env_illegal_value_fails_fast_before_any_inference` ×20 参数 = **32 个收集项**，与「+32」一致。
- 全量回归：`raw/regression-run.log:398-399` = `1 failed, 1812 passed, 1 skipped, 1 warning in 127.39s`；唯一失败 `tests/m2_test_assets/test_catalog.py`（`:383-390`，`assert 122 == 97`，gitignored 素材计数），与本 Task 面零交集。基线 1780 有库内证据：`verification/M2-SFX-T4-SWITCH/raw/pytest-regression-console.log:398`、`switch-report.md:86`；`1812 = 1780 + 32` 算术自洽，T4 时该文件 38/38（`switch-report.md:86`）→ +32 = 70/70 亦自洽。
- 偏差登记①（测试初版两处设计错、红证据为首跑 collection error）已如实写入 Task §偏差，未见伪造过程证据痕迹。

### R6 性能数据可信度 — **PASS（协议弱、已如实披露）**

- 协议：`perf_tile_dual.py:83-107` 每页 warm-up 1 次不计 + 计测 1 次；`perf-summary.json:5` 明文。行级数字与 `perf-run.log:3-16`、部署记录 §1 表**三方逐字一致**（CPU 9.26/17.96/11.24/3.36，均值 10.46；GPU v2b 0.95/1.89/1.14/0.34，均值 1.08；GPU chiqui7 均值 1.27）。
- GPU 与生产关系如实：生产 `_build_engine` 仍硬编码 `providers=["CPUExecutionProvider"]`（`src:763-765`）；GPU 档只在 perf 脚本内新建 DML session 并替换引擎元组（`perf_tile_dual.py:69-80`），tile 序列调用生产代码本体，**生产引擎未被改动**，GPU=呈报性质。
- ORT DML warning **已核实**：`perf-run.log:11-12` = `Some nodes were not assigned to the preferred execution providers which may or may not have a negative impact on performance. e.g. ORT explicitly assigns shape related ops to CPU…`，与部署记录 §1 描述一致。
- 参照数据可核：`verification/M2-KO-TILE-CALIB/raw/run-full.log:57` 的 `71.6s`（261 tiles × 2 conf = 522 tile-passes；8.9 s/页推导 `ko-caliber-proposal.md:98`）成立。
- 弱项（已披露）：每页仅 1 次计测、无重复与方差，统计功效低；文档以 directional 措辞登记，不作质量判定。

### R7 纪律 — **PASS（worktree clean 未验证）**

- 「显著」全查：Task、Handoff、tile-deploy-report 均 0 命中；仅出现在禁用声明内（`parity-summary.json:58`、各 T3 raw `wording_discipline`）。
- directional 措辞在位（`perf-summary.json:183`、部署记录 §1「directional 数据如实登记不作质量判定」）。
- gitignored 权重/GT：worktree 内 `**/*.onnx` 与 `**/npd-gt.json` **零命中**；脚本全部指向外部 `G:\CODEX\New Manga.task-envs\…`（权重文件实存：`weights/yolo11s-seg.onnx`、`weights-v2b/yolo11s-seg.onnx`）与其他 worktree（NPD_GT/TRAIN_V4）。
- **worktree clean 未能验证**（无 shell 无法 `git status`）；仅能确认 ref=tip=`aa5095cc…`，工作区是否含未提交改动无法排除。

### R8 Task/Handoff 与证据一致性 — **PASS（含 P4 记录 nit）**

- 交付链逐环核实（reflog `logs/HEAD:3-8`）：`a3b0f537` →（217f3383 doc-only）→ `c11a2a9d` claim → `98338691` impl → `c9880955` test → `24ae2765` verify → `aa5095cc` docs，与 Task/Handoff 声称一致（tip=aa5095cc ✓）。
- 逐 AC 表 ↔ raw：AC2 表 = perf-summary/perf-run（逐字）；AC3 表 = parity-*.json/parity-run.log（逐字，且与 T3 raw 聚合独立对上）；AC4 表 = regression-run.log（1812+1sk+1 failed 逐字）；AC5 文档齐备（Task 回填 + deploy report + Handoff），r1 P3-2 闭合描述与 `_assert_tile_caliber` 实际面一致。
- 偏差四项（测试初版两处设计错 / GPU 呈报性质 / DML warning / 宽参数化缺口）均如实登记；未登记的跨域激活与计数 errata 见 P3-2、P4-1。

### 未能独立验证清单（运行级）

| 声称 | 状态 |
|---|---|
| `pytest tests/providers/test_detection_sfx.py` 70/70、tile 32 项 | 作者声称；log 与计数、基线算术自洽 |
| 先红（ImportError）先于 impl 的提交时序 | 作者声称；log 自洽，时序无锚 |
| `pytest tests -q` 1812+1sk+1 failed、test_catalog pre-existing | 作者声称；log 逐字、失败面与本 Task 零交集、1780 基线有库内他证 |
| AC3 parity / AC2 perf 实际执行 | 作者声称；产物三处互相逐字一致 + 与 T3 raw 独立交叉对上 |
| `git diff a3b0f537 -- contracts/ apps/` 空 | 作者声称；静态零命中自洽 |
| worktree clean / 无未提交改动 | **未验证**（无 shell） |
| 权重 sha 断言（944e8114 / d87389af） | 作者声称；文件实存，sha 未复算 |

---

## ④ 推荐下一步

1. **Codex（集成）**：按 **approved_with_conditions** 接收；把本报告落盘为 `doc/reviews/M2-SFX-T5-TILE-KO-aa5095cc-dsh-r1.md`（我方无写权限），并在 Task `review_events` 登记。
2. **条件收口（可并入集成提交的 doc/脚本 errata，不必返修 src）**：
   - P3-1：`verify_tile_parity.py` KO 段补 `assert all(bit_parity_vs_t3_raw)`，`bit_reproduction` 拆字段/更名；在部署记录注明该门语义（可一行 errata + 不重跑，因现有 flags 全 true）。
   - P3-2：Task §偏差/部署记录 §3 增补「路由按页形全局生效、非 KO 书域长条页亦走 tile（≈20×）」。
   - P3-3：补 1 例 `_assert_tile_caliber` degenerate 负例；注明常量冻结由 `test_tile_constants_are_frozen` 承担。
   - P4-1：补一行 errata「test 提交信息 22 例应读作 32 收集项」。
3. **集成后**：按 T4 先例更新 `doc/STATUS.md`（T5 done @merge <hash>），生产 pin 保持 v2b（944e8114）不变。
4. **下一任务建议（用户收口呈报项 + 已登记缺口）**：
   - **用户裁决**：部署形态 CPU 单档 vs GPU 加速档（GPU 档数据=1.08–1.27 s/页；启用 GPU 需新 Task，生产 EP 现仍冻结 CPU）。
   - **候选新 Task（Codex 释放）**：`M2-SFX-T5-TILE-KO-FU1` —— ① KO 形页宽≠600/690 的路由/口径逐宽校准（KO-TILE §9 既有缺口）；②（若用户选 GPU）`onnxruntime-gpu`/CUDA EP 复测与生产 EP 选择；③ 非 KO 长条页 tile 激活的代价评估与阈值复标。
