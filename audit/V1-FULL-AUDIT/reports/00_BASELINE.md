# 审计基线

日期：2026-10-24（Asia/Shanghai）；审计固定产品 HEAD：`349e61faff5f93067af5d4ce2d9e394e0d665b8c`；分支 `main`；common directory `G:/CODEX/New Manga/.git`。

{
  "timestamp": "2026-10-23T16:24:40.597019+00:00",
  "head": "349e61faff5f93067af5d4ce2d9e394e0d665b8c",
  "branch": "main",
  "common_dir": "G:/CODEX/New Manga/.git",
  "worktrees": "worktree G:/CODEX/New Manga\nHEAD 349e61faff5f93067af5d4ce2d9e394e0d665b8c\nbranch refs/heads/main",
  "initial_dirty": "6 pre-existing untracked verification/P04/diagnostic_p22_*.jsonl; audit created after baseline",
  "python": "C:\\Python314\\python.exe",
  "python_version": "3.14.6 (tags/v3.14.6:c63aec6, Jun 10 2026, 10:26:10) [MSC v.1944 64 bit (AMD64)]",
  "platform": "Windows-11-10.0.26300-SP0",
  "versions": {
    "node": "v24.15.0",
    "npm.cmd": "12.0.1",
    "rustc": "rustc 1.98.1 (48a229cea 2026-09-01)",
    "cargo": "cargo 1.98.1 (797e8a9bc 2026-08-05)"
  }
}

保留全部历史 Gate 与缺失证据，不继承历史 PASS。现有 6 个未跟踪诊断日志未修改。版本前端/Tauri为0.1.0（不代表V1验收）。用户授权独立审计文件与隔离测试；不修业务代码、不发布、不调用付费API。
