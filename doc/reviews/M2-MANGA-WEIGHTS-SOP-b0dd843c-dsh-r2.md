# DSH 非作者 Reviewer — round 2 定点复核（Task A / Task B）

> 复核方式：纯静态，逐文件 read/grep + 对 r1 review-input.diff（原始交付 diff）与新工作区现状做逐行对照重建返修 diff。
> **重要限制**：本轮 pwsh 沙箱初始化失败（`SetNamedSecurityInfoW Win32 5`），沙箱升级又无审批通道，故**本轮无任何 Git/命令执行能力**；所有 git 面结论降级为 NOT_VERIFIED，范围纪律改用「worktree 全量文件 mtime 排序（glob 溢出清单）」近似取证。

---

## Task A Verdict

**approved（可集成）** —— R-A1..A10 全部闭合；R-A1 的 mismatch 清理路径与错 pin 反证断言在代码上成立；仅余 2 项 P4 文档漂移（建议并入集成 commit，不阻塞）。

### R-A1..A10 逐条复核表

| 项 | 结论 | 依据（文件:行） |
|---|---|---|
| R-A1 [P2] `.part` 校验后才 replace + mismatch 清理/文案 | **closed** | `fetch_manga_weights.py:158-184`：`download_file(url, tmp)` 签名已改为只写 `.part`，**函数内不再触碰 target**，`except BaseException: tmp.unlink(missing_ok=True); raise`。`:252` 由调用方生成 `target.with_suffix(target.suffix+".part")`；`:258` 先在 `tmp` 上 `sha256_file`；`:259-269` 不符 → `tmp.unlink()` + 记 failure（`continue`，不 replace）；`:270` 命中才 `tmp.replace(target)`。文案 `:261-268`「mismatched bytes were DELETED and nothing was installed — <target> is unchanged」与磁盘事实**一致**（mismatch 分支内对 target 无任何写操作）。docstring `:41-43`、`:193-211` 与 SOP §1 `WEIGHTS-SOP.md:82-85` 同步，且与先例 `verification/T1.1.1/scripts/fetch_doctr_weights.py:80-90`（先 hash `.part` 再 `replace`）同款。**错 pin 反证逻辑支撑成立**：预置好文件 + 错 pin ⇒ `:228-232` 落入 re-download → 新字节仍不符 → `tmp.unlink()` → `failures` 非空 → `:276-280` return 1；全程 target 零写入（旧文件逐字节原样）、`.part` 两条退出路径（下载异常 / 校验不符）均 unlink（零残留）。附佐证：worktree 内出现 `verification/M2-PROD-DETECT-2/scripts/__pycache__/fetch_manga_weights.cpython-314.pyc`，说明确有一次「以 Python 3.14 import 该脚本」的 stub 驱动运行。 |
| R-A2 [P2] 场景 B 路径 + §6 排查行 | **closed** | `WEIGHTS-SOP.md:93-98` 改为 `<安装目录>\resources\core-sidecar\models\detector\ogkalu-comic-text-and-bubble-detector\`（与 `core_service.exe` 同目录、安装根 `%LOCALAPPDATA%\m2rc1-desktop`、并点名「不是 `C:\Program Files`」）；`:103-107` 校验命令含 `resources\core-sidecar` 段；§0 第 3 条 `:38-39` 同步精确化；§6 `:194` 新增「路径缺 `resources\core-sidecar` 段 → 必然 EXIT=1，不要误导向场景 A」。三处仓库事实复核：`apps/desktop/src-tauri/tauri.conf.json:3`（productName=`m2rc1-desktop`）、`:30-32`（`resources/core-sidecar` 资源映射）、`src/bootstrap/core_assembly.py:617-619`（bundle 候选=`sys.executable` 父目录）、`verification/M2-PROD-DETECT-2/raw/installed-weights-sha256.txt:3`（安装态实际 `resources\core-sidecar\models\detector\...`）——四者一致。 |
| R-A3 [P2] drift 非空目录 EXIT=2 / `--force` 全量重下 / SOP 登记 | **closed** | `:376-397`：drift 且有显式 `--dest` 时先 `dest.iterdir()` 取 `existing`，非空且无 `--force` → `parser.error(...)`（退出码 2）；`:398-405` WARNING 移到门之后。`--force` 全量重下实现正确：`:233-241` 的 `expected is None and not force` 早退分支在 force 时不成立 → `:242-249` 打印 `drift --force: re-fetching, old sha256 ...` → 逐文件重新下载并（无 pin）`tmp.replace` 覆盖。`:358-366` 新增 `--force` 参数与 help；SOP §5 `:177-182` 登记「空目录或不存在 + EXIT=2 门 + `--force` 不信任既有文件」并写明「EXIT=0 只在空目录全量下载路径成立、建议每次用新目录」。`--force` 在 pinned 模式被忽略但对语义无影响（`:227-232` 仍按 pin 校验）。 |
| R-A4 [P3] `.suffix` 误拒 | **closed（文档残留 P4-1）** | `:139` 已改为 `if candidate.exists() and not candidate.is_dir():`，并加 `:134-138` 注释说明「带点目录名是合法目录、不存在路径交给正常 mkdir 流程」；SOP §6 `:198` 行同步改为「exists-and-not-a-directory 错误」。**但** Task `:33` 与 Handoff `:24-25` 仍写「file/suffix 值拒绝 EXIT=2」——见「回潮与新问题 P4-1」。语义上与生产端（`core_assembly.py:613-614` verbatim 接受）现已一致 ✓ |
| R-A5 [P3] `.part` 残留/异常清理 + SOP 登记 | **closed** | `:182-184` `except BaseException: tmp.unlink(missing_ok=True); raise`（含 KeyboardInterrupt）；`:170-171` 仍保留「下次尝试先清 stale part」。SOP §6 `:197` 新增「残留 `<file>.part` 可安全删除 / 重跑即收敛」行 ✓ |
| R-A6 [P3] `--verify-only` 不再触发 drift 判定/WARNING | **closed** | `:369-374` `--verify-only` 在最前面提前 `return verify_only(dest, PINNED_FILES)`，`revision`/`unverified_drift`/WARNING 全部在其后，无自相矛盾诊断；`:342-346` help 注明「`--source-revision` is ignored in this mode」✓ |
| R-A7 [P4] `mkdir` 裸 traceback | **closed** | `:212-223` 捕获 `FileExistsError/NotADirectoryError` → stderr 指引 + `return 2`（经 `main` 的 `sys.exit` 落 EXIT=2）✓ |
| R-A8 [P4] 场景 C 数据根可变提示 | **closed** | `WEIGHTS-SOP.md:120-124` 新增提示块：数据根由 `NEWMANGA_DATA_ROOT` 决定、Tauri 配置用户根时派生值可能是 `<用户根>\data`、以 env 值为准。事实复核：`src/bootstrap/core_service.py:371-373`、`apps/desktop/src-tauri/src/main.rs:446-452` 确有该派生 ✓ |
| R-A9 [P4] 权重 gitignore 护栏缺失 | **closed（按 r1 备选路径转办）** | Task `:36` AC4 明确注记「护栏目前是过程性纪律，无 gitignore 兜底；`.gitignore` 不在本 Task 允许路径，兜底窄规则（`*.safetensors`、`*.pt`）由集成方补」；Handoff `:89-90` 把 gitignore 窄规则列入集成方允许路径。复核 `.gitignore:1-6` 确认无任何权重规则；glob 全量清单内无 `*.safetensors`/`*.part`/权重字节（仅 3 个文档/manifest 命中词）✓ |
| R-A10 [P4] Task frontmatter base 不一致 | **closed** | Task `:12` 已注明「契约编写时基线=095e314d…；分支/worktree 实际 base=46f079e8（R-A10）」✓ |

### 回潮与新问题

1. **[P4-1｜文档-代码漂移（本轮返修引入）]** `doc/tasks/M2-MANGA-WEIGHTS-SOP.md:33` 与 `doc/handoffs/M2-MANGA-WEIGHTS-SOP-1019ed6b.md:24-25` 仍写 `NEWMANGA_DETECTOR_WEIGHTS` 的「**file/suffix** 值拒绝 EXIT=2」，而 `fetch_manga_weights.py:139` 已改为只拒绝「存在且非目录」；SOP §6 与脚本注释已同步，Task/Handoff 未同步。方向不危险（比现状更严），但会误导后续读者/集成记录。建议集成 commit 内一并把该短语改为「仅『存在且非目录』拒绝（带点目录名放行，R-A4）」。
2. **[P4-2｜元数据未随返修更新]** A 侧 Handoff frontmatter `delivery_head: 1019ed6b`（`doc/handoffs/M2-MANGA-WEIGHTS-SOP-1019ed6b.md:6`）仍是返修前头部（真实头 `b0dd843c`）；正文 `:87`、`:105-106` 已用文字说明真实链，无阻，建议集成时或下次触碰时更新。
3. **[可选加固，非回归]** （a）`sha256_file(tmp)` 本身抛错（权限/磁盘）时 `.part` 不会被清理（unlink 只覆盖「下载异常」与「pin 不符」两条路径）；（b）`:270` `tmp.replace(target)` 未包在 try 内，若 `target` 恰为同名目录会裸 traceback（EXIT=1。属极端路径，r1 未要求，不影响本轮闭合判定）。
4. **未发现**：禁改面（`src/**`、`tests/**`、`requirements*`、`packaging/**`、`.gitignore`）零触碰；无二进制、无权重字节；r1 已通过项（三 pin 逐字、dest 镜像、四场景、幂等/退出码语义）在返修后逐段复读未见回归——`verify_only()` `:284-319`、pin 常量 `:73-96`、`default_data_root()` `:111-124` 与 r1 版本逐字相同。

---

## Task B Verdict

**approved（可集成）** —— R-B1..B5 全部闭合；**固化探针确系驱动真实测试函数**（非独立 mock 复刻）；新 skip 理由已无方向性错误。余 2 项 P4 文档残留。

### R-B1..B5 逐条复核表

| 项 | 结论 | 依据（文件:行） |
|---|---|---|
| R-B1 [P3] Handoff 修复前基线改直引 | **closed** | Handoff `:48-52` 已改为「providers **289 passed + 1 failed**、三套件合计 **401 passed + 1 failed**（`verification/M2-PROD-DETECT-2/release-notes.md:67`）」，并删除「288+1 可推出」推导句，改述「290 项数量不变、failed→skipped 不减 passed」。直引核对：`release-notes.md:67` 原文正是 `289 passed + 1 failed` 与 `（1 failed, 401 passed 三套件合计）` ✓ Task `:33` AC2 同口径 ✓ |
| R-B2 [P3] 方向性改写（作废 ≠ 被替代；独立且方向相反） | **closed（Handoff 残留见 P4-1）** | 测试 docstring `test_registry_readiness.py:200-211`：「That premise is **INVALIDATED** (R-B2: not "superseded and relocated")… Separately — and with the **OPPOSITE direction** — release-side ML-closure **COMPLETENESS** is guaranteed independently at BUILD time by … `_assert_ml_closure` (**it fails when the ML modules are MISSING from the frozen PYZ**)… Do not conflate the two: that build gate asserts ML **PRESENCE** in the shipped closure; this test asserted ML **ABSENCE** in the dev environment.」skip 理由 `:238-247` 同口径（INVALIDATED / independently guaranteed / opposite-direction / must not be read as this test's replacement）。事实核对：`packaging/m2ac5/core_sidecar.spec:106-123` 确实在 ML 模块**缺失**时 `raise SystemExit`（方向=要求存在）✓ |
| R-B3 [P4] 窄门意图注释 | **closed** | docstring Known limitations `:220-227`：「the skip gate probes ONLY torch (the same probe the loop itself uses)… a numpy-only environment still FAILS as drift; in an ML venv the absent-module facts for the unapproved providers are covered by `test_real_environment_reports_optional_providers_as_not_ready` (registry probes) — the narrow gate is intentional, not flakiness」，并有 `:234-235` 行内注释。覆盖性说法成立：`src/infrastructure/providers/runtime.py:513,528` 对 `manga_ocr`/`paddleocr` 用 `KIND_MODULE` 需求、`dependencies.py:81-84` 用 `importlib.util.find_spec` 探针，故这些模块若可导入，readiness 测试会红 ✓ |
| R-B4 [P4] `find_spec` 存在性盲区入 docstring | **closed** | `:228-232`：「`find_spec` is an EXISTENCE probe, not an importability probe: a half-installed torch … also trips the skip. This is the same probe the original assertion loop used … not a regression of this conditioning.」与 `:236,248-249` 实际探针一致 ✓ |
| R-B5 [P4] 判别力探针固化为可复跑测试 | **closed（真实驱动）** | `:255-301`：模块级 `_ABSENT_ALL`/`_FAKE_SPEC`，`@pytest.mark.parametrize` 两例。探针在 `:292-294` **只替换 `importlib.util.find_spec`**，随后 `:296/:301` **直接调用 `test_no_model_runtime_is_installed_in_this_environment()` 本体**；因被测函数在调用点做 `importlib.util.find_spec(...)` 属性查找（非局部绑定），monkeypatch 必然生效 ⇒ 真实 gate 与真实断言循环被执行，**不是另写一份 mock 逻辑**。两例语义成立：全 None ⇒ 不触发 skip、循环五模块逐字断言 ⇒ PASS；`|{"paddleocr": _FAKE_SPEC}` ⇒ 命中 `:249-252` 原始 AssertionError（`match="paddleocr unexpectedly present"` 与消息文本一致）⇒ 断言 drift 报警仍具判别力。计数自洽：原 8 项（7 passed+1 failed）→ +2 = 单文件 `9 passed, 1 skipped`；providers 289+1failed → 289+1skipped → **291 passed + 1 skipped**（+2）；三套件 401+1failed → 401+1skipped → **403 passed + 1 skipped** 与 Task `:33`/Handoff `:108-112` 一致 ✓ |

### 回潮与新问题

1. **[P4-1｜方向性措辞残留（同一文件内自相矛盾）]** `doc/handoffs/M2-FIX-REGISTRY-READINESS-ENV-3e4c3b44.md:21-22`（「交付结果/修复语义」段）仍写「**闭包级保证由** `packaging/m2ac5/core_sidecar.spec` `_assert_ml_closure` **构建期断言接管**」——正是 r1 R-B2 判定「方向性不成立」的原措辞；同一文件 `:103` 的返修表已给出正确口径，两处并存。建议集成前把 `:21-22` 改为「T1.1.1 起 TASK-019 环境证据**作废**；发布侧 ML 闭包**完整性**由构建期 `_assert_ml_closure` **独立**保证（方向相反）」。
2. **[P4-2｜契约历史文本遗留]** `doc/tasks/M2-FIX-REGISTRY-READINESS-ENV.md:27`（设计决策#2）仍保留旧 skip 理由原文「closure-level assertion **is enforced by** …」；`:45` 第 4 条与 `:51` 已纠正，属历史决策记录，可选加「（该表述已由第 4 条取代）」以免被引用。
3. **[P4-3｜判别力覆盖度，可选]** 探针只固化 torch-free 的两条路径；「torch 在位 ⇒ skip」分支仍只有真跑 `-rs` 的 `1 skipped` 作证据（未固化为第三参数化用例，例如 `{"torch": _FAKE_SPEC}` + `pytest.raises(pytest.skip.Exception)`）。R-B5 请求的两条路径已闭合，此项仅为可选加固。
4. **[P4-4｜元数据未随返修更新]** Handoff frontmatter `delivery_head: 3e4c3b44`（`:6`）非真实头（`59fe3467`），正文 `:77-78`/`:96-98` 已用文字说明真实链。
5. **未发现**：`src/**`、`packaging/**`、`requirements*`、conftest、其他测试语义零触碰（mtime 全序中位于末尾的**非**产物文件恰为 `tests/providers/test_registry_readiness.py`、`doc/tasks/M2-FIX-REGISTRY-READINESS-ENV.md`、`doc/handoffs/M2-FIX-REGISTRY-READINESS-ENV-3e4c3b44.md` 三个）；原断言循环 `:248-252` 与 r1 diff 上下文逐字一致（未动）；`.pytest_cache/`、`__pycache__/` 属 gitignore 面（A/B 同仓库 `.gitignore:1-3`）✓

---

## NOT_VERIFIED（集成方复跑项）

**方法学限制**：本轮无 shell（`SetNamedSecurityInfoW Win32 5`；升级审批不可用）⇒ 下列各项**全部**未经我复跑，仅按 Owner 自报 + 静态代码/文档核对采信。

1. **Git 面（两 Task 共同）**：`git log 8fa23edd..b0dd843c` / `32caab97..59fe3467` 的真实内容与工作区 HEAD 等同性；`git diff --check` EXIT=0；`git diff --name-only <base>..HEAD` 范围恰 4 / 3 文件；`git status --porcelain` 干净。我的替代证据是 worktree 全量 mtime 排序（A 尾部=脚本+SOP+Task+Handoff+1 个 `fetch_manga_weights.cpython-314.pyc`；B 尾部=测试+Task+Handoff+pytest/pyc 产物），属**近似**，不能替代 git。
2. **Task A 运行期**：`--verify-only` 快照 EXIT=0 三 hash 全符；真实下载 3/3（含 171,543,900 B `model.safetensors`，经代理 `127.0.0.1:7890`）；幂等二跑；AC3d 篡改重下；**错 pin 反证的实际 EXIT=1 / 旧文件逐字节原样 / `.part` 零残留**（代码逻辑成立，实测未见）；drift 三用例（非空 EXIT=2 / 空 EXIT=0 / `--force` 全量重下）；`NEWMANGA_DATA_ROOT` 默认布局落点；`mkdir`→EXIT=2 实测；env 带点目录名放行实测。
3. **Task A 网络面**：`resolve/16e8a622/<file>` 在 HF 侧可用性与 302→CDN 行为。
4. **Task B 运行期**：单文件 `9 passed, 1 skipped`、providers `291 passed + 1 skipped`、m2_acceptance `35`、core `77`、合计 `403 passed + 1 skipped 0 failed`；探针两用例在真实 pytest 下的通过（我仅静态推演到「必然通过」）；真实无 torch 环境行为。
5. **STATUS 口径落地**：两个 Task 的 AC 注记（A：gitignore 兜底 + STATUS 注记；B：providers 新口径与「历轮 +1 既有环境性失败」条目终结）均**未**在本 diff 内（不在 Owner 允许路径），属集成方动作。
6. **上述 P4-1..P4-4 的处置**：由集成方在同一 hygiene/merge commit 内决定是否吸收。

---

## 推荐下一步

由集成方代行 Codex 先复跑两侧门禁（A：`--verify-only --dest "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector"` + 临时目录真实下载一轮 + drift 空/非空/`--force` 三例 + 错 pin 反证；B：`PYTHONPATH=src <主venv>/python -m pytest tests/providers tests/m2_acceptance tests/core -q -rs` 预期 403 passed + 1 skipped 0 failed）与两 worktree 的 `git diff --check`/范围核对，通过即合并，并在同一 hygiene commit 内顺手修正 A 的「file/suffix」措辞、B 的 Handoff「接管」措辞，同时按清单落地 `.gitignore` 窄规则与 STATUS 口径注记。
