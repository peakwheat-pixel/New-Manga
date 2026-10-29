using System.Collections.ObjectModel;

namespace NewManga.App.Shell.V2;

/// <summary>Top-level spaces (contract §6.1): Ctrl+1 / Ctrl+2 / Ctrl+3.</summary>
public enum SpaceId
{
    Library,
    Studio,
    Console,
}

/// <summary>Studio's two work modes (contract §6.1): Tab switches, selection is shared.</summary>
public enum StudioMode
{
    Page,
    Batch,
}

/// <summary>Overlay surfaces stacked on top of the spaces (contract §6.1).</summary>
public enum ShellSurface
{
    Spaces,
    ThemeStudio,
    ReaderOverlay,
}

/// <summary>
/// The single selection model (FUSION_SPEC §1 hard rule 1, contract §6.1). Every workspace reads and
/// writes this object; no ViewModel is allowed to keep a second copy of the selection.
/// </summary>
public sealed record ShellSelection
{
    public static ShellSelection Empty { get; } = new();

    public string? BookId { get; init; }

    public string? ChapterId { get; init; }

    public string? PageId { get; init; }

    public string? RegionId { get; init; }

    /// <summary>Studio Batch / Library page multi-selection. Order is the user's click order.</summary>
    public IReadOnlyList<string> MultiPage { get; init; } = Array.Empty<string>();

    public bool HasBook => !string.IsNullOrEmpty(BookId);

    public bool HasChapter => !string.IsNullOrEmpty(ChapterId);

    public bool HasPage => !string.IsNullOrEmpty(PageId);

    public bool HasRegion => !string.IsNullOrEmpty(RegionId);

    public int MultiPageCount => MultiPage.Count;

    public bool IsEmpty => !HasBook && !HasChapter && !HasPage && !HasRegion && MultiPageCount == 0;

    public ShellSelection WithBook(string? bookId) => new() { BookId = bookId };

    public ShellSelection WithChapter(string? chapterId) => this with
    {
        ChapterId = chapterId,
        PageId = null,
        RegionId = null,
        MultiPage = Array.Empty<string>(),
    };

    public ShellSelection WithPage(string? pageId) => this with
    {
        PageId = pageId,
        RegionId = null,
    };

    public ShellSelection WithRegion(string? regionId) => this with { RegionId = regionId };

    public ShellSelection WithMultiPage(IReadOnlyList<string> multiPage) => this with
    {
        MultiPage = multiPage,
        PageId = multiPage.Count > 0 ? multiPage[^1] : PageId,
    };

    public string Describe()
    {
        var parts = new List<string>();
        if (HasBook)
        {
            parts.Add($"book:{BookId}");
        }

        if (HasChapter)
        {
            parts.Add($"chapter:{ChapterId}");
        }

        if (HasPage)
        {
            parts.Add($"page:{PageId}");
        }

        if (HasRegion)
        {
            parts.Add($"region:{RegionId}");
        }

        if (MultiPageCount > 0)
        {
            parts.Add($"multi:{MultiPageCount}");
        }

        return parts.Count == 0 ? "none" : string.Join(" ", parts);
    }
}

/// <summary>
/// Per-space retained UI context (contract §6.1 "各空间滚动与筛选"). The shell writes it on
/// deactivation and restores it on activation; switching spaces never rebuilds a ViewModel.
/// </summary>
public sealed class SpaceViewState
{
    public double ScrollOffsetX { get; set; }

    public double ScrollOffsetY { get; set; }

    public string SearchText { get; set; } = string.Empty;

    public string SortKey { get; set; } = string.Empty;

    public string FilterKey { get; set; } = string.Empty;

    public string? FocusKey { get; set; }

    public void ResetFilters()
    {
        SearchText = string.Empty;
        SortKey = string.Empty;
        FilterKey = string.Empty;
    }
}

