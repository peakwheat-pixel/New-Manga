---
task_id: M2-MANGA-WEIGHTS-SOP
author: ZCode
recipient: Codex（转 DeepSeek Harness 非作者 Review）
base_commit: 46f079e8
delivery_head: b0dd843c（review-fix DSH r1 终态；1019ed6b 为首轮 implement）
status: delivered
---

# Handoff：M2-MANGA-WEIGHTS-SOP（manga 权重 fetch/verify 脚本与安装 SOP）

## 交付结果

- **变更路径**（implement commit `1019ed6b`）：
  - 新增 `verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py`——pinned
    manga 检测器权重（`ogkalu/comic-text-and-bubble-detector` @ HF revision
    `16e8a622`）的 sanctioned 获取+校验脚本，补齐 docTR 同款
    （`verification/T1.1.1/scripts/fetch_doctr_weights.py`）的部署缺口（DSH r1 R6 / GOAL T2）；
  - 新增 `verification/M2-PROD-DETECT-2/WEIGHTS-SOP.md`——四场景安装 SOP +
    pin 漂移 re-pin 流程 + 故障排查速查表。
- **关键设计事实**：
  - pin 权威在 `src/infrastructure/providers/detection_manga.py`（`MANGA_*_SHA256`）；
    脚本内常量为同源部署便利副本，注释声明「两者不一致时脚本 fail」；
  - dest 解析：`--dest` > `NEWMANGA_DETECTOR_WEIGHTS`（目录语义；file/suffix
    值按 docTR 误配置拒绝，EXIT=2）> `<default_data_root()>/models/detector/
    ogkalu-comic-text-and-bubble-detector/`。`default_data_root()` 按
    `src/bootstrap/core_assembly.py:641` 逐字复刻（`NEWMANGA_DATA_ROOT` >
    `%LOCALAPPDATA%`（fallback `$HOME`）+ `New Manga`）——注意 Task 委托文本
    写的 `%LOCALAPPDATA%/NewManga/...` 不准确，实际默认根是
    `%LOCALAPPDATA%\New Manga`（带空格），脚本以真实代码为准并在 docstring
    注明镜像责任；
  - stdlib-only（urllib 默认 opener 原生尊重 HTTP(S)_PROXY，脚本不装自定义
    opener 以免遮蔽）；幂等（已验证 skip）；损坏/不完整自动重下（新字节过 pin
    才覆盖）；下载失败/持续 hash 不符 EXIT=1；
  - `--source-revision` 漂移模式：非 pin revision 强制显式 `--dest`（禁止落入
    生产默认布局），下载后不做 pin 对比、只报告实际 SHA-256 并标注
    UNVERIFIED——为将来 re-pin slice 提供取件通道，生产纪律不松。
- **commit 链**（branch `agent/zcode/M2-MANGA-WEIGHTS-SOP`，worktree
  `G:/CODEX/New Manga.worktrees/M2-WEIGHTS-SOP-zcode`）：
  - `d37ed6f0` claim：Task frontmatter `status: ready -> in_progress`；
  - `1019ed6b` implement：脚本 + SOP（delivery head）；
  - 本 Handoff + Task 回填为第三提交（真实历史，claim→implement→handoff）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 脚本 | `python verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py --help` + 全参数路径实测（见 AC3 各行） | Windows / Python 3.14.0（`C:\Python314`）/ `1019ed6b` 工作区 | PASS | 本表各行 |
| AC2 SOP | 人工核对四场景与 `core_assembly.py` 解析顺序、`default_data_root()` 实现逐字一致 | `1019ed6b` 工作区 | PASS | `verification/M2-PROD-DETECT-2/WEIGHTS-SOP.md` |
| AC3a 离线校验（本地快照） | `python .../fetch_manga_weights.py --verify-only --dest "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector"` | 同上 | PASS（EXIT=0，三 hash 全符：`037930a8…` / `b6d70793…` / `7e9e2245…`） | 本行命令可复现 |
| AC3b 真实下载（代理） | `python .../fetch_manga_weights.py --dest "G:/CODEX/New Manga.task-envs/M2-WEIGHTS-SOP-fetch-test/ogkalu-comic-text-and-bubble-detector"`（代理 `http://127.0.0.1:7890` 由环境注入，脚本启动打印 `proxy environment in effect`） | 同上，HF `resolve/16e8a622/` 经代理 302→CDN | PASS（EXIT=0；三文件含 171,543,900B `model.safetensors` 全部 pin 校验通过；测试目录已清理） | 本行命令可复现 |
| AC3c 幂等 | 同目录二跑下载模式 | 同上 | PASS（三行 `already fetched and verified`，EXIT=0） | — |
| AC3d 损坏重下 | 篡改 `config.json` → 重跑下载模式 | 同上 | PASS（检出 wrong sha256 → 重下 → 恢复 pin，EXIT=0） | — |
| AC3e 失败路径 | 缺失目录 `--verify-only` / 篡改文件 `--verify-only` / `--source-revision main` 无 `--dest` | 同上 | PASS（EXIT=1 / EXIT=1 / EXIT=2，报错点名文件并给指引） | — |
| AC3f 默认布局解析 | `NEWMANGA_DATA_ROOT=<临时目录>` 下无参数跑下载模式 | 同上 | PASS（落入 `<root>/models/detector/ogkalu-comic-text-and-bubble-detector/`，EXIT=0，后清理） | — |
| AC4 纪律 | `git diff --check 46f079e8..HEAD`、`git status --porcelain`、范围核对 | 本 worktree | PASS（见自检三项） | — |

