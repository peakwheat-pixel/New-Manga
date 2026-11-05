核验基线：`main@604a2d3433f45c051af4a7ee517935ab35a4ec4c`。仓库前后均干净，未修改仓库、未 commit/push；仅在指定仓外目录写入报告及隔离验证产物。授权依据限于已落盘记录，不将其延伸为对冻结语义的额外豁免。

1. **裁决 1：CONFIRM。**

   C-17 §2 明确将历史清理留给“另行契约”，D1 正式定义 X1；§7.1 的 lineage 隔离规则没有另设“彻底删除后仍须保留”的要求。因此，专门确认后在同一事务删除该书 binding/publication/lineage、保留 plan/operation，可以成立；不豁免第 3、4 项的确认缺口。

   证据：[C-17:30](<G:/CODEX/New Manga/doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:30>)、[D1:50](<G:/CODEX/New Manga/doc/reviews/ADJ-2026-11-05-FEA-12-SCOPE.md:50>)、[ADJ-001:65](<G:/CODEX/New Manga/doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md:65>)；代码在 [library.py:1636](<G:/CODEX/New Manga/src/infrastructure/sqlite/library.py:1636>) 开启事务，[:1831](<G:/CODEX/New Manga/src/infrastructure/sqlite/library.py:1831>) 重查关联非终态 operation 并以 `BOOK_BUSY` 阻断，[:1940](<G:/CODEX/New Manga/src/infrastructure/sqlite/library.py:1940>) 起执行子图删除。

   隔离对照：取 `035468a81` 的旧删除方法，在相同 v8 fixture 上复现 FK 失败且 DB 不变；当前真实 wire 删除成功，三表目标行清零、plan/operation 各保留 1 行、`foreign_key_check=[]`。这是旧方法级对照，不宣称完整旧 checkout 回归。见 [FK 对照](<G:/CODEX/New Manga.workspace/FEA-11/codex-adjudication/run-43e38c334dbb48439f82519792fbb34e/fk-before-after.json>)。

2. **裁决 2：CONFIRM，但“diff 仅新增行”不成立。**

   独立 Task 修订 M2-C1 的路径有冻结契约明文依据，无须为此新建 C-18；preview minor 11、trash minor 13、5 个码、3 个 capability 与 `PurgeTrash` 暂不实现的登记一致。18/18 pins 实测通过，`035468a81..604a2d343` 的 18 份契约及 ADJ-001 diff 为空，没有改动这些冻结文件的字节。

   但 M2-C1 实际为 **166 insertions / 2 deletions**：替换文档版本状态行及 §11 policy 行。后者有 D2 与既有用户裁决支撑，属于已登记的对账例外，不能描述为“纯追加、既有行零变化”。证据：`git diff --numstat 035468a81 3e37c595b -- doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`；[C-04b:99](<G:/CODEX/New Manga/doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md:99>)、[C-09:110](<G:/CODEX/New Manga/doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md:110>)、[D2:68](<G:/CODEX/New Manga/doc/reviews/ADJ-2026-11-05-FEA-12-SCOPE.md:68>)、[用户裁决记录:84](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-1.md:84>)及 [:87](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-1.md:87>)。

   `PurgeTrash` 的延期明确写入 [M2-C1:1008](<G:/CODEX/New Manga/doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:1008>)；实现的 typed 拒绝见 [core_service.py:6075](<G:/CODEX/New Manga/src/bootstrap/core_service.py:6075>)。这只确认首版延期合理，不代表该命令已完成。

