# TASK-045 集成验证（integration_commit `e2a8f01`）

**对象**：TASK-045「TASK-020/038 修订尾项（F-4/F-5/F-8/F-11/F-13/F-14）＋ TASK-042 R-01～R-04」。Owner=`DeepSeek Harness`、Reviewer=`Codex`（**非作者**，两轮）。

| 项 | 值 |
|---|---|
| 任务固定 base | `1c171dc`（开工 fast-forward 至 `6ea3dd3`） |
| 首轮被审 head | `1171bc5`（实现 `602cca8`+`1171bc5`、文档 `04a700a`）；首轮 Review `doc/reviews/TASK-045-1171bc5.md` = **`changes_requested`**（R-001 P1、R-002 P2、R-003～R-005 P3） |
| 修订范围 | `1171bc5..a99f10a`（实现 `a165aa3`、文档 `a99f10a`） |
| 复审 | `doc/reviews/TASK-045-a165aa3.md` = **`approved`**（Review 提交 `f6258a1`） |
| 集成前分支合并 master | `7261ec7`（把 `f6258a1` 与 TASK-046 释放合入分支，无冲突） |
| **integration_commit** | **`e2a8f019eea34f47e01904ae6805eef863ddd349`**（`git merge --no-ff`，父提交 `f6258a1` + `7261ec7`），集成前 master 为 `56f6409` |

## 集成后验证（本机实测）

口径：**PowerShell + `G:/CODEX/New Manga.task-envs/TASK-012-py312`**、`PYTHONDONTWRITEBYTECODE=1`、`-p no:cacheprovider`；证据 [integration-postmerge-tests.txt](integration-postmerge-tests.txt)。

| 场景 | 命令 | 结果 |
|---|---|---|
| 定向 | `pytest tests/reading_export tests/core -q -rs -rf` | **PASS** 133 passed / 0 skipped，exit 0 |
| 全仓 | `pytest -q -rs` | **PASS** 842 passed / 6 skipped，exit 0 |

**6 条 skip 原因（逐条）**：全部为既有 `tests/network` 的 `openssl unavailable`——
`test_connection_tester.py:106`、`test_transport_tls.py:39`、`:47`、`:62`、`:69`、`:83`。
**无新增 skip/xfail、无文件删除、无断言放宽**。

**计数一致性（为何全仓是 842 而非分支上的 830）**：分支基线 master（`c3d9ed2`）早于 TASK-041 的集成，故分支全仓 = 830；集成后 master 是**并集**：

```
825（master @56f6409：含 TASK-041 的 12 例）
 + 14（TASK-045 首轮实现，1171bc5）
 +  3（修订净增：新增 4 例 − 替换 1 例）
 = 842 passed / 6 skipped   ✓ 与实测一致
```

## 诊断痕迹

- **R-001 关闭依据（Reviewer 自己的探针，未改一行）**：`verification/TASK-045/review-1171bc5/reviewer_probe.py`（**从不调用 `requestTiles`**）在修订树上复跑——**B1 首个打开 → 2 个 page-1 瓦片文件**（原 `sources=[]`）、**B3 `nextPage()` 后 → 2 个 page-2 瓦片文件**（原 `[]`，与 page-1 不相交）、**A 段 `F-4 property holds: True`**。完整输出见 [review-a165aa3/reviewer-probe-on-revision.txt](review-a165aa3/reviewer-probe-on-revision.txt)。
- **判别力**：修订测试跑在 `1171bc5` 纯树上 → **8 failed / 125 passed，exit 1，无崩溃**（[review-a165aa3/discriminating-revision-tests-vs-1171bc5.txt](review-a165aa3/discriminating-revision-tests-vs-1171bc5.txt)）。
- **注释守卫**：`comment_drift_check.py` 复跑 exit 0，且新增守卫禁止 `at most one rewind` 在 `src/infrastructure/imaging/**` 回流。

## 关闭关系（本次登记的 findings）

