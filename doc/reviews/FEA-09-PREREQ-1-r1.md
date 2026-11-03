# FEA-09-PREREQ-1 契约独立复核 r1

## 0. 元信息与只读检查

- **Reviewer**：Codex，本次独立会话；未参与 C-15/C-16 起草，未执行实现或返修，本次审查后不参与其后续实现。
- **模型 / reasoning**：系统身份为 GPT-6 系列 Codex；本会话未提供可核实的具体模型 ID、reasoning 配置，不以 checkpoint 中的 CLI 派发配置代替实际运行配置。
- **审查日期**：2026-11-03。
- **仓库**：`G:\CODEX\New Manga`。
- **分支**：`main`。
- **Git common directory**：`.git`。
- **reviewed_head**：`920c09525ed3afd4d64c44923d36127f690b4a98`。
- **审查前后**：HEAD 未变化，`git status --porcelain=v1`、`git diff --name-only` 输出均为空。

| 被审文件 | `git hash-object` | 工作树 SHA-256 |
|---|---|---|
| `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` | `eac21b531d65aebf53f2650b9e87dcfc1c132c91` | `fed45d9519362608017c9f159b2b92ed90a88faf877f4dc0df8c7e93c38c7223` |
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `58fdc16e4b3deb7b88e6f5e94692936c3d0ee7af` | `18af93e0e13631b19ad475a57e41dbe8a4622144ac914f060c4bff253d68e43e` |

实际检查方式：

1. 首次 `exec_command` 在启动 PowerShell 前失败，返回 Windows 错误 740；未执行其文件读取命令。随后通过 Node REPL 的只读文件 API、`execFileSync` 执行读取和检查。
2. 实际执行 Git 命令：

   ```text
   git status --short
   git status --porcelain=v1
   git branch --show-current
   git rev-parse HEAD
   git rev-parse --git-common-dir
   git diff --name-only
   git hash-object doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md
   git hash-object doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md
   ```

3. 使用 `rg --files`、`rg -n` 和带行号的内存读取，对照任务、当前状态/DAG/checkpoint、上游审查、架构、冻结契约及相关真实代码。
4. 内存测试实际调用形式：

   ```javascript
   execFileSync("python", ["-B", "-c", script], {
     cwd: "G:/CODEX/New Manga/",
     encoding: "utf8",
     windowsHide: true
   });
   ```

   `script` 只存在于内存；SQLite 全部使用 `sqlite3.connect(':memory:')`，启用 `PRAGMA foreign_keys=ON`。通过现有 `default_migrations()`、`MigrationRunner` 和从 C-15 第一个 SQL 代码块提取的原文构造 v7；未修改源码、未创建测试文件。`-B` 禁止生成 Python 字节码文件。

5. 测试环境：Python `3.14.6`，SQLite `3.50.4`。实际结果：

   ```text
   upgrade 1 -> 7 [('half', 'incomplete')] fk 0
   upgrade 2 -> 7 [('full', 'complete'), ('half', 'incomplete')] fk 0
   upgrade 3 -> 7 [('full', 'complete'), ('half', 'incomplete')] fk 0
   upgrade 4 -> 7 [('full', 'complete'), ('half', 'incomplete')] fk 0
   upgrade 5 -> 7 [('full', 'complete'), ('half', 'incomplete')] fk 0
   upgrade 6 -> 7 [('full', 'complete'), ('half', 'incomplete')] fk 0
   ```

   每个升级后的内存库重新交给仅认识 v1–v6 的现有迁移器，均返回：

   ```text
   old_writer SchemaTooNewError
   ```

   约束反例：

   ```text
   CROSS_SOURCE_LOCATION_ACCEPTED
   DUP_STABLE_SORT_KEY_ACCEPTED
   SAME_PROJECT_DUP_ENTRY_ACCEPTED
   CACHE_WRONG_SOURCE_AND_ABSPATH_ACCEPTED; FK_CHECK 0
   ```

   v7 SQL 末尾追加故障语句 `SELECT missing_precommit_probe();`，通过真实迁移器执行：

   ```text
   forced_failure OperationalError
   post_failure_version 6 source_tables 0 new_columns []
   ```

   使用现有 managed 写入列集，在升级后的库插入完整页：

   ```text
   old_managed_insert ('managed', 'incomplete')
   ```

