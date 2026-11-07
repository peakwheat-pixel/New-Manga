using System.Text.Json;
using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11-L-S4-B-2 (AC-RUN-1…5): the Run source-RANGE resolution of an ENUMERATED scan target after
/// a B1 explicit re-authorization (the old registry entry stays revoked forever + ONE new live entry
/// over the SAME path/physical identity + the Core location row re-attested to the live pair).
///
/// The Run range must authorize such a target by its OWN live <c>(registry_id, generation)</c> entry
/// (the resolver L-S4-B-1 shipped for the scan face), never by a second path-only resolution that a
/// same-path REVOKED sibling row would fail closed. Non-enumerated (SCAN-1 in-memory) targets keep the
/// unchanged path resolver, and every unprovable authorization is only counted as unresolved —
/// best-effort, never thrown. These are pure-function fixtures: no Core is started; the real-Core
/// closed loop is the gated <c>Fea11RunGrantIpcTests</c> case.
/// </summary>
public sealed class SourceRunRangeResolutionTests
{
    private static readonly JsonElement AllPages =
        JsonDocument.Parse("""{"kind":"page","page_id":"p1"}""").RootElement.Clone();

    private static SourceRoot RootFor(string path) => new(path, 1, 1, "2026-11-07T00:00:00Z", true);

    private static SourceAuthorization RegistryEntry(
        string registryId, string locator, string rootPath, int generation = 1, string? revokedAt = null) =>
        new(registryId, locator, generation, "2026-11-07T00:00:00Z", "2026-11-07T00:00:00Z", revokedAt,
            new[] { RootFor(rootPath) });

    /// <summary>Production shape of an enumerated target: live registry id/generation + Core kind.</summary>
    private static SourceScanTarget EnumeratedTarget(
        string sourceId,
        string path,
        string registryId,
        int generation = 1,
        string sourceKind = "zip") =>
        new(sourceId, path, new[] { "b1" }, "1", registryId, generation, sourceKind, new string('a', 64));

    /// <summary>SCAN-1 in-memory target: no registry identity (the path resolver is its authorization).</summary>
    private static SourceScanTarget InMemoryTarget(
        string sourceId, string path, string? sourceKind = null) =>
        new(sourceId, path, new[] { "b1" }, "1", SourceKind: sourceKind);

    private static SourceIdentityCache WarmCache(
        params (string SourceId, string Version, SourceIdentityEntry[] Entries)[] identities)
    {
        var cache = new SourceIdentityCache();
        foreach (var (sourceId, version, entries) in identities)
        {
            Assert.True(cache.Remember(sourceId, version, entries), "warm cache identity");
        }
        return cache;
    }

    private static RunSourceAuthorizer Authorizer(
        bool probe,
        IReadOnlyList<SourceScanTarget>? known,
        IReadOnlyList<SourceAuthorization>? entries,
        Func<IReadOnlyList<RunSourceScope>, string, JsonElement, CancellationToken, Task<RunAuthorizationResult>> authorize,
        List<string>? warnings = null,
        SourceIdentityCache? identities = null,
        Func<SourceScanTarget, CancellationToken, Task>? onDemandScan = null) =>
        new(true,
            () => known ?? Array.Empty<SourceScanTarget>(),
            () => entries ?? Array.Empty<SourceAuthorization>(),
            _ => Task.FromResult(probe),
            authorize,
            (_, _) => throw new InvalidOperationException("no run slice expected"),
            _ => { },
            message => warnings?.Add(message),
            identities ?? new SourceIdentityCache(),
            onDemandScan);

    private const string FixturePath = @"C:\fixtures\book.zip";

