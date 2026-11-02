using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using NewManga.App.Services;
using NewManga.App.Views.Presentation;
using NewManga.Appearance;
using NewManga.Presentation.Avalonia.Switching;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07 slice 2b: the stable window keeps its native identity while hosting/switching the frontend
/// content tree; switch failures roll back to the previous tree (§7.1/§7.3/H2).
/// </summary>
public sealed class PresentationWindowTests : IDisposable
{
    private readonly string _root;
    private readonly AppearanceCoordinator _appearance;
    private readonly SwitchJournal _journal;

    public PresentationWindowTests()
    {
        _root = Path.Combine(Path.GetTempPath(), $"nm-fea07-window-{Guid.NewGuid():N}");
        Directory.CreateDirectory(_root);
        _appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(_root, AppearanceStore.FileName)));
        _appearance.Reload();
        _journal = new SwitchJournal(Path.Combine(_root, "switch-journal.json"));
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

    private static Border Content(string id, string marker) => new()
    {
        Child = new TextBlock { Text = $"{marker}:{id}" },
    };

    private static string TextOf(PresentationWindow window) =>
        (window.ContentHost.Current as Border)?.Child is TextBlock text ? text.Text ?? string.Empty : string.Empty;

    private PresentationWindow CreateWindow(Func<string, Control>? factory = null)
    {
        var options = AppOptions.Parse(Array.Empty<string>());
        return new PresentationWindow(
            options,
            FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null),
            hostController: null,
            _appearance,
            _journal,
            factory ?? (id => Content(id, "hosted")));
    }

    [AvaloniaFact]
    public void Window_HostsInitialFrontendContentAndGeometry()
    {
        var window = CreateWindow();

        Assert.Equal("New Manga", window.Title);
        Assert.Equal(1100, window.Width);
        Assert.Equal(760, window.Height);
        Assert.Equal(FrontendSelector.FluentFrontendId, window.CurrentFrontendId);
        Assert.Equal($"hosted:{FrontendSelector.FluentFrontendId}", TextOf(window));
    }

    [AvaloniaFact]
    public async Task Switch_ReplacesContentButKeepsWindowIdentity()
    {
        var window = CreateWindow();
        var nativeIdentity = window;

        var result = await window.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);

        Assert.True(result.Succeeded, result.Failure);
        Assert.Same(nativeIdentity, window);
        Assert.Equal(FrontendSelector.CurrentV2FrontendId, window.CurrentFrontendId);
        Assert.Equal($"hosted:{FrontendSelector.CurrentV2FrontendId}", TextOf(window));
        Assert.Equal(FrontendSelector.CurrentV2FrontendId, _appearance.FrontendId);
    }

    [AvaloniaFact]
    public async Task FailedSwitch_KeepsPreviousContentAndJournalRecordsRollback()
    {
        var window = new PresentationWindow(
            AppOptions.Parse(Array.Empty<string>()),
            FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null),
            hostController: null,
            _appearance,
            _journal,
            id => id == FrontendSelector.CurrentV2FrontendId
                ? throw new InvalidOperationException("cannot build v2")
                : Content(id, "hosted"));

        
        {
            var result = await window.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);

            Assert.False(result.Succeeded);
            Assert.Equal(FrontendSelector.FluentFrontendId, window.CurrentFrontendId);
            Assert.Equal($"hosted:{FrontendSelector.FluentFrontendId}", TextOf(window));
            Assert.True(_journal.TryRead(out var entry, out _));
            Assert.Equal(SwitchStage.RolledBack, entry!.Stage);
        }
    }

    [AvaloniaFact]
    public async Task UnknownFrontend_IsRejectedWithoutTouchingContent()
    {
        var window = CreateWindow();
        var before = TextOf(window);

        var result = await window.SwitchFrontendAsync("builtin.not-a-frontend");

        Assert.False(result.Succeeded);
        Assert.Equal(before, TextOf(window));
        Assert.Equal(FrontendSelector.FluentFrontendId, window.CurrentFrontendId);
    }

    [AvaloniaFact]
    public async Task RepeatedSwitches_KeepOneContentTree()
    {
        var window = CreateWindow();

        for (var i = 0; i < 20; i++)
        {
            var target = i % 2 == 0 ? FrontendSelector.CurrentV2FrontendId : FrontendSelector.FluentFrontendId;
            var result = await window.SwitchFrontendAsync(target);
            Assert.True(result.Succeeded, result.Failure);
            Assert.Equal(target, window.CurrentFrontendId);
            Assert.NotNull(window.ContentHost.Current);
        }

        Assert.IsType<Border>(window.ContentHost.Current);
        Assert.False(File.Exists(_journal.FilePath));
    }
}
