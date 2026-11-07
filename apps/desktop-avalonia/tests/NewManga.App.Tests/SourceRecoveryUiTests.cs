using System.Text.Json;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Interactivity;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.Shell.V2;
using NewManga.App.ViewModels.V2.Library;
using NewManga.App.Views.V2.Library;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Wire;
using Xunit;
using static NewManga.App.Tests.FakeHostController;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-11-L-S1-B-RECOVERY-REAUTH-1 (B1, AC-LSB-6): the recovery face is a SEPARATE, path-free port.
/// It reuses only the frozen C-16 v1.4 §1 root commands (no new command/capability/field/error code)
/// and never widens the frozen C-07 <see cref="IHostController"/> inventory.
/// </summary>
public sealed class SourceRecoveryAuthorityTests
{
    private static readonly string[] RecoveryMembers =
    [
        nameof(ISourceImportController.DiagnoseSourceRecoveryAsync),
        nameof(ISourceImportController.ReauthorizeSourceAsync),
        nameof(ISourceImportController.ResetSourceRegistryAsync),
    ];

    /// <summary>The frozen <c>HostCommandRegistry.All</c> cardinality at the B1 base commit.</summary>
    private const int CommandCountAtBase = 111;

    [Fact]
    public void RecoveryMembers_LiveOnTheSeparatePort_AndNeverOnTheFrozenHostController()
    {
        var frozen = typeof(IHostController).GetMethods().Select(method => method.Name).ToHashSet(StringComparer.Ordinal);
        var recoveryPort = typeof(ISourceImportController).GetMethods().Select(method => method.Name).ToHashSet(StringComparer.Ordinal);
        foreach (var name in RecoveryMembers)
        {
            Assert.Contains(name, recoveryPort);
            // AC-LSB-6 / C-07 pin: the frozen inventory must not grow a recovery member.
            Assert.DoesNotContain(name, frozen);
        }
    }

    [Fact]
    public void RecoveryMembers_AcceptNoPathOrOpaqueSourceArgument()
    {
        // AC-LSB-6: "re-authorize ONLY the entry's own registered roots[0]" is structural — there is
        // no path / registry id / locator parameter any caller could point at another root.
        foreach (var name in RecoveryMembers)
        {
            var method = typeof(ISourceImportController).GetMethod(name);
            Assert.NotNull(method);
            foreach (var parameter in method!.GetParameters())
            {
                Assert.True(
                    parameter.ParameterType == typeof(CancellationToken) || parameter.ParameterType == typeof(bool),
                    $"{name} must not take a path/id argument, found {parameter.ParameterType.Name} {parameter.Name}");
            }
        }
    }

    [Fact]
    public void RecoverySurface_AddsNoWireCommand_AndKeepsTheFrozenCommandCount()
    {
        // AC-LSB-6: no new command/capability/error code. The cardinality is pinned at the B1 base.
        Assert.True(
            HostCommandRegistry.All.Count == CommandCountAtBase,
            $"the frozen command registry cardinality changed: {HostCommandRegistry.All.Count} (expected {CommandCountAtBase})");
        Assert.DoesNotContain(HostCommandRegistry.All.Keys, key =>
            key.Contains("source_recover", StringComparison.OrdinalIgnoreCase) ||
            key.Contains("reauthor", StringComparison.OrdinalIgnoreCase));
        // Exactly the four frozen C-16 v1.4 §1 root commands exist for the root face.
        var rootCommands = HostCommandRegistry.All.Keys
            .Where(key => key is "source_list_roots" or "source_register_root" or "source_revoke_root" or "source_reset_registry")
            .OrderBy(key => key, StringComparer.Ordinal)
            .ToArray();
        Assert.Equal(
            new[] { "source_list_roots", "source_register_root", "source_reset_registry", "source_revoke_root" },
            rootCommands);
    }

    [Fact]
    public void PlanAndMintPath_NeverInvokesARecoveryCommand_OnlyTheExplicitActionDoes()
    {
        // AC-LSB-5 guard (R-1): the tempting "one-line fix" is to register on a mint failure — that
        // IS automatic re-authorization. The App's plan path may only LIST roots and register once
        // for a NEW root; revoke/reset may not appear there at all.
        var app = Path.Combine(NoDbOsAccessTests.RepoRoot, "apps", "desktop-avalonia", "src", "NewManga.App", "Services");
        var sourceImport = File.ReadAllText(Path.Combine(app, "SourceImportModels.cs"));
        Assert.Equal(1, CountCommandLiterals(sourceImport, "source_register_root"));
        Assert.Equal(1, CountCommandLiterals(sourceImport, "source_list_roots"));
        Assert.Equal(0, CountCommandLiterals(sourceImport, "source_revoke_root"));
        Assert.Equal(0, CountCommandLiterals(sourceImport, "source_reset_registry"));

        var recovery = File.ReadAllText(Path.Combine(app, "SourceRecoveryModels.cs"));
        Assert.Equal(1, CountCommandLiterals(recovery, "source_list_roots"));
        Assert.Equal(1, CountCommandLiterals(recovery, "source_revoke_root"));
        Assert.Equal(1, CountCommandLiterals(recovery, "source_register_root"));
        Assert.Equal(1, CountCommandLiterals(recovery, "source_reset_registry"));
    }

