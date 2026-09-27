# M2-S2 — Resource Channel Security Verification Spike

- Task：[M2-S2](../tasks/M2-S2.md)（`kind: research`，Owner=ZCode，非作者 Reviewer=Antigravity）
- 固定 base：`67c3d56ea77acd5b214877509bbcd1cffe5890f7`（`master`，M2-S1 集成收尾提交）
- 分支 / 工作区：`agent/zcode/M2-S2-resource-channel-security` / `G:/CODEX/New Manga.worktrees/M2-S2-zcode`
- 固定 M2-C1 Contract blob：`4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3`（本分支与 base 一致，未改动）
- 结论摘要：**在隔离原型层（Python/Win32，非产品代码），open-then-verify-from-handle 参考解析器
  对全部 12 个负向攻击场景给出类型化拒绝，8 个正向/静态对照全部 PASS；Core 侧随机映射 ID 原型
  在穷举式分析（编解码、哈希字典、5,225 次猜测、近邻变换）下无可还原路径/资源标识，错误、日志与
  遥测面零映射表泄漏，过期/撤销/滑动续期全部类型化。** 共 24 场景 PASS、0 FAIL、0 BLOCKED，
  两次连续运行逐场景一致（`raw/09-repeat-consistency.json`）。
- 这**不构成**产品安全保证：本 Task 无产品 IPC runtime、无 Tauri command、无 React consumer；
  S1-B11 的"目标打包/沙箱复跑"（依赖 S1-B8）与"DACL/完整性级别"（依赖 S1-B3）保持 `NOT_RUN`；
  映射 ID 的不透明性证明是**归纳性证据**（见 §6、§8）。
- 全部证据、探针与原始日志见 [`verification/M2-S2/`](../../verification/M2-S2/baseline-selfcheck.md)。

> 标签约定（沿用 M2-S1）：`MEASURED` 本次实测；`PROPOSAL` 本 Task 原型（**不是**产品决定）；
> `UNVERIFIED`/`NOT_RUN` 未验证/未运行。一切数字来自 **Python↔Python 单机探针**，不代表
> Tauri/Rust、WebView、React 或产品 IPC runtime 的行为。

---

## 1. 范围与方法

### 1.1 本 Task 做了什么

针对 M2-S1 §8.2 的两个安全 blocker，在隔离原型层关闭其验证缺口（需求源：[M2-S1 §7 阈值裁决]
(`../../verification/M2-S1/product-thresholds-ruling-67c3d56.md`)，该文档只读，本分支经
`git show 7671f0c1` 引用）：

1. **S1-B11（TOCTOU）**：实现 open-then-verify-from-handle 参考解析器
   `HandleVerifiedResolver`（解除条件①），并按解除条件②构建系统性负向探针矩阵（T-01P..T-21），
   覆盖检查与打开之间的并发内容替换（小/大量级）、目录组件换 junction/符号链接、**等大小**换内容
   （文件替换与原地写两种形态）、对手可写 scope root 与父目录场景；每次攻击类型化拒绝，正向对照
   逐场景复验合法资源可读且 sha 一致。
2. **S1-B12（引用不透明性）**：按裁决 T5.4（分层信任模型，WebView 层引用 = 不透明映射 ID）实现
   Core 侧随机映射 ID 参考原型 `MappingIdAuthority`（签发/查表/滑动续期/过期撤销），并以
   M-01..M-08 探针证明：无 Core 参与时无法从 ID 还原路径或资源标识（编解码、哈希字典、枚举、
   近邻变换）、错误/日志/遥测输出不含映射表条目、撤销后类型化拒绝。

### 1.2 本 Task 没有做什么（不得外推）

- 没有创建产品 IPC server/runtime、Tauri command、React consumer、QML、持久化写者。
- 没有改动 `src/**`、`tests/**`、`packaging/**`、`src-tauri/**`、依赖、Schema、
  `doc/contracts/**`、AD-001、M2-S1 任何工件、治理导航或其他 Task。
