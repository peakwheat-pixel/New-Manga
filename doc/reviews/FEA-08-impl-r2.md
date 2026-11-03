---
task_id: FEA-08
reviewer: "Codex 独立复核会话 01a19f56-a013-7511-bf1c-6baabd8d88c3（/root；用户本轮指定；未参与实现、scope 或 R2 返修）"
reviewer_kind: agent
author: "ZCode R2 session + DSH Integrator 收口"
base_commit: 2870a9fa5
reviewed_head: c583454e0fcea471a41ad73db9aabbb8261949c9
implementation_commit: 7b176be6a
decision: changes_requested
verdict: changes_requested
p0: 0
p1: 3
p2: 4
provenance:
  head_delta: "0；开始、实跑后及报告定稿时 HEAD 均为 c583454e0；main；Git common directory=.git"
  reviewer_sources:
    - "主审：Codex 会话 01a19f56-a013-7511-bf1c-6baabd8d88c3"
    - "Standards：/root/standards，独立上下文 Reviewer，会话 01a19f57-55fe-79c0-a577-2b36448854dd；只读"
    - "Spec：/root/spec，独立上下文 Reviewer，会话 01a19f57-82f1-7e43-8acb-61d27d4c1ce8；只读仓库；仅写隔离合成探针"
  delivery_delta: "7b176be6a..reviewed_head 并非证据完全不变：00a6c8579 更新 prototype_hashes.txt 的 pin_selfcheck.py 指纹，并新增 gates.log；c583454e0 新增 pin-verify.log。详见 F08I2-001。"
  workspace_evidence: "G:/CODEX/New Manga.workspace/FEA-08/impl-r2-review-codex-20261103-1056"
  uncovered:
    - "原始 run_all.py 全链未执行：其硬编码仓库目标，会改写 Canonical Evidence；本轮仅运行隔离 H4/H5/H6、verify_results 及隔离 staging 失败注入。"
    - "USB/SMB/云真实卷、交互取消、IFileOperation sink 未实跑；维持原有限制，未升级为 MET。"
    - "无生产 Source/数据库/UI 实现验收；本 Task 为隔离原型。"
---

# FEA-08 impl-r2 独立 Review

## 1. 结论

**changes_requested，P0=0 / P1=3 / P2=4。** F08I1-001 的 folder fixtures 缺口已闭合，H5 三连跑稳定；产品回归门禁全部达到基线。但 F08I1-002 的 commit pin 仍有 1 项断链，自校验错误地把 index 当成指定 commit；新增 H6 尺寸与 occurrence 唯一性反例均返回错误的 `exact_match`，故 AC-3/AC-4 不支持完整 `<<MET>>`。P0/P1 未解决前不能交 DSH 以 approved 集成或关闭。

实测：build **0 warning / 0 error**；无过滤 test **1292 passed / 0 failed / 57 skipped**；check **PASS(3)**；冻结 pins **15/15**；FEA-06 四 PNG 不变。仓库内仅新增本报告，未 commit、未 push。

## 2. 审查范围与依据

固定 base=`2870a9fa5`，reviewed_head=`c583454e0`，R2 交付=`7b176be6a`。读取 Task 全部冻结 AC/52 项 EV、research 报告、impl-r2 Handoff、impl-r1 Review、checkpoint §166/167、`.gitattributes`、入库 evidence 和 workspace 15 脚本；核对 scope-r2 的 LIMITED 授权。架构依据为 AD-002（含 AD-003 更新说明）、Task 引用的 AD-003/ADJ-001 边界、协作协议 §4/§5.1/§6 与 Review 模板。

执行 `git diff 2870a9fa5...HEAD` 及 `git log 2870a9fa5..HEAD --oneline`，再按 R1 实现、R2 实现、治理登记分层检查；没有把历史 FEA 线改动算成 R2 越界。本 base 到 reviewed_head 的 `src apps experiments tests packaging scripts tools` 本身就是空 diff。

下文 `P/` 指 `G:/CODEX/New Manga.workspace/FEA-08/prototype/`；`R/` 指 provenance 的本次隔离证据目录。脚本行号按当前 15/15 指纹一致的文件。所有复跑来自脚本隔离副本，H6 fixtures 只从入库目录复制；不依赖原 `workspace/FEA-08/tmp`。

## 3. Standards（executed）

- **写域 PASS**：`7b176be6a` 的 38 个变更仅在 `verification/FEA-08/**` 与 research 报告；`07724b88d` 仅 `.gitattributes`，有 checkpoint §166 的 DSH 集成裁决；其余治理提交无产品改动。`00a6c8579` 确实额外更新了脚本指纹证据，不能笼统称“只有登记文档变化”。
- **证据纪律 FAIL**：协作协议 §4.1 的 commit/path/SHA 链在 EV-F08-43 断裂（001）；§6 第12条要求完整运行日志、EXIT、shell/解释器及逐项 skip 原因，入库 gates 仅摘要（007）。
- **失败隔离 PARTIAL**：全链 staging 先破坏原 Canonical fixtures，后续失败留下新输入/旧成功结果（006）。
- **安全 PASS（本轮执行范围）**：全仓 tracked 文本搜索命中仅文档/证据，源代码无清空类 API；prototype 命中仅注释/说明字符串，无调用。H5 只回收本轮隔离 lab 自建路径，三轮均还原后清理。G: 始终 0 项/0 字节。没有真实库、用户源文件或真实回收站条目的修改。
- 未把 Fowler smell 启发式计为硬性违规；本轮 findings 均为可复现行为或证据规则问题。

## 4. Spec（executed）

### 4.1 逐 AC 核验