    [Fact]
    public void ReuseSelector_StillSkipsRevokedEntries_AndNeverFallsBackOnAFailedMint()
    {
        // AC-LSB-5: the reuse selector semantics are UNCHANGED — first non-revoked single-root match,
        // no "failed mint → register / try the next candidate" fallback.
        using var document = JsonDocument.Parse("""
        {"entries":[
          {"registry_id":"reg-revoked","roots":["C:\\sources\\book.zip"],"generation":9,"revoked":true},
          {"registry_id":"reg-live","roots":["C:\\sources\\book.zip"],"generation":2,"revoked":false}
        ]}
        """);
        var reuse = SourceImportCoordinator.SelectReusableRoot(document.RootElement, @"C:\sources\book.zip");
        Assert.NotNull(reuse);
        Assert.Equal("reg-live", reuse!.Value.RegistryId);
        Assert.Equal(2, reuse.Value.Generation);

        // Only revoked entries → NO reuse (the explicit register leg is the only next step).
        using var revokedOnly = JsonDocument.Parse("""
        {"entries":[{"registry_id":"reg-revoked","roots":["C:\\sources\\book.zip"],"generation":9,"revoked":true}]}
        """);
        Assert.Null(SourceImportCoordinator.SelectReusableRoot(revokedOnly.RootElement, @"C:\sources\book.zip"));
        // A different path / a multi-root entry is not a reuse match either.
        Assert.Null(SourceImportCoordinator.SelectReusableRoot(document.RootElement, @"C:\sources\other.zip"));
    }

    private static int CountCommandLiterals(string text, string command) =>
        text.Split(new[] { "\"" + command + "\"" }, StringSplitOptions.None).Length - 1;
}

/// <summary>
/// AC-LSB-2/3/4/5/7 at the production-orchestrator layer: the real
/// <see cref="SourceRecoveryCoordinator"/> over a scripted Host-local double, so the assertions are
/// about the exact command frames and their ORDER, not about a fake's counters.
/// </summary>
public sealed class SourceRecoveryOrchestrationTests
{
    private const string Path = @"C:\sources\book.zip";
    private const string OtherPath = @"C:\sources\other.zip";

    private static RecoveryHostDouble Host() => new();

    private static CancellationToken None => CancellationToken.None;

    // ---------------------------------------------------------------- AC-LSB-2 branching

    [Fact]
    public async Task FileLevelProbeFailure_OffersResetOnly_AndWritesNothing()
    {
        var host = Host();
        host.ProbeErrorCode = "SOURCE_REGISTRY_UNAVAILABLE";
        var recovery = new SourceRecoveryCoordinator(host.Dispatcher());

        var diagnosis = await recovery.DiagnoseAsync([Path], "SOURCE_REGISTRY_UNAVAILABLE", hostSideMintFailure: true, None);

        Assert.Equal(SourceRecoveryAction.ResetRegistry, diagnosis.Action);
        Assert.Equal(new[] { "source_list_roots" }, host.FrameNames());
        Assert.Equal(0, host.WriteFrameCount());
    }

    [Fact]
    public async Task OtherProbeCode_OffersNoRecoveryAction_AndDisplaysOnlyThatCode()
    {
        foreach (var probeCode in new[] { "CORE_CAPABILITY_MISSING", "SOURCE_REGISTRY_BUSY" })
        {
            var host = Host();
            host.ProbeErrorCode = probeCode;
            var recovery = new SourceRecoveryCoordinator(host.Dispatcher());

            var diagnosis = await recovery.DiagnoseAsync([Path], "SOURCE_REGISTRY_UNAVAILABLE", hostSideMintFailure: true, None);

            Assert.False(diagnosis.HasAction);
            Assert.Equal(probeCode, diagnosis.ErrorCode);
            Assert.Equal(0, host.WriteFrameCount());
        }
    }

    [Fact]
    public async Task CoreSideFailureOrAnotherPreviewCode_OffersNothing_AndNeverProbes()
    {
        // A Core-side SOURCE_REGISTRY_UNAVAILABLE (or any other preview code) must NOT be treated as
        // a root mismatch: revoking entries for it would be destructive guesswork.
        var host = Host();
        var recovery = new SourceRecoveryCoordinator(host.Dispatcher());

        var coreSide = await recovery.DiagnoseAsync([Path], "SOURCE_REGISTRY_UNAVAILABLE", hostSideMintFailure: false, None);
        var otherCode = await recovery.DiagnoseAsync([Path], "SOURCE_ACCESS_DENIED", hostSideMintFailure: true, None);
        var noFailure = await recovery.DiagnoseAsync(null, null, hostSideMintFailure: false, None);

        Assert.False(coreSide.HasAction);
        Assert.False(otherCode.HasAction);
        Assert.False(noFailure.HasAction);
        Assert.Empty(host.Frames);
    }

    [Fact]
    public async Task ReadableStorageWithStaleEntries_OffersReauthorizeOnly_WithLeafNameAndCount()
    {
        var host = Host();
        host.AddEntry(Path);
        host.AddEntry(Path);
        host.AddEntry(Path, revoked: true); // already revoked: not a recovery target
        host.AddEntry(OtherPath);
        var recovery = new SourceRecoveryCoordinator(host.Dispatcher());

        var diagnosis = await recovery.DiagnoseAsync([Path], "SOURCE_REGISTRY_UNAVAILABLE", hostSideMintFailure: true, None);

        Assert.Equal(SourceRecoveryAction.ReauthorizeSource, diagnosis.Action);
        Assert.Equal("book.zip", diagnosis.SourceLeafName);
        Assert.Equal(2, diagnosis.StaleEntryCount);
        Assert.Equal(new[] { "source_list_roots" }, host.FrameNames());
        Assert.Equal(0, host.WriteFrameCount());
        Assert.DoesNotContain(@"C:\sources", SourceRecoveryText.ReauthorizeOffer(diagnosis.SourceLeafName, diagnosis.StaleEntryCount));
    }

    [Fact]
    public async Task ReadableStorageWithoutAnyStaleEntry_OffersNothing()
    {
        var host = Host();
        host.AddEntry(OtherPath);
        var recovery = new SourceRecoveryCoordinator(host.Dispatcher());

        var diagnosis = await recovery.DiagnoseAsync([Path], "SOURCE_REGISTRY_UNAVAILABLE", hostSideMintFailure: true, None);

        Assert.False(diagnosis.HasAction);
        Assert.Equal(0, host.WriteFrameCount());
    }

