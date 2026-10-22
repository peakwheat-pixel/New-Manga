你是 P02PRE-R1F Round 5 的独立只读 Reviewer。你不是实现者。只阅读下列精确冻结文件，不运行命令、capture script、host getter、registry/ACL API，不访问 `.tmp.driveupload` 内容，不改写任何共享文件。

项目目录：`G:\CODEX\New Manga`

审查输入及 Codex 冻结 pins：
- `doc/tasks/P02PRE-R1F.md` — 17488 bytes / SHA-256 `0795FA274CED5694FF4586EDA0553AAAA9D463C44A78B373E47B4F30AF46B0CD`
- `verification/P02/p02pre-r1f-manifest-20261011.md` — 16284 bytes / SHA-256 `5B5C3740DFF998DFBC1833E01236429273DE5BA9C755512AFD88012F7E1AD1C9`
- `verification/P02/p02pre-r1f-capture.ps1` — 60725 bytes / SHA-256 `80C8BC311CE372832BF1D4567ABDCF7E8AA2D7296CBE339FE95BAD65D63E5216`
- `verification/P02/p02pre-r1f-r5-selfcheck-retry-20261011.json` — 1694 bytes / SHA-256 `06A8387E6ABCC6DD4F3912FDCBEE006E58B96C8E00F64A165C365435D7ADD2CE`
- 历史 helper 失败证据（仅用于区分失败对象）：`verification/P02/p02pre-r1f-r5-selfcheck-20261011.json` — 2975 bytes / SHA-256 `7C0F2E2CC4950018DB42D83472BF044B68A686E39D8D4AB9D3686BBDFCAE5E73`

背景：此前 R4 已批准并产生 R7 parse-only，但随后 path-only preflight 发现脚本会 hash 两仓 `.tmp.driveupload/` 下的用户上传暂存文件（每仓观察到 2148 个候选；一个文件 metadata 显示 29,124,800 bytes），因此当时正确地未调用 capture。另发现 scratch detached HEAD 下 `git symbolic-ref --short HEAD` 的精确结果为 exit 128、stdout 空、stderr Base64 `ZmF0YWw6IHJlZiBIRUFEIGlzIG5vdCBhIHN5bWJvbGljIHJlZgo=`。当前候选在 R5 中加入路径字符串规范化/仓库边界检查后的 `.tmp.driveupload` 精确根及后代排除，以及只接受预期 branch=`DETACHED` 时的精确错误响应。R5 PS 5.1 isolated self-check 记录了 `PARSE_OK`、四函数 assertions `PASS`、0 output、未调用 capture/host getter。首次 helper 失败是 harness 自身在解析前使用 PS 5.1 不支持的 `SHA256.HashData`，不得描述成脚本 parse 或自检失败。

请独立审查以下内容，检查实现与 Task/manifest 是否一致，并寻找会造成用户数据读取、错误接受 Git 响应、计数分类不实、边界绕过或误触发 capture 的缺陷：
1. `.tmp.driveupload` 根和任意深度后代在任何 `Get-Item`、`Get-FileHash`、`Get-Acl` 或其他文件内容/元数据访问前被排除；只保存聚合计数和首个相对路径，不读取/记录每项内容或 metadata；任何排除都使 repository inventory 为 `UNPROVABLE`。
2. path normalization 与 repository root boundary 校验是否先于排除且有正确边界；审查 path separator、大小写和路径形式。
3. detached `symbolic-ref` 只在所有冻结条件完全吻合时接受，其他退出码/stdout/stderr 仍 fail-stop；main branch 必须正常精确匹配。
4. inventory processed/omitted/hash/symlink/user-staging counters、失败路径、self-check 与 JSON 输出是否自洽；不把 skipped user files 或 symlink target 报作已验证 hash。
5. R1F 整体仍限于 manifest 精确只读 allowlist 与一次性 `CreateNew` evidence；没有绕过身份/目标校验、未知子进程、范围外写入或提前执行 capture 的路径。
6. Task、manifest、script 与自检 artifact 的叙述、参数、限制、禁止项及验收标准是否相互一致。清楚区分代码静态结论、Codex 自检证据与实际 host/Gate 证据。

请输出简体中文 Review，结构固定：
- Decision：`APPROVED` 或 `CHANGES_REQUESTED`
- counts：`P0/P1/P2/P3 = n/n/n/n`
- 每条 finding：ID、等级、文件/行号、可复现的具体原因、最小修复建议；若无 findings，写 `无 open findings`
- 单独核对上述 1–6 项，标 `PASS`/`FAIL`/`UNPROVEN` 并说明证据范围
- 明确声明你只读了文件，未运行命令、脚本、getter、capture，也未修改文件
- 不得把本次代码 Review 或 self-check 说成 P02PRE Gate/Build Gate PASS；不得建议跳过 R8 或 Codex pre-run adjudication
