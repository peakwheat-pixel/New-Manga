using System.Collections.ObjectModel;
using NewManga.App.Services;
using NewManga.App.Shell.V2;

namespace NewManga.App.ViewModels.V2.Library;

/// <summary>
/// FEA-12-UI: the V2 recycle-bin ViewModel. One data source only (Q3: <c>ListTrash</c>; the frozen
/// <c>ListRecycleBinBooks</c> face stays untouched), opaque cursor kept in memory only, no total
/// count, no thumbnails and no content preview (L2). The permanent-delete flow is the single-book
/// C flow: read-only disclosure (PD-01) → explicit "understood" gate + digest binding → one
/// <c>library_delete_book_permanently</c> frame → typed disposition (stale re-preview, busy
/// pre-block, cleanup retry, not-found refresh).
///
/// The VM keeps the exact reverse-frame discipline from the card: it never calls
/// <c>PurgeTrash</c> (OUT-2), never calls batch permanent delete (OUT-1/L1) and never probes the
/// Core with a command (the capability probe is <c>core.ping</c> only).
/// </summary>
public sealed class TrashViewModel : ObservableObject
{
    private readonly ITrashController? _trash;
    private readonly Func<bool> _writesAllowed;
    private readonly Action<string, NmStatus> _notify;
    private readonly List<TrashEntry> _loaded = new();
    private readonly List<TrashItemRowViewModel> _selectionOrder = new();

    private int _generation;
    private bool _isLoading;
    private bool _isLoadingMore;
    private string? _nextCursor;
    private string? _errorCode;
    private string? _errorMessage;
    private bool _capabilityProbed;
    private bool _capabilityMissing;   // READ face only: the list cannot be shown without it
    private string _capabilityMessage = string.Empty;
    private bool _readAvailable;
    private bool _writeAvailable;
    private bool _previewAvailable;
    private bool _hostReadOnly;        // Host policy only -- never derived from a capability
    private bool _probeFailed;
    private string? _probeErrorCode;
    private string? _probeErrorMessage;
    private string _statusMessage = string.Empty;
    private string _loadedCountText = "已加载 0 项";

    private bool _isPreviewOpen;
    private bool _isPreviewLoading;
    private bool _isDeleting;
    private bool _understood;
    private string _previewTitle = string.Empty;
    private string _previewDigestShort = string.Empty;
    private string _previewProtectionText = string.Empty;
    private string _previewCurrentText = string.Empty;
    private string _previewContentText = string.Empty;
    private string _previewSharedRefsText = string.Empty;
    private string? _previewBlockedReason;
    private string? _previewErrorCode;
    private string? _previewErrorMessage;
    private string? _deleteOutcomeCode;
    private string? _deleteOutcomeText;
    private bool _cleanupPendingVisible;
    private string _deleteResultTitle = string.Empty;

    private string? _activeBookId;
    private string? _activeDigest;
    private TrashPreviewItem? _activeItem;

    public TrashViewModel(
        ITrashController? trash,
        Func<bool> writesAllowed,
        Action<string, NmStatus> notify)
    {
        _trash = trash;
        _writesAllowed = writesAllowed;
        _notify = notify;

        RefreshCommand = new RelayCommand(() => _ = RefreshAsync());
        LoadMoreCommand = new RelayCommand(() => _ = LoadMoreAsync());
        RestoreCommand = new RelayCommand(() => _ = RestoreSelectedAsync());
        CancelPreviewCommand = new RelayCommand(CancelPreview);
        ConfirmDeleteCommand = new RelayCommand(() => _ = ConfirmDeleteAsync());
        RetryCleanupCommand = new RelayCommand(() => _ = RetryCleanupAsync());
        RetryPreviewCommand = new RelayCommand(() =>
        {
            if (IsPreviewOpen && _activeBookId is { Length: > 0 } bookId)
            {
                _ = BeginPermanentDeleteAsync(BuildRow(bookId));
            }
        });
        BeginPermanentDeleteCommand = new RelayCommand(parameter =>
        {
            if (parameter is TrashItemRowViewModel row)
            {
                _ = BeginPermanentDeleteAsync(row);
            }
        });
        CloseResultCommand = new RelayCommand(CloseResult);

        if (_trash is null)
        {
            _capabilityProbed = true;
            _capabilityMissing = true;
            _capabilityMessage = "回收站能力缺失（CORE_CAPABILITY_MISSING）：当前宿主未提供 ITrashController";
            _hostReadOnly = !_writesAllowed();
        }
    }

    public ObservableCollection<TrashItemRowViewModel> Items { get; } = new();

    public RelayCommand RefreshCommand { get; }

    public RelayCommand LoadMoreCommand { get; }

    public RelayCommand RestoreCommand { get; }

    public RelayCommand CancelPreviewCommand { get; }

    public RelayCommand ConfirmDeleteCommand { get; }

    public RelayCommand RetryCleanupCommand { get; }

    /// <summary>AC4 typed failure path: "重新预览" — a new preview frame, never a cached digest.</summary>
    public RelayCommand RetryPreviewCommand { get; }

    public RelayCommand BeginPermanentDeleteCommand { get; }

    public RelayCommand CloseResultCommand { get; }

    public bool HasController => _trash is not null;

