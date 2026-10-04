---
task_id: M2-SFX-ANNOTATE-R2
author: ZCode
recipient: DeepSeek Harness（独立 Review）→ 编排会话代行 Codex（集成）
base_commit: 99eab8b6
delivery_head: cb055135
status: in_review
---

# Handoff：M2-SFX-ANNOTATE-R2（T1b-R2 扩标轮：素材补齐+扩审+三集扩集重导出）

## 交付结果

分支 `agent/zcode/M2-SFX-ANNOTATE-R2`（worktree `G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode`），
基线 99eab8b6，交付提交：

| commit | 内容 |
|---|---|
| 9b9916af | AC1 素材登记：cases.json +BJ16-BJ25（+750/−0，既有 100 条 byte-identical）+ material 四脚本（fetch_ko/bj_render/scan_density/finalize） |
| cb055135 | AC5 三集扩集重导出：stage2_finalize_r2.py + verification/M2-SFX-ANNOTATE-R2/stage-r2-final-summary.json |
| （本次 docs 提交） | stage-r2-report.md + 本 Handoff + Task 回填（见 delivery_head 后的 docs head） |

与 AC 逐项对照（全部数字复算口径见 [stage-r2-report.md](../../verification/M2-SFX-ANNOTATE-R2/stage-r2-report.md)）：

- **AC1 素材补齐：PASS**。KO 15 候选直下 15/15（peppercarrot CC-BY-4.0）→ top-5 落位
  ep04/E04P07+E04P08+E04P01 与 ep20/E20P06+E20P01（=K13/K18/K15/K24/K19）；BJ 零新增网络
  下载（复用 M2-TA2B-OPEN-ASSETS 已下载卷 vol01/03/05，PDF sha256 3/3 MATCH，JASRAC 卷
  2/7/11 未触碰），自写 material_bj_render.py 以 pypdfium2 DPI150 渲染 54 候选页（避开
  BJ01-15 已用 source_id）→ chiqui7 整页 letterbox 扫描 top-10 → cases.json BJ16-BJ25
  （字段与 BJ13 同构、pipeline_status 如实全 NOT_RUN、page_sha256 逐页）。对账：fetch_bj
  verify BJ16-25 10/10 VERIFY_OK；resolve_asset_roots BJ 25/25 + KO 在册 15/15 可解析。
- **AC2 BJ 低置信扩审：N/A（空集如实登记）**。R1 残留 BJ 域 11 单元=ref_no_conf 7 +
  conf_lt_0.2 4，conf∈[0.2,0.5) 为 0，无判定输入。
- **AC3 回放 5 页补审：PASS**。6 单元双审全 delete，按判定如实排除出框列表并留痕
  （stage2r2），R1 stage2 链保留；R1 worktree 只读未动（git status 干净）。
- **AC4 BJ 新页预标注+扩审：PASS**。29 候选 → conf≥0.2 13 单元双 AI 审核：终判 confirm 11
  （BJ16/17/18/23/24 → 5 页 complete 正集）/ delete 8（含 BJ25 唯一框 → 零框负证据；
  BJ19-22 全候选 conf<0.2 保持 pseudo）。
- **AC5 三集扩集重导出：PASS WITH DEVIATION**。五 manifest 指纹一致
  `564498e13651bb2e7baba7540e7fd088e7ab17ff5fed438df4c4c162e525ccfa`；train 345/571
  （324 合成 pinned+21 真实）/val 4/53/test 2/5/challenge 0/0；组隔离 14 组 0 违例、
  合成 0 入 test；names 双通道 PASS；labels cls 恒 2/坐标∈[0,1]/stem 0 失配；T1a schema
  794 样本 0 错误。**偏差=challenge 仍空集**（本轮判定范围不含 BJ13/14/15、BJ13 delete
  未翻案、AC2 层空集无翻案输入），按 Task AC5 验收判据允许分支如实登记并交编排裁决。
  **BJ 正集 5 页 11 框入 train（R1 时为 0）**——A′ 主攻毛笔竖排形态首批真实正样本。
