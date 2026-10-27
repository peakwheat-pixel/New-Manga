---
id: RELEASE-REPACK-4
title: 最终发布包（含 PDF UI/工具/修复）与端到端验收
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-28_goal_all_authorized
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: f1b89c5e5
branch: task/RELEASE-REPACK-4
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-4
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RELEASE-REPACK-4
allowed_paths:
  - doc/tasks/RELEASE-REPACK-4.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - packaging/**; apps/desktop-avalonia/scripts/**; apps/desktop-avalonia/docs/**
  - verification/RELEASE-REPACK-4/**
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-4/**
  - G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-4/**
---

# RELEASE-REPACK-4：最终发布包（含 PDF UI / 翻译工具 / 最终修复）

## 背景
REPACK-3（repo_head dd2408869）之后合入了 PDF-EXPORT-UI-1（PDF 面板）、REAL-TRANSLATE-PROVIDER-1 工具与测试修复。需要一次**最终**打包，并做端到端验收（含 PDF 导出）。

## Acceptance Criteria

- [x] **AC1 重打包**：当前 HEAD 重打 base+models zip（记录新旧 sha256/大小/HEAD；torch-free 断言）。→ **MET**：构建 HEAD `f1b89c5e5`（含 Lead 修复 `4be1c3f4f`；原 base `84dd38978` 编译失败，证据 `build-head-failure.log`）；新 base zip **103,330,812B**、models zip **725,339,894B**（旧 103,326,248 / 725,334,588B）；sidecar base `bd23e66f…0d99`、models `3909a4a2…f57dde5`（未复用旧 exe）；VERSION `repo_head=f1b89c5e5…`；torch-free PASS。
- [x] **AC2 全流程（含 PDF）**：全新安装 → 导入 → 阅读 → 沉浸 Esc/H → 导出 ZIP → 导出 PDF（面板 PDF/searchable_dual_layer）→ 打开导出目录；每步截图/耗时。→ **MET**：安装 2,545.5ms、Host 就绪 1,100.1ms、console 0；导入 1 文件 9→10 页；阅读/滚动；沉浸（UIA 按钮）；**PDF 20,728,075B sha256 `c0a97eb3…b210` 3 页 `%PDF-1.7`+ToUnicode**；ZIP 7,070,562B sha256 `72d81db9…945c`（3 JPG+manifest）；打开导出目录 2.9s。证据 `screens/01–10`、`smoke.json`。
- [x] **AC3 真机 5 项**：Mica（actual/取色）、4K@200% DPI、工作集、Esc/H 键盘（前台自动化）、IME N/A。→ **部分**：Mica **本次 actual=None**（transparency=1、DWM 38=0；REPACK-3 同机曾 actual=Mica → 疑似回归，需复核）；4K@200% **NOT_AVAILABLE**（主屏 2560×1440@100%；Mi TV 3840×2160 物理连接但当前未在桌面扩展，REPACK-3 时为 150%）；WS App **526.7MB**、core 44.5MB、bridge 23.7MB；Esc/H **前台已取得（foreground_pid==app_pid）且真实 keybd_event 已发送，但前后截图 sha 相同、UI 无可观察变化** → PARTIAL；IME N/A。证据 `environment.json`、`screens/11–14`。
- [x] **AC4 稳定性**：0 残留、console 0、卸载干净。→ **MET**：WM_CLOSE 4,267.9ms；本安装 0 残留；卸载 exit=0、目录消失、数据根保留；注册表 `*NewManga*` 0；凭据 2 条历史/他 Agent 残留只上报未删。
- [x] **AC5 门禁**：干净 worktree test.ps1 全绿（≥241）；pytest 0F/2773P/10S；check.ps1 PASS；64-hex pin；Handoff。→ **MET（test 计数为 Lead 修复后预期 232/232，非 241；Mac 主题测试已移除待 THEME-MACOS-2 重做）**：`TEST PASS 232/232`；pytest **0F/2773P/10S**；check.ps1 PASS；pin 见下表；Handoff 已交付。

## 允许修改范围
`packaging/**`、`apps/desktop-avalonia/scripts/**`、`apps/desktop-avalonia/docs/**`、`verification/RELEASE-REPACK-4/**`、本卡/STATUS/PLAN/LEDGER、workspace。

## 禁止范围

不改 Python Core 语义/协议/Host 契约/旧壳、不 push、不 gc/prune；不得伪造结果；**禁止 `git add -A`（主工作树有其它会话改动）**。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E-R4-REPORT | AC1-AC5 | `verification/RELEASE-REPACK-4/REPORT.md` | `089714d1e` | `1b2a4a903ccf89892828c8503f9ee264dd16a42bde7f7f14d2709eaff9f3e080` | CANONICAL |
| E-R4-SMOKE | AC2-AC4 | `verification/RELEASE-REPACK-4/smoke.json` | `089714d1e` | `c47be54a36ce7b6252dc0caf749c78f92b0f3d932bba53a341b738271520200f` | CANONICAL |
| E-R4-PKG | AC1 | `verification/RELEASE-REPACK-4/package-hashes.json` | `089714d1e` | `16596c5d7d61d17514116af5568fb5820c1bf08b5b9dc7bbc2a2dad87a1c03a1` | CANONICAL |
| E-R4-ENV | AC3 | `verification/RELEASE-REPACK-4/environment.json` | `089714d1e` | `dfbcc362da656017a4afc516b9858e3329952f081ef8c8fac79798229149cdbe` | CANONICAL |
| E-R4-SHOT-BOOKSHELF | AC2 | `verification/RELEASE-REPACK-4/screens/01-bookshelf.png` | `089714d1e` | `35c8a407f0ae190058375b030d4de542c5291a658304757075aaf9a639937581` | CANONICAL |
| E-R4-SHOT-IMPORT | AC2 | `verification/RELEASE-REPACK-4/screens/03-import-result.png` | `089714d1e` | `a726872ae36473521bdfc3464269098df0e43d05f6f0703070a27de984fee1bc` | CANONICAL |
| E-R4-SHOT-READER | AC2 | `verification/RELEASE-REPACK-4/screens/04-reader.png` | `089714d1e` | `94f84dcfee1374d3a4b304fb26377080925c73691893aae7712afd741fa617d9` | CANONICAL |
| E-R4-SHOT-IMMERSIVE | AC2/AC3 | `verification/RELEASE-REPACK-4/screens/06-immersive.png` | `089714d1e` | `295796401b742955528e2d5249e42a40b174d9bca1d0f2809f30e7cadaa4d80b` | CANONICAL |
| E-R4-SHOT-PDFPANEL | AC2 | `verification/RELEASE-REPACK-4/screens/07-export-panel-pdf.png` | `089714d1e` | `603b8cfb25c79113c1ff5f8630bbee6bcf8653a6d67b14f88cafff2d59dd67d4` | CANONICAL |
| E-R4-SHOT-PDFDONE | AC2 | `verification/RELEASE-REPACK-4/screens/08-export-pdf-done.png` | `089714d1e` | `12b27cb9e7c1b112fda6952e30d30f20339db1a2ce5f95097e5077baca88cd05` | CANONICAL |
| E-R4-SHOT-ZIPDONE | AC2 | `verification/RELEASE-REPACK-4/screens/09-export-zip-done.png` | `089714d1e` | `b9f1883063a096cd84fc132775a9530d2a431572ac3f12e0b3cbd4c5e2eb23ef` | CANONICAL |
| E-R4-SHOT-FOLDER | AC2 | `verification/RELEASE-REPACK-4/screens/10-export-folder.png` | `089714d1e` | `a2b6ccd488d2deaac61f805388f3006fdfcff1e5b9f8cb84e04d1a95050466ca` | CANONICAL |
| E-R4-ESC-H | AC3 | `verification/RELEASE-REPACK-4/screens/12-esc-immersive.png` | `089714d1e` | `421093b3086134eb1b7b4f0d4e33b5e4fa93761da97399744a7b3ff19f6abd94` | CANONICAL |
| E-R4-DOTNET | AC5 | `verification/RELEASE-REPACK-4/dotnet-all.log` | `089714d1e` | `f174e8678ffb05939df0917cd44a11571007c27a21cbf4e4eae94417305ae5df` | CANONICAL |
| E-R4-PYTEST | AC5 | `verification/RELEASE-REPACK-4/pytest.log` | `089714d1e` | `9c7ec24538678c31cd0a9bae67841bb17c410930abb48095878de5123175ce99` | CANONICAL |
| E-R4-BLOCKER | AC1 | `verification/RELEASE-REPACK-4/build-head-failure.log` | `089714d1e` | `146b5b290ce0fba26169d950764b00667738dd9fc459ef072b9c665c103e9c89` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-4 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-4 | `out/`（新包）、`sidecar-*/`、`data-root/`、`screens/` | 证据已复制到 `verification/RELEASE-REPACK-4/`；旧包 REPACK-3/out 未动 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：Mica actual=None 疑似回归（待 DSH 复核）；4K@200% 环境不具备；Esc/H 键盘无可观察响应（待用户真机确认）；凭据 2 条历史残留待裁决。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。

## 构建阻塞记录

原 base `84dd38978`：`MainWindow.axaml.cs(593) error CS1061: SettingsPage 未包含 ApplyLayout`（`152538e34` 引入调用、未提交实现）；已上报 Lead，修复提交 `4be1c3f4f` 回退未落地主题 API（UI 文件→`4ea86e03a`，Mac 主题测试移出），其后 `f1b89c5e5` 为 ledger 提交；本任务以 `f1b89c5e5` 出包。
