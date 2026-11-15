# blocked 分类证据

Task `AC-BLOCKED-CLASSIFY-1`（Owner：DSH）｜基线 `73da5ab40`

## 1. 输入

`verify_final.py`（`AC_BASE=0b517259e`）核对：40 卡 / 260 AC / **182 verified / 72 blocked / 6 NA**。

## 2. 分类结果（脚本 `classify.py` 自动归类 + 人工复核）

| 分类 | 条数 | 可否由 Agent 闭合 | 依据 |
|---|---:|---|---|
| ARCHIVE | 15 | **否** | 旧架构（Tauri/React/WebView2）已由 AD-002 退役，AC 对象不存在；登记历史存档 |
| HUMAN | 7 | **否（需人）** | 真机/人眼/物理多屏/产品阈值裁决；见 `doc/reviews/HUMAN-REQUIRED-2026-11-15.md` |
| RERUN | 14 | **部分可** | 需复跑旧套件/旧 E2E；其中旧架构相关不可闭，当前架构的可另立 Task |
| DOC | 2 | **可** | 缺 Handoff / 缺截图（截图属人眼，Handoff 可补） |
| IMPL | 2 | **可** | 缺测试断言（`V11R-B-4` Partial 状态断言、`V11R-A-3` 契约测试） |
| OTHER | 32 | **混合** | 含旧架构未实施（`GOV-PIN-LINEAGE-1` 5 条）、真实实现缺口、机制性过时要求 |

明细表见 `classification.md`（72 行，逐条含卡、AC、分类与理由）。

## 3. 关键判定（不笼统）

1. **只有 6 条真正属于「人眼/物理/账号」**（`MICA-FIX-1` AC1/AC3、`FEA-07` AC-N1/N3/N4、
   `P20-MEM-OPT-1` 阈值），其余 `blocked` 都**不是等人的事**。
2. **`TASK-056` 的 AC⑥「STATUS 台账行」是机制性过时要求**：`doc/STATUS.md` 预算 3200 bytes
   只列当前 Task；`doc/TASK_LEDGER.md` 按状态汇总（`done` 525 张不逐卡列名）。
   两个台账都不提供「逐卡 STATUS 行」，该要求已不适用 → 建议判 `not-applicable`（需裁决）。
3. **`FEA-04` 的 8 条 `blocked`**（AC1–AC8）是「范围冻结完成、实现未开始」，属真实缺口，
   不是可归因闭合项。
4. **`GOV-PIN-LINEAGE-1` 的 5 条**属方案撤回后的历史状态（卡已 `closed_with_limitations`），
   不应改判 `verified`。

## 4. HUMAN-REQUIRED 清单

见 `doc/reviews/HUMAN-REQUIRED-2026-11-15.md`：5 项（H-01…H-05），
含「为什么必须人做」「最小操作步骤」「预估耗时」，累计约 10 分钟（H-03 另需 20 分钟）。

## 5. 本轮边界

**未改任何 AC 注释的 kind**（AC4）。可闭项的改判（如 `TASK-056`、`V11R-B-4`）需逐条验证
证据定位符后再做，留待后续卡。