- **AC6 零 src：PASS**（git status 仅 experiments/verification 新文件与 gitignored 树；
  遗留=2 个 AC4 工具脚本 untracked，见风险 §6）。

判定全量覆盖：consensus 18 ∪ divergence 1 = 19 单元，uncovered=0，仲裁 1/留用户 0；
`human_review=false` 保真（GT=ai-consensus，沿 R1 §0 口径）。

## 验证证据

环境：Windows；python（复算）= 系统 python 3.14；交付轮工具环境=M2-DOCTR-QUAL-C4-gpu-py312
（pypdfium2/onnxruntime）；被测 commit=cb055135（数据）+ 9b9916af（素材）。

| AC/场景 | 实际命令/步骤 | 结果 | 日志/产物 |
|---|---|---|---|
| AC1 cases.json 保真 | `git diff --numstat 9b9916af~1 9b9916af -- cases.json`；git show 旧版逐条对比 | PASS（+750/−0；前 100 条 byte-identical） | `test_assets/comic_golden_suite/manifests/cases.json` |
| AC1 BJ 页图完整性 | `python test_assets/comic_golden_suite/tools/fetch_bj.py verify` | PASS（BJ16-25 **10/10 VERIFY_OK**；BJ01-15 missing=预期，像素在跨根素材树） | 命令 stdout（逐页 sha256） |
| AC1 全量对账 | `resolve_asset_roots(extra=[R2 suite 根])` 逐 case `find_page_image` | PASS（BJ 25/25；KO 在册 15/15=K01-10 按 R1 manifest 路径 10/10 sha 一致+K13/15/18/19/24 5/5） | report §3.4 |
| AC1 PIL 抽验 | PIL 尺寸+sha256 逐页（KO 5 页、BJ16-25 10 页） | PASS（15/15 一致） | material-selection.json / cases.json page_sha256 |
| AC1 PDF 来源 | TA2B bj_download_manifest.json 三卷 sha256 对盘 | PASS 3/3 MATCH（jasrac=false） | report §3.2 |
| AC2 空集 | R1 user-residual.json BJ 11 单元分层复算 | PASS（ref 7+lt0.2 4；[0.2,0.5)=0） | judgments/units.json counts.bj_lowconf=0 |
| AC3/AC4 双审统计 | 逐批重算 judgments/{codex,agy,arbiter}/batch-*.json | PASS（codex 11/0/8；agy 12/0/7；共识 18；分歧 1；仲裁 1；uncovered=0） | judgments/{consensus,divergence}.json |
| AC5 指纹/组隔离 | 五 manifest fingerprint 读取；group→splits 反查 | PASS（564498e1…ccfa 一致；14 组 0 违例；合成 0 入 test） | final/manifest.*.json |
| AC5 YOLO 硬校验 | 重读盘上 labels（cls/坐标/行数/stem）+ pyyaml 6.0.3 safe_load names | PASS（cls 恒 2 共 629 行；0 越界；571/53/5 行=框数；stem 0 失配；names 逐字） | final/yolo/ |
| AC5 T1a schema | SampleRecord.from_dict+validate 逐样本（794 条） | PASS（0 错误） | report §2.2 |
| AC5 产物在盘 | stage2_finalize_r2.py --step manifest/split/yolo/summary（交付轮全跑） | PASS（产物+摘要 generated_at=2026-10-04T13:17:15Z；artifacts_sha256 8 件登记） | stage-r2-final-summary.json |

未运行项：Dominator 无；本轮无模型训练/推理质量评估（属 T2 范围）；chiqui7 密度扫描与
预标注推理为交付轮已执行（产物在盘），docs 收尾轮未重跑推理、只复算其产物。

## 接收方式

