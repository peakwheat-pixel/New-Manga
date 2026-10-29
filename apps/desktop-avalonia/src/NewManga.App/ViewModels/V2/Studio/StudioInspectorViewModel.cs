using System.Collections.ObjectModel;
using NewManga.CoreClient;

namespace NewManga.App.ViewModels.V2.Studio;

/// <summary>One of the four text tiers of DESIGN_SYSTEM §6.5 <c>TextTierPanel</c>.</summary>
public sealed record StudioTextTierSpec(string Key, string Label, string SourceHint);

/// <summary>The frozen four-tier vocabulary of the region text read face.</summary>
public static class StudioTextTierSpecs
{
    public const string OcrText = "ocr_text";
    public const string MachineTranslation = "machine_translation";
    public const string EditedTranslation = "edited_translation";
    public const string FinalTranslation = "final_translation";

    public static IReadOnlyList<StudioTextTierSpec> All { get; } = new[]
    {
        new StudioTextTierSpec(OcrText, "OCR 原文", "机器 · 识别阶段"),
        new StudioTextTierSpec(MachineTranslation, "机器翻译", "机器 · 翻译阶段"),
        new StudioTextTierSpec(EditedTranslation, "人工译文", "人工编辑 · 可保存"),
        new StudioTextTierSpec(FinalTranslation, "终稿", "人工确认 · 导出使用"),
    };
}

/// <summary>One text tier row. <see cref="IsWired"/> is false while the read face is missing.</summary>
public sealed class StudioTextTierViewModel : StudioObservable
{
    public StudioTextTierViewModel(StudioTextTierSpec spec)
    {
        Spec = spec;
    }

    public StudioTextTierSpec Spec { get; }

    public string Key => Spec.Key;

    public string Label => Spec.Label;

    public string SourceHint => Spec.SourceHint;

    public string? Value { get; private set; }

    /// <summary>Displayed value: the real text, or "—" when there is no text at all.</summary>
    public string ValueDisplay => string.IsNullOrEmpty(Value) ? "—" : Value;

    public bool IsWired { get; private set; }

    public bool IsLocked { get; private set; }

    public string LockBadge => IsLocked ? "▮" : string.Empty;

    /// <summary>Shown in place of the value while the tier read is NOT_WIRED.</summary>
    public string NotWiredNote => "能力待接入";

    public bool IsNotWired => !IsWired;

    /// <summary>True when this tier is the editable one (人工译文).</summary>
    public bool IsEditableTier => Key == StudioTextTierSpecs.EditedTranslation;

    internal void Apply(RegionTextTiers? tiers, RegionFlags? flags, bool wired)
    {
        IsWired = wired && tiers is not null;
        Value = tiers is null
            ? null
            : Key switch
            {
                StudioTextTierSpecs.OcrText => tiers.OcrText,
                StudioTextTierSpecs.MachineTranslation => tiers.MachineTranslation,
                StudioTextTierSpecs.EditedTranslation => tiers.EditedTranslation,
                StudioTextTierSpecs.FinalTranslation => tiers.FinalTranslation,
                _ => null,
            };
        IsLocked = IsEditableTier ? flags?.TranslationLocked ?? false : false;
        Raise(string.Empty);
    }
}

/// <summary>One of the four locks of DESIGN_SYSTEM §6.5 <c>LockControls</c>.</summary>
public sealed class StudioLockItemViewModel : StudioObservable
{
    public StudioLockItemViewModel(string key, string label, string explanation)
    {
        Key = key;
        Label = label;
        Explanation = explanation;
    }

    public string Key { get; }

    public string Label { get; }

    /// <summary>Plain-language consequence shown under the toggle (§6.5: 解释文案).</summary>
    public string Explanation { get; }

    public bool IsLocked { get; private set; }

    public bool IsWired { get; private set; }

    public bool IsNotWired => !IsWired;

    public string Glyph => IsLocked ? "▮" : "○";

    /// <summary>Toggle is disabled while the lock write command is missing (F0-1).</summary>
    public bool CanToggle => IsWired;

