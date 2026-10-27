using NewManga.CoreClient;
using NewManga.CoreClient.Bridge;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;
using NewManga.Host;

namespace NewManga.App.Services;

/// <summary>Production controller: starts <see cref="HostRuntime"/> and maps typed failures to UI text.</summary>
public sealed class HostController : IHostController
{
    private readonly HostOptions _options;
    private HostRuntime? _runtime;
    private HostViewSnapshot _snapshot = new(
        HostViewState.Starting,
        "正在启动 Host…",
        "—",
        null,
        null,
        Array.Empty<BookSummary>(),
        0,
        true,
        null);

    public HostController(HostOptions options)
    {
        _options = options;
    }

    public HostViewSnapshot Snapshot => _snapshot;

    public event EventHandler? Changed;

    public async Task StartAsync(CancellationToken cancellationToken = default)
    {
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
            };
            Changed?.Invoke(this, EventArgs.Empty);
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
            };
            Changed?.Invoke(this, EventArgs.Empty);
        }
        catch (SidecarException ex)
        {
            _snapshot = _snapshot with
            {
                State = HostViewState.Failed,
                StatusLine = "核心服务中断",
                ErrorCode = ex.Code.ToString(),
                ErrorMessage = ex.UserMessage,
            };
            Changed?.Invoke(this, EventArgs.Empty);
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
            Changed?.Invoke(this, EventArgs.Empty);
            await RefreshBooksAsync(cancellationToken).ConfigureAwait(false);
            return result.ExactMatch;
        }
        catch (ReadOnlyHostException)
        {
            _snapshot = _snapshot with
            {
                LastChineseRoundTrip = "只读模式：S2 parity 前禁止写生产数据",
            };
            Changed?.Invoke(this, EventArgs.Empty);
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
            };
            Changed?.Invoke(this, EventArgs.Empty);
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
            var books = await runtime.ListBooksAsync(cancellationToken).ConfigureAwait(false);
            BookSummary? book = null;
            if (!string.IsNullOrWhiteSpace(bookId))
            {
                book = books.FirstOrDefault(candidate => string.Equals(candidate.BookId, bookId, StringComparison.Ordinal));
            }

            book ??= books.FirstOrDefault(candidate => (candidate.PageCount ?? 0) > 0) ?? books.FirstOrDefault();
            if (book is null)
            {
                return null;
            }

            var chapters = await runtime.ListChaptersAsync(book.BookId, cancellationToken).ConfigureAwait(false);
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

        var runtime = _runtime;
        try
        {
            return await runtime.ListChaptersAsync(bookId, cancellationToken).ConfigureAwait(false);
        }
        catch (Exception ex) when (
            ex is CoreOperationException or SidecarException or BridgeException or OperationCanceledException or IOException)
        {
            return Array.Empty<ChapterSummary>();
        }
    }

    /// <summary>
    /// CREDENTIAL-UI-1 AC1/AC2: provider + proxy targets with the Core <c>credential_state</c>. Reads the
    /// two existing P15 profile-list commands (no new Host contract); an empty list means "no profiles or
    /// Host not ready". Never reads or returns a secret.
    /// </summary>
    public async Task<IReadOnlyList<CredentialTargetOption>> ListCredentialTargetsAsync(
        CancellationToken cancellationToken = default)
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

    public async ValueTask DisposeAsync()
    {
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
            _snapshot.LastChineseRoundTrip);
        Changed?.Invoke(this, EventArgs.Empty);
    }
}