- 没有访问真实用户漫画库、源文件、Managed Copy、凭据或模型缓存；fixture 全部为
  `%TEMP%\m2s2-lab` 下按固定种子生成的确定性 RGB 噪声 PNG（方法与 M2-S1 `make_fixtures.py`
  相同，种子不同）。
- 没有在 MSIX/AppContainer 打包形态、DACL/完整性级别模型、真实 Tauri asset protocol 下复跑。

### 1.3 环境与复现

| 项 | 值 |
|---|---|
| 主机 | Windows NT 10.0.26200.0（HOME-MY）、AMD64 |
| Python | 3.14.6（`C:\Python314\python.exe`，标准库 only） |
| shell | PowerShell（`pwsh -NoProfile`）；探针进程内单机 |
| 脚本身份 | `raw/01-script-hashes.log`（sha256，6 个脚本） |
| 环境 | `raw/02-environment.log`；worktree/git 基线见 [`baseline-selfcheck.md`](../../verification/M2-S2/baseline-selfcheck.md) |

```powershell
pwsh -NoProfile -File verification/M2-S2/probes/run_all.ps1
# 权威转录：raw/00-run-all.log（每步带 exit code；重复运行一致性：raw/09-repeat-consistency.json）
```

### 1.4 合成 fixture（确定性）

| fixture | 尺寸 | SHA-256 | 用途 |
|---|---:|---|---|
| `small_page_800x1200` | 2,882,143 | `d7e589cb…44bbfd3` | 主资产（绝大多数场景） |
| `typical_page_1600x2400` | 11,525,983 | `92781dc9…a97d5a6793` | 较大正向资产、超限拒绝演示、scope 外替换源 |

`media_limit_bytes = 64 MiB`（与 M2-S1 对齐）；`toctou_limit_bytes = 8 MiB`（**探针配置**，
非产品阈值——用它演示 `MEDIA_TOO_LARGE_BY_HANDLE` 的类型化拒绝路径）。两者都不是产品阈值；
产品尺寸预算由阈值裁决 T1（256 MiB 承诺线）约束，归 runtime Task 验收。

**威胁布局**：`<lab>/toctou/scope` 为 scope root（对手可写——攻击线程与解析器同用户同完整性
级别，即 M2-S1 §6.1 对手 2）；`<lab>/toctou/outside` 为对手控制的 scope 外树（替换源、junction/
symlink 目标、等大小变体、镜像树）。

### 1.5 关键实现事实（探针方法论）

- **确定性同步点**：每个负向场景的攻击在独立线程上运行，用 `threading.Event` 握手挂在解析器的
  `before_open` / `after_open_before_verify` / `during_read` 三个钩子上，交替顺序固定，
  不依赖时序竞速（Task 风险项要求的"事件/重试上限"以 Event 超时 30 s 实现，实际未触发）。
- **独立副本而非硬链接**：scope 内资产一律 `copyfile` 自 fixture。开发过程中曾用硬链接，发现
  T-16..T-18 的内容写攻击会**穿透硬链接污染共享 fixture 本体**（探针自身缺陷，已修复并重跑；
  修复后 fixture SHA 与 `raw/fixtures.json` 清单一致）。这一点本身是对 M2-S1 F-06 系列探针
  方法的强化记录。
- **校验顺序**（解析器内固定）：token 层（结构→签名→过期→撤销→scope→mode→词法→预打开
  reparse walk）→ open 一次 → **containment（从句柄 `GetFinalPathNameByHandle` 推导）→
  身份（volume serial + file index）→ 大小（签发时大小，再探针上限）→ 句柄 reparse tag** →
  仅经该句柄读取 → 内容 SHA-256 对照签发值 → 读后身份复核。

---

## 2. AC 对照（S2-AC1..AC6）

