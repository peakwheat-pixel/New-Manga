using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using NewManga.CoreClient;
using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11-L-S1-REGISTRY-RESILIENCE-1 (frozen card; C-15 v1.5 §5 Registry state machine split).
///
/// A registered ROOT that is currently missing / unreadable / replaced (volume+file identity no
/// longer matches) is NO LONGER whole-file corruption:
///
/// * <see cref="SourceAccessRegistry.Load"/> validates the FILE only (magic/version/length/DPAPI/
///   JSON/persisted entry structure) — one unavailable root no longer makes every entry unreadable;
/// * <see cref="SourceAccessRegistry.List"/> still returns every entry (derived unavailability, no
///   new persisted field, entries are never dropped or rewritten);
/// * <see cref="SourceAccessRegistry.Authorize"/> re-verifies the requested path's root PER REQUEST
///   inside the same lock/after the fresh read: unavailable/mismatched → that request's typed
///   <c>SOURCE_REGISTRY_UNAVAILABLE</c> with ZERO writes; a missing root is never "no authorization"
///   and never falls back to a parent/other root; no automatic identity rebuild / re-authorization /
///   recovery (explicit <c>source_reset_registry</c> stays the only recovery, and only for file-level
///   corruption);
/// * the file-level corruption path is unchanged: fail-closed, <c>.corrupt-&lt;utc&gt;</c> copy,
///   original bytes preserved, no empty registry created.
///
/// Discrimination: deleting the per-request identity verification (leaving only the Load deletion)
/// makes <see cref="ReplacedRoot_AuthorizeIsTypedAndPersistsNoNewIdentity"/> and
/// <see cref="MissingRoot_AuthorizeIsTypedAndWritesNothing"/> red; dropping the unavailable entry from
/// the projection makes the mixed-registry cases red; widening a file-level check makes
/// <see cref="FileLevelCorruptionStaysWholeFileFailClosed"/> red.
/// </summary>
public sealed class SourceRegistryResilienceTests
{
    private const string Magic = "NMSAR1\0";

    // ======================================================================================
    // AC-L2 / AC-L1: mixed registry (healthy + missing root) is readable, the unavailable entry
    // is kept, and unrelated commands (new registration) are no longer blocked.
    // ======================================================================================

    [Fact]
    public void MixedRegistry_ListReturnsEveryEntryIncludingTheUnavailableOne()
    {
        using var fixture = new RegistryFixture();
        var healthy = fixture.RegisterFile("healthy");
        var missing = fixture.RegisterFile("missing");
        File.Delete(missing.File); // the referenced source vanished; the registered ROOT stays

        var before = fixture.RegistryBytes;
        var listed = fixture.Registry.List();

        Assert.Equal(2, listed.Length);
        Assert.Equal(
            [healthy.Entry.RegistryId, missing.Entry.RegistryId],
            listed.Select(entry => entry.RegistryId));
        var kept = listed.Single(entry => entry.RegistryId == missing.Entry.RegistryId);
        Assert.Equal(missing.File, Assert.Single(kept.Roots).Root); // not deleted / not rewritten
        Assert.Equal(missing.Entry.Generation, kept.Generation);
        Assert.Null(kept.RevokedAt);
        Assert.Equal(before, fixture.RegistryBytes); // List is a read-only projection

        // AC-L2: a new registration (the import-unblock command) succeeds although another root
        // in the same file is currently unavailable.
        var fresh = fixture.Registry.Register("fresh", [fixture.NewDirectory("fresh")]);
        Assert.Equal(1, fresh.Generation);
        Assert.Equal(3, fixture.Registry.List().Length);
    }

