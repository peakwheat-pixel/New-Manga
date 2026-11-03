using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Nodes;
using NewManga.CoreClient;
using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>FEA-09 AC-6: real Host↔Core stdio IPC with the production wire.</summary>
public sealed class Fea09RealIpcTests
{
    private const string OnePixelPngBase64 =
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";

    [PythonIpcFact]
    public async Task ReferencedImportAndResolveOverRealStdio()
    {
        var repo = FindRepository();
        var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? "python";
        var sourceRoot = Path.Combine(repo + ".workspace", "FEA-09", "ipc-" + Guid.NewGuid().ToString("N"));
        var dataRoot = Path.Combine(sourceRoot, "data");
        var sourceDir = Path.Combine(sourceRoot, "source");
        Directory.CreateDirectory(sourceDir);
        var sourceFile = Path.Combine(sourceDir, "page.png");
        await File.WriteAllBytesAsync(sourceFile, Convert.FromBase64String(OnePixelPngBase64));
        var sourceDigest = Convert.ToHexString(SHA256.HashData(await File.ReadAllBytesAsync(sourceFile))).ToLowerInvariant();

        var options = new CoreServiceOptions
        {
            ExecutablePath = python,
            AdditionalArguments =
            [
                "-X", "utf8", "-c",
                $"import sys;sys.path.insert(0, r'{Path.Combine(repo, "src")}');import bootstrap.core_service as m;raise SystemExit(m.main())",
            ],
            DataRoot = dataRoot,
            DerivedRoot = Path.Combine(dataRoot, "derived"),
            CatalogDbPath = Path.Combine(dataRoot, "catalog", "catalog.sqlite"),
            StderrLogPath = Path.Combine(sourceRoot, "core.stderr.log"),
            WireLogPath = Path.Combine(sourceRoot, "wire.ndjson"),
            StartupTimeout = TimeSpan.FromSeconds(90),
            RequestTimeout = TimeSpan.FromSeconds(90),
        };

        await using var client = await CoreServiceClient.StartAsync(options);
        await client.OpenHostSessionAsync();

        var ping = await client.PingAsync();
        Assert.True(ping.Ready, "core must be ready");
        Assert.Contains("source.read/1", ping.Capabilities);

        var book = await client.CreateBookAsync("FEA-09 IPC book");
        var chapterResponse = await client.SendAsync(
            "CreateChapter", 8,
            writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("book_id", book.BookId);
                writer.WriteString("title", "FEA-09 IPC chapter");
                writer.WriteEndObject();
            },
            TimeSpan.FromSeconds(30));
        var chapterId = chapterResponse.Result!.Value.GetProperty("chapter_id").GetString()!;

        var registry = new SourceAccessRegistry(Path.Combine(sourceRoot, "host-data"));
        var coordinator = new SourceReadCoordinator(client, registry, () => true);
        var authorization = registry.Register("fea09-ipc-fixture", [sourceFile]);
        var rendition = JsonDocument.Parse(
            "{\"decoder\":\"image\",\"scale\":1.0,\"params_digest\":\""
            + new string('a', 64) + "\"}").RootElement.Clone();
        var grantId = await coordinator.IssueAsync(
            authorization.RegistryId,
            authorization.Generation,
            sourceFile,
            "image",
            "source-ipc-1",
            "1",
            rendition);
        Assert.False(string.IsNullOrWhiteSpace(grantId));

        var plan = await coordinator.InvokeAsync("plan_import_references", JsonDocument.Parse(
            $"{{\"chapter_id\":\"{chapterId}\",\"grants\":[\"{grantId}\"],\"duplicate_policy\":\"skip\"}}")
            .RootElement.Clone(), CancellationToken.None);
        var planId = plan.GetProperty("plan_id").GetString()!;
        var planDigest = plan.GetProperty("plan_digest").GetString()!;
        Assert.Equal(1, plan.GetProperty("totals").GetProperty("import").GetInt32());

        var operationId = "op-" + Guid.NewGuid().ToString("N");
        await coordinator.InvokeAsync("start_import_references", JsonDocument.Parse(
            $"{{\"chapter_id\":\"{chapterId}\",\"plan_id\":\"{planId}\",\"plan_digest\":\"{planDigest}\","
            + $"\"grants\":[\"{grantId}\"],\"duplicate_policy\":\"skip\",\"operation_id\":\"{operationId}\"}}")
            .RootElement.Clone(), CancellationToken.None);

