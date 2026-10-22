# GUI smoke evidence (SETTINGS-OPEN-A-1)

- Time: 2026-10-22 ~20:47 +08:00
- App: tools/dev/dev-preview.ps1 (Tauri dev window, isolated data root G:\CODEX\New Manga.workspace\dev-preview\data)
- Window: m2rc1-desktop.exe pid 604, title "M2-RC1 resource channel runtime", URL http://localhost:5188/
- Flow: 设置 → 图片修复 → background_complexity 改为 medium → 保存
- UI after save: status "无改动"; 当前持久化值: "均衡 (balanced) · 背景 中 (medium) · dilate 2 / erode 0"
- Persisted row (pipeline_defaults.settings_json, actual SQLite):
{"inpaint": {"background_complexity": "medium", "dilate_radius": 2, "erode_radius": 0, "preferred_quality": "balanced"}}
- Screenshots: see screenshots/01..06

## Restart re-read check (2026-10-22 ~21:05 +08:00)

- Closed the app (Alt+F4), relaunched `tools/dev/dev-preview.ps1` against the same isolated data root, opened 设置 → 图片修复.
- Panel loaded from SQLite: 首选质量 "均衡 (balanced)", 背景复杂度 "中 (medium)", dilate 2 / erode 0; status "无改动"; 当前持久化值 line reads:
  "均衡 (balanced) · 背景 中 (medium) · dilate 2 / erode 0"
- Screenshot: screenshots/07-restart-persisted.png

## Per-partition save + restart re-read (2026-10-22 ~21:25–21:31 +08:00; r2 build)

- OCR: 设置 → OCR → `ocr.script` 日语→韩语 → 保存. UI: status "无改动"; 当前持久化值 "韩语 (korean) · 横排 (horizontal)". Screenshot: screenshots/08-ocr-saved.png.
- 排版样式: 设置 → 排版样式 → 关闭 `stroke_enabled` → 保存. UI: status "无改动"; 当前持久化值 "文字 #000000 · 描边关闭 · 行距 1 · 左对齐 (left) · 自动 (auto) · 字号自动 · 偏移 0". Screenshots: screenshots/09-typeset-saved.png, 10-typeset-panel-r2.png (panel has no fill_color control; text_align hint says left/center; auto_font_size hint says manual_font_size required when off).
- 翻译参数面板 (translate.context_pages / context_token_budget) was opened and is editable; numeric-field driving in this environment could not be committed reliably, so no GUI save was attempted for that section — the write path is covered by pytest and the same section client used by the other panels. Screenshot: screenshots/03-translation-params-panel.png.
- Closed the app, relaunched against the same data root, re-opened OCR and 排版样式: both panels re-read the persisted values (OCR "韩语 (korean) · 横排 (horizontal)"; typeset "文字 #000000 · 描边关闭 · 行距 1 · 左对齐 (left) · 自动 (auto) · 字号自动 · 偏移 0"). Screenshot 09 is the same persisted-state view.
- Actual SQLite after the pass (`pipeline_defaults.settings_json`):

```json
{"inpaint": {"background_complexity": "medium", "dilate_radius": 2, "erode_radius": 0, "preferred_quality": "balanced"}, "ocr": {"direction": "horizontal", "script": "korean"}, "typeset": {"auto_font_size": true, "font_size_offset": 0, "line_spacing": 1.0, "manual_font_size": null, "stroke_color": "#ffffff", "stroke_enabled": false, "stroke_width": 3.0, "text_align": "left", "text_color": "#000000", "text_direction": "auto"}}
```

- The typeset object has exactly the 10 batch-A keys — no `fill_color` (B2), `text_align=left` (M2 domain), auto on + manual null (M1 legal combination).
- typeset rendering effect (merged defaults → RenderOp) is covered by `tests/rendering/test_typeset_defaults_merge.py`; no E2E page-render smoke was attempted in this empty-library environment.

## Notes

- The dev preview uses the isolated data root (never user library data); the app was closed after the checks.
- The app window title "M2-RC1 resource channel runtime" is the existing dev-preview title, unrelated to settings.
