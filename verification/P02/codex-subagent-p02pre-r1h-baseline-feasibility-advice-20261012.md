# P02PRE-R1H frozen Git baseline 架构建议（非 Review）

- Advisor：只读 Expert Advisor `/root/r1h_baseline_advice`。
- 范围：精确读取 R1H Task、R1H manifest、继承 R1G manifest、R1H capture/self-check/Handoff；未修改文件、未运行 candidate/self-check/getter/test，未枚举目录，未触碰 `.tmp.driveupload`。
- 该建议不是独立 Review、Gate、测试或 Codex adjudication。

## R1H-001

Task AC1 与 R1H manifest 要求 main/scratch frozen refs/index/status 精确匹配；但 R1G manifest 只提到历史 `mainGit.controlledStatus.nulRecords=873` 修正，没有冻结 status 原始内容/hash，也没有 scratch status/index expected values。candidate 固定 main/scratch HEAD/tree 常量并比较 root/common-dir/HEAD/tree/branch；status 只检查查询 exit 并记录当次 byte/hash；index 只比较当次 inventory 前后 hash。未发现可精确对照的 main/scratch frozen status/index expected values。

结论：不能证明当前 status/index 与冻结基线相同。最小安全实现是在 expected 值缺失时把该条件显式分类 `UNPROVABLE`，且非-reparse symlink skip 必须 fail-stop；status exit=0、本次 index 前后相同和固定 refs 均不能替代。

## 其他静态风险提示

- R1H-002：现有 `git ls-files --stage -z` parser 可在既有查询中保留并要求 stage=0；任何非零 stage 即 stop，不需新增 API/path/child。
- R1H-003：只从当前 `Get-Item` 的现有 metadata 采用窄 ordinary-file whitelist（例如精确 FileInfo 类型且排除 Device/未知属性）；无法证明即 stop，不增加 target getter。
- R1H-004：PowerShell AST 可定位真实 `Get-RepositoryRecord` 的 If/循环结构，约束非-reparse skip branch 的允许语句和外围 continue，并添加 baseline/stage/device 负例。AST 只证明局部静态结构，不能替代动态/OS 行为的独立审查。