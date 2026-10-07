# 轮换 preview 引用安全回收设计

Task：M2-DERIVED-GC-2-DESIGN；设计输入 `ab4b7c11`（生产树与审计 `32f9b932` 相同），release=`69d7cc08`。本稿是后继实现的设计输入，**不是现行 Schema/wire 修订，也不证明回收已实现**。

## 1. 实证与边界

| 事实 | 固定输入的代码/契约证据 | 结论 |
|---|---|---|
| 每次重渲染提交 Managed PNG，再复制随机 preview UUID | `src/application/rendering/service.py:544–590`；`src/bootstrap/core_service.py:876–938`；`src/infrastructure/resource_channel/render_preview.py:38–67` | preview 是副本；不移动、不覆盖、不删除 Managed artifact。 |
| Catalog 仅 resource_id/scope_class/rel_path | `src/infrastructure/resource_channel/catalog_store.py:34–40` | 无 page、artifact revision、退役状态；不能用当前行反推历史来源。 |
| Rust 单锁包住 rerender→revoke→map swap，map 仅进程内 | `apps/desktop/src-tauri/src/main.rs:332–349,397–437` | 前一 key 的 revoke 成功不等于持久退役或所有其他进程无引用。 |
| Core 生产与 channel 是两个 sidecar | `apps/desktop/src-tauri/src/main.rs:715–769`；`src/infrastructure/resource_channel/host_bridge.py:65–135` | Core GC 不能查看 channel 内存表；当前启动 channel 先于 production Core。 |
| Grant 在每个 ResourceChannelService 内存表，重启失效 | `src/application/resource_channel/service.py:11–15,80–82,180–208,255–284` | TTL/active_reference_count 仅本进程授权信息，不足以证明全命名空间无人使用。 |
| 当前/pinned 是主产品 artifact revision 指针和标志 | `src/infrastructure/sqlite/artifacts.py:81–118,229,258,293`；`src/ports/repositories/artifacts.py:56–66` | 可复用 get_artifact/list_revisions，不新增主产品表或 Artifact port。 |
| 旧 collector 只处理 orphan/dead row | `src/infrastructure/resource_channel/render_preview.py:106–163`；`src/bootstrap/core_service.py:1703–1724` | 有行有文件的旧 preview 仍增长；本设计不扩大原图 pages/ 回收。 |
| 每次 HTTP 读取 fresh resolve，已打开句柄不中断 | `apps/desktop/src-tauri/src/resource_protocol.rs:538–552,307–322`；M2-C1 §10.1 T6 | 不可删除仍有效 grant 的资源，也不能打断已打开流；Windows 当前只 FILE_SHARE_READ，不强制绕过分享冲突。 |

本次固定输入下 publish() 的生产调用点仅 CoreServiceServer.handle_rerender_page。手输 resource key、loader/实验 catalog、managed-read-only 与未知生产者均不是“可自动推断来源”的对象。

## 2. 选定最小方案：明确退役 + 启动静默窗口

**只在全部受管发布者和 channel 消费者都退出的受控启动窗口，回收“来源可核验、明确退役、源 revision 非 current/非 pinned”的 derived preview 副本。** 运行中不删除有行有文件的 preview；新旧 runtime 未统一接入保护时跳过 GC。当前第一刀 orphan/dead-row 行为保留，但在后继实现中也必须受同一窗口保护，不能把其现有启动扫描放在保护窗口外。

不用 TTL、文件时间、数量上限、目录名或“revoke_count=0”推导删除授权。不新建通用 GC 框架、后台调度、Reader 功能、全局 artifact 清理、引用计数系统或模型通道。

方案上限：同一长会话的文件增长仍保留；已 pinned 的历史副本也保留；只有安全重启窗口回收。故实现完成也只能说“轮换退役子集已回收”，不能声称磁盘绝对有界或 RC4-12 全部消失。若实测长会话磁盘成为问题，再单独设计在线读取租约/回收。

### 2.1 来源记录（拟议 catalog 辅助表，后继 Task 才能改）

