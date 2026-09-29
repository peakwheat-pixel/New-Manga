---
reviewer: DeepSeek Harness (non-author, static)
imported_by: ZCode (M2-DOCTR-QUAL-PREFLIGHT owner, r5)
original_location: task-envs/M2-DOCTR-QUAL-work/dsh-review-r2.md
---

复核完成。以下为第 2 轮独立复核结论。

approved_with_conditions

# 复核方法与被审对象固定

| 项 | 事实 | 来源(只读) |
|---|---|---|
| 被审对象(r1 实现) | `4d9d8d0c96facea9e75d5afa710fdc2d538bac7e` | Handoff L8 + `.git/logs/refs/heads/agent/zcode/M2-DOCTR-QUAL-PREFLIGHT` |
| r2 修订头 | `3e86c800f4c9b28b246787ae470a364c90ae1e42`(单提交,`fix(...): address DSH r1 changes_requested (P0-1..P3-8)`) | 同上 reflog + `.git/refs/heads/...` |
| r2 新增文件是否入库 | **已跟踪**:`.git/index` 中逐名命中 `snapshot_weights.py`、`env-gpu-py312.json`、`hash-recomputation.txt`、`consistency-and-sensitivity.json`、`git-evidence.txt` | 直接检索 `.git/index` |
| 分支/HEAD | `agent/zcode/M2-DOCTR-QUAL-PREFLIGHT` = `3e86c800` | `.git/HEAD` |

**环境限制披露(必须)**:本会话 DSH 沙箱 `pwsh` 全量失败(`SetNamedSecurityInfoW failed (Win32 5): grantWrite`),`danger-full-access` 升级无审批通道,故**无法执行 git / python**。这与 `doc/STATUS.md` 中 M2-AC2 checkpoint 记录的 DSH `grantWrite` 先例一致。替代手段:①直接读 `.git/logs/HEAD`、`.git/index`、`.git/refs/**` 做身份与入库核对;②对全部指标做**原始 JSON 字段级重读**(非抽样)并与报告逐数比对;③跨文件一致性交叉核对。

**无法独立复算项(如实声明)**:权重/素材 SHA-256 未由本 Reviewer 重算(需 hashlib);`sha256` 仅完成"三处引用互等 + 格式/字节数自洽"核对。

**编号约束披露**:r1 Review 原文未入库(`verification/M2-DOCTR-QUAL/` 下无 review 文件),本表按派发单给出的对照表 + `baseline-summary.md §8` 对齐编号;其中 **P3-5 未被 §8 落实清单点名**,经对照派发单唯一未编号项(`git 层证据(git-evidence.txt)`)判定 P3-5 = git 层证据。

---

# 逐项核对表

## P0 与 P1

| 编号 | r2 声称 | 独立核对结果 | 判定 |
|---|---|---|---|
| P0-1 | Handoff 固定 r1 head + 提交列表 + 变更路径 | Handoff L8 固定 `4d9d8d0c`、列 `480f12a2`+`4d9d8d0c`、变更路径全集;与 reflog、`git-evidence.txt` diff --stat 双向吻合 | **closed** |
| P1-1 | `snapshot_weights.py` 新建(不符即中止);Task AC1 行改引 | 脚本 L93–97 不符即 `SystemExit`、L99–103 复制后复算;Task L59 已改引;`.git/index` 命中该文件 = 入库 | **closed** |
| P1-2 | `env-gpu-py312.json` 版本/cuda/device/计时/峰值显存机器可读 | 字段齐全(→ N1 数值冲突) | **closed(附 N1)** |
| P1-3 | FP 归因加 `attribution_available`;§5 改 union 2985/2 | `eval_detection.py` L308–310/423–433;seg05 → `false`,union → `true`、`2985/2/2983` 与 §5 "2985/2(0.07%)" 一致 | **closed(附 N3)** |
| P1-4 | `thresholds.json` 三字段;§4 双口径 + 待裁决 | `primary_layer/judging_criterion/criterion_note` 齐;§4 L56 口径偏离显式上交,§4 表三层并列 | **closed** |
| P1-5 | results schema@2 含 `manifest_sha256`/`manifest_gt_mode`/`manifest_n_gt_boxes`;全部重跑绑定 | 5 份 results 全为 `eval-results@2`;seg05 四份指纹同为 `4f16425a…f11e`、union 为 `c62b7014…e499`;`gt_mode`/`917`/`1184`/`511` 全对 | **closed** |
| P1-6 | Harness 侧独立复算 + 逐块坐标比对;`n_match`/`coords_max_abs_delta_px` | `smoke_adapter_check.py` L25–47 独立前向 + 聚类;JSON `n_match=6`、`overall=0.0`、逐 region `count_match=true`/`coords_match=true` | **closed(附 N4)** |

## P2

