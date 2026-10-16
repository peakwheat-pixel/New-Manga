---
id: P15-CORE-1B
title: 设置面 Core 实现 B：G22 凭据面 + G23 Network CRUD/默认/解析（不含测试命令）
kind: feature
governance_version: 2
status: done
approval: coordinator_release_20261017_split_of_P15_CORE_1
suggested_owner: Codex
owner: Codex
reviewer: dsh
depends_on: [P15-C1]
base_commit: c279659117db56b93d5676e5bb39fd8453b0d385
branch: codex/P15-CORE-1B
worktree: G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1B
integration_commit: 3f1ac29a186fcb82f3c62c98ee4e8e6e18e357c6
delivery_head: 075bcbad88dedaf2cad33822ae7742e944079915
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/P15-CORE-1B
---

# P15-CORE-1B：设置面 Core 实现 B：G22 凭据面 + G23 Network CRUD/默认/解析（不含测试命令）

## 来源
P15-CORE-1 因契约 §5.2 的 TestNetworkProfile 目标缺口**失败关闭**，经裁决拆分为 1A/1B/1C（见 [ruling](../verification/PROJECT-ORCHESTRATION-20261016/ruling-P15-CORE-1-network-test.md)）。**本 Task 不受该缺口影响**，可直接实现。

## 范围
实现契约 **§4.2**（受信 Host↔Core：`BindProfileCredential` / `ClearProfileCredential`）与 **§5.1**（Network Profile CRUD、`settings_network_profile_default_set/clear`、`settings_network_profile_resolve`）。**不含** `settings_network_profiles_test`（属 1C，等 P15-C1-FU1）。

## Acceptance Criteria
- [x] **AC1**：上述命令逐字实现；`Bind/ClearProfileCredential` **只**经受信 Host→Core 路由，**不注册为 WebView 可调用**。
- [x] **AC2**：Network Profile 模式/`proxy_endpoint` 组合校验（HTTP/HTTPS/SOCKS5 必需且 scheme 相符；Direct/System 必须 null）；`verify_tls` 默认 true、关闭需 `confirm_disable_tls_verification: true`；`allow_proxy_failure_direct_fallback` **默认 false**；默认选择键**仅**由 `SetGlobalNetworkProfile` 写；解析顺序 **Provider→Global→System→Direct**。
- [x] **AC3**：凭据**先写新引用再切换**（失败保留旧绑定）、清除即撤销且后续 Run 解析**不换用其他 Provider/Credential**；`credential_ref` 由 Host 提供、Core 校验归属。
- [x] **AC4**：命令在 `core_service` 实现并使用 `core_assembly` 已注册的 Credential/Network Profile stores；既有命令与语义**零变化**。
- [x] **AC5/AC6**：全量回归、反例、证据与 Handoff 已归档；独立 Review 待执行。

