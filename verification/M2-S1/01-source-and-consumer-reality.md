# M2-S1 — 固定点、来源与消费者现实（AC1 证据）

本文件只记录**只读源码/仓库勘察**结果，不含任何产品实现、不改动 `src/**`/`tests/**`、不访问用户漫画库或凭据。
所有行号均指固定 base `85a2aa7fd07a2dca843bf5cea3ec34070b63bdbc`（本分支 HEAD）。

## 1. 固定点与工作区核验

原始转录：[`raw/00-recon.log`](raw/00-recon.log)（由 [`probes/00_recon.ps1`](probes/00_recon.ps1) 生成，可重跑）。

| 项目 | 实测值 | 判定 |
|---|---|---|
| `git rev-parse --show-toplevel` | `C:/Users/49745/.codex/worktrees/M2-S1-dsh-resource-channel` | 与派发一致 |
| `git rev-parse --git-dir` | `.git`（绝对路径在该 clone 内） | 本地 |
| `git rev-parse --git-common-dir` | `.git`（同上，`commondir` 不存在） | **独立 clone，非 linked worktree** |
| `.git/objects/info/alternates` | 不存在 | 非共享对象库 |
| `git rev-parse HEAD` | `85a2aa7fd07a2dca843bf5cea3ec34070b63bdbc` | 与 Task 固定 base 一致 |
| `git rev-parse --abbrev-ref HEAD` | `agent/deepseek/M2-S1-resource-channel-spike` | 与 Task 固定 branch 一致 |
| 开始工作时 `git status --porcelain` | 空 | 干净 |
| `HEAD:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3` | 与 Task 记录、`origin/master` 三方一致 |
| `git remote -v` | `origin = G:/CODEX/New Manga` | 仅为 remote 配置；git-dir/common-dir 均在 C:，未在 G: 创建或改动任何对象 |
| `git worktree list` | 仅本 clone 一条 | 未创建/删除其他 worktree |

结论：**G: 主仓库与其他 worktree 未被写入**。Codex 的释放证据位于 `origin/master`（`610f99d`）的
`verification/M2-S1/release-85a2aa7.md` 与 `dispatch-85a2aa7.md`；本交付分支刻意不 merge 该治理提交，故
这些文件**不在本分支**，也未被本 Task 覆写。[`README.md`](README.md) 记录了这一点。

## 2. 证据标签

- `AS-IS`：固定 base 的源码/测试直接证明。
- `TO-BE`：AD-001 已批准的目标架构约束。
- `PROPOSAL`：仅本次研究原型（见 `probes/**`），**不是**产品设计决定。
- `UNKNOWN` / `UNVERIFIED` / `NOT_RUN`：无证据或未运行。

## 3. AS-IS：图片与 tile 的生产者/消费者

当前**没有**任何跨进程资源通道。QML 与 Python 在同一进程内，图片/tile 通过**文件 URI**交给 QML
`Image` 元素，由 Qt 引擎自行读取文件。这一点是关键前提：未来 Tauri/React 宿主是否允许 WebView
直接读 `file://`（以及以什么授权方式）**本 Task 不假设**。

