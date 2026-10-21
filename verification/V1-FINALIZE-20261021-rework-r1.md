# V1 收口 r1 返修报告（2026-10-21）

**范围**：仅修复本 Review 指出的证据行尾/pin 复现性、P15/P19/GOV/RUST 收口说明、Plan 状态及必要的 STATUS/台账同步。
**基线**：`a689a1ec2510278bfe53519baa2e81665e94778b`；**返修提交**：`9f5262f19684a4bda1dbdec4e966b49b2c000442`。
**约束遵守**：未改产品代码 / 接口 / Schema / 依赖；未触碰 untracked 草稿；未执行清理、push、GC/prune、历史改写；原日志文本内容未变（仅工作区 EOL 统一为 LF，Git blob 未变）。

## 1. 修正清单

| ID | Review 问题 | 修正 | 验证 |
|---|---|---|---|
| R1-01 | 证据行尾/pin 不可复现：日志 blob 为 LF，但工作区/pin 为 CRLF；目录无 `text eol=lf`，在 `core.autocrlf=false/input` 的检出中 SHA-256 会失配 | `.gitattributes` 增加 `* text eol=lf`（保留 `-whitespace`）；把 V1 证据文件的工作区字节按 Git blob 的 LF 内容重写（文本不变）；`RUST-ENV-BASELINE-1` 的 13 个证据行 SHA-256 改为 LF 字节值；新增 `EV-V1-GITATTR` 登记 `.gitattributes` | `git archive` 提取后 **13/13** pin 匹配、**0 CRLF**（autocrlf=true / false 两种配置均通过，见 §3） |
| R1-02 | P15-CORE-1 收口说明错误地写成 `cancelled`/"未交付"；实际范围已由 `P15-CORE-1A/1B/1C`（均 `done`，commit `9232802c0`/`6cf3c8209`/`52b0974ad`）交付 | 状态 `cancelled` → **`superseded`**；收口说明改为"拆分交付、本 Task 自身无独立交付"；Resource Manifest 由伪造的自引用 `doc/tasks/P15-CORE-1.md` 改为真实 `verification/P15-CORE-1/resource-manifest.json` | 治理定向检查 PASS（§3）；manifest 文件存在且 JSON 可解析 |
| R1-03 | P19-AC3-1 限制说明把 AC1/AC2/AC4 一并写成"由后续 SEC/P15-HOST 系列承接"；实际只有 AC2 有专项修复 | 精确为：仅 AC2 由 `SEC-FIX-PATH-ECHO-1`（`done`）修复；AC1 未知顶层 key、AC4 错误投影未修复且未找到专项承接 Task，保留为已知产品缺陷（未复测） | 治理定向检查 PASS |
| R1-04 | P19-UI-FIX-3 只说"由 FEAT-CREATE 链覆盖"，未明确 AC5/GUI 证据归属 | 补充：`FEAT-CREATE-4` AC6 含真实 GUI/UIA 复验（空书架新建 → 建章节 → 导入入口转可用），覆盖本 Task AC1–AC5 目标；本 Task 自身未执行 | 治理定向检查 PASS |
| R1-05 | GOV-DEBT-CLEANUP-1 的 `superseded` 可能被读成"已完成" | 明确：AC1 完成；AC2/AC3/AC4/AC6 未全部完成；AC5 零触碰；`GOV-DEBT-CLEANUP-2` / `GOV-UNTRACKED-BACKLOG-1` / `GOV-PIN-LINEAGE-1` / `GOV-EVIDENCE-DIR-SWEEP-1` 仅部分承接；剩余历史证据保留、不再阻塞 v1 | 治理定向检查 PASS |
| R1-06 | RUST-ENV-BASELINE-1 AC4 分类计数错误（原写 13+7+3=23，实际 22） | 修正为 **12** 项 packaged 环境门卫 + **7** 项 ACL/计数漂移 + **2** 项 worker-registry 并行污染 + **1** 项 `M2RC1_PYTHON` 未设置 = 22；补充 EOL/pin 修正说明 | 与 `cargo-test-full.log` 失败清单逐项复核：`packaged_sidecar_tests::*`=12、`tests::*`=7、`library_bridge::*`=3 |
| R1-07 | Plan / STATUS / 台账未同步 P15、RUST 的最终状态 | Plan：`RUST-ENV-BASELINE-1` 从 proposed 组移出，改为 closed_with_limitations 节点；proposed 组仅余 P07/P21/tool-hardening。STATUS：`cancelled` 19→18、`superseded` 5→6。TASK_LEDGER 重生成 | 台账 322 files / 309 terminal / 13 non-terminal；治理默认 PASS |

原始裁定文档 `legacy-task-closure-adjudication.md` 仅**追加** §9 修正说明，原文保留。

## 2. 证据 pin 对照（旧 CRLF → 新 LF）