    // ---------------------------------------------------------------------------------------
    // AC-RUN-1: the enumerated target's Run range is authorized by its OWN live entry.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public void Resolve_EnumeratedTarget_UsesItsOwnLiveEntry_WhenARevokedSiblingSharesThePath()
    {
        var revokedOld = RegistryEntry(
            "reg-old", FixturePath, FixturePath, generation: 2, revokedAt: "2026-11-07T00:00:01Z");
        var liveNew = RegistryEntry("reg-live", FixturePath, FixturePath);
        var entries = new[] { revokedOld, liveNew };
        var target = EnumeratedTarget("s1", FixturePath, "reg-live");
        var cache = WarmCache(("s1", "sv-core-1",
            [new SourceIdentityEntry(null, "001.png", 0)]));

        // BEFORE: the pre-fix path-only resolution returns null (that is exactly why the old Run range
        // counted this source as unresolved even though its own live entry existed).
        Assert.Null(HostSourceScanExecutor.ResolveRegistryEntry(entries, FixturePath));

        var resolution = RunSourceRange.Resolve(new[] { target }, AllPages, entries, cache);

        var scope = Assert.Single(resolution.Targets);
        Assert.Equal(0, resolution.Unresolved);
        Assert.Empty(resolution.ColdSources);
        Assert.Equal("s1", scope.SourceId);
        Assert.Equal("reg-live", scope.RegistryId);
        Assert.Equal(1, scope.Generation);
        Assert.Equal("zip", scope.Kind);
        Assert.Equal("sv-core-1", scope.Version);
        Assert.Equal(FixturePath, scope.Path);
        // AC-RUN-1: the Core-authoritative container members still travel verbatim.
        Assert.NotNull(scope.ContainerEntries);
        Assert.Equal("001.png", Assert.Single(scope.ContainerEntries!).Locator);
    }

    [Fact]
    public void Resolve_EnumeratedTarget_NeverFallsBackToALiveSibling_WhenItsOwnEntryIsRevoked()
    {
        var revokedOwn = RegistryEntry(
            "reg-own", FixturePath, FixturePath, generation: 2, revokedAt: "2026-11-07T00:00:01Z");
        var liveSibling = RegistryEntry("reg-sibling", FixturePath, FixturePath);
        var target = EnumeratedTarget("s1", FixturePath, "reg-own", generation: 2);

        var resolution = RunSourceRange.Resolve(
            new[] { target }, AllPages, new[] { revokedOwn, liveSibling },
            WarmCache(("s1", "sv-core-1", [])));

        // AC-RUN-2 red line: a revoked target is NEVER auto-admitted through another same-path live
        // entry — it is unresolved and receives no grant.
        Assert.Empty(resolution.Targets);
        Assert.Equal(1, resolution.Unresolved);
        Assert.Empty(resolution.ColdSources);
    }

    [Fact]
    public void Resolve_EnumeratedTarget_IsUnresolved_OnMissingRegistryAndGenerationDrift()
    {
        var entries = new[] { RegistryEntry("reg-live", FixturePath, FixturePath) };

        var missing = RunSourceRange.Resolve(
            new[] { EnumeratedTarget("s1", FixturePath, "reg-missing") }, AllPages, entries,
            WarmCache(("s1", "sv-core-1", [])));
        Assert.Empty(missing.Targets);
        Assert.Equal(1, missing.Unresolved);
        Assert.Empty(missing.ColdSources);

        var drifted = RunSourceRange.Resolve(
            new[] { EnumeratedTarget("s1", FixturePath, "reg-live", generation: 2) }, AllPages, entries,
            WarmCache(("s1", "sv-core-1", [])));
        Assert.Empty(drifted.Targets);
        Assert.Equal(1, drifted.Unresolved);
        Assert.Empty(drifted.ColdSources);
    }

    [Fact]
    public void Resolve_DuplicateRegistryId_IsUnresolved_NotThrown()
    {
        // AC-RUN-5: SelectEnumeratedEntry uses SingleOrDefault; a duplicated id (impossible through the
        // registry's own Load validation, but possible for a synthetic snapshot) must degrade to
        // "unresolved", never to a thrown exception inside the best-effort Run authorization.
        var first = RegistryEntry("reg-live", FixturePath, FixturePath);
        var duplicate = RegistryEntry("reg-live", FixturePath, FixturePath);
        var target = EnumeratedTarget("s1", FixturePath, "reg-live");

        var resolution = RunSourceRange.Resolve(
            new[] { target }, AllPages, new[] { first, duplicate },
            WarmCache(("s1", "sv-core-1", [])));

        Assert.Empty(resolution.Targets);
        Assert.Equal(1, resolution.Unresolved);
    }

