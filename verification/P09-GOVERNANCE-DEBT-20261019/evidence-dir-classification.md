# evidence_dir 未登记文件的三分类提案

**依据**：`codex-debt-ruling.md` §5「DSH 提案、Codex 裁决」。
**这些是分类提案，不是处置**；是否登记进 Canonical Evidence、是否移入 workspace，由 Codex 决定。

分类口径：
- **A 有判别力**：审查/裁决/门禁/最终验证/清单类文件，形似应当版本化为当前证据。
- **B 过程产物**：重试、首选失败、试跑、抓取、诊断、临时类，形似应归入 workspace。
- **C 本不属此目录**：`.gitattributes` / `.gitignore` / `.gitmodules` / `.editorconfig` 之类配置文件。

**判定方法**：按文件名模式初判，再逐条对照该 Task 的 Canonical Evidence 表是否已列同名条目。
文件名不足以确定的，一律默认 B（保守：当作过程产物），并在此文末单列待 Codex 确认。

共 61 个文件、13 个 Task。

## EXPORT-REVEAL-1

| 文件 | 分类提案 | 依据 |
|---|---|---|
| `post-merge-packaged-capture-error.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `pytest-core.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `rust-packaged.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `rust-source.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |

## FEAT-CREATE-3

| 文件 | 分类提案 | 依据 |
|---|---|---|
| `dsh-review-r1.md` | A | 命名含审查/门禁/验证/清单语义 |

## FEAT-CREATE-4

| 文件 | 分类提案 | 依据 |
|---|---|---|
| `dsh-review-r1.md` | A | 命名含审查/门禁/验证/清单语义 |
| `gui-uia-command-r5.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `isolation-namespace-rebind.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `isolation-prepare.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `prepare-isolated-data.ps1` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `rebind-isolated-namespace.py` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `run-create-uia.ps1` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `source-preservation-check.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |

## FEAT-IMPORT-MULTI-1

| 文件 | 分类提案 | 依据 |
|---|---|---|
| `appdata-preservation.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `checkpoint.md` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `dsh-review-r1.md` | A | 命名含审查/门禁/验证/清单语义 |
| `fixture-generation.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `gui-runner-console.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `isolation-prepare.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `main-worktree-status.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `make-fixtures-r1.py` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |

## HOST-TTL-BOUNDARY-1

| 文件 | 分类提案 | 依据 |
|---|---|---|
| `ac3-rust-ttl-boundary-build-attempt-1.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `ac4-export-frozen-rust-attempt1-4662239.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `ac4-frozen-host-importpages.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `ac6-rust-tests.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |

## P14

| 文件 | 分类提案 | 依据 |
|---|---|---|
| `frontend-build.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `frontend-tests.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |

## P15-CORE-1C

| 文件 | 分类提案 | 依据 |
|---|---|---|
| `canonical-hash-verification.txt` | A | 命名含审查/门禁/验证/清单语义 |
| `pytest-core-focused.command.txt` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `pytest-core-focused.environment.txt` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `pytest-core-focused.exit-code.txt` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `pytest-core-focused.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |

## P15-HOST-1

| 文件 | 分类提案 | 依据 |
|---|---|---|
| `.gitattributes` | C | 配置文件，不属于证据目录 |
| `core-pytest-full-suite-extra.txt` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `resource-manifest.json` | A | 命名含审查/门禁/验证/清单语义 |

## P15-HOST-2

| 文件 | 分类提案 | 依据 |
|---|---|---|
| `ac1-coordinator-blocker.md` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `core-pytest-final.log` | A | 命名含审查/门禁/验证/清单语义 |
| `frontend-deps-setup.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `frontend-vitest-alias-attempt.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `frontend-vitest-final.log` | A | 命名含审查/门禁/验证/清单语义 |
| `frontend-vitest-isolated.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `host-only-rescan.ps1` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `modified-files-sha256.py` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |

## P15

| 文件 | 分类提案 | 依据 |
|---|---|---|
| `cargo-test-unfiltered-first-run.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |

## P19-BOOT-1

| 文件 | 分类提案 | 依据 |
|---|---|---|
| `.gitignore` | C | 配置文件，不属于证据目录 |

## P19-UI-FIX-1

| 文件 | 分类提案 | 依据 |
|---|---|---|
| `04-settings-before-final-code-refinement.uia.txt` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `04-settings-uia-pass-2.txt` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `04-settings-uia-pass-exit-code-blank.txt` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `app-err-before-final-code-refinement.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `app-err-namespace-mismatch.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `app-err-ui-a-pass-exit-code-blank-2.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `app-err-ui-load-failure.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `app-err-uia-pass-exit-code-blank.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |

## P19-UI-FIX-2

| 文件 | 分类提案 | 依据 |
|---|---|---|
| `appdata-source-after.json` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `appdata-source-before.json` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `bookshelf-import-targeted-test-final-r2.log` | A | 命名含审查/门禁/验证/清单语义 |
| `bookshelf-import-targeted-test-final.log` | A | 命名含审查/门禁/验证/清单语义 |
| `bookshelf-import-targeted-test.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `cargo-build-before.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |
| `dsh-review-r1.md` | A | 命名含审查/门禁/验证/清单语义 |
| `frontend-npm-build-before.log` | B | 命名含尝试/重试/诊断/临时语义，或语义不明 |

## 汇总

| 分类 | 文件数 |
|---|---:|
| A 有判别力（提案登记） | 10 |
| B 过程产物（提案移入 workspace） | 49 |
| C 本不属此目录 | 2 |

## 需要 Codex 确认的边界

- 文件名分类必然有误判风险：例如 `pytest-core.log` 可能是该 AC 的唯一运行证据（应 A），
  也可能只是重复运行的一次尝试（应 B）。本表不替 Codex 判断「哪个才是判别力结果」。
- `.gitattributes` / `.gitignore` 出现在 evidence_dir 的动机（例如排除大文件、固定行尾）
  未在本表核实；若确有功能用途，其去留需另行裁定。
- 本表不含任何「移走」「登记」「删除」动作。
