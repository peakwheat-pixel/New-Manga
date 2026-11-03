**结论：`changes_requested`；P0=0 / P1=2 / P2=0。r8 两项 P1 均部分闭合，r9 尚不可 approved。**

Reviewer：Codex，独立上下文 `/root`，`reviewer_kind=agent`；未参与指定实现、裁决或提案起草修订；未派子代理。
只读交付：未修改仓库、配置或用户数据，未 commit/push；仅标准输出，供 DSH 原字节归档。

仓库：`G:\CODEX\New Manga`；branch=`main`；common directory=`G:/CODEX/New Manga/.git`。
`reviewed_head`／结束 HEAD：`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`。
r9 是未跟踪工作树文件，4340 bytes，**不属于 reviewed_head 的提交字节**。
审查前后 r9 SHA-256 相同：
`ac948b355c09ba7537fb7d30f2138e4fbef126ff4bc184ed7adb343f76b55988`

审查前后 `git status --porcelain=v1` 完全相同：16 项 ` D`、14 项 `??`。
删除项均为 `verification/FEA-09/native-registry/` 下四组 registry/lock/corrupt/quarantine 文件。
未跟踪项：impl-design、r3–r8 amendments/review、r9 amendments。
status 输出 SHA-256：`399a67dbc3e541f92260db793f9c8b90d7823440f6d711a7750a055e8fd5c6c0`。

已核对指定 r3–r9 提案、r3–r8 Reviews、impl-design、六份契约、M2-C1、相关 FROZEN/矩阵及 I001 裁决。

1. **R8-001：错误分类 CLOSED；Reader 恢复契约仍 OPEN。**

PAGE 的11码枚举、其余错误保留原 envelope 整请求失败且不返回部分结果、unavailable 三字段，已明确。
锚点可读包含、向后寻找及回绕、全不可读成功返回，方向已确定；按错误类别决定成功/失败不再有原先的歧义。

**R9-001 — P1：恢复结果尚未形成与 M2-C1 兼容的完整 DTO 语义。**
位置：r9:22–26；M2-C1 §6.3:948、952–956。

- M2-C1 要求 `initial_position:{page_id,scroll_offset_y}`；r9:26 却将其定义为 logical_order 数值。若只是描述内部选择位置，仍缺少到既有对象的确定映射。
- 全不可读及空 V 时，必填 `page_id` 取何值未定；无保存进度时，空集也没有 `a`。
- 进度页不在 V 时，“使用其逻辑序”无法由当前 V 全集序直接求得；保存快照只有 `last_page_id`，没有历史 logical_order。
- 锚点仍可读时如何保留 Webtoon offset、跳到其他页或回绕时如何处理 offset，尚未落字节。

**最小修复**：明确保留或正式修订 `initial_position` 对象形状，补齐正常恢复、跳页、全不可读、空 V、进度页退出 V 的 page_id/offset 规则及旧客户端配对限制。无需冻结查找算法。

2. **R8-002：双层过期映射 CLOSED；完整唯一错误结果仍 OPEN。**

grant expiry→`SOURCE_GRANT_EXPIRED`，secret_ref expiry→`SOURCE_PASSWORD_REQUIRED`，两者同时过期优先前者，已消除原直接冲突。
r9 已列出的 code/category/retryable 与 C-16 §6 **逐字一致**；但 §6 只规定映射，不能替代 §2 的错误优先级。

**R9-002 — P1：第1–9步未与既有 grant 验证规则完整衔接。**
位置：r9:35–44；r8 §2.1①④；C-16 §2、§6；C-06 §2.2/§3。

- C-16 §2 明确签名→过期→撤销→授权失败；r9 顺序未给签名失败、grant 撤销/session/generation 失效的检查位置及结果，也未明确哪些优先级被替换。
- 例如其余条件正常、目标 grant 已撤销：继承规则应返回 `SOURCE_GRANT_REVOKED`；按 live 候选排除又可能返回 DENIED/REQUIRED。仅声明继承 fail-closed 不能唯一确定错误码。
- 第3步在第7步选择 Secret-G 之前检查“Auth-G / Secret-G 任一”过期，未限定候选集合。合法 live Auth-G 与旧过期 grant 共存时，存在性授权允许成功，任一过期解释却可返回 EXPIRED；缓存请求同样受影响。

**最小修复**：冻结过期检查所针对的请求相关候选范围，以及签名/撤销/session/generation 失败与新顺序的衔接和唯一结果；明确替换旧冲突规则。无需冻结选择函数、锁或代码结构。

3. **冻结与实现 Review 判断**

V/witness/R 分离、迁移守恒、投影最低集、managed 资源不可变及安全不变量，本轮未发现额外契约 P1。
impl-design 仍含旧 token 前置、缓存直接返回及冲突错误表；须按最终契约同步，不能视为已经完成。
上述两项补齐并获新上下文 approved、P0/P1=0 后，A→B 语义提交→三指纹/old-new blob→已提交字节复核→仅元数据重冻的流程可执行；M2-C1 单独登记。

实际检查：`check.ps1` EXIT 0、PASS（3 warnings）；`verify_pins.ps1` EXIT 0、17/17 PASS。
pytest／.NET／build／真实 IPC／DPAPI／迁移实测／竞态／泄漏扫描：**NOT_RUN**。机械 PASS 不覆盖 r9 语义。

推荐下一步由 **DSH** 准备两项最小契约补正，再 Appointment 新上下文复核；本 Reviewer 不参与返修。可直接转发：

> DSH：请原字节归档本报告。Task=FEA-09 契约修订；恢复点 `G:\CODEX\New Manga`、main，base/head=`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`。先刷新并保留既有变更，仅在登记写域修订新提案、同步 impl-design及必要治理记录，补齐 R9-001/002；禁止生产代码、Schema、依赖、UI、用户数据、历史证据改写及 push。交付逐项 disposition、修订稿和完整指纹；运行 `pwsh -NoProfile -File tools/governance/check.ps1` 与 `pwsh -NoProfile -File tools/governance/verify_pins.ps1`，未运行项保持 NOT_RUN。新上下文批准后再按 A→B 推进提交字节复核与元数据重冻；本建议不释放实现。