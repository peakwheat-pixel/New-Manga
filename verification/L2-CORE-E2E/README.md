# L2-CORE-E2E：Core → provider → 落库端到端翻译（2026-11-14，验证任务）

**结论：未取得翻译产出（BLOCKED，非通过）。** 本轮把链路推进到「StartRun 被接受 + Run 真实执行 + 逐 target 落 typed 失败」，但**停在 `detect` 步，translate 从未执行**。

## 1. 源码 Core 入口（探明结果）

| 问题 | 结论 |
|---|---|
| 入口 | `python -m bootstrap.core_service` **可跑**（`src/bootstrap/core_service.py:9008` 的 `if __name__ == "__main__": raise SystemExit(main())`） |
| 必需环境 | `cwd = <repo>/src` 且 `PYTHONPATH=<repo>/src`（二者都给最稳；缺 cwd 时 `bootstrap` 包不可导入） |
| 其它环境变量 | 与旧探针一致：`NEWMANGA_DATA_ROOT` / `M2RC1_DERIVED_ROOT` / `M2RC2_CATALOG_DB` / `M2RC1_MANAGED_ROOT` |
| 握手 | `core.ping` 返回 `protocol_version 2.3`、`status=ready` |

探针已加 `--python-core <repo>` 模式（`workspace/flea-loop/run_translate_probe.py`）：spawn `[sys.executable, "-m", "bootstrap.core_service"]`，cwd/PYTHONPATH 指向 `<repo>/src`；`--sidecar` 变为可选。

## 2. fixture 迁移

- 新 work-root：`workspace/task-envs/L2-CORE-E2E/work-root`（从 `BOOK-FIXTURE-1/isolated-data` **复制**，旧目录未动）。
- 迁移：**v6 → v14**（`[core.schema] applied 8 migration(s) up to v14`），自动备份 4,023,101 B（verified=True）。
- 迁移后计数不变：`books=1, chapters=1, pages=8, regions=0`；新增表 `source_entries` / `page_bindings`（均 0 行）；`media_artifacts` 0 行，但 8 张原图在 `managed/books/<book>/chapters/<chapter>/original/*.jpg` 且 `pages.managed_original_ref` 有值（Managed Copy 读路径仍可用）。

## 3. 关键结构性发现（比"缺模型"更根本）

provider 实例在**装配期**按 `pipeline_defaults` 行一次性构建（`core_assembly.py:1421-1426`，即 T-A AC8 的"配置变更需重启"）。因此：

- 只在 `StartRun.overrides.settings.providers.profiles` 里给 profile **不生效**：registry 的 `freeze_run_snapshots` 用装配期实例的 `config` 生成 `execution`，实测得到 `base_url="" / model="" / credential_ref=None` → `validate_provider_execution` 拒绝，StartRun 报 `RUN_SNAPSHOT_INCOMPLETE: provider replay configuration is incomplete or unsafe`。
- **正确做法**：先把 profile + bindings 写进 `pipeline_defaults`（DB 行），再启动 Core。本轮按此 seed 后 StartRun 即被接受。

## 4. 运行结果（真实输出）

```json
{"terminal":"completed_with_failures","counts":{"total":8,"completed":0,"failed":8,"skipped":0},
 "step_status":{"detect":{"failed":8}},
 "distinct (step,error_code)":[["detect","PROVIDER_NOT_CONFIGURED"]]}
```

- run_id `run-84394ff7494e43c5afad314074b56e8f`；`regions=0`、`region_revisions=0` ⇒ **`regions_translated_differs = 0`（无任何翻译产出）**。
- 卡在 `detect`：fixture 是 **0 region** 初始态，`translate_untranslated` 对 region-less 页先跑 `detect`；`manga-ocr` 只覆盖 OCR，**没有 detect provider 绑定**，故 8/8 死在 detect。

## 5. 已排除的假设

1. **"sidecar 缺模型"**：本轮完全绕开 sidecar（源码 Core），失败原因与模型无关（detect 连 provider 都没有）。
2. **"fixture 被污染"**：新目录 copy，迁移后 `regions=0` 未变。
3. **"Host/探针 payload 形状错"**：StartRun 被接受并产出真实 run/target 记录。
4. **"Credential 路径不通"**：尚未走到 translate 步，**未验证**（既不能确认也不能排除）。
5. **"profile 注入方式"**：已证明 run-level override 无效、必须 DB seed（§3）。

## 6. 下一步需要的条件（三条，任一即可推进）

