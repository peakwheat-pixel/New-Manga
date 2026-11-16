# READER-OVERLAY-HEADLESS-PNG-1

渲染 HEAD：`96c54844401f7f73cb7d60fb796f5b6994cf4c09`

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
