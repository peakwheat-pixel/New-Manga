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
                bookId, new[] { chapterId }, orderedPageIds);
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