/// <summary>
/// V11R-B-1: the ONLY state source of the new shell (contract §6.1). Holds the current space, the
/// Studio mode, the shared selection, per-space scroll/filter context and the overlay surface stack.
/// ViewModels observe this object instead of owning a second copy.
/// </summary>
public sealed class ShellState : ObservableObject
{
    private readonly List<ShellSurface> _surfaces = new() { ShellSurface.Spaces };
    private readonly Dictionary<string, SpaceViewState> _views = new(StringComparer.Ordinal)
    {
        [Key(SpaceId.Library, null)] = new SpaceViewState(),
        [Key(SpaceId.Studio, StudioMode.Page)] = new SpaceViewState(),
        [Key(SpaceId.Studio, StudioMode.Batch)] = new SpaceViewState(),
        [Key(SpaceId.Console, null)] = new SpaceViewState(),
    };

    private SpaceId _currentSpace = SpaceId.Library;
    private StudioMode _studioMode = StudioMode.Page;
    private ShellSelection _selection = ShellSelection.Empty;

    // V11R-INT-0: registered workspaces (Library/Console from this Owner; Studio from ui-studio;
    // Theme Studio uses its own surface stack, registered by the integration step).
    private readonly Dictionary<SpaceId, IWorkspaceView> _workspaces = new();

    public event EventHandler? SpaceChanged;

    public event EventHandler? ModeChanged;

    public event EventHandler? SelectionChanged;

    public event EventHandler? SurfaceChanged;

    /// <summary>Raised when a workspace is registered/unregistered so the host can refresh placeholders.</summary>
    public event EventHandler? WorkspacesChanged;

    public SpaceId CurrentSpace => _currentSpace;

    public StudioMode StudioMode => _studioMode;

    public ShellSelection Selection => _selection;

    /// <summary>Bottom → top. Always starts with <see cref="ShellSurface.Spaces"/>.</summary>
    public IReadOnlyList<ShellSurface> SurfaceStack => _surfaces;

    public ShellSurface CurrentSurface => _surfaces[^1];

    public bool HasOverlay => CurrentSurface != ShellSurface.Spaces;

    public bool IsReaderOpen => CurrentSurface == ShellSurface.ReaderOverlay;

    public bool IsThemeStudioOpen => CurrentSurface == ShellSurface.ThemeStudio;

    public bool IsStudioSpace => CurrentSpace == SpaceId.Studio;

    public SpaceViewState LibraryView => GetView(SpaceId.Library, null);

    public SpaceViewState StudioPageView => GetView(SpaceId.Studio, StudioMode.Page);

    public SpaceViewState StudioBatchView => GetView(SpaceId.Studio, StudioMode.Batch);

    public SpaceViewState ConsoleView => GetView(SpaceId.Console, null);

    /// <summary>View context of the current space+mode (Studio splits Page/Batch, others ignore mode).</summary>
    public SpaceViewState CurrentView => GetView(_currentSpace, _currentSpace == SpaceId.Studio ? _studioMode : null);

    public void SwitchSpace(SpaceId space)
    {
        if (_currentSpace == space)
        {
            return;
        }

        _currentSpace = space;
        OnPropertyChanged(nameof(CurrentSpace), nameof(CurrentView), nameof(IsStudioSpace));
        SpaceChanged?.Invoke(this, EventArgs.Empty);
    }

    public void SetStudioMode(StudioMode mode)
    {
        if (_studioMode == mode)
        {
            return;
        }

        _studioMode = mode;
        OnPropertyChanged(nameof(StudioMode), nameof(CurrentView));
        ModeChanged?.Invoke(this, EventArgs.Empty);
    }

    public void ToggleStudioMode() =>
        SetStudioMode(_studioMode == StudioMode.Page ? StudioMode.Batch : StudioMode.Page);

    public void SetSelection(ShellSelection selection)
    {
        if (ReferenceEquals(selection, _selection) || selection == _selection)
        {
            return;
        }

        _selection = selection;
        OnPropertyChanged(nameof(Selection));
        SelectionChanged?.Invoke(this, EventArgs.Empty);
    }