6. Python `ctypes` 的纯内存 DPAPI 探测实际调用了 `CryptProtectData`、`CryptUnprotectData`，配置 `CRYPTPROTECT_UI_FORBIDDEN`。本环境在保护阶段返回：

   ```text
   protect 0 last_error 2
   ```

   因而**未取得 DPAPI 原生往返成功证据**。标准库检查确认 `ZipFile.open(..., pwd=None, ...)` 及 `_ZipDecrypter` 存在；本次 Python 环境未安装 `pypdfium2`。

7. 未运行完整治理门禁。`check.ps1` 存在临时文件写入分支（`tools/governance/check.ps1:705–710`），本次坚持仅内存实测；不借用 checkpoint 的历史结果声称本次 PASS。未执行完整产品测试或构建。

**只读声明**：未修改仓库任何文件，未创建报告或测试文件，未执行 `git add/commit/push`，未写入用户数据，未读取生产 AppData 数据库或实际源文件。报告仅通过标准输出交付。

## 1. Verdict

**`changes_requested`**

发现 **P0=0、P1=10、P2=3**。

v7 SQL 的基本执行、回填样例和迁移回滚成立，但冻结契约一致性、授权撤销、身份约束及可取消导入协议仍有阻断。两份草案当前均不可冻结。

## 2. 逐项核验

### 1. DDL 正确性：部分通过

**已验证：**

- 由现有 v1–v6 迁移链构造的各版本内存库，补齐后续迁移再执行 v7 均成功。
- C-15 `:49–53` 的回填与当前合法 schema 上的 `_COMPLETE_PAGE_WHERE` 相符：维度正数由既有 CHECK 保证。样例完整页变为 `complete`，placeholder 保持 `incomplete`。
- `page_bindings` 的两组复合 FK 分别指向 `source_versions(source_id, version_id)` 唯一键和 `source_entries(version_id, entry_id)` 主键，父键合法（C-15 `:96,121,144–147`）。
- 现有旧迁移器会拒绝 v7 库（`migrator.py:76–80`）。

**未通过：**

- 未约束稳定排序键在版本内唯一。
- 未约束同项目内同一 entry 的重复当前绑定。
- `source_versions.source_id` 与 `location_id` 所属 Source 可以错配。
- `rendition_cache.source_id` 与其 version/entry 可以错配。
- 跨版本保留 `entry_id` 有复合行键载体，但缺少可执行的身份匹配规则，源复用规则还会合并不同物理来源。

依据：C-15 `:81,90,101–125,143–171,178`；C-14 `:42–45,51–60`。详见 R1-004、R1-005。

### 2. 迁移安全：部分通过

单次迁移事务可落地。现有 `_apply_one` 在 `BEGIN IMMEDIATE` 后逐语句执行，在记录 schema 元数据后提交；失败路径回滚（`migrator.py:141–185`）。故障注入确认 v7 的表、列和版本记录均未遗留。

但草案的 pre-commit 回调尚未定义：

- 旧集合和人工数据基线何时捕获；
- 回调如何获得同一事务连接；
- 回调禁止提交、关闭连接或产生业务写入；
- 非 `sqlite3.Error` 验证失败的 typed 映射；
- “资源可读”如何进入守恒断言。

C-15 `:31–34,218` 主要检查数据库投影。它不能证明旧 Managed 文件存在或可通过可信根读取，也未覆盖上游要求的缺文件暂停入口切换。SQL 回滚成功不等于启动入口切换已验证。

另需明确：现有迁移器是**每个版本一个事务**，并非 v1→v7 整条链一个事务（`migrator.py:82–100,141–174`）。v7 失败时，先前成功补齐的版本可能已提交。详见 R1-010。

### 3. 与冻结契约一致性：FAIL

