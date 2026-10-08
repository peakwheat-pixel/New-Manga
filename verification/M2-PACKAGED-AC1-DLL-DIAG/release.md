# 正式释放与恢复点

Timestamp=2026-10-08T09:45:03+08:00；Agent=Codex。
Task=M2-PACKAGED-AC1-DLL-DIAG；Owner=DeepSeek Harness；Reviewer=Codex（非作者）；Integrator=Codex。
TaskStatus=ready；ExecutionState=IDLE；诊断尚未派发/开始。
base_commit=9063c317937b86bed1f6ff3e2f2c5d224dc10553；release_commit=4330b792479c7d251b6dd2389aefa4b1a1b7fe6f；synced_owner_HEAD=4330b792479c7d251b6dd2389aefa4b1a1b7fe6f。
branch=agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG；worktree=G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh；common-dir=G:/CODEX/New Manga/.git。
worktree创建于base，实测clean后merge --ff-only到release，同步后HEAD和clean/common-dir再次核验。
主线后续只追加本恢复点/指令与元数据，Owner固定留在release，无需追随main。

Completed：Task/Plan/STATUS/索引ready，冻结只读范围，硬依赖GC-2祖先核验、installer实测SHA匹配、工作区分配同步。
Current point：等待DSH接手Reality Check和Codex串行登记认领；不自动执行诊断。
Tests remaining：诊断AC1-AC5全部NOT_RUN，未做DLL探针/产品验收；释放验证是治理检查，不是诊断PASS。
Open questions：具体DLL/符号/闭包/环境原因UNKNOWN；先有证据再提出最小修复范围，修复须单独冻结。
Resume safety：释放时RESUME_SAFE；开始前核对固定HEAD/clean/common-dir/installer SHA，漂移记DRIFT_DETECTED。
旧runner debt保持blocked，旧实现未合并，完整Gate未通过。主线.qoder-credits他人dirty保留，不提交不清理。

[完整可转发DSH指令](DSH_INSTRUCTION.md)。此恢复追加仅在主仓库，以绝对路径读取；Owner checkout不需包含此追加提交。
