using System.Collections.ObjectModel;
using System.Text.Json;
using NewManga.App.Services;
using NewManga.CoreClient;
using NewManga.CoreClient.Wire;

namespace NewManga.App.ViewModels.Fluent;

public sealed class WorkbenchViewModel : FluentViewModel
{
    private readonly IHostController? _host;
    private readonly string _sessionId;
    private string? _chapterId;
    private string? _pageId;
    private ChapterPageSummary? _selectedPage;
    private RegionSummary? _selectedRegion;
    private RegionPageProjection? _projection;
    private byte[]? _pageImageBytes;
    private RegionRevisionHistory? _revisions;
    private Draft? _draft;
    private DraftLease? _lease;
    private RegionCandidate? _candidate;
    private string _draftText = string.Empty;
    private string _persistedDraftText = string.Empty;
    private IReadOnlyList<Draft> _drafts = Array.Empty<Draft>();
    private bool _isBatch;
    private bool _isApplying;
    private bool _isInspectorCollapsed;
    private double _filmStripScrollOffset;

    public WorkbenchViewModel(IHostController? host, string sessionId)
    {
        _host = host;
        _sessionId = sessionId;
        State = FluentPageState.Empty;
        Status = "从书架选择章节以开始编辑。";
    }

    public ObservableCollection<ChapterPageSummary> Pages { get; } = new();
    public ObservableCollection<RegionSummary> Regions { get; } = new();
    public IReadOnlyList<Draft> Drafts
    {
        get => _drafts;
        private set => Set(ref _drafts, value);
    }
    public ChapterPageSummary? SelectedPage { get => _selectedPage; private set => Set(ref _selectedPage, value); }
    public RegionSummary? SelectedRegion { get => _selectedRegion; private set => Set(ref _selectedRegion, value); }
    public RegionPageProjection? Projection { get => _projection; private set => Set(ref _projection, value); }
    public byte[]? PageImageBytes { get => _pageImageBytes; private set => Set(ref _pageImageBytes, value); }
    public Draft? CurrentDraft { get => _draft; private set => Set(ref _draft, value); }
    public string DraftText
    {
        get => _draftText;
        set
        {
            if (Set(ref _draftText, value ?? string.Empty)) Changed(nameof(HasUnsavedDraft));
        }
    }
    public bool IsBatch { get => _isBatch; set => Set(ref _isBatch, value); }
    public bool IsApplying { get => _isApplying; private set => Set(ref _isApplying, value); }

    /// <summary>I-1/I-2：检查器折叠状态；同一运行期 UI memento，不落盘（页面往返/frontend 切换后保留）。</summary>
    public bool IsInspectorCollapsed
    {
        get => _isInspectorCollapsed;
        set => Set(ref _isInspectorCollapsed, value);
    }

    /// <summary>I-1：film-strip 横向滚动偏移；同一运行期 UI memento，不落盘。</summary>
    public double FilmStripScrollOffset
    {
        get => _filmStripScrollOffset;
        set => Set(ref _filmStripScrollOffset, value);
    }
    public bool IsReadOnly => _host is null || !_host.Snapshot.WritesAllowed;
    public bool HasUnsavedDraft => CurrentDraft is not null && !string.Equals(DraftText, _persistedDraftText, StringComparison.Ordinal);
    public string ErrorCategory { get; private set; } = string.Empty;
    public IReadOnlyList<string> ErrorCodes => DraftErrorMap.Codes;