- **C-05 冲突明确成立**：其 `V(p,t)` 要求未删除的父书/章节和同一个 artifact 的有效 current revision（C-05 `:26–35`）。C-15 `:183–206` 允许没有 artifact/revision 的 referenced 页进入可见集合，并声称“不改 C-05 字节”。这是语义变更，不能仅靠新文档声明完成。
- **C-06 冲突明确成立**：申请方、通信方向和 Verify 归属被改变，且 grant 未承载冻结的四维 scope。见第 6 项。
- `source_sync_plans/source_operations` 留给后续契约的结论本身可接受（C-15 `:37`），但当前导入协议必须自行给出完整的会话内状态机，不能以预留表代替它。
- `rendition_cache` 的可再生、受管根、校验、引用保护方向符合 C-01b/C-14；新增元数据表不天然越权。但必须区分原始 `user-source` 字节与允许缓存的 rendition，不能沿用 managed 分支将新源原字节直接发布到 derived。

依据：C-01b `:34–36,87`；C-14 `:157–189`；C-15 `:153–179,206,256`。详见 R1-001、R1-002、R1-012。

### 4. 代码事实及写域：部分通过

当前 FEA-09 写域已覆盖主要必改位置（`doc/tasks/FEA-09.md:28–56`）：

- `library.py` 的列投影、mapper、读写路径；
- `domain/pages/entities.py`；
- decoder、Core 组合根/dispatch；
- Host、CoreClient Issuer/Commands/Wire、`WireLog`；
- 对应 Python/.NET 测试。

真实代码确认：

- mapper 直接拒绝 NULL managed ref（`library.py:79–85`）。
- `Page` 类型和校验要求 managed ref（`entities.py:28,43–44`）。
- `add_page` 不写新完整性列（`library.py:339–352`）。
- resolver 只读 managed，并发布到 derived（`core_service.py:3328–3372`）。
- reader catalog 从 managed ref 生成路径（`core_assembly.py:488–548`）。
- PDF adapter 没有密码参数，当前将密码保护返回 `ENCRYPTED`（`infrastructure/importing.py:315–338`）。
- 旧 `ImportPages` 的字段检查不能直接承载新增协议（`core_service.py:3538–3554`）。

遗漏或未冻结的必要改动是：**旧 managed 写入如何维护新 complete 状态、异步导入如何调度、取消/查询如何与长任务并行**。如最终需要修改 `Transport/SidecarProcess.cs`，该文件当前未在精确写域内，应在 scope-r2 先登记；本审查不直接扩域。

### 5. Host Registry 落地：部分通过

`HostOptions.DataRoot`、Host 生命周期与 Host-local handler 模式能承载 Registry（`HostOptions.cs:42–56`；`HostRuntime.cs:600,645–647,705–733`）。magic、长度、DPAPI、同目录临时文件及原子替换方向可实现。

当前仍不足以形成可测规范：

- 单一 `identity_facts` 无法明确对应多个 `authorized_roots` 的逐根身份。
- `Local\...` 互斥量未定义 DataRoot 派生算法，且跨 Windows session 不能保护同一数据根。
- 未规定加锁后重新加载最新快照，存在旧内存快照覆盖新 generation 的风险。
- 缺失文件首次创建与损坏文件恢复没有清楚区分；“不得重建”与“重新 register 恢复”之间缺少可执行状态转换。
- DPAPI 原生验证本次未成功，测试隔离不能仅等同于替换 DataRoot。
- Core DB 不存绝对路径已有原则，但 `locator/display_name/source_filename/decoder_params_json` 等写入字段仍需明确类型与归一边界；DDL 的 TEXT 本身不能执行这一安全边界。

备份仅交接设计输入、跨机不自动继承授权的范围合理；不能把“DPAPI 解密失败”当作唯一跨机授权判据。详见 R1-011。

### 6. C-16 传输裁决：FAIL

**明确裁决：当前 C-16 是对冻结 C-06 的语义改写，不能认定为合规实现。**

依据：

