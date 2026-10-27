# Rolling Checkpoint — MANUAL-VERIFY-1（真机核验）

Date: 2026-10-27 · HEAD: 待提交

## 已完成（DSH 自动化）

- AC2 DPR2：**PASS（真机）**——Philips 4K @200%，应用窗口 DPI=192，渲染正常锐利。
- AC2b 跨屏动态 DPI：**发现缺陷**——100%→200% 拖动后内容被位图拉伸（需修 WM_DPICHANGED 重渲染）。
- AC3 工作集：空载峰值 143.6MB（App）+37.5+22；webtoon 滚动未测（无书）。
- AC1 Mica：PARTIAL——代码请求 Mica，视觉未呈现，DWM 属性探针无效（spike 同样为 0）。
- AC4 IME、AC5 Esc/H：NOT_RUN（需人工/书库）。

## 未完成

- 真机 Mica 确证（建议加 Avalonia `ActualTransparencyLevel` 诊断日志或用深浅壁纸对比）。
- webtoon 工作集（需要导入一本书）。
- IME 20 字（用户手工）。
- 显示布局恢复（Windows 拒绝脚本摆位；备份在 workspace `display-before.json`）。

## 后续建议（需释放新 Task）

1. `MICA-DIAG-1`：主窗增加 Mica 实际生效诊断（ActualTransparencyLevel/背景采样）并修复不可见问题。
2. `DPI-DYNAMIC-1`：实现 WM_DPICHANGED 后重渲染（跨屏拖动清晰）。
3. 书架接真实书库后复测 webtoon 工作集与 Esc/H。
