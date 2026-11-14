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

## 11. 条件 1 进度再更正：4/8 已关闭（codex 外部裁决，2026-11-14）

- codex 外部裁决（用户 2026-11-14 授权代裁）指出 DSH 的前提错误：`ChapterSummary` **已投影** `kind` 与 `custom_rank`，且该投影已由 **M2-C1 rev 2.16 冻结**（`CoreServiceClient.cs:38`、`core_service.py:4609`、`M2-C1:34/:204`）。
- ⇒ **L-L1-1 判 `SOLVED`**；**条件 1 关闭进度：3/8 → 4/8**。
- 剩余 4 项：`IMPL-CARD` 3（L-R1-1、L-R2-1 阅读器 UI 控件；L-L1-2 手动排序）+ `KEEP-NOTRUN` 1（L-F1-3 压测）。
- **条件 1 仍未完成**；**Gate 仍 `BLOCKED`**。

## 12. codex 外部裁决结论（用户授权代裁，`MAINT-1-EXTERNAL-ADJUDICATION-codex-2026-11-14.md`）

| 事项 | 裁决 |
|---|---|
| **A. `custom_rank` 排序语义** | **选 1：手动拖拽排序**。理由：章节号是字符串，存在特别篇/空值/重复值/非数字编号，自动重排不可靠且可能打乱既有顺序。**契约边界**：wire 返回顺序**冻结为 `sort_order`**，排序在 UI/Host 消费投影层做；若要改 wire 顺序或加批量原子重排命令，须另行评估并经 DSH 授权 UNFREEZE。开 **1 张候选卡**（拖拽 + 持久化 + 重启回读 + 空值/重复/新增 + 失败与并发保护）。 |
| **B. provider 配置生效缺陷** | **选 3：暂时保持现状**，不为热重建或错误码拆分单开实现卡。理由：热重建会引入进行中任务、并发切换、资源回收、密钥生命周期风险；错误码 UNFREEZE 有兼容成本。保留并清楚展示重启提示，**不得声称保存后立即生效**；不新增 wire 命令、不拆错误码、不授权 UNFREEZE。若出现高频配置变更或恢复失败，再由 DSH 重新排期。 |

## 13. 条件 2 更正：调查已完成（接手会话复核，2026-11-14）

**此前 §2/§3/§8 记的"条件 2 未完成、需远端访问"是滞后记录。** 复核实现与 Task 状态后更正：

| 项 | 证据 |
|---|---|
| Gate 条件 2 原文 | "完成 `AUDIT-11-INC-001` 的只读远端可见性调查**或**由产品 Owner 明确接受该未知风险"（`audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:26`） |
| 调查 Task | `SEC-01-REMOTE-VISIBILITY-1`：`status: done`，`integration_commit = delivery_head = de79702b96f99e663442da3a2158c88d98385962` |
| 调查结论 | 远端可见性 **从 `unknown` 升级为「已确认可见」**：仓库匿名公开；`cc88d1ee`、`b1c1f5a5` 公开可见；`.tmp.driveupload` 在两者历史树中可枚举文件与 blob SHA；不在默认分支当前 tip。证据 `verification/SEC-01-REMOTE-VISIBILITY-1/REPORT.md:34-39` |
| 处置 Task | `SEC-02-REMOTE-DISPOSITION-1`：`status: done`，`integration_commit = 1a3b3616b0496f4e61b2f6a08eef32de872a90f0`；推荐 **A：保持现状 + 监测**（处置动作均不可逆或影响外部协作者，需显式 Owner 授权） |

**判定：条件 2 的「调查」分支已满足 ⇒ 条件 2 由「未完成」改为 `MET`。**

**必须同时登记的限制（不得淡化）**：

1. 调查结论是"**已确认可见**"，不是"已消除"。风险本体仍然存在。
2. 处置动作（删除含素材分支、force-push 改写历史、仓库转私有、联系 GitHub）**一项都未执行**，且按 SEC-02 均需 Owner 显式授权。这不属条件 2 字面，但属发布决策必须披露的已知风险。
3. 因此**`Gate` 仍 `BLOCKED`** —— 条件 2 满足不改变条件 1/3/4/5 的缺口，也不构成发布许可。

**教训（并入纪律）**：handoff 与本文档 §2/§8 都可能滞后于实际 Task 状态；"依赖任何计数前先核实现"同样适用于 Gate 条件表本身。

## 14. 条件 1 逐项复核：8 项均有处置依据（2026-11-14 接手会话）

对 `MAINT-1-GATE-CONDITION-1-FINDING-ADJUDICATION-2026-11-14.md` §1 的 8 项逐条核实现，**不是**依赖矩阵/旧计数：

