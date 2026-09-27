# M2-C2 条款-来源追溯与一致性对账

- 日期：2026-09-26
- Owner：ZCode
- 对象：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 修订 `1.0` → `1.1`
- base：`3f468e6eb791ab112e38afaff50f511eb2ebc0c9`；本文件在修订后工作区生成。

## 1. Blob 记录（修订前后）

| 版本 | blob (git rev-parse / git hash-object) | 说明 |
|---|---|---|
| 修订前（`1.0`，M2-C1） | `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3` | base `3f468e6e` 的 HEAD blob，与释放指令引用一致（C2-AC1 核对） |
| 修订后（`1.1`，M2-C2 工作区） | `fc35913801297ee1876ea395f9c5041a16226f20` | `git hash-object` 于修订完成后记录；提交后即该文件 blob |

diff 规模：`git diff --stat` = 1 file changed, +38 / −4；`git diff --check` 干净。

## 2. 变更清单（实际触碰面）

| 位置 | 变更 | 类型 |
|---|---|---|
| 文档头 | 版本 `1.0` → `1.1`；新增未编号 **Revision history** 段 | 授权修订点 |
| §10 | 既有 7 条 bullets 原样保留；`Import sources` 行后半句 DEFERRED 指向更新（语义保留，见 §4 表）；`Credentials/secrets` 行原样保留；其后新增 **10.1**（T1–T7 阈值落约）与 **10.2**（安全语义落约） | 授权修订点 |
| §11 | `Large-media transport and import path capability` 行 `DEFERRED` → `PARTIALLY RULED (M2-C2)` | 授权修订点 |
| §5 | `ImportPages` 行仅更新 DEFERRED 指向尾巴（"to data-channel Spike" → "to the runtime Task；semantics ruled in §10.1/§10.2"），保护语义（host 授权、不透明受限可过期、禁 Base64/JSON）零改动 | **§1–§9 最小触碰**（理由见 Handoff） |
| §1–§4、§6–§9、§12 | 零改动（`git diff` 中无任何这些节的 +/- 行） | 未触碰 |

## 3. 新条款 → 来源逐条追溯

### 3.1 §10.1 阈值条款 → M2-S1 §7 裁决（T1–T7）

| Contract 条款 | 来源锚点 | 对账要点（裁决原文要素 → 条款要素） |
|---|---|---|
| 单资源 256 MiB 上限、`RESOURCE_TOO_LARGE` 建议码、无部分交付 | 裁决 T1 | 256 MiB 承诺线 ✓；64 MiB=M2-S1 探针配置非产品阈值 ✓；默认值可由 runtime 复测修订、承诺线变更须新裁决 ✓ |
| ≥32 活跃引用 / ≥16 单资源订阅者、类型化限流、不静默无界排队 | 裁决 T2 | 数值与语义逐字对应 ✓ |
| 首帧：热 200 ms P95 / 冷 1 s P95 目标；首帧=通道层字节到宿主，不含解码渲染 | 裁决 T3 | 200 ms/1 s、≤25 MiB、"channel-layer"定义 ✓；**冷缓存 S1-B6 `NOT_RUN`、1 s 不得表述为达标——条款内原文标注** ✓（Task 风险项①的兑现） |
| Core 单资源峰值 ≤ 字节+64 MiB（流式常驻 ≤32 MiB）；宿主带外 ≈0 / 流式 ≤32 MiB；禁整份 Base64/JSON 物化 | 裁决 T4 | 数值逐项对应 ✓；Base64 禁令表述为"重申既有 §10 禁令为验收线"（不放松、不新设矛盾）✓ |
| 分层信任：WebView 零 OS 路径；host 可信层解析派生缓存相对路径、不下发绝对路径；Core 批复不含 user-source 绝对路径；`user-source` 无前端可见实现 | 裁决 T5.1–T5.3 | 四条逐项对应 ✓；T5.1 的 Tauri asset protocol 标注 `NOT_RUN`(S1-B1)（裁决未标验证状态，条款按 M2-S1 §8.2 S1-B1 如实补标——收紧而非放松） |
| 引用绑定 resource_id+revision 指纹；TTL=300 s 滑动续期；revision 切换/删除/pin 释放/管理操作立即撤销（`REF_REVOKED`）；在途句柄不强制中断 | 裁决 T6 | 语义逐项对应 ✓；"TTL 可配置"注记与裁决"TTL=300 s 为默认配置，产品可配置"一致 ✓ |
| 模型权重独立通道/独立生命周期；不适用 T1–T4 与 T6；受控读取含 hash 校验；机制与打包影响归 runtime | 裁决 T7 | 逐项对应 ✓；S1-B8 `NOT_RUN` 标注（联动原文）✓ |

