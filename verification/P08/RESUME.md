# P08 可恢复检查点

时间：2026-10-08（Asia/Shanghai）；Owner=Codex；TaskStatus=blocked；previous=in_progress；ExecutionState=CHECKPOINTED。
仓库G:/CODEX/New Manga；branch=main；worktree=当前主工作区；common-dir=G:/CODEX/New Manga/.git；start/base=ab2f813c0ce311a6712002cafd852b9e7a258380；P08 initial delivery head=f7d4a947；independent preliminary review head=f7d4a947。最新 review-fix commit以`git log -1 -- verification/P08 doc/tasks/P08.md`核验。

已完成：Reality Check、既有审计与当前代码差量核验、四页建议范围/数据保护/质量发布口径、D08全部193条编号AC、AC-SMOKE及§68–79总Gate覆盖、P09–P20切片/责任/Gate与待裁决选项。
当前工作点：SCOPE_DRAFT的D1–D7待用户回答；D08 §53/73/76发布门槛、模型下载P0/P1和扩展范围有明确冲突，未批准修改D08；数值质量资格标准尚未冻结；非作者Reviewer建议DSH但未派发/认领。没有独立批准，P08不done，不能实施P09以后。
下一确切步骤：读取用户D1–D7回答→逐项更新P08草案与Task/Plan/Status→固定提交→DSH非作者Review（单独授权/派发前只准备指令）→修订与集成检查；未回答保持pending，不按等待时长推断同意。

恢复核验：git status --short --branch；git rev-parse HEAD；git rev-parse --path-format=absolute --git-common-dir；读取doc/STATUS.md、doc/tasks/P08.md与SCOPE_DRAFT。base以来已知治理/P08文档与导航提交包括f7d4a947及当前审查修订；若有新产品/规则差量先记录DRIFT_DETECTED，不覆盖。
既有dirty归原作者：.qoder-credits/report.json、.qoder-credits/通路探测__8602db50.canvas.tsx，以及Runner Guard的antigravity-dispatch.json/.stderr.log；不stage/clean/reset/stash。
初次交付head=`f7d4a947594cc41663a9ab557551f267c3070cd6`。review-fix head=`4de7fb444d0abfb62c3eec327a7071a18f8ad90c`；此head上两套文档检查实际再跑通过，validation.log已更新。base以来还包含P系列编号统一、Qoder治理及P08初次提交。
本轮自有路径：doc/tasks/P08.md、verification/P08/**及Plan/Status/Index/短Roadmap/tasks索引、当前派生路线图/恢复导航与验证脚本的P08状态更新。
测试：python verification/P08/verify_scope.py与历史verify_plan.py，修订后validation.log记录命令、精确HEAD与结果；测试HEAD记录：P08首交付验证base=`ab2f813c`；此轮审查修订以`f7d4a947`为父HEAD，提交后再次运行文档检查并记录准确commit。产品pytest/cargo/vitest/GUI/build/模型推理全部NOT_RUN（文档范围）。
额度耗尽只中断执行，不代表Task完成；恢复后复用现有审计与本草案，只刷新漂移部分。Qoder仍退出，未来UI设计/实现ZCode；独立Review必须非作者。
