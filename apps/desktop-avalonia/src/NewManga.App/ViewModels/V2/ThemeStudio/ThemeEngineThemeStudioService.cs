using System.Text;
using NewManga.ThemeEngine;

namespace NewManga.App.ViewModels.V2.ThemeStudio;

/// <summary>
/// Production Theme Studio service: the thin UI-facing sequence over the real Theme Engine
/// (<see cref="IThemeService"/> + <see cref="IThemeRegistry"/> + <see cref="IThemePreviewEngine"/> +
/// <see cref="IThemeValidator"/> + <see cref="ThemePackageJson"/> + <see cref="LegacyThemeMigration"/>).
///
/// <para>
/// It owns no theme semantics. Theme selection preview is delegated to the engine's preview session, which
/// applies and restores the application-wide layer; persistence, migration and fallback are the engine's;
/// palette composition for <em>uninstalled</em> editor drafts is delegated to
/// <see cref="ThemePaletteComposer"/> through <see cref="ThemeStudioPaletteBuilder"/>. This class only maps
/// results into UI facts — including the honest "persisted / preview-only" distinction.
/// </para>
/// </summary>
public sealed class ThemeEngineThemeStudioService : IThemeStudioService
{
    private readonly ThemeService _themeService;
    private readonly ThemeRegistry _registry;
    private readonly ThemeSettingsStore _settingsStore;
    private readonly IThemeValidator _validator;
    private readonly ThemeStudioPaletteBuilder _palettes;
    private readonly ThemeStudioFavoritesStore _favoritesStore;
    private readonly Func<bool> _isSandbox;
    private readonly Func<bool> _persistsToDisk;

    private readonly HashSet<string> _favorites = new(StringComparer.Ordinal);
    private readonly List<ThemeStudioIssue> _lastIssues = new();
    private IReadOnlyList<ThemeStudioMigrationNotice> _migrationNotices = [];
    private ThemeStudioValidationReport _startupIssues = ThemeStudioValidationReport.Ok;

    private ThemePreviewSession? _session;
    private ThemePackage? _localDraft;
    private bool _followSystemAccent;
    private bool _initialized;
    private bool _disposed;
    private string? _lastError;

    /// <summary>Creates the adapter over an engine service assembled by the host.</summary>
    public ThemeEngineThemeStudioService(
        ThemeService themeService,
        ThemeRegistry registry,
        ThemeSettingsStore settingsStore,
        ThemeStudioFavoritesStore favoritesStore,
        ThemeStudioPaletteBuilder? palettes,
        bool isSandbox,
        bool persistsToDisk)
    {
        _themeService = themeService ?? throw new ArgumentNullException(nameof(themeService));
        _registry = registry ?? throw new ArgumentNullException(nameof(registry));
        _settingsStore = settingsStore ?? throw new ArgumentNullException(nameof(settingsStore));
        _favoritesStore = favoritesStore ?? throw new ArgumentNullException(nameof(favoritesStore));
        _validator = ThemeValidator.Default;
        _palettes = palettes ?? new ThemeStudioPaletteBuilder();
        _isSandbox = () => isSandbox;
        _persistsToDisk = () => persistsToDisk;
    }

    /// <summary>
    /// Creates the production adapter: real registry + settings store + <c>DesignSystemThemeLayerSink</c> +
    /// <see cref="ThemeService"/>. This is the only construction path the shipped UI uses.
    /// </summary>
    /// <param name="application">Running Avalonia application (the sink's resource host).</param>
    /// <param name="manager">The application's single <c>DesignSystemThemeManager</c> (already initialized).</param>
    /// <param name="themeDirectory">User theme directory override (tests use a temp directory).</param>
    /// <param name="settingsFilePath">Settings document override.</param>
    /// <param name="favoritesFilePath">Favorites document override.</param>
    public static ThemeEngineThemeStudioService CreateProduction(
        Avalonia.Application application,
        NewManga.DesignSystem.Theming.DesignSystemThemeManager manager,
        string? themeDirectory = null,
        string? settingsFilePath = null,
        string? favoritesFilePath = null)
    {
        ArgumentNullException.ThrowIfNull(application);
        ArgumentNullException.ThrowIfNull(manager);

        var registry = new ThemeRegistry(themeDirectory);
        var store = new ThemeSettingsStore(settingsFilePath, registry);
        var sink = new DesignSystemThemeLayerSink(application, manager);
        var service = new ThemeService(registry, store, sink);
        return new ThemeEngineThemeStudioService(
            service,
            registry,
            store,
            new ThemeStudioFavoritesStore(favoritesFilePath),
            palettes: null,
            isSandbox: false,
            persistsToDisk: true);
    }

