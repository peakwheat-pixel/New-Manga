using System.Collections.ObjectModel;
using NewManga.App.Services;
using NewManga.App.Shell.V2;

namespace NewManga.App.ViewModels.V2.Library;

/// <summary>
/// V11R-B-1: the Library import dock (screen spec §2). Files are imported one by one through the
/// existing <see cref="IHostController.ImportFilesAsync"/> seam so every row carries a REAL per-file
/// outcome (imported / duplicate-skipped / failed) instead of a fabricated aggregate. A folder is a
/// single Host call, so its row honestly reports the aggregate result.
/// The "no chapter yet" entry closes audit F011: it calls the real Core <c>CreateChapterAsync</c>
/// (V11R-A-1, merged); it never pretends to succeed and never fabricates a chapter.
/// FEA-09-UI-1: the dock additionally carries the referenced-source import face (plan preview →
/// optional password → confirm → running cancel → receipt polling) through the C-16 v1.1
/// command face. That face is the SEPARATE <see cref="ISourceImportController"/> capability
/// (the frozen C-07 <see cref="IHostController"/> inventory is not widened); the dock resolves
/// it from the injected controller and reports a typed refusal when it is absent. The legacy
/// managed path above is untouched; the password never appears in any displayed text and is
/// cleared immediately after the single start call.
/// </summary>
public sealed class ImportDockViewModel : ObservableObject
{
    private readonly IHostController _controller;
    private readonly ISourceImportController? _sourceImport;
    private readonly IFilePickerGateway? _picker;
    private readonly Action<string, NmStatus> _notify;
    private readonly Func<string?> _chapterId;
    private readonly Func<string?> _chapterTitle;
    private readonly Func<Task> _afterImport;
    private readonly Action _requestCreateChapter;
    private readonly Func<Task> _referencePollDelay;
    private bool _isOpen;
    private bool _isRunning;
    private string _summary = string.Empty;

    // FEA-09-UI-1 referenced-import state.
    private SourcePlanPreview? _activePlan;
    private IReadOnlyList<ReferenceImportSource>? _referenceSources;
    private string? _activeOperationId;
    private bool _isReferenceRunning;
    private string _referencePassword = string.Empty;
    private string _referencePlanSummary = string.Empty;
    private string _referenceProgressText = string.Empty;
    private string _referenceErrorText = string.Empty;

    public ImportDockViewModel(
        IHostController controller,
        IFilePickerGateway? picker,
        Action<string, NmStatus> notify,
        Func<string?> chapterId,
        Func<string?> chapterTitle,
        Func<Task> afterImport,
        Action requestCreateChapter,
        Func<Task>? referencePollDelay = null)
    {
        _controller = controller;
        // FEA-09-UI-1: the referenced-import face is an OPTIONAL capability next to the frozen
        // C-07 IHostController inventory — no constructor signature change (LibraryViewModel and
        // every existing fake keep compiling); when a controller does not implement it, the
        // reference-import entries report a typed "unavailable" refusal below.
        _sourceImport = controller as ISourceImportController;
        _picker = picker;
        _notify = notify;
        _chapterId = chapterId;
        _chapterTitle = chapterTitle;
        _afterImport = afterImport;
        _requestCreateChapter = requestCreateChapter;
        _referencePollDelay = referencePollDelay ?? (() => Task.Delay(300));
        Rows = new ObservableCollection<ImportRowViewModel>();
        ReferencePlanItems = new ObservableCollection<ReferencePlanRowView>();
        ReferenceReceiptItems = new ObservableCollection<ReferenceReceiptRowView>();
        StartCommand = new RelayCommand(() => _ = StartAsync());
        RetryFailedCommand = new RelayCommand(RetryFailed);
        SkipFailedCommand = new RelayCommand(SkipFailed);
        CloseCommand = new RelayCommand(Close);
        RequestCreateChapterCommand = new RelayCommand(RequestCreateChapter);
        PickReferenceSourcesCommand = new RelayCommand(() => _ = PickReferenceSourcesAsync());
        ConfirmReferenceImportCommand = new RelayCommand(() => _ = ConfirmReferenceImportAsync());
        CancelReferenceImportCommand = new RelayCommand(() => _ = CancelReferenceImportAsync());
        ReplanReferenceImportCommand = new RelayCommand(() => _ = ReplanReferenceImportAsync());
    }