- C-06 `:37–39`：Core 申请，Host 授予，按 `SourceId/version/entry/rendition` 限定。
- C-06 `:51–52`：`RequestSourceRead` 为 Core→Host；`VerifySourceRead` 为 Host 内部，并在 Verify 时执行 scope 到授权根的解析。
- C-16 `:22,68`：Host 在 dispatch 前铸造，Verify 改到 Core 本地。
- C-16 `:43–60`：只有 `entry_key/path/facts`，没有冻结要求的四维 scope，也没有 `entry_key→EntryId→locator→授权根` 的规范映射。

“不新增反向通道”是合理设计选择，但不能自动取消已冻结的方向和校验归属。DSH 应选择保持 C-06，或通过精确 UNFREEZE 修订相应条款并重新复核。

**版本面单独判断：**

- 保持 Core 默认 `PROTOCOL_MINOR=3`、用 additive 命令和能力 Gate 区分支持情况，有现有实现先例，可接受；不应将它与 source-access wire 1.1 混为一谈。
- 新 Host 对旧 Core 缺 `source.read/1` 拒绝，方向成立。
- 旧 Host 不能被新契约追溯要求执行它不认识的能力检查；应明确由新 Core 在无有效 source grant 时拒绝新源操作。
- snake_case Host 命令与 PascalCase Core 命令符合现有映射惯例（`HostCommandRegistry.cs:170–183,264–272`）。
- 新增控制命令必须明确加入 host-control allowlist 和独立 handler；现有未知命令会在校验阶段拒绝（`core_service.py:1277–1292`）。

另有即时撤销不可执行问题，见 R1-003。

### 7. 密码与 AES：部分通过

- 密码通过短期 DPAPI 文件、wire 只传 opaque 引用，设计方向符合安全目标；DPAPI 密文不属于普通 hex/base64 的可逆编码。
- `ctypes` 能声明 Windows API 调用，但本环境 `CryptProtectData` 返回错误 2，本次不能宣称成功或产品可用。
- 一次性引用在 Plan 解密后删除，Import 再次读取如何获得密码没有冻结；Plan 请求也没有 operation ID，无法确定“≤本 operation”的生命周期。
- C-16 `:57,67` 允许引用在 wire 中出现，`:149` 又禁止“secret_ref 内容”出现在 wire，文本自相矛盾。
- AES typed unsupported、预生成 fixture、不新增依赖已在 C-16 `:82` 及 FEA-09 Task `:98,105` 登记，符合本轮产品限制。
- 标准库具有 ZipCrypto 解密入口；现有项目没有因此自动获得 ZIP/CBZ 导入实现。PDF adapter 当前未传密码，不能把“PDFium 可解密 PDF”当作已验证产品能力。

详见 R1-008、R1-013。

### 8. Plan/Import/Cancel/Receipt：FAIL

页级原子提交和已提交保留的方向正确（C-16 `:119`），但协议尚不可直接实施：

- 未定义 Import 的异步接受响应；现有 stdio 循环同步 dispatch，无法在同步 Import 阻塞期间处理 Cancel/GetReceipt（`core_service.py:5655–5667`）。
- `plan_digest` 匹配保存 plan，不等于重新验证当前源；generation/entry 内容重验与提交边界未闭合。
- `operation_id` 重用但参数不同、并发重试、进行中重试的行为未定义。
- 跨重启自然键跳过与 `import_as_new` 冲突。
- 一个容器提交部分页后取消，receipt 的单一 outcome、source 级 pending 及 page 级 committed count 无法充分表达剩余边界。
- unsupported 没有对应 counts，最终 receipt 无明确 operation 终态字段。
- 页级提交意味着“Core 崩溃→事务回滚”只能指当前页，不能指已经提交的整次导入。

详见 R1-007、R1-008、R1-009。

### 9. 错误码、证据与安全：部分通过

错误码闭集及不泄露路径的目标合理；C-07 的边界正确：本轮不新增 `IHostController`，UI-1 增加方法时必须同步 inventory 并走 UNFREEZE（C-07 `:12`；C-16 `:34,162`）。

仍需修订：

