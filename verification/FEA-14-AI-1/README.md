# FEA-14-AI-1 证据索引（提示词模板）

- Task：`FEA-14-AI-1`（FEA-14 S5 AI 切片；复用 PREQ 预冻结 wire P21–P25）
- 实现提交：`1b5bdb1f2`（r1 处置后；初版 `13d9e39e1` → v14 适配 `aac1aba9d` → r1 处置 `1b5bdb1f2`；base `36c4376d1` = EDIT-1 收口 + AI-1 冻结提交）
- 日期：2026-11-10
- 日志生成口径：4 个 Canonical 日志均于本轮门禁在 **`1b5bdb1f2`** 生成，头行记录生成时 HEAD 与 `git status --short`（同批顺序生成，后生成的日志会看到前序日志/证据目录未提交；产品字节均为 `1b5bdb1f2`）。README 与证据表在日志之后写入，属证据簿记，不含产品字节。

## 结论状态

| AC | 判别 | 结果 |
|---|---|---|
| AC1 数据面/v14 | `prompt_templates`（唯一 name、version、软删）+ `prompt_template_references` additve 建表 + 索引；v1–v13 字节不变；旧库升级无损 | **MET**：schema **v14** 仅新增两表 + `idx_prompt_templates_name`（`WHERE deleted_at IS NULL`，软删不占名）/`idx_prompt_template_references_template`；迁移测试先升 v13、插入真实 book 行、再升 v14 并做行级快照比较 |
| AC2 P21/P24 列表与复制 | 列表 = 内置常量 + 未软删自建；`builtin`/`builtin_count`；P24 复制 version=1 | **MET**：P21 返回内置 2 条 + 自建（`builtin` 标记、`builtin_count`）；P24 复制内置（缺省名 `"<builtin> (copy)"`、显式名、重名 → `TEMPLATE_NAME_EXISTS`、未知 builtin → `TARGET_NOT_FOUND`） |
| AC3 P22 保存 | 新建 v1 / 更新 v+1；name 唯一；body 非空；内置不可覆盖 | **MET**：新建 version=1、按 id 更新 version+1；重名（跨模板或更新到已有名）→ `TEMPLATE_NAME_EXISTS/conflict`；空 name/body、超长 → `INVALID_REQUEST`；内置 id → `INVALID_REQUEST` |
| AC4 P23/P25 删除与引用 | P25 列引用；P23 强制 replacement，引用重指派后软删 | **MET**：P25 返回 `{kind,owner_id,label}`（无引用 = 空数组，内置也返回空）；P23 缺失/空/自身/内置/不存在 replacement → typed；成功路径引用行指向 replacement、目标 soft-delete 后列表不可见、再次删除 → `TARGET_NOT_FOUND`；**重指派+软删为单事务（F-01 修复，故障注入回滚测试）** |
| AC5 契约/门禁 | C-07 UNFREEZE v1.8（79/86）成员表逐行 = stdout；S5 25/25；pin 重算 | **MET**：inventory **79/86**，正式成员表 79 方法 + 4 非方法 = stdout（`ALL_MATCH: True`，含 `Changed（事件）`）；S5 计划节无待实现行（25/25 全部落地）；v1.8 pin `8ccaba05…`（v1.7 原值保留）；`--check` EXIT 0、`verify_pins` 18/18 |
| AC6 证据 | 定向/回归/App.Tests、日志 EXIT、NOT_RUN | **MET**：见下表与 NOT_RUN |

## 门禁与证据（本目录）

| 文件 | 内容 | EXIT |
|---|---|---|
| `logs/pytest-ai.log` | `test_prompt_templates.py` + `test_prompt_template_wire.py` **8 passed**（含事务故障注入） | 0 |
| `logs/regression-v14.log` | v14 回归：storage+core+fea09+fea11 **1268 passed** | 0 |
| `logs/dotnet-app-tests.log` | App.Tests 全量 **888 passed / 0 failed / 11 skipped**（5m36s） | 0 |
| `logs/pins-api.log` | `verify_pins` 18/18（C07=`8ccaba05cbc2`）、`generate_api_inventory.py --check` EXIT 0（79/86） | 0 |

**提交同步更新**：`doc/plan/FEA-C07_API_INVENTORY.md`（成员表 = 脚本 stdout，79 方法 + 4 非方法成员；S5 计划节 25/25 全部落地）、`doc/plan/FEA-CONTRACT-FROZEN-C07.md`（§1 v1.7/v1.8 pin 链、§1B、§2 条件 3 `1/79/6=86`、§3、§5）、`doc/reviews/CONTRACT-UNFREEZE-2026-11-10-AI1.md`。