    public ObservableCollection<ImportRowViewModel> Rows { get; }

    // FEA-09-UI-1: referenced-import face.
    public ObservableCollection<ReferencePlanRowView> ReferencePlanItems { get; }

    public ObservableCollection<ReferenceReceiptRowView> ReferenceReceiptItems { get; }

    public RelayCommand StartCommand { get; }

    public RelayCommand RetryFailedCommand { get; }

    public RelayCommand SkipFailedCommand { get; }

    public RelayCommand CloseCommand { get; }

    public RelayCommand RequestCreateChapterCommand { get; }

    public RelayCommand PickReferenceSourcesCommand { get; }

    public RelayCommand ConfirmReferenceImportCommand { get; }

    public RelayCommand CancelReferenceImportCommand { get; }

    public RelayCommand ReplanReferenceImportCommand { get; }

    public bool IsOpen
    {
        get => _isOpen;
        private set
        {
            if (Set(ref _isOpen, value))
            {
                RaiseDerived();
            }
        }
    }

    public bool IsRunning
    {
        get => _isRunning;
        private set
        {
            if (Set(ref _isRunning, value))
            {
                RaiseDerived();
            }
        }
    }

    public string Summary
    {
        get => _summary;
        private set => Set(ref _summary, value);
    }

    public bool HasRows => Rows.Count > 0;

    public bool HasFailures => Rows.Any(row => row.State == ImportRowState.Failed);

    public bool HasPending => Rows.Any(row => row.State == ImportRowState.Pending);

    public bool HasTargetChapter => !string.IsNullOrEmpty(_chapterId());

    public bool ShowCreateChapterEntry => !HasTargetChapter;

    public string Title => HasTargetChapter
        ? $"导入到「{_chapterTitle()}」"
        : "导入：尚未选择章节";

    /// <summary>Honest degradation notice: chapter creation is a real Core write (V11R-A-1).</summary>
    public string CapabilityText =>
        "当前没有章节：请先在右侧就地「新建章节」（走 Core CreateChapter，V11R-A-1），创建成功后即可导入；" +
        "不会伪造章节或伪造导入成功。";

    public string TargetChapterText => HasTargetChapter
        ? $"目标章节：{_chapterTitle()}"
        : "先选择作品与章节，再导入文件。";

    public bool CanStart => IsOpen && !IsRunning && HasPending && HasTargetChapter;

    // ---------------------------------------------------------------------------------------
    // FEA-09-UI-1: referenced-source import (C-16 v1.1). Displayed text carries file names,
    // typed codes and counts only — never paths, never the password.
    // ---------------------------------------------------------------------------------------

    public bool IsReferenceRunning
    {
        get => _isReferenceRunning;
        private set
        {
            if (Set(ref _isReferenceRunning, value))
            {
                RaiseReferenceDerived();
            }
        }
    }

    /// <summary>
    /// The password lives ONLY in this property between input and the single start call; it is
    /// cleared the moment the call returns and never appears in any other field or text.
    /// </summary>
    public string ReferencePassword
    {
        get => _referencePassword;
        set
        {
            if (Set(ref _referencePassword, value))
            {
                RaiseReferenceDerived();
            }
        }
    }

    public string ReferencePlanSummary
    {
        get => _referencePlanSummary;
        private set => Set(ref _referencePlanSummary, value);
    }

    public string ReferenceProgressText
    {
        get => _referenceProgressText;
        private set => Set(ref _referenceProgressText, value);
    }

    public string ReferenceErrorText
    {
        get => _referenceErrorText;
        private set
        {
            if (Set(ref _referenceErrorText, value))
            {
                OnPropertyChanged(nameof(HasReferenceError));
            }
        }
    }

    public bool HasReferenceError => !string.IsNullOrEmpty(ReferenceErrorText);

    public bool HasReferencePlan => _activePlan is not null;

