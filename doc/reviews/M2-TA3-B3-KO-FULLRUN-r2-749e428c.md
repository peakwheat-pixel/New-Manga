# M2-TA3-B3-KO-FULLRUN r2 快速复核报告（DSH，2026-10-03）

verdict: approved

r2 指令范围 6 项全部闭合，返修 diff 面干净无越面。残留问题仅 1 处 P4 文字级数字（r1 未点名位置）+ 2 处 §1.2b 文字级自引用瑕疵，均不阻塞集成。

## 逐项核对结果

| # | 项 | 结论 | 证据 |
|---|---|---|---|
| 1 | **F1 闭合（ledger note）** | **✓ 闭合** | budget-ledger.json 现含 invalidated_entries_note（keys 复验通过）；与 cd76cac0 版逐字节对比：旧 note 527 字符为当前 note 的 verbatim 前缀（startswith==True），新增 366 字符后缀以 ` PROVENANCE (DSH r1 F1): this ` 开始，尾注完整登记覆盖机制（driver 启动单次 ledger_load() + 逐 phase 全量重写）与 F5 假 K09 条目清除；entries 仍 9 条、est_tokens 加总复算 = 950,954 ✓、requests = 1,568 ✓ |
| 2 | **F2 闭合（五处数字）** | **✓ 闭合（附 1 处范围外残留 R2-1）** | §2 合计行：detect 1,114 ✓、OCR 非空 1,074/1,114（96.4%）✓、翻译非空 1,073 ✓，并附 r1 F2 修正注；§4.2：40 个空 OCR + 逐 case 分布与 r1 复算完全一致 ✓；§1.1：0/879 ✓；§8：854 est token/region（950,954/1,114）✓。逐 case 表格行值未触碰：diff 仅一个 hunk 变更合计行 ✓。旧值全文扫描：1,248 / 96.2% / 958 / 1,115 / 853 全部清零 ✓ |
| 3 | **F3 措辞** | **✓ 闭合** | §1.1 第一现场改为「run1.steps 中 OCR step 全部为 failed/PROVIDER_DEPENDENCY_MISSING（run2 per-region OCR steps 同码 879/879——DSH r1 R-B 逐份扫描证实；F3 措辞修正：部分 case 的 steps 首条为 detect/completed，非 OCR）」✓；§1.1 处置 bullet 同步补 F1 覆盖机制说明 ✓ |
| 4 | **新增 §1.2b** | **✓ 成立** | F4/F5/F6/F8/F9 五项齐全，开头声明「不改写 git 历史，以正文为准」；F7 未入正文（留给集成者，符合指令）✓；与正文无事实冲突 ✓ |
| 5 | **DSH 报告原字节 import** | **✓ 一致** | doc/reviews/M2-TA3-B3-KO-FULLRUN-r1-0ca8c740.md sha256 = 99c52eaf51ceedc538b690467b26c60cc0ead5e4e7b8f05edea4177ce37eb0b4 ✓；内容抽查确认为 r1 原文（verdict/9 findings 齐全）✓ |
| 6 | **返修 diff 面** | **✓ 无越面** | git diff --name-status 3a046657..749e428c 恰好 3 个文件：A doc/reviews/…r1…md + M ko-fullrun-report.md + M budget-ledger.json——全部在允许修改面内 ✓；新 HEAD = 749e428ca7490af8d91805e1760b812ad9a90b30 ✓ |

## 残留问题（均不阻塞集成，集成方顺手处理）

- **R2-1 [P4]** ko-fullrun-report.md:99（§4.2 第二条 bullet）「翻译非空 1,069/1,070」旧聚合值残留——应为 1,073/1,074。
- **R2-2 [P4]** §1.2b 称假 K09「本报告 §1.2 已述」——实为 §1.2b 首次登记，自引用文字不准（事实正确）。
- **R2-3 [P4]** §1.2b「UTC 应为 04:22-04:29」与正文 §1.1「04:17–04:29」5 分钟起点差——两种口径并存易困惑，文字级。

## 推荐下一步

以 749e428c 为交付头走标准门禁（三套件 pytest，预期 611+1skipped 0 failed），集成时顺手处理 R2-1/R2-2/R2-3，随后完成 merge 与 post-merge STATUS/PLAN 收口。
