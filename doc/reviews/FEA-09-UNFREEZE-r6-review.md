**结论：`changes_requested`；P0=0 / P1=3 / P2=1。r6 尚不能进入获批语义提交或重冻。**

Reviewer：Codex，独立会话 `/root`，`reviewer_kind=agent`；未参与 FEA-09 实现、I001 裁决、r1–r5 起草或 r6 修订；未派子代理。
只读交付：未修改仓库、未创建报告文件、未 commit/push；本输出供 DSH 原字节归档。

仓库：`G:\CODEX\New Manga`；分支 `main`；Git common directory：`G:/CODEX/New Manga/.git`。
`reviewed_head`／结束 HEAD：`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`。
r6 为未跟踪工作树文件，不属于上述 commit；6606 bytes。
审查前后 SHA-256 均为：
`4690b16e51d75db2e35619d7741ab807bdb2332f8e713aac22448f21cec67983`。

审查前后 `git status --porcelain=v1` 字节相同：16 项既有 ` D`、7 项 `??`。
删除项均位于 `verification/FEA-09/native-registry/`，四个目录为：
`37d836da52c94ad082d1bd01dcad9ea0`、`59949b7674c84c5297963275759606bf`、
`94737b1ab618406b9329c68637a2decc`、`d5e7ddf952c14c3b8e01ac92af56e6d4`。
每组均为 `isolated-data/host/source-access/` 下 registry、lock、corrupt 与 quarantine 文件各一项。
未跟踪项：impl-design；r3 amendments/review；r4 amendments/review；r5 amendments；r6 amendments。

**证据限制：指定的 `doc/reviews/FEA-09-UNFREEZE-r5-review.md` 不存在。**
直接读取返回 `ENOENT`，`git log --all -- <path>` 为空；不能反向根据 r6 重建原报告。
以下按用户指定的 R5-001/002 主题及实际契约核验，不能证明与 r5 原始 findings 逐字闭合。

**R5-001：部分闭合，仍 OPEN。**
页级集合已有明确成员；V 全集序、可读页保留空位、全不可读成功返回及新旧客户端职责已明确。
这些规则不要求改变 C-16 既有错误三元组；C-05 §5 的不可见性诊断也不应自动变成 V 页的 unavailable。
但整请求集合尚未覆盖所有既有码，恢复位置边界也未完全确定，见 R6-001。
旧客户端可忽略新增字段，但不会展示不可读页；其现有恢复逻辑也不能保证执行新的“向后找可读页”语义。

**R5-002：部分闭合，仍 OPEN。**
cache 在 cooldown 前、每 key 单准入、第三次失败起冷却300秒、冷却结束/解密成功清零已明确。
DPAPI/口令失败计数，缓存/取消/超时/授权失败不计数，claim 后 token 永不复用及 Host 清理失败重试/启动回收，语义方向闭合。
锁、句柄及重试代码结构可以委托实现设计；但授权条件、错误三元组和 expiry 优先级仍冲突，见 R6-002/003。

| ID | 级别 | 位置 | 最小必须再改项 |
|---|---|---|---|
| R6-001 | P1 | r6:19–32；M2-C1 §6.3 | `REQUEST_LEVEL_CODES` 的兜底只写“内部/发布/catalog 错误”，未明确覆盖 `SOURCE_GRANT_EXPIRED`、`REF_SIGNATURE_INVALID` 等其余授权/validation 错误。最小修复：定义其为**所有非 PAGE_UNAVAILABLE_CODES 错误的补集**，明确保持原 envelope 传播。另冻结 resume 锚点自身可读时是否包含该页，以及锚点后无可读页、但前方有可读页时的确定结果；不能只覆盖“全章节无可读页”。 |
| R6-002 | P1 | r6:42–43、51–65；C-16 §6 | 所谓“继承”实际把 `CORE_CAPABILITY_MISSING` 从 `protocol` 改成 `unavailable`，把 `SOURCE_ACCESS_DENIED` 从 `authorization` 改成 `permission`。同时第3步 expiry 不满足→DENIED，第65行 grant expiry→REQUIRED；仅过期 grant 又可能被 live 筛选排除而走无匹配。最小修复：恢复既有 category；给 grant 过期与 secret_ref 过期各一个明确检查位置和唯一结果，并明确是否修订既有 `SOURCE_GRANT_EXPIRED` 映射。 |
| R6-003 | P1 | r6:42–44、67 | 第3步必须按 `secret_ref.token == secret_token` 选 G，第4步及缓存授权条款却规定“不需要 token”。无 token 的合法缓存请求无法通过第3步；复用已消费 token 也不能等同“不需要 token”。最小修复：将**当前 source-read 授权**与**cache miss 时的 secret 引用选择**分开定义，明确无 token 缓存命中的授权依据及多 grant 选择规则；继续保留撤销/失联 fail-closed。 |
| R6-004 | P2 | r6:4–5 | r5 review 来源缺失，无法核验原两项 P1及其 CLOSED 清单。最小修复：DSH 原字节归档真实 r5 review，登记完整 SHA-256、reviewed_head，并建立原 findings 到修订条款的对应；不得重建历史报告。 |