### 3.2 §10.2 安全语义条款 → M2-S1 / M2-S2 / 裁决

| Contract 条款 | 来源锚点 | 对账要点 |
|---|---|---|
| open-then-verify-from-handle：单次打开；containment（句柄 final path 在 scope root 内）→身份→大小；仅经句柄读取；digest 对照签发值；读后身份复核；check-then-use 不得作为安全边界 | M2-S1 §6.3 条 3、§8.1 强制限定 1、§8.2 S1-B11 条件①②；M2-S2 §3（`HandleVerifiedResolver` 校验顺序）、§4（T-01P..T-21） | 校验顺序与 M2-S2 实测实现一致（containment→identity→size→read→digest→post-read）✓；Windows flags（`FILE_FLAG_BACKUP_SEMANTICS`、reparse 处理）对应 M2-S1 条件①原文 ✓；**S1-B11 条件③（打包复跑）④（DACL/S1-B3）`NOT_RUN` 保留在条款内** ✓（Task 要求"产品级保证仍 UNVERIFIED"的兑现） |
| WebView 层引用保密 = Core 侧不透明映射 ID；不得编码/泄露路径或资源标识；Core↔host 可信层豁免；**加密载荷方案已关闭，重开须新裁决** | M2-S1 F-01/R-002、§6.3 条 4、§8.2 S1-B12；M2-S2 §5（M-01..M-08）；裁决 T5.4 | 映射 ID 方案选择=裁决 T5.4 ✓；"加密载荷关闭"为裁决原文（"除非映射 ID 方案在验证中被证明不可行（须新裁决）"）✓；证据为归纳性（M2-S2 §5 证明边界）如实引用 ✓ |
| 用户源文件绝对路径不得经 IPC 下发到任何层；派生缓存相对路径仅存在于可信 host/Core 层 | M2-S1 §6.3 条 2、§5（路径/secret 不入 DTO）；裁决 T5.2/5.3；M2-C1 §10 既有语义的明确化 | 与 §8 `message`"不得含本地绝对路径"互补不冲突 ✓；M-05（错误/日志/遥测零泄漏）为该条的实测支撑 ✓ |
| 类型化错误码最小集（16 码，经 §8 `ErrorEnvelope.code` 值域）+ 错误不泄漏映射表/路径 | M2-S2 §3 错误码族、§4 表（expected/actual 拒绝码）、§5 M-04/M-05；T1 建议码 `RESOURCE_TOO_LARGE` | 16 码逐一来自 M2-S2 实测错误码（`REF_*` 9 个 + `RESOURCE_TOO_LARGE`(T1) + `MEDIA_TOO_LARGE_BY_HANDLE`/`FILE_IDENTITY_CHANGED`/`FILE_SIZE_CHANGED`/`CONTENT_DIGEST_MISMATCH`/`OPEN_FAILED_SHARING_VIOLATION`）✓；"runtime 可增不可减语义、wire 命名可微调"避免把原型命名冻结为产品命名 ✓；未触碰 §8 定义 ✓ |
| 模型权重独立通道（条款正文在 §10.1 T7） | 裁决 T7；M2-S1 §5（权重 NOT_RUN）、§8.2 S1-B9 | §10.2 仅交叉引用，不重复定义 ✓ |

## 4. 既有语义零放松对照（C2-AC4）

