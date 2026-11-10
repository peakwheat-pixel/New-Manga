# FEA-15 集成验收计划（准备版）

- 编制：DSH（Lead / Integrator）
- 日期：2026-11-09；依据：FEA-00 §S5（`:654`）、FEA-13/15 前置证据
- 状态：**准备版**（FEA-14 六切片未全部完成前不构成正式验收）

## 1. 验收范围（方案 §S5）

| # | 验收项 | 判别 | 当前状态 |
|---|---|---|---|
| A1 | 隔离干净构建 | 全新 worktree / 无 bin,obj 下 Release 构建 0 错误 0 警告 | 已执行：`d63d735a7` 干净 worktree，0 警告/0 错误，EXIT 0；见 `verification/FEA-15-ACCEPT-1/build.log`。 |
| A2 | 安装 | 真实安装包安装 + 启动 + 四页面可达 | 当前 HEAD 安装及四页 **NOT_RUN**：缺当前版本安装交付物；历史 setup 仅作旧版本参考，不代表当前产品字节。 |
| A3 | 双 UI 回归 | legacy `MainWindow.Show()` 与 Fluent shell 两套入口冒烟 + 关键路径测试 | 部分：A3-1 为较早版本的真实进程证据；当前 HEAD 真实会话尚未实测。App.Tests 本次 884/4/11，4 项仓库定位失败。 |
| A4 | 升级与回退报告 | 旧库升级（FEA-13 迁移/备份/恢复证据）+ 回退（pre_restore）可执行 | 部分：A4-1 合成库 v8→v9 + pre_restore 演练；当前 v14 真实用户库升级及回退 **NOT_RUN**。内存 v7→v14 查询探针仅是有限补充。 |
| A5 | 全量测试基线 | pytest + .NET 全绿 | 不满足：当前复跑 pytest 3515/16/12、EXIT 1；.NET 8 项目中 2 项失败、EXIT 1；原因和适用范围待复核。 |
| A6 | 契约与 pin | 18 pins 全绿、无 UNFREEZE 未决 | pins 18/18 PASS；无未决 UNFREEZE 的人工核对待完成。 |
| A7 | FEA-14 领域能力 | 七切片按各自冻结 Task 验收 | 已汇总各卡历史状态与限制，见 §6；不等同于当前 HEAD 的独立验收通过。 |
| A8 | 已知 limitation 登记 | 逐项列明并指向后续卡 | ◐ 「源授权元数据未入包」→ `FEA-13-SRC-6`（ZCode 裁决 2026-11-09：同机恢复有效、跨机须重授权） |

## 2. 本次可验收子集（不依赖 FEA-14）

A1（干净构建）、A5（全量基线）、A6（契约/pin）已具备证据；A3/A4 具备「测试层」证据，真实 UI/安装层留待正式验收。

## 3. 待冻结的 FEA-14 切片（DSH 拟定的优先顺序）

| 顺序 | 切片 | 理由 | 主要风险 |
|---|---|---|---|
| 1 | `FEA-14-SET`（Host 能力：托盘/退出协调/启动页/语言/通知/更新/诊断预览） | 不涉 DDL/契约字节；可与 ZCode UI 分 Task | 托盘/语言需产品取舍（交 ZCode/用户裁决） |
| 2 | `FEA-14-FONT`（漫画字体库） | 独立资产库；但需存储位置与 DDL/元数据决定 | 字体许可、库位置 |
| 3 | `FEA-14-LIB`（ContentItem 兼容 DTO） | 数据模型改动 | 需 C-01b/C-15 兼容性裁决 |
| 4 | `FEA-14-READ`（阅读器） | UI 为主 | ZCode 主导 |
| 5 | `FEA-14-EDIT` / `FEA-14-AI` | 大切片、依赖 provider/编辑栈 | 产品取舍与安全 |

> **口径注记（2026-11-10，`ADJ-2026-11-10-FEA14-S5-SCOPE`）**：本表按 FEA-00 §12.2/§15.6 为**七切片**（原文含 `EXPORT`，本表现有行漏列）；`FEA-14-SET-1`（`done`，`c543b51cc`）交付的是 SET 的**视觉子集**（设置页字体只读投影），真实 SET 能力另立 `FEA-14-SET-2`；`EXPORT` 纳入 S5。历史原句字节保留；优先序与共用 wire 原则见该裁决 §2.2/§2.3。

## 4. 正式验收前置（清单）

1. FEA-14 六切片按各自 Task 完成并 done（或明确 out_of_scope 裁决）。
2. 真实安装包（`dotnet publish` 产物）安装与卸载验证。
3. 双 UI 真实会话冒烟（legacy MainWindow + Fluent shell 四页面）。
4. 真实旧库升级 + pre_restore 回退演练（隔离用户数据副本）。
5. 独立验证 Agent 复核（上下文独立），报告入 `doc/reviews/`。

