using System;
using System.IO;
using System.Threading.Tasks;
using NewManga.Appearance;
using Xunit;

namespace NewManga.Appearance.Tests;

/// <summary>
/// FEA-06-PREREQ-1 AC2 + FEA-06-PREREQ-2 P5/AC5: the coordinator reads/validates/broadcasts, never
/// applies resources itself (that stays the shell's job), and — after the P5 migration — is the single
/// writer of <c>presentation-settings.json</c>.
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

    private string Path_(string? name = null) =>
        Path.Combine(_directory, name ?? AppearanceStore.FileName);

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

    [Fact]
    public async Task SaveAsync_WritesThePresentationDocument_AndRaisesChangedOnce()
    {
        var path = Path_();
        var coordinator = new AppearanceCoordinator(new AppearanceStore(path));
        coordinator.Reload();
        var changed = 0;
        coordinator.Changed += (_, _) => changed++;
        var next = AppearanceDefaults.Settings with
        {
            FrontendId = "builtin.fluent",
            VisualThemeId = "builtin.fluent-dark",
            Mode = AppearanceMode.Dark,
        };

        await coordinator.SaveAsync(next);

        Assert.Equal(1, changed);
        Assert.True(File.Exists(path), "the canonical appearance document must be written");
        Assert.Equal(next, coordinator.Settings);
        Assert.Equal("builtin.fluent", coordinator.FrontendId);

        // Round-trip: a fresh coordinator reads the written document back.
        var reopened = new AppearanceCoordinator(new AppearanceStore(path)).Reload();
        Assert.Equal(next, reopened);

        // Atomic write must not leave the temporary file behind.
        Assert.False(File.Exists(path + ".tmp"));
    }

    [Fact]
    public async Task SaveAsync_DoesNotWriteTheLegacyDocument()
    {
        var legacyPath = Path_("theme-settings.json");
        var coordinator = new AppearanceCoordinator(new AppearanceStore(Path_(), legacyPath));

        await coordinator.SaveAsync(AppearanceDefaults.Settings);

        Assert.True(File.Exists(Path_()));
        Assert.False(File.Exists(legacyPath), "the coordinator must never write the legacy theme-settings.json");
    }

    [Fact]
    public void Reload_MigratesTheLegacyDocument_WhenTheNewOneIsAbsent()
    {
        var directory = Path.Combine(_directory, "legacy-only");
        Directory.CreateDirectory(directory);
        var legacyPath = Path.Combine(directory, "theme-settings.json");
        File.WriteAllText(legacyPath, "{\"themeId\":\"newmanga-default\"}");
        var coordinator = new AppearanceCoordinator(
            new AppearanceStore(Path.Combine(directory, AppearanceStore.FileName), legacyPath));

        coordinator.Reload();

        Assert.NotEmpty(coordinator.Warnings);
        Assert.Equal(legacyPath, Path.Combine(directory, "theme-settings.json"));
    }

    [Fact]
    public async Task SaveAsync_WithAnIdenticalDocument_DoesNotRaiseChanged()
    {
        var coordinator = new AppearanceCoordinator(new AppearanceStore(Path_()));
        coordinator.Reload();
        var changed = 0;
        coordinator.Changed += (_, _) => changed++;

        await coordinator.SaveAsync(AppearanceDefaults.Settings);

        Assert.Equal(0, changed);
    }
}
