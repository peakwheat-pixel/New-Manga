# IMPORT-TRIAGE-1 Handoff（REPACK-5 导入 BLOCKED 诊断）

- Task: `doc/tasks/IMPORT-TRIAGE-1.md`（task-58）；Branch `task/IMPORT-TRIAGE-1`；Base `441b7b57a`；Delivery head: 见 Task 卡。
- 结论：**非 HEAD 回归、非数据根/catalog 缺陷，产品无需修复**；烟测 BLOCKED = 烟测脚本/安装环境产物。
- 证据：`verification/IMPORT-TRIAGE-1/REPORT.md` + `evidence/`（evidence.json、wire ndjson、grants、4 张截图、fixture 创建证据）。

## 复现（成功路径）

1. `apps/desktop-avalonia/scripts/new-test-book.ps1 -DataRoot <fresh-root> -SidecarDirectory <REPACK-5 models sidecar> -EvidencePath <evidence>` 生成全新 fixture 根（8 页）。
2. 启动 `RELEASE-REPACK-5/out/NewManga-0.1.0-win-x64-models/app/NewManga.App.exe`：
   `--data-root=<fresh-root> --sidecar-dir=<pkg>/app/core-sidecar --parity --log-dir=<private logs>`。
3. 书架 → 导入文件 → 选择 `verification` 里的烟测同文件（`ui-import-2.png`，sha `e1b6787b…`）→ 目标书/章/策略保持默认 → 开始导入。
4. 期望：UI「已导入 1 个文件」；wire `RegisterImportSource` 后 16–18 ms 出现 `ImportPages`；`library.db` pages 8→9。

## 烟测失败签名（Lead 已解析，证据见 `RELEASE-REPACK-5/import-wire-tail.ndjson`）

`RegisterImportSource`（`ui-import-2.png`, 134 B, sha `e1b6787b…`, grant 还剩 299 s）→ **同秒 `RevokeImportSource`** → 之后 34 s 无命令；无 `ImportPages`。定位为客户端流程中途放弃（自动化未完成目标确认/误点关闭），不是 grant 过期、不是输入缺失、不是 Core 拒绝。

## 遗留/建议

1. 烟测脚本按 REPORT §4 硬化（断言选择器+结果行+DB 增量，保留失败上下文）。
2. 烟测安装目录已删除，无法复核其二进制混装；建议以后烟测保留 install 目录哈希清单。
3. 本卡未改产品代码；AC5 不适用（check.ps1 PASS）。

## 下一步

无需产品修复；建议将烟测脚本硬化作为 REPACK-6 的前置项（或单独小卡）。
