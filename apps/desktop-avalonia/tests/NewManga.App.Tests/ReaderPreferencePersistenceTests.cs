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
        // P2-4 (r1 复核): "0 writes" must not satisfy a coalescing assertion.
        Assert.InRange(host.SaveReadingPreferencesCallCount, 1, 2);
        // r2 复核: also pin THAT the coalesced write carried the final value, not just the count.
        Assert.Equal(1.6, host.LastSavedPreferences!.Zoom!.Value, 3);
    }

    /// <summary>
    /// P2-1 (r2 复核): the intent must carry its own diff baseline. Without it, a book switch that
    /// happens inside the 80ms coalesce window replaces the baseline with the NEW book's snapshot;
    /// if that happens to equal the pending value the change looks already-stored and **zero**
    /// writes happen -- the first book's edit is silently lost.
    /// </summary>
    [Fact]
    public async Task PendingChange_QueuedBeforeASwitchToAMatchingBook_IsStillWritten()
    {
        var (host, vm) = await LoadedAsync();

        // Queue the intent for b1 (zoom 1.0 -> 1.5); the drain waits one coalesce window.
        await vm.ZoomByPersistingAsync(0.5);
        Assert.Equal(0, host.SaveReadingPreferencesCallCount);

        // Inside that window the user opens b2, whose stored zoom happens to be exactly 1.5.
        host.ReadingPreferences = new ReadingPreferencesInfo(
            "b2", "original", "ltr", 1.5, false, "single", "2026-01-01", false);
        host.ReaderBook = new ReaderBookData(
            "b2", "Book Two", "c2", "Ch Two", "single",
            new[] { new ReaderPageData("q1", 0, 100, 200) });
        await vm.LoadAsync("b2", "c2");
        Assert.Equal(1.5, vm.Zoom, 3); // b2's snapshot, not b1's pending value

        // The queued change must still reach the host (for b1): a captured baseline makes
        // "1.5 vs 1.0" a real difference even though the reader now reports 1.5.
        for (var spin = 0; spin < 400 && host.SaveReadingPreferencesCallCount == 0; spin++)
        {
            await Task.Delay(5);
        }
        Assert.True(
            host.SaveReadingPreferencesCallCount >= 1,
            "the queued change was dropped after the switch (0 writes)");
        Assert.Equal(1.5, host.LastSavedPreferences!.Zoom!.Value, 3);
    }

    /// <summary>
    /// P1-1 (r1 review): a change made WHILE a save is in flight must still be persisted.
    /// The first implementation recorded the VM's then-current values as "applied" after the await,
    /// so the newer change looked already-stored and the follow-up diff was empty.
    /// </summary>
    [Fact]
    public async Task ChangeMadeWhileASaveIsInFlight_IsStillPersisted()
    {
        var (host, vm) = await LoadedAsync();
        var gate = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        host.SaveReadingPreferencesOverride = (_, _) => gate.Task;

        await vm.ZoomByPersistingAsync(0.5); // → 1.5
        for (var spin = 0; spin < 200 && host.SaveReadingPreferencesCallCount == 0; spin++)
        {
            await Task.Delay(5);
        }
        Assert.Equal(1, host.SaveReadingPreferencesCallCount);
        Assert.Equal(1.5, host.LastSavedPreferences!.Zoom!.Value, 3);

        // Change again while that write is still pending.
        await vm.ZoomByPersistingAsync(0.2); // → 1.7
        host.SaveReadingPreferencesOverride = null;
        gate.SetResult(true);

        for (var spin = 0; spin < 400 && host.SaveReadingPreferencesCallCount < 2; spin++)
        {
            await Task.Delay(5);
        }

        Assert.Equal(1.7, host.LastSavedPreferences!.Zoom!.Value, 3);
        Assert.Equal(1.7, vm.Zoom, 3);
    }

    /// <summary>
    /// AC5/R2: the write is awaited, so the reader can switch books mid-flight. A result that
    /// belongs to the book the reader has left must not paint a status on the book now on screen.
    /// </summary>
    [Fact]
    public async Task FailedSave_ForABookTheUserAlreadyLeft_DoesNotPolluteTheNewBook()
    {
        var host = new FakeHostController(new HostViewSnapshot(
            HostViewState.Ready, "ready", "—", null, null, Array.Empty<BookSummary>(), 0, false, null));
        host.ReaderBook = new ReaderBookData(
            "b1", "Book", "c1", "Ch", "single",
            new[] { new ReaderPageData("p1", 0, 100, 200) });
        host.ReadingPreferences = new ReadingPreferencesInfo(
            "b1", "original", "ltr", 1.0, false, "single", "2026-01-01", false);
        var vm = new ReaderViewModel(host);
        await vm.LoadAsync("b1", "c1");

        var gate = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        host.SaveReadingPreferencesOverride = (_, _) => gate.Task;

        await vm.ZoomByPersistingAsync(0.5);
        // The drain waits one coalesce window before writing; wait until the write is in flight.
        for (var spin = 0; spin < 200 && host.SaveReadingPreferencesCallCount == 0; spin++)
        {
            await Task.Delay(5);
        }
        Assert.Equal(1, host.SaveReadingPreferencesCallCount);

        // The user opens another book while the write is still pending.
        host.SaveReadingPreferencesOverride = null;
        host.ReaderBook = new ReaderBookData(
            "b2", "Book Two", "c2", "Ch Two", "single",
            new[] { new ReaderPageData("q1", 0, 100, 200) });
        await vm.LoadAsync("b2", "c2");
        Assert.Equal("b2", vm.Book!.BookId);

        // The write for the book the user already left fails afterwards.
        gate.SetResult(false);
        await Task.Delay(50);

        Assert.DoesNotContain("失败", vm.PreferenceSaveStatus, StringComparison.Ordinal);
    }
}
