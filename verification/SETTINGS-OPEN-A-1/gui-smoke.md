# GUI smoke evidence (SETTINGS-OPEN-A-1)

- Time: 2026-10-22 ~20:47 +08:00
- App: tools/dev/dev-preview.ps1 (Tauri dev window, isolated data root G:\CODEX\New Manga.workspace\dev-preview\data)
- Window: m2rc1-desktop.exe pid 604, title "M2-RC1 resource channel runtime", URL http://localhost:5188/
- Flow: 设置 → 图片修复 → background_complexity 改为 medium → 保存
- UI after save: status "无改动"; 当前持久化值: "均衡 (balanced) · 背景 中 (medium) · dilate 2 / erode 0"
- Persisted row (pipeline_defaults.settings_json, actual SQLite):
{"inpaint": {"background_complexity": "medium", "dilate_radius": 2, "erode_radius": 0, "preferred_quality": "balanced"}}
- Screenshots: see screenshots/01..06