| 文件 | 旧 SHA-256（CRLF 工作区） | 新 SHA-256（LF，可复现） |
|---|---|---|
| `cargo-source-fixed.log` | `8f2f94684291117b5eb5e04479175aa19e5758e5d2cf7253e99975e55366994e` | `bc0d3b4bdf9f84609d5653ffddce78bb6bd8f9f266fd23f398f2e871e3302b42` |
| `cargo-packaged-fixed.log` | `c83ee5828c31d9220bf4211618dc232fbe30d17b7f1f311c710ea420cf5a26c3` | `90f0d62738bebbc59196fbe230f8b978e2c541181def5bf30862f0360b755ddd` |
| `vitest.log` | `de1bb344dd99678056b344e145783b41ac4f77a58f6135ef328592a0822372a7` | `374378e58d19a47730b43d73c7363d2b4bd94159f6088d3d3c92a9adc4494652` |
| `pytest-m2.log` | `a3a074188908f523411bb54c127fb9ddb4f746c11852a75b0d0c1a33e973b657` | `86e84af0a51cc53553e05fae33a80e8839a72e7833b69a1778c3df13340f4af4` |
| `tauri-build-installer.log` | `7fa190f4c05ed2bf439def9e3b870a0367149a52433e8a8936344d23d504b007` | `b042fa7ce560dc353ce5218ec101e910a8b69bf8a99a94d6a069d417b69c0cd4` |
| `sidecar-build.log` | `c9e29c32f856083c2e8833dcd7847ea157dfaa3b916bf19e94d31468452140a3` | `a2a50b3c88a7605a52947756024ec805ace36adbf6ac4fbd11f1cac144d2f276` |
| `frontend-build.log` | `8039ccb0ce829811075d16940d0c36bd1e75d97205c3821eca32ebc70ba7f1c6` | `29868ad9b003e04e619571546598c195ffba187015410645c677d01ba92a955c` |
| `npm-ci.log` | `a36e1aad0294731fdcb15139368c3d680ee4398c9484ca917fcc43c17b8d9785` | `0ed44d6c754e05d9f46bfe41ca8fb9b3e565692373c495ce4a219a3cca92e060` |
| `cargo-test-full.log` | `55d01b23ef6c04320651cc656d7c46569ccf04f725baa7200d5011a2a09e170e` | `0803303ba0a0e671cb523e1d5306c78049946044e521bf4c1dbba2bcfb70e778` |
| `cargo-test.log` | `1e0a05b92a88741775a89c8bba0b9fb46cdf8532bb9f214b221ac223da59ca71` | `c588edf7036e543c2c1311e60a039029ada7609cc969a8042d0b1fa912255cf5` |
| `legacy-task-closure-adjudication.md` | `798e25a2c3d6adee17edf463eebc5bce3dc1dc1a69516df58cae20eef5a89370` | `089b25505a81a7fbb69f01f89a00a593d04962b0c5750cff58a0e903353f9212` |
| `.gitattributes` | （新增） | `abf835c828cacebff6df5c223e8db57b972a3404aba941ef18718286f5d29383` |
| `v1-verification-20261021.md` | `5b39fde0921a11a9dd7b1b31015fa7c250d3ab0a5078b29113d168651fc64e0e` | （未变，原本即 LF） |

日志文本内容未改：10 个日志与 `v1-verification-20261021.md` 在 `a689a1ec2..9f5262f19` 间 `git diff` 为空；`legacy-task-closure-adjudication.md` 仅按裁定要求**追加** §9（原文逐字节保留，新增 10 行）。`git diff a689a1ec2..9f5262f19 -- verification/V1-FINALIZE-20261021/*.log` 为空。

## 3. 验证记录（明确退出码）

### 3.1 台账

```
python tools/governance/task_ledger.py --write
task files 322; terminal 309; non-terminal 13 (tracked 2, untracked drafts 11)
by status: done 251, closed_with_limitations 34, cancelled 18, superseded 6, blocked 7, in_progress 2, in_review 2, proposed 2
exit=0
```

### 3.2 治理检查（全部 PASS，每项 3 warnings）

| 检查 | 退出码 | warnings |
|---|---|---|
| 默认（`check.ps1`） | 0 | 13 个非终态；STATUS 3041 B/26 行；Plan 6469 B/56 行 |
| `-TaskPath doc/tasks/RUST-ENV-BASELINE-1.md` | 0 | 同上 3 项；**无** evidence_dir 未登记文件 warning（修正前存在） |
| `-TaskPath doc/tasks/P15-CORE-1.md` | 0 | 同上 3 项 |
| `-TaskPath doc/tasks/P19-AC3-1.md` | 0 | 同上 3 项 |
| `-TaskPath doc/tasks/P19-UI-FIX-3.md` | 0 | 同上 3 项 |
| `-TaskPath doc/tasks/GOV-DEBT-CLEANUP-1.md` | 0 | 同上 3 项 |

