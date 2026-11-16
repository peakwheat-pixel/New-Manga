# READER-OVERLAY-HEADLESS-PNG-1

渲染 HEAD：`a1233003bc10a5facde6d294339f60b6ada0344b`

| 项 | 值 |
|---|---|
| 文件 | `immersive-reader.png` |
| 尺寸 | 1024x768 |
| 字节 | 11883 |
| SHA256 | `BD5435BA3839BE7666E6160431F3547F3108CC86156DAC5CC836091F622E5182` |
| 来源 | `[AvaloniaFact]` headless + `Window.CaptureRenderedFrame()` |
| 入口 | production `MainWindow.TryHandleGlobalKey(Key.F11)` |
| 命令 | `dotnet test --filter FullyQualifiedName~ImmersiveReaderVisualEvidenceTests` |

**这张图是 headless 渲染，不是真实显示器截图。** 它证明 `ReaderWindow` 的内容树能渲染出非空帧，
不证明真实窗口在物理屏幕上的显示效果。签署：NOT_RUN。

## 全量测试回归确认

新增的 `ImmersiveReaderVisualEvidenceTests` 已并入 App 测试项目，**全量跑通**：

```
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj
已通过! - 失败: 0，通过: 955，已跳过: 11，总计: 966，持续时间: 7 m 1 s
```

| 项 | 基线（本会话早前） | 本次 | 差异 |
|---|---|---|---|
| passed | 954 | **955** | **+1**（新增的这一条） |
| failed | 0 | **0** | 0 |
| skipped | 11 | **11** | 0（**未新增 skip**） |
| total | 965 | **966** | +1 |

**⇒ 零回归；未放宽任何既有断言；未新增任何 skip/xfail。**
