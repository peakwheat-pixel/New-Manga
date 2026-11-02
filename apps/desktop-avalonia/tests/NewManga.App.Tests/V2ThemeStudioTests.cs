using System.Text.Json;
using Avalonia;
using Avalonia.Headless.XUnit;
using NewManga.App.ViewModels.V2.ThemeStudio;
using DesignSystemThemeManager = NewManga.DesignSystem.Theming.DesignSystemThemeManager;
using NewManga.ThemeEngine;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-C-2 Theme Studio behaviour tests (THEME_STUDIO_SPEC AC1–AC11 minus pixels):
/// section state machine, dirty/three-exit lifecycle, cancel rollback against the real engine service,
/// live WCAG audit, import blocking, export round-trip, legacy-id migration disclosure, keyboard routing
/// and the responsive grid metric.
///
/// These tests run the <b>real</b> engine chain (registry / settings store / preview engine / service /
/// validator) over a temporary directory; only the Avalonia layer sink is a recording double where the
/// application instance would otherwise be needed.
/// </summary>
public sealed class V2ThemeStudioTests : IDisposable
{
    private readonly string _root = Path.Combine(
        Path.GetTempPath(),
        "nm-theme-studio-tests",
        Guid.NewGuid().ToString("N")[..10]);

    public V2ThemeStudioTests() => Directory.CreateDirectory(_root);