    [Fact]
    public void MixedRegistry_HealthyRootAuthorizeSucceedsAndOnlyPersistsItsLastUse()
    {
        using var fixture = new RegistryFixture();
        var healthy = fixture.RegisterFile("healthy");
        var missing = fixture.RegisterFile("missing");
        File.Delete(missing.File);

        var authorized = fixture.Registry.Authorize(
            healthy.Entry.RegistryId, healthy.Entry.Generation, [healthy.File]);
        Assert.Equal(1, authorized.Generation);
        Assert.NotEqual(healthy.Entry.LastUsedAt, authorized.LastUsedAt);

        // The persisted state advanced for the healthy entry only; the unavailable entry was neither
        // dropped nor touched (its last_used_at is still the registration timestamp).
        var listed = fixture.Registry.List();
        Assert.Equal(authorized.LastUsedAt,
            listed.Single(e => e.RegistryId == healthy.Entry.RegistryId).LastUsedAt);
        var missingEntry = listed.Single(e => e.RegistryId == missing.Entry.RegistryId);
        Assert.Equal(missingEntry.CreatedAt, missingEntry.LastUsedAt);
    }

    // ======================================================================================
    // AC-L1 / AC-L3: a missing root is a per-request typed refusal with zero writes; it is not
    // file-level corruption (no `.corrupt-*` copy) and not a silent deny-all/allow-all.
    // ======================================================================================

    [Fact]
    public void MissingRoot_AuthorizeIsTypedAndWritesNothing()
    {
        using var fixture = new RegistryFixture();
        var healthy = fixture.RegisterFile("healthy");
        var missing = fixture.RegisterFile("missing");
        File.Delete(missing.File);

        var before = fixture.RegistryBytes;
        var corruptCopiesBefore = fixture.CorruptCopyCount();

        var error = Assert.Throws<SourceAccessException>(
            () => fixture.Registry.Authorize(
                missing.Entry.RegistryId, missing.Entry.Generation, [missing.File]));
        Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", error.Code); // frozen code: zero new error codes
        Assert.Equal(before, fixture.RegistryBytes);             // zero persistence on refusal
        Assert.Equal(corruptCopiesBefore, fixture.CorruptCopyCount()); // root-level != file-level

        // The healthy sibling root in the SAME registry file is unaffected.
        Assert.Equal(1, fixture.Registry.Authorize(
            healthy.Entry.RegistryId, healthy.Entry.Generation, [healthy.File]).Generation);
        Assert.Equal(2, fixture.Registry.List().Length); // still not dropped by the refusal
    }

