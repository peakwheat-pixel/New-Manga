# TASK-005 Minimal Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立可由 Python 3.12 启动的最小 PySide6/QML 工程入口，以及可运行的 Domain/UI import 架构守卫。

**Architecture:** `bootstrap.app` 只负责 Qt Application 装配与 QML 加载，`ui/qml/Main.qml` 只提供无业务行为的根窗口。架构规则由 pytest 内的标准库 `ast` 扫描执行，不引入生产抽象、数据库、Provider、导航或业务实体。

**Tech Stack:** Python 3.12.3、PySide6_Essentials 6.11.2、shiboken6 6.11.2、pytest 9.1.1、PowerShell、stdlib `ast`。

**Spec:** `doc/tasks/TASK-005.md`

## Global Constraints

- 固定基线为 `d65901b953e6fb26043344ed3d668520847eb295`，分支为 `agent/codex/TASK-005-minimal-bootstrap`。
- 只修改 TASK-005 `允许修改范围`；TASK-006～TASK-027 与业务功能保持冻结。
- Core 只依赖 `PySide6_Essentials==6.11.2` 与 `shiboken6==6.11.2`，不安装 torch、transformers、onnxruntime 或 OCR/Inpaint Runtime。
- 唯一运行入口为设置 `PYTHONPATH=src` 后执行 `python -m bootstrap.app`；`--smoke-test` 必须真实加载 QML 后退出 0。
- 不创建 Application、Ports、Infrastructure、Repository、Provider、数据库、四页导航、打包配置或 CI。
- 每个生产行为必须先观察对应测试因该行为缺失而失败，再写最小实现。

---

### Task 1: 精确依赖与隔离环境

**Files:**
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `.gitignore`

**Interfaces:**
- Consumes: TASK-004 已验证的 Python 3.12.3 / Qt 6.11.2 / pytest 9.1.1 / PyInstaller 6.22.3 组合。
- Produces: 仓库外 `G:/CODEX/New Manga.task-envs/TASK-005-py312` 解释器，供后续全部测试与验证使用。

- [x] **Step 1: 写入唯一 requirements 锁定**

`requirements.txt`：

```text
PySide6_Essentials==6.11.2
shiboken6==6.11.2
```

`requirements-dev.txt`：

```text
-r requirements.txt
altgraph==0.17.5
colorama==0.4.6
iniconfig==2.3.0
packaging==26.3
pefile==2024.8.26
pluggy==1.6.0
Pygments==2.21.0
pyinstaller==6.22.3
pyinstaller-hooks-contrib==2026.7
pytest==9.1.1
pywin32-ctypes==0.2.3
setuptools==84.0.0
```

`.gitignore`：

```text
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
build/
dist/
```

- [x] **Step 2: 创建并安装 Python 3.12 隔离环境**

Run:

```powershell
py -3.12 -m venv 'G:/CODEX/New Manga.task-envs/TASK-005-py312'
& 'G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe' -m pip install -r requirements-dev.txt
```

Expected: 两条命令退出码均为 0，安装不包含 `PySide6_Addons`、torch、transformers 或 onnxruntime。

- [x] **Step 3: 核对锁定环境**

Run:

```powershell
& 'G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe' --version
& 'G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe' -m pip check
& 'G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe' -m pip freeze
```

Expected: Python 3.12.3；`pip check` 为 `No broken requirements found.`；freeze 与两个 requirements 文件的闭包一致。

- [x] **Step 4: 提交依赖入口**

```powershell
git add -- .gitignore requirements.txt requirements-dev.txt
git commit -m "build(TASK-005): lock minimal core dependencies"
```

### Task 2: 用 AST 守卫锁定包边界

**Files:**
- Create: `tests/core/test_architecture.py`
- Create: `src/domain/__init__.py`
- Create: `src/ui/__init__.py`

