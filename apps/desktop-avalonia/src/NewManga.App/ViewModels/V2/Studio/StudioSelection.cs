using NewManga.App.Shell.V2;

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
/// R-16 裁决：作用域的唯一解析结果。显式多选（Batch 框选/Shift）**优先于** Region 与当前页。
/// </summary>
public enum StudioScopeKind
{
    Chapter,
    SelectedPages,
    Page,
    Region,
}

/// <summary>
/// R-16 裁决：<c>ShellState.Selection</c> 是唯一权威；本类型只是它的**投影 + 变更路由**。
/// 所有 book/chapter/page/region/多选 的读写都落到 <see cref="ShellState"/>，本类不保留第二份副本。
/// UI-only 状态（版面模式、检查器页签、缩放/平移）不属于 selection，仍保存在本对象上。
/// </summary>
public sealed class StudioSelection : StudioObservable
{
    private readonly ShellState _shell;
    private StudioSurfaceMode _surfaceMode = StudioSurfaceMode.Page;
    private StudioInspectorTab _inspectorTab = StudioInspectorTab.Text;
    private bool _filmStripExpanded;
    private bool _inspectorExpanded = true;
    private double _zoom = StudioCoordinates.DefaultZoom;
    private double _offsetX;
    private double _offsetY;

    public StudioSelection(ShellState? shell = null)
    {
        _shell = shell ?? new ShellState();
        _shell.SelectionChanged += OnShellSelectionChanged;
    }

    /// <summary>The single authority this projection reads and routes writes through.</summary>
    public ShellState Shell => _shell;

    public ShellSelection ShellSelection => _shell.Selection;

    /// <summary>Raised for every selection change (projection refresh + canvas invalidation).</summary>
    public event EventHandler? Changed;

    /// <summary>Atomic context write: book+chapter in one ShellState transition (no intermediate wipe).</summary>
    public void SetContext(string? bookId, string? chapterId) =>
        _shell.SetSelection(new ShellSelection
        {
            BookId = bookId,
            ChapterId = chapterId,
            PageId = null,
            RegionId = null,
        });

    public string? BookId
    {
        get => _shell.Selection.BookId;
        set
        {
            if (!string.Equals(BookId, value, StringComparison.Ordinal))
            {
                _shell.SelectBook(value);
            }
        }
    }

    public string? ChapterId
    {
        get => _shell.Selection.ChapterId;
        set
        {
            if (!string.Equals(ChapterId, value, StringComparison.Ordinal))
            {
                _shell.SelectChapter(value);
            }
        }
    }

    public string? CurrentPageId
    {
        get => _shell.Selection.PageId;
        set
        {
            if (!string.Equals(CurrentPageId, value, StringComparison.Ordinal))
            {
                _shell.SelectPage(value);
            }
        }
    }

    public string? CurrentRegionId
    {
        get => _shell.Selection.RegionId;
        set
        {
            if (!string.Equals(CurrentRegionId, value, StringComparison.Ordinal))
            {
                _shell.SelectRegion(value);
            }
        }
    }

    /// <summary>Batch-mode multi-page scope (ShellState.MultiPage); order is the user's click order.</summary>
    public IReadOnlyList<string> SelectedPageIds => _shell.Selection.MultiPage;

    public int SelectedPageCount => _shell.Selection.MultiPageCount;

    /// <summary>
    /// R-16: explicit multi-selection wins over Region/Page (FUSION hard rule 1). A Batch box
    /// selection of 3 pages keeps that scope after switching to Page mode.
    /// </summary>
    public StudioScopeKind ResolvedScope
    {
        get
        {
            if (_shell.Selection.MultiPageCount > 0)
            {
                return StudioScopeKind.SelectedPages;
            }

            if (_shell.Selection.HasRegion)
            {
                return StudioScopeKind.Region;
            }

            return _shell.Selection.HasPage ? StudioScopeKind.Page : StudioScopeKind.Chapter;
        }
    }

    /// <summary>Scope text every batch action/export preflight carries (FUSION §2.3: 作用域后缀).</summary>
    public string SelectionSummary => ResolvedScope switch
    {
        StudioScopeKind.SelectedPages => $"选中 {_shell.Selection.MultiPageCount} 页",
        StudioScopeKind.Region => "当前 Region",
        StudioScopeKind.Page => "当前页",
        _ => "本章",
    };

    /// <summary>Suffix form used by batch actions: " · 选中 3 页" / " · 当前页".</summary>
    public string ScopeSuffix => ResolvedScope switch
    {
        StudioScopeKind.SelectedPages => $" · 选中 {_shell.Selection.MultiPageCount} 页",
        StudioScopeKind.Region => " · 当前 Region",
        StudioScopeKind.Page => " · 当前页",
        _ => " · 全部",
    };

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

    /// <summary>Replaces the multi-page selection; routed to <c>ShellState</c> (the only authority).</summary>
    public void SetSelectedPages(IEnumerable<string> pageIds)
    {
        var unique = new List<string>();
        foreach (var pageId in pageIds)
        {
            if (!string.IsNullOrEmpty(pageId) && !unique.Contains(pageId, StringComparer.Ordinal))
            {
                unique.Add(pageId);
            }
        }

        _shell.SetMultiPage(unique);
    }

    /// <summary>Adds/removes one page from the multi-page scope (Ctrl-click semantics).</summary>
    public void TogglePage(string pageId)
    {
        if (string.IsNullOrEmpty(pageId))
        {
            return;
        }

        _shell.ToggleMultiPage(pageId);
    }

    public void ClearSelectedPages() => _shell.ClearMultiPage();

    private void OnShellSelectionChanged(object? sender, EventArgs e)
    {
        Raise(nameof(BookId));
        Raise(nameof(ChapterId));
        Raise(nameof(CurrentPageId));
        Raise(nameof(CurrentRegionId));
        Raise(nameof(SelectedPageIds));
        Raise(nameof(SelectedPageCount));
        Raise(nameof(ResolvedScope));
        Raise(nameof(SelectionSummary));
        Raise(nameof(ScopeSuffix));
        Changed?.Invoke(this, EventArgs.Empty);
    }

    private void SetField<T>(ref T field, T value, [System.Runtime.CompilerServices.CallerMemberName] string? name = null)
    {
        if (Set(ref field, value, name))
        {
            Changed?.Invoke(this, EventArgs.Empty);
        }
    }
}