    public bool NeedsPassword => _activePlan?.NeedsPassword == true;

    public bool HasReferenceReceipt => ReferenceReceiptItems.Count > 0;

    public bool CanConfirmReference =>
        HasReferencePlan && !IsReferenceRunning && !IsRunning && HasTargetChapter &&
        (!NeedsPassword || !string.IsNullOrEmpty(ReferencePassword));

    public bool CanCancelReference => IsReferenceRunning && _activeOperationId is not null;

    /// <summary>Re-preview after a terminal state (retry = fresh plan → fresh operation; the Core's
    /// natural keys keep already-committed pages from being duplicated).</summary>
    public bool CanReplanReference => !IsReferenceRunning && _referenceSources is { Count: > 0 };

    public async Task PickReferenceSourcesAsync()
    {
        if (_picker is null)
        {
            _notify("文件选择器不可用（Host/窗口未就绪）", NmStatus.Blocked);
            return;
        }

        var paths = await _picker.PickFilesAsync().ConfigureAwait(true);
        if (paths.Count == 0)
        {
            return;
        }

        await PlanReferenceImportAsync(paths.Select(path => new ReferenceImportSource(path, IsFolder: false)).ToList())
            .ConfigureAwait(true);
    }

    /// <summary>Plan preview: registers the sources with the Host, renders the Core's plan (AC-1).</summary>
    public async Task PlanReferenceImportAsync(IReadOnlyList<ReferenceImportSource> sources)
    {
        if (IsReferenceRunning)
        {
            _notify("引用导入进行中：完成或取消后再开始新的预览", NmStatus.Running);
            return;
        }

        if (_sourceImport is null)
        {
            _notify("引用导入不可用：当前控制器未提供引用导入能力（SOURCE_IMPORT_UNSUPPORTED）", NmStatus.Blocked);
            return;
        }

        var chapterId = _chapterId();
        if (string.IsNullOrWhiteSpace(chapterId))
        {
            _notify("引用导入被拒绝：尚未选择章节（不会伪造章节或导入结果）", NmStatus.Blocked);
            return;
        }

        _referenceSources = sources;
        IsOpen = true;
        var plan = await _sourceImport.PlanReferencedImportAsync(chapterId, sources).ConfigureAwait(true);
        if (plan is null)
        {
            var code = _controller.Snapshot.LastError;
            ReferenceErrorText = $"预览失败：{SourceImportText.CodeText(code)}（{code}）";
            _notify("引用导入预览失败：" + SourceImportText.CodeText(code), NmStatus.Blocked);
            return;
        }

        ApplyPlan(plan);
    }

    /// <summary>Confirm: one start call (never re-submits a consumed plan), then receipt polling.</summary>
    public async Task ConfirmReferenceImportAsync()
    {
        if (!CanConfirmReference || _activePlan is not { } plan || _sourceImport is not { } sourceImport)
        {
            return;
        }

        var password = NeedsPassword ? ReferencePassword : null;
        if (NeedsPassword && string.IsNullOrEmpty(password))
        {
            ReferenceErrorText = "该计划包含加密源：请输入密码后再确认";
            return;
        }

        IsReferenceRunning = true;
        try
        {
            var result = await sourceImport.StartReferencedImportAsync(plan, password).ConfigureAwait(true);
            // The plaintext password's lifetime ends here — wiped from the view model state.
            ReferencePassword = string.Empty;
            if (!result.Ok)
            {
                ReferenceErrorText = result.ErrorCode is { Length: > 0 }
                    ? $"{result.Message}（{result.ErrorCode}）"
                    : result.Message;
                if (result.ErrorCode == "SOURCE_PLAN_STALE")
                {
                    // The plan is consumed/stale — force a fresh preview before any new confirm.
                    _activePlan = null;
                    RaiseReferenceDerived();
                }

                _notify("引用导入未提交：" + result.Message, NmStatus.Failed);
                return;
            }

            _activeOperationId = result.OperationId;
            _activePlan = null;
            RaiseReferenceDerived();
            await PollReferenceReceiptAsync(sourceImport).ConfigureAwait(true);
        }
        finally
        {
            IsReferenceRunning = false;
        }
    }

