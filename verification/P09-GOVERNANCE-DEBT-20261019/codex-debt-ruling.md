# P09 收尾后的治理债逐类处置裁定

日期：2026-10-19  
身份：Codex / Lead / Architect / Integrator  
性质：治理规则裁定；不是交付 head 复审，不是对 300 个 Task 的逐项批准。  
适用范围：Owner 报告的当前 191 个错误行及其明确列出的治理债类别。事实计数沿用 Owner 的逐 Task 检查结果；本文件不把这些计数扩展为独立复核结论。

## 总规则与窗口

1. 机械改格式、修路径、补准确 pin 或补资源表之前，Owner（DSH）先逐项保全原值、当前值、依据和 Task ID；只在新建/释放的治理债清理 Task 与有效 Coordinator lease 下实施。当前 epoch 8 的 lease 不授权本次 Agent 写共享文件；本次只形成裁定。
2. Codex 保留状态、范围转移、Canonical Evidence 取舍、Resource Manifest disposition 和集成认定。Owner 不得以检查器错误、分支名、worktree 存在或“任务看起来已做完”代替这些裁定。用户保留产品范围、AC 删除/转移及改变既定目标的取舍。
3. “清理窗口”指新的治理债 Task 已明确 allowed_paths、Owner/Reviewer、基线和证据要求，Coordinator lease 有效后；“approved integration closeout window”另须满足协作协议 §4.2 的固定 delivery head、独立 Review、Codex 批准集成及集成后验证。只有后一窗口可执行已授权的物理资源处置。
4. 校验器 PASS 仅表示格式/路径/pin 条件满足，不证明内容真实、修改获授权或资源可删。任何不能达到下述判据的条目标为 BLOCKED，保留旧值和资源，不猜测。

## 1. Evidence SHA-256 不匹配（66 行 / 28 Task）

- **处置规则 / 判据：** 先比较当前文件 raw SHA-256、Task 原 pin、以及原 pin 对应来源的不可变版本（若为 Git，使用 pin 指向的 commit 中同路径文件；若为外部来源，使用当时的固定快照/收据）。三种 newline hash 都不匹配只证明字节不同，不证明谁对。只有证据链能说明“当前文件是后来经授权选作该 AC 的证据”（批准的内容变更/明确替换、对应来源版本及新 hash）时，判为“pin 过时”；否则判为“证据完整性未证实/文件被改动待查”，旧 pin 不得覆盖。LF/CRLF 归一化相等只可按既定格式惯例修正表示 pin，并记录原始值。
- **重钉授权：** Owner 提交每行的旧 pin、新 raw SHA-256、旧/新版本差异、含新文件的 commit 或快照来源及其授权/替代关系；Codex 对每个证据项确认其仍支持对应 AC 后，才可在获批清理 Task 中更新活动 pin。不能据此改写旧 Review 或把 FAIL 改成 PASS。
- **旧 pin：** 必须保留可审计的 SUPERSEDED 记录（Task 内简短变更记录或有 pin 的 adjudication 记录）：旧路径、旧 commit/hash、被替换的新 pin、原因和裁定者。Canonical Evidence 当前表只指当前证据；不要把不受支持的 SUPERSEDED 填作检查器不接受的 Evidence class。
- **执行者 / 窗口：** DSH 做逐项比对和证据整理；Codex 核准重钉；新治理债清理窗口。若要重新生成/修改证据内容，另走对应 Owner/Review 流程。
- **禁止：** 不得仅因当前磁盘 hash 可读、路径存在、三种行尾 hash 都不等于旧值，就把旧 pin 称为“过时”；不得覆盖唯一旧值、从当前未审查内容重钉、批量重钉或伪造历史 commit。

## 2. 当前 DAG 未登记非终态 Task（29 行 / 29 Task；含 READY 子类）