| 关闭项 | 依据 |
|---|---|
| **F-4**（tile 落盘几何） | 首轮实现 + 我自写 PNG 编码器逐行复现（"瓦片行拼接 == 整页行"）；本轮 A 段仍 `holds: True` |
| **F-5**（翻页/打开显示） | 修订后 B1/B3 均自动服务，且新增 2 个**不手动请求**的 QML 用例（对修前树 8 failed） |
| **F-8**（`@Slot` 缺 `result=`） | 元对象断言 `returnType == QVariantMap`（首轮） |
| **F-11**（显示像素 vs 页像素） | `requestTiles(top, bottom, scale)` + QML `tileScale()`，比值与 delegate 高度绑定一致（首轮复核） |
| **F-13 / F-14**（注释口径） | `setClipRect` 归零、缓存键内容寻址；本轮类 docstring 改为实测口径 + 守卫 |
| **TASK-042 R-01** | `zlib.error` → typed `CORRUPT_DATA` + 端到端优雅退化 |
| **TASK-042 R-02** | 内存构成实测口径（源 + 2×最大 IDAT + O(带)），修正"≈3–4× 带宽" |
| **TASK-042 R-03（AC ⑩）** | **文档化 + 实测**（见下"AC ⑩ 最终口径"）；解码面收口移交 TASK-046 |
| **TASK-042 R-04** | Qt 编码 `1600×20000` 夹具带状读与 Qt 逐字节一致 |

## AC ⑩ 最终口径（入档）

- `visible_tiles` 升序**只保证"不向后跳"**；
- 生产 `overlap=64`（`src/bootstrap/app.py:553`）使**每个非首块的解码窗起点落在游标之前**，故**每块各 rewind 一次并从 row 0 重扫**——多块视口成本 **O(块数²)**（实测：`400×20000` 全页 25 块 = **24 次 rewind**；`1600×8000` Qt 编码页两块同调用多付 ≈**8.9s**，作者留证 ≈9.7s）；
- **TASK-042 Handoff 的"全页只需一次顺序扫描"仅在 `overlap=0` 时成立**；
- **TASK-045 F-4 之后 overlap 对落盘像素已无贡献**（瓦片已裁到 content band）；
- **收口责任**：解码面（overlap 取值 / 复用上一窗尾部）由 **TASK-046** 承接（本切片只做注释与实测，未改解码策略）。

## TASK-020/038 勘误

`ReaderView.qml` 的瓦片 `Repeater` 曾用未限定 `model.tiles`，而 `model` 在该作用域解析为 **Repeater 自身**的 `model` ⇒ **delegate 从未创建**，同时整图回退因 `tilesActive` 为真被隐藏 ⇒ **分块（webtoon tiled）视图自 TASK-020 起实际渲染空白**。

由此更正两处历史表述（不改已入档 Review 正文，按惯例以 STATUS 勘误行 + 本记录登记）：

- **TASK-020** 的"QML webtoon viewer tiled 分支已交付"**过强**：几何/缓存/VM 侧交付属实，QML 渲染面自始不可见；
- **TASK-038** 的"tile 在生产可达"仅到**装配层可达**（`tile_factory` 注入成功），未到"渲染可见"。

本轮修订已修复该缺陷（`rv.model.tiles` + `tilesHost.visible`），并有"打开即服务/换页自动服务"的机器化断言。

## 遗留与风险

- **R-101（P3，登记）**：bootstrap 会把 `_viewport_page` 记为 `(0,0)`，`span` 退化为 1 行；生产 `prefetch=1` 下服务集合仍为 `{0,1}`，**当前行为正确**，仅语义含糊（建议改 `None` 或显式常量）。
- **R-102（P3，已声明）**：`clearTileCache()` 清缓存后不自动补服务（当前无 QML 入口；接线时建议同补一次当前视口物化）。
- **仍未验证**：真机屏幕最终栅格（断言覆盖瓦片文件与 delegate `source` 生命周期）；真实商业超大 webtoon 页。
- **时延**：超大页分块阅读仍受解码面 O(块数²) 影响——TASK-046 的靶子。
- **TASK-046 开工门已解除**（写集合冲突随本次集成消除）。