    public bool IsLoading
    {
        get => _isLoading;
        private set => Set(ref _isLoading, value);
    }

    public bool IsLoadingMore
    {
        get => _isLoadingMore;
        private set => Set(ref _isLoadingMore, value);
    }

    public bool HasError => _errorMessage is { Length: > 0 };

    public string? ErrorCode => _errorCode;

    public string ErrorMessage => _errorMessage ?? string.Empty;

    /// <summary>READ face missing (or no controller): the list/empty states must not render.</summary>
    public bool IsCapabilityMissing => _capabilityMissing;

    /// <summary>Typed capability gap message for the READ face (list replacement state).</summary>
    public string CapabilityMessage => _capabilityMessage;

    public bool CapabilityProbed => _capabilityProbed;

    /// <summary>Any of the three faces missing while reading is still possible (degraded mode).</summary>
    public bool HasCapabilityGap =>
        _capabilityProbed && (!_readAvailable || !_writeAvailable || !_previewAvailable);

    /// <summary>Typed degraded banner: names exactly which capability is missing (CORE_CAPABILITY_MISSING).</summary>
    public string CapabilityGapMessage
    {
        get
        {
            if (!HasCapabilityGap)
            {
                return string.Empty;
            }

            var missing = new List<string>();
            if (!_readAvailable) missing.Add("library.trash.read/1");
            if (!_writeAvailable) missing.Add("library.trash.write/1");
            if (!_previewAvailable) missing.Add("library.delete.preview/1");
            var impact = (!_writeAvailable, !_previewAvailable) switch
            {
                (true, true) => "软删/恢复/彻底删除已禁用",
                (true, false) => "软删/恢复/彻底删除已禁用（列表只读可用）",
                (false, true) => "彻底删除已禁用（恢复仍可用）",
                _ => "回收站部分能力不可用",
            };
            return $"能力受限（CORE_CAPABILITY_MISSING）：Core 未公布 {string.Join(" / ", missing)}；{impact}";
        }
    }

    /// <summary>Host policy read-only: only the Host write gate, NEVER a capability result.</summary>
    public bool IsHostReadOnly => _hostReadOnly;

    /// <summary>
    /// I-4: the Host read-only policy and a Core capability gap are two INDEPENDENT causes; whenever the
    /// Host is really read-only its banner is shown (it is never suppressed by a capability gap).
    /// </summary>
    public bool ShowHostReadOnlyBanner => _hostReadOnly;

    /// <summary>
    /// Typed Host read-only banner text (the literal HOST_READ_ONLY stays visible). It must not claim the
    /// recycle bin is browsable: the READ capability can be missing at the same time (I-4 / L-R7).
    /// </summary>
    public string HostReadOnlyBannerText =>
        "Host 处于只读模式（HOST_READ_ONLY）：不会执行任何写入；软删/恢复/彻底删除已禁用。";

    /// <summary>Independent failure state for a failed capability probe (CORE_UNAVAILABLE etc.).</summary>
    public bool IsProbeFailed => _probeFailed;

    public bool ShowProbeErrorState => !IsLoading && _probeFailed && !_capabilityMissing;

    public string? ProbeErrorCode => _probeErrorCode;

    public string ProbeErrorMessage => _probeErrorMessage ?? string.Empty;

    /// <summary>Probe failed: list data is unknowable, so the empty state must not claim "回收站是空的".</summary>
    public bool CanWrite => _writeAvailable && !_hostReadOnly && _trash is not null;

    public bool CanPreview => _previewAvailable && _trash is not null;

    public bool IsEmpty => !IsLoading && !HasError && !_capabilityMissing && !_probeFailed && Items.Count == 0;

    public string LoadedCountText => _loadedCountText;

    public bool HasMore => _nextCursor is not null;

    public bool ShowList => !IsLoading && !HasError && !_capabilityMissing && !_probeFailed && Items.Count > 0;

    public bool ShowEmptyState => IsEmpty;

    public bool ShowErrorState => !IsLoading && HasError;

    /// <summary>READ capability missing: the whole page is replaced by the typed capability state.</summary>
    public bool ShowCapabilityState => !IsLoading && _capabilityMissing;

    /// <summary>Partial capability gap: the list stays visible plus a typed degraded banner.</summary>
    public bool ShowCapabilityDegraded => !IsLoading && HasCapabilityGap && !_capabilityMissing && !_probeFailed;

    public string StatusMessage => _statusMessage;

    public bool HasStatus => _statusMessage.Length > 0;

    public int SelectionCount => _selectionOrder.Count;

    public bool HasSelection => _selectionOrder.Count > 0;

    /// <summary>AC7⑤: restore is gated by WRITE only (a missing preview must not disable restore).</summary>
    public bool CanRestore => HasSelection && CanWrite && !IsBusy;

    public string SelectionSummary => HasSelection
        ? $"已选 {SelectionCount} 项"
        : "勾选条目后可恢复";

    public bool IsBusy => _isPreviewLoading || _isDeleting;

    // ── permanent-delete disclosure / confirmation ─────────────────────────────────────

    public bool IsPreviewOpen
    {
        get => _isPreviewOpen;
        private set => Set(ref _isPreviewOpen, value);
    }

