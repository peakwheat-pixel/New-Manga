# M2-PROD-DETECT-3 验证证据（frozen 命令面 core.detect 端到端）

Task：`doc/tasks/M2-PROD-DETECT-3.md`（Owner=ZCode，Reviewer=DSH 非作者，Integrator=acting Codex）。
当前证据 = **集成修正轮**（DSH r1 `approved_with_conditions` 条件全闭 + 全量重建复跑），构建输入绑定集成 commit `7314ad20`（branch `agent/zcode/M2-PROD-DETECT-3`，base `46f079e8`）；构建时工作树干净、未再触碰 src/spec（可静态验证）。
Owner 交付轮证据（构建输入 `983a50d5`，NSIS `ea34041c…`）见 commit `46d20842..9bcfd969` 的本目录历史版本；其叙述性数字的两处口径更正（R12/R16）随本 README 生效。

## 证据索引

| 文件 | 内容 |
|---|---|
| `frozen-detect-probe.py` | AC4 探针（4 场景 / 3 语义：FD-1 frozen 进程内真实推理、FD-2 无权重 typed NOT_CONFIGURED、FD-2b 还原恢复、FD-3 doctr 切回 typed NOT_CONFIGURED）；全部推理在 frozen core_service.exe 进程内执行，无闭包外 driver；R17：models 树 rename/restore 加 try/finally 复原保护 |
| `frozen-detect-probe-results.json` | 探针结果（verdict=PASS，4/4，本轮复跑绑定新 NSIS 安装态；FD-3 message_head=脱敏安全短句——R1 生效实证） |
| `raw/build-sidecar-console.log` | PyInstaller 全量重建 console（`closure assertion: … transformers, transformers.models.rt_detr, transformers.models.rt_detr_v2 (8572 pure modules) + extensions torchvision/_C_stable.pyd, torchvision/image_stable.pyd`；`build_sidecar: OK … HEAD=7314ad20…`） |
| `raw/tauri-build-console.log` | tauri NSIS 重打包 console |
| `raw/cleanstart-runner-stdout.log` | GATE（M2-AC5 runner）25/25 PASS，CS-E2 绑 NSIS sha256 `61c06973…`，CS-L1 protocol 1.1 |
| `raw/fd1-frozen-session.log` 等 `fd*.log` | 探针四个 frozen 会话的原始 stderr（FD-1 含 transformers 加载条；FD-2 含装配 `probed candidates` 警告 + core.detect provider error 的 stderr 细节行；FD-2b 警告消失） |
| `raw/pyz-core-service-listing.txt` | frozen core_service.exe PYZ 纯模块清单（PYZ TOC 8,571 模块；transformers 2,320 条、rt_detr 家族 11 条、PIL.Image* 22 条） |

## 关键数字（绑定 7314ad20）

| 项 | 值 |
|---|---|
| onedir | 1,118,301,886 B / 5,557 文件 / PyInstaller 237s（Owner 轮 1,118,300,869 B：本轮增量=core_service.py 集成修正） |
| NSIS | 460,795,026 B（439.45 MiB；MiB 值=字节/1,048,576 四舍五入，与 tauri console 一致）/ sha256 `61c0697360ffac1adf7ae329395bab7f947a7390078f80e27726880cac62bae7` / tauri 254s |
| GATE | 25/25 PASS（`GATE: PASS`；CS-L1 protocol 1.1）；M2-AC5 raw 6 文件 + gen/schemas（2）+ permissions（12）已 `git checkout --` 还原，专项 diff 空 |
| 探针 | 4/4 PASS：FD-1 真实推理 2 候选（manga-1/manga-2，conf 0.9430/0.9274，page-global，handler elapsed 4,645ms——detect 计时（含首次模型加载；与 DETECT-2 稳态 273ms/页非同一口径），会话 wall 5,350ms）；FD-2 typed PROVIDER_NOT_CONFIGURED + 装配警告 + ping ready；FD-2b 还原后警告消失；FD-3 doctr typed NOT_CONFIGURED（message 为脱敏安全短句，权重路径不上线——R1） |
| pytest | providers **289 passed + 1 failed**（`test_registry_readiness::test_no_model_runtime_is_installed_in_this_environment`——本分支基于 T3 合入之前，该用例在 main 已改 skipped；口径差如实登记，合并后以 main 复跑为准）/ m2_acceptance **35 passed** / core **111 passed**（基数 77 + Owner 轮 30 + 集成轮 +4：R1 脱敏/R9 wiring/R10 像素上限/R11 格式白名单）——合计 435 passed + 1 failed |
| cargo test | **44 passed + 0 failed + 1 ignored**（R4：main.rs:1228 断言 minor 0→1 集成修正后全绿；:1194 MockChannel 自洽桩保持 minor 0） |
| vitest | 未复跑（前端零触碰，引 Owner 轮 31 passed / 5 文件） |
| 权重治理 | `git ls-files` 零权重（safetensors/.pt/bin 均 0）；Copy-MangaWeights sha256 校验 + FD-1 provider 内三文件 pin 校验传递 NSIS 安装态（成功推理即证明） |

## 口径注（R16）

- NSIS「MiB」值=字节数 / 1,048,576 四舍五入到两位小数（Owner 轮 README 的「439.44 MiB」实为 439.47 的截断笔误；本轮 460,795,026 B = 439.45 MiB）。
- PYZ「模块数」有两种统计面：构建期 closure assertion 的 `analysis.pure`=8,572（PyInstaller Analysis 纯 Python 模块分析面，含 PYZ 未列项）；本清单为 frozen exe 内嵌 PYZ TOC 实际条目=8,571。两者口径不同、均如实引用。

## 已知限制与登记

- 协议 `new-manga.core` 1.0→1.1（minor bump，向后兼容 widening）：既有三命令命令语义零变化（payload/result/错误码；envelope protocol minor 随 bump 0→1）；`core.ping` version 携带 1.1。
- `run_clean_start_e2e.py` 的 CS-L1 断言与请求 envelope 同步 1.0→1.1（严格相等断言保持）——经集成追认为唯一禁改面例外（裁决①必要后承，DSH r1 R3）；`apps/desktop/src-tauri/src/main.rs:1228` 断言同步一行亦为集成追认改动（R4）。
- core.detect 为验证与工具面：Tauri host 不注册该命令（apps/** 禁改），产品 UI 的 detect 仍走 pipeline；§10 大媒体禁令的例外登记见 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` Revision history（R2）。
- provider 错误消息已脱敏（R1）：线上仅 error_code + 固定安全短句，细节只走 stderr；`ports.py` docstring 修订（R15）登记为 doc-only 后续 slice（本 Task 禁改 ports 正确）。
- 真干净 Windows 覆盖仍为 M2 Release Gate 口径冻结 NOT_RUN（沿用既有边界）。
