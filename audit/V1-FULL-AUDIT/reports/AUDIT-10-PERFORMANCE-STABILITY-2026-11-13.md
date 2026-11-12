# AUDIT-10：性能与稳定性

状态：`PARTIAL`。完成一组可重复的 Core 合成微基准，未达到原始清单要求的完整应用性能、模型吞吐、批量输入、长时运行和恢复测试；没有性能基线阈值，因此不据此判定产品“够快”或“稳定”。

## 方法与环境

- 固定产品源码基线：`10e4ee013835605800d3830fb960ae8d3aa04167`；本轮执行 generated HEAD=`4e04e68c0db07ab136bc801e7fee27e7a5097564`、branch=`main`。该 HEAD 的审计提交不改变产品源代码。
- runner：`python audit/V1-FULL-AUDIT/tests/audit_runner.py audit10-performance`；规范样本输出见 `logs/audit10-performance-20261112T222445371097Z.log` 与 `evidence/audit10-performance-20261112T222445371097Z.json`，微基准详细 JSON 为 `evidence/audit10-performance-metrics-20261112T222445371097Z.json`；pytest/产品源码未修改。
- Windows 11（10.0.26300）、AMD64 Family 25 Model 97 Stepping 2、32 logical CPU；Python 3.14.6、Pillow 12.3.0。系统物理内存约 33.98 GB；采集后可用约 17.43 GB。进程 working set 约 48.13 MB，进程 lifetime peak 约 48.29 MB；这是探针进程级数据，不是应用稳态内存曲线。
- 所有输入在进程内生成，无磁盘 I/O 或真实用户数据：720×1080、5,437-byte PNG，8 个文本区域；`simple-fill` mask 为 28,800 pixels（3.704%）。每项 20 个计时样本、2 组 warm-up；细粒度操作按 32/8/4 次批量计时再折算单次时间，以降低 Windows CPU 计时粒度误差。

## 结果

| 生产代码路径 | median / p95（毫秒/操作） | 单样本定义 | 结果 |
|---|---:|---|---|
| `PillowImageCompositor._open` PNG decode | 0.968 / 1.040 | 解码一个 720×1080 内存 PNG | 20×32 批量；process CPU median 0.977 ms/页 |
| `PillowTextLayoutEngine.layout` | 1.330 / 1.373 | 对 8 个合成 CJK 区域各排版一次 | 20×32 批量；process CPU median 1.465 ms/8 区域组 |
| `PillowImageCompositor.compose_page` | 9.132 / 9.543 | 在 720×1080 页上合成 8 个已排版区域 | 20×8 批量；process CPU median 9.766 ms/页 |
| `SimpleFillProvider.inpaint` / protected-pixel check | 109.972 / 110.846 | 720×1080 RGB24 页、3.704% 矩形 mask 的一处 `simple-fill` | 20×4 批量；process CPU median 109.375 ms/区域 |

process CPU 时间为所有进程线程的合计，少数合成操作结果略高于 wall time；本表不是整机 CPU 利用率。首次字体索引 call 的探针在两次未用于最终数值的先导运行中分别约 106 ms 与约 20 ms，受 OS 文件缓存状态影响，不能称为稳定冷启动指标。两个先导运行日志与 JSON保留；首次输出曾与 runner metadata 路径冲突，计时器粒度粗的 CPU 样本亦未用于上表。规范运行把 metrics 和 runner metadata 分存为不同文件。

## 未测矩阵

| 原始清单 | 状态 | 原因/边界 |
|---|---|---|
| 应用冷/热启动、窗口/Host 首次响应 | `NOT_RUN` | 字体首次索引不等于应用启动；GUI runner 退出耗时不是 UI 启动基准。 |
| 大批图片导入、长条漫载入/连续翻页/缩放拖动 | `NOT_RUN` | 无大规模文件集或有效 Reader 页面；本微基准只在内存中解码单页。 |
| OCR、翻译、图像修复模型、导出全流程 | `NOT_RUN` | 没有加载真实模型/GT、调用 API 或执行磁盘导出。`simple-fill` 是结构化基础 route，不代表 learned inpainting。 |
| 数据库 I/O、缓存增长、实际 GUI/sidecar 长时资源曲线 | `NOT_RUN` | 微基准没有 database、进程树、取消/重试或 soak 测试。 |
| 后台任务取消、资源释放、长时间运行 | `NOT_RUN` | 没有启动后台任务、强制退出或多小时运行。 |

结论只适用于记录的合成输入和当前本机环境，不外推到模型、真实作品或安装后应用。全 Task AC2/AC3/AC4 继续 `PARTIAL`，Release Gate 继续 `BLOCKED`。
