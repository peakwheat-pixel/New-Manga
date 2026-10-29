using System.Collections.ObjectModel;
using NewManga.App.Services;

namespace NewManga.App.ViewModels.V2.Studio;

/// <summary>Export target format (the frozen Host contract accepts exactly zip/pdf).</summary>
public enum StudioExportFormat
{
    Zip,
    Pdf,
}

/// <summary>PDF composer mode of PDF-EXPORT-UI-1 (<c>image_only</c> / <c>searchable_dual_layer</c>).</summary>
public enum StudioPdfContentMode
{
    ImageOnly,
    SearchableDualLayer,
}

/// <summary>Export scope: the chapter or the shared multi-page selection.</summary>
public enum StudioExportScope
{
    Chapter,
    SelectedPages,
}

/// <summary>Stale policy of the frozen Core export face.</summary>
public enum StudioStalePolicy
{
    Abort,
    ContinueExisting,
}

/// <summary>Export preflight/job phase.</summary>
public enum StudioExportPhase
{
    Idle,
    Loading,
    Ready,
    Running,
    Completed,
    Failed,
    Cancelled,
    NotWired,
}

/// <summary>One export history row (real <c>GetExportHistory</c> entry).</summary>
public sealed class StudioExportHistoryItemViewModel : StudioObservable
{
    public StudioExportHistoryItemViewModel(ExportHistoryEntry entry)
    {
        Entry = entry;
    }

    public ExportHistoryEntry Entry { get; }

    public string ExportId => Entry.ExportId;

    public string Format => string.IsNullOrWhiteSpace(Entry.Format) ? "—" : Entry.Format.ToUpperInvariant();

    public StudioStateKind State => Entry.Status.Trim().ToLowerInvariant() switch
    {
        "completed" => StudioStateKind.Done,
        "failed" => StudioStateKind.Failed,
        "cancelled" => StudioStateKind.Skipped,
        "running" or "publishing" => StudioStateKind.Running,
        "pending" => StudioStateKind.Queued,
        _ => StudioStateKind.NotStarted,
    };

    public string StateGlyph => StudioStates.Glyph(State);

    public string StateClass => StudioStates.StyleClass(State);

    public string StateLabel => StudioStates.Label(State);

    public string PageCountText => $"{Entry.PageCount} 页";

    /// <summary>File name only: absolute OS paths are never rendered in the UI.</summary>
    public string FileName => string.IsNullOrWhiteSpace(Entry.OutputPath)
        ? "—"
        : Path.GetFileName(Entry.OutputPath);

    public string CompletedAt => string.IsNullOrWhiteSpace(Entry.CompletedAt) ? "—" : Entry.CompletedAt;

    public string ShaPrefix => string.IsNullOrWhiteSpace(Entry.Sha256)
        ? "—"
        : Entry.Sha256.Length <= 12 ? Entry.Sha256 : Entry.Sha256[..12];

    public string Tooltip => $"{Format} · {PageCountText} · {StateLabel} · {FileName}";
}

/// <summary>
/// V11R-B-5 export preflight + history/progress/cancel.
///
/// Verified facts driving this design (evidence `verification/V11R-B-5/preflight.json`):
/// * Core supports BOTH stale policies (<c>handle_start_export</c> validates abort|continue_existing)
///   BUT the frozen <see cref="IHostController.StartExportAsync"/> does not expose a <c>stale_policy</c>
///   parameter — the Host always sends the payload default <c>abort</c>. The UI therefore offers
///   「abort」 as supported and renders 「continue_existing · 未支持」 (disabled + reason); it never
///   pretends the option can be applied.
/// * 未确认 / 过期 counts have no read face before StartExport (review state is the Region revision
///   face, F0-2; stale is computed by the Core inside StartExport and surfaces as EXPORT_STALE) → those
///   counters render "—" with the reason, never a fabricated 0.
/// * Real data used: <c>GetTranslatedPageIdsAsync</c>, the Batch run projection counts (failed/blocked),
///   <c>StartExportAsync</c>, <c>GetExportSnapshotAsync</c> (injectable poll), <c>CancelExportAsync</c>,
///   <c>GetExportHistoryAsync</c>, <c>RevealExportFolderAsync</c>, <c>ExportDirectorySuggestion</c>.
/// </summary>
public sealed class StudioExportViewModel : StudioObservable
{
    public const string ContinueExistingDescription =
        "跳过 stale 页继续导出（Core 不再以 EXPORT_STALE 中止；仍导出其余有效翻译页）";

