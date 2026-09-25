# M2-UI1 Visual Regression Baseline manifest

baseline_commit: 6a68fdeb92d8a1c7903166a8076d6260bf8fa79a (src tree identical at capture HEAD 5d989bab6c5c8a24a5112303f95c2b8eea356bdc)
capture_date_utc: 2026-09-25
platform: Windows 11 10.0.26200 x64, default (windows) QPA platform, DPI 100%
python: 3.12.3 @ G:/CODEX/New Manga.task-envs/TASK-012-py312 (PySide6 6.11.2)
script: ../../capture_baseline.py (derived from ../../../../T3.2.1/repair-13/probe_ui_states.py)
window: 1280x800 DIP, dark mode (Tokens.mode=dark, F default)

## frames
e19cf1a1d4e18b4e63022d2771831e47ee99a6bec2a17cd3943e0982924f2557 *screenshots/01-bookshelf-empty.png
705e5d23fd83a316966f53abe0c2c4699233d45bdbfc3458e1916343405f29ed *screenshots/02-new-book-dialog.png
0d07c464d46411b9b8c0881d1d8bf984178e4674924f9cc864d5152c06297455 *screenshots/03-bookshelf-detail.png
7fe1541e24a5cb587a8d5cf568175df75deb1f59a3afa262b665151cb867c5f8 *screenshots/04-toolbar-checked.png
5b8b9e7ea603535e601202cf522e605fb5726a0bc6eb5247cef7c9ed5fdc6997 *screenshots/05-chapter-selected.png
5b8b9e7ea603535e601202cf522e605fb5726a0bc6eb5247cef7c9ed5fdc6997 *screenshots/05b-import-picker-opened.png
5b8b9e7ea603535e601202cf522e605fb5726a0bc6eb5247cef7c9ed5fdc6997 *screenshots/06-pages-imported.png
17162ce0e6f76613f415893d49c4755b8f884321de2514d67fda062a1b23a672 *screenshots/07-reader-active.png
ac89634848eabef706e0303d0cb39c3158af6b08914d134d6aba3b99521055ca *screenshots/08-reader-chapter-picker.png
88322bd02f6c8c9f29eb4894f556295371c11244e10c12d57ee0840fd12714ae *screenshots/09-export-window.png
831b191ef3e458cc83205c509ee448e6e176e54f6183d31be662bfa5de75eb08 *screenshots/10-export-after.png
8bb6e4f31d47fd7f50a35d9ecd88efeadd017588ce89d9ffddb45a1e239b4913 *screenshots/11-workbench.png
e44615c36879ca504cf30d818575b058e55bbe613ef203d532643f8d00bc03ee *screenshots/12-settings.png
a4fa38689bf211a530c714ffb66957d48b7c0a1f5728c39a50220d3438372fd1 *screenshots/13-focus-create-book.png

## attempt history
- attempt1: unmodified repair-13 probe -> stale identical frames 05/05b/06, 2 input FAILs (log attempt1-capture.log)
- attempt2: + window show/requestActivate -> still tile-click + focus FAILs (attempt2-capture.log)
- attempt3 (this manifest): + vm.selectPage fallback for tile selection + focus retry -> only focus FAIL remains

## 日志编码注记

- capture*.log / attempt*.log 为脚本 stdout 原样字节（Windows 控制台 cp936 混排 UTF-8），中文行可能呈 mojibake；按原样保留不清洗（证据纪律）。
- 帧 13 与 tile 点击在本机的失败记录在 attempt1/attempt2 日志内，均有更正段。
