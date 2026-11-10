# FEA-15-ACCEPT-1 验收执行交接

- Owner：Codex；接续基线 `164ebabcfa90b92fc46c07238280960fc01f7423`；执行产品字节基线 `d63d735a712dbe47100db2e72b4d59a73dfd1f62`；证据提交 `8cad6d68c1e455c087a20346c9b1c0217bef129e`、`b7344445e3abc520c4d03fcb642b97880fe47738`。二者相对执行基线仅包含任务文档与证据。
- 交付：A1 Release 干净构建 0 警告/0 错误，EXIT 0；A7 各卡状态与限制汇总见 `doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md`；A6 pins 18/18 与治理双检查 PASS。五条证据的 commit 与 SHA-256 见任务卡。
- A5 未满足全绿：pytest 3515 passed/16 failed/12 skipped，EXIT 1；.NET 八项目中 App 884/4/11、Host 198/123/74，整体 EXIT 1；其他六项目无失败。失败对照和归因边界见 `verification/FEA-15-ACCEPT-1/README.md`，不能把失败全部归为环境问题或产品缺陷。
- A2 当前 HEAD 安装包缺失；旧包仅历史参考。A3 两入口隐藏进程级启动 EXIT 0，可见窗口和四页交互 NOT_RUN。A4 真实用户库 v14 升级与 `pre_restore` 回退 NOT_RUN；历史合成演练和内存探针不能代替它们。
- 保护与资源：共享 FEA-11 fixture 候选 62 个、系统 Python ACL 和 AppContainer profile 无事前完整快照，归属未明，保留不清理；任务专用 worktree、归档、夹具和 venv 保留待裁决。未修改生产代码、测试或冻结契约，未 push。
- 接收者：ZCode 独立 Review 会话。请对固定提交审查范围、五条证据 pin、失败与 NOT_RUN 的真实性、资源影响、验收结论及后续任务；最终验收结论由 ZCode 独立裁决，不由本执行会话自行宣布通过。