    public const string AbortDescription =
        "有 stale 输入即中止（Core 返回 EXPORT_STALE 明细，先重渲染过期页）";

    public const string UnconfirmedNotWired =
        "未确认计数读取命令未接入（review 状态在 Region revision 面，V11R-F0-2）";

    public const string StaleNotWired =
        "过期计数无预读命令：Core 在 StartExport 内部计算 stale 并以 EXPORT_STALE 错误返回明细";

    private readonly IHostController _host;
    private readonly StudioSelection _selection;
    private readonly StudioPageViewModel _page;
    private readonly TimeSpan _pollInterval;
    private DateTime _lastPollUtc = DateTime.MinValue;
    private StudioExportPhase _phase = StudioExportPhase.Idle;
    private StudioExportFormat _format = StudioExportFormat.Zip;
    private StudioPdfContentMode _pdfContent = StudioPdfContentMode.ImageOnly;
    private StudioExportScope _scope = StudioExportScope.Chapter;
    private StudioStalePolicy _stalePolicy = StudioStalePolicy.Abort;
    private IReadOnlyList<string> _translatedPageIds = Array.Empty<string>();
    private string? _errorText;
    private string? _statusText;
    private ExportSnapshotInfo? _snapshot;
    private string? _exportId;
    private string _targetFileName = string.Empty;

    public StudioExportViewModel(
        IHostController host,
        StudioSelection selection,
        StudioPageViewModel page,
        TimeSpan? pollInterval = null)
    {
        _host = host;
        _selection = selection;
        _page = page;
        _pollInterval = pollInterval ?? TimeSpan.FromMilliseconds(700);
        History = new ObservableCollection<StudioExportHistoryItemViewModel>();
        RefreshTargetFileName();
        _selection.Changed += (_, _) =>
        {
            Raise(nameof(HasSelectedPages));
            Raise(nameof(SelectedPageCount));
            Raise(nameof(ScopeText));
            Raise(nameof(ExportablePageIds));
            Raise(nameof(ExportablePagesText));
            Raise(nameof(CanStart));
        };
    }

    public TimeSpan PollInterval => _pollInterval;

    public bool IsHostReady => _host.Snapshot.State == HostViewState.Ready;

    public bool WritesAllowed => _host.Snapshot.WritesAllowed;

    public StudioExportPhase Phase
    {
        get => _phase;
        private set
        {
            if (Set(ref _phase, value))
            {
                Raise(nameof(IsRunning));
                Raise(nameof(IsTerminal));
                Raise(nameof(CanCancel));
                Raise(nameof(CanStart));
                Raise(nameof(PhaseText));
            }
        }
    }

    public bool IsRunning => Phase == StudioExportPhase.Running;

    public bool IsTerminal => Phase is StudioExportPhase.Completed or StudioExportPhase.Failed or StudioExportPhase.Cancelled;

    public bool CanCancel => Phase == StudioExportPhase.Running && _exportId is not null;

    public bool CanStart => Phase is StudioExportPhase.Ready or StudioExportPhase.Idle or StudioExportPhase.Completed
        or StudioExportPhase.Failed or StudioExportPhase.Cancelled
        && IsHostReady && WritesAllowed && ExportablePageIds.Count > 0;

    public string PhaseText => Phase switch
    {
        StudioExportPhase.Idle => "预检未加载",
        StudioExportPhase.Loading => "正在读取预检数据…",
        StudioExportPhase.Ready => $"预检就绪 · 可导出 {ExportablePageIds.Count} 页",
        StudioExportPhase.Running => $"导出中 · {SnapshotCompleted}/{SnapshotTotal} 页",
        StudioExportPhase.Completed => "导出完成",
        StudioExportPhase.Failed => "导出失败",
        StudioExportPhase.Cancelled => "已取消",
        _ => "数据不可用",
    };

    public StudioExportFormat Format
    {
        get => _format;
        set
        {
            if (Set(ref _format, value))
            {
                Raise(nameof(IsPdf));
                Raise(nameof(FormatText));
                RefreshTargetFileName();
            }
        }
    }

