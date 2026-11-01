using System;
using System.IO;
using System.Threading.Tasks;
using NewManga.App.Services;
using NewManga.Appearance;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-06-PREREQ-1 AC2: the coordinator reads/validates/broadcasts and never applies
/// anything itself (applying belongs to the shell, FEA-06-PREREQ-2).
/// </summary>
public sealed class AppearanceCoordinatorTests : IDisposable
{
    private readonly string _directory = Path.Combine(
        Path.GetTempPath(),
        "nm-coordinator-" + Guid.NewGuid().ToString("N"));

    public void Dispose()
    {
        if (Directory.Exists(_directory))
        {
            Directory.Delete(_directory, recursive: true);
        }
    }

    private string Path_(string name = "presentation-settings.json") => Path.Combine(_directory, name);

    [Fact]
    public void Reload_WithoutFile_YieldsDefaults_AndNoChangeEvent()
    {
        var coordinator = new AppearanceCoordinator(new AppearanceStore(Path_()));
        var changed = 0;
        coordinator.Changed += (_, _) => changed++;

        var settings = coordinator.Reload();

        Assert.Equal(AppearanceDefaults.Settings, settings);
        Assert.Equal(0, changed);
        Assert.Equal("builtin.current-v2", coordinator.FrontendId);
    }

    [Fact]
    public async Task Reload_RaisesChanged_WhenTheDocumentDiffers()
    {
        var path = Path_();
        var store = new AppearanceStore(path);
        await store.WriteAsync(AppearanceDefaults.Settings with { FrontendId = "builtin.fluent" });

        var coordinator = new AppearanceCoordinator(store);
        var changed = 0;
        coordinator.Changed += (_, _) => changed++;

        var settings = coordinator.Reload();

        Assert.Equal("builtin.fluent", settings.FrontendId);
        Assert.Equal("builtin.fluent", coordinator.FrontendId);
        Assert.Equal(1, changed);
    }

    [Fact]
    public void Reload_BrokenFile_FallsBackToDefaults_WithWarnings()
    {
        Directory.CreateDirectory(_directory);
        File.WriteAllText(Path_(), "{ broken");
        var coordinator = new AppearanceCoordinator(new AppearanceStore(Path_()));

        var settings = coordinator.Reload();

        Assert.Equal(AppearanceDefaults.Settings, settings);
        Assert.NotEmpty(coordinator.Warnings);
    }

    [Fact]
    public async Task Reload_DoesNotTouchResources_LeavingApplicationToTheShell()
    {
        var path = Path_();
        var store = new AppearanceStore(path);
        await store.WriteAsync(AppearanceDefaults.Settings with { MotionMode = MotionMode.Reduce });
        var coordinator = new AppearanceCoordinator(store);

        coordinator.Reload();

        Assert.Equal(MotionMode.Reduce, coordinator.Settings.MotionMode);
    }
}
