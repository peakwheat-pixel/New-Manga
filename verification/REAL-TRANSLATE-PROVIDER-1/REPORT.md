# REAL-TRANSLATE-PROVIDER-1 交付报告：真实翻译接入（OpenCode / OpenAI-compatible）

> **结论先行：AC3（真实翻译产物）BLOCKED——OpenCode Zen key 可通过鉴权（`/models` HTTP 200，44 个模型），但该 key 无付费余额（402）且免费模型被限流（429）；真实 translate 运行以 typed `PROVIDER_RATE_LIMITED` 失败，未产出翻译、未伪造结果。AC1/AC2/AC4 达成**；AC5 门禁通过。

- Task: `doc/tasks/REAL-TRANSLATE-PROVIDER-1.md`（team task-48）；Owner `route-research`；Reviewer `dsh`
- Branch: `task/REAL-TRANSLATE-PROVIDER-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/REAL-TRANSLATE-PROVIDER-1`
- Base: 卡面 `13cf26f6c`；Lead 指定 base HEAD `170878dc4`；交付前 rebase 到 main `606314829`（FLAKY-PYTEST-1 等先落地；无冲突）
- Delivery head: 见 `doc/tasks/REAL-TRANSLATE-PROVIDER-1.md` 的 `delivery_head`（含回归证据与工具；未改 Core 语义/协议/Host 契约/旧壳；未 push）

## 0. AC 判定

| AC | 判定 | 依据 |
|---|---|---|
| AC1 探测 | **MET** | `https://opencode.ai/zen/v1`（OpenAI-compatible）；`GET /models` HTTP 200 → 44 models；chat 探测：免费模型 429、付费模型 402；key 仅记录“存在”，未落盘 |
| AC2 密钥安全 | **MET** | key 从 `%TEMP%\nm-opencode-key.txt` 读取 → `credential_put` 写 Windows vault 并绑定 profile `3819f991…` → 临时文件删除；证据/日志无 key（`oc_sk_` 扫描为空）；失败尝试的 2 个孤儿 vault 条目已清理 |
| AC3 真实翻译 | **BLOCKED（额度）** | profile+binding+settings 装配成功；真跑 `translate_untranslated` 在 3 个有文字页的 translate step 全部 `PROVIDER_RATE_LIMITED`（真实 HTTP 429），运行 `completed_with_failures`，0 条翻译产出；未伪造 |
| AC4 降级/回退 | **MET** | 真实 provider 4xx → typed `PROVIDER_RATE_LIMITED`（retryable）；同一根目录切回 `identity-translation` 后 translate 22/22 completed，segment/mask_refine/inpaint/render 22/22 completed；切换仅是 frozen binding |
| AC5 回归/门禁 | **MET** | `test.ps1` **235/235 passed, 0 skipped**（61/56/118）；pytest **2773 passed / 10 skipped / 0 failed**（rebase 后基线 0 失败）；`check.ps1 -TaskPath` PASS；64-hex pin；本 Handoff + Record Decision |

## 1. AC1 探测（证据：`evidence/ac1-probe.json`）

| 项 | 结果 |
|---|---|
| base_url | `https://opencode.ai/zen/v1` |
| API 形态 | OpenAI-compatible（`/models`、`/chat/completions`；另有 `/responses`、`/messages` 供其他模型） |
| 鉴权 | `Authorization: Bearer <key>`；`GET /models` → **HTTP 200**，44 个模型 id |
| 模型探测（chat/completions，`ping`，max_tokens=8） | `deepseek-v4.1-flash-free` → **429**（2.0s）；`big-pickle` → 429；`glm-5.3-flash-free` → 429；`deepseek-v4.1-flash` → **402**；`gpt-5.4-nano` → 402 |
| 结论 | key 有效且可列举模型；**无可用推理额度**（付费 402 = 无余额；免费 429 = 免费层限流）。已尝试 OpenCode 客户端 UA/session/referer 头，仍 429 |
| key 记录 | 仅 `key_present: true`，无前缀/长度/hash/值 |

## 2. AC2 密钥安全（证据：`evidence/real-translate/host-config.json`、`evidence/host-logs/`）