    /// <summary>The engine service (host wiring may need it for non-Studio consumers).</summary>
    public IThemeService ThemeService => _themeService;

    /// <summary>True once <see cref="InitializeAsync"/> completed.</summary>
    public bool IsInitialized => _initialized;

    /// <summary>Session-scoped system-accent flag (see <see cref="SetFollowSystemAccentAsync"/>).</summary>
    public bool FollowSystemAccent => _followSystemAccent;

    /// <inheritdoc />
    public ThemeStudioCapabilities Capabilities { get; private set; } = new(
        EngineConnected: false,
        PersistsSettings: false,
        CanApplyAppWide: false,
        CanManageUserThemes: false,
        IsSandbox: false,
        SourceLabel: "未初始化",
        Note: null);

    /// <inheritdoc />
    public ThemeSettings Settings => _themeService.Settings;

    /// <inheritdoc />
    public ThemeDescriptor CurrentTheme => _themeService.Current;

    /// <inheritdoc />
    public ThemePackage AppliedPackage => ResolvePackage(_themeService.Settings.ThemeId);

    /// <inheritdoc />
    public IReadOnlyList<ThemePackage> Themes
    {
        get
        {
            var descriptors = _registry.All;
            var packages = new List<ThemePackage>(descriptors.Count);
            foreach (var descriptor in descriptors)
            {
                if (TryLoad(descriptor.Id, out var package))
                {
                    packages.Add(package);
                }
            }

            return packages;
        }
    }

    /// <inheritdoc />
    public IReadOnlyList<ThemeStudioMigrationNotice> MigrationNotices => _migrationNotices;

    /// <inheritdoc />
    public ThemeStudioValidationReport StartupIssues => _startupIssues;

    /// <inheritdoc />
    public IReadOnlyList<ThemeStudioIssue> LastIssues => _lastIssues;

    /// <summary>Last non-fatal error (palette application, persistence, …).</summary>
    public string? LastError => _lastError ?? _themeService.LastError;

    /// <inheritdoc />
    public event EventHandler? Changed;

    /// <inheritdoc />
    public async Task InitializeAsync(CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        await _themeService.InitializeAsync(ct).ConfigureAwait(false);

        _lastIssues.Clear();
        _lastIssues.AddRange(_themeService.LastIssues.Select(ThemeStudioIssue.From));
        _lastIssues.AddRange(_settingsStore.LastLoadIssues.Select(ThemeStudioIssue.From));

        _migrationNotices = BuildMigrationNotices(_themeService.LastIssues.Concat(_settingsStore.LastLoadIssues));
        _startupIssues = BuildStartupIssues(_lastIssues, _registry.Diagnostics);

        foreach (var id in _favoritesStore.Load())
        {
            _favorites.Add(id);
        }

        _followSystemAccent = _themeService.Settings.FollowSystemAccent;

        Capabilities = new ThemeStudioCapabilities(
            EngineConnected: true,
            PersistsSettings: _persistsToDisk(),
            CanApplyAppWide: true,
            CanManageUserThemes: true,
            IsSandbox: _isSandbox(),
            SourceLabel: _isSandbox() ? "STUB 沙箱（临时目录）" : "Theme Engine v1",
            Note: BuildCapabilityNote());

        _initialized = true;
        RaiseChanged();
    }

    /// <inheritdoc />
    public ThemePackage? DraftPackage
    {
        get
        {
            if (_localDraft is not null)
            {
                return _localDraft;
            }

            var pending = _session is { State: ThemePreviewState.Active } active ? active.PendingThemeId : null;
            return pending is not null && TryLoad(pending, out var package) ? package : null;
        }
    }

    /// <inheritdoc />
    public bool IsDraftPackageScoped => _localDraft is not null;

    /// <inheritdoc />
    public bool HasDraft =>
        _localDraft is not null || (_session is { State: ThemePreviewState.Active } active && active.HasChanges);

    /// <inheritdoc />
    public void BeginPreview()
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        if (_session is { State: ThemePreviewState.Active })
        {
            return;
        }

