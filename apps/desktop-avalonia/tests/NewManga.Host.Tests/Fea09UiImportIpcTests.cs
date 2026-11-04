using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using NewManga.App.Services;
using NewManga.CoreClient;
using NewManga.CoreClient.Commands;
using NewManga.Host.Sources;
using Xunit;
using Xunit.Abstractions;
using Xunit.Sdk;

namespace NewManga.Host.Tests;

/// <summary>
/// FEA-09-UI-1 AC-1…AC-4: the ImportDock's referenced-import flow over REAL Python Core stdio.
/// The chain is exactly the production one the App uses: <c>CoreServiceClient</c> (real child
/// process) → <c>HostCommandDispatcher</c> (Host-local routing, mirroring
/// HostRuntime.HostLocalAsync) → <c>SourceReadCoordinator</c> (registry/grants/Secret-G) →
/// the App's production <see cref="SourceImportCoordinator"/> (the class behind the
/// ISourceImportController.Plan/Start/Receipt/Cancel face — kept OUTSIDE the frozen C-07
/// IHostController inventory). No fake controller, no in-process substitute;
/// assertions are on the UI-facing models (plan preview, receipt counts, typed reasons).
/// </summary>
[TestCaseOrderer("NewManga.Host.Tests.Fea09UiImportIpcTests+AlphabeticalOrderer", "NewManga.Host.Tests")]
public sealed class Fea09UiImportIpcTests : IClassFixture<Fea09UiImportIpcTests.Fea09UiIpcContext>
{
    /// <summary>
    /// The evidence writer runs LAST so it audits the session's full wire history; xunit's
    /// default order is discovery order, so the class pins an explicit alphabetical order.
    /// </summary>
    public sealed class AlphabeticalOrderer : ITestCaseOrderer
    {
        public IEnumerable<TTestCase> OrderTestCases<TTestCase>(IEnumerable<TTestCase> testCases)
            where TTestCase : ITestCase =>
            testCases.OrderBy(testCase => testCase.TestMethod.Method.Name, StringComparer.Ordinal);
    }

    /// <summary>
    /// Skip unless NEWMANGA_FEA09_IPC=1 (same gate as Fea09RealIpcTests) — one real Python Core
    /// child process shared by the whole class (IClassFixture), like one Host session.
    /// </summary>
    private sealed class UiIpcFactAttribute : FactAttribute
    {
        public UiIpcFactAttribute()
        {
            if (Environment.GetEnvironmentVariable("NEWMANGA_FEA09_IPC") != "1")
            {
                Skip = "reason: set NEWMANGA_FEA09_IPC=1 to run the real Python-source Core stdio IPC test";
            }
        }
    }

    private const string OnePixelPngBase64 =
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";

    // Frozen FEA-09 fixture (tests/fea09/fixtures/FIXTURES.md) — the password is part of the
    // public fixture record; it must still never appear in wire frames, logs or evidence.
    private const string ZipCryptoPassword = "fea09-fixture";

    private readonly Fea09UiIpcContext _context;

    public Fea09UiImportIpcTests(Fea09UiIpcContext context)
    {
        _context = context;
    }

    public sealed class Fea09UiIpcContext : IAsyncLifetime
    {
        public CoreServiceClient Client { get; private set; } = null!;

        public SourceImportCoordinator Imports { get; private set; } = null!;

        public string Root { get; private set; } = null!;

        public List<JsonObject> Evidence { get; } = new();

