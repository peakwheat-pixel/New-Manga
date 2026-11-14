using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.CoreClient;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// READER-PREF-PERSIST (E-4): the reader's own controls must persist what they change.
/// Before this card the single/double-page, direction and zoom buttons only mutated VM state and
/// nothing in the production path called <c>SaveReadingPreferencesAsync</c>, so every reader
/// preference was silently lost on restart.
/// </summary>
public sealed class ReaderPreferencePersistenceTests
{
    private static async Task<(FakeHostController Host, ReaderViewModel Vm)> LoadedAsync()
    {
        var host = new FakeHostController(new HostViewSnapshot(
            HostViewState.Ready, "ready", "—", null, null, Array.Empty<BookSummary>(), 0, false, null));
        host.ReaderBook = new ReaderBookData(
            "b1", "Book", "c1", "Ch", "single",
            new[]
            {
                new ReaderPageData("p1", 0, 100, 200),
                new ReaderPageData("p2", 1, 100, 200),
            });
        host.ReadingPreferences = new ReadingPreferencesInfo(
            "b1", "original", "ltr", 1.0, false, "single", "2026-01-01", false);
        var viewModel = new ReaderViewModel(host);
        await viewModel.LoadAsync("b1", "c1");
        return (host, viewModel);
    }

    /// <summary>AC6: the queued save runs asynchronously; wait for it to settle.</summary>
    private static async Task SettleAsync(FakeHostController host, int expectedMinimum = 1)
    {
        for (var spin = 0; spin < 200 && host.SaveReadingPreferencesCallCount < expectedMinimum; spin++)
        {
            await Task.Delay(5);
        }
    }

    [Fact]
    public async Task ToggleDoublePage_PersistsTheNewValue()
    {
        var (host, vm) = await LoadedAsync();
        Assert.False(vm.DoublePage);

        await vm.ToggleDoublePagePersistingAsync();
        await SettleAsync(host);

        Assert.True(vm.DoublePage);
        Assert.NotNull(host.LastSavedPreferences);
        Assert.True(host.LastSavedPreferences!.DoublePage);
    }

    [Fact]
    public async Task ToggleDirection_PersistsTheNewDirection()
    {
        var (host, vm) = await LoadedAsync();
        Assert.False(vm.ReverseDirection);

        await vm.ToggleDirectionPersistingAsync();
        await SettleAsync(host);

        Assert.True(vm.ReverseDirection);
        Assert.Equal("rtl", host.LastSavedPreferences!.Direction);
    }

    [Fact]
    public async Task ZoomControls_PersistTheNewZoom()
    {
        var (host, vm) = await LoadedAsync();

        await vm.ZoomByPersistingAsync(0.5);
        await SettleAsync(host);
        Assert.Equal(1.5, vm.Zoom);
        Assert.Equal(1.5, host.LastSavedPreferences!.Zoom);

        var before = host.SaveReadingPreferencesCallCount;
        await vm.ResetZoomPersistingAsync();
        await SettleAsync(host, before + 1);

        Assert.Equal(1.0, vm.Zoom);
        Assert.Equal(1.0, host.LastSavedPreferences!.Zoom);
    }

    /// <summary>AC5: a rejected write must be visible and must not be recorded as applied.</summary>
    [Fact]
    public async Task FailedSave_IsReportedAndNotTreatedAsApplied()
    {
        var (host, vm) = await LoadedAsync();
        host.SaveReadingPreferencesResult = false;

        await vm.ZoomByPersistingAsync(0.5);
        await SettleAsync(host);

        Assert.Contains("失败", vm.PreferenceSaveStatus, StringComparison.Ordinal);

        // The snapshot must NOT record 1.5 as applied: a later save still has to send the zoom,
        // otherwise the value the user changed would never reach Core again. Move to a value that
        // differs from BOTH the failed one and the original, so "skipped as unchanged" cannot pass
        // for "recorded correctly".
        host.SaveReadingPreferencesResult = true;
        var before = host.SaveReadingPreferencesCallCount;
        await vm.ZoomByPersistingAsync(0.2);
        await SettleAsync(host, before + 1);
        Assert.Equal(1.7, host.LastSavedPreferences!.Zoom!.Value, 3);
    }

    [Fact]
    public async Task SuccessfulSave_ClearsTheStatus()
    {
        var (host, vm) = await LoadedAsync();
        host.SaveReadingPreferencesResult = false;
        await vm.ZoomByPersistingAsync(0.5);
        await SettleAsync(host);
        Assert.NotEqual(string.Empty, vm.PreferenceSaveStatus);

        host.SaveReadingPreferencesResult = true;
        var before = host.SaveReadingPreferencesCallCount;
        await vm.ZoomByPersistingAsync(0.2);
        await SettleAsync(host, before + 1);

        Assert.Equal(string.Empty, vm.PreferenceSaveStatus);
    }

    /// <summary>
    /// AC6: rapid repeated changes must not each hit the wire. The queue coalesces them: the loop
    /// drains whatever changed while it was awaiting, so N clicks cost far fewer than N writes.
    /// </summary>
    [Fact]
    public async Task RapidZoomClicks_CoalesceIntoFewWrites()
    {
        var (host, vm) = await LoadedAsync();

        for (var click = 0; click < 6; click++)
        {
            await vm.ZoomByPersistingAsync(0.1);
        }
        await SettleAsync(host);

        Assert.Equal(1.6, vm.Zoom, 3);
        Assert.True(
            host.SaveReadingPreferencesCallCount <= 2,
            $"expected coalesced writes (<=2), got {host.SaveReadingPreferencesCallCount}");
    }
}
