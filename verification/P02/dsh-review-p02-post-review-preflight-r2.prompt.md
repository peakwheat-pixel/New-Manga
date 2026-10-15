请对本地仓库当前 HEAD=8a0685c9bf5aec7e7cc51f466f3fec7b176c35de（tree=980a2a47d30630c5d0a7ad6adca32e644fc5ae95）做只读、独立的 P02 follow-up Review。parent D22=0a843a65c28818f92726bd91ae4c244e66fb37ea；main/base D19=1d5845e2b185179d7b683e5279f6520fc0882d97。当前是 detached reviewer worktree；保持 HEAD 不变且不修改文件。

上一轮 R1 exact HEAD=d92c405304cb88712cb8777d8ec59618f4806df7，Verdict=APPROVED，P0/P1/P2/P3=0/0/0/4。follow-up 目标是核验 P3-1..4 已关闭：
1. doc/tasks/P02.md 旧 preflight-start continuation 已明确标为历史快照。
2. checkpoint next action 与当前执行阶段一致。
3. route/diff validation reports 明确绑定 base/head/tree/command/exit/stdout/stderr hashes；D22 exact route=7/7 PASS，D19..D22 与 parent..D22 diffcheck 均为 EXIT 0。
4. doc/00_INDEX.md、doc/STATUS.md 与 doc/REBASELINE_PLAN.md 的 R5 count/disposition 摘要一致。

检查完整 diff D19..HEAD 及 P02 当前 Task、Plan、Status、Index、blocker checkpoint、R1 DSH report、r3/r4 validation artifacts。确认仅改冻结范围 doc/00_INDEX.md、doc/REBASELINE_PLAN.md、doc/STATUS.md、doc/tasks/P02.md、verification/P02/**，没有产品代码/接口/依赖改动。禁止修改文件、提交或切换 HEAD。

只允许运行只读命令：python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py、git diff D19 HEAD --check、git diff HEAD^ HEAD --check、git status/rev-parse/read files. 不要访问 main root 的其他脏文件，也不要读取 root manifest 指向的用户文件。不要运行 HostFolder 重扫、host inventory、Windows Feature query、wsb start、guest command、build、Cargo/Tauri、Vitest、GUI 或产品验收。

核对产品边界仍为 Feature=UNKNOWN、fresh preflight=BLOCKED、wsb start=NOT_RUN、build=NOT_AUTHORIZED / NOT_RUN、Hard Build Barrier=EFFECTIVE；不得将 Review、准入、Build Gate 与产品验收混为一谈。报告 raw HostFolder stdout 的绝对路径属已知本地路径暴露提示，确认未新增 SID、身份值、无关窗口标题或其他路径泄漏。

输出简体中文：Verdict（APPROVED 或 CHANGES_REQUESTED）、review HEAD/base、P3-1..4 closure matrix、route/diff 命令/exit、remaining findings（严重级别、路径/行号、最小修复）、是否允许 fast-forward 到 main。只有 P0/P1/P2=0 且四项 closure 有充分证据时才 APPROVED；未运行项记 NOT_RUN。