    internal void Apply(RegionFlags? flags, bool wired)
    {
        IsWired = wired && flags is not null;
        IsLocked = flags is null
            ? false
            : Key switch
            {
                "page" => flags.PageLocked,
                "region" => flags.RegionLocked,
                "translation" => flags.TranslationLocked,
                "inpaint" => flags.InpaintLocked,
                _ => false,
            };
        Raise(string.Empty);
    }
}

/// <summary>One revision row of the 历史 tab (<c>list_region_revisions</c>).</summary>
public sealed class StudioRevisionItemViewModel : StudioObservable
{
    private bool _isSelected;

    public StudioRevisionItemViewModel(RegionRevisionSummary revision)
    {
        Revision = revision;
    }

    public RegionRevisionSummary Revision { get; }

    public int RevisionNo => Revision.RevisionNo;

    public string RevisionLabel => $"r{RevisionNo}";

    public string Origin => Revision.Origin;

    public string OriginLabel => string.Equals(Revision.Origin, "user", StringComparison.OrdinalIgnoreCase) ? "人工" : "机器";

    public string ReviewState => Revision.ReviewState;

    /// <summary>Review state mapped onto the shared seven-state vocabulary.</summary>
    public StudioStateKind? State => StudioStates.FromReviewState(ReviewState);

    public string StateGlyph => State is { } state ? StudioStates.Glyph(state) : "○";

    public string StateLabel => State is { } state ? StudioStates.Label(state) : "未开始";

    public string StateClass => State is { } value ? StudioStates.StyleClass(value) : "studio-state-notstarted";

    public bool IsCurrent => Revision.IsCurrent;

    public bool IsPinned => Revision.IsPinned;

    public string PinBadge => IsPinned ? "▮" : string.Empty;

    public string RegionType => Revision.RegionType;

    public string SfxPolicy => Revision.SfxPolicy;

    public string? CreatedAt => Revision.CreatedAt;

    public string? RestoredFromRevisionId => Revision.RestoredFromRevisionId;

    public string Detail => $"类型 {RegionType} · sfx {SfxPolicy} · {OriginLabel} · {StateLabel}";

    public string PreviewTitle => $"r{RevisionNo} {OriginLabel} · {StateLabel}";

    public bool IsSelected
    {
        get => _isSelected;
        set => Set(ref _isSelected, value);
    }

    public override string ToString() =>
        $"r{RevisionNo} {OriginLabel} {StateLabel}{(IsCurrent ? " 当前" : string.Empty)}";
}

/// <summary>
/// V11R-B-3 AC1/AC4: the right-hand inspector, five tabs (文本/样式/修复/锁定/历史). Every operation
/// that depends on the unmerged F0-1 write face is visible but disabled with the contract's
/// "能力待接入" tooltip; nothing fakes a successful save.
/// </summary>
public sealed class StudioInspectorViewModel : StudioObservable
{
    private readonly StudioPageViewModel _page;
    private StudioRevisionItemViewModel? _selectedRevision;
    private bool _isHistoryLoading;
    private string? _historyError;
    private string? _historyEmptyNote;
    private string? _pendingRegionType;
    private string? _actionStatus;

    public StudioInspectorViewModel(StudioPageViewModel page)
    {
        _page = page;
        Locks = new ObservableCollection<StudioLockItemViewModel>
        {
            new("page", "页面锁", "锁定后整页不参与自动流程，人工仍可编辑"),
            new("region", "Region 锁", "锁定后该 Region 不参与重检测、重分割"),
            new("translation", "译文锁", "锁定后机器翻译不会覆盖人工译文"),
            new("inpaint", "修复锁", "锁定后重修复不会覆盖当前修复结果"),
        };
        TextTiers = new ObservableCollection<StudioTextTierViewModel>(
            StudioTextTierSpecs.All.Select(spec => new StudioTextTierViewModel(spec)));
        Revisions = new ObservableCollection<StudioRevisionItemViewModel>();
        RegionTypeOptions = new[] { "speech", "narration", "sfx", "note", "other" };
        Refresh(null);
    }

