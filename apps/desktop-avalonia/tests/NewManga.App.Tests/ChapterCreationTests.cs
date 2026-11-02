using System.Globalization;
using NewManga.App.Services;
using NewManga.CoreClient;
using NewManga.Host;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-A-1 (audit P-01, contract §5.1): the service-layer <c>CreateChapterAsync</c> seam.
/// The Core envelope was verified against <c>src/bootstrap/core_service.py</c>
/// (<c>handle_create_chapter</c> / <c>_CREATE_FIELDS</c> / <c>_create_validation_details</c>):
/// request <c>{"book_id","title"}</c> at protocol minor 8, result
/// <c>{chapter_id,title,chapter_number,sort_order}</c>, blank title → <c>INVALID_REQUEST</c>,
/// unknown book → <c>TARGET_NOT_FOUND</c>, duplicates allowed, no title length limit.
/// </summary>
public sealed class CreateChapterNullControllerTests
{
    private static readonly NullHostController Controller = NullHostController.Instance;

    [Fact]
    public async Task NullController_ValidCall_ReturnsDeterministicIncrementingChapter()
    {
        var first = await Controller.CreateChapterAsync("book-null-1", "第 1 章");
        var second = await Controller.CreateChapterAsync("book-null-1", "第 2 章");

        Assert.NotNull(first);
        Assert.NotNull(second);
        Assert.Equal("第 1 章", first!.Title);
        Assert.Equal("第 2 章", second!.Title);
        Assert.NotEqual(first.ChapterId, second.ChapterId);
        Assert.Equal(first.SortOrder + 1, second.SortOrder);
        Assert.StartsWith("null-chapter-", first.ChapterId, StringComparison.Ordinal);
        Assert.Equal(first.SortOrder.ToString(CultureInfo.InvariantCulture), first.ChapterNumber);
    }

    [Fact]
    public async Task NullController_BlankArgumentsAndCancellation_ReturnNullWithoutAdvancingSequence()
    {
        var baseline = await Controller.CreateChapterAsync("book-null-2", "基线章");
        Assert.NotNull(baseline);

        Assert.Null(await Controller.CreateChapterAsync("  ", "空书"));
        Assert.Null(await Controller.CreateChapterAsync("book-null-2", "   "));
        Assert.Null(await Controller.CreateChapterAsync("book-null-2", "取消", new CancellationToken(canceled: true)));

        var next = await Controller.CreateChapterAsync("book-null-2", "下一章");
        Assert.NotNull(next);
        Assert.Equal(baseline!.SortOrder + 1, next!.SortOrder);
    }
}

/// <summary>
/// V11R-A-1: the host controller's local refusal paths need no sidecar — they must return null and
/// publish a typed code through <see cref="HostViewSnapshot.LastError"/> (contract §5.1/AC3).
/// </summary>
public sealed class CreateChapterHostLocalFailureTests
{
    private static HostOptions Options() => new()
    {
        DataRoot = Path.Combine(Path.GetTempPath(), "newmanga-a1-local-" + Guid.NewGuid().ToString("N")[..10]),
        LogDirectory = Path.Combine(Path.GetTempPath(), "newmanga-a1-local-logs"),
        SidecarDirectoryOverride = Path.Combine(Path.GetTempPath(), "no-sidecars-in-this-test"),
        MutexName = @"Local\NewManga.App.Tests.A1.Local." + Guid.NewGuid().ToString("N")[..10],
        DetectLegacyShell = false,
        ParityReached = true,
    };

    [Fact]
    public async Task CreateChapter_BeforeStart_PublishesHostNotReady()
    {
        await using var controller = new HostController(Options());
        var changed = 0;
        controller.Changed += (_, _) => changed++;

        var chapter = await controller.CreateChapterAsync("book-1", "第 1 章");

        Assert.Null(chapter);
        Assert.Equal("HOST_NOT_READY", controller.Snapshot.LastError);
        Assert.True(changed > 0);
        Assert.Equal(HostViewState.Starting, controller.Snapshot.State);
    }

    [Fact]
    public async Task CreateChapter_EmptyBookId_IsRejectedBeforeAnyWireFrame()
    {
        await using var controller = new HostController(Options());

        var chapter = await controller.CreateChapterAsync("   ", "第 1 章");

        Assert.Null(chapter);
        Assert.Equal("INVALID_REQUEST", controller.Snapshot.LastError);
    }

    [Fact]
    public async Task CreateChapter_CancelledToken_PublishesCancelled()
    {
        await using var controller = new HostController(Options());

        var chapter = await controller.CreateChapterAsync(
            "book-1",
            "第 1 章",
            new CancellationToken(canceled: true));

        Assert.Null(chapter);
        Assert.Equal("CANCELLED", controller.Snapshot.LastError);
    }
}

