# VERSION-MANIFEST-GUARD-1 证据

卡面：`doc/tasks/VERSION-MANIFEST-GUARD-1.md`。基线 `939049edd`。

## 1. 为什么做这个

`INSTALLER-MATRIX-1` 的 r1 复核 **REJECT** 并抓到审核者我两处**造假**：

1. `VERSION.json` 的 `app_build.repo_head` 写 `fe7da5d92…`，而 stage 里 exe 内嵌的是 `5dda04437…`
   ⇒ **那个包根本不含当前 head 的传输层修复**；
2. `sidecar_build.repo_head` 写的完整 hash 是 **bad object**（我编造了尾部）。

**根因不是"写错"，而是没有任何机器校验** —— 复核者靠手工重算才发现。本卡把那次手工重算变成**阻断式检查**。

## 2. 交付

### 2.1 新增 `tools/ci/verify-package-manifest.ps1`

fail-closed 校验，逐项比对（任何不一致 → 非零退出，**从不"警告后继续"**）：

| 检查 | 说明 |
|---|---|
| `app/NewManga.App.exe` | sha256 + 字节数 == `VERSION.json.app_build` |
| **`app_build.repo_head`** | **从 exe 内嵌 `ProductVersion`（`x.y.z+<40hex>`）反解**，与 json 比对 |
| 该 head 是否存在于仓库 | `git cat-file -e <head>`，不存在即失败 |
| `app/core-sidecar/core_service.exe` | sha256 + 字节数 == `sidecar_build` |
| `*.onnx` 数量与总字节 | 与 `models_bundled` / `models_bundled_bytes` 比对，且 `models_bundled` 必须等于 `(count > 0)` |
| 字段缺失 | `models_bundled` 缺失也**算失败**（不允许"省略即通过"） |

### 2.2 接入构建（AC4）

`apps/desktop-avalonia/scripts/build-installer.ps1` 在 **makensis 之前**调用它；校验失败即 `throw`，
**拒绝出包**。脚本缺失同样 `throw`（不放行）。

## 3. 判别力（三次实验，全部实测）

| # | 实验 | 结果 |
|---|---|---|
| 1 | 把 `exe_sha256` 改一个字符 | **FAIL**：`app_build.exe_sha256 mismatch: json=b3ec2133… actual=a3ec2133…`（exit 1） |
| **2** | **把 `repo_head` 改回我当初那个假值 `5dda04437`（一个真实存在的 head）** | **FAIL**：`app_build.repo_head mismatch: json=5dda04437… embedded=71cecb95a…`（exit 1）—— **这正是能抓住我造假的机制** |
| 3 | 把 `exe_bytes` 改成 `99554851` 后**跑构建脚本** | **构建中止**：`VERSION-MANIFEST-GUARD-1: stage does not match VERSION.json … refusing to build the installer`（exit 1） |
| — | 三次实验后复原 | **OK**：`exe, core_service, 3 onnx / 632552582 B all match VERSION.json`（exit 0） |

**实验 2 是关键**：它证明**即使写成"另一个真实存在的 head"**（最像人手的错误写法），
也会被"exe 内嵌 head vs json head"的比对抓住 —— 不再是"两个都合法所以放过"。

## 4. 四件套与基线（AC7）

```
check          PASS (3 warnings)
verify_pins    18/18
inventory      OK (1/80/6=87)
CoreClient     192 / 0 / 30 / 222（无夹具）
Host           321 / 0 / 74 / 395（无夹具）
```

## 5. 未完成（如实登记）

- **AC6（E-8 守卫）未做**：在测试里捕获 Avalonia binding error（或解析启动日志出现
  `[Binding] An error occurred` 即失败）**尚未实现**。卡面允许拆出，此处**明确登记**，不静默跳过。
  E-8 本身仍未修（Studio 页 10 条绑定错误）。
- 校验脚本**只覆盖 stage 层**：不校验 setup.exe 与 stage 的一致性（setup 是 makensis 产物，
  其 sha256 由 `build-info.json` 记录，但未进入 fail-closed 链）。
- 未覆盖 `package-manifest.json`（stage 内另一份清单）与 `VERSION.json` 的一致性。

## 6. 诚实边界

本卡**没有**让发布管线自动运行在 CI 里 —— 它只在**有人跑 `build-installer.ps1`** 时生效。
若绕过该脚本直接调 makensis，校验不会执行（`build-info.json` 里会缺它的输出）。
**因此"今后不会再有假 head"这句话不能成立** —— 只能说"走标准构建路径时，假 head 会被拦住"。
