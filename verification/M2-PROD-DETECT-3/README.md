# M2-PROD-DETECT-3 验证证据（frozen 命令面 core.detect 端到端）

Task：`doc/tasks/M2-PROD-DETECT-3.md`（Owner=ZCode，Reviewer=DSH 非作者）。
构建输入：`src/**`+`packaging/m2ac5/**` @ commit `983a50d5`（branch `agent/zcode/M2-PROD-DETECT-3`，base `46f079e8`）；构建时工作树干净、未再触碰 src/spec（可静态验证）。

## 证据索引

| 文件 | 内容 |
|---|---|
| `frozen-detect-probe.py` | AC4 探针（4 场景 / 3 语义：FD-1 frozen 进程内真实推理、FD-2 无权重 typed NOT_CONFIGURED、FD-2b 还原恢复、FD-3 doctr 切回 typed NOT_CONFIGURED）；全部推理在 frozen core_service.exe 进程内执行，无闭包外 driver |
| `frozen-detect-probe-results.json` | 探针结果（verdict=PASS，4/4） |
| `raw/build-sidecar-console.log` | PyInstaller 全量重建 console（`closure assertion: … transformers, transformers.models.rt_detr, transformers.models.rt_detr_v2 (8572 pure modules) + extensions torchvision/_C_stable.pyd, torchvision/image_stable.pyd`；`build_sidecar: OK … HEAD=983a50d5`） |
| `raw/tauri-build-console.log` | tauri NSIS 重打包 console |
| `raw/cleanstart-runner-stdout.log` | GATE（M2-AC5 runner）25/25 PASS，CS-E2 绑 NSIS sha256 `ea34041c…`，CS-L1 protocol 1.1 |
| `raw/fd1-frozen-session.log` 等 `fd*.log` | 探针四个 frozen 会话的原始 stderr（FD-1 含 transformers 加载条；FD-2 含装配 `probed candidates` 警告；FD-2b 警告消失） |
| `raw/pyz-core-service-listing.txt` | frozen core_service.exe PYZ 全清单（8,571 模块；transformers 2,320 条、rt_detr/rt_detr_v2 全家、PIL.Image* 22 条） |

## 关键数字（绑定 983a50d5）

| 项 | 值 |
|---|---|
| onedir | 1,118,300,869 B / 5,557 文件 / PyInstaller 238s（上轮 1,116,381,309 B / 5,550：+torchvision 两个 stable-ABI 扩展等） |
| NSIS | 460,814,288 B（439.44 MiB）/ sha256 `ea34041cf8fe3a5074c40cb064b92b6fe54e5dcc2c0018a742dd8bf83e340729` / tauri 251s |
| GATE | 25/25 PASS（`GATE: PASS`；CS-L1 protocol 1.1） |
| 探针 | 4/4 PASS：FD-1 真实推理 2 候选（manga-1/manga-2，conf 0.943/0.927，page-global，handler elapsed 4,687ms 进程内含模型加载；首次冷启动实测 21.4s）；FD-2 typed PROVIDER_NOT_CONFIGURED + 装配警告 + ping ready；FD-2b 还原后警告消失；FD-3 doctr typed NOT_CONFIGURED |
| pytest | providers **289 passed + 1 failed**（既有环境性 `test_registry_readiness::test_no_model_runtime_is_installed_in_this_environment`，T3 范围）/ m2_acceptance **35 passed** / core **107 passed**（基数 77 + 本 Task 新增 30）——合计 431 passed + 1 failed |
| cargo test | **43 passed + 1 failed + 1 ignored**——1 failed=`tests::real_library_sidecar_round_trip_and_eof`（apps/desktop/src-tauri/src/main.rs:1228 断言 `protocol_version.minor==0`，协议 1.0→1.1 后过期；apps/** 为本 Task 禁改面，产品主路径零影响——请求仍发 minor 0（服务端向后兼容接受）、`decode_response` 不校验 minor 数值、GATE（含 Rust 宿主真实运行）25/25 PASS。修复=该行断言改 `1`，交集成方/后续 slice） |
| vitest | **31 passed（5 文件）**（零前端触碰，实测同上轮） |
| 权重治理 | `git ls-files` 零权重（safetensors/.pt/bin 均 0）；Copy-MangaWeights sha256 校验 + FD-1 provider 内三文件 pin 校验传递 NSIS 安装态（成功推理即证明） |

## 已知限制与登记

- 协议 `new-manga.core` 1.0→1.1（minor bump，向后兼容 widening）：既有三命令行为零变化；`core.ping` version 携带 1.1。
- `run_clean_start_e2e.py` 的 CS-L1 断言与请求 envelope 同步 1.0→1.1（严格相等断言保持）——本 Task 唯一禁改面偏差，理由与 diff 见 Handoff「禁改面登记」。
- cargo `real_library_sidecar_round_trip_and_eof` 的 minor 断言过期未修（apps/** 禁改）——见上表，交集成方处置。
- core.detect 为验证与工具面：Tauri host 不注册该命令（apps/** 禁改），产品 UI 的 detect 仍走 pipeline。