| AC | 结论 | 证据 |
|---|---|---|
| S2-AC1 范围与基线 | **PASS** | `verification/M2-S2/baseline-selfcheck.md`：toplevel/git-dir/common-dir/HEAD=67c3d56e/分支/干净工作区/Contract blob `4b503a17…` 全部核对一致；G: 主工作区未触碰 |
| S2-AC2 S1-B11 参考解析器 | **PASS（PROPOSAL 级原型）** | `probes/m2s2_lab.py::HandleVerifiedResolver`：open 一次，containment+identity+size 从句柄校验，读取只用该句柄；docstring 明确边界与 `UNVERIFIED` 保留（§3） |
| S2-AC3 S1-B11 负向探针 | **PASS（24 场景中 16 个 TOCTOU 场景全 PASS）** | `probes/probe_s2_toctou.py` T-01P..T-21（§4）；命令/输入 hash/exit code/结果入 `raw/`（§4.3） |
| S2-AC4 S1-B12 映射 ID 原型 | **PASS（8 个场景全 PASS，归纳性证明）** | `probes/m2s2_lab.py::MappingIdAuthority` + `probes/probe_s2_mapping.py` M-01..M-08（§5） |
| S2-AC5 报告与证据 | **PASS（本文件）** | §6 逐条对照解除条件；§7 NOT_RUN/UNVERIFIED 清单含 S1-B11③打包复跑与④DACL |
| S2-AC6 范围与交接 | **PASS** | 交付 diff 与 `git diff --check` 见 Handoff（`doc/handoffs/M2-S2-*.md`）；产品代码/依赖/Schema/共享 Contract 零改动 |

---

## 3. S1-B11 解除条件①：open-then-verify-from-handle 参考解析器（`PROPOSAL`）

`verification/M2-S2/probes/m2s2_lab.py` 的 `HandleVerifiedResolver`（研究仪器，非产品代码）：

1. **签发（Core 侧）**：词法校验 rel 后打开目标文件一次，把 (volume serial, file index)、大小、
   SHA-256 作为 issue-time 事实签入引用（`m2s2.<b64url(json)>.<b64url(hmac)>`，M2-S1 路线 A
   同族扩展）。**签发时刻内容可信是 digest 层的信任前提**（见 §7 限制）。
2. **解析（open-then-verify）**：`CreateFileW(GENERIC_READ, share, FILE_FLAG_BACKUP_SEMANTICS)`
   打开**一次**；从**该句柄**依次校验 containment（`GetFinalPathNameByHandle` + 归一化前缀
   比较，路径级逃逸）→ 身份 → 大小 → reparse tag；读取**只用该句柄**（`ReadFile` 循环）；
   读毕同句柄 digest 对照；读后身份复核。
3. **两种共享模式**（产品取舍的原型化）：
   - **窄共享（默认，`FILE_SHARE_READ` only）**：预持写句柄的对手使 open 直接
     fail-closed（`OPEN_FAILED_SHARING_VIOLATION`，T-21）；句柄持有期间任何新写打开被内核以
     sharing violation 拒绝（T-19）；文件不可被 rename/replace（无 `FILE_SHARE_DELETE`）。
     代价：句柄持有期间该文件对其他写者不可用（可用性问题，产品 runtime 决策）。
   - **宽共享（`share_write=True`，CRT `open()` 对齐 M2-S1 probe F 现实）**：预持写句柄的对手
     可继续写——此时**签发时 digest 层承担防线**（T-16/T-18 拦截等大小写，T-17 拦截扩写）。
4. **预打开 reparse walk** 保留为早期拒绝层（与 M2-S1 A-15/F-02 的静态策略对齐）；它自身有
   check-then-use 窗口，**权威防线在句柄层**（T-13/14/15/20 由句柄 containment 拦截）。