    // ---------------------------------------------------------------------------------------
    // AC-RUN-3: non-enumerated targets keep the unchanged path resolver.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public void Resolve_NonEnumeratedTarget_KeepsThePathOnlyResolver()
    {
        var revokedOld = RegistryEntry(
            "reg-old", FixturePath, FixturePath, generation: 2, revokedAt: "2026-11-07T00:00:01Z");
        var liveNew = RegistryEntry("reg-live", FixturePath, FixturePath);
        var entries = new[] { revokedOld, liveNew };

        // The path-only resolver (unchanged) fails closed on the revoked exact row: the same state that
        // RECOVERS an enumerated target must still leave an in-memory target unresolved.
        var inMemory = RunSourceRange.Resolve(
            new[] { InMemoryTarget("s1", FixturePath) }, AllPages, entries,
            WarmCache(("s1", "sv-core-1", [])));
        Assert.Empty(inMemory.Targets);
        Assert.Equal(1, inMemory.Unresolved);

        // Its existing exact-match semantics still resolve a plain live entry.
        var plain = RunSourceRange.Resolve(
            new[] { InMemoryTarget("s1", FixturePath) }, AllPages,
            new[] { RegistryEntry("reg-only", FixturePath, FixturePath) },
            WarmCache(("s1", "sv-core-1", [])));
        Assert.Equal("reg-only", Assert.Single(plain.Targets).RegistryId);
        Assert.Equal(0, plain.Unresolved);
    }

    // ---------------------------------------------------------------------------------------
    // AC-RUN-4: an enumerated live target with a cold Core identity is COLD (not unresolved) and the
    // authorizer fills it with exactly one bounded on-demand scan before minting.
    // ---------------------------------------------------------------------------------------

    [Fact]
    public void Resolve_EnumeratedColdSource_IsReportedAsCold_NotUnresolved()
    {
        var target = EnumeratedTarget("s1", FixturePath, "reg-live");

        var cold = RunSourceRange.Resolve(
            new[] { target }, AllPages, new[] { RegistryEntry("reg-live", FixturePath, FixturePath) },
            new SourceIdentityCache());

        Assert.Empty(cold.Targets);
        Assert.Equal(0, cold.Unresolved);        // it RESOLVED (own live entry) but has no version yet
        Assert.Equal("s1", Assert.Single(cold.ColdSources).SourceId);
    }

    [Fact]
    public async Task Authorizer_EnumeratedColdSource_PerformsOneOnDemandScan_ThenMints()
    {
        var target = EnumeratedTarget("s1", FixturePath, "reg-live");
        var cache = new SourceIdentityCache();
        var scans = new List<string>();
        var versions = new List<string>();
        var authorizer = Authorizer(
            probe: true,
            known: [target],
            entries: [RegistryEntry("reg-live", FixturePath, FixturePath)],
            authorize: (scopes, _, _, _) =>
            {
                var scope = Assert.Single(scopes);
                Assert.Equal("reg-live", scope.RegistryId);
                versions.Add(scope.Version);
                return Task.FromResult(new RunAuthorizationResult(1, 1, 0, []));
            },
            identities: cache,
            onDemandScan: (coldTarget, _) =>
            {
                scans.Add(coldTarget.SourceId);
                cache.Remember(coldTarget.SourceId, "sv-from-scan", []);
                return Task.CompletedTask;
            });

        await authorizer.AuthorizeSliceAsync("reocr_all", AllPages, CancellationToken.None);
        Assert.Equal(["s1"], scans);
        Assert.Equal(["sv-from-scan"], versions); // minted with the Core-authoritative version

        // Second slice: the cache is warm, so NO second on-demand scan is performed.
        await authorizer.AuthorizeSliceAsync("reocr_all", AllPages, CancellationToken.None);
        Assert.Equal(["s1"], scans);
        Assert.Equal(["sv-from-scan", "sv-from-scan"], versions);
    }

