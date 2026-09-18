# 交接包：TASK-045 的 ZCode 独立 post-hoc 复审

**委托**：用户 2026-09-18 指示「用 zcode 再审核一次 TASK-045」。委托方=`Codex`（本切片原 Reviewer）；**Reviewer=`ZCode`**（**非本切片作者**、**非本切片 Reviewer**）；作者=`DeepSeek Harness`（已交付并集成）。

**为什么可以并且应当复审**：TASK-045 已由 Codex 一轮 Review + 一轮复审后集成并置 `done`，但按 [协作协议](../09_COLLABORATION.md) §6 与既有先例（[POSTHOC-WINDOW-2026-09-17](../reviews/POSTHOC-WINDOW-2026-09-17.md)、[POSTHOC-WINDOW-DSH-2026-09-18](../reviews/POSTHOC-WINDOW-DSH-2026-09-18.md)），**已集成切片仍须接受外部独立复审，且复审可推翻 `done`**。本次即该复审。

## 固定对象

| 项 | 值 |
|---|---|
| Task 固定 base | `1c171dcdeafc1cbffe6111d503dd0cd598e22dea` |
| 首轮被审 head | `1171bc5eae390639c4caf9d8be5e27069dfba4de`（实现 `602cca8a7bd2a5c850f289d2b73d8f4d6e1d4658` + `1171bc5`；文档 `04a700a6`） |
| 修订被审 head | `a165aa38523aacf1935f935d52293ef389ae9931`（文档 `a99f10a8c88f9ba4771b8c5eee8596b8859f6c93`） |
| 集成提交 | `e2a8f019eea34f47e01904ae6805eef863ddd349`（`--no-ff`，父 `f6258a1` + `7261ec7`） |
| 收口提交 / 工作区起点 | `cb93d66a4ee97de32857ea8f4f018aa7d4ede3a7` |
| Review 工作区 | `G:/CODEX/New Manga.worktrees/TASK-045-posthoc-zcode`（分支 `agent/zcode/TASK-045-posthoc`，已 checkout 到 `cb93d66`；无未提交内容） |

## 交付物

- `doc/reviews/TASK-045-posthoc-zcode.md`：四轴声明（Standards / Spec / Architecture / Verification，逐轴 `executed`/`N/A` + 一行小结，不跨轴排名）+ Findings 表（ID/级别/文件行/触发与影响/复现证据/建议/状态）。
- `verification/TASK-045/posthoc-zcode/**`：复跑日志、探针脚本与输出（**证据必须入库**，会话与仓库外路径不算）。
- **结论口径**（三选一，并给理由）：`uphold`（维持 `done` 与 F-4/F-5/F-8/F-11/F-13/F-14、TASK-042 R-01～R-04 的关闭）/ `uphold_with_findings`（维持关闭，但需另开切片）/ **`overturn`（推翻：须给可复现反例与 P0/P1 依据，Codex 将据此重开）**。
- 可选：在 [TASK-045-1171bc5](../reviews/TASK-045-1171bc5.md) / [TASK-045-a165aa3](../reviews/TASK-045-a165aa3.md) 末尾追加**日期化 post-hoc 勘误小节**（**不得改既有结论正文**）；STATUS 台账由 Codex 落地。

## 复审靶点（按价值排序；含我方证据自身的空白）

