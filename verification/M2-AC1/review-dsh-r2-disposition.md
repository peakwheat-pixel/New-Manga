# M2-AC1 DSH r2 Review disposition（Owner=ZCode）

- Review report: [M2-AC1-d8c1173b-dsh-r2.md](../../doc/reviews/M2-AC1-d8c1173b-dsh-r2.md)（DeepSeek Harness 非作者，静态 Review，`decision: approved` 条件批准；r2 新增 P2×2、P3×1、P4×4）
- r2 被审 head：`d8c1173b`；返修提交：`521d96ca`（findings 落实）→ `b9d9a8ab`（干净 tip 重采日志，落实 R2-02）→ `a57e4834`（终版 gate 证据）→ `cd261f70`（whitespace）

## 逐条处置

| ID | 级别 | disposition | 处置说明 |
|---|---|---|---|
| R2-01 | P2 | **fixed**（r3 复核进一步修正，见 R3-01/R3-02/R3-03） | Handoff §验证证据表与 Task 表同步更新（cargo 26 / vitest 19 / gate 场景数 / front-matter delivery_head 演进）。首轮更新遗留三处（场景计数 44 应为 45、全仓行 PASS 口径、AC3 旧 PID），由 r3 R3-01/02/03 收敛修复。 |
| R2-02 | P2 | **fixed** | 四套件日志在干净 tip 重采：cargo / pytest-m2-acceptance / pytest-full-suite 头部 `worktree HEAD=521d96ca`（重采时 tip）+ `worktree clean` 计数 + `# EXIT:`；vitest 重采存在重定向缺陷未落盘，r3 R3-05 补齐（HEAD=`cd261f70`、19 passed EXIT 0）。 |
| R2-03 | P3 | **fixed** | `e2e-evidence/NOTE.md` 标注旧存档 stale（旧格式、PATH python 探针歧义、无新增断言场景）。r3 指出其中场景计数错误（27→36、44→45），随 R3-02 修正。 |
| R2-04 | P4 | **fixed** | `run_e2e.py` 新场景 null/缺键容忍：`(x or {})`、`isinstance` 守卫、`pages_comparable()` 校验（缺键记 FAIL 并 return None，fail-closed 不崩溃）。 |
| R2-05 | P4 | **fixed** | `implementation_commit()` 对非零退出/空串回退可见的 `"UNKNOWN"`。 |
| R2-06 | P4 | **fixed** | main.rs ACL 测试 doc 注释改为 "ten live commands (seven resource-channel + three M2-AC1 acceptance)"。 |
| R2-07 | P4 | **fixed** | `record_environment` 新增 `EVN-pyside6` 探测（`import PySide6` + `__version__`），失败并入 `usable` 走 BLOCKED exit 2；终版 gate 该场景 PASS（6.11.2）。 |

## 返修后验证（r2 返修系列提交上执行）

| 门禁 | 结果 |
|---|---|
| `pytest tests/m2_acceptance -q` | 4 passed, EXIT 0（HEAD=521d96ca） |
| `cargo test --locked` | 26 passed, EXIT 0（HEAD=521d96ca） |
| `npm test`（vitest） | 19 passed, EXIT 0（HEAD=cd261f70 重采） |
| 全仓 pytest | 1320 passed + 2 failed（Legacy QML 会话级环境回归，base 对照 @1347a67c 复现同 2 失败；r3 已接受该披露） |
| `python verification/M2-AC1/run_e2e.py`（完整构建版） | GATE PASS 45 场景（`implementation_commit=b9d9a8ab`） |

r3 复核报告：[M2-AC1-cd261f70-dsh-r3.md](../../doc/reviews/M2-AC1-cd261f70-dsh-r3.md)；r3 findings 的逐条处置见 [review-dsh-r3-disposition.md](review-dsh-r3-disposition.md)。
