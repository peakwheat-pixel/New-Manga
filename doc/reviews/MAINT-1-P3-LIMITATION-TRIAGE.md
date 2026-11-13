# P3 · 9 个 `closed_with_limitations` 节点限制分类与处置建议（MAINT-1，2026-11-14）

分类口径沿用 `doc/plan/RESIDUAL-CLOSEOUT-PLAN-2026-11-08.md:9-21`：
**C1** 工程可闭环（补实现/补测试可 MET）｜**C2** 契约对齐（已冻结契约要求未遵守，或需 additive/UNFREEZE）｜
**C3** 设计选择/范围外（有意不做）｜**C4** 硬件/真机/外部条件（只能 waiver + 保留 NOT_RUN）。

本记录只做分类与建议，**不翻转状态、不改历史字节**。需"人该裁"的项进入 §4 双签队列。

## 1. 分类总表

| 节点 | 限制条目 | 类 | 建议处置 |
|---|---|---|---|
| **FEA-15-ACCEPT-1** | pytest 16F（既有） | C1 | 逐条归因或永久登记；不得当绿 |
| 同上 | .NET 127F「根因未定」 | **已解** | 本循环 P1 归因为环境（93 ACL + 31 路径 + 3 删除），真实仓库 1875/0/109 |
| 同上 | 可见 UI NOT_RUN | **已补** | 本循环 P2 四页冒烟 PASS（首屏层） |
| 同上 | 安装 / 真实库升级回退 NOT_RUN | C1（安装）/ C4（真实用户库） | 安装可隔离演练；真实库只能 waiver |
| 同上 | 30 条 pin 中 27 条跨 checkout 不可复现 | C1 | pin 口径治理（哈希基准归一化） |
| **FEA-14-AI-1** | ① P24 只回 `template_id`；② 引用写入方后续卡；⑥ 死方法/旧注释 | C1 | 合并为 AI-2 实现卡 |
| 同上 | ③ `UPDATE OR REPLACE` 覆盖同 `(kind,owner_id)` label（F-03）；④ name 唯一/规范化（F-05，待 ADJ） | C2 | 需 errata 或 ADJ 裁决 |
| 同上 | ⑤ DDL「version 不可变」裁决 | C3 | 已裁（调用方不可指定、Core 单调 +1），转 OUT |
| 同上 | ⑦ 真实 IPC / 活 Core 端到端 / 模板 UI / 真实 AI 网络 / 并发大库 | C4 | 真机/费用类，waiver |
| **FEA-14-EDIT-1** | ① `issue_markers` 无外键、删书不清理孤儿行（F-05） | C2/C3 | 与 `reading_bookmarks` 先例一致 → 转 OUT + 清理卡 |
| 同上 | ② `position` 形状 `{x,y}` 属未定义处实现裁决 | C3 | 若提升为跨卡契约需 PREQ errata |
| 同上 | ③ 批量 resolve/delete、分页/跨书过滤、`kind` 预置 | C3 | 属于 EDIT-2/EDIT-3 范围，登记为后续 |
| 同上 | ④ 真实 Host↔Core IPC 映射 / EDIT UI / 管线联动 / 万级性能 | C4 | waiver |
| **FEA-14-FONT-1** | FONT-2 范围（渲染消费、设置页字体 UI、元数据解析、内置字体授权） | C3 | 拆分卡，不随包字体 |
| 同上 | wire 级 `FONT_DELETE_FAILED` 负例未补；大文件/并发/占用未压测 | C1 | 补测试 + 压测 |
| 同上 | 日志 HEAD 为生成时工作树 | C1 | 证据口径治理 |
| **FEA-14-LIB-1** | ① `ChapterSummary` 不投影 `kind`；② `custom_rank` write-only；④ 64 位边界校验缺失 | C1 | LIB-2 实现卡 |
| 同上 | ③ R-11 三项 deferral（kind 语义体积、`number_value`、`normalized_title` 唯一索引） | C2 | 需 additive/UNFREEZE 或 ADJ |
| 同上 | ⑤ 真实联调 / LIB UI / Volume 实体 / 万级性能 | C4 | waiver |
| **FEA-14-READ-1** | Fluent Reader UI 未接线（偏好/书签面板/整书进度/reset 确认） | C1 | 已立 READ-2，但 READ-2 仍留可见控件 |
| 同上 | P12/P15 返回类型与 `confirm_token` 偏差 | C2 | 按 PREQ §8 对齐或登记 errata |
| 同上 | 真实手势 / IME / 多屏 / DPI / 主题 / 托盘 / 进程重启 | C4 | waiver |
| **FEA-14-READ-2** | 书签面板 / 整书进度 / reset 确认的**可见控件**未接线（VM+测试已覆盖） | C1 | 一张 UI 控件卡即可闭环 |
| **FEA-15-A3-1** | `logs/window-material.log` 在**只给 `--data-root`、不给 `--log-dir`** 时回落真实 `%APPDATA%\com.newmanga.desktop\logs`（A3-1 实测追加 166 B） | **C3/C1 边界**（**已核对源码，非硬编码缺陷**） | 源码 `MainWindow.axaml.cs:1041-1047` `ResolveDiagnosticsRoot` 明确：显式 `--log-dir` 拥有全部日志；无 `--log-dir` 时保留历史每用户位置（注释写"发行默认行为不变"）。改进方向＝`--data-root` 也隐含日志根，属**行为变更/产品取舍** → 进 §4 **Q5** 双签，不在本循环单裁 |
| 同上 | 真实手势 / IME / 多屏 / DPI / 主题 / 托盘 | C4 | waiver |
| **FEA-15-PIN-BASIS-ENFORCE-1** | `FEA-06-PREREQ-1` TaskPath FAIL（13 errors / EXIT 1）；`CHAPTER-SELECTOR-1` TaskPath FAIL（6 errors / EXIT 1） | **C1** | 修卡面使其通过门禁 |
| 同上 | full suite 历史 `61 passed / 2 skipped / 3 failed / EXIT 1` | C1 | 归因或登记 |
| 同上 | Linux `NOT_RUN`；P2-1/P2-2/P3-B/P3-D 原分类 | C4 | waiver |

