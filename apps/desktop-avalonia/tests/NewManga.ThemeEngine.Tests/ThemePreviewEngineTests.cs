using NewManga.ThemeEngine;

namespace NewManga.ThemeEngine.Tests;

/// <summary>
/// Preview session state machine: baseline capture, update, commit (applied settings move) and cancel
/// (complete rollback), including misuse and re-entrance rules. The engine is pure logic — palette
/// application and persistence belong to the service, so these tests assert observable session state
/// and the event sequence.
/// </summary>
public sealed class ThemePreviewEngineTests : IDisposable
{
    private readonly TempDirectory _temp = new();
    private readonly ThemeRegistry _registry;
    private readonly ThemePreviewEngine _engine;
    private readonly List<(ThemePreviewChangeKind Kind, string ThemeId, bool HasChanges)> _events = [];

    public ThemePreviewEngineTests()
    {
        _registry = new ThemeRegistry(_temp.File("themes"));
        _registry.InstallAsync(ThemeFixtures.Stream(
            ThemeFixtures.AsUser(ThemeFixtures.DefaultPackage, "ocean", "Ocean"))).GetAwaiter().GetResult();
        _engine = new ThemePreviewEngine(_registry);
        _engine.Changed += (_, args) => _events.Add((args.Kind, args.Settings.ThemeId, args.HasChanges));
    }

    public void Dispose() => _temp.Dispose();

    [Fact]
    public void Begin_captures_the_current_settings_as_baseline()
    {
        using var session = (ThemePreviewSession)_engine.Begin();

        Assert.Equal(ThemePreviewState.Active, session.State);
        Assert.Equal(_engine.CurrentSettings, session.Baseline);
        Assert.Null(session.PendingThemeId);
        Assert.False(session.HasChanges);
        Assert.Same(session, _engine.ActiveSession);
        Assert.Single(_events);
        Assert.Equal((ThemePreviewChangeKind.Began, ThemeDefaults.DefaultThemeId, false), _events[0]);
    }

    [Fact]
    public void Update_previews_another_theme_without_touching_the_applied_settings()
    {
        using var session = (ThemePreviewSession)_engine.Begin();
        var appliedBefore = _engine.CurrentSettings;

        session.Update("ocean");

        Assert.Equal("ocean", session.PendingThemeId);
        Assert.Equal("ocean", session.SessionSettings.ThemeId);
        Assert.True(session.HasChanges);
        Assert.Equal(appliedBefore, _engine.CurrentSettings);
        Assert.Equal(ThemePreviewChangeKind.Updated, _events[^1].Kind);
        Assert.Equal("ocean", _events[^1].ThemeId);
        Assert.True(_events[^1].HasChanges);
    }

    [Fact]
    public void Update_back_to_the_baseline_theme_clears_the_dirty_flag()
    {
        using var session = (ThemePreviewSession)_engine.Begin();
        session.Update("ocean");
        session.Update(ThemeDefaults.DefaultThemeId);

        Assert.False(session.HasChanges);
        Assert.False(_events[^1].HasChanges);
    }

    [Fact]
    public void Commit_moves_the_applied_settings_to_the_previewed_theme()
    {
        var session = (ThemePreviewSession)_engine.Begin();
        session.Update("ocean");

        session.Commit();

        Assert.Equal(ThemePreviewState.Committed, session.State);
        Assert.Equal("ocean", _engine.CurrentSettings.ThemeId);
        Assert.Null(_engine.ActiveSession);
        Assert.Equal(ThemePreviewChangeKind.Committed, _events[^1].Kind);
        Assert.Equal("ocean", _events[^1].ThemeId);

        session.Dispose();
        Assert.DoesNotContain(_events, change => change.Kind == ThemePreviewChangeKind.Cancelled);
    }

    [Fact]
    public void Cancel_rolls_back_to_the_baseline_settings()
    {
        var session = (ThemePreviewSession)_engine.Begin();
        session.Update("ocean");
        session.Cancel();

        Assert.Equal(ThemePreviewState.Cancelled, session.State);
        Assert.Equal(ThemeDefaults.DefaultThemeId, _engine.CurrentSettings.ThemeId);
        Assert.Null(_engine.ActiveSession);
        Assert.Equal(ThemePreviewChangeKind.Cancelled, _events[^1].Kind);
        Assert.Equal(ThemeDefaults.DefaultThemeId, _events[^1].ThemeId);

        session.Cancel();
        Assert.Single(_events, change => change.Kind == ThemePreviewChangeKind.Cancelled);
    }

