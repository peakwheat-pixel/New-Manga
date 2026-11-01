using NewManga.App.Shell.V2;

namespace NewManga.App.Shell.V2.Frontends;

/// <summary>Cross-scheme session values only; this object carries UI state, never business authority.</summary>
public sealed class CurrentSessionMemento
{
    private readonly object _knownRunGate = new();
    private readonly List<string> _knownRunIds = new();

    public CurrentShellMemento Shell { get; } = new();
    public CurrentStudioMemento Studio { get; } = new();
    public CurrentReaderMemento Reader { get; } = new();
    public CurrentConsoleMemento Console { get; } = new();
    public CurrentAppearanceDraftMemento Appearance { get; } = new();

    public IReadOnlyList<string> KnownRunIds
    {
        get { lock (_knownRunGate) return _knownRunIds.ToArray(); }
    }

    internal void RememberRunId(string runId)
    {
        lock (_knownRunGate)
        {
            var existing = _knownRunIds.IndexOf(runId);
            if (existing == 0) return;
            if (existing > 0) _knownRunIds.RemoveAt(existing);
            _knownRunIds.Insert(0, runId);
            if (_knownRunIds.Count > 12) _knownRunIds.RemoveAt(_knownRunIds.Count - 1);
        }
    }
}

/// <summary>Shell selection, per-space filters/layout, and surface stack shared by recreated content.</summary>
public sealed class CurrentShellMemento
{
    public SpaceId CurrentSpace { get; set; } = SpaceId.Library;
    public StudioMode StudioMode { get; set; } = StudioMode.Page;
    public ShellSelection Selection { get; set; } = ShellSelection.Empty;
    public List<ShellSurface> SurfaceStack { get; } = new() { ShellSurface.Spaces };
    public Dictionary<string, SpaceViewState> Views { get; } = new(StringComparer.Ordinal)
    {
        [ViewKey(SpaceId.Library, null)] = new SpaceViewState(),
        [ViewKey(SpaceId.Studio, StudioMode.Page)] = new SpaceViewState(),
        [ViewKey(SpaceId.Studio, StudioMode.Batch)] = new SpaceViewState(),
        [ViewKey(SpaceId.Console, null)] = new SpaceViewState(),
    };
    public bool HasUnmappedState { get; set; }

    internal static string ViewKey(SpaceId space, StudioMode? mode) =>
        space == SpaceId.Studio && mode is not null ? $"Studio.{mode}" : space.ToString();
}

/// <summary>Studio confirmation/navigation and ephemeral summaries, retained until user resolves them.</summary>
public sealed class CurrentStudioMemento
{
    public string? PendingNavigationPageId { get; set; }
    public StudioMode? PendingMode { get; set; }
    public bool HasPendingConfirmation { get; set; }
    public string? LastRerenderSummary { get; set; }
    public string? RunId { get; set; }
}

/// <summary>Reader UI anchor mapped by page ID, plus the already persisted Core progress projection.</summary>
public sealed class CurrentReaderMemento
{
    public string? BookId { get; set; }
    public string? ChapterId { get; set; }
    public string? PageId { get; set; }
    public string? SemanticAnchor { get; set; }
    public string Layout { get; set; } = "Paged";
    public string Direction { get; set; } = "Rtl";
    public double ScrollOffset { get; set; }
    public bool AnchorMapped { get; set; } = true;
    public bool HasAnchor => !string.IsNullOrWhiteSpace(PageId) || !string.IsNullOrWhiteSpace(SemanticAnchor);
}

/// <summary>Console inputs and run selection that survive rebuilding the shell content.</summary>
public sealed class CurrentConsoleMemento
{
    public string RunIdInput { get; set; } = string.Empty;
    public string RunIdempotencyKey { get; set; } = string.Empty;
    public string? TrackedRunId { get; set; }
    public string SelectedSectionId { get; set; } = "Tasks";
    public bool PollingPreferred { get; set; } = true;
}

/// <summary>Appearance draft is inspected read-only by preflight; it is never applied there.</summary>
public sealed class CurrentAppearanceDraftMemento
{
    public bool IsDirty { get; set; }
    public bool IsMapped { get; set; } = true;
    public string? DraftKey { get; set; }
    public string? DraftValue { get; set; }
}
