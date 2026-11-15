# blocked 分类证据（r1 复核后重做）

Task `AC-BLOCKED-CLASSIFY-1`（Owner：DSH）｜基线 `73da5ab40`｜本目录对应 commit 见卡面 `integration_commit`

## 1. 输入

`verify_final.py`（`AC_BASE=0b517259e`）核对：40 卡 / 260 AC / **182 verified / 72 blocked / 6 NA**。

> 注：该脚本 EXIT=1，是 8 张卡的**先存** EOL/numstat 检查项（`V11R-B-1…B-5`、`V11R-C-1`、`MICA-FIX-1`、
> `FEA-07` 在本 commit 中 diff 为空），不是本轮引入；计数部分（40/260/72）可信。

## 2. 分类结果（`classification-v2.md`，逐条人工判定 + 依据）

**r1 复核要求：`ARCHIVE` 只允许「AC 对象在当前架构不存在」；当前架构的 live gap 必须落到可操作类。**

| 分类 | 条数 | 能否由 Agent 闭合 |
|---|---:|---|
| `ARCHIVE` | 15 | 否 —— 对象已退役（Tauri/React/WebView2 冻结） |
| `WITHDRAWN` | 6 | 否 —— 方案撤回/已裁决（`GOV-PIN-LINEAGE-1` AC1–AC6） |
| `HUMAN` | 5 | 否 —— 需人眼/物理设备 |
| `RERUN` | 10 | **是** —— 当前架构复跑/复算 |
| `DOC` | 9 | **是** —— 补文档/证据/登记 |
| `IMPL` | 22 | **是** —— 写代码/测试 |
| `MECHANISM_NA` | 5 | 否 —— 要求本身不适用（待裁决改判 NA） |
| **合计** | **72** | **可闭 41 条（RERUN+DOC+IMPL）** |

## 3. 关键判定（相对 r1 前的修正）

r1 复核指出初版是「脚本关键词规则原样输出、未人工复核」，本版**逐条给依据**并修正了 6 组误分类：

| 条目 | 初版 | 本版 | 依据 |
|---|---|---|---|
| `V11R-D-1` AC8 | ARCHIVE | **IMPL** | 当前 `App.axaml:20` 仍 include 旧 `AppStyles.axaml`（固定 Transitions）→ **当前树 live gap**，非旧架构 |
| `V11R-C-1` AC1/AC6/AC7 | HUMAN | **MECHANISM_NA** | headless 库卡，无「关键屏」对象；同卡 AC2/3/5 已判 NA |
| `P20-MEM-OPT-1` AC2/AC3/AC4 | HUMAN + RERUN | **ARCHIVE** | 旧 Tauri/WebView2 卡（证据为 `m2rc1-desktop`/`msedgewebview2`），AD-002 已退役；卡内 `:93-95` 已记录用户 2026-10-18 裁决 |
| `TASK-056` AC⑤ | ARCHIVE | **RERUN** | 「缺当前全仓基线 + 5 次复跑」是当前可做工作，不是旧架构 |
| `V11R-C-RESEARCH-1` AC5 | OTHER（称无法验证） | **DOC** | 卡有 `delivery_head: ba59a6c0d`，`git show --stat` 可证 0 个生产文件 → 补核验记录即可 |
| `RUN-IPC-1` AC4 | RERUN | **IMPL** | 理由主体是「缺 typed 拒绝单测」= 缺测试 |
| `GOV-PIN-LINEAGE-1` | 5 条 OTHER + AC3 落 RERUN | **6 条全部 WITHDRAWN** | AC3 与其余 5 条同根因（r27 撤回/r28 停止改造），不应拆分 |

## 4. HUMAN 的 5 条与清单 5 项的对账

| 清单项 | 覆盖的 `blocked` | 说明 |
|---|---|---|
| H-01 | `MICA-FIX-1` AC1、AC3（2 条） | Mica 真机 A/B 截图 + Win10 环境限制 |
| H-02 | `FEA-07-AC5-NATIVE-1` AC-N1、AC-N3、AC-N4（3 条） | 剩余 DPI 组合 + 物理拔屏 + 恢复点还原 |
| H-03 | （无 `blocked`） | `FINAL-HANDOFF` 未关闭项 1：F11 全屏 |
| H-04 | （无 `blocked`） | `FINAL-HANDOFF` 未关闭项 2：GitHub 默认分支 + 发布工作流 |
| H-05 | （无 `blocked`） | `FINAL-HANDOFF` 未关闭项 3：质量基线判断 |

⇒ **5 条 human AC → H-01(2) + H-02(3)**；**3 个非 blocked 项 → H-03/H-04/H-05**；共 5 项。

## 5. 已移除项

原 H-04「P20 内存阈值裁决」**移除**：P20 是旧 Tauri/WebView2 卡且卡内已记录用户 2026-10-18 裁决
（AC2 无需实施），再让用户二选一属重复。该卡 3 条 `blocked` 已归 `ARCHIVE`。

## 6. 待 DSH 裁决（不需要人）

1. **`MECHANISM_NA` 5 条**是否改判 `not-applicable`：
   `V11R-C-2` AC6、`V11R-C-1` AC1/AC6/AC7、`TASK-056` AC⑥。
2. **`TASK-056` AC⑥ 的「STATUS 台账行」**：`doc/STATUS.md` 预算 3200 bytes / 45 lines 只列当前 Task；
   `doc/TASK_LEDGER.md` 按状态汇总（`done` 525 张不逐卡列名）。r1 复核补充：历史 commit
   （`1d41e00c2`/`cc4e976fd`）的 STATUS **曾包含** TASK-056 done 行，是后来压缩才没有 →
   更准确的处置是 `verified`（引历史 commit，§4.1 允许「含该文件的 commit」）或 `not-applicable`
   且理由改为「历史已满足、当前台账不再承载」。
3. **`FEA-07` 的 `EV-AC5-P05` ID 重复**（两个不同文件同 ID），建议后续清理。

## 7. 本轮边界

**未改任何 AC 注释的 kind**（AC4 通过，复核已确认）。可闭的 41 条改判需逐条验证证据定位符，
留待后续卡。

## 8. 证据清单

- `classification-v2.md`：72 条逐条明细（分类 + 依据 + 原理由全文）
- `classify_v2.py`：判定脚本（含 72 条显式判定表，漏判/多判会直接报错退出）
- `four-pieces.log`：check / pins / inventory 三件套实测输出
