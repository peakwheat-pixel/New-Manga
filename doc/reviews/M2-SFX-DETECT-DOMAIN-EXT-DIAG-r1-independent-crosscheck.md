# M2-SFX-DETECT-DOMAIN-EXT-DIAG — DSH r1 独立交叉复核报告（编排会话派发，2026-10-03）

verdict: approved_with_conditions（条件=本报告 P1-1 登记冲突裁决；交付实质经独立复算全部成立）

> **P1-1 编排裁决（2026-10-03，集成前）**：本 Task 存在两条 r1 review 链——(a) 本报告（编排会话在配额恢复后派发的独立 DSH 静态复核，初读时 worktree tip=cc2109ac）；(b) 分支内置 r1 rework 链（d849c967+3952a00f，verdict=changes_requested 1×P1+4×P2+3×P3+3×P4→11 条返修闭合）。两链的发现高度重合、互为印证（本报告对 rework 的数字声明逐项抽查属实：3.5–5.4×、BJ14 bubble IoU 0.122/0.399、~71% 等）。会话身份不可从 git 区分（author 统一 peakwheat-pixel），如实登记为不可判定。**裁决：两链并存登记、采信含返修 tip=3952a00f 为 reviewed_head、本报告条件（P1-1 裁决）就此闭合**。返修内容已经两条链交叉验证，质量风险可控。

## R-A..R-F 逐项结论（全部 PASS）

- **R-A AC1 根因分层 PASS**：假设(a) 域外=成立——L3 七框 best_sfx 0.0000–0.0109（7/7 count=0）vs BJ06 @0.5 档 0.721–0.9355，跨 2–3 个数量级（raw/l3-reference-crops.json + l1-fullpage-conf-scan.json 逐字段人工复算吻合）；假设(b) 症状层成立/机制层否定成立（pre-NMS ref1=16 候选 top sfx 0.0855 vs 同候选 text 0.5195，「竞争没有发生」）；假设(c) 不成立（L2 参照框 7/7 sfx_box=False；letterbox 等比缩放无各向异性机理，detection_sfx.py L393-409）。不可判定项（imgsz 残余、§6 limitations 7 项）如实标记。P3-1（87a8bc34 版「2.4–3.4×」应为 3.5–5.4×，逐框复算 3.92/3.55/4.59/4.50/4.65/4.95/5.41）已被 d849c967 修正，复算确认正确。
- **R-B AC2 五方案 PASS**：五方案×五要素逐格齐备；DETECT-EVAL §4.4 七项前置条件与 C4 §7.1 条件式先例引用核实；只评估不实施守住（无实施动作、无越权 Gate）。
- **R-C AC3 PASS**：排序 ⑤＞③（条件式）＞①（条件性次优）＞④（不推荐独立立项）＞②（否决）；「不实施」选项明示；三个裁决问题显式移交（用户×2、Codex×1），无代裁。
- **R-D AC4 零 src PASS**：真实增量 497621df..cc2109ac=8 文件全在允许面；分支带入的 SFX-E2E 集成历史文件与 main 22 文件三方逐对象 SAME（预核 4 个+扩展抽查 18 个）；磁盘与旧 worktree 的 2 文件差异系该 worktree HEAD 停在 ca107e1d 未更新，非篡改。
- **R-E 结构性发现 PASS**：三处独立证据（detection_sfx.py:599-601 直接拼接无重叠检查；handlers.py:286-298 逐候选建 region 无仲裁；core_assembly.py:1013-1049 按 sfx- 前缀分发+SfxPolicy 只挂 SFX region）——「recall 恢复不闭合误路由损害」推论成立。
- **R-F 诊断脚本 PASS**：只读 import、L1 分档等价性经 NMS 贪心逻辑验证、raw 4 JSON 落盘。

## Findings

- P1-1（流程）：见顶部裁决块（两链并存登记，本条件闭合）。
- P3-1：L3 等效倍数文档缺陷——已被 d849c967 修正，无需动作。
- P4-1：base 口径双轨（Task 24a89d7d vs Handoff 497621df）——rework P3-2 已加注记。
- P4-2：任务书 R-D 字面口径在该分支拓扑下不可满足——后续 Task 书以 claim 前提作 diff anchor。
- P4-3：L1 分档 conf 严格相等候选的理论次序不确定性——数量级判定零影响，登记为已知边界。

## NOT_VERIFIED

1. conf_scan_diag.py 未实际重跑（静态审读+raw 人工复算代替）。
2. weights sha256 pin 实测匹配（运行时校验）。
3. 页面图像 sha256 四值未逐一复算。
4. BJ06 人工抽检与 DETECT-EVAL §3.3 引用链未逐条回溯。
5. 并行 r1 的会话身份（git 不可区分）。

## 推荐下一步

以 tip 3952a00f 流转集成（merge --no-ff + post-merge 三套件 + STATUS/PLAN 收口）；报告 §5 三个裁决问题（用户×2：不实施+UI 缓解、AGPL 衍生许可；Codex×1：重叠仲裁契约授权）随集成移交。