## 2. 按类汇总

| 类 | 条目数（约） | 处置路径 |
|---|---:|---|
| **C1 工程可闭环** | 13 | 拆实现卡（Codex 主体 / ZCode UI），补测试与压测，可翻 `done` |
| **C2 契约对齐** | 5 | 需 errata / additive / UNFREEZE 或 ADJ；DSH 裁 |
| **C3 设计选择** | 7 | 转 `OUT` + waiver 记录（含 A3-1 日志根，待 Q5） |
| **C4 硬件/真机/外部** | 10 | 只能 waiver，保留 `NOT_RUN` |
| **已解（本循环）** | 2 | .NET 127F 归因（P1）、可见 UI 首屏（P2） |

## 3. 价值排序（下一批实现卡候选）

1. ~~A3-1 日志路径跟随数据根~~ → **降级**：源码显示为有意的发行默认（见 §1 与 Q5），不作为 C1 实现卡；是否改进由 Q5 双签裁决。
2. **PIN-BASIS-ENFORCE-1 的两处 TaskPath FAIL**（C1，纯治理，直接关系 DoD §4）。
3. **READ-2 可见控件接线**（C1，用户可见的阅读器控件）。
4. **LIB-2 / AI-2 / FONT 补测 / EDIT 清理**（C1 批量，可合卡节流）。

## 4. 需"人该裁"的双签队列（Codex + ZCode 各出一份书面建议，DSH 终裁）

| # | 议题 | 为何不是 DSH 单裁 |
|---|---|---|
| Q1 | AI-1 ④ name 唯一/规范化范围（F-05 待 ADJ） | 涉及产品语义（是否区分大小写/空白） |
| Q2 | EDIT-1 ② `position` 形状是否提升为跨卡契约 | 涉及契约演进与后续 UI 兼容 |
| Q3 | FONT-1 FONT-2 范围是否拆卡、内置字体授权如何登记 | 涉及许可证边界（GPL/字体随包禁止） |
| Q4 | READ-1 P12/P15 偏差：对齐 PREQ §8 还是登记 errata | 涉及契约字节是否改动 |
| Q5 | A3-1 日志路径：修实现 or 接受现状 | 涉及用户目录写入的取舍 |
| Q6 | pytest 16F：修复 or 永久登记为既有限制 | 涉及"完成"口径底线 |

> 双签产出格式：两份独立书面建议（各附证据与复现命令），结论若冲突，DSH 取更保守一方并把另一方理由登记为残留风险。

## 5. 与 DoD-Line 的关系

本分类不改变任何节点状态。DoD §3（"所有 limitation 逐条处置"）的达成判定，将依据本表逐项：
C1 项需实现 + 证据 + 独立 Review；C2/C3 项需裁决记录；C4 项需 waiver 且保留 `NOT_RUN` 证据。