- 仓库：G:/CODEX/New Manga（Git linked worktree `G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode`），
  分支 `agent/zcode/M2-SFX-ANNOTATE-R2`，base=99eab8b6，head=cb055135+docs。
- 复现核对（Reviewer 最小集）：
  1. `python test_assets/comic_golden_suite/tools/fetch_bj.py verify`（BJ16-25 应 10/10 VERIFY_OK）；
  2. 读 `verification/M2-SFX-ANNOTATE-R2/stage-r2-final-summary.json` 与
     `verification/M2-SFX-ANNOTATE-R2/stage-r2-report.md` §2.2 复算记录，抽查任一数字
     （数据树=`training_data/sfx-v1/annotate-r2/`，gitignored）；
  3. 对账脚本需以 `SFX_DATA_ASSET_ROOTS` 指向 R2 suite 根
     （`G:\CODEX\New Manga.worktrees\M2-SFX-ANNOTATE-R2-zcode\test_assets\comic_golden_suite`）
     或 `resolve_asset_roots(extra=...)` 传参——R2 worktree 不在 `importers.DEFAULT_ASSET_ROOTS`。
- 数据路径：`training_data/sfx-v1/annotate-r2/{preannotate,final,judgments,worksheet,scan,selection,ko-candidates,bj-candidates,previews}`。
- 依赖变化：无（pypdfium2/PIL/pyyaml/onnxruntime 均既有生产/实验依赖）。

## 下一任务建议（必填）

- Task ID / 标题：M2-SFX-ANNOTATE-R2 独立 Review（DSH）→ 集成（编排会话代行 Codex）。
- 推荐 Agent / Reviewer：DeepSeek Harness（非作者 Review，Task frontmatter reviewer 已指定）；
  Review 通过后由编排会话代行 Codex 集成（沿 R1 先例：r1/r2 审查→merge→Task done 回填）。
- 推荐原因与前置依赖：Task 合同要求 Reviewer=DeepSeek Harness（非作者）；本交付为
  T2 释放前置，DSH 需复核 A′ 复核表（report §7）与 challenge 空集分支处置是否可接受。
- Recovery point：仓库 G:/CODEX/New Manga；branch `agent/zcode/M2-SFX-ANNOTATE-R2`；
  base=99eab8b6，实现 head=cb055135（docs 提交在其后）。
- 允许修改路径（Review 轮）：`verification/M2-SFX-ANNOTATE-R2/**`（审查证据）、
  `doc/tasks/M2-SFX-ANNOTATE-R2.md`（review_events 回填）。
- 禁止范围与新增授权条件：`src/**`、`tests/**`、数据树（gitignored 只读）、cases.json
  既有条目、R1 交付物；Review 不改实现代码（问题走 review_events 交 Owner 返工）。
- 交付物：DSH review 报告（沿 doc/templates/REVIEW.md）落
  `verification/M2-SFX-ANNOTATE-R2/`；结论 approved / approved_with_conditions /
  changes_requested + P0/P1/P2 分级。
- 验证命令、环境与完成 Gate：上节「复现核对」三项；Gate=判定范围覆盖复核（19 单元
  uncovered=0）+ BJ 正集 5 页 11 框入 train 复核 + challenge 空集分支处置裁决意见。
- 可直接转发给 DSH 的指令：