    // ---------------------------------------------------------------- AC-LSB-3 ordering / idempotency

    [Fact]
    public async Task Reauthorize_RevokesEverySamePathEntryFirst_ThenRegistersExactlyOnce()
    {
        var host = Host();
        var first = host.AddEntry(Path);
        var second = host.AddEntry(Path, generation: 4);
        var other = host.AddEntry(OtherPath);
        var recovery = new SourceRecoveryCoordinator(host.Dispatcher());

        var result = await recovery.ReauthorizeAsync([Path], None);

        Assert.True(result.Ok, result.ErrorCode + " " + result.Message);
        Assert.Equal(2, result.RevokedCount);
        Assert.Equal(1, result.RegisteredCount);
        Assert.Equal("book.zip", result.LeafName);

        // Exact frame order: probe → revoke(first) → revoke(second) → register(once).
        Assert.Equal(
            new[] { "source_list_roots", "source_revoke_root", "source_revoke_root", "source_register_root" },
            host.FrameNames());
        var revokedIds = host.Frames
            .Where(frame => frame.Name == "source_revoke_root")
            .Select(frame => frame.RegistryId)
            .ToArray();
        Assert.Equal(new[] { first.RegistryId, second.RegistryId }, revokedIds);

        // Both stale entries are revoked with generation+1; exactly ONE active entry remains and the
        // unrelated path is untouched.
        Assert.True(first.Revoked);
        Assert.True(second.Revoked);
        Assert.Equal(2, first.Generation);
        Assert.Equal(5, second.Generation);
        Assert.False(other.Revoked);
        Assert.Single(host.ActiveEntries(Path));
        Assert.Equal(1, host.ActiveEntries(Path)[0].Generation);

        // The re-registration used the entry's OWN persisted root string, never a caller path.
        var registration = Assert.Single(host.Frames, frame => frame.Name == "source_register_root");
        Assert.Equal(Path, registration.RegisteredRoot);
    }

    [Fact]
    public async Task Reauthorize_UsesTheRegisteredRootString_NotTheCallerSpelling()
    {
        var host = Host();
        host.AddEntry(@"C:\SOURCES\BOOK.ZIP");
        var recovery = new SourceRecoveryCoordinator(host.Dispatcher());

        var result = await recovery.ReauthorizeAsync([Path], None);

        Assert.True(result.Ok, result.ErrorCode + " " + result.Message);
        var registration = Assert.Single(host.Frames, frame => frame.Name == "source_register_root");
        Assert.Equal(@"C:\SOURCES\BOOK.ZIP", registration.RegisteredRoot);
        Assert.Equal("BOOK.ZIP", result.LeafName);
    }

    [Fact]
    public async Task Reauthorize_RepeatedExecution_KeepsExactlyOneActiveEntry()
    {
        var host = Host();
        host.AddEntry(Path);
        host.AddEntry(Path);
        var recovery = new SourceRecoveryCoordinator(host.Dispatcher());

        var firstRun = await recovery.ReauthorizeAsync([Path], None);
        var activeAfterFirst = host.ActiveEntries(Path).Count;
        var secondRun = await recovery.ReauthorizeAsync([Path], None);
        var activeAfterSecond = host.ActiveEntries(Path).Count;

        Assert.True(firstRun.Ok && secondRun.Ok, firstRun.ErrorCode + "/" + secondRun.ErrorCode);
        Assert.Equal(1, activeAfterFirst);
        Assert.Equal(1, activeAfterSecond); // idempotent invariant: never two active same-path entries
        Assert.Equal(1, secondRun.RevokedCount); // it revoked the one it had created, then re-registered
        Assert.Equal(1, secondRun.RegisteredCount);
        Assert.Single(host.ActiveEntries(Path));
    }

    // ---------------------------------------------------------------- AC-LSB-4 fail-closed

    [Fact]
    public async Task Reauthorize_RegisterFailure_ReportsRevokedNotReauthorized_WithNoRollback()
    {
        var host = Host();
        var entry = host.AddEntry(Path);
        host.AddEntry(Path);
        host.RegisterErrorCode = "SOURCE_ACCESS_DENIED";
        var recovery = new SourceRecoveryCoordinator(host.Dispatcher());

        var result = await recovery.ReauthorizeAsync([Path], None);

        Assert.False(result.Ok);
        Assert.Equal("SOURCE_ACCESS_DENIED", result.ErrorCode);
        Assert.Equal(2, result.RevokedCount);
        Assert.Equal(0, result.RegisteredCount);
        Assert.True(result.RevokedButNotRegistered);
        Assert.Contains("已撤销", result.Message);
        Assert.Contains("未重新授权", result.Message);
        Assert.Contains("SOURCE_ACCESS_DENIED", result.Message);
        Assert.DoesNotContain(@"C:\sources", result.Message);
        // Revocation is an irreversible persisted fact: nothing rolled it back.
        Assert.True(entry.Revoked);
        Assert.Equal(2, entry.Generation);
        Assert.Empty(host.ActiveEntries(Path));

        // Retryable: clearing the register failure completes the same explicit action.
        host.RegisterErrorCode = null;
        var retry = await recovery.ReauthorizeAsync([Path], None);
        Assert.True(retry.Ok, retry.ErrorCode + " " + retry.Message);
        Assert.Single(host.ActiveEntries(Path));
    }

    [Fact]
    public async Task Reauthorize_RevokeFailure_AbortsBeforeAnyRegistration()
    {
        var host = Host();
        host.AddEntry(Path);
        host.RevokeErrorCode = "SOURCE_REGISTRY_BUSY";
        var recovery = new SourceRecoveryCoordinator(host.Dispatcher());

        var result = await recovery.ReauthorizeAsync([Path], None);

        Assert.False(result.Ok);
        Assert.Equal("SOURCE_REGISTRY_BUSY", result.ErrorCode);
        Assert.Equal(0, result.RegisteredCount);
        Assert.DoesNotContain("source_register_root", host.FrameNames());
    }