保留现行 resource_catalog 三列与 CatalogEntry/lookup 形状，新增仅由 Core 写入的 `preview_lifecycle` 辅助表，resource_id 唯一：

| 字段 | 含义 |
|---|---|
| resource_id | 现有随机 preview key，与 catalog 行对应；不是 page-original key。 |
| producer_root | 生产数据根的规范化绑定；与本次 Core 数据根不一致即 UNKNOWN。路径只存 Core 本地，不发 WebView。 |
| artifact_id / artifact_revision_id | 生产 TRANSLATED artifact 与确切源 revision；Core 复用 `list_revisions(artifact_id)` 从 outcome.revision_no 找到唯一行，不拿 rev-N 字符串当全局 ID。 |
| managed_rel_path | 源 revision 的既有不可变路径，必须与 revision 记录逐字一致；只用于证明，永不 unlink。 |
| retired | 默认 0；仅明确退役请求可改成 1；不从时间/TTL 自动转换。 |

数据根/源 revision 无法绑定，或无对应 artifact/revision，**不为其创建可回收来源记录**。未知历史 catalog 行不回填猜测，不根据 UUID 格式补造关系。

发布顺序：Managed commit 已成功 → 原 publish 的 temp/fsync/replace → 在同一个 catalog SQLite 事务写 catalog + 来源记录（retired=0）→ 返回 preview。来源查找/写入失败应沿既有 PREVIEW_UNAVAILABLE fail-closed 语义；Managed commit 不回滚，未完整发布副本按当前失败清理路径处理。不可先返回 key 再异步补来源。

### 2.2 明确退役的触发与失败

后继 Task 拟议 trusted host→channel 内部方法 `mark_preview_retired(resource_id)`，只把已登记自有 preview 的 retired 置 1；不删除字节、不撤销任何额外 grant、不改变 resolve/issue/touch 语义。前端没有调用该方法的 Tauri 命令/ACL；传路径、scope、producer_root 或 arbitrary SQL 一律拒绝。未知 key、原图/managed scope、来源表与 catalog 不一致均不得新增来源/退役记录；失败返回既有 typed refusal，具体映射在实现 Task 冻结，不擅自加新 WebView 错误面。

Rust 复用现有 rerender 全局锁：Core committed/published → 旧 key 与新 key 不等时按当前代码 revoke previous → **只在 revoke 成功后**请求标记旧 key → 维持当前 map swap。相同 key、不知 previous、revoke 失败，均不标记可回收；None-preview 分支仍须完成旧 revoke 成功才可标记旧 key。mark 失败仅漏回收：记录诊断、保留旧来源 retired=0，不改已有成功 rerender/new preview 语义。不能把 mark 失败伪装成历史 revoke 失败，也不能再次撤销有效新 key。

retired=1 表示“此 key 曾被一个已知轮换显式退役”，**不表示现在无活跃消费者**；另一实例仍可持有/再 issue 同 key，整个活跃窗口不删除。新的 issue 不清除 retired：其保活由下一节的全命名空间窗口保证。不可把一般 revoke_ref/revoke_resource_refs、pin release 或 ttl 到期默认转为此回收标记。

### 2.3 命名空间静默保护：跨进程，而非 Python mutex

拟议保护为一个稳定的 Windows 内核文件锁，锚定规范化 catalog 路径的专用 lock 文件，位于 catalog 旁、**不在 previews/pages/ 清理目录内**。所有支持该协议的 production Core 与 resource channel 进程，在访问 catalog/文件前取得共享租约，并持有到其最后一条业务/授权请求结束、清理完毕、进程退出；进程崩溃由 OS 释放租约。GC 只能在共享租约为零时取得独占租约，且持有到所有判定、unlink 与 metadata 更新完成。