| 环节 | 主体 | 证据（base 行号） | 标签 |
|---|---|---|---|
| Webtoon 页面 → tile 分区几何 | `TileGrid`（纯几何，`visible_tiles` 带 prefetch） | `src/infrastructure/imaging/webtoon_tiles.py:115-195` | AS-IS |
| tile 解码/落盘 | `TiledPageRasterizer`：每次只解码一条 band，写成 `tile-*.png`，返回**文件路径** | `src/infrastructure/imaging/webtoon_tiles.py:14-19, 247-260, 317-320` | AS-IS |
| tile 缓存身份 | 缓存键含 `_TILE_CACHE_FORMAT|source_digest|WxH|tile_height|overlap|index` | `src/infrastructure/imaging/webtoon_tiles.py:41-56, 416-427` | AS-IS |
| tile 缓存清理 | `clear()` 删除全部 `tile-*.png` 代 | `src/infrastructure/imaging/webtoon_tiles.py:431-445` | AS-IS |
| tile 缓存目录与内存预算（生产） | `<managed_root>/cache/webtoon-tiles`，`tile_height=4000`，`overlap=0`，`prefetch=1`，`TileCache(max_bytes=512MiB)` | `src/bootstrap/core_assembly.py:830-844` | AS-IS |
| 「QML 不触碰文件/模型」的现有边界声明 | 注释：tile factory 是 Python-only | `src/bootstrap/core_assembly.py:797-801` | AS-IS |
| 整页图片 → QML | `_source_path` → `QUrl.fromLocalFile(path).toString()` | `src/ui/viewmodels/reader/viewmodel.py:179-187` | AS-IS |
| tile → QML | `requestTiles()` 调 `tile_file()` 后用 `QUrl.fromLocalFile` 填 `row["url"]` | `src/ui/viewmodels/reader/viewmodel.py:379-429` | AS-IS |
| tile 生命周期归 ViewModel | `_rebuild_tiles()` / `clearTileCache()`，注明「tile 是可重建像素缓存，清理绝不触碰业务真相」 | `src/ui/viewmodels/reader/viewmodel.py:293-338, 431-438` | AS-IS |
| QML 消费面 | `Image { source: model.sourcePath }` 与 `Repeater` 中 `Image { source: modelData.url }` | `src/ui/qml/reader/ReaderView.qml:201-205, 284-292` | AS-IS |
| 导出侧字节提供者 | `file_bytes_provider(page.original_path)`（进程内回调） | `src/ui/viewmodels/reader/viewmodel.py:469-483` | AS-IS |
| 整页/裁剪像素的 Core 侧来源 | `_ManagedPageImageSource._page_image`：只读 Managed Copy，做 containment 检查后 `QImage` 解码；缺失/不可解码是 typed provider failure | `src/bootstrap/core_assembly.py:217-260` | AS-IS |
| region 裁剪 → PNG bytes | `region_crop()` 经 `QBuffer` 编码 PNG（进程内 bytes） | `src/bootstrap/core_assembly.py:269-299` | AS-IS |
| 整页 → PNG bytes | `page_png()`（color step 输入，进程内 bytes） | `src/bootstrap/core_assembly.py:301-313` | AS-IS |
| 导入侧解码 | `QImageReader(buffer)` / `QImage(raw, w, h, bpl, fmt)` | `src/infrastructure/importing.py:47-54, 181-211` | AS-IS |
| tile-local 坐标（**命名冲突**） | `COORDINATE_SPACE_TILE = "tile-local"` 是检测 provider 的坐标系，与 Webtoon 像素 band 无关 | `src/ports/detection/ports.py:22-48` | AS-IS |
| 同上（**命名冲突**） | 分页列表模型注释「The rows are page tiles」指页面列表行，与像素 tile 无关 | `src/ui/models/tasks/page_list_model.py:1-8` | AS-IS |
| tile 不进入译文上下文 | 「Tiles are an image-processing concern and never appear here」 | `src/application/translation/context/builder.py:285` | AS-IS |
| 已知 Qt 耦合例外（导出） | `application/export/pdf_qt.py` 使用 `QImage`/`QPdfWriter` | `src/application/export/pdf_qt.py:20-24`；M2-C1 §2 | AS-IS |
| 现有页内容解析（原图/译图 + stale 提示） | `resolve_page()` 返回 `(path, status_message)`；`current_source_path` | `src/application/reading/service.py:253-276` | AS-IS |

要点：**「tile」在本仓库有三种含义**（Webtoon 像素 band、检测 tile-local 坐标系、页面列表行）。本研究报告
中的 tile 一律指 **Webtoon 像素 band**（`800x4000` 合成 fixture 对应 `tile_height=4000` 的生产默认值）。

## 4. 四类资源的生命周期/安全类别（AC4 分类前提）

