# 更正：FPS 早已实测通过，是我看错了

**产出**: 2026-10-20 · **性质**: 更正记录 · **触发**: Codex r31

## 一、我错了什么

`verification/P20/ac4-measurability-analysis.md`（我上一轮写的）断言：

> **`FpsRecorderPanel` 从未挂载到产品界面**
> **全仓搜索「谁 import 它」：只有 `FpsRecorderPanel.test.tsx`**
> **FPS 测量不可行，需产品改动**

**这三条全错。**

## 二、实际情况

### 2.1 面板**已挂载**

`apps/desktop/frontend/src/main.tsx` L3-4、L15-23：

```tsx
import { FpsRecorderPanel } from "./perf/FpsRecorderPanel";
import { readFpsRecorderRequest, startFpsRecorder } from "./perf/fpsRecorder";

const fpsSamplingRequested = readFpsRecorderRequest();
const fpsRecorder = fpsSamplingRequested ? startFpsRecorder() : null;

ReactDOM.createRoot(...).render(
  <>
    <App />
    {fpsRecorder ? <FpsRecorderPanel recorder={fpsRecorder} /> : null}
  </>,
);
```

**三种开关已接在入口上，面板条件挂载。设计是对的。**

### 2.2 FPS **早已实测**

`verification/P20-AC4-FPS-1/ac3-real-desktop/`：

| 场景 | samples | **avg** | p95 | max | excluded | 判定 |
|---|---:|---:|---:|---:|---:|---|
| **单页滚动** | **1266** | **16.681 ms** | 16.8 ms | 17 ms | **0** | **`avg<=50ms: PASS`** |
| **Webtoon 长图** | **1202** | **17.527 ms** | 33.3 ms | 33.5 ms | **0** | **`avg<=50ms: PASS`** |

**16.7 ms ≈ 59.9 FPS；17.5 ms ≈ 57.1 FPS。两项都在 60 FPS 附近。**

`fps-single-title-summary.txt` 原文：

```
M2FPS state=STOPPED samples=1266 avg=16.681 p95=16.8 max=17 allmax=17 excluded=0 avg<=50ms:PASS
```

**p95 也远低于 50 ms（16.8 / 33.3），max 同样（17 / 33.5）。**

## 三、我为什么会看错

**我用错了 grep。**

```
Select-String -Path "apps\desktop\frontend\src\**\*.tsx" -Pattern "FpsRecorderPanel"
```

**PowerShell 的 `-Path` 里 `**` 不做递归**——它不是 glob 通配符，`**` 被当成字面目录名。
所以该命令只匹配 `src\**\*.tsx` 这个不存在的路径，**静默返回空**。

**而 `main.tsx` 直接在 `src\` 下，不在任何子目录，因此永远不会被这条命令命中。**

**正确做法**（本轮的写法）：

```
Get-ChildItem "apps\desktop\frontend\src" -Recurse -Include "*.ts","*.tsx" |
  ForEach-Object { Select-String -Path $_.FullName -Pattern "FpsRecorderPanel" }
```

**我后来改用了这条命令，`main.tsx` 立刻出现了。**

## 四、这个错误的性质

**不是"没查到"，是"查错了还确信"。**

`Select-String -Path` 对一个不存在的通配路径**不报错、不警告，只返回空**。
而我把"空结果"读成了"不存在"。

**这与本 Session 反复出现的模式一致**：

| 之前的例子 | 这次的例子 |
|---|---|
| 检查器报错，我只读了"有错"没读"错在哪" | grep 返回空，我把"空"读成"没有" |
| r25 从"未使用 commit 字段"推出"pin 是 blob hash" | 从"grep 没结果"推出"面板没挂载" |

**共同点：把工具输出直接当成事实，而没有问"这个输出是怎么产生的"。**

**而 r27 §5 已经写下了这条规范**：

> 机器输出是按实现规则产生的**观察结果**，不天然等于**事实类别**。

**我知道这条规范，还在同一轮里违反了它。**

## 五、因此 AC4 的真实状态

| 子项 | 实测 | 判据（用户 2026-10-20 裁决）| 判定 |
|---|---|---|---|
| 交互延迟 | **avg 36.0 ms**（p95 62.4）| avg ≤ 50 ms | **MET** |
| **滚动帧率（单页）** | **avg 16.681 ms**，p95 16.8，max 17 | avg ≤ 50 ms，p95/max 须报 | **MET** |
| **滚动帧率（Webtoon）** | **avg 17.527 ms**，p95 33.3，max 33.5 | 同上 | **MET** |
| 缩放平移撕裂 | 未观察 | 人工观察（r30 认可）| **UNOBSERVED** |

**AC4 的四项里三项已 MET。只剩撕裂要人看一眼。**

## 六、我撤回的结论

`ac4-measurability-analysis.md` 的以下结论**全部作废**：

- ~~「FpsRecorderPanel 从未挂载」~~ → **已挂载于 `main.tsx`**
- ~~「FPS 测量不可行」~~ → **已实测，1266 + 1202 样本，avg 16.681 / 17.527**
- ~~「需立 Task 挂载面板」~~ → **不需要，r31 也这样裁定**

**该文件保留原文不改**（它是当时的判断记录），**本文件是它的更正**。