- **A. 提供 detect provider**：给 `detect` 绑一个可用检测器（远程视觉模型或本地 ONNX + 模型文件），才能让 0-region 页走到 ocr→translate。
- **B. 预置 regions + OCR 文本**：直接 seed 区域与日文文本，改跑 `retranslate_region`（translate+render），跳过 detect/ocr。**需要 OCR 文本形状定义**（`regions.text_json` 的 key 约定）。
- **C. 本地 OCR 模型**：`manga-ocr` 需要模型文件（仓库内没有；0.1.1 发布包内有 detector，但那是 sidecar 资源）。

**未做产品代码改动**（只改探针与本次 work-root/DB 数据，均在工作区）。

## 7. 证据文件

- `l2-run.json`：StartRun → 轮询 → GetTaskProjection 的完整原始响应（无 key）
- `core-stderr.log`：源码 Core 的 stderr（含 T-B 新增的 `[core.run]` 精确原因行）
- `probe-console.log`、`profile-deepseek.json`（只含 `credential_ref`，不含 secret）
## 8. 路线 B 复跑（DeepSeek 凭据已换；seed 走产品 API）

**结论：仍未证明 Core→落库端到端。** 数据与凭据都已就位，但 translate 始终未执行。

### 8.1 凭据

- 取自用户授权文件 `C:\Users\49745\DeskBox\杂项文件\api.txt` 的 **deepseek** 段（第 3 行 `api：sk-…`，35 字符）。
- 先用一次最小 `POST https://api.deepseek.com/v1/chat/completions`（model=`deepseek-chat`, max_tokens=5）探测：**HTTP 200，返回 "OK"** ⇒ key 有效（`key_present: true`）。
- 用 `cmdkey /generic:NewManga/provider/3819f991cbe54001ba45b6f8524f260c/3218c7670af30a61c068a7caeafa0d0f /user:apikey /pass:<key>` 写入 Windows 通用凭据（覆盖 OpenCode 时代的旧值）；**key 未进入任何仓库文件/日志/提交**，探测输出不含 key。

### 8.2 seed 形状（VERIFIED vs INFERRED）

走**产品 API** seed，不手写 SQL/JSON 快照：

| 字段/结构 | 依据 | 等级 |
|---|---|---|
| region 创建：`core.editing.create_region(page_id, RegionGeometry(bbox=BBox(x,y,w,h)))` | `src/application/editing/service.py:680-711`；`BBox/RegionGeometry` 定义 `src/domain/regions/entities.py:62-105` | **VERIFIED** |
| 首修订与 current 指针同一事务 | `service.py:712-717` 注释与实现 | **VERIFIED** |
| 原文写入：`core.editing.apply_ocr_result(region_id, ocr_text)` → `RegionText.ocr_text` | `src/application/editing/service.py:1248-1259`；`RegionText` 字段 `src/domain/regions/entities.py`（`ocr_text`/`machine_translation`/`edited_translation`） | **VERIFIED** |
| 「原文」语义 = `ocr_text`，译文 = `machine_translation`，final 由 `resolve_final()` 决定 | `entities.py` `RegionText.resolve_final` | **VERIFIED** |
| 区域类型默认 `SPEECH`、`sfx_policy=SKIP` | `service.py:685-687` 默认参数 | **VERIFIED** |
| 手动译文会触发 manual 保护（我曾用 `save_manual_translation` 写日文，导致后续 `retranslate_region` 直接 skipped） | 实测：revision_no=2 / `manual_edited=True` 的目标被 `skipped` | **INFERRED（实测现象推导）** |

seed 后核对（脱敏）：`pipeline_defaults.settings_json.providers.profiles["openai-compatible-translation"]` 有 `base_url=https://api.deepseek.com/v1`、`model=deepseek-chat`、`credential_ref=NewManga/provider/3819f991…`；`provider_bindings_json={"ocr":"manga-ocr","translate":"openai-compatible-translation"}`。

### 8.3 两次运行的真实结果

| 命令 | 终态 | 关键输出 |
|---|---|---|
| `retranslate_region`（region scope，全新无手动译文的区域） | **blocked** | `counts={"total":1,"blocked":1}`，`step_status={}`、`error_codes=[]`、`blocked_reasons=[]` ⇒ 阻塞发生在**步骤执行前**，投影未给出原因（见 §8.4 待查点） |
| `translate_single`（region scope） | start_failed | typed `TARGET_NOT_FOUND: page command requires page scope`（命令要求 page scope，属输入形状问题，已排除为"无关失败"） |

区域复查：`ocr_text=おはようございます。今日はいい天気ですね。`、`machine_translation=""`、`final=""` ⇒ **`regions_translated_differs = 0`**。

### 8.4 剩余待查（下一轮的第一步）