- `SOURCE_PASSWORD_REQUIRED/INVALID` 对“引用失效”的归类不一致（C-16 `:81,134–135`）。
- `SOURCE_ACCESS_DENIED` 与 `FILE_IDENTITY_CHANGED/SOURCE_ENTRY_MISSING` 的分流边界不明确。
- capability 探测异常不能沿用 `StartupSelfCheck` 当前的 Degraded-but-writable 行为放行 source 操作（`StartupSelfCheck.cs:140–146`）。
- `WireLog` 当前记录请求原文和 UTF-8 hex（`:82–105`）；新命令必须在进入内存 Frames 和 NDJSON 前明确抑制敏感字段，不能只扫描落盘日志。
- 不应为满足新命令的安全要求而改变旧 `ImportPages` 的字段/授权语义。

详见 R1-003、R1-013。

### 10. 范围与冻结就绪：FAIL

DDL、Registry、wire、密码和导入状态机属于 PREREQ-1 的契约范围。缓存元数据载体用于落实既有缓存要求，本身没有明显产品扩域；源复用规则则新增了会影响持久身份的决策，必须满足 SC-04 后才可冻结。

当前问题超出文字性 minor 修订：至少涉及 C-05/C-06 的显式契约处置、DDL 约束和导入协议状态机。修订后可重新送审；不得先冻结再以实现解释补齐。

## 3. Findings