        public async Task InitializeAsync()
        {
            var python = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? "python";
            Root = Directory.CreateDirectory(Path.Combine(
                FindRepository() + ".workspace", "FEA-09-UI-1", "ipc-" + Guid.NewGuid().ToString("N"))).FullName;
            var dataRoot = Path.Combine(Root, "data");
            Directory.CreateDirectory(dataRoot);

            var options = new CoreServiceOptions
            {
                ExecutablePath = python,
                AdditionalArguments =
                [
                    "-X", "utf8", "-c",
                    $"import sys;sys.path.insert(0, r'{Path.Combine(FindRepository(), "src")}');import bootstrap.core_service as m;raise SystemExit(m.main())",
                ],
                DataRoot = dataRoot,
                DerivedRoot = Path.Combine(dataRoot, "derived"),
                CatalogDbPath = Path.Combine(dataRoot, "catalog", "catalog.sqlite"),
                StderrLogPath = Path.Combine(Root, "core.stderr.log"),
                WireLogPath = Path.Combine(Root, "wire.ndjson"),
                StartupTimeout = TimeSpan.FromSeconds(90),
                RequestTimeout = TimeSpan.FromSeconds(90),
            };

            Client = await CoreServiceClient.StartAsync(options);
            await Client.OpenHostSessionAsync();
            var ping = await Client.PingAsync();
            Assert.True(ping.Ready, "core must be ready");
            Assert.Contains("source.read/1", ping.Capabilities);
            Assert.Contains("source.resolve-secret/1", ping.Capabilities);

            var registry = new SourceAccessRegistry(Path.Combine(Root, "host-data"));
            var sources = new SourceReadCoordinator(Client, registry, () => true);
            // HostRuntime.HostLocalAsync routes the SourceCommandNames onto the coordinator; that
            // exact production routing is replicated here (the runtime itself needs sidecars).
            HostCommandDispatcher dispatcher = new(
                Client,
                bridge: null,
                hostLocal: async (name, payload, token) => new HostCommandResult(
                    name,
                    HostCommandStatus.Implemented,
                    HostCommandChannel.HostLocal,
                    await sources.InvokeAsync(name, payload, token)));
            Imports = new SourceImportCoordinator(dispatcher, sources, Root);
        }

        public async Task DisposeAsync()
        {
            if (Imports is not null)
            {
                await Imports.DisposeAsync();
            }

            if (Client is not null)
            {
                await Client.DisposeAsync();
            }
        }
    }

    private static string Repo => FindRepository();

