**FEA-09 UNFREEZE 修订提案 r1 独立契约审查报告**

**结论：`changes_requested`；P0=0 / P1=6 / P2=3。**  
支持方案 B 的方向，但当前精确文本存在内部矛盾与安全边界缺口，不能据此重冻或启动 I001/I005 返修。

1. **审查身份、对象与基线**

Reviewer：Codex，本次独立上下文 `/root`；未参与 FEA-09 实现、I001 裁决或本提案起草。未派发子代理。  
仓库：`G:\CODEX\New Manga`；分支：`main`；Git common directory：`.git`。  
`reviewed_head`／审查后 HEAD：`68a46dfe501f0dbe02d4e223817f3ff17e3bb99c`，未变化。  
被审对象：工作树未跟踪文件 `doc/reviews/FEA-09-UNFREEZE-r1-amendments.md`，**不属于该 HEAD 的提交内容**。  
提案：12127 bytes；SHA-256=`2ffe0c7ed7fc0097e1d8f53df99702afd6ba2be04314b99c12c7c0d84e9acbb3`；结束时指纹相同。

审查前后 `git status --porcelain=v1` 完全相同：提案为 `??`，下列 16 项为既有 ` D`。共同前缀为 `verification/FEA-09/native-registry/`；每组目录后接 `/isolated-data/host/source-access/`：

| 目录 | quarantine 文件 | corrupt 文件 |
|---|---|---|
| `37d836da52c94ad082d1bd01dcad9ea0` | `78129efd63cd4a4ab5ccd56fd9a7f0e2.dat` | `registry.v1.dat.corrupt-202611031328183382729` |
| `59949b7674c84c5297963275759606bf` | `fae26d327bb4463d940427d17881f9ae.dat` | `registry.v1.dat.corrupt-202611031328047249567` |
| `94737b1ab618406b9329c68637a2decc` | `2953b0220e7c424194e26d207017e793.dat` | `registry.v1.dat.corrupt-202611031353035436397` |
| `d5e7ddf952c14c3b8e01ac92af56e6d4` | `189d4ab58a1c4194a5d9862b6701e88a.dat` | `registry.v1.dat.corrupt-202611031354042159987` |

每组另外两项为 `registry.v1.dat`、`registry.v1.lock`；quarantine 文件位于 `quarantine/` 下。本报告不推断这些状态的原因。

只读声明：未修改仓库、用户数据或 Git 配置；未创建报告文件；未 commit/push；未重开 FEA-08。报告仅通过标准输出交付。

2. **方案 B、P1–P5 与 witness 独立性**

**结论：B 与 C-01b/ADJ-001 原则兼容，但确实改变 C-05 v1.1 的总可见集合，必须显式 UNFREEZE。**  
C-01b SC-07/15/39 要求旧 Managed Copy 继续读取、不自动迁移删除；ADJ-001 要求保护、披露及删除事务语义，均不要求补造 ORIGINAL 行。`rendering/service.py:232` 注释也确认 Page copy 是既有 original 表示。

P1–P5 的冻结正文当前仍完整存在（C-05:30）；提案能够原字节保留它们，但**尚无修订后文件可核验“最终字节不变”**。总 `V` 扩大不得表述成旧语义不变。

独立 OR 正确：坏 copy 不应否定合格 artifact，坏 artifact 也不应否定合格 copy。  
因此，合格 thumbnail 可以使 `V=true`，同时 copy 不合格、original 不可读；这是 `V/R` 分离的合法状态，不能把它说成 copy 已通过验证。当前反例④及开头概括未遵守此限定，见 U-001。

3. **反例①–⑥、投影与解析**

**结论：矩阵不完备，且部分行不能按现文本唯一判定。**  
①②可作为正例；③与①重叠，并把“投影按④”指向负例；④未限定无其他 witness；⑤缺少与合格 copy 同时存在的明确预期；⑥方向正确。

