# V11R-C-1 旧主题 ID 迁移用例表

来源：`doc/plan/V11R_THEME_RETIREMENT_PLAN.md` §2.1（必须全部覆盖，缺一不可）。
实现：`apps/desktop-avalonia/src/NewManga.ThemeEngine/Persistence/LegacyThemeMigration.cs`
入口：`ThemeSettingsStore.Load()` → `ThemeSettingsJson.Read()` → `LegacyThemeMigration.Migrate()`
测试：`apps/desktop-avalonia/tests/NewManga.ThemeEngine.Tests/LegacyThemeMigrationTests.cs`

| # | 输入（旧配置） | 期望主题 | 期望外观 | 期望其它 | migration issue | 测试 |
|---|---|---|---|---|---|---|
| 1 | `themeId = saber-purple` | `newmanga-default` | `Dark` | 布局不变 | `settings.legacy-theme-id` (warning) | `Preset_theme_ids_map_to_the_default_theme_and_the_planned_appearance` |
| 2 | `themeId = saber-light` | `newmanga-default` | `Light` | 布局不变 | 同上 | 同上 |
| 3 | `themeId = midnight` | `newmanga-default` | `Dark` | 布局不变 | 同上 | 同上 |
| 4 | `themeId = sakura` | `newmanga-default` | `Light` | 布局不变 | 同上 | 同上 |
| 5 | `themeId = emerald` | `newmanga-default` | `Dark` | 布局不变 | 同上 | 同上 |
| 6 | `themeId = mono` | `newmanga-default` | `Dark` | 布局不变 | 同上 | 同上 |
| 7 | `themeId = macos-sonoma` | `newmanga-default` | **保留旧变体**（示例 Light） | 布局不变（V1 仅 TopBand） | 同上 | `Macos_layout_packs_keep_the_configured_appearance` |
| 8 | `themeId = macos-launchpad` | `newmanga-default` | **保留旧变体**（示例 Dark） | `Density = Compact`（仅当旧值为 Comfortable） | 同上 | `Macos_launchpad_keeps_the_appearance_and_maps_the_shelf_density_to_compact` / `Macos_launchpad_does_not_override_an_explicit_user_density` |
| 9 | `themeId = macos-split` | `newmanga-default` | **保留旧变体** | 布局不变（用户后续可在 Theme Studio 选，V1 仅 TopBand 生效） | 同上 | `Macos_layout_packs_keep_the_configured_appearance` |
| 10 | `themeId = <未知/损坏 id>`（registry 确认不存在） | `newmanga-default` | `Dark` | 不抛异常、不阻塞启动 | `settings.unknown-theme-id` (warning) | `Unknown_theme_id_recovers_to_the_default_theme_with_dark_appearance` / `Unknown_theme_id_is_recovered_when_a_registry_is_available` |
| 11 | `themeId` 缺失或空字符串 | `newmanga-default` | `System`（首次启动默认；若配置显式给出外观则保留） | 不写 issue | 无 | `Empty_theme_id_lands_on_the_default_theme_without_a_warning` / `Missing_settings_file_returns_shipped_defaults_without_issues` |

附加覆盖：

| 场景 | 期望 | 测试 |
|---|---|---|
| 旧键名 `theme` + 旧外观键 `variant` | 正常读取并迁移（`sakura`+`dark` → `newmanga-default`/`Light`） | `Legacy_theme_key_and_variant_alias_are_read_and_migrated` |
| 旧默认别名 `NewManga.Default` | 归一为 `newmanga-default` + warning | `Legacy_default_alias_is_normalized_to_the_shipped_id` |
| 已安装用户主题 id（如 `ocean`） | 原样保留，不迁移 | `Installed_user_theme_id_is_preserved` |
| 设置文件损坏（非 JSON） | 回退出厂设置，仅 warning，不抛异常 | `Corrupt_settings_file_falls_back_to_defaults_without_throwing` |
| 设置字段类型非法 | 逐字段回退 + `settings.invalid-value` warning | `Invalid_setting_values_fall_back_field_by_field_with_warnings` |
| 设置文件不存在 | 出厂默认，无 issue | `Missing_settings_file_returns_shipped_defaults_without_issues` |
| 设置往返（SaveAsync → Load） | 完全相等 | `Settings_round_trip_through_the_store` |