    public void SelectBook(string? bookId) => SetSelection(_selection.WithBook(bookId));

    public void SelectChapter(string? chapterId) => SetSelection(_selection.WithChapter(chapterId));

    public void SelectPage(string? pageId) => SetSelection(_selection.WithPage(pageId));

    public void SelectRegion(string? regionId) => SetSelection(_selection.WithRegion(regionId));

    public void SetMultiPage(IEnumerable<string> pageIds) =>
        SetSelection(_selection.WithMultiPage(pageIds.ToList()));

    public void ToggleMultiPage(string pageId)
    {
        var current = _selection.MultiPage;
        var next = current.Contains(pageId, StringComparer.Ordinal)
            ? current.Where(id => !string.Equals(id, pageId, StringComparison.Ordinal)).ToList()
            : current.Concat(new[] { pageId }).ToList();
        SetSelection(_selection.WithMultiPage(next));
    }

    public void ClearMultiPage() => SetSelection(_selection.WithMultiPage(Array.Empty<string>()));

    public void ClearSelection() => SetSelection(ShellSelection.Empty);

    public bool PushSurface(ShellSurface surface)
    {
        if (surface == ShellSurface.Spaces || CurrentSurface == surface)
        {
            return false;
        }

        _surfaces.Add(surface);
        RaiseSurfaceChanged();
        ActivateSurfaceWorkspace(surface);
        return true;
    }

    /// <summary>Esc level-by-level exit: closes exactly one overlay surface.</summary>
    public bool CloseTopSurface()
    {
        if (_surfaces.Count <= 1)
        {
            return false;
        }

        var closed = _surfaces[^1];
        _surfaces.RemoveAt(_surfaces.Count - 1);
        RaiseSurfaceChanged();
        DeactivateSurfaceWorkspace(closed);
        return true;
    }

    public void CloseSurfaces()
    {
        if (_surfaces.Count <= 1)
        {
            return;
        }

        var closed = _surfaces.Skip(1).ToList();
        _surfaces.RemoveRange(1, _surfaces.Count - 1);
        RaiseSurfaceChanged();
        foreach (var surface in closed)
        {
            DeactivateSurfaceWorkspace(surface);
        }
    }

    // ── V11R-INT-0 surface workspaces (Theme Studio overlay) ────────────────────────────────

    private readonly Dictionary<ShellSurface, ISurfaceWorkspace> _surfaceWorkspaces = new();

    public ISurfaceWorkspace? GetSurfaceWorkspace(ShellSurface surface) =>
        _surfaceWorkspaces.TryGetValue(surface, out var workspace) ? workspace : null;

    public bool IsSurfaceWorkspaceRegistered(ShellSurface surface) =>
        _surfaceWorkspaces.ContainsKey(surface);

    public bool RegisterSurfaceWorkspace(ISurfaceWorkspace workspace)
    {
        if (workspace is null || _surfaceWorkspaces.ContainsKey(workspace.Surface))
        {
            return false;
        }

        _surfaceWorkspaces[workspace.Surface] = workspace;
        RaiseWorkspacesChanged();
        if (CurrentSurface == workspace.Surface)
        {
            workspace.OnActivated(this);
        }

        return true;
    }

    public bool UnregisterSurfaceWorkspace(ShellSurface surface)
    {
        if (!_surfaceWorkspaces.Remove(surface))
        {
            return false;
        }

        RaiseWorkspacesChanged();
        return true;
    }

    private void ActivateSurfaceWorkspace(ShellSurface surface) =>
        GetSurfaceWorkspace(surface)?.OnActivated(this);

    private void DeactivateSurfaceWorkspace(ShellSurface surface) =>
        GetSurfaceWorkspace(surface)?.OnDeactivated(this);

    /// <summary>Honest placeholder copy for the Theme Studio surface when no implementation is registered.</summary>
    public static string ThemeStudioPlaceholderDetail =>
        "主题中心尚未注册：V11R-C-2 的 Theme Studio 接入后由壳承载；此处不显示伪造主题编辑内容。";


