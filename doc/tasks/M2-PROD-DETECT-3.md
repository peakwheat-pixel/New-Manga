---
id: M2-PROD-DETECT-3
title: "core.detect 命令面扩展 + frozen 进程内真实 detect 端到端验证（M2-PROD-DETECT-2 AC5 PARTIAL 闭合；Goal T1，自治执行 2026-10-01）"
kind: feature
status: done
integration_commit: 8fe5199c44b06e679a2f0e6ee47767032217eb47
approval: user_autonomous_mode_2026-10-01
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权 2026-09-28/30、自治授权 2026-10-01）
depends_on: [M2-PROD-DETECT-2]
base_commit: 46f079e83f39ae945c456f8876994ff609a7e0cb
branch: agent/zcode/M2-PROD-DETECT-3
worktree: G:/CODEX/New Manga.worktrees/M2-PROD-DETECT-3-zcode
delivery_head: 69a6e4e1（集成轮证据 commit；链=9d29a0c9→983a50d5→46d20842→9bcfd969→7314ad20（集成修正/重建输入）→69a6e4e1；status 保持 in_review，merge 由编排会话执行）
base_commit_note: 分支实际 base=46f079e8（release T1/T2/T3 同基分发）；契约（core.detect wire 设计）编写时参考的代码基线为 095e314d（46f079e8 的直接父代，见 git log），集成时已按 DSH r1 R13 更正锚点。
---

# M2-PROD-DETECT-3：core.detect 命令面扩展 + frozen detect 端到端验证

> 交付记录：`doc/handoffs/M2-PROD-DETECT-3-983a50d5.md`（实现 9d29a0c9 → 修复 983a50d5 → 证据 46d20842；构建输入绑定 983a50d5）。
> 集成修正：DSH r1 `approved_with_conditions` 全闭 @`7314ad20`（重建输入）+ 集成轮证据（见「集成修正记录」）；最终交付锚点见 frontmatter `delivery_head`。

## 来源与目标

- 来源：M2-PROD-DETECT-2 AC5=PARTIAL 的 NOT_RUN 子项（frozen 进程内 ML import/detect——frozen 命令面 core.ping/ListBooks/core.shutdown 无 detect RPC，结构性不可达）。登记的后续 slice 由本轮 Goal（GOAL.md T1）释放。
- 目标：core_service 新增 **`core.detect`** 命令（真实 ML 推理的 IPC 面），重新构建发布包，在安装后环境对 frozen 进程直接发 `core.detect` 完成真实推理——把「发布形态 detect 端到端可用」从不可达变为已验证。

## 设计决策（代理裁决，用户可撤销）

1. **协议扩展=minor bump（1.0→1.1）**：新增命令属向后兼容 widening（M2-FIX-LISTBOOKS 契约 rev 1.2 §5 先例）；既有三命令行为零变化；`core.ping` 的 version 字段自然携带新 minor。
2. **core.detect 请求/响应**：请求 payload=`{"page": "<base64 PNG/JPEG bytes>", "width": <int>, "height": <int>}`（字节计数与解码后尺寸由 provider 的 `_validate_request` fail-closed 校验，匿名 label/coordinate space 与 ports.detection 一致）；响应 result=`{"candidates": [{"provider_label","polygon","coordinate_space"}...], "elapsed_ms": <int>}`（provider 原始输出直通，不发明业务 ID）；错误走既有 error envelope（typed：PROVIDER_NOT_CONFIGURED/PROVIDER_FAILED/PROVIDER_DEPENDENCY_MISSING/E_INVALID_REQUEST）。
3. **实现路径**：core_service 的 `assemble_production_core` 产物中 detector 在 provider_runtime registry——命令 handler 经 provider runtime 解析 detect provider（与 pipeline detect step 同源），**不绕过装配**；mock_local_providers 模式下 core.detect 返回 mock provider 输出（装配语义一致）。
4. **发布形态验证口径（AC5 闭合）**：新 NSIS 安装后，探针直接 spawn core_service.exe 发 `core.detect`（合成漫画页）→ 断言 EXIT=0、candidates>0、provider 内部 pin 校验通过 → **M2-PROD-DETECT-2 AC5 的 NOT_RUN 子项转为 RUN**，其 Task 的 PARTIAL 判定由集成方在本 Task 集成时加注升级注记（原 Task 历史不改写）。

