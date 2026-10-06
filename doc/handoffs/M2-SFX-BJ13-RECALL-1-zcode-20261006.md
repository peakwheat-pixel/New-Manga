---
task_id: M2-SFX-BJ13-RECALL-1
author: ZCode
recipient: Codex（集成）/ DeepSeek Harness（非作者 Review）
base_commit: 2a1a9f73（release-followup：PLAN 三行回填实际 release hash 630c3f51）
delivery_head: d95bbdfe（首轮 verify 证据锚；其后的 fix(review) r1 返修 commit 为当前证据锚——r1fix 重跑互证+全部条件闭合，hash 见 git log 分支头）
status: delivered → DSH r1 approved_with_conditions（0×P0/P1；1×P2+5×P3+7×P4）→ fix(review) 返修交付，待 DSH r2 或集成收口（Task status: in_review 停写）
---

# Handoff：M2-SFX-BJ13-RECALL-1 — BJ13 召回恢复链（v2b 生产链召回实测探针，零 src）

## 交付结果

AC1-AC5 全部交付，**零 src**（`src/**`/`tests/**` 零字节变化）。在当前 v2b 生产链语义（letterbox 路由、conf 0.5、NMS IoU 0.7、`NEWMANGA_SFX_EP` 默认 dml 实测生效、v2b 权重 pin `944e8114…d418d` 由 `_build_engine` 强制校验）对 BJ13/BJ14/BJ15 + 域内对照 BJ06 完成 sfx 召回实测，回答「召回恢复是否发生」三态结论：

