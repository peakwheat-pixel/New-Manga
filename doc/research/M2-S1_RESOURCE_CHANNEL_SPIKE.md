# M2-S1 — Large-Media Resource Channel Feasibility Spike

- Task：[M2-S1](../tasks/M2-S1.md)（`kind: research`，Owner=DeepSeek Harness，非作者 Reviewer=Codex）
- 固定 base：`85a2aa7fd07a2dca843bf5cea3ec34070b63bdbc`
- 分支 / 工作区：`agent/deepseek/M2-S1-resource-channel-spike` / `C:/Users/49745/.codex/worktrees/M2-S1-dsh-resource-channel`（C: 独立 clone）
- 固定 M2-C1 Contract blob：`4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3`
- 结论摘要：**在 Windows 上，大媒体（页图/Webtoon tile）跨进程可行**；推荐以
  **受限资源引用（签名、可解码，非不透明）+ Core 侧解析 + 带外文件读取** 为主通道，**流式/分块字节通道** 作为
  需要“无文件路径”或需要显式背压时的第二通道。普通 JSON/Base64 在测量上被证伪。
  命名共享内存不具备能力语义（可匿名写、随创建者销毁）；`DuplicateHandle` 只受源进程 ACL 约束，
  同用户同完整性级进程可复制（已实测）。**产品阈值缺失，选型进入 Contract/Runtime 前仍需用户决定与独立 Review。**
- 引用模型的准确表述（Review R-002）：原型引用是 `m2s1.<base64url(json)>.<base64url(hmac)>`，
  **签名只提供完整性与来源真实性，不提供保密性**——`rel`（相对路径）、`rid`、`scope`、`exp`、`mode`
  对持有该字符串的任何人都可解出（实测 F-01）。
- 边界限制（Review R-001）：原型的解析与读取是**先检查后使用**（check-then-use），检查与调用方
  `open()` 之间存在竞态窗口；静态路径输入下的负向拒绝已实测，**并发替换场景的防护仍为 `UNVERIFIED`**
  （实测窗口 F-03/F-04/F-05/F-06，隔离缓解对照 F-07/F-08；见 §12）。
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
| **A** | 受限资源引用 / 签名引用：Core 持有签名密钥与 scope root，签发 `m2s1.<base64url(json)>.<base64url(hmac)>`；**正文可解码、并非不透明**，签名只保证完整性与来源；宿主只拿到引用，由 Core 解析并批准后再**带外**读文件 | `probes/probe_a_token.py`、`probes/probe_f_boundary.py` |
| **B** | 流式 / 分块传输：字节经 OS 管道按块流动，宿主按块读取并增量校验 | `probes/probe_b_stream.py` |
| **C1** | Windows **命名** section（`CreateFileMappingW` + 名字） | `probes/probe_c_section.py` |
| **C2** | Windows **匿名** section + `DuplicateHandle`（能力式句柄移交） | `probes/probe_c_section.py` |
| **C3** | 只读句柄 / 只读文件映射的写屏障 | `probes/probe_c_section.py` |
| **D** | 对照：普通 JSON/Base64（Contract §10 已禁止用于大媒体，此处作为量化对照） | `probes/probe_d_base64.py` |

### 3.2 候选矩阵