必有 `V=true` 而 original 解析失败的页：仅有合格 thumbnail/clean、导入列缺失、无合格 original revision。  
提案原则上要求 typed R 失败且保留 V，但没有定义这类页的 get/list/projection 形状。现有 `_page_from_row` 在 `library.py:103–108` 直接拒绝缺 hash、尺寸或 managed ref 的行；仅要求“不得冒充 original”不能解决丢页，见 U-002。

矩阵还须覆盖：两 witness 均真／均假、各自失败的交叉组合、页/章节/书软删、两种时间字段分别越界、NULL/dangling current、多 artifact 去重，以及资源缺失/越根/不可读。

4. **C-15 迁移断言 2/5**

**结论：新集合原则上可实现，v7 事务失败可回滚；当前修订遗漏断言 3，且验证执行方式仍需收紧。**  
expected 应为同一固定 `t`、同父级条件下的 artifact 集合与正尺寸 copy 集合之并，去重后按明确顺序比较；旧库没有新增完整性列，应由旧列正尺寸谓词推导 copy 集合。

C-15:42 仍要求“旧 complete、无 artifact 页仍不可见”，与新断言 2 直接冲突。  
断言 5 可以在同一事务视图解析资源，借 `IResourceVerifier` 检查；失败拒绝切入口。thumbnail-only 旧页即使 V 真，也可按既有门禁阻断升级；不得通过隐藏该页消除失败。

“生产读路径”应明确包含 **get、list、reader projection 全部**，使用回调提供的同一连接/只读视图及同一 `t`。不得调用会另开连接、维护缓存、发布资源或写 last-used 的完整读取服务。现有 repository 构造接收连接，可作为复用方向。

仍有假通过风险：两 SQL 同错、mapper 静默过滤、空集样本，以及 verifier 缺失。当前 `migrator.py:562` 在 verifier 为 None 时直接返回；非空待验资源必须禁止这种跳过。

回滚边界仍为逐迁移事务；无自动降级，恢复须按 C-01b SC-37 使用隔离新根与 verified 备份，不承诺整条升级链回滚。

5. **C-16 resolve secret 与密码生命周期**

**结论：可选字段不必另建命令，但不能绕过冻结 wire、签名 grant 与能力门禁。**  
C-06:39 要求签名覆盖全部 signed fields；C-16:149/151 限定绝对路径和读取来源属于签名 grant。新 resolve 的 `secret_ref.path` 若未经同一已验证 grant 绑定，便引入未授权文件读取及零填充删除目标，见 U-004。

生产 import 已在 `core_service.py:3823` 调用 `verify_secret_ref`，后者检查与 grant 内引用一致及 expiry（`source_read_refs.py:289`）；resolve 修订必须明确同等绑定，不能只写“先授权后 secret”。

生命周期已有 Host 生成、一次读取、TTL、销毁和脱敏框架，但尚未闭环：
- 三次失败按页、source、版本还是会话计数；何时重置；并发如何原子计数；锁定后返回什么。
- cache hit 是否消费/清理 secret，是否需要密码；未消费、授权前拒绝、取消、EOF、超时、进程崩溃的清理责任。
- token 与路径对应、私有目录/reparse/替换防护、一次消费与重放拒绝。
- PDF raster 密码传递；当前 `reader.py:111` 仍调用 `document_raster.open(raw)`，未传密码。

现有两种密码码可复用；锁定等分支必须冻结到明确 code/category/retryable。是否新增专码属于设计选择，不能靠 message 区分。AES ZIP 继续 typed unsupported。

6. **M2-C1 rev 2.12、minor 与旧 Core**

**结论：不能仅凭“additive”批准当前写法；也不能断言所有可选字段都必须 bump minor。**  
M2-C1 §3.2 允许未知可选字段被忽略，rev 1.5 有可选响应扩展零 bump 先例；C-16 §0 也允许新增命令零 Core minor bump。它们不自动证明既有 resolve 的密码扩展安全兼容。

当前旧 Core `handle_resolve_page_resource` 只取 `payload.get("page_id")`（:3386），会忽略新 secret；加密读取仍失败，且不会消费该文件。`source.read/1` 已由这个旧实现宣告，不能识别新能力。

