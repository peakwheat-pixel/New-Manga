# Release Gate 差距评估（FEA 收口后）— 2026-11-14

**结论：Release Gate 仍 `BLOCKED`。** 本文件只更新事实与可执行性，不改 Gate 结论，不构成发布许可。

基线：`main` @ `a30f78d7d`（工作区 clean）。

## 1. 相较 `13_RELEASE_GATE.md` 的已变事实

| 报告中的旧事实 | 当前实测 | 影响 |
|---|---|---|
| Python Core 全量 pytest `3519 passed / 16 failed / EXIT 1` | **pytest 3544 passed / 0 failed / 10 skipped** | 该阻断项**已解除**；报告数字需更新 |
| FEA 线 DoD §1/§3 未达成 | **DoD v2 五条达成**（`MAINT-1-FEA-LINE-CLOSEOUT-v2-2026-11-14.md`） | 不直接解锁 Gate，但消除了"产品面未收口"的疑问 |
| 4B「无像素级视觉证据」 | **已关闭**：`verification/FEA-06-RESIDUAL-4B/visuals/` 两张真实帧 + DSH 目视确认 | 视觉证据从"缺失"变为"有签署证据"，但仍不作 AC 判据 |
| `.NET` 全量 `1875/0/109`（MAINT-1 P1） | 本项目三项目实测：App 914/0/11、Host 321/0/74、CoreClient 180/0/24 | 无 failed；全量 8 项目未在本轮复跑 |

**注意**：`13_RELEASE_GATE.md` 第 3 条同时提到"Avalonia TestHost 8/8 runner EXIT 1、TRX 0 tests"——本轮的 `dotnet test` 是真实跑通的（914 passed），与该旧描述不符；差异原因（不同 runner/不同时点）本轮**未核实**，不得据此声称该条已解。

## 2. Gate 六条解锁条件的现状

| # | 条件 | 状态 | 本环境可执行性 |
|---|---|---|---|
| 1 | 处置并验证 7 项开放 finding | **未完成** | 需逐项实现 + 独立 Review；`MAINT-1` P4 只处置了 4 张**提案卡**，不等于 7 项 finding 关闭 |
| 2 | `AUDIT-11-INC-001` 只读远端可见性调查 | **未完成** | 需网络与远端仓库访问；本轮未做 |
| 3 | 补齐完整 GUI / Core / Host 关键流程与 Avalonia TestHost | **部分** | headless 与三项目测试已绿；真实 GUI 全流程矩阵未做 |
| 4 | 当前 commit 生成 Windows 包 + clean install / 启动 / 升级回退 / 四页 / 卸载矩阵 | **未完成** | 需重新打包 sidecar（现存只有 `0.1.1` 旧包）+ 安装器签名；**本轮未做** |
| 5 | 模型 / API 与代表性质量验证，或 Owner 明确接受有边界限制 | **部分**（真实调用已验） | 已用产品自身 `OpenAiTranslationProvider` + `StdlibTransport` 对 DeepSeek 完成一次真实翻译：`deepseek-chat`、763/738ms、`valid_protocol=True`、`region-1 → 你好，你好吗？`、`region-2（sfx, ドガ）→ 轰`。证据 `verification/MAINT-1-RELEASE-MONITOR/model-api-verification.log`（凭据仅经环境变量注入，日志已核无密钥）。**仍未做**：代表性质量基线（无人工 GT，不得宣称翻译准确率达标）、App/Host 端到端走完整 UI 流程 |
| 6 | 当前 head 的 Canonical Evidence / governance / TaskPath / verify_pins / API inventory + 独立最终 Review | **部分** | 四件套已绿（check PASS / pins 18/18 / inventory EXIT 0）；**独立最终 Review 未做** |

## 3. 诚实边界