    [Fact]
    public void Dispose_without_commit_cancels_the_session()
    {
        var session = _engine.Begin();
        session.Update("ocean");

        session.Dispose();

        Assert.Equal(ThemeDefaults.DefaultThemeId, _engine.CurrentSettings.ThemeId);
        Assert.Contains(_events, change => change.Kind == ThemePreviewChangeKind.Cancelled);
    }

    [Fact]
    public void Commit_is_idempotent_and_cancel_after_commit_is_a_no_op()
    {
        var session = (ThemePreviewSession)_engine.Begin();
        session.Update("ocean");
        session.Commit();
        session.Commit();
        session.Cancel();

        Assert.Equal("ocean", _engine.CurrentSettings.ThemeId);
        Assert.Single(_events, change => change.Kind == ThemePreviewChangeKind.Committed);
        Assert.DoesNotContain(_events, change => change.Kind == ThemePreviewChangeKind.Cancelled);
    }

    [Fact]
    public void Update_after_commit_throws()
    {
        var session = (ThemePreviewSession)_engine.Begin();
        session.Commit();

        var exception = Assert.Throws<InvalidOperationException>(() => session.Update("ocean"));
        Assert.Contains("Committed", exception.Message, StringComparison.Ordinal);
    }

    [Fact]
    public void Commit_after_cancel_throws()
    {
        var session = (ThemePreviewSession)_engine.Begin();
        session.Cancel();

        Assert.Throws<InvalidOperationException>(() => session.Commit());
    }

    [Fact]
    public void Update_with_an_unknown_theme_throws_and_keeps_the_session_active()
    {
        var session = (ThemePreviewSession)_engine.Begin();

        var exception = Assert.Throws<ThemePreviewException>(() => session.Update("ghost"));
        Assert.Contains(exception.Issues, issue => issue.Code == ThemeIssueCodes.PreviewThemeUnknown);

        Assert.Equal(ThemePreviewState.Active, session.State);
        Assert.Null(session.PendingThemeId);
        Assert.DoesNotContain(_events, change => change.Kind == ThemePreviewChangeKind.Updated);
    }

    [Fact]
    public void Update_with_an_empty_id_is_rejected()
    {
        var session = (ThemePreviewSession)_engine.Begin();

        Assert.Throws<ArgumentException>(() => session.Update("   "));
        Assert.Equal(ThemePreviewState.Active, session.State);
    }

    [Fact]
    public void Begin_while_a_session_is_active_cancels_the_previous_session()
    {
        var first = _engine.Begin();
        first.Update("ocean");

        using var second = (ThemePreviewSession)_engine.Begin();

        Assert.Equal(ThemePreviewState.Cancelled, ((ThemePreviewSession)first).State);
        Assert.Equal(ThemeDefaults.DefaultThemeId, second.Baseline.ThemeId);
        Assert.Same(second, _engine.ActiveSession);
        Assert.Contains(_events, change => change.Kind == ThemePreviewChangeKind.Cancelled);
        Assert.Equal(ThemePreviewChangeKind.Began, _events[^1].Kind);
    }

    [Fact]
    public void SetCurrentSettings_is_rejected_while_previewing_and_allowed_afterwards()
    {
        var session = _engine.Begin();
        var next = _engine.CurrentSettings with { Appearance = AppearanceMode.Light };

        Assert.Throws<InvalidOperationException>(() => _engine.SetCurrentSettings(next));

        session.Cancel();
        _engine.SetCurrentSettings(next);
        Assert.Equal(AppearanceMode.Light, _engine.CurrentSettings.Appearance);
    }

    [Fact]
    public void Disposed_session_rejects_every_operation()
    {
        var session = (ThemePreviewSession)_engine.Begin();
        session.Dispose();

        Assert.Equal(ThemePreviewState.Disposed, session.State);
        Assert.Throws<ObjectDisposedException>(() => session.Update("ocean"));
        Assert.Throws<ObjectDisposedException>(() => session.Commit());
        session.Cancel();
        session.Dispose();
    }

    [Fact]
    public void Event_payloads_carry_the_resolved_descriptor()
    {
        ThemeDescriptor? lastTheme = null;
        _engine.Changed += (_, args) => lastTheme = args.Theme;

        using var session = _engine.Begin();
        session.Update("ocean");

        Assert.NotNull(lastTheme);
        Assert.Equal("ocean", lastTheme!.Id);
        Assert.Equal("Ocean", lastTheme.Name);
    }
}