    public bool IsPdf => _format == StudioExportFormat.Pdf;

    public string FormatText => IsPdf ? "PDF" : "ZIP";

    public StudioPdfContentMode PdfContent
    {
        get => _pdfContent;
        set
        {
            if (Set(ref _pdfContent, value))
            {
                Raise(nameof(PdfContentText));
            }
        }
    }

    public string PdfContentText => _pdfContent == StudioPdfContentMode.SearchableDualLayer
        ? "searchable_dual_layer（可搜索双图层）"
        : "image_only（仅图像）";

    public StudioExportScope Scope
    {
        get => _scope;
        set
        {
            if (Set(ref _scope, value))
            {
                Raise(nameof(ScopeText));
                RefreshTargetFileName();
            }
        }
    }

    public bool HasSelectedPages => _selection.SelectedPageIds.Count > 0;

    public int SelectedPageCount => _selection.SelectedPageIds.Count;

    public string ScopeText => Scope == StudioExportScope.SelectedPages
        ? $"选中 {_selection.SelectedPageIds.Count} 页"
        : "本章";

    public StudioStalePolicy StalePolicy
    {
        get => _stalePolicy;
        private set
        {
            if (Set(ref _stalePolicy, value))
            {
                Raise(nameof(StalePolicyText));
                Raise(nameof(StalePolicyTooltip));
            }
        }
    }

    public string StalePolicyText => StalePolicy == StudioStalePolicy.Abort
        ? "abort · 有 stale 即中止"
        : "continue_existing · 跳过 stale 继续导出";

    public string StalePolicyTooltip => StalePolicy == StudioStalePolicy.Abort
        ? AbortDescription
        : ContinueExistingDescription;

    /// <summary>A-7 merged: both stale policies are real and passed through to the Host/Core.</summary>
    public bool CanSelectStalePolicy(StudioStalePolicy policy) =>
        policy is StudioStalePolicy.Abort or StudioStalePolicy.ContinueExisting;

    public string ContinueExistingTooltip => ContinueExistingDescription;

    /// <summary>Selects a supported policy; unknown values are refused locally (Host would reject them).</summary>
    public bool TrySelectStalePolicy(StudioStalePolicy policy)
    {
        if (!CanSelectStalePolicy(policy))
        {
            _statusText = "非法 stale 策略：仅支持 abort / continue_existing";
            Raise(nameof(StatusText));
            return false;
        }

        StalePolicy = policy;
        return true;
    }
    public IReadOnlyList<string> TranslatedPageIds => _translatedPageIds;

    public int TranslatedPageCount => _translatedPageIds.Count;

    public IReadOnlyList<string> ExportablePageIds
    {
        get
        {
            if (_translatedPageIds.Count == 0)
            {
                return Array.Empty<string>();
            }

            if (Scope == StudioExportScope.Chapter)
            {
                return _translatedPageIds;
            }

            var selected = _selection.SelectedPageIds;
            return _translatedPageIds
                .Where(pageId => selected.Contains(pageId, StringComparer.Ordinal))
                .ToList();
        }
    }

    public string ExportablePagesText => ExportablePageIds.Count == 0
        ? "无可导出页（需要已翻译的页）"
        : $"{ExportablePageIds.Count} 页可导出";

    /// <summary>Failed/blocked page counts from the live run projection (real read face).</summary>
    public int FailedPageCount => _page.RunProjection?.FailedPageCount ?? 0;

    public int BlockedPageCount => _page.RunProjection?.BlockedPageCount ?? 0;

    public bool HasRunProjection => _page.RunProjection is not null;

    /// <summary>Null = no read face; rendered "—" with <see cref="UnconfirmedNotWired"/>.</summary>
    public int? UnconfirmedPageCount => null;

    /// <summary>Null = computed by the Core inside StartExport (EXPORT_STALE), no pre-read.</summary>
    public int? StalePageCount => null;

    public string UnconfirmedText => UnconfirmedPageCount is { } count ? count.ToString() : "—";

    public string StaleText => StalePageCount is { } count ? count.ToString() : "—";

    public string UnconfirmedTooltip => UnconfirmedPageCount is null ? UnconfirmedNotWired : "已确认页数";