| 维度 | A 签名引用（可解码） | B 流式管道 | C1 命名 section | C2 匿名 section + DuplicateHandle | D JSON/Base64（对照） |
|---|---|---|---|---|---|
| 控制/数据分离 | 控制与数据完全分离（MEASURED：85.3 MB 媒体 vs 15,095 B 控制） | 数据即通道（MEASURED：`bytes_on_wire = resource bytes`） | 需另行传名字（≈60 B） | 需另行传 `(pid, handle)`（≈40 B） | 同一消息（MEASURED：×1.3333–1.3336） |
| 拷贝次数（进程间） | 0（宿主按需从文件读；是否再拷贝由消费者决定） | 1（内核管道缓冲 + 读取；可用复用缓冲做到常量内存） | 0（两侧映射同一物理页） | 0（同上） | ≥3（原始→base64 串→JSON 文本→解码） |
| 序列化成本 | 无（不序列化媒体） | 无（原始字节） | 无（映射） | 无（映射） | MEASURED：76 MB 载荷 naive 编码 342 ms |
| 引用保密性（R-002） | **NONE**：正文为 Base64URL JSON，无密钥即可解出 `rel`/`rid`/`scope`/`exp`/`mode`（MEASURED F-01）；签名不保密 | 不适用（无引用） | 名字即可泄漏 | 句柄值泄漏即等同于能力 | 无（载荷即明文语义） |
| 权限边界 | MEASURED（**仅静态路径输入**）：签名、过期、撤销、scope class、只读、词法/包含/reparse 全部拒绝；**检查→打开之间的替换未防护**（F-03..F-06，`UNVERIFIED`） | MEASURED：只有“打开通道”与“关闭通道”，无细粒度权限 | MEASURED：**默认 DACL 下任何同用户同会话进程只要知道名字即可读写** | MEASURED：`DuplicateHandle` 只受源进程 ACL；同用户可复制 | 无（消息一旦发出即失去控制） |
| 跨进程关闭/撤销 | MEASURED：撤销后同一 token 立即 `REF_REVOKED`；文件删除后 `REF_NOT_FOUND` | MEASURED：消费者关闭通道后生产者收到错误并退出（无挂起） | MEASURED：创建者退出后 section 立即消失（`SECTION_OPEN_FAILED`） | MEASURED：宿主持有的复制句柄让 section 在创建者退出后存活 | 不适用 |
| 失效与诊断 | MEASURED：9 个稳定错误码（另含 F 的 `FILE_IDENTITY_CHANGED`、`MEDIA_TOO_LARGE_BY_HANDLE`，仅隔离对照） | MEASURED：`STREAM_TRUNCATED` 可判别；但**EOF 本身不足以判断完整性**（见 §4.3 B-10） | MEASURED：`SECTION_OPEN_FAILED`（名字不存在/已销毁） | MEASURED：`DUPLICATE_HANDLE_FAILED`、`SECTION_MAP_FAILED` | 无稳定错误语义（编码失败即崩溃） |
| 受控拒绝 | MEASURED：`MEDIA_TOO_LARGE`，0 字节、0 内存增长；**大小检查同样是先检查后打开**（F-05） | MEASURED：`MEDIA_TOO_LARGE`，0 字节，生产者被关闭通道终止 | MEASURED：`SECTION_LIMIT_EXCEEDED`，未创建 section | 同 C1 | MEASURED：拒绝时 0 字节；不拒绝时 265.6 MB 峰值增长 |
| 多消费者经济学 | N 个消费者各读一次文件（MEASURED 8 消费者 81,032,259 B/11.6 ms，页缓存热） | N 条流，N 份拷贝 | 1 份拷贝，N 个映射 | 1 份拷贝，N 个复用句柄 | N × 1.33 倍字节 |
| 现有代码契合度（AS-IS） | 高：现有 Reader 已经是“Core 给文件 URI，QML 读文件” | 中：需要新增字节通道 | 低：无先例 | 低：无先例 | 低且被禁止 |
| 宿主机（Tauri/WebView）可行性 | **UNVERIFIED**（asset protocol 未运行） | **UNVERIFIED**（sidecar 字节通道未运行） | **UNVERIFIED** | **UNVERIFIED** | UNVERIFIED 且 Contract 禁止 |

---

## 4. AC3 — 可复现容量证据

全部为 MEASURED；原始 JSON 见 `raw/probeA..E-result.json`，日志见 `raw/10..14-*.log`。
原交付每个探针的 exit code 均为 0；`probeE` 的 11 个并发场景、`probeA` 的 15 个、`probeB` 的 12 个、
`probeC` 的 14 个、`probeD` 的 8 个场景全部 `PASS`（合计 60/60）。
**修订（Review R-001/R-002）新增 probe F 的 8 个边界场景，8/8 `PASS`、exit 0（§4.7）；两条路线合计 68/68。**
A–E 的日志为原交付产物，**修订未重跑**，其原始命令与 exit code 保持不变。