| ID | 级别 | 文件:行 | 问题与依据 | 精确修改建议 |
|---|---|---|---|---|
| R1-001 | P1 | C-15 `:183–206` | 新谓词允许无 artifact/revision 的 referenced 页可见，且缺父书/章节删除条件；与 C-05 `:26–35` 冻结的必要条件冲突。“不改字节”不构成语义兼容。 | 分离 `is_complete_page`、`V(p,t)`、资源授权判定。明确 referenced 的 V 分支及父级删除、时间、稳定性规则；如选择无 revision 模型，先对 C-05 及 C-06 `:71` 建立精确 UNFREEZE 处置，重新复核冻结。 |
| R1-002 | P1 | C-16 `:22,43–68` | Core→Host 请求改为 Host 预铸，Host Verify 改为 Core Verify；payload 缺 `sourceId/version/entry/rendition`，`entry_key` 未与 EntryId 对齐。违反 C-06 `:37–39,51–54`。 | 在 C-06 精确 UNFREEZE 中裁决方向和职责；C-16 增加签名覆盖的完整 scope、类型、初次导入身份分配和 EntryId/locator/授权根解析规则。 |
| R1-003 | P1 | C-15 `:231,245`；C-16 `:65–69` | Core 仅持有旧签名/generation/expiry，无法获知 Host 已撤销；签名和旧 identity 仍可有效至过期。也没有 Host 失联时阻止新读/提交的机制。违反 C-06 `:62` 的即时撤销。 | 冻结撤销/失联通知或在线授权确认协议，以及撤销完成的线性化边界。明确在途 lease、commit 前确认、通知失败的 fail-closed 行为；负测覆盖 grant 有效期内撤销和 Host 断连。不得以 300 秒 TTL 代替即时撤销。 |
| R1-004 | P1 | C-15 `:90,121–122,143–150,156–168` | 实测接受跨 Source 的 version/location、重复稳定排序键、同项目两个页绑定同 entry，以及错配的 cache source。现有 partial index 只限制“每页一个 current”。不满足 C-14 SC-S10/S11。 | 增加 `UNIQUE(version_id, stable_sort_key)`；为 version/location、cache/version 增加同 Source 的复合父键/FK。定义项目为 book 或其它实体，并通过可验证的项目归属键和唯一约束/触发器执行当前 entry 唯一性；列明 needs_confirmation/missing/软删行是否占位。 |
| R1-005 | P1 | C-15 `:101,124–125,178` | `(registry_id, content_digest)` 不包含物理身份/lineage；同一授权根下两份同字节文件会被合并为同 Source。违背 SC-04 和“同一物理来源共享”的边界。跨版本重复 digest 的匹配歧义也未定义。 | 复用须同时验证授权、lineage、volume serial/file ID 与内容证据；区分“同物理源复用”和“相同内容去重”。定义重复 digest occurrence 的匹配与歧义拒绝规则，不得仅凭 digest 保续 EntryId。 |
| R1-006 | P1 | C-15 `:47–48,204,212–218`；C-16 `:153` | v7 后旧 `add_page` 插入完整 managed 页仍默认 incomplete，按新谓词不可见；实测成立。另 §3 统一谓词含 deleted_at，而 max_source_order 必须包含软删页，二者不能直接共用。 | 冻结所有 managed 创建路径显式写 `source_mode='managed', integrity_status='complete'` 的规则，保留半写默认 incomplete；将完整性、live 可见性和资源授权拆开，明确 max_source_order 使用含软删集合。增加升级后旧 ImportPages 的回归。 |
| R1-007 | P1 | C-16 `:91–94,119–123` | 未定义异步启动响应，当前同步 stdio dispatch 无法在 Import 阻塞时服务 Cancel/GetReceipt。不能仅以“长任务期间可查询”构成可执行协议。 | 冻结 Import 的即时接受响应、operation 状态机、后台工作/DB 连接归属、查询和取消响应、超时与重连行为；维持单请求交换即可采用“接受→轮询”模型。需要新增传输写域时先在 scope-r2 登记。 |
| R1-008 | P1 | C-16 `:75–81,91–92,118` | digest 匹配请求未充分规定当前源重验；Plan 消费一次性密码文件后，Import 的密码交接及解锁保留边界不存在，Plan 又无 operation ID。 | 定义 plan 的 canonical 内容、有效期、绑定目标/策略/有序成员及确认时重验；变化统一 stale 并重预览。冻结 Plan/Import 各自密码引用或安全内存解锁句柄的生命周期、重试和删除规则，禁止跨阶段复用已消费文件。 |
| R1-009 | P1 | C-16 `:96–123`；C-15 `:247` | operation ID 无参数冲突规则；`import_as_new` 与跨重启自然键跳过、同项目 1:1 约束冲突；部分容器取消和 unsupported 计数不完整。“Core 崩溃回滚”表述掩盖已提交页。 | 给 operation ID 绑定请求指纹并定义冲突/进行中/终态重试；裁决 import_as_new 在 referenced 模式的合法含义。receipt 增加 operation 终态、页/成员剩余边界及完整计数，规定部分提交后崩溃与重试只补未提交单元。 |
| R1-010 | P1 | C-15 `:27–35,218` | pre-commit 回调契约不完整，断言没有覆盖旧资源可信读取/缺文件暂停切换；“单事务”未区分逐版本事务与整条升级。上游 scope-r1 `:232` 要求仍未闭合。 | 明确基线捕获、事务内连接、回调禁止提交及失败映射；纳入外部资源检查和入口发布 Gate，分别定义失败停留 schema/根状态。PNG 产品回归放在集成门禁，不作为 SQLite 回调内部动作。 |
| R1-011 | P1 | C-15 `:225–234` | 多根对应单份 identity facts、Local 互斥跨 session 不覆盖、DataRoot 绑定规则缺失、锁后刷新和损坏恢复状态机未定义；无法判定并发写与重新授权恢复安全。 | JSON 改为逐根身份记录；冻结规范化 DataRoot 派生锁名及跨 session 排他机制、ACL、持锁范围、锁后重读/代次检查。区分首次缺失、损坏和重新授权恢复；补 isolated DataRoot、替身故障测试与真实 DPAPI 原生测试边界。 |
| R1-012 | P2 | C-15 `:108–119,177,179` | pixel digest 作为内容身份与 decoder 参数观察的关系未说明；decoder/scale 升级可能改变 pixel digest，影响匹配和 verified_digest，存在触发源变化的歧义。 | 明确与版本身份绑定的规范像素算法及版本，或将 rendition digest 与源内容身份拆开；增加“仅 decoder/scale 改变不产生 SourceVersion/EntryId 漂移”判据，遵守 SC-28。 |
| R1-013 | P2 | C-16 `:57,81,134–150`；C-15 `:37,247,272` | secret_ref 在 wire 的允许/禁止自相矛盾；引用失效错误分类不同；日志抑制位置未规定；C-15 引用 receipt 为 §5，实际在 C-16 §4；DDL 变更记录写“7 表 + … + rendition_cache”，与实际五张 Source 表加 cache 不符。 | 明确 wire 只允许 opaque 引用元数据，禁止的是密码/文件明文；统一引用失效错误，列出新命令在 Frames/NDJSON 前的抑制策略和 signed-fields 闭集；修正节号与表数。 |