    /// <summary>Running cancel (C-16 cancel_import); the receipt converges through the poll loop.</summary>
    public async Task CancelReferenceImportAsync()
    {
        if (!CanCancelReference || _activeOperationId is not { } operationId || _sourceImport is not { } sourceImport)
        {
            return;
        }

        var result = await sourceImport.CancelReferencedImportAsync(operationId).ConfigureAwait(true);
        if (!result.Ok)
        {
            ReferenceErrorText = "取消失败：" + SourceImportText.CodeText(result.ErrorCode);
        }
        else if (!result.Accepted)
        {
            ReferenceProgressText = "取消请求被拒绝（导入可能已结束：" +
                SourceImportText.StateText(SourceImportJson.ParseState(result.State)) + "）";
        }
        else
        {
            ReferenceProgressText = "已请求取消，等待导入停止…";
        }
    }

    /// <summary>Retry entry: a FRESH plan (the old operation stays committed-side; the Core's
    /// natural keys deduplicate already-committed pages — C-16 §4).</summary>
    public async Task ReplanReferenceImportAsync()
    {
        if (!CanReplanReference || _referenceSources is not { } sources)
        {
            return;
        }

        ReferenceErrorText = string.Empty;
        await PlanReferenceImportAsync(sources).ConfigureAwait(true);
    }

    private async Task PollReferenceReceiptAsync(ISourceImportController sourceImport)
    {
        while (_activeOperationId is { } operationId)
        {
            await _referencePollDelay().ConfigureAwait(true);
            var receipt = await sourceImport.GetReferencedImportReceiptAsync(operationId).ConfigureAwait(true);
            if (receipt is null)
            {
                ReferenceErrorText = "无法读取导入进度（Host/核心不可用）";
                return;
            }

            ApplyReceipt(receipt);
            if (receipt.IsTerminal)
            {
                break;
            }
        }

        await _afterImport().ConfigureAwait(true);
    }

    private void ApplyPlan(SourcePlanPreview plan)
    {
        _activePlan = plan;
        ReferencePlanItems.Clear();
        foreach (var item in plan.Items)
        {
            ReferencePlanItems.Add(new ReferencePlanRowView(
                item.DisplayName,
                item.SourceKind,
                SourceImportText.PlanStatus(item.Status, item.ReasonCode),
                item.WillImport is { } count ? $"将导入 {count} 页" : "—",
                item.AlreadyReferenced ? "已引用" : string.Empty));
        }

        ReferencePlanSummary =
            $"计划：导入 {plan.Totals.Import} · 跳过 {plan.Totals.Skip} · 不支持 {plan.Totals.Unsupported} · 失败 {plan.Totals.Failed}";
        ReferenceErrorText = string.Empty;
        ReferenceProgressText = string.Empty;
        ReferenceReceiptItems.Clear();
        RaiseReferenceDerived();
    }

    private void ApplyReceipt(SourceImportReceipt receipt)
    {
        ReferenceReceiptItems.Clear();
        foreach (var item in receipt.Items)
        {
            ReferenceReceiptItems.Add(new ReferenceReceiptRowView(
                item.SourceName,
                SourceImportText.ReceiptOutcome(item.Outcome, item.ReasonCode),
                $"已提交 {item.CommittedPages} 页 · 待处理 {item.RemainingPages} 页"));
        }

        var totals = receipt.Totals;
        ReferenceProgressText =
            $"{SourceImportText.StateText(receipt.State)} · 已导入 {totals.ImportedPages} · 跳过 {totals.SkippedPages}" +
            $" · 不支持 {totals.UnsupportedEntries} · 失败源 {totals.FailedSources} · 待处理 {totals.PendingPages}" +
            (receipt.CancelRequested ? " · 取消已请求" : string.Empty);
        OnPropertyChanged(nameof(HasReferenceReceipt));
    }

    private void RaiseReferenceDerived() => OnPropertyChanged(
        nameof(HasReferencePlan),
        nameof(NeedsPassword),
        nameof(CanConfirmReference),
        nameof(CanCancelReference),
        nameof(CanReplanReference),
        nameof(HasReferenceReceipt));