`retranslate_region` 的 blocked 没有 error_code —— 需要查 planning 阶段的门（`PROVIDER_UNAVAILABLE`/readiness gate 或 lineage guard）。已知不是：凭据（key 200 有效）、profile 装配（§3 已 seed 且 StartRun 被接受）、scope（region 合法）。

## 9. 对 L2 的一句话结论

**Core→落库的端到端翻译尚未被证明。** 已证明的相邻事实：源码 Core 入口可跑、fixture v6→v14 迁移无损、装配期 provider 约束（含 `RUN_SNAPSHOT_INCOMPLETE` 实测）、DeepSeek 凭据可用、区域/原文经产品 API 可 seed、`retranslate_region` 在 region scope 下被接受并执行到 planning（blocked，原因未投影）。
## 10. page scope 尝试（L2 最后一轮）

**结论：仍无产出 ⇒ L2 登记 `BLOCKED`（环境资源缺失，非产品缺陷、非代码问题）。**

### 10.1 本轮设置（全新建根，不叠上一轮状态）

- 新 work-root：`workspace/task-envs/L2-CORE-E2E/work-root-pagescope`（从 `BOOK-FIXTURE-1/isolated-data` 复制，**v6 → v14**，`applied 8 migration(s)`，自动备份 4,024,374 B verified）。
- seed 全部走产品 API：
  - 2 个 region 在同一页 `f52f2772…`（`editing.create_region` + `apply_ocr_result`，日文 `ocr_text`：`おはようございます。` / `今日はいい天気ですね。`），**未用** `save_manual_translation`；
  - `pipeline_defaults`：`save_settings_section("providers", {profiles:{openai-compatible-translation: deepseek…}})` + `save_provider_binding("ocr","manga-ocr")` / `("translate","openai-compatible-translation")`（T-A 的 seam，非手写 SQL）。
- 凭据：vault 已有 DeepSeek key（§8.1，`key_present: true`）。

### 10.2 结果

```
translate_all + page scope → terminal=completed_with_failures
counts={"total":1,"completed":0,"failed":1}
step_status={"ocr":{"failed":1}}
error_codes=[("ocr","PROVIDER_NOT_CONFIGURED")]
```

⇒ **卡在 `ocr`，translate 从未执行**；`machine_translation` 仍为空，`regions_translated_differs = 0`。

**为什么是 OCR**：`translate_all` 对页面先跑 ocr；`ocr` 绑定虽已 seed 为 `manga-ocr`，但本地 `manga-ocr` 需要 ONNX 模型文件，而**仓库与工作区都没有该模型**（本 work-root 内 `*.onnx` = 0 个）⇒ provider 未就绪，按 fail-closed 报 `PROVIDER_NOT_CONFIGURED`。这与 `REAL-TRANSLATE-PROVIDER-1` 轮次 29 的 `ocr / INVALID_INPUT`（region-less 页）和本轮同一根因族：**执行链需要一个真正可用的模型/视觉 provider，工作区里没有**。

### 10.3 三条路线的终局汇总（L2 已验证到的最远处）

| # | 命令 + scope | 终态 | typed 结果 | 卡点 |
|---|---|---|---|---|
| 1 | `translate_untranslated` + book | completed_with_failures | `detect / PROVIDER_NOT_CONFIGURED`（8/8） | 0-region 页先跑 detect，无 detect provider |
| 2 | `retranslate_region` + region | **blocked** | 无 error_code（planning 门） | 步骤执行前被拒，原因未投影 |
| 3 | `translate_all` + page | completed_with_failures | `ocr / PROVIDER_NOT_CONFIGURED` | 本地 `manga-ocr` 模型缺失 |

### 10.4 BLOCKED 登记

- **卡点**：执行链第一个需要**推理模型**的步骤（detect / ocr）。
- **typed 错误**：`PROVIDER_NOT_CONFIGURED`（路线 1、3，有 code）；路线 2 为**无 error_code 的 planning 门**。
- **已排除的假设（6 项）**：① sidecar 缺模型（已改源码 Core）；② fixture 污染（每轮新建根，regions 由 seed 控制）；③ Host/探针 payload 形状（StartRun 均被接受并产生 run/target）；④ 协议 minor/字段错位（minor 3 直连，T-B 已证）；⑤ 凭据无效（DeepSeek key HTTP 200）；⑥ 装配期 profile 缺失（`RUN_SNAPSHOT_INCOMPLETE` 已解，seed 后 StartRun 通过）。
- **下一轮需要的具体条件（任一）**：
  - **D. 提供 `manga-ocr`（或任一 OCR）ONNX 模型文件**并放到 Core 能解析的位置 → 路线 3 即可走通（detect 可跳过：page 已有 region）。
  - **E. 配置远程视觉/OCR provider**（如 GLM-4V 等，需要对应 key）→ 可同时替代 detect/ocr。