    public string StaleTooltip => StalePageCount is null ? StaleNotWired : "过期页数";

    public string TargetFileName => _targetFileName;

    public string TargetHint => $"目标目录由 Host 授予并限定（{_host.ExportDirectorySuggestion.Length} 字符路径，UI 不显示绝对路径）";

    public ExportSnapshotInfo? Snapshot => _snapshot;

    public int SnapshotCompleted => _snapshot?.CompletedPages ?? 0;

    public int SnapshotTotal => _snapshot?.TotalPages ?? 0;

    public double SnapshotPercent => _snapshot?.ProgressPercent ?? 0;

    public string ProgressText => _snapshot is { } snapshot
        ? $"{snapshot.CompletedPages}/{snapshot.TotalPages} 页 · {Math.Round(snapshot.ProgressPercent):0}% · {StateText(snapshot.State)}"
        : "尚未开始";

    public string OutputText => _snapshot is { OutputPath: { Length: > 0 } path }
        ? $"输出：{Path.GetFileName(path)} · sha256 {ShortHash(_snapshot.Sha256)}"
        : "—";

    private static string ShortHash(string? sha) =>
        string.IsNullOrWhiteSpace(sha) ? "—" : sha.Length <= 12 ? sha : sha[..12];

    private static string StateText(ExportJobState state) => state switch
    {
        ExportJobState.Pending => "排队",
        ExportJobState.Running => "进行中",
        ExportJobState.Publishing => "发布中",
        ExportJobState.Completed => "完成",
        ExportJobState.Skipped => "跳过",
        ExportJobState.Cancelled => "已取消",
        ExportJobState.Failed => "失败",
        _ => "未知",
    };

    public string? ErrorText => _errorText;

    public bool HasError => !string.IsNullOrWhiteSpace(_errorText);

    public string? StatusText => _statusText;

    public string? ExportId => _exportId;

    public bool CanReveal => _exportId is not null && _snapshot is { State: ExportJobState.Completed };

    public ObservableCollection<StudioExportHistoryItemViewModel> History { get; }

    public bool IsHistoryLoading { get; private set; }

    public string HistoryEmptyText => History.Count == 0 ? "还没有导出记录" : string.Empty;

    // ---------------------------------------------------------------- preflight

    /// <summary>Reads the real preflight inputs: translated page ids + the live run projection counts.</summary>
    public async Task<bool> RefreshPreflightAsync(CancellationToken cancellationToken = default)
    {
        if (!IsHostReady)
        {
            Phase = StudioExportPhase.NotWired;
            _errorText = $"Host 未就绪（{_host.Snapshot.State}）：{_host.Snapshot.LastError ?? _host.Snapshot.StatusLine}";
            Raise(nameof(ErrorText));
            Raise(nameof(HasError));
            return false;
        }

        Phase = StudioExportPhase.Loading;
        var chapterId = _selection.ChapterId ?? _page.ChapterId;
        if (string.IsNullOrWhiteSpace(chapterId))
        {
            Phase = StudioExportPhase.NotWired;
            _errorText = "没有可用章节：无法预检导出";
            Raise(nameof(ErrorText));
            Raise(nameof(HasError));
            return false;
        }

        _translatedPageIds = await _host.GetTranslatedPageIdsAsync(chapterId, cancellationToken).ConfigureAwait(true);
        _errorText = null;
        Phase = StudioExportPhase.Ready;
        RefreshTargetFileName();
        RaisePreflightProps();
        return true;
    }

    /// <summary>Called by the batch/page models after a projection refresh so counts stay current.</summary>
    public void NotifyRunProjectionChanged() => RaisePreflightProps();

    private void RaisePreflightProps()
    {
        Raise(nameof(TranslatedPageIds));
        Raise(nameof(TranslatedPageCount));
        Raise(nameof(ExportablePageIds));
        Raise(nameof(ExportablePagesText));
        Raise(nameof(FailedPageCount));
        Raise(nameof(BlockedPageCount));
        Raise(nameof(HasRunProjection));
        Raise(nameof(UnconfirmedText));
        Raise(nameof(StaleText));
        Raise(nameof(CanStart));
        Raise(nameof(PhaseText));
        Raise(nameof(TargetFileName));
        Raise(nameof(ScopeText));
    }

