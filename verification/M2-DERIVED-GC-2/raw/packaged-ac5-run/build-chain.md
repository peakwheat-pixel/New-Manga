# 第三轮 packaged 验收的构建链绑定（Codex r3 F-08）

- 返修代码 commit = 70ab9da0ca72535e6a399adbfd82b5c0282f7f73
- sidecar 重建命令 = powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1 -Force
- build_sidecar 输出（后台运行日志原行）：build_sidecar: OK -> apps/desktop/src-tauri/target/core-sidecar/core-sidecar (HEAD=70ab9da0ca72535e6a399adbfd82b5c0282f7f73, pyinstaller=6.22.3)
- NSIS 构建命令 = npx --yes @tauri-apps/cli@2 build --bundles nsis（cwd apps/desktop/src-tauri，紧随 sidecar 重建）
- NSIS 产物 = apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe（553.80 MiB）
- NSIS 产物 SHA256 = 9b7ff1b2a862fb680f4846f38beadf80c3e112e60de11dfd989bd73a641de97d
- 验收命令 = python packaging/m2ac5/run_clean_start_e2e.py --installer <上述 NSIS 路径>（完整输出 third-round-full-stdout.log，头部含 HEAD/指纹/EXIT）
- 闭环：sidecar(HEAD=70ab9da0) → NSIS 打包同一 sidecar 目录 → runner --installer 指向该 NSIS → 安装态场景执行的就是 70ab9da0 的 core_service/host_bridge/catalog_loader。


---

# 第四轮（FINAL）构建链：绑定 e3ad330f（Codex r4 F-08 闭合）

本轮全部证据来自单一日志 fourth-round-build-and-run.log（step1..step5 带 EXIT 头，
含完整 build_sidecar / tauri build / 定向 pytest / runner stdout——不再有手写汇总层）：

- 返修代码 commit = e3ad330f4831c868074a4941b14d90711b01c2d1（r4 F-01 主键布局校验）
- 日志头 HEAD=e3ad330f… + worktree 指纹（仅 tauri CRLF 再生成）
- [step1] build_sidecar.ps1 -Force → 原文行：
  build_sidecar: OK -> ... (HEAD=e3ad330f4831c868074a4941b14d90711b01c2d1, pyinstaller=6.22.3)（step1 EXIT=0）
- [step2] npx @tauri-apps/cli@2 build --bundles nsis → NSIS 553.80 MiB（step2 EXIT=0）
- [step3] installer SHA256（日志内联输出）
- [step4] 定向回归 tests/m2_resource_channel + tests/core/test_derived_gc.py（step4 EXIT=0）
- [step5] m2ac5 clean-start runner：**25 项场景 PASS，唯一 FAIL=CS-L1（runner 协议
  minor 3 陈旧快照，既有漂移，按 F-07 口径保持 FAIL 记录至独立 debt Task）**（step5 EXIT=1）
- 历史保护：runner 写入 M2-AC5/raw 的新产物搬至 fourth-run-artifacts/，tracked 历史字节 restore

第三轮（70ab9da0）记录保留在下方与 third-round-full-stdout.log——本轮（e3ad330f）为
最终绑定轮。
