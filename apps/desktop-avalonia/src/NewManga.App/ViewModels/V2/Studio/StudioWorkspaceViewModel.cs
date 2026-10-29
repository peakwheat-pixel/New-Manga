using NewManga.App.Services;

namespace NewManga.App.ViewModels.V2.Studio;

/// <summary>
/// V11R-B-3 root of the Studio area. It owns exactly one <see cref="StudioPageViewModel"/> for the
/// whole session so switching Page ⇄ Batch never rebuilds it and never loses the shared
/// <see cref="StudioSelection"/>, zoom, pan, filters or inspector tab (AC2).
/// Batch mode itself is delivered by V11R-B-4; until then it renders its NOT_WIRED surface — no fake
/// matrix and no fabricated run data.
/// </summary>
public sealed class StudioWorkspaceViewModel : StudioObservable
{
    private StudioWorkspaceMode _mode = StudioWorkspaceMode.Page;
    private StudioWorkspaceMode? _pendingMode;

    public StudioWorkspaceViewModel(
        IHostController host,
        StudioSelection? selection = null,
        IRunDataSource? runSource = null,
        IRegionTextSource? textSource = null,
        IRegionFlagSource? flagSource = null)
    {
        Selection = selection ?? new StudioSelection();
        Page = new StudioPageViewModel(host, Selection, runSource, textSource, flagSource);
        Host = host;
        Batch = new StudioBatchViewModel(host, Selection, Page, host as IRunController);
    }

    public IHostController Host { get; }

    public StudioSelection Selection { get; }

    public StudioPageViewModel Page { get; }

    /// <summary>V11R-B-4: Batch mode view model (one instance for the session, like Page).</summary>
    public StudioBatchViewModel Batch { get; }

    public StudioWorkspaceMode Mode
    {
        get => _mode;
        private set
        {
            if (Set(ref _mode, value))
            {
                Raise(nameof(ModeIndex));
                Raise(nameof(IsPageMode));
                Raise(nameof(IsBatchMode));
                Raise(nameof(HeaderModeText));
            }
        }
    }

    public int ModeIndex => (int)Mode;

    public bool IsPageMode => Mode == StudioWorkspaceMode.Page;

    public bool IsBatchMode => Mode == StudioWorkspaceMode.Batch;

    public string HeaderModeText => Mode == StudioWorkspaceMode.Page ? "Studio · Page" : "Studio · Batch";

    /// <summary>Batch surface status: honest NOT_WIRED line for this build.</summary>
    public string BatchNotWiredNote =>
        "Batch 模式在 V11R-B-4 交付；Run 投影（IRunController / V11R-A-2）未合入 → NOT_WIRED";

    public string BatchNotWiredDetail =>
        "本构建不显示任何阶段矩阵或进度：没有 GetTaskProjection 读数时宁可空态，也不伪造。";

    public bool BatchAvailable => false;

    /// <summary>Guard-aware mode switch (HeaderModeText keeps the shell breadcrumb in sync).</summary>
    public bool RequestMode(StudioWorkspaceMode mode)
    {
        if (mode == Mode)
        {
            return true;
        }

        if (Page.HasUnsavedChanges)
        {
            _pendingMode = mode;
            Page.OpenLeaveModal();
            return false;
        }

        Mode = mode;
        return true;
    }

    /// <summary>Toggles Page ⇄ Batch (`Tab` in the Studio space).</summary>
    public bool ToggleMode() =>
        RequestMode(Mode == StudioWorkspaceMode.Page ? StudioWorkspaceMode.Batch : StudioWorkspaceMode.Page);

    /// <summary>
    /// Resolves the unsaved-change modal and completes a deferred mode switch. 取消 keeps both the
    /// edit and the current mode.
    /// </summary>
    public async Task<StudioLeaveOutcome> ResolveLeaveAsync(
        StudioLeaveChoice choice,
        CancellationToken cancellationToken = default)
    {
        var outcome = await Page.ResolveLeaveAsync(choice, cancellationToken).ConfigureAwait(true);
        if (outcome is StudioLeaveOutcome.Saved or StudioLeaveOutcome.Discarded or StudioLeaveOutcome.NoChanges)
        {
            if (_pendingMode is { } mode)
            {
                Mode = mode;
                _pendingMode = null;
            }
        }

        return outcome;
    }

    public Task<bool> LoadAsync(
        string? bookId = null,
        string? chapterId = null,
        CancellationToken cancellationToken = default) =>
        Page.LoadAsync(bookId, chapterId, cancellationToken);

    /// <summary>The command-palette friendly title ("Studio · Page — 作品 › 章节 › 页").</summary>
    public string TitleLine => $"{HeaderModeText} — {Page.BreadcrumbText}";
}
