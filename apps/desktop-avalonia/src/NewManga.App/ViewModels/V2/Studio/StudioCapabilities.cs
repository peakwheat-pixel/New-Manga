namespace NewManga.App.ViewModels.V2.Studio;

/// <summary>
/// Every Studio write command, split by who provides the wire. The three "existing" commands are
/// already on <c>IHostController</c> (set_region_type / restore_region_revision / rerender_page);
/// the rest belong to the V11R-F0-1 region write face and are NOT wired in this build.
/// </summary>
public enum StudioCommand
{
    /// <summary>Wired: <c>IHostController.SetRegionTypeAsync</c> (set_region_type).</summary>
    SetRegionType,

    /// <summary>Wired: <c>IHostController.RestoreRegionRevisionAsync</c> (restore_region_revision).</summary>
    RestoreRevision,

    /// <summary>Wired: <c>IHostController.RerenderPageAsync</c> (rerender_page).</summary>
    RerenderPage,

    // ---- V11R-F0-1 region write face: not merged into this branch yet (never faked) ----
    CreateRegion,
    ReOcrRegion,
    DeleteRegion,
    MoveRegion,
    ResizeRegion,
    MergeRegions,
    SplitRegion,
    ReorderRegions,
    SaveEditedTranslation,
    SaveFinalTranslation,
    ConfirmFinal,
    LockPage,
    LockRegion,
    LockTranslation,
    LockInpaint,
    PinRevision,
}

/// <summary>
/// V11R-B-3 AC4 (降级): UI never guesses whether a write works. The gate answers "may this control be
/// enabled, and if not why", with the contract's "能力待接入" wording for F0-1 commands and the real
/// host reason for wired commands on a not-ready/read-only host.
/// </summary>
public sealed class StudioCapabilityGate
{
    public const string NotWiredTooltip = "能力待接入（V11R-F0-1 写面未合入）";
    public const string HostNotReadyTooltip = "Host 未就绪：启动失败或正在启动";
    public const string ReadOnlyTooltip = "只读模式：Host 未达 parity，写操作已禁用";

    private static readonly HashSet<StudioCommand> WiredCommands = new()
    {
        StudioCommand.SetRegionType,
        StudioCommand.RestoreRevision,
        StudioCommand.RerenderPage,
    };

    public StudioCapabilityGate(bool hostReady = true, bool writesAllowed = true)
    {
        HostReady = hostReady;
        WritesAllowed = writesAllowed;
    }

    /// <summary>Default gate for a headless/standalone Studio host (writable fake host).</summary>
    public static StudioCapabilityGate Ready { get; } = new(true, true);

    public bool HostReady { get; }

    public bool WritesAllowed { get; }

    /// <summary>True when the command has a wire in this build.</summary>
    public static bool IsWired(StudioCommand command) => WiredCommands.Contains(command);

    /// <summary>True when the control must be enabled.</summary>
    public bool CanExecute(StudioCommand command) =>
        IsWired(command) && HostReady && WritesAllowed;

    /// <summary>Tooltip text; empty when the command is enabled.</summary>
    public string Tooltip(StudioCommand command) =>
        CanExecute(command)
            ? string.Empty
            : !IsWired(command)
                ? NotWiredTooltip
                : !HostReady
                    ? HostNotReadyTooltip
                    : ReadOnlyTooltip;

    /// <summary>True when the command's control must render the "能力待接入" marker.</summary>
    public bool IsNotWired(StudioCommand command) => !IsWired(command);

    /// <summary>Gate with the current host state applied (rebuilt on every host transition).</summary>
    public StudioCapabilityGate WithHost(bool hostReady, bool writesAllowed) => new(hostReady, writesAllowed);
}

/// <summary>
/// V11R-B-3/B-4: read faces the frozen <c>IHostController</c> does not expose yet. Each source is
/// either wired or explicitly <c>NOT_WIRED</c>; the UI shows "能力待接入" instead of inventing values.
/// When V11R-F0-1 (region text / locks) and V11R-A-2 (run projection) merge, only the adapter class is
/// swapped — no view or view-model change.
/// </summary>
public sealed record RegionTextTiers(
    string? OcrText,
    string? MachineTranslation,
    string? EditedTranslation,
    string? FinalTranslation,
    string? ReviewState,
    string? SourceProvider);

/// <summary>Region protection/health flags (四把锁 + failed badge). Not on the frozen read face.</summary>
public sealed record RegionFlags(
    bool PageLocked,
    bool RegionLocked,
    bool TranslationLocked,
    bool InpaintLocked,
    bool Failed,
    string? ErrorCode = null);

/// <summary>Read seam for the four text tiers; <c>null</c> = the read is unavailable.</summary>
public interface IRegionTextSource
{
    bool IsWired { get; }

    Task<RegionTextTiers?> LoadAsync(string regionId, CancellationToken cancellationToken = default);
}

/// <summary>Read seam for the four locks + failed badge.</summary>
public interface IRegionFlagSource
{
    bool IsWired { get; }

    Task<RegionFlags?> LoadAsync(string regionId, CancellationToken cancellationToken = default);
}

/// <summary>
/// Degradation source for this build: no text/lock read command exists, so every call returns
/// <c>null</c> and the UI renders NOT_WIRED. It never fabricates empty strings as if they were data.
/// </summary>
public sealed class NotWiredRegionTextSource : IRegionTextSource
{
    public bool IsWired => false;

    public Task<RegionTextTiers?> LoadAsync(string regionId, CancellationToken cancellationToken = default) =>
        Task.FromResult<RegionTextTiers?>(null);
}

/// <summary>Degradation source for locks/failed flags (see <see cref="NotWiredRegionTextSource"/>).</summary>
public sealed class NotWiredRegionFlagSource : IRegionFlagSource
{
    public bool IsWired => false;

    public Task<RegionFlags?> LoadAsync(string regionId, CancellationToken cancellationToken = default) =>
        Task.FromResult<RegionFlags?>(null);
}