> 请对 M2-SFX-ANNOTATE-R2 做独立 Review（非作者）。工作区
> `G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode`，分支
> `agent/zcode/M2-SFX-ANNOTATE-R2`，基线 99eab8b6，交付 commit 9b9916af（素材）+cb055135
> （三集）。先读 [Project Rebaseline Plan] 与 [doc/tasks/M2-SFX-ANNOTATE-R2.md] 核对合同，
> 再读 [verification/M2-SFX-ANNOTATE-R2/stage-r2-report.md]（全部数字为 Owner 侧复算，
> 需抽验）与 stage-r2-final-summary.json。重点：①AC1 素材链（cases.json 既有 100 条
> 保真、BJ16-25 登记口径与 BJ13 同构、fetch_bj verify 10/10、resolve_asset_roots 对账
> 需 SFX_DATA_ASSET_ROOTS/extra 指向 R2 suite 根）；②双审统计复算（codex 19=11/0/8、
> agy 19=12/0/7、共识 18/分歧 1/仲裁 1、uncovered=0、human_review=false 保真）；③三集
> （指纹 564498e1…ccfa 五 manifest 一致、组隔离 14 组 0 违例、labels cls 恒 2/stem 0
> 失配、YOLO names 双通道）；④**A′ 复核表（report §7）与 challenge 空集分支（§5.4）
> 的处置是否满足 Task AC5 允许分支条款，给出裁决意见**；⑤R1 底册只读并入证明（67 条
> 逐字节一致+R1 worktree 干净）。输出 REVIEW 模板报告落 verification/M2-SFX-ANNOTATE-R2/，
> 结论+P0/P1/P2 分级；不改实现与数据。

## 风险与遗留

1. **challenge 空集**：BJ13/14/15 无 complete 样本（本轮零新判定、BJ13 R1 delete 未翻案）；
   已按 Task AC5 允许分支登记并交编排/用户裁决（`lock.challenge_note`）。若裁决要求
   翻案，路径=用户抽检通道或 BJ13/14/15 候选页扩标补审后重跑 split+yolo（工具链已就绪）。
2. **BJ 正集量级小**：5 页 11 框（A′ 首批真实正样本）；BJ 域深度仍依赖 324 合成（横排
   系统字体/限定毛笔字体，与真竖排毛笔形态覆盖度未经验证）——T2 Gate 归因时注意。
3. **2 个 AC4 工具脚本 untracked**：`build_r2_units.py`、`stage1_preannotate_bj_new.py`
   未随 9b9916af/cb055135 入库（四脚本+stage2 已入库）；建议集成轮补录，否则 AC4 判定
   单元构建与 BJ 新页预标注过程不可从 Git 复现（产物与判定链在 gitignored 树/判定文件中留痕）。
4. **真实 split 漂移**：R1→R2 real 18/3/1→21/4/2（组池 10→13 组同算法同 seed 重切）；
   与 R1 产物对比时以 `r1_baseline_for_diff` 为准，勿跨指纹直比。
5. **KO 新 5 页未标注**：本轮判定范围不含 KO 新页；K11-15+10 张 KO 候选与 44 张 BJ 候选、
   16 个 BJ conf<0.2 候选留扩标池（`annotate-r2/` 内，后续轮免重下载/渲染/扫描）。
6. **跨 worktree 依赖**：previews 引用 R1 worktree 绝对路径；BJ01-15 像素在 TA2B/E2E 树；
   R2 worktree 不在 DEFAULT_ASSET_ROOTS——对账须 env/extra 指根（见接收方式）。
7. **GT 性质**：ai-consensus（human_review=false），不声称人工标注质量；用户抽检/翻案
   通道（R1 user-residual.json）仍开放。

## 实验附录（实验任务）

- **数据来源与许可**：KO=peppercarrot.com 韩文版页图（CC BY 4.0，attribution；sources 页
  直下 15/15）；BJ=densho810.com 官方免费卷 vol01/03/05（作者 free-use 条款：商用/非商用
  免费、强制署名「ブラックジャックによろしく 佐藤秀峰」、公开使用后 1 个月内邮件报告
  info@densho810.com——**报告窗口至 2026-11-02**；禁 Kindle 商店分发；JASRAC 卷 2/7/11
  未触碰）。合成=R1 渲染产物只读并入（324）。
- **数据 Hash**：cases.json page_sha256 逐页（BJ16-25）；KO 5 页 sha256 在
  material-selection.json；五 manifest 指纹 `564498e13651bb2e7baba7540e7fd088e7ab17ff5fed438df4c4c162e525ccfa`
  ；artifacts_sha256 8 件（summary）；TA2B 卷 PDF sha256 3/3 MATCH。