错误码（稳定选择器，全部类型化）：`REF_MALFORMED`、`REF_SIGNATURE_INVALID`、`REF_EXPIRED`、
`REF_REVOKED`、`REF_SCOPE_DENIED`、`REF_READ_ONLY`、`REF_OUT_OF_SCOPE`（词法/绝对/句柄
containment）、`REF_REPARSE_POINT`、`REF_NOT_FOUND`、`OPEN_FAILED_SHARING_VIOLATION`、
`FILE_IDENTITY_CHANGED`、`FILE_SIZE_CHANGED`、`MEDIA_TOO_LARGE_BY_HANDLE`、
`CONTENT_DIGEST_MISMATCH`。

---

## 4. S1-B11 解除条件②③：负向探针矩阵（`MEASURED`）

`probe_s2_toctou.py`，16 场景：**16 PASS / 0 FAIL / 0 BLOCKED**，exit 0
（`raw/04-toctou-first.log`、`raw/toctou-result.json`）。每个负向场景内置 **restore check**：
攻击后恢复合法文件并重新签发/解析，必须读回 fixture 原 sha——场景内正向对照。

### 4.1 正向与静态对照

| 场景 | 结果 | 测量 |
|---|---|---|
| T-01P 合法小资产 | PASS | open→verify→read 全链路，sha 与 fixture 一致（2,882,143 B） |
| T-02P 合法较大资产 | PASS | 11,525,983 B 在 64 MiB 探针上限内完整交付 |
| T-03P 超限类型化拒绝 | PASS | 8 MiB 探针上限下 `MEDIA_TOO_LARGE_BY_HANDLE`，字节读取前拦截 |
| T-04P 静态负向复核 | PASS | 词法 `../`、绝对路径、scope 内 junction（`REF_REPARSE_POINT`）、`user-source`（`REF_SCOPE_DENIED`）、写模式（`REF_READ_ONLY`）——静态路径输入下早期层与 M2-S1 A-09..A-15/F-02 对齐 |

### 4.2 负向矩阵（检查→打开窗口 + 句柄期窗口；全部确定性 Event 同步）

| 场景 | 攻击 | 同步点 | 拒绝码（期望=实测） |
|---|---|---|---|
| T-10 | 检查→打开之间替换文件（scope 外小文件副本） | before_open | `FILE_IDENTITY_CHANGED` |
| T-11 | 检查→打开之间替换为大量级文件（11.5 MB） | before_open | `FILE_IDENTITY_CHANGED`（身份先于大小） |
| T-12 | 检查→打开之间**等大小**替换（F-06 形态） | before_open | `FILE_IDENTITY_CHANGED`（仅大小复检不可见，身份可见） |
| T-13 | 目录组件 `derived/inner` 换 **junction**→scope 外 | before_open | `REF_OUT_OF_SCOPE`（句柄 containment） |
| T-14 | **scope root 整体** rename + junction→镜像树（对手可写父目录） | before_open | `REF_OUT_OF_SCOPE`（句柄 containment） |
| T-15 | 父目录组件 `derived/sub` 换 junction→scope 外 | before_open | `REF_OUT_OF_SCOPE`（句柄 containment） |
| T-20 | 目录组件换**符号链接**→scope 外 | before_open | `REF_OUT_OF_SCOPE`（本机 symlink 特权可用，实测无 BLOCKED） |
| T-16 | 对手预持写句柄，open 后**等大小原地改写** | after_open_before_verify | `CONTENT_DIGEST_MISMATCH`（宽共享模式） |
| T-17 | 对手预持写句柄，open 后扩写越过 EOF | after_open_before_verify | `FILE_SIZE_CHANGED`（宽共享模式） |
| T-18 | 读取进行中原地改写后续块 | during_read | `CONTENT_DIGEST_MISMATCH`（宽共享模式） |
| T-19 | 解析器持句柄期间对手新开写句柄 | after_open_before_verify | 攻击被 OS 拒绝（`ERROR_SHARING_VIOLATION` 32）+ 正读回合法内容 |
| T-21 | 对手预持写句柄（窄共享默认模式） | before_open* | `OPEN_FAILED_SHARING_VIOLATION`（fail-closed，0 字节） |