    public bool IsPreviewLoading
    {
        get => _isPreviewLoading;
        private set
        {
            if (Set(ref _isPreviewLoading, value))
            {
                OnPropertyChanged(nameof(IsBusy), nameof(CanConfirmDelete), nameof(CanRestore));
            }
        }
    }

    public bool IsDeleting
    {
        get => _isDeleting;
        private set
        {
            if (Set(ref _isDeleting, value))
            {
                OnPropertyChanged(nameof(IsBusy), nameof(CanConfirmDelete), nameof(CanRestore));
            }
        }
    }

    public string PreviewTitle => _previewTitle;

    public string PreviewDigestShortText => _previewDigestShort;

    public string PreviewProtectionText => _previewProtectionText;

    public string PreviewCurrentText => _previewCurrentText;

    public string PreviewContentText => _previewContentText;

    public string PreviewSharedRefsText => _previewSharedRefsText;

    /// <summary>Why confirmation is blocked (unknown current set / active runs / read-only); null = confirmable.</summary>
    public string? PreviewBlockedReason => _previewBlockedReason;

    public bool IsPreviewBlocked => _previewBlockedReason is { Length: > 0 };

    public string? PreviewErrorCode => _previewErrorCode;

    public string PreviewErrorMessage => _previewErrorMessage ?? string.Empty;

    public bool HasPreviewError => _previewErrorMessage is { Length: > 0 };

    /// <summary>AC5 hard gate: explicit "I understand this cannot be undone" checkbox.</summary>
    public bool UnderstandIrrecoverable
    {
        get => _understood;
        set
        {
            if (Set(ref _understood, value))
            {
                OnPropertyChanged(nameof(CanConfirmDelete));
            }
        }
    }

    /// <summary>
    /// Enabled only when: preview loaded, nothing in flight, the disclosure is complete+known,
    /// no protection/busy/read-only block, and the hard "understood" gate is checked.
    /// </summary>
    public bool CanConfirmDelete =>
        IsPreviewOpen && !IsPreviewLoading && !IsDeleting && _understood &&
        !IsPreviewBlocked && !HasPreviewError && _activeDigest is { Length: > 0 } &&
        CanWrite && CanPreview;

    public bool IsCleanupPending => _cleanupPendingVisible;

    public bool HasDeleteResult => _deleteOutcomeCode is not null || _cleanupPendingVisible;

    public string DeleteResultTitle => _deleteResultTitle;

    public string DeleteOutcomeText => _deleteOutcomeText ?? string.Empty;

    public string? DeleteOutcomeCode => _deleteOutcomeCode;

    /// <summary>
    /// L3 narrowed per r1 P2-1: the cleanup retry stays reachable only while the result panel is
    /// kept open; the close path states explicitly that closing loses the retry (no pending list
    /// command exists, and a re-preview of a cleanup-pending book is BOOK_NOT_FOUND on the Core).
    /// </summary>
    public bool CanRetryCleanup => _cleanupPendingVisible && CanWrite && _activeBookId is not null && _activeDigest is not null;

    // ── list flow ──────────────────────────────────────────────────────────────────────

    /// <summary>AC1/IN-2: entering the page probes capabilities once, then sends exactly one list frame.</summary>
    public async Task EnterAsync()
    {
        var generation = ++_generation;
        ResetTransientState();
        Items.Clear();
        _loaded.Clear();
        _selectionOrder.Clear();
        OnPropertyChanged(nameof(SelectionCount), nameof(HasSelection), nameof(SelectionSummary), nameof(CanRestore));
        _nextCursor = null;
        _loadedCountText = "已加载 0 项";
        _errorCode = null;
        _errorMessage = null;
        IsLoading = true;
        RaiseStates();
        await ProbeAndLoadAsync(generation, reset: true).ConfigureAwait(true);
    }

    /// <summary>Leaving the page clears list, cursor, digest and the understood checkbox (AC1).</summary>
    public void Exit()
    {
        _generation++;
        ResetTransientState();
        Items.Clear();
        _loaded.Clear();
        _selectionOrder.Clear();
        _nextCursor = null;
        _loadedCountText = "已加载 0 项";
        IsLoading = false;
        _errorCode = null;
        _errorMessage = null;
        RaiseStates();
        OnPropertyChanged(nameof(SelectionCount), nameof(HasSelection), nameof(SelectionSummary), nameof(CanRestore),
            nameof(LoadedCountText));
    }

    public Task RefreshAsync() => ReloadAsync();

    public Task LoadMoreAsync()
    {
        // r1 P3: re-entry guard - a double click must not send two frames with the same cursor.
        if (IsLoading || IsLoadingMore || _nextCursor is null)
        {
            return Task.CompletedTask;
        }

        return LoadAsync(_nextCursor, append: true);
    }

    private async Task ReloadAsync()
    {
        var generation = ++_generation;
        ResetTransientState();
        _errorCode = null;
        _errorMessage = null;
        IsLoading = true;
        _nextCursor = null;
        RaiseStates();
        await ProbeAndLoadAsync(generation, reset: true).ConfigureAwait(true);
    }

