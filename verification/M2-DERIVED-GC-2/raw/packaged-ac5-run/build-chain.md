# 第三轮 packaged 验收的构建链绑定（Codex r3 F-08）

- 返修代码 commit = 70ab9da0ca72535e6a399adbfd82b5c0282f7f73
- sidecar 重建命令 = powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1 -Force
- build_sidecar 输出（后台运行日志原行）：build_sidecar: OK -> apps/desktop/src-tauri/target/core-sidecar/core-sidecar (HEAD=70ab9da0ca72535e6a399adbfd82b5c0282f7f73, pyinstaller=6.22.3)
- NSIS 构建命令 = npx --yes @tauri-apps/cli@2 build --bundles nsis（cwd apps/desktop/src-tauri，紧随 sidecar 重建）
- NSIS 产物 = apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe（553.80 MiB）
- NSIS 产物 SHA256 = 9b7ff1b2a862fb680f4846f38beadf80c3e112e60de11dfd989bd73a641de97d
- 验收命令 = python packaging/m2ac5/run_clean_start_e2e.py --installer <上述 NSIS 路径>（完整输出 third-round-full-stdout.log，头部含 HEAD/指纹/EXIT）
- 闭环：sidecar(HEAD=70ab9da0) → NSIS 打包同一 sidecar 目录 → runner --installer 指向该 NSIS → 安装态场景执行的就是 70ab9da0 的 core_service/host_bridge/catalog_loader。
