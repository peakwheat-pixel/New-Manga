---
task_id: M2-PROD-DETECT-3
author: ZCode
recipient: Codex（integrator）；reviewer=DeepSeek Harness（非作者）
base_commit: 46f079e8
delivery_head: 9bcfd969（tip；构建被测输入=983a50d5，其后仅 doc/hygiene）
status: in_review
---

# Handoff：M2-PROD-DETECT-3（core.detect 命令面 + frozen 进程内真实 detect 端到端）

## 交付结果

M2-PROD-DETECT-2 AC5 的 PARTIAL 判定源头——「frozen 命令面无 detect RPC，frozen 进程内真实 detect 结构性不可达」——本 Task 闭合：协议 `new-manga.core` **1.0→1.1**（minor bump），core_service 新增 **`core.detect`** 命令，重建发布包后 **NSIS 安装态 frozen 进程内真实推理 PASS（2 候选）**。M2-PROD-DETECT-2 AC5 的 NOT_RUN 子项（frozen 进程内 ML import/detect）**转 RUN**；原 Task 历史不改写，升级注记由集成方在集成 commit 处理。

**实现范围**（全部在 Task 允许清单内，`errors.py`/`ports.py`/providers/** 零改动）：

| 文件 | 变化 |
|---|---|
| `src/bootstrap/core_service.py` | `PROTOCOL_MINOR` 0→1；docstring Allowed commands + 信封示例 1.1；新常量 `E_INVALID_REQUEST`、`MAX_DETECT_PAGE_BYTES`（32 MiB）；`handle_detect`（payload 校验→base64 解码→Pillow 解码为 raw RGB→宽高一致性校验→`CoreServices.detector` 解析→`DetectionRequest`→provider 直通序列化）；dispatch 新增 `core.detect` 分支（typed 错误映射）；既有三分支零改动 |
| `src/bootstrap/core_assembly.py` | `CoreServices` 新增带默认值字段 `detector: object = None`，装配段传入 pipeline detect step 用的**同一实例**（向后兼容，唯一构造点不受影响） |
| `tests/core/test_core_detect.py` | 新增 30 用例（矩阵见 AC2） |
| `tests/core/test_core_service.py` | 两处 ping `protocol_version` 断言 1.0→1.1；subprocess e2e 追加 core.detect 场景（生产装配无权重 → typed PROVIDER_NOT_CONFIGURED + INVALID_REQUEST + 存活回归） |
| `packaging/m2ac5/core_sidecar.spec` | `ML_BINARY_IMPORT_MODULES`（`torchvision._C_stable`/`image_stable`）pin 进 core_service Analysis；`_assert_ml_closure` 增加 binaries 断言 |
| `packaging/m2ac5/run_clean_start_e2e.py` | CS-L1 请求 envelope 与断言 1.0→1.1（**唯一禁改面偏差**，见下） |

## 协议 1.0→1.1 变化表

| 面 | 1.0（前） | 1.1（后） | 兼容性 |
|---|---|---|---|
| 命令面 | core.ping / ListBooks / core.shutdown | + `core.detect`（`{"page": base64 PNG/JPEG, "width": int, "height": int}` → `{"candidates":[{provider_label,polygon,reading_order,confidence,coordinate_space}], "elapsed_ms": int}`） | 向后兼容 widening（M2-FIX-LISTBOOKS 契约 rev 1.2 §5 先例） |
| core.ping version | `{"major":1,"minor":0}` | `{"major":1,"minor":1}` | 客户端按 minor 读取，无破坏 |
| 既有三命令 | — | 字节级行为零变化（测试钉住） | 无 |
| minor-0 请求 | 接受 | 仍接受（版本校验只看 major） | 旧客户端/Rust 宿主（发 minor 0）不受影响 |
| 错误信封 | INVALID_JSON / INVALID_REQUEST / PROTOCOL_VERSION_UNSUPPORTED / UNKNOWN_COMMAND / LIST_BOOKS_FAILED / UNKNOWN | + core.detect 的 typed code：`INVALID_REQUEST`（请求契约）、provider `error_code` 直通（`PROVIDER_NOT_CONFIGURED` / `PROVIDER_DEPENDENCY_MISSING` / `PROVIDER_FAILED` / `INVALID_INPUT` / …，retryable 沿用 ProviderError 自身裁定） | 既有 code 零变化 |
| 消费方影响 | — | Tauri host 不注册 core.detect（apps/** 禁改，裁决⑤）；产品 UI detect 仍走 pipeline | 无 |

## 四条裁决的落地与偏差登记

1. **裁决①（minor bump）**：落地；GATE CS-L1 断言硬编码 `minor==0` 过期是其后承——`run_clean_start_e2e.py` 两处字面量同步 1.1（严格相等断言保持，非放宽）。依据：Task 允许范围 `packaging/m2ac5/**`「如需最小适配」条款；不修则 GATE 必然 24/25。
2. **裁决②（payload/响应/错误）**：wire 契约按裁决落地。**事实修正**：provider 的 `_validate_request` 只收 raw 像素（"never an encoded file"），故 handler 承担 PNG/JPEG→raw RGB 解码（Pillow，transformers 依赖已在闭包）；「解码后尺寸由 provider 校验」落实为 handler 校验声明宽高 vs 解码尺寸（`INVALID_REQUEST`），provider 字节计数校验保持第二道防线（`INVALID_INPUT` 直通）。candidate 序列化按 `RegionCandidate` 实际字段（polygon/reading_order/confidence/provider_label）+ result 级 coordinate_space；空候选直通空数组（观测面语义，区别于 pipeline step 的 INVALID_INPUT）。
3. **裁决③（同源解析）**：侦察登记「detector 在 registry」与代码不符——registry 的 detection slot 是远程 vision；pipeline detect step 用装配段实例。落地为 `CoreServices.detector` 暴露同一实例（不绕过装配）；mock 装配下 `MockLocalDetectionProvider` 同时注册 registry 并设为 detector，core.detect 自然一致（有测试钉住）。
4. **裁决④（发布形态口径）**：探针三语义全 PASS（+还原恢复共 4 场景），FD-1 的推理**在 frozen 进程内**执行（对比 DETECT-2 探针的闭包外 L3）；-SkipWeights 产物以「安装后移权重」等价替代（裁决④括号内允许）。

## 验证证据（构建输入=983a50d5，全量重跑）

| 验证 | 结果 | 证据 |
|---|---|---|
| PyInstaller（-Force 全量） | OK，HEAD=983a50d5；closure assertion 三 transformers 名 + `torchvision/_C_stable.pyd, torchvision/image_stable.pyd` | raw/build-sidecar-console.log |
| onedir | 1,118,300,869 B / 5,557 文件 / 238s | 同上 |
| NSIS | 460,814,288 B（439.44 MiB）/ sha256 `ea34041cf8fe3a5074c40cb064b92b6fe54e5dcc2c0018a742dd8bf83e340729` / tauri 251s | raw/tauri-build-console.log |
| GATE | **25/25 PASS**（CS-E2 绑 `ea34041c…`；CS-L1 protocol 1.1） | raw/cleanstart-runner-stdout.log |
| frozen 探针 | **4/4 PASS**：FD-1 frozen 进程内真实推理（900x1300 合成页，2 候选 manga-1/manga-2，conf 0.943/0.927，page-global；cold 21.4s / 热 4.7s，均含模型加载）+ FD-2 无权重 typed PROVIDER_NOT_CONFIGURED（retryable=false + 装配 stderr `probed candidates` 警告 + ping ready）+ FD-2b 还原恢复（警告消失）+ FD-3 doctr typed PROVIDER_NOT_CONFIGURED（包内无 doctr 权重，反证在案） | frozen-detect-probe-results.json + raw/fd*.log |
| PYZ 清单 | 8,571 模块；transformers 2,320 / rt_detr+rt_detr_v2 全家 / PIL.Image* 22 | raw/pyz-core-service-listing.txt |
| pytest 三套件 | providers **289+1**（既有环境性 `test_registry_readiness::test_no_model_runtime_is_installed_in_this_environment`，T3 范围）/ m2_acceptance **35** / core **107**（基数 77 + 新增 30） | 本表 |
| cargo / vitest | **43 passed + 1 failed + 1 ignored**（失败=main.rs:1228 Rust 测试断言过期，见「已知限制」）/ **31 passed** | 本表 |
| diff --check | `46f079e8..HEAD` EXIT=0 | 本表 |
| M2-AC5 raw 还原 | runner 重写 6 文件 + gen/schemas（2）+ permissions（12）`git checkout --` 还原，porcelain 干净 | git status |
| 权重治理 | `git ls-files` 零权重（safetensors/.pt/bin=0）；Copy-MangaWeights sha256 校验 + FD-1 provider 内 pin 校验传递 NSIS 安装态 | 本表 + build console |

## 构建期实证修复：torchvision stable-ABI 缺口（AC4 探针的价值证明）

首次 FD-1 失败：`RuntimeError: operator torchvision::nms does not exist`（transformers `_LazyModule` 包装为 "Could not import module 'RTDetrImageProcessor'"）。根因链：`RTDetrImageProcessor` → `torchvision.transforms.v2.functional` → torchvision 完整初始化 → `_load_library("_C_stable")` 找不到扩展。torchvision 0.29 的 C++ 算子改为 stable-ABI 命名（`_C_stable`/`image_stable`）且经 `torchvision.extension._load_library` **动态加载**，PyInstaller `hook-torchvision` 仍 pin 旧名 `torchvision._C`——扩展从未进闭包。这正是 DETECT-2 AC5 PARTIAL 的结构性盲区（warn 分类曾登记 torchvision._C 为软告警，但当时 frozen detect 不可达、无从暴露）；core.detect 第一次真正执行 frozen 内 ML 加载即暴露。修复：spec pin 两个扩展 + binaries 断言（未来 torchvision 再改名 → build 失败，不静默降级）。

## 已知限制与遗留

1. **cargo `real_library_sidecar_round_trip_and_eof` 1 failed（未修）**：`apps/desktop/src-tauri/src/main.rs:1228` 断言 `ping.protocol_version.minor==0`，协议 1.1 后过期。`apps/**` 为本 Task 硬禁改面，产品主路径零影响（Rust 请求仍发 minor 0、`decode_response` 不校验 minor 数值、GATE 含 Rust 宿主真实运行 25/25 PASS）。修复=该行断言 `0`→`1`（同文件 :1194 为 MockChannel 自洽桩，可选同步），交集成方或后续 slice。
2. **core.detect 为验证与工具面**：Tauri host 不注册（apps/** 禁改，裁决⑤）；产品 UI 的 detect 仍走 pipeline。IPC 面暴露真实推理的风险已评估（stdio 本地 spawn、无网络面）。
3. **协议 bump 的消费方同步点**：Rust 宿主测试断言（上条）与 GATE（本 Task 已同步）；无其他消费方。
4. mock 模式 core.detect 只在 `mock_local_providers=True` 装配下可用（仅 acceptance_bridge 设置）——core_service 生产装配恒为 manga/doctr 后端。
5. 真干净 Windows 覆盖仍为 M2 Release Gate 口径冻结 NOT_RUN（沿用既有边界）。
6. 上轮 NSIS `07d7daa1…` → 本轮 `ea34041c…`（+632,976 B，torchvision 扩展等闭包增量）。

## 提交列表（branch `agent/zcode/M2-PROD-DETECT-3`，未 push；**tip=`9bcfd969`**）

- `9d29a0c9` implement：core_service/core_assembly + 30 新测试 + 既有测试协议断言同步
- `983a50d5` fix：spec torchvision stable-ABI pin + binaries 断言；GATE CS-L1 协议 1.1 同步（**构建被测输入 commit**）
- `46d20842` evidence：verification/M2-PROD-DETECT-3/**（probe + raw + README）+ Task 回填 + 本 Handoff
- `9bcfd969` hygiene（raw 日志 LF 规范化 + EOF 空行剥离；探针脚本写 LF；内容不变；`git diff --check 46f079e8..HEAD` EXIT=0 恢复）+ task record（frontmatter `delivery_head`→tip、`status`→`in_review`，doc-only，随本 tip 在库）

## 接收方式

- 复现构建：`powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1 -Force`（观察 closure assertion 五名字）→ `cd apps/desktop/src-tauri && npx --yes @tauri-apps/cli@2 build` → `python packaging/m2ac5/run_clean_start_e2e.py` → `python verification/M2-PROD-DETECT-3/frozen-detect-probe.py --install-dir %TEMP%/m2ac5-cleanstart/install`。
- pytest：主 venv `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`，`PYTHONPATH=src`，`pytest tests/providers tests/m2_acceptance tests/core`。
- 重点核查建议：①FD-1 的推理进程归属（`frozen-detect-probe.py` 无闭包外 driver；`raw/fd1-frozen-session.log`）；②spec binaries 断言（故意删名应 build 失败）；③`run_clean_start_e2e.py` 两处 1.1 字面量（唯一禁改面偏差的 diff 审定）；④main.rs:1228 遗留处置（集成修 or 后续 slice）。

## 下一任务建议

- Task ID / 标题：无新 Task——等待 DSH 非作者 Review（锚：本 Handoff + 证据 commit）；集成方 merge 前处置两条登记（main.rs:1228 断言同步一行 + M2-PROD-DETECT-2 AC5 升级注记）。
- 推荐 Agent / Reviewer：DSH（review）；集成方（merge + STATUS + DETECT-2 注记）。
- 可直接转发的指令：`「你是 DSH（非作者 Reviewer）。复审 agent/zcode/M2-PROD-DETECT-3（base 46f079e8）：对照 doc/handoffs/M2-PROD-DETECT-3-983a50d5.md 核验 AC1-AC6——重点 FD-1 frozen 推理进程归属、spec binaries 断言有效性、run_clean_start_e2e.py 最小适配 diff 审定、main.rs:1228 遗留登记准确性；pytest/cargo 计数与本表核对后出 review 报告。」`
- Recovery point：worktree `G:/CODEX/New Manga.worktrees/M2-PROD-DETECT-3-zcode`，branch `agent/zcode/M2-PROD-DETECT-3`，base `46f079e8`，构建输入 `983a50d5`。