    private async Task ProbeAndLoadAsync(int generation, bool reset)
    {
        // r1 P1-1: Host read-only, capability gaps and probe failure are THREE independent states.
        _hostReadOnly = !_writesAllowed();
        _probeFailed = false;
        _probeErrorCode = null;
        _probeErrorMessage = null;

        if (_trash is null)
        {
            _capabilityProbed = true;
            _capabilityMissing = true;
            _capabilityMessage = "回收站能力缺失（CORE_CAPABILITY_MISSING）：当前宿主未提供 ITrashController";
            IsLoading = false;
            RaiseStates();
            return;
        }

        var probe = await _trash.ProbeTrashCapabilitiesAsync().ConfigureAwait(true);
        if (generation != _generation)
        {
            return;
        }

        _capabilityProbed = probe.Probed;
        if (!probe.Probed)
        {
            // Not a capability verdict: the probe itself failed (CORE_UNAVAILABLE / channel error).
            _probeFailed = true;
            _probeErrorCode = probe.Code ?? TrashErrorCodes.CoreUnavailable;
            _probeErrorMessage = "回收站能力探测失败（" + _probeErrorCode + "）：" +
                (probe.Message ?? "Core/通道不可用，未发送任何回收站命令") + "；可重试。";
            _readAvailable = false;
            _writeAvailable = false;
            _previewAvailable = false;
            _capabilityMissing = false;
            IsLoading = false;
            RaiseStates();
            return;
        }

        _readAvailable = probe.ReadAvailable;
        _writeAvailable = probe.WriteAvailable;
        _previewAvailable = probe.PreviewAvailable;
        _capabilityMissing = !_readAvailable;
        _capabilityMessage = _capabilityMissing
            ? "回收站能力缺失（CORE_CAPABILITY_MISSING）：Core 未公布 library.trash.read/1，回收站列表不可用"
            : string.Empty;

        if (_capabilityMissing)
        {
            IsLoading = false;
            RaiseStates();
            return;
        }

        await LoadAsync(null, append: false, generation).ConfigureAwait(true);
    }

    private async Task LoadAsync(string? cursor, bool append, int? expectedGeneration = null)
    {
        if (_trash is null)
        {
            return;
        }

        var generation = expectedGeneration ?? _generation;
        if (append)
        {
            IsLoadingMore = true;
        }
        else
        {
            IsLoading = true;
        }

        var page = await _trash.ListTrashAsync(cursor).ConfigureAwait(true);
        if (generation != _generation)
        {
            // AC1: a late response from a previous entry must not repaint the current list.
            return;
        }

        if (!page.Ok)
        {
            _errorCode = page.Code;
            _errorMessage = page.Message ?? "读取回收站失败";
            IsLoading = false;
            IsLoadingMore = false;
            RaiseStates();
            return;
        }

        if (!append)
        {
            Items.Clear();
            _loaded.Clear();
            _selectionOrder.Clear();
        }

        foreach (var entry in page.Items)
        {
            _loaded.Add(entry);
            var row = new TrashItemRowViewModel(entry);
            row.SelectionChanged += OnRowSelectionChanged;
            Items.Add(row);
        }

        _nextCursor = page.NextCursor;
        _loadedCountText = $"已加载 {_loaded.Count} 项";
        _errorCode = null;
        _errorMessage = null;
        IsLoading = false;
        IsLoadingMore = false;
        RaiseStates();
        OnPropertyChanged(nameof(LoadedCountText), nameof(SelectionSummary), nameof(SelectionCount), nameof(HasSelection), nameof(CanRestore));
    }

    private void OnRowSelectionChanged(object? sender, EventArgs e)
    {
        if (sender is not TrashItemRowViewModel row)
        {
            return;
        }

        _selectionOrder.Remove(row);
        if (row.IsSelected)
        {
            _selectionOrder.Add(row);
        }

        OnPropertyChanged(nameof(SelectionCount), nameof(HasSelection), nameof(SelectionSummary), nameof(CanRestore));
        RestoreCommand.RaiseCanExecuteChanged();
    }

    // ── restore (1..N) ─────────────────────────────────────────────────────────────────

    public async Task RestoreSelectedAsync()
    {
        if (_trash is null || !CanRestore || _selectionOrder.Count == 0)
        {
            return;
        }

        var targets = _selectionOrder.Select(row => row.BookId).ToArray();
        _statusMessage = $"正在恢复 {targets.Length} 项…";
        OnPropertyChanged(nameof(StatusMessage), nameof(HasStatus));
        var generation = _generation;
        var result = await _trash
            .RestoreFromTrashAsync(targets, TrashIdempotency.NewKey())
            .ConfigureAwait(true);
        if (generation != _generation)
        {
            return;
        }

        if (!result.Ok && result.SucceededIds.Count == 0 && result.FailedItems.Count == 0)
        {
            _notify($"恢复失败（{result.Code ?? TrashErrorCodes.Unknown}）：{result.Message ?? "未执行任何写入"}", NmStatus.Failed);
            _statusMessage = result.Message ?? "恢复失败";
            OnPropertyChanged(nameof(StatusMessage), nameof(HasStatus));
            return;
        }

        var restored = new HashSet<string>(result.SucceededIds, StringComparer.Ordinal);
        foreach (var row in Items.Where(row => restored.Contains(row.BookId)).ToArray())
        {
            row.SelectionChanged -= OnRowSelectionChanged;
            Items.Remove(row);
            _selectionOrder.Remove(row);
            _loaded.RemoveAll(entry => string.Equals(entry.BookId, row.BookId, StringComparison.Ordinal));
        }

        // AC3/IN-4: per-item reasons; never "pretend the whole batch succeeded".
        foreach (var issue in result.FailedItems)
        {
            var row = Items.FirstOrDefault(candidate => string.Equals(candidate.BookId, issue.BookId, StringComparison.Ordinal));
            if (row is not null)
            {
                row.ConflictReasonText = issue.ReasonText;
            }
        }

        _loadedCountText = $"已加载 {_loaded.Count} 项";
        _statusMessage = result.FailedItems.Count == 0
            ? $"已恢复 {result.SucceededIds.Count} 项"
            : $"已恢复 {result.SucceededIds.Count} 项，{result.FailedItems.Count} 项未恢复（见逐项说明）";
        _notify(_statusMessage, result.FailedItems.Count == 0 ? NmStatus.Done : NmStatus.Failed);
        RaiseStates();
        OnPropertyChanged(nameof(StatusMessage), nameof(HasStatus), nameof(LoadedCountText),
            nameof(SelectionCount), nameof(HasSelection), nameof(SelectionSummary), nameof(CanRestore));
    }

