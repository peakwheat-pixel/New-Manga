# FEA-11 Scope Review r2（独立审查）

- 审查者：**ZCode 全新上下文**（session `sess_f3e93ab8-db5a-4360-b326-a2cfaca2dfcb`；未参与建卡/scope-r1 处置/PREREQ 起草/Review/冻结）。
- 审查基线：`main@1c519aec7a7e184700c3aa5e4923e4bd23baedff`；对象 = 修订版 `doc/tasks/FEA-11.md` + 依赖闭包（PREREQ-1 done、C-17 v1.0 FROZEN、Appointment、PLAN/STATUS）。
- 结论：**approved（P0=0 / P1=0 / P2=4）**。S11-001…011 全部实质闭合；写域 19/19 现有文件存在、27 新建落点合理、无越界；AC 实际 **10 条**（AC11-1…10）全部可验收、与 C-17 无冲突。
- 报告正文由 DSH 依据其最终回复归档（ZCode 只读）。

全部核对完成（conftest 动态引用 `default_migrations`——v8 自动进链无需写权；wire-schema 三方哈希一致无漂移）。以下为审查报告正文。

---

# FEA-11 Scope Review r2（独立审查报告）

**审查者**：ZCode 全新上下文（本会话；未参与 FEA-11 建卡、scope-r1 处置、PREREQ-1 起草/Review/冻结）。**只读**：未修改任何仓库文件、未 commit/push；本报告为唯一产出，由 DSH 归档。
**审查基线**：`main@1c519aec7a7e184700c3aa5e4923e4bd23baedff`（工作区 clean）；对象 = 修订版 `doc/tasks/FEA-11.md`（d1341945 处置后字节）+ 依赖闭包（PREREQ-1 done、C-17 v1.0 FROZEN、Appointment、PLAN/STATUS）。这是 scope 审查，不是对不存在实现的批准。

## 结论

**approved（P0=0 / P1=0 / P2=4）。可由 DSH 冻结 scope 并 Appointment 释放实施。**

修订卡在 PREREQ-1 done + C-17 v1.0 冻结后，S11-001…011 全部实质闭合：11 项 findings 的处置落点（10 条 AC + 逐文件写域 + 证据/资源计划 + DAG 修正）与 C-14/C-15 §3.2/§5–6/C-17 §2–§8 逐条对得上，未发现 AC 与冻结契约冲突。4 项 P2 均为文档口径修正，DSH 可在冻结/Appointment 时顺带处理，不构成阻塞。

## Findings

### P2-1 · AC 计数口径失实（12 vs 实际 10）
- **位置**：`d1341945` 提交信息「FEA-11 逐文件写域/12 AC」；本次 Appointment 提示「12 AC」；实际 `doc/tasks/FEA-11.md:94–103` 为 **10 条**（AC11-1…AC11-10，`git show d1341945:doc/tasks/FEA-11.md` 复核同版本即 10 条，非后续改动丢失）。
- **问题/影响**：后续 Gate/集成若按「12 AC」核对会误判缺项。
- **建议**：DSH 冻结 scope 时在处置记录或 Appointment 中澄清实际 AC 数=10（AC11-1…10），并按 10 条细化断言。

### P2-2 · 冻结契约不可改清单漏列 C-17 与 M2-C1
- **位置**：`doc/tasks/FEA-11.md:72`（out_of_scope「冻结契约字节（C-01b/C-05/C-08/C-13/C-14/C-15/C-16/FEA-01）」）与 `:90`（依赖节冻结契约清单）。
- **问题/影响**：C-17 是本卡**最直接**的冻结上游（DDL/状态机/命令面/CAS/lineage/resolve 全由它承载），M2-C1 rev 2.12 已裁定 NO_INCREMENT；两者未列入「不修改其字节」清单，留有解释空间（allowed_paths 白名单机制下实际不可写，故仅口径问题）。
- **建议**：out_of_scope 与依赖节补列 C-17 v1.0、M2-C1 rev 2.12。