        JsonElement receipt = default;
        var deadline = DateTime.UtcNow + TimeSpan.FromSeconds(60);
        while (DateTime.UtcNow < deadline)
        {
            receipt = await coordinator.InvokeAsync("get_import_receipt", JsonDocument.Parse(
                $"{{\"operation_id\":\"{operationId}\"}}").RootElement.Clone(), CancellationToken.None);
            var state = receipt.GetProperty("state").GetString();
            if (state is "completed" or "failed" or "cancelled") break;
            await Task.Delay(100);
        }
        Assert.Equal("completed", receipt.GetProperty("state").GetString());
        var pageId = receipt.GetProperty("items")[0].GetProperty("pages")[0]
            .GetProperty("page_id").GetString()!;

        var resolved = await client.ResolvePageResourceAsync(pageId);
        Assert.Equal("page-rendition-" + pageId, resolved.ResourceId);
        var published = Path.Combine(options.DerivedRoot, "pages", resolved.ResourceId + ".png");
        Assert.True(File.Exists(published), "referenced resolve must publish a derived PNG rendition");
        Assert.NotEqual(sourceDigest, Convert.ToHexString(SHA256.HashData(await File.ReadAllBytesAsync(published))).ToLowerInvariant());

        var frameCommands = client.Wire.Frames
            .Select(frame =>
            {
                try
                {
                    using var document = JsonDocument.Parse(frame.RequestLine);
                    return document.RootElement.TryGetProperty("command", out var command)
                        ? command.GetString()
                        : null;
                }
                catch (JsonException)
                {
                    return null;
                }
            })
            .Where(command => !string.IsNullOrWhiteSpace(command))
            .ToArray();
        Assert.Contains("core.ping", frameCommands);
        Assert.Contains("RegisterSourceReadGrant", frameCommands);
        Assert.Contains("PlanImportReferences", frameCommands);
        Assert.Contains("StartImportReferences", frameCommands);
        Assert.Contains("GetImportReceipt", frameCommands);
        Assert.Contains("resolve_page_resource", frameCommands);

        var evidenceDir = Path.Combine(repo, "verification", "FEA-09", "ipc");
        Directory.CreateDirectory(evidenceDir);
        var evidence = new JsonObject
        {
            ["generated_at"] = DateTimeOffset.UtcNow.ToString("O"),
            ["mode"] = "real Host<->Core stdio (python source process)",
            ["python"] = python,
            ["source_file_sha256"] = sourceDigest,
            ["grant_id"] = grantId,
            ["chapter_id"] = chapterId,
            ["plan_id"] = planId,
            ["plan_digest"] = planDigest,
            ["operation_id"] = operationId,
            ["receipt_state"] = receipt.GetProperty("state").GetString(),
            ["page_id"] = pageId,
            ["resource_id"] = resolved.ResourceId,
            ["published_png_sha256"] = Convert.ToHexString(
                SHA256.HashData(await File.ReadAllBytesAsync(published))).ToLowerInvariant(),
            ["wire_frame_count"] = client.Wire.Frames.Count,
            ["wire_commands"] = new JsonArray(frameCommands.Select(command =>
                (JsonNode)JsonValue.Create(command)!).ToArray()),
        };
        await File.WriteAllTextAsync(
            Path.Combine(evidenceDir, "fea09-real-ipc.json"),
            evidence.ToJsonString(new JsonSerializerOptions { WriteIndented = true }));
        await File.WriteAllTextAsync(
            Path.Combine(evidenceDir, "fea09-real-ipc.wire.ndjson"),
            string.Join(Environment.NewLine, client.Wire.Frames.Select(frame => frame.RequestLine)));
    }

    private sealed class PythonIpcFactAttribute : FactAttribute
    {
        public PythonIpcFactAttribute()
        {
            if (Environment.GetEnvironmentVariable("NEWMANGA_FEA09_IPC") != "1")
            {
                Skip = "reason: set NEWMANGA_FEA09_IPC=1 to run the real Python-source Core stdio IPC test";
            }
        }
    }

    private static string FindRepository()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
        {
            directory = directory.Parent;
        }
        return directory?.FullName ?? throw new InvalidOperationException("repository not found");
    }
}
