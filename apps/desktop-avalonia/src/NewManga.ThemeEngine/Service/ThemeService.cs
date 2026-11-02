namespace NewManga.ThemeEngine;

/// <summary>
/// The application-facing theme service (contract §4 <c>IThemeService</c>). It owns the state machine:
/// load persisted settings → migrate retired ids → resolve + validate the package → compose the
/// <c>Nm.*</c> theme layer → hand it to the <see cref="IThemeLayerSink"/> → persist settings → notify.
/// Any failure is recovered to the shipped <c>newmanga-default</c> (and, if even that cannot be applied,
/// to the design system's built-in layer) and surfaced through <see cref="LastError"/>/<see cref="LastIssues"/>:
/// the service never throws on the startup path (behavior 2) and never leaves a half-applied state.
/// <para>
/// The service also owns a <see cref="ThemePreviewEngine"/> and keeps the live preview in sync: preview
/// <c>Update</c> applies the session theme layer, <c>Cancel</c> restores the applied layer, and the
/// Theme Studio's "应用" step calls <c>Commit()</c> followed by <see cref="ApplyAsync"/> (THEME_STUDIO_SPEC §4).
/// Preview never mutates persisted settings or <see cref="Changed"/> semantics.
/// </para>
/// </summary>
public sealed class ThemeService : IThemeService, IDisposable
{
    private readonly object _gate = new();
    private readonly IThemeRegistry _registry;
    private readonly IThemePersistence _persistence;
    private readonly IThemeLayerSink _sink;
    private readonly IThemeValidator _validator;
    private readonly ThemePreviewEngine _previewEngine;
    private readonly ThemeDescriptor _fallbackDescriptor;

    private ThemeSettings _settings = ThemeDefaults.Settings;
    private IReadOnlyList<ThemeValidationIssue> _lastIssues = [];
    private string? _lastError;
    private bool _initialized;
    private bool _disposed;

    /// <summary>Creates the service over a catalog, the settings store and the application-layer sink.</summary>
    public ThemeService(
        IThemeRegistry registry,
        IThemePersistence persistence,
        IThemeLayerSink sink,
        IThemeValidator? validator = null)
    {
        _registry = registry ?? throw new ArgumentNullException(nameof(registry));
        _persistence = persistence ?? throw new ArgumentNullException(nameof(persistence));
        _sink = sink ?? throw new ArgumentNullException(nameof(sink));
        _validator = validator ?? ThemeValidator.Default;

        _previewEngine = new ThemePreviewEngine(_registry);
        _previewEngine.Changed += OnPreviewChanged;
        _sink.PlatformThemeChanged += OnPlatformThemeChanged;
        _fallbackDescriptor = ResolveDescriptor(ThemeDefaults.DefaultThemeId) ?? SyntheticDefaultDescriptor();
    }

    /// <inheritdoc />
    public event EventHandler? Changed;

    /// <inheritdoc />
    public ThemeDescriptor Current
    {
        get
        {
            lock (_gate)
            {
                return ResolveDescriptor(_settings.ThemeId) ?? _fallbackDescriptor;
            }
        }
    }

    /// <inheritdoc />
    public ThemeSettings Settings
    {
        get
        {
            lock (_gate)
            {
                return _settings;
            }
        }
    }

    /// <summary>The preview engine owned by this service (Theme Studio entry point).</summary>
    public ThemePreviewEngine PreviewEngine => _previewEngine;

    /// <summary>True once <see cref="InitializeAsync"/> completed successfully (or with a recovered state).</summary>
    public bool IsInitialized
    {
        get
        {
            lock (_gate)
            {
                return _initialized;
            }
        }
    }

    /// <summary>Last recoverable error (load, apply, save, sink), or null.</summary>
    public string? LastError
    {
        get
        {
            lock (_gate)
            {
                return _lastError;
            }
        }
    }

    /// <summary>Findings produced by the last initialize/apply/change (warnings explain recovered fallbacks).</summary>
    public IReadOnlyList<ThemeValidationIssue> LastIssues
    {
        get
        {
            lock (_gate)
            {
                return _lastIssues;
            }
        }
    }

