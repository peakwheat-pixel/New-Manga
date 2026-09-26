# M2-S1 — Large-Media Resource Channel Feasibility Spike

- Task：[M2-S1](../tasks/M2-S1.md)（`kind: research`，Owner=DeepSeek Harness，非作者 Reviewer=Codex）
- 固定 base：`85a2aa7fd07a2dca843bf5cea3ec34070b63bdbc`
- 分支 / 工作区：`agent/deepseek/M2-S1-resource-channel-spike` / `C:/Users/49745/.codex/worktrees/M2-S1-dsh-resource-channel`（C: 独立 clone）
- 固定 M2-C1 Contract blob：`4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3`
- 结论摘要：**在 Windows 上，大媒体（页图/Webtoon tile）跨进程可行**；推荐以
  **受限资源引用/能力 token + Core 侧解析 + 带外文件读取** 为主通道，**流式/分块字节通道** 作为
  需要“无文件路径”或需要显式背压时的第二通道。普通 JSON/Base64 在测量上被证伪。
  命名共享内存不具备能力语义（可匿名写、随创建者销毁）；`DuplicateHandle` 只受源进程 ACL 约束，
  同用户同完整性级进程可复制（已实测）。**产品阈值缺失，选型进入 Contract/Runtime 前仍需用户决定与独立 Review。**
- 全部证据、探针与原始日志见 [`verification/M2-S1/`](../../verification/M2-S1/README.md)。

> 标签约定：`MEASURED` 本次实测；`AS-IS` 固定 base 源码/测试直接证明；`TO-BE` AD-001 已批准约束；
> `PROPOSAL` 本研究原型或设计建议（**不是**产品决定）；`UNVERIFIED`/`NOT_RUN` 未验证/未运行。
> 本报告中的一切跨进程数字都来自**Python↔Python 进程**的隔离探针，**不代表** Tauri/Rust、WebView、
> React 或产品 IPC runtime 的行为——后者本 Task 明确未运行。

---

## 1. 范围与方法

### 1.1 本 Task 做了什么

在同一台 Windows 主机上，用**合成、隔离、可重跑**的探针，对三条候选通道 + 一条对照通道测量：
权限边界、拷贝/序列化次数、容量与吞吐、峰值内存、受控拒绝、取消/崩溃/截断、跨进程关闭与清理、
以及安全属性。载荷是 `%TEMP%\m2s1-lab` 下按固定种子生成的确定性 RGB 噪声 PNG，
仓库内只保留生成器、hash、结果 JSON 与日志（约 200 MB 字节留在 lab 目录，不进入 Git）。

### 1.2 本 Task 没有做什么（不得外推）

- 没有创建产品 IPC server/runtime、Tauri command、React consumer、GUI 实现。
- 没有运行 Tauri/Rust、WebView asset protocol、React 或产品 pytest/GUI。
- 没有解耦 Qt 依赖，没有改动 `src/**`、`tests/**`、依赖、Schema、M2-C1 Contract、AD-001 或治理导航。
- 没有访问真实用户漫画库、源文件、Managed Copy、凭据或模型缓存；**模型权重通道未测量**（`NOT_RUN`）。

### 1.3 环境与复现

主机 Windows NT 10.0.26200.0（Windows 11 家族）、AMD64、32 逻辑处理器、物理内存 32.4 GB
（运行时可用 9.06 GB，负载 72%）、Python 3.14.6、PowerShell 7.6.6。完整环境见
[`verification/M2-S1/00-environment-and-recon.md`](../../verification/M2-S1/00-environment-and-recon.md)
与 `raw/00-recon.log`、`raw/02-host-memory-and-environment.log`。

```powershell
pwsh -NoProfile -File verification/M2-S1/probes/run_all.ps1 `
  | Tee-Object -FilePath verification/M2-S1/raw/00-run-all.log