## Acceptance Criteria

- [x] AC1（协议与命令）：`PROTOCOL_MINOR` 1→1.1（常量+docstring Allowed commands 列表）；`core.detect` handler（base64 解码 fail-closed/字节计数校验/provider 解析/typed error envelope/elapsed 计时）；既有三命令与 Unknown command 行为零变化。
- [x] AC2（单元测试）：core_detect 命令 handler 测试（mock provider：正常输出直通/空页零候选/typed NOT_CONFIGURED/坏 base64/尺寸不符/超大载荷拒绝）+ 既有命令回归。
- [x] AC3（重建与 GATE）：新 onedir+NSIS 构建；GATE 25/25；M2-AC5 raw 还原（既有先例）。
- [x] AC4（frozen 端到端探针）：安装后环境 core_service.exe 发 core.detect 真实推理（manga 权重包内）PASS + core.detect 在无权重安装（-SkipWeights 产物或移权重）typed NOT_CONFIGURED PASS + doctr backend 切回语义探针。
- [x] AC5（回归与纪律）：pytest 三套件基数（401+1 既有失败+新增）；cargo/vitest 留痕；diff --check EXIT=0；禁改面除经集成追认的 GATE 协议字面量同步（`run_clean_start_e2e.py` CS-L1 1.0→1.1，裁决①必要后承，严格相等断言不变）外为空。
- [x] AC6（交付）：Task/Handoff/verification 证据回填。

## 实施记录（Owner=ZCode，2026-10-01）

- 实现 commit `9d29a0c9`（core_service/core_assembly + 30 个新测试）；构建/闭包修复 commit `983a50d5`（torchvision stable-ABI 扩展 + GATE 协议 1.1 同步）；证据与交付见 Handoff。
- **契约-事实偏差（裁决②的落实修正）**：`ports.detection` 的两个 provider（manga/doctr）的 `_validate_request` 只接受 **raw 像素缓冲**（rgb24/rgb32，"never an encoded file"），不接受 PNG/JPEG 编码字节。core.detect 的 wire 契约维持裁决②（base64 PNG/JPEG + 宽高声明），handler 内用 Pillow（transformers 依赖、已在 frozen 闭包）解码为 raw RGB 再构造 `DetectionRequest`；声明宽高 vs 解码尺寸不符 → `INVALID_REQUEST`；provider 的字节计数校验保持为第二道防线（typed `INVALID_INPUT` 直通）。`errors.py`/`ports.py` 零改动。
- **装配事实修正（侦察登记）**：detector 不在 provider registry（registry 的 detection slot 是远程 `openai-vision-detection`）；pipeline detect step 用的是装配段构造的 detector 实例（`build_production_handlers(detector=…)`)。core_detect 经 `CoreServices.detector`（本次最小新增字段，默认 `None`）拿到**同一实例**——与 pipeline 严格同源、不绕过装配；mock 装配模式自然一致（装配段把 `MockLocalDetectionProvider` 同时注册进 registry 并设为 detector）。
- **空候选语义**：core.detect 为观测/工具面，provider 零候选直通为空数组（与 pipeline step 的 `INVALID_INPUT` 不同——那是区域后续步骤需要写入目标的产品语义）。
- **构建期实证修复（AC4 探针暴露）**：首次 frozen 进程内 detect 失败 `operator torchvision::nms does not exist`（transformers `_LazyModule` 包装为 "Could not import module 'RTDetrImageProcessor'"）——torchvision 0.29 的 C++ 算子改为 stable-ABI 扩展（`_C_stable`/`image_stable`）且经 `_load_library` 动态加载，而 PyInstaller `hook-torchvision` 仍 pin 旧名 `torchvision._C`，扩展从未进闭包（M2-PROD-DETECT-2 的 warn 分类曾登记为软告警；当时 frozen detect 结构性不可达故未暴露）。修复=`core_sidecar.spec` `ML_BINARY_IMPORT_MODULES` pin 两个扩展 + `_assert_ml_closure` 增加 binaries 断言（未来改名即 build 失败）。
- **禁改面登记（唯一偏差）**：`packaging/m2ac5/run_clean_start_e2e.py` CS-L1 断言与请求 envelope 1.0→1.1（严格相等断言保持）——Task 允许范围 `packaging/m2ac5/**` 最小适配条款覆盖；裁决①「core.ping version 自然携带 1.1」的直接后承；不修则 GATE 必然 24/25（断言硬编码 minor=0 过期）。
- **cargo 遗留（未修，登记）**：`apps/desktop/src-tauri/src/main.rs:1228`（`real_library_sidecar_round_trip_and_eof`）断言 `minor==0` 过期 → 1 failed；`apps/**` 为硬禁改面，产品主路径零影响（请求发 minor 0 被向后兼容接受、`decode_response` 不校验 minor 数值、GATE 含 Rust 宿主真实运行 25/25 PASS）；修复=断言改 `1`，交集成方/后续 slice。

