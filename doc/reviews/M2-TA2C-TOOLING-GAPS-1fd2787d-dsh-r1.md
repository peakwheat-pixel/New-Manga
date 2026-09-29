verdict: approved（0×P0/P1/P2；7×P3，均非阻塞；AC1–AC5 全部 PASS。本次为只读静态审查，未写入任何文件）

# M2-TA2C-TOOLING-GAPS 独立非作者静态 Review（对象 head=a164e414，交付文档头=1fd2787d）

## 0. 取证基础与沙箱局限（先说清楚）
- 本会话 `pwsh` 不可用：每次调用返回 `Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)` → **未能独立复跑 pytest / CLI**；按派发说明，集成方已复跑 `pytest tests/m2_test_assets` 34 passed EXIT=0、`git diff --check` EXIT=0。以下结论全部由 read/glob/grep + `.git` 明文取证。
- Git 明文取证（可直接复核）：
  - `G:/CODEX/New Manga/.git/HEAD` → `ref: refs/heads/main`；`refs/heads/main` = **f3d684eb**（= 本次 base）→ 主工作区树可作 base 对照，我用它做了逐文件 base/head 比对。
  - `.git/worktrees/M2-TA2C-TOOLING-GAPS-zcode/HEAD` → `ref: refs/heads/agent/zcode/M2-TA2C-TOOLING-GAPS`；该 ref = **1fd2787dc3f69fc7e05112697409f88a61e4e18a**（与声称的交付头一致）。
  - `worktrees/.../logs/HEAD`（reflog）确认提交链：`f3d684eb → 19f8200e（claim）→ a164e414（实现）→ 1fd2787d（交付文档）`，与 Task/Handoff 声明逐字一致。
  - `.git/refs/heads/master` 另存 78faeee5（非本次相关），排除误用 master 作 base 的可能。

## 1. P0–P3 问题清单（file / 位置 / 问题 / 建议）
**P0：无。P1：无。P2：无。**

- **P3-1｜`test_assets/comic_golden_suite/tools/assets.py:252-255`｜非字符串非空值静默跳过（fail-open）**：`if not isinstance(raw, str) or not raw: continue`。若 `checksum_inventory` 被写成 `0`/`[]`/`{}`，既不报 failure 也不计入 `checked`，且测试端 `benchmark_inventory_params()`（`tests/m2_test_assets/test_catalog.py:89-95`）同样过滤 → “所有非空 inventory 路径必须存在”这条 AC 在类型错误数据上静默失效。建议：`raw is None → continue`；`not isinstance(raw, str) or not raw → failures.append(f"{source_id}: invalid checksum_inventory value")`；或在 `load_manifest` 内补 `benchmark_sources[*]` 轻量 schema 校验。
- **P3-2｜`assets.py:264-266`｜符号链接校验弱于被仿写的兄弟函数**：只判 `candidate.is_symlink()`（叶子），缺 `resolve()` 后的 `is_relative_to(REPO_ROOT)` 包含性检查；`verify_inventory_files()`（`:213-220`）是两者都做的。中间目录为 symlink 时可指向仓库外“存在”文件而不报 unsafe。Handoff 第 17 行的“拒绝 … symlink”表述因此略强于实现。建议对齐 `verify_inventory_files()` 的 resolve+containment。
- **P3-3｜`assets.py:243-273` + `README.md:12`｜“local_asset_inventory.json 条目沿用逐文件 SHA-256 复核”是机制耦合而非身份绑定**：哈希复核实际由 `verify_inventory_files()` 按模块常量 `INVENTORY_PATH` 完成；`verify_benchmark_source_inventories()` 本身只做存在性。若某日清单该字段改指另一份“已存在的 JSON”，命令仍输出 `checked=N failures=0`，该条目实际无哈希复核。建议函数内显式断言该相对路径等于 `INVENTORY_PATH.relative_to(REPO_ROOT)`，或对非该文件的条目在注释/输出中明示“仅存在性消费”。
- **P3-4｜`tests/m2_test_assets/test_catalog.py:158-159`｜JA 命名快照只钉 J38–J40**：raw/03 显示 JA smoke 实为 J38–**J47**（10 例，全在 `日漫_JA/02_open_ground_truth_peppercarrot/{ep04,ep20}`），J41–J47 的 `local_path` 漂移不会被捕获。建议改为全枚举/集合断言。
- **P3-5｜`verification/M2-TA2C-TOOLING-GAPS/raw/07-ac5-diff-check-and-scope-proof.log:3`｜`git diff --check` 判别力为零**：该行自述 “empty diff at implementation HEAD”，即在干净工作树上跑，只证明了工作树无未提交改动，对提交区间 `f3d684eb..a164e414` 无空白/范围判别力（真正的校验是集成方复跑的 range 版）；且该 log 未保存 `git diff --name-only base..head`，使“仅 4 路径”的 scope 声明缺一手清单。建议后续日志直接记录 range 级命令。
- **P3-6｜`assets.py:883-895` + `README.md:12`｜仓库级前置校验不受 `--language/--case-id` 限制**：`verify/list/missing` 无条件消费全部 `benchmark_sources`，定向命令（如 `verify --case-id K11`）也会因无关 inventory 失败；`missing` 的退出码语义由“案例缺失不失败”扩展为“仓库级 inventory 失败即 1”。README 已说明其失败性，建议再显式写“不受 --language/--case-id 限制”。
- **P3-7｜`assets.py:44-58`｜畸形端口的异常未归入白名单错误路径**：`https://huggingface.co:abc/`、`:99999` 由 `urlsplit`/`.port` 直接抛 `ValueError`（fail-closed 保留，但消息不是 whitelist 文案），单测只覆盖 2 例且都用 `match="whitelist"`。建议把 `.port` 访问包进 try 并统一为同一 ValueError，或补端口非法用例。

