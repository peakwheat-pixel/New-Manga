## Verdict
approved（可集成）

核定范围：仅核对下述 10 条 r1 发现是否闭合（逐文件+上游 raw JSON/源码比对），未重审全文、未重跑实验、未修改任何文件。

## 逐条闭合表

| 编号 | 结论 | 证据（文件+位置） |
|---|---|---|
| P1-1 | 闭合 | 报告 §3:128 判语已改为「BJ13=text（与 ko 域同型）；BJ14=bubble 主导＋text 并存（ref2 bubble 0.122 > panel 0.094 > text 0.086，ref3 bubble 0.399 > text 0.274 > panel 0.126）；panel 平凡覆盖 IoU 0.013–0.126 非独立根因」；`sfx-detect-diagnosis.json:416/429/442/469/482/495/389` 四值逐一核对一致；Task:54 与 Handoff:19 同步同口径 |
| P2-1 | 闭合 | 三处均为 3.5–5.4× 且给同公式：报告 §2.1:46、§2.4:79+91、§3(c):121（另 §0:15 同步）；=page_h/crop_h=1/0.282–1/0.185，与 `l3-reference-crops.json` 的 `effective_scale_vs_fullpage` 0.282/0.185 一致；Handoff:22、Task:54 亦同步 |
| P2-2 | 闭合 | 报告 §2.5:102 已改写为目标占模型输入高≈71%（=1/1.4，外扩 20% 上下各一）——与 ref 高/crop 高（如 BJ13 ref1 760/1064、BJ15 ref2 550/770）实测一致；「目标太小」明确不成立、「目标太大」替代假设明示未单独排除、声明不影响主根因；§3(c):124 与 §6 limitation 3:211 同步 |
| P2-3 | 闭合 | 报告 §2.4:86 BJ14 ref2 行已为「bubble 0.9151 + text 0.9046（并存）」；`l3-reference-crops.json`（BJ14 第 2 crop boxes_top[0]=bubble 0.9151、[1]=text 0.9046）一致 |
| P2-4 | 闭合 | 报告 §2.2:68 已注「≥20（探针上限 20，按 sfx 降序截断；最高 sfx 0.0001 为截断前首位，判定不受影响）」；`conf_scan_diag.py:175-176`（`hits.sort(key=sfx, reverse=True); return hits[:20]`）与 `l1-fullpage-conf-scan.json:8660-8672`（ref3 首位 sfx 0.0001）一致 |
| P3-1 | 闭合 | 报告 §2.3:75 已改「BJ13 0.0001–0.0002；BJ14 0.0000–0.0003；BJ15 0.0000」；`l2-tiles-resolution-probe.json`：BJ13 ref1/ref2 0.0002/0.0001、BJ14 0.0/0.0003/0.0001、BJ15 0.0/0.0 — 逐值一致（0.0003 确属 BJ14 ref2） |
| P3-2 | 闭合 | Task:50 已加基线口径注「任务基线=24a89d7d（frontmatter base_commit）；claim 时仓头=497621df；全部 diff 固定点=497621df（claim commit 303d7e14 的 parent）」 |
| P3-3 | 闭合 | Handoff:32-34 提交清单已补 `cc2109ac` 与 `d849c967`（并说明 tip 自引用限制）；Task frontmatter:8 `rework_head: d849c967`、:9 `reviewed_head` 口径（r1 @87a8bc34 / r2 @d849c967 待复核）已对齐；Handoff frontmatter:7 亦含 `rework_head` |
| P4-1 | 闭合 | 报告 §2.1:44 L1 行已注分档实现=「同一 conf≥0.01 全集 NMS 后按 conf 重筛」，等价性依赖 `_nms` 贪心降序；`detection_sfx.py:469-477` 实测为 `order = numpy.argsort(scores)[::-1]`（高 conf 先处理，低分候选不可能抑制高分候选），引证与论证成立 |
| P4-2 | 闭合 | 报告 §4 五方案 SfxPolicy 行全部含「manual 与 skip 同判 SKIP」：§4①:142、②:152、③:162、④:172、⑤:182；`src/application/translation/context/gate.py:32-42` 实测 `skip`/`manual` 同返 `SKIP_POLICY(sfx_skip)`，`translate` 才进入翻译流 |
| P4-3 | 闭合 | 报告 §2.2:67 已注「pre-NMS 候选（text 0.5195）与 NMS 后保留框（text 0.7436）不是同一候选对象，两侧数字不得互推」；raw 核对：ref1 候选表同时存在 text 0.5195（sfx 0.0855，`l1:5331-5332`）与 text 0.7436（sfx 0.0004，`l1:5409-5410`）两条不同记录，后者与 NMS 保留框（`l1:4405-4416`）对应 — 注记属实 |

## 新发现
- P4（信息性，不阻塞）：`doc/handoffs/...-87a8bc34.md:5` frontmatter `base_commit: 497621df` 与 `doc/tasks/...md:17` `base_commit: 24a89d7d` 字段值仍不同，二义消解仅存在于 Task:50 的正文口径注；仅读 Handoff frontmatter 的下游消费者仍可能复现 r1 P3-2 的二义。可选后续：在 Handoff frontmatter 旁加同一句口径注（或显式区分 `task_base` / `diff_base`）。
- Reviewer 环境限制（非交付缺陷）：本会话 `pwsh` 全部调用在沙箱初始化阶段失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`），因此 `cc2109ac`/`d849c967` 的 git 对象存在性与「返修仅触碰报告/Task/Handoff 三文件、`experiments/**`+`raw/**` 零改动」两项**未能用 git 命令独立复核**；已确认的替代证据为：raw JSON 内容与 r1 版本数值/字段完全自洽（未发现被改写的痕迹），且报告 §8/Handoff:38 的处置声明与三文件文本同步一致。此限制不影响上述 10 条闭合判定。

推荐下一步：本 r2 复核结论为 approved，可交 Codex（编排会话代行）做集成验证并把 `doc/tasks/M2-SFX-DETECT-DOMAIN-EXT-DIAG.md` 流转为 done；集成前建议顺手补上上述 P4 的 Handoff 基线口径注（一行文字，无实验/代码影响），随后按报告 §5 三个裁决问题移交用户裁决。
