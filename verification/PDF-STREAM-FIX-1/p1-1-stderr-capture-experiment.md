# P1-1 实验：子进程也无法捕获 MuPDF 的 stderr

**产出**: 2026-10-20 · **对应**: `PDF-STREAM-FIX-1` 的 P1-1
**ZCode 的建议**（Review §3.3）：用子进程隔离渲染，在 OS 层用管道接收 fd 2，
**「无论 MuPDF 走 CRT `fprintf(stderr)` 还是自有 callback，只要最终写到标准错误句柄，管道就能收到」**。

**ZCode 因无 shell 无法执行这个实验。我执行了。结论是它不成立。**

## 一、实验

**三步**：

1. **生成两个 PDF**：一个用修复后的代码，一个用回滚后的代码（缺陷版）
2. **在子进程里渲染**：`subprocess.run([sys.executable, child, pdf_path], capture_output=True)`
3. **检查子进程的 stderr 里有没有 `zlib error`**

## 二、结果

### 2.1 第一轮（默认配置）

```
fixed   exit=0  child_done=True  zlib_in_stderr=False  stderr_bytes=0
broken  exit=0  child_done=True  zlib_in_stderr=False  stderr_bytes=0
```

**两个都是 0 字节 stderr。**

### 2.2 第二轮（显式启用 MuPDF 的错误显示）

**先查 PyMuPDF 的显示控制**：

```
TOOLS attrs: ['mupdf_display_errors', 'mupdf_display_warnings']
mupdf_display_errors: 1        ← 默认已启用
mupdf_display_warnings: 0
```

**然后在子进程里显式调用 `pymupdf.TOOLS.mupdf_display_errors(True)`**：

```
fixed   exit=0  done=True  stderr_bytes=0  zlib_in_stderr=False
broken  exit=0  done=True  stderr_bytes=0  zlib_in_stderr=False
```

**仍然是 0 字节。**

## 三、所以 ZCode 的推理哪里不成立

**它的假设是**：「只要 MuPDF 最终写到标准错误句柄，管道就能收到」。

**实测表明这个假设在当前环境下不成立。**

**可能的原因是 MuPDF 的 `fz_warn` / `fz_error` 输出路径做了 TTY 检测**——
**输出到管道时静默，输出到终端时可见。**

**这解释了全部观察**：

| 场景 | stderr 是 | 是否可见 |
|---|---|---|
| `python -c` 直接在终端跑 | 终端 | **可见** |
| pytest 的 `capsys` | Python 对象 | 不可见 |
| pytest 的 `capfd` | 管道 | 不可见 |
| **子进程 + `capture_output=True`** | **管道** | **不可见** |

**所以「不可见」的条件是「stderr 不是终端」，而不是「pytest 的捕获机制有 bug」。**

**ZCode 把原因归给 pytest 的捕获，实际原因更靠上——在 MuPDF 自己。**

## 四、这不改变它的结论，但改变了理由

**ZCode 说「AC3 本身不是不可测的」，并列了两点理由**：

1. **AC4 在逻辑上蕴含 AC3**（渲染出非白像素 ⟹ inflate 成功 ⟹ 无 zlib error）
2. **子进程方案大概率可测**

**第 2 条被证伪。第 1 条成立。**

**所以 AC3 的处置仍然是**：

- **「MuPDF 不报 zlib error」这个文本断言在当前环境下不可机器验证**
- **但 AC3 的实质要求（content stream 能被正确解析）由 AC4 覆盖**

**这比「AC3 不可测」更准确，也比「子进程能测」更诚实。**

## 五、另一个可以试但没试的方向

**如果 stderr 必须是终端才可见，那么理论上有两条路**：

1. **伪终端（pty）**——`pty.openpty()` 然后把 fd 2 接到 slave 端。
   **Windows 上没有 POSIX `pty`；`conpty` 需要额外 API。** 成本高，且对 Windows 的收益不确定。
2. **MuPDF 的 callback 配置**——但 PyMuPDF 只暴露了 `mupdf_display_errors(bool)`，
   **没有暴露自定义 callback 的接口**（`TOOLS` 的两个 attrs 之外没有别的）。

**两条路我都没做，因为**：

- **第 1 条的收益不抵成本**——为一个测试引入 pty 依赖
- **第 2 条在 PyMuPDF 的公开 API 里不可行**

**而 AC4 已经覆盖了实质。**

## 六、结论与处置

**按 ZCode 的 P1-1 选项 2**：

- **删除 `test_mupdf_reports_no_zlib_error`**
- **在本 Task 文档记录「AC3 的 stderr 文本不可机器断言」及其机制证据**
- **AC3 的实质由 AC4 蕴含**

**本文件就是那个「机制证据」。**

## 七、这个实验值得记在哪

**它的价值不在「ZCode 错了」——它的建议是合理的，只是前提未验证。**

**它的价值在于**：

> **一个「不可测」的结论，只有在**试过最可能可行的那条路**之后才成立。**

**ZCode 提出子进程方案时说「未验证」。**

**如果我信了「子进程能测」而不做实验，我会：**

- **或者写出一个永远绿的测试**（和现在这个一样）
- **或者在一个无法实现的方向上继续花时间**

**做了实验，我才知道应该走选项 2 而不是选项 1。**

## 八、明确未做

- **未尝试 pty / conpty 方案**（§五，成本收益不成立）
- **未确认 MuPDF 静默的确切机制**（是 `isatty` 检测还是别的）——
  本文件只证明「管道下静默」这个现象
- **未检查其它 MuPDF 版本是否有不同行为**（本机是 PyMuPDF 1.28.2 / MuPDF 1.28.2）