    // ── permanent delete: disclosure → understood gate → digest-bound frame ───────────

    public async Task BeginPermanentDeleteAsync(TrashItemRowViewModel row)
    {
        if (_trash is null)
        {
            return;
        }

        // AC7⑤: permanent delete is gated by WRITE + PREVIEW separately from restore/write-only.
        if (!CanPreview)
        {
            _notify("彻底删除不可用（CORE_CAPABILITY_MISSING：缺少 library.delete.preview/1）；未发送任何帧", NmStatus.Blocked);
            return;
        }

        if (!CanWrite)
        {
            _notify(_hostReadOnly
                    ? "彻底删除被拒绝：Host 处于只读模式（HOST_READ_ONLY）"
                    : "彻底删除不可用（CORE_CAPABILITY_MISSING：缺少 library.trash.write/1）",
                NmStatus.Blocked);
            return;
        }

        ResetPreview();
        _activeBookId = row.BookId;
        _activeItem = null;
        _activeDigest = null;
        IsPreviewOpen = true;
        IsPreviewLoading = true;
        _previewTitle = row.Title;
        _previewCurrentText = "读取中…";
        _previewProtectionText = "读取中…";
        _previewContentText = "读取中…";
        _previewSharedRefsText = "读取中…";
        RaisePreviewStates();

        var generation = _generation;
        var preview = await _trash
            .PreviewPermanentDeleteAsync(new[] { row.BookId })
            .ConfigureAwait(true);
        if (generation != _generation)
        {
            return;
        }

        IsPreviewLoading = false;
        if (!preview.Ok && string.Equals(preview.Code, TrashErrorCodes.BookNotFound, StringComparison.Ordinal))
        {
            // I-2 (AC4 "提示并刷新"): the book is gone (no longer returned by the list). Keep no ghost
            // disclosure panel, tell the user and refresh ONCE; never re-preview or send a delete frame.
            _notify("作品已不存在（BOOK_NOT_FOUND）：已刷新回收站列表", NmStatus.Failed);
            ResetPreview();
            RaisePreviewStates();
            await ReloadAsync().ConfigureAwait(true);
            return;
        }

        if (!preview.Ok || preview.Items.Count == 0 || string.IsNullOrEmpty(preview.InventoryDigest))
        {
            _previewErrorCode = preview.Code ?? TrashErrorCodes.Unknown;
            _previewErrorMessage = "读取删除影响清单失败（" + (preview.Code ?? TrashErrorCodes.Unknown) + "）：" + (preview.Message ?? "未启用确认");
            RaisePreviewStates();
            return;
        }

        var item = preview.Items[0];
        if (!preview.Digests.TryGetValue(item.BookId, out var boundDigest) || boundDigest.Length == 0)
        {
            // §5.13: the single delete is bound to the PER-BOOK digest; without it the confirmation
            // must not be enabled (a collection digest would be stale on the Core).
            _previewErrorCode = preview.Code ?? TrashErrorCodes.Unknown;
            _previewErrorMessage = "删除预览没有返回该作品的逐书 inventoryDigests，无法绑定确认（已禁用彻底删除）";
            RaisePreviewStates();
            return;
        }

        _activeItem = item;
        _activeDigest = boundDigest;
        _previewTitle = item.Title.Length > 0 ? item.Title : row.Title;
        _previewDigestShort = "确认绑定 " + ShortDigest(boundDigest) +
            (preview.InventoryDigest is { Length: > 0 } collection ? " · 集合 " + ShortDigest(collection) : string.Empty);
        _previewProtectionText = BuildProtectionText(item.Protection, item.Content);
        _previewCurrentText = BuildCurrentText(item.Protection);
        _previewContentText = BuildContentText(item.Content);
        _previewSharedRefsText = BuildSharedRefsText(item.SharedFileRefs);
        _previewBlockedReason = BuildBlockedReason(item, out var blockedCode);
        _previewErrorCode = null;
        _previewErrorMessage = null;
        if (blockedCode is not null)
        {
            _notify(blockedCode, NmStatus.Blocked);
        }

        RaisePreviewStates();
    }

    public void CancelPreview()
    {
        if (IsDeleting)
        {
            return;
        }

        ResetPreview();
        RaisePreviewStates();
    }