正面确认（非问题项，但属审查要点）：
- `cases.json` 白名单集合与数据完全一致：我逐行核对全部 68 个 `source_url`，仅 `huggingface.co` 47 + `www.peppercarrot.com` 21（=68）；`manga109.github.io` **确实不出现在任何 case 的 `source_url`**，仅出现在 `download_sources.manga109.official_project_url`（cases.json:338）与 README:79 —— 编排预期的第 3 host 属字段混淆，作者的 2-host 冻结是正确的“以数据为准”选择（未来新增 host 会 fail-closed，README:11 已声明需显式扩常量）。
- `validate_source_url` 的绕过面已查：`host@evil`（`hostname` 取最后一个 `@` 后段→拒）、`evil\@huggingface.co`（`username` 非空→拒）、`huggingface.co.evil.com`/`evil.huggingface.co`（精确成员→拒）、大小写（`hostname` 归一为小写→通过）、非 443 端口（拒）、缺 host/非 https（拒）；`is_public_comic_url`、`PUBLIC_COMIC_HOST`、`validate_public_profile` 未被改动。
- `download` 分支与 base 逐行一致；`status()`、`verify_inventory_files()`、`print_cases()`、`is_public_comic_url()` 与 base 完全相同（仅 `verify_inventory_files` 调用点新增消费），改动面确为“新增函数 + 3 处挂接 + 文档”。
- 判别力真实：base（f3d684eb，经主工作区实读）`load_manifest` 无任何 host 校验 → raw/02 的 RED 声明与代码事实吻合，GREEN 文案与实现字符串逐字一致（`source_url host is outside the approved whitelist: K01`）；AC3 演示对“变异副本”断言 `failures == [期望单条]`、`checked == healthy-1`，是真实判别而非同义反复，且新参数化断言使“路径漂移”从“无测试变红”变为必红（修复了 r2 P3-10）。

## 2. 缺失证据（如实登记）
1. **无 `git diff --name-status/--stat f3d684eb..a164e414` 原始清单**：raw/07 只有 `git status --short` + untracked 列表 + 空树 `diff --check`，因此“仅 14 允许路径”依赖集成方复核 + 我的抽查（见 §3 AC5）。未发现越界证据，但缺一手清单。
2. **raw/01、02、08 只保存结论行**，未保存 heredoc 脚本本体与完整 stdout（raw/02 新旧版各 1 行结果），因此这三个演示不可字节复现；静态可复核（base 无校验、错误串一致），且 AC1/AC3 的判别力已由单测独立承载。
3. **未由我独立复跑** `pytest tests/m2_test_assets` 与 CLI 六命令（沙箱无 shell）；仅消费作者 34 passed EXIT=0 日志与集成方复跑结论。
4. **AC2 的 `INVENTORY checked=92` 不可由分支 clean checkout 复现**：依赖从主工作区只读复制的 96 个 gitignored 媒体（JA 12 + KO 4 + KO webtoon 80），Task/Handoff/log 头均已如实披露（`.gitignore`：`韩漫_KO/.gitignore:1:/*`、`日漫_JA/.gitignore:1:/*` + 图像/压缩包排除）；96 文件的 `git check-ignore` 原始输出未入新日志（raw/07 的“零媒体污染”status 输出可作替代佐证）。
5. `tests/m2_acceptance`、`download` **NOT_RUN**，Task:76 与 Handoff:43-48 已如实标注，不属本 Task 范围。
6. `verification/M2-TA2C/ko-webtoon-audit.json` 为 tracked（主工作区与 worktree 两侧均存在；worktree 不继承未跟踪文件）→ 参数化断言与 `verify` 在干净 checkout 下仍可绿；但我无法用 `git ls-files` 直接取证其 tracked 状态，仅作强推断。