    public async Task OpenWithFilesAsync(IReadOnlyList<string> paths)
    {
        if (paths.Count == 0)
        {
            return;
        }

        IsOpen = true;
        foreach (var path in paths)
        {
            Rows.Add(new ImportRowViewModel(path, isFolder: false));
        }

        UpdateSummary();
        if (HasTargetChapter)
        {
            await StartAsync().ConfigureAwait(true);
        }
        else
        {
            _notify("导入已就绪：请先选择或就地新建章节（「新建章节」走 Core CreateChapter）", NmStatus.Blocked);
        }
    }

    public async Task OpenWithFolderAsync(string folderPath)
    {
        if (string.IsNullOrWhiteSpace(folderPath))
        {
            return;
        }

        IsOpen = true;
        Rows.Add(new ImportRowViewModel(folderPath, isFolder: true));
        UpdateSummary();
        if (HasTargetChapter)
        {
            await StartAsync().ConfigureAwait(true);
        }
        else
        {
            _notify("导入已就绪：请先选择或就地新建章节（「新建章节」走 Core CreateChapter）", NmStatus.Blocked);
        }
    }

    /// <summary>Opens the picker and imports the chosen files; used by the Library import buttons.</summary>
    public async Task PickFilesAsync()
    {
        if (_picker is null)
        {
            _notify("文件选择器不可用（Host/窗口未就绪）", NmStatus.Blocked);
            return;
        }

        var paths = await _picker.PickFilesAsync().ConfigureAwait(true);
        if (paths.Count == 0)
        {
            return;
        }

        await OpenWithFilesAsync(paths).ConfigureAwait(true);
    }

    public async Task PickFolderAsync()
    {
        if (_picker is null)
        {
            _notify("文件夹选择器不可用（Host/窗口未就绪）", NmStatus.Blocked);
            return;
        }

        var folder = await _picker.PickFolderAsync().ConfigureAwait(true);
        if (string.IsNullOrWhiteSpace(folder))
        {
            return;
        }

        await OpenWithFolderAsync(folder).ConfigureAwait(true);
    }

    public async Task StartAsync()
    {
        if (!IsOpen)
        {
            return;
        }

        if (!HasTargetChapter)
        {
            _notify("导入被拒绝：尚未选择章节（不会伪造章节或导入结果）", NmStatus.Blocked);
            return;
        }

        if (IsRunning)
        {
            return;
        }

        var chapterId = _chapterId();
        if (string.IsNullOrWhiteSpace(chapterId))
        {
            return;
        }

        IsRunning = true;
        try
        {
            foreach (var row in Rows.Where(item => item.State == ImportRowState.Pending).ToList())
            {
                row.State = ImportRowState.Importing;
                row.Message = "导入中…";
                await ImportOneAsync(chapterId, row).ConfigureAwait(true);
            }
        }
        finally
        {
            IsRunning = false;
            UpdateSummary();
        }

        await _afterImport().ConfigureAwait(true);

        if (HasFailures)
        {
            _notify($"导入部分失败：{Rows.Count(row => row.State == ImportRowState.Failed)} 个文件失败，可重试或跳过", NmStatus.Failed);
        }
        else if (Rows.Any(row => row.State == ImportRowState.Imported))
        {
            _notify(Summary, NmStatus.Done);
        }
    }

    public void RetryFailed()
    {
        if (IsRunning)
        {
            return;
        }

        var failed = Rows.Where(row => row.State == ImportRowState.Failed).ToList();
        if (failed.Count == 0)
        {
            return;
        }

        foreach (var row in failed)
        {
            row.ResetForRetry();
        }

        UpdateSummary();
        _ = StartAsync();
    }

    public void SkipFailed()
    {
        if (IsRunning)
        {
            return;
        }

        foreach (var row in Rows.Where(item => item.State == ImportRowState.Failed))
        {
            row.State = ImportRowState.SkippedByUser;
            row.Message = "已跳过（用户选择）";
        }

        UpdateSummary();
    }

