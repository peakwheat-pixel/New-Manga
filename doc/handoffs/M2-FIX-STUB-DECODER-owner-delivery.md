# Handoff — M2-FIX-STUB-DECODER core_service stub decoder 签名修复

- Owner: ZCode（子 agent 代行实现，用户授权 2026-09-28）
- Task: `doc/tasks/M2-FIX-STUB-DECODER.md`（`in_progress → in_review / CLAIMED_IN_PROGRESS → DELIVERED_FOR_REVIEW`）
- Base / release: `f5d91425` / `fc419905`
- Branch / worktree: `agent/zcode/M2-FIX-STUB-DECODER` / `G:/CODEX/New Manga.worktrees/M2-FIX-STUB-DECODER-zcode`
- Head ledger: claim=`0f4f881a` → 实现+证据+handoff=交付 tip（`git rev-parse HEAD` 于交付 commit；本文件即在该 commit 内；`delivery_head` frontmatter 按 Task 约定保持 null，由 Integrator 在 merge 后回填）→ task 回填=最终 tip（其 commit message 注明交付 tip hash）
- Status: delivered（等 DeepSeek Harness 非作者 Review；Integrator=Codex，Owner≠Integrator 保持）

## 交付物

| 文件 | 说明 |
|---|---|
| `src/bootstrap/core_service.py` | **唯一产品代码改动**：`_PassthroughImageDecoder.decode` 返回行 `format="rgb"` → `mime_type="image/rgb"` + 一行注释（取值理由）。类体外零改动，`DecodedImage` 契约零改动 |
| `tests/core/test_stub_decoder.py` | 新增回归锁定（2 场景）：① production 装配路径（`assemble_production_core` → `core.importer._decoder`）断言 decode 返回 `DecodedImage` 且 width==1/height==1/mime_type 非空 str；② 直构 stub（私有名 import，注释说明）验证任意 payload passthrough 不抛异常 |
| `verification/M2-FIX-STUB-DECODER/verification-results.md` | 主证据：先红/绿/回归数字、AC 判定表、判别力说明、语义发现、NOT_RUN |
| `verification/M2-FIX-STUB-DECODER/raw/02-red-before-fix.log` | 先红：`TypeError: DecodedImage.__init__() got an unexpected keyword argument 'format'` @ `src\bootstrap\core_service.py:54`，2 failed，EXIT=1（带头带时间戳） |
| `verification/M2-FIX-STUB-DECODER/raw/03-green-after-fix.log` | 修复后同测试 2 passed，EXIT=0 |
| `verification/M2-FIX-STUB-DECODER/raw/04-regression-tests-core.log` | `tests/core/ -q` → 76 passed，EXIT=0 |
| `verification/M2-FIX-STUB-DECODER/raw/05-regression-tests-m2_acceptance.log` | `tests/m2_acceptance -q` → 32 passed, 2 xfailed，EXIT=0（2 xfailed=M2-AC4 F-1/F-2 受控缺陷证据，未触碰） |
| `verification/M2-FIX-STUB-DECODER/raw/06-scope-self-check.log` | 交付 tip `5cacebfa` 上自检：全量 diff（[1]）、Owner 专属 diff `fc419905..5cacebfa`（[2]，仅允许路径）、`git diff --check f5d91425..5cacebfa` **EXIT=0**（[3]）；[1] 中 `STATUS.md`/`release-f5d91425.md` 来自 release commit `fc419905`（编排者，pre-claim），日志内 NOTE 说明 |
| `doc/tasks/M2-FIX-STUB-DECODER.md` | AC 判定回填、测试矩阵 executed、`status: in_review` / `dispatch_state: DELIVERED_FOR_REVIEW`（回填 commit） |

## AC 判定表（全部实测）

| AC | 判定 | 要点 |
|---|---|---|
| AC1 stub 签名修正 | **PASS** | 仅 `_PassthroughImageDecoder` 类体一行修复；`mime_type="image/rgb"` 非空语义合理（保留原 rgb 语义）；`assemble_production_core` 其他注入与 `DecodedImage` 零改动 |
| AC2 先红后绿 | **PASS** | 先红 TypeError @ core_service.py:54（正是被修复行），2 failed EXIT=1 → 修复后 2 passed EXIT=0；测试经 production 装配取真实注入 decoder |
| AC3 证据纪律 | **PASS**（最终 tip 复跑按协议归 Integrator） | 全部日志带头（shell/解释器/HEAD/ISO 时间戳）尾记 EXIT；范围自检 diff --check EXIT=0，变更仅落允许路径 |