- **BJ13：部分恢复（信号面）**——两个目检拟声词参照框在 conf≥0.5 下**零检出**（产品行为与 chiqui7 零差异，误路由 manga-1/3 乱译照旧）；但参照框内低 conf sfx 信号较 chiqui7 基线真实抬升（ref1 0.3727/IoU 0.5235 = 4.4x；ref2 0.1796/IoU 0.5584 = 42x）——fine-tune 域适应起效但未达生产 conf 线。
- **BJ14：未恢复**（conf≥0.01 全 rung 零候选）。**BJ15：未恢复**（参照框零；页面级孤立候选 conf 0.5118 仅注记）。
- **BJ06 对照：5/8 region 命中**（chiqui7 为 8/8；该回退为 T4 G7 已登记形态，本探针与 G7 v2b 臂**逐框亚像素一致**（5=5，差 <0.5px 存储取整）——探针有效性的最强判别）。
- **AC2 分支履行**（部分恢复触发）：BJ13 真实形态 sfx×primary **max IoU=0.0**——0.90 冻结域无对象（比历史合成口径 0.490/0.550 更远离），重审条件语境读法未触发；**提案=维持 0.90 冻结域不变**（域内 0.8732<0.90 与历史 0.8865 同侧同形态；降阈值只会造成域内真对白 precision 损害且对 BJ13 零收益）。`sfx-arb-` 改标链路本次零触发。
- **AC3 分支登记**：③维持现状（推荐 1，兜底已在位）→ ②ai-direct 补画形态扩展（推荐 2）→ ①BJ13 补标（推荐 3，须先翻案 R1 delete 并与 fine-tune 反转条件联动）——交用户裁决。
- **新增事实（历史口径修正）**：chiqui7 在 BJ13 并非页面级零检出——仲裁 rerun raw `sfx-1`（conf 0.8222）即 Slipknot T 恤印刷字检出；v2b 同位 conf 0.8914、跨权重框 IoU 0.9444（两代权重在该区——DOMAIN-EXT-DIAG 判定域外页 BJ13——判定一致的正面证据）。DOMAIN-EXT-DIAG「零响应」仅在拟声词参照框口径成立。Slipknot 区无 ogkalu text 候选 → 孤立 sfx region → SfxPolicy SKIP，无乱译损害、无仲裁材料。
- **DSH r1 返修（2026-10-06，approved_with_conditions 全条件闭合，全部文本级）**：P2-1 chiqui7 基线 imgsz 更正 1024（两代同 imgsz，4.4x/42x 无 letterbox 混杂）+基线 CPU↔本次 DML 跨形态声明（P4-6 随闭）；P3-1 tile 路由不适用登记；P3-2 BJ06 自证清单限制承继；P3-3 探针 conf 口径两点差异登记；P3-4 base_commit 对账统一 2a1a9f73；P3-5 r1fix 重跑互证（json 全树逐位一致，原 raw 零触碰）；P4-3/P4-4/P4-5 措辞修正；P4-7 类别翻转证据补登（chiqui7 text 0.5195/sfx 0.0855 → v2b sfx 0.3727/text 0.0）。逐条对照见 Task 执行记录 r1 返修段。
- 变更路径：`experiments/M2-SFX-BJ13-RECALL-1/recall_probe.py`（新建，唯一脚本）、`verification/M2-SFX-BJ13-RECALL-1/**`（报告+2 raw）、`doc/tasks/M2-SFX-BJ13-RECALL-1.md`（回填）、本 Handoff。
- commit 链：`0f175b89` claim → `47df4dbc` impl → `d95bbdfe` verify → docs（本文件+Task 回填，tip 为分支头）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 四页召回实测 | `"G:/CODEX/New Manga.task-envs/M2-SFX-T5-TILE-gpu/Scripts/python.exe" experiments/M2-SFX-BJ13-RECALL-1/recall_probe.py`（fail-fast：引擎 exit 4/页面 exit 2/primary 身份漂移 exit 3） | venv M2-SFX-T5-TILE-gpu（onnxruntime 1.24.4 DML+numpy 2.5.3+PIL 12.3.0）；HEAD=`d95bbdfe`；权重 pin `944e8114…`（sha256 门强制） | **EXIT=0**；`ENGINE OK imgsz=1024 (metadata_parsed) ep_requested=dml ep_effective=dml ep_fallback=None`（真 DML 无回退）；每页 session.run 0.007-0.016s（GPU 前向口径，letterbox 不计入） | `verification/M2-SFX-BJ13-RECALL-1/raw/recall-probe-run.log`、`raw/recall-probe.json` |
| 有效性交叉验证（探针↔生产装配） | BJ06 五个 conf≥0.5 sfx 框与 `verification/M2-SFX-T4-SWITCH/raw/g7-smoke-v2b/summaries/qual-BJ06.json` 的 5 个 sfx region 逐框比对 | G7=2026-10-05 生产装配 deep-call smoke（v2b 臂） | **PASS**：计数 5=5、五框亚像素一致（G7 整型存储差 <0.5px）；类分布形态一致（v2b 四页 bubble/panel/text 通道 conf≥0.01 全零） | recall-report §1；G7 json 为既有证据 |
| AC2 重审切片 | 探针内建：真实 sfx 候选 × 仲裁 rerun primary（`manga-` 前缀过滤，与 `arbitrate_bj13.py:215` 一致；`sfx-N` 排除并登记）；primary 复用合法性=ogkalu 三文件 sha256 当次重验 vs `detection_manga.py` 冻结 pin | 同上，HEAD=`d95bbdfe` | **PASS**：BJ13 max=0.0（无对）；BJ06 max=0.8732/0.85+ 对 1/内含形 1（prim⊆sfx，IoU 0.7576）/模拟 0.90 relabels=0+partial 0.8732；四页 `sfx-arb-` 零触发 | `raw/recall-probe.json` `arbitration_overlap_vs_primary_rerun` 段；提案=recall-report §3.3 |
| AC3 三选项登记 | 报告撰写（不新发明方案） | — | **PASS**（③②①推荐序+成本收益） | recall-report §4 |
| AC4 零 src+纪律 | `git status`（src/tests 零变化）；`git diff --check` | HEAD=`d95bbdfe` | **EXIT=0**；不跑全量 pytest 的理由=代码面零改动+冻结回归锚未触碰+只读 import（recall-report §5） | recall-report §5 |
| AC5 文档 | 报告+raw+Task 回填+本 Handoff | — | **PASS** | `verification/M2-SFX-BJ13-RECALL-1/recall-report.md`、`doc/tasks/M2-SFX-BJ13-RECALL-1.md` 执行记录段 |
| r1fix 重跑互证（DSH r1 P3-5） | 同一探针重跑：`"...M2-SFX-T5-TILE-gpu/Scripts/python.exe" experiments/M2-SFX-BJ13-RECALL-1/recall_probe.py --out-dir verification/M2-SFX-BJ13-RECALL-1/raw/r1fix`（log 含命令行/venv/EP/EXIT 头） | r1fix commit；同 venv/同权重 pin/同页面 | **PASS**：与原 run json **全树逐位一致**（排除 `generated_at_utc`/`inference_s` 后 0 diff；四页 conf≥0.5 sfx 5/1/0/1、BJ06 max 0.8732、BJ13 ref1 峰值 0.3727 全部相同）——同形态 DML→DML run-to-run 确定性互证（非跨形态声明）；原 raw 文件零触碰 | `verification/M2-SFX-BJ13-RECALL-1/raw/recall-probe-run-r1fix.log`、`raw/r1fix/recall-probe.json` |

