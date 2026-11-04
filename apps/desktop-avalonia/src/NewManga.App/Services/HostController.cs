using Avalonia.Threading;
using NewManga.CoreClient;
using NewManga.CoreClient.Bridge;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;
using NewManga.Host;
using NewManga.Host.Sources;

namespace NewManga.App.Services;

/// <summary>
/// Production controller: starts <see cref="HostRuntime"/> and maps typed failures to UI text.
/// FEA-09-UI-1: also implements <see cref="ISourceImportController"/> — a SEPARATE face, so the
/// frozen C-07 <see cref="IHostController"/> inventory (54 members) stays byte-identical.
/// </summary>
public sealed class HostController : IHostController, ISourceImportController
{
    private readonly HostOptions _options;
    private readonly object _startLock = new();

    /// <summary>
    /// REALUSE-DATA-SAFETY-3 AC3: chapter lists already read this session (per book id). Guarded by
    /// <see cref="_chapterCacheLock"/>: the UI can issue concurrent reads (Library + reader + tests).
    /// </summary>
    private readonly Dictionary<string, IReadOnlyList<ChapterSummary>> _chapterCache = new(StringComparer.Ordinal);

    private readonly object _chapterCacheLock = new();
    private HostRuntime? _runtime;
    private Task? _startTask;
    private int _startRequests;
    private HostViewSnapshot _snapshot = new(
        HostViewState.Starting,
        "正在启动 Host…",
        "—",
        null,
        null,
        Array.Empty<BookSummary>(),
        0,
        true,
        null)
    {
        // V11R-A-5: until the Host is ready the write gate stays closed and the reason is explicit.
        WritesAllowed = false,
        ReadOnlyReason = "Host 未就绪（只读）",
    };

    public HostController(HostOptions options)
    {
        _options = options;
    }

    /// <summary>
    /// V11R-INT-2: Changed is consumed by UI ViewModels (shell chrome, Studio page, legacy panels). Host
    /// continuations run on the thread pool, so the event is always marshalled to the UI thread.
    /// </summary>
    private void RaiseChanged()
    {
        if (Dispatcher.UIThread.CheckAccess())
        {
            Changed?.Invoke(this, EventArgs.Empty);
        }
        else
        {
            Dispatcher.UIThread.Post(() => Changed?.Invoke(this, EventArgs.Empty));
        }
    }

    public HostViewSnapshot Snapshot => _snapshot;

    /// <inheritdoc />
    public int StartRequests => Volatile.Read(ref _startRequests);

    public event EventHandler? Changed;

    /// <summary>
    /// V11R-INT-2: idempotent startup. The sidecar must be started exactly once per process, no matter
    /// how many shell/lifecycle paths ask (v2 shell initialization is the product path; the legacy
    /// shell keeps its single call). Repeated calls return the same task.
    /// </summary>
    public Task StartAsync(CancellationToken cancellationToken = default)
    {
        lock (_startLock)
        {
            Interlocked.Increment(ref _startRequests);
            // REALUSE-DATA-SAFETY-2 AC2: a FAILED start used to be cached forever, which made the
            // UI's "retry" a silent no-op (audit MA-04). A completed, unsuccessful attempt is
            // cleared first so retry is a real second attempt; a completed *successful* start stays
            // cached (one sidecar per process).
            //
            // Review r1 M1: dropping the old runtime without disposing it leaks the Win32
            // single-instance mutex. HostRuntime.StartAsync RETURNS a runtime even on failure (the
            // catch blocks set Result = Failed and stop sidecars, but never release _guard), so a
            // retry would then see AlreadyRunning forever. The stale instance is handed to
            // StartCoreAsync, which disposes it before the new attempt.
            HostRuntime? staleRuntime = null;
            if (_startTask is { IsCompleted: true } && _snapshot.State != HostViewState.Ready)
            {
                staleRuntime = _runtime;
                _startTask = null;
                _runtime = null;
                _snapshot = new HostViewSnapshot(
                    HostViewState.Starting,
                    "正在重试启动 Host…",
                    "—",
                    null,
                    null,
                    Array.Empty<BookSummary>(),
                    0,
                    true,
                    null)
                {
                    WritesAllowed = false,
                    ReadOnlyReason = "Host 未就绪（只读）",
                };
                RaiseChanged();
            }

            return _startTask ??= StartCoreAsync(cancellationToken, staleRuntime);
        }
    }

    private async Task StartCoreAsync(CancellationToken cancellationToken, HostRuntime? staleRuntime = null)
    {
        if (staleRuntime is not null)
        {
            // Release the previous attempt's single-instance mutex and sidecar handles before the
            // new attempt tries to acquire them. Cleanup failures must not hide the retry.
            try
            {
                await staleRuntime.DisposeAsync().ConfigureAwait(false);
            }
            catch (Exception ex) when (ex is ObjectDisposedException or IOException or InvalidOperationException)
            {
                // Best effort: the retry must proceed even if the stale instance is half-disposed.
                // Only the exception type is written (never a path or message).
                System.Diagnostics.Debug.WriteLine($"stale runtime cleanup failed: {ex.GetType().Name}");
            }
        }

        try
        {
            _runtime = await HostRuntime.StartAsync(_options, cancellationToken).ConfigureAwait(false);
            UpdateFromRuntime();
        }
        catch (Exception ex) when (ex is SidecarException or IOException or UnauthorizedAccessException or OperationCanceledException)
        {
            _snapshot = _snapshot with
            {
                State = HostViewState.Failed,
                StatusLine = "Host 启动失败",
                ErrorCode = ex is SidecarException sidecar ? sidecar.Code.ToString() : "HOST_START_IO",
                ErrorMessage = ex is SidecarException typed ? typed.UserMessage : "Host 启动时发生 I/O 错误，详见 host.log。",
                WritesAllowed = false,
                ReadOnlyReason = "Host 启动失败（只读）",
            };
            RaiseChanged();
        }

        if (_snapshot.State == HostViewState.Ready)
        {
            await RefreshBooksAsync(cancellationToken).ConfigureAwait(false);
        }
    }

    public async Task RefreshBooksAsync(CancellationToken cancellationToken = default)
    {
        if (_runtime is null || !_runtime.Result.IsReady)
        {
            return;
        }

        try
        {
            var books = await _runtime.ListBooksAsync(cancellationToken).ConfigureAwait(false);
            // A real shelf read is the user-visible "refresh" (and follows import/restore). Chapter
            // lists cached for the session must not outlive it.
            lock (_chapterCacheLock)
            {
                _chapterCache.Clear();
            }

            UpdateFromRuntime(books);
        }
        catch (CoreOperationException ex)
        {
            _snapshot = _snapshot with
            {
                State = HostViewState.Failed,
                StatusLine = "读取书架失败",
                ErrorCode = ex.Code,
                ErrorMessage = "Core 返回了错误码，详见 host.log。",
                WritesAllowed = false,
                ReadOnlyReason = "Host 不可用（只读）",
            };
            RaiseChanged();
        }
        catch (SidecarException ex)
        {
            _snapshot = _snapshot with
            {
                State = HostViewState.Failed,
                StatusLine = "核心服务中断",
                ErrorCode = ex.Code.ToString(),
                ErrorMessage = ex.UserMessage,
                WritesAllowed = false,
                ReadOnlyReason = "Host 不可用（只读）",
            };
            RaiseChanged();
        }
    }

    public async Task<bool> TryChineseRoundTripAsync(string title, CancellationToken cancellationToken = default)
    {
        if (_runtime is null || !_runtime.Result.IsReady)
        {
            return false;
        }

        try
        {
            var result = await _runtime.RoundTripChineseTitleAsync(title, cancellationToken).ConfigureAwait(false);
            _snapshot = _snapshot with
            {
                LastChineseRoundTrip = result.ExactMatch
                    ? $"往返一致：{result.Expected}"
                    : $"往返不一致：expected={result.Expected} received={result.Received}",
            };
            RaiseChanged();
            await RefreshBooksAsync(cancellationToken).ConfigureAwait(false);
            return result.ExactMatch;
        }
        catch (ReadOnlyHostException)
        {
            _snapshot = _snapshot with
            {
                LastChineseRoundTrip = "只读模式：S2 parity 前禁止写生产数据",
            };
            RaiseChanged();
            return false;
        }
        catch (Exception ex) when (ex is CoreOperationException or SidecarException)
        {
            _snapshot = _snapshot with
            {
                State = HostViewState.Failed,
                StatusLine = "中文往返失败",
                ErrorCode = ex is CoreOperationException core ? core.Code : ((SidecarException)ex).Code.ToString(),
                ErrorMessage = "核心服务返回错误，详见 host.log。",
                WritesAllowed = false,
                ReadOnlyReason = "Host 不可用（只读）",
            };
            RaiseChanged();
            return false;
        }
    }

    public async Task<bool> TryCreateBookAsync(string title, CancellationToken cancellationToken = default)
    {
        if (_runtime is null || !_runtime.Result.IsReady)
        {
            return false;
        }

        try
        {
            await _runtime.CreateBookAsync(title, cancellationToken).ConfigureAwait(false);
            await RefreshBooksAsync(cancellationToken).ConfigureAwait(false);
            return true;
        }
        catch (Exception ex) when (ex is ReadOnlyHostException or CoreOperationException or SidecarException or OperationCanceledException)
        {
            return false;
        }
    }

    /// <summary>
    /// V11R-A-1 (audit P-01, contract §5.1): creates one chapter through the Core
    /// <c>CreateChapter</c> command (protocol minor 8, C037). The typing layer is
    /// <see cref="HostRuntime.CreateChapterAsync"/>: the wire payload is exactly
    /// <c>{"book_id", "title"}</c> and the result is <c>{chapter_id, title, chapter_number,
    /// sort_order}</c> — verified against <c>src/bootstrap/core_service.py</c>
    /// (<c>handle_create_chapter</c> + <c>_CREATE_FIELDS</c> + <c>_create_validation_details</c>).
    /// Refusals never throw into the UI: they return null and publish the typed code through
    /// <see cref="HostViewSnapshot.LastError"/>. Title semantics stay with the Core (blank title →
    /// INVALID_REQUEST, duplicates allowed, no length limit); only an empty book id is rejected
    /// locally before any wire frame is sent.
    /// </summary>
    public async Task<ChapterSummary?> CreateChapterAsync(
        string bookId,
        string title,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(bookId))
        {
            SetLastError("INVALID_REQUEST");
            return null;
        }

