---
task_id: M2-REGION-OVERLAP-ARBITRATION
author: ZCode（Owner 实现 subagent）
recipient: Codex（Integrator，编排会话代行）；Reviewer=DeepSeek Harness（非作者）
base_commit: eb7cd15e
delivery_head: b27c826f
status: r2_delivered_awaiting_dsh_r2
---

# Handoff：M2-REGION-OVERLAP-ARBITRATION（region 创建跨 provider 重叠仲裁）— r2 返修版

- **r2 修订声明**：DSH r1（`changes_requested`，0×P0；3×P1+5×P2+4×P3+4×P4）已逐条处置（对照表=[arbitration-report.md §9](../../verification/M2-REGION-OVERLAP-ARBITRATION/arbitration-report.md)）。编排裁决 P1-1 采纳选项 (a)：**AC2 修订为「结构性不可达登记 + 近重复双检出形态级闭环」**（Task 文件 AC2/目标/依赖段同步改写，标注裁决日期与依据）。r2 新增 KO 域 10 case 证据（P1-2）与第二道门量化评估（P2-2）。Owner 程序瑕疵（未预提交范围修订请求）已登记，不再追责。

## 交付结果

- **分支/worktree**：`agent/zcode/M2-REGION-OVERLAP-ARBITRATION` @ `G:/CODEX/New Manga.worktrees/M2-REGION-OVERLAP-ARBITRATION-zcode`；base=`eb7cd15e`、claim=`8c74d170`、实现主体（delivery_head）=`b27c826f`、r1 文档收尾=`4d8aaee0`、r2 返修=本 Handoff 所在 commit（提交链见 git log）。
- **提交清单**：`8c74d170` claim → `b27c826f` 实现主体（`detection_sfx.py` 仲裁 + 15 仲裁用例 + 分发矩阵锚定行）→ `0451c84a` r1 证据/报告 → `4d8aaee0` r1 Handoff/Task → r2 commit（P4-1 src 重命名 + P4-2/P4-4 experiments 清理 + `ko_iou_scan.py` + KO raw + 报告 r2 + 本 Handoff/Task 同步）。
- **AC 对照（r2）**：
  - **AC1 PASS**（DSH r1 确认）：拼接层 + bbox IoU + directional 改标 + 冻结 0.90 + 双 env typed 旋钮。
  - **AC2 DELIVERED（编排裁决 (a) 修订口径）**：①结构性不可达登记——BJ13 红态真实对位，双层不可达（现状 sfx 零候选 + 召回恢复后 0.49-0.55 仍在 0.90 域外）typed 可诊断，召回恢复前 **no-op**（挂 sfx 召回恢复 Task 依赖链）；②近重复双检出形态级闭环（实现路径验证，代码级）：口径 B 3/3 改标落 RegionType.SFX；**真实 0.90+ 形态至今 0 观测**（BJ 4 页 22×25 + KO 10 case 全部真实候选对）。绿态成立条件=`sfx.policy=skip`（qual-BJ06 translate 实测背书门消费；translate 残余损害未评估限定）。
  - **AC3 DELIVERED（KO 补证后完整）**：BJ06 off/on 逐位一致（17=17）+ **KO 10 case off/on 全部逐位一致**（合计 1034 候选；sfx 候选 1 @K11，sfx×primary 最高 IoU **0.1325**，0 对 ≥0.90，无 STOP）+ qual 基线对位；三套件 r2 重跑 **627 passed + 1 skipped，0 failed，EXIT=0**（显式落码）；cargo/vitest 零改动面。
  - **AC4 PASS**（DSH r1 确认）：env typed 拒绝 + 冻结依据 + 不可达 typed 诊断；off 回退经 BJ06+KO 11 次真实 off 跑复验。
  - **AC5 PASS**（DSH r1 确认）：零契约面；options 新键消费方审计证明非 wire（§3.4）。
- **结构性定案（Review 必读）**：域内/误路由重叠反向不可分离（0.886 vs 0.490-0.550，DSH 手算确认）；0.90 的安全性=观测经验+AC3 经验回归（margin 0.0135/0.0138 + 内含形敏感 + 参照框不确定度 ±0.03-0.05 三项登记，§1.3.2），**非几何保证**；重审条件挂召回恢复 Task。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC2 红态+不可达+形态级闭环 | `arbitrate_bj13.py`（r2 清理版） | M2-TA3-B-ocr venv；ogkalu（pin 校验）+chiqui7（pin 校验）；@r2 | PASS（同 r1：BJ13 3+1 对位；口径 A partial 0.5501；口径 B relabels=3 全 RegionType.SFX） | `raw/{arbitrate-run.log,arbitrate-pages.json,arbitrate-manifest.json,bj06-on-off-candidates.json}` |
| AC3 BJ06 | 同上（off/on 双跑） | 同上 | PASS（17=17 bit-identical） | `raw/bj06-on-off-candidates.json` |
| AC3 KO（r2 P1-2） | `ko_iou_scan.py`：10 case off/on 各一次真实推理（K01-K10 tiling，~700 tiles×2） | 同上 | **PASS：10/10 逐位一致；最高 IoU 0.1325（K11 唯一 sfx 候选）；无 STOP 条件** | `raw/ko-scan/`、`raw/ko-scan-run.log` |
| AC3 套件（r2 重跑） | `T1.1.1-impl-py312/.../python.exe -m pytest tests/providers tests/core tests/m2_acceptance -q -p no:cacheprovider -rs`（日志显式 `EXIT=$?`） | T1.1.1-impl-py312 | **627 passed, 1 skipped, 0 failed, EXIT=0** | `raw/pytest-three-suites-r2.log` |
| AC3 全量（补充口径） | 同 venv 全量 | 同上 | 1731+1sk, 1 failed（本地素材计数环境性失败，与本 Task 零交集）, EXIT=1 | `raw/pytest-full-suite-r2.log` |
| AC4 env typed 拒绝（先红后绿） | 实现前 14 failed/1 passed（EXIT=1）→ 实现后全绿 | 系统 python 3.14 | PASS | `raw/red-phase-arbitration-tests.log` |
| P4-1 src 改动复验 | `python -m pytest tests/providers/test_detection_sfx.py -q -p no:cacheprovider` | 系统 python 3.14，@r2 | 38 passed | §3.5 r2 复验行 |
| AC5 契约零变化 | `git diff --stat`；`git diff --check` EXIT=0；options 消费方审计（§3.4） | @r2 | PASS | git + 报告 §3.4 |
| cargo/vitest | 未运行（零改动面声明） | — | N/A（集成方复跑） | — |

