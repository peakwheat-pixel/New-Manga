using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11-L-S4-B-1 (AC-SER-1…4): the execution face of an ENUMERATED scan target after a B1 explicit
/// re-authorization. B1 leaves the old registry entry revoked forever and registers ONE new entry over
/// the SAME path/physical identity, and L-S4-B re-attests the Core location row to the live pair. The
/// scan must then authorize the target with its OWN live <c>(registry_id, generation)</c> entry; the
/// path-exact resolver — which meets the sibling REVOKED row first and fails closed — stays the
/// authorization source for non-enumerated (SCAN-1 in-memory) targets only.
///
/// These fixtures run without a Core. <see cref="HostSourceScanExecutor.ScanAsync"/> reaches the grant
/// mint only when a real Core is attached (the closed loop over the real Python Core is proved by the
/// gated <c>Fea11ScanIpcTests.ReauthorizedSource_IsReattested_ThenEnumerated_WithoutReimport</c>), so
/// the null-Core fixtures stop exactly at that boundary. The boundary is itself the discriminator:
/// before the fix the recovered target returned <c>Error(SOURCE_ACCESS_DENIED)</c> from the second,
/// path-only resolution and never reached the mint at all.
/// </summary>
public sealed class SourceScanExecutionRecoveryTests
{
    private static readonly string ValidDigest = new('a', 64);

    private static SourceRoot RootFor(string path) => new(path, 1, 1, "2026-11-07T00:00:00Z", true);

    private static SourceAuthorization RegistryEntry(
        string registryId, string locator, string rootPath, int generation = 1, string? revokedAt = null) =>
        new(registryId, locator, generation, "2026-11-07T00:00:00Z", "2026-11-07T00:00:00Z", revokedAt,
            new[] { RootFor(rootPath) });

    private static SourceScanTarget EnumeratedTarget(
        string path, string registryId, int generation = 1, string sourceId = "src-1") =>
        new(sourceId, path, new[] { "b1" }, "1", registryId, generation, "zip", ValidDigest);

    private static SourceScanTarget InMemoryTarget(string path, string sourceId = "src-1") =>
        new(sourceId, path, new[] { "b1" }, "1");

    /// <summary>
    /// AC-SER-4: the registry STRUCTURE a scan may never change. The pre-existing <c>last_used_at</c>
    /// audit (written by <see cref="SourceAccessRegistry.Authorize"/> on a successful mint) is
    /// deliberately not part of it.
    /// </summary>
    private static string[] DescribeRegistryEntries(IReadOnlyList<SourceAuthorization> entries) =>
        entries.Select(entry =>
                entry.RegistryId + "|" + entry.Locator + "|" + entry.Generation + "|"
                + entry.CreatedAt + "|" + entry.RevokedAt + "|"
                + string.Join(";", entry.Roots.Select(root =>
                    root.Root + "|" + root.VolumeSerial + "|" + root.FileId)))
            .ToArray();