1. `settings_provider_profiles_create`：`provider_id=openai-compatible`、`capabilities=["Translation"]`、`endpoint=https://opencode.ai/zen/v1`、`model=deepseek-v4.1-flash-free` → profile `3819f991cbe54001ba45b6f8524f260c`。
2. `credential_put`：target `{kind:provider_api, profile_id}`、intent `create` → Host 写 Windows Credential Manager，绑定 `NewManga/provider/<profile>/<ref>`；`credential_state=configured`；Host 审计文件仅含 `owner_hash`（无 secret）。
3. `settings_provider_bindings_set`：global / Translation → profile。
4. 运行时镜像：settings UI 保存 profile/binding 时写入 `pipeline_defaults.settings["providers"]` 的镜像形状（`base_url/model/credential_ref/enabled/options/provider_type/network_profile_id/proxy_policy`）由测试用 `settings_update_section` 写入；**只含 credential_ref，不含 secret**。
5. key 临时文件在 `credential_put` 成功后立即删除（`key_file_deleted: true`）；失败重试尝试遗留的 2 个孤儿 vault 条目已按前缀清理（保留成功 profile 与既有的 p15 smoke 条目）。
6. 泄漏扫描：仓库证据与测试源码 `oc_sk_` 前缀 0 命中；Host wire/审计/核心 stderr 均无 key。

## 3. AC3 真实翻译运行（BLOCKED，证据：`evidence/ac3-real-attempt.json`、`evidence/run-db-after.json`）

- 隔离数据根：`task-envs/REAL-TRANSLATE-PROVIDER-1/work-root`（`BOOK-FIXTURE-1` 的私有副本，8 页；运行前 0 regions）。
- 装配：RELEASE-REPACK-2 models sidecar（`core_service` sha `c5531930…`）；运行探针 `tools/run_translate_probe.py`（冻结 Core stdio，`StartRun translate_untranslated` book scope，`overrides.provider_bindings={ocr:manga-ocr, translate:openai-compatible-translation}`）。
- 结果：`run-6a044e6d2a974074a4931fc2f9ec0a40` **completed_with_failures**，总耗时 **7.78s**（含 detect 8 页 completed、ocr/color/term_extract 各 3 completed）。
  - translate step：3 个目标全部 **failed / `PROVIDER_RATE_LIMITED`**（真实 429）。
  - DB：3 个有文字页共 26 regions，`regions_translated_differs=0`、`regions_identity=22`（沿用运行前状态）→ **无新翻译产物**。
- **BLOCKED 原因**：该 key 的账户没有可用推理额度（付费 402、免费 429）；需要用户充值/开通额度或提供可用 key 才能完成 AC3 的“completed 且产出≠输入”。未以任何方式伪造翻译结果。
- 附注：真实 provider 调用链本身已被证明接通（`PROVIDER_RATE_LIMITED` 只能由真实 HTTP 429 产生；`PROVIDER_NOT_CONFIGURED` 为 0），一旦额度可用，同一配置即可产出翻译。

## 4. AC4 降级与回退（证据：`evidence/ac4-identity-fallback.json`）

| 路径 | 运行 | 结果 |
|---|---|---|
| 真实 provider（失败） | `run-6a044e…` | translate 3 步 `PROVIDER_RATE_LIMITED`（typed、retryable），无输出；运行继续完成其它步骤 |
| identity 回退（可切换） | `run-f36ad7…` | `overrides.provider_bindings.translate="identity-translation"`；translate **22/22 completed**；segment/mask_refine/inpaint/render 各 **22/22 completed**；耗时 **76.12s**；DB 中 22/26 regions `machine_translation == ocr_text`（identity 占位，符合预期） |
| 切换机制 | frozen run `provider_bindings`；运行期只改一处 binding 即可回退/前移 |

- 说明：identity 回退运行另有 5 个 OCR `INVALID_INPUT`（region-less 页的既有行为，与 translate 无关）；运行状态 `completed_with_failures`。identity 是 EXPERIMENTAL 占位（输入=输出），**不构成翻译质量验收**。
- 可配置性：真实 provider 的 profile/binding 走 Host 命令面与 `settings.providers`；identity 通过运行 binding 选择，两条路径均可切换。

## 5. AC5 回归/门禁（rebase 后 main `606314829`）

| 门 | 结果 |
|---|---|
| `apps/desktop-avalonia/scripts/test.ps1` | **235/235 passed, 0 skipped**（coreclient 61 / host 56 / app 118；本卡新增 Host 配置测试 1 例，无 key 时自跳过网络/vault） |
| pytest | **2773 passed, 10 skipped, 0 failed**（FLAKY-PYTEST-1 修复后基线；本卡未改 Python 源码，只新增 verification 工具） |
| check.ps1 | PASS（Task 卡收口） |

## 6. Record Decision