### P2-3 · PLAN 文末叙述行与表格漂移（S11-011 残留）
- **位置**：`doc/REBASELINE_PLAN.md:45`「FEA-11-PREREQ-1（**proposed**，契约前置）」vs `:11` 表格行 **done**；`:43` 完成行亦未反映 PREREQ done。
- **问题/影响**：DAG 表格（权威）已按 S11-011 正确修复，但文末叙述行滞后——与项目「收口只刷表格不刷叙述=假事实源」历史教训同类。
- **建议**：DSH 下次 PLAN 编辑时同步刷新 `:43/:45` 叙述行。

### P2-4 · 「待 DSH 裁决（剩余）」清单未随 PREREQ 落地刷新
- **位置**：`doc/tasks/FEA-11.md:127–132`。第 1 条（契约 ID 建议 C-17）与第 3 条（relink/repoint/resync wire/命令面由 PREREQ 冻结后回填）**已由 C-17 v1.0 落地**（§5.1 `source_relink/source_repoint/source_resync` + 确认语义冻结），但卡内仍以「待裁决」原文留存；第 2 条（定时扫描/目录 watcher 生产者归属：本卡或登记承接 Task）仍开放。
- **问题/影响**：实施者可能误判 1/3 仍悬置；第 2 条若悬置到实施中，AC11-1 的四路断言集无法完全冻结。
- **建议**：冻结 scope 时标注 1/3 已闭合；第 2 条须在 **Appointment 前显式裁决**（AC11-1 已把「不做须 DSH 裁定并登记承接 Task、不得静默缺失」显式化，可接受延期裁决，不可悬置）。

## S11-001…011 逐项闭合判断表

| Finding | 修订卡落点（核对证据） | 判定 |
|---|---|---|
| S11-001 DDL/wire 前置无硬 Gate | `FEA-11-PREREQ-1` **done**（integration `75d11739b`，AC-P1…P8 全 MET）；C-17 **v1.0 FROZEN**（冻结记录三指纹齐全；本会话实测工作树 SHA-256 `86b89ff8…`==pin）；`depends_on` 含 PREREQ-1，卡首「未 done 前不得 ready/实施」 | **闭合** |
| S11-002 relink/repoint/resync 与 C-14 | AC11-6 三操作分列（命令/确认文案/身份断言；relink 保 EntryId/PageId/人工/区域/进度、repoint 改 EntryId、内容变走 resync 确认）；跨卷重验、同 bytes 不合并、SC-S11 顺序、当前/全部范围+确认前引用集变化重新预览；C-14（SC-S01–S03/S07/S11）列入目标节直接依据 | **闭合** |
| S11-003 C-15 §3.2 匹配规则 | AC11-3 两条路径（同源同容器 direct 保续 vs 跨版本逐项验证 algorithm/decoder/version/params/尺寸/方向+一对一唯一）；重复 occurrence 整组待确认不按 ordinal/locator 搬运；PDF 插页/ZIP 重排/目录重复内容不合并；旧证据缺失且不能按冻结参数重算→待确认/不可验证、禁伪造；FEA-09 真实导入旧库 fixture。与 C-17 §7.3 映射表、C-15 §3.2 原文逐条对应 | **闭合** |
| S11-004 CAS/原子性/零写 | AC11-4 三类代次+人工 revision/Lock/draft 基线的比较对象与事务内重读；单 plan/多项目原子单元；整批回滚唯一口径；并发 apply/四类漂移/授权撤销/第三区域 BaseRevisionId 冲突/DB 失败断言；零写精确比较集（pages/bindings/source rows/regions/text/current/revisions/保护/进度/receipt）；拒绝审计须 DSH 明确。C-17 §6.1/§6.2 已冻结同口径 | **闭合** |
| S11-005 lineage/在途 Run-draft | AC11-5 lineage 可恢复且隔离（新图编辑/渲染/导出/Run 不套旧坐标）；手动迁移新 RegionCandidate/revision+BaseRevisionId+Lock+第三项失败整批回滚；Prepare 后旧 Accept 阻止留 candidate；旧 edit token 不写新 binding；不改已接受 Run 快照。C-17 §7.1（含 7 行交错表）冻结 | **闭合** |
| S11-006 durable 双确认/崩溃点 | AC11-8 Host durable 授权在先（不得反序两阶段提交）；operationId 绑定 digest/目标集合；每步 durable receipt+ACK/重放/恢复顺序；同 key 同请求原结果/异请求拒绝；ACK 前读门控持久化（C-17 §3.3 `source_binding_publications.read_gate` 落 DB，非内存）；逐崩溃点真实新进程读取 journal/registry/DB；撤销/磁盘满/旧 snapshot/grant 过期失联断言且不重放破坏性 OS 操作。`tests/fea11/support/restart_core.py` 落 helper | **闭合** |
| S11-007 同步后生产读图 | 新增 AC11-9：先 resolve 旧绑定读字节→同步→生产 resolve/issue 读新内容；旧资源键/已发布摘要不可变；版本选择由 PREREQ 冻结（C-17 §7.2 `page-rendition-v2-` 选择函数+K0/Kv1/Kv2 对照）；core_service.py 窄 seam 入写域——本会话实测两处构键（`:3413/:3581`）与 `_publish_rendition_bytes`（`:3547`）均在该文件 | **闭合** |
| S11-008 写域精确性/诊断出口 | allowed_paths 逐文件（详见下节）；AC11-7 管理诊断走既有 V/R 区分（C-05 P8）、不暗改可见性、不扩 V(p,t)、reader typed 失败、不以新源/derived 冒充旧证据；AC11-9 验收至 Host/API（真实 IPC）、UI 后续独立切片 | **闭合** |
| S11-009 四路检测 | AC11-1 四路（启动/访问前、操作前、定时扫描、watcher 生产者/消费者）各有调用证据；丢 hint/overflow 全量重枚举；同 mtime/size 字节变可发现；mtime/size 未变不作内容未变证明；lease+digest 强验证不被缓存替代；Dirty 阻断新写而非直接换 binding；定时扫描延期须 DSH 裁定并登记承接 | **闭合**（归属裁决仍开放→P2-4） |
| S11-010 证据/资源计划 | 「证据与资源计划」节（AC-MATRIX/logs/IPC 输出/迁移负测；EV-AC11-1…10 每 AC 独立 pin；隔离根固定 `G:/CODEX/New Manga.workspace/FEA-11/`；不清理、不复写 FEA-09/10 tracked 证据）+ AC11-10 + 逐 AC 验证矩阵（断言/命令/证据三列） | **闭合** |
| S11-011 PLAN DAG 错位 | PLAN `:11/:12` FEA-11-PREREQ-1 与 FEA-11 独立行、依赖列正确、状态与 STATUS/TASK_LEDGER 一致 | **基本闭合**（文末叙述行残留漂移→P2-3） |

