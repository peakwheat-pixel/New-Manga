using NewManga.CoreClient;
using NewManga.CoreClient.Bridge;
using NewManga.CoreClient.Commands;
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
        CancellationToken cancellationToken = default)
    {
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
                bookId, new[] { chapterId }, orderedPageIds, format, pdfContent: pdfContent);
            var started = await grants.StartExportAsync(request, targetPath, cancellationToken).ConfigureAwait(false);
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
        Changed?.Invoke(this, EventArgs.Empty);
    }

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
            _snapshot.LastChineseRoundTrip)
        {
            // READER-WORKBENCH-1 AC3: the workbench's write gate mirrors the Host data-root policy.
            WritesAllowed = _runtime.Policy.WritesAllowed,
        };
        Changed?.Invoke(this, EventArgs.Empty);
    }
}
