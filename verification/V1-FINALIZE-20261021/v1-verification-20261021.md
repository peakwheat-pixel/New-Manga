# v1 收口验证（2026-10-21，HEAD `239b165c2`）

**目的**：在 P20 Windows 发布（用户 2026-10-20 已授权 `closed_with_limitations`）基础上，从当前 HEAD 重新执行构建与测试、修复发布后发现的 ACL 缺口，并重建安装包；为「第一版软件完成」提供可复算证据。
**边界**：本轮不发布、不签名、不 push、不改写历史；只修产品 ACL 缺口与测试期望，并重跑验证。

## 1. 环境

- Windows 11 Pro（26200）；PowerShell 7.6.6；Python 3.14.6（`C:\Python314\python.exe`）；
  Cargo 1.98.1 / rustc 1.98.1；Node v24.15.0；npm 12.0.1；tauri-cli 2.12.3；PyInstaller 6.22.3。
- 构建 venv：`G:\CODEX\New Manga.task-envs\m2ac5-build`（含 ML 运行时与 packaging 依赖）。

## 2. 缺陷：recycle-bin 命令生产 ACL 缺失（已修复）

- 现象：`cargo test` 的 `tests::app_acl_manifest_is_generated_and_enforced` 失败：
  `app ACL must define allow-library-list-recycle-bin-books (from library_list_recycle_bin_books)`；
  另有 7 个命令面计数断言仍按 53 个 production 命令。
- 根因：`library_list_recycle_bin_books` 已加入 `PRODUCTION_COMMANDS`、`generate_handler!` 与前端 client，
  但 `build.rs` 的 app manifest 与 `capabilities/m2rc1-commands.json` 未同步；`gen/schemas` 为陈旧生成物。
  生产 WebView 调用该命令会被 ACL 拒绝（recycle-bin 读取面不可用）。
- 修复（commit `239b165c2`）：
  1. `build.rs` app manifest 增加该命令；`capabilities` 增加 `allow-library-list-recycle-bin-books`；重生成 `gen/schemas`；
  2. 新增 `RECYCLE_BIN_PRODUCTION_ONLY_COMMANDS`，保持 probe=7 / AC1=6 冻结面；
  3. 单测 53→54，并补派生计数中的新组扣减。
- 修复前完整 source 运行：`140 passed / 22 failed / 1 ignored`（exit 101，含 13 个 packaged 环境门卫与 7 个 ACL/计数漂移）。
- 修复后 source：`150 passed / 0 failed / 1 ignored / 12 filtered`（exit 0）；
  修复后 packaged：`12 passed / 0 failed / 151 filtered`（exit 0）。

## 3. 构建与测试结果（本轮实测）

| 检查 | 命令/方式 | 结果 | 原始日志 |
|---|---|---|---|
| Sidecar 构建 | `packaging/m2ac5/build_sidecar.ps1` | exit 0；bundle `target/core-sidecar/core-sidecar`；权重 SHA 校验通过 | `sidecar-build.log` |
| Rust source 套件 | `M2RC1_PYTHON=C:\Python314\python.exe`；`cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop -- --skip packaged_sidecar_tests --test-threads=1` | **150 passed / 0 failed / 1 ignored / 12 filtered，exit 0**；唯一 ignored 为 `perf_chunk_request_digest_cost` | `cargo-source-fixed.log` |
| Rust packaged 套件 | `M2RC1_PACKAGED=1`、`M2RC1_PYTHON`/`M2RC1_SRC_ROOT` unset；`cargo test ... packaged_sidecar_tests -- --test-threads=1` | **12 passed / 0 failed，exit 0**（真实 frozen Core） | `cargo-packaged-fixed.log` |
| 前端测试 | `npm test --prefix apps/desktop/frontend -- --run` | **32 files / 327 tests passed**，exit 0 | `vitest.log` |
| 前端构建 | `npm run build --prefix apps/desktop/frontend` | exit 0；`dist` 生成 | `frontend-build.log` |
| Python M2 资源通道 | `python -m pytest tests/m2_resource_channel -q` | **106 passed**，exit 0 | `pytest-m2.log` |
| 安装包重建 | `cargo tauri build`（tauri-cli 2.12.3） | exit 0；NSIS 单包生成 | `tauri-build-installer.log` |

## 4. 产物（gitignored，仅本机）

| 产物 | 大小 | SHA-256 |
|---|---:|---|
| `apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe` | 579,979,256 B | `b0ad46f5df01f4ffc287e9aeaef9ecaf5b163778d9ac632db92c6ce66ac38c7b` |
| `apps/desktop/src-tauri/target/release/m2rc1-desktop.exe` | 11,882,496 B | `7063ac321b951091aa1a17daa9fdf272c94e473f8aefa34dc816a0a395fb85f9` |
| frozen `target/core-sidecar/core-sidecar/core_service.exe` | 68,793,273 B | `b61074d48b6c8d59e3dc930bd3482422e8d0309568a518527fad94f549564a46` |

安装包时间戳 2026-10-21 00:50:02；构建 HEAD=`239b165c2`（P20 交付 `e66927a31` 的后续唯一产品改动为本轮 ACL 修复）。

## 5. 未声称 / 已知限制

1. **未做代码签名/公证**；安装包仅本机构建，未做全新机器安装/卸载复验（P20 发布 Gate 的安装面证据仍为历史证据）。
2. Rust source 套件在**并行**运行（默认 test-threads）时有 3 个 `UNREAPED_WORKER_REGISTRY` 用例相互污染；本轮采用既有的 `--test-threads=1` 口径。该并行不稳定是既有测试隔离问题，不冒充全绿。
3. `RUST-ENV-BASELINE-1` 的 AC2 基线 `8bf3ae30` 未在本轮重跑（历史基线不重写）；本 Task 以当前 HEAD 的修复后套件收口为 `closed_with_limitations`。
4. P20 已知 `AC4 撕裂项 = LIMITATION/UNOBSERVED`；本轮未重新观测。
5. 产品架构与依赖未改；本轮只补 ACL 声明、生成物与测试期望。

## 6. 结论

当前 HEAD 的 v1 验收链（sidecar → Rust source/packaged → 前端 → Python M2 → NSIS 安装包）全部 exit 0；发现的 recycle-bin ACL 缺口已修复并有前后对照。**v1 可视为构建与测试完成**；发布签名、全新机器安装与既有 P20 limitation 仍按原记录保留，不声称超出证据。