| AC | 独立实证 | 判断 |
|---|---|---|
| AC-1 H4 | 隔离复跑 10 场景：7 complete_old_digest、S4 unavailable、S5a/S5b undetected_mixed；S5 评估 outcome=unavailable、protocol=digest_returned、risk=true、consistent=true；strict-only 硬约束在报告/summary 明示 | **限定 strict 能力成立**；tolerant+mmap 必须维持 UNAVAILABLE。矩阵校验器仍漏必要断言（005），不能把研究结论当成生产实现已保证 |
| AC-2 H5 | 3 次独立运行，每次 9 PASS + R7/R8 2 LIMITED(mocked)，R2/R9 poll=0、timed_out=false；5 条还原日志、G: 0→0、lab leftover=0；失败注入得到非零退出，二层 verdict 校验拒绝 R2 FAIL | **measured 主链 PASS，限定范围接受**。R3 不可回收分支仅 LIMITED(mocked)，R7/R8 仍 LIMITED；没有将这些子项升级 MET；符合 scope-r2 接受无硬件 LIMITED 的边界 |
| AC-3 H6 | 33 内容 fixture 双 manifest SHA 33/33；入库复制复跑 17 条，与 Canonical 每条结果内容完全相同；M8M9 可复现；另两项真实合成反例返回误 exact | **PARTIAL**，受 002/003 阻断；Task 当前完整 MET 不成立 |
| AC-4 完整交付 | 60 格 current/needed 全具备，状态计数一致；52/52 文件有 EV；工作树 hash 52/52；指定 commit blob 49/50 + SHA-only 2/2；15/15 脚本匹配；非 NTFS evidence 分类被污染 | **PARTIAL**，001/004/005/006/007；完整 MET 不成立。接受研究报告如实登记 LIMITED，不等于这些能力已 measured PASS |

### 4.2 impl-r1 各 finding 逐项核验

| 原 finding | 核验与复现证据 | 处置结论 |
|---|---|---|
| F08I1-001 P1 | `folder_v1/p1,p2,p3.png`、`folder_v2/p1,p2renamed,p4.png` 六文件实际在库；manifest/evidence_manifest 均逐文件 SHA 33/33；复制入 R/lab/evidence/fixtures，运行 `python -B R/lab/prototype/h6_run.py --fixtures R/lab/evidence/fixtures`；M8M9=`needs_confirmation`、digest_type=`folder_membership+bytes_sha256`，3→3 成员 | **FIXED**；不依赖原 workspace tmp。Canonical fixtures_root 指入库目录，独立复跑指向其逐字节一致副本（cli --fixtures），两个 manifest 指针均实际存在 |
| F08I1-002 P1 | 全部52行独立取原始 `git cat-file -p commit:path` 字节；EV43失败，其余49个commit pin通过；两个SHA-only通过；Get-FileHash52/52；core.autocrlf=true干净导出当前HEAD52/52，但按交付commit导出49/50 | **NOT CLOSED** →001。LF/CRLF旧问题已消除，新的commit指针漏报仍阻断 |
| F08I1-003 P2 | Canonical与隔离H4的S5a/S5b字段均为risk=true/protocol=digest_returned/评估unavailable/classification=undetected_mixed/consistent=true；NTFS单图H4双态；报告§3.3/summary strict-only | **FIXED（限定 strict）** |
| F08I1-004 P2 | 两份H4 S2均`blocked(win32=32)`；S5读前/读后真实FileIdentity均存在，mtime_100ns相等，`mtime_changed=false`为实测盲区；S4为true；报告表述与结果相符 | **FIXED** |
| F08I1-005 P2 | R2/R9有界poll代码及字段在；3次H5各9 PASS、R2/R9均0次等待且未超时；AST只替换run()输出为R2 FAIL，真实CLI尾部门禁EXIT=1；隔离verify_results阳性对照PASS，单改R2 verdict后抛`verify_results FAILED (1 errors)` | **FIXED**；并非只看进程返回码。R/harness-probes/h5-injected.log、verdict-failure.txt |
| F08I1-006 P2 | R6b destructive execute前4、execute后5、recovery后5；R5b实测directory/0x10、目录file handle被拒32以外的win32=5、类型变化后拒绝且零destructive；R3 measured可回收，ret0x79注入返回keep_at_origin/fallback_rmdir_used=false，子分支明确LIMITED | **FIXED**；三次H5同样结果；没有声称mock不可回收分支已真实触发 |
| F08I1-007 P2 | M12独立构造两路径、candidate且self-read单列；M13两份不同ZipCrypto密文带密exact；M15两份不同加密PDF带密渲染exact；comparison_mode在；AES ZIP error与LIMITED(pyzipper)均在；M17=10 candidate/M18=11 no_match独立复现 | **原列举返修项 FIXED**；不覆盖新反例002/003，AC-3整体仍PARTIAL |
| F08I1-008 P2 | 60格都有current/needed；NTFS状态确由derive_ntfs消费结果；7个格式无关H4/H5格标LIMITED(inferred)；但非NTFS继承错误evidence，且derive缺必要断言 | **PARTIAL** →004/005 |
| F08I1-009 P2 | Task实际存在门禁表；build/test/check/pins/四PNG/禁止diff数值与本轮一致。gates.log是历史快照，pin自校验51/51仅index口径，不能当commit pin审计 | **记录存在性 FIXED，证据纪律PARTIAL** →001/007；未把快照当实时日志 |
| F08I1-010 P2 | 原workspace/FEA-08/tmp实际空；run_all_log tmp_removed=[fixtures,h4_lab]、tmp_remaining=[]；本轮H5各轮lab/tmp也空 | **FIXED（当前成功交付）**；全链失败时清理/发布另见006 |
| F08I1-011 P2 | Canonical h6 fixtures_manifest=`G:/CODEX/New Manga/verification/FEA-08/results/fixtures_manifest.json`存在；副本布局含同名results manifest，复跑解析成功；15脚本实数，5核心步骤=make_fixtures/H4/H5/H6/matrix，另重复生成、staging、verify、pin不混计 | **FIXED**；“51项”旧叙述是加入pin-verify前口径，现为52 EV、校验日志排除自身后51 |