    private async Task ConfirmDeleteAsync()
    {
        if (_trash is null || !CanConfirmDelete || _activeBookId is null || _activeDigest is null)
        {
            return;
        }

        IsDeleting = true;
        IsPreviewLoading = false;
        _deleteOutcomeCode = null;
        _deleteOutcomeText = null;
        _cleanupPendingVisible = false;
        _deleteResultTitle = string.Empty;
        RaisePreviewStates();

        var generation = _generation;
        var bookId = _activeBookId;
        var digest = _activeDigest;
        var result = await _trash.DeletePermanentlyAsync(bookId, digest).ConfigureAwait(true);
        if (generation != _generation)
        {
            return;
        }

        IsDeleting = false;
        switch (result.Outcome)
        {
            case TrashDeleteOutcome.Deleted:
                RemoveDeletedRow(bookId);
                _notify("已彻底删除该作品（单事务提交；应用内删除不含原文件）", NmStatus.Done);
                ResetPreview();
                RaisePreviewStates();
                return;

            case TrashDeleteOutcome.CleanupPending:
                _cleanupPendingVisible = true;
                _deleteOutcomeCode = result.Code ?? TrashErrorCodes.CleanupPending;
                _deleteOutcomeText =
                    "内容已删除，但文件清理尚未完成（BOOK_DELETE_CLEANUP_PENDING）。" +
                    "可在本会话内用同一 digest 重试清理；不会重新进行预览确认。";
                _deleteResultTitle = "待重试清理";
                _notify("已删除内容，文件清理待重试（未伪报完成）", NmStatus.Queued);
                RaisePreviewStates();
                return;

            case TrashDeleteOutcome.Stale:
                _notify("确认信息已过期（BOOK_DELETE_STALE_PREVIEW）：未删除任何内容，正在重新读取影响清单", NmStatus.Stale);
                _understood = false;
                OnPropertyChanged(nameof(UnderstandIrrecoverable));
                ResetPreviewKeepTarget(bookId);
                await BeginPermanentDeleteAsync(BuildRow(bookId)).ConfigureAwait(true);
                return;

            case TrashDeleteOutcome.Busy:
                _previewBlockedReason = "作品存在进行中的任务（BOOK_BUSY），删除被拒绝且未产生任何写入";
                _deleteOutcomeCode = result.Code;
                _deleteOutcomeText = "删除被拒绝：BOOK_BUSY（零删除帧写入，未删除任何内容）";
                _deleteResultTitle = "删除被拒绝";
                RaisePreviewStates();
                return;

            case TrashDeleteOutcome.NotFound:
                _notify("作品已不存在（BOOK_NOT_FOUND）：已刷新回收站列表", NmStatus.Failed);
                ResetPreview();
                RaisePreviewStates();
                await ReloadAsync().ConfigureAwait(true);
                return;

            case TrashDeleteOutcome.ReadOnly:
                _previewBlockedReason = "Host 处于只读模式，删除被拒绝";
                _deleteOutcomeCode = result.Code;
                _deleteOutcomeText = "删除被拒绝：Host 只读（未删除任何内容）";
                _deleteResultTitle = "删除被拒绝";
                RaisePreviewStates();
                return;

            case TrashDeleteOutcome.CapabilityMissing:
                // I-1 defensive invariant only (production-unreachable today): a delete-time result is
                // NOT a page-level READ capability verdict, so the real list stays and no probe is
                // re-run. The typed result is shown and the same stale preview cannot be confirmed again.
                _deleteOutcomeCode = result.Code ?? TrashErrorCodes.CapabilityMissing;
                _deleteOutcomeText =
                    "删除被拒绝：Core 未公布删除能力（CORE_CAPABILITY_MISSING，未删除任何内容）；" +
                    "可点「刷新」重新探测能力。";
                _deleteResultTitle = "删除被拒绝";
                _previewBlockedReason = "删除返回能力缺失（CORE_CAPABILITY_MISSING）：本预览不可再确认，可刷新重新探测";
                RaisePreviewStates();
                RaiseStates();
                return;

            default:
                _deleteOutcomeCode = result.Code ?? TrashErrorCodes.Unknown;
                _deleteOutcomeText = (result.Outcome == TrashDeleteOutcome.Failed
                        ? "删除失败，未确认任何写入："
                        : "删除未完成：") + (result.Code ?? TrashErrorCodes.Unknown) +
                    "（" + (result.Message ?? "见日志") + "）";
                _deleteResultTitle = "删除未完成";
                _notify(_deleteOutcomeText, NmStatus.Failed);
                RaisePreviewStates();
                return;
        }
    }

