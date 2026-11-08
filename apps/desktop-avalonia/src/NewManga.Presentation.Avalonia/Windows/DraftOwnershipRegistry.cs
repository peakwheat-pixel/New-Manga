namespace NewManga.Presentation.Avalonia.Windows;

/// <summary>
/// FEA-07 AC2 / FEA-07-RESIDUAL-2 AC-R4a-1: the draft identity a window claims —
/// <c>(SessionId, RegionId)</c>. A null <see cref="RegionId"/> addresses a page-level draft (the Core
/// draft payload allows that); a non-null value addresses one page region. The rules this key takes part
/// in are not restated here: C-13 SC-D03 (<c>doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:55-66</c>) plus
/// the frozen R4a interpretation (<c>doc/tasks/FEA-07-RESIDUAL-2.md:45</c>).
/// </summary>
public readonly record struct DraftKey(string SessionId, string? RegionId)
{
    /// <summary>Key of one page-region draft.</summary>
    public static DraftKey ForRegion(string sessionId, string regionId) => new(sessionId, regionId);

    /// <summary>Key of one page-level draft (no region).</summary>
    public static DraftKey ForPage(string sessionId) => new(sessionId, null);
}

/// <summary>Mechanical outcome kind of one ownership call; it names a result, never a rule.</summary>
public enum DraftClaimStatus
{
    /// <summary>This window became the single owner of the key.</summary>
    Granted = 0,

    /// <summary>The claiming window already owns the key (another panel of the same window).</summary>
    Shared = 1,

    /// <summary>The key is owned by the requested target window after an explicit transfer.</summary>
    Transferred = 2,

    /// <summary>Repeat of an already-satisfied call; nothing changed.</summary>
    Retained = 3,

    /// <summary>The claim may read but not write; <see cref="DraftOwnershipResult.Denial"/> is typed.</summary>
    ReadOnly = 4,
}

/// <summary>Typed reason carried by a read-only <see cref="DraftOwnershipResult"/>.</summary>
public enum DraftDenialReason
{
    /// <summary>No denial.</summary>
    None = 0,

    /// <summary>A different OS window already owns the key.</summary>
    OtherWindowOwner = 1,

    /// <summary>The region is bound to a different session.</summary>
    CrossSessionRegionOwner = 2,

    /// <summary>The window role is constructed read-only.</summary>
    FloatingWindowReadOnly = 3,

    /// <summary>Only the current owner may transfer the key.</summary>
    NotOwner = 4,

    /// <summary>No owner exists for the key yet.</summary>
    UnknownKey = 5,
}

/// <summary>
/// FEA-07-RESIDUAL-2 AC-R4a-1: immutable outcome of one draft ownership call. Every field is init-only, so
/// callers can keep a result (diagnostics, typed refusals) without being able to rewrite ownership state.
/// </summary>
public sealed record DraftOwnershipResult(
    DraftKey Key,
    string WindowToken,
    WindowRole WindowRole,
    DraftClaimStatus Status,
    bool CanEdit,
    string? DraftId,
    string? OwnerWindowToken,
    string? OwnerSessionId,
    DraftDenialReason Denial)
{
    /// <summary>True only when this result allows the calling window to submit draft writes.</summary>
    public bool IsEditable => CanEdit;

    /// <summary>
    /// Typed write gate: read-only outcomes throw instead of silently dropping a write, so a caller can
    /// never turn a refusal into a blank success (FEA-07-RESIDUAL-2 AC-R4a-1).
    /// </summary>
    public void EnsureEditable()
    {
        if (!CanEdit)
        {
            throw new DraftWriteRejectedException(this);
        }
    }
}

/// <summary>Typed refusal raised by <see cref="DraftOwnershipResult.EnsureEditable"/>.</summary>
public sealed class DraftWriteRejectedException : InvalidOperationException
{
    public DraftWriteRejectedException(DraftOwnershipResult ownership)
        : base($"draft write rejected ({ownership.Denial}) for window '{ownership.WindowToken}' on session '{ownership.Key.SessionId}'")
    {
        Ownership = ownership;
    }