    [Fact]
    public async Task Authorizer_UnresolvedEnumeratedSource_NeverSendsAuthorizeSourceReadForRun()
    {
        var target = EnumeratedTarget("s1", FixturePath, "reg-own", generation: 2);
        var revokedOwn = RegistryEntry(
            "reg-own", FixturePath, FixturePath, generation: 2, revokedAt: "2026-11-07T00:00:01Z");
        var liveSibling = RegistryEntry("reg-sibling", FixturePath, FixturePath);
        var authorizeCalls = 0;
        var warnings = new List<string>();
        var authorizer = Authorizer(
            probe: true,
            known: [target],
            entries: [revokedOwn, liveSibling],
            authorize: (_, _, _, _) =>
            {
                authorizeCalls++;
                return Task.FromResult(new RunAuthorizationResult(1, 1, 0, []));
            },
            warnings: warnings,
            identities: new SourceIdentityCache());

        await authorizer.AuthorizeSliceAsync("reocr_all", AllPages, CancellationToken.None);

        Assert.Equal(0, authorizeCalls); // zero grants, zero AuthorizeSourceReadForRun frames
        Assert.Contains(warnings, message =>
            message.Contains("unresolved_sources=1", StringComparison.Ordinal));
    }

    // ---------------------------------------------------------------------------------------
    // AC-RUN-5: the resolution never writes the registry structure (real registry snapshot).
    // ---------------------------------------------------------------------------------------

    [Fact]
    public async Task Authorizer_ResolvedEnumeratedSource_LeavesRegistryStructureUntouched()
    {
        var root = Path.Combine(Path.GetTempPath(), "fea11-l-s4b2-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        try
        {
            var file = Path.Combine(root, "book.zip");
            await File.WriteAllBytesAsync(file, new byte[4]);
            var registry = new SourceAccessRegistry(root);
            var old = registry.Register("fea11-l-s4b2", new[] { file });
            var revokedRow = registry.Revoke(old.RegistryId);
            var live = registry.Register("fea11-l-s4b2-reauth", new[] { file });
            var target = EnumeratedTarget("s1", file, live.RegistryId);

            // Warm cache so the source resolves straight to a mintable scope.
            var cache = new SourceIdentityCache();
            Assert.True(cache.Remember("s1", "sv-core-1", []));
            var entriesBefore = DescribeRegistryEntries(registry.List());

            var authorizer = new RunSourceAuthorizer(
                true,
                () => [target],
                registry.List,
                _ => Task.FromResult(true),
                (scopes, _, _, _) =>
                {
                    Assert.Equal(live.RegistryId, Assert.Single(scopes).RegistryId);
                    return Task.FromResult(new RunAuthorizationResult(1, 1, 0, []));
                },
                (_, _) => throw new InvalidOperationException("no run slice expected"),
                _ => { },
                _ => { },
                cache);

            await authorizer.AuthorizeSliceAsync("reocr_all", AllPages, CancellationToken.None);
            var resolution = RunSourceRange.Resolve(
                new[] { target }, AllPages, registry.List(), cache);
            Assert.Equal(0, resolution.Unresolved);

            // AC-RUN-5: no registration/revocation/reset and no structural write happened; the old
            // revoked row is still there with its revoked_at/generation unchanged.
            Assert.Equal(entriesBefore, DescribeRegistryEntries(registry.List()));
            var stillRevoked = registry.List().Single(entry => entry.RegistryId == old.RegistryId);
            Assert.Equal(revokedRow.RevokedAt, stillRevoked.RevokedAt);
            Assert.Equal(revokedRow.Generation, stillRevoked.Generation);
            Assert.Equal(2, registry.List().Length);
        }
        finally
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
    }

    /// <summary>AC-RUN-5: registry STRUCTURE projection (the pre-existing last_used_at audit excluded).</summary>
    private static string[] DescribeRegistryEntries(IReadOnlyList<SourceAuthorization> entries) =>
        entries.Select(entry =>
                entry.RegistryId + "|" + entry.Locator + "|" + entry.Generation + "|"
                + entry.CreatedAt + "|" + entry.RevokedAt + "|"
                + string.Join(";", entry.Roots.Select(root =>
                    root.Root + "|" + root.VolumeSerial + "|" + root.FileId)))
            .ToArray();
}