    /// <summary>Raised when the pending (unsaved) region type changes, so the page can track dirty state.</summary>
    public event EventHandler? PendingEditChanged;

    public StudioSelection Selection => _page.Selection;

    public StudioCapabilityGate Gate => _page.Gate;

    public StudioInspectorTab ActiveTab
    {
        get => _page.Selection.InspectorTab;
        set
        {
            if (value == _page.Selection.InspectorTab)
            {
                return;
            }

            _page.Selection.InspectorTab = value;
            Raise();
            Raise(nameof(ActiveTabIndex));
            Raise(nameof(ActiveTabLabel));
        }
    }

    public int ActiveTabIndex => (int)ActiveTab;

    public string ActiveTabLabel => ActiveTab switch
    {
        StudioInspectorTab.Text => "文本",
        StudioInspectorTab.Style => "样式",
        StudioInspectorTab.Repair => "修复",
        StudioInspectorTab.Locks => "锁定",
        StudioInspectorTab.History => "历史",
        _ => "文本",
    };

    /// <summary>Five tabs in design order with their collapsed-rail glyph.</summary>
    public IReadOnlyList<(StudioInspectorTab Tab, string Glyph, string Label)> Tabs { get; } = new[]
    {
        (StudioInspectorTab.Text, "文", "文本"),
        (StudioInspectorTab.Style, "样", "样式"),
        (StudioInspectorTab.Repair, "修", "修复"),
        (StudioInspectorTab.Locks, "锁", "锁定"),
        (StudioInspectorTab.History, "史", "历史"),
    };

    // ---------------------------------------------------------------- 文本 tab

    public ObservableCollection<StudioTextTierViewModel> TextTiers { get; }

    public bool TextReadWired => _page.TextSource.IsWired;

    /// <summary>Explicit degradation line above the tiers (contract: 未接入必须显示标记).</summary>
    public string TextTiersNote => TextReadWired
        ? "四级文本来自 Core 读取命令"
        : "四级文本读取命令未接入（V11R-F0-1）· 仅显示结构与来源";

    public bool SaveTranslationEnabled => Gate.CanExecute(StudioCommand.SaveEditedTranslation);

    public string SaveTranslationTooltip => Gate.Tooltip(StudioCommand.SaveEditedTranslation);

    public string SaveTranslationLabel => SaveTranslationEnabled ? "保存译文" : "保存译文 · 能力待接入";

    // ---------------------------------------------------------------- 样式 tab

    public IReadOnlyList<string> RegionTypeOptions { get; }

    public string? PendingRegionType => _pendingRegionType;

    /// <summary>Selection index used by the 样式 tab ComboBox (VM-driven, no code-behind state).</summary>
    public int PendingRegionTypeIndex =>
        _pendingRegionType is null ? -1 : RegionTypeOptions.ToList().IndexOf(_pendingRegionType);

    /// <summary>Sets the pending type; the commit is a separate step so "未保存更改" is real.</summary>
    public void SetPendingRegionType(string? regionType)
    {
        var normalized = string.IsNullOrWhiteSpace(regionType) ? null : regionType;
        if (_pendingRegionType == normalized)
        {
            return;
        }

        _pendingRegionType = normalized;
        Raise(nameof(PendingRegionType));
        Raise(nameof(PendingRegionTypeIndex));
        Raise(nameof(HasPendingTypeEdit));
        Raise(nameof(ApplyRegionTypeEnabled));
        Raise(nameof(ApplyRegionTypeTooltip));
        Raise(nameof(PendingEditSummary));
        PendingEditChanged?.Invoke(this, EventArgs.Empty);
    }

    public bool HasPendingTypeEdit =>
        _pendingRegionType is not null &&
        _page.SelectedRegion is { } region &&
        !string.Equals(_pendingRegionType, region.RegionType, StringComparison.Ordinal);

    public bool ApplyRegionTypeEnabled => HasPendingTypeEdit && Gate.CanExecute(StudioCommand.SetRegionType);