    public void Close()
    {
        if (IsRunning || IsReferenceRunning)
        {
            _notify("导入进行中：完成或取消后再关闭导入面板", NmStatus.Running);
            return;
        }

        IsOpen = false;
        Rows.Clear();
        Summary = string.Empty;
        // FEA-09-UI-1: drop the referenced-import face with the panel (never mid-operation).
        _activePlan = null;
        _activeOperationId = null;
        _referencePassword = string.Empty;
        ReferencePlanItems.Clear();
        ReferenceReceiptItems.Clear();
        ReferencePlanSummary = string.Empty;
        ReferenceProgressText = string.Empty;
        ReferenceErrorText = string.Empty;
        RaiseDerived();
        RaiseReferenceDerived();
    }

    public void RequestCreateChapter()
    {
        _requestCreateChapter();
        NotifyChapterContextChanged();
    }

    /// <summary>Raised when the Library selection changes so the dock header follows the target.</summary>
    public void NotifyChapterContextChanged()
    {
        OnPropertyChanged(nameof(HasTargetChapter), nameof(ShowCreateChapterEntry), nameof(Title), nameof(TargetChapterText), nameof(CanStart));
    }

    private async Task ImportOneAsync(string chapterId, ImportRowViewModel row)
    {
        try
        {
            var outcome = row.IsFolder
                ? await _controller.ImportFolderAsync(chapterId, row.Path).ConfigureAwait(true)
                : await _controller.ImportFilesAsync(chapterId, new[] { row.Path }).ConfigureAwait(true);

            if (!outcome.Ok)
            {
                row.State = ImportRowState.Failed;
                row.Message = outcome.ErrorCode is { Length: > 0 }
                    ? $"{outcome.Message}（{outcome.ErrorCode}）"
                    : outcome.Message;
                return;
            }

            if (row.IsFolder)
            {
                row.State = outcome.ImportedFiles > 0 ? ImportRowState.Imported : ImportRowState.Skipped;
                row.Message = outcome.Message;
                return;
            }

            if (outcome.ImportedFiles > 0)
            {
                row.State = ImportRowState.Imported;
                row.Message = "已导入";
            }
            else if (outcome.SkippedFiles > 0)
            {
                row.State = ImportRowState.Skipped;
                row.Message = "跳过（重复）";
            }
            else
            {
                row.State = ImportRowState.Skipped;
                row.Message = "没有新内容";
            }
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            row.State = ImportRowState.Failed;
            row.Message = "导入异常：" + ex.Message;
        }
    }

    private void UpdateSummary()
    {
        if (Rows.Count == 0)
        {
            Summary = string.Empty;
        }
        else
        {
            var imported = Rows.Count(row => row.State == ImportRowState.Imported);
            var skipped = Rows.Count(row => row.State is ImportRowState.Skipped or ImportRowState.SkippedByUser);
            var failed = Rows.Count(row => row.State == ImportRowState.Failed);
            var pending = Rows.Count(row => row.State is ImportRowState.Pending or ImportRowState.Importing);
            Summary = $"已导入 {imported} · 跳过 {skipped} · 失败 {failed} · 待处理 {pending}";
        }

        RaiseDerived();
    }

    private void RaiseDerived() => OnPropertyChanged(
        nameof(HasRows),
        nameof(HasFailures),
        nameof(HasPending),
        nameof(CanStart),
        nameof(ShowCreateChapterEntry),
        nameof(HasTargetChapter),
        nameof(Title),
        nameof(TargetChapterText));
}

/// <summary>
/// FEA-09-UI-1: one plan-preview row. Pre-formatted text (file name + typed status + counts);
/// the source path and any secret material are deliberately not carried.
/// </summary>
public sealed record ReferencePlanRowView(
    string DisplayName,
    string KindText,
    string StatusText,
    string WillImportText,
    string AlreadyReferencedText);

/// <summary>FEA-09-UI-1: one receipt row (file name + typed outcome + committed/remaining counts).</summary>
public sealed record ReferenceReceiptRowView(
    string SourceName,
    string OutcomeText,
    string CountsText);