**Interfaces:**
- Consumes: 仓库根下的 `src/domain` 与 `src/ui` Python 文件。
- Produces: `find_forbidden_imports(root: Path, forbidden_roots: frozenset[str]) -> list[str]` 测试守卫；违规文本依次包含实际路径、实际行号、`forbidden import` 与实际模块名。

- [x] **Step 1: 写架构守卫与合成违规测试**

`tests/core/test_architecture.py` 使用 `ast.parse` 遍历 `Import`/`ImportFrom`；Domain 禁止根模块 `PySide6/sqlite3/torch/transformers/onnxruntime`，UI 禁止根模块 `infrastructure`。测试必须包含：

```python
def test_source_packages_exist_and_respect_boundaries() -> None:
    assert DOMAIN_ROOT.is_dir(), f"missing package boundary: {DOMAIN_ROOT}"
    assert UI_ROOT.is_dir(), f"missing package boundary: {UI_ROOT}"
    violations = find_forbidden_imports(DOMAIN_ROOT, DOMAIN_FORBIDDEN)
    violations += find_forbidden_imports(UI_ROOT, UI_FORBIDDEN)
    assert not violations, "\n".join(violations)


def test_domain_violation_reports_file_line_and_module(tmp_path: Path) -> None:
    source = tmp_path / "bad_domain.py"
    source.write_text("\nfrom PySide6.QtCore import QObject\n", encoding="utf-8")
    assert find_forbidden_imports(tmp_path, DOMAIN_FORBIDDEN) == [
        f"{source}:2: forbidden import PySide6.QtCore"
    ]


def test_ui_violation_reports_file_line_and_module(tmp_path: Path) -> None:
    source = tmp_path / "bad_ui.py"
    source.write_text("import infrastructure.sqlite_repository\n", encoding="utf-8")
    assert find_forbidden_imports(tmp_path, UI_FORBIDDEN) == [
        f"{source}:1: forbidden import infrastructure.sqlite_repository"
    ]
```

- [x] **Step 2: 运行 RED，确认真实包边界缺失**

Run:

```powershell
& 'G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe' -m pytest tests/core/test_architecture.py -v
```

Expected: `test_source_packages_exist_and_respect_boundaries` 因 `src/domain` 或 `src/ui` 不存在而 FAIL；两个合成违规测试 PASS。

- [x] **Step 3: 写最小包边界**

创建空的 `src/domain/__init__.py` 和 `src/ui/__init__.py`；不创建未来层目录或占位类。

- [x] **Step 4: 运行 GREEN**

Run: 与 Step 2 相同。

Expected: 3 passed。

- [x] **Step 5: 提交架构守卫**

```powershell
git add -- src/domain/__init__.py src/ui/__init__.py tests/core/test_architecture.py
git commit -m "test(TASK-005): enforce minimal architecture boundaries"
```

### Task 3: 用真实 QML 建立启动入口

**Files:**
- Create: `tests/core/test_bootstrap.py`
- Create: `src/bootstrap/__init__.py`
- Create: `src/bootstrap/app.py`
- Create: `src/ui/qml/Main.qml`

**Interfaces:**
- Consumes: `PYTHONPATH=src`、Qt offscreen platform、`src/ui/qml/Main.qml`。
- Produces: `bootstrap.app.main(argv: Sequence[str] | None = None) -> int`；CLI `python -m bootstrap.app [--smoke-test]`。

- [x] **Step 1: 写真实 subprocess 成功启动测试**

`tests/core/test_bootstrap.py` 用当前 Python 子进程和 `QT_QPA_PLATFORM=offscreen` 执行真实 module，先加入：

```python
def test_smoke_startup_loads_qml_and_exits_zero() -> None:
    result = run_app(SRC_ROOT)
    assert result.returncode == 0, result.stderr
```

`run_app` 固定执行 `[sys.executable, "-m", "bootstrap.app", "--smoke-test"]`，将传入目录置于 `PYTHONPATH`，并设置 `QT_QPA_PLATFORM=offscreen`。