## 验证命令（worktree 根目录，$py=`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`）

1. `$py -m pytest tests/core/test_stub_decoder.py -v` → **2 passed**，EXIT=0
2. `$py -m pytest tests/core/ -q` → **76 passed**，EXIT=0（含新增 2 条）
3. `$py -m pytest tests/m2_acceptance -q` → **32 passed, 2 xfailed**，EXIT=0
4. `git diff --name-status fc419905..HEAD` → Owner 变更仅允许路径；`git diff --check f5d91425..HEAD` → **EXIT=0**（全量 vs base 中 `STATUS.md`/`release-f5d91425.md` 来自 release commit `fc419905`）

环境：Windows x64 · Git Bash · Python 3.12.3 · pytest 9.1.1。

## 实现过程中的语义发现（供 Reviewer 核对）

1. **`CoreServices` 无 `image_decoder` 属性**：decoder 经 `assemble_core_services` 注入 `ImportImagesUseCase`（`core_assembly.py:626-630`），production 装配路径取用为 `core.importer._decoder`（`service.py:46`）。Task 指令示例 `core.image_decoder` 与真实装配不符；AC2「或等价最小路径」覆盖，测试已注释说明。
2. **判别力自证省略说明**：步骤 2 先红的红点即 TypeError @ `src\bootstrap\core_service.py:54`，与被修复行逐字对应，红/绿差异仅由该一行修复产生——临时回滚再证红等价于已有先红，未重复执行。
3. **同类 stub 隐患仍在范围外**：`assemble_production_core` 中 `font_catalog/layout_engine/compositor=object()`（`core_service.py:82-84`）为 Task 明示观察项，未触碰。
4. **mime_type 取值**：`image/rgb` 非 IANA 注册类型；stub 为占位实现，判据取「非空 str + 保留原 stub rgb 语义」，真实 decoder 另立 Task 时自然替换。
5. **Task 锚点核对**：`core_service.py:51-54`、`ports.py:11-16`（实为 11-17 含 docstring 闭合）与缺陷描述相符，AC 措辞无需修订。

## NOT_RUN / BLOCKED

- 经 stub 的端到端 `import_files` 全链（decoder→copy_store→sink）：NOT_RUN——M2-IPC1 冻结 IPC 命令面不含 import；真实 decoder 引入属另立 Task。
- BLOCKED：无。

## 风险 / 遗留

- 交付 commit 有一次 amend 轨迹：初版 `550b4269` 中 `raw/02-red-before-fix.log` 含 2 处 pytest 原样输出的行尾空白（diff --check EXIT=2），按 M2-AC4 先例做 whitespace-only 清理（traceback 内容逐字保留，仅去行尾空格）后 amend 为交付 tip `5cacebfa`；轨迹见 `raw/06-scope-self-check.log` 与 `verification-results.md` §范围自检。
- 2 xfailed（M2-AC4 F-1/F-2）与本 Task 无耦合，保持原状；其修复落地会 XPASS 报错提醒移除标记（既有约定）。
- 回归 `tests/core/` 日志尾部的 QML TypeError 行为既有 UI shell 测试 stderr 噪音，pytest 判定全绿，与本 Task 无关。

## 启动 / 复现方式

```bash
cd "G:/CODEX/New Manga.worktrees/M2-FIX-STUB-DECODER-zcode"
git checkout agent/zcode/M2-FIX-STUB-DECODER   # tip = delivery head
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/core/test_stub_decoder.py -v
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/core/ -q
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/m2_acceptance -q
git diff --check f5d91425..HEAD
```

## 下一接收者

DeepSeek Harness（非作者 Review）：按 `doc/templates/REVIEW.md` 审 `agent/zcode/M2-FIX-STUB-DECODER` 交付 tip，重点核对 AC1 最小性（`git diff f5d91425..HEAD -- src/` 应只有 `_PassthroughImageDecoder` 类体）与 AC2 先红日志真实性（`raw/02-red-before-fix.log` 红点行号=被修复行）。Review 通过后交 Codex 集成。
