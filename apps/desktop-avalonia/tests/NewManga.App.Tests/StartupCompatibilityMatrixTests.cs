using System;
using System.Collections.Generic;
using System.IO;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.Views;
using NewManga.App.Views.Fluent;
using NewManga.App.Views.Presentation;
using NewManga.Appearance;
using NewManga.DesignSystem.Theming;
using Xunit;
using DsAppearanceMode = NewManga.DesignSystem.Theming.AppearanceMode;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07 AC4/AC7: startup compatibility matrix — the composition root keeps the frozen fail-safe
/// fallbacks (unknown frontend → Current V2, <c>--shell=legacy</c> wins over everything) and the opt-in
/// stable presentation window.</summary>
public sealed class StartupCompatibilityMatrixTests : IDisposable
{
    private readonly string _root;

    public StartupCompatibilityMatrixTests()
    {
        _root = Path.Combine(Path.GetTempPath(), $"nm-fea07-startup-{Guid.NewGuid():N}");
        Directory.CreateDirectory(_root);
    }

    public void Dispose()
    {
        try
        {
            Directory.Delete(_root, recursive: true);
        }
        catch (IOException)
        {
            // best-effort cleanup
        }
    }

    [AvaloniaFact]
    public void StartupMatrix_KeepsTheFrozenFailSafeFallbacks()
    {
        var application = Application.Current!;
        using var manager = new DesignSystemThemeManager(application);
        Assert.True(manager.Initialize(DsAppearanceMode.Dark), manager.LastError);
        var controller = new FakeHostController(FakeHostController.ReadySnapshot());
        var coordinator = new AppearanceCoordinator(new AppearanceStore(Path.Combine(_root, AppearanceStore.FileName)));
        coordinator.Reload();

        Window Create(params string[] args)
        {
            // W-9/R-006: every startup matrix case must stay inside the test root; never touch %APPDATA%.
            var isolatedArgs = new List<string>(args) { "--theme-home", _root };
            var options = AppOptions.Parse(isolatedArgs.ToArray());
            var themeHome = ThemeHome.Resolve(options);
            var selection = FrontendSelector.Select(options.FrontendId, coordinator.FrontendId);
            return App.CreateShell(options, controller, selection, coordinator, themeHome, manager, application);
        }

        var defaultWindow = Create();
        Assert.IsType<AppShellV2>(defaultWindow.Content);
        defaultWindow.Close();

        var fluent = Create("--frontend=builtin.fluent");
        Assert.IsType<FluentShell>(fluent);
        fluent.Close();

        // Unknown/visual-theme ids are rejected and the Current V2 shell starts (fail-safe).
        var fallback = Create("--frontend=builtin.unknown-x");
        Assert.IsType<AppShellV2>(fallback.Content);
        fallback.Close();

        var visualThemeFallback = Create("--frontend=builtin.fluent-dark");
        Assert.IsType<AppShellV2>(visualThemeFallback.Content);
        visualThemeFallback.Close();

        // --shell=legacy is the one-release operator rollback and wins over the frontend selection.
        var legacy = Create("--shell=legacy");
        Assert.IsType<MainWindow>(legacy);
        legacy.Close();

        var legacyWithFluent = Create("--shell=legacy", "--frontend=builtin.fluent");
        Assert.IsType<MainWindow>(legacyWithFluent);
        legacyWithFluent.Close();

        // FEA-07 opt-in stable window, and legacy still wins over it.
        var presentation = Create("--presentation-host=true");
        Assert.IsType<PresentationWindow>(presentation);
        presentation.Close();

        var presentationLegacy = Create("--presentation-host=true", "--shell=legacy");
        Assert.IsType<MainWindow>(presentationLegacy);
        presentationLegacy.Close();

        Assert.True(FrontendSelector.Select("builtin.unknown-x", coordinator.FrontendId).IsFallback);
    }


    [AvaloniaFact]
    public void CorruptAppearanceDocument_FailsSafeToCurrentV2()
    {
        var application = Application.Current!;
        using var manager = new DesignSystemThemeManager(application);
        Assert.True(manager.Initialize(DsAppearanceMode.Dark), manager.LastError);
        var corruptDirectory = Path.Combine(_root, "corrupt");
        Directory.CreateDirectory(corruptDirectory);
        var corruptPath = Path.Combine(corruptDirectory, AppearanceStore.FileName);
        File.WriteAllText(corruptPath, "{ this is not a json appearance document");
        var coordinator = new AppearanceCoordinator(new AppearanceStore(corruptPath));
        coordinator.Reload();
        Assert.NotEmpty(coordinator.Warnings);

        var options = AppOptions.Parse(new[] { "--theme-home", _root });
        var plan = SafeStartupPlanner.Plan(options, coordinator.Settings, coordinator.Warnings);
        Assert.True(plan.IsFallback);
        Assert.Equal(FrontendSelector.CurrentV2FrontendId, plan.EffectiveFrontendId);

        var controller = new FakeHostController(FakeHostController.ReadySnapshot());
        var window = App.CreateShell(options, controller, plan.Selection, coordinator, ThemeHome.Resolve(options), manager, application);
        Assert.IsType<AppShellV2>(window.Content);
        window.Close();
    }
}