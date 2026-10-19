# AC7 — 61 个 evidence_dir 未登记文件的只读分类

**Task**: GOV-DEBT-CLEANUP-2 · **AC**: AC7 · **性质**: 只读分类

**事实来源**: `verification/P09-GOVERNANCE-DEBT-20261019/evidence-dir-classification.md`。

**关键限制（本 AC 的诚实边界）**：AC7 要求「只有证实文件是已释放 AC 的唯一最终证据时，
才可列入对应 Canonical Evidence」。判定「唯一最终证据」需要逐文件阅读内容并对照 AC 原文，
**本文件没有做这件事**。因此下列 61 项**全部保持候选分类**，没有任何一项被登记进 Canonical Evidence。

| 候选分类 | 数量 | 本 Task 的处理 |
|---|---:|---|
| A 形似有判别力 | 10 | 仅记录为候选，**未登记进 Canonical Evidence**（未验证唯一性） |
| B 形似过程产物 | 49 | 仅记录为候选过程产物，**未移走** |
| C 本不属此目录 | 2 | 记录用途待核实，**未删除、未移动** |

## 逐文件

### EXPORT-REVEAL-1

| 文件 | 候选分类 | 唯一最终证据 | 处理结论 |
|---|---|---|---|
| `post-merge-packaged-capture-error.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `pytest-core.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `rust-packaged.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `rust-source.log` | B | 未验证 | 保持候选，不登记、不移走 |

### FEAT-CREATE-3

| 文件 | 候选分类 | 唯一最终证据 | 处理结论 |
|---|---|---|---|
| `dsh-review-r1.md` | A | 未验证 | 保持候选，不登记、不移走 |

### FEAT-CREATE-4

| 文件 | 候选分类 | 唯一最终证据 | 处理结论 |
|---|---|---|---|
| `dsh-review-r1.md` | A | 未验证 | 保持候选，不登记、不移走 |
| `gui-uia-command-r5.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `isolation-namespace-rebind.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `isolation-prepare.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `prepare-isolated-data.ps1` | B | 未验证 | 保持候选，不登记、不移走 |
| `rebind-isolated-namespace.py` | B | 未验证 | 保持候选，不登记、不移走 |
| `run-create-uia.ps1` | B | 未验证 | 保持候选，不登记、不移走 |
| `source-preservation-check.log` | B | 未验证 | 保持候选，不登记、不移走 |

### FEAT-IMPORT-MULTI-1

| 文件 | 候选分类 | 唯一最终证据 | 处理结论 |
|---|---|---|---|
| `appdata-preservation.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `checkpoint.md` | B | 未验证 | 保持候选，不登记、不移走 |
| `dsh-review-r1.md` | A | 未验证 | 保持候选，不登记、不移走 |
| `fixture-generation.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `gui-runner-console.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `isolation-prepare.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `main-worktree-status.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `make-fixtures-r1.py` | B | 未验证 | 保持候选，不登记、不移走 |

### HOST-TTL-BOUNDARY-1

| 文件 | 候选分类 | 唯一最终证据 | 处理结论 |
|---|---|---|---|
| `ac3-rust-ttl-boundary-build-attempt-1.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `ac4-export-frozen-rust-attempt1-4662239.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `ac4-frozen-host-importpages.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `ac6-rust-tests.log` | B | 未验证 | 保持候选，不登记、不移走 |

### P14

