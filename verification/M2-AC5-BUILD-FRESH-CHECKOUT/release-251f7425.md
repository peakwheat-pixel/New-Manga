# Release evidence：M2-AC5-BUILD-FRESH-CHECKOUT

- release commit：`251f7425`（parent `a0ffc4f3`=T1 integration 后的 main HEAD；T1 收口与 T2 release 同 commit）
- release 时间：2026-09-30（编排会话代行 Codex 自主释放，Goal「M2 遗留技术债清算」T2，doc/GOAL.md）
- Owner：ZCode（子 agent，worktree `G:/CODEX/New Manga.worktrees/M2-AC5-BUILD-FRESH-CHECKOUT-zcode`）
- Reviewer：DeepSeek Harness（非作者静态，r1/r2 两轮）
- 方案冻结：build.rs 可诊断探测（不自动 PyInstaller）+ build_sidecar.ps1 增量短路 + 不加 beforeBuildCommand（理由记录 README）
