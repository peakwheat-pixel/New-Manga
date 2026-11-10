# CONTRACT UNFREEZE：C-07 API Inventory（v1.2，2026-11-10）

- 契约：`doc/plan/FEA-C07_API_INVENTORY.md`（冻结记录 `doc/plan/FEA-CONTRACT-FROZEN-C07.md`）
- Task：`FEA-14-S5-PREQ-1`（AC2 共用 wire 契约包）
- 授权：DSH（Lead / Architect）2026-11-10，依据 `ADJ-2026-11-10-FEA14-S5-SCOPE` §2.3 与 PREQ 卡 AC2

## 1. 变更范围（append-only 计划节，代码零改动）

| 项 | 旧（v1.1 冻结） | 新（v1.2 UNFREEZE） |
|---|---|---|
| 文件 sha256（pin） | `3fdb44e49afe9fb25e715c5a41bd247cee269c194d045e1f79946f25067dd714` | `5673b1c4b53e69ec36f1897ea5bb0ba8eeedbf437320381ee1b2a04448bf2aa6` |
| r1 复核锚（未冻结） | — | `c67c40e72938ac3d5284d778758a17e66f65d760c38e2aa7c6da548a79f47550`（r1 复核时的字节；r1 处置后 pin 已重算为新值） |
| 新增内容 | — | `## S5 计划追加（尚未实现）` 一节：25 条计划命令（FONT 4 / LIB 4 / READ 7 / EDIT 5 / AI 5），含计划返回类型、切片归属与语义摘要；状态行加 v1.2 UNFREEZE 注记 |
| 代码 | `IHostController` 54 方法；三接口合计 61 | **不变**（仍 54 / 61；`generate_api_inventory.py --check` 基线不变） |
| 旧成员/旧签名/统计 | — | **不变**（只新增一节，不删不改旧行） |

**为什么必须 UNFREEZE**：C-07 冻结记录要求「条款字节自记录起不得改动；修订须走 UNFREEZE 载体 + 重新独立复核 + 重新冻结」。本次为 FEA-14 S5 五切片**预冻结**命令面，避免每切片各走一次 UNFREEZE（五次复核成本）；计划节明确「尚未实现」，不改变代码实测统计。

## 2. 为什么是计划节而不是代码

- 本 PREQ 卡 out_of_scope 明确「不写产品代码」；25 条命令由各切片实现卡落地。
- 若现在就改 `IHostController`，会引入未实现/未测试的代码面，违反「零产品代码」与「NOT_RUN 不冒充 PASS」纪律。
- 计划节的价值：锁名称/返回类型/切片归属，防止各卡各自扩面；实现卡落地时把这些行并入正式成员表、重算统计与 pin（届时属实现卡自己的 C-07 更新，不重复本 UNFREEZE 的「名单裁决」）。

## 3. 不变量与门禁

1. 旧 54 个 `IHostController` 方法 + `IReaderProgressSink` 1 + `IRunController` 6 的签名与返回类型**零改动**。
2. `python tools/generate_api_inventory.py --check` 仍以代码实测 **1/54/6 = 61** 为基线并 EXIT 0（计划节不计入脚本统计）。
3. `pwsh -NoProfile -File tools/governance/verify_pins.ps1` 以新 pin 校验 C-07 并通过；其余 17 pins 不变。
4. `check.ps1`（默认 + `-TaskPath`）PASS。
5. 无 `src/**`/`apps/**` 实现 diff；无 DDL diff。

## 4. 独立复核（必需）

- 按 C-07 冻结语义，本次 UNFREEZE 须由**未参与本卡写作**的独立上下文 reviewer 复核：审 §1 变更范围、计划节内容、pin 重算、`--check`/`verify_pins`/`check.ps1` 实测。
- 复核结论（approved / changes_requested）追加到本文件 §5 并同步冻结记录 §1B。

## 5. 复核记录

### r1（2026-11-10，fresh 独立上下文子 agent，未参与本卡写作）

- 报告：`doc/reviews/FEA-14-S5-PREQ-1-wire-review-r1.md`。
- 结论：**changes_requested**（P0=0 / P1=1 / P2=4 / P3=5）。
  - 通过面：旧 54 方法/统计零改动；新 pin `c67c40e7…`（当时字节）三方一致；`verify_pins` 18/18 且其余 17 项逐项不变；25 条计划与 inventory/wire 一致、无重名；UNFREEZE 要素齐备、代码零改动；errata 0 pin。
  - P1/R-001：wire 缺 per-command `minor` 与 `payload 形状`；P2：R-002 errata 文件不在 allowed_paths、R-003 errata 未锚定冻结记录、R-004 prompt_templates 载体矛盾、R-005 `fonts/` 与 SC-11 未 reconcile；P3：链接/行号/日志等。
- 处置（2026-11-10，Lead）：
  - R-001：wire 新增 §8 per-command 映射（Host command id / Core wire / minor=3 计划值 / request/response keys），§1.4 措辞同步；
  - R-002：卡面 allowed_paths 增加本 ADJ 与 C01b/C09 冻结记录；卡 AC6 改 `git status --short` 范围断言；
  - R-003：`FEA-CONTRACT-FROZEN-C01b.md` / `-C09.md` 追加 2026-11-10 errata 锚点（0 pin，不改契约草案）；
  - R-004：errata 裁决 prompt_templates 统一落库、内置模板不落库/不备份；DDL 计划同步；
  - R-005：errata 澄清 `fonts/` 默认包含与 SC-11 可选性的优先级；
  - P3：inventory 链接改 `../reviews/…`、`:42→:43`、冻结记录新增 §5 v1.2 变更记录、生成 `verification/FEA-14-S5-PREQ-1/logs/`。
  - 处置后 pin 重算为 `5673b1c4…`（r1 锚 `c67c40e7…` 保留为未冻结中间值）。
- **待 r2 复核**（对处置后字节）；r2 approved 后本 UNFREEZE 视为生效，并在本文件与冻结记录 §1B 回填 approved。

## 6. 不构成什么

- 不构成任何切片实现授权；
- 不构成远端 push 授权；
- 不构成 FEA-15 正式验收。