应增加可辨识能力或明确版本配对，缺失时 Host 在创建/发送 secret 前 typed 拒绝。可在 DSH 明确裁决下保留 Core 2.3；也可选择逐命令版本提升，须冻结准确请求/响应面，不能用文档 rev 替代协议版本。

M2-C1 本身必须纳入明确 amendment/UNFREEZE 范围，至少登记原指纹、条款 diff、兼容矩阵、错误面和批准身份；可与 C-16 共用载体，无须强制独立文件。未参与 17 项 pin 不等于无需冻结审查。

此外，新 original-revision 优先规则必须对齐 M2-C1 rev 1.7 的不可变 original、稳定 `page-original-{page_id}` 与 first-publish-wins：明确 revision 变化是否允许及缓存失效规则，否则可能返回旧内容。

7. **Findings 与必须改写条款**

| ID | 级别 | 位置 | 问题与最小修复 |
|---|---|---|---|
| U-001 | P1 | 提案 §0.1、§1.2；C-05 §5；C-15 §4.3 | “零尺寸/未来页不可见”不能覆盖合格 artifact witness。将负例限定为两个 witness 均失败；说明 page 时间/尺寸只约束 copy，revision 时间约束 artifact；限定旧失败表与 incomplete 不可见说明的适用分支。 |
| U-002 | P1 | 提案 §1.2–1.3、§2.3 | 非 original artifact-only 页缺完整投影定义，生产 mapper 会丢页。冻结可表达缺 original 元数据的只读投影与 typed resolve 失败；禁止伪造 provenance、禁止静默过滤；共享类型扩域须由 DSH 明确。 |
| U-003 | P1 | 提案 §2.2；C-15 §1 断言 3 | 遗留“无 artifact complete 仍不可见”与并集冲突。同步修订断言 3；完整性状态守恒与可见性扩展分开陈述，软删/父删及时间反例保留。 |
| U-004 | P1 | 提案 §3.2；C-06 §2.2；C-16 §2/§7 | resolve 路径未要求与签名 grant 内 secret 严格绑定。采用 fresh grant 携带并签名引用，resolve 只作匹配提示；Core 验证 scope/session/expiry/token/path 后方可消费；不接受独立任意路径。 |
| U-005 | P1 | 提案 §3.2–3.3 | 三次失败、重置、并发、缓存命中及所有终止分支未闭环。补确定状态机、原子消费/计数、清理责任与完整错误映射；明确 PDF raster 密码接缝。 |
| U-006 | P1 | 提案 §3.1、§4、§7 | “旧行为不变/错误面不变”过宽；旧 capability 无法识别扩展，M2-C1 冻结语义修改未完整登记。补 capability/版本配对及四象限兼容表；显式登记 M2-C1 amendment、typed 错误和 original 资源键语义。 |
| U-007 | P2 | 提案 §2.2、§5.3 | “get/list 或 projection”允许漏验，且未说明同连接调用方式。改为三者全部核验，固定 t/顺序；非空资源禁跳 verifier；故意破坏查询/mapper 必须检测失败。 |
| U-008 | P2 | 提案 §0.1、§1.2③、§3.4 | 1298 是 .NET 用例数，不能写成受影响页数或已证回归规模；③误指④；M2-C1 “1.9”与目标 2.12 不一致。逐处纠正。 |
| U-009 | P2 | 提案 §5.1–5.2 | 流程未明确语义修订提交、最终冻结提交及 §1B 字节差异的分离。按 FROZEN-C05:66–70 补齐固定 reviewed bytes、最终元数据差异、三种指纹与历史 pin 保留。 |

8. **重冻、同步范围与最小批次**

建议拆成两个语义包，按序复核、冻结；不是强制另建两个契约：
- **A：I001**——C-05 v1.2 + C-15 迁移/投影条款；同时裁定 M2-C1 managed original 选择与稳定键影响。去掉 C-15 对密码修订的无关同批硬依赖。
- **B：I005**——C-16 + M2-C1 密码/能力/兼容 amendment；沿用 C-06 的签名授权原则。如改变 grant 字段、作用域或签名语义，须连同 C-06 显式 UNFREEZE。

