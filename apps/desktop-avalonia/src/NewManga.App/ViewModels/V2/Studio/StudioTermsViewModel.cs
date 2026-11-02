namespace NewManga.App.ViewModels.V2.Studio;

/// <summary>The three terms/constraints work faces of SCREEN_SPECS §6.</summary>
public enum StudioTermsSection
{
    Terms,
    DoNotTranslate,
    Conflicts,
}

/// <summary>One terms row, only produced by a real source (none exists today).</summary>
public sealed record StudioTermRow(
    string TermId,
    string SourceText,
    string TargetText,
    string Scope,
    bool IsPinned,
    bool IsConflict);

/// <summary>
/// The seam a future Core face (settings/knowledge domain) must implement; the UI consumes only this.
/// </summary>
public interface IStudioTermsSource
{
    bool IsWired { get; }

    string CapabilityNote { get; }

    Task<IReadOnlyList<StudioTermRow>> ListTermsAsync(CancellationToken cancellationToken = default);

    Task<IReadOnlyList<StudioTermRow>> ListDoNotTranslateAsync(CancellationToken cancellationToken = default);

    Task<IReadOnlyList<StudioTermRow>> ListConflictsAsync(CancellationToken cancellationToken = default);
}

/// <summary>
/// NOT_WIRED implementation: verified on 2026-10-30 that
/// (a) <c>HostCommandRegistry</c> declares **zero** glossary / do-not-translate / constraint / term
///     commands (grep: no matches),
/// (b) Core has term *pipeline* stages (<c>term_extract</c>) and constraint entities but exposes no
///     command handler for listing/editing them,
/// so there is no real command to bind. This source returns empty lists and a capability note; the UI
/// renders the NOT_WIRED banner and never fabricates rows or interactions.
/// </summary>
public sealed class NotWiredTermsSource : IStudioTermsSource
{
    public static NotWiredTermsSource Instance { get; } = new();

    public bool IsWired => false;

    public string CapabilityNote =>
        "未接入：Core/命令注册表没有术语表/不译表/冲突的读取或编辑命令（已核实 settings_* 无术语分区，term_extract 仅为流水线阶段）。本页面不伪造数据。";

    public Task<IReadOnlyList<StudioTermRow>> ListTermsAsync(CancellationToken cancellationToken = default) =>
        Task.FromResult<IReadOnlyList<StudioTermRow>>(Array.Empty<StudioTermRow>());

    public Task<IReadOnlyList<StudioTermRow>> ListDoNotTranslateAsync(CancellationToken cancellationToken = default) =>
        Task.FromResult<IReadOnlyList<StudioTermRow>>(Array.Empty<StudioTermRow>());

    public Task<IReadOnlyList<StudioTermRow>> ListConflictsAsync(CancellationToken cancellationToken = default) =>
        Task.FromResult<IReadOnlyList<StudioTermRow>>(Array.Empty<StudioTermRow>());
}

/// <summary>
/// V11R-B-5 terms &amp; constraints workbench: 术语表 / 不译表 / 冲突提示.
///
/// Honest by construction: the capability was verified absent (no command, no settings section, no
/// typed Host method), so this view model exposes the NOT_WIRED banner, the exact reason and disabled
/// controls — it never invents term rows, fake conflicts or fake interactions. When a real
/// <see cref="IStudioTermsSource"/> lands (knowledge-domain contract), the same VM binds it.
/// </summary>
public sealed class StudioTermsViewModel : StudioObservable
{
    private readonly IStudioTermsSource _source;
    private StudioTermsSection _section = StudioTermsSection.Terms;
    private bool _isLoading;
    private string? _statusText;

    public StudioTermsViewModel(IStudioTermsSource? source = null)
    {
        _source = source ?? NotWiredTermsSource.Instance;
    }

    public bool IsWired => _source.IsWired;

    public bool IsNotWired => !_source.IsWired;

    public string CapabilityNote => _source.CapabilityNote;

    public string BannerTitle => IsWired ? "术语与约束" : "能力待接入 · NOT_WIRED";

    public string BannerBody => IsWired
        ? "术语表 / 不译表 / 冲突来自知识域命令。"
        : CapabilityNote;

    public StudioTermsSection Section
    {
        get => _section;
        set
        {
            if (Set(ref _section, value))
            {
                Raise(nameof(SectionText));
                Raise(nameof(SearchPlaceholder));
            }
        }
    }

    public string SectionText => Section switch
    {
        StudioTermsSection.Terms => "术语表",
        StudioTermsSection.DoNotTranslate => "不译表",
        _ => "冲突提示",
    };

    public string SearchPlaceholder => IsWired ? "搜索术语 / 原文 / 译文" : "搜索不可用（未接入）";

    public bool IsSearchEnabled => IsWired;

    /// <summary>Always empty while NOT_WIRED — no invented rows.</summary>
    public IReadOnlyList<StudioTermRow> Rows { get; private set; } = Array.Empty<StudioTermRow>();

    public int RowCount => Rows.Count;

    public bool HasRows => Rows.Count > 0;

    public bool IsLoading
    {
        get => _isLoading;
        private set => Set(ref _isLoading, value);
    }

    public string? StatusText => _statusText;

    public string EmptyText => IsWired ? "没有条目" : "未接入：不展示任何条目";

    /// <summary>Reads the bound source; the NOT_WIRED source returns empty lists by contract.</summary>
    public async Task<bool> LoadAsync(CancellationToken cancellationToken = default)
    {
        IsLoading = true;
        try
        {
            Rows = Section switch
            {
                StudioTermsSection.Terms => await _source.ListTermsAsync(cancellationToken).ConfigureAwait(true),
                StudioTermsSection.DoNotTranslate => await _source.ListDoNotTranslateAsync(cancellationToken).ConfigureAwait(true),
                _ => await _source.ListConflictsAsync(cancellationToken).ConfigureAwait(true),
            };
            _statusText = IsWired ? $"已读取 {Rows.Count} 条" : CapabilityNote;
            Raise(nameof(Rows));
            Raise(nameof(RowCount));
            Raise(nameof(HasRows));
            Raise(nameof(EmptyText));
            Raise(nameof(StatusText));
            return true;
        }
        catch (OperationCanceledException)
        {
            return false;
        }
        finally
        {
            IsLoading = false;
        }
    }

    /// <summary>Editing/creating terms is NOT_WIRED: any attempt reports the reason instead of pretending.</summary>
    public bool TryEdit() => Refuse();

    public bool TryCreate() => Refuse();

    public bool TryResolveConflict() => Refuse();

    private bool Refuse()
    {
        if (IsWired)
        {
            return true;
        }

        _statusText = "未接入：该操作需要知识域命令（当前不可用），未执行任何写入";
        Raise(nameof(StatusText));
        return false;
    }

    /// <summary>Evidence inventory for the NOT_WIRED list.</summary>
    public IReadOnlyList<string> BuildCapabilityInventory() => new[]
    {
        "术语表读取/编辑：无命令（registry 零匹配 glossary/term）",
        "不译表（do-not-translate）：无命令",
        "冲突提示：无命令",
        "settings_* 存在但不含术语分区；IHostController 无对应 typed 方法",
        $"当前源：{(_source.IsWired ? "真实" : "NOT_WIRED（返回空、不伪造）")}",
    };
}