    /// <inheritdoc />
    public async Task InitializeAsync(CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ct.ThrowIfCancellationRequested();

        // Registry refresh is best-effort: a broken user theme directory must not block startup.
        try
        {
            await _registry.RefreshAsync(ct).ConfigureAwait(true);
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
        {
        }

        lock (_gate)
        {
            if (_initialized)
            {
                return;
            }

            InitializeCore();
            _initialized = true;
        }

        RaiseChanged();
    }

    /// <inheritdoc />
    public Task<ThemeApplyResult> ApplyAsync(string themeId, CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ArgumentException.ThrowIfNullOrWhiteSpace(themeId);
        ct.ThrowIfCancellationRequested();

        ThemeApplyResult result;
        var changed = false;
        lock (_gate)
        {
            var issues = new List<ThemeValidationIssue>();
            result = ApplyThemeLocked(themeId, _settings.Appearance, issues);
            if (result.Success)
            {
                _settings = _settings with { ThemeId = result.AppliedThemeId ?? ThemeDefaults.DefaultThemeId };
                SyncPreviewEngineSettings(_settings);
                _lastError = TrySave(_settings, issues) ? null : _lastError;
                changed = true;
            }
            else
            {
                _lastError = _sink.LastError ?? "theme layer could not be applied";
            }

            _lastIssues = issues;
        }

        if (changed)
        {
            RaiseChanged();
        }

        return Task.FromResult(result);
    }

    /// <inheritdoc />
    public Task SetAppearanceAsync(AppearanceMode mode)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        var changed = false;
        lock (_gate)
        {
            var issues = new List<ThemeValidationIssue>();
            var previous = _settings;
            if (!_sink.SetAppearance(mode))
            {
                _lastError = _sink.LastError ?? "appearance could not be applied";
                _lastIssues = issues;
                return Task.CompletedTask;
            }

            var candidate = _settings with { Appearance = mode };
            if (!ApplyThemeLayerFor(candidate, issues))
            {
                // The appearance switch could not be paired with a palette swap: restore the previous
                // appearance so the live UI is never left on a half-switched state.
                _sink.SetAppearance(previous.Appearance);
                ApplyThemeLayerFor(previous, issues);
                _lastError = _sink.LastError ?? "theme layer could not follow the appearance change";
                _lastIssues = issues;
                return Task.CompletedTask;
            }

            _settings = candidate;
            SyncPreviewEngineSettings(candidate);
            _lastError = TrySave(candidate, issues) ? null : _lastError;
            _lastIssues = issues;
            changed = true;
        }

        if (changed)
        {
            RaiseChanged();
        }

        return Task.CompletedTask;
    }

    /// <inheritdoc />
    public Task SetContrastAsync(ContrastMode mode)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        var changed = false;
        lock (_gate)
        {
            var issues = new List<ThemeValidationIssue>();
            if (!_sink.SetContrast(mode))
            {
                _lastError = _sink.LastError ?? "contrast could not be applied";
                _lastIssues = issues;
                return Task.CompletedTask;
            }

            _settings = _settings with { Contrast = mode };
            SyncPreviewEngineSettings(_settings);
            _lastError = TrySave(_settings, issues) ? null : _lastError;
            _lastIssues = issues;
            changed = true;
        }

        if (changed)
        {
            RaiseChanged();
        }

