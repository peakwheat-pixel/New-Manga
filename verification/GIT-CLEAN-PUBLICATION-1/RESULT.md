# 干净源码快照交付结果

2026-10-24 / Codex。固定候选：`e34a90d001cce1fa966aec7d2b032bb5ad1cf148`。

独立仓库：`G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/source-export-r4`；分支 `codex/clean-source-snapshot`。仅一个无父提交的根提交，没有remote，不与原main共享对象库。**材料排除已核查，软件完整验证仍有阻断，DSH r1 已独立审查且 blocked；未 push。**

## 内容与边界

- 724个源文件、5个从自制生成器重建的PNG和1个manifest、3个快照说明/来源/忽略文件，共733个tracked文件。
- 来源固定 `349e61faff5f93067af5d4ce2d9e394e0d665b8c`；源blob/SHA与导出SHA逐项记录于候选 `SOURCE_MANIFEST.json`。仅两处文档/测试的个人目录字面量变为USER；生产实现、接口、Schema、依赖与锁文件不改。
- 逐文件例外包括TASK-016合成样本生成器、项目图标及P04/P22两个纯测试sidecar源码；没有把verification目录或历史日志整包带入。
- 169个JPEG和169个压缩外层blob共338个禁止对象，在候选Git对象库中全部missing；原件、原main、原历史和6个P04日志保留且指纹不变。
- 未导出私有漫画/测试素材、模型、数据库、日志、审计证据、旧历史、agent配置或上传缓存。生成的测试诊断日志被忽略，不属于候选commit。对凭据规则的6个命中已按固定源文件/值hash核对为脱敏或本地proxy测试构造数据；不声称穷尽所有编码秘密。
- 候选逐文件hash、Git图、git fsck、无remote、清洁状态均通过，见 `validation.json`。早期source-export/r2/r3本地候选全部保留，不push、不删改、不重写它们的历史。

## 实际验证

| 检查 | 真实结果 | 条件与限制 |
|---|---|---|
| 前端离线依赖与构建 | r4 npm ci --offline、npm run build均exit 0 | 未复制原仓node_modules/dist |
| 前端单测 | 45文件、435通过 | 实测r3；r3与最终r4的整个frontend Git subtree完全一致，树hash已核验，不伪称在r4重复执行 |
| Rust源码单测 | r4串行153通过、0失败、1 ignored、12 filtered | ignored为 `perf_chunk_request_digest_cost`；12项为独立frozen-sidecar环境测试，当前未构建安装包，因此过滤 |
| Core单测 | 771通过、1个参数化用例的3组参数失败 | 实测r2；最终r4的src及tests/core两个Git subtree与r2完全一致。失败均为导出Hook测试，插件audit记录 `PLUGIN_HOOK_UNAVAILABLE: cannot grant sandbox access to python.exe`；不修系统Python ACL、不把失败标skip |
| Rust并行对照 | 先前r2有2个worker-registry共享状态失败，另一个缺fixture | 完整失败日志保留；串行通过不裁决并行隔离风险 |
| 安装包/真实模型/GUI/全产品审计 | NOT_RUN | 不借用原仓ignored bundle/模型伪造fresh结果，不冒充发布通过 |

首轮APPDATA隔离使用户site的pytest不可见；后续显式提供既有PYTHONUSERBASE来加载已安装依赖，同时保持数据目录隔离。没有安装新的Python依赖。后续发现源码测试对合成PNG、P04/P22优先sidecar的依赖，补齐的是源代码/自制夹具；原生产代码没有为测试修改。

## 当前Gate与交接

本地快照可供材料与来源独立Review；**完整验证Gate未通过**：Core 三组参数失败、旧 icacls 错误码未知，r4 默认并发 151通过/2失败；packaged 结果以诊断 RESULT 为准。不建议现在push。

主仓源HEAD仍为 `349e61faf`，暂存区保持空；只新增/更新治理与本Task证据。Task进入 `in_review`，不置done；Reviewer=DeepSeek Harness，r1 decision=blocked。冻结证据在 `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/review-package`，以Task的SHA表核验。

推荐下一步：完成 `GIT-CLEAN-PUBLICATION-DIAG-1` 的证据冻结并交 DSH 按新 Appointment 只读独审；父候选不变，不升级 head/push/done。详细处置见 `../GIT-CLEAN-PUBLICATION-DIAG-1/RESULT.md`。

补充披露：r2、r3 串行分别均为152 passed/1 failed/1 ignored/12 filtered，exit101；r4补齐P22夹具后才153/0/1/12、exit0。旧日志原字节保留，review-package-r2 的 EXIT envelope 是依据 checks 事后整理，缺失环境不补造。当前实际1个loose ref、无packed-refs；只允许通过Git tracked对象交付，禁止打包live目录或本地复审包。private_profile_path_hits=[]仅指实际个人标识49745；测试占位C:\Users路径仍在。第六个manifest也是固定生成器产物；源同路径旧PNG/manifest是不同渲染批次，新hash不等于旧blob。候选未带.gitattributes，换行由core.autocrlf=false控制。本说明补充DSH R-009–R-013，不修改旧候选。

## DIAG独审后当前口径

DIAG DSH r1对fed为approved，仅诊断交付；上文“待诊断独审”的建议已被此段取代。父e34仍in_review/r1 blocked，Core及真实并发Gate不解除。父升级前必须携带DIAG Review R-01/R-02/R-03门槛与DIAG-50..52→父DB-41..43→DIAG-53/父SUP-38→包内DB的交叉链，重新Appointment新父head。

R-04–R-13及旧包文档快照口径见DIAG RESULT最新追加段和workspace/review-disposition-r1/PACKAGE_MANIFEST.json（只追加说明，旧包原字节不改）。当前下一步为Antigravity认领GIT-CLEAN-RUST-ISOLATION-1；Core ENV-2仅proposed。没有新父head，不push、不done、不改源main/系统ACL。