    [Fact]
    public async Task Reauthorize_WithNothingToRevoke_WritesNothing()
    {
        // AC-LSB-5 adjacent: a readable storage with no stale entry for the path must NOT fall back
        // to "just register a fresh one" (that would be an unannounced re-authorization).
        var host = Host();
        host.AddEntry(OtherPath);
        var recovery = new SourceRecoveryCoordinator(host.Dispatcher());

        var result = await recovery.ReauthorizeAsync([Path], None);

        Assert.False(result.Ok);
        Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", result.ErrorCode);
        Assert.DoesNotContain("source_register_root", host.FrameNames());
        Assert.DoesNotContain("source_revoke_root", host.FrameNames());
    }

    [Fact]
    public async Task Reauthorize_PartialOutcomeRetry_FinishesTheRegisterLegFromTheRevokedRoot()
    {
        // AC-LSB-4 "可重试": after the revokes completed and the register failed, the path is
        // revoked-only. Retrying the SAME explicit action must finish the register leg from the
        // path's own already-registered root — and only from an explicit action.
        var host = Host();
        host.AddEntry(Path);
        host.RegisterErrorCode = "SOURCE_ACCESS_DENIED";
        var recovery = new SourceRecoveryCoordinator(host.Dispatcher());
        var partial = await recovery.ReauthorizeAsync([Path], None);
        Assert.False(partial.Ok);
        Assert.Empty(host.ActiveEntries(Path));

        host.RegisterErrorCode = null;
        var retry = await recovery.ReauthorizeAsync([Path], None);

        Assert.True(retry.Ok, retry.ErrorCode + " " + retry.Message);
        Assert.Equal(0, retry.RevokedCount); // nothing left to revoke — the revokes already happened
        Assert.Equal(1, retry.RegisteredCount);
        Assert.Single(host.ActiveEntries(Path));
        var registration = host.Frames.Last(frame => frame.Name == "source_register_root");
        Assert.Equal(Path, registration.RegisteredRoot);
    }

    [Fact]
    public async Task Reauthorize_ReadOnlyHost_WritesNothing()
    {
        var host = Host();
        host.AddEntry(Path);
        var recovery = new SourceRecoveryCoordinator(host.Dispatcher(), () => false);

        var result = await recovery.ReauthorizeAsync([Path], None);

        Assert.False(result.Ok);
        Assert.Equal("HOST_READ_ONLY", result.ErrorCode);
        Assert.Empty(host.Frames);
    }

    // ---------------------------------------------------------------- AC-LSB-2/7 reset + sanitization

