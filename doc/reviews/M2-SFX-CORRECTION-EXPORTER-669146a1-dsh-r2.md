审查工具限制先说明：本会话 `pwsh` 在沙箱授权阶段即失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`），我**无法执行 pytest / git**，也无法读取 r1 历史的 commit 对象。因此以下全部为静态核对（逐文件读源码+算术复算），凡涉及"必须跑才知道"的点我都标注了。

## Verdict
approved_with_conditions

r1 的 P1-1（必修）与 P2-1、P3-1..P3-5 全部闭合，未发现未闭合项；条件均为文档/导出元数据级（P4），不含逻辑与测试改动，无需再开一整轮 review。

## 逐条闭合表

| 条目 | 状态 | 证据 |
|---|---|---|
| P1-1 bbox 语义 | 闭合 | `samples.py:103-108` 已改用 T1a `importers.bbox_to_polygon(x,y,w,h)`（`importers.py:54-55` 确为 xywh），`w<=0 or h<=0` raise fail-closed；`fixture.py:93-104` geom 改 xywh 且 `205-214` 全部矩形页内（我复算 rgA/G/B/C1/H/I/I2/N/O2 四角均 ≤64×48）；`test_samples.py:140` 期望 `[[6,8],[46,8],[46,36],[6,36]]`，与 bbox=[6,8,40,28] 的 x+w/y+h 推导一致；`fixture.py:419` reg-dup 已同步为 rgA 新四角 (10,10)-(50,38)，与 `test_samples.py:102` 一致。判别力静态复算成立：旧 xyxy 读法得 [[6,8],[40,8],[40,28],[6,28]] ≠ 新期望（旧代码必红）。新增 `test_samples.py:145-163` rgO 纯函数用例（三点/空两形态+非正宽 fail-closed），不进 fixture 矩阵，不影响冒烟计数。 |
| P2-1 YOLO scope | 闭合 | `export.py:46-47` `YOLO_SCOPES/YOLO_SCOPE_DEFAULT="main"`、`178` `run_export(yolo_scope=)`、`182-183` 非法值 raise、`260-263` `main if scope=="main" else kept`、`308` `export.yolo_scope` 入 summary；`cli.py:38-42` `choices=("main","all")` 默认 main；`test_export.py:83-97` all 用例（yolo_labels=6、train5+challenge1）；`README.md:27-33` 已登记节。 |
| P3-1 存活判据 (a) | 闭合 | `eligibility.py:34-38` `SURVIVAL_UNDONE_RULE` 明写"保守误杀，非 §5.4 唯一读法"；`fixture.py:321-330` rgO2 链 = m(speech)→u(sfx)→restored(speech,r1)→restored(sfx,r2)；`test_scanner.py:156-168` 钉住 `undone=True, superseded=False, survives=False`，与 `scanner.py:157-161` 实现一致（我按链复算一致）；`scanner.py` docstring 19-20 同步。 |
| P3-2 几何门读法登记 | 闭合（附带 P4-a 文案缺陷） | `eligibility.py:23-29` 明写"restore 至已改标 revision 读作用户背书该 revision 几何"及现实现不触发 complete；`test_samples.py:63-78` 合成链钉住现读法 `("partial","machine_only")`；`README.md:65` 表行同步。**但**条文中把该用例称作 "rgO3"，而实际用例是 `test_geometry_gate_restore_endorsement_readout_pinned`（region 写作 "rgX"），全仓无 rgO3——见新发现 P4-a。 |
| P3-3 partial 理由 | 闭合 | `README.md:72-76` 给出 partial 判据构成（类型人工确认 origin=user + 几何机器产出）与"不落 pseudo"分界理由（pseudo=连类型都无人工背书）。 |
| P3-4 计数/红态 EXIT | 闭合 | 报告 `§3:33-43` 记录 r1 误记 12/5/8/10/6=41 与 r1 实际 16/5/9/10/6=46，返修后 17/7/9/11/6=50；`red-run.txt:61` 尾行 `pytest EXIT=2`，报告与 Handoff `90-93` 均对齐 EXIT=2；Task `50-53`、Handoff `38-45` 分项同步。我静态点数 5 个测试文件用例数 = 17/7/9/11/6 = 50，与 `green-run.txt:3` 的 50 passed 自洽（r1 时点 46 因无 VCS 无法复算，仅文档自洽）。 |
| P3-5 Task 状态/AC 注记 | 闭合 | `doc/tasks/M2-SFX-CORRECTION-EXPORTER.md:5` `status: in_review`；`26-29` AC 节注记"Owner 自评…待 Reviewer 确认…r1=changes_requested"。 |

P4 择要（按 claim 抽验）：P4-3 已登记于报告 `§5:78-80` 且 `README.md:95-96`；P4-5 已实现 `samples.py:168` + `test_samples.py:119` + `README.md:88-89`；P4-4 见上闭合；P4-2/6/7/8/9/10 在 Handoff `102-103` 与报告 `128` 逐号登记为"登记不修"（原文未随返修提供，其实质无法逐条复核，按约定以报告为准）。

## 新发现

- **P4-a（幽灵标识符，建议修）**：`CONSTANTS["GEOMETRY_CONFIRM_RULE"]`（`eligibility.py:27`）与 `README.md:100` 把 P3-2 判别用例写作 "rgO3"，但不存在该 fixture region 或该名用例（实际为 `test_samples.py:63` 的 `test_geometry_gate_restore_endorsement_readout_pinned`，链上 region_id="rgX"）。该常量字符串会被写进每份 export summary（`fixture-smoke-summary.json:20`、`real-db-smoke-summary.json:20`、`selfcheck.txt:7`、`green-run.txt:1`），即 P3-2 要求登记的落地证据指向一个不存在的锚点，削弱可追溯性。修法：改为实际用例名并重生成四处证据文案（纯文案，零逻辑改动）。
- **P4-b（导出元数据与 scope 不一致，建议登记或对齐）**：`export.py:264` `splits_present = sorted({s.split for s in kept})` 取的是全部 kept 样本，而 YOLO 树按 `yolo_scope` 裁剪（`260`）。默认 `main` 下 `dataset.yaml` 仍声明 `challenge: images/challenge` / `val` 等空 split（`test_export.py:112` 明确断言 `images/challenge` 为 0 个文件），即 yaml 声明的 split 集合与实际落盘树不一致；`scope=all` 时一致。当前测试不校验 `dataset.yaml` 的 split 键，故不红。建议 `splits_present` 改由 `yolo_samples` 推导（或在 README/摘要显式登记该差异）。
- **P4-c（红态证据性质，仅记录）**：`evidence/red-run.txt` 是 5 个测试文件 `ModuleNotFoundError` 的 collection error（断言级红态从未记录），报告 `§8:141` 已如实说明其为历史记录且不可复现。判别力实际由 rgN/rgO/rgO2 用例承担，我用算术复算确认；若要更稳，后续可补一条断言级红态（先写期望→跑红）记录。不阻塞。
- 其余无（无 P0/P1/P2/P3 级新发现）。

（再次声明：因沙箱禁止执行命令，P1-1"旧代码必红"与 50 passed 均为静态复算/文档互证，未经本机实测。）