**计数说明**：上表 R1-001…R1-011 中 P1 为 11 项；其中 R1-010 的迁移回调/资源守恒属于同一迁移阻断项，仍须独立处置。以表为准，**最终计数更正为 P0=0、P1=11、P2=2**。本报告 Verdict 不变。

## 4. 未覆盖 / 无法核验项

- 未运行真实用户库、生产 DataRoot、外部卷、实际 Registry 或密码文件测试。
- 未执行真实磁盘原子替换、断电恢复、跨进程/跨 session 互斥及 ACL 测试。
- DPAPI 原生探测失败，不能证明 CurrentUser、跨用户或跨机恢复行为已通过；也不能据此判断产品实现必然失败。
- 本环境缺 `pypdfium2`，未执行加密 PDF 解密；未生成或解密 ZIP fixture。
- 未执行全量 .NET/Python 回归、构建、四 PNG 校验或当前治理门禁；历史结果不计入本次 PASS。
- 内存迁移使用合法 schema 与代表性完整/半写行，不代表覆盖任意损坏库、全部人工数据组合或真实资源集合。
- 未验证尚未存在的 pre-commit 回调、授权撤销通道、后台导入调度和 receipt 存储实现。
- 未重开或重新验收 FEA-08；仅使用当前任务和冻结契约中的约束。

## 5. 冻结建议

**C-15、C-16 当前均不可冻结。**

最小修订集：

1. 先裁决 C-05 referenced 可见性模型，以及 C-06 请求方向、Verify 归属和四维 scope。需要改变冻结语义时，由 DSH 建立精确 UNFREEZE 载体并重新复核。
2. 补齐即时撤销、Host 失联、commit 前确认机制。
3. 修正 DDL 的同 Source 关系、稳定排序键唯一性、项目内 entry 唯一性及源复用身份规则。
4. 冻结旧 managed 写入对完整性列的维护，拆分完整性/live/授权谓词。
5. 完成异步 Plan/Import/Cancel/Receipt 状态机、幂等冲突、部分提交恢复和计数形状。
6. 闭合预览后源变化检查及密码一次性引用在 Plan/Import 间的生命周期。
7. 补齐迁移回调、资源守恒、入口切换与 Registry 并发/恢复规范。
8. 修正文档矛盾、签名字段和日志抑制规则；补足尚未验证的原生测试计划。

修订后重新独立复核，P0/P1 清零并完成门禁，才可记录冻结字节。不得将现有 SQL 执行成功或历史治理 PASS 当作上述语义缺口已关闭。

## 6. 结论与推荐下一步

**PREREQ-1 需返修，不能冻结并 done；FEA-09 继续保持 `proposed`。**

推荐下一步由 **DSH** 处置本报告并修订契约。可直接转发：

> 基于 `920c09525ed3afd4d64c44923d36127f690b4a98`，处置 FEA-09-PREREQ-1-r1 的 R1-001…R1-013。仅修订本 Task 授权文档；先对 C-05/C-06 的语义冲突建立精确 UNFREEZE 处置，再补齐 DDL 不变量、授权撤销/失联、异步导入与幂等状态机、密码引用生命周期、迁移守恒及 Registry 并发恢复规范。保持 FEA-09 proposed，不实施生产代码，不修改历史冻结证据，不触碰用户数据，不 push。交付逐项 disposition、修订文件和固定 head 后，提交新的独立只读复核；本次 reviewer 不参与实现或返修。