        if (cancellationToken.IsCancellationRequested)
        {
            SetLastError("CANCELLED");
            return null;
        }

        if (_runtime is null || !_runtime.Result.IsReady)
        {
            SetLastError("HOST_NOT_READY");
            return null;
        }

        try
        {
            var chapter = await _runtime.CreateChapterAsync(bookId, title, cancellationToken).ConfigureAwait(false);
            // REALUSE-DATA-SAFETY-3 AC3: a new chapter invalidates the cached list for that book.
            lock (_chapterCacheLock)
            {
                _chapterCache.Remove(bookId);
            }
            SetLastError(null);
            return chapter;
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            // Core errors keep their typed code (INVALID_REQUEST / TARGET_NOT_FOUND / ...);
            // read-only, transport and cancellation failures map exactly like the rest of the
            // service layer (ErrorCodeOf), so nothing is silently swallowed.
            SetLastError(ErrorCodeOf(ex));
            return null;
        }
    }

    public async Task<ReaderBookData?> LoadReaderBookAsync(
        string? bookId = null,
        string? chapterId = null,
        CancellationToken cancellationToken = default)
    {
        if (_runtime is null || !_runtime.Result.IsReady)
        {
            return null;
        }

        var runtime = _runtime;
        try
        {
            // REALUSE-DATA-SAFETY-3 AC3 (audit MA-08): the shelf already lives in the snapshot from
            // startup; listing it again here was the third ListBooks of one launch.
            //
            // Review r1 M1: reuse is only safe while the snapshot can answer the question. If the
            // caller asked for a specific book that the snapshot does not contain (it was imported or
            // restored after startup, or a different shell wrote it), reusing the stale shelf used to
            // fall through to `book ??= first book`, silently opening a DIFFERENT book — a far worse
            // outcome than one extra read. A cold/insufficient snapshot therefore re-reads.
            var books = _snapshot.Books;
            var askedForMissingBook = !string.IsNullOrWhiteSpace(bookId)
                && !books.Any(candidate => string.Equals(candidate.BookId, bookId, StringComparison.Ordinal));
            if (books.Count == 0 || askedForMissingBook)
            {
                books = await runtime.ListBooksAsync(cancellationToken).ConfigureAwait(false);
            }

            BookSummary? book = null;
            if (!string.IsNullOrWhiteSpace(bookId))
            {
                book = books.FirstOrDefault(candidate => string.Equals(candidate.BookId, bookId, StringComparison.Ordinal));
                if (book is null)
                {
                    // An explicitly requested book that does not exist is a refusal, never a silent
                    // substitution with some other book.
                    return null;
                }
            }

            book ??= books.FirstOrDefault(candidate => (candidate.PageCount ?? 0) > 0) ?? books.FirstOrDefault();
            if (book is null)
            {
                return null;
            }

            var chapters = await ListChaptersAsync(book.BookId, cancellationToken).ConfigureAwait(false);
            if (chapters.Count == 0)
            {
                return null;
            }

            // CHAPTER-SELECTOR-1: an explicit chapter wins; otherwise the first chapter is the
            // reader's previous behaviour (projection order is the user's sort order).
            var chapter = string.IsNullOrWhiteSpace(chapterId)
                ? chapters[0]
                : chapters.FirstOrDefault(candidate => string.Equals(candidate.ChapterId, chapterId, StringComparison.Ordinal))
                  ?? chapters[0];

            // READER-PROGRESS-1 AC1: resume so the Core echoes the persisted page for
            // (book, chapter, mode); the projection read never mutates saved progress.
            var projection = await runtime
                .GetReaderProjectionAsync(chapter.ChapterId, ReaderStartPosition.Resume, cancellationToken)
                .ConfigureAwait(false);
            if (projection.Pages.Count == 0)
            {
                return null;
            }

            return ReaderBookData.FromProjection(
                book,
                chapter,
                projection,
                (pageId, token) => LoadPageBytesAsync(runtime, pageId, token));
        }
        catch (Exception ex) when (
            ex is CoreOperationException or SidecarException or BridgeException or OperationCanceledException or IOException)
        {
            return null;
        }
    }

    /// <summary>
    /// READER-PROGRESS-1: persist one reading position. Typed degradation only — nothing is thrown
    /// into the UI: no Core = NotReady, parity not reached = ReadOnly, Core rejection = Failed(code).
    /// </summary>
    public async Task<ReaderProgressSaveResult> SaveReadingProgressAsync(
        string chapterId,
        string pageId,
        string mode = "original",
        double? scrollOffsetY = null,
        double elapsedSecondsDelta = 0,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(chapterId) || string.IsNullOrWhiteSpace(pageId))
        {
            return ReaderProgressSaveResult.Failed("INVALID_REQUEST");
        }

        if (_runtime is null || !_runtime.Result.IsReady)
        {
            return ReaderProgressSaveResult.NotReady();
        }

        var runtime = _runtime;
        try
        {
            var snapshot = await runtime
                .SaveReadingProgressAsync(
                    chapterId,
                    mode,
                    pageId,
                    scrollOffsetY,
                    elapsedSecondsDelta > 0 ? elapsedSecondsDelta : null,
                    cancellationToken)
                .ConfigureAwait(false);
            return ReaderProgressSaveResult.Saved(snapshot.ProgressPercent, snapshot.LastPageId);
        }
        catch (ReadOnlyHostException)
        {
            return ReaderProgressSaveResult.ReadOnly();
        }
        catch (CoreOperationException ex)
        {
            return ReaderProgressSaveResult.Failed(ex.Code);
        }
        catch (Exception ex) when (
            ex is SidecarException or BridgeException or IOException or InvalidOperationException or OperationCanceledException)
        {
            return ReaderProgressSaveResult.Failed(
                ex is SidecarException sidecar ? sidecar.Code.ToString() : "READER_PROGRESS_UNAVAILABLE");
        }
    }

    private static async Task<byte[]?> LoadPageBytesAsync(HostRuntime runtime, string pageId, CancellationToken token) =>
        await runtime.ReadPageImageAsync(pageId, token).ConfigureAwait(false);

    /// <summary>
    /// CHAPTER-SELECTOR-1 AC1: read-only chapter list for the reader's selector. Degrades to an empty
    /// list (selector hidden, single-chapter behaviour) when the Host/Core is unavailable.
    /// </summary>
    public async Task<IReadOnlyList<ChapterSummary>> ListChaptersAsync(
        string bookId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(bookId) || _runtime is null || !_runtime.Result.IsReady)
        {
            return Array.Empty<ChapterSummary>();
        }

        // REALUSE-DATA-SAFETY-3 AC3 (audit MA-08): the Library lists chapters for the selected book
        // and the reader listed the same book again a moment later. One read per book per session is
        // enough; CreateChapterAsync invalidates the entry, and a failure never caches.
        lock (_chapterCacheLock)
        {
            if (_chapterCache.TryGetValue(bookId, out var cached))
            {
                return cached;
            }
        }

        var runtime = _runtime;
        try
        {
            var chapters = await runtime.ListChaptersAsync(bookId, cancellationToken).ConfigureAwait(false);
            lock (_chapterCacheLock)
            {
                _chapterCache[bookId] = chapters;
            }

            return chapters;
        }
        catch (Exception ex) when (
            ex is CoreOperationException or SidecarException or BridgeException or OperationCanceledException or IOException)
        {
            return Array.Empty<ChapterSummary>();
        }
    }

    // ---------------------------------------------------------------------------------------
    // READER-WORKBENCH-1 AC1/AC2: single-page workbench region data. Reads degrade to empty/null;
    // writes return typed outcomes and never throw into the UI.
    // ---------------------------------------------------------------------------------------

    /// <summary>AC1: ordered pages of one chapter; empty when the Host/Core is unavailable.</summary>
    public async Task<IReadOnlyList<ChapterPageSummary>> ListChapterPagesAsync(
        string chapterId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(chapterId) || _runtime is null || !_runtime.Result.IsReady)
        {
            return Array.Empty<ChapterPageSummary>();
        }

        var runtime = _runtime;
        try
        {
            return await runtime.ListChapterPagesAsync(chapterId, cancellationToken).ConfigureAwait(false);
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            return Array.Empty<ChapterPageSummary>();
        }
    }

    /// <summary>AC1: live regions + page pixel extent; null when the Host/Core is unavailable.</summary>
    public async Task<RegionPageProjection?> LoadPageRegionsAsync(
        string pageId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(pageId) || _runtime is null || !_runtime.Result.IsReady)
        {
            return null;
        }

        var runtime = _runtime;
        try
        {
            return await runtime.ListRegionsAsync(pageId, cancellationToken).ConfigureAwait(false);
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            return null;
        }
    }

    /// <summary>AC1: region revision history; null when the Host/Core is unavailable.</summary>
    public async Task<RegionRevisionHistory?> LoadRegionRevisionsAsync(
        string regionId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(regionId) || _runtime is null || !_runtime.Result.IsReady)
        {
            return null;
        }

        var runtime = _runtime;
        try
        {
            return await runtime.ListRegionRevisionsAsync(regionId, cancellationToken).ConfigureAwait(false);
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            return null;
        }
    }

    /// <summary>AC1: page image bytes through the Host resource channel; null when unavailable.</summary>
    public async Task<byte[]?> ReadPageImageAsync(
        string pageId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(pageId) || _runtime is null || !_runtime.Result.IsReady)
        {
            return null;
        }

        var runtime = _runtime;
        try
        {
            return await runtime.ReadPageImageAsync(pageId, cancellationToken).ConfigureAwait(false);
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            return null;
        }
    }

    /// <summary>AC2: retype one region with the caller's read revision as the optimistic guard.</summary>
    public async Task<RegionOperationResult> SetRegionTypeAsync(
        string regionId,
        string newRegionType,
        int expectedRevision,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(regionId) || string.IsNullOrWhiteSpace(newRegionType) || expectedRevision <= 0)
        {
            return RegionOperationResult.Failed("INVALID_REQUEST", "region_id / new_region_type / expected_revision 无效");
        }

        if (_runtime is null || !_runtime.Result.IsReady)
        {
            return RegionOperationResult.NotReady();
        }

        var runtime = _runtime;
        try
        {
            var snapshot = await runtime
                .SetRegionTypeAsync(regionId, newRegionType, expectedRevision, cancellationToken)
                .ConfigureAwait(false);
            return RegionOperationResult.Success(snapshot, $"类型已更新为 {snapshot.RegionType}（revision {snapshot.RevisionNo}）");
        }
        catch (ReadOnlyHostException)
        {
            return RegionOperationResult.ReadOnly();
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            return RegionOperationResult.Failed(ErrorCodeOf(ex), UserMessageOf(ex));
        }
    }

    /// <summary>AC2: restore one region revision into a new revision.</summary>
    public async Task<RegionOperationResult> RestoreRegionRevisionAsync(
        string regionId,
        int revisionNo,
        int expectedRevision,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(regionId) || revisionNo <= 0 || expectedRevision <= 0)
        {
            return RegionOperationResult.Failed("INVALID_REQUEST", "region_id / revision_no / expected_revision 无效");
        }

        if (_runtime is null || !_runtime.Result.IsReady)
        {
            return RegionOperationResult.NotReady();
        }

        var runtime = _runtime;
        try
        {
            var snapshot = await runtime
                .RestoreRegionRevisionAsync(regionId, revisionNo, expectedRevision, cancellationToken)
                .ConfigureAwait(false);
            return RegionOperationResult.Success(
                snapshot,
                $"已恢复 revision {revisionNo} → revision {snapshot.RevisionNo}（{snapshot.RegionType}）");
        }
        catch (ReadOnlyHostException)
        {
            return RegionOperationResult.ReadOnly();
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            return RegionOperationResult.Failed(ErrorCodeOf(ex), UserMessageOf(ex));
        }
    }

    /// <summary>AC2: manual page rerender with a typed outcome (artifact/revision/preview).</summary>
    public async Task<PageRerenderOutcome> RerenderPageAsync(
        string pageId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(pageId))
        {
            return PageRerenderOutcome.Failed("INVALID_REQUEST", "page_id 无效");
        }

        if (_runtime is null || !_runtime.Result.IsReady)
        {
            return PageRerenderOutcome.NotReady();
        }

        var runtime = _runtime;
        try
        {
            var result = await runtime.RerenderPageAsync(pageId, cancellationToken).ConfigureAwait(false);
            var preview = !string.IsNullOrEmpty(result.PreviewResourceId) ? "预览已发布" : "预览不可用";
            return PageRerenderOutcome.Success(
                result,
                $"已重渲染 revision {result.RevisionNo}（{result.Reports.Count} 区域，{preview}）");
        }
        catch (ReadOnlyHostException)
        {
            return PageRerenderOutcome.ReadOnly();
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            return PageRerenderOutcome.Failed(ErrorCodeOf(ex), UserMessageOf(ex));
        }
    }

    /// <summary>
    /// CREDENTIAL-UI-1 AC1/AC2: provider + proxy targets with the Core <c>credential_state</c>. Reads the
    /// two existing P15 profile-list commands (no new Host contract); an empty list means "no profiles or
    /// Host not ready". Never reads or returns a secret.
    /// </summary>
    public async Task<IReadOnlyList<CredentialTargetOption>> ListCredentialTargetsAsync(        CancellationToken cancellationToken = default)
    {
        if (_runtime is null || !_runtime.Result.IsReady || _runtime.Commands is not { } commands)
        {
            return Array.Empty<CredentialTargetOption>();
        }

        var options = new List<CredentialTargetOption>();
        await CollectProfilesAsync(commands, "settings_provider_profiles_list", CredentialKinds.ProviderApi, "profile_id");
        await CollectProfilesAsync(commands, "settings_network_profiles_list", CredentialKinds.ProxyAuth, "network_profile_id");
        return options;

        async Task CollectProfilesAsync(
            NewManga.CoreClient.Commands.HostCommandDispatcher dispatcher,
            string command,
            string kind,
            string ownerProperty)
        {
            try
            {
                var response = await dispatcher.InvokeAsync(command, default, cancellationToken).ConfigureAwait(false);
                if (response.Value.ValueKind != System.Text.Json.JsonValueKind.Object ||
                    !response.Value.TryGetProperty("profiles", out var profiles) ||
                    profiles.ValueKind != System.Text.Json.JsonValueKind.Array)
                {
                    return;
                }

                foreach (var profile in profiles.EnumerateArray())
                {
                    if (profile.ValueKind != System.Text.Json.JsonValueKind.Object)
                    {
                        continue;
                    }

                    var owner = ReadString(profile, ownerProperty);
                    if (string.IsNullOrEmpty(owner))
                    {
                        continue;
                    }

                    var display = FirstNonEmpty(
                        ReadString(profile, "display_name"),
                        ReadString(profile, "name"),
                        ReadString(profile, "label"),
                        owner);
                    var state = ReadString(profile, "credential_state") ?? "missing";
                    options.Add(new CredentialTargetOption(kind, owner, display, state));
                }
            }
            catch (Exception ex) when (
                ex is CoreOperationException or SidecarException or BridgeException or IOException or
                    InvalidOperationException or OperationCanceledException)
            {
                // Degrade: the settings block renders its own "unavailable" hint.
            }
        }
    }

    /// <summary>
    /// CREDENTIAL-UI-1 AC1: store one credential through the Host-local <c>credential_put</c> command.
    /// The secret goes only into the transient dispatcher payload; nothing is logged or retained here.
    /// </summary>
    public async Task<CredentialOperationResult> PutCredentialAsync(
        string kind,
        string ownerId,
        string intent,
        string secret,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(secret))
        {
            return CredentialResultMapper.MapCode("INVALID_ARGUMENTS", "secret must not be empty");
        }

        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            return CredentialOperationResult.NotReady();
        }

        try
        {
            await commands
                .InvokeAsync("credential_put", CredentialCommandPayload.BuildPut(kind, ownerId, intent, secret), cancellationToken)
                .ConfigureAwait(false);
            return CredentialOperationResult.Configured();
        }
        catch (Exception ex) when (ex is not OutOfMemoryException)
        {
            return CredentialResultMapper.MapException(ex);
        }
    }

    /// <summary>CREDENTIAL-UI-1 AC1: clear one credential through <c>credential_clear</c>.</summary>
    public async Task<CredentialOperationResult> ClearCredentialAsync(
        string kind,
        string ownerId,
        CancellationToken cancellationToken = default)
    {
        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            return CredentialOperationResult.NotReady();
        }

        try
        {
            await commands
                .InvokeAsync("credential_clear", CredentialCommandPayload.BuildClear(kind, ownerId), cancellationToken)
                .ConfigureAwait(false);
            return CredentialOperationResult.Cleared();
        }
        catch (Exception ex) when (ex is not OutOfMemoryException)
        {
            return CredentialResultMapper.MapException(ex);
        }
    }

    private static string? ReadString(System.Text.Json.JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == System.Text.Json.JsonValueKind.String
            ? value.GetString()
            : null;

    private static string FirstNonEmpty(params string?[] candidates) =>
        candidates.FirstOrDefault(candidate => !string.IsNullOrWhiteSpace(candidate)) ?? string.Empty;

    // -------------------------------------------------------------------------------------
    // SETTINGS-PROFILE-UI-1: P15 provider / network profile management + binding slots.
    // Payloads are built by SettingsProfilePayload; every failure is mapped to a typed result.
    // -------------------------------------------------------------------------------------

    public async Task<IReadOnlyList<ProviderProfileInfo>> ListProviderProfilesAsync(
        CancellationToken cancellationToken = default)
    {
        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            return Array.Empty<ProviderProfileInfo>();
        }

        try
        {
            var response = await commands
                .InvokeAsync("settings_provider_profiles_list", default, cancellationToken)
                .ConfigureAwait(false);
            return ParseProviderProfiles(response.Value);
        }
        catch (Exception ex) when (
            ex is CoreOperationException or SidecarException or BridgeException or IOException or
                InvalidOperationException or OperationCanceledException)
        {
            return Array.Empty<ProviderProfileInfo>();
        }
    }

    public async Task<SettingsProfileResult> SaveProviderProfileAsync(
        string? profileId,
        ProviderProfileDraft draft,
        CancellationToken cancellationToken = default)
    {
        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            return SettingsProfileResult.NotReady();
        }

        try
        {
            var create = string.IsNullOrEmpty(profileId);
            var payload = create
                ? SettingsProfilePayload.ProviderCreate(draft)
                : SettingsProfilePayload.ProviderUpdate(profileId!, draft);
            await commands
                .InvokeAsync(
                    create ? "settings_provider_profiles_create" : "settings_provider_profiles_update",
                    payload,
                    cancellationToken)
                .ConfigureAwait(false);
            return SettingsProfileResult.Success(create ? "provider profile 已创建" : "provider profile 已更新");
        }
        catch (Exception ex) when (ex is not OutOfMemoryException)
        {
            return SettingsProfileResultMapper.MapException(ex);
        }
    }

    public async Task<SettingsProfileResult> DeleteProviderProfileAsync(
        string profileId,
        CancellationToken cancellationToken = default)
    {
        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            return SettingsProfileResult.NotReady();
        }

        try
        {
            await commands
                .InvokeAsync("settings_provider_profiles_delete", SettingsProfilePayload.ProviderDelete(profileId), cancellationToken)
                .ConfigureAwait(false);
            return SettingsProfileResult.Success("provider profile 已删除");
        }
        catch (Exception ex) when (ex is not OutOfMemoryException)
        {
            return SettingsProfileResultMapper.MapException(ex);
        }
    }

    public async Task<IReadOnlyList<NetworkProfileInfo>> ListNetworkProfilesAsync(
        CancellationToken cancellationToken = default)
    {
        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            return Array.Empty<NetworkProfileInfo>();
        }

        try
        {
            var response = await commands
                .InvokeAsync("settings_network_profiles_list", default, cancellationToken)
                .ConfigureAwait(false);
            return ParseNetworkProfiles(response.Value);
        }
        catch (Exception ex) when (
            ex is CoreOperationException or SidecarException or BridgeException or IOException or
                InvalidOperationException or OperationCanceledException)
        {
            return Array.Empty<NetworkProfileInfo>();
        }
    }

    public async Task<SettingsProfileResult> SaveNetworkProfileAsync(
        string? networkProfileId,
        NetworkProfileDraft draft,
        CancellationToken cancellationToken = default)
    {
        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            return SettingsProfileResult.NotReady();
        }

        try
        {
            var create = string.IsNullOrEmpty(networkProfileId);
            var payload = create
                ? SettingsProfilePayload.NetworkCreate(draft)
                : SettingsProfilePayload.NetworkUpdate(networkProfileId!, draft);
            await commands
                .InvokeAsync(
                    create ? "settings_network_profiles_create" : "settings_network_profiles_update",
                    payload,
                    cancellationToken)
                .ConfigureAwait(false);
            return SettingsProfileResult.Success(create ? "network profile 已创建" : "network profile 已更新");
        }
        catch (Exception ex) when (ex is not OutOfMemoryException)
        {
            return SettingsProfileResultMapper.MapException(ex);
        }
    }

    public async Task<SettingsProfileResult> DeleteNetworkProfileAsync(
        string networkProfileId,
        CancellationToken cancellationToken = default)
    {
        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            return SettingsProfileResult.NotReady();
        }

        try
        {
            await commands
                .InvokeAsync(
                    "settings_network_profiles_delete",
                    SettingsProfilePayload.NetworkDelete(networkProfileId),
                    cancellationToken)
                .ConfigureAwait(false);
            return SettingsProfileResult.Success("network profile 已删除");
        }
        catch (Exception ex) when (ex is not OutOfMemoryException)
        {
            return SettingsProfileResultMapper.MapException(ex);
        }
    }

    public async Task<SettingsProfileResult> SetNetworkDefaultAsync(
        string? networkProfileId,
        CancellationToken cancellationToken = default)
    {
        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            return SettingsProfileResult.NotReady();
        }

        try
        {
            if (string.IsNullOrEmpty(networkProfileId))
            {
                await commands
                    .InvokeAsync("settings_network_profile_default_clear", SettingsProfilePayload.Empty(), cancellationToken)
                    .ConfigureAwait(false);
                return SettingsProfileResult.Success("默认 network profile 已清除");
            }

            await commands
                .InvokeAsync(
                    "settings_network_profile_default_set",
                    SettingsProfilePayload.NetworkDefaultSet(networkProfileId),
                    cancellationToken)
                .ConfigureAwait(false);
            return SettingsProfileResult.Success("默认 network profile 已设置");
        }
        catch (Exception ex) when (ex is not OutOfMemoryException)
        {
            return SettingsProfileResultMapper.MapException(ex);
        }
    }

    public async Task<NetworkTestInfo?> TestNetworkProfileAsync(
        string networkProfileId,
        string providerProfileId,
        CancellationToken cancellationToken = default)
    {
        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady ||
            string.IsNullOrWhiteSpace(networkProfileId) || string.IsNullOrWhiteSpace(providerProfileId))
        {
            return null;
        }

        try
        {
            var response = await commands
                .InvokeAsync(
                    "settings_network_profiles_test",
                    SettingsProfilePayload.NetworkTest(networkProfileId, providerProfileId),
                    cancellationToken)
                .ConfigureAwait(false);
            var value = response.Value;
            if (value.ValueKind != System.Text.Json.JsonValueKind.Object)
            {
                return null;
            }

            var stages = new List<NetworkTestStageInfo>();
            if (value.TryGetProperty("stages", out var stageArray) &&
                stageArray.ValueKind == System.Text.Json.JsonValueKind.Array)
            {
                foreach (var stage in stageArray.EnumerateArray())
                {
                    if (stage.ValueKind != System.Text.Json.JsonValueKind.Object)
                    {
                        continue;
                    }

                    stages.Add(new NetworkTestStageInfo(
                        ReadString(stage, "stage") ?? "?",
                        ReadString(stage, "status") ?? "?",
                        ReadString(stage, "reason"),
                        stage.TryGetProperty("duration_ms", out var duration) &&
                        duration.ValueKind == System.Text.Json.JsonValueKind.Number &&
                        duration.TryGetInt32(out var ms)
                            ? ms
                            : null));
                }
            }

            return new NetworkTestInfo(
                ReadString(value, "status") ?? "unknown",
                ReadString(value, "failed_stage"),
                ReadBool(value, "direct_fallback_used", false),
                stages);
        }
        catch (Exception ex) when (
            ex is CoreOperationException or SidecarException or BridgeException or IOException or
                InvalidOperationException or OperationCanceledException or HostCommandInvalidArgumentsException)
        {
            return null;
        }
    }

    public async Task<NetworkResolveInfo?> ResolveNetworkProfileAsync(
        string? providerProfileId,
        CancellationToken cancellationToken = default)
    {
        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            return null;
        }

        try
        {
            var response = await commands
                .InvokeAsync(
                    "settings_network_profile_resolve",
                    SettingsProfilePayload.NetworkResolve(providerProfileId),
                    cancellationToken)
                .ConfigureAwait(false);
            var value = response.Value;
            if (value.ValueKind != System.Text.Json.JsonValueKind.Object)
            {
                return null;
            }

            return new NetworkResolveInfo(
                ReadString(value, "network_profile_id"),
                ReadString(value, "mode") ?? "?",
                ReadString(value, "source") ?? "?");
        }
        catch (Exception ex) when (
            ex is CoreOperationException or SidecarException or BridgeException or IOException or
                InvalidOperationException or OperationCanceledException)
        {
            return null;
        }
    }

    public async Task<SettingsProfileResult> SetProviderBindingAsync(
        ProfileBindingScope scope,
        string capability,
        string profileId,
        CancellationToken cancellationToken = default)
    {
        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            return SettingsProfileResult.NotReady();
        }

        try
        {
            await commands
                .InvokeAsync(
                    "settings_provider_bindings_set",
                    SettingsProfilePayload.BindingSet(scope, capability, profileId),
                    cancellationToken)
                .ConfigureAwait(false);
            return SettingsProfileResult.Success($"绑定已保存：{capability} → {profileId}");
        }
        catch (Exception ex) when (ex is not OutOfMemoryException)
        {
            return SettingsProfileResultMapper.MapException(ex);
        }
    }

    public async Task<SettingsProfileResult> ClearProviderBindingAsync(
        ProfileBindingScope scope,
        string capability,
        CancellationToken cancellationToken = default)
    {
        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            return SettingsProfileResult.NotReady();
        }

        try
        {
            await commands
                .InvokeAsync(
                    "settings_provider_bindings_clear",
                    SettingsProfilePayload.BindingClear(scope, capability),
                    cancellationToken)
                .ConfigureAwait(false);
            return SettingsProfileResult.Success($"绑定已清除：{capability}");
        }
        catch (Exception ex) when (ex is not OutOfMemoryException)
        {
            return SettingsProfileResultMapper.MapException(ex);
        }
    }

    public async Task<ProviderBindingResult?> ResolveProviderBindingAsync(
        string capability,
        CancellationToken cancellationToken = default)
    {
        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            return null;
        }

        try
        {
            var response = await commands
                .InvokeAsync(
                    "settings_provider_bindings_resolve",
                    SettingsProfilePayload.BindingResolve(capability),
                    cancellationToken)
                .ConfigureAwait(false);
            var value = response.Value;
            if (value.ValueKind != System.Text.Json.JsonValueKind.Object)
            {
                return null;
            }

            var source = value.TryGetProperty("source", out var sourceElement) &&
                         sourceElement.ValueKind != System.Text.Json.JsonValueKind.Null
                ? sourceElement.GetRawText()
                : null;
            return new ProviderBindingResult(false, ReadString(value, "profile_id"), capability, source);
        }
        catch (Exception ex) when (
            ex is CoreOperationException or SidecarException or BridgeException or IOException or
                InvalidOperationException or OperationCanceledException)
        {
            return null;
        }
    }

    private static IReadOnlyList<ProviderProfileInfo> ParseProviderProfiles(System.Text.Json.JsonElement value)
    {
        var providers = new List<ProviderProfileInfo>();
        if (value.ValueKind != System.Text.Json.JsonValueKind.Object ||
            !value.TryGetProperty("profiles", out var profiles) ||
            profiles.ValueKind != System.Text.Json.JsonValueKind.Array)
        {
            return providers;
        }

        foreach (var profile in profiles.EnumerateArray())
        {
            if (profile.ValueKind != System.Text.Json.JsonValueKind.Object)
            {
                continue;
            }

            var profileId = ReadString(profile, "profile_id");
            if (string.IsNullOrEmpty(profileId))
            {
                continue;
            }

            var capabilities = new List<string>();
            if (profile.TryGetProperty("capabilities", out var caps) &&
                caps.ValueKind == System.Text.Json.JsonValueKind.Array)
            {
                foreach (var capability in caps.EnumerateArray())
                {
                    if (capability.ValueKind == System.Text.Json.JsonValueKind.String)
                    {
                        capabilities.Add(capability.GetString()!);
                    }
                }
            }

            providers.Add(new ProviderProfileInfo(
                profileId,
                ReadString(profile, "provider_id") ?? string.Empty,
                ReadString(profile, "display_name") ?? profileId,
                capabilities,
                ReadString(profile, "endpoint") ?? string.Empty,
                ReadString(profile, "model") ?? string.Empty,
                ReadString(profile, "network_profile_id"),
                ReadBool(profile, "enabled", true),
                ReadString(profile, "credential_state") ?? "missing"));
        }

        return providers;
    }

    private static IReadOnlyList<NetworkProfileInfo> ParseNetworkProfiles(System.Text.Json.JsonElement value)
    {
        var networks = new List<NetworkProfileInfo>();
        if (value.ValueKind != System.Text.Json.JsonValueKind.Object ||
            !value.TryGetProperty("profiles", out var profiles) ||
            profiles.ValueKind != System.Text.Json.JsonValueKind.Array)
        {
            return networks;
        }

        foreach (var profile in profiles.EnumerateArray())
        {
            if (profile.ValueKind != System.Text.Json.JsonValueKind.Object)
            {
                continue;
            }

            var profileId = ReadString(profile, "network_profile_id");
            if (string.IsNullOrEmpty(profileId))
            {
                continue;
            }

            networks.Add(new NetworkProfileInfo(
                profileId,
                ReadString(profile, "display_name") ?? profileId,
                ReadString(profile, "mode") ?? NetworkModes.Direct,
                ReadString(profile, "proxy_endpoint"),
                ReadBool(profile, "verify_tls", true),
                ReadString(profile, "tls_verification_state") ?? "enabled",
                ReadBool(profile, "allow_proxy_failure_direct_fallback", false),
                ReadString(profile, "credential_state") ?? "missing"));
        }

        return networks;
    }

    private static bool ReadBool(System.Text.Json.JsonElement element, string property, bool fallback) =>
        element.TryGetProperty(property, out var value) &&
        value.ValueKind is System.Text.Json.JsonValueKind.True or System.Text.Json.JsonValueKind.False
            ? value.GetBoolean()
            : fallback;

    // ---------------------------------------------------------------------------------------
    // IMPORT-EXPORT-UI-1: import/export entries. Import uses the Host grant chain
    // (HostGrantCoordinator.ImportAsync: host session -> RegisterImportSource -> ImportPages);
    // export uses the Host grant + StartExport chain (EXPORT-E2E-CLOSE-1 verified), while
    // snapshot/history/cancel are the Host command faces the UI polls.
    // ---------------------------------------------------------------------------------------

    public string ExportDirectorySuggestion => Path.Combine(_options.DataRoot, "exports");

    public async Task<ImportOutcome> ImportFilesAsync(
        string chapterId,
        IReadOnlyList<string> paths,
        string duplicatePolicy = "skip",
        CancellationToken cancellationToken = default) =>
        await ImportAsync(chapterId, paths, "file", duplicatePolicy, cancellationToken).ConfigureAwait(false);

    public async Task<ImportOutcome> ImportFolderAsync(
        string chapterId,
        string folderPath,
        string duplicatePolicy = "skip",
        CancellationToken cancellationToken = default) =>
        await ImportAsync(chapterId, new[] { folderPath }, "directory", duplicatePolicy, cancellationToken)
            .ConfigureAwait(false);

    private async Task<ImportOutcome> ImportAsync(
        string chapterId,
        IReadOnlyList<string> paths,
        string sourceKind,
        string duplicatePolicy,
        CancellationToken cancellationToken)
    {
        if (string.IsNullOrWhiteSpace(chapterId))
        {
            return ImportOutcome.Failed("INVALID_ARGUMENTS", "导入需要先选择目标章节");
        }

        if (paths.Count == 0)
        {
            return ImportOutcome.Failed("INVALID_ARGUMENTS", "没有选择要导入的文件或文件夹");
        }

        if (_runtime is null || !_runtime.Result.IsReady || _runtime.Grants is not { } grants)
        {
            return ImportOutcome.NotReady();
        }

        try
        {
            var projection = await grants
                .ImportAsync(chapterId, paths, sourceKind, duplicatePolicy, cancellationToken)
                .ConfigureAwait(false);
            var imported = ReadInt(projection, "imported_files") ?? 0;
            var skipped = ReadInt(projection, "skipped_files") ?? 0;
            return ImportOutcome.Success(imported, skipped);
        }
        catch (ReadOnlyHostException)
        {
            return ImportOutcome.Failed("HOST_READ_ONLY", "Host 处于只读模式（parity 未达成），导入被拒绝");
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            var code = ErrorCodeOf(ex);
            return ImportOutcome.Failed(code, $"导入失败：{UserMessageOf(ex)}");
        }
    }

    // ---------------------------------------------------------------------------------------
    // FEA-09-UI-1: referenced-source import face (ISourceImportController — kept OUTSIDE the
    // frozen C-07 IHostController inventory; C-16 v1.1 §1/§4). All four entries delegate
    // to the production SourceImportCoordinator (real HostCommandDispatcher routing + real
    // SourceReadCoordinator grants); refusals are typed outcomes, never thrown into the UI, and
    // the plaintext password exists only inside one Start call (C-16 v1.1 §3 secret_ref).
    // ---------------------------------------------------------------------------------------

    private SourceImportCoordinator? _sourceImports;
    private HostRuntime? _sourceImportsRuntime;

    /// <summary>
    /// The coordinator is cached per runtime instance so the one-shot password context of a
    /// running import survives the plan→start→receipt sequence; a restart replaces it (the
    /// stale context is cleaned best-effort — secrets expire on their own regardless).
    /// </summary>
    private SourceImportCoordinator? SourceImports
    {
        get
        {
            var runtime = _runtime;
            if (runtime is null || !runtime.Result.IsReady ||
                runtime.Commands is not { } commands || runtime.Sources is not { } sources)
            {
                return null;
            }

            if (!ReferenceEquals(_sourceImportsRuntime, runtime))
            {
                var stale = _sourceImports;
                _sourceImports = null;
                _sourceImportsRuntime = runtime;
                if (stale is not null)
                {
                    _ = stale.DisposeAsync();
                }
            }

            return _sourceImports ??= new SourceImportCoordinator(commands, sources, _options.DataRoot);
        }
    }

    public async Task<SourcePlanPreview?> PlanReferencedImportAsync(
        string chapterId,
        IReadOnlyList<ReferenceImportSource> sources,
        string duplicatePolicy = "skip",
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(chapterId) || sources.Count == 0)
        {
            SetLastError("INVALID_REQUEST");
            return null;
        }

        var imports = SourceImports;
        if (imports is null)
        {
            SetLastError("HOST_NOT_READY");
            return null;
        }

        if (!_runtime!.Policy.WritesAllowed)
        {
            SetLastError("HOST_READ_ONLY");
            return null;
        }

        try
        {
            var plan = await imports.PlanAsync(chapterId, sources, duplicatePolicy, cancellationToken).ConfigureAwait(false);
            SetLastError(plan is null ? "HOST_UNAVAILABLE" : null);
            return plan;
        }
        catch (Exception ex) when (ex is SourceAccessException or CoreOperationException or SidecarException or HostCommandInvalidArgumentsException or IOException or InvalidOperationException or OperationCanceledException)
        {
            SetLastError(ex is CoreOperationException core ? core.Code
                : ex is SourceAccessException source ? source.Message
                : ex is SidecarException sidecar ? sidecar.Code.ToString()
                : ex is HostCommandInvalidArgumentsException ? "INVALID_ARGUMENTS"
                : ex is OperationCanceledException ? "CANCELLED"
                : "HOST_UNAVAILABLE");
            return null;
        }
    }

    public async Task<SourceImportStartResult> StartReferencedImportAsync(
        SourcePlanPreview plan,
        string? password,
        CancellationToken cancellationToken = default)
    {
        if (plan is null)
        {
            return SourceImportStartResult.Failed("INVALID_REQUEST", "导入计划无效");
        }

        var imports = SourceImports;
        if (imports is null)
        {
            SetLastError("HOST_NOT_READY");
            return SourceImportStartResult.NotReady();
        }

        if (!_runtime!.Policy.WritesAllowed)
        {
            SetLastError("HOST_READ_ONLY");
            return SourceImportStartResult.ReadOnly();
        }

        var result = await imports.StartAsync(plan, password, cancellationToken).ConfigureAwait(false);
        SetLastError(result.Ok ? null : result.ErrorCode);
        return result;
    }

    public async Task<SourceImportReceipt?> GetReferencedImportReceiptAsync(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(operationId))
        {
            return null;
        }

        var imports = SourceImports;
        if (imports is null)
        {
            SetLastError("HOST_NOT_READY");
            return null;
        }

        try
        {
            var receipt = await imports.GetReceiptAsync(operationId, cancellationToken).ConfigureAwait(false);
            SetLastError(receipt is null ? "HOST_UNAVAILABLE" : null);
            return receipt;
        }
        catch (Exception ex) when (ex is SourceAccessException or CoreOperationException or SidecarException or IOException or InvalidOperationException or OperationCanceledException)
        {
            SetLastError(ex is CoreOperationException core ? core.Code
                : ex is SourceAccessException source ? source.Message
                : ex is SidecarException sidecar ? sidecar.Code.ToString()
                : ex is OperationCanceledException ? "CANCELLED"
                : "HOST_UNAVAILABLE");
            return null;
        }
    }

    public async Task<SourceImportCancelResult> CancelReferencedImportAsync(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(operationId))
        {
            return SourceImportCancelResult.Failed("INVALID_REQUEST");
        }

        var imports = SourceImports;
        if (imports is null)
        {
            SetLastError("HOST_NOT_READY");
            return SourceImportCancelResult.Failed("HOST_NOT_READY");
        }

        if (!_runtime!.Policy.WritesAllowed)
        {
            SetLastError("HOST_READ_ONLY");
            return SourceImportCancelResult.Failed("HOST_READ_ONLY");
        }

        var result = await imports.CancelAsync(operationId, cancellationToken).ConfigureAwait(false);
        if (!result.Ok)
        {
            SetLastError(result.ErrorCode);
        }

        return result;
    }

    public async Task<IReadOnlyList<string>> GetTranslatedPageIdsAsync(
        string chapterId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(chapterId) || _runtime is null || !_runtime.Result.IsReady)
        {
            return Array.Empty<string>();
        }

        if (_runtime.Commands is not { } commands)
        {
            return Array.Empty<string>();
        }

        try
        {
            var response = await commands.InvokeAsync(
                    "library_get_reader_projection",
                    ImportExportPayloads.ReaderProjectionTranslated(chapterId),
                    cancellationToken)
                .ConfigureAwait(false);
            var value = response.Value;
            if (value.ValueKind != System.Text.Json.JsonValueKind.Object ||
                !value.TryGetProperty("pages", out var pages) ||
                pages.ValueKind != System.Text.Json.JsonValueKind.Array)
            {
                return Array.Empty<string>();
            }

            var translated = new List<(int Order, string PageId)>();
            foreach (var page in pages.EnumerateArray())
            {
                if (page.ValueKind != System.Text.Json.JsonValueKind.Object)
                {
                    continue;
                }

                if (!page.TryGetProperty("translated", out var translatedInfo) ||
                    translatedInfo.ValueKind != System.Text.Json.JsonValueKind.Object)
                {
                    continue;
                }

                var revision = ReadString(translatedInfo, "artifact_revision_id");
                var pageId = ReadString(page, "page_id");
                if (string.IsNullOrWhiteSpace(revision) || string.IsNullOrWhiteSpace(pageId))
                {
                    continue;
                }

                translated.Add((ReadInt(page, "order") ?? translated.Count, pageId));
            }

            return translated.OrderBy(item => item.Order).Select(item => item.PageId).ToList();
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            return Array.Empty<string>();
        }
    }

    public async Task<ExportStartInfo?> StartExportAsync(
        string bookId,
        string chapterId,
        IReadOnlyList<string> orderedPageIds,
        string targetPath,
        string format = "zip",
        string? pdfContent = null,
        string? stalePolicy = null,
        CancellationToken cancellationToken = default)
    {
        // V11R-A-7: the Core accepts exactly abort | continue_existing (core_service.py:2854-2863,
        // HostIssuer.ValidateExportRequest mirrors it). Refuse anything else locally with a typed code
        // and zero frames; null/blank keeps the historical default abort.
        var effectiveStalePolicy = string.IsNullOrWhiteSpace(stalePolicy) ? "abort" : stalePolicy;
        if (effectiveStalePolicy is not ("abort" or "continue_existing"))
        {
            SetLastError("INVALID_REQUEST");
            return null;
        }

        if (string.IsNullOrWhiteSpace(bookId) || string.IsNullOrWhiteSpace(chapterId) ||
            orderedPageIds.Count == 0 || string.IsNullOrWhiteSpace(targetPath))
        {
            return null;
        }

        if (_runtime is null || !_runtime.Result.IsReady || _runtime.Grants is not { } grants)
        {
            return null;
        }

        // Export targets are confined to the Host-owned exports directory; the UI only offers paths
        // inside it and the Host re-validates (EXPORT_PATH_UNAVAILABLE otherwise).
        try
        {
            var directory = Path.GetDirectoryName(Path.GetFullPath(targetPath));
            if (!string.IsNullOrWhiteSpace(directory))
            {
                Directory.CreateDirectory(directory);
            }
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or ArgumentException)
        {
            return null;
        }

        try
        {
            var request = ImportExportPayloads.StartExportRequest(
                bookId, new[] { chapterId }, orderedPageIds, format,
                stalePolicy: effectiveStalePolicy, pdfContent: pdfContent);
            var started = await grants.StartExportAsync(request, targetPath, cancellationToken).ConfigureAwait(false);
            SetLastError(null);
            return ExportStartInfo.FromJson(started);
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            return null;
        }
    }

    public async Task<ExportSnapshotInfo?> GetExportSnapshotAsync(
        string exportId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(exportId))
        {
            return null;
        }

        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            return null;
        }

        try
        {
            var response = await commands
                .InvokeAsync("library_get_export_snapshot", ImportExportPayloads.ExportId(exportId), cancellationToken)
                .ConfigureAwait(false);
            return ExportSnapshotInfo.FromJson(response.Value);
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            return null;
        }
    }

    public async Task<IReadOnlyList<ExportHistoryEntry>> GetExportHistoryAsync(
        CancellationToken cancellationToken = default)
    {
        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            return Array.Empty<ExportHistoryEntry>();
        }

        try
        {
            var response = await commands.InvokeAsync("library_get_export_history", default, cancellationToken)
                .ConfigureAwait(false);
            if (response.Value.ValueKind != System.Text.Json.JsonValueKind.Object ||
                !response.Value.TryGetProperty("exports", out var exports) ||
                exports.ValueKind != System.Text.Json.JsonValueKind.Array)
            {
                return Array.Empty<ExportHistoryEntry>();
            }

            return exports.EnumerateArray()
                .Where(entry => entry.ValueKind == System.Text.Json.JsonValueKind.Object)
                .Select(ExportHistoryEntry.FromJson)
                .Where(entry => !string.IsNullOrWhiteSpace(entry.ExportId))
                .ToList();
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            return Array.Empty<ExportHistoryEntry>();
        }
    }

    public async Task<ExportSnapshotInfo?> CancelExportAsync(
        string exportId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(exportId))
        {
            return null;
        }

        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            return null;
        }

        try
        {
            var response = await commands
                .InvokeAsync("library_cancel_export", ImportExportPayloads.ExportId(exportId), cancellationToken)
                .ConfigureAwait(false);
            return ExportSnapshotInfo.FromJson(response.Value);
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            return null;
        }
    }

    public async Task<bool> RevealExportFolderAsync(
        string exportId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(exportId) || _runtime is null || !_runtime.Result.IsReady ||
            _runtime.Grants is not { } grants)
        {
            return false;
        }

        try
        {
            var result = await grants.RevealExportFolderAsync(exportId, cancellationToken).ConfigureAwait(false);
            return ReadBool(result, "revealed", false) || ReadBool(result, "opened", false);
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            return false;
        }
    }

    // ---------------------------------------------------------------------------------------
    // REALUSE-DATA-SAFETY-1 AC2: .nmbak backup packages (backup.list/create/delete/restore).
    // The Host data-root policy is enforced inside HostRuntime; refusals surface their typed code
    // through LastError and return null/false/empty rather than throwing into the UI.
    // ---------------------------------------------------------------------------------------

    public async Task<IReadOnlyList<BackupPackageInfo>> ListBackupsAsync(
        CancellationToken cancellationToken = default)
    {
        if (_runtime is null || !_runtime.Result.IsReady)
        {
            return Array.Empty<BackupPackageInfo>();
        }

        try
        {
            return await _runtime.ListBackupsAsync(cancellationToken).ConfigureAwait(false);
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            SetLastError(ErrorCodeOf(ex));
            return Array.Empty<BackupPackageInfo>();
        }
    }

    /// <summary>REALUSE-DATA-SAFETY-4 AC1: plugin inventory (read).</summary>
    public async Task<PluginListInfo> ListPluginsAsync(CancellationToken cancellationToken = default)
    {
        if (_runtime is null || !_runtime.Result.IsReady)
        {
            SetLastError("HOST_NOT_READY");
            return new PluginListInfo(false, Array.Empty<PluginInfo>());
        }

        try
        {
            return await _runtime.ListPluginsAsync(cancellationToken).ConfigureAwait(false);
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            SetLastError(ErrorCodeOf(ex));
            return new PluginListInfo(false, Array.Empty<PluginInfo>());
        }
    }

    public async Task<bool?> SetPluginsGlobalEnabledAsync(bool enabled, CancellationToken cancellationToken = default)
    {
        if (_runtime is null || !_runtime.Result.IsReady)
        {
            SetLastError("HOST_NOT_READY");
            return null;
        }

        if (!_runtime.Policy.WritesAllowed)
        {
            SetLastError("HOST_READ_ONLY");
            return null;
        }

        try
        {
            bool? value = await _runtime.SetPluginsGlobalEnabledAsync(enabled, cancellationToken).ConfigureAwait(false);
            SetLastError(null);
            return value;
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            SetLastError(ErrorCodeOf(ex));
            return null;
        }
    }

    public async Task<bool?> SetPluginEnabledAsync(
        string pluginId,
        bool enabled,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(pluginId))
        {
            SetLastError("INVALID_REQUEST");
            return null;
        }

        if (_runtime is null || !_runtime.Result.IsReady)
        {
            SetLastError("HOST_NOT_READY");
            return null;
        }

        if (!_runtime.Policy.WritesAllowed)
        {
            SetLastError("HOST_READ_ONLY");
            return null;
        }

        try
        {
            bool? value = await _runtime.SetPluginEnabledAsync(pluginId, enabled, cancellationToken).ConfigureAwait(false);
            SetLastError(null);
            return value;
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            SetLastError(ErrorCodeOf(ex));
            return null;
        }
    }

    /// <summary>
    /// REALUSE-DATA-SAFETY-4 AC1 (audit MA-06): the Console's cache section. The preview is a pure
    /// read; the run is a write and therefore obeys the same data-root policy as every other write.
    /// </summary>
    public async Task<CleanupPreviewInfo> GetCleanupPreviewAsync(CancellationToken cancellationToken = default)
    {
        if (_runtime is null || !_runtime.Result.IsReady)
        {
            SetLastError("HOST_NOT_READY");
            return new CleanupPreviewInfo(Array.Empty<CleanupTargetInfo>(), 0, 0);
        }

        try
        {
            return await _runtime.GetCleanupPreviewAsync(cancellationToken).ConfigureAwait(false);
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            SetLastError(ErrorCodeOf(ex));
            return new CleanupPreviewInfo(Array.Empty<CleanupTargetInfo>(), 0, 0);
        }
    }

    public async Task<CleanupOutcomeInfo?> RunCleanupAsync(CancellationToken cancellationToken = default)
    {
        if (_runtime is null || !_runtime.Result.IsReady)
        {
            SetLastError("HOST_NOT_READY");
            return null;
        }

        if (!_runtime.Policy.WritesAllowed)
        {
            SetLastError("HOST_READ_ONLY");
            return null;
        }

        try
        {
            var outcome = await _runtime.RunCleanupAsync(cancellationToken).ConfigureAwait(false);
            SetLastError(null);
            return outcome;
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            SetLastError(ErrorCodeOf(ex));
            return null;
        }
    }

    public async Task<CleanupOutcomeInfo?> RetryPendingCleanupsAsync(CancellationToken cancellationToken = default)
    {
        if (_runtime is null || !_runtime.Result.IsReady)
        {
            SetLastError("HOST_NOT_READY");
            return null;
        }

        if (!_runtime.Policy.WritesAllowed)
        {
            SetLastError("HOST_READ_ONLY");
            return null;
        }

        try
        {
            var outcome = await _runtime.RetryPendingCleanupsAsync(cancellationToken).ConfigureAwait(false);
            SetLastError(null);
            return outcome;
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            SetLastError(ErrorCodeOf(ex));
            return null;
        }
    }

    public async Task<BackupPackageInfo?> CreateBackupAsync(
        string backupType = "manual",
        CancellationToken cancellationToken = default)
    {
        if (_runtime is null || !_runtime.Result.IsReady)
        {
            SetLastError("HOST_NOT_READY");
            return null;
        }

        try
        {
            var created = await _runtime.CreateBackupAsync(backupType, cancellationToken).ConfigureAwait(false);
            SetLastError(null);
            return created;
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            SetLastError(ErrorCodeOf(ex));
            return null;
        }
    }

    public async Task<bool> DeleteBackupAsync(
        string backupId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(backupId))
        {
            SetLastError("INVALID_REQUEST");
            return false;
        }

        if (_runtime is null || !_runtime.Result.IsReady)
        {
            SetLastError("HOST_NOT_READY");
            return false;
        }

        try
        {
            await _runtime.DeleteBackupAsync(backupId, cancellationToken).ConfigureAwait(false);
            SetLastError(null);
            return true;
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            SetLastError(ErrorCodeOf(ex));
            return false;
        }
    }

    public async Task<string?> RestoreBackupAsync(
        string backupId,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(backupId))
        {
            SetLastError("INVALID_REQUEST");
            return null;
        }

        if (_runtime is null || !_runtime.Result.IsReady)
        {
            SetLastError("HOST_NOT_READY");
            return null;
        }

        try
        {
            var rollback = await _runtime.RestoreBackupAsync(backupId, cancellationToken).ConfigureAwait(false);
            // REALUSE-DATA-SAFETY-3 AC3: a restore replaces the whole library, so both the cached
            // chapter lists and the shelf from startup are stale. Refresh before returning, otherwise
            // the UI keeps showing the pre-restore library (imports only add pages, so they do not
            // need this).
            lock (_chapterCacheLock)
            {
                _chapterCache.Clear();
            }
            await RefreshBooksAsync(cancellationToken).ConfigureAwait(false);
            SetLastError(null);
            return rollback;
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            SetLastError(ErrorCodeOf(ex));
            return null;
        }
    }
    // ---------------------------------------------------------------------------------------
    // V11R-A-2 (audit P-02, contract §5.2): Run control through the registered production commands
    // C056-C061 (library_start_run / library_control_run / library_resume_blocked_run /
    // library_get_run_snapshot / library_get_task_projection / library_retry_failed_targets, all
    // protocol minor 3). The dispatcher enforces the legacy argument shapes; refusals return null and
    // publish the typed code through HostViewSnapshot.LastError. Writes follow the Host data-root
    // policy exactly like the existing region writes.
    // ---------------------------------------------------------------------------------------

    public async Task<RunStartInfo?> StartRunAsync(RunStartRequest request, CancellationToken ct = default)
    {
        if (request is null ||
            string.IsNullOrWhiteSpace(request.Command) ||
            request.Scope is null ||
            string.IsNullOrWhiteSpace(request.IdempotencyKey))
        {
            SetLastError("INVALID_REQUEST");
            return null;
        }

        if (ct.IsCancellationRequested)
        {
            SetLastError("CANCELLED");
            return null;
        }

        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            SetLastError("HOST_NOT_READY");
            return null;
        }

        if (!_runtime.Policy.WritesAllowed)
        {
            SetLastError("HOST_READ_ONLY");
            return null;
        }

        try
        {
            var response = await commands
                .InvokeAsync("library_start_run", RunPayloads.StartRun(request), ct)
                .ConfigureAwait(false);
            var info = RunStartInfo.FromJson(response.Value);
            SetLastError(null);
            return info;
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            SetLastError(ErrorCodeOf(ex));
            return null;
        }
    }

    public async Task<RunControlInfo?> ControlRunAsync(
        string runId,
        RunControlAction action,
        string? idempotencyKey = null,
        CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(runId))
        {
            SetLastError("INVALID_REQUEST");
            return null;
        }

        // R-08: restart always needs the caller's key (never generated here); other actions ignore it
        // because the frozen Core rejects an idempotency_key on them.
        if (action == RunControlAction.Restart && string.IsNullOrWhiteSpace(idempotencyKey))
        {
            SetLastError("INVALID_REQUEST");
            return null;
        }

        return await InvokeRunWriteAsync(
                "library_control_run",
                RunPayloads.ControlRun(
                    runId,
                    action,
                    action == RunControlAction.Restart ? idempotencyKey : null),
                ct)
            .ConfigureAwait(false);
    }

    public async Task<RunControlInfo?> ResumeBlockedRunAsync(string runId, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(runId))
        {
            SetLastError("INVALID_REQUEST");
            return null;
        }

        return await InvokeRunWriteAsync("library_resume_blocked_run", RunPayloads.RunId(runId), ct)
            .ConfigureAwait(false);
    }

    public async Task<RunSnapshotInfo?> GetRunSnapshotAsync(string runId, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(runId))
        {
            SetLastError("INVALID_REQUEST");
            return null;
        }

        if (ct.IsCancellationRequested)
        {
            SetLastError("CANCELLED");
            return null;
        }

        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            SetLastError("HOST_NOT_READY");
            return null;
        }

        try
        {
            var response = await commands
                .InvokeAsync("library_get_run_snapshot", RunPayloads.RunId(runId), ct)
                .ConfigureAwait(false);
            return RunSnapshotInfo.FromJson(response.Value);
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            SetLastError(ErrorCodeOf(ex));
            return null;
        }
    }

    public async Task<TaskProjectionInfo?> GetTaskProjectionAsync(string runId, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(runId))
        {
            SetLastError("INVALID_REQUEST");
            return null;
        }

        if (ct.IsCancellationRequested)
        {
            SetLastError("CANCELLED");
            return null;
        }

        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            SetLastError("HOST_NOT_READY");
            return null;
        }

        try
        {
            var response = await commands
                .InvokeAsync("library_get_task_projection", RunPayloads.RunId(runId), ct)
                .ConfigureAwait(false);
            // AC4: the projection is parsed exactly as the Core composes it; nothing is derived here.
            return TaskProjectionInfo.FromJson(response.Value);
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            SetLastError(ErrorCodeOf(ex));
            return null;
        }
    }

    public async Task<RunControlInfo?> RetryFailedTargetsAsync(
        string runId,
        string idempotencyKey,
        CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(runId) || string.IsNullOrWhiteSpace(idempotencyKey))
        {
            // R-08: the retry key is mandatory — a missing key must never be generated silently.
            SetLastError("INVALID_REQUEST");
            return null;
        }

        return await InvokeRunWriteAsync(
                "library_retry_failed_targets",
                RunPayloads.RetryFailedTargets(runId, idempotencyKey),
                ct)
            .ConfigureAwait(false);
    }

    /// <summary>
    /// V11R-A-2: shared body of the four Run write faces (ControlRun / ResumeBlockedRun /
    /// RetryFailedTargets). Local validation and the Host data-root policy gate run before any wire
    /// frame; Core refusals keep their typed code (INVALID_RUN_TRANSITION / TARGET_NOT_FOUND /
    /// IDEMPOTENCY_KEY_REUSED / …).
    /// </summary>
    private async Task<RunControlInfo?> InvokeRunWriteAsync(
        string command,
        System.Text.Json.JsonElement payload,
        CancellationToken ct)
    {
        if (ct.IsCancellationRequested)
        {
            SetLastError("CANCELLED");
            return null;
        }

        if (_runtime?.Commands is not { } commands || !_runtime.Result.IsReady)
        {
            SetLastError("HOST_NOT_READY");
            return null;
        }

        if (!_runtime.Policy.WritesAllowed)
        {
            SetLastError("HOST_READ_ONLY");
            return null;
        }

        try
        {
            var response = await commands.InvokeAsync(command, payload, ct).ConfigureAwait(false);
            var info = RunControlInfo.FromJson(response.Value);
            SetLastError(null);
            return info;
        }
        catch (Exception ex) when (IsUiFacingFailure(ex))
        {
            SetLastError(ErrorCodeOf(ex));
            return null;
        }
    }

    private static bool IsUiFacingFailure(Exception ex) => ex is
        CoreOperationException or SidecarException or BridgeException or ReadOnlyHostException or
        HostCommandInvalidArgumentsException or ShellActionException or IOException or
        UnauthorizedAccessException or InvalidOperationException or ArgumentException or
        OperationCanceledException;

    private static string ErrorCodeOf(Exception ex) => ex switch
    {
        CoreOperationException core => core.Code,
        SidecarException sidecar => sidecar.Code.ToString(),
        ShellActionException shell => shell.Code,
        ReadOnlyHostException => "HOST_READ_ONLY",
        HostCommandInvalidArgumentsException => "INVALID_ARGUMENTS",
        OperationCanceledException => "CANCELLED",
        _ => "HOST_UNAVAILABLE",
    };

    private static string UserMessageOf(Exception ex) => ex switch
    {
        CoreOperationException core => core.Message,
        SidecarException sidecar => sidecar.UserMessage,
        ShellActionException shell => shell.Message,
        ReadOnlyHostException => "Host 处于只读模式（parity 未达成）",
        HostCommandInvalidArgumentsException invalid => invalid.Message,
        _ => "Host 请求失败",
    };

    private static int? ReadInt(System.Text.Json.JsonElement element, string property) =>
        element.ValueKind == System.Text.Json.JsonValueKind.Object &&
        element.TryGetProperty(property, out var value) &&
        value.ValueKind == System.Text.Json.JsonValueKind.Number &&
        value.TryGetInt32(out var parsed)
            ? parsed
            : null;

    /// <summary>
    /// V11R-A-1: publish the typed code of the last refused service-layer write (null = recovered).
    /// Only the code travels — never a message, a path or a secret — and <see cref="Changed"/> fires
    /// only when the value actually changes so a failing UI never gets an event storm.
    /// </summary>
    private void SetLastError(string? code)
    {
        if (string.Equals(_snapshot.LastError, code, StringComparison.Ordinal))
        {
            return;
        }

        _snapshot = _snapshot with { LastError = code };
        RaiseChanged();
    }

    public async ValueTask DisposeAsync()
    {
        // FEA-09-UI-1: release any one-shot password context before the runtime goes away.
        if (_sourceImports is not null)
        {
            await _sourceImports.DisposeAsync().ConfigureAwait(false);
            _sourceImports = null;
        }

        if (_runtime is not null)
        {
            await _runtime.DisposeAsync().ConfigureAwait(false);
            _runtime = null;
        }
    }

    private void UpdateFromRuntime(IReadOnlyList<BookSummary>? books = null)
    {
        if (_runtime is null)
        {
            return;
        }

        var result = _runtime.Result;
        var wireCount = _runtime.CoreService?.Wire.Count ?? 0;
        var bridgeFrames = _runtime.HostBridge?.Wire.Count ?? 0;
        var allAscii = _runtime.CoreService?.Wire.AllRequestsAsciiOnly ?? false;
        _snapshot = new HostViewSnapshot(
            result.Status switch
            {
                HostStatus.Ready => HostViewState.Ready,
                HostStatus.AlreadyRunning => HostViewState.AlreadyRunning,
                _ => HostViewState.Failed,
            },
            result.Status switch
            {
                HostStatus.Ready => "Host 就绪 · core_service protocol 2.3 + host_bridge wire v1",
                HostStatus.AlreadyRunning => "已有 New Manga 主机在运行",
                _ => "Host 启动失败",
            },
            $"{CoexistenceRules.Describe(result.Mode)} · {(result.Status == HostStatus.Ready ? "sidecars ready" : "no sidecars")}",
            result.ErrorCode,
            result.UserMessage,
            books ?? Array.Empty<BookSummary>(),
            wireCount + bridgeFrames,
            allAscii,
            _snapshot.LastChineseRoundTrip)
        {
            // READER-WORKBENCH-1 AC3: the workbench's write gate mirrors the Host data-root policy.
            WritesAllowed = _runtime.Policy.WritesAllowed,
            // V11R-A-5: when the gate is closed the UI gets the explicit reason, never a silent refusal.
            ReadOnlyReason = _runtime.Policy.WritesAllowed
                ? null
                : CoexistenceRules.Describe(result.Mode),
            // REALUSE-DATA-SAFETY-2 AC3: surface the startup self check so it is not a log-only fact.
            SelfCheckStatus = _runtime.SelfCheck.Status.ToString(),
            SelfCheckLine = _runtime.SelfCheck.Status switch
            {
                NewManga.Host.SelfCheckStatus.Passed => "启动自检通过",
                NewManga.Host.SelfCheckStatus.Degraded =>
                    $"启动自检降级：{_runtime.SelfCheck.Reason}",
                NewManga.Host.SelfCheckStatus.Failed =>
                    $"启动自检未通过：{_runtime.SelfCheck.ErrorCode} · {_runtime.SelfCheck.Reason}",
                _ => "启动自检尚未运行",
            },
        };
        RaiseChanged();
    }
    // FEA-05-PORT-1: the Draft command surface (C078-C083). Reads return null when the
    // host is not ready; writes surface typed exceptions from the dispatcher unchanged.
    private NewManga.CoreClient.Commands.HostCommandDispatcher? DraftCommands =>
        _runtime is { Result.IsReady: true } runtime ? runtime.Commands : null;

    public async Task<DraftLease?> OpenDraftAsync(string sessionId, string pageId, string? regionId,
        string? baseRevisionId, int pageBindingVersion, CancellationToken cancellationToken = default)
    {
        var commands = DraftCommands;
        if (commands is null)
        {
            return null;
        }

        var args = new Dictionary<string, object?>
        {
            ["sessionId"] = sessionId,
            ["pageId"] = pageId,
            ["regionId"] = regionId,
            ["baseRevisionId"] = baseRevisionId,
            ["pageBindingVersion"] = pageBindingVersion,
        };
        var response = await commands.InvokeAsync("drafts_open", System.Text.Json.JsonSerializer.SerializeToElement(args), cancellationToken).ConfigureAwait(false);
        var value = response.Value;
        if (value.ValueKind != System.Text.Json.JsonValueKind.Object || !value.TryGetProperty("draft", out var draft))
        {
            return null;
        }

        var canEdit = value.TryGetProperty("canEdit", out var canEditValue) && canEditValue.ValueKind == System.Text.Json.JsonValueKind.True;
        EditToken? token = value.TryGetProperty("token", out var tokenValue) && tokenValue.ValueKind == System.Text.Json.JsonValueKind.Object
            ? ReadEditToken(tokenValue)
            : null;
        return new DraftLease(ReadDraft(draft), canEdit, token);
    }

    public async Task<Draft?> PatchDraftAsync(string draftId, string sessionId, DraftPatchRequest patch,
        int? undoCursor = null, CancellationToken cancellationToken = default)
    {
        var commands = DraftCommands;
        if (commands is null)
        {
            return null;
        }

        var args = new Dictionary<string, object?>
        {
            ["draftId"] = draftId,
            ["sessionId"] = sessionId,
            ["patch"] = DraftPatchJson(patch),
            ["undoCursor"] = undoCursor,
        };
        var response = await commands.InvokeAsync("drafts_patch", System.Text.Json.JsonSerializer.SerializeToElement(args), cancellationToken).ConfigureAwait(false);
        return response.Value.TryGetProperty("draft", out var draft) ? ReadDraft(draft) : null;
    }

    public async Task<RegionCandidate?> PrepareCandidateAsync(string regionId, DraftPatchRequest patch,
        string origin, string? draftId = null, string? baseRevisionId = null,
        CancellationToken cancellationToken = default)
    {
        var commands = DraftCommands;
        if (commands is null)
        {
            return null;
        }

        var args = new Dictionary<string, object?>
        {
            ["regionId"] = regionId,
            ["patch"] = DraftPatchJson(patch),
            ["origin"] = origin,
            ["draftId"] = draftId,
            ["baseRevisionId"] = baseRevisionId,
        };
        var response = await commands.InvokeAsync("drafts_prepare", System.Text.Json.JsonSerializer.SerializeToElement(args), cancellationToken).ConfigureAwait(false);
        if (!response.Value.TryGetProperty("candidate", out var candidate))
        {
            return null;
        }

        return new RegionCandidate(
            candidate.TryGetProperty("candidateId", out var id) ? id.GetString() ?? "" : "",
            candidate.TryGetProperty("RegionId", out var rid) ? rid.GetString() ?? "" : "",
            candidate.TryGetProperty("BaseRevisionId", out var baseRev) ? baseRev.GetString() ?? "" : "",
            candidate.TryGetProperty("origin", out var org) ? org.GetString() ?? "" : "");
    }

    public async Task<IReadOnlyDictionary<string, string>> ApplyCandidatesAsync(EditToken token,
        IReadOnlyList<string> candidateIds, CancellationToken cancellationToken = default)
    {
        var commands = DraftCommands;
        if (commands is null)
        {
            return new Dictionary<string, string>();
        }

        var args = new Dictionary<string, object?>
        {
            ["token"] = new Dictionary<string, object?>
            {
                ["tokenId"] = token.TokenId,
                ["DraftId"] = token.DraftId,
                ["DraftSequence"] = token.DraftSequence,
                ["SessionId"] = token.SessionId,
                ["issuedAt"] = token.IssuedAt,
                ["expiresAt"] = token.ExpiresAt,
            },
            ["candidateIds"] = candidateIds,
        };
        var response = await commands.InvokeAsync("drafts_apply", System.Text.Json.JsonSerializer.SerializeToElement(args), cancellationToken).ConfigureAwait(false);
        var result = new Dictionary<string, string>(StringComparer.Ordinal);
        if (response.Value.ValueKind == System.Text.Json.JsonValueKind.Object)
        {
            foreach (var property in response.Value.EnumerateObject())
            {
                if (property.Value.ValueKind == System.Text.Json.JsonValueKind.String)
                {
                    result[property.Name] = property.Value.GetString() ?? "";
                }
            }
        }

        return result;
    }

    public async Task<Draft?> GetDraftAsync(string draftId, CancellationToken cancellationToken = default)
    {
        var commands = DraftCommands;
        if (commands is null)
        {
            return null;
        }

        var response = await commands.InvokeAsync("drafts_status", System.Text.Json.JsonSerializer.SerializeToElement(new Dictionary<string, object?> { ["draftId"] = draftId }), cancellationToken).ConfigureAwait(false);
        return response.Value.TryGetProperty("draft", out var draft) ? ReadDraft(draft) : null;
    }

    public async Task<IReadOnlyList<Draft>> ListDraftsAsync(string sessionId,
        CancellationToken cancellationToken = default)
    {
        var commands = DraftCommands;
        if (commands is null)
        {
            return Array.Empty<Draft>();
        }

        var response = await commands.InvokeAsync("drafts_status", System.Text.Json.JsonSerializer.SerializeToElement(new Dictionary<string, object?> { ["sessionId"] = sessionId }), cancellationToken).ConfigureAwait(false);
        if (!response.Value.TryGetProperty("drafts", out var drafts) || drafts.ValueKind != System.Text.Json.JsonValueKind.Array)
        {
            return Array.Empty<Draft>();
        }

        return drafts.EnumerateArray().Select(ReadDraft).ToArray();
    }

    public async Task DiscardDraftAsync(string draftId, string sessionId,
        CancellationToken cancellationToken = default)
    {
        var commands = DraftCommands;
        if (commands is null)
        {
            return;
        }

        await commands.InvokeAsync("drafts_discard", System.Text.Json.JsonSerializer.SerializeToElement(new Dictionary<string, object?> { ["draftId"] = draftId, ["sessionId"] = sessionId }), cancellationToken).ConfigureAwait(false);
    }

    private static Draft ReadDraft(System.Text.Json.JsonElement value)
    {
        // Draft.to_json() (domain/drafts/entities.py:11 persisted SC-D01 fields).
        var patch = value.TryGetProperty("patch", out var patchValue) && patchValue.ValueKind == System.Text.Json.JsonValueKind.Object
            ? patchValue.Clone()
            : (System.Text.Json.JsonElement?)null;
        int? undo = value.TryGetProperty("undoCursor", out var undoValue) && undoValue.ValueKind == System.Text.Json.JsonValueKind.Number && undoValue.TryGetInt32(out var undoNumber)
            ? undoNumber
            : null;
        return new Draft(
            value.TryGetProperty("DraftId", out var draftId) ? draftId.GetString() ?? "" : "",
            value.TryGetProperty("SessionId", out var sessionId) ? sessionId.GetString() ?? "" : "",
            value.TryGetProperty("PageId", out var pageId) ? pageId.GetString() ?? "" : "",
            value.TryGetProperty("RegionId", out var regionId) && regionId.ValueKind == System.Text.Json.JsonValueKind.String ? regionId.GetString() : null,
            value.TryGetProperty("BaseRevisionId", out var baseRev) && baseRev.ValueKind == System.Text.Json.JsonValueKind.String ? baseRev.GetString() : null,
            value.TryGetProperty("PageBindingVersion", out var binding) && binding.TryGetInt32(out var bindingNumber) ? bindingNumber : 0,
            value.TryGetProperty("DraftSequence", out var seq) && seq.TryGetInt32(out var sequence) ? sequence : 0,
            patch,
            undo,
            value.TryGetProperty("savedAt", out var savedAt) ? savedAt.GetString() ?? "" : "",
            value.TryGetProperty("status", out var status) ? status.GetString() ?? "" : "");
    }

    private static EditToken ReadEditToken(System.Text.Json.JsonElement value) => new(
        value.TryGetProperty("tokenId", out var tokenId) ? tokenId.GetString() ?? "" : "",
        value.TryGetProperty("DraftId", out var draftId) ? draftId.GetString() ?? "" : "",
        value.TryGetProperty("DraftSequence", out var seq) && seq.TryGetInt32(out var sequence) ? sequence : 0,
        value.TryGetProperty("SessionId", out var sessionId) ? sessionId.GetString() ?? "" : "",
        value.TryGetProperty("issuedAt", out var issuedAt) ? issuedAt.GetString() ?? "" : "",
        value.TryGetProperty("expiresAt", out var expiresAt) ? expiresAt.GetString() ?? "" : "");

    private static Dictionary<string, object?> DraftPatchJson(DraftPatchRequest patch) =>
        patch.Patch.ToDictionary(pair => pair.Key, pair => pair.Value, StringComparer.Ordinal);
}