明确未运行项：①CPU 对照臂（DML 单形态实测；跨形态比较按 ≤2e-06 漂移窗口既有登记，禁写位级可复现）；②全量 pytest（零 src 保证，理由上表）；③BJ15 孤立候选与 Slipknot 的 GT 判定（无标注，仅登记不采信；Slipknot 视觉核查=Owner 对裁剪临时图目检，未入库）。

## 接收方式

- 分支 `agent/zcode/M2-SFX-BJ13-RECALL-1` @ worktree `G:/CODEX/New Manga.worktrees/M2-SFX-BJ13-RECALL-1-zcode`；base=`2a1a9f73`，delivery_head=`d95bbdfe`（docs commit 为其后继，tip 以分支头为准）。
- 复现探针：`"G:/CODEX/New Manga.task-envs/M2-SFX-T5-TILE-gpu/Scripts/python.exe" experiments/M2-SFX-BJ13-RECALL-1/recall_probe.py`（worktree 根执行；权重在 gitignored task-envs、页图在 peer worktree `test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/`——该目录由其 `.gitignore:26` 忽略，零入库结论不变；路径+sha256 登记于 recall-report §1）。
- Review 检查建议：①raw json 的 `excluded_non_primary_labels`（BJ06 八个 `sfx-N`、BJ13 一个 `sfx-1`）核对仲裁口径（`arbitrate_bj13.py:215` 同过滤）；②G7 逐框对位（recall-report §1 表）；③BJ13 三态判据的 Owner 裁量线（IoU≥0.1 恢复/≥10x 或 conf≥0.2 部分恢复）是否接受；④AC2 提案「维持 0.90」的理由链（§3.3 三条）。

## 下一任务建议（必填）

- Task ID / 标题：M2-SFX-BJ13-RECALL-1 r2 独立 Review（DSH 非作者；核 r1 approved_with_conditions 全条件闭合）
- 推荐 Agent / Reviewer：DeepSeek Harness（Owner=ZCode 非作者隔离成立）
- 推荐原因与前置依赖：r1（0×P0/P1；1×P2+5×P3+7×P4）返修已全部文本级闭合；依赖=本分支 fix(review) 返修 commit（tip 以 git log 分支头为准，delivery_head 注记见 frontmatter）；无新授权需求（零 src，review 只读+写 review 文件）。
- Recovery point：`G:/CODEX/New Manga.worktrees/M2-SFX-BJ13-RECALL-1-zcode`，branch `agent/zcode/M2-SFX-BJ13-RECALL-1`，base `2a1a9f73`，首轮 verify 锚 `d95bbdfe`，返修=fix(review) commit（tip 为准）。
- 允许修改路径：`doc/reviews/M2-SFX-BJ13-RECALL-1-<head>-dsh-r2.md`（新建）。
- 禁止范围与新增授权条件：零 src/零 tests；不改冻结阈值域与历史证据文件；status 变更与集成由 Codex 处置。
- 交付物：Review 报告（r1 全条件闭合核对+AC 判定）。
- 验证命令、环境与完成 Gate：探针可按接收方式复跑（DML venv，<1 min；r1fix 逐位互证已登记，r2 可再跑一次核对三度一致）；Gate=Review 报告落档、判定明确（approved / changes_requested）。
- 可直接转发给 Agent 的指令：「对 M2-SFX-BJ13-RECALL-1 做非作者 r2 Review（核 r1 approved_with_conditions 全条件闭合）：worktree `G:/CODEX/New Manga.worktrees/M2-SFX-BJ13-RECALL-1-zcode`，分支 `agent/zcode/M2-SFX-BJ13-RECALL-1`，tip 以 git log 为准（r1 原始报告=编排方 /tmp/dsh-bj13-r1/result.md，r1 返修对照=Task 执行记录 r1 返修段+`doc/handoffs/M2-SFX-BJ13-RECALL-1-zcode-20261006.md` 返修条目+`verification/M2-SFX-BJ13-RECALL-1/recall-report.md`）。逐条核：P2-1 imgsz 1024（三项记录对齐）、P3-1 tile 不适用、P3-2 BJ06 自证限制、P3-3 conf 口径两点、P3-4 base_commit=2a1a9f73、P3-5 r1fix 逐位互证（`raw/recall-probe-run-r1fix.log`+`raw/r1fix/recall-probe.json`，原 raw 零触碰）、P4-3/4/5/6/7 各措辞与补登。结论写 `doc/reviews/M2-SFX-BJ13-RECALL-1-<head>-dsh-r2.md`，不改 src/tests/冻结域/原 raw。」
- 集成收口（Review 通过后，Codex）：AC2 提案（维持 0.90）与 AC3 推荐序交用户裁决（r1 复核建议：双分支按原文双口径呈报，不取其一）；无需 src 集成动作；若用户选③维持现状，BJ13 依赖链注记保持 open 并以下次 sfx 权重迭代为复测点（本探针脚本可直接重跑，r1fix 互证已证确定性）。