- [x] **Step 2: 运行 RED，确认入口缺失**

Run:

```powershell
& 'G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe' -m pytest tests/core/test_bootstrap.py -v
```

Expected: `test_smoke_startup_loads_qml_and_exits_zero` 因 `No module named bootstrap` 而 FAIL；不接受测试收集错误作为 RED。

- [x] **Step 3: 写最小成功启动实现**

`src/bootstrap/app.py` 使用 `argparse` 接受唯一可选参数 `--smoke-test`，创建 `QGuiApplication` 与 `QQmlApplicationEngine`，从模块位置计算 `src/ui/qml/Main.qml`。smoke 模式用 `QTimer.singleShot(0, app.quit)`，其余情况进入正常事件循环；此步尚不实现缺失 QML 的专用错误分支。

`src/ui/qml/Main.qml`：

```qml
import QtQuick
import QtQuick.Controls

ApplicationWindow {
    visible: true
    width: 960
    height: 640
    title: "New Manga"
}
```

- [x] **Step 4: 运行成功启动 GREEN**

Run:

```powershell
& 'G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe' -m pytest tests/core/test_bootstrap.py -v
```

Expected: 启动测试 1 passed。

- [x] **Step 5: 写缺失 QML 测试**

追加：

```python
def test_missing_qml_returns_nonzero_with_path(tmp_path: Path) -> None:
    isolated_src = tmp_path / "src"
    shutil.copytree(SRC_ROOT / "bootstrap", isolated_src / "bootstrap")
    result = run_app(isolated_src)
    expected = isolated_src / "ui" / "qml" / "Main.qml"
    assert result.returncode != 0
    assert str(expected) in result.stderr
```

- [x] **Step 6: 运行错误分支 RED**

Run: 与 Step 4 相同。

Expected: 成功启动测试 PASS；缺失 QML 测试因当前进程返回 0 或 stderr 缺少确定路径而 FAIL。

- [x] **Step 7: 写最小错误处理**

加载后若 `engine.rootObjects()` 为空，向 stderr 输出 `Failed to load QML:` 和计算出的绝对路径并返回 1；不增加错误类型层级或日志框架。

- [x] **Step 8: 运行完整 GREEN**

Run:

```powershell
& 'G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe' -m pytest tests/core/test_bootstrap.py -v
& 'G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe' -m pytest tests/core -v
```

Expected: 启动测试 2 passed；完整 core 5 passed；无 warning/error。

- [x] **Step 9: 提交启动入口**

```powershell
git add -- src/bootstrap/__init__.py src/bootstrap/app.py src/ui/qml/Main.qml tests/core/test_bootstrap.py
git commit -m "feat(TASK-005): add minimal QML bootstrap"
```

### Task 4: 固化可复现验证

**Files:**
- Create: `verification/TASK-005/verify.ps1`
- Create: `verification/TASK-005/author-verification.md`

**Interfaces:**
- Consumes: 参数 `-BaseCommit`（默认 TASK 基线）、`-ReviewedHead`（默认 `HEAD`）、`-PythonExe`（默认 `python`）。
- Produces: allowed-path、锁定依赖、可选依赖缺失、架构测试、真实 QML smoke、链接/围栏和 `git diff --check` 的退出码证据。

- [ ] **Step 1: 写 PowerShell 验证脚本**

脚本必须：

1. 解析 base/head 并拒绝 base 不是 head 祖先；
2. 只允许 TASK-005 白名单路径，显式拒绝任何 `doc/tasks/TASK-006.md`～`TASK-027.md` 变更；
3. 核对 Python 为 3.12、requirements 精确集合且无重型依赖；
4. 核对 torch/transformers/onnxruntime 在传入解释器中均 `find_spec(...) is None`；
5. 设置 `PYTHONPATH=src`、`QT_QPA_PLATFORM=offscreen`，依次运行 `python -m pytest tests/core` 与 `python -m bootstrap.app --smoke-test`；
6. 核对 TASK-005 相关 Markdown 本地链接与代码围栏；
7. 使用解析后的 base/head 运行 `git diff --check`，任一子命令非零即整体非零。

