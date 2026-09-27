# M2-S3 探针运行记录（原始命令与 exit code）

- 日期：2026-09-26；shell：Git Bash（命令）/ Python 3.14.6 subprocess（运行器）
- 所有路径中 `%TEMP%` = `C:\Users\49745\AppData\Local\Temp`

## 1. fixture 生成

```
python experiments/M2-S3/fixtures/gen_fixtures.py
```
- exit 0；产出 `%TEMP%\m2s3-lab\`（scope 内 asset.png/typical.png 独立副本、scope 外对抗树、junction `scope/derived/linkj -> outside/dir` created=True）与 `fixtures.json`（SHA-256 清单，副本见本目录 `fixtures.json`）。
- 同步写入 Tauri 构建所需最小 icon `experiments/M2-S3/probe/icons/icon.ico`。

## 2. 构建

```
cd experiments/M2-S3/probe && cargo build --release
```
- 首次全栈编译：完成（依赖 300+ crates；见 `experiments/M2-S3/probe/Cargo.lock` 锁定版本）。
- 过程中修复的 Owner 侧缺陷（如实记录，均在探针代码内，不涉产品）：
  1. E0308/E0599：缺 `use tauri::Manager;` 与借用错误——编译错误，修复。
  2. **首次运行挂起（180 s 无结果）**：`window.__TAURI__` 未注入——`tauri.conf.json` 缺 `app.withGlobalTauri: true`；修复并给 JS 加 20 s 兜底退出。
  3. **启动 fail-fast（0xC0000409，0.4 s）**：`sign_all()` 对 junction rel 调用 `issue().unwrap()`，而 issue 侧 canonicalize 会解析 junction 触发 `REF_OUT_OF_SCOPE` panic；按 M2-S2 语义修正——issue 只做存在性记录，containment 权威在 resolve 层；`sign_all` 的 unwrap 改为容错（issue 被拒时写入哨兵 ID，由场景如实记录 FAIL）。
  4. **ID 长度缺陷（16 场景全 FAIL→修复后全 PASS）**：`b64_id` 用 24 字节随机（32 字符）而格式门按 43 字符（32 字节）判定——合法 ID 全被 `REF_MALFORMED` 拒绝；修正为 32 字节（256-bit，43 字符）。JS 侧 N-01 的随机 ID 同步改为合法格式。
  5. 移除 `windows_subsystem="windows"` 以保留启动 stderr 作为证据。

## 3. 探针运行（两次，重复运行一致性）

运行器（等价命令）：
```
M2S3_LAB=%TEMP%\m2s3-lab M2S3_PROBE_OUT=%TEMP%\m2s3-probe-results.json \
M2S3_PROBE_LOG=%TEMP%\m2s3-probe.log WEBVIEW2_USER_DATA_FOLDER=%TEMP%\m2s3-webview2-udd \
experiments/M2-S3/probe/target/release/m2s3-probe.exe
```
- 第 1 次运行：**exit 0**，elapsed 4.2 s；结果 `raw/probe-results-first.json`
- 第 2 次运行（lab 重入，fixture 不重建）：**exit 0**，elapsed 4.1 s；结果 `raw/probe-results-repeat.json`
- 一致性：16/16 场景两次运行 status 逐项相同（差异 NONE）；P-01 交付字节 SHA-256 跨运行一致（`50f5a4cc…f4526a3`）。
- 结果矩阵：16 PASS / 0 FAIL / 0 BLOCKED（详见研究报告 §4 与两份结果 JSON）。

## 4. 泄漏扫描

```
python（对 raw/probe-results-first.json 与 raw/probe-results-repeat.json 全文扫描）
```
- 扫描词表：`49745`、`C:\Users`、`AppData`、`m2s3-lab`、`asset.png`、`typical.png`、`outside_secret`、`user_source_private`、`outside\dir`、`scope\derived`、`linkj`
- 结果：**0 命中**，CLEAN（`leakage-scan.json`）。

## 5. 未运行项

- WebView2 `asset:` 内置协议（convertFileSrc）对照：**未运行**——其形态要求 WebView 持 OS path，被 Contract 1.1 T5.1 直接排除（设计层面不合格），见报告 §3。
- 冷缓存（S1-B6）、DACL/完整性（S1-B3）、打包/沙箱（S1-B8）、产品 pytest：不在本 Task 范围，NOT_RUN。
- 真流式（分块 body）在途撤销窗口：handler 形态为一次性 body（`chunks=1`），无法构造"流中途"窗口；限制记录，见报告 §5。
