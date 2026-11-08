using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using NewManga.App.Services;
using NewManga.App.Views.Presentation;
using NewManga.Appearance;
using NewManga.Presentation.Avalonia.Switching;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07 AC2 / FEA-07-RESIDUAL-2 AC-R4a-2: the stable presentation window owns native window identity
/// only. Closing, rebuilding or switching it must leave every Host lifecycle item unchanged — the window
/// never starts and never disposes the Host (the items are asserted one by one, not as an aggregate).
/// The discriminating cases use a fake Host whose Start/Dispose would throw and clear their script, so a
/// window that wrongly touched the Host could not pass silently.
/// </summary>
public sealed class PresentationWindowHostLifecycleTests : IDisposable
{
    private readonly string _root;
    private readonly AppearanceCoordinator _appearance;
    private readonly SwitchJournal _journal;

    public PresentationWindowHostLifecycleTests()
    {
        _root = Path.Combine(Path.GetTempPath(), $"nm-fea07-window-lifecycle-{Guid.NewGuid():N}");
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

    private PresentationWindow CreateWindow(IHostController host, Func<string, Control>? factory = null)
    {
        var options = AppOptions.Parse(Array.Empty<string>());
        var window = new PresentationWindow(
            options,
            FrontendSelector.Select(FrontendSelector.FluentFrontendId, persistedFrontendId: null),
            host,
            _appearance,
            _journal,
            factory ?? (id => Content(id, "hosted")));
        window.Show();
        return window;
    }

    [AvaloniaFact]
    public async Task CloseAndRebuild_LeaveEveryHostLifecycleItemUnchanged()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("book-a"));
        var changedEvents = 0;
        host.Changed += (_, _) => changedEvents++;
        var startsBefore = host.StartCalls;
        var startRequestsBefore = host.StartRequests;
        var lifecycleBefore = host.LifecycleLog.ToArray();
        var disposesBefore = host.DisposeCalls;

        var first = CreateWindow(host);
        try
        {
            var firstSwitch = await first.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);
            Assert.True(firstSwitch.Succeeded, firstSwitch.Failure);
        }
        finally
        {
            first.Close();
        }

        var rebuilt = CreateWindow(host);
        try
        {
            var rebuiltSwitch = await rebuilt.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);
            Assert.True(rebuiltSwitch.Succeeded, rebuiltSwitch.Failure);
            var backSwitch = await rebuilt.SwitchFrontendAsync(FrontendSelector.FluentFrontendId);
            Assert.True(backSwitch.Succeeded, backSwitch.Failure);
        }
        finally
        {
            rebuilt.Close();
        }

        Assert.Equal(startsBefore, host.StartCalls);
        Assert.Equal(startRequestsBefore, host.StartRequests);
        Assert.Equal(lifecycleBefore, host.LifecycleLog);
        Assert.Equal(disposesBefore, host.DisposeCalls);
        Assert.Equal(0, host.StartCalls);
        Assert.Equal(0, host.StartRequests);
        Assert.Empty(host.LifecycleLog);
        Assert.Equal(0, host.DisposeCalls);
        Assert.Equal(0, changedEvents);
    }

    [AvaloniaFact]
    public async Task SwitchingFrontends_DoesNotStartOrDisposeTheHost()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("book-a"));
        var window = CreateWindow(host);
        try
        {
            for (var i = 0; i < 4; i++)
            {
                var target = i % 2 == 0
                    ? FrontendSelector.CurrentV2FrontendId
                    : FrontendSelector.FluentFrontendId;
                var result = await window.SwitchFrontendAsync(target);
                Assert.True(result.Succeeded, result.Failure);
            }
        }
        finally
        {
            window.Close();
        }

        Assert.Equal(0, host.StartCalls);
        Assert.Equal(0, host.StartRequests);
        Assert.Empty(host.LifecycleLog);
        Assert.Equal(0, host.DisposeCalls);
    }

    /// <summary>
    /// Window-level discriminator (the FEA-04 rebuild shape, lifted to the OS window): a Host whose
    /// Start/Dispose would throw and whose scripted lifecycle counters move on any call is handed to the
    /// window; close + rebuild + switch must leave both scripts unconsumed and both counters at zero.
    /// </summary>
    [AvaloniaFact]
    public async Task WindowLifecycle_IsDiscriminatingAgainstHostStartAndDisposeCalls()
    {
        var startFailure = new InvalidOperationException("the presentation window must not start the Host");
        var disposeFailure = new InvalidOperationException("the presentation window must not dispose the Host");
        var host = new FakeHostController(FakeHostController.ReadySnapshot("book-a"))
        {
            StartException = startFailure,
            DisposeException = disposeFailure,
        };

        var window = CreateWindow(host);
        try
        {
            var switched = await window.SwitchFrontendAsync(FrontendSelector.CurrentV2FrontendId);
            Assert.True(switched.Succeeded, switched.Failure);
            window.Close();

            var rebuilt = CreateWindow(host);
            try
            {
                var rebuiltSwitch = await rebuilt.SwitchFrontendAsync(FrontendSelector.FluentFrontendId);
                Assert.True(rebuiltSwitch.Succeeded, rebuiltSwitch.Failure);
            }
            finally
            {
                rebuilt.Close();
            }
        }
        finally
        {
            if (window.IsVisible)
            {
                window.Close();
            }
        }

        Assert.Equal(0, host.StartCalls);
        Assert.Equal(0, host.DisposeCalls);
        Assert.Empty(host.LifecycleLog);
        // The fake consumes (and clears) a scripted exception when it is called: both still pending
        // proves neither StartAsync nor DisposeAsync ever ran.
        Assert.Same(startFailure, host.StartException);
        Assert.Same(disposeFailure, host.DisposeException);
    }
}
