---
id: P15-CORE-1A
title: 设置面 Core 实现 A：G21 Provider 面 + G24 覆盖解析
kind: feature
governance_version: 2
status: done
approval: coordinator_release_20261017_split_of_P15_CORE_1
suggested_owner: Codex
owner: Codex
reviewer: dsh
depends_on: [P15-C1]
base_commit: b1f4d08c79ad8f7c11bbc945cdbeddd3ef5f6523
branch: codex/P15-CORE-1A
worktree: G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1A
integration_commit: a810ee65483f4234d207e570da3a866ffb94a62e
delivery_head: 99641c41f180abba6536715599a1809c1f620e94
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/P15-CORE-1A
---

# P15-CORE-1A：设置面 Core 实现 A：G21 Provider 面 + G24 覆盖解析

## 来源
P15-CORE-1 因契约 §5.2 的 TestNetworkProfile 目标缺口**失败关闭**，经裁决拆分为 1A/1B/1C（见 [ruling](../../verification/PROJECT-ORCHESTRATION-20261016/ruling-P15-CORE-1-network-test.md)）。**本 Task 不受该缺口影响**，可直接实现。

## 范围
实现契约 **§3.2**（Provider Profile CRUD、Capability 默认绑定）、**§3.3**（Run Snapshot 冻结查看）与 **§6**（`settings_resolve_overrides` 只读）对应的 Core 命令：`settings_provider_profiles_list/create/update/delete`、`settings_provider_bindings_set/clear/resolve`、`settings_provider_run_snapshot_get`、`settings_resolve_overrides`。

## Acceptance Criteria
- [x] **AC1**：上述命令逐字实现，参数/结果/错误与契约一致。
- [x] **AC2**：**多 Profile 同 Provider** 可表达；Capability 绑定解析顺序 **任务→章节→作品→全局**，**缺失/禁用不隐式回退**；Run Snapshot 为**创建时冻结值的只读投影**（编辑配置不改既有 Snapshot）。
- [ ] **AC3**：命令在 `core_service` 实现**并**在 `core_assembly` 的 `build_production_handlers` 注册；既有命令与语义**零变化**。
- [x] **AC4**：`settings_provider_run_snapshot_get` 返回**去路径/去引用**投影；不得含 Secret/认证头/`CredentialRef`/可解析路径。
- [x] **AC5/AC6**：见下"测试与证据"。

  **AC3 待审说明**：真实 `build_production_handlers` 是 Pipeline step handler 注册表，定义于 `src/infrastructure/providers/handlers.py`；`core_assembly` 使用其键初始化 Pipeline `known_steps`。新增 IPC 命令已注册在 `core_service` command dispatch，所需 Store 在 `core_assembly` 装配。将 IPC 命令塞入 Pipeline step 表会改变既有步骤语义；AC3 的指定注册点需要独立 Reviewer / Coordinator adjudication 后才能勾选。