- **性质**：环境资源缺失，**不改产品代码即可解决**；L2 验证结论不影响产品可用性，仅影响 Gate 条件 5 的措辞。

### 10.5 一句话

**Core→落库的端到端翻译未获证明**（三次尝试均在"第一个需要模型的步骤"止步，或止步于无 code 的 planning 门）；已证明的相邻事实见 §3/§8.2/§9 与本节 10.1。
## 11. 路线 E：远程视觉 OCR（GLM-4V）— 最后一次尝试，仍未产出

**结论：仍 `BLOCKED`。** 且证据指向**不是 provider 配置形状**问题，而是 Core 侧 provider **就绪/解析**判定（属产品缺口范畴，按指令 STOP 上报，未改 `src/**`）。

### 11.1 本轮设置（全新根）

- 新 work-root `workspace/task-envs/L2-CORE-E2E/work-root-glm`（从 `BOOK-FIXTURE-1/isolated-data` 复制，`v6 → v14`，自动备份 4,024,458 B verified）。
- 凭据：从用户授权 `api.txt` 的**智普**段（`模型名称：glm` / `base url：https://open.bigmodel.cn/api/paas/v4`）取出 key，`cmdkey /generic:NewManga/provider/glm-vision-ocr/ocr-basic /user:apikey /pass:<key>` 写入 vault（`key_present: true`；未进仓库/日志/提交）。
- seed（`pipeline_defaults`，写后启 Core）：profiles = `openai-vision-ocr`（`provider_type=openai-compatible-vision`, `base_url=https://open.bigmodel.cn/api/paas/v4`, `model=glm-4v-flash`）+ `openai-compatible-translation`（DeepSeek）；bindings = `{"ocr":"openai-vision-ocr","translate":"openai-compatible-translation"}`。
- 区域：同一页 2 个 region，日文 `ocr_text`（`おはようございます。` / `今日はいい天気ですね。`）。

### 11.2 三种绑定形状都试过（这是关键证据）

| # | ocr 绑定形状 | 结果 |
|---|---|---|
| E-1 | `{"ocr": "glm-vision-ocr"}`（用户 profile id，profile_type=openai-compatible-vision） | `ocr / PROVIDER_NOT_CONFIGURED` |
| E-2 | `{"ocr": "openai-vision-ocr"}`（**固定注册槽 id**），且 profiles 只留槽 profile（误删 translate → 触发 `RUN_SNAPSHOT_INCOMPLETE`，已排除为操作失误） | start_failed（配置不全，非目标结论） |
| E-3 | `{"ocr": "openai-vision-ocr"}` + profiles **同时**含 translate（正确形状） | `ocr / PROVIDER_NOT_CONFIGURED` |

**进程内核对（E-1 形状）**：`create_run` 后 `run.provider_binding_snapshot["ocr"]` 是**完整**的
`{provider_id:"glm-vision-ocr", execution:{provider_id:"openai-vision-ocr", provider_type:"openai-compatible-vision", base_url:"https://open.bigmodel.cn/api/paas/v4", model:"glm-4v-flash", credential_ref:"NewManga/provider/glm-vision-ocr/ocr-basic", adapter_version:"openai-compatible-v1", network_profile:{...}}}` + 合法 digest。

⇒ **冻结快照里的 replay 配置是完整的**，但执行期该 step 仍报 `PROVIDER_NOT_CONFIGURED`。按卡面判据：这不是"provider 配置形状不对"（形状已被快照证明），而是 **Core 侧 vision provider 的就绪/解析判定**（registry resolve/readiness gate）未接受该配置 —— **属产品缺口，STOP 上报，未改 `src/**`**。

### 11.3 已排除（本轮新增）

1. `ocr` 绑定缺失（快照里明确存在）；2. 槽位 id 写错（E-2/E-3 直接绑 `openai-vision-ocr` 仍同样失败）；3. translate 配置被 profile 段覆盖（E-3 已同时保留两者，StartRun 通过、只有 ocr step 失败）；4. GLM key 未落 vault（cmdkey 成功且 target 与 profile `credential_ref` 一致）；5. 区域缺失（同页 2 个 region 已 seed，且 page scope 展开成功）。

### 11.4 下一步需要的条件（不再是"跑一次"能解决）