## 5. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| F08I2-001 | **P1** | `doc/tasks/FEA-08.md:136` EV43；`P/pin_selfcheck.py:60,113`；`verification/FEA-08/logs/pin-verify.log:64` | 解析EV时丢弃commit，只检index。00a6c8579已更改prototype_hashes.txt，却仍pin到7b176be6a；自校验51/51掩盖实际断链，AC-4不完整 | 原始blob SHA=`58a54329a295c8b6ecd4065181c443dac26a5a18f4f2810b2f0c756b7d385b86`；登记/当前工作树SHA=`3336a7b45923af469b094d5aec045250e0a2b8d5152a6203ef2a86c9372cabca`。`git diff 7b176be6a..HEAD -- verification/FEA-08/prototype_hashes.txt`显示pin_selfcheck指纹20f10d…→7198fa…；交付commit checkout也失败 | EV43指向含当前字节的真实commit（如00a6c8579）；校验器逐项读取commit:path，明确区分提交前index候选与已登记commit证明；重出日志和pin | open |
| F08I2-002 | **P1** | `P/h6_run.py:58-65`；research §5.3；Task AC-3 | 规范像素只比原始RGB字节，尺寸只展示。相同像素数、不同形状的图片会误exact，违反尺寸/方向精确条件，后续据此迁移人工内容会错页/错坐标 | 真实PNG：RGB(50,80,110)，A=2×6、B=3×4；match_single_image返回exact_match/canonical_pixel_sha256，同时size_a=[2,6]/size_b=[3,4]。R/spec-probes/probe.py、probe_results.json | 规范化函数返回并比较EXIF变换后的尺寸/像素；digest语义绑定尺寸与规范色彩表示；加邻界fixture并重出H6证据，未闭合前AC-3降PARTIAL | open |
| F08I2-003 | **P1** | `P/h6_run.py:128-150`；提案`:457`；Task AC-3 | 容器只比较内容digest多重集，仅同名不同内容时降candidate；不同名的重复同图没有唯一旧→新occurrence，仍误exact，违反“一对多默认需确认” | 真实ZIP A含a.png/b.png，B含c.png/d.png，4项均为同一PNG；match_container返回exact_match、multiset_equal=true、duplicate_names=[]。R/spec-probes/probe_results.json | 保留成员身份/ordinal，构造唯一一对一映射；重复内容但无法唯一定位时只给candidate/needs_confirmation，不能仅Counter相等；加入真实容器反例 | open |
| F08I2-004 | P2 | `P/matrix.py:163-197`；`verification/FEA-08/results/capability_matrix.json:145,266,387`等 | 非NTFS分支没有重设h4_ev/h5_ev/h6_ev，继承上一NTFS PDF迭代的inferred/inferred/measured。15个未测卷H6格标measured；USB/SMB的20个H4/H5格status=mocked而evidence=inferred，违反逐格来源纪律 | JSON实数：NTFS measured8/inferred7；USB、SMB、Cloud每行measured5/inferred10；无硬件卷H6共15格measured，note却称无法measured；60格status计数仍正确，故计数掩盖错误 | 每个卷分支明确赋三项evidence；逐格检查status/evidence/current一致；重出JSON/MD，MD应能读到H4/H5/H6各自来源 | open |
| F08I2-005 | P2 | `P/matrix.py:23-27,54-59` | 推导只看部分顶层classification/result，漏strict拦截断言及M3/M5/M7/M16等必要证据，无法兑现“任一底层场景失败即降级” | 隔离副本仅将S5c拦截断言=false/writer=opened，M16 result=error且蓝帧反证=false，derive_ntfs仍h4_pass=true、h6单图=true。R/spec-probes/matrix_probe.py、matrix_mutation_results.json。当前正常结果未因此误报；run_all会挡M16顶层error，但也不检S5c拦截断言 | 按固定必需场景集合与语义断言校验strict blocked/old digest、GIF反证、尺寸/唯一性等；矩阵与总驱动共享判据或交叉核验，失败降级 | open |
| F08I2-006 | P2 | `P/run_all.py:68-81,180-203,223-231` | H4/H5/H6及verdict之前删除旧Canonical fixtures并改写manifest；后续失败无回滚/失败批次标记，旧h*_results及EXIT=0日志仍在，形成新输入+旧PASS；tmp也只在成功尾部清理 | 在R/harness-probes/fake-repo中调用真实stage_fixtures/main，注入H4非零：old.bin被new.bin取代，而h4_results保留old PASS、run_all.log保留EXIT=0。无真实H4/H5调用，未写仓库。staging_failure.json | 全批次先在workspace构建、验证后统一晋升；失败保留上一完整Canonical集，失败日志单独记录；清理用finally且不得误删待还原回收条目 | open |
| F08I2-007 | P2 | `verification/FEA-08/logs/gates.log:3,7-21`；Task`:147`；协作协议§6第12条 | Task称gates.log为原始输出，文件却明确把原始输出放非Git r2-gates-raw.log；入库仅摘要/程序集总数，缺shell/解释器路径及57个skip逐项来源原因，不满足版本化运行证据要求 | gates.log全文50行；第3行指向workspace原始日志，build/test仅EXIT与统计。独立实跑数值吻合，但不能回填成原交付日志已入库 | 将完整脱敏原始输出连同shell/解释器/EXIT、逐项skip原因纳入证据并登记；gates摘要继续明确快照；新一轮实际运行单独留档 | open |

## 6. 验证

审查运行环境：Windows / pwsh（`C:/Program Files/PowerShell/7/pwsh.exe`）、Python `C:/Python314/python.exe` 3.14.6、.NET SDK 10.0.401；HEAD 全程 c583454e0。`R/` 中保存逐轮原始日志，报告为唯一仓库写入；附录保留足以判别的新反例输出。这里不把仓外日志冒充已版本化的原交付证据。

