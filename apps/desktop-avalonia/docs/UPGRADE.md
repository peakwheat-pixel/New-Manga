# 升级路径（RELEASE-PACKAGE-1）

- 版本策略：SemVer `MAJOR.MINOR.PATCH`；安装包文件名 `NewManga-<version>-win-x64.zip`；`VERSION.json` 内嵌版本与数据根。
- 数据根：**不变** `%APPDATA%\com.newmanga.desktop`（ADR-0001 安装标识）。
- 首启备份：`install.ps1` 检测已有数据根时，压缩到 `<data>\backups\first-run-<UTC>.zip`；不删除旧数据。
- 覆盖升级：同目录解压覆盖 `app/`，保留 `VERSION.json` 与数据根；失败可回滚到备份压缩包。
- 旧 Tauri 版迁移：`migrate-legacy-dryrun.ps1` 只读扫描旧数据根并输出计划（files/bytes/目标），**dry-run 不写任何文件**；确认后由用户在 S5-C 归档后执行正式迁移（本卡不执行）。
- 模型：不随包（>150MB 风险）；模型目录 `%APPDATA%\com.newmanga.desktop\models`，升级不动。