## 允许 / 禁止范围
- **允许**：src/**（Python Core）、	ests/core/**（新增与必要修改，**不得弱化既有断言**）、本 Task、doc/handoffs/P15-CORE-1A-*.md、erification/P15-CORE-1A/**
- **禁止**：不得实现 G22 凭据面、G23 Network 面与 `settings_network_profiles_test`（分别属 1B/1C）
- 契约 **wire 已冻结**（doc/contracts/P15_SETTINGS_IPC_CONTRACT.md）：命令名/参数/结果/错误**逐字一致**，**不得**改名或增删字段；若发现契约问题**停下上报**，不得自行改契约；
- **不得**改 pps/desktop/**、Schema/迁移/依赖；不改 doc/STATUS.md / doc/REBASELINE_PLAN.md；不触碰用户 19 项 dirty；不 push/merge/
eset。

## 安全硬红线
Secret / 明文凭据 / 认证头 / CredentialRef / 原始响应 / 路径 / 异常文本**不得**出现在任何**返回、错误、事件**中；错误只走契约 **§9 封闭投影**的键集；CredentialRef 不得进入普通 settings DTO。

## 测试与证据
- 覆盖本范围全部 AC，**必须含反例**（非法键/类型、未授权引用、缺省路径等）；python -m pytest tests/core -q -p no:cacheprovider **全绿且不回归**（基线 **407 passed**，用 G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe）；归档原始日志 + 退出码到 erification/P15-CORE-1A/**；
- 固定 commit + doc/handoffs/P15-CORE-1A-*.md + Canonical Evidence（status: in_review；**BL-15** delivery_head 不自引用；**BL-17** commit 列**原样** git rev-parse HEAD；**BL-19** class 仅 CANONICAL/SOURCE_PIN；**BL-16/RV-P15-04** sha256 按磁盘字节且**须能从主仓库验证**；**BL-18** 不得自请审查冒充独立 Review）。

## 依赖、风险与阻塞
- **前置**：P15-C1（契约，done）。**阻塞条件**：若某面语义不完备 → **失败关闭并上报 Coordinator**（引契约行号），**不得**伪造或静默降级。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6）；Owner Codex。基线 `b1f4d08c79ad8f7c11bbc945cdbeddd3ef5f6523`，分支 `codex/P15-CORE-1A`，worktree `G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1A`。
- 实现交付 head：`9232802c08b983225898cb784504fee49c4c43f4`；Handoff：[P15-CORE-1A-9232802c.md](../handoffs/P15-CORE-1A-9232802c.md)。证据文档提交由下方 Canonical Evidence 表固定。
- 最终测试：`& 'G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe' -m pytest tests/core -q -p no:cacheprovider`；420 passed / 0 skipped / 1 deprecation warning，exit 0；基线 407，增加 13 项。完整日志和退出码见 `verification/P15-CORE-1A/`。
- 首次全量运行曾因协议版本常量整体提升出现 5 个旧面版本断言失败；已将既有面保留为 2.3、P15 面设为 2.6，并在固定实现 head 重跑全绿。诊断日志独立保存。
- 未修改契约、`apps/desktop/**`、Schema/迁移/依赖；未实现 1B/1C；未修改 `STATUS` / `REBASELINE_PLAN`；未触碰主仓 19 项 dirty；未 push/merge/reset。Owner 未发起独立 Review。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (CANONICAL / SOURCE_PIN) |
|---|---|---|---|---|---|
| EVD-P15-1A-CONTRACT | AC1 / frozen wire | `doc/contracts/P15_SETTINGS_IPC_CONTRACT.md` | `b1f4d08c79ad8f7c11bbc945cdbeddd3ef5f6523` | `b6b29246c01cb4cdd7a360bf8d34b4499cabbd751cce6d98e6309fe7a0d40090` | SOURCE_PIN |
| EVD-P15-1A-P10-BOUNDARY | AC1 / P10 logic boundary | `doc/contracts/P10_CREDENTIAL_CONFIG_CONTRACT.md` | `b1f4d08c79ad8f7c11bbc945cdbeddd3ef5f6523` | `7e186ca9818654448582e769505597fe93376179e2dca5972bd36f5632b4828d` | SOURCE_PIN |
| EVD-P15-1A-REGISTRY-FACT | AC3 / registry adjudication | `src/infrastructure/providers/handlers.py` | `b1f4d08c79ad8f7c11bbc945cdbeddd3ef5f6523` | `3e1386f1a561cf721320e19e8a9d06daa2b9bb5a2796842c74de2510da3e6be9` | SOURCE_PIN |
| EVD-P15-1A-COMMANDS | AC1–AC4 | `src/bootstrap/settings_commands.py` | `9232802c08b983225898cb784504fee49c4c43f4` | `a9b1ad574b8d90c33f5647fd53b849c27f28a7e3a7c1e02c26d63d28f0efb7b5` | CANONICAL |
| EVD-P15-1A-DISPATCH | AC1 / protocol compatibility | `src/bootstrap/core_service.py` | `9232802c08b983225898cb784504fee49c4c43f4` | `33ddb0f83b8d344d33b5e7ebfdd6c8399599a81629615b4a7f9e3c19fe937bc5` | CANONICAL |
| EVD-P15-1A-ASSEMBLY | AC3 / Core Store assembly | `src/bootstrap/core_assembly.py` | `9232802c08b983225898cb784504fee49c4c43f4` | `95b3267166f3d1d407ed8c30b66bce3642ce8e3b23fec005a663a301102a4f15` | CANONICAL |
| EVD-P15-1A-START-RUN | AC2 / frozen StartRun | `src/application/tasks/service.py` | `9232802c08b983225898cb784504fee49c4c43f4` | `efaa266ad2ad7571f2a637a337fef8d3d519e3bdaf74b1382a376f83b977eb12` | CANONICAL |
| EVD-P15-1A-SETTINGS-STORE | AC2 / snapshot projection | `src/application/tasks/store.py` | `9232802c08b983225898cb784504fee49c4c43f4` | `da3c1848d62898b558f4f397d8de9e7c2b9f8fd889f38596e5bc533d8e96139f` | CANONICAL |
| EVD-P15-1A-PROFILE-STORE | AC1 / binding persistence | `src/infrastructure/settings/json_profile_stores.py` | `9232802c08b983225898cb784504fee49c4c43f4` | `47b15a0dfd6b2e025c075f99d56f7b954522a655edb46f793747fc1bb1b293b8` | CANONICAL |
| EVD-P15-1A-SQLITE-SNAPSHOT | AC2 / reserved metadata filtering | `src/infrastructure/sqlite/pipeline.py` | `9232802c08b983225898cb784504fee49c4c43f4` | `d6c18cff8a2fdbf5a746c92791bde61075b70b754aafe868506f7e619311a551` | CANONICAL |
| EVD-P15-1A-CAPABILITY | AC1 / Rendering capability | `src/ports/providers/profiles.py` | `9232802c08b983225898cb784504fee49c4c43f4` | `1ff37b589a0963014734516786a371fddc53dad2e7adb5c8e1edd613f56c3073` | CANONICAL |
| EVD-P15-1A-TESTS | AC1–AC4 / counterexamples and matrix | `tests/core/test_p15_core_settings.py` | `9232802c08b983225898cb784504fee49c4c43f4` | `a163d7bb104eb54ad0210b11455060e1ac89dd484fe786d7441311cebbe1b04e` | CANONICAL |
| EVD-P15-1A-FULL-TEST-LOG | AC5 / full regression | `verification/P15-CORE-1A/pytest-core.log` | `3f11a8d52f1d4b3fe9f9847c0466ca293643eba2` | `ca9f00193b986700b7eacdd2afe962d15aec96ebab9f84c1b19729927a07c1ad` | CANONICAL |
| EVD-P15-1A-EXIT | AC5 / exit status | `verification/P15-CORE-1A/pytest-core.exit-code.txt` | `3f11a8d52f1d4b3fe9f9847c0466ca293643eba2` | `13bf7b3039c63bf5a50491fa3cfd8eb4e699d1ba1436315aef9cbe5711530354` | CANONICAL |
| EVD-P15-1A-FIRST-ATTEMPT | Diagnostic / corrected protocol compatibility | `verification/P15-CORE-1A/pytest-core-first-attempt.log` | `3f11a8d52f1d4b3fe9f9847c0466ca293643eba2` | `61a05ffa0e5c36ced6b87e5bd9ebc3b900ca10bcdbf8037b55e62257aba69a41` | CANONICAL |
| EVD-P15-1A-FIRST-ATTEMPT-META | Diagnostic / shell and interpreter | `verification/P15-CORE-1A/pytest-core-first-attempt.meta.txt` | `3f11a8d52f1d4b3fe9f9847c0466ca293643eba2` | `91efa4b404e1d7644aa6b6ac976ae3519cd8eace463e13edd7ddbd17045cbc14` | CANONICAL |
| EVD-P15-1A-FIRST-ATTEMPT-EXIT | Diagnostic / exit status | `verification/P15-CORE-1A/pytest-core-first-attempt.exit-code.txt` | `3f11a8d52f1d4b3fe9f9847c0466ca293643eba2` | `f1b2f662800122bed0ff255693df89c4487fbdcf453d3524a42d4ec20c3d9c04` | CANONICAL |
| EVD-P15-1A-RESOURCES | AC6 / resource preservation | `verification/P15-CORE-1A/resource-manifest.json` | `3f11a8d52f1d4b3fe9f9847c0466ca293643eba2` | `c1b7919170b55a9a2b259abd058d3c2945d6ce60640d4203428c06a8523de661` | CANONICAL |
| EVD-P15-1A-HANDOFF | AC6 / handoff | `doc/handoffs/P15-CORE-1A-9232802c.md` | `3f11a8d52f1d4b3fe9f9847c0466ca293643eba2` | `fafe815e1bd5173b358fcca742cd5768b71e266ed8fb0b67a04672d715547541` | CANONICAL |

| EVD-P15-1A-REVIEW-R1 | AC1–AC6 | `verification/P15-CORE-1A/dsh-review-r1.md` | `fc8a770b9` | `4050d177a6245ede9e04e18a4f223885c4b6161c4993b0177ed157d52677d0bd` | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1A | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1A | `verification/P15-CORE-1A/resource-manifest.json` | branch `codex/P15-CORE-1A`、delivery head 已固定；保留供独立 Review |
| test-env | G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312 | PRESERVE_REFERENCED | G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312 | `verification/P15-CORE-1A/resource-manifest.json` | 只读运行既有 Python 3.12 环境，未安装/更新依赖 |

## Closeout Record

- Closeout date / Coordinator：2026-10-17（dsh, epoch 6）。Reviewer=**dsh**（本会话，`route-agent.py` 路由；Owner=Codex 已机器排除）。
- canonical_evidence_status：`complete`。**15 条证据行**（原 14 + 独立 Review）；**BL-17 包含性成立**；class 仅 `CANONICAL`/`SOURCE_PIN`（**BL-19**）。
- **pin 复算（RV-P15-04）**：源码/测试/证据文件的 pin 由 Owner 在其工作树以 LF 计算 → closeout 已在**主仓库**按规范磁盘字节**复算**全部行。
- resource_closeout_status：`complete`（worktree `PRESERVE_REFERENCED`）。删除、迁移、归档数量/字节数：0。
- 交付：`done`。集成合并 `a810ee654`（`--no-ff`，**无冲突**）；**集成期契约对齐** `fc8a770b9`；delivery_head（分支实际 HEAD）`3f11a8d52`。
- **独立复核（我亲做）**：范围合规（9 个 src/tests 文件）；**命令名与契约逐字一致、无发明 wire**（其余命中为 §9 message key 与 phase 名）；分发接入既有机制（`core_service` L2671 分发 + L3247 门控）；**处置语义有实现+测试双证据**（多 Profile 同 Provider、解析优先级**无隐式回退**、Snapshot **`frozen: True`** + 来源 + 无引用、覆盖分层 fail-closed）；`SettingsSurfaceError` **仅四字段**（§9 封闭投影）；**拒绝 endpoint 内嵌凭据**（`urlsplit(...).password is not None` → 拒绝）；既有命令语义零变化；**我复跑 pytest 420 passed**（基线 407 → +13 新测试，零回归）。
- **集成期契约对齐（本次发现并处置，非实现缺陷）**：本 Task 基点 `b1f4d08c7` **早于 FU1 的合并**，故实现按 **minor 6** 门控，而 FU1 已把**全部 P15 Core 命令**定为 **minor 7**。按"**契约权威 + 合并期按真实值对齐**"（同跨任务计数断言先例）由 Coordinator 对齐 **3 处**：`core_service._P15_PROTOCOL_MINOR` 6→7、测试断言 `{2,6}`→`{2,7}`、测试断言 `_P15_PROTOCOL_MINOR == 6`→`== 7`；对齐后 **420 passed**。**教训（同类全类扫描）**：首轮扫描用 `= 6` 未覆盖 `== 6`，**第三处由此遗漏**——扫描模式必须覆盖 `=`/`==`/字面量等多种写法。
- **未关闭项**：真实 Provider profile 持久化的端到端行为**未在 host 层验证**（host 注册属 P15-HOST-1）；本 Task 仅 Core 侧。
- **DAG 效果**：1A 关闭 → 解除 **P15-CORE-1B** 的前置（同为 `core_service`/`core_assembly` 写范围 → **串行**）→ 本 closeout **同步释放 P15-CORE-1B**；1C 仍须待 1B 关闭。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 同批同步。