        return Task.CompletedTask;
    }

    /// <inheritdoc />
    public Task SetLayoutAsync(LayoutProfile layout)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        ArgumentNullException.ThrowIfNull(layout);

        lock (_gate)
        {
            var issues = new List<ThemeValidationIssue>();
            _settings = _settings with { Layout = layout };
            SyncPreviewEngineSettings(_settings);
            _lastError = TrySave(_settings, issues) ? null : _lastError;
            _lastIssues = issues;
        }

        RaiseChanged();
        return Task.CompletedTask;
    }

    /// <inheritdoc />
    public Task SetReducedMotionAsync(bool enabled)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        var changed = false;
        lock (_gate)
        {
            var issues = new List<ThemeValidationIssue>();
            if (!_sink.SetReducedMotion(enabled))
            {
                _lastError = _sink.LastError ?? "reduced-motion could not be applied";
                _lastIssues = issues;
                return Task.CompletedTask;
            }

            _settings = _settings with { ReducedMotion = enabled };
            SyncPreviewEngineSettings(_settings);
            _lastError = TrySave(_settings, issues) ? null : _lastError;
            _lastIssues = issues;
            changed = true;
        }

        if (changed)
        {
            RaiseChanged();
        }

        return Task.CompletedTask;
    }

    /// <inheritdoc />
    public Task ResetToDefaultAsync()
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        lock (_gate)
        {
            var issues = new List<ThemeValidationIssue>();
            _sink.SetContrast(ContrastMode.Standard);
            _sink.SetReducedMotion(false);
            _sink.SetAppearance(AppearanceMode.System);

            var result = ApplyThemeLocked(
                ThemeDefaults.DefaultThemeId,
                AppearanceMode.System,
                issues);

            _settings = ThemeDefaults.Settings;
            SyncPreviewEngineSettings(_settings);
            var saved = TrySave(_settings, issues);
            _lastError = result.Success && saved ? null : _sink.LastError ?? _lastError ?? "default theme layer could not be applied";
            _lastIssues = issues;
        }

        RaiseChanged();
        return Task.CompletedTask;
    }

    /// <summary>Detaches from the preview engine; the live application state is left as-is.</summary>
    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        lock (_gate)
        {
            if (_disposed)
            {
                return;
            }

            _disposed = true;
        }

        _previewEngine.Changed -= OnPreviewChanged;
        _sink.PlatformThemeChanged -= OnPlatformThemeChanged;
    }

    private void InitializeCore()
    {
        var issues = new List<ThemeValidationIssue>();

        ThemeSettings loaded;
        try
        {
            loaded = _persistence.Load();
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or InvalidOperationException)
        {
            // IThemePersistence promises not to throw on load, but a third-party implementation might.
            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.SettingsIoFailed,
                $"settings could not be loaded ({exception.Message}); shipped defaults are used"));
            loaded = ThemeDefaults.Settings;
        }

        if (_persistence is ThemeSettingsStore store)
        {
            issues.AddRange(store.LastLoadIssues);
        }

        var migrated = LegacyThemeMigration.Migrate(loaded, id => _registry.Find(id) is not null);
        issues.AddRange(migrated.Issues);

        // The persisted appearance/contrast/motion must reach the surface before (and independently of)
        // the palette, so a reloaded session shows the same shell state as before.
        ApplyAuxiliarySettings(migrated.Settings, issues);

        var result = ApplyThemeLocked(migrated.Settings.ThemeId, migrated.Settings.Appearance, issues);
        _settings = result.Success
            ? migrated.Settings with { ThemeId = result.AppliedThemeId ?? ThemeDefaults.DefaultThemeId }
            : migrated.Settings with { ThemeId = ThemeDefaults.DefaultThemeId };

        var needsSave = migrated.Changed || (_persistence is ThemeSettingsStore persistedStore && persistedStore.NeedsSave);
        if (needsSave || _settings != migrated.Settings)
        {
            TrySave(_settings, issues);
        }

        SyncPreviewEngineSettings(_settings);
        _lastIssues = issues;
        _lastError = result.Success
            ? _lastError
            : _sink.LastError ?? "theme layer could not be applied";
    }

    private void ApplyAuxiliarySettings(ThemeSettings settings, List<ThemeValidationIssue> issues)
    {
        if (!_sink.SetAppearance(settings.Appearance))
        {
            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.ThemeLayerApplyFailed,
                _sink.LastError ?? "persisted appearance could not be applied"));
        }

        if (!_sink.SetContrast(settings.Contrast))
        {
            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.ThemeLayerApplyFailed,
                _sink.LastError ?? "persisted contrast could not be applied"));
        }

        if (!_sink.SetReducedMotion(settings.ReducedMotion))
        {
            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.ThemeLayerApplyFailed,
                _sink.LastError ?? "persisted reduced-motion could not be applied"));
        }
    }

    /// <summary>
    /// Resolves, validates and applies one theme, falling back to the shipped default when anything
    /// fails. Never throws for theme/content problems; returns a result describing what was applied.
    /// </summary>
    private ThemeApplyResult ApplyThemeLocked(
        string themeId,
        AppearanceMode appearance,
        List<ThemeValidationIssue> issues)
    {
        ThemePackage? package;
        try
        {
            package = LoadAndValidate(themeId, issues, out var isFallback);
            if (isFallback || package is null)
            {
                return ApplyDefaultFallback(themeId, appearance, issues);
            }
        }
        catch (Exception exception) when (exception is ThemeException or IOException or UnauthorizedAccessException)
        {
            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.ThemeNotFound,
                $"theme '{themeId}' could not be loaded ({exception.Message})"));
            return ApplyDefaultFallback(themeId, appearance, issues);
        }

        var variant = ThemePaletteComposer.ResolveVariant(appearance, _sink.IsPlatformLight);
        if (!TryApplyPackageLayer(package, variant, themeId, issues))
        {
            return ApplyDefaultFallback(themeId, appearance, issues);
        }

        return new ThemeApplyResult(true, themeId, issues, Recovered: false);
    }

    private ThemePackage? LoadAndValidate(string themeId, List<ThemeValidationIssue> issues, out bool isFallback)
    {
        isFallback = false;
        if (_registry.Find(themeId) is null)
        {
            issues.Add(ThemeValidationIssue.Warning(
                ThemeIssueCodes.ThemeNotFound,
                $"theme '{themeId}' is not installed; the shipped default theme is applied"));
            isFallback = true;
            return null;
        }

        ThemePackage package;
        try
        {
            package = _registry.Load(themeId);
        }
        catch (ThemeException exception)
        {
            issues.AddRange(exception.Issues);
            isFallback = true;
            return null;
        }

        var validation = _validator.Validate(package);
        if (!validation.IsValid)
        {
            issues.AddRange(validation.Errors);
            isFallback = true;
            return null;
        }

        // Validation warnings (e.g. contrast edge surfaces) are informative for the caller but do not
        // block application.
        issues.AddRange(validation.Warnings);
        return package;
    }

    private bool TryApplyPackageLayer(
        ThemePackage package,
        PaletteVariant variant,
        string paletteId,
        List<ThemeValidationIssue> issues)
    {
        IReadOnlyDictionary<string, object?> layer;
        try
        {
            layer = ThemePaletteComposer.Compose(package, variant);
        }
        catch (ThemeException exception)
        {
            issues.AddRange(exception.Issues);
            return false;
        }

        if (_sink.ApplyThemeLayer(layer, paletteId))
        {
            return true;
        }

        issues.Add(ThemeValidationIssue.Error(
            ThemeIssueCodes.ThemeLayerApplyFailed,
            _sink.LastError ?? $"theme layer for '{paletteId}' could not be applied"));
        return false;
    }

    private ThemeApplyResult ApplyDefaultFallback(
        string requestedThemeId,
        AppearanceMode appearance,
        List<ThemeValidationIssue> issues)
    {
        var variant = ThemePaletteComposer.ResolveVariant(appearance, _sink.IsPlatformLight);

        ThemePackage? defaultPackage = null;
        try
        {
            defaultPackage = BuiltInThemes.IsDefaultAvailable ? BuiltInThemes.Default : null;
        }
        catch (ThemeException)
        {
            defaultPackage = null;
        }

        var applied = false;
        if (defaultPackage is not null)
        {
            applied = TryApplyPackageLayer(defaultPackage, variant, ThemeDefaults.DefaultThemeId, issues);
        }

        if (!applied)
        {
            // The design system's shipped palette is semantically identical to the default theme: use it
            // as the last line of defence so the application still has a complete token set.
            applied = _sink.RevertToBuiltInLayer();
            if (!applied)
            {
                issues.Add(ThemeValidationIssue.Error(
                    ThemeIssueCodes.ThemeLayerApplyFailed,
                    _sink.LastError ?? "default theme layer and built-in fallback both failed"));
                return new ThemeApplyResult(false, null, issues, Recovered: false);
            }
        }

        issues.Add(ThemeValidationIssue.Warning(
            ThemeIssueCodes.ThemeFallbackApplied,
            $"theme '{requestedThemeId}' could not be applied; '{ThemeDefaults.DefaultThemeId}' was applied instead"));
        return new ThemeApplyResult(true, ThemeDefaults.DefaultThemeId, issues, Recovered: true);
    }

    /// <summary>
    /// Re-applies the palette for an already-accepted settings document (appearance switch, preview
    /// rollback). Returns false when the layer could not be applied and no fallback succeeded.
    /// </summary>
    private bool ApplyThemeLayerFor(ThemeSettings settings, List<ThemeValidationIssue> issues)
    {
        var result = ApplyThemeLocked(settings.ThemeId, settings.Appearance, issues);
        return result.Success;
    }

    /// <summary>
    /// Platform light/dark flip while following the system: recompose the current theme for the new
    /// variant. The appearance setting itself does not change, so no <see cref="Changed"/> is raised.
    /// </summary>
    private void OnPlatformThemeChanged(object? sender, EventArgs args)
    {
        lock (_gate)
        {
            if (_disposed || _settings.Appearance != AppearanceMode.System)
            {
                return;
            }

            var issues = new List<ThemeValidationIssue>();
            if (!ApplyThemeLayerFor(_settings, issues))
            {
                _lastError = _sink.LastError ?? "platform theme change could not be reflected";
            }

            _lastIssues = [.. _lastIssues, .. issues];
        }
    }

    /// <summary>
    /// Keeps the preview engine's baseline equal to the applied settings. If a session is still active
    /// (a consumer applied settings without committing the preview), it is cancelled defensively —
    /// otherwise its rollback baseline would be stale and could later undo a committed theme.
    /// </summary>
    private void SyncPreviewEngineSettings(ThemeSettings settings)
    {
        try
        {
            _previewEngine.SetCurrentSettings(settings);
        }
        catch (InvalidOperationException)
        {
            _previewEngine.ActiveSession?.Cancel();
            _previewEngine.SetCurrentSettings(settings);
        }
    }

    private void OnPreviewChanged(object? sender, ThemePreviewChangedEventArgs args)
    {
        lock (_gate)
        {
            if (_disposed)
            {
                return;
            }

            var settings = args.Kind == ThemePreviewChangeKind.Cancelled ? _settings : args.Settings;
            var issues = new List<ThemeValidationIssue>();
            if (!ApplyThemeLayerFor(settings, issues))
            {
                _lastError = _sink.LastError ?? "preview theme layer could not be applied";
            }

            _lastIssues = [.. _lastIssues, .. issues];
        }
    }

    private ThemeDescriptor? ResolveDescriptor(string themeId) => _registry.Find(themeId);

    /// <summary>Persists settings, recording a warning instead of throwing; returns false on IO failure.</summary>
    private bool TrySave(ThemeSettings settings, List<ThemeValidationIssue> issues)
    {
        try
        {
            _persistence.SaveAsync(settings).GetAwaiter().GetResult();
            return true;
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or NotSupportedException)
        {
            var message = $"theme settings could not be saved ({exception.Message})";
            _lastError = message;
            issues.Add(ThemeValidationIssue.Warning(ThemeIssueCodes.SettingsIoFailed, message));
            return false;
        }
    }

    private void RaiseChanged() => Changed?.Invoke(this, EventArgs.Empty);

    private static ThemeDescriptor SyntheticDefaultDescriptor() => new(
        ThemeDefaults.DefaultThemeId,
        "New Manga Default",
        "0.0.0",
        "New Manga",
        null,
        ThemeKind.BuiltIn,
        [],
        SupportsLight: true,
        SupportsDark: true,
        PreviewHint: null);
}