- **产品侧**：查 vision OCR 的 registry 就绪/解析为何在 execution 完整时仍判 `PROVIDER_NOT_CONFIGURED`（候选：`requirements` 的 endpoint/credential 校验、`resolve_for_run` 对 profile-id vs 槽 id 的比较、或 vision provider 需要 detect 前置）。这需要读 `src/infrastructure/providers/**` 并可能改代码 —— 超出本验证任务边界。
- 或回到 **D（本地 ONNX 模型）**，绕开远程视觉路径。

### 11.5 一句话

**Core→落库的端到端翻译仍未证明**；本轮把失败从"缺模型"精确推进到「execution 完整但 provider 解析判 not-configured」，这是产品侧需要单独定位的缺口，不是配置问题。
## 12. 路线 E 重做（严格时序，全新根 work-root-glm3）

### 12.1 两个时间戳 + 无重启

| 事件 | 本地时间 |
|---|---|
| **T1 seed 完成** | `2026-11-14T21:44:44` |
| **T2 Core 进程启动** | `2026-11-14T21:44:44` |
| **T3 run 结束** | `2026-11-14T21:44:48` |

**T2 之后没有重启任何进程**：probe 只 spawn 一次 Core（`python -m bootstrap.core_service`），StartRun→轮询→GetTaskProjection 全程在**同一进程**内完成，T3 即该进程退出。seed 由**独立进程**在 T2 之前完成并关闭连接；`pipeline_defaults` 用**纯 SQL** 写入（不再经过任何 Core 装配），因此 run Core 装配时读到的一定是已提交的行。

### 12.2 `pipeline_defaults` dump（脱敏，取自同一 work-root 的 DB 行）

```
providers.profiles:
  openai-vision-ocr            provider_type=openai-compatible-vision
                               base_url=https://open.bigmodel.cn/api/paas/v4
                               model=glm-4v-flash
                               credential_ref=NewManga/provider/glm-vision-ocr/ocr-basic
  openai-compatible-translation provider_type=openai-compatible-translation
                               base_url=https://api.deepseek.com/v1
                               model=deepseek-chat
                               credential_ref=NewManga/provider/3819f991…/3218c767…   (引用，非 key)
provider_bindings:
  {"ocr": "openai-vision-ocr", "translate": "openai-compatible-translation"}
```

### 12.3 本轮结果：**OCR 首次真正跑通**，但 translate 仍未执行

```
terminal = completed_with_failures
counts   = {"total":1,"completed":0,"failed":1}
step_status = {"ocr": {"completed": 1}, "color": {"completed": 1}, "term_extract": {"failed": 1}}
error_codes = [("term_extract", "INVALID_INPUT")]
```

**`step_runs.error_detail`（原文）**：

| step | status | error_code | error_detail |
|---|---|---|---|
| ocr | **completed** | — | （无） |
| color | **completed** | — | （无） |
| term_extract | failed | `INVALID_INPUT` | **`region has no OCR text to extract terms from (stage=term_extract)`** |

⇒ **GLM-4V 远程视觉 OCR 在 Core 里成功执行**（route E 的核心假设成立），失败点前移到 `term_extract`：某 region 的 `ocr_text` 为空（运行后实测 region `d1775151…` 的 `ocr_text` 为空串，另一个 region 仍保留日文）。

### 12.4 关键发现：之前 3 轮失败的真因是**探针自己的 override**

`run_translate_probe.py` 一直硬编码
`overrides.provider_bindings = {"ocr": "manga-ocr", "translate": <provider>}`，
而 **Run overrides 的优先级高于 `pipeline_defaults`**，所以无论怎么 seed，`ocr` 都被打回本地 `manga-ocr`（这正是 `manga-ocr ONNX weights are not installed` 的来源）。上一轮我把它误判为"Core 侧就绪判定缺陷"，**该判断作废**。
本轮给探针加 `--ocr-provider`（config-only 改动，不在仓库内），传 `openai-vision-ocr` 后 OCR 立刻 completed。

### 12.5 剩余缺口（下一步条件，改动仍在配置/数据层）

`term_extract` 需要该 region 有非空 `ocr_text`。当前 OCR 覆盖写回后 region 1 变空（GLM 对该 bbox 的识别结果为空或写回为空）。可选（都无需改产品代码）：
- 换一张文字更清晰的页/调整 region bbox，让 GLM 对每个 region 都返回非空文本；
- 或先跑 `ocr` 单步、人工确认 region 文本后，再跑不含 ocr 的 translate 命令。

### 12.6 一句话

**Core→落库的端到端翻译仍未证明**，但链路已推进到 **ocr(远程视觉) completed + color completed**，`regions_translated_differs = 0`；阻断点从"provider 配不上"变成"某 region 的 OCR 文本为空导致 term_extract 失败"，属于**数据/图片质量**层，而非 provider 形状或时序。