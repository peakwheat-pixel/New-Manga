<!-- FEA-09-UI-1 implementation review r2 (Codex independent) -->
# FEA-09-UI-1 实现 Review r2（Codex 独立）

- Reviewer：Codex 全新上下文；未参与实现/返修；只读。
- reviewed_head：`64ab9b9a8425a8b9e5e5babe4029b0427b89f9ef`。
- 结论：changes_requested，P0=0/P1=1/P2=4（N1–N5）。
- DSH 处置：见 Task/Handoff r2 处置节。

---

verdict: **changes_requested**
分级：**P0=0 / P1=1 / P2=4**（下列 N1–N5；R6 残留计入 N2，不重复计数）。
reviewed_head: `64ab9b9a8425a8b9e5e5babe4029b0427b89f9ef`
base: `7f4f4d3cda882cc4c3bb7c24c37a180480333a17`
Reviewer：Codex 独立实现 Reviewer r2，`reviewer_kind=agent`，全新上下文 `/root`；未参与实现或返修。
辅助只读审查：`/root/standards`、`/root/spec`。全程未修改仓库、commit 或 push；结束时工作树干净。

| 原 finding | verdict | 核验结果 |
|---|---|---|
| R1 | PASS（代码及断言） | token 创建即登记；未 accepted 出口经 finally 删除并撤销。G/H/I/J 真正断言 token 文件为零、章节页为零；运行门禁证据受 N1 限制。 |
| R2 | PASS | null/暂时异常保留 operation、运行态、轮询和取消；关闭受保护；仅终态或 `SOURCE_OPERATION_NOT_FOUND` 释放。两例恢复测试有成功日志。 |
| R3 | PASS | App 已删除递归、排序和 Registry.Authorize；folder 路径及 kind 交 Host IssueAsync。F 是真实链路，验证两页及隐藏过滤，但未断言自然顺序。 |
| R4 | PARTIAL | `HostController(HostOptions)`＋真实 VM＋HostRuntime＋Python stdio 成立，无 fake 替代；launcher 故障注入已披露。业务材料存在，16/16 成功门禁缺合规原始记录，见 N1/N4。 |
| R5 | PASS | VM 和 coordinator 双层拒绝 >1 encrypted 源，typed 文案明确；未扩 wire，逐源确认限制已披露。 |
| R6 | 未闭环 | CountsText 已绑定，测试只证明文本存在；receipt Grid 第二行遗漏，见 N2。 |
| R7 | PASS（计数投影） | skipped_pages/skipped_sources 分开显示；真实整源 skip 保持一页且显示“0 页 / 1 源”。行布局仍受 N2 影响。 |

**Standards / Architecture findings**

- **N2 · P2：计数与首行内容落入同一 Grid 行。**
  `apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/ImportDockView.axaml:150–161` 未声明 RowDefinitions，却给 CountsText 设置 `Grid.Row="1"`；两行定义误加在顶部标题 Grid。
  影响：计数与名称/结果可能重叠，R6 所需两行展示未完成。最小修复：在 receipt Grid 声明 `Auto,Auto`，补布局边界不相交断言；仅检查 TextBlock.Text 无法发现。

- **N5 · P2：当前 Task 交付字段仍为过期状态。**
  `doc/tasks/FEA-09-UI-1.md:18` 仍称“IPC 环境阻塞，非完成交付”；`:50` 仍称 proposed，与当前提交和 Appointment 矛盾。
  最小修复：DSH 更新 delivery_head，将草案段明确标为历史；旧 IHostController+4/C-07 UNFREEZE 已有作废说明，不另报。

**Spec / Verification findings**

- **N1 · P1：全量及 IPC 成功门禁证据未闭环。**
  当前 `gates.json`/`dsh-integration.json` 仅汇总声称 1317/0/74、16/16；仓内原始 `repair-full.log` 为 EXIT=1，八 TRX 合计 1306/11/74；`repair-ipc.log` 为 EXIT=1、16 例初始化失败。
  Handoff 已说明这些属于 Owner 失败记录，但未提供 DSH 成功逐次日志/TRX；Task 引用的 `logs/dsh-integration.log` 也不存在。
  依协作协议 §6.12，成功汇总不能替代带 EXIT、shell/解释器头的逐次记录。最小修复：补 DSH 成功原始日志、TRX、逐项 skip 原因及 pin。此项不推断 DSH 未运行或产品测试失败。

- **N3 · P2：Registry 密码审计覆盖声明不成立。**
  `Fea09UiImportIpcProductionTests.cs:231–232` 只扫描 `.log/.ndjson/.json`；实际 Registry 为 `registry.v1.dat`，未读取其明文模型或解密视图。
  最小修复：扫描 Registry.List() 等明文结果，更新 AC-MATRIX/gates 的覆盖说明。当前未发现实际泄漏，但不能宣称该面已验证零命中。

- **N4 · P2：源变化负测可被前序记录满足。**
  同测试文件 `:150–152` 在整个 fixture 历史 wire 中寻找任意 `SOURCE_`；前序 AES/错密记录即可满足，未约束本次请求或 UI 拒绝。
  当前保存材料确有本例 `FILE_IDENTITY_CHANGED` 与零页；最小修复：关联本次 request/operation，断言本次 typed 原因、UI 呈现和零页。

AC 判定：**AC-1/AC-3/AC-4 有真实业务材料，但受 N1/N4 限制，暂为 PARTIAL；AC-2 因 N3 为 PARTIAL；AC-5 静态符合，全量通过待 N1 补证。** 未把 fake VM 测试作为 AC-4。

范围核验：已读完整返修 diff 与 show stat；源码/测试在 allowed_paths，STATUS 为已登记 DSH 集成例外。
C-05/C-15/C-16/C-07、FEA-08/09 closeout、组合根、其他页面及旧 ImportPages 未改；`verification/FEA-09/**` 无 diff，canonical 污染恢复得到支持。

本次实际复跑：C-07 `--check` **PASS**；governance **PASS（3 warnings）**；pins **17/17 PASS**；Task EV 哈希 **30/30 一致**。
密码静态扫描：本 Task 29 个证据文件，已知密码字面量及 hex/base64/url-encoded 探针 **0 命中**；不替代 Registry 动态审计。
**NOT_RUN**：build、全量 .NET、17 个 UI 测试、16 个真实 IPC 测试及完整动态密码审计（只读限制，运行会写产物/证据）；布局动态探针被 PowerShell ConstrainedLanguage 拒绝。17/17 UI 成功仅为仓内日志结果。

推荐下一步：交 DSH 处置 N1–N5，保持 Task 未关闭。
可直接转发：**“DSH：以 `G:\CODEX\New Manga`、main、base/head=`64ab9b9a` 释放 FEA-09-UI-1 定点返修；由新 Codex 会话处理上述 App/View、测试及 Task evidence，禁止改冻结契约、旧路径或 push。补布局/关联断言、Registry 审计和成功门禁原始记录，更新 Handoff/pins；新 head 再交独立上下文复审。”**