using System.Security.Cryptography;
using System.Text.Json;
using NewManga.Host.Sources;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-13-SRC-6 (C-09 SC-B07 ④): the Host-side restore import.
///
/// HONEST LABELLING: the DPAPI-failure cases use an injectable protector (simulated
/// cross-user/cross-machine). A REAL cross-machine DPAPI round trip cannot be constructed
/// on one machine and is reported as NOT_RUN in the evidence, never as a PASS.
/// </summary>
public sealed class SourceAccessRestoreTests : IDisposable
{
    private readonly string _root;
    private readonly string _sourceRoot;

    public SourceAccessRestoreTests()
    {
        _root = Path.Combine(Path.GetTempPath(), "nm-src6-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_root);
        _sourceRoot = Path.Combine(_root, "source");
        Directory.CreateDirectory(_sourceRoot);
        File.WriteAllText(Path.Combine(_sourceRoot, "page-1.png"), "pixels");
    }

    public void Dispose()
    {
        try { Directory.Delete(_root, recursive: true); } catch { /* best effort */ }
    }

    /// <summary>Reversible stand-in for DPAPI (layout/merge tests; NOT a real DPAPI proof).</summary>
    private sealed class XorProtector : ISecretProtector
    {
        public byte[] Protect(byte[] plaintext) =>
            plaintext.Select(value => (byte)(value ^ 0x5A)).ToArray();

        public byte[] Unprotect(byte[] ciphertext) =>
            ciphertext.Select(value => (byte)(value ^ 0x5A)).ToArray();
    }

    /// <summary>Simulates another Windows user/machine: unprotect always fails.</summary>
    private sealed class BrokenProtector : ISecretProtector
    {
        public byte[] Protect(byte[] plaintext) => throw new CryptographicException("denied");

        public byte[] Unprotect(byte[] ciphertext) => throw new CryptographicException("denied");
    }

    private SourceAccessRegistry NewRegistry(string name, ISecretProtector? protector = null)
    {
        var dataRoot = Path.Combine(_root, name);
        Directory.CreateDirectory(dataRoot);
        return new SourceAccessRegistry(dataRoot, protector ?? new XorProtector());
    }

    /// <summary>Build a real handoff directory from the live registry's on-disk bytes.</summary>
    private string BuildHandoff(SourceAccessRegistry source, string? backupId = null)
    {
        var id = backupId ?? Guid.NewGuid().ToString("N");
        var handoffRoot = Path.Combine(_root, "data", "backups", "restore-handoff", id);
        var segmentDir = Path.Combine(handoffRoot, "source-access");
        Directory.CreateDirectory(segmentDir);
        var bytes = File.ReadAllBytes(source.RegistryPath);
        File.WriteAllBytes(Path.Combine(segmentDir, "registry.v1.dat"), bytes);
        var sha = Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
        File.WriteAllText(Path.Combine(handoffRoot, "handoff.json"), JsonSerializer.Serialize(new
        {
            backup_id = id,
            member = "extras/source-access/registry.v1.dat",
            sha256 = sha,
            size_bytes = bytes.Length,
            database_id = (string?)null,
            created_at = DateTimeOffset.UtcNow.ToString("O"),
        }));
        return id;
    }

    private SourceAccessRegistry DataRootRegistry(ISecretProtector? protector = null)
    {
        var dataRoot = Path.Combine(_root, "data");
        Directory.CreateDirectory(dataRoot);
        return new SourceAccessRegistry(dataRoot, protector ?? new XorProtector());
    }

    [Fact]
    public void HandoffImportAddsTheRestoredAuthorization()
    {
        var source = NewRegistry("live-a");
        var live = source.Register("loc-live", [ _sourceRoot ]);
        var backupId = BuildHandoff(source);

        var target = DataRootRegistry();
        var outcome = SourceAccessRestore.TryImportFromHandoff(_root + "/data", backupId, target);

        Assert.True(outcome.Succeeded);
        Assert.Equal("imported", outcome.Status);
        Assert.Equal(1, outcome.Imported);
        var restored = target.List().Single();
        Assert.Equal(live.RegistryId, restored.RegistryId);
        Assert.Equal(live.Generation, restored.Generation);
        Assert.Equal(live.Roots.Select(root => root.Root), restored.Roots.Select(root => root.Root));
    }

    [Fact]
    public void SecondImportIsIdempotentAndTheReceiptStopsStartupRevival()
    {
        var source = NewRegistry("live-b");
        source.Register("loc-live", [ _sourceRoot ]);
        var backupId = BuildHandoff(source);
        var target = DataRootRegistry();

        var first = SourceAccessRestore.TryImportFromHandoff(_root + "/data", backupId, target);
        Assert.Equal("imported", first.Status);

        var second = SourceAccessRestore.TryImportFromHandoff(_root + "/data", backupId, target);
        Assert.Equal("unchanged", second.Status);

        // A user-visible reset must never be undone by the startup scan (receipt guard).
        target.Reset(true);
        Assert.Empty(target.List());
        var pending = SourceAccessRestore.TryImportPending(_root + "/data", target);
        Assert.All(pending, outcome => Assert.Equal("unchanged", outcome.Status));
        Assert.Empty(target.List());
    }

    [Fact]
    public void LiveEntryWinsOverAnOlderOrRevokedCandidate()
    {
        var source = NewRegistry("live-c");
        source.Register("loc-live", [ _sourceRoot ]);
        var backupId = BuildHandoff(source);

        var target = DataRootRegistry();
        SourceAccessRestore.TryImportFromHandoff(_root + "/data", backupId, target);
        var imported = target.List().Single();

        // Simulate a newer live state: revoke the imported entry.
        target.Revoke(imported.RegistryId);
        var liveBytes = File.ReadAllBytes(target.RegistryPath);

        var conflict = SourceAccessRestore.TryImportFromHandoff(_root + "/data", backupId, target);

        // The receipt would normally short-circuit; force a real merge by removing it.
        if (conflict.Status == "unchanged" && conflict.Conflicts == 0)
        {
            File.Delete(Path.Combine(
                SourceAccessRestore.HandoffRoot(_root + "/data", backupId), "import-receipt.json"));
            conflict = SourceAccessRestore.TryImportFromHandoff(_root + "/data", backupId, target);
        }
        Assert.Equal(1, conflict.Conflicts);
        Assert.Equal(0, conflict.Imported);
        Assert.Equal(liveBytes, File.ReadAllBytes(target.RegistryPath));
        Assert.NotNull(target.List().Single().RevokedAt);
    }

    [Fact]
    public void ForeignDpapiSnapshotIsRejectedWithZeroWrites()
    {
        var source = NewRegistry("live-d");
        source.Register("loc-live", [ _sourceRoot ]);
        var backupId = BuildHandoff(source);

        var target = DataRootRegistry(new BrokenProtector());
        var outcome = SourceAccessRestore.TryImportFromHandoff(_root + "/data", backupId, target);

        Assert.False(outcome.Succeeded);
        Assert.Equal("rejected", outcome.Status);
        Assert.Equal("SOURCE_ACCESS_DENIED", outcome.Code);
        Assert.Empty(target.List());
    }

    [Fact]
    public void TamperedOrTruncatedSegmentIsRejected()
    {
        var source = NewRegistry("live-e");
        source.Register("loc-live", [ _sourceRoot ]);
        var backupId = BuildHandoff(source);
        var segment = Path.Combine(
            SourceAccessRestore.HandoffRoot(_root + "/data", backupId),
            "source-access", "registry.v1.dat");
        File.WriteAllBytes(segment, File.ReadAllBytes(segment)[..10]);

        var target = DataRootRegistry();
        var outcome = SourceAccessRestore.TryImportFromHandoff(_root + "/data", backupId, target);

        Assert.Equal("rejected", outcome.Status);
        Assert.Equal("handoff_corrupt", outcome.Reason);
        Assert.Empty(target.List());
    }

    [Fact]
    public void MissingHandoffIsNotPresentAndWritesNothing()
    {
        var target = DataRootRegistry();
        var outcome = SourceAccessRestore.TryImportFromHandoff(
            _root + "/data", Guid.NewGuid().ToString("N"), target);
        Assert.Equal("not_present", outcome.Status);
        Assert.Empty(target.List());
    }

    [Fact]
    public void MalformedBackupIdIsRejected()
    {
        var target = DataRootRegistry();
        var outcome = SourceAccessRestore.TryImportFromHandoff(_root + "/data", "../escape", target);
        Assert.Equal("rejected", outcome.Status);
        Assert.Equal("handoff_corrupt", outcome.Reason);
    }

    [Fact]
    public void ExplicitForceReimportsAfterAReceipt()
    {
        var source = NewRegistry("live-f");
        source.Register("loc-live", [ _sourceRoot ]);
        var backupId = BuildHandoff(source);
        var target = DataRootRegistry();

        var first = SourceAccessRestore.TryImportFromHandoff(_root + "/data", backupId, target);
        Assert.Equal("imported", first.Status);

        // Startup scan respects the receipt...
        var pending = SourceAccessRestore.TryImportPending(_root + "/data", target);
        Assert.All(pending, outcome => Assert.Equal("unchanged", outcome.Status));

        // ...but an EXPLICIT restore of the same package re-imports it, and the merge
        // reports the already-present entry as Unchanged (not a Conflict).
        var forced = SourceAccessRestore.TryImportFromHandoff(
            _root + "/data", backupId, target, force: true);
        Assert.Equal("unchanged", forced.Status);
        Assert.Equal(0, forced.Conflicts);
        Assert.Equal(1, forced.Unchanged);
    }

    [Fact]
    public void UnsupportedSnapshotVersionIsRejectedDistinctly()
    {
        var source = NewRegistry("live-g");
        source.Register("loc-live", [ _sourceRoot ]);
        var backupId = BuildHandoff(source);
        var segment = Path.Combine(
            SourceAccessRestore.HandoffRoot(_root + "/data", backupId),
            "source-access", "registry.v1.dat");
        var bytes = File.ReadAllBytes(segment);
        // Flip the magic to NMSAR2 and keep the length/sha consistent with the manifest.
        bytes[5] = (byte)'2';
        File.WriteAllBytes(segment, bytes);
        var manifestPath = Path.Combine(
            SourceAccessRestore.HandoffRoot(_root + "/data", backupId), "handoff.json");
        var manifest = System.Text.Json.Nodes.JsonNode.Parse(File.ReadAllText(manifestPath))!;
        var sha = Convert.ToHexString(
            System.Security.Cryptography.SHA256.HashData(bytes)).ToLowerInvariant();
        manifest["sha256"] = sha;
        manifest["size_bytes"] = bytes.Length;
        File.WriteAllText(manifestPath, manifest.ToJsonString());

        var target = DataRootRegistry();
        var outcome = SourceAccessRestore.TryImportFromHandoff(_root + "/data", backupId, target);

        Assert.Equal("rejected", outcome.Status);
        Assert.Equal("registry_version_unsupported", outcome.Reason);
        Assert.Empty(target.List());
    }
}
