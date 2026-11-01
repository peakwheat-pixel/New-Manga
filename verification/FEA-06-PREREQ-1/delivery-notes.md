# FEA-06-PREREQ-1 交付说明（进行中）

日期：2026-11-02；实现：DSH（Codex 通道故障、ZCode 未安装）。

## 已完成（AC1 核心）

- 新建项目 pps/desktop-avalonia/src/NewManga.Appearance（C-03 v6 写者）：
  - AppearanceSettings（C-03 §2.2 逐字段：	heme.frontendId/	heme.visualThemeId/ppearance.mode/ppearance.contrast/ppearance.followSystemAccent/motion.mode（auto/full/reduce）/motion.categories（三类 + off）/corners.scale/material.acrylicStrength/material.micaEnabled/layout.*/schemaVersion=2）；
  - AppearanceJson：宽容读（坏 JSON/未知值回退 + 警告，永不抛）+ canonical 写（schemaVersion 2、LF、末尾换行）+ **旧 educedMotion 迁移**（true→reduce、false→**full** 非 auto）+ 旧 	hemeId→	heme.visualThemeId；
  - AppearanceStore：原子写（temp + replace）+ 旧文档读一次保留（LegacyDocument）；
  - IMotionPreferenceSource + NullMotionPreferenceSource（uto 平台 SPI，失败降级 full）。
- NewManga.Appearance.Tests：12 测试（roundtrip/迁移/坏文件/未知值/off/夹紧/canonical 写/原子写/缺文件/读一次），全绿。
- `NewManga.sln` 已加入两项目。

## 待完成（AC2–AC6）

- AC2：AppearanceCoordinator（App 侧读取/校验/变更通知）+ AppOptions.FrontendId。
- AC3：G-1 令牌（DerivedGlobals + TokenValueKind.BoxShadows + 重生成 + --check + R14 计数）。
- AC4：IMotionPreferenceSource 的 Windows 实现 + 三态测试（判据①–⑤）。
- AC5：uiltin.fluent-dark 主题包。
- AC6：全量回归（当前 961/0/57）。

## 本轮验证

- 全量 sln **961 passed / 0 failed / 57 skipped**（+12 Appearance）；
- 证据：uild.log、sln-test.log、ppearance-tests.log。