    /// <summary>PD-07 retry: SAME book id + SAME persisted digest; no new preview (AC6/L3).</summary>
    private async Task RetryCleanupAsync()
    {
        if (_trash is null || !CanRetryCleanup || _activeBookId is null || _activeDigest is null)
        {
            return;
        }

        IsDeleting = true;
        RaisePreviewStates();
        var generation = _generation;
        var bookId = _activeBookId;
        var result = await _trash.DeletePermanentlyAsync(bookId, _activeDigest).ConfigureAwait(true);
        if (generation != _generation)
        {
            return;
        }

        IsDeleting = false;
        if (result.Outcome == TrashDeleteOutcome.Deleted)
        {
            RemoveDeletedRow(bookId);
            _notify("清理重试成功：文件清理已完成", NmStatus.Done);
            ResetPreview();
            RaisePreviewStates();
            return;
        }

        _cleanupPendingVisible = result.Outcome == TrashDeleteOutcome.CleanupPending;
        _deleteOutcomeCode = result.Code ?? TrashErrorCodes.Unknown;
        _deleteOutcomeText = result.Outcome == TrashDeleteOutcome.NotFound
            ? "清理重试：条目已不存在，已刷新列表"
            : $"清理重试未完成（{_deleteOutcomeCode}），未伪报完成";
        if (result.Outcome == TrashDeleteOutcome.NotFound)
        {
            // I-3: the result text set above is cleared by ResetPreview right below, so the user would
            // never see it -- the typed notice must go through _notify. Refresh ONCE, never auto-retry.
            _notify("作品已不存在（BOOK_NOT_FOUND）：已刷新回收站列表", NmStatus.Failed);
            ResetPreview();
            await ReloadAsync().ConfigureAwait(true);
        }

        RaisePreviewStates();
    }

    private void CloseResult()
    {
        if (IsDeleting)
        {
            return;
        }

        if (_cleanupPendingVisible && HasDeleteResult)
        {
            // r1 P2-1: closing really loses the retry (no pending-list command; a re-preview of a
            // cleanup-pending book is BOOK_NOT_FOUND on the Core). Say exactly that.
            _notify("关闭结果后本会话内将无法再重试清理（wire 无 pending 清单；重新预览会 BOOK_NOT_FOUND）；如需重试请先点「重试清理」。",
                NmStatus.Blocked);
        }

        ResetPreview();
        RaisePreviewStates();
    }

    private void RemoveDeletedRow(string bookId)
    {
        var row = Items.FirstOrDefault(candidate => string.Equals(candidate.BookId, bookId, StringComparison.Ordinal));
        if (row is null)
        {
            return;
        }

        row.SelectionChanged -= OnRowSelectionChanged;
        Items.Remove(row);
        _selectionOrder.Remove(row);
        _loaded.RemoveAll(entry => string.Equals(entry.BookId, bookId, StringComparison.Ordinal));
        _loadedCountText = $"已加载 {_loaded.Count} 项";
        RaiseStates();
        OnPropertyChanged(nameof(LoadedCountText), nameof(SelectionCount), nameof(HasSelection),
            nameof(SelectionSummary), nameof(CanRestore));
    }

    private TrashItemRowViewModel BuildRow(string bookId)
    {
        var row = Items.FirstOrDefault(candidate => string.Equals(candidate.BookId, bookId, StringComparison.Ordinal));
        if (row is not null)
        {
            return row;
        }

        var entry = _loaded.FirstOrDefault(candidate => string.Equals(candidate.BookId, bookId, StringComparison.Ordinal));
        return new TrashItemRowViewModel(entry ?? new TrashEntry(bookId, bookId, string.Empty));
    }

    private void ResetPreviewKeepTarget(string bookId)
    {
        ResetPreview();
        _activeBookId = bookId;
        IsPreviewOpen = true;
        IsPreviewLoading = true;
        _previewTitle = BuildRow(bookId).Title;
        _previewCurrentText = "重新读取中…";
        _previewProtectionText = "重新读取中…";
        _previewContentText = "重新读取中…";
        _previewSharedRefsText = "重新读取中…";
        RaisePreviewStates();
    }

    private void ResetPreview()
    {
        _isPreviewOpen = false;
        _isPreviewLoading = false;
        _isDeleting = false;
        _understood = false;
        _previewTitle = string.Empty;
        _previewDigestShort = string.Empty;
        _previewProtectionText = string.Empty;
        _previewCurrentText = string.Empty;
        _previewContentText = string.Empty;
        _previewSharedRefsText = string.Empty;
        _previewBlockedReason = null;
        _previewErrorCode = null;
        _previewErrorMessage = null;
        _deleteOutcomeCode = null;
        _deleteOutcomeText = null;
        _deleteResultTitle = string.Empty;
        _cleanupPendingVisible = false;
        _activeItem = null;
        _activeBookId = null;
        _activeDigest = null;
        OnPropertyChanged(nameof(UnderstandIrrecoverable));
    }

    private void ResetTransientState()
    {
        ResetPreview();
    }

    private void RaisePreviewStates() =>
        OnPropertyChanged(
            nameof(IsPreviewOpen), nameof(IsPreviewLoading), nameof(IsDeleting), nameof(IsBusy),
            nameof(PreviewTitle), nameof(PreviewDigestShortText), nameof(PreviewProtectionText),
            nameof(PreviewCurrentText), nameof(PreviewContentText), nameof(PreviewSharedRefsText),
            nameof(PreviewBlockedReason), nameof(IsPreviewBlocked), nameof(PreviewErrorCode),
            nameof(PreviewErrorMessage), nameof(HasPreviewError), nameof(UnderstandIrrecoverable),
            nameof(CanConfirmDelete), nameof(IsCleanupPending), nameof(HasDeleteResult),
            nameof(DeleteResultTitle), nameof(DeleteOutcomeText), nameof(DeleteOutcomeCode),
            nameof(CanRetryCleanup), nameof(CanRestore));

