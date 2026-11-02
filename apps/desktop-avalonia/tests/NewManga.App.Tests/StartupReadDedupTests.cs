using Avalonia.Headless.XUnit;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.V2.Library;
using NewManga.CoreClient;

namespace NewManga.App.Tests;

/// <summary>
/// REALUSE-DATA-SAFETY-3 AC3 (audit MA-08): one launch used to read the whole shelf three times
/// (Host startup refresh, Library first paint, then the reader's own ListBooks). The evidence must be
/// call counts, not a feeling that startup got faster.
/// </summary>
public sealed class StartupReadDedupTests
{
    private static LibraryViewModel NewLibrary(FakeHostController fake) =>
        new(fake, new ShellState(), (_, _) => { }, _ => { });

    [AvaloniaFact]
    public async Task LibraryFirstPaint_ReusesTheStartupShelf_WithoutASecondRead()
    {
        var fake = V2Fixture.Create();
        Assert.Equal(HostViewState.Ready, fake.Snapshot.State); // the Host finished starting
        var library = NewLibrary(fake);

        await library.InitializeAsync();

        // The startup snapshot already carries the shelf: no extra Host read on first paint.
        Assert.Equal(0, fake.RefreshCalls);
        Assert.NotEmpty(library.Books);
    }

    [AvaloniaFact]
    public async Task ExplicitRefresh_StillReadsTheHost()
    {
        var fake = V2Fixture.Create();
        var library = NewLibrary(fake);
        await library.InitializeAsync();
        Assert.Equal(0, fake.RefreshCalls);

        await library.RefreshAsync();

        // A user refresh (or import/retry) must still go to the Host — dedup must not hide staleness.
        Assert.Equal(1, fake.RefreshCalls);
    }

    [AvaloniaFact]
    public async Task ColdSnapshot_StillReadsTheHost()
    {
        var fake = V2Fixture.Create();
        fake.Snapshot = fake.Snapshot with
        {
            State = HostViewState.Starting,
            Books = Array.Empty<BookSummary>(),
        };
        var library = NewLibrary(fake);

        await library.InitializeAsync();

        // No startup read happened yet, so the first paint must perform one.
        Assert.Equal(1, fake.RefreshCalls);
    }
}