未运行项：无（AC3 真实下载路径实测成功，无 NOT_RUN）。pytest 全套不在本 Task
Gate 内（本交付不触碰任何 Python import 面；脚本仅手工执行验证）。

## 接收方式

- 分支 `agent/zcode/M2-MANGA-WEIGHTS-SOP` @ worktree
  `G:/CODEX/New Manga.worktrees/M2-WEIGHTS-SOP-zcode`，base `46f079e8`，
  delivery head `1019ed6b`（+ 本文档提交）。
- 复现命令（任一 Python 3.10+ 环境，无需 torch/transformers）：
  - 离线复核：`python "verification/M2-PROD-DETECT-2/scripts/fetch_manga_weights.py" --verify-only --dest "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector"`
  - 真实下载复核（代理环境）：设 `HTTPS_PROXY=http://127.0.0.1:7890` 后去掉
    `--verify-only` 任选临时 `--dest`。
- 接收者检查建议：核对 SOP §0 表格三 pin 与 `detection_manga.py` 常量逐字
  一致；核对 dest 解析顺序与 `_resolve_detector_weights_path` /
  `default_data_root` 一致；抽跑 AC3a 一行命令。

## 下一任务建议（必填）

- Task ID / 标题：M2-MANGA-WEIGHTS-SOP 集成（r1 条件已全部闭合，见上文
  「DSH r1 处置」小节）；可选：DSH r2 快速抽查（非阻塞）；
- 推荐 Agent / Reviewer：编排会话代行 Codex（集成）；可选抽查=DeepSeek
  Harness（非作者）；
- 推荐原因与前置依赖：r1 verdict=approved_with_conditions，三项 P2
  （R-A1/A2/A3）与全部 P3/P4（R-A4~R-A10）均已闭合并复跑（见处置表）；
  r1 清单第 9 项的 `.gitignore` 兜底规则由集成方在集成时补（本 Task 无权
  路径）；无其他前置依赖；
- Recovery point：仓库 `G:/CODEX/New Manga`，worktree
  `G:/CODEX/New Manga.worktrees/M2-WEIGHTS-SOP-zcode`，branch
  `agent/zcode/M2-MANGA-WEIGHTS-SOP`，base `46f079e8` / head=`1019ed6b`
  implement + `8fa23edd` handoff + r1 返修 fix + 本文档提交（真实链见
  `git log`）；
- 允许修改路径（集成方）：合并入 master + `.gitignore` 窄规则
  （`*.safetensors`、`*.pt`）+ STATUS 注记；
- 禁止范围与新增授权条件：pin 数值变更属 re-pin slice，须新 Task 授权；
- 交付物（集成方）：merge commit + gitignore 兜底 + STATUS 口径；
- 验证命令、环境与完成 Gate：`--verify-only --dest "G:/CODEX/New
  Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector"`
  EXIT=0 + 任一临时目录真实下载一轮 + `git diff --check 46f079e8..HEAD`
  EXIT=0 + 变更范围仅 `verification/M2-PROD-DETECT-2/**` + Task + Handoff；
- 可直接转发给 Agent 的指令：「对 M2-MANGA-WEIGHTS-SOP 做集成前复验：
  读 doc/handoffs/M2-MANGA-WEIGHTS-SOP-1019ed6b.md 的『DSH r1 处置』小节，
  抽跑其复跑列两条命令（--verify-only 快照 + 临时目录真实下载），确认
  R-A1/A2/A3 闭合与 R-A9 转办事项，然后按协作协议集成；集成时在根
  .gitignore 补权重兜底窄规则。禁止修改实现语义。」

## DSH r1 处置（review：G:/CODEX/New Manga.task-envs/M2-WEIGHTS-SOP/dsh-review-r1.md，verdict=approved_with_conditions）