    public async Task LoadAsync(string? chapterId, CancellationToken cancellationToken = default)
    {
        _chapterId = chapterId;
        if (_host is null || string.IsNullOrWhiteSpace(chapterId))
        {
            State = FluentPageState.Empty;
            Status = "未选择章节。返回书架并选择章节。";
            return;
        }

        State = FluentPageState.Loading;
        Status = "正在读取工作台…";
        try
        {
            var pages = await _host.ListChapterPagesAsync(chapterId, cancellationToken);
            Pages.Clear();
            foreach (var page in pages.OrderBy(item => item.SortOrder))
            {
                Pages.Add(page);
            }

            if (Pages.Count == 0)
            {
                State = FluentPageState.Empty;
                Status = "本章节暂无页面。";
                return;
            }

            SelectedPage = Pages.FirstOrDefault(item => item.PageId == _pageId) ?? Pages[0];
            _pageId = SelectedPage.PageId;
            await LoadPageAsync(SelectedPage.PageId, cancellationToken);
            Drafts = await _host.ListDraftsAsync(_sessionId, cancellationToken);
            CurrentDraft = Drafts.FirstOrDefault(item => item.PageId == SelectedPage.PageId && item.RegionId == SelectedRegion?.RegionId);
            if (CurrentDraft is not null)
            {
                _lease = await _host.OpenDraftAsync(_sessionId, CurrentDraft.PageId, CurrentDraft.RegionId,
                    CurrentDraft.BaseRevisionId, CurrentDraft.PageBindingVersion, cancellationToken);
                DraftText = ReadDraftText(CurrentDraft.Patch);
                _persistedDraftText = DraftText;
            }

            State = IsReadOnly ? FluentPageState.ReadOnly : FluentPageState.Ready;
            Status = IsReadOnly ? _host.Snapshot.ReadOnlyReason ?? "只读模式" : "工作台已就绪";
        }
        catch (CoreOperationException ex)
        {
            ApplyDraftError(ex);
            State = FluentPageState.Error;
            Status = Error;
        }
        catch (Exception ex)
        {
            State = FluentPageState.Error;
            Error = $"读取工作台失败（{ex.GetType().Name}）。画布保留上一帧。";
            Status = Error;
        }
    }

    public async Task SelectPageAsync(string pageId, CancellationToken cancellationToken = default)
    {
        if (HasUnsavedDraft && CurrentDraft is not null && _host is not null)
        {
            await _host.GetDraftAsync(CurrentDraft.DraftId, cancellationToken);
        }

        _pageId = pageId;
        SelectedPage = Pages.FirstOrDefault(item => item.PageId == pageId);
        if (SelectedPage is not null)
        {
            await LoadPageAsync(pageId, cancellationToken);
            CurrentDraft = null;
            _lease = null;
            DraftText = string.Empty;
        }
    }

    public async Task SelectRegionAsync(RegionSummary? region, CancellationToken cancellationToken = default)
    {
        SelectedRegion = region;
        _revisions = null;
        CurrentDraft = null;
        _lease = null;
        _candidate = null;
        DraftText = string.Empty;
        if (_host is null || region is null || SelectedPage is null)
        {
            return;
        }

        _revisions = await _host.LoadRegionRevisionsAsync(region.RegionId, cancellationToken);
        Drafts = await _host.ListDraftsAsync(_sessionId, cancellationToken);
        CurrentDraft = Drafts.FirstOrDefault(item => item.PageId == SelectedPage.PageId && item.RegionId == region.RegionId);
        if (CurrentDraft is not null)
        {
            _lease = await _host.OpenDraftAsync(_sessionId, CurrentDraft.PageId, CurrentDraft.RegionId,
                CurrentDraft.BaseRevisionId, CurrentDraft.PageBindingVersion, cancellationToken);
            DraftText = ReadDraftText(CurrentDraft.Patch);
            _persistedDraftText = DraftText;
        }

        Changed(nameof(HasUnsavedDraft));
    }

    /// <summary>
    /// The frozen Host projection does not expose PageBindingVersion. A new draft cannot be opened
    /// safely without it, so this method fails closed instead of inventing a version.
    /// </summary>
    public async Task<bool> OpenDraftAsync(int? pageBindingVersion = null, CancellationToken cancellationToken = default)
    {
        if (_host is null || SelectedPage is null || SelectedRegion is null || IsReadOnly)
        {
            return false;
        }

        if (pageBindingVersion is null)
        {
            State = FluentPageState.ReadOnly;
            Error = "当前 Host 页面投影未提供 pageBindingVersion，无法安全开启新草稿。";
            Status = Error;
            return false;
        }

        try
        {
            _revisions ??= await _host.LoadRegionRevisionsAsync(SelectedRegion.RegionId, cancellationToken);
            var baseRevisionId = _revisions?.Revisions.FirstOrDefault(item => item.IsCurrent)?.RegionRevisionId;
            _lease = await _host.OpenDraftAsync(_sessionId, SelectedPage.PageId, SelectedRegion.RegionId,
                baseRevisionId, pageBindingVersion.Value, cancellationToken);
            if (_lease is null || !_lease.CanEdit || _lease.Token is null)
            {
                State = FluentPageState.Conflict;
                Error = "草稿当前不可编辑或 Host 未提供 EditToken。";
                Status = Error;
                return false;
            }

            CurrentDraft = _lease.Draft;
            DraftText = ReadDraftText(CurrentDraft.Patch);
            _persistedDraftText = DraftText;
            State = FluentPageState.Ready;
            return true;
        }
        catch (CoreOperationException ex)
        {
            ApplyDraftError(ex);
            State = ex.Category == "conflict" ? FluentPageState.Conflict : FluentPageState.Error;
            Status = Error;
            return false;
        }
    }

