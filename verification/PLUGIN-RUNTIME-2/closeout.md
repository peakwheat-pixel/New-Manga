# PLUGIN-RUNTIME-2 Codex 集成与资源 closeout

日期：2026-10-23；用户授权：Codex 完成集成记录与资源 closeout。

- reviewed_head / delivery_head：2ea97edd6e65260d1276e7b1e505a036dc612f80。
- integration_commit：eb5e821f3798b4d411ddbd60cd52db65208a2812（main 已含被审实现及最终交接，无 merge 操作）。
- `git merge-base --is-ancestor 2ea97edd6e65260d1276e7b1e505a036dc612f80 HEAD`：exit 0。
- `git diff --exit-code 2ea97edd6e65260d1276e7b1e505a036dc612f80 HEAD -- src tests`：exit 0，无差异；工作区无源码/测试改动。
- 独立 r3 approved，Review 文件保持不变；R1/R2/R3 均 fixed。
- 集成验证：Windows / Python 3.14 / PYTHONUTF8=1；111 passed / 0 skipped。

```powershell
python -m pytest tests/providers/test_handlers_pipeline.py tests/infrastructure/test_plugin_runtime.py tests/core/test_core_plugin_wire.py tests/reading_export/test_export.py tests/core/test_p16_reader_export.py tests/core/test_core_assembly.py -q --tb=short --basetemp='G:/CODEX/New Manga.workspace/temp/PLUGIN-RUNTIME-2/closeout-20261023'
```

原始结果：integration-pytest.log。包含生产装配、真实 SQLite/插件子进程、真实 StartExport；模型使用 fake，无 GUI/打包/模型质量声明。

## 资源裁定

资源完整文件路径、字节与 SHA-256 清单见 resource-manifest.json。temp（4568 files / 266702806 bytes）、agent-output（1 files / 730 bytes）全部 PRESERVE_REFERENCED，供测试恢复及审计。现有主工作区与版本化证据原位保留；不把 clean/可达当作删除授权。没有新增 task-env、dataset/model、独立 build/artifact 或 exchange；test-material 包含在 temp 清单中。

六个既有 verification/P04/diagnostic_p22_*.jsonl 保持原样，不属于本 Task，PRESERVE_UNKNOWN。没有删除、移动或归档资源（均 0 项 / 0 字节），未执行 push/merge/reset/stash、worktree remove/prune/GC。

## 关闭与下一步

AC1/AC2：集成 111 passed；AC3：固定提交与 Handoff、r3 独审、证据 pin 通过治理检查。STATUS 3062 字节（≤3200）。Task done，canonical_evidence_status 与 resource_closeout_status 均 complete，STATUS 不再列其为 Active，Plan 保留终态依赖，LEDGER 重新生成；Task README 无该 Task Active 指针。

无需下一步操作：当前 Plan 无 READY 节点，PLUGIN-RUNTIME-SANDBOX-1 未授权；签名任务仍等待证书/发布签核，不派发新产品任务。

最终治理：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/PLUGIN-RUNTIME-2.md` PASS（3 warnings：2 个非终态、STATUS/Plan 体量预警）；`git diff --check` PASS。初次收口检查发现 STATUS 的当前 Task 行仍含终态链接、Resource destination 使用“原位”非路径，已将终态移入最近完成并填真实目标路径/manifest 后复跑通过。