## 验证证据（M2-PROD-DETECT-3）

证据在 `verification/M2-PROD-DETECT-3/`（README 有完整索引）。下表为**集成修正轮**（构建输入绑定 `7314ad20`，全量重建复跑）；Owner 轮（绑定 `983a50d5`，NSIS `ea34041c…`）数字见该 commit 历史：

| 验证 | 结果 |
|---|---|
| onedir | 1,118,301,886 B / 5,557 文件 / PyInstaller 237s（closure 断言含 torchvision 两 stable-ABI 扩展） |
| NSIS | 460,795,026 B（439.45 MiB）/ sha256 `61c06973…` / tauri 254s |
| GATE（M2-AC5 runner） | 25/25 PASS（CS-E2 绑 `61c06973…`；CS-L1 protocol 1.1）；raw/gen/permissions 已还原，专项 diff 空 |
| frozen 探针 | 4/4 PASS：FD-1 frozen 进程内真实推理（2 候选，conf 0.9430/0.9274，首测 handler elapsed 4,645ms——含模型加载；与 DETECT-2 稳态 273ms/页非同一口径）+ FD-2 无权重 typed NOT_CONFIGURED + FD-2b 恢复 + FD-3 doctr typed NOT_CONFIGURED（**message=脱敏安全短句，R1 生效实证**）—— **M2-PROD-DETECT-2 AC5 的 NOT_RUN 子项（frozen 进程内 ML import/detect）转 RUN** |
| pytest 三套件 | providers 289+1（既有环境性失败保持；T3 在 main 已改 skipped，本分支基于其前——口径差如实登记，合并后以 main 复跑为准）/ m2_acceptance 35 / core 111（基数 77 + Owner 轮 30 + 集成轮 +4） |
| cargo / vitest | **44 passed + 1 ignored, 0 failed**（R4 修复后全绿）/ 未复跑（前端零触碰，引 Owner 轮 31 passed） |
| diff --check | `46f079e8..HEAD` EXIT=0 |
| 禁改面 | providers/ports/acceptance_bridge/tauri.conf.json/requirements.txt/experiments 零 diff；经追认例外=`run_clean_start_e2e.py` 协议 1.1 同步（Owner 轮）+ `main.rs:1228` 断言一行（集成轮 R4）；权重零 tracked |

## 集成修正记录（acting Codex，2026-10-01，DSH r1 条件全闭）

Review：DSH r1 `approved_with_conditions`（报告 `G:/CODEX/New Manga.task-envs/M2-PROD-DETECT-3/dsh-review-r1.md`，R1-R17）。处置（逐条 how+落点见各文件与 Handoff 集成节）：