*T-21 的钩子实际未触发：open 在 before_open 前失败。

### 4.3 原始证据

- 权威转录（含每步 exit code 与 shell 头）：`raw/00-run-all.log`——`probe_s2_toctou.py` 首轮与
  复跑均 **exit 0**；`make_fixtures.py` 均与已提交 fixture hash 一致（`raw/03/06-*.log`）。
- 逐场景 JSON：`raw/toctou-result.json`（含 expected/actual 拒绝码、攻击线程 outcome、
  restore check、共享模式标注）；脚本 sha256：`raw/01-script-hashes.log`。
- 输入 hash：fixture SHA-256 记录于 `raw/03-make-fixtures.log` 与结果 JSON 的
  `small_fixture_sha256` / `typical_fixture_sha256` 字段。

---

## 5. S1-B12：映射 ID 原型与探针（`MEASURED` + 归纳边界）

`MappingIdAuthority`（`PROPOSAL`，非产品组件）：WebView 可见引用 = `m2id.v1.<token_urlsafe(24)>`
（192 bit 随机，`secrets` 模块）；Core 内表映射 ID → (scope, rel, rid, expires_at, revoked)。
T6 语义：滑动续期 `touch()`、立即撤销 `revoke()`、过期/撤销/未知全部类型化。
`resource_id` 与 rel 一样被视为**不得从引用面还原的资源标识**（T5.4 第 4 点从严执行）。

`probe_s2_mapping.py`，8 场景：**8 PASS / 0 FAIL / 0 BLOCKED**，exit 0
（`raw/05-mapping-first.log`、`raw/mapping-result.json`）。

| 场景 | 结果 | 测量 |
|---|---|---|
| M-01 签发/解析正向 | PASS | Core 受信调用方查表还原 (scope, rel, rid) 正确 |
| M-02 格式分析 | PASS | 5 个映射路径的 ID：长度恒定；同路径两次签发 ID 不同（不可链接）；ID 及其 b64url/b64std/base32/hex/raw 解码视图均不含任何路径片段；ID 段间无有意义公共前缀 |
| M-03 无 Core 参与还原 | PASS | 对手持有全部 ID：子串匹配、五类编解码、md5/sha1/sha256/sha512（rel/反斜杠 rel/文件名/rid 的 hex+大写+b64 共 48 组）全部无还原；recovered=0 |
| M-04 枚举与猜测 | PASS | 5,000 随机猜测 + 近邻变换（尾字符替换/截断/追加）共 5,225 次 → 全部 `REF_UNKNOWN_ID`，错误形态一致（无区分近失的 oracle）；键空间 192 bit |
| M-05 错误/日志/遥测零泄漏 | PASS | 未知/过期/撤销/写模式错误 + 全部日志行与遥测事件（JSON 逐条扫描）不含任何 rel、路径段、文件名 stem、rid（扫描词表含全部映射路径组件）；错误面只出稳定码 |
| M-06 过期类型化 | PASS | 到期后 `REF_EXPIRED`；到期前可解析 |
| M-07 撤销类型化 | PASS | 撤销前可解析；撤销后 `REF_REVOKED`（下次解析立即生效，对应 T6） |
| M-08 滑动续期 | PASS | `touch()` 重置 TTL；闲置后 `REF_EXPIRED` |

**证明边界（必须与 PASS 一起引用）**：M-02..M-05 的"无法还原"是**归纳性证据**——一个有限但
覆盖常见攻击面（编解码、哈希字典、枚举、近邻）的分析空间，对 192 bit 随机 ID 归零；它不是
密码学证明。映射表保护 Core 进程内存、崩溃转储或被攻陷 host 超出范围（T5 将 host 定为可信层）。

---

## 6. 与 M2-S1 §8.2 解除条件的逐条对照