### 4.1 路线 A（签名引用，可解码）

| 场景 | 结果 | token 字符数 | Core 内解析 | 宿主带外读取 | 宿主 WS 增量 |
|---|---|---:|---:|---:|---:|
| A-01 小图 2.88 MB | PASS sha 匹配 | 227 | 0.410 ms | 2.113 ms | < 0.15 MB |
| A-02 典型页 11.53 MB | PASS sha 匹配 | 233 | 0.334 ms | 6.993 ms | < 0.15 MB |
| A-03 tile 10.13 MB | PASS sha 匹配 | 243 | 0.355 ms | 6.061 ms | < 0.15 MB |
| A-04 超长页 60.77 MB | PASS sha 匹配 | 247 | 0.354 ms | 35.242 ms | < 0.15 MB |
| A-05 超限 75.95 MB | PASS `MEDIA_TOO_LARGE`（未读取任何字节） | 244 | 0.358 ms | — | 0.00 MB |

拒绝路径（全部 PASS，且都是稳定错误码；**限定为静态路径输入**，见下方 R-001 说明）：`REF_EXPIRED`、
`REF_REVOKED`（撤销前同一 token 可解析成功）、`REF_SIGNATURE_INVALID`（篡改 body）、`REF_OUT_OF_SCOPE`
（`../` 词法穿越；绝对路径；**指向 scope 外的 junction**）、`REF_READ_ONLY`（请求 `mode=write`）、
`REF_SCOPE_DENIED`（token 声明 `user-source` scope）、`REF_REPARSE_POINT`（**scope 内** junction 指向
`managed/`，包含性检查会放行，只有 reparse 遍历能拦住——这正是 `ManagedFileStorage.remove_managed`
记录的同一威胁）、`REF_NOT_FOUND`。

> **R-001 限定（必须与上表一起引用）**：上述拒绝是在**静态路径输入**下测得的。解析器返回的是**路径**，
> 调用方随后用另一次文件系统操作打开它——即 **check-then-use**。检查与打开之间的并发替换（文件内容、
> 目录组件被换成 junction、文件大小）**未防护、原探针也未测量**；修订探针 F 现已把该窗口实测出来
> （F-03/F-04/F-05/F-06），并在 §4.7 与 §12 给出解除条件。不得把上表读作“攻击已被缓解”。

通道计量：**控制通道 7,098 B（去）+ 7,997 B（回）= 15,095 B**，同期带外交付 **85,310,202 B** 媒体。
宿主峰值工作集 26.2 MB，Core 峰值 23.6 MB。签名密钥只存在于 Core，且**未**出现在任何结果 JSON
（探针只记录密钥长度）。**但引用本身不保密（R-002）**：正文是 Base64URL 的 JSON，`rel` 等字段
无密钥即可读出（实测 F-01），因此相对路径会随引用字符串暴露给持有者。

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
7. **原会话 lab 目录已被平台回收**：修订时按提交的种子重新生成 fixture，10/10 个 SHA-256 与已提交的
   `raw/fixtures.json` 完全一致（`raw/16-revision-fixture-reproducibility.log`）。A–E 的原始日志**未重跑**，
   仍为首次执行产物；修订新增的 probe F 在新的 lab 路径下运行（确切命令与 exit code 见 `raw/15-…log`）。

### 4.7 路线 A 的边界实测（修订新增：probe F，对应 Review R-001/R-002）

`probes/probe_f_boundary.py`，8/8 场景 PASS，exit 0；原始日志 `raw/15-probe-F-boundary.log`、
结果 `raw/probeF-result.json`。