| 既有 §10 条目 | 修订后状态 |
|---|---|
| Core 是业务/SQLite 唯一权威 | 原样保留（未触碰） |
| Never overwrite or mutate original source files；Managed Copy；前端路径不是写许可 | 原样保留（未触碰） |
| Preserve human edits / `Lock` / current Revision / pinned Revision / recoverable task state；写边界校验 | 原样保留（未触碰） |
| 禁止大图/Webtoon/模型权重进 JSON/Base64 IPC | 原样保留（未触碰）；T4 将其重申为验收线（加强表述，非放松） |
| 不 pick file URI/token/OS handle/shared-memory/streaming/tile/chunk transport；须独立 spike 验证后才能发布大媒体命令 | 原样保留（未触碰）——通道选型维持 M2-S1 §8.1 条件性状态，与本修订"不授权 runtime"一致 |
| Import sources 只能 Core/host mediated scoped references | **保留前半句原样**；后半句 `DEFERRED` 指向更新：该 Spike（M2-S1/M2-S2）已完成，security/lifecycle semantics 已 ruled（§10.1 T5/T6、§10.2），wire 值对象形态仍 DEFERRED——DEFERRED 面收窄是本 Task 的授权目标，非放松 |
| Credentials/secrets 排除 | 原样保留（未触碰） |

## 5. 跨文档一致性对账（C2-AC4）

| 对账对象 | 检查内容 | 结论 |
|---|---|---|
| AD-001 Migration constraint 4 | 大媒体/权重不进普通 JSON/Base64 IPC | §10 既有 + T4 重申，一致 ✓ |
| AD-001 constraint 6 | IPC contracts 保留 source-file safety、Managed Copy、human edits、Lock、current/pinned Revision、recoverable task state | §10 既有 bullets 全保留，一致 ✓ |
| AD-001 TARGET_INTENT 表 | Tauri=传输+权限边界（无域规则/DB writer）；React 仅呈现 | T5 分层信任模型与其同构（host 可信层、WebView 零路径），一致 ✓ |
| M2-S1 §6.3 设计要求 | 条 2/3/4 落约、条 1（解析时重校验）由 T6+§10.2 承接、条 7（`user-source` 无实现）由 T5.3 承接 | 一致 ✓ |
| M2-S1 §8.1 推荐 | 路线 A 条件性建议状态**不因本修订改变**；三项强制限定（R-001 句柄校验、R-002 映射 ID、绝对路径不下发）全部落约 | 一致 ✓（修订记录明示"不授权 runtime"） |
| M2-S1 §8.2 解除条件 | S1-B11 ①②→§10.2 设计要求；③④→条款内 `NOT_RUN` 保留；S1-B12 解除条件→映射 ID 条款 | 一致 ✓ |
| M2-S1 §8.3 前置条件 | "S1-B11/S1-B12 解决前路线 A 不得当作安全边界已完成" | §10.2 诚实边界声明保留该语义 ✓ |
| M2-S2 报告 §6/§7 | NOT_RUN/UNVERIFIED 清单 | 条款未把 NOT_RUN 项写成已满足；"S1-B11 产品级防护保持 UNVERIFIED"原文引用 ✓ |
| 裁决文档 scope of effect | 裁决约束未来 Task、不追溯改变 M2-S1 结论、不构成集成批准；Contract 落地须另行冻结范围的 Contract 修订 Task | 本 Task 即该 Task（release `47da6477`）；修订记录"不代表已实现"与裁决生效范围一致 ✓ |
| 裁决文档"生效与后续"第 2 条 | Contract 修订**不直接修改**裁决时点的 Contract；由修订 Task 落约 | 本修订即执行该后续，blob 前后记录齐全 ✓ |

## 6. grep 守卫结果与人工判定

原始输出见 [`guard-checks.log`](guard-checks.log)。

| 守卫 | 结果 | 人工判定 |
|---|---|---|
| G1 所有 "absolute path" 命中均为禁止语境 | 3 处（279/280/291 行），全部带 must not/never/不得 | PASS |
| G2 "下发路径给 WebView" 无否定词表述 | 1 处正则命中（279 行），该句本身含 "must not forward"，为禁止表述 | PASS |
| G3 新增行无越界宣称 | 2 处命中均为**否定语境**（修订记录与 §10.1 头部的"不代表已实现/没有任何条款代表已实现"），非越界宣称 | PASS |
| G4 新增行保留 UNVERIFIED/NOT_RUN 边界标注 | 7 行含标注（正向检查） | PASS |
| G5 版本 `1.1` 与 Revision history 就位 | 行 3 / 行 5 | PASS |
| G6 节标题无删改 | diff 中无 §1–§12 标题的 -/+ 行；新增标题仅未编号的 Revision history 段与 §10 内的 10.1/10.2 小节 | PASS |
