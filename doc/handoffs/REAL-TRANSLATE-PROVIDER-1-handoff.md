# REAL-TRANSLATE-PROVIDER-1 Handoff（真实翻译接入：OpenCode / OpenAI-compatible）

- Task: `doc/tasks/REAL-TRANSLATE-PROVIDER-1.md`（team task-48）
- Branch: `task/REAL-TRANSLATE-PROVIDER-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/REAL-TRANSLATE-PROVIDER-1`
- Base: 卡面 `13cf26f6c`；Lead 指定 HEAD `170878dc4`；交付前 rebase 到 main `606314829`（FLAKY-PYTEST-1 等先落地；无冲突）
- Delivery head: `be587bf822c05ccae7dce7cdeba68b6e6b95b150`（证据/工具/测试提交；**未改产品代码**，未改协议/Host 契约/旧壳；未 push）
- **AC3 = BLOCKED（额度）**；AC1/AC2/AC4 达成；AC5 通过。

## 1. 结论

| AC | 判定 | 证据 |
|---|---|---|
| AC1 探测 | **MET** | `https://opencode.ai/zen/v1`，OpenAI-compatible；`/models` HTTP 200 → 44 models；chat：free 429 / paid 402；key 仅标存在。`evidence/ac1-probe.json` |
| AC2 密钥安全 | **MET** | `%TEMP%\nm-opencode-key.txt` → Host `credential_put` → Windows vault 绑定 profile `3819f991…` → 临时文件删除；证据/日志 `oc_sk_` 扫描 0 命中；2 个失败尝试孤儿 vault 条目已清理。`evidence/real-translate/host-config.json`、`evidence/host-logs/` |
| AC3 真实翻译 | **BLOCKED（额度）** | 真跑 `translate_untranslated`：3 个有文字页 translate step 全 `PROVIDER_RATE_LIMITED`（真实 429）；`completed_with_failures`；0 条翻译、未伪造。`evidence/ac3-real-attempt.json`、`evidence/run-db-after.json` |
| AC4 降级/回退 | **MET** | typed 降级（RATE_LIMITED）+ identity 回退：translate 22/22 completed，下游 22/22；切换仅 frozen binding。`evidence/ac4-identity-fallback.json` |
| AC5 回归/门禁 | **MET** | `test.ps1` 235/235（61/56/118）；pytest 2773P/10S/0F；`check.ps1 -TaskPath` PASS；64-hex pin |

## 2. 真跑事实

- 隔离根：`task-envs/REAL-TRANSLATE-PROVIDER-1/work-root`（BOOK-FIXTURE-1 私有副本；运行前 0 regions）。
- sidecar：RELEASE-REPACK-2 models（`core_service` sha `c5531930…`）。
- 真实 provider 运行 `run-6a044e6d2a974074a4931fc2f9ec0a40`：**completed_with_failures**，7.78s；detect 8/8、ocr/color/term_extract 各 3 completed、translate 3 failed `PROVIDER_RATE_LIMITED`。
- identity 回退运行 `run-f36ad73724b64ff2aa56875ec4b7ad36`：**completed_with_failures**，76.12s；translate 22/22、segment/mask_refine/inpaint/render 各 22/22；DB 22/26 regions identity（输入=输出，EXPERIMENTAL 占位）。
- **BLOCKED 原因**：该 key 可鉴权（`/models` 200）但无付费余额（402）、免费模型限流（429）；需用户充值/开通额度或提供可用 key，之后用 `tools/run_translate_probe.py` 复跑即可验证 AC3（无需改代码）。

## 3. 代码/工具清单

| 路径 | 说明 |
|---|---|
| `apps/desktop-avalonia/tests/NewManga.Host.Tests/RealTranslateProviderTests.cs`（新增） | opt-in Host 配置测试：profile + `credential_put`（vault）+ translate binding + settings mirror（只含 `credential_ref`）；key 用后即删；无 `NEWMANGA_REAL_TRANSLATE_KEY_FILE` 时直接跳过 → 普通 `test.ps1` 不触网、不写 vault。 |
| `verification/REAL-TRANSLATE-PROVIDER-1/tools/probe_opencode.py`（新增） | AC1 探测；key 只从文件读入内存，不落盘。 |
| `.../tools/run_translate_probe.py`（新增） | 冻结 Core stdio 真跑：StartRun → 轮询 GetRunSnapshot → GetTaskProjection 证据；provider 参数化（真实/identity）。 |
| `.../tools/inspect_translate_run.py`（新增） | DB 只读检查（region 文本三元组 + 失败 step 错误码）。 |
| 产品代码 | **0 改动**：既有 `openai-compatible-translation`、CredentialPort、profile/binding/settings 命令面直接复用。 |

## 4. 复跑方式（关键）

见 `verification/REAL-TRANSLATE-PROVIDER-1/REPORT.md` §8。要点：
1. key 放回 `%TEMP%\nm-opencode-key.txt`（用户临时放置；用后自动删除）；
2. Host 配置测试（需 `NEWMANGA_CORECLIENT_SIDECAR_DIR` + `NEWMANGA_REAL_TRANSLATE_*` 环境）；
3. `tools/run_translate_probe.py --provider openai-compatible-translation` 跑真实；`--provider identity-translation` 跑回退；
4. `tools/inspect_translate_run.py` 检查 DB 翻译是否 `machine_translation != ocr_text`（AC3 的“产出≠输入”判据）。

## 5. 遗留

1. **AC3 额度 BLOCKED**：见上；不计为代码缺陷。
2. **Host `library_start_run` 兼容性发现**：隔离根 + REPACK-2 models sidecar 下，经 Host dispatcher 直发 StartRun 返回 `INVALID_REQUEST`（同 payload 直连 Core stdio 可接受）。本卡因此用 Core stdio 探针跑正文；建议 DSH 开专项定位 Host dispatcher 差异（影响 App 工作台运行入口的可测性）。
3. **target language 未接入**：`OpenAiTranslationProvider.target_language` 未从 book 设置注入（请求体 `target_language` 为空）；即使额度可用，译文目标语种可能不符。建议另开质量 Task。
4. **UI 配置路径未真机点击**：本卡只在私有隔离根验证 Host 命令面；Settings UI 的 profile/credential/binding 保存流程（同一套 Host 命令 + settings mirror）未在真实 App 点击验证。
5. **免费层限流**：free-tier models 对非 OpenCode 客户端形态请求返回 429（UA/session/referer 均尝试），属上游行为。
6. 需独立 Review（Owner 不得自审；reviewer=`dsh`）。