## 写域精确性结论

**逐文件核对（git ls-files）**：46 项中现有 19 项全部真实存在（schema/library/migrator 邻接、core_service/core_assembly、resource_channel/source_read_refs、Host Sources 2+HostRuntime、CoreClient 3、C# 测试 4、py 测试 3）；新建 27 项落点合理（`src/application/sources/` 10 文件、`source_sync.py`、`SourceOperationCoordinator.cs`、`Fea11SourceIpcTests.cs`、`SourceOperationTests.cs`、`tests/fea11/` 12 文件）。

**关键覆盖验证（本次实测）**：
- v8 迁移登记落点 = `schema.py:747 default_migrations()`（写域内）；`migrator.py` 仅通用 runner 无需改动（FK check 仅 v5、validate 仅 v7，v8 纯新增空表不触发——与 r1-light 复核的代码事实一致）；**不含 migrator.py 正确**。
- resolve 键选择/发布/自愈三处 seam 全在 `core_service.py`（写域内）；`referenced/resolve.py` 仅被复用（`prepare/render` 函数），无需写权。
- Host journal（`<DataRoot>/host/source-operations/`）落新增 `SourceOperationCoordinator.cs` + 既有 `SourceAccessRegistry.cs`（DPAPI/锁/原子替换规范复用 C-15 §5）。
- `tests/storage/conftest.py` 动态 `from …schema import default_migrations`——v8 自动进链，**无需 conftest 写权**。