| 场景 | 实际命令/步骤 | head | 结果 | 证据 |
|---|---|---|---|---|
| 固定点/工作区 | git rev-parse HEAD；git branch --show-current；git rev-parse --git-common-dir；git status --porcelain=v1 | c583454e0 | main/.git；开始clean；结束仅本报告untracked | R/status-before.txt；本报告定稿检查 |
| build | `dotnet build apps/desktop-avalonia/NewManga.sln --nologo` | 同上 | PASS，EXIT=0，0w/0e | R/build.log |
| 无过滤全量test | `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings --nologo` | 同上 | PASS，EXIT=0，1292/0/57；八程序集21/38/51/253/117/31/128/653，skip0/0/28/0/0/0/22/7 | R/test.log；逐项skip见附录C |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1` | 同上 | PASS，EXIT=0，3warnings（9非终态Task、STATUS预算80%、PLAN预算80%） | R/governance.log；报告落盘后同命令再验 |
| 冻结pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 同上 | PASS，EXIT=0，all15 | R/freeze-pins.log |
| FEA-06四PNG | Get-FileHash verification/FEA-06/screens/*.png -Algorithm SHA256 | 同上 | PASS，四SHA全等，见下 | 命令输出/附录B |
| 产品路径diff | git diff --name-only 2870a9fa5..HEAD -- src apps experiments tests packaging scripts tools | 同上 | PASS，空；R2产品改动0 | 实测空输出；R2 38文件及登记commit逐层检查 |
| EV指定commit原始字节 | subprocess.check_output([git,cat-file,-p,commit:path])→hashlib.sha256；避免PowerShell文本管道转码 | 同上 | **FAIL：49/50 commit pin；2/2 SHA-only；合计51/52** | R/pins.json；附录A逐项 |
| 工作树Get-FileHash | 解析52 EV→每路径Get-FileHash SHA256与表比较 | 同上 | PASS，52/52 | R/get-filehash.json |
| 干净checkout | 隔离GIT_INDEX_FILE，git read-tree HEAD或7b176be6a；git -c core.autocrlf=true checkout-index -f --prefix=R/checkout-*/ -- files | 同上 | HEAD52/52；**delivery49/50**；2个SHA-only按HEAD字节核对；不移动真实HEAD/index | R/checkout-index、checkout-delivery；001 |
| EV覆盖与自引用 | 枚举verification/FEA-08全文件对EV集合；pin-verify.log单独SHA | 同上 | 52文件/52 EV，missing/unregistered=0；自校验排除自身合理，但不能借此忽略其他行commit | R/pins.json；附录A |
| manifests/脚本 | 双manifest逐文件SHA；prototype_hashes.txt对15实际.py重算 | 同上 | 33/33 + 33/33；15/15；deterministic22/33 | R/pins.json；实际文件内容 |
| H6入库复跑 | 复制入库fixtures+results/fixtures_manifest到lab/evidence；python -B R/lab/prototype/h6_run.py --fixtures R/lab/evidence/fixtures | 同上 | PASS（既有17场景），EXIT=0，17条result完整与Canonical相同；M8M9成立 | R/h6.log、lab/out/h6_results.json |
| H4隔离复跑 | python -B R/lab/prototype/h4_run.py | 同上 | PASS（分类及字段），EXIT=0，10场景 | R/h4.log、lab/out/h4_results.json |
| H5三连跑 | python -B R/lab/prototype/h5_run.py ×3；每轮留JSON/日志且查询G:计数 | 同上 | PASS，3次EXIT=0，每次9 PASS/2 LIMITED，R2/R9均无timeout；每轮bin0/0→0/0、leftover0、tmp空 | R/h5-1..3.log、h5-1..3.json |
| H5失败传播 | 只在隔离AST中替换run()输出为R2 FAIL后执行真实__main__尾部；verify_results阳性/阴性对照 | 同上 | PASS：CLI EXIT=1；总驱动阳性对照通过，单R2FAIL触发1error | R/harness-probes/h5-injected.log、verdict-failure.txt |
| H6新反例 | python -B R/spec-probes/probe.py（真实PNG/ZIP，纯合成文件） | 同上 | **FAIL：两项错误exact**；预映射H4探针strict-open被32拒绝，无额外H4finding | R/spec-probes/probe_results.json；002/003 |
| matrix负控 | python -B R/spec-probes/matrix_probe.py；读Canonical60格 | 同上 | **FAIL**：遗漏断言仍PASS；非NTFS evidence污染 | R/spec-probes/matrix_mutation_results.json；004/005 |
| staging负控 | 重定向run_all所有目标至fake-repo；make_fixtures/stage_evidence替身；真实stage_fixtures，H4失败注入 | 同上 | **FAIL**：新输入与旧PASS并存；本轮未碰真正Canonical | R/harness-probes/staging_failure.json |
| 安全/临时数据 | 全仓git grep与prototype检索清空API；G:只读bin_count；检查原tmp与隔离tmp | 同上 | PASS：清空调用0；G:0→0；H5零残留；原tmp空，隔离H4 lab已按绝对路径清理 | R/empty-api-search.txt、三轮H5JSON |
| 原始全链重跑 | 未执行真实run_all（会写仓库） | 同上 | **NOT_RUN（边界限制）**；以隔离分模块/门禁/负控核验，无全链EXIT=0冒称 | provenance |
| 未push | git branch -r --contains 7b176be6a；本会话无push命令 | 同上 | PASS，无remote ref包含交付commit | 空输出 |

## 7. Architecture

**隔离原型边界 PASS，能力结论 PARTIAL。** 没有修改 Avalonia/Host/Core/DB/schema/共享契约/生产依赖；未把旧Tauri/QML当成实现路线。H4 strict-only、H5合成回收和receipt事实恢复符合本Task边界。AES ZIP无读取支持、USB/SMB/云无硬件、R3/R7/R8等限制必须保持LIMITED/UNAVAILABLE。PyMuPDF仅研究用途、pdfium生产候选和pyzipper未引入的登记未被本轮扩大成生产依赖授权。

H6 002/003 涉及后续 Source binding 和人工修改迁移的可信基础，不能因当前仅原型就降低为文字建议；应先修正研究判据及证据，再由DSH决定如何传递至FEA-09+。本报告不裁决任何生产契约或Schema变化。

## 8. Verification 结论

- **产品回归层 PASS**：build/test/check/冻结pins/四PNG/禁止路径均达到要求；57skip保持原原因，没有当成通过。
- **旧缺口修复层 PARTIAL**：folder入库闭合；H4字段、H5稳定性/失败传播/实测计数、H6独立副本/阈值/指针和当前tmp清理成立；commit pin与矩阵仍未完整闭合。
- **新增判别层 FAIL**：两项H6反例误exact；staging失败会遗留混合证据；完整门禁原始输出未版本化。
- 因此 Task 的AC-3/AC-4完整MET应由DSH处置为PARTIAL或返修后再恢复，不能由Reviewer越权改Task。所有LIMITED子项维持限制，不以研究原型“已做”替换能力证据。

## 9. 复审与下一步

推荐下一步由 **DSH** 按本报告处置001—007并冻结FEA-08返修范围，优先修001/002/003；随后由 **ZCode** 承担同Task返修，或由DSH重新分配协作Agent。当前不关闭FEA-08，不释放FEA-09实施，不push。Review切片完成不等于Task done。

可直接转发给DSH/下一Owner的指令：

> Task=FEA-08 impl-r2 findings disposition / 下一轮返修；工作路径=G:/CODEX/New Manga，branch=main，worktree=同路径；恢复点base=2870a9fa5、reviewed_head=c583454e0，报告doc/reviews/FEA-08-impl-r2.md，原型G:/CODEX/New Manga.workspace/FEA-08/prototype。DSH先裁定F08I2-001…007并登记新scope/base/head/Owner/Reviewer，再交ZCode返修。允许范围沿Task的research/handoff/evidence/workspace原型；Task与治理登记由DSH负责；禁止改src/apps/experiments/tests/packaging/scripts/tools、共享契约/Schema/依赖与真实用户文件，.gitattributes若需再次调整须DSH单独授权。交付修正的逐commit pin校验、H6尺寸/一对多golden反例、矩阵来源/负控、失败不污染Canonical的全链、完整门禁日志与逐项skip、Handoff及新固定证据commit。验证build0w/0e、无过滤test至少1292 passed/0 failed并保留57skip来源、check PASS(3)、冻结pins15/15、四PNG不变、产品路径diff0、H5隔离三连跑及G:0→0、全部EV按指定commit/工作树/core.autocrlf=true干净checkout一致；Review须新独立上下文。未过P0/P1与DSH集成验证不得done；不push。本指令为建议，不自动释放新Task。

## 附录A：52项Canonical逐项核验

Blob列按表中commit原始字节；`—`表示Task明确采用工作树SHA-only。WT=Get-FileHash；HEAD/delivery clean=core.autocrlf=true的隔离checkout。复现原始blob不能经PowerShell文本重编码；例如Python `hashlib.sha256(subprocess.check_output(['git','cat-file','-p','7b176be6a:verification/FEA-08/prototype_hashes.txt'])).hexdigest()`。

| EV | 路径（verification/FEA-08/下） | commit blob | WT | clean HEAD | clean delivery |
|---|---|---|---|---|---|
| EV-F08-01 | fixtures/anim.gif | PASS | PASS | PASS | PASS |
| EV-F08-02 | fixtures/book_dup.zip | PASS | PASS | PASS | PASS |
| EV-F08-03 | fixtures/book_dup_copy.zip | PASS | PASS | PASS | PASS |
| EV-F08-04 | fixtures/book_enc_aes.zip | PASS | PASS | PASS | PASS |
| EV-F08-05 | fixtures/book_enc_zipcrypto.zip | PASS | PASS | PASS | PASS |
| EV-F08-06 | fixtures/book_enc_zipcrypto_copy.zip | PASS | PASS | PASS | PASS |
| EV-F08-07 | fixtures/book_v1.cbz | PASS | PASS | PASS | PASS |
| EV-F08-08 | fixtures/book_v1.zip | PASS | PASS | PASS | PASS |
| EV-F08-09 | fixtures/book_v1_recompressed.zip | PASS | PASS | PASS | PASS |
| EV-F08-10 | fixtures/doc_enc.pdf | PASS | PASS | PASS | PASS |
| EV-F08-11 | fixtures/doc_enc_copy.pdf | PASS | PASS | PASS | PASS |
| EV-F08-12 | fixtures/doc_v1.pdf | PASS | PASS | PASS | PASS |
| EV-F08-13 | fixtures/doc_v1_regen.pdf | PASS | PASS | PASS | PASS |
| EV-F08-14 | fixtures/evidence_manifest.json | PASS | PASS | PASS | PASS |
| EV-F08-15 | fixtures/firstframe_extract.png | PASS | PASS | PASS | PASS |
| EV-F08-16 | fixtures/folder_v1/p1.png | PASS | PASS | PASS | PASS |
| EV-F08-17 | fixtures/folder_v1/p2.png | PASS | PASS | PASS | PASS |
| EV-F08-18 | fixtures/folder_v1/p3.png | PASS | PASS | PASS | PASS |
| EV-F08-19 | fixtures/folder_v2/p1.png | PASS | PASS | PASS | PASS |
| EV-F08-20 | fixtures/folder_v2/p2renamed.png | PASS | PASS | PASS | PASS |
| EV-F08-21 | fixtures/folder_v2/p4.png | PASS | PASS | PASS | PASS |
| EV-F08-22 | fixtures/img_base.png | PASS | PASS | PASS | PASS |
| EV-F08-23 | fixtures/img_cmyk.jpg | PASS | PASS | PASS | PASS |
| EV-F08-24 | fixtures/img_copy.png | PASS | PASS | PASS | PASS |
| EV-F08-25 | fixtures/img_dhash_dist10.png | PASS | PASS | PASS | PASS |
| EV-F08-26 | fixtures/img_dhash_dist11.png | PASS | PASS | PASS | PASS |
| EV-F08-27 | fixtures/img_dhash_ref.png | PASS | PASS | PASS | PASS |
| EV-F08-28 | fixtures/img_exif_o6.png | PASS | PASS | PASS | PASS |
| EV-F08-29 | fixtures/img_flipped.png | PASS | PASS | PASS | PASS |
| EV-F08-30 | fixtures/img_gray.png | PASS | PASS | PASS | PASS |
| EV-F08-31 | fixtures/img_gray_as_rgb.png | PASS | PASS | PASS | PASS |
| EV-F08-32 | fixtures/img_reenc.jpg | PASS | PASS | PASS | PASS |
| EV-F08-33 | fixtures/img_rotated_phys.png | PASS | PASS | PASS | PASS |
| EV-F08-34 | fixtures/wrongframe_blue.png | PASS | PASS | PASS | PASS |
| EV-F08-35 | logs/h4_run.log | PASS | PASS | PASS | PASS |
| EV-F08-36 | logs/h5_run.log | PASS | PASS | PASS | PASS |
| EV-F08-37 | logs/h6_run.log | PASS | PASS | PASS | PASS |
| EV-F08-38 | logs/make_fixtures.log | PASS | PASS | PASS | PASS |
| EV-F08-39 | logs/make_fixtures_regeneration.log | PASS | PASS | PASS | PASS |
| EV-F08-40 | logs/matrix.log | PASS | PASS | PASS | PASS |
| EV-F08-41 | logs/run_all.log | PASS | PASS | PASS | PASS |
| EV-F08-42 | logs/stage_evidence.log | PASS | PASS | PASS | PASS |
| EV-F08-43 | prototype_hashes.txt | **FAIL** | PASS | PASS | **FAIL** |
| EV-F08-44 | results/capability_matrix.json | PASS | PASS | PASS | PASS |
| EV-F08-45 | results/capability_matrix.md | PASS | PASS | PASS | PASS |
| EV-F08-46 | results/fixtures_manifest.json | PASS | PASS | PASS | PASS |
| EV-F08-47 | results/h4_results.json | PASS | PASS | PASS | PASS |
| EV-F08-48 | results/h5_results.json | PASS | PASS | PASS | PASS |
| EV-F08-49 | results/h6_results.json | PASS | PASS | PASS | PASS |
| EV-F08-50 | results/run_all_log.json | PASS | PASS | PASS | PASS |
| EV-F08-51 | logs/gates.log | —（SHA-only） | PASS | PASS | — |
| EV-F08-52 | logs/pin-verify.log | —（SHA-only） | PASS | PASS | — |

52/52覆盖、WT/HEAD checkout 52/52，并不等于指定commit pin 52/52。pin-verify.log排除自身生成过程合理：其自身最终字节另由EV52 SHA-only校验；本轮其SHA=`52eab88ec81243bd216675f46fb30fbd758f69c079092dcc96bd326cb3f3936c`，gates.log SHA=`fd227b34a27093c1498fbe73622bf33ca16661e0f3995cb138635f9911d6f177`，均匹配。001并非自引用问题。

## 附录B：判别输出与旧PNG

```text
M8M9: needs_confirmation / folder_membership+bytes_sha256 / members_a=3, members_b=3
M17: candidate / dhash_distance=10 / assert_distance_is_10=true
M18: no_match / dhash_distance=11 / assert_distance_is_11=true
H6 dimensions counterexample: exact_match, size_a=[2,6], size_b=[3,4]
H6 ambiguous repeated pages: exact_match, multiset_equal=true, members_a=2, members_b=2
matrix mutated assertions: h4_pass=true, h6[单图]=true
staging H4 failure: fixtures=[new.bin], old_pin_removed=true,
                   old_results={"old":"PASS"}, success_log="EXIT=0 old successful run"