## r1 处置（2026-11-10，对 `41d54395a` 的 changes_requested）

- **F-01（P2，已修）**：P23 的「引用重指派 + 软删」原为两次 store 提交（可半删）→ 合并为 store 单事务 `delete_with_reassign`；补故障注入测试（软删语句抛错 → 整体回滚：引用仍指向目标、目标仍可见）。
- **F-02（P2，已修）**：C-07 成员表重建时把 `Changed` 误标「属性」→ 改回「事件」；逐行 `ALL_MATCH: True`；pin `58dbae4c…`→`8ccaba05…`，FROZEN/载体/README/卡面同步。
- **F-03（P3，登记）**：`UPDATE OR REPLACE` 在 replacement 已有同 `(kind,owner_id)` 引用时覆盖该行 label（引用身份不丢）；引用写入方未启用，AI-2/维护卡可改 UPSERT 合并策略。
- **F-04（P3，接受）**：P22 no-op 保存也 version+1（卡面已写明「每次保存 +1」）。
- **F-05（P3，登记）**：`name` 唯一仅覆盖未软删行、不覆盖内置名、未做大小写/空白规范化（重名规范化待 ADJ 裁决，留 AI-2/后续 errata）。
- **F-06（P3，已修/说明）**：`test_issue_markers` 的 v13 迁移测试现跨 v13→v14，补注释说明断言口径（v13 表/索引存在 + 旧行无损）。
- **F-07（P3，已修）**：Fake 与 Core 语义对齐（未知 id 保存 → null、名称唯一、delete 校验 replacement、引用按模板 id 存储）。
- **F-08（P3，已裁决登记）**：DDL §2.4「`version`（不可变）」裁决为「调用方不可指定、Core 单调 +1 管理」，P22 更新必然递增；跨卡口径以卡面「裁决」为准。
- **F-09（P3，已修）**：`test_upgrade_schema_data.py` 的 `LATEST_TABLES` 补 v10–v14 新表，消除既有表覆盖漂移。

## 设计说明与 limitation

- **内置模板**：Core 常量 `BUILTIN_PROMPT_TEMPLATES`（本卡 2 条，不落库）；P22/P23 对内置 id typed 拒绝；P24 复制为自建（version=1）。内置集合的最终内容/文案属 AI-2/UI 卡。
- **版本语义**：自建模板 `version` 从 1 起、P22 更新 +1（调用方不可指定）；`name` 未软删行唯一。
- **删除语义**：P23 强制 replacement（必填、存在、非自身、非内置）；引用行与目标软删在**同一 store 事务**内完成（`delete_with_reassign`）；引用表由译文/任务/规则卡写入，本卡只读/重指派。
- **P24 客户端投影 limitation**：wire 只回 `template_id`，`CoreServiceClient.CopyBuiltinPromptTemplateAsync` 返回的 `PromptTemplateInfo` 中 `Name` 为空串（未显式传 name 时）、`Version=1`；UI 应通过 P21 刷新（与 FONT 系列 P2 投影 limitation 同类）。
- **无 AI/网络调用**：PREQ §6 明确本清单不触发网络/AI 调用；本卡只做模板数据面。
- C-07 契约只按流程改统计/成员表（UNFREEZE v1.8），无其他契约字节；S5 计划 25 条全部落地（74+5=79 / 81+5=86，与 PREQ 目标一致）。

## NOT_RUN（不得记 PASS）

- 模板 UI/编辑器/预览、内置模板最终文案 = NOT_RUN（AI-2/UI 卡）。
- 真实 AI 模型/网络调用 = NOT_RUN（PREQ 明确本清单不触发）。
- 真实 Host↔Core 进程级联调：5 个新 `CoreServiceClient` 方法未对活 Core 调用；C# 5 个端口测试覆盖 NullHost 降级 + Fake 记录/内置只读/删除/引用迁移，但**不覆盖真实 IPC 读写映射**。
- 引用表写入方（译文/任务/规则引用）= NOT_RUN（本卡不创建引用；删除重指派用测试 fixture 验证）。
- 并发（同一模板并发 save/delete）、万级模板性能、真实大库迁移 = NOT_RUN。
- FEA-15 正式验收声明未审。

## 复现

```powershell
python -m pytest tests/storage/test_prompt_templates.py tests/core/test_prompt_template_wire.py -q
python -m pytest tests/storage tests/core tests/fea09/test_v7_migration.py tests/fea11/test_source_gate_unify.py -q
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo
python tools/generate_api_inventory.py --check
pwsh -NoProfile -File tools/governance/verify_pins.ps1
```