Core 启动尝试独占租约（非阻塞）；拿不到则 **跳过 GC**，以共享租约正常服务。拿到则静默扫描，结束后转为共享租约，再进入服务循环。独占到共享不能制造“无保护的生产访问”：若 native 不支持原子降级，可先释放独占再取得共享，但这段窗口不能发业务请求/读取 grant/发布；竞争者可以安全完成另一轮扫描。共享租约获取失败不能无租约继续参与；返回既有 Core unavailable/fatal 路径，不改成绕过保护。

当前 Rust 是 channel-first，必须调整**生产路径**为 production Core 启动/握手完成 GC 后再启动 channel；probe/ac1 路径不得默默启用此 GC。第二个实例已有共享租约时，后来的 Core 跳过扫描并正常共享；不得为了 GC 禁止正常多实例，也不能等待固定 TTL 强制清理。

Lock 路径必须是单一 namespace 权威，拒绝被替换/重解析的 lock 文件及上级异常；所有参与者验证相同 catalog/derived 根绑定。两个路径别名、混合数据根、旧版未加入租约的进程、绕过 host_bridge 的未知发行方式，均是 **UNKNOWN，GC 禁用**。本设计不声称已经具备这个租约，不用 PID 列表、时间戳、心跳/进程名或锁文件存在作为“旧进程全退出”证据。

**上线 Gate**：实现者必须证明受支持发布/服务入口全部接入租约（含实例重连/测试构造路径），并给出受控版本切换时旧 runtime 全退出的可核验证据；不能证明则整个新 live-preview sweep 保持 fail-soft skipped，标 BLOCKED，不能凭设计批准启用删除。未知旧 runtime 的迁移保护是实施与分发验收 Gate，不由本稿自动豁免。

### 2.4 current/pinned 与路径检查

持有独占 namespace 租约后，Core 从正确 producer_root 的生产 repository 重新读 artifact/current/list_revisions；匹配 artifact_revision_id、managed_rel_path 与 artifact 类型 TRANSLATED。source 为 current 或 is_pinned=True 必须保留。失联、查询异常、多义/失配、artifact/revision 缺失、数据库只读/迁移版本不兼容，均 UNKNOWN→保留，不以“没查到”作无引用证明。

若还有不受 namespace 租约约束的产品写者能改 current/pin，必须在生产 SQLite `BEGIN IMMEDIATE` 的同一连接事务下完成判定至删除（使用既有连接归属约束；仅 SELECT，不改产品行），或者保留该候选。不得先查完所有候选释放保护，再在磁盘循环删除。SQLite busy 只导致保留/跳过，不降低保护。

候选只允许 `derived-read-only` + 来源表已登记 + retired=1 + catalog rel_path 等于 `previews/<完整 resource_id>.png`，目录/文件均拒绝 reparse/symlink/junction，原始 rel_path 经过既有 lexical gate。最终删除必须针对核验的同一文件身份；不能用 resolve()+路径 unlink() 的检查后使用窗口作为最终安全证明。复用现有 Win32 句柄事实/identity/最终路径核验思路，以对核验句柄的 native delete disposition 完成删除；无法证明身份/分享模式安全则保留。

不修改现有读取的 FILE_SHARE_READ，不强制关闭其他进程句柄、不加 FILE_SHARE_DELETE 来迎合 GC。即使退休 grant 已失效，存在遗留已打开流时删除失败保留；重试只在下一安全窗口，不能终止流。managed/source/人工文件和其他 scope 永不进入候选，更不调用其删除器。

## 3. 删除/恢复顺序

在独占租约及必要产品事务保护下，对每个候选重读 catalog/来源、核验 current/pin、核验路径/句柄身份；**先删除 derived 副本，后在 catalog 单事务删除 catalog 行与来源记录**。不跨数据库伪造原子提交。

