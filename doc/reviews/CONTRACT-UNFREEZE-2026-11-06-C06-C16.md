# CONTRACT-UNFREEZE-2026-11-06-C06-C16：C-06 v1.2 + C-16 v1.3（Run-scoped source-read 授权建立命令）

> 载体用途：按 [C-06 冻结记录](../plan/FEA-CONTRACT-FROZEN-C06.md) 与 [C-16 冻结记录](../plan/FEA-CONTRACT-FROZEN-C16.md) 的 UNFREEZE 流程，提出 C-06 v1.2 / C-16 v1.3 字节修订；须经独立上下文 fresh subagent 做 **byte-level 复核** + DSH 重新冻结后方可视为最终字节。
> 触发：用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH，无需用户介入」；`FEA-11-RUN-GRANT-1` 权威 scope review `doc/reviews/FEA-11-RUN-GRANT-1-scope-r1.md` 判 **READY-WITH-UNFREEZE** 并推荐 U-A；Codex 第二意见 `…-scope-r1-delta.md` 结论一致（非权威存档）。
> 授权链：用户 2026-11-06 全授权 → DSH 裁决 U-A（`doc/tasks/FEA-11-RUN-GRANT-1-PREREQ-1.md`「DSH 裁决」D-1…D-8）。
> 顺序约束：本载体 + 两份契约 + 两冻结记录 + 矩阵为 UNFREEZE 提交；CORE/HOST 实现另卡（`FEA-11-RUN-GRANT-1`，PREREQ-1 done 后释放）。

## 1. 背景与目标

`FEA-11-RENDITION-1`（done，`a05a419f7`）交付了 Core 侧 referenced rendition 读路径，但生产 referenced 页 Run 仍不可端到端（L-R1）。scope review 证明缺口不是「Host 不会铸 grant」，而是 **Core 没有任何命令能把一份已铸 grant 建立成一次 Run 的 page-binding 读授权**：

- 授权面 = 进程内 `SourceReadGrantRegistry._bindings`（`src/infrastructure/resource_channel/source_read_refs.py:411-440`）；写入口只有 import（`src/application/importing/referenced/runtime.py:567-569`）与 sync apply（`src/application/sources/service.py:287,295-323`）。
- Run 命令面无 grant 字段（`src/bootstrap/core_service.py:5867-5923`）；host-control 闭集无授权建立命令（`:355-364`）；scan 铸 grant 但不绑 page binding。
- 结果：除 import/sync 后 ≤300s 窗口外，provider 读图与 commit guard 均 typed 失败（`src/bootstrap/core_assembly.py:1773`、`src/infrastructure/sqlite/pipeline.py:897-899`）。

目标：新增一个 **Host→Core host-control 授权建立命令**，让 Host 在 Run dispatch 前把已铸 grant 绑定到本次 Run 的目标页 binding；**不改 Run wire、不改 schema/依赖、不加错误码、不改 grant 形状/TTL/撤销语义**。identity/facts 回退路径被否决（会重开 `FEA-09-impl-r1` R1-I002，folder 源失配，并违反 C-17 §7.2/§7.3 单一选择规则）。

## 2. 提议修订

### A. C-06 v1.2（`doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md`）

1. 头部状态行 → `FROZEN v1.2（2026-11-06 重冻；v1.0 2026-11-01 / v1.1 2026-11-03）` + 本载体/冻结记录链接；日期行追加 v1.2。
2. §2.2 新增一行 **「授权建立（v1.2，第三生产者）」**：source-read grant→page binding 的读授权可由 Core 的 host-control 授权建立命令（C-16 v1.3 §2.4）在 Run dispatch 前建立；Core 用与 Run 相同的 scope 展开器解析目标页，按签名 grant 的四维 scope/facts 校验当前 healthy binding 后，写入与导入/同步同构的进程内映射（零 DB 写）；不延长 ≤300s、不改变撤销/失联、不得路径回退；同一 binding 允许多份 grant，读时选择沿用 `find_bound_for_source`（live、最高 generation/grant_id）；失败必须 typed 且零业务写。
3. §2.3 命令表新增一行 `AuthorizeSourceReadForRun`（Host→Core，host-control；入参 `{grant_ids[], command, scope}`，`command` 限定为可由 scope 展开的 Run 起始命令；成功 `{bound_pages}`；任一目标页不可授权 → 整体 typed 失败、零绑定写入；Host 不得 dispatch）。
4. §6 变更记录追加 v1.2 行（§5 条件 4 **不修改**；v1.2 additive 说明由 C-16 §0 与冻结记录承载）。

### B. C-16 v1.3（`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`）