    [Fact]
    public void MissingRoot_NeverAuthorizesAnyPathAndContainmentStaysExact()
    {
        using var fixture = new RegistryFixture();
        var healthy = fixture.RegisterFile("healthy");
        var missing = fixture.RegisterFile("missing");
        File.Delete(missing.File);

        // A vanished root is a typed refusal — never "no roots, therefore allow".
        Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", Assert.Throws<SourceAccessException>(
            () => fixture.Registry.Authorize(missing.Entry.RegistryId, 1, [missing.File])).Code);

        // Path outside every registered root: denied (no fallback to a parent/other root).
        var outside = Path.Combine(fixture.NewDirectory("outside"), "page.txt");
        File.WriteAllText(outside, "outsider");
        Assert.Equal("SOURCE_ACCESS_DENIED", Assert.Throws<SourceAccessException>(
            () => fixture.Registry.Authorize(healthy.Entry.RegistryId, 1, [outside])).Code);

        // Prefix sibling: "<root>-evil\page.txt" is NOT inside "<root>".
        var siblingDirectory = healthy.File + "-evil";
        Directory.CreateDirectory(siblingDirectory);
        var sibling = Path.Combine(siblingDirectory, "page.txt");
        File.WriteAllText(sibling, "sibling");
        Assert.Equal("SOURCE_ACCESS_DENIED", Assert.Throws<SourceAccessException>(
            () => fixture.Registry.Authorize(healthy.Entry.RegistryId, 1, [sibling])).Code);

        // Traversal / relative paths are rejected by normalization (never resolved against a root).
        Assert.Equal("SOURCE_ACCESS_DENIED", Assert.Throws<SourceAccessException>(
            () => fixture.Registry.Authorize(
                healthy.Entry.RegistryId, 1, [healthy.File + "\\..\\..\\outside.txt"])).Code);
        Assert.Equal("SOURCE_ACCESS_DENIED", Assert.Throws<SourceAccessException>(
            () => fixture.Registry.Authorize(healthy.Entry.RegistryId, 1, ["relative\\page.txt"])).Code);
    }

    // ======================================================================================
    // AC-L3 (security core) / AC-L4: a REPLACED root (persisted identity != current identity) is
    // refused per request, the persisted identity is never rebuilt and the entry stays listed.
    // ======================================================================================

    [Fact]
    public void ReplacedRoot_AuthorizeIsTypedAndPersistsNoNewIdentity()
    {
        using var fixture = new RegistryFixture(new PassthroughProtector());
        var healthy = fixture.RegisterFile("healthy");
        var replaced = fixture.RegisterFile("replaced");

        // Deterministic stand-in for "same path, different physical file": NTFS may recycle file ids
        // after re-create (review R4 flaky risk), so the mismatch is written on the registry side —
        // exactly the state a replacement leaves behind (registered identity != current identity).
        const ulong Volume = 0xDEADBEEF;
        const ulong FileId = 0x0123456789ABCDEF;
        RewriteRootIdentity(fixture.Registry.RegistryPath, replaced.Entry.RegistryId, Volume, FileId);

        var before = fixture.RegistryBytes;
        var error = Assert.Throws<SourceAccessException>(
            () => fixture.Registry.Authorize(
                replaced.Entry.RegistryId, replaced.Entry.Generation, [replaced.File]));
        Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", error.Code);
        Assert.Equal(before, fixture.RegistryBytes); // no identity write-back, no re-authorization

        // AC-L4: no automatic identity rebuild — the persisted (mismatched) identity is untouched.
        Assert.Equal((Volume, FileId),
            ReadRootIdentity(fixture.Registry.RegistryPath, replaced.Entry.RegistryId));

        // The entry is still listed and the healthy sibling keeps authorizing.
        Assert.Equal(2, fixture.Registry.List().Length);
        Assert.Equal(1, fixture.Registry.Authorize(
            healthy.Entry.RegistryId, healthy.Entry.Generation, [healthy.File]).Generation);
    }

    // ======================================================================================
    // AC-L3: the probe is per request, never cached across calls (a healthy verdict must not
    // survive the root disappearing inside the same process/session).
    // ======================================================================================

    [Fact]
    public void RootIdentityIsReProbedOnEveryAuthorize()
    {
        using var fixture = new RegistryFixture();
        var healthy = fixture.RegisterFile("healthy");
        Assert.Equal(1, fixture.Registry.Authorize(healthy.Entry.RegistryId, 1, [healthy.File]).Generation);

        File.Delete(healthy.File); // same instance, same process: no cached "ok" may be reused
        Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", Assert.Throws<SourceAccessException>(
            () => fixture.Registry.Authorize(healthy.Entry.RegistryId, 1, [healthy.File])).Code);
    }

    // ======================================================================================
    // AC-L4 / AC-L5: revoke + explicit reset semantics are unchanged; recovery from an
    // unavailable ROOT does not exist (only the explicit file-level reset remains).
    // ======================================================================================

    [Fact]
    public void RevokeAndExplicitResetAreUnaffectedByAnUnavailableRoot()
    {
        using var fixture = new RegistryFixture();
        var revoked = fixture.RegisterFile("revoked");
        var missing = fixture.RegisterFile("missing");
        File.Delete(missing.File);

        var result = fixture.Registry.Revoke(revoked.Entry.RegistryId);
        Assert.Equal(2, result.Generation);
        Assert.NotNull(result.RevokedAt);
        Assert.Equal("SOURCE_GRANT_REVOKED", Assert.Throws<SourceAccessException>(
            () => fixture.Registry.Authorize(revoked.Entry.RegistryId, 2, [revoked.File])).Code);

        // No automatic recovery exists: the unavailable entry is still there and only the explicit
        // reset (file-level recovery command) clears the registry.
        Assert.Equal(2, fixture.Registry.List().Length);
        Assert.Equal("INVALID_REQUEST", Assert.Throws<SourceAccessException>(
            () => fixture.Registry.Reset(false)).Code);
        var quarantine = fixture.Registry.Reset(true);
        Assert.True(Directory.Exists(quarantine));
        Assert.Empty(fixture.Registry.List());
    }

    // ======================================================================================
    // AC-L1: the file-level corruption path is unchanged (fail-closed, corrupt copy, original
    // bytes preserved, no empty registry created). Any widening of these checks is discriminating.
    // ======================================================================================

    [Fact]
    public void FileLevelCorruptionStaysWholeFileFailClosed()
    {
        AssertFileLevelCorruption("short", (_, path) => File.WriteAllBytes(path, [1, 2, 3]));
        AssertFileLevelCorruption("truncated", (_, path) =>
        {
            var bytes = File.ReadAllBytes(path);
            File.WriteAllBytes(path, bytes[..10]);
        });
        AssertFileLevelCorruption("magic", (_, path) =>
        {
            var bytes = File.ReadAllBytes(path);
            bytes[0] = (byte)'X';
            File.WriteAllBytes(path, bytes);
        });
        AssertFileLevelCorruption("length", (_, path) =>
        {
            var bytes = File.ReadAllBytes(path);
            BitConverter.TryWriteBytes(
                bytes.AsSpan(Magic.Length, 4), (uint)(bytes.Length - Magic.Length - 4 + 5));
            File.WriteAllBytes(path, bytes);
        });
        AssertFileLevelCorruption("json", (_, path) => File.WriteAllBytes(path, Frame("not json")));
        AssertFileLevelCorruption("format_version", (_, path) =>
            MutateSnapshot(path, node => node["format_version"] = JsonValue.Create(2)));
        AssertFileLevelCorruption("duplicate_id", (_, path) => MutateSnapshot(path, node =>
        {
            var entries = node["entries"]!.AsArray();
            entries.Add(entries[0]!.DeepClone());
        }));
        AssertFileLevelCorruption("generation", (_, path) =>
            MutateSnapshot(path, node => node["entries"]![0]!["generation"] = JsonValue.Create(0)));
        AssertFileLevelCorruption("empty_roots", (_, path) =>
            MutateSnapshot(path, node => node["entries"]![0]!["roots"] = new JsonArray()));
        AssertFileLevelCorruption("non_normalized_root", (_, path) => MutateSnapshot(
            path, node => node["entries"]![0]!["roots"]![0]!["root"] = JsonValue.Create(@"C:\..\synthetic")));
        AssertFileLevelCorruption("unreadable_flag", (_, path) => MutateSnapshot(
            path, node => node["entries"]![0]!["roots"]![0]!["readable"] = JsonValue.Create(false)));

        // The real DPAPI wrapper is still part of the file-level judgement (tampered ciphertext).
        AssertFileLevelCorruption("dpapi", (_, path) =>
        {
            var bytes = File.ReadAllBytes(path);
            bytes[^1] ^= 0x42;
            File.WriteAllBytes(path, bytes);
        }, passthrough: false);
    }

    private static void AssertFileLevelCorruption(
        string label, Action<string, string> corrupt, bool passthrough = true)
    {
        var root = Path.Combine(Path.GetTempPath(), "newmanga-ls1-corrupt-" + Guid.NewGuid().ToString("N")[..12]);
        try
        {
            var dataRoot = Path.Combine(root, "host-data");
            ISecretProtector protector = passthrough ? new PassthroughProtector() : new DpapiSecretProtector();
            var writer = new SourceAccessRegistry(dataRoot, protector);
            var sourceDirectory = Path.Combine(root, "source");
            Directory.CreateDirectory(sourceDirectory);
            var file = Path.Combine(sourceDirectory, "book.zip");
            File.WriteAllBytes(file, [0x50, 0x4b, 0x05, 0x06, 0, 0, 0, 0]);
            var entry = writer.Register("fixture", [file]);

            corrupt(dataRoot, writer.RegistryPath);
            var corrupted = File.ReadAllBytes(writer.RegistryPath);
            var directory = Path.GetDirectoryName(writer.RegistryPath)!;
            var copiesBefore = Directory.GetFiles(directory, "*.corrupt-*").Length;

            var reader = new SourceAccessRegistry(dataRoot, protector);
            Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE",
                Assert.Throws<SourceAccessException>(() => reader.List()).Code);
            // The original file is never overwritten with an empty registry and never deleted.
            Assert.Equal(corrupted, File.ReadAllBytes(writer.RegistryPath));
            // A best-effort `.corrupt-<utc>` copy of the original bytes is still produced.
            Assert.True(Directory.GetFiles(directory, "*.corrupt-*").Length > copiesBefore,
                label + ": expected a .corrupt-* diagnostic copy");
            // Every source operation is fail-closed, not only List.
            Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", Assert.Throws<SourceAccessException>(
                () => reader.Authorize(entry.RegistryId, 1, [file])).Code);
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

    // ======================================================================================
    // AC-L6 / D-7: ONE gated real-stdio-IPC case with a MIXED registry (healthy + missing root).
    // Opt-in only (`NEWMANGA_FEA11_IPC=1`); the fixture lives in the task's isolated workspace
    // root (never a tracked repository path, never `verification/FEA-09/native-registry/**`).
    // ======================================================================================

    [SourceRegistryIpcFact]
    public async Task Ipc_MixedRegistry_ListRegisterMintSucceedAndMissingRootIsTyped()
    {
        var (repo, python) = IpcEnvironment();
        var root = Path.Combine(repo + ".workspace", "FEA-11-L-S1-REGISTRY-RESILIENCE-1",
            "fixtures", "ipc-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        var healthyFile = Path.Combine(root, "healthy", "book.png");
        Directory.CreateDirectory(Path.GetDirectoryName(healthyFile)!);
        await File.WriteAllBytesAsync(healthyFile, [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
        var missingFile = Path.Combine(root, "missing", "book.png");
        Directory.CreateDirectory(Path.GetDirectoryName(missingFile)!);
        await File.WriteAllBytesAsync(missingFile, [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

        var options = new CoreServiceOptions
        {
            ExecutablePath = python,
            AdditionalArguments =
            [
                "-X", "utf8", "-c",
                $"import sys;sys.path.insert(0, r'{Path.Combine(repo, "src")}');"
                + "import bootstrap.core_service as m;raise SystemExit(m.main())",
            ],
            DataRoot = root,
            DerivedRoot = Path.Combine(root, "derived"),
            CatalogDbPath = Path.Combine(root, "catalog.sqlite"),
            StderrLogPath = Path.Combine(root, "core.stderr.log"),
            WireLogPath = Path.Combine(root, "wire.ndjson"),
            StartupTimeout = TimeSpan.FromSeconds(90),
            RequestTimeout = TimeSpan.FromSeconds(60),
        };

        await using var client = await CoreServiceClient.StartAsync(options);
        Assert.Contains("source.read/1", (await client.PingAsync()).Capabilities);
        await client.OpenHostSessionAsync();

        var registry = new SourceAccessRegistry(root);
        var healthy = registry.Register("ipc-healthy", [healthyFile]);
        var missing = registry.Register("ipc-missing", [missingFile]);
        File.Delete(missingFile);
        var coordinator = new SourceReadCoordinator(client, registry, () => true);
        var evidence = new List<string>();

        // (1) Real host-control command face over real stdio: a mixed registry lists BOTH entries.
        var listed = await coordinator.InvokeAsync(
            "source_list_roots", JsonObject(), CancellationToken.None);
        var ids = listed.GetProperty("entries").EnumerateArray()
            .Select(entry => entry.GetProperty("registry_id").GetString()).ToArray();
        Assert.Equal(2, ids.Length);
        Assert.Contains(healthy.RegistryId, ids);
        Assert.Contains(missing.RegistryId, ids);
        evidence.Add("source_list_roots (mixed registry) -> entries=2");

        // (2) Healthy root: the production mint path works over the real IPC session.
        var rendition = JsonSerializer.SerializeToElement(new Dictionary<string, object?>
        {
            ["decoder"] = "image", ["scale"] = 1.0, ["params_digest"] = new string('a', 64),
        });
        var grantId = await coordinator.IssueAsync(
            healthy.RegistryId, healthy.Generation, healthyFile, "image",
            "s-ipc-healthy", "sv-ls1", rendition);
        Assert.StartsWith("source-", grantId);
        evidence.Add("IssueAsync(healthy root) -> grant minted");

        // (3) Missing root: typed refusal, zero registry writes, no corrupt copy.
        var before = await File.ReadAllBytesAsync(registry.RegistryPath);
        var registryDirectory = Path.GetDirectoryName(registry.RegistryPath)!;
        var copiesBefore = Directory.GetFiles(registryDirectory, "*.corrupt-*").Length;
        var error = await Assert.ThrowsAsync<SourceAccessException>(() => coordinator.IssueAsync(
            missing.RegistryId, missing.Generation, missingFile, "image",
            "s-ipc-missing", "sv-ls1", rendition));
        Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", error.Code);
        Assert.Equal(before, await File.ReadAllBytesAsync(registry.RegistryPath));
        Assert.Equal(copiesBefore, Directory.GetFiles(registryDirectory, "*.corrupt-*").Length);
        evidence.Add("IssueAsync(missing root) -> " + error.Code + " zero_write=1 no_corrupt_copy=1");

        // (4) A new root can still be registered over real IPC while a root is unavailable.
        var freshDirectory = Path.Combine(root, "fresh");
        Directory.CreateDirectory(freshDirectory);
        var registered = await coordinator.InvokeAsync(
            "source_register_root",
            JsonSerializer.SerializeToElement(new { locator = "ipc-fresh", roots = new[] { freshDirectory } }),
            CancellationToken.None);
        Assert.False(string.IsNullOrEmpty(registered.GetProperty("registry_id").GetString()));
        evidence.Add("source_register_root (mixed registry) -> registered");

        // (5) The unavailable entry is still listed in-process (never dropped, not rewritten).
        var finalList = registry.List();
        Assert.Equal(3, finalList.Length);
        Assert.Contains(missing.RegistryId, finalList.Select(entry => entry.RegistryId));
        evidence.Add("registry.List() -> entries=3 (unavailable entry kept)");

        var receipt = Path.Combine(root, "ls1-ipc-receipt.txt");
        await File.WriteAllTextAsync(receipt,
            "FEA-11-L-S1-REGISTRY-RESILIENCE-1 mixed-registry real stdio IPC\n"
            + string.Join("\n", evidence) + "\nPASS\n");
        Assert.Contains("PASS", await File.ReadAllTextAsync(receipt));
    }

    private static JsonElement JsonObject() =>
        JsonDocument.Parse("{}").RootElement.Clone();

    private static (string Repo, string Python) IpcEnvironment()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
        {
            directory = directory.Parent;
        }
        var repo = directory?.FullName ?? throw new InvalidOperationException("repository not found");
        var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON")
            ?? "C:/Python314/python.exe";
        return (repo, python);
    }

    private sealed class SourceRegistryIpcFactAttribute : FactAttribute
    {
        public SourceRegistryIpcFactAttribute()
        {
            if (Environment.GetEnvironmentVariable("NEWMANGA_FEA11_IPC") != "1")
            {
                Skip = "set NEWMANGA_FEA11_IPC=1 for the real isolated Python Core mixed-registry IPC test";
            }
        }
    }

    private sealed class PassthroughProtector : ISecretProtector
    {
        public byte[] Protect(byte[] plaintext) => plaintext.ToArray();
        public byte[] Unprotect(byte[] ciphertext) => ciphertext.ToArray();
    }

    private sealed class RegistryFixture : IDisposable
    {
        private readonly string _root;

        public RegistryFixture(ISecretProtector? protector = null)
        {
            _root = Path.Combine(Path.GetTempPath(), "newmanga-ls1-" + Guid.NewGuid().ToString("N")[..12]);
            Directory.CreateDirectory(_root);
            Registry = new SourceAccessRegistry(Path.Combine(_root, "host-data"), protector);
        }

        public SourceAccessRegistry Registry { get; }

        public string NewDirectory(string name)
        {
            var path = Path.Combine(_root, name);
            Directory.CreateDirectory(path);
            return path;
        }

        /// <summary>A production-shaped registered FILE root (a referenced source file is the root).</summary>
        public (SourceAuthorization Entry, string File) RegisterFile(string locator)
        {
            var directory = NewDirectory(locator + "-dir");
            var file = Path.Combine(directory, "book.zip");
            File.WriteAllBytes(file, [0x50, 0x4b, 0x05, 0x06, 0, 0, 0, 0]);
            return (Registry.Register(locator, [file]), file);
        }

        public byte[] RegistryBytes => File.ReadAllBytes(Registry.RegistryPath);

        public int CorruptCopyCount()
        {
            var directory = Path.GetDirectoryName(Registry.RegistryPath)!;
            return Directory.Exists(directory)
                ? Directory.GetFiles(directory, "*.corrupt-*").Length
                : 0;
        }

        public void Dispose()
        {
            try
            {
                if (Directory.Exists(_root)) Directory.Delete(_root, recursive: true);
            }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException)
            {
                // isolated temp fixture expires with the OS temp directory
            }
        }
    }

    // --------------------------------------------------------------------------------------
    // Crafted-registry helpers (valid with the identity PassthroughProtector).
    // --------------------------------------------------------------------------------------

    private static byte[] Frame(string plaintext)
    {
        var payload = Encoding.UTF8.GetBytes(plaintext);
        var bytes = new byte[Magic.Length + 4 + payload.Length];
        Encoding.ASCII.GetBytes(Magic).CopyTo(bytes, 0);
        BitConverter.TryWriteBytes(bytes.AsSpan(Magic.Length, 4), (uint)payload.Length);
        payload.CopyTo(bytes, Magic.Length + 4);
        return bytes;
    }

    private static JsonNode ParseSnapshot(string registryPath)
    {
        var bytes = File.ReadAllBytes(registryPath);
        Assert.Equal(Magic, Encoding.ASCII.GetString(bytes, 0, Magic.Length));
        var length = BitConverter.ToUInt32(bytes, Magic.Length);
        Assert.Equal((uint)(bytes.Length - Magic.Length - 4), length);
        return JsonNode.Parse(
            Encoding.UTF8.GetString(bytes, Magic.Length + 4, bytes.Length - Magic.Length - 4))!;
    }

    private static void WriteSnapshot(string registryPath, JsonNode snapshot) =>
        File.WriteAllBytes(registryPath, Frame(snapshot.ToJsonString()));

    private static void MutateSnapshot(string registryPath, Action<JsonNode> mutate)
    {
        var snapshot = ParseSnapshot(registryPath);
        mutate(snapshot);
        WriteSnapshot(registryPath, snapshot);
    }

    private static void RewriteRootIdentity(
        string registryPath, string registryId, ulong volume, ulong fileId) =>
        MutateSnapshot(registryPath, snapshot =>
        {
            var entry = EntryNode(snapshot, registryId);
            entry["roots"]![0]!["volume_serial"] = JsonValue.Create(volume);
            entry["roots"]![0]!["file_id"] = JsonValue.Create(fileId);
        });

    private static (ulong Volume, ulong FileId) ReadRootIdentity(string registryPath, string registryId)
    {
        var entry = EntryNode(ParseSnapshot(registryPath), registryId);
        return (entry["roots"]![0]!["volume_serial"]!.GetValue<ulong>(),
            entry["roots"]![0]!["file_id"]!.GetValue<ulong>());
    }

    private static JsonNode EntryNode(JsonNode snapshot, string registryId) =>
        snapshot["entries"]!.AsArray()
            .Single(node => node!["registry_id"]!.GetValue<string>() == registryId)!;
}