“契约语义冻结 + 实现设计委托”**仍成立**。
上述错误传播、恢复位置、缓存授权和 expiry 结果均为外部可观察语义，必须由契约裁决；不能留给 impl-design 选择。
impl-design 当前仍含旧顺序/错误优先级；r6 已要求同步，可在语义定稿时落实，无需扩大为实现细节清单。

生产代码核查表明这些边界可实现，但当前实现不代表 r6 已满足：
`library.py:355–459` 仍用旧 managed 列谓词；`migrator.py:328–346/481–484/562–563` 仍有旧基线及 verifier 缺失跳过。
`resolve.py:73–90` 仍依赖 import-bound grant；`source_read_refs.py:453–478` 明确区分过期、撤销和授权拒绝。
`secrets.py:105–154` 尚无本提案完整 claim/同句柄生命周期；`errors.py:12–31` 证实既有 category。
`core_service.py:3418–3445` 已具备授权准备→缓存接缝；Reader `3589–3654` 仍整请求失败、逐可读数组编号。
CoreClient `1227–1317` 只解析 pages；`ReaderLibrary.cs` 按 order 排序、按 initial page_id 查找，缺失时默认索引0。

A/B 拆分与 **A→B** 顺序可执行：A 冻结可见性/投影，B 基于 A 的 M2-C1 定稿字节扩展 secret。
语义提交→逐文件三指纹及 old/new blob→新上下文复核已提交字节→仅元数据重冻，符合 FROZEN 纪律。
最终元数据编辑后须重算最终 pin，并保留旧 pin 与语义提交指纹。
M2-C1 单独登记**足够**，前提是包含精确字节、diff、兼容/错误面及批准身份；17项 pin PASS 不覆盖它。
无需仅因 additive 字段强制 bump minor；配对限制和行为变化必须在正式 amendment 中落字节。

实际只读核验命令／结果：

| 命令／操作 | 结果 |
|---|---|
| `git --no-optional-locks -C "G:/CODEX/New Manga" rev-parse HEAD`；`branch --show-current`；`rev-parse --path-format=absolute --git-common-dir` | EXIT 0；上述基线 |
| 同前缀 `status --porcelain=v1`，审查前后比较 | EXIT 0；完全相同 |
| 同前缀 `log --all --oneline -- doc/reviews/FEA-09-UNFREEZE-r5-review.md` | EXIT 0；空 |
| Node `fs.readFile`、行号切片；`crypto.createHash('sha256')` | 指定可用文档及生产文件已核对；r6 哈希前后相同 |
| `pwsh -NoProfile -File tools/governance/check.ps1` | EXIT 0；PASS，3 warnings |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | EXIT 0；PASS all 17 |
| 常规 `exec_command` | Windows error 740；改用 Node 只读 API及直接子进程，无提权 |
| pytest／.NET tests／build／真实 IPC／DPAPI／迁移实测／竞态／泄漏扫描 | **NOT_RUN** |

推荐下一步由 **DSH** 处置本报告并准备最小修订；本 Reviewer 不参与返修。可直接转发：
> DSH：请原字节归档本报告。Task=FEA-09 契约修订；恢复点 `G:\CODEX\New Manga`、main，base/head=`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`。先刷新并保留既有变更；仅修订提案、同步 impl-design 及必要治理登记，按 R6-001…004补齐语义和来源，禁止生产代码、Schema、依赖、UI、用户数据、历史证据改写及 push。交付修订稿与逐项 disposition，运行上述 check/pins，委派新上下文只读复核；approved且P0/P1=0后再按A→B执行提交字节复核与重冻。建议不等于实现任务释放。