    public string ApplyRegionTypeTooltip => ApplyRegionTypeEnabled
        ? string.Empty
        : !StudioCapabilityGate.IsWired(StudioCommand.SetRegionType)
            ? StudioCapabilityGate.NotWiredTooltip
            : Gate.Tooltip(StudioCommand.SetRegionType);

    public string PendingEditSummary => HasPendingTypeEdit
        ? $"未保存：类型 {_page.SelectedRegion?.RegionType} → {_pendingRegionType}"
        : "无未保存修改";

    public int RegionTypeIndex => _page.SelectedRegion is { } region
        ? RegionTypeOptions.ToList().IndexOf(region.RegionType)
        : -1;

    public string SfxPolicyText => _page.SelectedRegion?.SfxPolicy ?? "—";

    public string OriginText => _page.SelectedRegion?.OriginLabel ?? "—";

    public string RevisionText => _page.SelectedRegion is { } region ? $"r{region.RevisionNo}" : "—";

    public string FontFamilyNote => "字体 / 字号 / 对齐：能力待接入（F0-1 排版写面）";

    public string GeometryText => _page.SelectedRegion is { } region && region.HasGeometry
        ? $"x {region.Normalized.X:0.###} · y {region.Normalized.Y:0.###} · w {region.Normalized.Width:0.###} · h {region.Normalized.Height:0.###}"
        : "—";

    // ---------------------------------------------------------------- 修复 tab

    public bool RerenderEnabled => Gate.CanExecute(StudioCommand.RerenderPage);

    public string RerenderTooltip => RerenderEnabled
        ? "重渲染当前页（rerender_page）"
        : Gate.Tooltip(StudioCommand.RerenderPage);

    public string RerenderLabel => RerenderEnabled ? "重渲染本页" : "重渲染本页 · 不可用";

    public string RepairNote =>
        "重修复 / 换 Mask / 换路线：能力待接入（F0-1）；重渲染为已接入命令";

    public string LastRerenderText => _page.LastRerenderSummary ?? "尚未执行重渲染";

    // ---------------------------------------------------------------- 锁定 tab

    public ObservableCollection<StudioLockItemViewModel> Locks { get; }

    public string LocksNote => _page.FlagSource.IsWired
        ? "锁状态来自 Core 读取命令"
        : "四把锁写命令与读取命令均未接入（V11R-F0-1）";

    public bool LockToggleEnabled => Gate.CanExecute(StudioCommand.LockRegion);

    public string LockToggleTooltip => Gate.Tooltip(StudioCommand.LockRegion);

    // ---------------------------------------------------------------- 历史 tab

    public ObservableCollection<StudioRevisionItemViewModel> Revisions { get; }

    public StudioRevisionItemViewModel? SelectedRevision
    {
        get => _selectedRevision;
        set
        {
            if (ReferenceEquals(_selectedRevision, value))
            {
                return;
            }

            _selectedRevision = value;
            Raise();
            Raise(nameof(PreviewTitle));
            Raise(nameof(PreviewDetail));
            Raise(nameof(RestoreEnabled));
            Raise(nameof(RestoreTooltip));
        }
    }

    public bool IsHistoryLoading
    {
        get => _isHistoryLoading;
        private set => Set(ref _isHistoryLoading, value);
    }

    public string? HistoryError
    {
        get => _historyError;
        private set
        {
            if (Set(ref _historyError, value))
            {
                Raise(nameof(HasHistoryError));
            }
        }
    }

    public bool HasHistoryError => !string.IsNullOrEmpty(_historyError);

    public string? HistoryEmptyNote
    {
        get => _historyEmptyNote;
        private set
        {
            if (Set(ref _historyEmptyNote, value))
            {
                Raise(nameof(IsHistoryEmpty));
            }
        }
    }

    public bool IsHistoryEmpty => !IsHistoryLoading && Revisions.Count == 0 && string.IsNullOrEmpty(_historyError);