3. **裁决 3：OVERTURN，问题在 (a)；(b)、(c) 的规则可确认。**

   冻结文本未把 current 定义为“首个可见 region 的代表值”。ADJ-001 要求披露目标 current 保护，并在保护变化时拒绝旧确认；选取一个代表值会漏掉其他 region/artifact current，lineage 不可见也不表示该历史保护不会被彻底删除。C-04b 的单值字段暴露了契约表达缺口，不能通过 Task 排序裁决证明完整披露已经满足。

   **已复现反例**：同书两个 region，预览披露 `rr1`；将第二个 current 从 `rr2` 改为 `rr2-new`，摘要完全不变，旧摘要删除返回成功、Book 行归零。证据：[ADJ-001:51](<G:/CODEX/New Manga/doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md:51>)、[:58](<G:/CODEX/New Manga/doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md:58>)、[:64](<G:/CODEX/New Manga/doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md:64>)；[代表值选择:1811](<G:/CODEX/New Manga/src/bootstrap/core_service.py:1811>)、[摘要字段:280](<G:/CODEX/New Manga/src/application/library/service.py:280>)；[隔离反例](<G:/CODEX/New Manga.workspace/FEA-11/codex-adjudication/run-43e38c334dbb48439f82519792fbb34e/current-pointer-probe.json>)。

   (b) 两类 `is_pinned=1` revision 的去重并集符合保护定义，没有因纳入 artifact pin 而过度披露；(c) catalog 派生文件本就属于 PD-01 要求的清理披露，按绝对路径去重、catalog 查询异常返回 unavailable 合理。见 [library.py:1194](<G:/CODEX/New Manga/src/infrastructure/sqlite/library.py:1194>)、[core_service.py:1740](<G:/CODEX/New Manga/src/bootstrap/core_service.py:1740>)及 [:1869](<G:/CODEX/New Manga/src/bootstrap/core_service.py:1869>)。golden 的单书、集合摘要独立复算均一致，派生向量为 **3 files / 46 bytes**；但 golden 可复算不能证明保护清单完整。

4. **裁决 4：OVERTURN。**

   M2-C1 只豁免“针对 pending IDs/manifest 的显式重试”重跑预览，没有豁免混合批次中新删除存活书的集合绑定。C-04b 明文要求集合级与逐书 digest **都校验**；“未定义 retry 集合绑定”不能推出“只要混入一个 retry，即可跳过整个集合比较”。这削弱了冻结的有序集合确认保障；逐书校验保留不能替代集合校验。

   证据：[C-04b:32](<G:/CODEX/New Manga/doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md:32>)及 [:54](<G:/CODEX/New Manga/doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md:54>)、[M2-C1:802](<G:/CODEX/New Manga/doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:802>)及 [:810](<G:/CODEX/New Manga/doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:810>)；[core_service.py:2437](<G:/CODEX/New Manga/src/bootstrap/core_service.py:2437>) 在存在 retry 时跳过集合比较。已复跑的 [测试:1348](<G:/CODEX/New Manga/tests/core/test_core_delete_commands.py:1348>)明确以 `FAKE_DIGEST` 删除存活 `b2` 成功。Task/AC5 登记限定及 Review approved 均不能替代契约修订。

本次验证：两份删除/预览测试 **44 passed**；pins **18/18 PASS**；治理检查 **PASS，3 warnings**；golden 单书与集合摘要复算一致。未跑全量 .NET/pytest，未操作真实用户数据。[验证产物](<G:/CODEX/New Manga.workspace/FEA-11/codex-adjudication/run-43e38c334dbb48439f82519792fbb34e>)。

推荐下一步：**交 DSH 处置第 3、4 项并释放窄范围契约/返修 Task**，本轮不改仓库。需跟进：

- 完整披露并绑定所有将删除的 current 保护，明确受保护 artifact 数的表达。涉及 C-04b closed shape 或 canonical 算法时正式 UNFREEZE/重冻，不能只改 Task 解释；补“非首个 current 变化 → STALE、零副作用”判别测试。
- 先避免混合 live+pending 请求绕过集合确认；后续以版本化契约明确纯 pending 与混合请求的绑定规则。若保留弱化行为，必须显式修订冻结要求，不能称作无语义变化的 additive 澄清。补错误集合 digest、重排及换目标均拒绝的测试。
- 将裁决 2 的“纯 additive 行”表述更正为“协议增量 + 两处已授权文本替换”；`PurgeTrash` 启用前另行冻结 digest 绑定与能力声明。

DECISION-SUMMARY: 1=CONFIRM; 2=CONFIRM（非纯新增行）; 3=OVERTURN（a；b/c规则确认）; 4=OVERTURN.