**缺**：无阻塞性缺失。两个条件项留 Appointment 条款：① C-17 §7.2「catalog 丢文件自愈先验证已登记摘要一致」若需 `render_preview.py`（`RenderPreviewPublisher`，写域外）内部支持，须回 DSH 逐文件窄批；② C-17 §7.1「现有 page_id-only repository 不得成为旁路」按契约由应用装配（`core_assembly.py`，写域内）解决，若实现证明必须改 `regions.py` 等，同样回 DSH 补清单（scope-r1 条件项口径已预留此流程）。
**多**：未发现。`doc/reviews/FEA-11-*.md` 在 Owner 命名范围是项目惯例列法（Review 独立性由 Appointment+上下文独立保证），注记非 finding。
**越界**：无——无 App/UI/冻结契约（含 C-17 交付物）/共享组合根/FEA-08/09/10 证据；C-17 契约文件正确不在实施写域。

## AC 可验收性判断（实际 10 条）

AC11-1…10 全部具备：客观可测验言（身份/版本/digest/字节/前后集合精确比较，非数量断言）+ 验证矩阵测试文件 + EV 出口。与 C-17 覆盖面对齐：DDL/迁移（§2→AC11-10）、状态机（§3→AC11-2/8）、命令/DTO/错误/能力（§4–5/§8→AC11-6/9）、CAS/原子性（§6→AC11-4/5）、lineage/在途（§7.1→AC11-5）、resolve（§7.2→AC11-9）、证据降级（§7.3→AC11-3）——**无遗漏面、无冲突**。重点复核三处一致：AC11-6 repoint 身份与 C-14 SC-S01 一致；AC11-8 ACK 门控与 C-17 §3.3 pending gate 持久化一致；AC11-9 旧键不可变与 §7.2 K0/Kv1/Kv2 语义一致。`<<PARTIAL: 待 scope-r2 冻结逐项断言>>` 标记 + 「禁止把未执行项标 MET」治理自洽：本报告 approved 后由 DSH 按 10 条 AC 细化冻结断言。

## 是否可冻结 / Appointment

**可以**：DSH 可冻结 FEA-11 scope 并 Appointment 释放实施（建议处置 4 项 P2：P2-1/P2-2/P2-4 修卡、P2-3 修 PLAN 叙述行；P2-4 中「定时扫描/watcher 归属」须在 Appointment 前显式裁决）。依赖序满足（FEA-09/10/PREREQ-1 全 done）。

## 实际验证与 NOT_RUN

| 项 | 方式 | 结果 |
|---|---|---|
| HEAD/分支/clean | `git rev-parse/status/log` | `1c519aec7`、main、clean；d1341945 处置 diff（6 文件）核对 |
| S11-001…011 静态追溯 | 精读 FEA-11.md/PREREQ-1.md/C-17 全文/冻结记录/Appointment/r1-light + C-14 SC-S01–S07、C-15 §3.2/§5–6 原文比对 | 全部实质闭合（上表） |
| 写域逐文件存在性 | `git ls-files` + 代码定位（schema:747/core_service:3413,3547,3581/conftest:26） | 现有 19/19 存在；新建 27 落点合理 |
| Pin 等价核验 | `sha256sum`：C17 工作树==冻结 pin `86b89ff8…`；C14/C15/C16/C05/C13 与 scope-r1 pin 表逐一吻合 | PASS（18 项中核心 6 项抽查+clean 工作树） |
| wire-schema 无漂移 | `sha256sum`==DSH 日志 `WIRE_SCHEMA_SHA256`==EV 表（`9fed28fa…`） | PASS |
| `check.ps1` / `verify_pins.ps1` / `validate_contract.py` | 未运行 | **NOT_RUN**：plan mode 门禁拦截 pwsh/Python 进程调用（与 PREREQ r1-light 会话同情形，非脚本问题）；已以上述只读哈希等价核验替代，DSH 集成时可复跑取正式 EXIT |
| FEA-11 功能/迁移/IPC 测试 | 未运行 | NOT_RUN：无实现，scope review 不适用 |

---

**推荐下一步**（DSH）：接收本报告归档为 `doc/reviews/FEA-11-scope-r2.md` → 处置 4 项 P2（修 FEA-11.md AC 计数口径/契约清单/待裁决节 + PLAN :43/:45 叙述行）→ 裁决定时扫描归属 → 冻结 scope（10 条 AC 断言）→ Appointment（Owner 建议按卡 `suggested_owner: codex`，新实现会话，独立 worktree）→ 释放 FEA-11 实施。