/// <summary>
/// V11R-A-1 AC5: the UI test double exposes the same success / failure / cancellation channels, so a
/// create-chapter dialog can be driven headlessly without sidecars.
/// </summary>
public sealed class CreateChapterUiSeamTests
{
    private static FakeHostController Ready() => new(FakeHostController.ReadySnapshot("书一"));

    [Fact]
    public async Task FakeController_ValidCall_RecordsRequestAndReturnsChapter()
    {
        var controller = Ready();

        var chapter = await controller.CreateChapterAsync("book-0", "第 1 章");

        Assert.NotNull(chapter);
        Assert.Equal("第 1 章", chapter!.Title);
        Assert.Equal(("book-0", "第 1 章"), controller.CreateChapterRequests.Single());
        Assert.Null(controller.Snapshot.LastError);
    }

    [Fact]
    public async Task FakeController_ScriptedFailure_ReturnsNullWithTypedCode()
    {
        var controller = Ready();
        controller.ScriptedCreateChapters.Enqueue(null);

        var chapter = await controller.CreateChapterAsync("book-0", "第 1 章");

        Assert.Null(chapter);
        Assert.Equal("SCRIPTED_FAILURE", controller.Snapshot.LastError);
    }

    [Fact]
    public async Task FakeController_BlankOrCancelled_ReturnsNullWithTypedCode()
    {
        var controller = Ready();

        Assert.Null(await controller.CreateChapterAsync("  ", "第 1 章"));
        Assert.Equal("INVALID_REQUEST", controller.Snapshot.LastError);

        Assert.Null(await controller.CreateChapterAsync("book-0", "第 1 章", new CancellationToken(canceled: true)));
        Assert.Equal("CANCELLED", controller.Snapshot.LastError);
    }
}

