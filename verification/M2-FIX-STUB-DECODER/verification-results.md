# Verification Results — M2-FIX-STUB-DECODER（core_service stub decoder 签名修复）

- Owner: ZCode（子 agent 代行，用户授权 2026-09-28）
- Task: `doc/tasks/M2-FIX-STUB-DECODER.md`
- Base: `f5d91425`（release commit `fc419905`）
- Branch / worktree: `agent/zcode/M2-FIX-STUB-DECODER` / `G:/CODEX/New Manga.worktrees/M2-FIX-STUB-DECODER-zcode`
- 环境: Windows x64 · Git Bash · Python 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-012-py312`）· pytest 9.1.1 · pluggy 1.6.0
- 所有日志带头（shell、`$py --version`、`git rev-parse HEAD`、ISO 时间戳）、尾记 `EXIT=`；raw 文件在本目录 `raw/`。

## 缺陷与修复摘要

- 缺陷锚点（base 上核实）：`src/bootstrap/core_service.py:51-54` `_PassthroughImageDecoder.decode` 构造 `DecodedImage(width=1, height=1, format="rgb")`；真实契约 `src/application/importing/images/ports.py:11-17` 为 frozen dataclass `width/height/mime_type` → 双重 TypeError（多余 `format=` + 缺失 `mime_type`）。
- 修复（最小）：该行改为 `DecodedImage(width=1, height=1, mime_type="image/rgb")`，附一行注释说明取值理由（保留 stub 原 `format="rgb"` 的 rgb 语义并落在 `image` 主类型下）。除该类体外 `src/bootstrap/core_service.py` 零改动；`DecodedImage` 契约零改动。

## AC2 先红证据（base 工作树 + 新测试，src 未改）

- 日志：`raw/02-red-before-fix.log`（HEAD=claim commit `0f4f881a`，src 仍为缺陷态）
- 命令：`$py -m pytest tests/core/test_stub_decoder.py -v`
- 红点（两条测试同点）：
  - `TypeError: DecodedImage.__init__() got an unexpected keyword argument 'format'`
  - 位置：`src\bootstrap\core_service.py:54`（正是被修复的那一行）
- 结果：`2 failed in 0.91s`，**EXIT=1**

## AC2 修复后绿

- 日志：`raw/03-green-after-fix.log`
- 命令：`$py -m pytest tests/core/test_stub_decoder.py -v`
- 结果：`2 passed in 0.30s`（`test_production_stub_decoder_returns_valid_decoded_image`、`test_stub_decoder_passthrough_any_payload_does_not_raise`），**EXIT=0**

## AC3 回归

- `tests/core/`（全目录）：`raw/04-regression-tests-core.log` → **76 passed in 9.14s**，EXIT=0（含本 Task 新增 2 条；日志尾部 QML TypeError 行为既有 UI shell 测试的 stderr 噪音，pytest 判定全绿）
- `tests/m2_acceptance`：`raw/05-regression-tests-m2_acceptance.log` → **32 passed, 2 xfailed in 9.42s**，EXIT=0（与释放预期一致；2 xfailed = M2-AC4 F-1/F-2 已知受控缺陷证据，strict=True，非本 Task 范围，未触碰）

## 判别力自证（说明）

- 临时回滚修复行再证红的步骤省略：先红运行（`raw/02-red-before-fix.log`）的红点即为 `TypeError ... unexpected keyword argument 'format'` @ `src\bootstrap\core_service.py:54`，与被修复行逐字对应，且测试经 production 装配路径（`assemble_production_core` → `core.importer._decoder`）取得真实注入实例——红/绿差异仅由该一行修复产生，判别力已由步骤 2/3 直接证明。

## AC 判定

| AC | 判定 | 证据 |
|---|---|---|
| AC1 stub 签名修正 | **PASS** | 修复仅 `_PassthroughImageDecoder` 类体（`git diff` 实证）；`mime_type="image/rgb"` 非空、语义合理（注释在位）；`DecodedImage` 与 `assemble_production_core` 其他注入零改动 |
| AC2 回归测试先红后绿 | **PASS** | 先红 TypeError @ core_service.py:54（2 failed, EXIT=1）→ 修复后 2 passed, EXIT=0；测试经 production 装配路径断言 `DecodedImage` + 字段合法 |
| AC3 证据纪律 | **PASS**（Owner 交付日志；最终 tip 复跑按协议归 Integrator） | 全部日志带头带 EXIT；范围自检见下 |

## 范围自检

- 命令：`git diff --name-status f5d91425..<delivery-tip>` 与 `git diff --check f5d91425..<delivery-tip>`
- 结果：见 `raw/06-scope-self-check.log`（在交付 tip 上实测）；变更仅落允许路径（`src/bootstrap/core_service.py`、`tests/core/test_stub_decoder.py`、`doc/tasks/M2-FIX-STUB-DECODER.md`、`verification/M2-FIX-STUB-DECODER/**`、`doc/handoffs/M2-FIX-STUB-DECODER-owner-delivery.md`），diff --check EXIT=0。

## 实现过程中的语义发现（供 Reviewer 参考）

1. **`CoreServices` 无 `image_decoder` 属性**：指令示例 `core.image_decoder.decode(...)` 与真实装配不符——decoder 在 production 装配中注入 `ImportImagesUseCase`（`core_assembly.py:626-630`），经 `core.importer._decoder` 取得。AC2 措辞「或等价最小路径」覆盖此选择；测试已注释说明。
2. **同类 stub 隐患仍在范围外**：`assemble_production_core` 中 `font_catalog/layout_engine/compositor=object()`（`core_service.py:82-84`）为 Task 明示范围外观察项，未触碰。
3. **production 装配开销**：`assemble_production_core(tmp_path)` 会建库迁移 + `recover_running_runs`，与既有 `tests/core/test_core_service.py` 用法一致，测试内 `finally: core.conn.close()` 释放 Windows 文件锁。

## NOT_RUN / BLOCKED

- 经 stub 的端到端 `import_files` 用例流（decoder→copy_store→sink 全链）：NOT_RUN——production IPC 冻结命令面不含 import（M2-IPC1），stub decode 的直接单元锁定即本 Task 承诺面；真实 decoder 引入属另立 Task。
- BLOCKED：无。

## 风险 / 遗留

- `mime_type="image/rgb"` 非 IANA 注册媒体类型；stub 本身是占位实现，语义合理性以「非空 str + 保留原 rgb 语义」为判据，真实 decoder Task 落地时自然替换。
- 2 xfailed（M2-AC4 F-1/F-2）与本 Task 无耦合，保持原状。