    private void RefreshTargetFileName()
    {
        var chapter = _selection.ChapterId ?? _page.ChapterId ?? "chapter";
        var stamp = DateTime.Now.ToString("yyyyMMdd-HHmmss");
        var extension = IsPdf ? "pdf" : "zip";
        _targetFileName = $"newmanga-{chapter}-{stamp}.{extension}";
        Raise(nameof(TargetFileName));
    }

    // ---------------------------------------------------------------- start / poll / cancel

    /// <summary>Starts the export through the Host grant chain (null request → typed refusal kept in place).</summary>
    public async Task<ExportStartInfo?> StartExportAsync(CancellationToken cancellationToken = default)
    {
        if (!CanStart)
        {
            _statusText = Phase == StudioExportPhase.NotWired
                ? "数据不可用：不能导出"
                : ExportablePageIds.Count == 0
                    ? "没有可导出页：至少需要 1 页已翻译页面"
                    : "Host 未就绪或只读：不能导出";
            Raise(nameof(StatusText));
            return null;
        }

        var bookId = _selection.BookId ?? _page.BookId;
        var chapterId = _selection.ChapterId ?? _page.ChapterId;
        if (string.IsNullOrWhiteSpace(bookId) || string.IsNullOrWhiteSpace(chapterId))
        {
            _statusText = "缺少 book/chapter 上下文：不能导出";
            Raise(nameof(StatusText));
            return null;
        }

        var target = Path.Combine(_host.ExportDirectorySuggestion, _targetFileName);
        var started = await _host.StartExportAsync(
            bookId,
            chapterId,
            ExportablePageIds,
            target,
            _format == StudioExportFormat.Pdf ? "pdf" : "zip",
            _format == StudioExportFormat.Pdf
                ? _pdfContent == StudioPdfContentMode.SearchableDualLayer ? "searchable_dual_layer" : "image_only"
                : null,
            stalePolicy: _stalePolicy == StudioStalePolicy.ContinueExisting ? "continue_existing" : "abort",
            cancellationToken).ConfigureAwait(true);

        if (started is null)
        {
            Phase = StudioExportPhase.Failed;
            _errorText = _host.Snapshot.LastError is { } code
                ? code == "EXPORT_STALE"
                    ? "EXPORT_STALE：存在过期输入（abort 策略中止），先重渲染过期页"
                    : $"StartExport 被拒绝：{code}"
                : "StartExport 被拒绝";
            Raise(nameof(ErrorText));
            Raise(nameof(HasError));
            return null;
        }

        _exportId = started.ExportId;
        _snapshot = null;
        _errorText = null;
        _statusText = $"已创建导出 {started.ExportId}（{started.PageCount} 页）";
        Phase = StudioExportPhase.Running;
        LastPollUtc = DateTime.UtcNow;
        Raise(nameof(ExportId));
        Raise(nameof(StatusText));
        Raise(nameof(ErrorText));
        Raise(nameof(HasError));
        await RefreshSnapshotAsync(cancellationToken).ConfigureAwait(true);
        return started;
    }

    private DateTime LastPollUtc
    {
        get => _lastPollUtc;
        set => _lastPollUtc = value;
    }

    /// <summary>One snapshot read; terminal states settle the phase and stop polling.</summary>
    public async Task<ExportSnapshotInfo?> RefreshSnapshotAsync(CancellationToken cancellationToken = default)
    {
        if (_exportId is null)
        {
            return null;
        }

        var snapshot = await _host.GetExportSnapshotAsync(_exportId, cancellationToken).ConfigureAwait(true);
        if (snapshot is null)
        {
            _errorText = _host.Snapshot.LastError is { } code ? $"读取导出快照失败：{code}" : "读取导出快照失败";
            Phase = StudioExportPhase.Failed;
            Raise(nameof(ErrorText));
            Raise(nameof(HasError));
            return null;
        }

        _snapshot = snapshot;
        ApplySnapshotState(snapshot.State);
        Raise(nameof(Snapshot));
        Raise(nameof(SnapshotCompleted));
        Raise(nameof(SnapshotTotal));
        Raise(nameof(SnapshotPercent));
        Raise(nameof(ProgressText));
        Raise(nameof(OutputText));
        Raise(nameof(CanReveal));
        Raise(nameof(CanCancel));
        return snapshot;
    }