- **处置规则 / 判据：** 不得批量把 29 个 Task 登记进 DAG，也不得为消除错误批量改终态。DSH 为每项整理现状：Task 状态、当前 STATUS/Plan 是否引用、依赖是否满足、是否有用户授权的未完成目标、交付/集成事实。仍获授权且确需继续的非终态 Task 留在当前 DAG；仅因旧架构/旧目标已被正式取代，且替代依据可定位的，Codex 才可按 §4.1/状态定义裁定 historical 或 closed_with_limitations。proposed 仍未释放也必须符合 Plan 登记规则。READY Task 必须同时列在 READY 节点声明中。状态来源不明、用户目标取舍不清的，保持原状态并 BLOCKED，交用户决定，不伪造终态。
- **具体预算方案：** 当前限制是 tools/governance/check.ps1 中 doc/REBASELINE_PLAN.md 的 2500 bytes / 35 lines；Plan 当前 2332 bytes / 35 lines。为保留“Plan 是唯一 DAG”的约束，不把仍有效的任务藏入历史快照，也不以外部清单替代 DAG。下一治理文档维护窗口将该预算明确改为 **7000 bytes / 64 lines**（仅改该文件中对应的两个预算数值）；最多容纳原 35 行加 29 个紧凑 Task 行，READY 声明仍复用现有行。每个新增行只写 ID、依赖、状态/必要裁定，不复制背景散文。若 29 项审计后有终态，只登记仍非终态的子集；节余预算不构成释放任务授权。预算修改须在相应治理 Task 与有效 lease 下由 Codex 提案、用户确认防膨胀上限后实施。
- **执行者 / 窗口：** DSH 做逐项状态/依赖事实表；Codex 逐项裁定及改 Plan；涉及是否继续产品工作、是否撤销/替代 AC 的项由用户决定。仅在治理文档维护窗口扩预算。
- **禁止：** 不得只为通过检查把状态改为终态、把有效非终态放入 ## 历史快照、把 29 项合并成无法辨认状态/依赖的伪节点，或先提高上限再无差别登记全部 Task。

## 3. Canonical evidence 路径缺失（P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION，23 行）

- **处置规则 / 判据：** 现有事实不足以认定已集成：报告的 integration_commit 不是当前 HEAD 祖先且不含所列证据文件，证据仅见于该 Task 的 ZCode 分支，Task 文件本身在当前分支 untracked。将 integration_status: integrated 与这些事实记为冲突；在 Codex 找到可验证的集成提交（该提交为目标主线历史的一部分，且含准确证据文件）前，集成状态不得作为已证实事实，Task 不得仅因字段值认作 integrated/done。
- **路径选择：** 不把 G:\...workspace\worktrees\... 绝对路径当 Canonical Evidence（它不可移植且不满足版本化证据要求）；不擅自合并该分支，也不在当前主线补入 72 个文件。先由 DSH/Reviewer 对分支固定 head 和证据作事实清点；Codex 依 Plan/Task 授权决定是否启动正式 review 与 integration。若获批集成，在 approved integration window 中只集成审查通过、被 AC 引用的最小证据集合，随后以含文件的集成 commit 更新 pin；其余过程文件按资源规则处理。
- **执行者 / 窗口：** DSH 整理分支证据及准确 commit；独立 Reviewer 复核；Codex 纠正 integration 事实并决定是否释放/集成；只有 review 通过后的批准集成窗口才写主线。
- **禁止：** 不得改 pin 指向绝对 worktree 路径、不得将分支提交称为主线集成、不得因 72 个文件存在而全量补入、不得改写原 review 或跳过独立审查。

## 4. Resource manifest 不存在（20 行 / 14 Task；其中 11 个是未兑现占位符）

- **处置规则 / 判据：** 占位句“closeout 时复核后填写”不是 manifest，也不构成 closeout。DSH 对每个真实 worktree/resource 逐项记录 source、精确 disposition、当前最终路径、integrity manifest/hash、引用/进程检查和结果。worktree 当前仍存在且无删除授权时，默认 PRESERVE_UNKNOWN，destination 写实际存在的精确路径；只有确有引用证据才用 PRESERVE_REFERENCED，用户数据用 PRESERVE_USER_DATA。不能核实的保留并标限制。若资源确实不存在，须有可复核的不存在/已处置证据，不能写占位符冒充清单。
- **状态：** 不因补表本身回退 done。§4.2 明确允许资源保留而不阻止 DONE；当逐项保留 disposition、目标路径、integrity 和检查结果闭环后可保持 done。若发现此前实际未满足的 AC 或资源已被未经授权地删除，Codex 暂停终态认定并依新证据裁定恢复状态；不得把 closed_with_limitations 当一般补表状态，因其只适用于协议规定的用户裁决/目标替代情形。
- **执行者 / 窗口：** DSH 编制清单；Codex 按 §4.2 作 disposition 裁定。涉及 worktree 的任何移除，先重读当前 Worktree Safety Inventory、逐项检查 clean/untracked/独有 commit/进程和引用，并仅在 approved integration closeout window 用普通 git worktree remove。不能证明删除条件的就保留，不为完成表格而做物理 closeout。
- **禁止：** 不得将文字占位符视作 manifest，不得仅依据 2026-10-13 快照删除或迁移 worktree，不得用 DELETE_SAFE 代替未知，不得把存在资源等同于必须删除，不得使用 --force 或 git worktree prune。