| 场景 | 结果 | 测量 |
|---|---|---|
| F-01 token 正文无密钥可解 | PASS | 用无关密钥解出 `{"rel":"derived/asset.png","rid":"rid-asset","scope":"derived-read-only","exp":…,"mode":"read"}`；同一 token 用无关密钥验签失败 `REF_SIGNATURE_INVALID` → **完整性有、保密性无** |
| F-02 静态负向控制复核 | PASS | traversal / 绝对路径 / 域内 junction / scope 越权 / 写模式全部按静态输入被拒（与 A-09..A-15 一致） |
| F-03 检查→打开之间替换文件 | PASS（缺陷被证实） | 校验时 sha `5742503d…`，替换为 scope 外文件后打开读到 `c312ef5e…`（与 scope 外文件一致）→ `toctou_window_confirmed = true` |
| F-04 目录组件被换成 junction | PASS（缺陷被证实） | 校验时目录为真实目录、reparse 遍历通过；替换为指向 scope 外的 junction 后，同一路径读到 scope 外文件 |
| F-05 大小校验后被替换 | PASS（缺陷被证实） | 校验时 2,882,143 B（≤ 64 MiB），替换后实际 75,948,811 B；朴素读取实际读满 68,157,440 B（`> limit`） |
| F-06 等大小换内容 | PASS（判别性） | 换入文件与校验文件**字节数完全相同**（2,882,143 B）→ 仅凭大小复检无法发现；文件身份（`dev+inode`）改变可发现 |
| F-07 句柄绑定身份校验可拦截 | PASS（隔离对照） | 打开后 `os.fstat` 身份比对 → `FILE_IDENTITY_CHANGED`，拦截本次替换 |
| F-08 句柄绑定正常路径 | PASS（正向对照） | 未替换时读回 sha 与合法资源一致 |

结论（与 §12 一致）：**静态路径输入的拒绝已实测；检查→打开之间的竞态窗口已实测为“开着”；句柄绑定方向
在一个受控替换上被验证可拦截，但产品级保证仍为 `UNVERIFIED`**（对手可写 scope root/父目录/卷、
reparse 点在打开时刻替换、以其他方式取得同身份句柄等均未测）。

---

## 5. AC4 — 数据保护与生命周期