    /// <summary>The immutable ownership outcome that caused the refusal.</summary>
    public DraftOwnershipResult Ownership { get; }

    /// <summary>Typed denial reason (<see cref="DraftDenialReason"/>).</summary>
    public DraftDenialReason Reason => Ownership.Denial;

    /// <summary>The draft key the refused write targeted.</summary>
    public DraftKey Key => Ownership.Key;
}

/// <summary>
/// FEA-07-RESIDUAL-2 AC-R4a-1: thread-safe <c>(SessionId, RegionId)</c> draft ownership registry for the
/// window layer. It routes the rules by reference — C-13 SC-D03
/// (<c>doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:55-66</c>) and the frozen R4a interpretation
/// (<c>doc/tasks/FEA-07-RESIDUAL-2.md:45</c>) — and only encodes them mechanically:
/// one owner per key across OS windows, one window may claim the same key repeatedly (panels of that
/// window share one <see cref="DraftOwnershipResult.DraftId"/>), an explicit transfer moves the owner and
/// is idempotent, release makes the key claimable again, and concurrent callers produce exactly one owner.
/// Results are immutable; state is only mutated under <c>_sync</c>.
/// </summary>
public sealed class DraftOwnershipRegistry
{
    private readonly object _sync = new();
    private readonly Dictionary<DraftKey, Owner> _owners = new();
    private readonly Dictionary<string, string> _regionOwners = new(StringComparer.Ordinal);
    private readonly Dictionary<string, WindowRole> _windowRoles = new(StringComparer.Ordinal);
    private long _draftSequence;

    /// <summary>Number of keys currently owned by some window.</summary>
    public int Count
    {
        get
        {
            lock (_sync)
            {
                return _owners.Count;
            }
        }
    }

    /// <summary>
    /// Claims the key for <paramref name="windowToken"/>. The same window (including a second panel of it)
    /// gets <see cref="DraftClaimStatus.Shared"/> and the existing draft id; a different window gets a
    /// read-only result instead of a second owner.
    /// </summary>
    public DraftOwnershipResult TryClaim(DraftKey key, string windowToken, WindowRole role)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(windowToken);
        ValidateKey(key);