## 风险与遗留

- BJ13 的「自动化闭合」最终目标**未达成**（参照框零召回→误路由 manga-1/3 仍乱译）；损害兜底=UI-MITIGATION 实现+`sfx-policy=skip` 既有面（已释放）。
- BJ06 域内对照 5/8（v2b 较 chiqui7 少 3 检出）为 T4 已接受形态，本探针如实复现——若未来翻案 fine-tune 路线，此读数是基线之一。
- primary 候选为 2026-10-03 仲裁 rerun 复用（非当次重跑）：ogkalu 快照身份当次重验一致+确定性复现既有口径；亚像素级重跑差不影响读数量级（BJ06 0.8732 距 0.90 余量 0.027；BJ13 为 0.0）。
- G7 harness-meta 未登记运行时 EP 形态；「逐框亚像素一致」对位不依赖 EP 假设（DML↔CPU 漂移 ≤2e-06 远小于 0.5px 存储粒度）。
- BJ15 孤立候选（conf 0.5118）真伪不可判定（无 GT）；下次权重迭代复测时顺带观察其稳定性。
- 措辞纪律执行登记：本交付全篇按 DML 单形态口径表述，未出现「位级可复现」；跨运行对位表述为「逐框亚像素一致（<0.5px 存储取整差）」。

## 实验附录

- 权重：`G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx`，sha256 `944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d`（=src pin，T4 @cff4923e；部署链 base .pt `1f0fd609…`/best.pt `c22f0175…`/best.onnx `944e8114…` 见 `detection_sfx.py:115-122` 注释）。零入库。
- 页面像素（零入库；peer worktree，页图目录 `test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/` 由该目录 `.gitignore:26` 忽略，DSH r1 P4-5）：BJ06 `G:/CODEX/New Manga.worktrees/M2-TA2B-OPEN-ASSETS-zcode/test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/vol03/pages/vol03_p0056.png`；BJ13/14/15 `G:/CODEX/New Manga.worktrees/M2-SFX-E2E-MATERIAL-zcode/.../vol03_p0048.png / vol03_p0060.png / vol03_p0159.png`。
- Runtime/硬件：onnxruntime 1.24.4（DmlExecutionProvider 生效）、numpy 2.5.3、PIL 12.3.0、Windows x64、DirectX12 DML 设备；imgsz=1024（v2b ONNX metadata，与 chiqui7 生产基线相同——P2-1 更正，三项记录一致）；NMS IoU 0.7（冻结）、conf 0.5（冻结）。
- primary 快照：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector`（model.safetensors `037930a8…`/config.json `b6d70793…`/preprocessor_config.json `7e9e2245…`，与 pin 逐一一致）。
- 运行次数：每页 1 次推理（conf≥0.01 全保留+分 rung 过滤）+pre-NMS 参照框内查询（同一次推理输出共享，docstring 登记与先例「每 ref 重跑」的改编差异及理由）。
- 原始结果：`raw/recall-probe.json`（含 per-rung 类计数、参照框 verdict、pre-NMS top20、BJ06 region 命中、四页仲裁重叠对全列）。
- 质量判断办法：三态判据（Owner 裁量，recall-report §2）+G7 生产装配逐框交叉验证+pre-NMS/NMS 后双口径同值（NMS 未吞信号）自洽检查。
- 失败样例：无（EXIT=0）；首轮交付三轮运行中第 1 轮为口径缺陷（未过滤 `sfx-N`），已修正并重跑，缺陷形态登记于 recall-report §3 口径注记；r1 返修再补一次 r1fix 重跑（逐位互证，见验证证据表末行）。
- 限制与建议：见 recall-report §6（引用时不得省略）。
