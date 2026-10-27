# Handoff — MICA-FIX-1

- 完成：Mica 可见化（透明根/半透明标题栏）+ 启动材质诊断日志（`%APPDATA%\com.newmanga.desktop\logs\window-material.log`）。
- 真机证据：`verification/MICA-FIX-1/mica/titlebar-solid.png` / `titlebar-pattern.png` / `two-wallpapers.json`；取样色 #FFFFFF→#F0EBF7。
- 诊断：`actual=Mica`（requested=Mica,Blur,None），确认非 None 回退。
- 回退：Win10/不支持环境仍用 `MicaFallback` 不透明（单测覆盖；真机 Win10 NOT_RUN）。
- 回归：test.ps1 102/102、vitest 60/567、pytest 3F/2739P/9S。
- 集成：93aaaeb8c（DSH）。
- 遗留：Win10 真机验证（环境限制）；DPI-DYNAMIC-1 另行处理。
