using System.Text.Json;
using NewManga.App.Services;
using NewManga.Host.Tests.Support;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-12-UI AC1/AC5/AC6/AC10 over REAL Host → Python Core stdio: the production App trash port
/// (<see cref="ITrashController"/> implemented by <see cref="HostController"/>) against the real
/// Core handlers. Asserts typed outcomes, the digest-bound single-delete frame and the raw wire
/// evidence: 0 purge frames, 0 batch frames, exactly one delete payload key set.
/// </summary>
public sealed class Fea12TrashUiIpcTests : IClassFixture<Fea12ProductionFixture>
{
    private readonly Fea12ProductionFixture _fixture;

    public Fea12TrashUiIpcTests(Fea12ProductionFixture fixture) => _fixture = fixture;

    [Fea12IpcFact]
    public async Task TrashFlow_OverRealIpc_DisclosesBindsDigestAndNeverUsesPurgeOrBatch()
    {
        var controller = _fixture.Controller;
        var trash = Assert.IsAssignableFrom<ITrashController>(controller);

        // AC8: the isolated Core DataRoot is OUTSIDE the repository; a sentinel tree outside that
        // DataRoot must stay byte-identical (the delete flow never touches original files).
        var repo = Path.GetFullPath(_fixture.Repo);
        var dataRoot = Path.GetFullPath(_fixture.DataRoot);
        Assert.False(dataRoot.StartsWith(repo + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase),
            "real-IPC DataRoot must live outside the repository");
        var sentinelBefore = FingerprintTree(_fixture.SentinelRoot);

        // 1) Capability probe is a core.ping read, and the new Core advertises all three faces.
        var capabilities = await trash.ProbeTrashCapabilitiesAsync();
        Assert.True(capabilities.Probed, capabilities.Message);
        Assert.True(capabilities.ReadAvailable, capabilities.Message);
        Assert.True(capabilities.WriteAvailable, capabilities.Message);
        Assert.True(capabilities.PreviewAvailable, capabilities.Message);

        // 2) Real book through the frozen write gate, then one soft delete.
        Assert.True(await controller.TryCreateBookAsync("FEA-12 UI IPC 作品"), controller.Snapshot.LastError);
        await controller.RefreshBooksAsync();
        var book = controller.Snapshot.Books.First(candidate => candidate.Title == "FEA-12 UI IPC 作品");

        var move = await trash.MoveToTrashAsync(new[] { book.BookId }, TrashIdempotency.NewKey());
        Assert.True(move.Ok, move.Message);
        Assert.Contains(book.BookId, move.SucceededIds);

        var page = await trash.ListTrashAsync();
        Assert.True(page.Ok, page.Message);
        Assert.Contains(page.Items, item => item.BookId == book.BookId);

        // 3) Restore closes the soft-delete loop (single frame, per-item result).
        var restore = await trash.RestoreFromTrashAsync(new[] { book.BookId }, TrashIdempotency.NewKey());
        Assert.True(restore.Ok, restore.Message);
        Assert.Contains(book.BookId, restore.SucceededIds);
        Assert.DoesNotContain((await trash.ListTrashAsync()).Items, item => item.BookId == book.BookId);

        // 4) Move again and read the PD-01 disclosure: the rev 2.14 complete current sets MUST be
        //    present on a new Core (only an old Core may report them as unknown/null).
        Assert.True((await trash.MoveToTrashAsync(new[] { book.BookId }, TrashIdempotency.NewKey())).Ok);
        var preview = await trash.PreviewPermanentDeleteAsync(new[] { book.BookId });
        Assert.True(preview.Ok, preview.Message);
        var item = Assert.Single(preview.Items);
        Assert.Equal(book.BookId, item.BookId);
        Assert.True(item.Protection.CurrentSetKnown, "new Core must return both current arrays");
        Assert.NotNull(preview.InventoryDigest);
        Assert.StartsWith("sha256:", preview.InventoryDigest, StringComparison.Ordinal);
        Assert.True(preview.Digests.TryGetValue(book.BookId, out var boundDigest), "preview must expose the per-book digest");
        Assert.StartsWith("sha256:", boundDigest, StringComparison.Ordinal);

        // 5) A wrong digest never deletes: typed stale-preview (zero side effects).
        var stale = await trash.DeletePermanentlyAsync(book.BookId, "sha256:" + new string('0', 64));
        Assert.Equal(TrashDeleteOutcome.Stale, stale.Outcome);
        Assert.Contains((await trash.ListTrashAsync()).Items, entry => entry.BookId == book.BookId);

        // 6) The bound digest deletes exactly once; a second attempt is typed not-found.
        var deleted = await trash.DeletePermanentlyAsync(book.BookId, boundDigest!);
        Assert.Equal(TrashDeleteOutcome.Deleted, deleted.Outcome);
        Assert.DoesNotContain((await trash.ListTrashAsync()).Items, entry => entry.BookId == book.BookId);
        var second = await trash.DeletePermanentlyAsync(book.BookId, boundDigest!);
        Assert.NotEqual(TrashDeleteOutcome.Deleted, second.Outcome);

        // 7) Raw wire evidence: only the registered commands, no purge, no batch permanent delete.
        var frames = Fea12WireEvidence.CoreFrames(_fixture.WireDirectory);
        Assert.NotEmpty(frames);
        var commands = frames.Select(frame => frame.Command).Where(command => command.Length > 0).ToArray();
        Assert.Contains("PreviewPermanentDeleteBooks", commands);
        Assert.Contains("MoveToTrash", commands);
        Assert.Contains("RestoreFromTrash", commands);
        Assert.Contains("PermanentlyDeleteBook", commands);
        Assert.DoesNotContain("PurgeTrash", commands);
        Assert.DoesNotContain("PermanentlyDeleteBooks", commands);

        var deleteFrames = frames
            .Where(frame => frame.Command == "PermanentlyDeleteBook")
            .Select(frame => frame.Payload)
            .ToArray();
        Assert.Equal(3, deleteFrames.Length); // stale attempt + successful delete + post-delete retry
        foreach (var payload in deleteFrames)
        {
            var keys = payload.EnumerateObject().Select(property => property.Name)
                .OrderBy(name => name, StringComparer.Ordinal).ToArray();
            Assert.Equal(
                new[] { "book_id", "confirm_permanent_delete", "inventory_digest" },
                keys);
            Assert.NotEqual("0", payload.GetProperty("inventory_digest").GetString());
        }

        // The delete bound the SAME PER-BOOK digest the preview computed (byte-for-byte binding);
        // the collection digest is NOT accepted by the single-delete command.
        var deleteDigests = deleteFrames
            .Select(payload => payload.GetProperty("inventory_digest").GetString())
            .ToArray();
        Assert.Contains(boundDigest, deleteDigests);
        if (!string.Equals(preview.InventoryDigest, boundDigest, StringComparison.Ordinal))
        {
            Assert.DoesNotContain(preview.InventoryDigest, deleteDigests);
        }

        // AC8: sentinel tree outside the isolated DataRoot is byte-identical before/after.
        var sentinelAfter = FingerprintTree(_fixture.SentinelRoot);
        Assert.Equal(sentinelBefore, sentinelAfter);

        // Evidence snapshot for the Handoff (temp-first; curated runs sync it).
        EvidenceJson.Write("fea12-trash-ui-ipc.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("core", "real core_service over stdio");
            writer.WriteString("bookId", book.BookId);
            writer.WriteString("collectionDigest", preview.InventoryDigest);
            writer.WriteString("perBookDigest", boundDigest);
            writer.WriteNumber("wire_frames", frames.Count);
            writer.WriteBoolean("purge_frames", commands.Contains("PurgeTrash"));
            writer.WriteBoolean("batch_permanent_delete_frames", commands.Contains("PermanentlyDeleteBooks"));
            writer.WriteBoolean("dataRootOutsideRepo", true);
            writer.WriteBoolean("sentinelUnchanged", sentinelBefore == sentinelAfter);
            writer.WriteString("sentinelFingerprint", sentinelBefore);
            writer.WriteEndObject();
        });
    }

    /// <summary>Deterministic SHA-256 over relative names + bytes of a sentinel tree.</summary>
    private static string FingerprintTree(string root)
    {
        using var hash = System.Security.Cryptography.IncrementalHash.CreateHash(
            System.Security.Cryptography.HashAlgorithmName.SHA256);
        foreach (var file in Directory.EnumerateFiles(root, "*", SearchOption.AllDirectories)
                     .OrderBy(path => path, StringComparer.Ordinal))
        {
            var relative = Path.GetRelativePath(root, file).Replace('\\', '/');
            var bytes = File.ReadAllBytes(file);
            hash.AppendData(System.Text.Encoding.UTF8.GetBytes(relative));
            hash.AppendData(new[] { (byte)0 });
            hash.AppendData(bytes);
            hash.AppendData(new[] { (byte)0 });
        }

        return Convert.ToHexString(hash.GetHashAndReset()).ToLowerInvariant();
    }
}

/// <summary>Evidence writer mirroring the App test discipline (never writes the repo by default).</summary>
internal static class EvidenceJson
{
    public static string Directory
    {
        get
        {
            var root = Environment.GetEnvironmentVariable(HostFixture.EvidenceDirectoryVariable);
            if (string.IsNullOrWhiteSpace(root))
            {
                root = Path.Combine(Path.GetTempPath(), "newmanga-fea12-ui-evidence");
            }

            System.IO.Directory.CreateDirectory(root);
            return root;
        }
    }

    public static void Write(string relativePath, Action<Utf8JsonWriter> write)
    {
        var path = Path.Combine(Directory, relativePath);
        System.IO.Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        using var stream = File.Create(path);
        using var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true });
        write(writer);
    }
}