/// <summary>
/// V11R-A-1 AC5 integration: the real <see cref="HostController"/> against the frozen sidecars in an
/// isolated writable data root. Self-skips with an explicit reason when the AC11 sidecar copy is not
/// available (the repository's existing fixture convention, see
/// <c>tests/NewManga.Host.Tests/Support/HostFixture.cs</c>).
/// </summary>
public sealed class CreateChapterHostIntegrationTests
{
    [HostSidecarFact]
    public async Task HostController_CreateChapter_SucceedsThenMapsCoreFailures()
    {
        var options = CreateChapterSidecarFixture.CreateOptions("v11r-a1-create", parity: true, out var dataRoot);
        var controller = new HostController(options);
        try
        {
            await controller.StartAsync();
            Assert.True(
                controller.Snapshot.State == HostViewState.Ready,
                $"host not ready: {controller.Snapshot.ErrorCode} {controller.Snapshot.ErrorMessage}");
            Assert.True(controller.Snapshot.WritesAllowed);

            var bookTitle = "V11R-A-1 建章夹具 " + Guid.NewGuid().ToString("N")[..8];
            Assert.True(await controller.TryCreateBookAsync(bookTitle));
            var book = controller.Snapshot.Books.Single(candidate => candidate.Title == bookTitle);

            // AC1/AC2 success: Core CreateChapter (protocol minor 8) returns the new chapter.
            var chapter = await controller.CreateChapterAsync(book.BookId, "第 1 章");
            Assert.NotNull(chapter);
            Assert.False(string.IsNullOrWhiteSpace(chapter!.ChapterId));
            Assert.Equal("第 1 章", chapter.Title);
            Assert.Equal(string.Empty, chapter.ChapterNumber);
            Assert.True(chapter.SortOrder >= 1);
            Assert.Null(controller.Snapshot.LastError);

            var chapters = await controller.ListChaptersAsync(book.BookId);
            Assert.Contains(chapters, candidate => candidate.ChapterId == chapter.ChapterId);

            // AC4 duplicate titles keep the Core semantics: a new chapter, never a de-duplication.
            var duplicate = await controller.CreateChapterAsync(book.BookId, "第 1 章");
            Assert.NotNull(duplicate);
            Assert.NotEqual(chapter.ChapterId, duplicate!.ChapterId);
            Assert.True(duplicate.SortOrder > chapter.SortOrder);

            // AC4 no local length policy either: the Core is the authority (it stores any non-blank
            // title), so the service layer must not truncate or reject a long title.
            var longTitle = new string('长', 1024);
            var longChapter = await controller.CreateChapterAsync(book.BookId, longTitle);
            Assert.NotNull(longChapter);
            Assert.Equal(longTitle, longChapter!.Title);

            // AC3 blank title: the Core rejects it with INVALID_REQUEST; null + typed code here.
            Assert.Null(await controller.CreateChapterAsync(book.BookId, "   "));
            Assert.Equal("INVALID_REQUEST", controller.Snapshot.LastError);

            // AC3 unknown book: Core TARGET_NOT_FOUND is preserved verbatim.
            Assert.Null(await controller.CreateChapterAsync("missing-book-id", "第 1 章"));
            Assert.Equal("TARGET_NOT_FOUND", controller.Snapshot.LastError);

            // AC5 cancellation: null + typed code, and no Core row is created.
            var beforeCancel = (await controller.ListChaptersAsync(book.BookId)).Count;
            Assert.Null(await controller.CreateChapterAsync(
                book.BookId,
                "取消章",
                new CancellationToken(canceled: true)));
            Assert.Equal("CANCELLED", controller.Snapshot.LastError);
            Assert.Equal(beforeCancel, (await controller.ListChaptersAsync(book.BookId)).Count);
        }
        finally
        {
            await controller.DisposeAsync();
            CreateChapterSidecarFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [HostSidecarFact]
    public async Task HostController_CreateChapter_WhenReadOnly_PublishesHostReadOnly()
    {
        var options = CreateChapterSidecarFixture.CreateOptions("v11r-a1-readonly", parity: false, out var dataRoot);
        var controller = new HostController(options);
        try
        {
            await controller.StartAsync();
            Assert.True(
                controller.Snapshot.State == HostViewState.Ready,
                $"host not ready: {controller.Snapshot.ErrorCode} {controller.Snapshot.ErrorMessage}");
            Assert.False(controller.Snapshot.WritesAllowed);

            var chapter = await controller.CreateChapterAsync("any-book-id", "第 1 章");

            Assert.Null(chapter);
            Assert.Equal("HOST_READ_ONLY", controller.Snapshot.LastError);
            Assert.Equal(HostViewState.Ready, controller.Snapshot.State);
        }
        finally
        {
            await controller.DisposeAsync();
            CreateChapterSidecarFixture.TryDeleteDirectory(dataRoot);
        }
    }
}

/// <summary>
/// V11R-A-1: self-skipping integration fact — same convention as the existing Host fixture
/// (<c>NEWMANGA_CORECLIENT_SIDECAR_DIR</c> points at the AC11 unlabelled sidecar copy).
/// </summary>
public sealed class HostSidecarFactAttribute : FactAttribute
{
    public HostSidecarFactAttribute()
    {
        if (!CreateChapterSidecarFixture.TryGetSidecarDirectory(out _, out var reason))
        {
            Skip = reason;
        }
    }
}

/// <summary>V11R-A-1: isolated writable data root + frozen sidecar directory for the integration facts.</summary>
internal static class CreateChapterSidecarFixture
{
    private const string SidecarVariable = "NEWMANGA_CORECLIENT_SIDECAR_DIR";
    private const string EvidenceVariable = "NEWMANGA_EVIDENCE_DIR";

    public static bool TryGetSidecarDirectory(out string directory, out string reason)
    {
        directory = Environment.GetEnvironmentVariable(SidecarVariable) ?? string.Empty;
        if (string.IsNullOrWhiteSpace(directory))
        {
            reason = $"reason: needs sidecar fixture - set {SidecarVariable} or run " +
                     "apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy)";
            return false;
        }

        foreach (var exe in new[] { "core_service.exe", "host_bridge.exe" })
        {
            if (!File.Exists(Path.Combine(directory, exe)))
            {
                reason = $"reason: needs sidecar fixture - {exe} missing under {SidecarVariable}";
                return false;
            }
        }

        reason = string.Empty;
        return true;
    }

    public static HostOptions CreateOptions(string label, bool parity, out string dataRoot)
    {
        if (!TryGetSidecarDirectory(out var sidecarDirectory, out var reason))
        {
            throw new InvalidOperationException(reason);
        }

        dataRoot = Path.Combine(
            Path.GetTempPath(),
            "newmanga-app-tests",
            label + "-" + Guid.NewGuid().ToString("N")[..10]);
        foreach (var child in new[] { "derived", "catalog", "managed" })
        {
            Directory.CreateDirectory(Path.Combine(dataRoot, child));
        }

        var evidence = Environment.GetEnvironmentVariable(EvidenceVariable);
        var logDirectory = string.IsNullOrWhiteSpace(evidence)
            ? Path.Combine(Path.GetTempPath(), "newmanga-app-tests-logs", label)
            : Path.Combine(evidence, "host-logs", label);
        Directory.CreateDirectory(logDirectory);

        return new HostOptions
        {
            DataRoot = dataRoot,
            LogDirectory = logDirectory,
            SidecarDirectoryOverride = sidecarDirectory,
            MutexName = @"Local\NewManga.App.Tests.A1." + Guid.NewGuid().ToString("N")[..12],
            DetectLegacyShell = false,
            ParityReached = parity,
            EnableWireEvidence = true,
            StartupTimeout = TimeSpan.FromSeconds(90),
            RequestTimeout = TimeSpan.FromSeconds(60),
        };
    }

    public static void TryDeleteDirectory(string path)
    {
        try
        {
            if (Directory.Exists(path))
            {
                Directory.Delete(path, recursive: true);
            }
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
        {
            // best effort; temp roots are disposable
        }
    }
}