## 接收方式

- 分支/worktree 同 r1；Review 起点=r2 commit（实现仍为 `b27c826f` 未变，仅 P4-1 变量重命名属其后续 commit）。
- 复现：报告 §7 三条命令（BJ rerun / KO 扫描 / 三套件）。
- DSH r2 复核建议重点：①P1-2 KO 证据的口径（off/on 双真实推理、K11 唯一 sfx 样本的重叠上界 0.1325）；②§1.3.2 三项登记（margin/内含形/不确定度）是否闭合 P2-4/P3-4；③P2-2 第二道门「零区分力」结论；④P1-1 修订后的 Task 合同文本与实现的一致性。

## 下一任务建议（必填）

- Task ID / 标题：M2-REGION-OVERLAP-ARBITRATION 的 DSH r2 复核（现行 Task 内流转）
- 推荐 Agent / Reviewer：DeepSeek Harness（非作者；编排方派发）
- 推荐原因与前置依赖：r1 16 条已全部处置，需 r2 verdict；P1-2 KO 证据与 P1-1 合同修订为重点复核对象。
- Recovery point：本仓库、branch `agent/zcode/M2-REGION-OVERLAP-ARBITRATION`、worktree 如上、base=`eb7cd15e`、实现 head=`b27c826f`、r2 tip=本 commit。
- 允许修改路径：review 意见落 `verification/M2-REGION-OVERLAP-ARBITRATION/` 与 Task 文件交付记录；返修限 Task 允许面。
- 禁止范围与新增授权条件：Task 合同禁止范围不变。
- 交付物：r2 verdict 文档（模板 doc/templates/REVIEW.md）。
- 验证命令、环境与完成 Gate：报告 §7 三条命令；Gate=r2 verdict + 集成方复跑三套件与 cargo/vitest。
- 可直接转发给 Agent 的指令：
  「对 `agent/zcode/M2-REGION-OVERLAP-ARBITRATION` r2 tip（base `eb7cd15e`、实现 `b27c826f`）出具 DSH r2 复核：读 `arbitration-report.md` §9 闭合对照表逐条核对 16 条处置；重点复核 §3.2 KO 证据、§1.3.2 三项登记、§3.3 第二道门结论、Task AC2 修订文本；复跑报告 §7 三条命令；非作者约束。」

## 风险与遗留

1. **BJ13/14 现状不闭合（登记为不可达）**：本仲裁对当前生产权重下的 BJ13 误路由乱译损害**无直接缓解**（no-op until 召回恢复）——损害兜底仍是 M2-SFX-MISROUTE-UI-MITIGATION（人工改标）+ SfxPolicy 默认 SKIP 既有面；自动化闭合挂 sfx 召回恢复 Task（fine-tune 路线用户裁决②暂不投入，反转条件已登记）。
2. **0.90 域的未来行为与脆弱性**：内含形（IoU 上界 1.0）可击穿任何有限阈值；margin 0.0135/0.0138 < 参照框不确定度传播——0.85+ 对或内含形出现时必须重审阈值域（登记条件）。
3. **同位置双 SFX region 副作用**（P2-3）：触发时 region 计数+1、UI 双 region 展示、OCR 双跑——去重切片候选已登记。
4. **全量 pytest 的 1 个环境性失败**（本地素材计数 97 vs 100）：与本 Task 零因果，建议编排/集成方择机清理本地 `test_assets` 状态或断言改区间校验（另行小切片）。
5. **UI-MITIGATION 接口注记**需 Codex 转写（本 Task 未改他人 Task 产物）。
6. 回退方法：revert 实现链，或运行时 `NEWMANGA_SFX_ARBITRATION=off`（回退语义经 BJ06+KO 11 次真实 off 跑复验）。

## 实验附录

- 权重：ogkalu `ogkalu/comic-text-and-bubble-detector` @ `16e8a622`（三文件 pin provider 强制校验）；chiqui7 `chiqui7/yolo11-manga-seg` @ `7f5f5c04`（sha256 pin 强制）。
- Runtime：M2-TA3-B-ocr venv（torch 2.14.0+cpu、transformers 5.17.0、onnxruntime 1.30.0 CPU、PIL，`Image.MAX_IMAGE_PIXELS=None` 供 KO 长条页）；KO 扫描耗时合计 ~4.5 分钟（paged 秒级、长条 6-42s/页/次）。
- 网络：全程离线。参数：仲裁默认 `on`/0.90；其余沿生产冻结值。
- 原始结果：`raw/arbitrate-pages.json`、`raw/arbitrate-manifest.json`、`raw/ko-scan/*.json`、`raw/bj06-on-off-candidates.json`。
- 质量判断办法：同 r1 + KO off/on 指纹对照与 IoU 上界扫描。
- 失败样例：无（两个实验脚本单次通过 EXIT=0；KO 扫描含断点续跑设计，本跑未中断）。
