using System.Text.Json;
using NewManga.CoreClient;
using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11-L-S4-B (C-16 v1.5 §2.5/§0) Host evidence:
/// <list type="bullet">
/// <item>AC-LS4B-2: the <see cref="SourceRootReattestPlanner"/> candidate matrix — ONLY
/// "old entry revoked + exactly one root, exactly one live entry + exactly one root + equal
/// normalized path + equal (volume, file) identity + live.CreatedAt &gt; old.RevokedAt + non-folder"
/// becomes a candidate; every ambiguity/partial match stays a typed skip (no wire, no mint);</item>
/// <item>AC-LS4B-1: the enumerator NEVER sends/creates anything without the frozen
/// <c>source.reattest/1</c> capability (missing or probe failure), and the legacy constructor keeps
/// the pre-L-S4-B behaviour;</item>
/// <item>AC-LS4B-9: at most ONE re-attest attempt per source id per enumeration round (no retry
/// storm; a typed failure is final for that round).</item>
/// </list>
/// All planner tests are pure (no I/O); the enumerator tests inject the frozen seams so no Python
/// Core is started and no file is ever created by a refused attempt.
/// </summary>
public sealed class SourceReattestTests : IDisposable
{
    private const string SourceId = "src-11111111-1111-1111-1111-111111111111";
    private const string IdentityDigest = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    private readonly string _root;

    public SourceReattestTests()
    {
        _root = Path.Combine(
            RepoWorkspaceRoot(),
            "FEA-11-L-S4-B-AUTO-RECOVERY-1",
            "host-unit-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_root);
    }

    public void Dispose()
    {
        try
        {
            if (Directory.Exists(_root)) Directory.Delete(_root, recursive: true);
        }
        catch (IOException)
        {
        }
        catch (UnauthorizedAccessException)
        {
        }
    }

    private static string RepoWorkspaceRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
        {
            directory = directory.Parent;
        }

        var repo = directory?.FullName ?? throw new InvalidOperationException("repository not found");
        var workspace = repo + ".workspace";
        Directory.CreateDirectory(workspace);
        return workspace;
    }

    // ------------------------------------------------------------------
    // AC-LS4B-2: the exact candidate matrix (pure)
    // ------------------------------------------------------------------

    private const string BookZip = @"C:\fixtures\book.zip";

    private static string Iso(DateTimeOffset value) => value.ToString("O");

    private static SourceAuthorization Entry(
        string registryId,
        string path = BookZip,
        string? revokedAt = null,
        string? createdAt = null,
        ulong volume = 7,
        ulong fileId = 8,
        params string[] extraRoots)
    {
        var now = DateTimeOffset.UtcNow;
        var roots = new List<SourceRoot>
        {
            new(path, volume, fileId, Iso(now), true),
        };
        roots.AddRange(extraRoots.Select(root => new SourceRoot(root, volume, fileId, Iso(now), true)));
        return new SourceAuthorization(
            registryId, path, 1,
            createdAt ?? Iso(now.AddMinutes(-10)),
            createdAt ?? Iso(now.AddMinutes(-10)),
            revokedAt,
            roots.ToArray());
    }

    private static JsonElement Target(
        string registryId = "reg-old",
        int generation = 1,
        string kind = "zip",
        string sourceId = SourceId,
        string identityDigest = IdentityDigest,
        string[]? projectIds = null)
    {
        var payload = new
        {
            source_id = sourceId,
            registry_id = registryId,
            generation,
            source_kind = kind,
            identity_digest = identityDigest,
            project_ids = projectIds ?? new[] { "b1" },
        };
        return JsonDocument.Parse(JsonSerializer.Serialize(payload)).RootElement.Clone();
    }

    private static SourceRootReattestDecision Plan(
        JsonElement target, params SourceAuthorization[] entries) =>
        SourceRootReattestPlanner.Plan(target, entries);