1. **F-4 像素等价在"非 filter-0 行"上是**（我方最大的证据空白）——我在首轮复审的 A 段探针用**自己写的 filter-0（无过滤）PNG**，因此**没有覆盖** libpng/Qt 会用到的 Average/Paeth/Up 等行过滤；而"overlap 是否被解码正确性依赖"恰恰要在这种页上才成立（**这也是 TASK-046 AC ① 的前置**）。请用 Qt/libpng 编码的页（含多种过滤器、含首块/末块/越界带）重做「瓦片行 == 该页对应行」「全部瓦片行拼接 == 整页行」「文件高 == 声明 `content_height`」，并**在 `1171bc5` 树上做判别力对照**。若发现 crop 会丢行/错行，请直接给反例。
2. **触发面不变式（我方裁定的核心）**——穷举所有会改变"当前页来源"的入口（`openChapter` / `nextPage` / `previousPage` / `jumpToPage` / `continueReading` / `restartFromBeginning` / `setMode` 以及 `_rebuild_tiles` 的全部调用点），确认"改源必重建并服务"没有遗漏；并复核 `_viewport_page` 的 `(0,0)` 双重语义（我方登记的 R-101）是否在任一路径产生**空窗或过窄窗**（生产 `prefetch=1`）。
3. **断言强度与测试有效性**——逐条审计本次 5 处断言更新（是否确为加强、有无放宽/删除）；两个新 QML 用例是否可能**因错误原因通过**（例如断言到陈旧对象、`childItems()` 取值时机）；**等待预算从 5s 收到 3s** 是否把"偶发失败"变成"偶发通过"（正常路径实测 <100ms 是否足以论证 ~30× 余量）。
4. **QML 面**——`ReaderView.qml` 是否仍有其它**未限定名/遮蔽**（同族陷阱）；`tilesHost.visible && rv.model` 在"非 tiled / 隐藏 / model 为空"各态的取值；delegate 的 `width/height/fillMode` 与 `tileScale()`、`requestTiles(scale)` 的比值是否仍自洽（F-11）。
5. **历史勘误核实**——用 git 历史核实我方勘误「Repeater 未限定 `model.tiles` ⇒ **自 TASK-020 起 delegate 从未创建**，分块视图实际渲染空白，故 TASK-020『tiled 分支已交付』过强、TASK-038『tile 生产可达』仅到装配层」。**若证据不支持，请直接反驳我方勘误。**
6. **清理与缓存路径**——`clearTileCache()`（R-102）与 `_TILE_CACHE_FORMAT` 升版遗留（R-005）是否还有**未声明的用户可见后果**；`_decode` 的短读硬失败（R-004）在真实 Qt 编码页上是否会误报。
7. **TASK-042 侧**——`streaming_png.py` 的 AC ⑧（`zlib.error` → typed `CORRUPT_DATA`）与 AC ⑨（内存构成为"常驻源 + 2×最大 IDAT + O(带)"）是否与实现/用例一致；`_pump` 的包装是否有吞错或漏路径。

## 边界

- **只读**：不得修改 `src/**`、`tests/**`、Schema/migration、依赖清单、`AGENTS.md`、其他 Task；不得改已入档 Review 的**既有结论正文**（只可追加日期化勘误小节）。
- 不与 TASK-042/TASK-046 的带状解码/`overlap=0` 改动混做（解码策略变更属 TASK-046）。
- 不 push；不释放任何冻结 Task；发现需修订时**退回 Codex**（由 Codex 决定重开/另开切片），**不自行改产品代码**。

## 验证要求

- 同一 shell + 同一 venv：**PowerShell + `G:/CODEX/New Manga.task-envs/TASK-012-py312`**，`PYTHONDONTWRITEBYTECODE=1`，`-p no:cacheprovider`；命令、退出码、**passed/skipped 分列 + skip 原因**逐条记录；全仓建议 ≥3 次。
- 报告中**必须分列**：哪些结论是**你独立复跑/自建探针**，哪些是**复用作者或前序 Reviewer 的证据**（并标明复用对象与文件）。
- 凡主张"实现有误"或"关闭不当"，**必须给可复现反例**（命令 + 期望/实际 + 证据文件）。
- 参考入口：[TASK-045-1171bc5](../reviews/TASK-045-1171bc5.md)、[TASK-045-a165aa3](../reviews/TASK-045-a165aa3.md)、[integration-e2a8f01](../../verification/TASK-045/integration-e2a8f01.md)、[review-1171bc5/reviewer_probe.py](../../verification/TASK-045/review-1171bc5/reviewer_probe.py)（我方探针，可直接复用/修改）、[rewind_cost_probe.py](../../verification/TASK-045/rewind_cost_probe.py)、[comment_drift_check.py](../../verification/TASK-045/comment_drift_check.py)。

## 接收方式

```powershell
cd "G:\CODEX\New Manga.worktrees\TASK-045-posthoc-zcode"
$env:PYTHONDONTWRITEBYTECODE='1'
$py = "G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe"
& $py -m pytest -q -rs -p no:cacheprovider     # 期望 842 passed / 6 skipped（既有 tests/network openssl skip）
```