    private void ApplySnapshotState(ExportJobState state)
    {
        switch (state)
        {
            case ExportJobState.Completed:
                Phase = StudioExportPhase.Completed;
                _statusText = "导出完成";
                break;
            case ExportJobState.Cancelled:
                Phase = StudioExportPhase.Cancelled;
                _statusText = "导出已取消";
                break;
            case ExportJobState.Failed:
                Phase = StudioExportPhase.Failed;
                _errorText = "导出失败";
                break;
            default:
                Phase = StudioExportPhase.Running;
                break;
        }
    }

    /// <summary>Tick from the view's timer (interval = <see cref="PollInterval"/>); no-op when idle/terminal.</summary>
    public async Task TickAsync(CancellationToken cancellationToken = default)
    {
        if (Phase != StudioExportPhase.Running || _exportId is null)
        {
            return;
        }

        if (DateTime.UtcNow - _lastPollUtc < _pollInterval)
        {
            return;
        }

        _lastPollUtc = DateTime.UtcNow;
        await RefreshSnapshotAsync(cancellationToken).ConfigureAwait(true);
    }

    public async Task<ExportSnapshotInfo?> CancelAsync(CancellationToken cancellationToken = default)
    {
        if (_exportId is null)
        {
            return null;
        }

        var snapshot = await _host.CancelExportAsync(_exportId, cancellationToken).ConfigureAwait(true);
        if (snapshot is not null)
        {
            _snapshot = snapshot;
            ApplySnapshotState(snapshot.State);
            Raise(nameof(Snapshot));
            Raise(nameof(ProgressText));
            Raise(nameof(OutputText));
        }

        _statusText = "已请求取消导出";
        Raise(nameof(StatusText));
        return snapshot;
    }

    /// <summary>「打开导出目录」— only the Host may open a folder; false means it did not happen.</summary>
    public async Task<bool> RevealAsync(CancellationToken cancellationToken = default)
    {
        if (_exportId is null)
        {
            return false;
        }

        var revealed = await _host.RevealExportFolderAsync(_exportId, cancellationToken).ConfigureAwait(true);
        _statusText = revealed ? "已打开导出目录" : "Host 未打开导出目录";
        Raise(nameof(StatusText));
        return revealed;
    }

    /// <summary>「打开导出目录」for a history row (id-based; the Host owns the folder).</summary>
    public async Task<bool> RevealExportAsync(string exportId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(exportId))
        {
            return false;
        }

        var revealed = await _host.RevealExportFolderAsync(exportId, cancellationToken).ConfigureAwait(true);
        _statusText = revealed ? "已打开导出目录" : "Host 未打开导出目录";
        Raise(nameof(StatusText));
        return revealed;
    }

    // ---------------------------------------------------------------- history

    public async Task<bool> LoadHistoryAsync(CancellationToken cancellationToken = default)
    {
        IsHistoryLoading = true;
        Raise(nameof(IsHistoryLoading));
        try
        {
            var entries = await _host.GetExportHistoryAsync(cancellationToken).ConfigureAwait(true);
            History.Clear();
            foreach (var entry in entries.OrderByDescending(item => item.CompletedAt ?? string.Empty, StringComparer.Ordinal))
            {
                History.Add(new StudioExportHistoryItemViewModel(entry));
            }

            Raise(nameof(HistoryEmptyText));
            return true;
        }
        catch (OperationCanceledException)
        {
            return false;
        }
        finally
        {
            IsHistoryLoading = false;
            Raise(nameof(IsHistoryLoading));
        }
    }

    /// <summary>Evidence helper: capability inventory with the verified reasons.</summary>
    public IReadOnlyList<string> BuildCapabilityInventory()
    {
        var items = new List<string>();
        if (!IsHostReady)
        {
            items.Add($"Host 未就绪：{_host.Snapshot.LastError ?? _host.Snapshot.State.ToString()}");
        }

        if (!WritesAllowed)
        {
            items.Add("Host 只读：导出写操作被 Host 拒绝");
        }

        items.Add("stale_policy=abort / continue_existing：两值均由 Host 透传到 Core（V11R-A-7）");
        items.Add("未确认计数：" + UnconfirmedNotWired);
        items.Add("过期计数：" + StaleNotWired);
        return items;
    }
}