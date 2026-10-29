namespace NewManga.App.ViewModels.V2.Studio;

/// <summary>Page surface presentation: 页面 / 成品 / 分屏 (SCREEN_SPECS §3, SegmentedControl).</summary>
public enum StudioSurfaceMode
{
    Page,
    Final,
    Split,
}

/// <summary>Studio working mode (contract §6.1 <c>StudioMode</c>).</summary>
public enum StudioWorkspaceMode
{
    Page,
    Batch,
}

/// <summary>Inspector tabs (SCREEN_SPECS §3: 文本/样式/修复/锁定/历史).</summary>
public enum StudioInspectorTab
{
    Text,
    Style,
    Repair,
    Locks,
    History,
}

/// <summary>
/// V11R-B-3 AC2: the one selection model shared by both Studio modes. The V2 shell will own the
/// authoritative copy in <c>ShellState</c>; until that merges, this object is the Studio-side single
/// source and the shell adapter only forwards it. No view model keeps a second copy of any of it.
/// </summary>
public sealed class StudioSelection : StudioObservable
{
    private string? _bookId;
    private string? _chapterId;
    private string? _currentPageId;
    private string? _currentRegionId;
    private StudioSurfaceMode _surfaceMode = StudioSurfaceMode.Page;
    private StudioInspectorTab _inspectorTab = StudioInspectorTab.Text;
    private bool _filmStripExpanded;
    private bool _inspectorExpanded;
    private double _zoom = StudioCoordinates.DefaultZoom;
    private double _offsetX;
    private double _offsetY;
    private readonly List<string> _selectedPageIds = new();

    /// <summary>Raised for every change so the shell can write it back to <c>ShellState</c>.</summary>
    public event EventHandler? Changed;

    public string? BookId
    {
        get => _bookId;
        set => SetField(ref _bookId, value);
    }

    public string? ChapterId
    {
        get => _chapterId;
        set => SetField(ref _chapterId, value);
    }

    public string? CurrentPageId
    {
        get => _currentPageId;
        set => SetField(ref _currentPageId, value);
    }

    public string? CurrentRegionId
    {
        get => _currentRegionId;
        set => SetField(ref _currentRegionId, value);
    }

    /// <summary>Batch-mode multi-page scope (Shift/box selection). Ordered as selected.</summary>
    public IReadOnlyList<string> SelectedPageIds => _selectedPageIds;

    public StudioSurfaceMode SurfaceMode
    {
        get => _surfaceMode;
        set => SetField(ref _surfaceMode, value);
    }

    public StudioInspectorTab InspectorTab
    {
        get => _inspectorTab;
        set => SetField(ref _inspectorTab, value);
    }

    public bool FilmStripExpanded
    {
        get => _filmStripExpanded;
        set => SetField(ref _filmStripExpanded, value);
    }

    public bool InspectorExpanded
    {
        get => _inspectorExpanded;
        set => SetField(ref _inspectorExpanded, value);
    }

    /// <summary>Persisted zoom/pan so a mode switch restores the exact canvas state (AC2).</summary>
    public double Zoom
    {
        get => _zoom;
        set => SetField(ref _zoom, StudioCoordinates.ClampZoom(value));
    }

    public double OffsetX
    {
        get => _offsetX;
        set => SetField(ref _offsetX, value);
    }

    public double OffsetY
    {
        get => _offsetY;
        set => SetField(ref _offsetY, value);
    }

    /// <summary>Replaces the multi-page selection (Batch box/Shift selection).</summary>
    public void SetSelectedPages(IEnumerable<string> pageIds)
    {
        _selectedPageIds.Clear();
        foreach (var pageId in pageIds)
        {
            if (!string.IsNullOrEmpty(pageId) && !_selectedPageIds.Contains(pageId, StringComparer.Ordinal))
            {
                _selectedPageIds.Add(pageId);
            }
        }

        Raise(nameof(SelectedPageIds));
        Raise(nameof(SelectionSummary));
        Changed?.Invoke(this, EventArgs.Empty);
    }

    /// <summary>Adds/removes one page from the multi-page scope (Ctrl-click semantics).</summary>
    public void TogglePage(string pageId)
    {
        if (string.IsNullOrEmpty(pageId))
        {
            return;
        }

        if (!_selectedPageIds.Remove(pageId))
        {
            _selectedPageIds.Add(pageId);
        }

        Raise(nameof(SelectedPageIds));
        Raise(nameof(SelectionSummary));
        Changed?.Invoke(this, EventArgs.Empty);
    }

    /// <summary>Scope text every batch action must carry as a suffix (FUSION §2.3: 作用域后缀).</summary>
    public string SelectionSummary
    {
        get
        {
            if (!string.IsNullOrEmpty(CurrentRegionId) && !string.IsNullOrEmpty(CurrentPageId))
            {
                return "当前 Region";
            }

            if (_selectedPageIds.Count > 0)
            {
                return $"选中 {_selectedPageIds.Count} 页";
            }

            return string.IsNullOrEmpty(CurrentPageId) ? "本章" : "当前页";
        }
    }

    private void SetField<T>(ref T field, T value, [System.Runtime.CompilerServices.CallerMemberName] string? name = null)
    {
        if (Set(ref field, value, name))
        {
            Changed?.Invoke(this, EventArgs.Empty);
        }
    }
}