reader    8533c263c79bd53cefa68a21d2aabe6501556fd62218ebf653b528c9cbec78b2
settings  fd30b166e30aec7a43e4d82ecd1fefb14dffef3bebe2f5f952e41d45e324a162
shelf     307f8f6748522d1cdb3226135a3f733961744a3b2aa5d410f89aad3fde138b0a
workbench d5d878bbba9e47e2b59d9dd03816a370688a7afebec6d6e00016f262a46e2df5
```

隔离原件/反例/输出保存在R/供DSH复现，均为本轮自建合成数据或入库证据副本，无真实用户数据；原workspace/tmp和H5 lab空。保留的反例PNG/ZIP为判别artefact，不作为临时残留或新Canonical。报告摘录关键输出，不代替下一轮Owner补齐版本化证据。

## 附录C：57个skip来源与原因

本次进程未设置`NEWMANGA_CORECLIENT_SIDECAR_DIR`。下列各属性先检查sidecar guard，因AC11无标签sidecar fixture不可用而Skip；Book/Region附加fixture检查在此之后，本轮没有执行到。HostFixture、SidecarFixture、App的CreateChapterSidecarFixture/RunFixture均有明确reason返回。总数=Host28 + CoreClient22 + App7 =57；无删除/过滤。表中S表示同一完整原因“needs sidecar fixture；设置NEWMANGA_CORECLIENT_SIDECAR_DIR或运行apps/desktop-avalonia/scripts/test.ps1（AC11 unlabelled copy）”。来源路径前缀为apps/desktop-avalonia/tests/。

| 测试（完整标识） | 源文件:行 / 属性 | 原因 |
|---|---|---|
| NewManga.CoreClient.Tests.Commands.CommandWiringB1Tests.B1Commands_RejectInvalidArgumentsBeforeAnyCoreFrame | NewManga.CoreClient.Tests/Commands/CommandWiringB1Tests.cs:267 / SidecarFact | S |
| NewManga.CoreClient.Tests.Commands.CommandWiringB1Tests.B1Commands_ExecuteAgainstFrozenCore | NewManga.CoreClient.Tests/Commands/CommandWiringB1Tests.cs:124 / SidecarFact | S |
| NewManga.Host.Tests.RealTranslateProviderTests.RealOpenCodeProvider_HostConfiguration | NewManga.Host.Tests/RealTranslateProviderTests.cs:64 / HostSidecarFact | S |
| NewManga.Host.Tests.HostReaderChaptersIntegrationTests.ConcurrentChapterAndProjectionReads_AreSerialized | NewManga.Host.Tests/HostReaderChaptersIntegrationTests.cs:74 / BookFixtureFact | S |
| NewManga.Host.Tests.HostReaderChaptersIntegrationTests.ListChapters_MatchesReaderProjection | NewManga.Host.Tests/HostReaderChaptersIntegrationTests.cs:35 / BookFixtureFact | S |
| NewManga.Host.Tests.GrantIssuerTests.ShellActions_Open_Whitelisted_Directories_And_Refuse_Outside_Paths | NewManga.Host.Tests/GrantIssuerTests.cs:230 / HostSidecarFact | S |
| NewManga.Host.Tests.GrantIssuerTests.Export_GrantRegisters_ThenCoreFailsTyped_OnMissingTranslatedPages | NewManga.Host.Tests/GrantIssuerTests.cs:118 / HostSidecarFact | S |
| NewManga.Host.Tests.GrantIssuerTests.Import_IntoNewChapter_Executes_AndRegistersGrant | NewManga.Host.Tests/GrantIssuerTests.cs:64 / HostSidecarFact | S |
| NewManga.Host.Tests.GrantIssuerTests.ShellActions_RealOpener_OpensExplorer_WhenEnabled | NewManga.Host.Tests/GrantIssuerTests.cs:187 / HostSidecarFact | S |
| NewManga.Host.Tests.HostReaderProgressIntegrationTests.SaveReadingProgress_PersistsAcrossHostRestart_AndResumes | NewManga.Host.Tests/HostReaderProgressIntegrationTests.cs:36 / BookFixtureFact | S |
| NewManga.Host.Tests.HostReaderProgressIntegrationTests.SaveReadingProgress_UnknownPage_IsTypedCoreRejection | NewManga.Host.Tests/HostReaderProgressIntegrationTests.cs:138 / BookFixtureFact | S |
| NewManga.Host.Tests.HostReaderProgressIntegrationTests.SaveReadingProgress_ReadOnlyHost_IsTypedRefusal_NoCoreCall | NewManga.Host.Tests/HostReaderProgressIntegrationTests.cs:168 / HostSidecarFact | S |
| NewManga.Host.Tests.ExportStalePolicyWireTests.BothPolicies_AreSentToTheCore_AsStartExportFrames | NewManga.Host.Tests/ExportStalePolicyWireTests.cs:18 / HostSidecarFact | S |
| NewManga.Host.Tests.CredentialPortTests.CredentialPutAndClear_AgainstFrozenSidecar_FullChain | NewManga.Host.Tests/CredentialPortTests.cs:197 / HostSidecarFact | S |
| NewManga.Host.Tests.StartupSelfCheckTests.MajorMismatch_DowngradesToReadOnly_AndRefusesWrites | NewManga.Host.Tests/StartupSelfCheckTests.cs:153 / HostSidecarFact | S |
| NewManga.Host.Tests.StartupSelfCheckTests.RealHost_PassesCheapChecks_AndStaysWritable | NewManga.Host.Tests/StartupSelfCheckTests.cs:107 / HostSidecarFact | S |
| NewManga.Host.Tests.StartupSelfCheckTests.MissingCapability_DowngradesToReadOnly_AndRefusesWrites | NewManga.Host.Tests/StartupSelfCheckTests.cs:162 / HostSidecarFact | S |
| NewManga.Host.Tests.LegacyShellRealTests.LegacyShellRunning_ForcesReadOnlyMode_AndBlocksWrites | NewManga.Host.Tests/LegacyShellRealTests.cs:48 / HostSidecarFact | S |
| NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionReads_SerializeOnTheCorePipe | NewManga.Host.Tests/HostRegionWorkbenchIntegrationTests.cs:304 / RegionFixtureFact | S |
| NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionWrites_ReadOnlyHost_AreTypedRefusals_WithZeroCoreFrames | NewManga.Host.Tests/HostRegionWorkbenchIntegrationTests.cs:240 / RegionFixtureFact | S |
| NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionReadWriteFace_ExecutesAgainstFrozenCore_AndProjectsOverlayGeometry | NewManga.Host.Tests/HostRegionWorkbenchIntegrationTests.cs:37 / RegionFixtureFact | S |
| NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionWrite_StaleExpectedRevision_IsTypedInputRevisionChanged | NewManga.Host.Tests/HostRegionWorkbenchIntegrationTests.cs:198 / RegionFixtureFact | S |
| NewManga.Host.Tests.HostRuntimeIntegrationTests.ReadOnlyUntilParity_Ready_WithBothSidecars_AndWriteBlocked | NewManga.Host.Tests/HostRuntimeIntegrationTests.cs:15 / HostSidecarFact | S |
| NewManga.Host.Tests.HostRuntimeIntegrationTests.ParityReached_ChineseRoundTrip_IsExact_ThroughHost | NewManga.Host.Tests/HostRuntimeIntegrationTests.cs:62 / HostSidecarFact | S |
| NewManga.Host.Tests.HostRuntimeIntegrationTests.SecondInstance_IsAlreadyRunning_WithoutSpawningSidecars | NewManga.Host.Tests/HostRuntimeIntegrationTests.cs:141 / HostSidecarFact | S |
| NewManga.Host.Tests.ExportE2ETests.Export_Zip_Produces_RealArtifact_AndSnapshotHistory | NewManga.Host.Tests/ExportE2ETests.cs:74 / HostSidecarFact | S |
| NewManga.Host.Tests.ExportE2ETests.Export_Cancel_LeavesNoArtifact | NewManga.Host.Tests/ExportE2ETests.cs:279 / HostSidecarFact | S |
| NewManga.Host.Tests.WritePolicyTests.DefaultStart_IsReadWrite_AndCanCreateBook | NewManga.Host.Tests/WritePolicyTests.cs:59 / HostSidecarFact | S |
| NewManga.Host.Tests.WritePolicyTests.ExplicitParityFalse_RefusesWrites_WithTypedReadOnlyError | NewManga.Host.Tests/WritePolicyTests.cs:95 / HostSidecarFact | S |
| NewManga.Host.Tests.WritePolicyTests.FirstRunBackup_CreatesRealBackupFile_OnFirstWritableStartWithCatalog | NewManga.Host.Tests/WritePolicyTests.cs:173 / HostSidecarFact | S |
| NewManga.App.Tests.CreateChapterHostIntegrationTests.HostController_CreateChapter_SucceedsThenMapsCoreFailures | NewManga.App.Tests/ChapterCreationTests.cs:164 / HostSidecarFact | S |
| NewManga.App.Tests.CreateChapterHostIntegrationTests.HostController_CreateChapter_WhenReadOnly_PublishesHostReadOnly | NewManga.App.Tests/ChapterCreationTests.cs:230 / HostSidecarFact | S |
| NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_InvalidOverrides_AreRejectedBeforeAnyCoreFrame | NewManga.CoreClient.Tests/Commands/RunBindingFixTests.cs:265 / SidecarFact | S |
| NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_DefaultDisabled_OmitsProviderBindings | NewManga.CoreClient.Tests/Commands/RunBindingFixTests.cs:242 / SidecarFact | S |
| NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_InjectsDefaultBindings_WhenOverridesAbsentOrEmpty | NewManga.CoreClient.Tests/Commands/RunBindingFixTests.cs:179 / SidecarFact | S |
| NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_KeepsExplicitUserBindings_AndOtherOverrides | NewManga.CoreClient.Tests/Commands/RunBindingFixTests.cs:212 / SidecarFact | S |
| NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.DomainServices_CoverEveryCommandExactlyOnce | NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs:378 / SidecarFact | S |
| NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.NotSupportedSurface_ReturnsTypedErrorsWithReasons | NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs:333 / SidecarFact | S |
| NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.ChineseTitle_ThroughCommandDispatcher_RoundTripsWithoutMojibake | NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs:288 / SidecarFact | S |
| NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.TwelveImplementedCommands_ExecuteAgainstFrozenSidecars | NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs:90 / SidecarFact | S |
| NewManga.CoreClient.Tests.SidecarFailureTests.StartupTimeout_IsTyped_NotAHang | NewManga.CoreClient.Tests/SidecarFailureTests.cs:65 / SidecarFact | S |
| NewManga.App.Tests.WritePolicyUiIntegrationTests.DefaultController_IsWritable_AndParityFalse_IsReadOnlyWithReason | NewManga.App.Tests/WritePolicyUiTests.cs:55 / WritePolicySidecarFact | S |
| NewManga.CoreClient.Tests.Commands.CommandWiringB2Tests.ListRegionRevisions_ExecutesAgainstRegionFixture | NewManga.CoreClient.Tests/Commands/CommandWiringB2Tests.cs:418 / S4RegionFixtureFact | S |
| NewManga.CoreClient.Tests.Commands.CommandWiringB2Tests.B2Commands_ExecuteAgainstFrozenCore | NewManga.CoreClient.Tests/Commands/CommandWiringB2Tests.cs:267 / SidecarFact | S |
| NewManga.CoreClient.Tests.Commands.CommandWiringB2Tests.B2Commands_RejectInvalidArgumentsBeforeAnyCoreFrame | NewManga.CoreClient.Tests/Commands/CommandWiringB2Tests.cs:464 / SidecarFact | S |
| NewManga.CoreClient.Tests.CoreServiceIntegrationTests.RawUtf8Request_ReplicatesUnknownError | NewManga.CoreClient.Tests/CoreServiceIntegrationTests.cs:105 / SidecarFact | S |
| NewManga.CoreClient.Tests.CoreServiceIntegrationTests.ChineseTitle_CreateThenList_RoundTripsExactly_AndWireIsAsciiEscaped | NewManga.CoreClient.Tests/CoreServiceIntegrationTests.cs:54 / SidecarFact | S |
| NewManga.CoreClient.Tests.CoreServiceIntegrationTests.Ping_ReturnsReady_WithProtocol23 | NewManga.CoreClient.Tests/CoreServiceIntegrationTests.cs:20 / SidecarFact | S |
| NewManga.CoreClient.Tests.CoreServiceIntegrationTests.WireFrames_AreSingleLineUtf8AndAsciiForEveryEscapedRequest | NewManga.CoreClient.Tests/CoreServiceIntegrationTests.cs:146 / SidecarFact | S |
| NewManga.CoreClient.Tests.HostBridgeIntegrationTests.WireFrames_AreSingleLineJson_AsciiOnly | NewManga.CoreClient.Tests/HostBridgeIntegrationTests.cs:84 / SidecarFact | S |
| NewManga.CoreClient.Tests.HostBridgeIntegrationTests.TypedErrors_UnknownResource_AndCoreOwnedPathSmuggling | NewManga.CoreClient.Tests/HostBridgeIntegrationTests.cs:57 / SidecarFact | S |
| NewManga.CoreClient.Tests.HostBridgeIntegrationTests.Ping_IssueResolveRevoke_FullLifecycle | NewManga.CoreClient.Tests/HostBridgeIntegrationTests.cs:14 / SidecarFact | S |
| NewManga.CoreClient.Tests.Commands.S4RegionReaderCommandTests.RegionWriteFace_AndReaderProgressFace_ExecuteAgainstFrozenCore | NewManga.CoreClient.Tests/Commands/S4RegionReaderCommandTests.cs:77 / S4RegionFixtureFact | S |
| NewManga.App.Tests.StartupSelfCheckUiTests.SelfCheckFailure_IsVisibleInTheSnapshot | NewManga.App.Tests/StartupSelfCheckUiTests.cs:15 / WritePolicySidecarFact | S |
| NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_WhenReadOnly_PublishHostReadOnly | NewManga.App.Tests/RunControllerTests.cs:394 / RunSidecarFact | S |
| NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_StartSuccessfulRun_ProjectRealPerPageState_AndReuseKey | NewManga.App.Tests/RunControllerTests.cs:302 / RunBookFixtureFact | S |
| NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_MapCoreErrors_AndReuseIdempotencyKeys | NewManga.App.Tests/RunControllerTests.cs:248 / RunSidecarFact | S |
