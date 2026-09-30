## approved

（M2-TA2B DSH r2 限定复核：实测 r1 条件全部关闭，0×P0/P1/P2；新增 6 项 P3 记录，均不阻断集成）

---

### 复核方式声明

- **本轮为「限定复核」**：只核对 r1 条件闭合，不重审全量；所有结论以当前 HEAD 实体文件 + 入库日志为准，并以**独立复算**（字节求和、哈希前缀/长度、计数、映射关系）交叉验证，而非采信 commit/Task 自述。
- **执行能力受限（必须声明）**：本会话 `pwsh` 完全不可用——沙箱在 workspace-write 下授予工作区写权限失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-TA2B-OPEN-ASSETS-zcode)`），`danger-full-access` 升级因无审批通道被拒。因此 **无法执行** `pytest`、`fetch_bj.py verify`、`git log/diff/status`，也**无法重跑**任何命令；本轮为**纯静态核验 + 日志证据复核**。相应地：返修 diff 的字面内容（`9db2dca8..118b4df3` 逐行差异、`a93a61f3`→`118b4df3` amend 轨迹、`31dcbde0` 与 `118b4df3` 的对象存在性）**未能独立验证**，仅以 ac6/ac8 日志 + 当前树内容间接佐证。
- 可读资产已用只读方式消费：`test_assets/comic_golden_suite/**`（含 gitignored 素材本体）、`tests/m2_test_assets/**`、`doc/tasks|handoffs/**`、`verification/M2-TA2B/**`（14 份日志）、6 份 BJ manifest，并**自行打开 BJ04 渲染页像素**核对标签依据。
- 未修改任何文件。

---

### 复核点逐项

#### 1. P1-1（OpenMantra 三处登记）— **closed**
- README `:35`：13 个文件（annotation/LICENSE/README + 10 张样本 ja 页，2,341,834 bytes）、`日漫_JA/99_optional_openmantra/`、`READY_OPTIONAL_ISOLATED`。
- `local_asset_inventory.json:630-648`：`status=READY_OPTIONAL_ISOLATED`、`file_count=13`、`image_file_count=10`、`byte_size=2341834`、`local_path` 一致，并新增 `inventory_tracking: excluded_optional_noncommercial_checksums:648`；`files: []` 与该标记自洽（`assets.py:198-242` 只遍历有 `files` 的条目，故不计入 110）。
- `cases.json:198-229`：同 status / 同 local_path / `local_file_count=13` / `byte_size=2341834` / `image_redistribution_status` 明写「gitignored isolated directory … 13 files … excluded from Git/生产许可基线/levels」。
- **独立复算**：磁盘实际 13 个文件（3 顶层 + 10 图，glob 确认）；把 `ac5b:2-14` 的 13 个字节数逐项相加 = **2,341,834**，与三处登记完全一致；ac5 与 ac5b 的 13 个 SHA-256 逐一相同（含我一度怀疑行长的 `tojime_no_siora/000.jpg`，用 `sha256=[0-9a-f]{64}` 正则确认 13/13 均为合法 64 hex）。
- 第 4 处（`doc/tasks/M2-TA2B.md:113`）亦一致。**三处（+1）与实况无矛盾。**

#### 2. P2-1（BJ 完整性路径 + asset_status 语义）— **closed**
- **代码实证**：`fetch_bj.py:407-443` `verify_rendered_pages()` 真实消费 `assets.load_manifest()`，按 `case_id` 过滤 `BJ\d{2}`，读 `page_file`/`page_sha256`，对 `assets.ROOT/local_path/page_file` 重算 `sha256_file()` 并逐页比对；缺失/不匹配→`VERIFY_FAILED`，`failures>0 → 返回 1`。**是对 cases.json 注册哈希的真对比，不是自述。**
- **日志**：`ac7b-fetch-bj-verify.log` 头 `HEAD=118b4df3…`，BJ01–BJ12 全 `VERIFY_OK`，`SUMMARY cases=12 failures=0`、`# EXIT=0`。我另把日志中的 size/哈希前缀与 6 份 `bj_*_manifest.json` + `cases.json` 三方对照：BJ01 `ff3365868f3402b0`/10512311、BJ04 `42dabc22dacaa6c8`/2657459、BJ07 `cba84cdbfba27f6b`/113664、BJ12 `a314450f63807b40`/2822828 **全部一致**。
- **README 登记为门槛**：`README:42` 明写「BJ 渲染页的自动完整性校验走 `python …/fetch_bj.py verify`（对照 cases.json 的 `page_sha256` 逐页重算，**12/12 为绿色门槛**）」；`cases.json:343` `checksum_note` 同口径。
- **asset_status 语义处置**：采用约定方案——保留快照 `asset_status: READY`，不删字段，并同时具备 ①`README:14`「status/asset_status 是快照；运行时以 CLI 计算为准」②`README:7` READY 定义 ③`README:42`「上述 READY 只表示资产文件状态」。实证 CLI 口径：`ac7d:49-60` BJ01–BJ12 运行时为 **PARTIAL**（`assets.py:162-163`：`manual_source_page` 只在文件存在时给 PARTIAL，无 READY 态），与 cases.json 的 READY 快照并存但被上述规则覆盖。**该处置可接受**（仅余一条 P3 文档建议，见 N-6）。
- 残留（不构成 open）：verify 仍属**手动 CLI 门槛**，未接入任何自动化 runner（像素 gitignored，CI 无法承载）；属结构性限制而非条件未闭。

#### 3. P2-2（source 计数 / BJ 条目 / ko 合并口径）— **closed**
- **ja**：`cases.json:172-196` ＝ 15 图 / 17 文件 / 42,126,680 B；inventory `peppercarrot_e04_ja`(9 文件/8 图/17,782,135) + `peppercarrot_e20_ja`(8/7/24,344,545) ⇒ **17 文件、15 图、42,126,680 B 逐位吻合**。
- **ko**：`cases.json:232-254` ＝ 15 图 / 17 文件 / 42,097,368 B；`peppercarrot_e04_ko`(9/8/17,757,746) + `peppercarrot_e20_ko`(8/7/24,339,622) ⇒ **17/15/42,097,368 吻合**；`notes` 的 E04(K11–K18)+E20(K19–K25) 与 cases 映射一致。
- **black_jack_official_free 完整性**：`cases.json:329-353` 含 id/source/source_name/status/optional/license/license_class/attribution/image_redistribution_status/local_path/local_file_count/local_image_file_count/byte_size/checksum_inventory/checksum_note/ground_truth_types/pipeline_applicability/pipeline_status/notes。**独立复算**：文件数 3 ZIP+3 PDF+12 PNG=18 ✓；字节 = 1,068,836,615（3 ZIP，与 README:27 一致）+1,108,536,976（3 PDF）+73,999,349（12 PNG）＝ **2,251,373,940 ✓** 与登记一致；`checksum_inventory: null` + `checksum_note` 指向 verify 路径，语义自洽。
- **ko 合并口径偏差**：**可接受**。与 ja 侧结构对称（同一父目录、跨 episode 合并、`local_path` 从 ep04 目录升为族目录）；`benchmark_sources[*].local_path` 无任何消费方（`assets.py:245-259` 只读 `checksum_inventory`），改动对工具链惰性；episode 级拆分仍由 inventory 两条目 + notes 保留。
- 计数类残余（P3）：新 source 未带 `redistributable` 字段；ko `ground_truth_types` 为 `svg_text_layer` 而 ja 为 `svg_text_layer_partial`（非矛盾，措辞不对称）。

#### 4. P2-3（12 处 /ko/→/kr/）— **closed**
- 全仓 `peppercarrot.com/ko` / `/ko/webcomic` grep **0 命中**。
- K14–K25 的 `source` 共 12 处（`cases.json:5545,5595,5645,5695,5745` 为 ep04×5；`5795,5845,5895,5945,5995,6045,6095` 为 ep20×7）**全部 `/kr/webcomic/…`**；连既有 K11–K13 共 15 处 kr 全部正确；`ac7d` K14–K25 全部 READY。
- 附带核实：`cases.json:5295-5523` 的 J48–J52 为 ja 侧 ep04（`source_id` E04P00/P01/P04/P07/P08），与 README:42「5 张 ja 页」、Task:112「ja E04×5」、`ac4` `downloaded=18` 完全自洽 —— 我先前怀疑的「ja 新增页归属」经 J38–J40(E04P02/P03/P06)、K11–K13(E04P02/P03/P07) 映射与 inventory 旧值反推后**排除**。

#### 5. P2-4（fetch_bj 单测判别力）— **closed（附 P3 覆盖精度问题，见 N-3）**
`tests/m2_test_assets/test_fetch_bj.py` 7 个用例，全部离线（monkeypatch `build_opener` + `OUTPUT_DIR=tmp_path`），**不触网、不依赖真实素材**（`main()` 路径亦被 OUTPUT_DIR/argv 隔离）。逐个「删掉防护是否变红」判定：

| 用例 | 删防护后 | 判定 |
|---|---|---|
| redirect_to_foreign_host | `build_opener` 被整体替换为 `FakeOpener`，**RedirectGuard 从未被构造**；删 guard 仍绿 | ✗ 无判别力（名字高估覆盖） |
| missing Content-Length | `int("not-a-number")`→ValueError 逃出→红 | ✓ |
| oversized declared size | 删 600MB 上限后仍走 `incomplete download`→同样抛 `OSError("download failed")`→绿 | ✗ 弱（只证「不发布」） |
| non_zip_payload_never_published | 删 `valid_zip` 校验即发布→`pytest.raises` 红 | ✓ |
| valid_payload_publishes_atomically | 原子发布/hardlink/`.part` 清理任一坏→红 | ✓ |
| __MACOSX AppleDouble 跳过 | 删跳过→`expected exactly one PDF member`→红 | ✓（正对 vol05 真实缺陷） |
| JASRAC 2/7/11 拒收 | 删策略→`main()` 返回 1/SystemExit≠2→红 | ✓ |

结论：**5/7 真判别力**，P2-4 的「零覆盖」实质已闭（含真实缺陷回归），但 Task:131/Handoff:83 的「跨 host 重定向拒」并无有效覆盖。

#### 6. P2-5（AC6/AC8 归档证据）— **closed**
- **ac6**：方法与结论为「对 base `9db2dca8` 做程序化字段级比对，允许 delta 逐类显式枚举」。我**独立复算其全部关键数字**：新增 29（BJ12+J5+K12）✓、既有 68（31 unchanged + 37 cancel-flag）✓、68+29=97 ✓、`sources.peppercarrot` ja 10→15 / ko 3→15 ✓、ja 12→17/40,284,868→42,126,680 ✓、ko 4→17 / 3→15 / 1→2 / 16,292,579→42,097,368 ✓、`generated_from` 后缀 ✓、levels 68→97 ✓（我另证 97 个 case 全部含 regression）。结论 `ZERO_CHANGE_VERIFIED` 与当前树一致。
- **ac8**：头 `HEAD=118b4df3…`，`git diff --name-status 9db2dca8..HEAD` 覆盖**全范围**共 19 条，**`src/**`、`apps/**`、`packaging/**` 零命中**；`check-ignore -v` 命中 `日漫_JA/.gitignore:26/27`（BJ 目录、OpenMantra 目录）；`# DIFF_CHECK_EXIT=0`。
- 残留（P3）：①ac6 无 `# shell=/cwd=/HEAD=/cmd=` 头与 `# EXIT=` 尾（其余 13 份日志都有），且是可复现脚本缺位的叙述型日志；②ac8 审计范围止于 `118b4df3`，交付 commit `31dcbde0`（doc + 5 日志）在范围之外（其自身 `git status` 如实标注 3 份日志未 tracked）。

#### 7. P2-6（BJ04 horizontal_text）— **closed（我做了独立像素复核）**
- 我**自行打开** `日漫_JA/01_black_jack_official/vol01/pages/vol01_p0209.png`（2946×4167，与 README:27 一致）：画面确含**横排副题「第一外科編」**与 6 条白色贴条上的**横排「GIVE / MY / REGARDS / TO / BLACK / JACK」**，另有竖排主标题「ブラックジャックによろしく」与「完全版／佐藤秀峰」小字。`cases.json:4674-4679` tags `vertical_text, low_contrast, huge_text, horizontal_text` + `feature_notes:4730`「vertical title + horizontal small labels」**与像素实况相符**；`orientation: vertical` 作为单一字段取主标题方向可接受。
- **断言集合同步**：`test_catalog.py:70-75` 的 BJ 标签并集断言包含 `horizontal_text`，而 grep 证明**全部 BJ case 中仅 BJ04 携带该标签** → 删除该 tag 必红，断言集与数据双向锁定；`horizontal_text` 也在 `cases.json:17` taxonomy 内（`load_manifest:81-82` 会拒绝未知标签）。

#### 8. P3 项
| 项 | 状态 | 证据 |
|---|---|---|
| P3-1 ac5b 日志 | **closed** | `ac5b` 头 `HEAD=118b4df3`，13 文件 SHA-256 + bytes + `SUMMARY files=13 bytes=2341834` + `EXIT=0`；与 ac5 逐值一致（独立比对，含 64-hex 正则 13/13 校验） |
| P3-2 计数勘误（7 份） | **closed（按效果）** | 我逐族复算全部关键计数：97=68+29、110=92+18、15/17 与 42,126,680 / 42,097,368、18=3+3+12 与 2,251,373,940、17 新页+1 ZIP=18、39→46 tests、12/12 verify、13/2,341,834 —— **无一冲突**。但「7 份」未逐项登记、r1 报告未入库 `doc/reviews/`，无法逐条对照（P3，见 N-7） |
| P3-3 KO ZIP 2 个 | **closed** | README:29「2 个官方 SVG language-pack ZIP（E04+E20）」；grep 全清单仅 `ep04_…lang-pack.zip`/`ep20_…lang-pack.zip` 两个文件名；inventory ko 两条各 1 ZIP |
| P3-4 官方署名格式+attribution_note | **closed（主干）/ 遗留见 N-1** | `fetch_bj.py:54` + `cases.json:336,4515…5283`（12 case + 1 source）均为 `ブラックジャックによろしく\u3000佐藤秀峰`（正则 `\x{3000}` 验证 17 处全用全角空格）；`README:73` 明写格式原样、`attribution_note` 另列；`test_catalog:62` 断言 note 含 densho810.com |
| P3-5 输入校验进 try + 死分支删除 | **closed（代码层）** | `fetch_bj.py:261-263` `is_allowed_archive_url` 校验确在 `try` 内；通读输入路径未见不可达分支（`volume<=0/>999` 守卫可达、`isdecimal`/上限/`written!=expected` 均可达）。**「删除了哪个死分支」无法 diff 复核**（声明见上） |
| P3-6 取消语义声明 | **closed** | `README:42` 末段完整：仅标注 `removed_from_scope_2026-09-30`、不参与可运行计数与选取、levels 历史定义不动，故 `--level full` 仍如实报 37×`MISSING_GATED_ASSET`（`ac7d:66` 实测吻合） |
| P3-7 COO 豁免说明 | **closed** | `README:42` 末句：`coo_and_manga109_dialog` 不打取消标注（已取得 CC BY 4.0 标注、不依赖 Manga109 像素）、保持 PARTIAL 可用；与 `cases.json:109-128` 一致 |

#### 9. 新问题扫描（返修是否引入新缺陷）
- **cases.json 大改未破坏既有数据**：`ac7d`（HEAD=118b4df3）ja `MISSING_GATED_ASSET=37 PARTIAL=12 READY=15`、ko `MISSING=8 READY=25`、`INVENTORY checked=110 missing=0 failures=0`、`BENCHMARK_INVENTORY checked=4`，与 r1 时点 `ac7-verify-ja-ko-full.log:66-68/104-106` **逐项完全相同**（64+33=97）→ 返修未改变任何既有 case 的运行态分布；`load_manifest` 全量 schema 校验（`assets.py:63-110`）由 46 passed 日志覆盖。我另独立确认 97 case × regression、smoke 20、taxonomy 16 项一致。
- **fetch_bj.py verify 路径拼接鲁棒性**：`fetch_bj.py:426-431` 的 `base = ROOT/local_path` → 先试 `base/page_file`，失败且 `page_file.startswith(f"{base.name}/")` 时退回 `base.parent/page_file`。当前数据（`local_path=…/vol01/pages`、`page_file=pages/vol01_p0001.png`）成立，但该「去重段」依赖**目录名与 page_file 前缀同名**的巧合；不成立时是 fail-closed（报 VERIFY_FAILED），**不误判为 OK**，故仅 P3（N-5）。另 `page_file` 未做 traversal 校验（`local_path` 有，见 `load_manifest:97-99`）。
- **新测试不依赖网络/真实素材**：已逐用例确认（tmp_path + FakeOpener + OUTPUT_DIR/argv monkeypatch；happy path 无网络；只有「删除 JASRAC 守卫」这一变异态才会触网，且会先 SystemExit/红）。测试导入路径沿用既有 `test_public_assets.py:11` 约定。
- 其余新发现见下。

---

### 新问题（P 级，全部 P3，不阻断）

| ID | P | 位置 | 事实与影响 | 建议 |
|---|---|---|---|---|
| N-1 | P3 | `verification/M2-TA2B/densho810-report-draft.txt:42`；6 份 `日漫_JA/01_black_jack_official/vol*/bj_{download,pages}_manifest.json`（各 `attribution` 行） | P3-4 只改了代码常量 + cases.json + README，**未回写**邮件草稿与磁盘 manifest：草稿仍写「ブラックジャックによろしく © 佐藤秀峰（densho810.com **経由**、二次利用フリー）」并声明「管理ファイルには下記の表記を記録しています」，而受管清单已改为官方格式；6 份 manifest 仍为「…**经由**…」旧串（下次 `fetch/render` 会自愈重写） | 用户发信前把草稿 `:42` 改为官方串或改为「Git 管理清单记录官方署名串；本地 manifest 为历史形态」 |
| N-2 | P3 | `cases.json:1197-1554`(O01–O08)、`4346/4399/4452`(K11–K13)；`test_catalog.py:254-256` | 既有 `naming_note` 文本仍写「K11-**K13** localized pages」，且新增 K14–K25 未携带该 note；README:19「已记录在相关 Case 的 naming_note 字段并由快照断言锁定」对新增 12 个同族 case 不再成立 | 把 note 文本扩为 K11–K25，并把快照断言范围同步到 K14–K25（或注明仅存量 case 打标） |
| N-3 | P3 | `test_fetch_bj.py:63-73`（及 `:87-95`）vs `doc/tasks/M2-TA2B.md:131`、Handoff:83 | Task/Handoff 宣称覆盖「跨 host 重定向拒」，但该用例把 `build_opener` 整体替换，`RedirectGuard` 从未被构造——删 guard 仍绿；超限用例在删上限后也仍绿（fallback 报错同文案） | 校正措辞，或补一条直接驱动 `RedirectGuard().redirect_request(...)`（或 `is_allowed_archive_url`）的判别性用例 |
| N-4 | P3 | `fetch_bj.py:340-377` | `render_volumes` 只对 `PdfDocument` 打开做 try/except；`len(pdf)` 或 `page.render` 抛错会绕过每卷 `failures` 统计直接冒栈（无 `RENDER_FAILED` / 非 `EXIT=1`）。r1 实现即如此，**非本轮引入** | 把渲染循环纳入 per-volume try，统一 `RENDER_FAILED` |
| N-5 | P3 | `fetch_bj.py:426-431` | verify 的「去重段」路径回退依赖 `base.name == page_file 前缀` 的巧合；`page_file` 未做 traversal 校验（fail-closed，无静默误报） | 用显式约定（如 manifest 记录 `page_rel_to_suite`）替换启发式；对 `page_file` 加 `..`/绝对路径拒绝 |
| N-6 | P3 | `README:14/42`、`ac7d:49-60` | 快照 `READY` 与 CLI `PARTIAL` 的并存只用通用句覆盖，未点明 BJ 因 `asset_profile.kind=manual_source_page` **结构上永不出现 READY** | README BJ 行加一句示例说明，避免读者据 `ac7d` 判 README 失实 |
| N-7 | P3（记录） | r1 报告与 P3-2 清单 | `doc/reviews/` 无 `M2-TA2B-*-dsh-r1.md`；Task:131 的「P3-2 计数勘误（7 份）」未逐项枚举 → 复核链缺少可对照原件 | 集成方随本轮归档 r1/r2 报告（含原字节 SHA-256），并把 7 项勘误落到 Task 附注或 verification 索引 |
| N-8 | P3（记录） | `fetch_bj.py:38-39` | `sys.path.insert` + `import assets` 使同一进程存在 `assets` 与 `test_assets...tools.assets` **两个模块对象**；当前各方 patch 不重叠（46 passed 佐证），但未来 `patch.object(assets, "ROOT")` 不会影响 fetch_bj | 改为包内相对导入或 `importlib` 单一身份 |

> 说明：我**未**把 N-1（草稿/manifest 署名串陈旧）提到 P2——它只影响尚未发送的草稿与 gitignored 副产品，受管清单（cases.json/README）本身正确且对外署名要求（作品名+作者名）并未缺失；但它是本轮**最应随手修掉**的一项，尤其在用户发信前。

---

### 结论与下一步

- **结论**：r1 的 1×P1 + 6×P2 + 9×P3 条件**全部关闭**（P3-2 为按效果关闭并留痕）；返修未引入 P0/P1/P2；本轮新增 8 项 P3 记录。**verdict = approved**，准予 Codex 集成。
- **验证强度与限制**：所有能静态复算的数字（字节求和、文件计数、SHA-256 前缀/长度、case↔inventory↔磁盘映射、r1 与返修两套 verify 摘要逐项对照）均**独立复现一致**；`pytest 46 passed`、`verify 12/12 EXIT=0`、`assets verify ja/ko EXIT=0` 三项采信 HEAD=118b4df3 的入库日志（本会话沙箱无终端，无法复跑）；返修 commit 字面 diff 与 `a93a61f3`/`31dcbde0` 对象存在性未独立验证。
- **推荐下一步（可直接转发）**：

> **Agent：Codex（Integrator；如需代行可由 ZCode 代行，保持 Owner≠Integrator）。Task：M2-TA2B 集成收口。** 输入：worktree `G:/CODEX/New Manga.worktrees/M2-TA2B-OPEN-ASSETS-zcode`、branch `agent/zcode/M2-TA2B-OPEN-ASSETS`、base `9db2dca8`、repair/delivery head `118b4df3`/`31dcbde0`；依据 DSH r2 报告 `approved`（0×P0/P1/P2，8×P3 待收口）。动作：①**发信前**修 `verification/M2-TA2B/densho810-report-draft.txt:42` 的署名串为官方格式（N-1，用户待办依赖此项）；②顺手收口 N-2/N-3/N-6/N-7（note 范围与断言、测试措辞/补 RedirectGuard 判别用例、README 补 BJ 快照↔运行时示例句、归档 r1/r2 报告并登记 7 项勘误）；③N-4/N-5/N-8 登记为候选（可留 planning）。**禁止**：改 `src/**`、`apps/**`、`packaging/**`；素材像素/文件入 Git；改写既有 case 字段值（取消标注除外）；代发 densho810 邮件。Gate：集成 head 上复跑 `python -m pytest tests/m2_test_assets -q`（期望 46 passed）、`python test_assets/comic_golden_suite/tools/fetch_bj.py verify`（期望 12/12 EXIT=0）、`python test_assets/comic_golden_suite/tools/assets.py verify --language ja|ko --level full`（期望 EXIT=0、INVENTORY checked=110 missing=0）、`git diff --check` EXIT=0；合入后置 Task `done` 并登记 STATUS。完成后队列下一 Task 为 **M2-TA3-A**（STATUS 记为 `ready`，depends_on T-D2），释放前请按 Rebaseline Plan 复核其范围与允许路径。
- **用户待办（不可由 Agent 代发）**：素材公开用于测试后 1 个月内向 `info@densho810.com` 发送利用报告（草稿已备，见上 N-1 的署名串修正）。