    [Fact]
    public void Plan_ExactRevokedThenReauthorizedEntry_IsACandidate()
    {
        var revokedAt = DateTimeOffset.UtcNow.AddMinutes(-5);
        var old = Entry("reg-old", revokedAt: Iso(revokedAt));
        var live = Entry("reg-new", createdAt: Iso(revokedAt.AddMinutes(1)));

        var decision = Plan(Target(), old, live);

        Assert.True(decision.IsCandidate, decision.Reason);
        var candidate = decision.Candidate!;
        Assert.Equal(SourceId, candidate.SourceId);
        Assert.Equal("zip", candidate.Kind);
        Assert.Equal("reg-new", candidate.LiveRegistryId);
        Assert.Equal(1, candidate.LiveGeneration);
        Assert.Equal(BookZip, candidate.LiveRoot);
        Assert.Equal("reg-old", candidate.CoreRegistryId);
        Assert.Equal(1, candidate.CoreGeneration);
        // The witness grant reuses the same frozen placeholder the scan path mints
        // for an enumerated target; ReattestSourceLocation never reads it.
        Assert.Equal("1", candidate.Version);
        // Never leak the path in text/status.
        Assert.DoesNotContain(BookZip, candidate.ToString(), StringComparison.Ordinal);
    }

    [Fact]
    public void Plan_NormalizedPathEquality_IsWhatMatches()
    {
        var revokedAt = DateTimeOffset.UtcNow.AddMinutes(-5);
        // A trailing separator normalizes to the same fully qualified path (the
        // registry persists only normalized roots; this pins the comparison).
        var old = Entry("reg-old", path: BookZip + @"\", revokedAt: Iso(revokedAt));
        var live = Entry("reg-new", path: BookZip, createdAt: Iso(revokedAt.AddMinutes(1)));

        var decision = Plan(Target(), old, live);

        Assert.True(decision.IsCandidate, decision.Reason);
        Assert.Equal(BookZip, decision.Candidate!.LiveRoot);
    }

    [Theory]
    [InlineData("folder")]
    [InlineData("image")]
    public void Plan_OnlyNonFolderKindsCanBeCandidates(string kind)
    {
        var revokedAt = DateTimeOffset.UtcNow.AddMinutes(-5);
        var old = Entry("reg-old", revokedAt: Iso(revokedAt));
        var live = Entry("reg-new", createdAt: Iso(revokedAt.AddMinutes(1)));

        var decision = Plan(Target(kind: kind), old, live);

        if (kind == "folder")
        {
            Assert.False(decision.IsCandidate);
            Assert.Equal("folder-source", decision.Reason);
        }
        else
        {
            Assert.True(decision.IsCandidate, decision.Reason);
        }
    }

    [Fact]
    public void Plan_OldEntryMissing_IsSkipped()
    {
        var live = Entry("reg-new");
        var decision = Plan(Target(registryId: "reg-gone"), live);
        Assert.False(decision.IsCandidate);
        Assert.Equal("old-entry-missing", decision.Reason);
    }

    [Fact]
    public void Plan_LiveRecordedEntry_IsNotTheGap_AndIsNeverReattested()
    {
        var old = Entry("reg-old"); // NOT revoked
        var live = Entry("reg-new");
        var decision = Plan(Target(), old, live);
        Assert.False(decision.IsCandidate);
        Assert.Equal("old-entry-live", decision.Reason);
    }

    [Fact]
    public void Plan_OldEntryWithMultipleRoots_IsSkipped()
    {
        var revokedAt = DateTimeOffset.UtcNow.AddMinutes(-5);
        var old = Entry("reg-old", revokedAt: Iso(revokedAt), extraRoots: @"C:\fixtures\other.zip");
        var live = Entry("reg-new", createdAt: Iso(revokedAt.AddMinutes(1)));
        var decision = Plan(Target(), old, live);
        Assert.False(decision.IsCandidate);
        Assert.Equal("old-entry-multiple-roots", decision.Reason);
    }

    [Fact]
    public void Plan_NoLiveEntry_IsSkipped()
    {
        var old = Entry("reg-old", revokedAt: Iso(DateTimeOffset.UtcNow.AddMinutes(-5)));
        var decision = Plan(Target(), old);
        Assert.False(decision.IsCandidate);
        Assert.Equal("no-live-entry", decision.Reason);
    }

    [Fact]
    public void Plan_TwoLiveEntries_AreAmbiguous_AndAreSkipped()
    {
        var revokedAt = DateTimeOffset.UtcNow.AddMinutes(-10);
        var old = Entry("reg-old", revokedAt: Iso(revokedAt));
        var first = Entry("reg-new-1", createdAt: Iso(revokedAt.AddMinutes(1)));
        var second = Entry("reg-new-2", createdAt: Iso(revokedAt.AddMinutes(2)));
        var decision = Plan(Target(), old, first, second);
        Assert.False(decision.IsCandidate);
        Assert.Equal("ambiguous-live-entries", decision.Reason);
    }

    [Fact]
    public void Plan_PathMismatch_IsSkipped()
    {
        var revokedAt = DateTimeOffset.UtcNow.AddMinutes(-5);
        var old = Entry("reg-old", revokedAt: Iso(revokedAt));
        var live = Entry("reg-new", path: @"C:\fixtures\replaced.zip", createdAt: Iso(revokedAt.AddMinutes(1)));
        var decision = Plan(Target(), old, live);
        Assert.False(decision.IsCandidate);
        Assert.Equal("no-live-entry", decision.Reason);
    }

    [Theory]
    [InlineData(7UL, 9UL)]
    [InlineData(8UL, 8UL)]
    public void Plan_VolumeFileIdentityMismatch_IsSkipped(ulong liveVolume, ulong liveFileId)
    {
        var revokedAt = DateTimeOffset.UtcNow.AddMinutes(-5);
        var old = Entry("reg-old", volume: 7, fileId: 8, revokedAt: Iso(revokedAt));
        var live = Entry(
            "reg-new",
            volume: liveVolume,
            fileId: liveFileId,
            createdAt: Iso(revokedAt.AddMinutes(1)));
        var decision = Plan(Target(), old, live);
        Assert.False(decision.IsCandidate);
        Assert.Equal("no-live-entry", decision.Reason);
    }

    [Fact]
    public void Plan_LiveEntryWithMultipleRoots_IsSkipped()
    {
        var revokedAt = DateTimeOffset.UtcNow.AddMinutes(-5);
        var old = Entry("reg-old", revokedAt: Iso(revokedAt));
        var live = Entry(
            "reg-new", createdAt: Iso(revokedAt.AddMinutes(1)), extraRoots: @"C:\fixtures\second.zip");
        var decision = Plan(Target(), old, live);
        Assert.False(decision.IsCandidate);
        Assert.Equal("no-live-entry", decision.Reason);
    }

    [Fact]
    public void Plan_HistoricalDuplicateCreatedBeforeTheRevoke_IsSkipped()
    {
        var revokedAt = DateTimeOffset.UtcNow.AddMinutes(-1);
        var old = Entry("reg-old", revokedAt: Iso(revokedAt));
        var historical = Entry("reg-new", createdAt: Iso(revokedAt.AddMinutes(-30)));
        var decision = Plan(Target(), old, historical);
        Assert.False(decision.IsCandidate);
        Assert.Equal("time-order-invalid", decision.Reason);
    }

    [Fact]
    public void Plan_UnparsableTimestamps_AreSkipped()
    {
        var old = Entry("reg-old", revokedAt: "not-a-timestamp");
        var live = Entry("reg-new");
        var decision = Plan(Target(), old, live);
        Assert.False(decision.IsCandidate);
        Assert.Equal("invalid-timestamps", decision.Reason);
    }

    [Theory]
    [InlineData("unknown-kind")]
    [InlineData("bad-identity")]
    [InlineData("zero-generation")]
    [InlineData("too-many-projects")]
    public void Plan_MalformedTargets_AreSkipped(string caseName)
    {
        var revokedAt = DateTimeOffset.UtcNow.AddMinutes(-5);
        var old = Entry("reg-old", revokedAt: Iso(revokedAt));
        var live = Entry("reg-new", createdAt: Iso(revokedAt.AddMinutes(1)));
        var target = caseName switch
        {
            "unknown-kind" => Target(kind: "rar"),
            "bad-identity" => Target(identityDigest: "ZZZ"),
            "zero-generation" => Target(generation: 0),
            _ => Target(projectIds: Enumerable.Range(0, 21).Select(index => "b" + index).ToArray()),
        };
        var decision = Plan(target, old, live);
        Assert.False(decision.IsCandidate);
        Assert.Equal("malformed-target", decision.Reason);
    }

    // ------------------------------------------------------------------
    // AC-LS4B-1/9: the enumerator capability gate + one attempt per round
    // ------------------------------------------------------------------

    private sealed class MutableRegistryState
    {
        public required SourceAccessRegistry Registry { get; init; }
        public required string OldRegistryId { get; init; }
        public required int OldGeneration { get; init; }
        public required string LiveRegistryId { get; init; }
        public required string SourcePath { get; init; }
    }

    private MutableRegistryState SeedRevokedThenReauthorizedRegistry()
    {
        var sourcePath = Path.Combine(_root, "book.zip");
        File.WriteAllBytes(sourcePath, new byte[] { 1, 2, 3, 4 });
        var registry = new SourceAccessRegistry(_root);
        var old = registry.Register("fea11-l-s4b", new[] { sourcePath });
        registry.Revoke(old.RegistryId);
        var live = registry.Register("fea11-l-s4b", new[] { sourcePath });
        return new MutableRegistryState
        {
            Registry = registry,
            OldRegistryId = old.RegistryId,
            OldGeneration = old.Generation,
            LiveRegistryId = live.RegistryId,
            SourcePath = sourcePath,
        };
    }

    private static JsonElement TargetsJson(string sourceId, string registryId, int generation)
    {
        var payload = new
        {
            targets = new[]
            {
                new
                {
                    source_id = sourceId,
                    registry_id = registryId,
                    generation,
                    source_kind = "zip",
                    identity_digest = IdentityDigest,
                    project_ids = new[] { "b1" },
                },
            },
        };
        return JsonDocument.Parse(JsonSerializer.Serialize(payload)).RootElement.Clone();
    }

    private static JsonElement TargetsJson(params Dictionary<string, object>[] targets)
    {
        var payload = new { targets };
        return JsonDocument.Parse(JsonSerializer.Serialize(payload)).RootElement.Clone();
    }

    [Fact]
    public async Task Enumerator_MissingCapability_SendsNothing_AndKeepsTheTypedSkip()
    {
        var seeded = SeedRevokedThenReauthorizedRegistry();
        var targets = TargetsJson(SourceId, seeded.OldRegistryId, seeded.OldGeneration);
        var sources = new SourceReadCoordinator(null!, seeded.Registry, () => true);
        var warnings = new List<string>();
        var enumerator = new HostSourceScanTargetEnumerator(
            core: null!,
            registry: seeded.Registry,
            sources: sources,
            options: new SourceScanOptions(),
            listTargets: _ => Task.FromResult(targets),
            reattestCapability: _ => Task.FromResult(false),
            warnLog: warnings.Add);

        var result = await enumerator.EnumerateAsync(CancellationToken.None);

        Assert.True(result.Ok);
        Assert.Empty(result.Targets);
        Assert.Equal(1, result.Skipped);
        // The capability gate runs before mint/send: no file, no grant, no warning about an attempt.
        Assert.Empty(warnings);
    }

    [Fact]
    public async Task Enumerator_CapabilityProbeFailure_IsTreatedAsMissing()
    {
        var seeded = SeedRevokedThenReauthorizedRegistry();
        var targets = TargetsJson(SourceId, seeded.OldRegistryId, seeded.OldGeneration);
        var sources = new SourceReadCoordinator(null!, seeded.Registry, () => true);
        var warnings = new List<string>();
        var enumerator = new HostSourceScanTargetEnumerator(
            core: null!,
            registry: seeded.Registry,
            sources: sources,
            options: new SourceScanOptions(),
            listTargets: _ => Task.FromResult(targets),
            reattestCapability: _ => Task.FromException<bool>(
                new InvalidOperationException("probe failed")),
            warnLog: warnings.Add);

        var result = await enumerator.EnumerateAsync(CancellationToken.None);

        Assert.True(result.Ok);
        Assert.Empty(result.Targets);
        Assert.Equal(1, result.Skipped);
        Assert.Single(warnings);
        Assert.Contains("capability probe failed", warnings[0], StringComparison.Ordinal);
    }

    [Fact]
    public async Task Enumerator_AttemptsEachSourceAtMostOncePerRound()
    {
        var seeded = SeedRevokedThenReauthorizedRegistry();
        // The SAME source id appears twice (the Core never does this; it proves the guard).
        var targets = TargetsJson(
            new Dictionary<string, object>
            {
                ["source_id"] = SourceId,
                ["registry_id"] = seeded.OldRegistryId,
                ["generation"] = seeded.OldGeneration,
                ["source_kind"] = "zip",
                ["identity_digest"] = IdentityDigest,
                ["project_ids"] = new[] { "b1" },
            },
            new Dictionary<string, object>
            {
                ["source_id"] = SourceId,
                ["registry_id"] = seeded.OldRegistryId,
                ["generation"] = seeded.OldGeneration,
                ["source_kind"] = "zip",
                ["identity_digest"] = IdentityDigest,
                ["project_ids"] = new[] { "b1" },
            });
        var sources = new SourceReadCoordinator(null!, seeded.Registry, () => true);
        var warnings = new List<string>();
        var enumerator = new HostSourceScanTargetEnumerator(
            core: null!,
            registry: seeded.Registry,
            sources: sources,
            options: new SourceScanOptions(),
            listTargets: _ => Task.FromResult(targets),
            reattestCapability: _ => Task.FromResult(true),
            warnLog: warnings.Add);

        var result = await enumerator.EnumerateAsync(CancellationToken.None);

        // The real coordinator is bound to a null Core, so the ONE attempted send fails typed and
        // the target keeps its skip; TWO entries for the same source must still produce ONE attempt.
        Assert.True(result.Ok);
        Assert.Empty(result.Targets);
        Assert.Single(warnings);
        Assert.Contains("reattest skipped", warnings[0], StringComparison.Ordinal);
        // No retry storm: a single enumeration round never re-reads targets after a failed send.
        Assert.DoesNotContain(warnings, line => line.Contains("pre-pass failed", StringComparison.Ordinal));
    }

    [Fact]
    public async Task LegacyConstructor_WithTwoArguments_KeepsThePreLS4BBehaviour()
    {
        var seeded = SeedRevokedThenReauthorizedRegistry();
        var targets = TargetsJson(SourceId, seeded.OldRegistryId, seeded.OldGeneration);
        var enumerator = new HostSourceScanTargetEnumerator(
            core: null!,
            registry: seeded.Registry,
            listTargets: _ => Task.FromResult(targets));

        var result = await enumerator.EnumerateAsync(CancellationToken.None);

        Assert.True(result.Ok);
        Assert.Empty(result.Targets);
        Assert.Equal(1, result.Skipped);
    }

    [Fact]
    public void TryMap_StillMapsAnExactlyAuthorizedTarget()
    {
        var sealedAt = DateTimeOffset.UtcNow;
        var entry = Entry("reg-live", createdAt: Iso(sealedAt));
        var entries = new Dictionary<string, SourceAuthorization>(StringComparer.Ordinal)
        {
            [entry.RegistryId] = entry,
        };
        var target = Target(registryId: "reg-live");

        Assert.True(HostSourceScanTargetEnumerator.TryMap(target, entries, out var mapped));
        Assert.Equal(SourceId, mapped.SourceId);
        Assert.Equal(BookZip, mapped.Path);
        Assert.Equal("reg-live", mapped.RegistryId);
        Assert.Equal(1, mapped.Generation);
        Assert.Equal("zip", mapped.SourceKind);
        Assert.Equal(IdentityDigest, mapped.IdentityDigest);
        Assert.True(mapped.IsEnumerated);
    }
}