## 3. AC 逐项裁定
- **AC1 主机白名单 — PASS**。`SOURCE_URL_HOSTS`（assets.py:37-41）+ `validate_source_url`（:44-58）+ `load_manifest` 挂接（:92）实现与方案冻结一致（显式常量、无网络、fail-closed）。白名单集合经全量数据核对正确且完整（47+21=68），`manga109.github.io` 仅存在于 `official_project_url` 字段，“未纳入”属数据驱动正确决策并在 Task:36/Handoff:16,73/README:11 三处披露。base 无任何 host 校验（主工作区实读 `load_manifest:38-90`）→ 红演示可信。新增 2 条参数化单测（evil.example https + 同 host http 降级）覆盖拒毒与降级。
- **AC2 inventory 运行时消费 — PASS**。`verify_benchmark_source_inventories()`（:243-273）做仓库根相对安全路径校验（`\`/`:`/drive/绝对/`..`/归一化）+ 存在性；`verify`/`list`/`missing` 统一挂接（:884-895），新增 `BENCHMARK_INVENTORY checked=N failures=M`、`INVALID_BENCHMARK_INVENTORY`、`SUMMARY FAILED` 且 failures→return 1；`download` 未触碰。ja/ko smoke EXIT=0、READY=10、`INVENTORY checked=92 missing=0 failures=0`、`BENCHMARK_INVENTORY checked=4 failures=0`，list READY=20，三份日志头均带 `HEAD=a164e414` 与 `# EXIT=`（证据纪律合格）。哈希复核语义见 P3-3（今日数据下成立：3 条 local_asset_inventory.json 字面值由既有测试锁定为 `INVENTORY_PATH` 的仓库根相对形式）。
- **AC3 判别性断言 — PASS**。`test_benchmark_checksum_inventory_paths_exist` 参数化恰好 4 条（=4 个非空条目，覆盖 ko_sfx）；`test_benchmark_inventory_missing_path_detection_demo` 断言 real 全绿 + broken 单条 failure + `checked` 递减，与 raw/08（REAL checked=4 failures=[] / BROKEN checked=3 failures=[missing: verification/M2-TA2C/does-not-exist.json]）逐字一致；参数化在收集期调用 `load_manifest`（损坏清单=collection error，fail-closed，Handoff:75 已披露）。类型边界见 P3-1。
- **AC4 命名快照 — PASS**。`cases.json` base 4369 行 → head 4380 行 = **恰好 +11 行**；3 处锚点交叉验证为纯插入（base:1549 = head:1557 Manga109 首条 `source_url`；base:4251 = head:4259 K11 `source_url`；文件尾 +11），插入位置均为各 case 对象最后一个字段（`source_id` 之后），11 个 case 与 grep 到的 11 条 `naming_note` 一一对应；**既有字段值零变更**（含 ko_sfx `checksum_inventory`：base:161 已是 `verification/M2-TA2C/ko-webtoon-audit.json`，与“实测非 null、非本次改动”相符）；未重命名任何盘上目录；快照断言（test_catalog.py:143-159）钉住 O01–O08/K11–K13/J38–J40 前缀并校验 `naming_note` 存在。唯一不足见 P3-4。
- **AC5 范围与证据 — PASS（带证据等级注记）**。34 passed EXIT=0 日志含 18 个 def / 22 个 test item（13 旧 + 5 新 def = 9 新 test item），与“新增 9 测试”完全吻合，旧断言逐行未削弱（base `test_catalog.py` 279 行内容在 head 中 1:1 保留）；`test_public_assets.py` 两侧同为 283 行（未改）。范围：4 个允许代码/数据文件 + Task + Handoff + 8 个 raw 日志 = 14 路径，与集成方复核一致；我另抽查 README 差异仅 3 处（:11 白名单句、:12 运行时消费句、:18 新增 naming_note 条目），无越界迹象；素材零改动与 git 零污染由两侧 `.gitignore` + raw/07 status 佐证。证据等级瑕疵见 P3-5（作者的 `diff --check` 为空树跑，已由集成方 range 复跑补强）。

## 4. 结论与建议
- 实现与冻结方案、AC1–AC5 与证据对应关系成立；两处“侦察偏差”（白名单 2 host、ko_sfx 非 null）均按预案处置并如实上报，未越权改 cases.json 既有值——处置正确。
- 建议（不阻塞集成）：P3-1/P3-2 可在集成前一并加固（各约 3–6 行 + 或 1 条测试）；P3-3/P3-5/P3-6 建议登记为后续证据/文档 Task；P3-4 建议顺手把 JA 快照扩到 J38–J47；P3-7 可选。
- 我未在作者 worktree 或主工作区写入任何文件（避免污染作者 `git status` 与 master 树）。本报告如需入库，建议由 Codex 在集成/review 树落为 `doc/reviews/M2-TA2C-TOOLING-GAPS-a164e414-dsh-r1.md`（内容即本文）。