    public string PreviewTitle => SelectedRevision?.PreviewTitle ?? "选择一条 revision 预览";

    /// <summary>
    /// Preview is metadata only: the frozen read face does not return text/geometry snapshots, so the
    /// UI must not pretend to preview content it never received.
    /// </summary>
    public string PreviewDetail => SelectedRevision is { } revision
        ? $"{revision.Detail} · 预览为元数据（内容快照读取未接入）"
        : "—";

    public bool RestoreEnabled =>
        SelectedRevision is { IsCurrent: false } && Gate.CanExecute(StudioCommand.RestoreRevision);

    public string RestoreTooltip => !Gate.CanExecute(StudioCommand.RestoreRevision)
        ? Gate.Tooltip(StudioCommand.RestoreRevision)
        : SelectedRevision is { IsCurrent: true }
            ? "该 revision 已是当前版本"
            : SelectedRevision is null
                ? "先选择一条 revision"
                : $"恢复 r{SelectedRevision.RevisionNo}（生成新 revision，不覆盖历史）";

    public string RestoreLabel => RestoreEnabled ? "恢复此版本" : "恢复此版本 · 不可用";

    /// <summary>Transient result line for the last inspector action.</summary>
    public string? ActionStatus
    {
        get => _actionStatus;
        private set => Set(ref _actionStatus, value);
    }

    // ---------------------------------------------------------------- behaviour

    /// <summary>Called by the page after a selection/region/revision refresh.</summary>
    public void Refresh(RegionTextTiers? tiers, RegionFlags? flags = null, IReadOnlyList<RegionRevisionSummary>? revisions = null)
    {
        var textWired = _page.TextSource.IsWired && tiers is not null;
        foreach (var tier in TextTiers)
        {
            tier.Apply(tiers, flags, textWired);
        }

        foreach (var item in Locks)
        {
            item.Apply(flags, _page.FlagSource.IsWired);
        }

        if (revisions is not null)
        {
            var previous = SelectedRevision?.RevisionNo;
            Revisions.Clear();
            foreach (var revision in revisions.OrderByDescending(item => item.RevisionNo))
            {
                Revisions.Add(new StudioRevisionItemViewModel(revision));
            }

            HistoryError = null;
            HistoryEmptyNote = Revisions.Count == 0 ? "该 Region 还没有 revision" : null;
            SelectedRevision = previous is { } revisionNo
                ? Revisions.FirstOrDefault(item => item.RevisionNo == revisionNo) ?? Revisions.FirstOrDefault()
                : Revisions.FirstOrDefault();
        }

        Raise(string.Empty);
    }

    public void BeginHistoryLoad()
    {
        IsHistoryLoading = true;
        HistoryError = null;
        HistoryEmptyNote = null;
    }

    public void EndHistoryLoad(string? error)
    {
        IsHistoryLoading = false;
        HistoryError = error;
        HistoryEmptyNote = Revisions.Count == 0 && string.IsNullOrEmpty(error) ? "该 Region 还没有 revision" : null;
        Raise(nameof(IsHistoryEmpty));
    }

    public void ReportAction(string? status) => ActionStatus = status;

    /// <summary>Clears the pending type edit (放弃 path of the leave modal).</summary>
    public void DiscardPendingType()
    {
        _pendingRegionType = null;
        Raise(nameof(PendingRegionType));
        Raise(nameof(PendingRegionTypeIndex));
        Raise(nameof(HasPendingTypeEdit));
        Raise(nameof(ApplyRegionTypeEnabled));
        Raise(nameof(ApplyRegionTypeTooltip));
        Raise(nameof(PendingEditSummary));
        PendingEditChanged?.Invoke(this, EventArgs.Empty);
    }

    /// <summary>Clears the pending edit after a successful save.</summary>
    public void ClearPendingAfterSave() => DiscardPendingType();

    /// <summary>Revisions were replaced by a write refresh (keeps the selected revision when possible).</summary>
    public void SetRevisions(IReadOnlyList<RegionRevisionSummary> revisions) => Refresh(null, null, revisions);
}
