---
id: REAL-TRANSLATE-PROVIDER-1
title: 接入真实翻译服务（OpenCode/OpenAI-compatible）
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_round_2_5
suggested_owner: route-research
owner: route-research
reviewer: dsh
depends_on: []
base_commit: 13cf26f6c
branch: task/REAL-TRANSLATE-PROVIDER-1
worktree: G:/CODEX/New Manga.workspace/worktrees/REAL-TRANSLATE-PROVIDER-1
integration_commit: 6bf084222
delivery_head: be587bf822c05ccae7dce7cdeba68b6e6b95b150 
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/REAL-TRANSLATE-PROVIDER-1
allowed_paths:
  - doc/tasks/REAL-TRANSLATE-PROVIDER-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - src/**; apps/desktop-avalonia/**
  - verification/REAL-TRANSLATE-PROVIDER-1/**
  - G:/CODEX/New Manga.workspace/task-envs/REAL-TRANSLATE-PROVIDER-1/**
  - G:/CODEX/New Manga.workspace/worktrees/REAL-TRANSLATE-PROVIDER-1/**
---

# REAL-TRANSLATE-PROVIDER-1：接入真实翻译服务（OpenCode / OpenAI-compatible）

## 背景

`identity-translation` 仅为 EXPERIMENTAL 占位（输入=输出）；用户提供 OpenCode key（`oc_sk_…`，`%TEMP%\nm-opencode-key.txt`），要求接入真实翻译服务。命令面 66/0 已实现，`openai-compatible-translation` provider、CredentialPort（Windows vault）、ProviderProfile/Binding 存储均已在代码中，本卡负责真实服务接入、密钥安全与真跑证据。

分支基于 Lead 指定 HEAD `170878dc4`，交付前 rebase 到 main `606314829`（FLAKY-PYTEST-1 等先落地；无冲突）。Handoff：`doc/handoffs/REAL-TRANSLATE-PROVIDER-1-handoff.md`。

## Acceptance Criteria

- [x] **AC1 探测**：确认 `https://opencode.ai/zen/v1`（OpenAI-compatible）与可用模型；`GET /models` HTTP 200 → 44 models；chat 探测免费模型 429、付费模型 402；记录 base_url/模型名，key 仅标“存在”。证据 `evidence/ac1-probe.json`（R3）。<<MET>>
- [x] **AC2 密钥安全**：key 从临时文件读取 → `credential_put` 写入 Windows vault 并绑定 profile `3819f991…`（`credential_state=configured`）→ 临时文件删除；证据/日志/截图无 key（`oc_sk_` 扫描 0 命中）；失败尝试遗留的 2 个 vault 孤儿条目已清理。证据 R4/R16、`run-summary.json`。<<MET>>
- [ ] **AC3 真实翻译**：profile（openai-compatible）+ translate binding + settings 装配成功；真跑 `translate_untranslated` 时 3 个有文字页的 translate step 全部 typed `PROVIDER_RATE_LIMITED`（真实 HTTP 429），运行 `completed_with_failures`、0 条新翻译、未伪造。**BLOCKED：该 key 无付费余额（402）且免费层限流（429），无法获得 completed 且产出≠输入的真实翻译。** 证据 R5/R6/R9/R10。<<BLOCKED: OpenCode 账户额度受限（付费 402/免费 429），需用户充值或提供可用 key 后复跑；已实现链路经真实 429 证明接通>> <<BLOCKED: OpenCode 额度——free=429 / paid=402；3 页真实 HTTP 429→typed PROVIDER_RATE_LIMITED，0 条翻译（未伪造）；充值后跑 tools/run_translate_probe.py 即可复验>>
- [x] **AC4 降级**：真实 provider 4xx → typed `PROVIDER_RATE_LIMITED`（retryable）；同一数据根切回 `identity-translation` 后 translate 22/22、segment/mask_refine/inpaint/render 各 22/22 completed（76.1s），DB 22/26 regions identity；切换仅是 frozen run binding，可配置回退。证据 R7/R10。<<MET>>
- [x] **AC5 回归/门禁**：`test.ps1` **235/235 passed, 0 skipped**（61/56/118）；pytest **2773 passed / 10 skipped / 0 failed**（rebase 后基线）；`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision（REPORT §6）。<<MET>>

## 实现摘要

**未改产品代码（无需新增 provider 实现）**；复用既有：
- `src/infrastructure/providers/translation_openai.py`（`openai-compatible-translation`）+ `openai_client.py` 错误映射（401/403→AUTH，429→RATE_LIMITED，5xx→UNAVAILABLE，剩余 4xx→INPUT）；
- Host `credential_put`/`settings_provider_profiles_create`/`settings_provider_bindings_set`/`settings_update_section` 命令面与 Windows vault；
- 运行链路 `translate_untranslated` 的 frozen provider binding。

新增（证据/测试工具，均在允许范围）：
| 文件 | 作用 |
|---|---|
| `apps/desktop-avalonia/tests/NewManga.Host.Tests/RealTranslateProviderTests.cs` | opt-in Host 配置测试：profile + credential_put（vault）+ binding + settings mirror；key 用后即删；无 key 变量时直接跳过（普通 test.ps1 不触网/不写 vault） |
| `verification/REAL-TRANSLATE-PROVIDER-1/tools/probe_opencode.py` | AC1 探测（/models + 多模型 chat 探测；不记录 key） |
| `.../tools/run_translate_probe.py` | 冻结 Core stdio 真跑（StartRun → 轮询 → GetTaskProjection 证据） |
| `.../tools/inspect_translate_run.py` | DB 只读检查（ocr_text/machine_translation/失败 step 错误码） |

## 实际测试记录

| 项 | 命令 | 结果 |
|---|---|---|
| 全量 .NET | `apps/desktop-avalonia/scripts/test.ps1` | **TEST PASS 235/235（61/56/118），0 skipped** |
| pytest | `python -m pytest -q` | **2773 passed, 10 skipped, 0 failed**（rebase `606314829`） |
| AC1 | `tools/probe_opencode.py` | models HTTP 200 / 44 models；chat：free 429、paid 402 |
| AC3 | `tools/run_translate_probe.py --provider openai-compatible-translation` | run `run-6a044e…` completed_with_failures（7.78s）；translate 3 步 `PROVIDER_RATE_LIMITED`；0 翻译产物 |
| AC4 | `tools/run_translate_probe.py --provider identity-translation` | run `run-f36ad7…`（76.12s）；translate 22/22 completed；DB identity 22/26 |
| AC2 | Host 配置测试 | `credential_state=configured`；vault ref 绑定；key 临时文件已删 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| R3 | AC1 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/ac1-probe.json | - | a54fe1afbf81d10bae6f26dd18a04c12d65678e6d47c39bb76b08fffd533e277 | CANONICAL |
| R5 | AC3 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/ac3-real-attempt.json | - | 157dc44b20ef13526204c273307ae6a90e5ab74640220947feed09a9e196048e | CANONICAL |
| R6 | AC3 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/ac3-real-attempt.stderr.log | - | eeffe579faa06e8c4e1413a5a610eba38685995aa50091c846b7a7068aa6baf2 | CANONICAL |
| R7 | AC4 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/ac4-identity-fallback.json | - | 2f892216c0f468ad75c5afaeed0e7746a6e085bad41d1c172cfaa59c37fb2bbc | CANONICAL |
| R8 | AC4 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/ac4-identity-fallback.stderr.log | - | 3da5c558be89117dcf6f2c98d59682c9c267b950da3e08fd8f0b48a43ed5afca | CANONICAL |
| R15 | AC5 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/dotnet/dotnet-test-Debug.log | - | 0198a1db77f88b1c4f3ba24fecaa16c84ee7a3518dd894a4bdd75c9c4ba410a6 | CANONICAL |
| R14 | AC5 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/dotnet/results-host.trx | - | 8f1c632c506fb905f5f261f73056e0c0851a1d2d157fe6a23d6bc97d23377dd6 | CANONICAL |
| R13 | AC5 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/dotnet/summary.json | - | 32a3ed8bfc55f38ca7ab16e200ad6c2c224a5121793b8dd99494d35ef592e709 | CANONICAL |
| R16 | AC2 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/host-logs/real-translate/core_service.stderr.log | - | c59789a51ef33cd4c1f0a5439f67f4c84800186dbb9fa35a08b3874e6200f5d1 | CANONICAL |
| R16 | AC2 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/host-logs/real-translate/credentials/put-20261027T1539323495079Z.json | - | d2dde05edeeccd4b6b9b30e987a87c9f7294bce0cb59eb453787f648fe639599 | CANONICAL |
| R16 | AC2 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/host-logs/real-translate/credentials/put-20261027T1555266821441Z.json | - | 9610aef5d0646c15faac2116d5852615ee89e75260fbd387739e09aa6f020da8 | CANONICAL |
| R16 | AC2 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/host-logs/real-translate/credentials/put-20261027T1556323671425Z.json | - | c547bb543ae4bec50f1599ec33defdccd53dc295c8933bbd9dc248ae10c450be | CANONICAL |
| R16 | AC2 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/host-logs/real-translate/host.log | - | 4ce53cf20a1c6acd343f0340b9f892c33deb4ccb2aa6c959cc9cb54f768cb606 | CANONICAL |
| R16 | AC2 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/host-logs/real-translate/host_bridge.stderr.log | - | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | CANONICAL |
| R16 | AC2 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/host-logs/real-translate/wire/core-service.ndjson | - | 08bde3f84d60838bc639223d826423ce7bfa5ee6acb4d3a53ccc6a6643d61846 | CANONICAL |
| R16 | AC2 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/host-logs/real-translate/wire/host-bridge.ndjson | - | 18f0da09593b55bedbe303f5bda03bb0833c1465db099c4b3f5a5d7af86dae8a | CANONICAL |
| R12 | AC5 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/pytest.log | - | ee5177bcd569fd16e5bca276f7eac371b4ac90f69582fb453d0d6a32c0dcdc2a | CANONICAL |
| R4 | AC2 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/real-translate/host-config.json | - | 0bbe976a89c2bac88203e2ed85b8ed89789e72f3ee2725b133693359a592cab4 | CANONICAL |
| R10 | AC3/AC4 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/run-db-after.json | - | d8db97705214c31cd91b9d9395b69b41d696e91526c563504d8ce747a604e95e | CANONICAL |
| R9 | AC3 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/run-db-before.json | - | 19b3f099c81c0308dd5693c6bca1437c8377e0f65a560d505bd92292eac03267 | CANONICAL |
| R2 | AC1-AC5 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/run-summary.json | - | 011f069e2b0f704b224e3646743ff64d9a54398699a8513578d7092914a7a833 | CANONICAL |
| R11 | AC5 | verification/REAL-TRANSLATE-PROVIDER-1/evidence/test-ps1.log | - | ea76f409d73253de980223a24aa1b3b0d9ae18def4396e64e7edff6624435d47 | CANONICAL |
| R1 | AC1-AC5 | verification/REAL-TRANSLATE-PROVIDER-1/REPORT.md | - | bd787991b18173202b31e8531194cff0f1e8a88e2d6e816541de83d495b8b1c7 | CANONICAL |
| R17 | AC3 | verification/REAL-TRANSLATE-PROVIDER-1/tools/inspect_translate_run.py | - | c2a0dad4ba833385c1ca639f3f6825353e6eca41f3efeb197893c7baddf1e568 | CANONICAL |
| R17 | AC3 | verification/REAL-TRANSLATE-PROVIDER-1/tools/probe_opencode.py | - | a49ee271295988b57a1ac09d61799df49024cec3ca710eff2f2ea078c731d8c2 | CANONICAL |
| R17 | AC3 | verification/REAL-TRANSLATE-PROVIDER-1/tools/run_translate_probe.py | - | 3a67ef3159cd95a987d67102e54da23254cb4c7872d1a2900c5e3645f2a83030 | CANONICAL |
| R18 | AC2/AC4 | apps/desktop-avalonia/tests/NewManga.Host.Tests/RealTranslateProviderTests.cs | - | 26c4286d3180e581189ff9f638ba90d17878fbdd21b1df96d4dd1b5647c1a02e | SOURCE_PIN |
| R19 | AC1 | verification/REAL-TRANSLATE-PROVIDER-1/tools/probe_opencode.py | - | a49ee271295988b57a1ac09d61799df49024cec3ca710eff2f2ea078c731d8c2 | SOURCE_PIN |
| R20 | AC3/AC4 | verification/REAL-TRANSLATE-PROVIDER-1/tools/run_translate_probe.py | - | 3a67ef3159cd95a987d67102e54da23254cb4c7872d1a2900c5e3645f2a83030 | SOURCE_PIN |
| R21 | AC3/AC4 | verification/REAL-TRANSLATE-PROVIDER-1/tools/inspect_translate_run.py | - | c2a0dad4ba833385c1ca639f3f6825353e6eca41f3efeb197893c7baddf1e568 | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/REAL-TRANSLATE-PROVIDER-1 | PRESERVE_REFERENCED | 原路径 | `work-root`（BOOK-FIXTURE 私有副本 + 已装配 provider profile/settings）、`dotnet-evidence-rebased/`、`base-root/`、日志 | 保留真跑现场与回归证据；vault 条目保留（绑定 profile，AC2 交付物）；临时 key 文件已删除。 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-2 | PRESERVE_REFERENCED | 原路径 | models sidecar core_service sha `c5531930…` | 真跑/回归只读消费；归属 RELEASE-REPACK-2。 |
| vault | Windows Credential Manager `NewManga/provider/3819f991…/<ref>` | PRESERVE | 系统 vault | 仅存 secret，无任何副本 | key 由用户提供并授权写入；审计仅 owner_hash；孤儿条目已清理。 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`complete`（证据 pin 见上表，全部 64-hex sha256）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：AC3 BLOCKED（额度）；Host `library_start_run` 兼容性发现；目标语言未接入。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-28）— PASS（AC3 BLOCKED 额度）

- AC1/AC2/AC4/AC5 MET；key 入 Windows vault（profile 3819f991…）、临时文件即删、oc_sk_ 0 命中、孤儿条目已清。
- AC3 BLOCKED：额度（429/402），装配链路正确、typed 降级正确、0 条翻译未伪造；充值后 	ools/run_translate_probe.py 复验。
- 发现待定位：Host library_start_run 经 dispatcher 对该 sidecar 返回 INVALID_REQUEST（直连 Core 可用）→ 需专项诊断。
- 集成：6bf084222。