- **R1[P2] §8 路径泄漏 → 脱敏（选 a，需重建）**：`core_service.py` dispatch 的 ProviderError 分支不再透传 `str(error)`——按 error_code 映射固定安全短句（NOT_CONFIGURED/FAILED/DEPENDENCY_MISSING/UNAVAILABLE，兜底同 FAILED），`INVALID_INPUT` 保留参数级消息（无路径，测试钉住），原文细节只走 stderr；FD-3 message_head 复跑实证脱敏生效。
- **R2[P2] §10 契约冲突 → 双动作**：契约 Revision history 例外登记（core.detect=verification/tooling surface，本地 stdio 无网络面，32 MiB 文件上限+像素上限，无写库，不构成大媒体先例）+ core.detect 本为 Tauri host 不注册面（Task/Handoff 已标注 verification-only）。
- **R3[P2] 允许-禁止自相矛盾 → 修订**：允许/禁止条款与 AC5 措辞改为「禁改面除经追认的 GATE 协议字面量同步外为空」——**追认 run_clean_start_e2e.py CS-L1 1.0→1.1**（裁决①必要后承，严格度不变）。
- **R4[P2] cargo 红灯 → 集成方一行修复**：`main.rs:1228` 断言 minor `0`→`1`（只此一行，`:1194` MockChannel 桩不动）；复跑 **44 passed + 1 ignored, 0 failed**。该一行登记为**集成方追认改动**。
- **R5-R11, R14（P3）**：e2e env 净化；elapsed_ms docstring=「detect（含首次模型加载）」；「byte-identically」改「命令语义零变化+envelope minor 0→1」；mock 装配测试改真装配（`mock_local_providers=True`）+ 措辞降「行为一致（实例不共享）」；补装配 wiring 同一实例断言；解码像素上限（32 MiB RGB24 等效=11,184,810 px，convert 前校验，注释改「base64-decoded file bytes; pixel-count cap separately enforced」）；格式白名单 `{PNG, JPEG}` fail-closed；category 最小映射（INVALID_INPUT→validation，其余 internal）——各配单测，core 107→111。
- **R12/R16（P3）**：`cold 21.4s`（无 artifact）从 Task/Handoff/README 删除；耗时口径改「首测 handler elapsed（含模型加载；与 DETECT-2 稳态 273ms/页非同一口径）」；NSIS MiB 修正口径（439.47 而非 439.44）+ PYZ 两统计面口径注。
- **R13（P3）**：frontmatter `base_commit`→`46f079e8`（分支实际 base；契约编写时基线 095e314d 已注明）；`delivery_head` 由集成轮证据 commit 锚定。
- **R15（P3）**：`src/ports/detection/ports.py:59` docstring 与两 provider raw-pixel 契约相悖——**doc-only 后续 slice 登记**（本 Task 禁改 ports 正确），见「遗留与边界」。
- **R17（P4）**：探针 models 树 rename/restore 加 try/finally 复原保护。
- **DETECT-2 注记（集成方清单#5）**：`verification/M2-PROD-DETECT-2/integration.md` 加「集成后注记」节（不改历史原文）——torchvision `_C_stable` stable-ABI 扩展经动态加载绕过 PyInstaller hook，DETECT-2 轮 frozen 闭包未含（其探针 L3 为闭包外等价推理故结论不受影响，「闭包含 ML 运行时」强表述以注记收窄）；AC5 NOT_RUN 子项由本 Task 转 RUN。
- **集成轮重建与复跑（绑定 `7314ad20`）**：全量重建（PyInstaller 237s + tauri 254s）→ 新 NSIS `61c06973…`；GATE 25/25；探针 4/4（FD-3 脱敏实证）；pytest 435+1（providers 289+1 / m2_acceptance 35 / core 111）；cargo 44+1ig, 0 failed；M2-AC5 raw/gen/permissions 还原专项 diff 空。

## 允许修改范围

- `src/bootstrap/core_service.py`（PROTOCOL_MINOR+docstring+core.detect handler）
- `src/bootstrap/core_assembly.py`（如 handler 需要 detect provider 解析 helper，仅最小新增）
- `tests/**`（core_detect 测试）
- `packaging/m2ac5/**`（如需最小适配——实际用于 GATE 协议字面量同步，见下「禁改面追认」）
- `doc/tasks/M2-PROD-DETECT-3.md`、`doc/handoffs/M2-PROD-DETECT-3-*.md`、`verification/M2-PROD-DETECT-3/**`
- M2-PROD-DETECT-2 AC5 注记由集成方在集成 commit 处理（Owner 不改旧 Task）