        _session = (ThemePreviewSession)_themeService.PreviewEngine.Begin();
    }

    /// <inheritdoc />
    public void PreviewTheme(string themeId)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        if (!TryLoad(themeId, out _))
        {
            _lastError = $"主题 '{themeId}' 不存在";
            return;
        }

        EnsureSession();
        _localDraft = null;

        try
        {
            _session!.Update(themeId);
        }
        catch (ThemePreviewException)
        {
            // The service cancels the engine session whenever the persisted settings change (appearance,
            // contrast, density, apply). Our handle can therefore be stale: drop it and begin a fresh
            // session so a preview after a settings switch still works.
            _session = null;
            EnsureSession();
            _session!.Update(themeId);
        }

        RaiseChanged();
    }

    /// <inheritdoc />
    public void PreviewDocument(ThemePackage package)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ArgumentNullException.ThrowIfNull(package);
        _localDraft = package;
        RaiseChanged();
    }

    /// <inheritdoc />
    public Task CancelPreviewAsync(CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ct.ThrowIfCancellationRequested();

        CancelSession();
        _localDraft = null;
        RaiseChanged();
        return Task.CompletedTask;
    }

    /// <inheritdoc />
    public async Task<ThemeStudioApplyResult> ApplyAsync(CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ct.ThrowIfCancellationRequested();

        var issues = new List<ThemeStudioIssue>();
        var localDraft = _localDraft;
        string targetId;

        if (localDraft is not null)
        {
            var install = await InstallDraftAsThemeAsync(localDraft, ct).ConfigureAwait(false);
            if (!install.Success || install.ThemeId is null)
            {
                return ThemeStudioApplyResult.Failed(install.Issues);
            }

            targetId = install.ThemeId;
            issues.AddRange(install.Issues);
        }
        else
        {
            targetId = (_session is { State: ThemePreviewState.Active } active ? active.PendingThemeId : null)
                ?? _themeService.Settings.ThemeId;
        }

        // Commit the engine session only after the target is installable; a failed install keeps the draft.
        if (_session is not null)
        {
            try
            {
                _session.Commit();
            }
            catch (ThemePreviewException exception)
            {
                issues.AddRange(exception.Issues.Select(ThemeStudioIssue.From));
            }

            _session = null;
        }

        var result = await _themeService.ApplyAsync(targetId, ct).ConfigureAwait(false);
        issues.AddRange(result.Issues.Select(ThemeStudioIssue.From));
        if (!result.Success)
        {
            _lastError = _themeService.LastError ?? "主题应用失败";
            _localDraft = localDraft;
            RaiseChanged();
            return ThemeStudioApplyResult.Failed(issues);
        }

        _localDraft = null;
        _lastError = null;
        var persisted = _persistsToDisk() && _themeService.LastError is null;
        var appliedId = result.AppliedThemeId ?? _themeService.Settings.ThemeId;
        var recovered = !string.Equals(appliedId, targetId, StringComparison.Ordinal);
        RaiseChanged();
        return recovered
            ? ThemeStudioApplyResult.RecoveredWith(appliedId, persisted, issues)
            : new ThemeStudioApplyResult(true, appliedId, persisted, issues, false);
    }

    /// <inheritdoc />
    public async Task SetAppearanceAsync(AppearanceMode mode, CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ct.ThrowIfCancellationRequested();
        await _themeService.SetAppearanceAsync(mode).ConfigureAwait(false);
        CaptureServiceIssues();
        RaiseChanged();
    }

    /// <inheritdoc />
    public async Task SetContrastAsync(ContrastMode mode, CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ct.ThrowIfCancellationRequested();
        await _themeService.SetContrastAsync(mode).ConfigureAwait(false);
        CaptureServiceIssues();
        RaiseChanged();
    }

    /// <inheritdoc />
    public async Task SetDensityAsync(Density density, CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ct.ThrowIfCancellationRequested();
        var layout = _themeService.Settings.Layout with { Density = density };
        await _themeService.SetLayoutAsync(layout).ConfigureAwait(false);
        CaptureServiceIssues();
        RaiseChanged();
    }

    /// <inheritdoc />
    public async Task SetReducedMotionAsync(bool enabled, CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ct.ThrowIfCancellationRequested();
        await _themeService.SetReducedMotionAsync(enabled).ConfigureAwait(false);
        CaptureServiceIssues();
        RaiseChanged();
    }

    /// <inheritdoc />
    public Task SetFollowSystemAccentAsync(bool enabled, CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ct.ThrowIfCancellationRequested();

        // The frozen IThemeService contract has no system-accent setter (GAP-3 reported to the Lead).
        // Until adjudicated the flag is session-scoped: every scoped palette this surface composes honours
        // it, and the UI states that it is not persisted app-wide.
        _followSystemAccent = enabled;
        RaiseChanged();
        return Task.CompletedTask;
    }

    /// <inheritdoc />
    public ThemeStudioPalette ComposePalette(ThemePackage package, ThemeStudioPaletteRequest request) =>
        _palettes.Build(package, request with { FollowSystemAccent = _followSystemAccent });

    /// <inheritdoc />
    public ThemeStudioPalette ComposePalette(string themeId, ThemeStudioPaletteRequest request) =>
        TryLoad(themeId, out var package)
            ? ComposePalette(package, request)
            : ComposePalette(AppliedPackage, request);

    /// <inheritdoc />
    public ThemeStudioPalette GetAppliedPalette() =>
        ComposePalette(AppliedPackage, ThemeStudioPaletteRequest.FromSettings(_themeService.Settings));

    /// <inheritdoc />
    public ThemeStudioPalette? GetDraftPalette() =>
        _localDraft is null
            ? null
            : ComposePalette(_localDraft, ThemeStudioPaletteRequest.FromSettings(_themeService.Settings));

    /// <inheritdoc />
    public ThemeStudioContrastReport Audit(ThemePackage package, PaletteVariant variant) =>
        ThemeStudioContrastAuditor.Evaluate(package, variant);

    /// <inheritdoc />
    public ThemeStudioValidationReport ValidatePackage(ThemePackage package)
    {
        ArgumentNullException.ThrowIfNull(package);
        return ThemeStudioValidationReport.From(_validator.Validate(package));
    }

    /// <inheritdoc />
    public ThemePackage? FindPackage(string themeId) => TryLoad(themeId, out var package) ? package : null;

    /// <inheritdoc />
    public ThemeStudioValidationReport ValidateJson(string json, string? sourceName = null)
    {
        ArgumentNullException.ThrowIfNull(json);
        if (json.Length > ThemePackageJson.MaxDocumentBytes)
        {
            return ThemeStudioValidationReport.From([
                Issue(
                    ThemeIssueCodes.InstallTooLarge,
                    ThemeStudioIssueLevel.Error,
                    $"{sourceName ?? "主题包"} 超过 {ThemePackageJson.MaxDocumentBytes} 字节上限",
                    null),
            ]);
        }

        var read = ThemePackageJson.Read(json);
        var issues = read.Issues.Select(ThemeStudioIssue.From).ToList();
        if (read.Package is null)
        {
            return ThemeStudioValidationReport.From(issues);
        }

        var validation = _validator.Validate(read.Package);
        issues.AddRange(validation.Issues.Select(ThemeStudioIssue.From));
        return ThemeStudioValidationReport.From(issues);
    }

    /// <inheritdoc />
    public async Task<ThemeStudioOperationResult> ImportAsync(
        string json,
        string sourceName,
        bool overwrite = false,
        CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ct.ThrowIfCancellationRequested();

        var report = ValidateJson(json, sourceName);
        if (!report.IsValid)
        {
            return ThemeStudioOperationResult.Fail($"导入被阻止：{report.ErrorCount} 个错误", report.Issues);
        }

        var read = ThemePackageJson.Read(json);
        if (read.Package is null)
        {
            return ThemeStudioOperationResult.Fail("主题包无法读取", report.Issues);
        }

        var id = read.Package.Descriptor.Id;
        if (!overwrite && _registry.Find(id) is { Kind: ThemeKind.User })
        {
            return ThemeStudioOperationResult.Fail(
                $"主题 ID '{id}' 已存在。请选择覆盖或改名后导入。",
                [
                    Issue(
                        ThemeIssueCodes.RegistryDuplicateId,
                        ThemeStudioIssueLevel.Error,
                        $"主题 ID '{id}' 已存在",
                        "descriptor.id"),
                ]);
        }

        var installed = await InstallJsonAsync(json, ct).ConfigureAwait(false);
        if (!installed.IsValid)
        {
            return ThemeStudioOperationResult.Fail(
                $"导入被阻止：{ThemeStudioValidationReport.From(installed).ErrorCount} 个错误",
                installed.Issues.Select(ThemeStudioIssue.From));
        }

        await _registry.RefreshAsync(ct).ConfigureAwait(false);
        CaptureServiceIssues();
        RaiseChanged();
        return ThemeStudioOperationResult.OkWith(
            $"已导入主题「{id}」",
            installed.Issues.Select(ThemeStudioIssue.From));
    }

    /// <inheritdoc />
    public async Task<ThemeStudioOperationResult> ImportFileAsync(
        string path,
        bool overwrite = false,
        CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ct.ThrowIfCancellationRequested();

        if (!IsAcceptedThemeFile(path))
        {
            return ThemeStudioOperationResult.Fail(
                "只接受 .nmtheme / .json 主题包文件",
                [
                    Issue(
                        ThemeIssueCodes.RegistryFileInvalid,
                        ThemeStudioIssueLevel.Error,
                        $"不支持的扩展名：{Path.GetFileName(path)}",
                        path),
                ]);
        }

        string json;
        try
        {
            var info = new FileInfo(path);
            if (!info.Exists)
            {
                return ThemeStudioOperationResult.Fail(
                    "文件不存在",
                    [Issue(ThemeIssueCodes.RegistryFileUnreadable, ThemeStudioIssueLevel.Error, path, path)]);
            }

            if (info.Length > ThemePackageJson.MaxDocumentBytes)
            {
                return ThemeStudioOperationResult.Fail(
                    "主题包过大",
                    [
                        Issue(
                            ThemeIssueCodes.InstallTooLarge,
                            ThemeStudioIssueLevel.Error,
                            $"文件 {info.Length} 字节，超过 {ThemePackageJson.MaxDocumentBytes} 字节上限",
                            path),
                    ]);
            }

            json = File.ReadAllText(path, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false, throwOnInvalidBytes: true));
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or DecoderFallbackException or NotSupportedException)
        {
            return ThemeStudioOperationResult.Fail(
                "主题包无法读取",
                [
                    Issue(
                        ThemeIssueCodes.RegistryFileUnreadable,
                        ThemeStudioIssueLevel.Error,
                        exception.Message,
                        path),
                ]);
        }

        return await ImportAsync(json, Path.GetFileName(path), overwrite, ct).ConfigureAwait(false);
    }

    /// <inheritdoc />
    public async Task<string?> ExportAsync(string themeId, CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ct.ThrowIfCancellationRequested();
        try
        {
            return await _registry.ExportAsync(themeId).ConfigureAwait(false);
        }
        catch (Exception exception) when (exception is ThemePackageException or InvalidOperationException)
        {
            _lastError = exception.Message;
            return null;
        }
    }

    /// <inheritdoc />
    public async Task<ThemeStudioOperationResult> DeleteAsync(string themeId, CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ct.ThrowIfCancellationRequested();

        var descriptor = _registry.Find(themeId);
        if (descriptor is null)
        {
            return ThemeStudioOperationResult.Fail(
                "主题不存在",
                [Issue(ThemeIssueCodes.ThemeNotFound, ThemeStudioIssueLevel.Error, themeId, themeId)]);
        }

        if (descriptor.Kind == ThemeKind.BuiltIn)
        {
            return ThemeStudioOperationResult.Fail(
                "内置主题不可删除",
                [
                    Issue(
                        ThemeIssueCodes.RegistryIdReserved,
                        ThemeStudioIssueLevel.Error,
                        $"'{themeId}' 是内置主题，只能复制或另存为",
                        "descriptor.kind"),
                ]);
        }

        var wasApplied = string.Equals(_themeService.Settings.ThemeId, themeId, StringComparison.Ordinal);
        if (wasApplied)
        {
            // Never leave the app pointing at a deleted theme: restore the shipped default first.
            CancelSession();
            _localDraft = null;
            await _themeService.ApplyAsync(ThemeDefaults.DefaultThemeId, ct).ConfigureAwait(false);
        }

        if (!await _registry.UninstallAsync(themeId).ConfigureAwait(false))
        {
            return ThemeStudioOperationResult.Fail(
                "主题文件删除失败",
                [
                    Issue(
                        ThemeIssueCodes.RegistryIoFailed,
                        ThemeStudioIssueLevel.Error,
                        $"'{themeId}' 无法删除（文件被占用或无权限）",
                        null),
                ]);
        }

        await _registry.RefreshAsync(ct).ConfigureAwait(false);
        _favorites.Remove(themeId);
        _favoritesStore.Save(_favorites);
        CaptureServiceIssues();
        RaiseChanged();
        return ThemeStudioOperationResult.Ok($"已删除主题「{themeId}」");
    }

    /// <inheritdoc />
    public async Task<ThemeStudioOperationResult> DuplicateAsync(
        string themeId,
        string newName,
        CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ct.ThrowIfCancellationRequested();

        if (!TryLoad(themeId, out var source))
        {
            return ThemeStudioOperationResult.Fail(
                "主题不存在",
                [Issue(ThemeIssueCodes.ThemeNotFound, ThemeStudioIssueLevel.Error, themeId, themeId)]);
        }

        var package = DeriveUserPackage(source, newName, source.Descriptor.Author, source.Descriptor.Tags);
        var installed = await InstallPackageAsync(package, ct).ConfigureAwait(false);
        if (!installed.IsValid)
        {
            return ThemeStudioOperationResult.Fail("复制失败", installed.Issues.Select(ThemeStudioIssue.From));
        }

        await _registry.RefreshAsync(ct).ConfigureAwait(false);
        RaiseChanged();
        return ThemeStudioOperationResult.Ok($"已复制为「{package.Descriptor.Id}」");
    }

    /// <inheritdoc />
    public async Task<ThemeStudioOperationResult> SaveDraftAsUserThemeAsync(
        string name,
        string? author,
        IReadOnlyList<string> tags,
        CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ct.ThrowIfCancellationRequested();

        var source = _localDraft ?? DraftPackage ?? AppliedPackage;
        var package = DeriveUserPackage(source, name, author, tags);
        var installed = await InstallPackageAsync(package, ct).ConfigureAwait(false);
        if (!installed.IsValid)
        {
            return ThemeStudioOperationResult.Fail("另存为失败", installed.Issues.Select(ThemeStudioIssue.From));
        }

        await _registry.RefreshAsync(ct).ConfigureAwait(false);
        _localDraft = _registry.Load(package.Descriptor.Id);
        RaiseChanged();
        return ThemeStudioOperationResult.Ok($"已保存为「{package.Descriptor.Id}」");
    }

    /// <inheritdoc />
    public bool IsFavorite(string themeId) =>
        !string.IsNullOrWhiteSpace(themeId) && _favorites.Contains(themeId);

    /// <inheritdoc />
    public Task<ThemeStudioOperationResult> ToggleFavoriteAsync(string themeId, CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ct.ThrowIfCancellationRequested();

        if (_registry.Find(themeId) is null)
        {
            return Task.FromResult(ThemeStudioOperationResult.Fail(
                "主题不存在",
                [Issue(ThemeIssueCodes.ThemeNotFound, ThemeStudioIssueLevel.Error, themeId, themeId)]));
        }

        var added = _favorites.Add(themeId);
        if (!added)
        {
            _favorites.Remove(themeId);
        }

        var saved = _favoritesStore.Save(_favorites);
        RaiseChanged();
        return Task.FromResult(saved
            ? ThemeStudioOperationResult.Ok(added ? "已加入收藏" : "已取消收藏")
            : ThemeStudioOperationResult.Fail(
                "收藏未能保存",
                [
                    Issue(
                        "favorites.io-failed",
                        ThemeStudioIssueLevel.Warning,
                        $"无法写入 {_favoritesStore.FilePath}",
                        _favoritesStore.FilePath),
                ]));
    }

    /// <inheritdoc />
    public async Task<ThemeStudioOperationResult> ResetToDefaultAsync(
        bool clearUserThemes,
        CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ct.ThrowIfCancellationRequested();

        var removed = new List<string>();
        var issues = new List<ThemeStudioIssue>();
        if (clearUserThemes)
        {
            foreach (var descriptor in _registry.All.Where(static descriptor => descriptor.Kind == ThemeKind.User).ToArray())
            {
                if (await _registry.UninstallAsync(descriptor.Id).ConfigureAwait(false))
                {
                    removed.Add(descriptor.Id);
                }
                else
                {
                    issues.Add(Issue(
                        ThemeIssueCodes.RegistryIoFailed,
                        ThemeStudioIssueLevel.Warning,
                        $"'{descriptor.Id}' 删除失败",
                        null));
                }
            }

            await _registry.RefreshAsync(ct).ConfigureAwait(false);
            _favorites.Clear();
            _favoritesStore.Save(_favorites);
        }

        CancelSession();
        _localDraft = null;
        await _themeService.ResetToDefaultAsync().ConfigureAwait(false);
        CaptureServiceIssues();
        RaiseChanged();

        var message = removed.Count == 0
            ? "已恢复出厂默认（主题 / 外观 / 密度 / 布局）"
            : $"已恢复出厂默认，并清除 {removed.Count} 个用户主题";
        return ThemeStudioOperationResult.OkWith(message, issues);
    }

    /// <inheritdoc />
    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;
        CancelSession();
        _themeService.Dispose();
    }

    // ------------------------------------------------------------------ internals

    private string BuildCapabilityNote()
    {
        var notes = new List<string>(2);
        if (_isSandbox())
        {
            notes.Add("STUB 沙箱：主题写入临时目录，仅用于截图/单测，不代表生产持久化路径。");
        }

        notes.Add("跟随系统强调色：IThemeService 无该 setter，V1 仅在工作室的作用域调色板生效（GAP-3 已报 Lead）。");
        return string.Join(" ", notes);
    }

    private void EnsureSession()
    {
        if (_session is { State: ThemePreviewState.Active })
        {
            return;
        }

        _session = (ThemePreviewSession)_themeService.PreviewEngine.Begin();
    }

    private void CancelSession()
    {
        if (_session is null)
        {
            return;
        }

        try
        {
            _session.Cancel();
        }
        catch (Exception exception) when (exception is ThemePreviewException or InvalidOperationException)
        {
            // The engine restores the applied layer on its own failure path; the surface re-reads
            // Settings/Current anyway, so a rollback hiccup must not break the UI.
            _lastError = exception.Message;
        }

        _session = null;
    }

    private void CaptureServiceIssues()
    {
        _lastIssues.Clear();
        _lastIssues.AddRange(_themeService.LastIssues.Select(ThemeStudioIssue.From));
    }

    private ThemePackage ResolvePackage(string themeId)
    {
        if (TryLoad(themeId, out var package))
        {
            return package;
        }

        var fallback = BuiltInThemes.All.FirstOrDefault(static candidate =>
            string.Equals(candidate.Descriptor.Id, ThemeDefaults.DefaultThemeId, StringComparison.Ordinal))
            ?? BuiltInThemes.All.FirstOrDefault();

        return fallback ?? throw new ThemePackageException(
            "no built-in theme is available; the theme catalog is unusable",
            [ThemeValidationIssue.Error(ThemeIssueCodes.ThemeNotFound, "no built-in theme is available")]);
    }

    private bool TryLoad(string themeId, out ThemePackage package)
    {
        package = null!;
        if (string.IsNullOrWhiteSpace(themeId) || _registry.Find(themeId) is null)
        {
            return false;
        }

        try
        {
            package = _registry.Load(themeId);
            return true;
        }
        catch (ThemePackageException exception)
        {
            _lastError = exception.Message;
            return false;
        }
    }

    private async Task<ThemeValidationResult> InstallJsonAsync(string json, CancellationToken ct)
    {
        ct.ThrowIfCancellationRequested();
        using var stream = new MemoryStream(new UTF8Encoding(false).GetBytes(json), writable: false);
        return await _registry.InstallAsync(stream, ct).ConfigureAwait(false);
    }

    private Task<ThemeValidationResult> InstallPackageAsync(ThemePackage package, CancellationToken ct) =>
        InstallJsonAsync(ThemePackageJson.Write(package), ct);

    private async Task<(bool Success, string? ThemeId, IReadOnlyList<ThemeStudioIssue> Issues)> InstallDraftAsThemeAsync(
        ThemePackage draft,
        CancellationToken ct)
    {
        var descriptor = draft.Descriptor;
        var keepId = descriptor.Kind == ThemeKind.User && _registry.Find(descriptor.Id) is not null;
        var package = keepId
            ? draft with { Descriptor = descriptor with { Kind = ThemeKind.User } }
            : DeriveUserPackage(draft, descriptor.Name, descriptor.Author, descriptor.Tags);

        var result = await InstallPackageAsync(package, ct).ConfigureAwait(false);
        var issues = result.Issues.Select(ThemeStudioIssue.From).ToArray();
        if (!result.IsValid)
        {
            return (false, null, issues);
        }

        await _registry.RefreshAsync(ct).ConfigureAwait(false);
        var id = package.Descriptor.Id;
        if (_registry.Find(id) is null)
        {
            return (false, null, [
                Issue("theme.not-found", ThemeStudioIssueLevel.Error, $"定制主题 '{id}' 安装后不可见", "themeId"),
            ]);
        }

        return (true, id, issues);
    }

    private ThemePackage DeriveUserPackage(
        ThemePackage source,
        string name,
        string? author,
        IReadOnlyList<string> tags)
    {
        var newId = MakeUniqueThemeId(name);
        var descriptor = source.Descriptor with
        {
            Id = newId,
            Name = string.IsNullOrWhiteSpace(name) ? source.Descriptor.Name + " 自定义" : name.Trim(),
            Author = string.IsNullOrWhiteSpace(author) ? source.Descriptor.Author : author.Trim(),
            Kind = ThemeKind.User,
            Tags = NormalizeTags(tags),
            Version = "1.0.0",
        };

        return source with
        {
            Descriptor = descriptor,
            Metadata = source.Metadata with { Generator = "newmanga-theme-studio/1" },
        };
    }

    private static IReadOnlyList<string> NormalizeTags(IReadOnlyList<string>? tags)
    {
        if (tags is null || tags.Count == 0)
        {
            return ["custom"];
        }

        var cleaned = tags
            .Where(static tag => !string.IsNullOrWhiteSpace(tag))
            .Select(static tag => tag.Trim())
            .Distinct(StringComparer.Ordinal)
            .Take(16)
            .ToArray();
        return cleaned.Length == 0 ? ["custom"] : cleaned;
    }

    /// <summary>Builds a unique, validator-legal theme id from a display name.</summary>
    private string MakeUniqueThemeId(string name)
    {
        var slug = Slugify(name);
        var candidate = "custom-" + slug;
        var index = 2;
        while (_registry.Find(candidate) is not null || BuiltInThemes.All.Any(package =>
                   string.Equals(package.Descriptor.Id, candidate, StringComparison.Ordinal)))
        {
            candidate = $"custom-{slug}-{index}";
            index++;
        }

        if (candidate.Length > 64)
        {
            candidate = candidate[..64].TrimEnd('-');
        }

        return candidate;
    }

    private static string Slugify(string name)
    {
        var builder = new StringBuilder(24);
        foreach (var character in (name ?? string.Empty).ToLowerInvariant())
        {
            if (character is >= 'a' and <= 'z' or >= '0' and <= '9')
            {
                builder.Append(character);
            }
            else if (builder.Length > 0 && builder[^1] != '-')
            {
                builder.Append('-');
            }
        }

        var slug = builder.ToString().Trim('-');
        return slug.Length == 0 ? "theme" : slug.Length > 40 ? slug[..40].Trim('-') : slug;
    }

    private static bool IsAcceptedThemeFile(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
        {
            return false;
        }

        var extension = Path.GetExtension(path);
        return string.Equals(extension, ThemeDefaults.ThemeFileExtension, StringComparison.OrdinalIgnoreCase) ||
               string.Equals(extension, ThemeDefaults.ThemeJsonExtension, StringComparison.OrdinalIgnoreCase);
    }

    private static IReadOnlyList<ThemeStudioMigrationNotice> BuildMigrationNotices(
        IEnumerable<ThemeValidationIssue> issues)
    {
        var notices = new List<ThemeStudioMigrationNotice>();
        foreach (var issue in issues)
        {
            if (!string.Equals(issue.Code, ThemeIssueCodes.SettingsLegacyThemeId, StringComparison.Ordinal) &&
                !string.Equals(issue.Code, ThemeIssueCodes.SettingsUnknownThemeId, StringComparison.Ordinal))
            {
                continue;
            }

            var notice = new ThemeStudioMigrationNotice(ExtractLegacyId(issue.Message), issue.Message);
            if (!notices.Any(existing => existing.LegacyId == notice.LegacyId && existing.Message == notice.Message))
            {
                notices.Add(notice);
            }
        }

        return notices;
    }

    /// <summary>Pulls the retired theme id out of the engine's migration message (display only).</summary>
    private static string ExtractLegacyId(string message)
    {
        // The engine message shape is "retired theme 'Display Name' (legacy-id) was migrated ...", so the
        // parenthesised token carries the id; fall back to the first quoted token for other shapes.
        var parenthesised = System.Text.RegularExpressions.Regex.Match(message, @"\(([^)]+)\)");
        if (parenthesised.Success)
        {
            return parenthesised.Groups[1].Value;
        }

        var quoted = System.Text.RegularExpressions.Regex.Match(message, "'([^']+)'");
        return quoted.Success ? quoted.Groups[1].Value : "themeId";
    }

    private static ThemeStudioValidationReport BuildStartupIssues(
        IReadOnlyList<ThemeStudioIssue> serviceIssues,
        IReadOnlyList<ThemeValidationIssue> catalogIssues)
    {
        var issues = new List<ThemeStudioIssue>(serviceIssues);
        issues.AddRange(catalogIssues.Select(ThemeStudioIssue.From));
        return ThemeStudioValidationReport.From(issues);
    }

    private static ThemeStudioIssue Issue(
        string code,
        ThemeStudioIssueLevel level,
        string? message,
        string? path = null) =>
        new(code, level, message ?? code, path, ThemeStudioSuggestions.For(code));

    private void RaiseChanged() => Changed?.Invoke(this, EventArgs.Empty);
}