## 5. 不构成什么

- 不构成正式验收通过；不构成 FEA-14 的释放授权；
- 不改任何契约字节/18 pins。

## 6. FEA-14 卡面汇总（FEA-15-ACCEPT-1，2026-11-10）

以下为各卡的历史收口状态与主要保留项，并非对当前 HEAD 的新验证；完整限制以各卡为准。SET、PREQ、EXPORT 三卡实际状态为 `done`，其余下表各卡为 `closed_with_limitations`，不将所有卡笼统标为同一状态。

| 卡 | 状态 | limitation / NOT_RUN |
|---|---|---|
| [SET-1](../tasks/FEA-14-SET-1.md) | `done` | 设置字体只读投影；字体选择/持久化不在范围；真实 Tab、UI 截图、用户主题包投影、指定真实 artefact 和 Host `WritesAllowed=false` 字体组视图测试 NOT_RUN。 |
| [S5-PREQ-1](../tasks/FEA-14-S5-PREQ-1.md) | `done` | wire minor、Core wire 名和 payload 键原为计划值，须以实现卡实际验证为准；原卡列为 NOT_RUN。 |
| [EXPORT-1](../tasks/FEA-14-EXPORT-1.md) | `done` | 阅读器已选页不可用；真实 Host+Core 导出 E2E、真实 UI 截图和并发压力 NOT_RUN；发布路径仍有已登记 TOCTOU 小窗口。 |
| [READ-1](../tasks/FEA-14-READ-1.md) | `closed_with_limitations` | UI 接线转 READ-2；P12/P15 返回类型和 `confirm_token` 偏差已登记；真实手势、IME、多屏、DPI、主题、托盘和进程重启 NOT_RUN。 |
| [READ-2](../tasks/FEA-14-READ-2.md) | `closed_with_limitations` | 书签面板、整书进度、reset 确认的可见控件未接线；真实手势、IME、多屏、DPI、主题、托盘、进程重启和 UI 截图 NOT_RUN。 |
| [FONT-1](../tasks/FEA-14-FONT-1.md) | `closed_with_limitations` | 字体渲染消费、设置 UI、完整字体元数据和内置字体转后续范围；wire 删除失败负例、大文件/并发/占用压力及真实字体渲染 NOT_RUN；不随包字体。 |
| [LIB-1](../tasks/FEA-14-LIB-1.md) | `closed_with_limitations` | `kind` 不投影、`custom_rank` write-only、排序及模型 deferral、64 位边界问题已登记；真实 Host↔Core 联调、LIB/tags UI、Volume、万级章性能 NOT_RUN。 |
| [EDIT-1](../tasks/FEA-14-EDIT-1.md) | `closed_with_limitations` | 永久删除后 marker 孤儿行、`position` 跨卡口径及批量/分页能力留后续；真实 Host↔Core IPC、EDIT UI、管线联动、万级性能 NOT_RUN。 |
| [AI-1](../tasks/FEA-14-AI-1.md) | `closed_with_limitations` | P24 名称需刷新；引用写入方、名称规范化与替换 label 等事项留后续；真实 Host↔Core IPC、活 Core 端到端、模板 UI、AI/网络、并发和大库 NOT_RUN。 |

补充保留项：SET-1 的样例未按 face 各一行、单 generic 栈无单测，测试共享 `Application.Initialize(Dark)` 存在顺序依赖提示；EXPORT-1 的源码顺序断言脆弱且 provenance 留档见原卡；FONT-1 未覆盖 weight 过滤、wire 级删除失败负例；LIB-1 的 `number_value`、`books.normalized_title` 唯一索引及 kind 语义体积属于已登记 deferral；EDIT-1 的批量 resolve/delete、分页/跨书过滤和 kind UI 预置集合留后续；AI-1 的 version 语义为 Core 单调递增、死方法与旧测试注释留维护卡。具体事实、限定条件和后续归属以对应卡原文为准。

A4 的历史替代证据入口：[BK2-1](../tasks/FEA-13-BK2-1.md)、[COV-2](../tasks/FEA-13-COV-2.md)、[ID-3](../tasks/FEA-13-ID-3.md)、[RESTORE-4](../tasks/FEA-13-RESTORE-4.md)、[SCHED-5](../tasks/FEA-13-SCHED-5.md)，以及 [A4-1](../tasks/FEA-15-A4-1.md)。它们的历史基线早于当前 v14，不构成真实用户库升级和回退的当前版本 PASS。