| 中断点 | 下一启动的行为 |
|---|---|
| Managed 已提交、publish 之前/失败 | 保留所有 Managed revision；按既有 PREVIEW_UNAVAILABLE 路线重试。 |
| 副本已 replace、catalog/来源尚未提交 | 新文件暂为 orphan；只在安全窗口内由现有第一刀处理；不能在活跃发布中扫描它。 |
| catalog/来源完整、返回/retire 之前 | retired=0，保留，允许漏回收。 |
| revoke 成功、mark 未完成/丢失 | retired=0，保留；失败不得影响新 preview。 |
| mark 已提交、其他实例仍 active | retired=1 只是候选；共享租约阻止扫描，grant/在途读继续。 |
| 副本已删除、catalog 删除事务失败/进程崩溃 | 当前无活跃通道；下一安全窗口第一刀 dead-row 清理。来源表的无 catalog 行记录可清掉（仅 metadata），不可据此删其他文件。 |
| catalog+来源已删除 | 重复扫描无操作；不会重绑旧 opaque ID，也不删除 Managed 源。 |
| 任一读取/锁/DB/删除错误 | fail-soft 保留，统计 skipped + 原因；不将 UNKNOWN 变成功、不阻断一般 Core 业务（共享租约缺失不能继续无保护业务）。 |

## 4. 可删 / 必留 / 未知矩阵

| ID | 对象/情形 | 判定 | 可执行条件或理由 |
|---|---|---|---|
| D1 | 已知自有 retired preview，源 revision 非 current/非 pinned，无活跃受管进程 | 可删 | 全部独占租约、正确 producer_root、源关系/DB保护、目录/句柄身份 Gate 成立。 |
| D2 | 同一 D1，unlink 已成功但 catalog/来源记录残留 | 可清 metadata | 下一安全窗口恢复；零 managed 删除。 |
| K1 | retired=0 或正在/刚刚发布的新 preview | 必留 | 不能仅按“目前没有 grant”删除。 |
| K2 | 源 revision 是 current 或 pinned | 必留 | 明确保护，即使只有 derived 副本、retired=1。 |
| K3 | 任一有效 grant 所属 channel/发布者仍 active | 必留 | 共享租约阻止整个 sweep；TTL 不改变判定。 |
| K4 | 已打开读取句柄尚未结束 | 必留/分享冲突跳过 | 不强制中断、不强制删除。 |
| K5 | managed-read-only、Managed/source/人工文件、pages 原图、模型 | 必留 | 不属于本 Task live-preview 删除集合。 |
| K6 | 同 key 轮换或 previous revoke 失败 | 必留 | 不设置 retired；保留当前 RC-4 语义。 |
| U1 | 历史有行有文件、无来源记录 | UNKNOWN→保留 | 不从文件名/mtime/rev-N 猜关联；不补填猜测。 |
| U2 | producer_root/源 revision 缺失、失配、DB查失败 | UNKNOWN→保留 | “未找到”不等于无引用。 |
| U3 | 多进程/mixed version/入口未加入租约、命名空间别名不确定 | UNKNOWN→禁用 sweep | 协议不覆盖所有读者就没有静默证明。 |
| U4 | symlink/junction/reparse、逃逸、身份被换或分享冲突 | UNKNOWN→保留 | 不降级为 pathname unlink。 |
| U5 | 错误/目录填充/未知 catalog loader 行 | UNKNOWN→保留 | 本设计不扩张第一刀/loader授权。 |

## 5. 与现有实现差量与后继范围

拟议 M2-DERIVED-GC-2 Owner=ZCode、Reviewer=DeepSeek Harness、Integrator=Codex；设计集成前不 ready。实际 branch/worktree/base 在 Task/交接中由 Codex 填入，不能把未来路径当成已创建。