## 允许 / 禁止范围
- **允许**：src/**（Python Core）、tests/core/**（新增与必要修改，**不得弱化既有断言**）、本 Task、doc/handoffs/P15-CORE-1B-*.md、verification/P15-CORE-1B/**
- **禁止**：不得实现 G21 Provider 面（属 1A）与 `settings_network_profiles_test`（属 1C）
- 契约 **wire 已冻结**（doc/contracts/P15_SETTINGS_IPC_CONTRACT.md）：命令名/参数/结果/错误**逐字一致**，**不得**改名或增删字段；若发现契约问题**停下上报**，不得自行改契约；
- **不得**改 apps/desktop/**、Schema/迁移/依赖；不改 doc/STATUS.md / doc/REBASELINE_PLAN.md；不触碰用户 19 项 dirty；不 push/merge/reset。

## 安全硬红线
Secret / 明文凭据 / 认证头 / CredentialRef / 原始响应 / 路径 / 异常文本**不得**出现在任何**返回、错误、事件**中；错误只走契约 **§9 封闭投影**的键集；CredentialRef 不得进入普通 settings DTO。

## 测试与证据
- 覆盖本范围全部 AC，**必须含反例**（非法键/类型、未授权引用、缺省路径等）；python -m pytest tests/core -q -p no:cacheprovider **全绿且不回归**（基线 **420 passed**，用 G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe）；归档原始日志 + 退出码到 verification/P15-CORE-1B/**；
- 固定 commit + doc/handoffs/P15-CORE-1B-*.md + Canonical Evidence（status: in_review；**BL-15** delivery_head 不自引用；**BL-17** commit 列**原样** git rev-parse HEAD；**BL-19** class 仅 CANONICAL/SOURCE_PIN；**BL-16/RV-P15-04** sha256 按磁盘字节且**须能从主仓库验证**；**BL-18** 不得自请审查冒充独立 Review）。

## 依赖、风险与阻塞
- **前置**：P15-C1（契约，done）。**阻塞条件**：若某面语义不完备 → **失败关闭并上报 Coordinator**（引契约行号），**不得**伪造或静默降级。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6）；Owner=Codex，Reviewer=dsh。基线 `c279659117db56b93d5676e5bb39fd8453b0d385`，分支 `codex/P15-CORE-1B`，worktree `G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1B`。
- 实现交付 head：`6cf3c820990591cf6e7581db1ae38eea54d14fdc`；Handoff：[P15-CORE-1B-6cf3c820.md](../handoffs/P15-CORE-1B-6cf3c820.md)。Handoff 和 Task 证据在后续文档提交，不自引用 delivery head。
- 最终测试：`& 'G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe' -m pytest tests/core -q -p no:cacheprovider`；**440 passed / 0 skipped / exit 0**，基线 420，增加 20；1 个既有 Pillow `Image.getdata` 弃用 warning。完整日志、退出码、命令与环境见 `verification/P15-CORE-1B/`。
- 首次完整运行发现一处测试固定读取随机排序列表第一项的假设；已按目标 `profile_id` 查找并重跑全绿。首次日志与退出码保留为诊断证据。
- 新增反例覆盖非法 mode/endpoint、scheme 不符、userinfo/query/fragment、TLS 未确认、默认 fallback=false、代理失败不直连、未授权 CredentialRef、绑定失败保留旧引用、清除后不改选其他 Provider、默认解析优先级与 Run Snapshot 删除保护。
- 协议 minor 声明：新增 P15 Core 命令均为 `{ major: 2, minor: 7 }`；既有 Core 命令保持 minor 3。
- 未修改契约、`apps/desktop/**`、Schema/迁移/依赖、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`；未实现 1C 的 `settings_network_profiles_test`；未触碰主仓库 dirty 文件；未 push/merge/reset；Owner 未自行发起独立 Review。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (CANONICAL / SOURCE_PIN) |
|---|---|---|---|---|---|
| EVD-P15-1B-CONTRACT | AC1–AC2 / frozen rev 2.7 wire | `doc/contracts/P15_SETTINGS_IPC_CONTRACT.md` | `c279659117db56b93d5676e5bb39fd8453b0d385` | `B6B29246C01CB4CDD7A360BF8D34B4499CABBD751CCE6D98E6309FE7A0D40090` | SOURCE_PIN |
| EVD-P15-1B-P10 | AC3 / credential lifecycle boundary | `doc/contracts/P10_CREDENTIAL_CONFIG_CONTRACT.md` | `c279659117db56b93d5676e5bb39fd8453b0d385` | `7E186CA9818654448582E769505597FE93376179E2DCA5972BD36F5632B4828D` | SOURCE_PIN |
| EVD-P15-1B-WEBVIEW-SOURCE | AC1 / Tauri command registration source | `apps/desktop/src-tauri/src/main.rs` | `c279659117db56b93d5676e5bb39fd8453b0d385` | `2A6852C425E6E394B9E0EB6E4B0D097A2BCBE6701D62DFA2AB970D20F03327A4` | SOURCE_PIN |
| EVD-P15-1B-COMMANDS | AC1–AC3 / G22 + G23 handlers | `src/bootstrap/settings_commands.py` | `6cf3c820990591cf6e7581db1ae38eea54d14fdc` | `C26173E9440DE66BC4B230CA5D743D2E2BD7016CE648E15B6DF0A3DDDDEAC5E3` | CANONICAL |
| EVD-P15-1B-DISPATCH | AC1 / minor 7 + §9 projection | `src/bootstrap/core_service.py` | `6cf3c820990591cf6e7581db1ae38eea54d14fdc` | `4D5C08A061A55BBBF49C90EA70C6D5940BD017273A8DE1BEB7A61ED447944D29` | CANONICAL |
| EVD-P15-1B-STORE | AC2 / Network Profile + global default persistence | `src/infrastructure/settings/json_profile_stores.py` | `6cf3c820990591cf6e7581db1ae38eea54d14fdc` | `B191A9E02A88E6C8DA4089C65D0FE9643C07B38B38758DAD7FC4CE278477CEF0` | CANONICAL |
| EVD-P15-1B-ASSEMBLY | AC4 / existing Core stores registration | `src/bootstrap/core_assembly.py` | `6cf3c820990591cf6e7581db1ae38eea54d14fdc` | `95B3267166F3D1D407ED8C30B66BCE3642CE8E3B23FEC005A663A301102A4F15` | CANONICAL |
| EVD-P15-1B-TESTS | AC1–AC4 / counterexamples | `tests/core/test_p15_core_settings.py` | `6cf3c820990591cf6e7581db1ae38eea54d14fdc` | `6F3E6507C922DBF927D9E77CDA7A534FCC0C5DD16D9305DC6A9D9F012938DDA4` | CANONICAL |
| EVD-P15-1B-FULL-TEST | AC5 / full regression log | `verification/P15-CORE-1B/pytest-core.log` | `6cf3c820990591cf6e7581db1ae38eea54d14fdc` | `05FE90117D804A486353BA8D140191BB1DC1B384C7D8B50B08610F1001C86081` | CANONICAL |
| EVD-P15-1B-EXIT | AC5 / exit status | `verification/P15-CORE-1B/pytest-core.exit-code.txt` | `6cf3c820990591cf6e7581db1ae38eea54d14fdc` | `13bf7b3039c63bf5a50491fa3cfd8eb4e699d1ba1436315aef9cbe5711530354` | CANONICAL |
| EVD-P15-1B-COMMAND | AC5 / exact test command | `verification/P15-CORE-1B/pytest-core.command.txt` | `6cf3c820990591cf6e7581db1ae38eea54d14fdc` | `1489AC706DC9BE5D2AF9643782C1DEE1315117CA4408B57C27537A4D6BA2D21F` | CANONICAL |
| EVD-P15-1B-ENV | AC5 / test environment | `verification/P15-CORE-1B/pytest-core.environment.txt` | `6cf3c820990591cf6e7581db1ae38eea54d14fdc` | `F517B29108D89A63AB0737259C95892EC390B4903B2DB472588EA5BF3A34E645` | CANONICAL |
| EVD-P15-1B-FIRST-ATTEMPT | Diagnostic / repaired test ordering | `verification/P15-CORE-1B/pytest-core-first-attempt.log` | `6cf3c820990591cf6e7581db1ae38eea54d14fdc` | `5A9A8CA245F9F9EF7E43E897F249348A2F18D521A0139E8C8368E6A338CCC08C` | CANONICAL |
| EVD-P15-1B-FIRST-ATTEMPT-EXIT | Diagnostic / first run exit | `verification/P15-CORE-1B/pytest-core-first-attempt.exit-code.txt` | `6cf3c820990591cf6e7581db1ae38eea54d14fdc` | `f1b2f662800122bed0ff255693df89c4487fbdcf453d3524a42d4ec20c3d9c04` | CANONICAL |
| EVD-P15-1B-WEBVIEW-SCAN | AC1 / private command exclusion scan | `verification/P15-CORE-1B/webview-route-scan.txt` | `6cf3c820990591cf6e7581db1ae38eea54d14fdc` | `62ea1dcf6ab7f8c2dcc362b5df84bd4d770ac9cefc191f6e37030eb137deeb8e` | CANONICAL |
| EVD-P15-1B-RESOURCES | AC6 / resource preservation | `verification/P15-CORE-1B/resource-manifest.json` | `6cf3c820990591cf6e7581db1ae38eea54d14fdc` | `1537961A217F96E398C6C4049D9A2E82CC4652C48BF68C82DAE1A99C144C7801` | CANONICAL |
| EVD-P15-1B-HANDOFF | AC6 / handoff | `doc/handoffs/P15-CORE-1B-6cf3c820.md` | `9cab8c112aa10e6049b34875bd2e77228a6eaf54` | `39927e46801f2526bc370a49b0cbf51e8e27f9b78dca5a2926bc6f3452246b67` | CANONICAL |

| EVD-P15-1B-REVIEW-R1 | AC1–AC6 | `verification/P15-CORE-1B/dsh-review-r1.md` | `3f1ac29a1` | `f333dfea2a36656395cc78e96ccc1945897c9565360d38c1a76133344e0a73f5` | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1B | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1B | verification/P15-CORE-1B/resource-manifest.json | branch 与 base 已核验；delivery head 固定，worktree 保留供 Review |
| test-env | G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312 | PRESERVE_REFERENCED | G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312 | verification/P15-CORE-1B/resource-manifest.json | Python 3.12.3；只读运行，未安装或修改依赖 |

## Closeout Record

- Closeout date / Coordinator：2026-10-17（dsh, epoch 6）。Reviewer=**dsh**（本会话，`route-agent.py` 路由；Owner=Codex 已机器排除）。
- canonical_evidence_status：`complete`（Owner 原记 `in_review`，closeout 按终态修正）。证据含独立 Review；**BL-17 包含性成立**；class 仅 `CANONICAL`/`SOURCE_PIN`（**BL-19**）。
- **pin 复算（RV-P15-04）**：由 Owner 在其工作树以 LF 计算 → closeout 已在**主仓库**按规范磁盘字节复算。
- resource_closeout_status：`complete`（worktree `PRESERVE_REFERENCED`）。删除、迁移、归档数量/字节数：0。
- 交付：`done`。集成 `3f1ac29a186fcb82f3c62c98ee4e8e6e18e357c6`（`--no-ff`，**无冲突**）；delivery_head（分支实际 HEAD）`075bcbad88dedaf2cad33822ae7742e944079915`。
- **独立复核（我亲做）**：范围**排他严格**——契约 8 条 Network 命令中**只实现 7 条**，`settings_network_profiles_test`（1C）**未实现**，G21/G24（1A）未重写；**协议 `_P15_PROTOCOL_MINOR = 7`**（直接吸收 1A 教训），并有专门测试同时锁定"凭据命令需 minor 7"与"1C 命令缺席"；**安全红线逐条有反例测试**——拒绝模式/endpoint 错配与**内嵌凭据**、`verify_tls` 默认 true + 关闭需确认、`allow_proxy_failure_direct_fallback` 默认 false、**代理失败不重试直连**、**凭据从不返回 `CredentialRef`**、**替换失败保留旧绑定并清理新引用**、**清除后不解析到其他 Provider**、代理凭据按 Profile 作用域且无 Secret；§9 封闭投影沿用四字段 `SettingsSurfaceError`；随附 **`webview-route-scan.txt`**（在 `apps/desktop/src-tauri/src` 扫描凭据命令与 1C 命令 → **零命中**）。
- **合并后验证**：main 上 `pytest tests/core` **440 passed**（1A 后基线 420 → +20，零回归）；minor=7；1C 命令零命中。
- **交接项（P15-HOST-1 必须验收）**：`BindProfileCredential`/`ClearProfileCredential` 在 **Core 侧必须可被受信 Host 调用**（正确），但契约要求**不注册为 WebView 可调用** → 落实点在 **Tauri host allowlist**；P15-HOST-1 的 AC 须含"**仅 Host 可达**"的测试或扫描证据。
- **DAG 效果**：1B 关闭 → 解除 **P15-CORE-1C** 的前置（串行最后一环）→ 本 closeout **同步释放 P15-CORE-1C**。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 同批同步。