```

权威转录：[`raw/00-run-all.log`](../../verification/M2-S1/raw/00-run-all.log)；
重复运行一致性：[`raw/04-repeat-run-1.log`](../../verification/M2-S1/raw/04-repeat-run-1.log)。
两次连续运行（第二次在已存在旧 report 文件的情况下）均 `all_zero = True`。

### 1.4 合成 fixture

| fixture | 尺寸 | PNG 字节 | 用途 |
|---|---|---:|---|
| `small_page_800x1200` | 800×1200 | 2,882,143 | 小图 |
| `typical_page_1600x2400` | 1600×2400 | 11,525,983 | 典型页 |
| `webtoon_tile_00..05_800x4000` | 800×4000 ×6 | 各 ≈10,129,000 | 超长 Webtoon 分块（对应生产 `tile_height=4000`） |
| `webtoon_long_800x24000` | 800×24000 | 60,773,055 | 超长整页（6 个 tile 之和） |
| `oversize_2000x12000` | 2000×12000 | 75,948,811 | 超过受控上限的拒绝路径 |

全部为**不可压缩噪声**，是字节量的最坏情况；真实扫描漫画页压缩率更好，因此表中字节数是相对原始像素的
**上界**，不是对真实页大小的断言。各 fixture 的 SHA-256 见
[`raw/fixtures.json`](../../verification/M2-S1/raw/fixtures.json)。

**受控拒绝上限**：探针统一使用 `M2S1_MAX_MEDIA_BYTES = 67,108,864`（64 MiB）。这是**探针配置**，
不是产品阈值；用户尚未给出大媒体尺寸预算，因此本报告不据此发明 PASS 门槛，只证明“超限被类型化拒绝且内存有界”。

---

## 2. AC1 — 来源与边界

完整证据见 [`verification/M2-S1/01-source-and-consumer-reality.md`](../../verification/M2-S1/01-source-and-consumer-reality.md)。
要点：

- **固定点**：`HEAD = base = 85a2aa7…`，branch 一致，`--git-common-dir` 为本地 `.git`、无 `commondir`、
  无 `alternates` → 独立 clone，未在 G: 创建或修改任何对象；开始时 workspace 干净。
- **现有图片/tile 生产者**：`TileGrid`/`TileCache`/`TiledPageRasterizer`
  （`src/infrastructure/imaging/webtoon_tiles.py`）把 tile 解码为 `tile-*.png` 并**返回文件路径**；
  生产装配把缓存放在 `<managed_root>/cache/webtoon-tiles`（`src/bootstrap/core_assembly.py:830-844`）。
- **现有消费者**：Reader ViewModel 把整页与 tile 都用 `QUrl.fromLocalFile(...)` 交给 QML `Image`
  （`src/ui/viewmodels/reader/viewmodel.py:179-187, 379-429`；`src/ui/qml/reader/ReaderView.qml:201-205, 284-292`）。
  也就是说，**当前 AS-IS 的“通道”就是文件 URI + Qt 引擎自读**——这与推荐路线 A 同构，是迁移成本最小的方向。
- **Qt/GUI 耦合**：`_ManagedPageImageSource`（`QImage`）、`qt_compositor`、`pixel_source_style`、
  `export/pdf_qt`、`importing` 仍耦合 Qt（AD-001 constraint 5 的 `MIGRATION_AUDIT_REQUIRED` 范围）；
  tile 的 grid/cache/raster 半部与 `application.tasks.projection`、`application.editing.region_canvas`
  是已存在的 Qt-free seam。本 Task 未改动任何一处。
- **四类资源必须区分**（AC4 前提）：用户源文件（managed root 之外）／Managed Copy（不可变 revision，
  `publish()` 拒绝覆盖）／派生缓存（`cache/**`，可重建、可清理）／模型权重（
  `<data root>/models/detector/`，**未被登记为可清理**）。
- **current/pinned Revision**：`ReaderPage.translated_revision_id` vs `current_translated_revision_id`
  构成 stale 判定；编辑侧以 `expected_current_revision_id` 做并发校验，`set_revision_pinned`
  存在于 `src/application/editing/service.py:574` 与 `src/infrastructure/sqlite/regions.py:183`。
  权威在 Core/SQLite；资源通道**不得**承载 revision 语义。
- **命名冲突提醒**：仓库中 “tile” 有三种含义（Webtoon 像素 band、检测 `tile-local` 坐标系、
  页面列表行）。本报告的 tile 一律指 Webtoon 像素 band。

---

## 3. AC2 — 候选与取舍

### 3.1 候选定义

| 代号 | 候选 | 探针 |
|---|---|---|
| **A** | 受限资源引用 / 能力 token：Core 持有签名密钥与 scope root，签发不透明引用；宿主只拿到引用，由 Core 解析并批准后再**带外**读文件 | `probes/probe_a_token.py` |
| **B** | 流式 / 分块传输：字节经 OS 管道按块流动，宿主按块读取并增量校验 | `probes/probe_b_stream.py` |
| **C1** | Windows **命名** section（`CreateFileMappingW` + 名字） | `probes/probe_c_section.py` |
| **C2** | Windows **匿名** section + `DuplicateHandle`（能力式句柄移交） | `probes/probe_c_section.py` |
| **C3** | 只读句柄 / 只读文件映射的写屏障 | `probes/probe_c_section.py` |
| **D** | 对照：普通 JSON/Base64（Contract §10 已禁止用于大媒体，此处作为量化对照） | `probes/probe_d_base64.py` |

### 3.2 候选矩阵

| 维度 | A 引用/token | B 流式管道 | C1 命名 section | C2 匿名 section + DuplicateHandle | D JSON/Base64（对照） |
|---|---|---|---|---|---|
| 控制/数据分离 | 控制与数据完全分离（MEASURED：85.3 MB 媒体 vs 15,095 B 控制） | 数据即通道（MEASURED：`bytes_on_wire = resource bytes`） | 需另行传名字（≈60 B） | 需另行传 `(pid, handle)`（≈40 B） | 同一消息（MEASURED：×1.3333–1.3336） |
| 拷贝次数（进程间） | 0（宿主按需从文件读；是否再拷贝由消费者决定） | 1（内核管道缓冲 + 读取；可用复用缓冲做到常量内存） | 0（两侧映射同一物理页） | 0（同上） | ≥3（原始→base64 串→JSON 文本→解码） |
| 序列化成本 | 无（不序列化媒体） | 无（原始字节） | 无（映射） | 无（映射） | MEASURED：76 MB 载荷 naive 编码 342 ms |
| 权限边界 | MEASURED：签名、过期、撤销、scope class、只读、词法/包含/reparse 全部拒绝 | MEASURED：只有“打开通道”与“关闭通道”，无细粒度权限 | MEASURED：**默认 DACL 下任何同用户同会话进程只要知道名字即可读写** | MEASURED：`DuplicateHandle` 只受源进程 ACL；同用户可复制 | 无（消息一旦发出即失去控制） |
| 跨进程关闭/撤销 | MEASURED：撤销后同一 token 立即 `REF_REVOKED`；文件删除后 `REF_NOT_FOUND` | MEASURED：消费者关闭通道后生产者收到错误并退出（无挂起） | MEASURED：创建者退出后 section 立即消失（`SECTION_OPEN_FAILED`） | MEASURED：宿主持有的复制句柄让 section 在创建者退出后存活 | 不适用 |
| 失效与诊断 | MEASURED：9 个稳定错误码 | MEASURED：`STREAM_TRUNCATED` 可判别；但**EOF 本身不足以判断完整性**（见 §4.3 B-10） | MEASURED：`SECTION_OPEN_FAILED`（名字不存在/已销毁） | MEASURED：`DUPLICATE_HANDLE_FAILED`、`SECTION_MAP_FAILED` | 无稳定错误语义（编码失败即崩溃） |
| 受控拒绝 | MEASURED：`MEDIA_TOO_LARGE`，0 字节、0 内存增长 | MEASURED：`MEDIA_TOO_LARGE`，0 字节，生产者被关闭通道终止 | MEASURED：`SECTION_LIMIT_EXCEEDED`，未创建 section | 同 C1 | MEASURED：拒绝时 0 字节；不拒绝时 265.6 MB 峰值增长 |
| 多消费者经济学 | N 个消费者各读一次文件（MEASURED 8 消费者 81,032,259 B/11.6 ms，页缓存热） | N 条流，N 份拷贝 | 1 份拷贝，N 个映射 | 1 份拷贝，N 个复用句柄 | N × 1.33 倍字节 |
| 现有代码契合度（AS-IS） | 高：现有 Reader 已经是“Core 给文件 URI，QML 读文件” | 中：需要新增字节通道 | 低：无先例 | 低：无先例 | 低且被禁止 |
| 宿主机（Tauri/WebView）可行性 | **UNVERIFIED**（asset protocol 未运行） | **UNVERIFIED**（sidecar 字节通道未运行） | **UNVERIFIED** | **UNVERIFIED** | UNVERIFIED 且 Contract 禁止 |

---

## 4. AC3 — 可复现容量证据

全部为 MEASURED；原始 JSON 见 `raw/probeA..E-result.json`，日志见 `raw/10..14-*.log`。
每个探针的 exit code 均为 0；`probeE` 的 11 个并发场景、`probeA` 的 15 个、`probeB` 的 12 个、
`probeC` 的 14 个、`probeD` 的 8 个场景全部 `PASS`（合计 60/60）。

### 4.1 路线 A（引用/token）

| 场景 | 结果 | token 字符数 | Core 内解析 | 宿主带外读取 | 宿主 WS 增量 |
|---|---|---:|---:|---:|---:|
| A-01 小图 2.88 MB | PASS sha 匹配 | 227 | 0.410 ms | 2.113 ms | < 0.15 MB |
| A-02 典型页 11.53 MB | PASS sha 匹配 | 233 | 0.334 ms | 6.993 ms | < 0.15 MB |
| A-03 tile 10.13 MB | PASS sha 匹配 | 243 | 0.355 ms | 6.061 ms | < 0.15 MB |
| A-04 超长页 60.77 MB | PASS sha 匹配 | 247 | 0.354 ms | 35.242 ms | < 0.15 MB |
| A-05 超限 75.95 MB | PASS `MEDIA_TOO_LARGE`（未读取任何字节） | 244 | 0.358 ms | — | 0.00 MB |

拒绝路径（全部 PASS，且都是稳定错误码）：`REF_EXPIRED`、`REF_REVOKED`（撤销前同一 token 可解析成功）、
`REF_SIGNATURE_INVALID`（篡改 body）、`REF_OUT_OF_SCOPE`（`../` 词法穿越；绝对路径；
**指向 scope 外的 junction**）、`REF_READ_ONLY`（请求 `mode=write`）、`REF_SCOPE_DENIED`
（token 声明 `user-source` scope）、`REF_REPARSE_POINT`（**scope 内** junction 指向 `managed/`，
包含性检查会放行，只有 reparse 遍历能拦住——这正是 `ManagedFileStorage.remove_managed` 记录的同一威胁）、
`REF_NOT_FOUND`。

通道计量：**控制通道 7,098 B（去）+ 7,997 B（回）= 15,095 B**，同期带外交付 **85,310,202 B** 媒体。
宿主峰值工作集 26.2 MB，Core 峰值 23.6 MB。token 中不含路径以外的秘密；签名密钥只存在于 Core，
且**未**出现在任何结果 JSON（探针只记录密钥长度）。

### 4.2 路线 B（流式管道）

| 场景 | 结果 | 字节 | 总耗时 | 吞吐 | 首字节 | 宿主 WS 增量 |
|---|---|---:|---:|---:|---:|---:|
| B-02 典型页 | PASS sha 匹配 | 11,525,983 | 83.2 ms | 132.1 MB/s | 77.3 ms | +0.99 MB |
| B-04 超长页 | PASS sha 匹配 | 60,773,055 | 109.2 ms | 530.9 MB/s | 77.4 ms | +0.96 MB |
| B-05 块 64 KiB | PASS | 11,525,983 | 86.1 ms | 127.7 MB/s | 78.5 ms | +0.12 MB |
| B-06 块 256 KiB | PASS | 11,525,983 | 85.2 ms | 129.1 MB/s | 78.4 ms | +0.36 MB |
| B-07 块 4 MiB | PASS | 11,525,983 | 87.6 ms | 125.5 MB/s | 78.8 ms | +0.99 MB |
| B-12 慢消费者（每 8 MiB 睡 150 ms） | PASS | 60,773,055 | 1158.7 ms | 50.0 MB/s | 74.8 ms | +0.96 MB |

关键观察：

1. **首字节 ≈ 75–85 ms 全部来自子进程 Python 解释器启动**，不是传输。扣除后 B-04 的 60.77 MB 实际
   传输约 32 ms（≈1.9 GB/s）。块大小 64 KiB→4 MiB 对总耗时几乎无影响（86.1/85.2/87.6 ms），
   说明瓶颈不在块大小；真正的工程结论是“块大小按内存预算与延迟目标选，不是按吞吐选”。
2. **背压真实存在**：慢消费者把 109.2 ms 拉到 1158.7 ms（≈10.6×），而生产者峰值工作集仍是 ~25 MB，
   证明管道没有把整份资源缓冲进内存。
3. **受控拒绝**：B-08 超限 → 0 字节送达；生产者观察到通道关闭后以 `OS_ERROR:22` 退出（exit 4），
   **没有挂起**。
4. **取消**：B-09 读到 4 MiB 后杀死生产者，生产者 exit 1，消费者判定
   `CHANNEL_CANCELLED_BY_CONSUMER`。
5. **截断**：B-10 生产者只写 8 MiB 后**正常退出（exit 0）**，消费者靠“期望长度”发现
   `STREAM_TRUNCATED` → **EOF 与退出码都不足以判断完整性，必须显式带长度/摘要 framing**。
6. **生产者崩溃**：B-11 写 4 MiB 后 `os._exit(3)`，消费者以短读 + 非零退出码判别，结果 PASS。

### 4.3 路线 C（Windows 句柄/共享内存）

| 场景 | 结果 | 观测 |
|---|---|---|
| C1-01 按名字读 | PASS | 另一进程按名字 `OpenFileMappingW`，sha 匹配 2.88 MB |
| C1-02 未授权可写打开 | PASS（**安全问题被证实**） | 一个只“得知名字”的同用户进程以 `FILE_MAP_READ\|FILE_MAP_WRITE` 打开成功，把前 8 字节改成 `HOSTILE!`；创建者读回 `484f5354494c4521` |
| C1-03 破坏可观测 | PASS | 恢复后可再次校验；`corruption_was_observable = true` |
| C1-04 未知名字 | PASS `SECTION_OPEN_FAILED` | 拒绝 |
| C1-05 创建者退出后 | PASS `SECTION_OPEN_FAILED` | 命名 section 随最后一个句柄消失，**无持久性** |
| C2-01 匿名 section 句柄复制进宿主 | PASS，sha 匹配 11,525,983 B | 创建者退出后宿主仍可映射；宿主 WS +10.97 MB |
| C2-02 同用户恶意复制 | PASS（**限制被证实**） | 仅凭 `(pid, handle)` 即可 `OpenProcess`+`DuplicateHandle` 并读取 → `hostile_duplication_succeeded = true` |
| C2-03 伪造句柄值 | PASS `DUPLICATE_HANDLE_FAILED` | 内核按所有者句柄表校验 |
| C2-06 相邻句柄值（+4） | PASS `SECTION_MAP_FAILED` | Windows 句柄 4 字节对齐，+4 可能命中**另一个有效句柄**，但仍不构成该 section |
| C2-04 外来句柄值用于自身句柄表 | PASS `SECTION_MAP_FAILED` | 句柄值只在拥有者进程内有意义 |
| C2-05 超限 section | PASS `SECTION_LIMIT_EXCEEDED` | 在 `CreateFileMappingW` **之前**判定；0 分配、WS 0 增长 |
| C3-01 `GENERIC_READ` 句柄写 | PASS `ERROR_ACCESS_DENIED (5)` | OS 按句柄访问模式拒绝写 |
| C3-02 只读映射写 | PASS `TypeError` | 映射本身只读 |

**内存计量要点**：映射并触碰 11.5 MB 让宿主工作集增长 10.97–12.01 MB。共享内存省掉的是**进程间拷贝**，
不是内存占用——触摸过的页会计入每个消费者的工作集。

### 4.4 路线 D（对照：JSON/Base64）

| 场景 | 结果 | 载荷 | 在线字节 | 膨胀 | 宿主 WS 增量 |
|---|---|---:|---:|---:|---:|
| D-01 小图 | PASS | 2,882,143 | 3,843,070 | 1.3334 | +11.1 MB |
| D-02 典型页 | PASS | 11,525,983 | 15,368,190 | 1.3334 | +42.2 MB |
| D-03 tile | PASS | 10,129,021 | 13,505,574 | 1.3334 | +35.4 MB |
| D-04 超长页 | PASS | 60,773,055 | 81,030,950 | 1.3333 | **+212.5 MB** |
| D-05 单个 JSON 文档内分块（11 块） | PASS | 11,525,983 | 15,368,245 | 1.3334 | +29.4 MB（**未变成有界**） |
| D-05b 按**消息**边界分块（11 条消息） | PASS | 11,525,983 | 15,370,491 | 1.3336 | **+2.8 MB（有界）** |
| D-06 超限受控拒绝 | PASS `MEDIA_TOO_LARGE` | 75,948,811 | 0 | — | +0.0 MB |
| D-07 naive 无界编码（仅一次，最坏情况对照） | PASS | 75,948,811 | 101,265,294 | 1.3333 | **+265.6 MB**（进程峰值 386.9 MB，316 ms） |

结论：Base64 既膨胀 1/3，又让接收端内存与资源大小成正比（58 MB 载荷 → 212 MB 增量）；
**只把分块放进同一个 JSON 文档并不能使内存有界**（D-05），必须有消息边界（D-05b）。

### 4.5 并发/容量（`probeE`）

| 路线 | 消费者 | 交付字节 | 耗时 | 聚合吞吐 | 宿主 WS 增量 |
|---|---:|---:|---:|---:|---:|
| A（一个 Core 控制通道，N 线程带外读） | 1 / 2 / 4 / 8 | 10.13 / 20.26 / 40.52 / 81.03 MB | 6.86 / 7.38 / 8.53 / 11.59 ms | 1.41 / 2.62 / 4.53 / **6.67 GB/s** | 均 < 0.12 MB |
| B（N 个生产者进程 + N 个读取线程） | 1 / 2 / 4 | 10.13 / 20.26 / 40.52 MB | 94.7 / 97.0 / 111.7 ms | 0.10 / 0.20 / 0.35 GB/s | ≤ 0.02 MB |
| C（一个命名 section，N 个读取进程） | 1 / 2 / 4 / 8 | 11.53 / 23.05 / 46.10 / 92.21 MB | 106.0 / 112.4 / 125.2 / 160.9 ms | 0.10 / 0.20 / 0.35 / 0.55 GB/s | ≤ 0.12 MB |

- A 的**控制面被锁串行化**，但带外读取并行；8 消费者仅 11.6 ms。探针同时断言
  `bytes_delivered == expected_bytes`，以避免并发累加本身掩盖丢失（见
  [`verification/M2-S1/02-evidence-manifest.md`](../../verification/M2-S1/02-evidence-manifest.md) §4 缺陷记录）。
  **该数字受 OS 页缓存影响**（fixture 已被反复读取），因此是“缓存热”上限，**冷缓存（首次触盘）吞吐 `NOT_RUN`**。
- B/C 的每消费者约 95–160 ms 主要是子进程 Python 启动成本，不是通道成本。

### 4.6 测量限制与混淆因素（必须与数字一起引用）

1. **首字节 ≈ 78 ms 是解释器启动**，不是通道延迟；A 的解析（0.3–0.45 ms）才是控制面延迟的真实量级。
2. **页缓存热**：所有读取都命中 OS 页缓存；磁盘冷启未测（`NOT_RUN`）。
3. **生产者/消费者都是 Python 进程**，不是 Tauri/Rust/WebView。
4. **峰值工作集单调**：同一进程内 `PeakWorkingSetSize` 不回落，因此以“每场景增量 + 最终累积峰值”表述
   （路线 D 的 386.9 MB 是 `probe_d` 进程的累积峰值）。
5. **fixture 不可压缩**：真实漫画页压缩率更好，故 §4 的字节数是上界。
6. 系统负载 72%、可用物理内存 9.06 GB：所有探针都设置受控上限，未使用耗尽内存的失败路径。

---

## 5. AC4 — 数据保护与生命周期

| 要求 | 结论 | 证据 |
|---|---|---|
| 只读 / 限域访问 | `PASS`（探针级） | A：scope class + 只读 + 包含性 + reparse 遍历（A-11/A-12/A-15）；C3-01 `ERROR_ACCESS_DENIED`、C3-02 `TypeError` |
| 不可从前端路径直接写源文件 | 探针级 `PASS`；OS 级 `UNVERIFIED` | token 类型无法表达 `user-source` scope（A-12 `REF_SCOPE_DENIED`）；但同用户进程仍可自行以可写方式打开文件——**ACL/完整性级别设计未验证** |
| 能力过期 / 撤销 | `PASS` | `REF_EXPIRED`（A-06）、`REF_REVOKED`（A-07，撤销前可用） |
| 取消 | 通道级 `PASS`；Core 工作线程语义 `UNVERIFIED` | B-09（读到 4 MiB 后 kill，生产者 exit 1，无残留） |
| 崩溃 / 重启 | 部分 `PASS`；Core 重启 `NOT_RUN` | B-11 生产者崩溃被判别；C2-01 section 在创建者退出后仍可读；C1-05 命名 section 随创建者消失 |
| 缓存清理 | `AS-IS` 有实现、探针 `NOT_RUN` | `application/maintenance/cleanup.py` 的 `CACHE_SAFE_PREFIXES=("cache/",)` 与 `tile-*.png` 清扫；本 Task 未跑清理探针 |
| 资源 ID 与 current/pinned Revision 绑定 | `PROPOSAL`；`NOT_RUN` | 见 §6.2 的设计要求；AS-IS revision 字段见 §2 |
| 断线后重新获取快照/引用 | `NOT_RUN` | Contract §7.2 已把它留给 runtime；本 Task 未运行任何断线场景 |
| Secret / 任意绝对路径 / 源文件字节 / 模型权重不进入普通 DTO、事件或日志 | 原型 `PASS`，含一处需改进项 | 控制通道只传 token 与类型化错误（15,095 B）；签名密钥只存在于 Core，未写入任何结果 JSON；**但 A 的 Core 批复把文件的绝对路径回给宿主**——产品实现应改为宿主侧资产 URL（PROPOSAL 改进项，见 §6.3） |

四类资源 + 两个额外 case 的处理：

| 生命周期/安全 case | 本 Spike 的处理 |
|---|---|
| 真实用户源文件 | 只用合成 fixture 代替；威胁模型列为“绝不可写、不得成为可写路径目标” |
| Managed Copy | A 中作为独立 scope class `managed-read-only`；不可变 revision 语义由 Core 保留 |
| 派生缓存 | A/B/C 的载荷类别；可重建、可清理 |
| 模型权重 | **未测量**（独立类别，见 §7 `NOT_RUN`）；建议单列通道与生命周期 |
| 取消 / 重启 | 通道级已测；Core worker/断线未测 |
| current/pinned Revision 绑定 | 仅设计要求；未测 |

---

## 6. 威胁模型

### 6.1 资产与对手

**资产**：用户源文件（完整性/可用性）、Managed Copy 与已提交 revision（不可变性）、派生缓存（可重建，但
不得成为写入源文件的跳板）、模型权重（离线、带 pinned SHA-256）、凭据/secret、Revision/Lock 一致性、
以及“前端不得成为写权限来源”这一不变量。

**对手（按能力递增）**：

1. 被攻陷的渲染层（WebView/React 树中的恶意包）：能发任意命令、能读它被授予的任何资源。
2. 同用户、同会话、同完整性级别的其他进程：可 `OpenProcess`、可打开默认 DACL 的对象（本机实测能力）。
3. 低完整性级别 / 不同会话的进程：通常被进程与对象的 ACL 挡住（本 Task 未构造该场景 → `UNVERIFIED`）。
4. 误操作的用户：请求超限资源、误点取消、拔盘/断电导致 Core 崩溃。

### 6.2 各路线威胁与实测状态

| 威胁 | A | B | C1 | C2 |
|---|---|---|---|---|
| 引用被伪造 | 已缓解：HMAC 失败 → `REF_SIGNATURE_INVALID`（实测） | 不适用（无引用） | 名字可猜/可泄漏（实测可写打开） | 句柄值需精确匹配（实测伪值/相邻值均失败） |
| 引用越界读 | 已缓解：词法 + 包含性 + reparse 遍历（实测 3 类拒绝） | 无（通道即数据，越界由打开者决定） | 无 | 无 |
| 引用被重放 | 部分：有 `exp` 与撤销集；**跨重启的密钥轮换策略未测** | 不适用 | 不适用 | 句柄在关闭后失效（未单独测重放） |
| 机密性（同用户对手） | 引用本身是能力；但宿主最终读的是**文件**，同用户进程本来就能读该文件 → 机密性不来自引用 | 管道句柄同样只受 ACL 约束 | **已被攻陷**：任何同用户进程可读写 | **已被攻陷**：同用户可 `DuplicateHandle`（实测成功） |
| 完整性 | 宿主读后可自校验 sha（实测匹配）；写入路径不在通道内 | 需显式 framing 才能判断截断（实测 EOF 不足） | **无完整性保证**（实测被改写） | 同 C1 |
| 资源耗尽 | 受控拒绝（实测 0 字节、0 增长）；并发需配额度 | 受控拒绝 + 背压（实测）；需配最大并发 | 需在创建前限制尺寸（实测 `SECTION_LIMIT_EXCEEDED`） | 同 C1 |
| 崩溃/孤儿 | Core 崩溃后文件仍在（可重建缓存）；引用密钥轮换即全失效 | 生产者崩溃被判别；无孤儿内存 | 随创建者消失，无孤儿 | 宿主句柄持有期间内核对象存活 |
| 生命周期可预测性 | 高（读文件，无内核对象生命周期问题） | 高（关闭通道即结束） | 低 | 中（依赖句柄生命周期与撤销时机） |

**结论**：Windows 句柄/共享内存**不是**“安全性更强的通道”，它只是“拷贝更少的通道”，而且在同用户威胁下
并不比“同用户可直接读的文件”更安全。因此不应以“用句柄/共享内存”作为安全论证。

### 6.3 PROPOSAL 设计要求（进入产品前的候选约束）

1. 引用类型必须携带 scope class、`resource_id`、失效时间、只读标记，并由 Core 在**解析时**重新校验；
   不接受任何形式的“前端传路径”。
2. 若采用 §4.1 的 proto，Core 批复**不得**把绝对路径交给前端；应由 host/Core 的资产协议以受限 URL 形式
   提供字节（本 Task 未测 Tauri 资产协议）。
3. 流式通道必须带显式长度 + 摘要 framing（B-10 证明 EOF 不足）。
4. 命名 section 不得用于承载不可信数据（C1-02 已证实默认可写）；若必须用共享内存，必须显式构建
   security descriptor 并把可写打开限制到指定消费者——**未测**。
5. 派生缓存与源文件/权重的 scope 必须分离；`user-source` scope 不得有任何实现。
6. Secret 不进入任何 DTO/事件/日志；本 Task 已按此执行（密钥只在 Core，结果 JSON 只记录密钥长度）。

---

## 7. 缺失的产品阈值（`USER_DECISION_REQUIRED`）

用户尚未给出大媒体性能/容量阈值，本报告**不**把这些当作既定标准：

1. 必须支持的最大页/tile 字节数（现在的 64 MiB 只是探针配置）。
2. 必须支持的最大并发资源数与订阅者数。
3. 首帧延迟预算（用户能接受多快看到页面）。
4. Core 与宿主的峰值内存预算。
5. 宿主是否被允许直接读 OS 路径（资产协议形态），派生缓存路径是否可以暴露给前端。
6. 引用的有效期与撤销语义（revision 变化时是否立即撤销）。
7. 模型权重是否必须复用同一通道，还是单独通道/单独生命周期。

在这些阈值确定前，路线 A/B 的容量验证只能表述为“在本机、本探针配置下，X 字节资源可被类型化拒绝或完整交付”，
不能表述为“达标”。

---

## 8. AC5 — 推荐与仍需验证项

### 8.1 推荐（`PROPOSAL`，需独立 Review + Codex 集成 + 单独实现 Task）

**主通道：路线 A —— 受限资源引用/token + Core 侧解析 + 带外读取。**

理由（全部有测量支撑）：控制通道零媒体字节（15 KB 控制 vs 85.3 MB 媒体）；无膨胀、无序列化成本；
宿主不必物化整份资源（读 60.77 MB 时 WS 增量 ≈0）；权限/过期/撤销/只读/越界/重解析逃逸全部为稳定
类型化拒绝；与 AS-IS 的“Core 给文件 URI、QML 读文件”同构，迁移面最小。

**第二通道：路线 B —— 流式/分块字节通道，显式长度+摘要 framing。**
用于“不能给出文件路径”或需要显式背压/取消的场景。已实测：有界内存（60.77 MB 载荷 WS 增量 0.96 MB）、
背压真实（慢消费者 10.3× 变慢而生产者内存不变）、取消与崩溃可判别。

**不作为大媒体通道**：路线 D（Contract §10 已禁止，且实测 1.33× 膨胀与随尺寸线性增长的内存）。
**不推荐**：C1 命名 section（无能力语义、默认可匿名写、随创建者消失）。
**有条件可选**：C2 匿名 section + `DuplicateHandle`（生命周期好、多消费者一份拷贝），条件是威胁模型
排除同用户同完整性对手，或 Core 在复制前做显式授权——本 Probe 的同用户复制**实测成功**，
所以不能把它当作机密性边界。

### 8.2 仍需验证（进入产品 Contract/Runtime 之前的 blocker 与解除条件）

| 编号 | 未验证项 | 状态 | 解除条件 |
|---|---|---|---|
| S1-B1 | Tauri/WebView 资产协议能否在给定权限模型下提供受限字节 | `NOT_RUN`（本 Task 无 Tauri runtime） | 在真实 Tauri 骨架中做一个最小 asset-protocol 探针并记录权限/缓存/生命周期 |
| S1-B2 | React 消费者重挂载/重连后的快照与引用重取 | `NOT_RUN`（Task 明确排除） | Runtime Task 按 Contract §7.2 定义并测试 |
| S1-B3 | 源文件边界的 OS 级 ACL/完整性级别设计 | `UNVERIFIED`（只测了按句柄只读） | 给出并验证 DACL/完整性方案，含同用户对手的负向测试 |
| S1-B4 | 真实 Core worker/线程模型的取消与重启语义 | `NOT_RUN`（只测了管道级 kill/崩溃） | 在 Core 任务模型上做取消与恢复探针 |
| S1-B5 | 引用跨 Core 重启/密钥轮换的策略 | `PROPOSAL` only | 定义密钥生命周期与撤销广播，并测试重启后旧引用行为 |
| S1-B6 | 冷缓存（首次触盘）吞吐与首帧延迟 | `NOT_RUN`（页缓存热） | 在清缓存后测量，并给出首帧预算对比 |
| S1-B7 | 真实漫画页压缩率下的字节量 | `UNVERIFIED`（fixture 为不可压缩上界） | 用合成但具真实纹理统计的样本复测 |
| S1-B8 | 打包/沙箱（MSIX/AppContainer）对句柄与管道的影响 | `NOT_RUN` | 在目标打包形态下复跑 C2/B 探针 |
| S1-B9 | 模型权重通道（同一通道 or 独立） | `NOT_RUN` | 由用户决定通道与生命周期后再测 |
| S1-B10 | 引用类型与 current/pinned Revision 的绑定与撤销 | `NOT_RUN` | Core 定义绑定规则并在 revision 变化时测试撤销 |

### 8.3 进入产品的前置条件

任何选型进入产品 Contract/Runtime 前仍需：非作者独立 Review（本 Task 由 Codex 执行）、Codex 集成、
以及用户对 §7 的阈值决定。本报告**不构成**产品集成批准，也不预选 Tauri command 形态或序列化库。

---

## 9. AC6 — 范围与交接

- 只写本 Task 授权的四类路径：`doc/tasks/M2-S1.md`、`doc/research/M2-S1_RESOURCE_CHANNEL_SPIKE.md`、
  `doc/handoffs/M2-S1-*.md`、`verification/M2-S1/**`。
- 保存 `git diff --name-status <base>..<delivery>`、`git diff --check`、原始运行输出与
  `NOT_RUN/BLOCKED` 清单（见 [`04-verification-plan-results.md`](../../verification/M2-S1/04-verification-plan-results.md)
  与 Handoff）。
- 产品代码/测试、依赖、Schema、M2-C1 Contract、AD-001、治理导航：**零改动**。
- Codex 释放证据（`origin/master:verification/M2-S1/release-85a2aa7.md`、`dispatch-85a2aa7.md`）
  不在本分支，未被覆写。

### 9.1 明确 `NOT_RUN` / `UNVERIFIED` 汇总

`NOT_RUN`：Tauri/WebView 资产协议；React 消费者/重连；真实 Core worker 取消；Core 重启后引用行为；
缓存清理探针；断线重取快照；冷缓存吞吐；打包/沙箱形态；模型权重通道；Revision 绑定撤销；
产品 pytest / GUI / IPC runtime（按 Task 范围本就不运行）。

`UNVERIFIED`：源文件边界的 OS 级 ACL/完整性；真实页压缩率下的字节量；低完整性/跨会话对手的拒绝；
命名 section 的显式 security descriptor 方案；`DuplicateHandle` 在非默认 DACL 下的行为。

`BLOCKED`：无。所有已设计实验均实际执行；未执行项均为范围或环境前提缺失（无 Tauri runtime、
无产品 Core 进程模型），而非失败。