    public SpaceViewState GetView(SpaceId space, StudioMode? mode) =>
        _views[Key(space, space == SpaceId.Studio ? mode : null)];

    // ── V11R-INT-0 workspace registry ────────────────────────────────────────────────────────

    public IReadOnlyCollection<IWorkspaceView> Workspaces => _workspaces.Values;

    /// <summary>Workspace registered for the space, or null when the integration has not arrived yet.</summary>
    public IWorkspaceView? GetWorkspace(SpaceId space) =>
        _workspaces.TryGetValue(space, out var workspace) ? workspace : null;

    public bool IsWorkspaceRegistered(SpaceId space) => _workspaces.ContainsKey(space);

    public bool RegisterWorkspace(IWorkspaceView workspace)
    {
        if (workspace is null || _workspaces.ContainsKey(workspace.Space))
        {
            return false;
        }

        _workspaces[workspace.Space] = workspace;
        RaiseWorkspacesChanged();
        return true;
    }

    public bool UnregisterWorkspace(SpaceId space)
    {
        if (!_workspaces.Remove(space))
        {
            return false;
        }

        RaiseWorkspacesChanged();
        return true;
    }

    /// <summary>Honest placeholder copy for a space whose workspace has not been registered.</summary>
    public static string WorkspacePlaceholderDetail(SpaceId space) => space switch
    {
        SpaceId.Library => "资料柜工作区尚未注册：壳不渲染任何伪造书架内容。",
        SpaceId.Studio => "工位工作区尚未注册：Studio（V11R-B-3/B-4）接入后由壳承载；此处不显示伪造画布、矩阵或进度。",
        SpaceId.Console => "控制台工作区尚未注册：壳不渲染任何伪造设置项。",
        _ => "工作区尚未注册：此处不显示伪造内容。",
    };

    public void SetScroll(SpaceId space, StudioMode? mode, double offsetX, double offsetY)
    {
        var view = GetView(space, mode);
        view.ScrollOffsetX = offsetX;
        view.ScrollOffsetY = offsetY;
    }

    public void SetSearch(SpaceId space, StudioMode? mode, string searchText)
    {
        GetView(space, mode).SearchText = searchText ?? string.Empty;
    }

    public void SetSort(SpaceId space, StudioMode? mode, string sortKey) =>
        GetView(space, mode).SortKey = sortKey ?? string.Empty;

    public void SetFilter(SpaceId space, StudioMode? mode, string filterKey) =>
        GetView(space, mode).FilterKey = filterKey ?? string.Empty;

    /// <summary>Breadcrumb labels are resolved by the space ViewModel; state only exposes the path ids.</summary>
    public IReadOnlyList<string> SelectionPath()
    {
        var path = new List<string>();
        if (_selection.HasBook)
        {
            path.Add(_selection.BookId!);
        }

        if (_selection.HasChapter)
        {
            path.Add(_selection.ChapterId!);
        }

        if (_selection.HasPage)
        {
            path.Add(_selection.PageId!);
        }

        if (_selection.HasRegion)
        {
            path.Add(_selection.RegionId!);
        }

        return path;
    }

    private void RaiseWorkspacesChanged()
    {
        OnPropertyChanged(nameof(Workspaces));
        WorkspacesChanged?.Invoke(this, EventArgs.Empty);
    }

    private void RaiseSurfaceChanged()
    {
        OnPropertyChanged(
            nameof(SurfaceStack),
            nameof(CurrentSurface),
            nameof(HasOverlay),
            nameof(IsReaderOpen),
            nameof(IsThemeStudioOpen));
        SurfaceChanged?.Invoke(this, EventArgs.Empty);
    }

    private static string Key(SpaceId space, StudioMode? mode) =>
        space == SpaceId.Studio && mode is not null ? $"Studio.{mode}" : space.ToString();
}