1. **provider 选型**：复用既有 `openai-compatible-translation`（`infrastructure/providers/translation_openai.py`）与 `openai_client` 错误映射；不新增远程调用代码，不引入新依赖/许可证。
2. **密钥处理**：key 只经 Host `credential_put` 进 Windows vault，profile 只保存 `credential_ref`；临时 key 文件用后即删；证据只记录存在性与 owner hash；任何日志/证据/截图无 secret。
3. **失败语义**：402/429 由既有映射变为 typed ProviderError（429→`PROVIDER_RATE_LIMITED` retryable；402→4xx request-side）；pipeline 不伪造输出，运行记录真实失败码。
4. **回退**：identity EXPERIMENTAL 保持默认不可隐式选择；回退通过运行 frozen binding 显式切换，已实测。
5. **运行路径**：Host 配置面（profile/credential/binding/settings）实测；运行探针改用冻结 Core stdio（与 RELEASE-REPACK-2 发布验证同路径）。**发现**：本次隔离根下经 Host `library_start_run` 直发该 sidecar 返回 `INVALID_REQUEST`（已记录为遗留，需 DSH triage），故运行证据走 Core stdio 探针。

## 7. 遗留 / NOT_RUN

1. **AC3 BLOCKED（额度）**：需用户为该 OpenCode 账号充值/开通付费额度（402）或解除免费层限流（429）；额度可用后可直接复跑 `tools/run_translate_probe.py` 完成 AC3。
2. **Host `library_start_run` 兼容性**：隔离根 + REPACK-2 models sidecar 下返回 `INVALID_REQUEST`（Core 直连同 payload 可接受）；未在本卡范围内修复，建议 DSH 开专项定位 Host dispatcher 差异。
3. **target language 未接入**：远程翻译请求体 `target_language` 为空（现有 code 未把 book.target_language 传给 provider）——即使额度可用，译文语种仍可能不符合预期；建议另开质量 Task。
4. **UI 配置路径**：本卡只在私有隔离根验证 Host 命令面；用户真实数据根的 Settings UI 配置（同样走 profile+credential+binding）未在真机 App 中点击验证。
5. **免费模型限流**：free-tier 模型对非 OpenCode 客户端形态请求返回 429；已尝试 UA/session/referer 头，仍 429（上游行为）。
6. 需独立 Review（Owner 不得自审；reviewer=`dsh`）。

## 8. 复跑方式

```powershell
# AC1 探测（只读，不落 key）
python verification/REAL-TRANSLATE-PROVIDER-1/tools/probe_opencode.py `
  --key-file "$env:TEMP\nm-opencode-key.txt" `
  --out verification/REAL-TRANSLATE-PROVIDER-1/evidence/ac1-probe.json

# AC2 配置（Host vault；opt-in，测试用 key 用后即删；普通 test.ps1 不设置该变量则自跳过）
$env:NEWMANGA_CORECLIENT_SIDECAR_DIR='<RELEASE-REPACK-2>/app/core-sidecar'
$env:NEWMANGA_REAL_TRANSLATE_SIDECAR_DIR=$env:NEWMANGA_CORECLIENT_SIDECAR_DIR
$env:NEWMANGA_REAL_TRANSLATE_KEY_FILE="$env:TEMP\nm-opencode-key.txt"
$env:NEWMANGA_REAL_TRANSLATE_BASE_ROOT='<task-env>/BOOK-FIXTURE-1/isolated-data'
$env:NEWMANGA_REAL_TRANSLATE_WORK_ROOT='<task-env>/REAL-TRANSLATE-PROVIDER-1/work-root'
$env:NEWMANGA_EVIDENCE_DIR='<worktree>/verification/REAL-TRANSLATE-PROVIDER-1/evidence'
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj --filter "FullyQualifiedName~RealTranslateProviderTests"

# AC3/AC4 运行（冻结 Core stdio）
python verification/REAL-TRANSLATE-PROVIDER-1/tools/run_translate_probe.py `
  --sidecar $env:NEWMANGA_CORECLIENT_SIDECAR_DIR --data-root $env:NEWMANGA_REAL_TRANSLATE_WORK_ROOT `
  --provider openai-compatible-translation --out verification/REAL-TRANSLATE-PROVIDER-1/evidence/ac3-real-attempt.json
python verification/REAL-TRANSLATE-PROVIDER-1/tools/run_translate_probe.py `
  --sidecar $env:NEWMANGA_CORECLIENT_SIDECAR_DIR --data-root $env:NEWMANGA_REAL_TRANSLATE_WORK_ROOT `
  --provider identity-translation --out verification/REAL-TRANSLATE-PROVIDER-1/evidence/ac4-identity-fallback.json
python verification/REAL-TRANSLATE-PROVIDER-1/tools/inspect_translate_run.py --db "$env:NEWMANGA_REAL_TRANSLATE_WORK_ROOT\library.db" `
  --page-id f52f2772e8044557a72e82f5ea6ab932 --page-id 4f8a24147b3044deabf4f5a2dd83b84f --page-id a607fc4ca3034f47b5bc43d59f94f2ca `
  --out verification/REAL-TRANSLATE-PROVIDER-1/evidence/run-db-after.json
```
