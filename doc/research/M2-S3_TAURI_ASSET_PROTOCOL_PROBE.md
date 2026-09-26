# M2-S3 — Tauri Asset Protocol Feasibility Probe

- Task：[M2-S3](../tasks/M2-S3.md)（`kind: research`，Owner=ZCode，非作者 Reviewer=DeepSeek Harness）
- 固定 base：`90c3e45962733799d43e3aefacf4fea99f662a2c`（master，M2-C2 集成收尾提交）
- 分支 / 工作区：`agent/zcode/M2-S3-tauri-asset-protocol-probe` / `G:/CODEX/New Manga.worktrees/M2-S3-zcode`
- 固定 Contract blob（1.1，M2-C2 修订后）：`fc35913801297ee1876ea395f9c5041a16226f20`
- 结论摘要：**S1-B1 = `PASS`（带适用边界）。** 在隔离的真实 Tauri 2 / WebView2 骨架中，自定义受限
  scheme（`http://m2res.localhost/m2id/<opaque-id>`）能够按 Contract 1.1 T5/T6 语义承载受限派生资源：
  WebView 侧只见不透明映射 ID 并成功解码渲染 PNG（含 11.5 MB 资产，SHA 一致）；未知/畸形/已撤销/已过期
  ID、user-source、词法与编码 traversal、绝对路径形态、junction 逃逸全部被**类型化拒绝**且错误体零泄漏；
  撤销后下一次请求即时 `REF_REVOKED`，已开始的消费不被中断，**未观察到协议/浏览器缓存绕过 resolve**。
  共 16 场景 16 PASS、两次运行逐项一致。**这不是产品实现、路线批准或 runtime 授权**（§7）。
- 全部证据、命令、exit code 与原始日志见 [`verification/M2-S3/`](../../verification/M2-S3/environment.md)。

> 标签约定（沿用 M2-S1/M2-S2）：`MEASURED` 本次实测；`PROPOSAL` 本 Task 原型；`UNVERIFIED`/`NOT_RUN`
> 未验证/未运行。本报告的一切数字来自**本机隔离探针**（真实 Tauri 2 + WebView2 153.0.4234.48 + 纯静态
> 前端），不代表产品 runtime 的行为。

---

## 1. 范围与方法

### 1.1 做了什么

针对 M2-S1 §8.2 的 S1-B1（`NOT_RUN`：在真实 Tauri 骨架中做一个最小 asset-protocol 探针并记录
权限/缓存/生命周期），在 `experiments/M2-S3/**` 构建了一个**独立的、真实的 Tauri 2 应用**（非模拟）：

- **Rust host 层**（`probe/src/main.rs`，~560 行）：内存映射表（M2-S2 `MappingIdAuthority` 的 Rust
  对应物）签发 256-bit 随机不透明 ID（43 字符 base64url）；`register_uri_scheme_protocol("m2res")`
  在请求时解析 `/m2id/<id>`，查表 → 撤销/过期/格式门 → 从 scope root 读取文件 → 返回字节；
  containment 在 **resolve 时**由 `canonicalize` 重新推导（issue 只记录 rel——junction 签发后目录
  逃逸正是 resolve 层要拦的，与 M2-S2 的 issue-facts/resolve-verification 分工一致）。
- **WebView 前端**（`ui/index.html`，纯静态无 npm）：真实 WebView2 网络栈中的 fetch 矩阵驱动器，
  自动执行 16 场景，经 Tauri command 写结果 JSON 后退出。
- **fixture**（`fixtures/gen_fixtures.py`，stdlib）：确定性 RGB 噪声 PNG（M2-S1/S2 同法、独立种子），
  scope 内为**独立副本**（不用硬链接——M2-S2 教训）；scope 外对抗树 + junction。
- 全部实验依赖与锁文件仅在 `experiments/M2-S3/probe/`（Cargo.lock 入库，`target/` 已 ignore）；
  根目录依赖、产品代码零触碰。

### 1.2 没有做什么（不得外推）

- 没有实现产品 IPC server、Python Core 进程、React consumer、产品 `src-tauri/**`。
- 没有访问真实用户库/凭据/模型缓存；fixture 全部合成（SHA 见 `raw/fixtures.json`）。
- 没有覆盖打包/沙箱（S1-B8）、DACL/完整性（S1-B3）、冷缓存（S1-B6）、产品 pytest。
- 没有把探针结果表述为产品安全保证；S1-B11 产品级防护仍为 `UNVERIFIED`（M2-S2 结论原样保留）。