    public async Task<bool> SaveDraftAsync(CancellationToken cancellationToken = default)
    {
        if (_host is null || CurrentDraft is null || IsReadOnly)
        {
            return false;
        }

        try
        {
            var patch = new DraftPatchRequest(new Dictionary<string, object?> { ["text"] = DraftText });
            CurrentDraft = await _host.PatchDraftAsync(CurrentDraft.DraftId, _sessionId, patch,
                cancellationToken: cancellationToken);
            Changed(nameof(HasUnsavedDraft));
            if (CurrentDraft is null)
            {
                Error = "Host 没有返回保存后的 Draft。";
                State = FluentPageState.Error;
                return false;
            }

            _persistedDraftText = DraftText;

            Drafts = await _host.ListDraftsAsync(_sessionId, cancellationToken);
            Status = "草稿已写入恢复日志。";
            return true;
        }
        catch (CoreOperationException ex)
        {
            ApplyDraftError(ex);
            State = ex.Category == "conflict" ? FluentPageState.Conflict : FluentPageState.Error;
            return false;
        }
    }

    public async Task<bool> ApplyCandidateAsync(CancellationToken cancellationToken = default)
    {
        if (_host is null || CurrentDraft is null || SelectedRegion is null || _lease?.Token is null || IsReadOnly)
        {
            return false;
        }

        IsApplying = true;
        try
        {
            var patch = new DraftPatchRequest(new Dictionary<string, object?> { ["text"] = DraftText });
            _candidate = await _host.PrepareCandidateAsync(SelectedRegion.RegionId, patch, "manual",
                CurrentDraft.DraftId, CurrentDraft.BaseRevisionId, cancellationToken);
            if (_candidate is null)
            {
                Error = "Host 未准备 Candidate，应用未执行。";
                State = FluentPageState.Error;
                return false;
            }

            var freshLease = await _host.OpenDraftAsync(_sessionId, CurrentDraft.PageId, CurrentDraft.RegionId,
                CurrentDraft.BaseRevisionId, CurrentDraft.PageBindingVersion, cancellationToken);
            if (freshLease?.Token is null || !freshLease.CanEdit)
            {
                State = FluentPageState.Conflict;
                Error = "应用前 Draft token 已不可用，请重新读取状态。";
                return false;
            }

            var applied = await _host.ApplyCandidatesAsync(freshLease.Token, [_candidate.CandidateId], cancellationToken);
            if (!applied.ContainsKey(_candidate.CandidateId))
            {
                Error = "Host 没有确认 Candidate 应用；保留当前画布状态。";
                State = FluentPageState.Error;
                return false;
            }

            _lease = freshLease;
            State = FluentPageState.Ready;
            Status = "Candidate 已由 Host 确认应用。";
            await LoadPageAsync(SelectedPage?.PageId ?? string.Empty, cancellationToken);
            return true;
        }
        catch (CoreOperationException ex)
        {
            ApplyDraftError(ex);
            State = ex.Category == "conflict" ? FluentPageState.Conflict : FluentPageState.Error;
            return false;
        }
        finally
        {
            IsApplying = false;
        }
    }

    public async Task<bool> ReloadDraftAsync(CancellationToken cancellationToken = default)
    {
        if (_host is null || CurrentDraft is null)
        {
            return false;
        }

        try
        {
            CurrentDraft = await _host.GetDraftAsync(CurrentDraft.DraftId, cancellationToken);
            if (CurrentDraft is null)
            {
                Error = "草稿不存在或当前 Host 不可用。";
                return false;
            }

            DraftText = ReadDraftText(CurrentDraft.Patch);
            _persistedDraftText = DraftText;
            Status = "草稿已重新读取。";
            return true;
        }
        catch (CoreOperationException ex)
        {
            ApplyDraftError(ex);
            return false;
        }
    }

