# Antigravity Owner 指令：P03

请在 `G:/CODEX/New Manga.worktrees/P03-packaged-sfx-entry-antigravity` 的 linked worktree 完成 `doc/tasks/P03.md`，不要在主checkout工作。Owner=Antigravity、Reviewer=DeepSeek Harness（非作者）、Integrator=Codex。Task固定base=`31abde9bf4b73aea2851931dcd48faa0f750b318`；branch=`agent/antigravity/P03-packaged-sfx-entry`。开工先核对 `git rev-parse --show-toplevel`、`git rev-parse --path-format=absolute --git-common-dir`、branch、HEAD、worktree list 与 clean status，并确认checkout位于本Task正式释放commit之后；然后把P03 Task自身状态从`ready`改为`in_progress`，在Task-local RESUME记录真实commit与状态。

先读 `AGENTS.md`、`doc/09_COLLABORATION.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P03.md`、本目录 `RESUME.md`，以及 `packaging/m2ac5/run_clean_start_e2e.py`、`src/bootstrap/sfx_detect_probe.py`、相关packaging tests、`verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py`。依Task逐项实现并交付；不得扩大范围，不要等待用户对已冻结细节再次确认。

## 只允许写入

- `packaging/m2ac5/run_clean_start_e2e.py`
- 新建 `tests/packaging/test_packaged_fifth_sfx_entry.py`
- `verification/P03-PACKAGED-SFX-ENTRY/**`
- `doc/tasks/P03.md`
- `doc/handoffs/P03-PACKAGED-SFX-ENTRY-*.md`

不得修改Codex维护的 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/tasks/README.md`、`doc/12_ROADMAP.md` 或派生全局路线图。不得改 `src/**`、`apps/**`、contracts、Schema、依赖、`packaging/m2ac5/core_sidecar.spec`、`build_sidecar.ps1`、requirements、既有测试行为或历史 raw。不得访问真实用户 `%APPDATA%` 数据；不得stage/改写 `.qoder-credits/**`、P08/DSH raw、历史 Runner raw 或其他Agent dirty。禁止push、发布、部署或清理其他worktree。

## 实现与验收

1. 在 packaged runner 的 `SIDECAR_EXES` 安装存在列表与终态sidecar process survivor零存活断言中纳入第五入口 `sfx_detect_probe.exe`。
2. 给runner增加只在显式传入 `--sfx-real-page <path>` 时执行的第五入口检查：同一份刚安装的P03 NSIS installer下，调用安装目录中的 `sfx_detect_probe.exe` 对固定K07页面执行真实成功场景，并对隔离Gate目录中保证不存在的页面路径执行预期失败场景。每次调用使用单独的 `--out`、保存 stdout/stderr/exit 和parse后的JSON；验证exactly one `SFX_PROBE_JSON: `、`python.frozen=true`、正向exit 0 / `error=null` / `n_candidates>0` / pinned weights SHA一致，失败exit 1 / 非空错误JSON。运行fallback信息必须原样记录；不要隐瞒fallback。两种场景都并入该runner自己的结构化Gate，不只验证文件存在。
3. 新增小型定向pytest，覆盖第五入口进入安装清单及终态清理判定、成功/失败JSON判别逻辑。无需改动任何production module或依赖。保留原 `--output-dir` required行为。
4. 在build / test前重新校验只读外部输入：K07=`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K07_R123.png` SHA-256必须为`28dab503aca3c903111488c03e857b430d309421a4a54bab335a63bbe7b9cec4`；SFX v2b weights=`G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx` SHA-256必须为`944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d`。任何缺失/hash drift都停止相关验收并记BLOCKED/NOT_RUN，不找旧文件替代，也不把图片/模型拷进Git。
5. 跑定向tests与 `python verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py`。然后在干净Owner checkout上fresh build：`npm ci --no-audit --no-fund`、`npm run build`（cwd=`apps/desktop/frontend`）；`powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1 -Force`（repo root）；`npx --yes @tauri-apps/cli@2 build`（cwd=`apps/desktop/src-tauri`）。每个步骤保存shell、解释器/工具版本、完整命令、完整stdout/stderr、EXIT。
6. 构建完成先固定完整source `HEAD` 与新NSIS installer路径/64位SHA-256，将二者写入P03证据；再运行单一完整Gate命令：`python packaging/m2ac5/run_clean_start_e2e.py --installer <fresh P03 installer> --output-dir verification/P03-PACKAGED-SFX-ENTRY/<unique-run> --sfx-real-page "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K07_R123.png"`。Gate JSON中的installer SHA必须相同；所有既有clean-start scenarios与两条frozen第五入口场景都必须过。完整输出写入新的P03目录，禁止使用或改写既有 `verification/M2-AC5/raw/**`、`verification/M2-PROD-SFX-PROBE-1/**` 或 `verification/M2-RUNNER-SNAPSHOT-DEBT/**`。
7. `git diff --name-only <base>..<delivery>`逐项证明路径全部获准；`git diff --check <base>..<delivery>` EXIT=0。固定代码delivery head，之后Handoff追加文档提交并明确区分build source HEAD与delivery/review HEAD。把Task推进到`in_review`，生成Handoff并留下Task-local RESUME；列明未运行项/限制。不要自审、不要宣称Review批准或Task done。

如遇到用户产品取舍以外的环境阻塞，保留已有数据与工作，记录确切阻塞和下一条命令；如果发现产品实现缺陷或需要触碰禁止范围，停止越界改动，把证据交Codex另立Task。
