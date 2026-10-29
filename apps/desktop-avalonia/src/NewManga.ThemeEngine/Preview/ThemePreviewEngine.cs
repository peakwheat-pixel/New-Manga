namespace NewManga.ThemeEngine;

/// <summary>Lifecycle state of one preview session.</summary>
public enum ThemePreviewState
{
    /// <summary>Session accepts <see cref="ThemePreviewSession.Update"/> and can be committed/cancelled.</summary>
    Active,

    /// <summary>Session was committed; later dispose does not roll back.</summary>
    Committed,

    /// <summary>Session was cancelled (rolled back to its baseline).</summary>
    Cancelled,

    /// <summary>Session object was disposed.</summary>
    Disposed,
}

/// <summary>What changed in a preview session.</summary>
public enum ThemePreviewChangeKind
{
    /// <summary>A session began; the payload carries the baseline settings.</summary>
    Began,

    /// <summary>The session theme changed; the payload carries the pending settings.</summary>
    Updated,

    /// <summary>The session was committed; the payload carries the applied settings.</summary>
    Committed,

    /// <summary>The session was cancelled; the payload carries the baseline settings to restore.</summary>
    Cancelled,
}

/// <summary>Preview change notification consumed by the service/UI that applies palettes.</summary>
public sealed class ThemePreviewChangedEventArgs : EventArgs
{
    /// <summary>Creates the event payload.</summary>
    public ThemePreviewChangedEventArgs(
        ThemePreviewChangeKind kind,
        ThemeSettings settings,
        ThemeDescriptor? theme,
        ThemePreviewSession session)
    {
        Kind = kind;
        Settings = settings;
        Theme = theme;
        Session = session;
    }

    /// <summary>What happened.</summary>
    public ThemePreviewChangeKind Kind { get; }

    /// <summary>Session settings for Began/Updated/Committed; the baseline to restore for Cancelled.</summary>
    public ThemeSettings Settings { get; }

    /// <summary>Resolved descriptor for the settings' theme (null only for the shipped baseline).</summary>
    public ThemeDescriptor? Theme { get; }

    /// <summary>Session that raised the change.</summary>
    public ThemePreviewSession Session { get; }

    /// <summary>True when the session currently differs from its baseline.</summary>
    public bool HasChanges => Session.HasChanges;
}

/// <summary>
/// Pure-logic preview engine (contract §4 <c>IThemePreviewEngine</c>). A session records the settings
/// captured by <c>Begin()</c> as its rollback baseline, lets the caller switch the previewed theme, and
/// then either commits (the engine's current settings move to the previewed theme) or cancels (the
/// engine keeps the baseline). It never touches Avalonia resources or persistence: the service that
/// subscribes to <see cref="Changed"/> applies the palette, and the Theme Studio's "应用" step calls
/// <c>Commit()</c> followed by <c>IThemeService.ApplyAsync</c> (THEME_STUDIO_SPEC §4).
/// </summary>
public sealed class ThemePreviewEngine : IThemePreviewEngine
{
    private readonly object _gate = new();
    private readonly IThemeRegistry _registry;
    private ThemePreviewSession? _active;

    /// <summary>Creates a preview engine over a theme catalog.</summary>
    public ThemePreviewEngine(IThemeRegistry registry)
    {
        _registry = registry ?? throw new ArgumentNullException(nameof(registry));
        CurrentSettings = ThemeDefaults.Settings;
    }

    /// <summary>Raised for every session transition so consumers can apply/restore palettes.</summary>
    public event EventHandler<ThemePreviewChangedEventArgs>? Changed;

    /// <summary>The committed settings (the preview session never mutates these until <c>Commit()</c>).</summary>
    public ThemeSettings CurrentSettings { get; private set; }

    /// <summary>The session currently accepting updates, if any.</summary>
    public ThemePreviewSession? ActiveSession
    {
        get
        {
            lock (_gate)
            {
                return _active;
            }
        }
    }

    /// <summary>
    /// Seeds the engine with the settings that are actually applied/persisted (service startup and
    /// service-side <c>ApplyAsync</c>). Rejected while a preview session is active.
    /// </summary>
    public void SetCurrentSettings(ThemeSettings settings)
    {
        ArgumentNullException.ThrowIfNull(settings);
        lock (_gate)
        {
            if (_active is not null)
            {
                throw new InvalidOperationException(
                    "cannot change the applied settings while a preview session is active; commit or cancel it first");
            }

            CurrentSettings = settings;
        }
    }

    /// <summary>
    /// Begins a session. Any session still active is cancelled (rolled back) first — a second
    /// <c>Begin()</c> means the UI left the previous session without closing it.
    /// </summary>
    public IThemePreviewSession Begin()
    {
        ThemePreviewSession session;
        ThemePreviewSession? previous;
        lock (_gate)
        {
            previous = _active;
            _active = null;
            session = new ThemePreviewSession(this, CurrentSettings);
            _active = session;
        }

        previous?.Cancel();

        Raise(new ThemePreviewChangedEventArgs(
            ThemePreviewChangeKind.Began,
            session.Baseline,
            ResolveOrNull(session.Baseline.ThemeId),
            session));
        return session;
    }

    internal ThemeDescriptor? ResolveOrNull(string themeId) => _registry.Find(themeId);