| # | finding | 原判 | 逐项核实结果 | 证据 |
|---|---|---|---|---|
| 1 | `L-R1-1` Reader UI 未接线（偏好应用/书签面板/整书进度/reset 确认） | `IMPL-CARD` | **四项均已实现**：书签面板/整书进度/reset 确认由 `MAINT-2-C1-BATCH-1` AC1 交付；偏好"应用"由 `ReaderViewModel.LoadAsync:273` → `ApplyReadingPreferencesAsync` 接线 | `ReaderVisibleControlsTests`（4 项，`931/0/11` 全绿中通过）；`ReaderPageView.cs:151/278/286/362` |
| 2 | `L-R2-1` 可见控件未接线 | `IMPL-CARD` | **`MAINT-2-C1-BATCH-1` AC1「READ-2 可见控件」= MET**（该卡 `closed_with_limitations`） | `doc/tasks/MAINT-2-C1-BATCH-1.md:AC1` |
| 3 | `L-F1-2` wire 级 `FONT_DELETE_FAILED` 负例 | `IMPL-NOW` | 已由 BATCH-1 AC2 关闭 | 同上 AC2；已在此前 §9 计入 |
| 4 | `L-F1-3` 大文件/并发/占用文件压测 | `KEEP-NOTRUN` | **处置维持 `KEEP-NOTRUN`**（重开条件已给出）。注意：BATCH-1 AC3 补的是**边界测试**，不等于压测，不得据此说压测已完成 | §1 裁决第 4 行；本文 `MAINT-1-EXISTING-FINDINGS` E-5 |
| 5 | `L-L1-1` `kind` 未投影 | `IMPL-CARD` | **`SOLVED`**（codex 纠正：M2-C1 rev 2.16 已冻结投影） | §11 |
| 6 | `L-L1-2` `custom_rank` write-only + 排序未实现 | `IMPL-CARD` | 读回闭环由 BATCH-1 AC5 完成；**排序 UI 由 `CHAPTER-MANUAL-SORT` 交付**（复用 `ReorderChapters`/`sort_order`，零 UNFREEZE） | `doc/tasks/CHAPTER-MANUAL-SORT.md`；`verification/CHAPTER-MANUAL-SORT/` |
| 7 | `L-L1-4` 64 位边界 | `IMPL-NOW` | 已由 BATCH-1 AC6 关闭 | 同上 AC6 |
| 8 | `L-AI1-6` 死方法/旧注释 | `IMPL-NOW` | 已由 BATCH-1 AC7 关闭 | 同上 AC7 |

**更正后的条件 1 计数（唯一口径，STATUS 与本表一致）**：

| 口径 | 数字 | 构成 |
|---|---|---|
| **已关闭（有实现与证据）** | **6/8** | L-R1-1、L-R2-1（BATCH-1 AC1）、L-F1-2（AC2）、L-L1-1（codex 纠正 SOLVED）、L-L1-4（AC6）、L-AI1-6（AC7） |
| **本卡收口** | +1 | L-L1-2（`CHAPTER-MANUAL-SORT`：复用 `ReorderChapters`/`sort_order` 实现排序闭环） |
| **裁决接受为已知限制** | 1 | L-F1-3 `KEEP-NOTRUN`（压测确实未做） |

- 合计 8 项均有处置依据；**但只有 6 项现在可以称"已关闭"**，`L-L1-2` 待本卡独立复核通过后计入，
  `L-F1-3` 永远不应写成"已验证通过"。
- r1 复核（`doc/reviews/CHAPTER-MANUAL-SORT-review-r1.md` F4）指出本文与 STATUS 曾出现 4/8 与 8/8 并存的
  两个口径；本节与 STATUS 已统一为上面的"6 + 1 + 1"。
- **同时必须登记两个相邻缺口**（不改变上述 8 项判定，但属真实用户可见问题）：
  - `E-4` 阅读偏好只有"应用"、**没有保存入口**（`SaveReadingPreferencesAsync` 生产路径零调用）；
  - `E-5` `L-F1-3` 的压测未被 BATCH-1 AC3 的边界测试替代。
- 两者见 `MAINT-1-EXISTING-FINDINGS-2026-11-14.md`。

**Gate 结论不变：仍 `BLOCKED`** —— 条件 3（完整 GUI/Core/Host 矩阵，且 sidecar 过期使真实集成不可跑）、
条件 4（当前 commit 的 Windows 包，需 PyInstaller）、条件 5（人工 GT 基线）仍未满足。条件 1 与 2 的
推进**不构成发布许可**。

