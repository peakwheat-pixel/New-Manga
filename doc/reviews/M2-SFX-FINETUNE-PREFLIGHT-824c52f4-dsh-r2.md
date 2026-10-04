## Verdict
approved_with_conditions

（12 项 r1 条件全部闭合；唯一条件为**集成方一次性口径确认**，不需作者返修。另说明：本轮 pwsh 沙箱仍报 `SetNamedSecurityInfoW … grantWrite` 失败（连试两次），我依旧**无 shell**，故 `git show` / `git diff --check` / `py_compile` 均由静态阅读与仓库配置交叉推定。）

## 逐条闭合表

| 项 | 结论 | 证据 |
|---|---|---|
| P2-1 | **闭合** | `preflight-report.md:124` 表述保留「追加利用报告已发（vol03 48/60/159 页…`74fa71e9`＝履行登记 commit，message 经集成方 git show 验证；DSH r1 因沙箱无 git 误判为无关引用）」+ Handoff:82 处置对照同步；按指令以集成方覆核结论为准。 |
| P2-2 | **闭合** | 四处收敛：report §0:14、§1.3:42（freeze 配置面无按类冻结｜类级屏蔽越界｜共享 backbone/neck 漂移三层）、`doc/tasks/…:28` AC1、Handoff:18；原文快照 `raw/ultralytics_docs_cfg_freeze_snapshot.html:469` 逐字命中「Freezes the first N layers of the model, or specific layers by index or module name」；grep 无旧判语残留。 |
| P2-3 | **闭合** | 五端点 raw 齐备（主/revision_main/refs/tree_main_recursive/readme_snapshot）；`preflight-report.md:25` usedStorage 排除逻辑在案（41,227,478 B 逐字节＝tree 中 onnx size，revision 件与主 API 同 sha 同 usedStorage，refs 仅 `main`/`tags:[]`/`converts:[]`）；AC2 限定语在 `:65`（r2 所称「:60」为行号漂移，实质在场）。 |
| P3-2 | **闭合** | `preflight-report.md:97`「约 925 MiB/张（reserved 1940→7488 over b2→b8）」；实算 (7488−1940)/6=924.67 ✓，b12/b16 外推 11.2/14.9GB 与新斜率自洽；全文无「810」残留。 |
| P3-3 | **闭合** | `:88` 表头（reserved/allocated 两列「含 final val」、`s/iter (中位)`、「整段 train() 墙钟（含初始化+final val）」）+ `:94` 口径注；`raw/vram_probe_summary.json:6-11` 数值逐字一致；「含 final val」有 `raw/vram_probe_console.log:61/130/199` 的 `Validating …best.pt` 与 `:58` `Optimizer stripped` 佐证；吞吐＝batch/中位（36.5/57.3/67.0）自洽。 |
| P3-5 | **闭合** | `vram_probe.py:9-13` docstring 与 `:40` `BATCH_REPEAT={2:20,4:40,8:80}`、`:146-148` 墙钟注释，与实测（80/160/320 张→各 40 iter；deltas 排除首 iter；峰值覆盖 final val/权重落盘）一致。**限制**：本轮无 shell，未能独立重跑 `py_compile`，仅静态阅读（未见语法问题）。 |
| P3-6 | **闭合** | `preflight-report.md:60` §2 硬约束（`names` 顺序须逐字＝`SFX_CLASS_MAP` 0:bubble/1:panel/2:sfx/3:text）+ Handoff:19 同步登记。 |
| P3-7 | **闭合** | `:30` 三项排除理由（权重/优化器状态缺失、算子兼容风险、无原训练配置）在位。 |
| P3-8 | **闭合** | `:61`「采纳 A′ 的输入条件：T1b 承诺最小标注量（页数下限）与召回基线回归口径」在位。 |
| P3-9 | **闭合** | Handoff:67 精确版本（onnx 1.23.1/opset 18、onnxslim 0.1.97、onnxruntime 1.30.0）+ AutoUpdate 事件引用 `raw/export_smoke_console.log:7-19`（实测 :7 attempting／:16 `+onnxslim==0.1.97`／:22 `onnx 1.23.1 opset 18`／:23 slimming）与「slim 影响 sha256、重跑需同版本」口径。 |
| P4-3 | **闭合** | `:107` 明示进程内常量重指未写回 src/env/registry、进程结束即失效、生产 pin 仍为 `d87389af…`；与 `src/infrastructure/providers/detection_sfx.py:110-111` 及 tree `lfs.oid` 逐字一致。 |
| P4-5 | **闭合** | `:146` 注「raw 日志 mAP 数字为 coco8-seg 合成/重映射冒烟副产物，不构成精度证据」，与 §0/§5 无精度主张口径一致。 |

附：`raw/hf_readme_main_snapshot.md:22` 行尾空白**处理可接受**——经逐字确认该空格确为 HF 上游 README 原文（Markdown 硬换行），全 `verification/**/*.md` 中仅此一处；保真优先于 lint 洁癖，实质无缺陷。

## 新发现
- **P4（集成门口径，条件项；无需作者返修）**：r2 声称的「`git diff --check` EXIT=0」只在**工作区/未跟踪口径**下成立。静态核验：仓库根 `.gitattributes`（仅 5 行 M2-RC2 条目）对该 raw 路径**无 `whitespace` 豁免**，`.git/config` 未覆盖 `core.whitespace`（默认 `blank-at-eol` 生效），且该文件在此交付中属新增。因此若集成方对 `git diff --check <base>..<head>` 执行 range 口径，预计恰好报 1 处 trailing whitespace 而非 EXIT=0（本轮无 shell，未能实测）。**建议条件**：集成验证沿用 AC6 的 pre-commit/工作区口径，或在 `.gitattributes` 增 `verification/M2-SFX-FINETUNE-PREFLIGHT/raw/** -whitespace`（该文件不在作者允许修改范围内，属集成方动作）。
- **P4（raw 字段命名，仅提示，不阻断）**：`vram_probe` 输出字段 `it_s` 实为 **iter/s**（18.25/14.32/8.38），报告吞吐列按 batch/中位算得 img/s（36.5/57.3/67.0）正确；下游引用 raw 时勿把 `it_s` 读作 img/s。既有 raw 已提交，无需返修。