| 文件 | 候选分类 | 唯一最终证据 | 处理结论 |
|---|---|---|---|
| `frontend-build.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `frontend-tests.log` | B | 未验证 | 保持候选，不登记、不移走 |

### P15

| 文件 | 候选分类 | 唯一最终证据 | 处理结论 |
|---|---|---|---|
| `cargo-test-unfiltered-first-run.log` | B | 未验证 | 保持候选，不登记、不移走 |

### P15-CORE-1C

| 文件 | 候选分类 | 唯一最终证据 | 处理结论 |
|---|---|---|---|
| `canonical-hash-verification.txt` | A | 未验证 | 保持候选，不登记、不移走 |
| `pytest-core-focused.command.txt` | B | 未验证 | 保持候选，不登记、不移走 |
| `pytest-core-focused.environment.txt` | B | 未验证 | 保持候选，不登记、不移走 |
| `pytest-core-focused.exit-code.txt` | B | 未验证 | 保持候选，不登记、不移走 |
| `pytest-core-focused.log` | B | 未验证 | 保持候选，不登记、不移走 |

### P15-HOST-1

| 文件 | 候选分类 | 唯一最终证据 | 处理结论 |
|---|---|---|---|
| `.gitattributes` | C | 未验证 | 保持候选，不登记、不移走 |
| `core-pytest-full-suite-extra.txt` | B | 未验证 | 保持候选，不登记、不移走 |
| `resource-manifest.json` | A | 未验证 | 保持候选，不登记、不移走 |

### P15-HOST-2

| 文件 | 候选分类 | 唯一最终证据 | 处理结论 |
|---|---|---|---|
| `ac1-coordinator-blocker.md` | B | 未验证 | 保持候选，不登记、不移走 |
| `core-pytest-final.log` | A | 未验证 | 保持候选，不登记、不移走 |
| `frontend-deps-setup.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `frontend-vitest-alias-attempt.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `frontend-vitest-final.log` | A | 未验证 | 保持候选，不登记、不移走 |
| `frontend-vitest-isolated.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `host-only-rescan.ps1` | B | 未验证 | 保持候选，不登记、不移走 |
| `modified-files-sha256.py` | B | 未验证 | 保持候选，不登记、不移走 |

### P19-BOOT-1

| 文件 | 候选分类 | 唯一最终证据 | 处理结论 |
|---|---|---|---|
| `.gitignore` | C | 未验证 | 保持候选，不登记、不移走 |

### P19-UI-FIX-1

| 文件 | 候选分类 | 唯一最终证据 | 处理结论 |
|---|---|---|---|
| `04-settings-before-final-code-refinement.uia.txt` | B | 未验证 | 保持候选，不登记、不移走 |
| `04-settings-uia-pass-2.txt` | B | 未验证 | 保持候选，不登记、不移走 |
| `04-settings-uia-pass-exit-code-blank.txt` | B | 未验证 | 保持候选，不登记、不移走 |
| `app-err-before-final-code-refinement.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `app-err-namespace-mismatch.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `app-err-ui-a-pass-exit-code-blank-2.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `app-err-ui-load-failure.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `app-err-uia-pass-exit-code-blank.log` | B | 未验证 | 保持候选，不登记、不移走 |

### P19-UI-FIX-2

| 文件 | 候选分类 | 唯一最终证据 | 处理结论 |
|---|---|---|---|
| `appdata-source-after.json` | B | 未验证 | 保持候选，不登记、不移走 |
| `appdata-source-before.json` | B | 未验证 | 保持候选，不登记、不移走 |
| `bookshelf-import-targeted-test-final-r2.log` | A | 未验证 | 保持候选，不登记、不移走 |
| `bookshelf-import-targeted-test-final.log` | A | 未验证 | 保持候选，不登记、不移走 |
| `bookshelf-import-targeted-test.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `cargo-build-before.log` | B | 未验证 | 保持候选，不登记、不移走 |
| `dsh-review-r1.md` | A | 未验证 | 保持候选，不登记、不移走 |
| `frontend-npm-build-before.log` | B | 未验证 | 保持候选，不登记、不移走 |

## 明确未做的事

- 未将任何文件登记进任何 Task 的 Canonical Evidence。
- 未移动、删除或归档任何 evidence 文件。
- 未修改 `.gitattributes` 或 `.gitignore`（C 类两项原样保留）。
- 未仅凭文件名把某项降级为「非证据」——候选分类不是结论。