- **本轮没有生成任何 Windows 包，没有做 clean install、升级/回退、卸载验证。** `G:\CODEX\New Manga.workspace\artifacts\release\NewManga-0.1.1-win-x64\` 是 `0.1.1` 的旧产物，**不绑定当前基线**，不得当作当前 commit 的安装包证据。
- **没有调用任何真实模型 API。** 设置页「模型与设备：待接入」的状态未变；此前 MAINT-1 P2 冒烟也确认界面未假装已接入。
- **没有做远端可见性调查**（`AUDIT-11-INC-001`）。
- 因此 Gate **不能**从 BLOCKED 改为 CONDITIONAL 或 PASS。

## 4. 可在后续会话安全推进的两项

1. **条件 6 的独立最终 Review**：对当前 head 做一次未参与实现的独立复核（照 4B/C1 批次的模式），验证 Canonical Evidence、三指针、门禁与 limitation 登记。
2. **条件 4 的前置**：用 `tools/ci/publish-release.ps1` 在**当前 HEAD** 重新打包 sidecar 并跑 singlefile + `-Smoke`（该脚本自带"启动 exe + 隔离数据根 + host.log ready + exit 0"的真实窗口冒烟），产出绑定当前 commit 的包与冒烟证据。这一步不等于 clean install 矩阵，但能替换掉过时的 `0.1.1` 证据。

条件 1、2、5 依赖用户侧资源（finding 实现决策、远端访问、模型 API key），本轮无法推进。

## 5. 追加：条件 5 的真实调用验证（2026-11-14 晚）

- **做了什么**：用产品自身的 OpenAI 兼容翻译适配器（`src/infrastructure/providers/translation_openai.py`）+ 标准库 transport（`src/infrastructure/transport/stdlib.py`），对真实远端端点完成一次翻译请求，含 1 条 `speech` 与 1 条 `sfx`。
- **结果**：`provider_id=openai-compatible-translation`、`model=deepseek-chat`、`elapsed_ms≈740`、`valid_protocol=True`（两个 region_id 均按协议返回）、`你好，你好吗？` / `轰`（SFX 走文化等效而非音译，符合 system prompt）。
- **证据**：`verification/MAINT-1-RELEASE-MONITOR/model-api-verification.log`。
- **凭据处理**：只从环境变量 `DEEPSEEK_API_KEY` 注入，未写入任何仓库文件；日志已用正则核验不含 `sk-` 形态密钥。
- **边界（不得扩大解读）**：这是「真实模型 API 调用」的证据，**不是**质量验收——没有人工 ground truth，不能据此宣称翻译准确率或识别质量达标；也没有走 App → Host → Core 的完整 UI 端到端流程。
- **Gate 结论不变**：条件 5 由「未完成」改为「部分」，其余条件未变，**Gate 仍 `BLOCKED`**。

## 6. 追加：第二条 provider 路径（视觉 OCR）与「端到端」的真实边界

### 6.1 已验（两条独立 provider 路径）

| 路径 | provider | 模型 | 结果 | 证据 |
|---|---|---|---|---|
| 翻译 | `OpenAiTranslationProvider` | `deepseek-chat` | `valid_protocol=True`；`你好，你好吗？` / `轰` | `model-api-verification.log` |
| 视觉 OCR | `VisionOcrProvider` | `glm-4v-flash` | 渲染图 `こんにちは` 被正确识别（`contains_expected=True`） | `vision-ocr-verification.log` |

- 两条路径都走产品自身适配器 + `StdlibTransport` + 真实远端端点，不是 curl 探测。
- **qwen 视觉模型在本环境不可用**：`qwen3-max` / `qwen-vl-plus` → HTTP 404，`qwen-vl-ocr` → HTTP 403（同一 dashscope compatible-mode 端点）。因此第二条路径改用智普 `glm-4v-flash`；验证目标是**协议与适配器**，不是特定厂商。
- 凭据均只经环境变量注入；两个已提交日志已用正则核验，无 `sk-` / `AIza` / 智普 key 形态字符串。

### 6.2 端到端「App → Host → Core 触发翻译」当前**不可达**（产品缺口，不是环境问题）

- `HostCommandRegistry` 的翻译相关命令只有 **`save_manual_translation`**（手动保存），**没有自动翻译命令**。
- UI 侧 `Translate` 仅出现在批处理动作枚举（`StudioBatchActionKind.Translate`）与阶段标签（`StudioStages`）中，没有调用 provider 的接线。
- 与此一致：设置页「模型与设备」显示「待接入」。
- **结论**：条件 5 的「端到端」不能靠提供 API key 解决，需先实现「自动翻译」的 Host 命令与 UI 接线；那是独立功能卡，不是维护事项。

### 6.3 条件 5 的最终表述

**部分**：真实模型 API 调用已在**两条 provider 路径**上验证通过；**未做**代表性质量基线（无人工 ground truth）与 UI 端到端（功能未接线）。**Gate 仍 `BLOCKED`。**

## 7. 追加：条件 1 的 8 项 finding 已逐项裁决（2026-11-14）

- **裁决文件**：[`MAINT-1-GATE-CONDITION-1-FINDING-ADJUDICATION-2026-11-14.md`](MAINT-1-GATE-CONDITION-1-FINDING-ADJUDICATION-2026-11-14.md)。
- **数量差异**：本评估原文写「7 项」，limitation 矩阵现有 **8 项 `IMPL`**（`L-AI1-6` 为后续增补）。**以矩阵 8 项为准**，原文按 append-only 不改。
- **裁决分布**：`IMPL-NOW` 3 项（L-F1-2 wire 负例、L-L1-4 64 位边界、L-AI1-6 死方法清理）／`IMPL-CARD` 4 项（L-R1-1、L-R2-1 UI 控件；L-L1-1 DTO 投影；L-L1-2 排序功能）／`KEEP-NOTRUN` 1 项（L-F1-3 压测）／`OUT` **0 项**。
- **对条件 1 的影响**：从「未处置」→「**已逐项裁决**」；但 **8 项中 0 项已关闭**（3 个 IMPL-NOW 尚未实现），故 **条件 1 仍未完成**。
- **Gate 结论不变：仍 `BLOCKED`。**

## 8. 条件状态快照（2026-11-14 晚，本轮末）

| # | 条件 | 状态 |
|---|---|---|
| 1 | 8 项 finding 处置并验证 | **已裁决 / 0 项关闭**（未完成） |
| 2 | `AUDIT-11-INC-001` 远端可见性调查 | 未完成（需远端访问） |
| 3 | 完整 GUI / Core / Host 流程 + TestHost | 部分 |
| 4 | 当前 commit 的 Windows 包 + clean install 矩阵 | 未完成（需重新打包 sidecar） |
| 5 | 模型 / API 与代表性质量验证 | 部分（两条 provider 路径真实调用已验；L2 因缺 OCR 模型 BLOCKED；无人工 GT） |
| 6 | 当前 head 门禁 + 独立最终 Review | **已完成**（交付头 `d0ae50305` 冻结，四件套绿，Review 已登记） |

## 9. 条件 1 进度更正：3/8 已关闭（2026-11-14）

- 复核实现发现裁决文档里判为 `IMPL-NOW` 的 3 项（L-F1-2、L-L1-4、L-AI1-6）**早已完成**，矩阵未回流。
- **条件 1 关闭进度：0/8 → 3/8。**
- 剩余 5 项：`IMPL-CARD` 4（L-R1-1、L-R2-1、L-L1-1、L-L1-2）+ `KEEP-NOTRUN` 1（L-F1-3）。
- **条件 1 仍未完成**（5 项未关闭），**Gate 仍 `BLOCKED`**。

## 10. 条件 5 重大推进：Core→落库的端到端翻译已被证明（2026-11-14）

- **结果**：`translate_all` 单次运行 `terminal = completed`、`error_codes = []`；`ocr`/`color`/`term_extract`/`translate`/`segment`/`mask_refine`/`inpaint`/`render` **全部 completed**；**`regions_translated_differs = 2`**。
- **实证译文**（`キャロット？` → `Carrot?`；`かあ かあ かあ` → `Caw caw caw`），写回 `regions.text_json.machine_translation`，与日文原文不同。
- **路径**：远程视觉 OCR（GLM-4V）+ 远程翻译（DeepSeek）在同一运行内串通，非 provider 层单点验证。
- **条件 5 的现状更新**：
  - 真实模型 API 调用：✅（翻译 + 视觉 OCR 两条路径）
  - **Core → provider → 落库端到端：✅（本次）**
  - 代表性质量基线（人工 GT）：❌ 仍未做
- **结论**：条件 5 仍是「部分」，但**剩余缺口只剩人工质量基线**；不再是"端到端未证"。
- **Gate 仍 `BLOCKED`**（条件 1 剩 5 项、2/4 未动）。
- **附带更正**：此前三轮 L2 失败的「Core 侧就绪判定缺陷」判断作废，真因是探针 `overrides` 硬编码 `manga-ocr` 且优先级高于 `pipeline_defaults`。