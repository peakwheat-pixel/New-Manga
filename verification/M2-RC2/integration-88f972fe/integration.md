# M2-RC2 Codex 集成核验

**结果：** M2-RC2 已集成并关闭为 done。代码合并 commit 为 `88f972fed921c7d7a010bef38a734de2601d9ca5`；Task 的 integration_commit 指向此 merge commit。当前文档与复跑证据记录在后续 Codex integration evidence commit。

## 输入与历史

- 集成基线（当前 main 在本次工作开始时）：`6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`。
- 验证树：`eac5cb3ed56b4531106cfa98ec6d4ea11ce8d51b`。
- 文档树：`dc8e5c95c31ccc0dd96fa2287b44aa962c70153d`，其祖先包含验证树；因此以 DC8 为 second parent 一次合入两者。
- 固定 Task base：`22a2c2bf9a70d8c3b81edcdbe0e1ef146db556e5`。Owner 分支 `agent/zcode/M2-RC2-resource-channel-hardening` 与 worktree `C:/Users/49745/.codex/worktrees/m2-rc2-zcode/New Manga` 保持原位，tip 仍为 DC8。
- Codex 使用 `--no-ff` 合并 DC8，merge commit parents 为 `6a68fdeb` 与 `dc8e5c95`；没有冲突，也没有改写 Owner 历史。FIX commit EAC5 位于 DC8 的 ancestry。
- 从 6A68 到 DC8 的整条输入分支带入 667 个路径，其中包含先前 M2 集成历史；M2-RC2 固定 base 到 DC8 的 Task delta 为 60 路径。按 Task allowed_paths 核对，超范围路径 0。FIX delta 为 31 路径，累计到 EAC5 为 58 路径。
- Owner worktree 中的 Reviewer 文件仍保持 untracked 且未被修改；只将副本导入主线。原主工作区既有修改与未跟踪内容未动。

## DSH 报告与证据导入

报告和 Reviewer 证据以原字节导入，共 56 个文件（2 份报告、54 个复核文件），导入前后 SHA256 全部一致，哈希清单：[review-dsh-import-sha256.txt](../review-dsh-import-sha256.txt)。

为避免 Windows Git `core.autocrlf` 改写来源字节，`.gitattributes` 仅对这两份报告、两组 Reviewer 证据与哈希清单禁用文本换行转换；暂存 Git blob 按清单复核为 56/56 匹配。

- [首轮 DSH Review（changes_requested）](../../../doc/reviews/M2-RC2-a8fb17ca.md)：`e01aabc6b90a782dd90fe3eb13c7a059378918a9f8bb58d53701e897b637243b`
- [FIX 轮 DSH Review（approved）](../../../doc/reviews/M2-RC2-FIX-eac5cb3e.md)：`02ea074e34b244a099dcd4380d0eefd65967d4facf19034e9811b80482f356dc`

## R3-01

已修正 [allow-deny-matrix.md](../allow-deny-matrix.md)：ACL 拒绝文本证据只归于 probe 阶段 D-01（`raw/e2e-probe-results.json`）；interactive 模式 IP-1 明确为页面自检且无归档输出。参数注入矩阵同步收窄为 D-01 与 Rust 构建断言证据。此次只改文案，无产品代码变化。

## 集成后验证

环境：Windows / PowerShell Core 7.6.6；Python 3.14.6（`C:\Python314\python.exe`）；Cargo 1.98.1；Rust 1.98.1；Node 24.15.0；npm 12.0.1。成功复跑的测试日志均带命令、环境头、时间与 EXIT。

| 命令 | 结果 | 转录 |
|---|---|---|
| `python -m pytest tests/m2_resource_channel -q` | 66 passed，EXIT=0 | [pytest.log](pytest.log) |
| `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked` | 20 passed，EXIT=0 | [cargo.log](cargo.log) |
| `npm test --prefix apps/desktop/frontend -- --run` | 2 files / 15 tests passed，EXIT=0 | [vitest.log](vitest.log) |
| `python verification/M2-RC2/run_e2e.py` | 13/13 probe PASS；10/10 gate PASS；EXIT=0 | [e2e.log](e2e.log) |
| `python verification/M2-RC2/review-dsh-a8fb17ca/probe_ttl_nan.py` | NaN、±Inf、0、301 拒绝；300 可签发并按期过期；wire NaN/Infinity 拒绝；EXIT=0 | [probe-ttl-nan.log](probe-ttl-nan.log) |

E2E 首次在空白 worktree 缺少 frontend dist 时，Cargo context build 与 E2E 返回非零；npm test 也因尚未安装 Vitest 返回非零。按既有 package-lock 执行 `npm ci --prefix apps/desktop/frontend` 与 `npm run build --prefix apps/desktop/frontend`，均 EXIT=0 后，上表五项全部重跑通过。首次失败转录位于 [initial-attempt](initial-attempt/)；环境准备转录为 [frontend-setup.log](frontend-setup.log)。准备步骤未更改 package.json 或锁文件。

E2E 生成的 tracked raw 文件及 Tauri 生成文件已恢复到源提交内容；Codex 复跑的完整 stdout 留在本目录，不覆盖 DSH 或 Owner 证据。TTL 探针由导入的首轮 Reviewer 脚本运行，未修改脚本。

## 契约与 Gate 边界

- Contract 1.1 blob 在固定 base 与集成 tree 均为 `fc35913801297ee1876ea395f9c5041a16226f20`。
- `apps/desktop/src-tauri/tauri.conf.json` 仍为 `"active": false`。
- S1-B3/B6/B8 保持 `NOT_RUN`，S1-B5 保持 `UNVERIFIED`；未作产品级安全、安装或打包就绪声明。
- **Whitespace check：** `git diff --check 22a2c2bf9a70d8c3b81edcdbe0e1ef146db556e5..HEAD`（HEAD=`88f972fed921c7d7a010bef38a734de2601d9ca5`）与当前文档工作树 `git diff --check` 均 `EXIT=0`。为保持 DSH 原始证据的 SHA256，导入文件禁用了换行转换；因此全量暂存 `git diff --cached --check` 会把来源 CRLF 行尾报告为尾随空白。排除两份报告、两组原始证据和其哈希清单后，对 Codex 集成内容执行的暂存 whitespace 检查 `EXIT=0`。
- `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/12_ROADMAP.md`、`doc/tasks/README.md` 与 `doc/00_INDEX.md` 已按完成状态更新。Current Active Task 保持 None；当前没有安全且已释放的下一 Task。Codex 须根据当前 Plan/STATUS 依 §5.1 另行选择、登记和释放，不自动启动实现。