## 禁止范围

- `src/infrastructure/providers/**` 两 provider 行为、`src/ports/**` 契约、`requirements.txt`
- acceptance_bridge（其面是 M2-AC1 冻结，本 Task 不触碰）
- `apps/**`、tauri.conf.json（GATE 口径）；`run_clean_start_e2e.py` 的 GATE 协议字面量同步（CS-L1 1.0→1.1）经集成追认为**唯一例外**（与上节允许清单 `packaging/m2ac5/**` 的字面冲突就此消解）——除该追认项外禁改面为空
- 权重/模型入库、下载器实现

## 依赖、风险与阻塞

- 依赖：M2-PROD-DETECT-2 `done` @`9e44fb21`（包内运行时+权重就绪）。
- 风险：①frozen 进程内 transformers 懒加载首次触发（探针 L3 闭包外已证，进程内冷启动 6-17s 量级——探针设足够超时）；②base64 大载荷（一页 PNG 数 MB——handler 设合理上限如 32MB 拒绝）；③core.detect 暴露真实推理给 IPC 面（产品安全面——当前 sidecar 只接受本地宿主 spawn，stdio 协议无网络面，风险可接受并登记）。
- 阻塞：无。

## 遗留与边界

- core.detect 仅为验证与工具面；产品 UI 的 detect 走 pipeline（Tauri host 不新增命令注册——apps/** 禁改）。
- T2（weights SOP）/T3（registry 断言）由并行 Task 处理，非本 Task 范围。
- **doc-only 后续 slice（登记不释放，DSH r1 R15）**：修订 `src/ports/detection/ports.py` `DetectionRequest` docstring——现文「the image arrives as encoded bytes」与两 provider 的 raw-pixel 契约（`detection_manga.py:191`、`detection_doctr.py:170-172`）相悖；由独立 doc-only slice 修正（本 Task 禁改 ports）。

## 集成记录（2026-10-01，acting Codex）

- Review 轨迹：DSH r1 [approved_with_conditions](../../doc/reviews/M2-PROD-DETECT-3-7314ad20-dsh-r1.md)（0×P0/P1，5×P2+P3/P4；核心实现/frozen 证据/torchvision 修复定性全 PASS，sha256 见入库文件）→ **全部条件由集成方闭合**：集成修正 `7314ad20`（R1 §8 脱敏选 a+重建、R2 §10 契约例外双动作、R3 偏差追认、R4 main.rs:1228、R5-R17 择要全闭）→ 证据 `69a6e4e1`（重建绑定：NSIS 460,795,026B sha256 `61c06973…`、GATE 25/25、探针 4/4（FD-1 frozen 真实推理 2 候选 conf 0.943/0.927=DETECT-2 AC5 NOT_RUN 转 RUN；FD-3 脱敏短句实证）、cargo 44+1ig 0 failed、core 111）→ `0a470407` 记录。
- **两条偏差裁定（acting Codex 追认）**：①run_clean_start_e2e.py CS-L1 协议字面量 1.0→1.1=裁决①必要后承（严格度不变，25 场景判定标准零变化）；②core.detect=verification-only 面（Tauri host 不注册，契约 Revision history 例外登记）。
- **torchvision `_C_stable` stable-ABI 缺口（本 Task 新发现并修复）**：动态加载绕过 PyInstaller hook，DETECT-2 轮 frozen 闭包未含——其 integration.md 已加集成后注记（L3 闭包外结论不受影响，强表述收窄；AC5 NOT_RUN 转 RUN）。
- merge=`8fe5199c`；集成后 main：pytest 三套件 **437 passed + 1 skipped 0 failed**（T3 后新基线：providers 291+1skipped/35/core 111）、cargo **44 passed 0 failed 1 ignored**。git 层 diff --check EXIT=0、禁改面空（providers/ports/bridge/tauri.conf.json/requirements/experiments）、权重零 tracked。
- 遗留（登记不释放）：ports.detection docstring 修订（R15，doc-only slice）；真实干净 Windows 覆盖维持 M2 Release Gate 冻结口径。

Owner branch/worktree 保留于 `0a470407`。