1. 头部状态行 → `FROZEN v1.3（2026-11-06 重冻；v1.0 2026-11-03 / v1.1 2026-11-04）` + 本载体/冻结记录链接；日期行追加 v1.3。
2. §0「source-access wire」行 → `source-access-wire/1.2`（v1.3 仅 additive：§2.4 新命令 + 能力）；能力列表追加 **`source.read.run/1`**（缺失 → 不铸/不绑定、按现状 dispatch；不得用未知命令探测）。
3. 新增 **§2.4 `AuthorizeSourceReadForRun`**：closed-shape 请求 `{grant_ids[], command, scope}`（`command` 限定为可由 scope 展开的 Run 起始命令）；成功响应 `{bound_pages}`；校验顺序（host-only → session → shape → 每个 grant live/expiry/revoked → 同一 Run scope 展开器）；per-page 匹配（managed 跳过；binding 非 healthy/gate 非 open → 不可授权；否则按签名 scope 的 source_id/version/entry(locator|ordinal|entry_key)+facts 逐项核对 `source_entries`/`source_locations`，**无路径回退**；gate 沿用 Run 目标/commit guard 的同一谓词，不引入第三套）；任一页不可授权 → **整体 typed `SOURCE_ACCESS_DENIED`（details `{refused_pages}`）且零映射写入**（不返回部分成功）；全部成功 → 写进程内映射并返回 `bound_pages`；**零 DB 写/不建 plan/不发布资源/不延长 TTL/幂等**；错误码沿用 §6 闭集（不新增）；`details` 仅计数/ID。
4. §10 冻结条件追加 v1.3 条目；变更记录追加 v1.3 行。

### C. 冻结记录与矩阵

- `doc/plan/FEA-CONTRACT-FROZEN-C06.md`：pin → C-06 v1.2 最终字节 sha256；新增 §6 v1.2 UNFREEZE 重冻（载体/触发/修订/复核/冻结字节/历史 pin/其余 16 pins 断言）。
- `doc/plan/FEA-CONTRACT-FROZEN-C16.md`：pin → C-16 v1.3 最终字节 sha256；§1B 增历史行；§2 增 v1.3 核验行；新增 §7 v1.3 UNFREEZE 重冻。
- `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`：状态行、C-06 行、C-16 行更新（`FROZEN v1.2` / `FROZEN v1.3`）。

## 3. 兼容与影响

- 旧 Core（无 `source.read.run/1`）→ Host 以 `core.ping` 判定缺失 → 不铸/不绑定、按现状 dispatch（referenced Run 仍 typed 失败；既有 managed Run 零变化）。
- 旧 Host × 新 Core：不发送新命令；import/sync/scan 授权面零变化。
- 无 schema/migration/依赖变化；`CORE_PROTOCOL_MINOR` 仍 3；Run 请求/响应字节零变化；M2-C1 不改（HostControl 枚举滞后登记 follow-up）。
- 其余 16 份冻结契约逐字节不变（复核须给出 16/16 断言与 `verify_pins 18/18` 证据）。

## 4. 风险与回退

- 风险：①2/18 pins 重签，必须独立 byte-level 复核；②命令语义若被实现者放宽（路径回退/身份回退/延长 TTL）将破坏 C-06 不变量——实现卡 AC 明确禁止；③300s 生命周期（L-G1）、Core 重启（L-G9）、加密 referenced Run（L-G2）、L-R11 两读面 gate 不一致（L-G10）仍由实现卡/后续卡登记 limitation；④M2-C1 文档滞后（L-P1 follow-up）。
- 回退：若独立复核否决或用户要求回退，恢复 C-06 v1.1 字节（sha `8faa8cd139f2e9c599dcd34063a5ac1a85941ecac287fcd693eb43d2109b2003`）与 C-16 v1.1 字节（sha `0b9511a55ea15fafdc2de7d33fb204e5c7e2cf2efed69977ee6dd092f22e5905`），并还原冻结记录/矩阵；`FEA-11-RUN-GRANT-1` 不释放。

## 5. 独立复核要求

- Reviewer：未参与本提案起草/前轮复核的 fresh subagent；只读工作树被审字节；记录 session 与 reviewed_head。
- 复核对象：**最终工作树字节**（C-06 v1.2、C-16 v1.3、两份冻结记录、矩阵、本载体、`verification/FEA-11-RUN-GRANT-1-PREREQ-1/**` 证据）。
- 必须核对：①本载体 §2 各项是否逐项落地；②改动只限两份契约的登记段落（diff 逐行）；③既有 grant 四维 scope/TTL≤300s/撤销/失联/错误闭集/§7 脱敏/WireLog 口径零改动；④未改 Run wire/`CORE_PROTOCOL_MINOR`/schema/依赖/M2-C1；⑤pin 值可由 `Get-FileHash` 复算，`verify_pins.ps1` 18/18，其余 16 项逐字节不变；⑥冻结记录 §1A/§1B 口径与历史 pin 保留；⑦载体/卡面未夸大（不写「产品可用」）。
- 通过标准：`approved`（可含非阻断 P3，须记录）；随后 DSH 提交 UNFREEZE 提交并重跑 pins；未通过 → 返修后窄面复审，不得先提交后补审。

## 6. 复核结果（独立 byte-level）