        lock (_sync)
        {
            _windowRoles[windowToken] = role;
            _owners.TryGetValue(key, out var owner);

            if (role == WindowRole.Floating)
            {
                return Result(
                    key,
                    windowToken,
                    role,
                    DraftClaimStatus.ReadOnly,
                    canEdit: false,
                    owner?.DraftId,
                    owner?.WindowToken,
                    owner is null ? null : key.SessionId,
                    DraftDenialReason.FloatingWindowReadOnly);
            }

            if (owner is not null)
            {
                return string.Equals(owner.WindowToken, windowToken, StringComparison.Ordinal)
                    ? Result(key, windowToken, role, DraftClaimStatus.Shared, true, owner.DraftId, owner.WindowToken, key.SessionId, DraftDenialReason.None)
                    : Result(key, windowToken, role, DraftClaimStatus.ReadOnly, false, owner.DraftId, owner.WindowToken, key.SessionId, DraftDenialReason.OtherWindowOwner);
            }

            if (key.RegionId is { } region
                && _regionOwners.TryGetValue(region, out var regionSession)
                && !string.Equals(regionSession, key.SessionId, StringComparison.Ordinal))
            {
                return Result(key, windowToken, role, DraftClaimStatus.ReadOnly, false, null, null, regionSession, DraftDenialReason.CrossSessionRegionOwner);
            }

            var draftId = NextDraftId();
            _owners[key] = new Owner(windowToken, draftId, key);
            if (key.RegionId is { } claimedRegion)
            {
                _regionOwners[claimedRegion] = key.SessionId;
            }

            return Result(key, windowToken, role, DraftClaimStatus.Granted, true, draftId, windowToken, key.SessionId, DraftDenialReason.None);
        }
    }

    /// <summary>
    /// Explicit ownership transfer. Only the current owner may move the key, the draft id is preserved, and
    /// repeating the same transfer is an idempotent <see cref="DraftClaimStatus.Retained"/> (same owner, same
    /// draft id, no error) instead of a second mutation.
    /// </summary>
    public DraftOwnershipResult RequestTransfer(DraftKey key, string windowToken, string targetWindowToken)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(windowToken);
        ArgumentException.ThrowIfNullOrWhiteSpace(targetWindowToken);
        ValidateKey(key);

        lock (_sync)
        {
            if (!_owners.TryGetValue(key, out var owner))
            {
                return Result(key, windowToken, KnownRole(windowToken), DraftClaimStatus.ReadOnly, false, null, null, null, DraftDenialReason.UnknownKey);
            }

            if (string.Equals(owner.WindowToken, targetWindowToken, StringComparison.Ordinal))
            {
                return Result(key, targetWindowToken, KnownRole(targetWindowToken), DraftClaimStatus.Retained, true, owner.DraftId, owner.WindowToken, key.SessionId, DraftDenialReason.None);
            }

            if (!string.Equals(owner.WindowToken, windowToken, StringComparison.Ordinal))
            {
                return Result(key, windowToken, KnownRole(windowToken), DraftClaimStatus.ReadOnly, false, owner.DraftId, owner.WindowToken, key.SessionId, DraftDenialReason.NotOwner);
            }

            var targetRole = KnownRole(targetWindowToken);
            if (targetRole == WindowRole.Floating)
            {
                return Result(key, targetWindowToken, targetRole, DraftClaimStatus.ReadOnly, false, owner.DraftId, owner.WindowToken, key.SessionId, DraftDenialReason.FloatingWindowReadOnly);
            }

            owner.WindowToken = targetWindowToken;
            return Result(key, targetWindowToken, targetRole, DraftClaimStatus.Transferred, true, owner.DraftId, owner.WindowToken, key.SessionId, DraftDenialReason.None);
        }
    }

    /// <summary>
    /// Releases one key owned by <paramref name="windowToken"/>. Returns false when the window is not the
    /// owner (a refusal must never steal another window's draft); after a successful release the key can be
    /// claimed again.
    /// </summary>
    public bool Release(DraftKey key, string windowToken)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(windowToken);
        ValidateKey(key);

        lock (_sync)
        {
            if (!_owners.TryGetValue(key, out var owner)
                || !string.Equals(owner.WindowToken, windowToken, StringComparison.Ordinal))
            {
                return false;
            }

            _owners.Remove(key);
            if (key.RegionId is { } region
                && !_owners.Values.Any(entry => string.Equals(entry.Key.RegionId, region, StringComparison.Ordinal)))
            {
                _regionOwners.Remove(region);
            }

            return true;
        }
    }

    /// <summary>Reads the current ownership of one key without claiming it.</summary>
    public bool TryGetOwnership(DraftKey key, out DraftOwnershipResult ownership)
    {
        ValidateKey(key);

        lock (_sync)
        {
            if (!_owners.TryGetValue(key, out var owner))
            {
                ownership = null!;
                return false;
            }

            ownership = Result(key, owner.WindowToken, KnownRole(owner.WindowToken), DraftClaimStatus.Retained, true, owner.DraftId, owner.WindowToken, key.SessionId, DraftDenialReason.None);
            return true;
        }
    }

    /// <summary>Stable snapshot of every owned key (diagnostics/tests); ordered by session then region.</summary>
    public IReadOnlyList<DraftOwnershipResult> Snapshot()
    {
        lock (_sync)
        {
            return _owners
                .OrderBy(pair => pair.Key.SessionId, StringComparer.Ordinal)
                .ThenBy(pair => pair.Key.RegionId, StringComparer.Ordinal)
                .Select(pair => Result(
                    pair.Key,
                    pair.Value.WindowToken,
                    KnownRole(pair.Value.WindowToken),
                    DraftClaimStatus.Retained,
                    true,
                    pair.Value.DraftId,
                    pair.Value.WindowToken,
                    pair.Key.SessionId,
                    DraftDenialReason.None))
                .ToArray();
        }
    }

    /// <summary>Remembers a window role without claiming anything (used by scope/transfer diagnostics).</summary>
    public void RememberWindow(string windowToken, WindowRole role)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(windowToken);

        lock (_sync)
        {
            _windowRoles[windowToken] = role;
        }
    }

    private WindowRole KnownRole(string windowToken) =>
        _windowRoles.TryGetValue(windowToken, out var role) ? role : WindowRole.Main;

    private string NextDraftId() => $"draft-{++_draftSequence:D4}";

    private static void ValidateKey(DraftKey key)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(key.SessionId);
        if (key.RegionId is not null)
        {
            ArgumentException.ThrowIfNullOrWhiteSpace(key.RegionId);
        }
    }

    private static DraftOwnershipResult Result(
        DraftKey key,
        string windowToken,
        WindowRole role,
        DraftClaimStatus status,
        bool canEdit,
        string? draftId,
        string? ownerWindowToken,
        string? ownerSessionId,
        DraftDenialReason denial) =>
        new(key, windowToken, role, status, canEdit, draftId, ownerWindowToken, ownerSessionId, denial);

    private sealed class Owner(string windowToken, string draftId, DraftKey key)
    {
        public string WindowToken { get; set; } = windowToken;

        public string DraftId { get; } = draftId;

        public DraftKey Key { get; } = key;
    }
}