    public async Task DiscardDraftAsync(CancellationToken cancellationToken = default)
    {
        if (_host is null || CurrentDraft is null || IsReadOnly)
        {
            return;
        }

        await _host.DiscardDraftAsync(CurrentDraft.DraftId, _sessionId, cancellationToken);
        CurrentDraft = null;
        _lease = null;
        DraftText = string.Empty;
        _persistedDraftText = string.Empty;
        Drafts = await _host.ListDraftsAsync(_sessionId, cancellationToken);
        State = FluentPageState.Ready;
        Status = "草稿已按请求丢弃。";
        Changed(nameof(HasUnsavedDraft));
    }

    private async Task LoadPageAsync(string pageId, CancellationToken cancellationToken)
    {
        if (_host is null || string.IsNullOrWhiteSpace(pageId))
        {
            return;
        }

        try
        {
            var projection = await _host.LoadPageRegionsAsync(pageId, cancellationToken);
            if (projection is null)
            {
                throw new InvalidOperationException("Core region projection unavailable");
            }

            var image = await _host.ReadPageImageAsync(pageId, cancellationToken);
            if (image is not null && image.Length > 0)
            {
                PageImageBytes = image;
            }

            Projection = projection;
            Regions.Clear();
            foreach (var region in projection.Regions)
            {
                Regions.Add(region);
            }

            if (SelectedRegion is null || !projection.Regions.Any(item => item.RegionId == SelectedRegion.RegionId))
            {
                SelectedRegion = Regions.FirstOrDefault();
            }
        }
        catch (CoreOperationException ex)
        {
            ApplyDraftError(ex);
            State = ex.Category == "conflict" ? FluentPageState.Conflict : FluentPageState.Error;
            Status = Error;
        }
    }

    private static string ReadDraftText(JsonElement? patch)
    {
        if (patch is { ValueKind: JsonValueKind.Object } value && value.TryGetProperty("text", out var text) && text.ValueKind == JsonValueKind.String)
        {
            return text.GetString() ?? string.Empty;
        }

        return string.Empty;
    }

    private void ApplyDraftError(CoreOperationException ex)
    {
        ErrorCategory = DraftErrorMap.Category(ex.Code, ex.Category);
        Error = DraftErrorMap.Presentation(ex.Code, ErrorCategory);
        Changed(nameof(ErrorCategory));
    }
}

public static class DraftErrorMap
{
    private static readonly IReadOnlyDictionary<string, string> Categories = new Dictionary<string, string>(StringComparer.Ordinal)
    {
        ["DRAFT_INVALID"] = "validation", ["DRAFT_PATCH_INVALID"] = "validation",
        ["DRAFT_CANDIDATE_INVALID"] = "validation", ["DRAFT_FLUSH_TRIGGER_INVALID"] = "validation",
        ["EDIT_TOKEN_INVALID"] = "validation", ["DRAFT_NOT_FOUND"] = "not_found",
        ["DRAFT_CANDIDATE_NOT_FOUND"] = "not_found", ["TARGET_NOT_FOUND"] = "not_found",
        ["DRAFT_READ_ONLY"] = "conflict", ["DRAFT_OWNER_CHANGED"] = "conflict",
        ["EDIT_TOKEN_EXPIRED"] = "conflict", ["EDIT_TOKEN_REUSED"] = "conflict",
        ["STALE_BASE_REVISION"] = "conflict", ["LOCK_CHANGED"] = "conflict",
        ["DRAFT_JOURNAL_UNWRITABLE"] = "unavailable", ["PAGE_SIZE_UNAVAILABLE"] = "unavailable",
        ["DRAFT_APPLY_FAILED"] = "internal", ["INTERNAL"] = "internal", ["UNKNOWN"] = "validation",
    };

    public static IReadOnlyList<string> Codes => Categories.Keys.OrderBy(value => value, StringComparer.Ordinal).ToArray();

    public static string Category(string code, string? fallback) => Categories.TryGetValue(code, out var category)
        ? category
        : fallback is "validation" or "not_found" or "conflict" or "unavailable" or "internal" ? fallback : "unknown";

    public static string Presentation(string code, string category) => category switch
    {
        "validation" => $"输入校验失败（{code}），请修正后重试。",
        "not_found" => $"目标已不存在（{code}），已保留当前工作区。",
        "conflict" => $"检测到并发或保护冲突（{code}），已停止应用，请重新读取并对照。",
        "unavailable" => $"Draft 服务暂不可用（{code}），可以重试。",
        "internal" => $"Draft 操作失败（{code}），已保留当前界面。",
        _ => $"Draft 操作被拒绝（{code}）。",
    };
}
