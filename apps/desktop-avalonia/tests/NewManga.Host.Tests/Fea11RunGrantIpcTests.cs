using System.Diagnostics;
using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Wire;
using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-11-RUN-GRANT-1 (C-16 v1.3 §2.4) real stdio IPC evidence.
///
/// Opt-in only (<c>NEWMANGA_FEA11_IPC=1</c>): starts the real Python Core over
/// an isolated workspace data root. The seed is one real zip container with two
/// real PNG members and TWO pure referenced pages bound to them, so the test can
/// prove:
///
/// * the Host mints the Run-scoped grant (real <c>IssueAsync</c>), the new
///   <c>AuthorizeSourceReadForRun</c> command binds it and the Core's
///   <c>resolve_page_resource</c> then reads the page through that binding;
/// * entry granularity is fail-closed: a page bound to another archive member
///   is refused typed (SOURCE_ACCESS_DENIED) with no partial success;
/// * a revoked grant is a typed refusal;
/// * the wire log/ndjson and the Core stderr carry NO fixture path (C-16 §7).
///
/// The fixture/evidence directories are the task's isolated workspace root
/// (<c>&lt;repo&gt;.workspace/FEA-11-RUN-GRANT-1/</c>), never a tracked file.
/// </summary>
public sealed class Fea11RunGrantIpcTests
{
    [Fea11RunGrantIpcFact]
    public async Task MintBindResolveAndRevoke_TypedWithNoPathLeak()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
        {
            directory = directory.Parent;
        }
        var repo = directory?.FullName ?? throw new InvalidOperationException("repository not found");
        var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? "C:/Python314/python.exe";
        var root = Path.Combine(repo + ".workspace", "FEA-11-RUN-GRANT-1", "fixtures",
            "ipc-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        var receipt = await SeedAsync(repo, python, root);
        var archive = receipt.GetProperty("archive").GetString()!;
        var evidence = new List<string>();

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

        await using (var client = await CoreServiceClient.StartAsync(options))
        {
            Assert.Contains("source.read.run/1", (await client.PingAsync()).Capabilities);
            await client.OpenHostSessionAsync();

            var registry = new SourceAccessRegistry(root);
            var authorized = registry.Register("fea11-run-grant", [root]);
            var coordinator = new SourceReadCoordinator(client, registry, () => true);
            Assert.True(await coordinator.SupportsRunAuthorizationAsync(CancellationToken.None));
            var registryId = authorized.RegistryId;
            var generation = authorized.Generation;
            var renditionScope = new RunSourceScope(
                registryId, generation, archive, "zip", "s1", "sv1");

            // (1) R1-03 boundary: page p1 is bound to the archive's FIRST member
            // (001.png, source_entries.ordinal = 0). The Host-minted CONTAINER
            // grant has one entry (locator = container name, ordinal = 0), so it
            // only matches via the ordinal-0 clause — this is the archive
            // first-member boundary of L-G12, NOT generic entry granularity.
            var bound = await coordinator.AuthorizeRunAsync(
                [renditionScope], "reocr_all",
                JsonSerializer.SerializeToElement(new { kind = "page", page_id = "p1" }));
            Assert.Equal(1, bound.BoundPages);
            Assert.Equal(1, bound.MintedGrants);
            Assert.False(bound.Skipped);
            evidence.Add("AuthorizeSourceReadForRun(p1=first member) -> bound_pages=1");

            var resolved = await client.SendAsync(
                "resolve_page_resource", 3,
                writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("page_id", "p1");
                    writer.WriteEndObject();
                }, TimeSpan.FromSeconds(60));
            Assert.NotNull(resolved.Result);
            Assert.True(resolved.Result!.Value.ValueKind == JsonValueKind.Object,
                "resolve_page_resource returned no object");
            evidence.Add("resolve_page_resource(first member) -> OK");

            // (2) R1-03 boundary: page p2 is bound to member 002.png
            // (source_entries.ordinal = 1). The container grant cannot carry a
            // member entry identity, so the Core refuses the whole request typed
            // (L-G12 second half; fail-closed, no partial binding, not an
            // authorization bypass).
            var refused = await Assert.ThrowsAsync<CoreOperationException>(() =>
                coordinator.AuthorizeRunAsync(
                    [renditionScope], "reocr_all",
                    JsonSerializer.SerializeToElement(new { kind = "page", page_id = "p2" })));
            Assert.Equal("SOURCE_ACCESS_DENIED", refused.Code);
            evidence.Add("AuthorizeSourceReadForRun(p2=second member) -> L-G12 " + refused.Code);

            // (2b) R1-01/R1-04: a Host-side mint failure (missing file) is a
            // BEST-EFFORT SKIP with a frozen §6 code — no exception, no Core
            // call, and a managed/unrelated Run is never blocked by it.
            var missingArchive = Path.Combine(
                root, "missing-" + Guid.NewGuid().ToString("N") + ".zip");
            var skippedMint = await coordinator.AuthorizeRunAsync(
                [new RunSourceScope(registryId, generation, missingArchive, "zip", "s1", "sv1")],
                "reocr_all",
                JsonSerializer.SerializeToElement(new { kind = "page", page_id = "p1" }));
            Assert.True(skippedMint.Skipped);
            Assert.Equal(0, skippedMint.BoundPages);
            Assert.Equal(0, skippedMint.MintedGrants);
            Assert.Equal(1, skippedMint.SkippedSources);
            Assert.Contains(
                skippedMint.SkippedCodes.Single(),
                new[] { "SOURCE_ENTRY_MISSING", "SOURCE_ACCESS_DENIED" });
            evidence.Add("mint failure (missing file) -> best-effort skip "
                         + skippedMint.SkippedCodes.Single());

            // (2c) partial source failure: the resolvable source is still
            // minted/bound; only the broken one is skipped.
            var mixed = await coordinator.AuthorizeRunAsync(
                [
                    renditionScope,
                    new RunSourceScope(registryId, generation, missingArchive, "zip", "s1", "sv1"),
                ],
                "reocr_all",
                JsonSerializer.SerializeToElement(new { kind = "page", page_id = "p1" }));
            Assert.Equal(1, mixed.BoundPages);
            Assert.Equal(1, mixed.MintedGrants);
            Assert.Equal(1, mixed.SkippedSources);
            evidence.Add("partial mint failure -> minted=1 bound_pages=1 skipped=1");

            // (3) revoking the root kills the page read typed (no silent read)
            // and prunes the Host ledger (R-8/L-G7).
            var revoked = await coordinator.InvokeAsync(
                "source_revoke_root",
                JsonSerializer.SerializeToElement(new { registry_id = registryId }),
                CancellationToken.None);
            Assert.Equal(JsonValueKind.Object, revoked.ValueKind);
            var afterRevoke = await Assert.ThrowsAsync<CoreOperationException>(() =>
                client.SendAsync("resolve_page_resource", 3, writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("page_id", "p1");
                    writer.WriteEndObject();
                }, TimeSpan.FromSeconds(60)));
            Assert.Equal("SOURCE_ACCESS_DENIED", afterRevoke.Code);
            evidence.Add("resolve_page_resource after revoke -> " + afterRevoke.Code);
            Assert.Equal(0, coordinator.TrackedGrantCount);
        }

        // (4) C-16 §7: neither the wire frame log nor the Core stderr may carry
        // the fixture path (the new command never carries paths at all).
        var wirePath = Path.Combine(root, "wire.ndjson");
        var stderrPath = Path.Combine(root, "core.stderr.log");
        var wire = File.Exists(wirePath) ? await File.ReadAllTextAsync(wirePath) : string.Empty;
        var stderr = File.Exists(stderrPath) ? await File.ReadAllTextAsync(stderrPath) : string.Empty;
        Assert.DoesNotContain(root, wire, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain(root, stderr, StringComparison.OrdinalIgnoreCase);
        // The signed grant carries the container path; the saveable frame is
        // rewritten BEFORE it is stored (C-16 §7) and the new command carries
        // no path at all.
        Assert.Contains("[REDACTED]", wire, StringComparison.Ordinal);
        Assert.DoesNotContain(archive, wire, StringComparison.OrdinalIgnoreCase);
        Assert.Contains("AuthorizeSourceReadForRun", wire, StringComparison.Ordinal);
        evidence.Add("wire/stderr path leak -> 0");

        await File.WriteAllTextAsync(
            Path.Combine(root, "run-grant-ipc.txt"),
            $"DataRoot={root}\n" + string.Join("\n", evidence) + "\nPASS\n");
    }

    [Fea11RunGrantIpcFact]
    public async Task CoreAdvertisesTheRunAuthorizationCapability_AndRefusesWithoutGrants()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
        {
            directory = directory.Parent;
        }
        var repo = directory?.FullName ?? throw new InvalidOperationException("repository not found");
        var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? "C:/Python314/python.exe";
        var root = Path.Combine(repo + ".workspace", "FEA-11-RUN-GRANT-1", "fixtures",
            "ipc-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        await SeedAsync(repo, python, root);
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
        await client.OpenHostSessionAsync();
        Assert.Contains("source.read.run/1", (await client.PingAsync()).Capabilities);
        // The command itself is host-control only and typed without a grant.
        var refused = await Assert.ThrowsAsync<CoreOperationException>(() =>
            client.SendHostControlAsync("AuthorizeSourceReadForRun", writer =>
            {
                writer.WriteStartArray("grant_ids");
                writer.WriteStringValue("source-" + new string('0', 32));
                writer.WriteEndArray();
                writer.WriteString("command", "reocr_all");
                writer.WriteStartObject("scope");
                writer.WriteString("kind", "page");
                writer.WriteString("page_id", "p1");
                writer.WriteEndObject();
            }));
        Assert.Equal("SOURCE_ACCESS_DENIED", refused.Code);
        var application = await Assert.ThrowsAsync<CoreOperationException>(() =>
            client.SendAsync("AuthorizeSourceReadForRun", 3, WireJson.EmptyObject,
                TimeSpan.FromSeconds(30)));
        Assert.Equal("HOST_ONLY_REQUIRED", application.Code);
        await File.WriteAllTextAsync(
            Path.Combine(root, "run-grant-ipc-capability.txt"),
            $"DataRoot={root}\ncapability=source.read.run/1\nno_grant={refused.Code}\n"
            + $"application_channel={application.Code}\nPASS\n");
    }

    private static async Task<JsonElement> SeedAsync(string repo, string python, string root)
    {
        var script = $$"""
import hashlib
import io
import json
import sqlite3
import sys
import zipfile
from pathlib import Path

repo = Path(r"{{repo}}")
root = Path(r"{{root}}")
sys.path[:0] = [str(repo), str(repo / "src"), str(repo / "tests" / "fea11")]

from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.schema import default_migrations
import conftest as fixture
from PIL import Image


def png(color):
    buffer = io.BytesIO()
    Image.new("RGB", (8, 6), color).save(buffer, format="PNG")
    return buffer.getvalue()


root.mkdir(parents=True, exist_ok=True)
db = root / "library.db"
archive = root / "source-v1.zip"
first, second = png((255, 0, 0)), png((0, 0, 255))
with zipfile.ZipFile(archive, "w") as archive_file:
    archive_file.writestr("001.png", first)
    archive_file.writestr("002.png", second)
facts = fixture.file_facts(archive)
first_digest = hashlib.sha256(first).hexdigest()
second_digest = hashlib.sha256(second).hexdigest()
conn = sqlite3.connect(db, isolation_level=None)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")
MigrationRunner(conn, default_migrations()).apply_pending()
conn.execute(
    "INSERT INTO books (book_id,title,created_at,updated_at) VALUES ('b1','IPC',?,?)",
    (fixture.NOW, fixture.NOW))
conn.execute(
    "INSERT INTO chapters (chapter_id,book_id,title,created_at,updated_at)"
    " VALUES ('c1','b1','Ch',?,?)", (fixture.NOW, fixture.NOW))
conn.commit()
fixture.add_source_tree(
    conn, source_id="s1", version_id="sv1", digest=facts["sha256"],
    entries=[("se1", "001.png", first_digest), ("se2", "002.png", second_digest)],
    volume_serial=facts["volume_serial"], file_id=facts["file_id"],
    legacy_v7_evidence=False)
conn.execute(
    "UPDATE source_locations SET size_bytes = ? WHERE source_id = 's1'",
    (facts["size"],))
fixture.add_referenced_page(
    conn, "p1", "c1", "b1", order=1, source_id="s1", version_id="sv1",
    entry_id="se1", digest=first_digest, width=8, height=6)
fixture.add_referenced_page(
    conn, "p2", "c1", "b1", order=2, source_id="s1", version_id="sv1",
    entry_id="se2", digest=second_digest, width=8, height=6)
conn.commit()
conn.close()
receipt = {
    "root": str(root), "db": str(db), "archive": str(archive),
    "source_id": "s1", "version_id": "sv1",
}
(root / "ipc-run-grant-receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
print("FEA11_RUN_GRANT_SEED_OK")
""";
        var startInfo = new ProcessStartInfo(python)
        {
            WorkingDirectory = repo,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        startInfo.ArgumentList.Add("-c");
        startInfo.ArgumentList.Add(script);
        using var process = Process.Start(startInfo)!;
        var stdout = process.StandardOutput.ReadToEndAsync();
        var stderr = process.StandardError.ReadToEndAsync();
        await process.WaitForExitAsync();
        Assert.True(process.ExitCode == 0, await stdout + await stderr);
        using var document = JsonDocument.Parse(
            await File.ReadAllTextAsync(Path.Combine(root, "ipc-run-grant-receipt.json")));
        return document.RootElement.Clone();
    }

    private sealed class Fea11RunGrantIpcFactAttribute : FactAttribute
    {
        public Fea11RunGrantIpcFactAttribute()
        {
            if (Environment.GetEnvironmentVariable("NEWMANGA_FEA11_IPC") != "1")
            {
                Skip = "set NEWMANGA_FEA11_IPC=1 for the real isolated Python Core Run-grant IPC test";
            }
        }
    }
}