原始输出：`verification/V1-FINALIZE-20261021-rework-r1-governance.txt`。

### 3.3 pin 检出可复现性

| 验证 | 命令 | 结果 / 退出码 |
|---|---|---|
| 归档提取 pin 匹配 | `git archive --format=tar -o ... HEAD verification/V1-FINALIZE-20261021` → `tar -xf` → 逐行比对 `RUST-ENV` 13 个 pin | **13/13 匹配，0 个 CRLF**；archive exit 0、tar exit 0 |
| 不同 autocrlf | `git -c core.autocrlf=false archive ...` 同上 | **13/13 匹配**；exit 0 |
| 历史 commit-pin 抽样 | 对 `P19-AC3-1` 17 行执行 `git cat-file blob <commit>:<path>` 并 SHA-256 | **17/17 匹配**；exit 0 |

## 4. 未做 / 未声称

- **未**把 dsh 日志当作独立复跑：v1 测试结果仍是 2026-10-21 00:29–00:50 的原始运行，本报告只修复证据表示与 pin。
- **未**重跑产品测试、未重建安装包（用户范围：不改产品代码；v1 产物 SHA-256 未变：`b0ad46f5…38c7b`）。
- **未**触碰 11 个 untracked 历史草稿（`P02PRE-*`、`P22`）；untracked 总数保持 1244。
- **未**删除旧 hash：对照保留在 §2；原始日志在 Git 历史与工作区均未删除。
- 本报告提交后才产生最终固定 head（父提交 `9f5262f19`）；Codex 复核见 §5–§7。

## 5. Codex 独立复核 r1（2026-10-21）

- 复核 head：`1fae46e991b9b462461ebeae05d9dc4954f49d01`；会话 `01a15bf2-5e2f-7c42-9d03-845b6e47ff34`。
- 结论：**`approved_with_conditions`**。A/B/C/D 四项均通过；唯一 finding **R1-REVIEW-01（low）**：A 项验收表述需精确——12 个日志/文档中实际是 **10 个日志 + `v1-verification-20261021.md`** 无 diff，`legacy-task-closure-adjudication.md` 按 B 要求仅追加 §9；不能笼统写"12 个文件 diff 为空"。
- 条件修正：仅改本报告 §2 的上述表述（见本提交）；**未**改代码、证据、pin、日志或裁定原文。已据此更新本报告。
- Codex 裁定："可以据此裁定最终收口（V1 完成 + 25 个 Task 收口 + r1 返修）"，条件是接受 §9 追加并修正该表述；产品功能与本轮测试未重新运行或复审（超出本轮复核范围）。
- 原始复核报告：`verification/V1-FINALIZE-20261021-codex-review-r1.md`。

## 6. 最终收口裁定（2026-10-21）

- Codex 对返修提交 `1fae46e99` 给出 `approved_with_conditions`，唯一条件 R1-REVIEW-01（A 项 12 文件表述）已在 `2982851df` 修正并入库原始复核报告。
- Codex 在 `2982851df` 上复核确认：**decision `approved`**，条件已满足、无新 finding；治理默认与 5 个受影响 Task 定向检查全部 PASS（各 3 warnings）；台账 322/309/13。
- **最终裁定**：接受 **V1 完成 + 25 个 Task 收口 + r1 返修通过**；无新增实现 Task。最终固定 head 为本裁定提交的 HEAD（父提交 `2982851df64c641b25929a18d9cbb9b407b7a269`）；确认报告见 `verification/V1-FINALIZE-20261021-codex-review-r1-confirm.md`。
- 未声明：产品功能/测试未在本轮重跑（v1 原始运行证据仍为 2026-10-21 00:29–00:50）；安装包仍为未签名，未做全新机器安装复验。

## 7. 最终收口复核确认（2026-10-21）

- Codex 对最终裁定 head `48cf5085a4f0d50af16e54fc5375cc674079ba71` 完成独立只读复核：**decision `approved`，findings 无**；接受该 head 为 **V1 最终收口 head**，建议最终集成。
- 核验：`2982851df..48cf5085a` 仅 3 个文档；产品路径 diff 为空；`git diff --check` exit 0；台账 322/309/13；默认 + 5 个定向治理检查全部 PASS（各 3 warnings）；V1 pin 13/13、P19 commit-pin 17/17；0 tracked dirty、1244 untracked（草稿未动）。
- 结论：**V1 完成 + 25 个 Task 收口 + r1 返修 + 最终复核全部通过；无需额外 merge 或新增实现 Task。** 原始报告：`verification/V1-FINALIZE-20261021-codex-review-r1-final.md`。
- 本 §7 及复核报告入库提交为 docs-only 记录；被批准的最终集成点仍为 `48cf5085a`。