| Blocker | 解除条件 | 本 Task 结果 |
|---|---|---|
| S1-B11 | ① 产品实现改为打开后从句柄校验（身份+大小，包含性由句柄重新推导；按需 `FILE_FLAG_OPEN_REPARSE_POINT`/`FILE_FLAG_BACKUP_SEMANTICS`），读取只用该句柄 | **原型层达成**：`HandleVerifiedResolver` 实现该形态（`FILE_FLAG_BACKUP_SEMANTICS` 已用；`FILE_FLAG_OPEN_REPARSE_POINT` 以预打开 walk + 句柄 reparse tag 等价覆盖）；T-01P..T-21 全 PASS。产品级实现与验收归属 runtime Task，`UNVERIFIED` 保留 |
| S1-B11 | ② 新增负向探针：并发替换文件内容（大/小量级）、目录组件换 junction/符号链接、等大小换内容，全部类型化拒绝 | **达成**：T-10/T-11（小/大）、T-13/T-15（junction）、T-20（symlink，环境可用）、T-12（等大小替换）、T-16/T-17/T-18（等大小原地写/扩写/读中写）全部类型化拒绝；正向对照逐场景 PASS |
| S1-B11 | ③ 覆盖对手可写 scope root/父目录/卷前提，并在目标打包/沙箱形态下复跑 | **部分达成**：对手可写 scope root（全部场景的 scope 即同用户可写目录）与父目录（T-14 scope root 整体替换、T-15 父组件替换）已覆盖；同卷对手（hardlink/copy 源均同卷）。**"目标打包/沙箱形态复跑" NOT_RUN**（依赖 S1-B8） |
| S1-B11 | ④ S1-B3 的 DACL/完整性级别同时生效 | **NOT_RUN**（依赖 S1-B3，未在本 Task 范围） |
| S1-B12 | 由用户决定是否需要保密 | **已由裁决 T5.4 回答**：需要（仅对 WebView 层），方案选定为 Core 侧映射 ID；加密载荷选项关闭 |
| S1-B12 | 若需要，改为 Core 侧随机映射 ID（前端只见不透明 ID，Core 查表解析）或加密载荷 | **原型层达成**：`MappingIdAuthority`（192 bit 随机 ID，表仅 Core 侧） |
| S1-B12 | 探针证明无密钥/无 Core 参与时无法从引用还原任何路径或资源标识 | **达成（归纳性）**：M-02/M-03/M-04；证明边界见 §5 |
| S1-B12 | 确认日志、错误与遥测中不泄漏映射表 | **达成**：M-05（错误码 + 日志 + 遥测逐条扫描零命中） |

**对照结论**：S1-B11/S1-B12 的**隔离原型层验证缺口**已按上述范围关闭；两个 blocker 的**产品级
解除**（把该形态写入 Contract 修订、在产品 runtime 实现并在打包/沙箱/DACL 模型下复验）仍属
未来 Contract 修订 Task 与 runtime Task。在产品实现落地前，M2-S1 §8.3 的告诫继续有效：
路线 A 不得被当作"安全边界已完成"。

---

## 7. 残留 `NOT_RUN` / `UNVERIFIED` 清单

**NOT_RUN**（范围或环境前提缺失，非失败）：

1. 目标打包/沙箱形态（MSIX/AppContainer）下复跑 TOCTOU 矩阵——依赖 S1-B8。
2. DACL/完整性级别设计及其负向测试——依赖 S1-B3（S1-B11 条件④）。
3. 真实 Tauri/WebView asset protocol 探针——S1-B1。
4. React consumer 重挂载/重连的引用重取——S1-B2。
5. 真实 Core worker/线程模型的取消与重启——S1-B4。
6. 映射表跨 Core 重启/持久化/密钥轮换语义——S1-B5（本原型表为进程内存态）。
7. 冷缓存（首次触盘）吞吐与首帧——S1-B6（与本 Task 无交叠，列全以免遗漏）。
8. 真实漫画页压缩率字节量——S1-B7。
9. 模型权重通道——S1-B9（T7 已决独立通道，机制归 runtime Task）。
10. 引用与 current/pinned Revision 的绑定与撤销——S1-B10（T6 语义的运行时验证）。
11. 产品 pytest / IPC runtime / GUI——按 Task 范围本就不运行。

