<!-- ZCode session: sess_2a802094-24f6-4254-9bfa-33cad3a6bf4e; turn: turn_e3aefd14-c1ee-4fb2-a1d3-1f365ab262ff; CLI EXIT 0. Response preserved verbatim below. -->

检查器代码与未提交 diff 全部核清。三条硬规则（`check.ps1` 实码确认）：`799-801` PRESERVE_\* 行 destination **必须 Test-Path 通过**（`—`/none 一律报错，保留型=最终位置必须真实存在）；`802-810` integrity 必须 64hex（Leaf 文件会被复核匹配）**或真实存在的 manifest 文件**；`192/196` STATUS 必须始终有 `- 当前 Task：…(tasks/*.md)` 可解析行。出裁决。

---

# 补充裁决：终态收口的门禁合规方案与串行次序

## 一、模拟失败的根因定性（三个都是可修的表述/次序问题，非治理阻塞）

1. **manifest FAIL**：PRESERVE 型行的 `destination=—` 违反 `799-801`——保留型资源的「最终路径」=**保留位置本身**，必须填真实存在路径；`integrity=—` 违反 `802-810`——必须给 64hex 或真实清单文件。
2. **PLAN 65 行**：超 64 上限，须真实减行。
3. **默认 check FAIL**：「当前 Task：无」不满足 `:192` 正则——**指针任何时刻不得悬空**，终态瞬间也必须指向一张存在的卡。这是次序问题，不是格式问题。

## 二、Resource Manifest 修复方案（逐行，全部真实可验证、零虚构、零清理）

| 行 | disposition | destination | integrity | 依据 |
|---|---|---|---|---|
| temp 隔离根 | PRESERVE_UNKNOWN | `G:\CODEX\New Manga.workspace\FEA-15-ACCEPT-1`（真实存在） | **新建 `verification/FEA-15-ACCEPT-1/workspace-inventory.md`**：一条 `Get-ChildItem -Recurse` 递归清单（相对路径+大小+文件数统计）落盘 | 清单真实生成、只读采集、不写入隔离根；`Resolve-LocalPath` 对仓库相对路径 Test-Path ✓ |
| user-data | NOT_APPLICABLE（不动） | — | — | `798/802` 双跳过 ✓ |
| build（clean-tree 构建） | PRESERVE_REFERENCED | `…\FEA-15-ACCEPT-1\clean-tree\apps\desktop-avalonia` | 同 `workspace-inventory.md` | 目录存在 ✓；清单文件存在 ✓ |
| worktree（clean-tree） | PRESERVE_REFERENCED | `…\FEA-15-ACCEPT-1\clean-tree` | 同上 | 同上 |
| runtime ACL（**拆两行**） | PRESERVE_UNKNOWN ×2 | ①`C:\Python314\python.exe` ②`C:\Python314` | ①**实测 64hex**：`Get-FileHash python.exe` 真算填入（`:809` 会对 Leaf 复核匹配，必须真算）②`verification/FEA-15-ACCEPT-1/python-acl-observation.log`（已存在） | 原行 source 双路径合并无法过检，拆行后各自可验；ACL 观察清单真实在库 |
| AppContainer profile | **NOT_APPLICABLE**（result 写明） | — | — | **唯一不虚构的过检写法**：无事前清单、归属未证明、**无可验证具体实例**；result 列写「无实例可核销（归属未证明）；保留不清理、禁止撤销；观察记录见 python-acl-observation.log」——`:798/:802` 跳过，`:782`「无资源写 NOT_APPLICABLE」同精神 |

要点：**不为机械检查虚构任何资源目标**——destination 全部是资源真实所在（原地保留），integrity 全部是实测哈希或真实存在的清单文件；不删除、不覆盖、不移动任何原有数据。

## 三、PLAN 减行与 STATUS 指针

- **PLAN**（目标 ≤63 行留余量，以检查器实测为准）：保留全部受引用治理事实（历史快照四条终态约束**不得删**），从 DAG 表终态节点合并取行：`FEA-14-EDIT-1 / FEA-14-AI-1` 合并一行（同依赖同终态）；FEA-11 系列再合并 1–2 行（如 SCAN-1/HOST-AUTH-1/LINEAGE-1 并行）；「当前活动程序」段两行并一行。proposed 节点用**合并行**（模拟中 `FEA-15-DIAG-ACL-1 / FEA-15-PIN-EOL-GOV-1` 一行写法正确，保留）。
- **STATUS**：删除「当前 Task：无」写法。终态 commit 时指针切为 `- 当前 Task：[FEA-15-DIAG-ACL-1](tasks/FEA-15-DIAG-ACL-1.md) **ready**（sandbox/export_hook/Host ACL 根因诊断；范围已冻结待认领）`——满足 `:192` 且唯一 Active 语义正确（ready≠Active，认领后才 in_progress）。

## 四、串行切换次序（每个 commit 点双门禁可过）

当前工作树四个未提交文件先按 Step 0 重整（模拟中的「指针悬空」「proposed 先行」是次序错误，回退重排）：