r1 三项 P2 条件全部闭合 + 7 项 P3/P4 顺手闭，返修 commit 为本 Handoff 之前的
`fix(M2-MANGA-WEIGHTS-SOP): DSH r1 处置` 提交（真实历史续链）。逐条：

| Finding | 处置 | 复跑证据 |
|---|---|---|
| R-A1[P2] 校验时机在安装后、mismatch 文案与磁盘事实相反 | `download_file` 只落 `.part`；调用方在 `.part` 上校验，通过才 `tmp.replace(target)`（对照 `fetch_doctr_weights.py:81-90` 先例）；mismatch 分支 `tmp.unlink()` + 文案「mismatched bytes were DELETED and nothing was installed — <target> is unchanged」；docstring/SOP §1 同步 | AC3d 复证：篡改 config.json → 重下恢复 pin EXIT=0；**错 pin 反证**：stub 错 pin 调 `download_and_verify` → EXIT=1、预置旧好文件逐字节原样（`sha256==CONFIG_SHA256`）、无 `.part` 残留 |
| R-A2[P2] 场景 B 路径错误 | 改 `<安装目录>\resources\core-sidecar\models\detector\<dir>\`（与 `core_service.exe` 同目录，安装根 `%LOCALAPPDATA%\m2rc1-desktop`）；§0 第 3 条同步；§6 加「缺 `resources\core-sidecar` 段 → EXIT=1」行 | 文档级（路径以 `raw/installed-weights-sha256.txt:3` 安装态记录为准） |
| R-A3[P2] drift 模式静默跳过且 EXIT=0 | 采 `--force` 方案：drift + 非空目录 → EXIT=2；`--force` 放行并**全量重下**（不信任既有文件）；SOP §5 登记 + 「每次 drift 用新目录」建议 | 非空无 --force EXIT=2；空目录 EXIT=0（3 文件 UNVERIFIED）；`--force` 全量重下 3 文件 EXIT=0 |
| R-A4[P3] `.suffix` 误拒合法目录 | 改 `exists() and not is_dir()` 判定，带点目录名放行，保留 `.pt` 指引 | 文档/代码级 |
| R-A5[P3] `.part` 残留未登记 | `download_file` 异常（含 KeyboardInterrupt）`tmp.unlink(missing_ok=True)`；SOP §6 加「残留 `.part` 可安全删除 / 重跑收敛」行 | 错 pin 反证中 `.part` 清理同路径验证 |
| R-A6[P3] `--verify-only` 触发 drift WARNING | drift 判定收进下载路径；`--verify-only` 帮助注明忽略 `--source-revision` | `--verify-only` 复跑 EXIT=0 无 WARNING |
| R-A7[P4] `dest.mkdir` 裸 traceback | 捕获 `FileExistsError/NotADirectoryError` → stderr 指引 + EXIT=2 | 代码级 |
| R-A8[P4] 场景 C 未提数据根可变 | 加 `NEWMANGA_DATA_ROOT`/Tauri 用户根派生（`<用户根>\data`）提示 | 文档级 |
| R-A9[P4] gitignore 护栏缺失 | **不改 `.gitignore`（不在允许路径）**；Task AC4 加注「护栏为过程性，gitignore 兜底由集成方补（窄规则建议 `*.safetensors`、`*.pt`）」 | 已转集成方清单 |
| R-A10[P4] Task frontmatter base 不一致 | frontmatter 注明「契约编写时基线=095e314d；分支实际 base=46f079e8」 | 文档级 |

r1 NOT_VERIFIED 项的本轮补强：全部运行期结论在本轮**真实复跑**（见上表复跑
列；环境 Windows / Python 3.14 / 代理 127.0.0.1:7890），不再仅有前轮自报。

## 风险与遗留

- 脚本 pin 常量与 `detection_manga.py` 是手工镜像：未来 re-pin slice 必须
  同步两处 + SOP §0 表格（SOP §5 已写死该流程）；无自动一致性测试（仓库无
  该脚本的 pytest 挂面，属部署脚本定位；如 Review 认为需要，可在新 slice
  加 lint 级一致性检查）。
- Windows 上 `urllib.getproxies()` 亦读注册表代理；若用户仅设注册表代理而
  未设环境变量，脚本仍会经系统代理生效（打印的 proxy 列表可审计）——SOP
  场景 D 以环境变量口径书写。
- 实测机代理 `http://127.0.0.1:7890` 由环境自带注入（含
  `zcode_http`/`all` 条目），非本 Task 配置；无网环境下场景 A 需走 SOP §4
  离线搬运路径。
- 关联：M2-PROD-DETECT-1（R6 来源）、M2-PROD-DETECT-2（发布形态权重随包
  证据，SOP 场景 B 引用其集成记录）、GOAL.md T2。