| 文件/路径（拟议 allowed_paths） | 最小变化 |
|---|---|
| src/infrastructure/resource_channel/catalog_store.py | 辅助来源表、事务型登记/退役、metadata 恢复；Windows namespace 租约本地 helper 放同一模块，stdlib/ctypes，无通用框架。 |
| src/infrastructure/resource_channel/render_preview.py | 已有 publish 扩显式来源、受保护窗口内 sweep；原 publish_original 行为不改。 |
| src/bootstrap/core_service.py | 发布时复用 artifact repo 确切源关联、Core 启动/退出共享租约、独占 GC/current-pinned 查询装配。 |
| src/infrastructure/resource_channel/host_bridge.py | 全生命周期共享租约；只追加内部 mark_preview_retired，不导入产品 domain/SQLite adapters。 |
| apps/desktop/src-tauri/src/core_bridge.rs | trusted mark 调用与 mock 定向支持；不改 public Tauri 命令表。 |
| apps/desktop/src-tauri/src/main.rs | 生产启动顺序与成功 revoke 后 mark；保持 rerender 锁/失败/same-key/None语义。 |
| tests/core/test_derived_gc.py、tests/core/test_rc4_stdio_render_preview.py、tests/m2_resource_channel/test_catalog_authority.py、tests/m2_resource_channel/test_sidecar_isolation.py | 改动所需判别断言；原名单之外增测试文件需在实现 Task 点名；沿用已有 pytest。 |
| doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md、doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md 的窄注记、正式 Task/Handoff/verification | 设计批准后由 Codex 追认内部生命周期字段与行为；不改现有 WebView wire。 |

明确允许的后继共享变更：**仅专用 catalog 辅助表及 trusted channel 内部 lifecycle 方法**；source_artifact_revision_id 不发 WebView、不新增 Tauri IPC/ACL、不变 CatalogEntry/issue 请求、不变 T6 撤销/TTL。现行产品 schema.py、migration、ArtifactRepositoryPort、ResourceChannelService 的公共语义、读取 share flags、React、依赖、packaging/spec、Legacy、用户文件禁止修改。

如实现无法保持上述边界，或需要解决混合旧 runtime 的产品启动/升级取舍，先记 BLOCKED，交 Codex 明确扩展 Task/必要用户裁决；不扩大当前设计授权。

## 6. 后继验收 Gate（全部 planned / NOT_RUN）

| Gate | 必须留下的判别证据 |
|---|---|
| G1 来源/权限 | 老资源不补猜测、跨 producer_root/不匹配 artifact/source 不删；page-original/managed/source/人工/Lock相关主产品行不写；任意路径/scope注入拒绝。 |
| G2 生命周期 | 两次/三次真实 rerender→不同 key→旧 revoke成功→mark旧；same-key/revoke失败/mark失败/None-preview 各分支；证明 current/pinned/source sha256 与 product DB行无改动。 |
| G3 静默窗口 | 至少两个独立真实 OS进程持共享租约，独占 GC被阻断；退出后独占成功；kill所属实验进程释放；第二实例正常服务且跳过 GC；所有支持入口覆盖，包括现有 orphan扫描。 |
| G4 保护/回收 | 知道 retired非current非pinned 时删；active grant（含无subscriber）、current、pin、unknown 时不删。改变单一条件的对照必须能红。 |
| G5 安全/恢复 | 目录+文件 junction/symlink/身份替换、在途句柄、sharing violation、DB busy；publish/mark/unlink/catalog事务各 crash点恢复、重复运行幂等、失败日志/skip原因。 |
| G6 回归/隔离 | 定向 pytest + cargo（真实 sidecar）+ F-05 import名单不扩大到产品adapter + dev/packaged入口装配检查；生产行为变化若触及构建必须使用相应 fixed-head build证据。 |
| G7 启用边界 | 受控旧 runtime退出/新入口全部租约协议证明；unknown/mixed-version 实证下不删，不能把风险仅写进文档然后默认启用。 |

建议命令（路径须采用实现 worktree和实测环境，非本稿执行结果）：

```powershell
& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -m pytest -q tests/core/test_derived_gc.py tests/core/test_rc4_stdio_render_preview.py tests/m2_resource_channel/test_catalog_authority.py tests/m2_resource_channel/test_sidecar_isolation.py
cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml
git diff --check
```

实际入口/lease安全 Gate 必须真实双进程运行；Mock 锁不证明 OS共享/独占，实测 product DB保护不可用则 BLOCKED。固定 head 非作者 Review→条件闭合→Codex merge→集成后受影响回归后才能 done。设计本身只做引用/矩阵/范围核验，不在真实用户库运行 collector。