    private async Task<(string BookId, string ChapterId)> CreateChapterAsync(string title)
    {
        var book = await _context.Client.CreateBookAsync("FEA-09-UI-1 " + title);
        var chapter = await _context.Client.SendAsync(
            "CreateChapter", 8,
            writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("book_id", book.BookId);
                writer.WriteString("title", title);
                writer.WriteEndObject();
            },
            TimeSpan.FromSeconds(30));
        return (book.BookId, chapter.Result!.Value.GetProperty("chapter_id").GetString()!);
    }

    private async Task<SourceImportReceipt> AwaitTerminalAsync(string operationId)
    {
        var deadline = DateTime.UtcNow + TimeSpan.FromSeconds(60);
        while (DateTime.UtcNow < deadline)
        {
            var receipt = await _context.Imports.GetReceiptAsync(operationId, CancellationToken.None);
            Assert.NotNull(receipt);
            if (receipt!.IsTerminal)
            {
                return receipt;
            }

            await Task.Delay(100);
        }

        throw new TimeoutException("import did not reach a terminal state");
    }

    private static async Task<string> WritePngAsync(string directory, string name)
    {
        Directory.CreateDirectory(directory);
        var path = Path.Combine(directory, name);
        await File.WriteAllBytesAsync(path, Convert.FromBase64String(OnePixelPngBase64));
        return path;
    }

    // ------------------------------------------------------------- AC-1/AC-4: plan + confirm

    [UiIpcFact]
    public async Task PlanPreviewConfirmAndReceiptOverRealStdio()
    {
        var (_, chapterId) = await CreateChapterAsync("plan-confirm");
        var sourceFile = await WritePngAsync(Path.Combine(_context.Root, "source"), "page.png");

        var plan = await _context.Imports.PlanAsync(chapterId, [new ReferenceImportSource(sourceFile, IsFolder: false)], "skip", CancellationToken.None);
        Assert.NotNull(plan);
        Assert.False(plan!.NeedsPassword);
        Assert.Equal(1, plan.Totals.Import);
        var item = Assert.Single(plan.Items);
        Assert.Equal("page.png", item.DisplayName);
        Assert.Equal("ok", item.Status);
        Assert.Equal(1, item.WillImport);

        var start = await _context.Imports.StartAsync(plan, password: null, CancellationToken.None);
        Assert.True(start.Ok, start.ErrorCode + " " + start.Message);
        var receipt = await AwaitTerminalAsync(start.OperationId!);
        Assert.Equal(SourceImportOperationState.Completed, receipt.State);
        Assert.Equal(1, receipt.Totals.ImportedPages);
        Assert.Equal(0, receipt.Totals.PendingPages);
        Assert.Equal("imported", Assert.Single(receipt.Items).Outcome);

        // the UI refresh face really sees the committed page
        var pages = await _context.Client.ListChapterPagesAsync(chapterId, CancellationToken.None);
        Assert.Single(pages);

        _context.Evidence.Add(new JsonObject
        {
            ["case"] = "plan-confirm",
            ["chapter_id"] = chapterId,
            ["plan_totals"] = plan.Totals.Import,
            ["receipt_state"] = receipt.State.ToString(),
            ["imported_pages"] = receipt.Totals.ImportedPages,
            ["chapter_pages_visible"] = pages.Count,
        });
    }

    // ------------------------------------------------------------- AC-1/AC-4: AES ZIP typed unsupported

    [UiIpcFact]
    public async Task AesZipPlanIsTypedUnsupportedOverRealStdio()
    {
        var (_, chapterId) = await CreateChapterAsync("aes-unsupported");
        var aes = Path.Combine(Repo, "tests", "fea09", "fixtures", "aes_member.zip");
        Assert.True(File.Exists(aes), "frozen AES fixture must exist");

        var plan = await _context.Imports.PlanAsync(chapterId, [new ReferenceImportSource(aes, IsFolder: false)], "skip", CancellationToken.None);
        Assert.NotNull(plan);
        var item = Assert.Single(plan!.Items);
        Assert.Equal("unsupported", item.Status);
        Assert.Equal("SOURCE_FORMAT_UNSUPPORTED", item.ReasonCode);
        Assert.Equal(0, item.WillImport);
        Assert.Equal(1, plan.Totals.Unsupported);
        // UI text renders the typed reason; no password is asked for an AES member
        Assert.Contains("格式不支持", SourceImportText.PlanStatus(item.Status, item.ReasonCode));
        Assert.False(plan.NeedsPassword);

        _context.Evidence.Add(new JsonObject
        {
            ["case"] = "aes-unsupported",
            ["status"] = item.Status,
            ["reason_code"] = item.ReasonCode,
            ["needs_password"] = plan.NeedsPassword,
        });
    }

    // ------------------------------------------------------------- AC-2: encrypted CBZ via one-shot password

    [UiIpcFact]
    public async Task EncryptedZipPasswordRetryOverRealStdio()
    {
        var (_, chapterId) = await CreateChapterAsync("zipcrypto");
        var cbz = Path.Combine(Repo, "tests", "fea09", "fixtures", "zipcrypto_page.cbz");
        Assert.True(File.Exists(cbz), "frozen ZipCrypto fixture must exist");

        // plan detects encryption without ever asking for the password
        var plan = await _context.Imports.PlanAsync(chapterId, [new ReferenceImportSource(cbz, IsFolder: false)], "skip", CancellationToken.None);
        Assert.NotNull(plan);
        Assert.True(plan!.NeedsPassword);
        var encrypted = Assert.Single(plan.Items);
        Assert.Equal("encrypted", encrypted.Status);
        Assert.Null(encrypted.WillImport);

        // wrong password → typed failure, nothing committed
        var wrong = await _context.Imports.StartAsync(plan, password: "definitely-wrong", CancellationToken.None);
        Assert.True(wrong.Ok);
        var failed = await AwaitTerminalAsync(wrong.OperationId!);
        Assert.Equal(SourceImportOperationState.Failed, failed.State);
        Assert.Equal("SOURCE_PASSWORD_INVALID", Assert.Single(failed.Items).ReasonCode);
        Assert.Equal(0, failed.Totals.ImportedPages);
        var noPages = await _context.Client.ListChapterPagesAsync(chapterId, CancellationToken.None);
        Assert.Empty(noPages);

        // retry with the right password = a FRESH plan (natural keys: still nothing committed)
        var retryPlan = await _context.Imports.PlanAsync(chapterId, [new ReferenceImportSource(cbz, IsFolder: false)], "skip", CancellationToken.None);
        Assert.NotNull(retryPlan);
        var right = await _context.Imports.StartAsync(retryPlan!, password: ZipCryptoPassword, CancellationToken.None);
        Assert.True(right.Ok, right.ErrorCode + " " + right.Message);
        var done = await AwaitTerminalAsync(right.OperationId!);
        Assert.Equal(SourceImportOperationState.Completed, done.State);
        Assert.Equal(2, done.Totals.ImportedPages);
        var pages = await _context.Client.ListChapterPagesAsync(chapterId, CancellationToken.None);
        Assert.Equal(2, pages.Count);

        // the one-shot token is gone (Core consumes it once; the host cleans any remainder)
        var secrets = Path.Combine(_context.Root, "host", "source-secrets");
        Assert.True(!Directory.Exists(secrets) || Directory.GetFiles(secrets, "*.bin").Length == 0,
            "no one-shot password token may survive the import");

        _context.Evidence.Add(new JsonObject
        {
            ["case"] = "zipcrypto-password",
            ["plan_status"] = encrypted.Status,
            ["wrong_password_reason"] = Assert.Single(failed.Items).ReasonCode,
            ["wrong_password_imported"] = failed.Totals.ImportedPages,
            ["retry_state"] = done.State.ToString(),
            ["retry_imported_pages"] = done.Totals.ImportedPages,
            ["retry_chapter_pages"] = pages.Count,
            ["secret_tokens_remaining"] = Directory.Exists(secrets)
                ? Directory.GetFiles(secrets, "*.bin").Length
                : 0,
        });
    }

    // ------------------------------------------------------------- AC-3: cancel keeps committed pages only

    [UiIpcFact]
    public async Task CancelKeepsCommittedPagesOverRealStdio()
    {
        var (_, chapterId) = await CreateChapterAsync("cancel");
        var directory = Path.Combine(_context.Root, "source-folder");
        for (var index = 1; index <= 5; index++)
        {
            await WritePngAsync(directory, $"p{index}.png");
        }

        var plan = await _context.Imports.PlanAsync(chapterId, [new ReferenceImportSource(directory, IsFolder: true)], "skip", CancellationToken.None);
        Assert.NotNull(plan);
        Assert.Equal(5, plan!.Totals.Import);

        var start = await _context.Imports.StartAsync(plan, password: null, CancellationToken.None);
        Assert.True(start.Ok, start.ErrorCode + " " + start.Message);

        // A cancel on a terminal operation is the protocol's frozen accepted:false path; a
        // cancel that lands mid-run is accepted:true. Both are exercised depending on timing —
        // the invariant under test is that only COMMITTED pages ever become visible.
        var receipt = await AwaitTerminalAsync(start.OperationId!);
        var late = await _context.Imports.CancelAsync(start.OperationId!, CancellationToken.None);
        Assert.True(late.Ok);
        Assert.False(late.Accepted);
        Assert.Equal("completed", late.State);

        var pages = await _context.Client.ListChapterPagesAsync(chapterId, CancellationToken.None);
        Assert.Equal(receipt.Totals.ImportedPages, pages.Count);
        Assert.Equal(receipt.Totals.ImportedPages, receipt.CommittedBoundary);

        // mid-run cancel path: a second, larger import whose cancel fires right after accept
        // (the poller itself proves the UI can always observe state; whatever the race outcome,
        // the visible pages must equal the committed boundary).
        var directory2 = Path.Combine(_context.Root, "source-folder-2");
        for (var index = 1; index <= 5; index++)
        {
            await WritePngAsync(directory2, $"q{index}.png");
        }

        var plan2 = await _context.Imports.PlanAsync(chapterId, [new ReferenceImportSource(directory2, IsFolder: true)], "skip", CancellationToken.None);
        Assert.NotNull(plan2);
        var start2 = await _context.Imports.StartAsync(plan2!, password: null, CancellationToken.None);
        Assert.True(start2.Ok);
        var cancelled = await _context.Imports.CancelAsync(start2.OperationId!, CancellationToken.None);
        Assert.True(cancelled.Ok, cancelled.ErrorCode);
        var receipt2 = await AwaitTerminalAsync(start2.OperationId!);
        Assert.Contains(receipt2.State.ToString(), new[] { "Cancelled", "Completed" });
        if (receipt2.State == SourceImportOperationState.Cancelled)
        {
            // a cancel that landed before the terminal state is always accepted (C-16 §4)
            Assert.True(cancelled.Accepted);
        }
        var pages2 = await _context.Client.ListChapterPagesAsync(chapterId, CancellationToken.None);
        Assert.Equal(receipt.Totals.ImportedPages + receipt2.Totals.ImportedPages, pages2.Count);

        _context.Evidence.Add(new JsonObject
        {
            ["case"] = "cancel",
            ["planned_pages"] = 5,
            ["terminal_cancel_accepted"] = late.Accepted,
            ["terminal_cancel_state"] = late.State,
            ["first_imported"] = receipt.Totals.ImportedPages,
            ["midrun_cancel_accepted"] = cancelled.Accepted,
            ["midrun_state"] = receipt2.State.ToString(),
            ["second_imported"] = receipt2.Totals.ImportedPages,
            ["chapter_pages_total"] = pages2.Count,
        });
    }

    // ------------------------------------------------------------- evidence + password audit (AC-4)

    [UiIpcFact]
    public async Task WriteEvidenceAndAssertZeroPasswordLeakage()
    {
        // Runs last (alphabetical orderer): audits the whole class session's wire history.
        var evidenceDir = Path.Combine(Repo, "verification", "FEA-09-UI-1", "ipc");
        Directory.CreateDirectory(evidenceDir);

        var wireLines = _context.Client.Wire.Frames.Select(frame => frame.RequestLine).ToArray();
        var probes = PasswordProbes(ZipCryptoPassword);
        Assert.All(wireLines, line => Assert.DoesNotContain(probes, probe => line.Contains(probe, StringComparison.OrdinalIgnoreCase)));

        var stderr = File.Exists(Path.Combine(_context.Root, "core.stderr.log"))
            ? await File.ReadAllTextAsync(Path.Combine(_context.Root, "core.stderr.log"))
            : string.Empty;
        Assert.DoesNotContain(probes, probe => stderr.Contains(probe, StringComparison.OrdinalIgnoreCase));

        var evidenceJson = JsonSerializer.Serialize(
            new JsonObject
            {
                ["generated_at"] = DateTimeOffset.UtcNow.ToString("O"),
                ["mode"] = "real Host<->Core stdio (python source process) + production SourceImportCoordinator",
                ["python"] = "NEWMANGA_BUILD_PYTHON (path redacted)",
                ["password_probe_sha256"] = Convert.ToHexString(
                    SHA256.HashData(Encoding.UTF8.GetBytes(ZipCryptoPassword))).ToLowerInvariant(),
                ["wire_frame_count"] = _context.Client.Wire.Frames.Count,
                ["cases"] = new JsonArray(_context.Evidence.Select(node => (JsonNode)node.DeepClone()).ToArray()),
            },
            new JsonSerializerOptions { WriteIndented = true });
        Assert.DoesNotContain(probes, probe => evidenceJson.Contains(probe, StringComparison.OrdinalIgnoreCase));

        var wire = string.Join(Environment.NewLine, wireLines);
        Assert.DoesNotContain(probes, probe => wire.Contains(probe, StringComparison.OrdinalIgnoreCase));

        await File.WriteAllTextAsync(Path.Combine(evidenceDir, "ui-import-ipc.json"), evidenceJson);
        await File.WriteAllTextAsync(Path.Combine(evidenceDir, "ui-import-ipc.wire.ndjson"), wire);

        // the command faces the dock uses really went over the wire
        var commands = wireLines.Select(line =>
        {
            try
            {
                using var document = JsonDocument.Parse(line);
                return document.RootElement.TryGetProperty("command", out var command) ? command.GetString() : null;
            }
            catch (JsonException)
            {
                return null;
            }
        }).Where(command => !string.IsNullOrWhiteSpace(command)).ToArray();
        Assert.Contains("RegisterSourceReadGrant", commands);
        Assert.Contains("PlanImportReferences", commands);
        Assert.Contains("StartImportReferences", commands);
        Assert.Contains("GetImportReceipt", commands);
        Assert.Contains("CancelImport", commands);
    }

    /// <summary>The password literal plus its UTF-8 hex and base64 encodings (C-16 §3 audit shape).</summary>
    private static List<string> PasswordProbes(string password)
    {
        var bytes = Encoding.UTF8.GetBytes(password);
        return
        [
            password,
            Convert.ToHexString(bytes).ToLowerInvariant(),
            Convert.ToHexString(bytes),
            Convert.ToBase64String(bytes),
        ];
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