    internal ThemeDescriptor RequireTheme(string themeId) =>
        _registry.Find(themeId) ?? throw new ThemePreviewException(
            $"theme '{themeId}' is not installed",
            [ThemeValidationIssue.Error(
                ThemeIssueCodes.PreviewThemeUnknown,
                $"theme '{themeId}' is not installed",
                "themeId")]);

    internal void Raise(ThemePreviewChangedEventArgs args) => Changed?.Invoke(this, args);

    internal void SetCommitted(ThemePreviewSession session)
    {
        lock (_gate)
        {
            CurrentSettings = session.SessionSettings;
            if (ReferenceEquals(_active, session))
            {
                _active = null;
            }
        }
    }

    internal void ClearActive(ThemePreviewSession session)
    {
        lock (_gate)
        {
            if (ReferenceEquals(_active, session))
            {
                _active = null;
            }
        }
    }
}

/// <summary>
/// One preview session. Session rules: <c>Update</c> is only legal while active; <c>Commit</c> moves the
/// engine's current settings to the session theme and is idempotent afterwards (a second commit is a
/// no-op, cancel can no longer roll back); <c>Cancel</c> restores the baseline and is idempotent;
/// disposing an uncommitted session cancels it.
/// </summary>
public sealed class ThemePreviewSession : IThemePreviewSession
{
    private readonly ThemePreviewEngine _engine;
    private readonly object _gate = new();
    private string? _pendingThemeId;
    private ThemePreviewState _state = ThemePreviewState.Active;

    internal ThemePreviewSession(ThemePreviewEngine engine, ThemeSettings baseline)
    {
        _engine = engine;
        Baseline = baseline;
    }

    /// <summary>Settings captured by <c>Begin()</c>; cancelling rolls back to exactly these.</summary>
    public ThemeSettings Baseline { get; }

    /// <summary>Theme the session currently previews, or null when it still shows the baseline theme.</summary>
    public string? PendingThemeId
    {
        get
        {
            lock (_gate)
            {
                return _pendingThemeId;
            }
        }
    }

    /// <summary>Settings the session would apply on commit.</summary>
    public ThemeSettings SessionSettings
    {
        get
        {
            lock (_gate)
            {
                return _pendingThemeId is null ? Baseline : Baseline with { ThemeId = _pendingThemeId };
            }
        }
    }

    /// <summary>True when the session differs from its baseline theme.</summary>
    public bool HasChanges
    {
        get
        {
            lock (_gate)
            {
                return _pendingThemeId is not null &&
                       !string.Equals(_pendingThemeId, Baseline.ThemeId, StringComparison.Ordinal);
            }
        }
    }

    /// <summary>Current lifecycle state.</summary>
    public ThemePreviewState State
    {
        get
        {
            lock (_gate)
            {
                return _state;
            }
        }
    }

    /// <inheritdoc />
    public void Update(string themeId)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(themeId);
        ThemeDescriptor theme;
        lock (_gate)
        {
            ThrowIfDisposed();
            if (_state != ThemePreviewState.Active)
            {
                throw new InvalidOperationException($"preview session is {_state}; it no longer accepts updates");
            }

            theme = _engine.RequireTheme(themeId);
            _pendingThemeId = themeId;
        }

        _engine.Raise(new ThemePreviewChangedEventArgs(
            ThemePreviewChangeKind.Updated,
            SessionSettings,
            theme,
            this));
    }

    /// <inheritdoc />
    public void Commit()
    {
        lock (_gate)
        {
            ThrowIfDisposed();
            if (_state == ThemePreviewState.Committed)
            {
                return;
            }

            if (_state != ThemePreviewState.Active)
            {
                throw new InvalidOperationException($"preview session is {_state}; it cannot be committed");
            }

            _state = ThemePreviewState.Committed;
        }

        _engine.SetCommitted(this);
        _engine.Raise(new ThemePreviewChangedEventArgs(
            ThemePreviewChangeKind.Committed,
            SessionSettings,
            _engine.ResolveOrNull(SessionSettings.ThemeId),
            this));
    }

    /// <inheritdoc />
    public void Cancel()
    {
        lock (_gate)
        {
            if (_state is ThemePreviewState.Committed or ThemePreviewState.Cancelled or ThemePreviewState.Disposed)
            {
                return;
            }

            _state = ThemePreviewState.Cancelled;
        }

        _engine.ClearActive(this);
        _engine.Raise(new ThemePreviewChangedEventArgs(
            ThemePreviewChangeKind.Cancelled,
            Baseline,
            _engine.ResolveOrNull(Baseline.ThemeId),
            this));
    }

    /// <inheritdoc />
    public void Dispose()
    {
        bool cancelled;
        lock (_gate)
        {
            if (_state == ThemePreviewState.Disposed)
            {
                return;
            }

            cancelled = _state == ThemePreviewState.Active;
        }

        if (cancelled)
        {
            Cancel();
        }

        lock (_gate)
        {
            _state = ThemePreviewState.Disposed;
        }
    }

    private void ThrowIfDisposed()
    {
        if (_state == ThemePreviewState.Disposed)
        {
            throw new ObjectDisposedException(nameof(ThemePreviewSession));
        }
    }
}