| 要求 | 结论 | 证据 |
|---|---|---|
| 只读 / 限域访问 | 静态路径输入下 `PASS`（探针级）；并发替换 `UNVERIFIED`（R-001） | A：scope class + 只读 + 包含性 + reparse 遍历（A-11/A-12/A-15）；C3-01 `ERROR_ACCESS_DENIED`、C3-02 `TypeError`；**F-03/F-04 证明检查→打开之间存在可被替换的窗口** |
| 不可从前端路径直接写源文件 | 探针级 `PASS`；OS 级 `UNVERIFIED` | token 类型无法表达 `user-source` scope（A-12 `REF_SCOPE_DENIED`）；但同用户进程仍可自行以可写方式打开文件——**ACL/完整性级别设计未验证** |
| 能力过期 / 撤销 | `PASS` | `REF_EXPIRED`（A-06）、`REF_REVOKED`（A-07，撤销前可用） |
| 取消 | 通道级 `PASS`；Core 工作线程语义 `UNVERIFIED` | B-09（读到 4 MiB 后 kill，生产者 exit 1，无残留） |
| 崩溃 / 重启 | 部分 `PASS`；Core 重启 `NOT_RUN` | B-11 生产者崩溃被判别；C2-01 section 在创建者退出后仍可读；C1-05 命名 section 随创建者消失 |
| 缓存清理 | `AS-IS` 有实现、探针 `NOT_RUN` | `application/maintenance/cleanup.py` 的 `CACHE_SAFE_PREFIXES=("cache/",)` 与 `tile-*.png` 清扫；本 Task 未跑清理探针 |
| 资源 ID 与 current/pinned Revision 绑定 | `PROPOSAL`；`NOT_RUN` | 见 §6.2 的设计要求；AS-IS revision 字段见 §2 |
| 断线后重新获取快照/引用 | `NOT_RUN` | Contract §7.2 已把它留给 runtime；本 Task 未运行任何断线场景 |
| 引用保密性（R-002） | **`FAIL`（作为保密假设）/ 已如实记录** | 引用正文可无密钥解码，相对路径可见（F-01）。若产品把该引用当作不泄漏路径的句柄使用，该假设不成立 |
| Secret / 任意绝对路径 / 源文件字节 / 模型权重不进入普通 DTO、事件或日志 | 原型 `PASS`，含两处需改进项 | 控制通道只传引用与类型化错误（15,095 B）；签名密钥只存在于 Core，未写入任何结果 JSON；**但（a）Core 批复把文件的绝对路径回给宿主，（b）引用正文本身包含相对路径**——产品实现应改为宿主侧资产 URL 与（如需要）服务端映射 ID/加密方案（PROPOSAL 改进项，见 §6.3、§12） |

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
| 引用越界读（**静态路径输入**） | 静态输入下已拒绝：词法 + 包含性 + reparse 遍历（实测 3 类拒绝，F-02 复核）；**这不等价于攻击被缓解** | 无（通道即数据，越界由打开者决定） | 无 | 无 |
| **检查→打开竞态（TOCTOU，R-001）** | **`UNVERIFIED`（窗口已实测为开）**：检查与调用方 `open()` 是两次独立文件操作；F-03 换文件、F-04 换目录组件为 junction、F-05 换大小、F-06 等大小换内容全部读到未校验内容 | 不适用（字节送达即消费，无路径再解析） | 不适用 | 不适用 |
| **引用保密性（R-002）** | **NONE**：正文可无密钥解码，相对路径可见（F-01）；不得把引用当作不泄漏路径的句柄 | 不适用 | 名字即泄漏 | 句柄值泄漏即能力 |
| 引用被重放 | 部分：有 `exp` 与撤销集；**跨重启的密钥轮换策略未测** | 不适用 | 不适用 | 句柄在关闭后失效（未单独测重放） |
| 机密性（同用户对手） | 引用不提供保密性；宿主最终读的是**文件**，同用户进程本来就能读该文件 → 机密性不来自引用 | 管道句柄同样只受 ACL 约束 | **已被攻陷**：任何同用户进程可读写 | **已被攻陷**：同用户可 `DuplicateHandle`（实测成功） |
| 完整性 | 宿主读后可自校验 sha（实测匹配）；但**校验与打开也可被竞态错配**（F-03：校验 sha 与实际读到不同）；写入路径不在通道内 | 需显式 framing 才能判断截断（实测 EOF 不足） | **无完整性保证**（实测被改写） | 同 C1 |
| 资源耗尽 | 受控拒绝（实测 0 字节、0 增长）；并发需配额度；**大小检查同样是先检查后打开**（F-05） | 受控拒绝 + 背压（实测）；需配最大并发 | 需在创建前限制尺寸（实测 `SECTION_LIMIT_EXCEEDED`） | 同 C1 |
| 崩溃/孤儿 | Core 崩溃后文件仍在（可重建缓存）；引用密钥轮换即全失效 | 生产者崩溃被判别；无孤儿内存 | 随创建者消失，无孤儿 | 宿主句柄持有期间内核对象存活 |
| 生命周期可预测性 | 高（读文件，无内核对象生命周期问题） | 高（关闭通道即结束） | 低 | 中（依赖句柄生命周期与撤销时机） |

**结论**：Windows 句柄/共享内存**不是**“安全性更强的通道”，它只是“拷贝更少的通道”，而且在同用户威胁下
并不比“同用户可直接读的文件”更安全。因此不应以“用句柄/共享内存”作为安全论证。路线 A 的优势是
**控制/数据分离与可校验的权限语义**，**不是**路径保密性；其检查→打开竞态必须在产品实现层单独解决。

### 6.3 PROPOSAL 设计要求（进入产品前的候选约束）

1. 引用类型必须携带 scope class、`resource_id`、失效时间、只读标记，并由 Core 在**解析时**重新校验；
   不接受任何形式的“前端传路径”。
2. 若采用 §4.1 的 proto，Core 批复**不得**把绝对路径交给前端；应由 host/Core 的资产协议以受限 URL 形式
   提供字节（本 Task 未测 Tauri 资产协议）。
