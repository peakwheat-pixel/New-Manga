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

## AC3 进展（部分）

- TokenMap.DerivedGlobals 新增 **6 键**：Nm.Focus.Ring.Width(2)/Offset(1)/Color(rgba accent ring)、Nm.Corner.Fluent.Sm/Md/Lg(4/6/8)。
- Tokens.Global.axaml/NmKeys.g.cs/TokenMap.md 经 TokenGen 重新生成；TokenGen -- --check **up to date**。
- 未完成：Nm.Elevation.*（需新增 TokenValueKind.BoxShadows + Writer 分支——本轮尝试后回滚，留待专门实现）、Nm.Material.*（主题层机制）。
- 全量 sln **961/0/57**（无回归）。

## AC3 完成（G-1/G-1c 全部 11 键）

- **BoxShadows 类型**：TokenValueKind.BoxShadows + TokenValues.ParseBoxShadows（x y blur spread color）+ TokenDictionaryWriter 分支。
- **新增 11 键**（全部经 DerivedGlobals + TokenGen）：
  - G-1c：Nm.Focus.Ring.Width(2)/Offset(1)/Color(rgba accent ring)
  - G-1：Nm.Corner.Fluent.Sm/Md/Lg(4/6/8)、Nm.Elevation.1/2/3(BoxShadows)、Nm.Material.Mica.Enabled(true)、Nm.Material.Acrylic.Opacity(0.8)
- Nm.Material.Acrylic.Base/Tint 为主题层键（取值随内置主题包，非全局常量——C-02 口径）。
- TokenGen -- --check **up to date**；ows: 287；全量 sln **961/0/57**。

## AC2 完成

- App/Services/AppearanceCoordinator.cs：读取/校验/变更通知（**不应用主题**——应用归 PREREQ-2）；FrontendId 暴露给壳；Warnings 透出；坏文件回退默认。
- App 项目引用 NewManga.Appearance。
- NewManga.App.Tests/AppearanceCoordinatorTests.cs 4 测试（默认/变更事件/坏文件/不碰资源）。
- 全量 sln **965/0/57**（+4）。

## AC4 完成

- App/Services/WindowsMotionPreferenceSource.cs：SystemParametersInfo(SPI_GETCLIENTAREAANIMATION) P/Invoke；非 Windows/失败 → null；不抛。
- App/Services/MotionResolver.cs：uto→平台源（null/异常降级 full + warning）、ull/educe 显式覆盖；reduce 时 ①时长全 0、②emphasis 禁、③feedback 类别标志保留但 Enabled=false、⑤不启动动效；motion.categories=off ④全禁。
- MotionSettings/MotionResolution（可测的纯函数）。
- NewManga.App.Tests/MotionResolverTests.cs 7 测试（auto 平台/降级两路/显式 full/reduce/off/单类）。
- 全量 sln **972/0/57**（+7）。
