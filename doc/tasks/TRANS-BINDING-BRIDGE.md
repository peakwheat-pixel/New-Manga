---
id: TRANS-BINDING-BRIDGE
title: 自动翻译配置桥：把 P15 profile/能力绑定镜像进 Run 侧 settings.providers.profiles
kind: implementation
governance_version: 3
status: closed_with_limitations
disposition: "L1-T-A（2026-11-14 DSH 释放）；依据 MAINT-1-AUTO-TRANSLATE-FEASIBILITY-2026-11-14 §7/§9"
approval: DSH 2026-11-14 释放（评估结论：零冻结契约改动、零 UNFREEZE；本卡是自动翻译唯一必做的新代码）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - MAINT-1-RELEASE-MONITOR
base_commit: 73a182a61
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 3db81c4f0
delivery_head: 659bb3053
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/TRANS-BINDING-BRIDGE
allowed_paths:
  - doc/tasks/TRANS-BINDING-BRIDGE.md
  - doc/reviews/TRANS-BINDING-BRIDGE-*.md
  - verification/TRANS-BINDING-BRIDGE/**
  - src/application/settings/**
  - src/infrastructure/providers/**
  - src/bootstrap/**
  - tests/**
out_of_scope:
  - 冻结契约字节（C-01b…C-17、M2-C1、ADJ-001）
  - 新增 Core wire 命令、新增 IHostController 成员
  - schema/DDL 变更、依赖变更、远端写操作
  - apps/**（Host/UI 侧由 T-B/T-C 承担）
  - doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/TASK_LEDGER.md（DSH 维护）
---

# TRANS-BINDING-BRIDGE：自动翻译配置桥

## 问题（评估 §0 / §5）

Run 运行时读取的是 `pipeline_defaults.settings["providers"]["profiles"]`（`src/infrastructure/providers/runtime.py:182-193` 的 `_profile_settings`），而 Settings 的 P15 profile / 能力绑定只写 JSON store（`src/bootstrap/settings_commands.py:590-682`）。**两者之间没有生产写入方**，因此 `translate` 步骤取不到 binding，停在 `PROVIDER_NOT_CONFIGURED`（`src/infrastructure/providers/handlers.py:1266-1274`）。

这正是「用户配好 Provider、点了翻译、仍报未配置」的根因。

## Acceptance Criteria

- [x] **AC1 镜像写入**：当 P15 profile 或能力绑定写入成功后，同一事务/同一 seam 内把对应条目镜像进 `pipeline_defaults.settings["providers"]["profiles"]`；镜像形状与 `runtime.py` 读取的键一致（至少 `provider_type` / `base_url` / `model` / `credential_ref` / `capabilities`）。 <<MET>>
- [x] **AC2 只含引用、不含密钥**：镜像**绝不**包含 secret 本体，只含 `credential_ref`（与 `REAL-TRANSLATE-PROVIDER-1` 的既有纪律一致）。 <<MET>>
- [x] **AC3 fail-closed**：镜像写入失败必须 typed 失败并回滚，不允许「JSON store 写了、镜像没写」的半写状态。 <<MET>>
- [x] **AC4 复用既有 seam**：优先复用 `PipelineDefaultsService.save_settings_section`（`src/bootstrap/core_service.py:3106-3113`）这一 seam，**不新增 wire 命令**。 <<MET>>
- [x] **AC5 不新增契约面**：不新增 Core wire 命令、不新增 `IHostController` 成员；`generate_api_inventory.py --check` 维持 `1/80/6=87`；`verify_pins` 18/18。 <<MET>>
- [x] **AC6 判别测试**：至少一条「写入 profile+binding 后，`_profile_settings` 能读到该 profile」的测试；再一条「镜像失败 → 不留半写」的测试。 <<MET>>
- [x] **AC7 门禁**：`check.ps1`（默认 + 本卡 TaskPath）、`verify_pins`、`generate_api_inventory --check`、受影响 pytest 全绿。 <<MET>>
- [x] **AC8 生效时机说明**：在卡面与证据里写明「装配期一次性闭包 settings（`core_assembly.py:1421-1423`）⇒ 配置变更需重启 Core 才生效」，供 T-C 的 UI 文案使用。 <<MET>>

## 允许修改范围

见 front matter `allowed_paths`。**不得**改 `apps/**`（Host/UI 属 T-B/T-C）。

## 禁止范围

冻结契约字节、新 wire 命令、新端口成员、schema/DDL、依赖、远端写、三指针。

## 测试要求

Python：`C:\Python314\python.exe -m pytest`（定向 + 全量不得新增 failed）。

## 风险

- 镜像与 store 双写可能引入一致性窗口：AC3 的 fail-closed 是硬要求。
- `settings["providers"]` 的存储位置需先确认（DB settings 表 vs JSON），**先取证再改**。
- 若发现镜像必须改冻结契约才能表达，**停下回卡报 DSH**，不得擅自 UNFREEZE。

## 证据计划

`verification/TRANS-BINDING-BRIDGE/README.md` + `logs/`（测试与门禁原始输出、镜像前后快照）。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-1 | AC1-AC8 | verification/TRANS-BINDING-BRIDGE/README.md | 3db81c4f0 | 04c72ac2b9697b86277cc2576547301682ba134a2952046c905d50a288b69e13 | canonical |
| EV-2 | AC1-AC8 | verification/TRANS-BINDING-BRIDGE/logs/gates-final.log | 3db81c4f0 | 2a04ec121fc9b9417270959df0afb64a0df5c5d4e6ef6b6ba3f8ad89e7e53acb | canonical |
| EV-3 | AC1-AC8 | verification/TRANS-BINDING-BRIDGE/logs/pytest-full.log | 3db81c4f0 | 530109d7ce114d54e016137f6b612bcdf2e494d2756955ec2dcdfe91dfb66280 | canonical |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | `G:\CODEX\New Manga`（main） | NOT_APPLICABLE | - | - | 复用主工作树 |
| evidence（仓库） | `verification/TRANS-BINDING-BRIDGE/**` | NOT_APPLICABLE | 仓库内 | `verification/TRANS-BINDING-BRIDGE/EV`（见 Canonical Evidence） | 门禁/测试原始日志已保留 |

## Closeout Record

- **收口（2026-11-14，DSH）**：`closed_with_limitations`。AC1–AC8 全部 `MET`；r1 `changes_requested`（P1-1 scope、P1-2 反向半写）→ 返修 → r2 `approved`；R2-001（`sqlite3.Error` 未捕获）→ 返修 → **r3 `approved`**（R2-001 真实关闭；矩阵 6/6 复算一致；`BindingValidationError` 确认为冗余成员）。
- **交付**：`94b8f33f5`（初版）→ `659bb3053`（r1 处置）→ `3db81c4f0`（R2-001）。全量 pytest **3562/0/10**；定向 **119 passed**；四件套绿；`apps/**` 与 `doc/contracts/**` **零改动**。
- **limitation（已如实登记，不得读作无缺口）**：
  1. **回滚本身失败**（SQLite 持续不可写等）⇒ 可能留「镜像新值 / JSON 旧值」，只抛 typed 失败，无二次修复；两存储**无跨库事务**。
  2. **两次写之间进程被强杀** ⇒ 无崩溃恢复标记、无跨库 WAL 协调。
  3. **JSON 文件被外部并发改写** ⇒ store 读-改-原子写的丢失更新（既有风险，与本桥无关）。
  4. **book/chapter scope 绑定不驱动执行**（R-6）⇒ 扁平槽只接受 global，仅配 book-scope 仍会 `PROVIDER_NOT_CONFIGURED`；根治需改 run 快照结构，已归入 T-C 前置约束。
- **P3（证据文本，r3 登记）**：README `:94` 的捕获元组漏写 `sqlite3.Error`；README `:137`/`test:536-539` 对 `ValueError` 敏感性的表述不准。**非阻断，未在本轮修**。
- **删除/迁移/归档**：0。

## 交付记录（2026-11-14）

- **commit**：`94b8f33f5`（6 文件，+860/−19）。
- **取证（重要，比卡面表述更精确）**：
  - `settings["providers"]["profiles"]` 存在 **SQLite `pipeline_defaults` 表**的 `settings_json` 列（`schema.py:431-437`、`pipeline.py:1766-1786`），**不是**独立 JSON 文件。
  - `PROVIDER_NOT_CONFIGURED` 的直接来源是 `_chain` 读 `run.provider_binding_snapshot[step]`（`handlers.py:1266-1274`）⇒ **只镜像 profiles 不够，必须同时写 `provider_bindings[step]`**。已按此实现双写。
  - P15 profile/binding 存 JSON 文件（`data_root/settings`，`core_assembly.py:1943-1945`）。
  - legacy QML 设置已有同投影参考：`src/ui/viewmodels/settings/viewmodel.py:453-475`、`:405`、`:52-57`。
- **结果**：全量 pytest **3551/0/10**（基线 3544 → +7）；定向 108 passed；四件套全绿；`--check` 维持 `1/80/6=87`；`apps/**` 零改动。
- **判别力实测**：把镜像 no-op 后 `profiles=[]`、`bindings={}`，相关断言必红。

## DSH 裁决（2026-11-14）

### R-1 接受 AC3 的「mirror-first + 回滚」口径（不判 PARTIAL）

跨两个存储（JSON store 与 SQLite `pipeline_defaults`）**没有跨库事务**是客观限制。卡面 AC3 的原意是排除「store 写了、镜像没写」这一方向，该方向已被**结构上**排除（mirror-first），故按 PASS 计。反向窗口（镜像已写、store 失败、回滚再失败）只能「尽力回滚 + typed 失败」，已在证据 README §5.3 显式披露。**若未来引入跨库事务能力，须重估本项。**

### R-2 接受 credential 写入接线为 AC1 的实质要求（非越权）

不镜像 `credential_ref` 会导致「profile 已建、key 已绑、运行侧仍无凭据」⇒ 认证失败，与本卡目标直接冲突。故 `BindProfileCredential`/`ClearProfileCredential` 的接线属 **AC1 的必要组成**，不判定 scope 扩张。

### R-3 networks 镜像**另开卡**，不在本卡

legacy QML 还镜像 `settings["providers"]["networks"]`（`viewmodel.py:485-520`）。本卡范围只覆盖 profiles/bindings/credential；networks 属**既有缺口**（`proxy_policy=profile` 且依赖网络 profile 时才会暴露），另立 T-D 处理。本卡证据 README §5 已登记为范围外。

### R-4 写入 T-C 的硬要求

`provider_runtime_mirror` 目前只被 `settings_commands.py` 消费。**T-C（及后续任何 Host 侧改配置路径）必须走同一条 Core 命令面**；否则镜像只在一条路径上生效，会出现「UI 改配置后仍 `PROVIDER_NOT_CONFIGURED`」的假死。此条已登记为 T-C 的前置约束。

### R-5 证据与门禁

全量 pytest 3551/0/10、四件套全绿、`--check` 1/80/6=87、`apps/**` 零改动 —— 均以本卡证据 README 为准；独立复核 `TRANS-BINDING-BRIDGE-r1.md` 待派。

## 返修记录（2026-11-14，`659bb3053`）

r1 复核 `changes_requested` 后返修：

- **P1-1 scope 真 bug 已修**。取证：执行链只读**扁平** step 槽（`handlers.py:1267` 的 `_chain` 读 `run.provider_binding_snapshot.get(step_type)`；同读取点 `executor.py:27`、`projection.py:285`、`service.py:797`），`pipeline_defaults.provider_bindings` 是 `{step: profile_id}` 扁平表（`pipeline_defaults.py:62-103`、`pipeline.py:1766-1786`），`provider_binding_snapshot[_p15_settings_snapshot]` 的 book/chapter 解析结果**仅供 resolve 显示**（`core_service.py:6707-6709`）。⇒ **只有 global scope 可写/可清扁平槽**；book/chapter 只落 P15 JSON 行。
  - 改动：`settings_commands.py` 的 `_bindings_set` / `_bindings_clear` 增加 `writes_flat_slot` / `clears_flat_slot = scope["kind"] == "global"`。
  - 新增 3 例：global→book 不覆盖全局；clear book 不动全局；clear chapter 不动全局。
- **P1-2 反向半写已修**。`_write_with_rollback` 捕获扩为 `(BindingValidationError, KeyError, OSError, TypeError, ValueError)`，选型原则是「两个协作者实际会抛的异常族」，**故意不捕获裸 `Exception`**（`AttributeError`/`NameError` 必须响亮）。
  - 新增 4 例反向：`update_profile` 抛 `KeyError`（r1 实测那条）、`add_profile` 抛 `OSError`、`delete_profile` 抛 `OSError`、`save_bindings` 抛 `OSError`；均断言 typed `SETTINGS_UNAVAILABLE` + 镜像回到调用前值 + 与 JSON 侧一致。
- **证据命令已修正**：`logs/gates-final.log` 每节首行改为完整可复制命令（含 `-TaskPath doc/tasks/TRANS-BINDING-BRIDGE.md`）并重跑。
- **实测**：全量 pytest **3558/0/10**（上轮 3551 → +7）；定向 115 passed（14 bridge + 101 P15，零回归）；四件套全绿；`--check` 1/80/6=87；`apps/**` 0 改动。

## DSH 裁决 R-6：book/chapter scope 不驱动执行 —— 登记 limitation，本轮**不开卡**

- **事实**：扁平槽只接受 global，故**仅配置 book/chapter scope 绑定时 `_chain` 仍会 `PROVIDER_NOT_CONFIGURED`**（run 快照无 per-book step 槽）。
- **裁决**：接受为**已知限制**，不在本卡扩面。理由：① 全局配置已覆盖自动翻译的主用例；② 根治需给 `provider_binding_snapshot` 加 scope 维度并改执行链读取面，风险与范围都超出本桥；③ 若日后出现「不同书用不同 provider」的真实需求，再开独立卡（届时须先出 run 快照结构评估）。
- **登记位置**：本节 + `verification/TRANS-BINDING-BRIDGE/README.md` §6.2。

## 仍无法保证的反向窗口（实施者如实登记，DSH 确认）

1. **回滚本身失败**（同一 SQLite 不可写时）：吞掉回滚异常仍抛 typed 失败，可能留下「镜像新值 / JSON 旧值」；两存储**无跨库事务**。
2. **两次写之间进程被强杀**：无崩溃恢复标记。
3. **JSON 文件被外部并发改写**：读-改-原子写的丢失更新（既有风险，与本桥无关）。
4. **book/chapter scope 不驱动执行**（见 R-6）。