| 编号 | r2 声称 | 独立核对结果 | 判定 |
|---|---|---|---|
| P2-1 | Pillow 声明 | `build_eval_manifest.py` docstring L7–8 + L91 | **closed** |
| P2-2 | seg05 manifest 命名 | L273 `eval-manifest.{level}.{gt_mode}.json`;引用全一致 | **closed** |
| P2-3 | region 全宽/y 不重叠断言 | L93–105 双断言(`b0 < a1` + `x0==0 and x1==strip_w`),L163 调用 | **closed** |
| P2-4 | pad 敏感性对照 | `consistency-and-sensitivity.json` production `0.4776/0.1250/0.7531/0.0385` ↔ shrunk6 `0.2628/0.0688/0.6842/0.1034`;§4 L58 与 Task L37 引用一致 | **closed** |
| P2-5 | severe 层级标注 | `"layer": "block_coverage"` + definition 入每层 summary → 见 N6 | **closed(附 N6)** |
| P2-6 | CPU/GPU diff 精确化 | `K01 R5 raw 16↔15`、`K01 R17 raw 23↔22 + block 20↔19`;与两份 limit80 results 的 `n_det`(1306/1304、850/849)逐项自洽 | **closed** |
| P2-7 | torchvision 0.26.0+cu128 vs 生产 0.29.0 | `requirements.txt` L17–18 实测 `torch==2.14.0`/`torchvision==0.29.0` ✓ 披露准确 | **closed** |
| P2-8 | `noncommercial_research_source_restricted` 措辞统一 | `cases.json` 中 Cleaned Webtoon 10 case 原文即该串,§3 L40 引用一致 | **closed** |
| P2-9 | `hash-recomputation.txt` 含 cases.json + 10 info.json | 1 + 10 行齐,含 UTF-8 路径与字节数(→ 无法复算) | **closed** |

## P3

| 编号 | r2 声称 | 独立核对结果 | 判定 |
|---|---|---|---|
| P3-1 | UTC 时间戳 | `weights-manifest`/`env-gpu`/5×results 为 `+00:00` ISO ✓;但 `adapter-spot-check-cuda.json`、`consistency-and-sensitivity.json` **无时间戳**,`build_eval_manifest.py` L245 `generated_at` 为**硬编码裸日期** `"2026-09-29"` | **partially_closed**(N5) |
| P3-2 | weights-manifest schema@2 + `verified_by`/`command` | `m2-doctr-qual/weights-manifest@2`;`verified_by` + 完整 `command` | **closed** |
| P3-3 | 三处 pin 注释 | `eval_detection.py` L43–50 "Three references on purpose" + 三处锚点 | **closed** |
| P3-4 | IoU 措辞 | docstring L9–19、§4/§5 表 "Mean matched(coverage/IoU)" 分离;`min_mean_iou` 仅作键名继承 | **closed** |
| P3-5 | git 层证据 | `git-evidence.txt` 存在且证明 base..`4d9d8d0c` 范围 + production 零改动;但**只覆盖 r1 delivery**,不含 r2 范围;§8 落实清单未点名此项 | **partially_closed**(C1) |
| P3-6 | AC 勾选 owner 自评注记 | Task L32 显式注记 | **closed** |
| P3-7 | docstring 同步 | `eval_detection.py` 三层描述与实现一致;`smoke_adapter_check.py` "count + coordinates" 与实现一致 | **closed** |
| P3-8 | `union_params` | L249–256 结构化(阈值/ctd/uncleaned/merge_rule) | **closed** |

**判定分布:closed 20、partially_closed 2(P3-1、P3-5)、open 0。**

---

# r2 新引入缺陷

| 编号 | 级 | 位置 | 事实 |
|---|---|---|---|
| N1 | P2 | Task L60、Handoff L28/L59、`baseline-summary §5` vs `env-gpu-py312.json`/results | 正文"engine 4.2s / 首推 0.59s / 稳态 35–38ms" ↔ 证据 `0.54 / 0.38 / [33.4,34.6]ms`;§5 表 db_resnet50 `22.0 s` ↔ JSON `17.11 s`(fast_base `23.4` ↔ `23.31`)。r2 重跑后正文未同步 |
| N2 | P2 | Handoff L9、`baseline-summary §8`、`doc/STATUS.md` | r2 修订头 `3e86c800` **未在任何交付文档登记**(L9 仅写"本文件之后的文档/脚本提交");Handoff L8 明细为 r1 交付 8 个 verification 文件,而 L8 文字写"7 份证据" |
| N3 | P3 | `baseline-summary §5` L89 | 声称"不再输出恒零的 pure 计数",但 seg05 三份 JSON 仍含 `"pure": 0`(`attribution_available:false` 语义正确,措辞过强) |
| N4 | P3 | `smoke_adapter_check.py` L100–109 | 两路径块数均为 0 时 `coords_match=False → record_match=False`,"两边一致地无块"被误判为不一致(实测 6 region 未触发) |
| N5 | P3 | `adapter-spot-check-cuda.json`、`consistency-and-sensitivity.json`、`build_eval_manifest.py` L245 | 缺 UTC 时间戳;manifest `generated_at` 硬编码,重跑不更新 |
| N6 | P3 | `eval_detection.py` L355–361 | 同一个 primary-layer severe 值被复制进 `raw_strict`/`block_strict` summary 并统一标 `layer=block_coverage`,易被读成各层自有指标 |
| N7 | P3 | `doc/REBASELINE_PLAN.md` L75、Task front-matter L9 | Plan 写 `in_progress` ↔ Task/STATUS 为 `in_review`;`reviewer: DeepSeek Harness(待派发)` 未随派发更新 |