    private void RaiseStates() =>
        OnPropertyChanged(
            nameof(IsLoading), nameof(IsLoadingMore), nameof(HasError), nameof(ErrorCode), nameof(ErrorMessage),
            nameof(IsCapabilityMissing), nameof(CapabilityMessage), nameof(CapabilityProbed),
            nameof(HasCapabilityGap), nameof(CapabilityGapMessage),
            nameof(IsHostReadOnly), nameof(ShowHostReadOnlyBanner), nameof(HostReadOnlyBannerText),
            nameof(IsProbeFailed), nameof(ShowProbeErrorState), nameof(ProbeErrorCode), nameof(ProbeErrorMessage),
            nameof(CanWrite), nameof(CanPreview), nameof(IsEmpty), nameof(LoadedCountText),
            nameof(HasMore), nameof(ShowList), nameof(ShowEmptyState), nameof(ShowErrorState),
            nameof(ShowCapabilityState), nameof(ShowCapabilityDegraded),
            nameof(StatusMessage), nameof(HasStatus), nameof(CanRestore), nameof(CanConfirmDelete));

    private string? BuildBlockedReason(TrashPreviewItem item, out string? notifyCode)
    {
        notifyCode = null;
        if (!item.Protection.CurrentSetKnown)
        {
            notifyCode = "当前 Core 未返回完整 current 保护集（old Core / 字段缺失）：按 fail-closed 禁止彻底删除";
            return "无法确认完整 current 保护集（旧 Core 未返回 currentRegionRevisionIds/currentArtifactRevisionIds）：已禁用彻底删除";
        }

        if (item.Protection.ActiveRunIds.Count > 0)
        {
            notifyCode = "作品有进行中的任务（BOOK_BUSY 预阻断）：未发送任何删除帧";
            return $"存在 {item.Protection.ActiveRunIds.Count} 个进行中的任务（BOOK_BUSY）：先结束任务再删除";
        }

        if (_hostReadOnly)
        {
            return "Host 处于只读模式（HOST_READ_ONLY）：彻底删除已禁用";
        }

        if (!CanPreview || !CanWrite)
        {
            return "能力受限（CORE_CAPABILITY_MISSING）：彻底删除所需的 write/preview 能力缺失";
        }

        return null;
    }

    private static string BuildProtectionText(TrashProtection protection, TrashContentSummary content) =>
        $"锁定 {protection.LockCount} 项 · 人工修改区域 {protection.ManualRegionCount} 处 · " +
        $"活动草稿页 {protection.DraftPageCount} 页 · 进行中任务 {protection.ActiveRunIds.Count} 个 · " +
        $"固定版本 {protection.PinnedRevisionIds.Count} 个 · 删除文件 {content.DeletedFiles} 个（{TrashCopy.BytesText(content.DeletedBytes)}）";

    private static string BuildCurrentText(TrashProtection protection) =>
        protection.CurrentSetKnown
            ? $"受保护 current：region {protection.CurrentRegionCount} 个 / artifact {protection.CurrentArtifactCount} 个" +
              (protection.CurrentRevisionId is { Length: > 0 } id ? $"（代表 {id}）" : string.Empty)
            : "受保护 current：未知（旧 Core 未返回完整集合，未当作 0）";

    private static string BuildContentText(TrashContentSummary content) =>
        $"内容：{content.Chapters} 章节 · {content.Pages} 页 · {content.Artifacts} 个 artifact";

    private static string BuildSharedRefsText(IReadOnlyList<TrashSharedFileRef> refs) =>
        refs.Count == 0
            ? "共享引用：无"
            : "共享引用：" + string.Join("、", refs.Select(reference =>
                $"{reference.FileId}（另有 {reference.OtherProjectCount} 个项目引用）"));

    private static string ShortDigest(string digest) =>
        digest.Length <= 18 ? digest : digest[..18] + "…";
}

/// <summary>One recycle-bin row (book-level only; no thumbnail/content preview).</summary>
public sealed class TrashItemRowViewModel : ObservableObject
{
    private bool _isSelected;
    private string? _conflictReasonText;

    public TrashItemRowViewModel(TrashEntry entry)
    {
        BookId = entry.BookId;
        Title = entry.Title.Length > 0 ? entry.Title : entry.BookId;
        DeletedAt = entry.DeletedAt;
    }

    public event EventHandler? SelectionChanged;

    public string BookId { get; }

    public string Title { get; }

    public string DeletedAt { get; }

    public bool IsSelected
    {
        get => _isSelected;
        set
        {
            if (Set(ref _isSelected, value))
            {
                SelectionChanged?.Invoke(this, EventArgs.Empty);
            }
        }
    }

    /// <summary>Typed per-item restore conflict reason (whitelist + fallback; null = no issue).</summary>
    public string? ConflictReasonText
    {
        get => _conflictReasonText;
        set
        {
            if (Set(ref _conflictReasonText, value))
            {
                OnPropertyChanged(nameof(HasConflict));
            }
        }
    }

    public bool HasConflict => _conflictReasonText is { Length: > 0 };

    public string DeletedAtText => DeletedAt.Length > 0 ? $"删除于 {DeletedAt}" : "删除时间未知";
}