- **Step 0 → Commit 1（本卡 allowed_paths 内）**：①生成 `workspace-inventory.md` + 实测 `python.exe` SHA-256；②manifest 六行按第二节改写；③task 卡：AC5 翻 `[x]<<MET>>`、`resource_closeout_status: complete`、Closeout 追加（00:23 双跑 EXIT、limitation 三条、P3-A 27/30 修正、资源终态声明）、**status 保持 in_review**；④PLAN **只减行**（不加 proposed、不翻终态）；⑤STATUS 指针**恢复指本卡**（in_review 措辞）；⑥重跑 `task_ledger --write`。→ 跑默认 + `-TaskPath` 双 PASS → Commit 1 → 复跑确认。
- **Step 1 → Commit 2（治理 commit，超本卡 allowed_paths 属治理动作；授权=用户委任 + 本裁决；先例 `164ebabcf`）**：创建 `FEA-15-DIAG-ACL-1.md`（ready，冻结范围=前次裁决五项 scope + out_of_scope）与 `FEA-15-PIN-EOL-GOV-1.md`（proposed，§4.4 前置 + 盘点基数 30 中 27 含 SRC-25）；PLAN 加 proposed 合并行（Commit 1 腾出的预算内）；LEDGER 重跑；**STATUS 不动（仍指本卡 in_review）**——本卡未终态，指针合法；DIAG ready 未认领，不违反唯一 Active。→ 默认 check PASS → Commit 2。
- **Step 2 → Commit 3（本卡终态，⊆ allowed_paths）**：status → `closed_with_limitations`；PLAN 本卡行翻终态 +「当前活动」段改写 DIAG；STATUS 指针切 DIAG 卡 +「刚收口」行更新；LEDGER 重跑；Closeout 注明 integration_commit 由下一治理 commit 回填。→ 默认（指针解析到 DIAG 卡文件 ✓）+ `-TaskPath` 本卡（终态四查全绿：canonical complete ✓ resource complete ✓ AC 标记合法 ✓ `:749` 对 closed_with_limitations **允许**保留 `[ ]` AC ✓）双 PASS → Commit 3 → 复跑确认。
- **Commit 4（小治理）**：回填 `integration_commit` = Commit 3 hash（`17618c0fb` 回填先例），可并入 DIAG 认领 commit。

三原则：**减行先行、建卡先于指针切换、指针永不悬空**。CRLF/bytes 差异以检查器实测为准（跑至 PASS，行数留余量）。

## 五、边界重申

新卡创建走治理 commit（Commit 2），与本卡交付 diff（Commit 1/3 ⊆ allowed_paths）**物理分离**——任务释放权（用户委任本会话，范围已在裁决中冻结）与 Owner 交付范围不混淆；不触冻结契约、不动 `.gitattributes`、不清理任何文件、pins 18/18 维持。

---

**推荐下一步**：Codex 按 Step 0 重整工作树（撤「指针悬空」、manifest 六行、inventory 生成）后走 Commit 1→4。可转发指令：

```text
ZCode 补充裁决 2026-11-11（终态门禁修复）：模拟三失败均表述/次序问题，按序修复。Step0→Commit1（⊆ allowed_paths）：① Get-ChildItem -Recurse 生成 verification/FEA-15-ACCEPT-1/workspace-inventory.md（隔离根+clean-tree 递归清单：路径+大小+文件数，只读采集）并 Get-FileHash 实测 C:\Python314\python.exe SHA256；② manifest 改六行：隔离根/clean-tree 构建/clean-tree worktree= PRESERVE_*，destination=各自真实绝对路径，integrity=workspace-inventory.md；runtime ACL 拆两行（python.exe 行 integrity=实测 64hex；C:\Python314 目录行 integrity=python-acl-observation.log）；AppContainer profile 行改 NOT_APPLICABLE+result 写「无实例可核销（归属未证明）；保留不清理禁止撤销；记录见 python-acl-observation.log」；user-data 不动；③卡面 AC5 翻 [x]<<MET>>、resource_closeout_status: complete、Closeout 追加（00:23 双跑 EXIT/limitation 三条/P3-A 27 含 SRC-25/资源终态声明），status 保持 in_review；④PLAN 只减行至 ≤63（EDIT/AI 合并行、FEA-11 系列并 1-2 行、活动段压缩；历史快照四约束不删、不加 proposed）；⑤STATUS 指针恢复指本卡 in_review；⑥task_ledger --write。双门禁 PASS 后提交，复跑确认。Step1→Commit2（治理 commit）：创建 FEA-15-DIAG-ACL-1.md（ready；scope/out_of_scope 按 2026-11-11 最终裁决五项）与 FEA-15-PIN-EOL-GOV-1.md（proposed；§4.4 前置+基数 30 中 27 含 SRC-25）；PLAN 加两卡合并 proposed 行；LEDGER 重跑；STATUS 不动。默认 check PASS 后提交。Step2→Commit3（终态，⊆ allowed_paths）：status→closed_with_limitations；PLAN 本卡行翻终态+活动段改 DIAG；STATUS 指针切「- 当前 Task：[FEA-15-DIAG-ACL-1](tasks/FEA-15-DIAG-ACL-1.md) **ready**（诊断 sandbox/export_hook/Host ACL 根因；范围已冻结待认领）」+刚收口行更新；LEDGER 重跑；Closeout 注明 integration_commit 待回填。默认+-TaskPath 双 PASS 后提交、复跑确认。Commit4：回填 integration_commit=Commit3 hash（可并入 DIAG 认领 commit）。全程：指针任何 commit 不得悬空；不减受引用治理事实；不虚构资源路径；不清理不覆盖任何数据；不动冻结契约与 .gitattributes；不 push。行数/bytes 以检查器实测 PASS 为准。
```