## 15. 条件 3 覆盖矩阵（2026-11-15，`GATE3-COVERAGE-MATRIX`，r3 定稿；引用需注明基线 `d86f185ca`）

条件 3 此前只记作"部分"，没有任何清单说明覆盖到哪。现已按 **GUI + Host + CoreClient 三层**逐格盘点，
见 `doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md`。要点：

- **GUI 层**：`App.Tests` **950/0/11/961**（`SETTINGS-ERROR-STATE-1` 后 +3），`[AvaloniaFact]` 文件 **63 个**。
  四页 × 13 类流程（**本矩阵限定范围**）**所有 ❌ 格已清零**（原先唯一缺的"设置页错误态"已由 `SettingsErrorStateTests.cs:35/:53` 补上：
  加载抛异常 → `State==Error` + 可重试文案 + 视图出现"设置错误"banner 与"重试"按钮；
  实测回退该 catch 后 2 个测试变红）。四页有 PNG 级渲染证据（断言四帧 `PixelSize` 非零）。
- **Host/Core 层**（r1/r2 复核两次纠正后）：本环境真实执行 `321 + 186 passed`（含 wire 契约、命令覆盖、
  Host 单元面、Source 调度、Run 授权及各 IPC 类的非 skip 方法）；**100 个 skip**（Host 74 + CoreClient 26；App 另 11）
  NOT_RUN，按实测类分布列于矩阵 §4.2/§4.3。
- **skip 归因（两次更正）**：App 11 skip = **7 sidecar**（4 个 attribute 类型：`HostSidecarFact`×2、
  `RunSidecarFact`×2、`RunBookFixtureFact`×1、`WritePolicySidecarFact`×2）+ **4 非 sidecar**
  （perf 预算 / 真实进程 / 崩溃注入 ×2）。**"100 个 skip 全部卡 E-2"已撤回**；"30 sidecar / 44 opt-in"的**总量可复现**（与 74 行实测相加一致），但逐类归属需逐条看 attribute。
- **我的一次实质判断失误（已登记在卡面）**：上一版把 `HostReaderChaptersIntegrationTests`(2) 与
  `HostRegionWorkbenchIntegrationTests`(4) 标为 `plain` 并声称"计入 passed"；r2 复核实跑证明它们是
  `[BookFixtureFact]` / `[RegionFixtureFact]`，6 个测试**全部 SKIP**。根因是用源码正则推断 gate 而非实测。r3 后 §4 已改为纯实测 skip 类分布（27 行合计 74），原始输出入库 `verification/GATE3-COVERAGE-MATRIX/host-skips.txt`、`coreclient-skips.txt`。
- **条件 3 的可判定形态**：剩余缺口分两类 —— ①被 skip 的 **111 个测试**（含 E-2 sidecar 与 opt-in 环境）；
  ②真机人工走查。**在本矩阵限定的 4 页 × 13 类内，❌ 格已清零**；仍有 2 个 ⚠️ 格、111 个 skip，且 §0 未纳回收站/命令面板/源恢复/沉浸等流程 —— 不得据此说"产品 GUI 无缺口"。
- **矩阵自身的边界**：只有 **13 格**被逐行核对断言（`SETTINGS-ERROR-STATE-1` 新增第 13 格），其余为"类摘要 + 方法名"，**不得当作已验证**；
  且它是**快照**，无自动失效检测（已在矩阵 §6 声明 staleness）。
- **条件 3 仍不判 MET。** 推进路径按性质分：解 E-2（本环境 PyPI 不可达，不可行）/ 开启 opt-in 矩阵 /
  补那 1 格 / Owner 接受边界。Gate 仍 `BLOCKED`。
## 16. 条件 4 打包探测（2026-11-15，`RELEASE-PACKAGE-PROBE-1`）—— 条件 4 首次真实推进

条件 4 此前一直被记作"未完成，需重新打包 sidecar + 签名"，但**从未探测过卡在哪一步**。本卡实测：