| 类别 | 位置与证据 | 现有保护 | 本 Spike 的处理 |
|---|---|---|---|
| 用户源文件 | 位于 managed root **之外**；`remove_managed` 的 docstring 明确「user source files are never inside the managed root at all」 | 只读导入；受管删除在结构上无法到达 | 探针只使用 `%TEMP%` 下的合成 fixture，**从未访问真实用户源文件**；威胁模型中把「前端路径不得成为写权限」单列 |
| Managed Copy | `books/{book_id}/chapters/{chapter_id}/{original,masks,clean,translated,thumbnails,previews,debug}`，`publish()` 用 `os.replace` 且拒绝覆盖已存在文件 | 已提交 revision 不可变；路径为相对路径 | 路线 A 的 scope 中设立 `managed/` 目录类别（`managed-read-only` scope class） |
| 派生缓存 | `cache/webtoon-tiles/tile-*.png`；`CACHE_SAFE_PREFIXES = ("cache/",)` | 可重建、可清理；清理不打开数据库 | 路线 A/B/C 的载荷就是这类派生像素的代表 |
| 模型权重 | `<data root>/models/detector/<DOCTR_WEIGHTS_FILENAME>`，可用 `NEWMANGA_DETECTOR_WEIGHTS` 覆盖；`cleanup.py` 明确「Model/weight directories can be registered later; none is registered by this slice」 | **未被登记为可清理**；离线、带 pinned SHA-256 | 本 Spike **未**把权重当作图片通道载荷；权重作为独立类别在威胁模型与推荐中单列，并标 `UNVERIFIED`（未测量） |

current/pinned Revision 绑定（AC4 需要区分的第四个 case）：

- 阅读侧：`ReaderPage.translated_revision_id`（磁盘上译图产自哪个 revision）与 `current_translated_revision_id` 不同即 `translated_stale`（`src/application/reading/ports.py:25-49`）。
- 编辑侧：`Region.current_revision_id` 在创作时确定；写入路径接受 `expected_current_revision_id` 做乐观并发校验（`src/application/editing/service.py:96-113, 484-510`）；`set_revision_pinned` 存在（`src/application/editing/service.py:574`，持久化 `src/infrastructure/sqlite/regions.py:183`）；`restore_revision` 复制快照为新 revision（`src/application/editing/service.py:550+`）。
- 结论：**current/pinned revision 的权威在 Core 进程与 SQLite**；资源通道只搬运像素，不得承载 revision 语义。这正是路线 A 推荐把 `resource_id` 与 revision 绑定、并由 Core 在签发时校验的原因（PROPOSAL）。

## 5. Qt/GUI 耦合与可用的 Core/host seam

- `src/bootstrap/core_assembly.py` 提供进程内可复用的 Core 装配（M2-I1 集成 `cff1e0a`），但**没有** IPC 进程/会话接口；`src/bootstrap/app.py` 仍是 Qt 入口。
- Qt-free seam：`application.tasks.projection`、`application.editing.region_canvas`（M2-C1 §2），以及 Webtoon tile 的 grid/cache/raster 半部（`webtoon_tiles.py:21-23` 声明「本模块完全没有 Qt import」）。
- 仍耦合 Qt 的部分：`_ManagedPageImageSource`（`QImage`）、`infrastructure/rendering/qt_compositor.py`、`infrastructure/rendering/pixel_source_style.py`、`application/export/pdf_qt.py`、`infrastructure/importing.py`。
- AD-001 Migration constraint 5 要求最终 Core 可 headless；本 Spike **不**修改这些依赖，也**不**声称它们已解耦。

## 6. 明确未实现（不得声称）

- 没有 Tauri、React↔Python IPC runtime、消息 schema 版本协商、事件重放或断线协议（M2-C1 §1 已声明；base 中无相关源码）。
- 没有跨进程大媒体通道；没有 `ImportSourceRef` 具体类型；没有 `CredentialRef` 交换（M2-C1 §5、§10、§11）。
- 因此本报告的一切跨进程数字都来自**本 Task 自建的隔离探针**，属于 `MEASURED (PROPOSAL prototype)`，不等于产品集成能力。

## 7. 方法与只读性

- 勘察命令集见 `probes/00_recon.ps1`；输出见 `raw/00-recon.log`。
- 全部 `git` 命令为只读（`rev-parse`、`status`、`log`、`ls-files`、`ls-tree`、`diff`、`show`、`hash-object`）。
- 未运行产品 pytest、未启动 GUI、未访问网络、未修改任何共享契约或 M2-C1 工件。