**UNVERIFIED**（本 Task 提供了原型层证据，但产品级保持未验证）：

1. S1-B11 产品级 TOCTOU 防护：本 Task 的解析器是 Python/Win32 研究原型；产品实现（语言、
   进程边界、句柄生命周期管理）未存在，未验证。
2. S1-B12 映射 ID 的产品实现与其在真实 Tauri/React 边界的保密性质。
3. 低完整性级别/跨会话对手的拒绝（M2-S1 §6.1 对手 3，两代 Task 均未构造）。

**BLOCKED**：无。设计场景全部实际执行；symlink 在本机特权可用（T-20 实测，无环境缺项）。

**设计层限制（如实记录，PASS 的组成部分）**：

- 身份 = (volume serial, file index)。NTFS 在删除后理论上可复用 file index；digest 层与
  fail-closed 共享模式构成纵深，但该复用窗口未单独构造攻击验证。
- digest 层保证"解析到的 = 签发时的"，**不**保证"签发时的 = 合法的"——签发时刻的内容完整性
  是前提（产品上由 Core 生成/发布流程负责）。
- 窄共享（fail-closed）与宽共享（可用性优先 + digest 兜底）是产品取舍；本 Task 两种模式都
  实测，不预选。
- 每个负向场景的 restore check 只证明"攻击后合法路径可恢复服务"，不证明产品的高可用语义。

---

## 8. 复现命令

```powershell
# 全套（fixtures → 首轮 → 复跑 → 一致性比对；每步 exit code 入 raw/00-run-all.log）
pwsh -NoProfile -File verification/M2-S2/probes/run_all.ps1

# 单项
python verification/M2-S2/probes/make_fixtures.py      # lab 默认 %TEMP%\m2s2-lab
python verification/M2-S2/probes/probe_s2_toctou.py
python verification/M2-S2/probes/probe_s2_mapping.py
python verification/M2-S2/probes/compare_runs.py --first-dir "$env:TEMP\m2s2-lab" `
  --repeat-dir "$env:TEMP\m2s2-lab" --out consistency.json
```

**重复运行一致性**：连续两轮（第二轮在旧 result 文件存在、scope 目录已存在的重入状态下）
`consistent: true`——TOCTOU 16 场景与 MAPPING 8 场景的 id/status/期望/实测拒绝码逐项一致
（`raw/09-repeat-consistency.json`；M2-S1 §1.3 的两次运行口径的延续）。

---

## 9. 结论

1. **open-then-verify-from-handle 方向在隔离原型层成立**：检查→打开窗口的全部已构造攻击
   （文件替换、等大小替换、junction/symlink 逃逸、scope root 替换）由"句柄 containment +
   身份 + 大小"拦截；句柄期攻击由共享模式（fail-closed 或 digest 兜底）拦截；合法资源在全部
   攻击场景后可恢复读回一致内容。M2-S1 F-03..F-06 实测的窗口在参考解析器形态下以类型化拒绝
   关闭。
2. **映射 ID 满足 T5.4 的保密要求（原型层）**：ID 无路径/资源标识语义（归纳性证明）、查询面
   无泄漏、生命周期类型化。加密载荷选项按裁决保持关闭。
3. 上述结论的适用范围 = **本机、Python↔Python、隔离临时目录、合成 fixture**。进入产品前的
   剩余前提：S1-B8（打包/沙箱复跑）、S1-B3（DACL/完整性）、S1-B1（Tauri asset protocol），
   以及把本 Task 结论转译为 Contract 修订的后续 Task（由 Codex 冻结范围）。
4. 本报告不构成产品集成批准，不预选序列化库或 Tauri command 形态，不授权大媒体 runtime 实现。