| # | 步骤 | 状态 |
|---|---|---|
| 1 | 构建绑定当前 commit 的包 | ✅ **完成**：`manifest-singlefile.json` 的 `git_head = 5dda04437…`（= 被探测 head），`result=PASS`，`NewManga.App.exe` 99,554,850 B，sha256 `EA01C8C7…76ED` |
| 2 | 启动冒烟 | ✅ **完成**：`window_found=true`、`window_title="New Manga"`、`host_ready=true`、`exit_code=0`、`exit_kind=natural`；截图显示四页导航与状态栏"Host 就绪" |
| 3 | 构建 `setup.exe` | 🟡 **工具具备、未执行**：`makensis v3.13` 在 `C:\Program Files (x86)\NSIS`（不在 PATH，`build-installer.ps1` 会 probe）；`.nsi` 用 `File /r "${STAGE_DIR}\*.*"`，不绑定特定布局 |
| 4 | sidecar 重建 | 🟡 **可做（已更正）**：默认 index 缺包，但 `pypi.org` 直连可下载 `pyinstaller 6.22.3`（r1 复核实测）；需再核 ML 栈 |
| 5 | 签名 | ⚪ **非阻塞**：`.nsi` 明确记载 unsigned 是已知限制，本机也无证书 |
| 6 | install/启动/升级回退/四页/卸载矩阵 | ❌ **未执行**（依赖第 3 步产物） |

**三条诚实边界（不得越过）**：
1. **「包能启动」≠「命令面完整」** —— 冒烟用的是 **2026-10-23 的旧 sidecar**，它早于 `ReorderChapters`
   （`83e45cfe5`）等多条现行命令（E-2 同根因）。
2. **包不自包含 sidecar** —— `singlefile-Release-win-x64\` 只有 `NewManga.App.exe`；smoke 是经
   `--sidecar-dir=` 外部注入。安装器 stage 必须把 sidecar 打进去。
3. **截图证明首屏，不证明四页可达** —— 冒烟只断言"窗口出现 + Host ready + exit 0"，不逐页导航。

**结论（r1 复核后更正）**：**不存在"只差一项"这种收窄** —— 我此前断言"PyPI 不可达"是错的
（`pypi.org` 直连可下载 `pyinstaller 6.22.3`）。工具层面全部具备，但工作量是完整的：
①重建 sidecar（Python 3.12+ 与钉死的 ML 栈）；②以 `app/core-sidecar/` 布局准备 stage 出 `setup.exe`；
③做 install / 启动 / 升级回退 / 四页 / 卸载矩阵。**它们尚未执行，条件 4 仍 NOT MET，Gate 仍 `BLOCKED`。**
另需注意：本次 `elapsed=7.7s` 是热缓存增量构建，只证明"本机可构建"，不证明 clean-room。
## 17. 条件 4 安装/卸载矩阵（2026-11-15，`INSTALLER-MATRIX-1`）

`RELEASE-PACKAGE-PROBE-1` 证明了"包能建、能起、Host 就绪"；本卡补上**安装器与 install/uninstall 矩阵**：

| 环节 | 结果 |
|---|---|
| stage | **848.15 MB / 1037 files**（exe 94.9 MB + sidecar 753 MB + 许可齐全） |
| `VERSION.json` | **实测值**（app exe sha256 / sidecar core_service sha256 / 两个 head），未沿用模板旧值 |
| `setup.exe` | `NewManga-0.1.1-setup.exe` **621.9 MB**，sha256 `3e6dcb1f…650a`，`makensis v3.13` |
| **clean install** | `/S` exit 0；程序目录、HKCU 卸载项（`New Manga 0.1.1`）、Start Menu 快捷方式齐备 |
| **安装后启动** | exit 0；`core_service ready` + `host_bridge ready` + `credential port ready` + **`self-check status=Passed`**（`core_protocol=2.3`，capabilities **17 条**） |
| **卸载** | `/S` exit 0；程序目录/HKCU/Start Menu 全部清理；**用户数据根 532 files / 967,726,273 B 逐字节未变** |
| 四页可达性 | **NOT_RUN**（未在打包产物上逐页导航，不用 headless 证据冒充） |
| 升级/回退 | **NOT_RUN**（需旧版 setup 作回退目标） |

**两条新记录**：

1. **我的副作用**：第一次启动漏传 `--data-root`（`NEWMANGA_DATA_ROOT` 只对 core_service 生效），
   污染了真实数据根（524→705 文件、+669 MB、`library.db` 被重写）；改为 `--data-root` 后实测未变。
   已写进证据 §3 并评估影响（新增主要是可再生的 `derived`/`logs`，且 sidecar 有 first-writable backup）。
2. **新缺陷 `E-8`**：安装后启动的 `startup.log` 有成批 **XAML 绑定错误**
   （`StudioPageViewModel` 缺 `IsEnabled`/`ActiveTabLabel`）⇒ 静默 UI 失效。
   **headless 测试抓不到**（不读该日志）—— 这正是"打包产物验证"的价值。

**条件 4 仍不判 MET**：sidecar 仍缺 SFX 权重（`yolo11s-seg.onnx`）、安装器 unsigned、
四页与升级/回退矩阵未做。但**安装/启动/卸载三条已实测通过**，且死字节级证明了用户数据根未被卸载触碰。