- **r1（`doc/reviews/FEA-11-RUN-GRANT-1-PREREQ-1-r1.md`）**：`changes_requested`，**P0=0 / P1=1 / P2=5 / P3=8**；契约字节本身无 P0/P1（不变量零改动、pins 18/18、16 项不变、Run wire 零 diff 均实测通过）；P1 为卡面能力缺口口径冲突；P2-1/P2-2（refused 响应 vs typed 失败、facts 校验）、P2-5（gate 口径）、P3 若干为契约文本精度问题 → DSH 已按 findings 处置（见下）。
- **处置（2026-11-06）**：C-06 v1.2 / C-16 v1.3 精确化（①命令失败语义统一为「整体 typed `SOURCE_ACCESS_DENIED`、零绑定写入、不返回部分成功」；②per-page 匹配补 facts 物理身份核验；③gate 明确沿用 Run 目标/commit guard 同一谓词，不引入第三套、L-R11 差异不在本命令；④`command` 限定为可由 scope 展开的 Run 起始命令）；卡 D-4/I-3 对齐「能力缺失 → 不铸/不绑、按现状 dispatch」；冻结记录/载体补 L-G2/L-R11/L-G10 与复核时间。**契约字节因此重算 pin 并重跑 pins 18/18。**
- **delta 复核 r2（`doc/reviews/FEA-11-RUN-GRANT-1-PREREQ-1-r2.md`）**：`changes_requested`，**P0=0 / P1=0 / P2=2 / P3=9**；r1 的 P1 与全部 P2 关闭；契约字节无不变量/证据问题（pins 18/18、16 项不变、Run wire 零 diff）。两项 P2 均在**登记面**：N-01（冻结记录/载体写「17 pins」，本批 2/18 重签应为 16）；N-02（C-06 §5 条件 4 的 v1.2 追加句未登记）。处置（2026-11-06）：**回退 C-06 §5 条件 4 追加句**（保持「仅新增条目」口径；additive 事实由 C-16 §0 与冻结记录承载），修正 17→16（含载体 §2.C），补 FROZEN-C06 §2 v1.2 核验行；C-06 因此重算 pin（`99831a20…`），C-16 pin 不变（`7c355ccb…`）；r1/r2 中间态字节保留记录，r3 复核最终字节。
- **P3 残余处置（按 r2 编号 P3-1…P3-9）**：P3-1（§2.4 置于 §2 下）为有意结构，接受；P3-2（「复用 §6 闭集」措辞未含 M2-C1 §5.7 envelope 既有码）接受并在此注明「§6 闭集 + M2-C1 §5.7 envelope 既有码，不新增」；P3-3（C-06 §2.3 末尾仍写「本组命令 v1.1」）为历史版本说明，不误导本批命令，接受；P3-4 已由 FROZEN-C06 §2 新增 v1.2 条件行覆盖；P3-5（`command` 措辞）接受（C-16 已写 `COMMAND_CATALOG` + Run 起始语义，卡面为中文释义）；P3-6（folder 源 facts 与 `source_locations` 映射精度）登记为**实现卡注意项**（容器源单 entry facts ↔ source_locations；folder 逐成员 facts ↔ source_entries），不改变「无路径回退」；P3-7（`carrier.md` 为逐字节副本）接受为证据快照，DSH 在本节追加结论后同步副本；P3-8 已在本节与卡面回填 r1/r2/r3 session 与 reviewed_head；P3-9（v1.1 pin 重复）登记为下轮记录维护去重。上述均**不涉及**契约条款、不变量或证据真实性。
- **最终字节窄面复核 r3（`doc/reviews/FEA-11-RUN-GRANT-1-PREREQ-1-r3.md`）**：**`approved`**，**P0=0 / P1=0**；N-01/N-02 关闭；字节面（C-06 `99831a20…`、C-16 `7c355ccb…` = 冻结记录 pin；pins **18/18**；其余 **16/16** 实算不变；Run wire/`PROTOCOL_MINOR=3`/schema/依赖/M2-C1/不变量零改动；证据可复算）全部通过；r3 仅 1 项非阻断 P2（载体 §6 P3 引用编号，已在本节按 r2 编号更正）+ 5 项 P3（上述处置）。**r3 session `3f908eee-d3a0-4698-b06d-a58e0fecacf9`；reviewed_head `b17d7282193afa6583c6c7a7bfc6456d04313af5`。**
- **结论**：UNFREEZE 通过独立 byte-level 复核（r1→r2→r3 approved，P0=0/P1=0），可提交并重冻。

## 7. 证据

- `verification/FEA-11-RUN-GRANT-1-PREREQ-1/pre-post.sha256`（两份契约改前/改后 sha256）
- `verification/FEA-11-RUN-GRANT-1-PREREQ-1/changed-lines.diff`（`git diff` 原始输出）
- `verification/FEA-11-RUN-GRANT-1-PREREQ-1/other-16-pins.txt`（其余 16 契约逐项 sha256 与不变断言）
- `verification/FEA-11-RUN-GRANT-1-PREREQ-1/logs/pins.log`、`logs/check.log`