- **模型/权重版本与 Hash**：chiqui7 密度扫描/预标注引擎=yolo11s-seg.onnx
  （`M2-SFX-DETECT/weights/`，生产 detection_sfx 同款；R1 轮已登记权重 hash，本轮未变更）。
- **Provider/Runtime**：onnxruntime（M2-DOCTR-QUAL-C4-gpu-py312 venv）；PDF 渲染
  pypdfium2 DPI 150；图像校验 PIL。
- **硬件**：本机 GPU（与 R1 相同环境）；docs 收尾轮复算仅 CPU（json/hash/文本解析）。
- **网络策略**：本轮零新增 BJ 网络下载（PDF 复用 TA2B）；KO 15 页直下 peppercarrot 官方
  sources（交付轮）；无镜像源、无凑数 fallback 场景。
- **参数**：seed=20261004（selection 决胜与 split 沿 R1 冻结）；密度扫描 imgsz=1024、
  conf_floor=0.01、BJ 整页 letterbox/KO tile 1024 重叠 128；判定单元门槛 conf≥0.2；
  split=group-hash-rank-v2 组隔离、challenge 单列桶（BJ13/14/15 预留）、合成 pinned train。
- **运行次数**：各步骤单次（产物+摘要时间戳 2026-10-04T12:37-13:17Z 区间）；docs 收尾轮
  复算为独立重读，非重跑。
- **原始结果**：train 345/571（21 real+324 synth）/val 4/53/test 2/5/challenge 0/0；
  双审 codex 11/0/8、agy 12/0/7；终判 confirm 11/delete 8；BJ 正集 5 页 11 框全 train。
- **质量判断办法**：判定=双 AI 共识+分歧仲裁（rationale 全文留痕）；GT 硬校验=T1a schema
  +labels 逐行校验+names 双通道；无模型质量评估（T2 范围）。
- **失败样例**：AC2 目标层空集（R1 残留 BJ 无 conf 0.2-0.5）——如实登记非失败；
  fetch_bj verify BJ01-15 missing=预期（跨根素材树）。
- **限制**：见「风险与遗留」1-7。
- **建议**：集成轮补录 2 个 untracked 脚本；T2 释放裁决以 report §7 复核表为准；
  densho810 报告义务（2026-11-02 前）由素材责任方跟踪。

## DSH r1 审查记录（2026-10-04，approved_with_conditions）

- **Verdict=approved_with_conditions（0×P0/P1、5×P2、6×P3、2×P4）**；AC1-AC6 实质全 PASS（AC5=PASS WITH DEVIATION 合同明许分支）。
- **Q1 空集属实**（DSH 三重复算：user-residual BJ 11 单元=conf<0.2×4+ref_no_conf×7，worksheet BJ 全量 20 单元无 conf∈[0.2,0.5)，124 层 BJ 贡献=0）。
- **Q2 判定质量方向正确**（8/11 confirm 裁切图目视核验一致；BJ17-B02 仲裁裁 delete 方向正确）。
- **Q3 漂移须固定切分**（组级迁移已补入 export-summary `group_split_migration_vs_r1`：717481 train→val 25 框、651664 val→test 3 框）。
- 返修落实：P2-1 计数更正/P2-2 组级迁移+声明/P2-3 BJ held-out 缺失登记/P2-4 框粒度口径+编排原页对照实证（BJ17 双框合并、BJ18/23 独立实例）/P3-1 扩标池位置/P3-2 cases_json_note 更正并重跑 assemble+finalize 全链（指纹不变 564498e1…）/P3-3 列举补全/P3-4 pixel_size 登记/P3-5 .bak 删除/P4-1/P4-2 措辞。
- 集成轮：P3-6 两 untracked 脚本补录；merge→Task done。
