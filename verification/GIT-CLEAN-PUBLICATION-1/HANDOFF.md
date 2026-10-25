---
task_id: GIT-CLEAN-PUBLICATION-1
author: Codex
recipient: DeepSeek Harness
base_commit: 349e61faff5f93067af5d4ce2d9e394e0d665b8c
delivery_head: e34a90d001cce1fa966aec7d2b032bb5ad1cf148
status: blocked_after_review
---

# Handoff：独立源码快照（尚未批准push）

## 交付结果

候选仓库 `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/source-export-r4`，branch `codex/clean-source-snapshot`，root commit `e34a90d001cce1fa966aec7d2b032bb5ad1cf148`。源仓仍为 `G:/CODEX/New Manga` / main / `349e61faff5f93067af5d4ce2d9e394e0d665b8c`。这两个SHA属于不同仓库，不是普通base..head增量或可直接合并的分支。

AC1–3的文件来源、私有材料排除、独立根历史与原件保护已核验。AC4仍BLOCKED：Core一个参数化用例的三组失败、先前Rust并行共享registry风险、packaged场景未执行；AC5交接/证据已形成，DSH r1已执行且blocked。完整结果见RESULT.md，机器证据见validation.json，稳定副本在Task的review-package目录。

## 验证证据

- r4离线frontend build通过；frontend435项在r3通过且整个frontend源码树与r4一致。
- r4 `cargo test --locked --offline -- --skip packaged_sidecar_tests:: --test-threads=1`：153 passed / 1 ignored / 12 filtered；显式M2RC1_DEV_PREVIEW=1、bundle.resources=[]、独立CARGO_TARGET_DIR。ignored仅性能探针，12项需要独立冻结sidecar，不能当PASS。
- r2 `python -B -m pytest tests/core -q -rs ...`：771 passed / 3 failed；src/tests/core树与r4完全一致。3项在两次相同条件下失败，限额已到，不再盲复跑；插件事件为无法给python.exe授予sandbox访问。
- 串行/并行和早期缺夹具失败日志全部保留；没有通过修改生产代码或跳过Core失败刷绿。

## 历史 r1 派发指令（已执行，勿重复）

- Task：GIT-CLEAN-PUBLICATION-1，独立Review阶段；不另释放业务修复。
- Agent：DeepSeek Harness（Reviewer）；Owner仍Codex，二者不同，r1已完成且blocked。
- Recovery：以上两个实际仓库/branch/base/head；无新linked worktree需要创建。当前checkpoint在本目录。
- Scope：只读检查源、候选和冻结证据；唯一允许写 `G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/dsh-review-r1.md`。不修改候选、生产代码、Task状态、系统Python ACL、素材、registry、历史/refs、未提交内容或远端。
- Deliverables：按REVIEW模板覆盖Architecture与Verification，绑定固定候选SHA，逐项AC/材料Gate与测试失败给出真实裁定；不得虚构独立批准。
- Verification：核对候选HEAD/root parent为空/remote为空/SOURCE_MANIFEST；检查Task canonical SHA和validation.json中的代码树等价；可运行只读Git核查以及必要的新变量验证。未运行则NOT_RUN；12项packaged与ignored不转PASS。对已达同条件失败上限的Core3项先静态核查原因，不重复盲跑；不修改系统ACL。

**可直接转发：**

在 `G:/CODEX/New Manga` 对 `GIT-CLEAN-PUBLICATION-1` 做只读独立Review。先读Task、当前checkpoint、RESULT.md和本Handoff。源main/base/head固定 `349e61faff5f93067af5d4ce2d9e394e0d665b8c`；候选在 `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/source-export-r4`、branch `codex/clean-source-snapshot`、独立root `e34a90d001cce1fa966aec7d2b032bb5ad1cf148`。不得把它当普通主线增量或擅自集成。用Task的外部SHA表核对 `review-package`，检查SOURCE_MANIFEST逐文件来源、2处目录字面量变换、5个自制PNG及P04/P22测试源码特许、169个JPEG及其外层共338个禁止对象缺失、新仓无main祖先/无remote、原main/index/P04日志保护。核查前端435通过的代码树等价、Rust串行153通过/1忽略/12过滤的边界、Core771通过/3失败的sandbox权限事实，以及先前并行registry失败；不得用串行通过或source测试冒充packaged/GUI/模型/完整审计PASS。Core一个参数化用例的三组失败已经达到同条件2次上限，先静态分析并提出新变量，不重复盲跑、不改真实Python ACL。唯一可写文件为 `verification/GIT-CLEAN-PUBLICATION-1/dsh-review-r1.md`，按项目REVIEW模板绑定精确候选SHA，报告架构/材料/验证结论与阻断，必要时建议另冻诊断Task；不修改生产代码、候选、Task状态、素材/registry、历史/refs/工作区或远端，不push、不清理、不改写历史。尚未满足的Gate保留原状态。

## 风险与资源

Core失败尚未在具备可用sandbox runtime的环境排除，Rust并行共享状态风险未裁决。4个本地候选、构建缓存、隔离数据和冻结证据均PRESERVE_REFERENCED；不删除或重写。源main的任何上传仍被用户“不传播”裁决禁止。当前快照只解决材料排除与独立历史准备，不代表产品release或完整审计完成。

## 当前交接（取代上面的历史派发建议）

DSH r1 blocked 原文件不改；父 Task 保持 in_review、父head=e34。当前唯一执行为 DIAG-1；恢复看其 Task、RESULT 和 APPOINTMENT。r2/r3串行均152/1 failed、r4串行153/0；当前r4默认并发151/2 failed，不能称并发安全。只通过Git tracked对象交付，禁止复制live目录/本地复审包。旧19日志的EXIT头由原checks事后封装，原日志未改。Core错误原DB已SOURCE_PIN；真实旧icacls returncode/stderr未知，补丁与mock在独立diag head，不在父候选/main。新的诊断head已重新Appointment，尚未独审；不沿用旧批准，不push、不done。