## 5. DONE evidence_dir 含未登记文件（13 行 / 13 Task）

- **处置规则 / 判据：** evidence_dir 只容纳当前有判别力、支持已释放 AC/Gate 的版本化证据；每个留存文件须在 Canonical Evidence 表中逐项登记并标 CANONICAL（直接验收结果）或 SOURCE_PIN（不可变来源/支撑输入），绑定 AC/Gate 与有效 commit/hash。审查记录可登记为其所评审 head 的证据；测试日志只有含可复核命令/环境/退出码且被 AC 引用时才作为证据。未支持某一 AC 的重复尝试日志、临时 stdout/stderr、checkpoint 和恢复过程记录属于过程产物，留在 workspace 的 Task agent-output/checkpoint 位置；不占 evidence_dir。gitattributes / gitignore 是仓库配置而非验收证据，不能因出现在目录就合法化为 evidence；须由有权 Owner 在独立授权路径中处理，不能在本次只读裁定中移动。
- **执行者 / 窗口：** DSH 逐文件分类并提出绑定 AC/Gate；Codex 决定证据类别和是否仍具判别力；经授权的清理 Task 才可迁出过程文件，涉及跨目录/仓外资源时依 §4.2 及 Safety Inventory。
- **禁止：** 不得把目录整体登记成一条 Evidence、不得把所有未登记文件一律标 SOURCE_PIN、不得删除/移动未知或有独有修改的文件、不得把配置文件伪装成 AC 证据。

## 6. DONE 保留未勾选 Acceptance Criteria（11 行 / 11 Task）

- **处置规则 / 判据：** done 要求所有已释放 AC 有实际通过证据；- [ ] 与 done 不兼容。逐项只有两种合法修复：①AC 实际已通过且有证据，则 Owner 补证、Codex核准后将该项勾选；②该项被有效范围裁决转移/取消/替代，则先取得该范围变更授权，保留原 AC 文本及原始未完成状态的审计记录，并在 Task 明确写 successor Task/用户裁决/替代依据；从活动 Acceptance Criteria 移出该项后，Task 状态是否仍为 done 由 Codex按余下所有已释放 AC 和集成/closeout事实核准。单纯在备注写“已转出”但仍留 - [ ] 不能过检查，也不能算完成。
- **用户裁决：** 若移除/转移改变用户要求的产品行为或验收范围，必须由用户裁定；Codex/Owner 无权把未完成 AC 改成 PASS。无此裁决时保持未完成事实并阻止 DONE。
- **执行者 / 窗口：** DSH提供每条 AC 的原始来源、证据或转移提案；用户决定产品范围变化；Codex核准 AC/状态记录。只在已授权 Task 的范围/状态维护窗口修改。
- **禁止：** 不得放宽检查器使 done + [ ] 通过、不得虚勾、不得删掉原始未完成记录、不得以 closed_with_limitations 自动替代（除非符合该状态定义且有对应授权）。

## 7. 其余较小类别（27 行；并含 Owner 停止的三类）