- [ ] **Step 2: 运行完整验证**

Run:

```powershell
pwsh -NoProfile -File ./verification/TASK-005/verify.ps1 -BaseCommit d65901b953e6fb26043344ed3d668520847eb295 -ReviewedHead HEAD -PythonExe 'G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe'
```

Expected: 退出码 0；每项打印 `PASS`；pytest 报告 5 passed。

- [ ] **Step 3: 记录作者验证证据**

`author-verification.md` 写入实际 `git rev-parse HEAD`、Windows/CPU、Python/Qt/pytest 版本、完整命令、退出码和结果。模型质量、SQL、性能、打包与干净 Windows 机器验证明确写 `NOT_RUN`；不得把 TASK-004 的实验结果冒充本 head 结果。

- [ ] **Step 4: 提交验证内容并固定 reviewed head**

```powershell
git add -- verification/TASK-005/verify.ps1 verification/TASK-005/author-verification.md
git commit -m "test(TASK-005): add reproducible bootstrap verification"
git rev-parse HEAD
```

打印的完整 SHA 是 DeepSeek 唯一 `reviewed_head`。

### Task 5: 作者交付与 Review 准备

**Files:**
- Modify: `doc/tasks/TASK-005.md`
- Create: Handoff 路径由下列命令计算，避免手填或猜测 commit：

```powershell
$reviewedHead = (git rev-parse HEAD).Trim()
$handoffPath = "doc/handoffs/TASK-005-$($reviewedHead.Substring(0, 7)).md"
```

**Interfaces:**
- Consumes: Task 4 打印的固定 reviewed head 与实际验证证据。
- Produces: 状态 `in_review`、绑定 base/head 的 Handoff、DeepSeek 可直接执行的 Review 指令。

- [ ] **Step 1: 复跑固定 head 验证**

在一次性 detached worktree 或当前干净 worktree 对固定 reviewed head 运行 Task 4 Step 2 的同一命令；记录准确输出和退出码。

- [ ] **Step 2: 写 Handoff 并更新 Task**

Handoff 记录固定 `base_commit`、`reviewed_head`、提交列表、变更路径、四条 AC 的证据、实际命令、PASS/NOT_RUN、风险和下一接收者 DeepSeek Harness。Task 状态改为 `in_review`；Handoff 元数据提交不改变 reviewed head。

- [ ] **Step 3: 提交 Handoff 元数据**

```powershell
git add -- doc/tasks/TASK-005.md $handoffPath
git commit -m "docs(TASK-005): hand off bootstrap for review"
```

- [ ] **Step 4: 核对冻结范围**

Run:

```powershell
git diff --name-only d65901b953e6fb26043344ed3d668520847eb295 HEAD
git diff --check d65901b953e6fb26043344ed3d668520847eb295 HEAD --
git status --short --branch
```

Expected: 所有路径符合 TASK-005 白名单，TASK-006～TASK-027 零变化，diff check 退出码 0，worktree 干净。

## Plan Self-Review

- Spec coverage：依赖锁定、Core 无重型依赖启动、最小 QML、Domain/UI 守卫、诊断失败、验证证据与 Handoff 均有对应任务。
- File map：只使用 TASK-005 白名单；未创建未来层、业务页、数据库、Provider、打包配置或 CI。
- Type consistency：唯一生产接口固定为 `main(argv: Sequence[str] | None = None) -> int`；唯一测试守卫接口固定为 `find_forbidden_imports(Path, frozenset[str]) -> list[str]`。
- Test integrity：生产入口先由 subprocess 测试观察缺失失败；测试断言真实退出码、stderr 与 QML 加载，不断言 mock。