/// <summary>
/// FEA-07-RESIDUAL-2 AC-R4a-1: per-window view of the shared <see cref="DraftOwnershipRegistry"/> exposed
/// as <c>PresentationWindow.DraftOwnership</c>. The window identity and role are fixed at construction, so a
/// <see cref="WindowRole.Floating"/> window stays read-only for every claim it makes — the write gate
/// (<see cref="EnsureWritable"/>) then fails typed instead of reaching the Host.
/// </summary>
public sealed class DraftOwnershipScope
{
    private readonly WindowBroker _broker;

    /// <summary>Creates the view for one OS window identity.</summary>
    public DraftOwnershipScope(WindowBroker broker, string windowToken, WindowRole role)
    {
        _broker = broker ?? throw new ArgumentNullException(nameof(broker));
        ArgumentException.ThrowIfNullOrWhiteSpace(windowToken);
        WindowToken = windowToken;
        Role = role;
    }

    /// <summary>Window identity this scope claims with.</summary>
    public string WindowToken { get; }

    /// <summary>Window role this scope was constructed with.</summary>
    public WindowRole Role { get; }

    /// <summary>
    /// Whether this window may submit draft writes at all. A <see cref="WindowRole.Floating"/> window is
    /// constructed read-only (FEA-07-RESIDUAL-2 AC-R4a-1 / frozen interpretation in the task file).
    /// </summary>
    public bool CanEdit => Role != WindowRole.Floating;

    /// <summary>Claims one draft key for this window (thin forward; see <see cref="DraftOwnershipRegistry"/>).</summary>
    public DraftOwnershipResult TryClaimDraft(DraftKey key) =>
        _broker.TryClaimDraft(key, WindowToken, Role);

    /// <summary>Requests an explicit transfer of this window's key to another window token.</summary>
    public DraftOwnershipResult RequestDraftTransfer(DraftKey key, string targetWindowToken) =>
        _broker.RequestDraftTransfer(key, WindowToken, targetWindowToken);

    /// <summary>Releases this window's key (false when this window is not the owner).</summary>
    public bool ReleaseDraft(DraftKey key) =>
        _broker.ReleaseDraft(key, WindowToken);

    /// <summary>
    /// Typed write gate. Callers run it before any Host draft write; a read-only scope or claim throws
    /// <see cref="DraftWriteRejectedException"/> so the write never starts (zero Host writes).
    /// </summary>
    public void EnsureWritable(DraftOwnershipResult result)
    {
        ArgumentNullException.ThrowIfNull(result);

        if (!CanEdit || !result.CanEdit)
        {
            throw new DraftWriteRejectedException(result);
        }
    }
}