3. **（R-001）** 解析结果不得以“裸路径”交给后续 `open` 作为安全保证：产品实现必须**先打开、再从同一句柄
   校验**（身份 + 大小 + 包含性），或直接以句柄/流交付；并补并发替换的负向探针（见 §8.2 S1-B11）。
4. **（R-002）** 引用**不是不透明的**，不得把“前端看不到路径”建立在签名之上。若产品要求路径/资源标识
   不泄漏，必须另设机制：Core 侧映射 ID（前端只见随机 ID，Core 查表解析）或加密载荷；该选择属于
   后续设计 Task，需用户决定（§8.2 S1-B12）。
5. 流式通道必须带显式长度 + 摘要 framing（B-10 证明 EOF 不足）。
6. 命名 section 不得用于承载不可信数据（C1-02 已证实默认可写）；若必须用共享内存，必须显式构建
   security descriptor 并把可写打开限制到指定消费者——**未测**。
7. 派生缓存与源文件/权重的 scope 必须分离；`user-source` scope 不得有任何实现。
8. Secret 不进入任何 DTO/事件/日志；本 Task 已按此执行（密钥只在 Core，结果 JSON 只记录密钥长度）。

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

**主通道：路线 A —— 受限资源引用（**签名、可解码**）+ Core 侧解析 + 带外读取。**

理由（全部有测量支撑）：控制通道零媒体字节（15 KB 控制 vs 85.3 MB 媒体）；无膨胀、无序列化成本；
宿主不必物化整份资源（读 60.77 MB 时 WS 增量 ≈0）；**静态路径输入下**权限/过期/撤销/只读/越界/重解析
逃逸全部为稳定类型化拒绝（F-02 复核）；与 AS-IS 的“Core 给文件 URI、QML 读文件”同构，迁移面最小。

**该推荐附带三项强制限定**（否则不成立）：

1. **（R-001）** 引用解析不得以裸路径 + 另一次 `open` 作为安全边界；必须先打开再从句柄校验
   （F-07 在隔离对照中证明该方向可拦截本次替换，F-08 证明合法资源仍可读），并补并发替换负向探针
   （S1-B11）。产品级保证仍为 `UNVERIFIED`。
2. **（R-002）** 引用**不保密**：相对路径随引用字符串可见（F-01）。若产品要求路径不泄漏，必须另设
   Core 侧映射 ID 或加密方案（S1-B12），并把该决定交用户。
3. 控制面**不得**把绝对路径回给前端（§6.3 第 2 条）。

**第二通道：路线 B —— 流式/分块字节通道，显式长度+摘要 framing。**
用于“不能给出文件路径”或需要显式背压/取消的场景。已实测：有界内存（60.77 MB 载荷 WS 增量 0.96 MB）、
背压真实（慢消费者 10.6× 变慢而生产者内存不变）、取消与崩溃可判别；且该路线**不引入路径再解析竞态**
（字节送达即消费），是 R-001 未决期间唯一不受该竞态影响的候选。

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
| **S1-B11** | **（R-001）检查→打开竞态（TOCTOU）的产品级防护** | **`UNVERIFIED`**：窗口已在探针中实测为开（F-03/F-04/F-05/F-06）；句柄绑定方向仅在隔离对照中拦截了本次替换（F-07/F-08） | 解除条件：①产品实现改为**打开后从句柄校验**——`open` 一次，用 `os.fstat`/`GetFileInformationByHandle` 校验文件身份与大小，包含性由句柄重新推导（Windows 上按需 `FILE_FLAG_OPEN_REPARSE_POINT` / `FILE_FLAG_BACKUP_SEMANTICS`），读取只用该句柄；②新增负向探针：在检查与打开之间并发替换文件内容、把目录组件换成 junction/符号链接、以及在**等大小**前提下换内容（F-06 已证明仅大小复检不够），全部必须类型化拒绝；③覆盖对手可写 scope root/父目录/卷的前提，并在目标打包/沙箱形态下复跑；④S1-B3 的 DACL/完整性级别同时生效 |
| **S1-B12** | **（R-002）引用不透明性 / 路径保密性** | **`UNVERIFIED`（当前为否）**：正文可无密钥解码，`rel` 等字段可见（F-01） | 解除条件：由用户决定是否需要保密；若需要，改为 Core 侧随机映射 ID（前端只见不透明 ID，Core 查表解析）或加密载荷，并新增探针证明：无密钥/无 Core 参与时无法从引用还原任何路径或资源标识；同时确认日志、错误与遥测中不泄漏映射表 |

