# 最终验收报告（AD-002 新桌面架构，2026-10-28）

- 仓库 HEAD：`8e4ec7066`（main，未 push）
- 依据：`doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md`（S0–S5 全部收口）
- 治理：`tools/governance/check.ps1` PASS

## 1. 产品与命令面

| 项 | 结果 |
|---|---|
| 生产命令面 | **66 / 66 IMPLEMENTED**（`extract-command-surface.py --check` 零漂移） |
| 页面 | 书架 / 工作台 / 阅读器 / 设置（含凭据、provider/network profile、绑定 slot、主题中心） |
| 主题 | 7 packs（默认 `saber-purple`），`macos-sonoma`「macOS 风」Light/Dark 双 token；热切换 **p95 10.456ms**（阈值 100ms） |
| 凭据 | `ICredentialStore` + Windows Credential Manager（UTF-16LE 与冻结 Core 字节兼容）；secret 零泄露（日志/证据扫描 0 命中） |

## 2. 端到端真机（最终包 RELEASE-REPACK-4，repo_head `f1b89c5e5`）

| 项 | 值 |
|---|---|
| base zip | 103,330,812 B，sha256 `cbd1b9e1…64adf` |
| models zip | 725,339,894 B，sha256 `aaa02c8b…4c3c7` |
| 安装 / Host 就绪 | 2,545.5 ms / 1,100.1 ms，console 0 |
| UI 导入 | 9 → 10 页（真实 grant 链） |
| ZIP 导出 | **7,070,562 B**，sha256 `72d81db9…945c`（3 JPG + manifest） |
| PDF 导出 | **20,728,075 B**，sha256 `c0a97eb3…b210`（3 页，`%PDF-1.7` + ToUnicode 可搜索层） |
| 打开导出目录 | 2.9 s |
| 退出/卸载 | WM_CLOSE 4.27 s、0 残留、卸载干净、注册表 0 |

## 3. 测试与质量

| 套件 | 结果 |
|---|---|
| `scripts/test.ps1` | **243 / 243**（coreclient 61 / host 56 / app 126，0 skipped） |
| pytest | **0 failed / 2773 passed / 10 skipped**（连续 5 次一致，skip 全部机器可判定） |
| vitest（旧壳） | 60 files / 567 tests |
| 构建 | Debug + Release PublishTrimmed（IL2026 已修，2026-10-27 起） |

## 4. 真机 5 项

| 项 | 结论 |
|---|---|
| Mica | ✅ `actual=Mica`（主窗可见时约 35 s 达峰；REPACK-4 首测 None 为遮挡/时序，非回归） |
| DPI | ✅ 跨屏 96→192→96 重渲染验证（DPR2）；⚠️ 4K@200% 目前 **NOT_ACHIEVABLE**（Mi TV 不被系统识别为输出，环境阻塞） |
| 工作集 | ✅ App 空闲 147.5 MB / 阅读滚动 411.9 MB；core 41.1 MB；host 22.7 MB |
| Esc/H | ✅ 键盘路径 PASS（沉浸窗聚焦后 H 隐藏 HUD、Esc 回阅读器；窗口数/sha 变化为判据） |
| IME | ⏸ 需人工确认（自动化无法注入微软拼音） |

## 5. 外部/遗留（不阻塞交付）

1. **真实翻译**：REAL-TRANSLATE-PROVIDER-1 已装配 OpenCode provider + vault，但账号 **额度 429/402** → AC3 BLOCKED；充值后 `tools/run_translate_probe.py` 直接复验，无需改码。
2. `identity-translation` 仍为 experimental 占位（输入=输出），不得宣传为真实翻译质量。
3. 4K@200%：需 Mi TV 被系统识别为可用输出后另测。
4. IME：需用户前台人工确认。
5. 冲突 worktree `worktrees/THEME-MACOS-2` 的外部 WIP 未清理（未触碰；处置见 `task-envs/EXTERNAL-THEME-WIP-20261028`）。
6. 历史凭据残留 2 条（`p15-host-2-smoke`、`3819f991…`）仅上报未删。

## 6. 关键提交索引

- 命令面收尾：`77eb7cfd6`（credential port，66/0）
- 导出闭环：`3f73c92a1`（EXPORT-E2E-CLOSE-1）；`dd2408869`（PDF 验收纠偏）
- UI 收口：`b874b2cf7`（选择器）、`13cf26f6c`（导入/导出入口）、`2591ef028`（PDF UI）
- 质量：`965d1d3bb`（flaky 根治，pytest 0F）、`8e4ec7066`（主线最终 HEAD）
- 发布：`caa0fdda8`（REPACK-4 done）、`cabdd7a28`（真机复测）