    [Fact]
    public async Task Reset_RequiresConfirmation_AndNeverSurfacesTheQuarantinePath()
    {
        var host = Host();
        var recovery = new SourceRecoveryCoordinator(host.Dispatcher());

        var refused = await recovery.ResetRegistryAsync(confirm: false, None);
        Assert.False(refused.Ok);
        Assert.Equal("INVALID_REQUEST", refused.ErrorCode);
        Assert.Empty(host.Frames); // the unconfirmed reset sends nothing at all

        var done = await recovery.ResetRegistryAsync(confirm: true, None);
        Assert.True(done.Ok, done.ErrorCode + " " + done.Message);
        Assert.Equal(new[] { "source_reset_registry" }, host.FrameNames());
        // The scripted response carried the production quarantine path; no App text may echo it.
        foreach (var text in new[]
                 {
                     SourceRecoveryText.ResetOffer(), SourceRecoveryText.ResetConfirmation(),
                     SourceRecoveryText.ResetSucceeded(), SourceRecoveryText.ResetFailed("SOURCE_REGISTRY_UNAVAILABLE"),
                     done.Message,
                 })
        {
            Assert.DoesNotContain("quarantine", text, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(@"C:\", text, StringComparison.Ordinal);
        }
    }

    [Fact]
    public async Task Reset_FailureKeepsTypedCode_AndNeverReadsAQuarantinePath()
    {
        var host = Host();
        host.ResetErrorCode = "SOURCE_REGISTRY_UNAVAILABLE";
        var recovery = new SourceRecoveryCoordinator(host.Dispatcher());

        var result = await recovery.ResetRegistryAsync(confirm: true, None);

        Assert.False(result.Ok);
        Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", result.ErrorCode);
        Assert.DoesNotContain("quarantine", result.Message, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public async Task RecoveryTransportFailures_BecomeTypedResults_AndNeverEscapeIntoTheUi()
    {
        // A read-only Host race / transport failure must never throw out of the recovery face: the
        // dock would otherwise surface an unhandled task exception instead of a typed refusal.
        var host = Host();
        host.AddEntry(Path);
        host.TransportErrorOn = "source_revoke_root";
        var recovery = new SourceRecoveryCoordinator(host.Dispatcher());
        var reauthorize = await recovery.ReauthorizeAsync([Path], None);
        Assert.False(reauthorize.Ok);
        Assert.False(string.IsNullOrEmpty(reauthorize.ErrorCode));
        Assert.DoesNotContain(@"C:\sources", reauthorize.Message);

        host.TransportErrorOn = "source_reset_registry";
        var reset = await recovery.ResetRegistryAsync(confirm: true, None);
        Assert.False(reset.Ok);
        Assert.False(string.IsNullOrEmpty(reset.ErrorCode));
        Assert.DoesNotContain("quarantine", reset.Message, StringComparison.OrdinalIgnoreCase);
    }

    // ---------------------------------------------------------------- parser / selector units

    [Fact]
    public void ParseRoots_ReadsTheFrozenProjection_AndSkipsUnusableRows()
    {
        using var document = JsonDocument.Parse("""
        {"entries":[
          {"registry_id":"reg-a","roots":["C:\\sources\\book.zip"],"generation":1,"revoked":false},
          {"registry_id":"reg-b","roots":["C:\\sources\\book.zip","C:\\sources\\two.zip"],"generation":1,"revoked":false},
          {"registry_id":"reg-c","roots":[],"generation":1,"revoked":false},
          {"registry_id":"","roots":["C:\\sources\\book.zip"],"generation":1,"revoked":false},
          {"registry_id":"reg-d","roots":["C:\\sources\\gone.zip"],"generation":3,"revoked":true}
        ]}
        """);

        var entries = SourceRecoveryCoordinator.ParseRoots(document.RootElement);

        Assert.Equal(new[] { "reg-a", "reg-d" }, entries.Select(entry => entry.RegistryId));
        Assert.True(entries[1].Revoked);
        Assert.Equal(3, entries[1].Generation);
    }

    [Fact]
    public void SelectStaleEntries_TakesOnlySingleRootNonRevokedMatches()
    {
        var entries = new[]
        {
            new SourceRegistryEntry("reg-old", Path, 1, Revoked: true),
            new SourceRegistryEntry("reg-live", Path, 2, Revoked: false),
            new SourceRegistryEntry("reg-other", OtherPath, 1, Revoked: false),
        };

        var selected = SourceRecoveryCoordinator.SelectStaleEntries(entries, [Path.ToLowerInvariant()]);

        var entry = Assert.Single(selected);
        Assert.Equal("reg-live", entry.RegistryId); // the revoked duplicate is skipped; matching is case-insensitive
    }

    // ---------------------------------------------------------------- the Host-local double

    private sealed class RecoveryHostDouble
    {
        private int _nextId = 100;

        public List<Frame> Frames { get; } = new();

        public List<Entry> Entries { get; } = new();

        public string? ProbeErrorCode { get; set; }

        public string? RevokeErrorCode { get; set; }

        public string? RegisterErrorCode { get; set; }

        public string? ResetErrorCode { get; set; }

        /// <summary>Production Host response shape: it DOES carry the absolute quarantine path.</summary>
        public string QuarantinePath { get; } = @"C:\host\quarantine\leaked.dat";

        /// <summary>When set to a command name, that Host-local call fails with a raw transport error.</summary>
        public string? TransportErrorOn { get; set; }

        public Entry AddEntry(string root, int generation = 1, bool revoked = false)
        {
            var entry = new Entry
            {
                RegistryId = "reg-" + (++_nextId),
                Root = root,
                Generation = generation,
                Revoked = revoked,
            };
            Entries.Add(entry);
            return entry;
        }

        public List<Entry> ActiveEntries(string root) => Entries
            .Where(entry => !entry.Revoked && string.Equals(entry.Root, root, StringComparison.OrdinalIgnoreCase))
            .ToList();

        public List<string> FrameNames() => Frames.Select(frame => frame.Name).ToList();

        public int WriteFrameCount() => Frames.Count(frame => frame.Name != "source_list_roots");

        public HostCommandDispatcher Dispatcher() => new(core: null, hostLocal: HostLocalAsync);

        private Task<HostCommandResult> HostLocalAsync(string name, JsonElement payload, CancellationToken token)
        {
            var registryId = payload.ValueKind == JsonValueKind.Object &&
                             payload.TryGetProperty("registry_id", out var id) &&
                             id.ValueKind == JsonValueKind.String
                ? id.GetString()
                : null;
            var registeredRoot = payload.ValueKind == JsonValueKind.Object &&
                                 payload.TryGetProperty("roots", out var roots) &&
                                 roots.ValueKind == JsonValueKind.Array &&
                                 roots.GetArrayLength() == 1
                ? roots[0].GetString()
                : null;
            Frames.Add(new Frame(
                name,
                payload.ValueKind == JsonValueKind.Object ? payload.GetRawText() : "{}",
                registryId,
                registeredRoot));
            if (string.Equals(TransportErrorOn, name, StringComparison.Ordinal))
            {
                return Task.FromException<HostCommandResult>(new InvalidOperationException("scripted transport failure"));
            }

            return name switch
            {
                "source_list_roots" => Listed(),
                "source_revoke_root" => Revoked(payload),
                "source_register_root" => Registered(payload),
                "source_reset_registry" => Reset(payload),
                _ => throw Typed("INVALID_REQUEST"),
            };
        }

        private Task<HostCommandResult> Listed()
        {
            if (ProbeErrorCode is { } code) throw Typed(code);
            return Task.FromResult(Result("source_list_roots", BuildEntries()));
        }

        private Task<HostCommandResult> Revoked(JsonElement payload)
        {
            if (RevokeErrorCode is { } code) throw Typed(code);
            var id = payload.GetProperty("registry_id").GetString();
            var entry = Entries.SingleOrDefault(candidate => candidate.RegistryId == id)
                ?? throw Typed("SOURCE_ACCESS_DENIED");
            if (!entry.Revoked)
            {
                entry.Revoked = true;
                entry.Generation++;
            }

            return Task.FromResult(Result("source_revoke_root", JsonSerializer.SerializeToElement(
                new { revoked = true, generation = entry.Generation })));
        }

        private Task<HostCommandResult> Registered(JsonElement payload)
        {
            if (RegisterErrorCode is { } code) throw Typed(code);
            var root = payload.GetProperty("roots")[0].GetString()!;
            var created = AddEntry(root);
            return Task.FromResult(Result("source_register_root", JsonSerializer.SerializeToElement(
                new { registry_id = created.RegistryId, generation = created.Generation })));
        }

        private Task<HostCommandResult> Reset(JsonElement payload)
        {
            if (ResetErrorCode is { } code) throw Typed(code);
            if (!payload.GetProperty("confirm").GetBoolean()) throw Typed("INVALID_REQUEST");
            Entries.Clear();
            // Exactly the production Host payload, INCLUDING the absolute quarantine path.
            return Task.FromResult(Result("source_reset_registry", JsonSerializer.SerializeToElement(
                new { reset = true, quarantine_path = QuarantinePath })));
        }

        private JsonElement BuildEntries()
        {
            var items = Entries.Select(entry => new
            {
                registry_id = entry.RegistryId,
                locator = entry.Root,
                roots = new[] { entry.Root },
                generation = entry.Generation,
                created_at = "2026-11-07T00:00:00.0000000+00:00",
                last_used_at = "2026-11-07T00:00:00.0000000+00:00",
                revoked = entry.Revoked,
            }).ToArray();
            return JsonSerializer.SerializeToElement(new { entries = items });
        }

        private static Exception Typed(string code) =>
            new CoreOperationException(code, "internal", true, "scripted host-local refusal", null);

        private static HostCommandResult Result(string name, JsonElement value) =>
            new(name, HostCommandStatus.Implemented, HostCommandChannel.HostLocal, value);

        public sealed record Frame(string Name, string RawPayload, string? RegistryId, string? RegisteredRoot);

        public sealed class Entry
        {
            public string RegistryId { get; init; } = string.Empty;

            public string Root { get; init; } = string.Empty;

            public int Generation { get; set; }

            public bool Revoked { get; set; }
        }
    }
}

/// <summary>
/// AC-LSB-1/2/3/4/7 at the view-model layer: the REAL <see cref="ImportDockViewModel"/> over the
/// scripted port. The port counters are the "nothing runs before an explicit click" evidence; the
/// texts are the fail-closed/sanitization contract.
/// </summary>
public sealed class SourceRecoveryUiTests
{
    private const string SourcePath = @"C:\manga\secret\book.zip";

    private static void Pump() => Dispatcher.UIThread.RunJobs();

    private static (ImportDockViewModel ViewModel, List<(string Text, NmStatus Status)> Notices) Create(FakeHostController host)
    {
        var notices = new List<(string, NmStatus)>();
        var viewModel = new ImportDockViewModel(
            host,
            picker: null,
            notify: (text, status) => notices.Add((text, status)),
            chapterId: () => "ch-1",
            chapterTitle: () => "第 1 章",
            afterImport: () => Task.CompletedTask,
            requestCreateChapter: () => { },
            referencePollDelay: () => Task.CompletedTask);
        return (viewModel, notices);
    }

    private static SourcePlanPreview Plan() => new(
        "ch-1",
        "skip",
        "plan-1",
        "digest-1",
        new[] { "grant-1" },
        new[] { new SourcePlanItemView(0, "book.zip", "zip", "ok", 1, null, false) },
        new SourcePlanTotals(1, 0, 0, 0));

    private static IEnumerable<string> AllVisibleText(ImportDockViewModel viewModel) => new[]
    {
        viewModel.Summary,
        viewModel.ReferencePlanSummary,
        viewModel.ReferenceProgressText,
        viewModel.ReferenceErrorText,
        viewModel.RecoveryOfferText,
        viewModel.RecoveryOutcomeText,
        viewModel.RecoveryConfirmationText,
        viewModel.Title,
    }.Concat(viewModel.ReferencePlanItems.Select(row => row.StatusText + row.WillImportText + row.DisplayName))
     .Concat(viewModel.ReferenceReceiptItems.Select(row => row.SourceName + row.OutcomeText + row.CountsText));

    /// <summary>AC-LSB-1/2: a preview fails with the frozen registry code; nothing has been clicked yet.</summary>
    private static async Task<(FakeHostController Host, ImportDockViewModel ViewModel, List<(string Text, NmStatus Status)> Notices)>
        FailPreviewAsync(SourceRecoveryDiagnosis diagnosis)
    {
        var host = new FakeHostController(ReadySnapshot());
        host.Snapshot = host.Snapshot with { LastError = "SOURCE_REGISTRY_UNAVAILABLE" };
        host.ScriptedReferencePlans.Enqueue(null);
        host.ScriptedRecoveryDiagnoses.Enqueue(diagnosis);
        var (viewModel, notices) = Create(host);
        await viewModel.PlanReferenceImportAsync([new ReferenceImportSource(SourcePath, IsFolder: false)]);
        return (host, viewModel, notices);
    }

    [AvaloniaFact]
    public async Task FailedPreview_ExplicitReauthorize_OnlyOffersThatOneAction_AndWritesNothingYet()
    {
        var (host, viewModel, notices) = await FailPreviewAsync(
            SourceRecoveryDiagnosis.Reauthorize("SOURCE_REGISTRY_UNAVAILABLE", "book.zip", 2));

        // AC-LSB-1: the write-port counters are 0 — the failure branch ran the READ-ONLY probe only.
        Assert.Equal(1, host.SourceRecoveryDiagnoseCalls);
        Assert.Equal(0, host.SourceReauthorizeCalls);
        Assert.Equal(0, host.SourceResetCalls);
        Assert.Empty(host.SourceResetConfirms);

        // AC-LSB-2: exactly the diagnosed branch is offered.
        Assert.True(viewModel.HasSourceRecoveryAction);
        Assert.True(viewModel.OffersReauthorizeSource);
        Assert.False(viewModel.OffersResetSourceRegistry);
        Assert.True(viewModel.CanReauthorizeSource);
        Assert.Contains("book.zip", viewModel.RecoveryOfferText);
        Assert.Contains("2", viewModel.RecoveryOfferText);
        Assert.Contains("SOURCE_REGISTRY_UNAVAILABLE", viewModel.ReferenceErrorText);

        // AC-LSB-7: leaf name / typed code / counts only.
        Assert.DoesNotContain(@"C:\manga", string.Concat(AllVisibleText(viewModel)));
        Assert.DoesNotContain(@"C:\manga", string.Concat(notices.Select(notice => notice.Text)));
        Assert.DoesNotContain("quarantine", string.Concat(AllVisibleText(viewModel)), StringComparison.OrdinalIgnoreCase);
    }

    [AvaloniaFact]
    public async Task FailedPreview_FileLevel_OnlyOffersReset_AndStillWritesNothing()
    {
        var (host, viewModel, _) = await FailPreviewAsync(
            SourceRecoveryDiagnosis.Reset("SOURCE_REGISTRY_UNAVAILABLE"));

        Assert.True(viewModel.HasSourceRecoveryAction);
        Assert.True(viewModel.OffersResetSourceRegistry);
        Assert.False(viewModel.OffersReauthorizeSource);
        Assert.False(viewModel.CanConfirmResetSourceRegistry); // no confirmation pending yet
        Assert.Equal(0, host.SourceReauthorizeCalls);
        Assert.Equal(0, host.SourceResetCalls);
        Assert.Contains("全部来源", viewModel.RecoveryOfferText);
        Assert.DoesNotContain("quarantine", viewModel.RecoveryOfferText, StringComparison.OrdinalIgnoreCase);
    }

    [AvaloniaFact]
    public async Task FailedPreview_OtherTypedCode_OffersNoRecoveryActionAtAll()
    {
        var (host, viewModel, notices) = await FailPreviewAsync(
            SourceRecoveryDiagnosis.NotApplicable("CORE_CAPABILITY_MISSING"));

        Assert.False(viewModel.HasSourceRecoveryAction);
        Assert.Empty(viewModel.RecoveryOfferText);
        Assert.Contains("CORE_CAPABILITY_MISSING", viewModel.ReferenceErrorText);
        Assert.Equal(0, host.SourceReauthorizeCalls);
        Assert.Equal(0, host.SourceResetCalls);
        Assert.NotEmpty(notices);
    }

    [AvaloniaFact]
    public async Task ExplicitReauthorize_RunsOnce_ThenReplansThePreview()
    {
        var (host, viewModel, notices) = await FailPreviewAsync(
            SourceRecoveryDiagnosis.Reauthorize("SOURCE_REGISTRY_UNAVAILABLE", "book.zip", 2));
        host.ScriptedReauthorizeResults.Enqueue(new SourceRecoveryResult(
            true, null, SourceRecoveryText.ReauthorizeSucceeded(2, 1, "book.zip"), 2, 1, "book.zip"));
        host.ScriptedReferencePlans.Enqueue(Plan());

        await viewModel.ReauthorizeSourceAsync();

        Assert.Equal(1, host.SourceReauthorizeCalls);
        Assert.Equal(0, host.SourceResetCalls);
        Assert.Equal(string.Empty, viewModel.ReferenceErrorText);
        Assert.True(viewModel.HasReferencePlan);         // the same explicit action re-ran the preview
        Assert.Equal(2, host.ReferencePlanCalls.Count);  // failure + post-recovery preview
        Assert.False(viewModel.HasSourceRecoveryAction); // the offer is consumed
        Assert.Contains("已重新授权", viewModel.RecoveryOutcomeText);
        Assert.Contains("book.zip", viewModel.RecoveryOutcomeText);
        Assert.DoesNotContain(@"C:\manga", string.Concat(AllVisibleText(viewModel).Concat(notices.Select(n => n.Text))));
    }

    [AvaloniaFact]
    public async Task PartialFailure_ShowsRevokedNotReauthorized_AndStaysRetryable()
    {
        var (host, viewModel, _) = await FailPreviewAsync(
            SourceRecoveryDiagnosis.Reauthorize("SOURCE_REGISTRY_UNAVAILABLE", "book.zip", 2));
        host.ScriptedReauthorizeResults.Enqueue(new SourceRecoveryResult(
            false, "SOURCE_ACCESS_DENIED",
            SourceRecoveryText.RevokedNotRegistered(2, "SOURCE_ACCESS_DENIED"), 2, 0, "book.zip"));

        await viewModel.ReauthorizeSourceAsync();

        Assert.Contains("已撤销", viewModel.ReferenceErrorText);
        Assert.Contains("未重新授权", viewModel.ReferenceErrorText);
        Assert.Contains("SOURCE_ACCESS_DENIED", viewModel.ReferenceErrorText);
        Assert.Equal(SourceRecoveryText.RevokedNotRegistered(2, "SOURCE_ACCESS_DENIED"), viewModel.ReferenceErrorText);
        // AC-LSB-4: never reported as success and the explicit action stays available for a retry.
        Assert.True(viewModel.HasSourceRecoveryAction);
        Assert.True(viewModel.CanReauthorizeSource);
        Assert.Single(host.ReferencePlanCalls); // no preview on a partial outcome

        // retry → the same explicit action now completes and re-previews
        host.ScriptedReauthorizeResults.Enqueue(new SourceRecoveryResult(
            true, null, SourceRecoveryText.ReauthorizeSucceeded(0, 1, "book.zip"), 0, 1, "book.zip"));
        host.ScriptedReferencePlans.Enqueue(Plan());
        await viewModel.ReauthorizeSourceAsync();
        Assert.Equal(2, host.SourceReauthorizeCalls);
        Assert.True(viewModel.HasReferencePlan);
    }

    [AvaloniaFact]
    public async Task ResetRequiresASecondExplicitConfirmation_BeforeAnyResetCall()
    {
        var (host, viewModel, _) = await FailPreviewAsync(
            SourceRecoveryDiagnosis.Reset("SOURCE_REGISTRY_UNAVAILABLE"));

        viewModel.RequestResetSourceRegistry();
        Assert.True(viewModel.IsResetConfirmationPending);
        Assert.False(viewModel.CanReauthorizeSource);
        Assert.Equal(0, host.SourceResetCalls); // arming alone writes nothing

        viewModel.CancelResetSourceRegistry();
        Assert.False(viewModel.IsResetConfirmationPending);
        Assert.Equal(0, host.SourceResetCalls);

        viewModel.RequestResetSourceRegistry();
        host.ScriptedResetResults.Enqueue(new SourceRecoveryResult(
            true, null, SourceRecoveryText.ResetSucceeded(), 0, 0, null));
        await viewModel.ConfirmResetSourceRegistryAsync();

        Assert.Equal(1, host.SourceResetCalls);
        Assert.Equal(new[] { true }, host.SourceResetConfirms); // only the confirmed, explicit call
        Assert.False(viewModel.HasSourceRecoveryAction);
        Assert.Contains("已重置", viewModel.RecoveryOutcomeText);
        Assert.DoesNotContain("quarantine", string.Concat(AllVisibleText(viewModel)), StringComparison.OrdinalIgnoreCase);
    }

    [AvaloniaFact]
    public async Task ResetFailure_KeepsTheOffer_AndNeverRendersAQuarantinePath()
    {
        var (host, viewModel, _) = await FailPreviewAsync(
            SourceRecoveryDiagnosis.Reset("SOURCE_REGISTRY_UNAVAILABLE"));
        host.ScriptedResetResults.Enqueue(new SourceRecoveryResult(
            false, "SOURCE_REGISTRY_UNAVAILABLE",
            SourceRecoveryText.ResetFailed("SOURCE_REGISTRY_UNAVAILABLE"), 0, 0, null));

        viewModel.RequestResetSourceRegistry();
        await viewModel.ConfirmResetSourceRegistryAsync();

        Assert.Contains("重置源授权存储失败", viewModel.ReferenceErrorText);
        Assert.DoesNotContain("quarantine", string.Concat(AllVisibleText(viewModel)), StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain(@"C:\", string.Concat(AllVisibleText(viewModel)), StringComparison.Ordinal);
        Assert.True(viewModel.OffersResetSourceRegistry); // still the only safe action, still explicit
    }

    [AvaloniaFact]
    public async Task PreviewSuccess_ClearsAStaleRecoveryOffer()
    {
        var (host, viewModel, _) = await FailPreviewAsync(
            SourceRecoveryDiagnosis.Reauthorize("SOURCE_REGISTRY_UNAVAILABLE", "book.zip", 1));
        Assert.True(viewModel.HasSourceRecoveryAction);

        host.ScriptedReferencePlans.Enqueue(Plan());
        await viewModel.ReplanReferenceImportAsync();

        Assert.False(viewModel.HasSourceRecoveryAction);
        Assert.Empty(viewModel.RecoveryOfferText);
        Assert.Equal(0, host.SourceReauthorizeCalls);
        Assert.Equal(0, host.SourceResetCalls);
    }

    [AvaloniaFact]
    public async Task CloseDropsTheRecoveryOffer()
    {
        var (_, viewModel, _) = await FailPreviewAsync(
            SourceRecoveryDiagnosis.Reset("SOURCE_REGISTRY_UNAVAILABLE"));

        viewModel.Close();

        Assert.False(viewModel.HasSourceRecoveryAction);
        Assert.False(viewModel.IsResetConfirmationPending);
        Assert.Empty(viewModel.RecoveryOfferText);
    }

    [AvaloniaFact]
    public async Task View_RendersTheReauthorizeActionFromRealControls()
    {
        var (host, viewModel, _) = await FailPreviewAsync(
            SourceRecoveryDiagnosis.Reauthorize("SOURCE_REGISTRY_UNAVAILABLE", "book.zip", 2));
        var view = new ImportDockView { DataContext = viewModel };
        var window = new Window { Content = view };
        window.Show();
        Pump();

        var reauthorize = view.GetControl<Button>("ReauthorizeSourceButton");
        Assert.True(reauthorize.IsVisible);
        Assert.True(reauthorize.IsEnabled);

        host.ScriptedReauthorizeResults.Enqueue(new SourceRecoveryResult(
            true, null, SourceRecoveryText.ReauthorizeSucceeded(2, 1, "book.zip"), 2, 1, "book.zip"));
        host.ScriptedReferencePlans.Enqueue(Plan());
        reauthorize.Command!.Execute(null);
        Pump();
        await viewModel.ReauthorizeSourceAsync();

        Assert.Equal(1, host.SourceReauthorizeCalls);
        window.Close();
    }

    [AvaloniaFact]
    public async Task View_RendersTheResetConfirmationFromRealControls()
    {
        var (host, viewModel, _) = await FailPreviewAsync(
            SourceRecoveryDiagnosis.Reset("SOURCE_REGISTRY_UNAVAILABLE"));
        var view = new ImportDockView { DataContext = viewModel };
        var window = new Window { Content = view };
        window.Show();
        Pump();

        var requestReset = view.GetControl<Button>("RequestResetSourceRegistryButton");
        Assert.True(requestReset.IsVisible);
        requestReset.Command!.Execute(null);
        Pump();

        var confirm = view.GetControl<Button>("ConfirmResetSourceRegistryButton");
        Assert.True(confirm.IsVisible);
        host.ScriptedResetResults.Enqueue(new SourceRecoveryResult(
            true, null, SourceRecoveryText.ResetSucceeded(), 0, 0, null));
        confirm.Command!.Execute(null);
        Pump();
        await viewModel.ConfirmResetSourceRegistryAsync();

        Assert.Equal(1, host.SourceResetCalls);
        Assert.Contains(view.GetVisualDescendants().OfType<TextBlock>(), block =>
            (block.Text ?? string.Empty).Contains("已重置", StringComparison.Ordinal));
        window.Close();
    }
}