### 1.3 环境（S3-AC1，详单见 [`environment.md`](../../verification/M2-S3/environment.md)）

| 项 | 值 |
|---|---|
| OS | Windows 11（NT 10.0.26200） |
| WebView2 Runtime | `153.0.4234.48`（Evergreen，HKLM） |
| Rust | `rustc/cargo 1.98.1`（stable-x86_64-pc-windows-msvc） |
| Node | `v24.15.0`（探针**未使用**——前端纯静态，`frontendDist` 直指目录） |
| Tauri | `tauri 2.11.6` / `tauri-build 2.6.3`（`wry 0.55.1`、`tao 0.35.3`；见 `experiments/M2-S3/probe/Cargo.lock`） |
| 页面源 | `http://tauri.localhost`（Windows 上 Tauri 2 的自定义 scheme 映射为 `http://<scheme>.localhost`） |

---

## 2. 协议形态选择（本 Task 明确的受限 protocol URL）

**选择：自定义 URI scheme `m2res`**（`register_uri_scheme_protocol`），WebView 请求形如
`http://m2res.localhost/m2id/<43-char-opaque-id>`，Rust handler 查表返回字节或类型化错误。

**为什么不是 Tauri 内置 `asset:` 协议（`convertFileSrc`）**：内置协议的 URL 直接携带 **OS 绝对路径**
（`asset://localhost/<url-encoded-path>`，由 `assetProtocol.scope` 白名单控制），即 WebView 侧必须
持有并传输路径——这与 Contract 1.1 §10.1 T5.1（"React/WebView must never touch any OS path"）在
设计层面直接冲突。因此本 Task 的受限形态 = 自定义 scheme + 映射 ID；内置协议不进入探针矩阵
（`NOT_RUN`，理由如上——它是被 T5 排除，不是被实测否定）。`tauri.conf.json` 中 `assetProtocol`
显式 `enable: false`。

**与 Contract 语义的对应**：

| Contract 条款 | 探针实现 |
|---|---|
| T5.4/§10.2 WebView 只见不透明映射 ID | URL 仅含随机 ID；表（rel/TTL/revoked）只在 Rust host |
| §10.2 resolve 时类型化拒绝 | 格式门 → 表查询 → 撤销 → 过期 → containment（canonicalize）→ 读文件 |
| T6 撤销立即生效（next resolve） | `revoke` command 后下一次请求 `410 REF_REVOKED` |
| T6 已打开消费不强制中断 | revoke 发生于首块之后，在途读取完整结束（L-02；形态限制见 §5） |
| §10.2 错误不泄漏 | 错误体恒为 `{"code":"<稳定码>"}`；两轮结果全文泄漏扫描 0 命中 |

---

## 3. 实测结果矩阵（`MEASURED`，两次运行一致）

`probe_s2` 风格的 fetch 矩阵在真实 WebView2 中执行；16 场景 **16 PASS / 0 FAIL / 0 BLOCKED**，
运行 exit 0。原始 JSON：`raw/probe-results-first.json`、`raw/probe-results-repeat.json`；
命令与 exit code：[`raw/00-run-log.md`](../../verification/M2-S3/raw/00-run-log.md)。

### 3.1 正向（S3-AC2）

| 场景 | 结果 | 测量 |
|---|---|---|
| P-01 合法 ID fetch | PASS | `200`、`image/png`、2,882,143 B，SHA `50f5a4cc…` 与 fixture 一致；JS 可见 URL 仅含 ID |
| P-02 `<img>` 渲染 | PASS | WebView 解码渲染成功（`naturalWidth 800 × 1200`）——协议字节可真实用于图像管线 |
| P-03 大资产 fetch | PASS | 11,525,983 B 完整交付（56 ms），SHA 一致 |
| P-04 WebView 可见性 | PASS | 页面源 `http://tauri.localhost`；JS 可达材料（URL/响应头/错误体）只含不透明 ID |

### 3.2 负向权限矩阵（S3-AC3，全部类型化拒绝且零泄漏）