### 8.3 进入产品的前置条件

任何选型进入产品 Contract/Runtime 前仍需：非作者独立 Review（本 Task 由 Codex 执行）、Codex 集成、
以及用户对 §7 的阈值决定。**在 S1-B11 与 S1-B12 解决之前，路线 A 不得被当作“安全边界已完成”的通道**；
若产品必须在此前推进，路线 B（流式，无路径再解析）是 R-001 竞态下唯一不受影响的候选。
本报告**不构成**产品集成批准，也不预选 Tauri command 形态或序列化库。

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

`UNVERIFIED`：**检查→打开竞态（TOCTOU）的产品级防护（R-001，S1-B11；窗口已实测为开，防护未测）**；
**引用的路径保密性（R-002，S1-B12；实测为“不保密”）**；源文件边界的 OS 级 ACL/完整性；
真实页压缩率下的字节量；低完整性/跨会话对手的拒绝；命名 section 的显式 security descriptor 方案；
`DuplicateHandle` 在非默认 DACL 下的行为。

`BLOCKED`：无。所有已设计实验均实际执行；未执行项均为范围或环境前提缺失（无 Tauri runtime、
无产品 Core 进程模型），而非失败。

---

## 10. 复现命令

```powershell
# 只读固定点核验
pwsh -NoProfile -File verification/M2-S1/probes/00_recon.ps1

# 原交付的 A–E 全套（日志保持不变，修订未重跑）
pwsh -NoProfile -File verification/M2-S1/probes/run_all.ps1 `
  | Tee-Object -FilePath verification/M2-S1/raw/00-run-all.log

# 修订新增：边界实测（probe F，独立命令，runner 未改动）
python verification/M2-S1/probes/probe_f_boundary.py --lab "$env:TEMP\m2s1-lab" `
  --out "$env:TEMP\m2s1-lab\probeF-result.json"

# 合成 fixture 的确定性复核（10/10 hash 应与 raw/fixtures.json 一致）
python verification/M2-S1/probes/make_fixtures.py --lab "$env:TEMP\m2s1-lab"
```

---

## 11. 结论与推荐（修订后）

- **路线 A（签名引用 + Core 解析 + 带外读取）** 仍是主通道候选：控制/数据分离、权限语义可校验、
  迁移面最小。**但**它当前**不提供路径保密性**，且其检查→打开竞态**未防护**；这两点分别由
  S1-B12 与 S1-B11 跟踪，未解决前不得作为“安全边界已完成”的通道。
- **路线 B（流式）** 为第二通道，且是 R-001 竞态下唯一不受影响的候选；必须带显式长度+摘要 framing。
- **路线 D（JSON/Base64）** 维持 Contract §10 的禁止：实测 1.33× 膨胀且接收端内存随资源线性增长。
- **C1 命名 section** 不推荐（无能力语义、默认可匿名写、随创建者销毁）；**C2** 仅在同用户对手被
  排除时可选（同用户复制实测成功）。

---

## 12. 修订记录：对 Codex Review R-001 / R-002 的逐项回应

Review 固定点：`origin/master:doc/reviews/M2-S1-4eaad68.md`（`f709e39`），`decision=changes_requested`，
`reviewed_head=4eaad684769a02035748b95186d478bbed926042`。本修订**不重写历史**：旧提交
`4eaad68`/`7766a2b` 保留，修订以新增 commit 交付。

### R-001（P1）check→open 竞态边界 — **已修订，边界标记为 `UNVERIFIED`**

