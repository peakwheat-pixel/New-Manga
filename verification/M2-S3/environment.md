# M2-S3 实验环境快照（S3-AC1）

- 日期：2026-09-26
- 记录者：ZCode（Owner）

## Git 基线

见 [`baseline-selfcheck.md`](baseline-selfcheck.md)：base `90c3e45962733799d43e3aefacf4fea99f662a2c`、分支 `agent/zcode/M2-S3-tauri-asset-protocol-probe`、linked worktree（common dir = `G:/CODEX/New Manga/.git`）、开工时干净。

## 主机与 OS

| 项 | 值 |
|---|---|
| OS | Windows 11，`Windows-11-10.0.26200-SP0`（NT 10.0.26200） |
| WebView2 Runtime（Evergreen，HKLM） | `153.0.4234.48`（注册表键 `EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}`，`pv` 值，经 Python `winreg` 读取——Git Bash 下 `reg query` 转义问题改用 winreg） |
| 主机名/用户 | HOME-MY / 49745 |

## Rust 工具链（cargo 管理；实验依赖与锁文件仅在 `experiments/M2-S3/probe/`）

| 项 | 值 |
|---|---|
| rustc | `rustc 1.98.1 (48a229cea 2026-09-01)` |
| cargo | `cargo 1.98.1 (797e8a9bc 2026-08-05)` |
| toolchain | `stable-x86_64-pc-windows-msvc`（rustup 默认） |
| host | `x86_64-pc-windows-msvc` |

## Node / 包管理器

| 项 | 值 |
|---|---|
| node | `v24.15.0` |
| npm | `12.0.1` |
| pnpm | `11.25.0` |
| 用途 | **探针未使用 npm/pnpm**——前端为纯静态目录（`experiments/M2-S3/ui/`），`tauri.conf.json` 的 `build.frontendDist` 直接指向它；无 Node 构建步骤、无 package.json。Node 仅存在于系统中（如实记录） |

## Tauri 与插件版本

| 项 | 值 |
|---|---|
| tauri（Rust crate） | `2.11.6`（`tauri-build 2.6.3`、`wry 0.55.1`、`tao 0.35.3`；Cargo.lock 锁定） |
| tauri-build | `2` |
| 其他插件 | 无（探针不引入 tauri-plugin-*） |
| 前端 | 纯静态 HTML/JS（无框架），Tauri core invoke API（`window.__TAURI__.core.invoke`，由 Tauri 注入） |

## 实验专用依赖边界

- `experiments/M2-S3/probe/Cargo.toml`：tauri 2、serde 1、serde_json 1、rand 0.8、base64 0.22（全部为实验 crate，锁文件 `Cargo.lock` 随实验提交）。
- `experiments/M2-S3/probe/target/` 构建产物被 `.gitignore` 排除，不入库。
- fixture 生成器 `experiments/M2-S3/fixtures/gen_fixtures.py` 仅用 CPython 标准库（确定性 RGB 噪声 PNG，方法与 M2-S1/M2-S2 一致；scope 内资产为独立副本，不用硬链接——M2-S2 教训）。
- 根目录依赖/锁文件零改动；`src/**`、`tests/**`、`packaging/**`、`src-tauri/**`、产品 React/QML 零触碰。