| 场景 | 攻击 | 拒绝 |
|---|---|---|
| N-01 未知 ID（格式合法、表中不存在） | 枚举猜测形态 | `404 REF_UNKNOWN_ID` |
| N-02 畸形 ID | 非 ID 文本 | `400 REF_MALFORMED` |
| N-03 已撤销 ID | revoke 后 fetch | `410 REF_REVOKED` |
| N-04 已过期 ID | TTL 2.5 s 到期后 fetch | `410 REF_EXPIRED` |
| N-05 user-source fixture | host 以该 fixture 的**绝对路径**直接判定 scope 越界 | host 守卫 `REF_OUT_OF_SCOPE`（`sign_all` 显式调用 `ensure_inside_scope`；对绝对路径无需 canonicalize 即可判定）。注意：`issue()` 本身不做 containment（见 §2），因此这是专门的 host 守卫场景而非 issue 层通用防线；WebView 侧无对应 ID 可请求（`webview_reachable: false`） |
| N-06 词法 traversal | `/m2id/../outside/outside_secret.png`（**fetch 前被浏览器 URL 解析器归一化**为 `/m2id/outside/outside_secret.png`——DSH F-03 更正：抵达 handler 的已是归一化形态） | `400 REF_MALFORMED`（归一化后末段仍非合法 ID 格式，格式门先于表查询）；真正穿透原始 `..` 的是编码形态 N-07 |
| N-07 编码 traversal | `/m2id/%2E%2E%2Foutside%2F…` | `400 REF_MALFORMED`（percent-decode 后仍非 ID） |
| N-08 路径参数/绝对路径段 | `/file?path=…`、`/abs/C:\…` | `400 REF_MALFORMED`（协议只接受 `/m2id/<id>`） |
| N-09 junction 逃逸 | ID 映射到 `linkj/nested.png`（scope 内 junction → scope 外） | `403 REF_OUT_OF_SCOPE`（resolve 时 canonicalize containment 拦截） |

### 3.3 缓存与生命周期（S3-AC4）

| 场景 | 结果 | 测量 |
|---|---|---|
| L-01 重复读取 | PASS | 两次读取字节与 SHA 一致（15/16 ms） |
| L-02 在途消费 vs 撤销 | PASS（形态限制见 §5） | 首块后 revoke，读取继续至完整 11,525,983 B、SHA 一致——已开始的消费不被撤销中断（T6 carve-out） |
| L-03 缓存绕过对照 | PASS（**未观察到绕过**） | 无 `Cache-Control`（bare）与 `no-store`（ctrl）两组：fetch#1 `200` → revoke → fetch#2 均 `410 REF_REVOKED`——WebView2 未用缓存的旧字节替代 resolve。机制解释：200 响应无 `Last-Modified`/`ETag`，HTTP 启发式缓存无依据；错误响应恒 `no-store`。**单宿主单样本观察**，见 §5 限制 |

### 3.4 一手官方文档核对（S3-AC5）

- Tauri 2 自定义协议：`register_uri_scheme_protocol`（Windows 上映射为 `http://<scheme>.localhost`，
  需自行返回完整 `http::Response`；本探针实测 CORS 需 `Access-Control-Allow-Origin`，实测页面源为
  `http://tauri.localhost`）。
- 内置资产协议：`app.security.assetProtocol`（`convertFileSrc`）——路径承载形态，见 §2 排除理由。
- 以上行为均以本探针实测值为准（文档核对 + 实测一致；实测细节记录于结果 JSON 的
  `page_origin`/`webview_user_agent` 与场景 observed）。

---

## 4. AC 对照（S3-AC1..AC6）

| AC | 结论 | 证据 |
|---|---|---|
| S3-AC1 固定基线与实验环境 | **PASS** | `verification/M2-S3/baseline-selfcheck.md`、`environment.md`（WebView2/Rust/Node/Tauri 精确版本）；依赖与锁文件仅在 `experiments/M2-S3/probe/` |
| S3-AC2 真实 asset protocol 路径 | **PASS** | §3.1 P-01..P-04；`raw/probe-results-*.json` |
| S3-AC3 负向权限矩阵 | **PASS** | §3.2 N-01..N-09（reparse/junction 平台支持实测；symlink 未构造——junction 已覆盖 reparse 逃逸类，`NOT_RUN` 注明）；泄漏扫描 `raw/leakage-scan.json`：host 侧零泄漏（2 个词表命中为探针自编攻击 URL——N-06/N-08 场景输入，已分类） |
| S3-AC4 缓存与引用生命周期 | **PASS（限制如实标注）** | §3.3 L-01..L-03；T6 逐条对照：撤销→next resolve 拒绝 ✓、在途不中断 ✓（形态限制）、缓存未绕过 resolve ✓（单样本观察） |
| S3-AC5 可复核结论与交接 | **PASS** | 本报告（S1-B1=PASS + 边界）+ `raw/00-run-log.md`（命令/exit/缺陷记录）+ fixture SHA + Handoff |
| S3-AC6 范围与恢复性 | **PASS** | `git diff --name-status 90c3e459..HEAD` 仅授权路径、`git diff --check` 干净（`raw/scope.log`，随 Handoff 提交入库）；产品路径零触碰 |
| 产品 tests / IPC runtime | NOT_RUN（范围要求） | 无产品实现 |

