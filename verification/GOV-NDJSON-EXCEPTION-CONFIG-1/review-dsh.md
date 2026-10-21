# DeepSeek 独立 Review

session: session-e1b0c15e-3fee-48ca-8b63-b09dbf8b39ed；exit 0；web_visibility=unverified

## 结论

**approved**（仅批准本 Task 的 2 个代码/配置路径及自身 Task 证据实现；不批准资源清理、GC/prune/push、父 Task done 或“只剩 main”。）

## 固定身份

| 项 | 值 |
|---|---|
| reviewed_head | `85a393dc43eaf60df20258040d5869b42700d2c5` |
| diff_base | `98993fe10dad65311c1c64de2ae73aaa8831a23a` |
| source 实现 | `7fd00e8b4a1ec53440aac64b4d44566761579cd6` |
| main | `b703878299d8d7604c4584dea5d319dce3bc50b2` |
| branch | `codex/gov-ndjson-exception-config-1` |
| 变更路径 | `tools/governance/clean_workspace.py`、`tools/governance/non-declaration-json-exceptions.json` |

## P0 / P1 / P2

- **P0：无**
- **P1：无**
- **P2（非阻断，证据快照标注）**：`configuration-proof.json`/`candidate-default-audit.json` 记录的是 `2427 declarations / 1764 protected roots`；本次对**当前 canonical main 数据**实测为 `2441 / 1778`。差额 14 与 canonical 主数据中的 14 份证据副本数量一致；候选与基线仍同集合，30 个错误不变。建议在 proof 中注明 snapshot commit/time，避免把 1764 误称为当前 main 的实时值。

## 关键实测

- **AST**：移除 `DEFAULT_JSON_EXCEPTION_MANIFEST` 赋值后，base 与候选 AST 完全相同；实现 commit `7fd00e8b4` 仅改此常量并新增配置，未改解析逻辑。
- **配置**：`69 = 67 + 2`；前 67 项与历史表逐项相等，路径无重复；新增两项与 `configuration-proof.json.new_entries` 完全相等。
- **历史表 pin**：`cacd1c021:...` 内容 SHA-256 = `c2f185fb489e4b89be28cdfb139eb649c7022a718d0d27877be4ca0d8fa4adc4`；HEAD 同 pin；磁盘 raw = `238039dd3a9a70243ff8ffaee8dbf5b080e211cb8dc747de1a5da29211efdef2`（既有 CRLF 差异，未误称 raw=pin）。
- **两条 NDJSON**：R23 磁盘 `bdabb170...f7a1`，未跟踪且 WT 中不存在；R24 磁盘与 main Git 内容均 `caac6afd...458e`。
- **实际 parser 注册**：候选模块扫描 canonical main 得 `30 errors / 1778 protected roots / 2441 declarations`；base 模块同数据得 `32 / 1778 / 2441`。仅移除两条指定 `JSON_PARSE`，其余 30 个错误逐项相等，保护集合及声明身份完全相等；R23 在 base 仍 fatal，在候选中成为精确 `JSON_NON_DECLARATION` warning。
- **精确匹配时序**：哈希匹配发生在 `load_json` 解码之前；不是通用坏 JSON 豁免。
- **diff/check**：`git diff --check 98993fe10..85a393dc4` 退出 0；3 个 caller 未改，仅共享 guard 默认入口。
- **治理 check**：canonical main 运行 `tools/governance/check.ps1` 为 **PASS (2 warnings)**，退出 0；warning 为非终态 Task 数量与 STATUS 预算，不是失败。
- **日志**：29 声明测试、80 安全回归均 `OK`；双回放各 `15 REJECT / 0 deleted / 0 violations`；`test-execution.json` 可解析且两条命令 exit 0。

## 未测 / 未复算

- **14 个自有证据的 raw SHA = Git blob = 表内 SHA：NOT_RUN**。本次复核脚本字段列错位，未形成有效结论；因此不声称这 14 个 SHA 已独立通过。核心代码、配置、历史表及两条 NDJSON 已完成独立核验。
- **109 项测试与 CLI exit 2/30：Owner 实测，Reviewer 未复跑**。日志与 `candidate-default-audit.json` 可解析，但该 JSON 未直接暴露 CLI exit 字段。
- **产品/构建：NOT_RUN**，与治理配置变更范围一致。

## 边界

批准仅覆盖上述 2 个代码/配置路径、Task/Handoff 及 `verification/GOV-NDJSON-EXCEPTION-CONFIG-1` 自身证据；允许 Codex 随后正常合并并在 main 复跑默认审计、pin 注册和治理 check。30 个残余错误继续 fail-closed；STATUS/r212 清理禁令、父 Task blocked 均不解除。后续 6 个 `NOT_APPLICABLE`/表格格式任务仍须另冻结，不在本 Review 实现范围。本次仅只读，未执行写文件、ACL、refs、checkout/commit/apply、清理、联网或派发。