    public void Dispose()
    {
        try
        {
            if (Directory.Exists(_root))
            {
                Directory.Delete(_root, recursive: true);
            }
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
        {
            // best effort: the temp directory is disposable
        }
    }

    // ---------------------------------------------------------------- AC1 state machine

    [AvaloniaFact]
    public void SevenSections_AreInTheFrozenOrder_WithIconsAndSubtitles()
    {
        var service = CreateSandboxService();
        using var viewModel = new ThemeStudioViewModel(service);

        Assert.Equal(7, viewModel.Sections.Count);
        Assert.Equal(
            [
                ThemeStudioSection.Library,
                ThemeStudioSection.Preview,
                ThemeStudioSection.MyThemes,
                ThemeStudioSection.Editor,
                ThemeStudioSection.Appearance,
                ThemeStudioSection.ImportExport,
                ThemeStudioSection.Reset,
            ],
            viewModel.Sections.Select(section => section.Section).ToArray());
        Assert.All(viewModel.Sections, item =>
        {
            Assert.False(string.IsNullOrWhiteSpace(item.Title));
            Assert.False(string.IsNullOrWhiteSpace(item.Subtitle));
            Assert.NotNull(item.Icon);
            Assert.NotNull(item.SelectCommand);
        });

        // Rail selection follows the main area and only one section is selected.
        viewModel.SelectSection(ThemeStudioSection.Editor);
        Assert.Single(viewModel.Sections, item => item.IsSelected);
        Assert.True(viewModel.ShowEditor);
        Assert.Equal("主题编辑", viewModel.SectionTitle);
    }

    [AvaloniaFact]
    public void SectionSwitch_KeepsTheDraft_AndDirtyMarkers()
    {
        var service = CreateSandboxService();
        using var viewModel = new ThemeStudioViewModel(service);
        viewModel.SelectSection(ThemeStudioSection.Library);
        viewModel.Library.Refresh();

        var card = viewModel.Library.Cards.First(card => card.Id == StubThemeStudioService.FixturePackages[0].Descriptor.Id);
        viewModel.PreviewThemeById(card.Id);
        Assert.True(viewModel.HasDraft);
        Assert.Equal("应用修改", viewModel.ApplyButtonLabel);

        viewModel.SelectSection(ThemeStudioSection.Preview);
        Assert.True(viewModel.HasDraft);
        Assert.Equal(ThemeStudioSection.Preview, viewModel.CurrentSection);
        Assert.Contains(viewModel.Sections, item => item.Section == ThemeStudioSection.Preview && item.IsDirty);

        viewModel.SelectSection(ThemeStudioSection.Library);
        Assert.True(viewModel.HasDraft);
        Assert.Equal(ThemeStudioSection.Library, viewModel.CurrentSection);
    }

    [AvaloniaFact]
    public void EscLadder_DialogThenUnsavedThenClose()
    {
        var service = CreateSandboxService();
        using var viewModel = new ThemeStudioViewModel(service);
        var closed = 0;
        viewModel.RequestClose += (_, _) => closed++;

        // Level 1: no draft, no dialog → Esc closes the surface.
        Assert.True(viewModel.HandleEscape());
        Assert.Equal(1, closed);

        // Level 2: dirty draft → Esc opens the three-exit dialog instead of closing.
        viewModel.PreviewThemeById(StubThemeStudioFixtureId(0));
        Assert.True(viewModel.HasDraft);
        Assert.True(viewModel.HandleEscape());
        Assert.True(viewModel.Dialog.IsOpen);
        Assert.Equal(ThemeStudioDialogKind.UnsavedChanges, viewModel.Dialog.Kind);
        Assert.Equal(3, viewModel.Dialog.Actions.Count);
        Assert.Equal(1, closed);

        // Level 3: Esc again closes the dialog (continue editing) and does not close the surface.
        Assert.True(viewModel.HandleEscape());
        Assert.False(viewModel.Dialog.IsOpen);
        Assert.Equal(1, closed);
    }

    [AvaloniaFact]
    public void UnsavedDialog_ApplyAction_CommitsAndCloses()
    {
        var service = CreateSandboxService();
        using var viewModel = new ThemeStudioViewModel(service);
        var closed = 0;
        viewModel.RequestClose += (_, _) => closed++;

        viewModel.PreviewThemeById(StubThemeStudioFixtureId(1));
        viewModel.Close();
        Assert.True(viewModel.Dialog.IsOpen);

        var apply = viewModel.Dialog.Actions[2];
        Assert.Equal("应用并退出", apply.Label);
        apply.Command.Execute(null);
        WaitFor(() => !viewModel.HasDraft, TimeSpan.FromSeconds(5));

        Assert.Equal(StubThemeStudioFixtureId(1), service.Settings.ThemeId);
        Assert.Equal(1, closed);
    }

    // ---------------------------------------------------------------- AC9 preview / cancel

    [AvaloniaFact]
    public void CancelPreview_RollsBackAppliedThemeAndPalette()
    {
        var (service, manager, root) = CreateProductionService();
        manager.RevertPalette();
        using var _ = service;
        try
        {
            var appliedBefore = service.Settings.ThemeId;
            Assert.Equal(ThemeDefaults.DefaultThemeId, appliedBefore);

            var fixture = StubThemeStudioService.FixturePackages[0];
            service.BeginPreview();
            service.PreviewTheme(fixture.Descriptor.Id);
            Assert.True(service.HasDraft);
            Assert.Equal(fixture.Descriptor.Id, manager.AppliedPaletteId);

            service.CancelPreviewAsync().GetAwaiter().GetResult();

            Assert.False(service.HasDraft);
            Assert.Equal(appliedBefore, service.Settings.ThemeId);
            Assert.Equal(ThemeDefaults.DefaultThemeId, manager.AppliedPaletteId);
            Assert.Equal(ThemeDefaults.DefaultThemeId, service.CurrentTheme.Id);
        }
        finally
        {
            manager.RevertPalette();
            manager.Dispose();
            DeleteDirectory(root);
        }
    }

    [AvaloniaFact]
    public void PreviewSession_DoesNotPersistUntilApply()
    {
        var (service, manager, root) = CreateProductionService();
        using var _ = service;
        try
        {
            var settingsPath = Path.Combine(root, "theme-settings.json");
            var before = File.Exists(settingsPath) ? File.ReadAllText(settingsPath) : string.Empty;

            service.BeginPreview();
            service.PreviewTheme(StubThemeStudioFixtureId(2));
            Assert.True(service.HasDraft);
            var during = File.Exists(settingsPath) ? File.ReadAllText(settingsPath) : string.Empty;
            Assert.Equal(before, during);

            var result = service.ApplyAsync().GetAwaiter().GetResult();
            Assert.True(result.Success);
            Assert.True(result.Persisted);
            Assert.Equal(StubThemeStudioFixtureId(2), result.AppliedThemeId);
            Assert.Contains(StubThemeStudioFixtureId(2), File.ReadAllText(settingsPath), StringComparison.Ordinal);

            // A fresh service over the same documents must come back with the applied theme (restart proof).
            var reloaded = new ThemeRegistry(Path.Combine(root, "themes"));
            var store = new ThemeSettingsStore(settingsPath, reloaded);
            Assert.Equal(StubThemeStudioFixtureId(2), store.Load().ThemeId);
        }
        finally
        {
            manager.RevertPalette();
            manager.Dispose();
            DeleteDirectory(root);
        }
    }

    [AvaloniaFact]
    public void EditorDraft_IsScoped_AndDoesNotTouchApplicationPalette()
    {
        var (service, manager, root) = CreateProductionService();
        using var _ = service;
        try
        {
            var appliedPalette = manager.AppliedPaletteId;
            var package = service.AppliedPackage;
            var dark = package.Dark;
            var colors = new Dictionary<string, string>(dark.Colors, StringComparer.Ordinal)
            {
                [NewManga.DesignSystem.NmKeys.Color.Accent.Base] = "#12AB34",
            };
            var edited = package with { Dark = dark with { Colors = colors } };

            service.PreviewDocument(edited);
            Assert.True(service.HasDraft);
            Assert.True(service.IsDraftPackageScoped);

            // The scoped draft palette carries the edit; the application palette is untouched.
            var draftPalette = service.GetDraftPalette();
            Assert.NotNull(draftPalette);
            Assert.NotNull(draftPalette!.Brush(NewManga.DesignSystem.NmKeys.Color.Accent.Base));
            Assert.Equal(appliedPalette, manager.AppliedPaletteId);

            service.CancelPreviewAsync().GetAwaiter().GetResult();
            Assert.False(service.HasDraft);
            Assert.Null(service.GetDraftPalette());
            Assert.Equal(appliedPalette, manager.AppliedPaletteId);
        }
        finally
        {
            manager.RevertPalette();
            manager.Dispose();
            DeleteDirectory(root);
        }
    }

    [AvaloniaFact]
    public void EditorDraft_Apply_PersistsAsUserTheme()
    {
        var (service, manager, root) = CreateProductionService();
        using var _ = service;
        try
        {
            var package = service.AppliedPackage;
            var colors = new Dictionary<string, string>(package.Dark.Colors, StringComparer.Ordinal)
            {
                [NewManga.DesignSystem.NmKeys.Color.Bg.Canvas] = "#101820",
                [NewManga.DesignSystem.NmKeys.Color.Text.Primary] = "#F2F5F8",
            };
            service.PreviewDocument(package with { Dark = package.Dark with { Colors = colors } });

            var result = service.ApplyAsync().GetAwaiter().GetResult();
            Assert.True(result.Success);
            Assert.True(result.Persisted);
            Assert.NotNull(result.AppliedThemeId);
            Assert.StartsWith("custom-", result.AppliedThemeId!, StringComparison.Ordinal);

            var installed = service.FindPackage(result.AppliedThemeId!);
            Assert.NotNull(installed);
            Assert.Equal(ThemeKind.User, installed!.Descriptor.Kind);
            Assert.Equal("#101820", installed.Dark.Colors[NewManga.DesignSystem.NmKeys.Color.Bg.Canvas]);
            Assert.Equal(
                result.AppliedThemeId,
                new ThemeSettingsStore(Path.Combine(root, "theme-settings.json")).Load().ThemeId);
        }
        finally
        {
            manager.RevertPalette();
            manager.Dispose();
            DeleteDirectory(root);
        }
    }

    // ---------------------------------------------------------------- AC5 contrast audit

    [AvaloniaFact]
    public void ContrastAudit_UsesTheEngineFormula_AndFlagsFailures()
    {
        var service = CreateSandboxService();
        using var _ = service;
        var package = service.AppliedPackage;
        var report = service.Audit(package, PaletteVariant.Dark);

        var primary = report.Rows.Single(row =>
            row.ForegroundKey == NewManga.DesignSystem.NmKeys.Color.Text.Primary &&
            row.BackgroundKey == NewManga.DesignSystem.NmKeys.Color.Bg.Panel);
        var expected = ThemeContrast.Ratio(
            package.Dark.Colors[NewManga.DesignSystem.NmKeys.Color.Text.Primary],
            package.Dark.Colors[NewManga.DesignSystem.NmKeys.Color.Bg.Panel]);
        Assert.Equal(expected, primary.Ratio, 6);
        Assert.Equal(7.0, primary.Floor);
        Assert.True(primary.Pass);

        // A tampered theme (text = background) must fail the audit and be rejected by the engine validator.
        var brokenColors = new Dictionary<string, string>(package.Dark.Colors, StringComparer.Ordinal)
        {
            [NewManga.DesignSystem.NmKeys.Color.Text.Primary] = package.Dark.Colors[NewManga.DesignSystem.NmKeys.Color.Bg.Panel],
        };
        var broken = package with { Dark = package.Dark with { Colors = brokenColors } };
        var brokenReport = service.Audit(broken, PaletteVariant.Dark);
        Assert.False(brokenReport.IsPassing);
        Assert.Contains(brokenReport.Failures, row => row.ForegroundKey == NewManga.DesignSystem.NmKeys.Color.Text.Primary);

        var validation = service.ValidatePackage(broken);
        Assert.False(validation.IsValid);
        Assert.Contains(validation.Issues, issue => issue.Code.StartsWith("contrast.", StringComparison.Ordinal));
    }

    // ---------------------------------------------------------------- AC7 import / export

    [AvaloniaFact]
    public void InvalidPackage_IsBlocked_WithPerItemIssues_AndCatalogUnchanged()
    {
        var service = CreateSandboxService();
        using var _ = service;
        var before = service.Themes.Select(package => package.Descriptor.Id).ToArray();

        var illegal = StubThemeStudioService.CreateIllegalFixture();
        var report = service.ValidateJson(ThemePackageJson.Write(illegal), "illegal.nmtheme");

        Assert.False(report.IsValid);
        Assert.True(report.ErrorCount > 0);
        Assert.All(report.Errors, issue =>
        {
            Assert.False(string.IsNullOrWhiteSpace(issue.Message));
            Assert.False(string.IsNullOrWhiteSpace(issue.SuggestionLabel));
            Assert.False(string.IsNullOrWhiteSpace(issue.PathLabel));
        });

        var result = service.ImportAsync(ThemePackageJson.Write(illegal), "illegal.nmtheme").GetAwaiter().GetResult();
        Assert.False(result.Success);
        Assert.Contains("阻止", result.Message, StringComparison.Ordinal);
        Assert.Equal(before, service.Themes.Select(package => package.Descriptor.Id).ToArray());
    }

    [AvaloniaFact]
    public void ValidPackage_Imports_AndDuplicateIdRequiresOverwrite()
    {
        var service = CreateSandboxService(seedFixtures: false);
        using var _ = service;

        var baseline = BuiltInThemes.Default;
        var imported = baseline with
        {
            Descriptor = baseline.Descriptor with
            {
                Id = "user-imported-one",
                Name = "导入主题",
                Kind = ThemeKind.User,
                Author = "QA",
            },
        };
        var json = ThemePackageJson.Write(imported);

        var report = service.ValidateJson(json, "user-imported-one.nmtheme");
        Assert.True(report.IsValid, string.Join(" | ", report.Issues.Select(issue => issue.Message)));

        var first = service.ImportAsync(json, "user-imported-one.nmtheme").GetAwaiter().GetResult();
        Assert.True(first.Success);
        Assert.NotNull(service.FindPackage("user-imported-one"));

        var duplicate = service.ImportAsync(json, "user-imported-one.nmtheme").GetAwaiter().GetResult();
        Assert.False(duplicate.Success);
        Assert.Contains(duplicate.Issues, issue => issue.Code == ThemeIssueCodes.RegistryDuplicateId);

        var overwritten = service.ImportAsync(json, "user-imported-one.nmtheme", overwrite: true).GetAwaiter().GetResult();
        Assert.True(overwritten.Success);
    }

    [AvaloniaFact]
    public void ExportThenImport_RoundTripsToTheSameDocument()
    {
        var service = CreateSandboxService();
        using var _ = service;
        var fixtureId = StubThemeStudioFixtureId(0);

        var exported = service.ExportAsync(fixtureId).GetAwaiter().GetResult();
        Assert.NotNull(exported);
        var read = ThemePackageJson.Read(exported!);
        Assert.NotNull(read.Package);
        Assert.Equal(ThemePackageJson.Write(read.Package!), exported);

        var report = service.ValidateJson(exported!, fixtureId + ".nmtheme");
        Assert.True(report.IsValid, string.Join(" | ", report.Issues.Select(issue => issue.Message)));

        service.DeleteAsync(fixtureId).GetAwaiter().GetResult();
        Assert.Null(service.FindPackage(fixtureId));
        var reimported = service.ImportAsync(exported!, fixtureId + ".nmtheme").GetAwaiter().GetResult();
        Assert.True(reimported.Success);
        var roundTripped = service.ExportAsync(fixtureId).GetAwaiter().GetResult();
        Assert.Equal(exported, roundTripped);
    }

    // ---------------------------------------------------------------- AC10 migration

    [AvaloniaTheory]
    [InlineData("saber-purple")]
    [InlineData("saber-light")]
    [InlineData("midnight")]
    [InlineData("sakura")]
    [InlineData("emerald")]
    [InlineData("mono")]
    [InlineData("macos-sonoma")]
    [InlineData("macos-launchpad")]
    [InlineData("macos-split")]
    public void LegacyThemeIds_MigrateToDefault_WithVisibleNotice(string legacyId)
    {
        var root = Path.Combine(_root, "legacy-" + legacyId);
        Directory.CreateDirectory(root);
        var settingsPath = Path.Combine(root, "theme-settings.json");
        var registry = new ThemeRegistry(Path.Combine(root, "themes"));
        var settings = new ThemeSettings(
            legacyId,
            AppearanceMode.Dark,
            ContrastMode.Standard,
            LayoutProfile.Default,
            ReducedMotion: false,
            FollowSystemAccent: false);
        File.WriteAllText(settingsPath, ThemeSettingsJson.Write(settings));

        var store = new ThemeSettingsStore(settingsPath, registry);
        var service = new ThemeService(registry, store, new NullThemeLayerSink());
        using var studio = new ThemeEngineThemeStudioService(
            service,
            registry,
            store,
            new ThemeStudioFavoritesStore(Path.Combine(root, "favorites.json")),
            palettes: null,
            isSandbox: true,
            persistsToDisk: true);
        studio.InitializeAsync().GetAwaiter().GetResult();

        Assert.Equal(ThemeDefaults.DefaultThemeId, studio.Settings.ThemeId);
        Assert.Equal(ThemeDefaults.DefaultThemeId, studio.CurrentTheme.Id);
        Assert.Contains(studio.MigrationNotices, notice => notice.LegacyId == legacyId);
        Assert.Contains(studio.MigrationNotices, notice => notice.Message.Contains(legacyId, StringComparison.Ordinal));
    }

    [AvaloniaTheory]
    [InlineData("")]
    [InlineData("completely-unknown-theme")]
    public void UnknownOrEmptyThemeId_RecoversToDefault_WithoutCrashing(string themeId)
    {
        var root = Path.Combine(_root, "unknown-" + (themeId.Length == 0 ? "empty" : themeId));
        Directory.CreateDirectory(root);
        var settingsPath = Path.Combine(root, "theme-settings.json");
        var registry = new ThemeRegistry(Path.Combine(root, "themes"));
        File.WriteAllText(
            settingsPath,
            ThemeSettingsJson.Write(new ThemeSettings(
                themeId,
                AppearanceMode.Dark,
                ContrastMode.Standard,
                LayoutProfile.Default,
                ReducedMotion: false,
                FollowSystemAccent: false)));

        var store = new ThemeSettingsStore(settingsPath, registry);
        var service = new ThemeService(registry, store, new NullThemeLayerSink());
        using var studio = new ThemeEngineThemeStudioService(
            service,
            registry,
            store,
            new ThemeStudioFavoritesStore(Path.Combine(root, "favorites.json")),
            palettes: null,
            isSandbox: true,
            persistsToDisk: true);

        var exception = Record.Exception(() => studio.InitializeAsync().GetAwaiter().GetResult());
        Assert.Null(exception);
        Assert.Equal(ThemeDefaults.DefaultThemeId, studio.CurrentTheme.Id);
        Assert.NotNull(studio.AppliedPackage);
    }

    // ---------------------------------------------------------------- AC11 keyboard + accessibility

    [AvaloniaFact]
    public void KeyboardRouting_EscCtrlEnterCtrlFAndArrows()
    {
        var service = CreateSandboxService();
        using var viewModel = new ThemeStudioViewModel(service);
        var focusRequested = 0;
        viewModel.FocusSearchRequested += (_, _) => focusRequested++;

        viewModel.SelectSection(ThemeStudioSection.Library);
        Assert.True(viewModel.HandleKey(Avalonia.Input.Key.Down, Avalonia.Input.KeyModifiers.None));
        Assert.Equal(ThemeStudioSection.Preview, viewModel.CurrentSection);
        Assert.True(viewModel.HandleKey(Avalonia.Input.Key.Up, Avalonia.Input.KeyModifiers.None));
        Assert.Equal(ThemeStudioSection.Library, viewModel.CurrentSection);

        Assert.True(viewModel.HandleKey(Avalonia.Input.Key.F, Avalonia.Input.KeyModifiers.Control));
        Assert.Equal(1, focusRequested);

        viewModel.PreviewThemeById(StubThemeStudioFixtureId(0));
        Assert.True(viewModel.HandleKey(Avalonia.Input.Key.Enter, Avalonia.Input.KeyModifiers.Control));
        WaitFor(() => !viewModel.HasDraft, TimeSpan.FromSeconds(5));
        Assert.Equal(StubThemeStudioFixtureId(0), service.Settings.ThemeId);
    }

    [AvaloniaFact]
    public void StatusStates_AreTextEncoded_NotColourOnly()
    {
        var service = CreateSandboxService();
        using var viewModel = new ThemeStudioViewModel(service);
        var report = service.Audit(service.AppliedPackage, PaletteVariant.Dark);

        Assert.All(report.Rows, row =>
        {
            Assert.Equal(row.Pass ? "通过" : "未通过", row.StateLabel);
            Assert.Contains(":1", row.RatioLabel, StringComparison.Ordinal);
        });

        var issues = service.ValidateJson("{ \"schema\": \"newmanga.theme/1\" }", "broken");
        Assert.All(issues.Issues, issue => Assert.False(string.IsNullOrWhiteSpace(issue.LevelLabel)));

        Assert.Equal("明暗均支持", viewModel.CurrentThemeSupport);
        Assert.Contains(viewModel.Sections, item => item.AccessibleLabel.Contains("主题库", StringComparison.Ordinal));
    }

    // ---------------------------------------------------------------- AC2 library / responsive grid

    [AvaloniaFact]
    public void LibraryBreakpoints_AreFourThreeTwoColumns()
    {
        Assert.Equal(4, ThemeStudioLibraryViewModel.ColumnsForWidth(1600));
        Assert.Equal(4, ThemeStudioLibraryViewModel.ColumnsForWidth(1920));
        Assert.Equal(3, ThemeStudioLibraryViewModel.ColumnsForWidth(1280));
        Assert.Equal(3, ThemeStudioLibraryViewModel.ColumnsForWidth(1599));
        Assert.Equal(2, ThemeStudioLibraryViewModel.ColumnsForWidth(1024));
        Assert.Equal(2, ThemeStudioLibraryViewModel.ColumnsForWidth(800));
    }

    [AvaloniaFact]
    public void LibraryFilters_SearchCategoryAndAppearance()
    {
        var service = CreateSandboxService();
        using var viewModel = new ThemeStudioViewModel(service);
        viewModel.SelectSection(ThemeStudioSection.Library);
        var library = viewModel.Library;

        var all = library.Cards.Count;
        Assert.True(all >= 2, "sandbox seeds one built-in plus fixtures");

        library.SearchText = "STUB";
        Assert.All(library.Cards, card => Assert.Contains("stub", card.Name, StringComparison.OrdinalIgnoreCase));

        library.SearchText = "no-such-theme-name";
        Assert.True(library.IsEmpty);
        Assert.Contains("没有匹配", library.EmptyTitle, StringComparison.Ordinal);

        library.ClearFiltersCommand.Execute(null);
        Assert.Equal(all, library.Cards.Count);

        library.SelectCategory("builtin");
        Assert.All(library.Cards, card => Assert.True(card.IsBuiltIn));

        library.SelectCategory("favorite");
        Assert.Empty(library.Cards);

        library.SelectCategory("all");
        library.SelectAppearance("dark");
        Assert.All(library.Cards, card => Assert.True(card.Package.Descriptor.SupportsDark));

        library.SetViewportWidth(1280);
        Assert.Equal(3, library.ColumnCount);
        Assert.All(library.Cards, card => Assert.True(card.Width > ThemeStudioLibraryViewModel.MinCardWidth));
        library.SetViewportWidth(1024);
        Assert.Equal(2, library.ColumnCount);
    }

    // ---------------------------------------------------------------- AC3 favourites / AC4 my themes

    [AvaloniaFact]
    public void FavoritesAndDelete_PersistAndProtectBuiltins()
    {
        var service = CreateSandboxService();
        using var _ = service;
        service.ToggleFavoriteAsync(ThemeDefaults.DefaultThemeId).GetAwaiter().GetResult();
        Assert.True(service.IsFavorite(ThemeDefaults.DefaultThemeId));

        var favorited = new ThemeStudioFavoritesStore(Path.Combine(_root, "fav.json"));
        favorited.Save(new HashSet<string>(StringComparer.Ordinal) { ThemeDefaults.DefaultThemeId });
        Assert.Contains(ThemeDefaults.DefaultThemeId, favorited.Load());

        var builtInDelete = service.DeleteAsync(ThemeDefaults.DefaultThemeId).GetAwaiter().GetResult();
        Assert.False(builtInDelete.Success);
        Assert.NotNull(service.FindPackage(ThemeDefaults.DefaultThemeId));

        var fixtureId = StubThemeStudioFixtureId(0);
        var delete = service.DeleteAsync(fixtureId).GetAwaiter().GetResult();
        Assert.True(delete.Success);
        Assert.Null(service.FindPackage(fixtureId));
    }

    // ---------------------------------------------------------------- AC8 reset

    [AvaloniaFact]
    public void ResetToDefault_RestoresSettings_AndKeepsUserThemeFilesUnlessAsked()
    {
        var (service, manager, root) = CreateProductionService();
        using var _ = service;
        try
        {
            var fixtureId = StubThemeStudioFixtureId(1);
            service.BeginPreview();
            service.PreviewTheme(fixtureId);
            service.ApplyAsync().GetAwaiter().GetResult();
            service.SetAppearanceAsync(AppearanceMode.Light).GetAwaiter().GetResult();
            service.SetContrastAsync(ContrastMode.High).GetAwaiter().GetResult();
            Assert.Equal(fixtureId, service.Settings.ThemeId);

            var reset = service.ResetToDefaultAsync(clearUserThemes: false).GetAwaiter().GetResult();
            Assert.True(reset.Success);
            Assert.Equal(ThemeDefaults.DefaultThemeId, service.Settings.ThemeId);
            Assert.Equal(AppearanceMode.System, service.Settings.Appearance);
            Assert.Equal(ContrastMode.Standard, service.Settings.Contrast);
            Assert.Equal(Density.Comfortable, service.Settings.Layout.Density);
            Assert.NotNull(service.FindPackage(fixtureId));

            var settingsPath = Path.Combine(root, "theme-settings.json");
            Assert.Equal(ThemeDefaults.DefaultThemeId, new ThemeSettingsStore(settingsPath).Load().ThemeId);
        }
        finally
        {
            manager.RevertPalette();
            manager.Dispose();
            DeleteDirectory(root);
        }
    }

    [AvaloniaFact]
    public void ResetWithClearUserThemes_DeletesUserThemeFiles()
    {
        var (service, manager, root) = CreateProductionService();
        using var _ = service;
        try
        {
            var fixtureId = StubThemeStudioFixtureId(0);
            var fixtureFile = Path.Combine(root, "themes", fixtureId + ".nmtheme");
            Assert.True(File.Exists(fixtureFile));

            var reset = service.ResetToDefaultAsync(clearUserThemes: true).GetAwaiter().GetResult();
            Assert.True(reset.Success);
            Assert.Contains("清除", reset.Message, StringComparison.Ordinal);
            Assert.False(File.Exists(fixtureFile));
            Assert.Null(service.FindPackage(fixtureId));
            Assert.NotNull(service.FindPackage(ThemeDefaults.DefaultThemeId));
        }
        finally
        {
            manager.RevertPalette();
            manager.Dispose();
            DeleteDirectory(root);
        }
    }

    // ---------------------------------------------------------------- AC3 preview + AC5 editor structure

    [AvaloniaFact]
    public void PreviewSwitches_ChangeModeAppearanceDensityAndZoom_WithScopedPalette()
    {
        var service = CreateSandboxService();
        using var viewModel = new ThemeStudioViewModel(service);
        viewModel.SelectSection(ThemeStudioSection.Preview);
        var preview = viewModel.Preview;

        Assert.Equal(3, preview.ModeOptions.Count);
        Assert.Equal(3, preview.AppearanceOptions.Count);
        Assert.Equal(3, preview.DensityOptions.Count);
        Assert.Equal(3, preview.ZoomOptions.Count);
        Assert.True(preview.IsShelf);

        preview.SelectMode(ThemeStudioPreviewMode.Workbench);
        Assert.True(preview.IsWorkbench);
        preview.SelectMode(ThemeStudioPreviewMode.Reader);
        Assert.True(preview.IsReader);
        Assert.Equal("阅读器", preview.ModeLabel);

        preview.SelectAppearance(AppearanceMode.Light);
        Assert.Equal(PaletteVariant.Light, preview.Palette?.Variant);
        preview.SelectAppearance(AppearanceMode.Dark);
        Assert.Equal(PaletteVariant.Dark, preview.Palette?.Variant);

        preview.SelectDensity(Density.Compact);
        Assert.Equal(Density.Compact, preview.Density);
        Assert.Equal(1, preview.DensityOptions.Count(option => option.IsSelected));

        preview.SelectZoom(0.5);
        Assert.Equal(0.5, preview.Zoom);
        Assert.Equal("50%", preview.ZoomLabel);

        // The preview palette is scoped: the application settings are untouched by these switches.
        Assert.Equal(AppearanceMode.System, service.Settings.Appearance);
        Assert.Equal(Density.Comfortable, service.Settings.Layout.Density);
        Assert.NotNull(preview.SampleBooks);
        Assert.NotEmpty(preview.SampleRegions);
    }

    [AvaloniaFact]
    public void Editor_HasSixGroupsWithThirtyFiveSemanticColours_AndLiveRatios()
    {
        var service = CreateSandboxService();
        using var viewModel = new ThemeStudioViewModel(service);
        viewModel.SelectSection(ThemeStudioSection.Editor);
        var editor = viewModel.Editor;

        Assert.Equal(6, editor.ColorGroups.Count);
        Assert.Equal(35, editor.ColorGroups.Sum(group => group.Rows.Count));
        Assert.Equal(6, editor.ColorGroups[0].Rows.Count); // background ladder
        Assert.Equal(4, editor.ColorGroups[1].Rows.Count); // lines
        Assert.Equal(5, editor.ColorGroups[2].Rows.Count); // text
        Assert.Equal(6, editor.ColorGroups[3].Rows.Count); // accent
        Assert.Equal(7, editor.ColorGroups[4].Rows.Count); // status
        Assert.Equal(7, editor.ColorGroups[5].Rows.Count); // status muted

        // Typography / corners / material / elevation / motion groups are all reachable.
        Assert.Equal(2, editor.VariantOptions.Count);
        Assert.Equal(2, editor.MaterialOptions.Count);
        Assert.Equal(2, editor.ElevationOptions.Count);
        Assert.Equal(3, editor.MotionOptions.Count);
        Assert.Equal(3, editor.LineHeightOptions.Count);
        Assert.NotNull(editor.FontFamilies);
        Assert.NotEmpty(editor.FontFamilies);
        Assert.NotEmpty(editor.AuditRows);
        Assert.All(editor.AuditRows, row => Assert.Contains(":1", row.RatioLabel, StringComparison.Ordinal));

        // A live colour edit lands in the draft and recomposes the scoped palette without touching app state.
        var row = editor.ColorGroups[2].Rows[0];
        row.HexValue = "#FFFFFF";
        Assert.True(viewModel.HasDraft);
        Assert.Equal(
            "#FFFFFF",
            service.DraftPackage!.Dark.Colors[NewManga.DesignSystem.NmKeys.Color.Text.Primary]);
        Assert.Equal(ThemeDefaults.DefaultThemeId, service.CurrentTheme.Id);
    }

    [AvaloniaFact]
    public void DuplicateTheme_CreatesIndependentUserCopy()
    {
        var service = CreateSandboxService();
        using var _ = service;
        var duplicate = service.DuplicateAsync(ThemeDefaults.DefaultThemeId, "我的副本").GetAwaiter().GetResult();
        Assert.True(duplicate.Success, duplicate.Message);

        var copies = service.Themes.Where(package => package.Descriptor.Name == "我的副本").ToArray();
        Assert.Single(copies);
        Assert.Equal(ThemeKind.User, copies[0].Descriptor.Kind);
        Assert.Equal(service.AppliedPackage.Dark.Colors, copies[0].Dark.Colors);
        Assert.StartsWith("custom-", copies[0].Descriptor.Id, StringComparison.Ordinal);
    }

    // ---------------------------------------------------------------- AC6 appearance

    [AvaloniaFact]
    public void AppearanceSettings_ApplyImmediately_AndPersist()
    {
        var (service, manager, root) = CreateProductionService();
        var application = Application.Current ?? throw new InvalidOperationException("headless Avalonia application is required");
        using var _ = service;
        try
        {
            service.InitializeAsync().GetAwaiter().GetResult();
            var package = service.AppliedPackage;
            service.SetAppearanceAsync(AppearanceMode.Light).GetAwaiter().GetResult();
            Assert.Equal(AppearanceMode.Light, service.Settings.Appearance);
            Assert.Equal(ThemeDefaults.DefaultThemeId, manager.AppliedPaletteId);
            Assert.Equal(
                Avalonia.Media.Color.Parse(package.Light.Colors[NewManga.DesignSystem.NmKeys.Color.Bg.Canvas]),
                CanvasColor(application));

            service.SetAppearanceAsync(AppearanceMode.Dark).GetAwaiter().GetResult();
            Assert.Equal(ThemeDefaults.DefaultThemeId, manager.AppliedPaletteId);
            Assert.Equal(
                Avalonia.Media.Color.Parse(package.Dark.Colors[NewManga.DesignSystem.NmKeys.Color.Bg.Canvas]),
                CanvasColor(application));

            service.SetContrastAsync(ContrastMode.High).GetAwaiter().GetResult();
            Assert.Equal(ContrastMode.High, service.Settings.Contrast);

            service.SetReducedMotionAsync(true).GetAwaiter().GetResult();
            Assert.True(service.Settings.ReducedMotion);

            service.SetDensityAsync(Density.Compact).GetAwaiter().GetResult();
            Assert.Equal(Density.Compact, service.Settings.Layout.Density);

            var persisted = new ThemeSettingsStore(Path.Combine(root, "theme-settings.json")).Load();
            Assert.Equal(AppearanceMode.Dark, persisted.Appearance);
            Assert.Equal(ContrastMode.High, persisted.Contrast);
            Assert.True(persisted.ReducedMotion);
            Assert.Equal(Density.Compact, persisted.Layout.Density);
        }
        finally
        {
            manager.RevertPalette();
            manager.Dispose();
            DeleteDirectory(root);
        }
    }

    // ---------------------------------------------------------------- helpers

    private static string StubThemeStudioFixtureId(int index) =>
        StubThemeStudioService.FixturePackages[index].Descriptor.Id;

    private ThemeEngineThemeStudioService CreateSandboxService(bool seedFixtures = true)
    {
        var service = StubThemeStudioService.Create(_root, seedFixtures, persistsToDisk: true);
        service.InitializeAsync().GetAwaiter().GetResult();
        return service;
    }

    private (ThemeEngineThemeStudioService Service, DesignSystemThemeManager Manager, string Root) CreateProductionService()
    {
        var root = Path.Combine(_root, "production-" + Guid.NewGuid().ToString("N")[..6]);
        var themeDirectory = Path.Combine(root, "themes");
        Directory.CreateDirectory(themeDirectory);
        foreach (var fixture in StubThemeStudioService.FixturePackages)
        {
            File.WriteAllText(
                Path.Combine(themeDirectory, fixture.Descriptor.Id + ThemeDefaults.ThemeFileExtension),
                ThemePackageJson.Write(fixture));
        }

        var application = Application.Current ?? throw new InvalidOperationException("headless Avalonia application is required");
        var manager = new DesignSystemThemeManager(application);
        manager.Initialize();
        var service = ThemeEngineThemeStudioService.CreateProduction(
            application,
            manager,
            themeDirectory,
            Path.Combine(root, "theme-settings.json"),
            Path.Combine(root, "favorites.json"));
        service.InitializeAsync().GetAwaiter().GetResult();
        return (service, manager, root);
    }

    private static Avalonia.Media.Color CanvasColor(Avalonia.Application application)
    {
        if (application.TryGetResource(
                NewManga.DesignSystem.NmKeys.Color.Bg.Canvas,
                Avalonia.Styling.ThemeVariant.Default,
                out var value) && value is Avalonia.Media.ISolidColorBrush brush)
        {
            return brush.Color;
        }

        Assert.Fail("Nm.Color.Bg.Canvas was not resolvable from the application resources");
        return default;
    }

    private static void WaitFor(Func<bool> condition, TimeSpan timeout)
    {
        var deadline = DateTime.UtcNow + timeout;
        while (DateTime.UtcNow < deadline)
        {
            if (condition())
            {
                return;
            }

            Avalonia.Threading.Dispatcher.UIThread.RunJobs();
            Thread.Sleep(10);
        }

        Assert.True(condition(), "condition was not met within " + timeout);
    }

    private static void DeleteDirectory(string path)
    {
        try
        {
            if (Directory.Exists(path))
            {
                Directory.Delete(path, recursive: true);
            }
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
        {
            // best effort
        }
    }
}