每包：DSH 登记范围与旧 pin → 精确修订稿/反例 → 新上下文复核 → 仅元数据冻结 → 工作树 SHA-256、blob ID、blob SHA-256 → §1B 差异 → FROZEN/矩阵 → check 与 **17/17**。
M2-C1 单独记录最终指纹与批准依据；不得声称 17/17 已覆盖它。保留历史 §1–§7、旧 pin、旧 Review 原字节。

需同步 FEA-09 Task/AC/disposition、Handoff/EV、STATUS/PLAN/checkpoint；下游 C-04b/C-08/C-09/导出消费方须登记影响。  
C-01b/C-14/ADJ-001 无须仅因本方案改字节；必须保留保护、缓存及授权边界。UI-1 应承接读取密码/重试/失败展示；如新增 C-07 方法则另行 UNFREEZE，不在本包暗加 UI。

9. **I001/I005 实施必测清单与风险**

以下均为 **PLANNED，本轮未执行**：
- 真 artifact-only、真 columns-only、两者交叉、thumbnail-only；get/list/projection 一致，typed R 失败不隐藏 V；多 artifact 不重复页。
- 页/章节/书删除、page/revision 两种未来时间、NULL/dangling/non-valid current、非 VISIBLE_TYPES；referenced 不穿透 managed。
- v1–v6 升级、已存在 v7 的读回归；固定 t/排序、完整性/人工数据/Lock/current/pinned 守恒；缺文件、越根、不可读、verifier 缺失及验证异常不切入口。
- 迁移回调第二连接/写入禁用；故意破坏生产 SQL 或 mapper 必须失败；事务回滚后无半迁移结构。
- ZipCrypto ZIP/CBZ、真实加密 PDF 的 import→fresh secret→resolve；无密、错密、成功重试、三次失败、并发、重放、TTL 边界、撤销/EOF/超时。
- 签名不匹配、跨页/源/版本引用、路径替换/reparse、cache hit/miss、进程重启与孤儿清理；错误授权不得消费未验证路径。
- 密码及 hex/base64/url-encoded、secret token/path 在 Frames/NDJSON/日志/receipt/UI/证据中零泄漏；旧/新 Host×旧/新 Core 四象限。
- original revision 选择与缓存键/失效回归；相关 Python、.NET/build、真实 IPC、check、17 pins，跳过项逐项说明；新上下文实现 Review 后由 DSH 集成。

10. **本轮实际验证及推荐下一步**

实际运行：Git 身份/status/只读文件核对、提案 SHA-256、`pwsh -NoProfile -File tools/governance/check.ps1`（EXIT 0，PASS，3 warnings）、`pwsh -NoProfile -File tools/governance/verify_pins.ps1`（EXIT 0，17/17 PASS）。  
常规终端启动遇 Windows error 740，改用 Node 只读文件 API 与直接子进程调用完成，未提权。未运行测试、build、迁移实测、原生密码/IPC或泄漏扫描。上述 PASS 只覆盖当前治理和既有冻结指纹。

**推荐下一步：DSH 在 FEA-09 下修订契约提案，先处理 A 包，再处理 B 包；当前不释放 I001/I005 生产返修。**

> DSH：请原字节归档本报告。恢复点 `G:\CODEX\New Manga`、`main`，本轮审查 base/head=`68a46dfe501f0dbe02d4e223817f3ff17e3bb99c`，执行前刷新 HEAD/status 并保留既有变更。按 U-001…U-009 交付 r2 精确条款、兼容矩阵、反例与逐项 disposition，先登记 C-05/C-15 的 A 包，再登记 C-16/M2-C1 的 B 包及必要 C-06 扩域。仅处理明确登记的契约、载体、Task 与冻结治理文档；禁止生产代码、Schema/依赖、UI、用户数据、历史证据改写及 push。修订语义固定后委派新上下文只读复核；approved 且 P0/P1=0 后按冻结纪律登记三种指纹与 §1B，运行上述 check/pins 命令。未运行项保持 NOT_RUN；重冻和 DSH 范围授权完成后再分配实现，不重开 FEA-08。