---

## 5. 限制与 `NOT_RUN`（必须与 PASS 一起引用）

1. **单宿主、单 WebView2 版本**（153.0.4234.48）：缓存行为（L-03）是单样本观察 + 机制解释
   （无 validator 头 → 无启发式缓存依据），不是跨版本保证。runtime Task 应保留响应头策略
   （`no-store`）作为防线而非依赖"默认不缓存"。
2. **在途撤销窗口未真正构造**（L-02 `chunks: 1`）：handler 以一次性 body 返回（`Vec<u8>`），
   WebView 一次收齐——revoke 落地时"在途"已结束。T6 carve-out 在此形态下退化为"已消费不受撤销影响
   + 缓存不绕过"；**真流式（分块 body）的在途窗口属 runtime 实现形态，`NOT_RUN`**。
3. **Rust 侧模拟表**：映射表/撤销/TTL 由探针 Rust 层模拟（对应 M2-S2 Python 原型），无产品 Core
   进程、无跨进程 IPC、无 Core 重启/持久化（S1-B5 `NOT_RUN`）。
4. **无产品安全边界**：TOCTOU 句柄语义仅以 resolve-time containment 简化对应（S1-B11 产品级防护
   仍 `UNVERIFIED`，M2-S2 结论不变）；DACL/完整性（S1-B3）、打包/沙箱（S1-B8）未覆盖。
5. `NOT_RUN` 清单：Tauri 内置 `asset:` 协议实测（被 T5 排除，§2）；symlink 目录逃逸（junction 已覆盖
   同类 reparse 逃逸；开发者模式特权未在本 Task 验证）；冷缓存 S1-B6；MSIX/AppContainer 复跑
   S1-B8；React consumer 集成形态（本探针前端为纯静态页）；产品 pytest/IPC runtime（范围）。
6. **BLOCKED**：无。所有设计场景实际执行。

---

## 6. S1-B1 结论

**`PASS`**——M2-S1 §8.2 S1-B1 的解除条件（"在真实 Tauri 骨架中做一个最小 asset-protocol 探针并记录
权限/缓存/生命周期"）已达成：真实 Tauri 2/WebView2 骨架 ✓；最小 asset-protocol 探针 ✓（受限自定义
scheme + 映射 ID 形态）；权限（9 类类型化拒绝 + 零泄漏）、缓存（绕过对照）、生命周期（TTL/撤销/在途）
全部实测记录 ✓。

**适用边界（不随 PASS 被引用则无效）**：结论限于本探针形态——单宿主、Rust 模拟表、一次性 body、
非打包运行。它回答的是"asset protocol 能否承载受限派生资源"的可行性（能），**不回答**产品通道选型
（M2-S1 §8.1 路线 A/B 条件性建议仍开放）、不构成产品实现授权、不关闭 S1-B3/S1-B6/S1-B8/S1-B5。

**对 runtime 路线的影响**：若未来 runtime Task 选择自定义 scheme 资产通道，本探针给出三条可直接
复用的工程事实——①自定义 scheme 在 Windows/WebView2 走 `http://<scheme>.localhost` 且需 CORS 头；
②错误面可用稳定错误码 JSON（`{"code":…}`）承载且默认不缓存；③`no-store` + 无 validator 头的组合
在实测中使撤销语义不被缓存绕过。

---

## 7. 复现命令

```powershell
# fixtures + icon（确定性，可重入）
python experiments/M2-S3/fixtures/gen_fixtures.py

# 构建（依赖与锁文件仅在 experiments/M2-S3/probe/）
cd experiments/M2-S3/probe; cargo build --release

# 运行（窗口自动执行 fetch 矩阵并退出；结果与日志写 %TEMP%）
$env:M2S3_LAB="$env:TEMP\m2s3-lab"; $env:M2S3_PROBE_OUT="$env:TEMP\m2s3-probe-results.json"
$env:M2S3_PROBE_LOG="$env:TEMP\m2s3-probe.log"; $env:WEBVIEW2_USER_DATA_FOLDER="$env:TEMP\m2s3-webview2-udd"
.\target\release\m2s3-probe.exe   # exit 0；重复运行结果一致（16/16）
```

本报告不构成产品集成批准，不预选 Tauri command 形态或序列化库，不授权大媒体 runtime 实现。