    private static (HostSourceScanExecutor Executor, SourceAccessRegistry Registry, string Root)
        ExecutorWithTempRegistry()
    {
        var root = Path.Combine(Path.GetTempPath(), "fea11-l-s4b1-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        var registry = new SourceAccessRegistry(root);
        var sources = new SourceReadCoordinator(null!, registry, () => true);
        var executor = new HostSourceScanExecutor(null!, sources, new SourceScanOptions());
        return (executor, registry, root);
    }

    private static string SeedFile(string root, byte fill = 4)
    {
        var file = Path.Combine(root, "book.zip");
        File.WriteAllBytes(file, new byte[fill]);
        return file;
    }

    private static void TryDeleteDirectory(string root)
    {
        try
        {
            if (Directory.Exists(root)) Directory.Delete(root, recursive: true);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            // isolated temp fixture expires with the OS temp directory
        }
    }

    // ---------------------------------------------------------------------------------------
    // AC-SER-1: the enumerated target is authorized by its OWN live entry (resolution matrix).
    // ---------------------------------------------------------------------------------------

    [Fact]
    public void SelectEnumeratedEntry_UsesTheTargetsOwnLiveEntry_WhenARevokedSiblingSharesThePath()
    {
        const string path = @"C:\fixtures\book.zip";
        var revokedOld = RegistryEntry(
            "reg-old", path, path, generation: 2, revokedAt: "2026-11-07T00:00:01Z");
        var liveNew = RegistryEntry("reg-live", path, path, generation: 1);
        var entries = new[] { revokedOld, liveNew };
        var target = EnumeratedTarget(path, "reg-live", generation: 1);

        // The exact state B1 + L-S4-B leave behind, and the pre-fix failure it used to hit: the
        // path-only resolver meets the revoked exact row first and returns null (never the live row),
        // so the executor reported Error(SOURCE_ACCESS_DENIED) although the target's own live entry
        // existed. This assertion is the "before" of the recovery (path-only resolution).
        Assert.Null(HostSourceScanExecutor.ResolveRegistryEntry(entries, path));

        var selected = HostSourceScanExecutor.SelectEnumeratedEntry(entries, target, out var verdict);
        Assert.Null(verdict);
        Assert.NotNull(selected);
        Assert.Equal("reg-live", selected!.RegistryId);
        Assert.Equal(1, selected.Generation);
        Assert.Null(selected.RevokedAt);
        Assert.Equal(path, selected.Roots[0].Root);
    }

    [Fact]
    public void SelectEnumeratedEntry_NeverFallsBackToALiveSibling_WhenTheTargetsOwnEntryIsRevoked()
    {
        const string path = @"C:\fixtures\book.zip";
        var revokedOwn = RegistryEntry(
            "reg-own", path, path, generation: 2, revokedAt: "2026-11-07T00:00:01Z");
        var liveSibling = RegistryEntry("reg-sibling", path, path, generation: 1);
        var entries = new[] { revokedOwn, liveSibling };
        var target = EnumeratedTarget(path, "reg-own", generation: 2);

        var selected = HostSourceScanExecutor.SelectEnumeratedEntry(entries, target, out var verdict);

        // Red line: a revoked target is NEVER auto-admitted through another same-path live entry.
        Assert.Null(selected);
        Assert.NotNull(verdict);
        Assert.Equal(SourceScanOutcomeKind.Skipped, verdict!.Kind);
        Assert.Equal("SOURCE_GRANT_REVOKED", verdict.ErrorCode);
    }

    [Fact]
    public void SelectEnumeratedEntry_IsTypedOnMissingRegistryAndGenerationDrift()
    {
        const string path = @"C:\fixtures\book.zip";
        var entries = new[] { RegistryEntry("reg-live", path, path, generation: 1) };

        var missing = HostSourceScanExecutor.SelectEnumeratedEntry(
            entries, EnumeratedTarget(path, "reg-missing"), out var missingVerdict);
        Assert.Null(missing);
        Assert.Equal(SourceScanOutcomeKind.Skipped, missingVerdict!.Kind);
        Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", missingVerdict.ErrorCode);

        var drifted = HostSourceScanExecutor.SelectEnumeratedEntry(
            entries, EnumeratedTarget(path, "reg-live", generation: 2), out var driftVerdict);
        Assert.Null(drifted);
        Assert.Equal(SourceScanOutcomeKind.Skipped, driftVerdict!.Kind);
        Assert.Equal("SOURCE_REGISTRY_BUSY", driftVerdict.ErrorCode);

        // The exact live pair stays a plain resolution (no typed verdict is fabricated).
        var exact = HostSourceScanExecutor.SelectEnumeratedEntry(
            entries, EnumeratedTarget(path, "reg-live", generation: 1), out var exactVerdict);
        Assert.Null(exactVerdict);
        Assert.NotNull(exact);
        Assert.Equal("reg-live", exact!.RegistryId);
    }

    // ---------------------------------------------------------------------------------------
    // AC-SER-1 + AC-SER-4: the executor no longer denies the recovered target, and the scan never
    // rewrites the registry structure (no auto authorization / no identity rebuild).
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task ScanAsync_RecoveredEnumeratedTarget_PassesTheAuthorizationGate_InsteadOfBeingDenied()
    {
        var (executor, registry, root) = ExecutorWithTempRegistry();
        try
        {
            var file = SeedFile(root);
            var revokedOld = registry.Register("fea11-l-s4b1", new[] { file });
            var revokedRow = registry.Revoke(revokedOld.RegistryId);
            var liveNew = registry.Register("fea11-l-s4b1-reauth", new[] { file });
            var entriesBefore = DescribeRegistryEntries(registry.List());
            var target = EnumeratedTarget(file, liveNew.RegistryId, liveNew.Generation);

            // The executor fixture has no Core, so a mint attempt can only abort at the capability
            // probe with a NullReferenceException; it can never return a scan outcome. Pre-fix the same
            // target returned Error(SOURCE_ACCESS_DENIED) from the path resolver BEFORE any mint.
            SourceScanOutcome? outcome = null;
            var error = await Record.ExceptionAsync(
                async () => outcome = await executor.ScanAsync(target, CancellationToken.None));

            Assert.Null(outcome);
            Assert.IsType<NullReferenceException>(error); // reached the (absent) Core mint boundary

            // AC-SER-4: nothing was authorized/registered/revoked/re-identified by the scan; the old
            // revoked row is still there (the pre-existing last_used_at audit is not even reached).
            Assert.Equal(entriesBefore, DescribeRegistryEntries(registry.List()));
            var stillRevoked = registry.List().Single(entry => entry.RegistryId == revokedOld.RegistryId);
            Assert.Equal(revokedRow.RevokedAt, stillRevoked.RevokedAt);
            Assert.Equal(revokedRow.Generation, stillRevoked.Generation);
            Assert.Equal(2, registry.List().Length);
        }
        finally
        {
            TryDeleteDirectory(root);
        }
    }

    // ---------------------------------------------------------------------------------------
    // AC-SER-2: the fail-closed matrix is unchanged (target's own registry).
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task ScanAsync_EnumeratedTarget_OwnRegistryRevokedMissingOrDrifted_IsTypedSkip()
    {
        var (executor, registry, root) = ExecutorWithTempRegistry();
        try
        {
            var file = SeedFile(root);
            var revoked = registry.Register("fea11-l-s4b1-revoked", new[] { file });
            var revokedRow = registry.Revoke(revoked.RegistryId);
            var live = registry.Register("fea11-l-s4b1-live", new[] { file });
            var entriesBefore = DescribeRegistryEntries(registry.List());

            var revokedOutcome = await executor.ScanAsync(
                EnumeratedTarget(file, revokedRow.RegistryId, revokedRow.Generation), CancellationToken.None);
            Assert.Equal(SourceScanOutcomeKind.Skipped, revokedOutcome.Kind);
            Assert.Equal("SOURCE_GRANT_REVOKED", revokedOutcome.ErrorCode);

            var missingOutcome = await executor.ScanAsync(
                EnumeratedTarget(file, "reg-not-registered", 1), CancellationToken.None);
            Assert.Equal(SourceScanOutcomeKind.Skipped, missingOutcome.Kind);
            Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", missingOutcome.ErrorCode);

            var driftedOutcome = await executor.ScanAsync(
                EnumeratedTarget(file, live.RegistryId, live.Generation + 7), CancellationToken.None);
            Assert.Equal(SourceScanOutcomeKind.Skipped, driftedOutcome.Kind);
            Assert.Equal("SOURCE_REGISTRY_BUSY", driftedOutcome.ErrorCode);

            // AC-SER-4: each typed skip is zero-write (no grant was minted, no entry touched).
            Assert.Equal(entriesBefore, DescribeRegistryEntries(registry.List()));
        }
        finally
        {
            TryDeleteDirectory(root);
        }
    }

    [Fact]
    public async Task ScanAsync_EnumeratedTarget_MissingOrReplacedRoot_IsRegistryUnavailable()
    {
        var (executor, registry, root) = ExecutorWithTempRegistry();
        try
        {
            var file = Path.Combine(root, "book.zip");
            await File.WriteAllBytesAsync(file, new byte[4]);
            var entry = registry.Register("fea11-l-s4b1", new[] { file });
            var entriesBefore = DescribeRegistryEntries(registry.List());
            var target = EnumeratedTarget(file, entry.RegistryId, entry.Generation);

            File.Delete(file); // cold start: the root vanished before this session verified it
            var missing = await executor.ScanAsync(target, CancellationToken.None);
            Assert.Equal(SourceScanOutcomeKind.Error, missing.Kind);
            Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", missing.ErrorCode);

            await File.WriteAllBytesAsync(file, new byte[4]); // same path, different physical file
            var replaced = await executor.ScanAsync(target, CancellationToken.None);
            Assert.Equal(SourceScanOutcomeKind.Error, replaced.Kind);
            Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", replaced.ErrorCode);

            // No identity was rebuilt from the replacement, no entry was rewritten.
            Assert.Equal(entriesBefore, DescribeRegistryEntries(registry.List()));
        }
        finally
        {
            TryDeleteDirectory(root);
        }
    }

    [Fact]
    public async Task ScanAsync_EnumeratedTarget_UnreadableRegistry_IsTypedFailClosed()
    {
        var (executor, registry, root) = ExecutorWithTempRegistry();
        try
        {
            var file = SeedFile(root);
            var entry = registry.Register("fea11-l-s4b1", new[] { file });
            var corrupted = new byte[] { 1, 2, 3 };
            File.WriteAllBytes(registry.RegistryPath, corrupted); // corrupt the registry file itself

            var outcome = await executor.ScanAsync(
                EnumeratedTarget(file, entry.RegistryId, entry.Generation), CancellationToken.None);

            // File-level corruption stays fail-closed: typed error, no grant, no ScanSourceSync frame
            // (with an absent Core any mint/frame attempt would throw instead of returning an outcome).
            Assert.Equal(SourceScanOutcomeKind.Error, outcome.Kind);
            Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", outcome.ErrorCode);
            // The unreadable file was not overwritten by an empty registry.
            Assert.Equal(corrupted, File.ReadAllBytes(registry.RegistryPath));
        }
        finally
        {
            TryDeleteDirectory(root);
        }
    }

    // ---------------------------------------------------------------------------------------
    // AC-SER-3: non-enumerated (SCAN-1 in-memory) targets keep the path resolver semantics.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task ScanAsync_NonEnumeratedTarget_KeepsThePathResolverSemantics()
    {
        var (executor, registry, root) = ExecutorWithTempRegistry();
        try
        {
            var file = SeedFile(root);
            var entry = registry.Register("fea11-l-s4b1", new[] { file });
            registry.Revoke(entry.RegistryId);

            // Same shape as the pre-existing resolver test: exact-first, revoked-exact -> null, and a
            // controlled containment fallback. Enumerated targets never use this resolver any more.
            const string fixtureRoot = @"C:\fixtures";
            const string exactFile = @"C:\fixtures\book.zip";
            var parent = RegistryEntry("reg-parent", fixtureRoot, fixtureRoot);
            var exact = RegistryEntry("reg-exact", exactFile, exactFile);
            Assert.Equal("reg-exact", HostSourceScanExecutor.ResolveRegistryEntry(
                new[] { parent, exact }, exactFile)!.RegistryId);
            Assert.Equal("reg-parent", HostSourceScanExecutor.ResolveRegistryEntry(
                new[] { parent }, exactFile)!.RegistryId);
            var revokedExact = exact with { RevokedAt = "2026-11-07T00:00:01Z" };
            Assert.Null(HostSourceScanExecutor.ResolveRegistryEntry(
                new[] { parent, revokedExact }, exactFile));

            // Executor level: an in-memory target whose path resolves to a revoked exact entry is the
            // unchanged typed failure (backoff error), not a skip and not a scan.
            var outcome = await executor.ScanAsync(InMemoryTarget(file), CancellationToken.None);
            Assert.Equal(SourceScanOutcomeKind.Error, outcome.Kind);
            Assert.Equal("SOURCE_ACCESS_DENIED", outcome.ErrorCode);
        }
        finally
        {
            TryDeleteDirectory(root);
        }
    }
}