**未发现**数据/正确性/安全类核心缺陷:全部主指标经原始 JSON 重读复算与报告一致(seg05 `0.47764/0.12496/0.75307/0.03846`、block_strict `0.45147/0.11812/0.70341`、db `0.60851/0.18575/0.77508/0.01923`、limit80 gpu/cpu `0.06824/0.06832`、`raw 5350 / gt 917 / blocks 3505`);版权纪律成立(派生像素在 `task-envs`,**未被 Git 跟踪**);`__pycache__/*.pyc` 已被 `.gitignore` L1–2 覆盖,不入库。

---

# 结论

r2 对 r1 的修订**实质性完成**:24 项中 20 项完全闭合、2 项部分闭合(P3-1、P3-5)、0 项 open;所有 r1 事实层发现均已被修正,且我未发现任何影响 AC1–AC4 事实成立的反证 —— AC1–AC4 的事实层(权重一致性、隔离环境、评测基座三层口径、首跑基线与判定界限)**经独立复核确认成立**,AC4 的 FAIL 结论对匹配口径与 pad 处理的双重稳健性也成立(`[0.26, 0.48]`)。

残余问题全部位于**证据层与文档层**:核心实测数值已全部互相自洽,但 r2 重跑生成的机器可读证据与正文计时数值未同步(N1),r2 自身修订头与变更范围未登记、git 证据仍停留在 r1 范围(N2/P3-5),以及 4 项 P3 级文档/脚本措辞与逻辑瑕疵(N3–N6)。这些不构成重做,但**N1 与 N2 涉及"文档声称与证据一致"与"评审对象可固定",应在集成前闭合**。

**条件(集成前必须闭合,可执行)**

- **C1(阻塞,可由作者或集成方执行)**:在 `doc/handoffs/M2-DOCTR-QUAL-PREFLIGHT-baseline.md` 增补一行固定 r2 修订头 `3e86c800f4c9b28b246787ae470a364c90ae1e42`(单提交,parent `4d9d8d0c`);并在 `verification/M2-DOCTR-QUAL/git-evidence.txt` **追加** `## git diff --stat 4d9d8d0c..3e86c800` 段与 production 零改动证明。验收:`git diff --stat 4d9d8d0c..3e86c800` 输出与文档逐字一致;`git diff --stat 4d9d8d0c..3e86c800 -- requirements.txt requirements-dev.txt src` 为空;清单含上述 5 个新增文件。
- **C2(阻塞)**:统一计时口径。将 Task L60、Handoff L28/L59、`baseline-summary §5` 耗时列改为与机器可读证据一致(**GPU 冒烟 `engine_build 0.54s` / `first_inference 0.38s` / 稳态 `33.4–34.6ms` / 峰值 `522.6 MiB`;fast_base `23.31s`;db_resnet50 `17.11s`**),或显式标注两次测量与口径差异;**不得同时保留两组互相矛盾的数**。
- **C3**:修正 `baseline-summary §5` 措辞(改为"输出 `attribution_available:false`,不再据此计算归因计数"),或在 `eval_detection.py` 中当 `attribution_available=false` 时省略 `with_text_evidence`/`pure` 字段。
- **C4**:为 `adapter-spot-check-cuda.json` 与 `consistency-and-sensitivity.json` 补 `generated_at`(UTC ISO);将 `build_eval_manifest.py` L245 的硬编码 `"2026-09-29"` 改为 `datetime.now(timezone.utc).isoformat(timespec="seconds")`。
- **C5**:修 `smoke_adapter_check.py` 空块集语义:两侧块数同为 0 时 `coords_match`/`record_match` 应为 `true`(或显式记 `skipped`),并追加一句注释说明该边界。

**不阻塞的收口建议**:补 §8 落实清单对 P3-5 的点名;N6 仅在主层输出 severe 或标注"primary-layer statistic, repeated for reference";N7 同步 `REBASELINE_PLAN` 状态措辞与 Task `reviewer` 字段。另建议集成方用 `hashlib` 对 2 份权重 + `cases.json` + 10 `info.json` 做一次独立复算,关闭本 Reviewer 环境中不可复算的那一项。

**推荐下一步(基于当前仓库状态)**:Task 保持 `in_review`、`integration_commit: null`;由 **ZCode(作者)** 在 `3e86c800` 之后追加一个纯文档/脚本修订提交闭合 C1–C5(其中 C1 若走 git 证据,亦可由 **Codex(集成方)** 代行关闭),提交后本 Reviewer 做 r3 定点复核(C1–C5 逐项 + 复核 N1 数值一致性),再转 Codex 集成收口并置 `done`。无需在条件闭合前释放正式 qualification run。