| 项 | 处置 |
|---|---|
| 原表述 | §3.2「权限边界…全部拒绝」、§6.2「引用越界读 已缓解」、§8.1「越界/重解析逃逸全部为稳定类型化拒绝」 |
| 修订后表述 | 一律限定为**静态路径输入**；§4.1 增加 R-001 限定块；§6.2 新增「检查→打开竞态」行并标 `UNVERIFIED`；§5 的「只读/限域访问」行加入 F-03/F-04 反证；§8.1 增加强制限定 1；§8.2 新增 **S1-B11**（含四条解除条件）；§9.1 纳入 `UNVERIFIED` |
| 新增测量 | `probes/probe_f_boundary.py`：F-03 文件被替换后读到 scope 外内容；F-04 目录组件被换成 junction 后读到 scope 外树；F-05 大小校验后被替换，朴素读取读到 68,157,440 B（>`limit` 64 MiB）；F-06 等大小换内容 → 仅大小复检无法发现、文件身份可发现；F-07 打开后按句柄校验身份 → `FILE_IDENTITY_CHANGED` 拦截；F-08 正常路径仍读回合法 sha |
| 未做的事（诚实边界） | **没有**在产品实现中修防护；F-07/F-08 是隔离对照，不构成产品保证；对手可写 scope root/父目录/卷、打开时刻的 reparse 替换、以其他方式取得同身份句柄等仍未测 |
| 证据 | `raw/15-probe-F-boundary.log`（exit 0）、`raw/probeF-result.json`、`probes/m2s1_lab.py` 顶部与 `ScopedResourceResolver`/`read_file_bounded` 的 docstring 限定（**仅注释/docstring 变更**，行为未改，diff 见 `raw/08-revision-code-diff.log`） |

### R-002（P2）引用并非不透明 — **已修订，保密性标记为“无”**

| 项 | 处置 |
|---|---|
| 原表述 | §1/§3.1「不透明引用」；`m2s1_lab.py: mint_token` docstring 亦写 "opaque" |
| 修订后表述 | 统一改为「**签名的可解码引用**」；§1 摘要新增 R-002 说明；§3.1/§3.2 增加「引用保密性（R-002）」行（值 = `NONE`）；§4.1 通道计量段说明相对路径随引用可见；§5 增加「引用保密性」行（作为保密假设 = `FAIL`）；§6.2 新增「引用保密性」威胁行；§6.3 新增设计第 4 条；§8.1 增加强制限定 2；§8.2 新增 **S1-B12**（含解除条件） |
| 新增测量 | F-01：用无关密钥解出 `{"rel":"derived/asset.png","rid":"rid-asset","scope":"derived-read-only","exp":…,"mode":"read"}`，同时同一引用验签失败 `REF_SIGNATURE_INVALID` → **完整性有、保密性无** |
| 未做的事（诚实边界） | **没有**实现映射 ID 或加密方案；仅把它列为后续设计与验证条件（S1-B12），由用户决定是否需要 |
| 证据 | `raw/15-probe-F-boundary.log`、`raw/probeF-result.json`；`m2s1_lab.py` 的 `mint_token` docstring 更正（仅注释） |

### 修订带来的其它变更

- `probes/probe_f_boundary.py`（新增探针，8 场景）；`probes/m2s1_lab.py`（**仅 docstring/注释**，
  行为不变，diff 记录于 `raw/08-revision-code-diff.log`）。
- `raw/15-probe-F-boundary.log`、`raw/probeF-result.json`、`raw/16-revision-fixture-reproducibility.log`
  （原会话 lab 被回收后按提交种子重建 fixture，10/10 SHA-256 与 `raw/fixtures.json` 一致）、
  `raw/07-revision-script-hashes.log`、`raw/08-revision-code-diff.log`。
- **A–E 原始日志未重跑**，其命令与 exit code 保持首次执行值；`run_all.ps1` **未改动**（因此
  `raw/01-probe-script-hashes.log` 对 A–E 的脚本身份仍然成立）。
- 受影响文件（均属原授权写集合）：本报告、`doc/tasks/M2-S1.md`、`doc/handoffs/M2-S1-*.md`、
  `verification/M2-S1/**`。未改 `src/**`、`tests/**`、共享契约、AD-001、Plan/STATUS 或 Review。