- **7a DONE 缺少 Resource Manifest（7 Task，worktree 均残留）：** 确认 Owner 停止自动处置。DSH 在治理清理 Task 中先逐资源盘点；Codex 按 §4.2 给 disposition。尚未核实的 worktree 默认 PRESERVE_UNKNOWN、destination 为精确存在路径、integrity 引用可复核 manifest；不得因 manifest 缺失删除 worktree。需删除时先重读当前 Safety Inventory 并满足第 4 节条件。已完成 Task 不因“补上 manifest 表格”本身回退，只要资源收口真实闭环。
- **7b 无效 Resource disposition（P02-NEW-TIME-X6-BUILD-CARGO，4 行）：** 确认 Owner 停止自动修。必须整行重写 source、disposition、destination、integrity、result，不能只换枚举。source 写真实路径；destination 写最终实际存在路径（同源保留写该路径，不写 same）；提供本次收口的有效文件 manifest/hash 和引用/进程检查。默认未查明构建缓存用 PRESERVE_UNKNOWN；确认仍有引用时 PRESERVE_REFERENCED。DELETED_EXACT_PROBE_ONLY 不是允许 disposition；已删除仅在确有删除收据时按真实终态记录，不得由本裁定授权删除。
- **7c 失效本地引用（7）：** 目标在仓库与 workspace 均不存在时，不可凭相似文件名替换。DSH 找原始产物/commit/Task 引用；找到相同内容且来源一致才由 Codex批准改链并保留旧目标记录为失效引用。找不到时标为证据缺失/BLOCKED，Codex adjudication 记录失效，不得声称证据已恢复。
- **7d READY / DAG 不一致（4）：** 与第 2 节同一裁定。READY Task 只有在当前授权且依赖满足时保留 ready，同时列入 Plan 的 READY 声明；否则 Codex 依证据裁为适当状态。不得只在 Plan 文字加 ID 而不核实任务依赖/授权。
- **7e Evidence class 无效（2）：** 在未集成分支 Task 上，先确定其是否可作为当前支持 AC 的证据。只允许 CANONICAL 或 SOURCE_PIN；未审查分支中的证据在完成独立审查/集成前不能标 CANONICAL。不得借换 class 掩盖路径或集成缺失；按第 3 节处理。
- **7f Resource SHA-256 指向 DSH 用户可变文件（1）：** C:/Users/49745/.dsh/storages/workspace.json 是会变化的用户态状态，不可作为稳定 pin。删除该活动 pin 前，先确认它并非 AC 唯一原始输入。若 AC 需要它，需由授权任务产生不包含秘密/不必要个人数据的固定、最小化且经批准快照，并对快照重新取 raw SHA-256；否则记录其非不变量、将该项标为不适用/缺证须由 Codex依 AC 判定。不得复制/公开整个 DSH 用户目录或以当前 hash 冻结持续变化文件。
- **7g 缺 resource_closeout_status / canonical_evidence_status（各 1）：** 按第 4 节逐项收口资源、按 §4.1 完成当前证据后再填写 complete。字段不能替代证据；终态不满足实质条件时由 Codex先裁定真实状态。不得为消警报直接填 complete。
- **执行者 / 窗口：** DSH 汇总事实并提出逐项修复；Codex裁 disposition、引用和状态；独立 Reviewer 按清理 Task 约定检查证据。涉及产品范围/AC 的不确定项交用户。
- **禁止：** 不得把本节裁定解读为任一资源的删除、移动、归档、合并或分支集成授权。

## Owner 已停止的三项

1. DONE evidence_dir 含未登记文件：**确认**停止自动修。须逐文件绑定 AC/class，且过程文件有的应离开 evidence_dir；按第 5 节由 DSH 提案、Codex裁决。
2. DONE 必须逐项填写 Resource Manifest：**确认**停止自动 disposition。依据 §4.2 disposition 属 Codex 权限；按第 7a 节先盘点再裁定。
3. Resource disposition 无效四行：**确认**停止只替换枚举。source/destination/disposition 必须整行由事实重建；按第 7b 节处理。

## 必须交用户裁决的事项

- 对任一未完成 AC 的取消、转移、替代，若改变用户要求的产品行为/验收范围。
- 29 个非终态 Task 中，证据不足以判定为继续、取消或被目标替代的范围/优先级选择。
- 将 Plan 防膨胀预算提高到 7000 bytes / 64 lines；这是对现行治理检查上限的政策变更，须用户确认后再按专门治理 Task 落盘。
- 要求冻结、共享或以其他方式处理含个人/秘密内容的 DSH 用户态配置快照时。

除此之外，是否重钉 pin、是否确认某个资源保留、是否有证据可支持既有 AC、以及某个集成事实是否成立，按本文件判据由 Codex在授权范围内裁决；不需要把每个机械事实再次交用户。

## 本轮工作区边界

本文件由 Codex在用户明确授权的唯一目标路径创建。写入前后分别执行 git status --porcelain；写入后除本文件外状态必须与写入前逐字相同。本轮不运行 AC probe，不执行 Git 写操作，不移动/删除仓外文件，不修改任何 Task、Plan、STATUS、检查器或其他 verification 文件。
