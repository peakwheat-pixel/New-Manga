---
id: RELEASE-REPACK-3
title: 第三次重打包（含 UI 收尾）与全流程复验
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_round_2_5
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: 10273c9ce
branch: task/RELEASE-REPACK-3
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-3
integration_commit: 4290afb1b
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RELEASE-REPACK-3
allowed_paths:
  - doc/tasks/RELEASE-REPACK-3.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - packaging/**
  - apps/desktop-avalonia/scripts/**
  - apps/desktop-avalonia/docs/**
  - verification/RELEASE-REPACK-3/**
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-3/**
  - G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-3/**
---

# RELEASE-REPACK-3：第三次重打包与全流程复验

## 背景
RELEASE-SMOKE-1 发现 REPACK-2 包 `repo_head=0f4b836a5` **早于** IMPORT-EXPORT-UI-1（`13cf26f6c`）→ 安装包无导入/导出 UI。当前 HEAD 已含全部 UI 收尾。

## Acceptance Criteria

- [x] **AC1**：用当前 HEAD 重打 base+models zip；记录 HEAD/新旧 sha256/大小；torch-free 断言。→ **MET**：HEAD `dd2408869`；base zip 103,326,248B、models zip **725,334,588B**；sidecar base `65d7b55a…c422b`、models `8cfc9080…9340`（旧 `091a201d…`/`c5531930…`，未复用旧 exe）；VERSION `repo_head=dd2408869…`；torch-free PASS（models bundle 无 `_internal/torch`、含 onnxruntime）。证据 `package-hashes.json`、`build-*.log`。
- [x] **AC2**：全新安装 → 书架→导入→阅读→进度→沉浸 Esc/H→导出 ZIP→打开导出目录（+ PDF 若 PDF-EXPORT-UI-1 已合）；每步截图/耗时。→ **MET（PDF 除外）**：安装 2,448.5ms、Host 就绪 1,133.0ms、console 0；UI 导入 1 文件（8→9 页、DB pages=9，~7.9s）；阅读器/滚动；`reading_progress`（13.55%、87.37s）；沉浸 UIA ImmersiveButton 全屏；**导出 ZIP 7,070,562B sha256 `d77ecf888ddbfbb479129c3db35bf4ff65461651bbfefa330affd0ecd11136f7`**（3 翻译页+manifest）；打开导出目录 2.9s。**PDF 未验**：PDF-EXPORT-UI-1（2591ef028）仅释放未实现 UI，当前导出面板仅 ZIP。证据 `screens/01–11`、`smoke.json`。
- [x] **AC3**：Mica/DPI 复核——明确 OS 版本/build；验证 Mica（actual/取色）与 4K@200% DPI（环境不满足则如实 BLOCKED + 当前显示器状态）。→ **结论已给**：OS=**Windows 11 26H2 build 26300.9711**（注册表 ProductName 仍写 Windows 10 Pro，CIM caption=Windows 11 专业版 → 纠正 smoke 的 Win10 判断）；**Mica actual=Mica**（app 诊断日志 requested=Mica,Blur,None；首帧 None→约 60s 后 Mica，与 MICA-FIX-1 一致）；主屏 2560×1440@96(100%)、副屏 **3840×2160@144(150%)** → **4K@200% NOT_AVAILABLE**（MICA-FIX-1 的 DPI=192 为 DPR2 仿真证据）。证据 `environment.json`、`mica-window-material.log`。
- [x] **AC4**：0 残留、console 0、卸载干净；历史凭据残留只上报不擅删。→ **MET**：console 0；WM_CLOSE 4,159.9ms；本安装 app/core/host_bridge 0 残留；卸载 exit=0、目录消失、数据根保留；注册表 `*NewManga*` 0；凭据管理器 2 条历史/他 Agent 残留（`p15-host-2-smoke`、`3819f991…`）只上报未删。
- [x] **AC5**：test.ps1 全绿（≥225，**须在干净 worktree 验证**）；pytest 无新增；check.ps1 -TaskPath PASS；64-hex pin；Handoff。→ **MET**：干净 worktree `TEST PASS (Debug): **234/234**`（CoreClient 61+Host 55+App 118，182.2s）；pytest **3F/2772P/9S**（与既有 3F/2739P/9S 失败集合一致，无新增）；check.ps1 PASS；pin 见下表；Handoff 已交付。

## 允许修改范围
`packaging/**`、`apps/desktop-avalonia/scripts/**`、`apps/desktop-avalonia/docs/**`、本卡、STATUS/PLAN/LEDGER、`verification/RELEASE-REPACK-3/**`、workspace。

## 禁止范围
不改 Core 语义/Host 契约/旧壳、不 push、不 gc/prune；不得复用旧 exe 冒充新构建；不伪造截图/数字；**不要在含他人未提交改动的主工作树上跑门禁**（用干净 worktree）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E-R3-REPORT | AC1-AC5 | `verification/RELEASE-REPACK-3/REPORT.md` | `b7e375921` | `b81a27d08f50511eb064a2be14bb158513507f6dab2eb7018d47b45a8fdbad57` | CANONICAL |
| E-R3-SMOKE | AC2-AC4 | `verification/RELEASE-REPACK-3/smoke.json` | `b7e375921` | `03c1c2f72b053ff70f5dbce109ab2cc915205d03648078cd363805f074a0b54a` | CANONICAL |
| E-R3-PKG | AC1 | `verification/RELEASE-REPACK-3/package-hashes.json` | `b7e375921` | `62f8bff84102925fed54421197b32bfa72769e1805e3f8704193a2a0da1bdaf3` | CANONICAL |
| E-R3-ENV | AC3 | `verification/RELEASE-REPACK-3/environment.json` | `b7e375921` | `a954f03790f89754420ed0ccc9f598a33ec8c783537826e915e891c56960f126` | CANONICAL |
| E-R3-SHOT-IMPORT | AC2 | `verification/RELEASE-REPACK-3/screens/11-import-result.png` | `b7e375921` | `0aca85cb9e307ac452834f539b4f0ae90bfea55cc03bc1340846700147809392` | CANONICAL |
| E-R3-SHOT-READER | AC2 | `verification/RELEASE-REPACK-3/screens/05-reader.png` | `b7e375921` | `7a00df2975d17c9f03f0490a11b0bb80b7a0dc60c8d94e58419dcc0b4de689ba` | CANONICAL |
| E-R3-SHOT-IMMERSIVE | AC2/AC3 | `verification/RELEASE-REPACK-3/screens/07-immersive.png` | `b7e375921` | `295796401b742955528e2d5249e42a40b174d9bca1d0f2809f30e7cadaa4d80b` | CANONICAL |
| E-R3-SHOT-EXPORT | AC2 | `verification/RELEASE-REPACK-3/screens/08-export-panel.png` | `b7e375921` | `e97272604efa978568b9d602ba7a822d39dbaacbdc466c84b7ff1a2ab33997f6` | CANONICAL |
| E-R3-SHOT-FOLDER | AC2 | `verification/RELEASE-REPACK-3/screens/10-export-folder.png` | `b7e375921` | `cfe4970101c4ef0f0c164fdfbf062224b62ed0d47616a5285708dec0a27f948e` | CANONICAL |
| E-R3-DOTNET | AC5 | `verification/RELEASE-REPACK-3/dotnet-all.log` | `b7e375921` | `41842c9ce8c8bda7902b812efd471ab82636b51cdfc65797f548ce5ed22b0c99` | CANONICAL |
| E-R3-PYTEST | AC5 | `verification/RELEASE-REPACK-3/pytest.log` | `b7e375921` | `68fb9c433c9950d19ed6f72b56c2c13bc0bab8f77fd2ca598d122ea88953439f` | CANONICAL |
| E-R3-MICA | AC3 | `verification/RELEASE-REPACK-3/mica-window-material.log` | `b7e375921` | `9e3d4b35b79579ab9cd63e3c91792bdf23b3fa7052a554c34b74a193d5ff533b` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-3 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-3 | `out/`（新包）、`sidecar-*/`、`data-root/`、`screens/` | 证据已复制到 `verification/RELEASE-REPACK-3/`；旧包 `RELEASE-REPACK-2/out` 未动 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：PDF 导出 UI 未实现（PDF-EXPORT-UI-1 仅释放）；4K@200% 环境不具备；键盘 Esc/H 与 IME 待用户确认；`HostCredentialCoordinator.cs` 的 trim 修复与 allowed_paths 偏差待 DSH 裁决。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。

## 实施偏差（需 DSH 裁决）

`apps/desktop-avalonia/src/NewManga.Host/HostCredentialCoordinator.cs`：Release `PublishTrimmed` 下
`error IL2026` 导致首轮打包失败；将证据 JSON 由反射 `JsonSerializer.Serialize` 改为
`Utf8JsonWriter(Indented=true)`（保持输出字段/格式；不改 Host 契约/语义）。该文件超出本卡
allowed_paths，请 DSH 确认接受或改由 CREDENTIAL-PORT-1 承接。
## Review（DSH 集成复核，2026-10-27）— PASS

- 新包：base zip 103,326,248B / models **725,334,588B**；新 sidecar base 65d7b55a…、models 8cfc9080…（旧  91a201d…/c5531930…，无复用）；VERSION epo_head=dd2408869；torch-free PASS。
- 全流程真机：安装 **2.45s**、Host 就绪 **1.13s**、console 0；书架 8 页 → **UI 导入 1 文件（8→9 页，DB pages=9）** → 阅读 → 滚动 → 进度 13.55%/87.37s → 沉浸全屏 → **导出 ZIP 7,070,562B sha256 d77ecf88…36f7** → 打开导出目录 2.9s。**PDF UI 未验**（PDF-EXPORT-UI-1 未实现，面板仍仅 ZIP）——如实。
- **Mica/DPI 结论（纠正 smoke）**：OS = **Windows 11 26H2 build 26300.9711**（注册表 ProductName 遗留字段误写 Win10）；**Mica actual=Mica**（首帧 None→约 60s 后 Mica，与 MICA-FIX-1 一致）；主屏 2560×1440@100%、副屏 3840×2160@150% → **4K@200% NOT_AVAILABLE**（DPI=192 属此前 DPR2 仿真证据，仍需真实 200% 环境复验）。
- 稳定性：WM_CLOSE 4.16s、0 残留；卸载干净；注册表 0；2 条历史/他 Agent 凭据残留仅上报。
- 回归：干净 worktree test.ps1 **234/234 PASS**；pytest 3F/2772P/9S（基线失败集合一致，无新增）；check PASS；12 条 pin。
- **裁决（超范围改动）**：接受 pps/desktop-avalonia/src/NewManga.Host/HostCredentialCoordinator.cs 的 Utf8JsonWriter(Indented) 改动——为解 Release PublishTrimmed **error IL2026**，未改 Host 契约；已记入本卡 Handoff，不转 CREDENTIAL-PORT-1。
- 遗留：PDF UI（PDF-EXPORT-UI-1 在途）；4K@200% 需真实环境；IME/键盘 Esc-H 待用户前台确认。
- 集成：4290afb1b。
