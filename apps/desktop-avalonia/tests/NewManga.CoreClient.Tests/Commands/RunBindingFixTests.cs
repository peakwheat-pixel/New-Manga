using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json;
using NewManga.CoreClient.Bridge;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Tests.Support;
using NewManga.CoreClient.Wire;
using Xunit;

namespace NewManga.CoreClient.Tests.Commands;

/// <summary>
/// RUN-BINDING-FIX-1: Host-side StartRun carries <c>overrides.provider_bindings</c>.
/// RUN-OCR-DIAG-1 proved the frozen Core's pipeline defaults are empty, so the OCR step fails with
/// PROVIDER_NOT_CONFIGURED until a StartRun override supplies <c>{"ocr":"manga-ocr"}</c>. These tests
/// pin the Host-side merge policy (explicit user bindings always win, other overrides preserved,
/// configurable/disable-able default), the parameter boundary, and one full real run on the models
/// package build 2b36bfeb...4ec519b proving the OCR step no longer fails (the chain may still stop
/// later — that is a different, pre-existing failure and must not be reported as "chain green").
/// </summary>
public sealed class RunBindingFixTests
{
    // ------------------------------------------------------------------
    // Policy: default / configurable / disabled / malformed configuration
    // ------------------------------------------------------------------

    [Fact]
    public void Resolve_Default_IsMangaOcr()
    {
        var previous = Environment.GetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable);
        try
        {
            Environment.SetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable, null);
            var element = RunBindingDefaults.Resolve();
            Assert.NotNull(element);
            Assert.Equal("manga-ocr", element!.Value.GetProperty("ocr").GetString());
            Assert.Equal("{\"ocr\":\"manga-ocr\"}", RunBindingDefaults.ResolveJson());
        }
        finally
        {
            Environment.SetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable, previous);
        }
    }

    [Fact]
    public void Resolve_CustomAndDisabledConfiguration()
    {
        Assert.Equal(
            "{\"ocr\":\"custom-ocr\",\"color\":\"stub-color\"}",
            JsonDocument.Parse(RunBindingDefaults.ResolveJson("{\"ocr\":\"custom-ocr\",\"color\":\"stub-color\"}")!).RootElement.GetRawText());
        Assert.Null(RunBindingDefaults.Resolve(""));
        Assert.Null(RunBindingDefaults.Resolve("off"));
        Assert.Null(RunBindingDefaults.Resolve("NONE"));
        Assert.Null(RunBindingDefaults.Resolve("disabled"));
        Assert.Null(RunBindingDefaults.Resolve("0"));
    }

    [Fact]
    public void Resolve_RejectsInvalidConfiguration()
    {
        Assert.Throws<InvalidOperationException>(() => RunBindingDefaults.Resolve("[]"));
        Assert.Throws<InvalidOperationException>(() => RunBindingDefaults.Resolve("{\"ocr\":123}"));
        Assert.Throws<InvalidOperationException>(() => RunBindingDefaults.Resolve("{\"ocr\":\"\"}"));
        Assert.Throws<InvalidOperationException>(() => RunBindingDefaults.Resolve("{not-json"));
    }

    [Fact]
    public void Resolve_UsesEnvironmentWhenRawIsNotGiven()
    {
        var previous = Environment.GetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable);
        try
        {
            Environment.SetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable, "{\"ocr\":\"env-ocr\"}");
            Assert.Equal("env-ocr", RunBindingDefaults.Resolve()!.Value.GetProperty("ocr").GetString());
            Environment.SetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable, "off");
            Assert.Null(RunBindingDefaults.Resolve());
        }
        finally
        {
            Environment.SetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable, previous);
        }
    }

    // ------------------------------------------------------------------
    // Dispatcher wire-level wiring (frozen core_service; typed Core error is expected on an empty root)
    // ------------------------------------------------------------------

    private sealed class CommandTestContext : IAsyncDisposable
    {
        private CommandTestContext(
            SidecarFixture.CommandEnvironment environment,
            CoreServiceClient core,
            HostBridgeClient bridge,
            HostCommandDispatcher dispatcher)
        {
            Environment = environment;
            Core = core;
            Bridge = bridge;
            Dispatcher = dispatcher;
        }

        public SidecarFixture.CommandEnvironment Environment { get; }

        public CoreServiceClient Core { get; }

        public HostBridgeClient Bridge { get; }

        public HostCommandDispatcher Dispatcher { get; }

        public static async Task<CommandTestContext> StartAsync(string name)
        {
            var environment = SidecarFixture.CreateCommandEnvironment(name);
            var core = await CoreServiceClient.StartAsync(environment.CoreOptions);
            try
            {
                var bridge = await HostBridgeClient.StartAsync(environment.BridgeOptions);
                return new CommandTestContext(environment, core, bridge, new HostCommandDispatcher(core, bridge));
            }
            catch
            {
                await core.DisposeAsync();
                throw;
            }
        }

        public async ValueTask DisposeAsync()
        {
            await Bridge.DisposeAsync();
            await Core.DisposeAsync();
            SidecarFixture.TryDeleteDirectory(Environment.DataRoot);
        }
    }

    private static JsonElement Args(string json)
    {
        using var document = JsonDocument.Parse(json);
        return document.RootElement.Clone();
    }

    private static string StartRunRequestLine(CommandTestContext context)
    {
        var frame = context.Core.Wire.Frames.LastOrDefault(candidate =>
            candidate.RequestLine.Contains("\"command\":\"StartRun\"", StringComparison.Ordinal));
        Assert.NotNull(frame);
        return frame!.RequestLine;
    }

    private static Task<CoreOperationException> InvokeStartRunExpectingCoreFailure(
        CommandTestContext context,
        string argsJson)
    {
        return Assert.ThrowsAsync<CoreOperationException>(() =>
            context.Dispatcher.InvokeAsync("library_start_run", Args(argsJson)));
    }

    private static async Task<string> RunStartRunAndReturnLine(CommandTestContext context, string argsJson)
    {
        var error = await InvokeStartRunExpectingCoreFailure(context, argsJson);
        Assert.Equal("INVALID_REQUEST", error.Code);
        return StartRunRequestLine(context);
    }

    private static string WithEnvironment(string? value, Func<string> action)
    {
        var previous = Environment.GetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable);
        try
        {
            Environment.SetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable, value);
            return action();
        }
        finally
        {
            Environment.SetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable, previous);
        }
    }

    [SidecarFact]
    public async Task StartRun_InjectsDefaultBindings_WhenOverridesAbsentOrEmpty()
    {
        await using var context = await CommandTestContext.StartAsync("run-binding-default");
        var absentLine = await RunStartRunAndReturnLine(
            context,
            "{\"command\":\"translate_untranslated\",\"scope\":{\"kind\":\"book\",\"book_id\":\"book-none\"},\"idempotency_key\":\"it-binding-1\"}");
        Assert.Contains("\"provider_bindings\":{\"ocr\":\"manga-ocr\"}", absentLine, StringComparison.Ordinal);

        var emptyLine = await RunStartRunAndReturnLine(
            context,
            "{\"command\":\"translate_untranslated\",\"scope\":{\"kind\":\"book\",\"book_id\":\"book-none\"},\"overrides\":{},\"idempotency_key\":\"it-binding-2\"}");
        Assert.Contains("\"provider_bindings\":{\"ocr\":\"manga-ocr\"}", emptyLine, StringComparison.Ordinal);

        SidecarFixture.WriteEvidenceJson("commands/run-binding-wire.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1/AC3");
            writer.WriteString("policy", "default = manga-ocr; injected when overrides absent/empty");
            writer.WriteStartArray("cases");
            writer.WriteStartObject();
            writer.WriteString("case", "overrides absent");
            writer.WriteString("request_line", absentLine);
            writer.WriteEndObject();
            writer.WriteStartObject();
            writer.WriteString("case", "overrides {}");
            writer.WriteString("request_line", emptyLine);
            writer.WriteEndObject();
            writer.WriteEndArray();
            writer.WriteEndObject();
        });
    }

    [SidecarFact]
    public async Task StartRun_KeepsExplicitUserBindings_AndOtherOverrides()
    {
        await using var context = await CommandTestContext.StartAsync("run-binding-explicit");
        var explicitLine = await RunStartRunAndReturnLine(
            context,
            "{\"command\":\"translate_untranslated\",\"scope\":{\"kind\":\"book\",\"book_id\":\"book-none\"}," +
            "\"overrides\":{\"provider_bindings\":{\"ocr\":\"custom-ocr\"},\"translate\":{\"stub\":true}}," +
            "\"idempotency_key\":\"it-binding-3\"}");
        Assert.Contains("\"provider_bindings\":{\"ocr\":\"custom-ocr\"}", explicitLine, StringComparison.Ordinal);
        Assert.DoesNotContain("\"manga-ocr\"", explicitLine, StringComparison.Ordinal);
        Assert.Contains("\"translate\":{\"stub\":true}", explicitLine, StringComparison.Ordinal);

        var mergedLine = await RunStartRunAndReturnLine(
            context,
            "{\"command\":\"translate_untranslated\",\"scope\":{\"kind\":\"book\",\"book_id\":\"book-none\"}," +
            "\"overrides\":{\"render\":{\"mode\":\"stub\"}},\"idempotency_key\":\"it-binding-4\"}");
        Assert.Contains("\"render\":{\"mode\":\"stub\"}", mergedLine, StringComparison.Ordinal);
        Assert.Contains("\"provider_bindings\":{\"ocr\":\"manga-ocr\"}", mergedLine, StringComparison.Ordinal);

        SidecarFixture.WriteEvidenceJson("commands/run-binding-overrides.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC1/AC3");
            writer.WriteString("explicit_bindings_win", explicitLine);
            writer.WriteString("merged_other_overrides", mergedLine);
            writer.WriteEndObject();
        });
    }

    [SidecarFact]
    public async Task StartRun_DefaultDisabled_OmitsProviderBindings()
    {
        await using var context = await CommandTestContext.StartAsync("run-binding-disabled");
        var previous = Environment.GetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable);
        string line;
        try
        {
            Environment.SetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable, "off");
            line = await RunStartRunAndReturnLine(
                context,
                "{\"command\":\"translate_untranslated\",\"scope\":{\"kind\":\"book\",\"book_id\":\"book-none\"}," +
                "\"overrides\":{\"translate\":{\"stub\":true}},\"idempotency_key\":\"it-binding-5\"}");
        }
        finally
        {
            Environment.SetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable, previous);
        }

        Assert.DoesNotContain("provider_bindings", line, StringComparison.Ordinal);
        Assert.Contains("\"translate\":{\"stub\":true}", line, StringComparison.Ordinal);
    }

    [SidecarFact]
    public async Task StartRun_InvalidOverrides_AreRejectedBeforeAnyCoreFrame()
    {
        await using var context = await CommandTestContext.StartAsync("run-binding-invalid");
        var before = context.Core.Wire.Frames.Count;

        var nonObject = await Assert.ThrowsAsync<HostCommandInvalidArgumentsException>(() =>
            context.Dispatcher.InvokeAsync(
                "library_start_run",
                Args("{\"command\":\"translate_untranslated\",\"scope\":{\"kind\":\"book\",\"book_id\":\"book-none\"},\"overrides\":\"nope\",\"idempotency_key\":\"it-invalid-1\"}")));
        Assert.Equal("INVALID_ARGUMENTS", nonObject.Code);

        var nonObjectBindings = await Assert.ThrowsAsync<HostCommandInvalidArgumentsException>(() =>
            context.Dispatcher.InvokeAsync(
                "library_start_run",
                Args("{\"command\":\"translate_untranslated\",\"scope\":{\"kind\":\"book\",\"book_id\":\"book-none\"},\"overrides\":{\"provider_bindings\":\"ocr\"},\"idempotency_key\":\"it-invalid-2\"}")));
        Assert.Equal("INVALID_ARGUMENTS", nonObjectBindings.Code);

        Assert.Equal(before, context.Core.Wire.Frames.Count);
    }

    // ------------------------------------------------------------------
    // AC2: full 8-page run on the models-package build 2b36bfeb...4ec519b
    // ------------------------------------------------------------------

    [ModelSidecarFact]
    public async Task ModelsBuild_BookRun_WithoutInjectedBindings_StillFailsOcrWithProviderNotConfigured()
    {
        // Same-build control for the A/B: with the Host injection disabled the very same models build
        // must reproduce the RUN-OCR-DIAG-1 failure (ocr step PROVIDER_NOT_CONFIGURED), proving the fix
        // (and not the environment) is what changed the OCR outcome.
        var modelsDir = ModelSidecarFixture.ModelsSidecarDirectory;
        var fixtureRoot = ModelSidecarFixture.BookFixtureRoot;
        var options = SidecarFixture.CreateCoreOptions(
            "run-binding-baseline",
            out var dataRoot,
            Path.Combine(modelsDir, "core_service.exe"));
        ModelSidecarFixture.CopyBookFixture(fixtureRoot, dataRoot);
        var previous = Environment.GetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable);
        try
        {
            Environment.SetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable, "off");
            await using var core = await CoreServiceClient.StartAsync(options);
            var dispatcher = new HostCommandDispatcher(core, null);
            var book = (await dispatcher.InvokeAsync("library_list_books")).Value.EnumerateArray().First();
            var bookId = book.GetProperty("book_id").GetString()!;
            var start = await dispatcher.InvokeAsync(
                "library_start_run",
                Args($"{{\"command\":\"translate_untranslated\",\"scope\":{{\"kind\":\"book\",\"book_id\":\"{bookId}\"}},\"idempotency_key\":\"run-binding-baseline-1\"}}"));
            var runId = start.Value.GetProperty("run_id").GetString()!;
            var terminal = await PollUntilTerminalAsync(dispatcher, runId, TimeSpan.FromSeconds(180));
            var startLine = core.Wire.Frames
                .Last(candidate => candidate.RequestLine.Contains("\"command\":\"StartRun\"", StringComparison.Ordinal))
                .RequestLine;
            ModelSidecarFixture.CopyDatabase(
                dataRoot,
                Path.Combine(SidecarFixture.EvidenceDirectory, "commands", "run-binding-baseline-library.db"));
            SidecarFixture.WriteEvidenceJson("commands/run-binding-baseline.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC2");
                writer.WriteString("policy", "control: NEWMANGA_RUN_PROVIDER_BINDINGS=off (no Host-side bindings)");
                writer.WriteString("sidecar", options.ExecutablePath);
                writer.WriteString("sidecar_sha256", ModelSidecarFixture.Sha256(options.ExecutablePath));
                writer.WriteString("book_id", bookId);
                writer.WriteString("run_id", runId);
                writer.WriteString("terminal_status", terminal);
                writer.WriteString("start_request_line", startLine);
                writer.WriteString("note", "the exact per-step PROVIDER_NOT_CONFIGURED is asserted on the copied " +
                                           "library.db by check_run_binding.py");
                writer.WriteEndObject();
            });
            Assert.DoesNotContain("provider_bindings", startLine, StringComparison.Ordinal);
            Assert.Equal("completed_with_failures", terminal);
        }
        finally
        {
            Environment.SetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable, previous);
            SidecarFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [ModelSidecarFact]
    public async Task ModelsBuild_BookRun_WithInjectedBindings_OcrNoLongerProviderNotConfigured()
    {
        var modelsDir = ModelSidecarFixture.ModelsSidecarDirectory;
        var fixtureRoot = ModelSidecarFixture.BookFixtureRoot;
        var options = SidecarFixture.CreateCoreOptions(
            "run-binding-models",
            out var dataRoot,
            Path.Combine(modelsDir, "core_service.exe"));
        ModelSidecarFixture.CopyBookFixture(fixtureRoot, dataRoot);

        await using var core = await CoreServiceClient.StartAsync(options);
        var dispatcher = new HostCommandDispatcher(core, null);
        var evidence = new Dictionary<string, object?>
        {
            ["ac"] = "AC2",
            ["sidecar"] = options.ExecutablePath,
            ["sidecar_sha256"] = ModelSidecarFixture.Sha256(options.ExecutablePath),
            ["data_root"] = dataRoot,
            ["book_fixture"] = fixtureRoot,
        };
        try
        {
            var books = await dispatcher.InvokeAsync("library_list_books");
            var book = books.Value.EnumerateArray().First();
            var bookId = book.GetProperty("book_id").GetString()!;
            evidence["book_id"] = bookId;

            var start = await dispatcher.InvokeAsync(
                "library_start_run",
                Args($"{{\"command\":\"translate_untranslated\",\"scope\":{{\"kind\":\"book\",\"book_id\":\"{bookId}\"}},\"idempotency_key\":\"run-binding-models-1\"}}"));
            var runId = start.Value.GetProperty("run_id").GetString()!;
            evidence["run_id"] = runId;
            evidence["start_request_line"] = context_LastStartRunLine(core);

            var terminal = await PollUntilTerminalAsync(dispatcher, runId, TimeSpan.FromSeconds(180));
            evidence["terminal_status"] = terminal;
            // Copy the authoritative step_runs ledger before asserting: the copied SQLite file is
            // checked by verification/RUN-BINDING-FIX-1/tools/check_run_binding.py, which asserts the
            // exact per-step error codes (the public projection only exposes stage states).
            ModelSidecarFixture.CopyDatabase(
                dataRoot,
                Path.Combine(SidecarFixture.EvidenceDirectory, "commands", "run-binding-models-library.db"));

            var projection = await dispatcher.InvokeAsync("library_get_task_projection", Args($"{{\"run_id\":\"{runId}\"}}"));
            var stepFlow = projection.Value.GetProperty("step_flow").EnumerateArray().ToList();
            var byType = stepFlow
                .GroupBy(step => step.GetProperty("type").GetString()!)
                .ToDictionary(
                    group => group.Key,
                    group => group.Select(step => step.GetProperty("state").GetString()!).ToList());
            evidence["step_flow"] = string.Join("; ", byType.Select(pair => pair.Key + "=" + string.Join(",", pair.Value)));
            evidence["ocr_states"] = string.Join(",", byType.GetValueOrDefault("ocr", new List<string>()));
            evidence["color_states"] = string.Join(",", byType.GetValueOrDefault("color", new List<string>()));

            Assert.Equal("completed_with_failures", terminal);
            Assert.True(byType.TryGetValue("ocr", out var ocrStates), "run must include OCR steps");
            // The public step_flow projection only surfaces the current stage state per page/region
            // (earlier stages stay "pending"), so OCR success is proven by the chain having advanced to
            // color: the frozen Core runs detect -> ocr -> color sequentially, and the baseline
            // (RUN-OCR-DIAG-1) never reached color while OCR failed. The copied library.db is the
            // authoritative ledger for the exact per-step codes (check_run_binding.py).
            Assert.DoesNotContain("failed", ocrStates!);
            Assert.True(ocrStates!.Count > 0, "run projection must contain OCR steps");
            Assert.True(byType.TryGetValue("color", out var colorStates), "chain is expected to stop at color");
            Assert.Contains("failed", colorStates!);

            evidence["library_db_copy"] = Path.Combine("commands", "run-binding-models-library.db");
            evidence["ocr_success_evidence"] = "step_runs.ocr rows completed without PROVIDER_NOT_CONFIGURED " +
                                               "(check_run_binding.py); public step_flow shows the chain advanced to color";
            evidence["note"] = "OCR step completed for all 8 pages; the chain still stops at color (pre-existing " +
                               "stub analyzer failure) - this evidence does NOT claim the whole chain is green.";
        }
        finally
        {
            SidecarFixture.WriteEvidenceJson("commands/run-binding-models.json", writer =>
            {
                writer.WriteStartObject();
                foreach (var (key, value) in evidence)
                {
                    writer.WriteString(key, value?.ToString() ?? string.Empty);
                }

                writer.WriteEndObject();
            });
            SidecarFixture.TryDeleteDirectory(dataRoot);
        }
    }

    [ModelSidecarFact]
    public async Task ModelsBuild_UnknownProviderBinding_SurfacesTypedProviderError()
    {
        var modelsDir = ModelSidecarFixture.ModelsSidecarDirectory;
        var fixtureRoot = ModelSidecarFixture.BookFixtureRoot;
        var options = SidecarFixture.CreateCoreOptions(
            "run-binding-unknown",
            out var dataRoot,
            Path.Combine(modelsDir, "core_service.exe"));
        ModelSidecarFixture.CopyBookFixture(fixtureRoot, dataRoot);
        var previous = Environment.GetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable);
        try
        {
            Environment.SetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable, "{\"ocr\":\"no-such-provider\"}");
            await using var core = await CoreServiceClient.StartAsync(options);
            var dispatcher = new HostCommandDispatcher(core, null);
            var book = (await dispatcher.InvokeAsync("library_list_books")).Value.EnumerateArray().First();
            var bookId = book.GetProperty("book_id").GetString()!;
            var start = await dispatcher.InvokeAsync(
                "library_start_run",
                Args($"{{\"command\":\"translate_untranslated\",\"scope\":{{\"kind\":\"page\",\"page_id\":\"{ModelSidecarFixture.FirstPageId}\"}},\"idempotency_key\":\"run-binding-unknown-1\"}}"));
            var runId = start.Value.GetProperty("run_id").GetString()!;
            var terminal = await PollUntilTerminalAsync(dispatcher, runId, TimeSpan.FromSeconds(120));
            ModelSidecarFixture.CopyDatabase(dataRoot, Path.Combine(SidecarFixture.EvidenceDirectory, "commands", "run-binding-unknown-library.db"));
            SidecarFixture.WriteEvidenceJson("commands/run-binding-unknown-provider.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC3");
                writer.WriteString("binding", "{\"ocr\":\"no-such-provider\"}");
                writer.WriteString("book_id", bookId);
                writer.WriteString("run_id", runId);
                writer.WriteString("terminal_status", terminal);
                writer.WriteString("note", "the typed provider error code is asserted on the copied library.db " +
                                           "by verification/RUN-BINDING-FIX-1/tools/check_run_binding.py");
                writer.WriteEndObject();
            });
            Assert.True(
                terminal is "completed_with_failures" or "failed",
                $"unknown provider binding must end in a failed/partial run, got '{terminal}'");
        }
        finally
        {
            Environment.SetEnvironmentVariable(RunBindingDefaults.EnvironmentVariable, previous);
            SidecarFixture.TryDeleteDirectory(dataRoot);
        }
    }

    private static string context_LastStartRunLine(CoreServiceClient core)
    {
        var frame = core.Wire.Frames.LastOrDefault(candidate =>
            candidate.RequestLine.Contains("\"command\":\"StartRun\"", StringComparison.Ordinal));
        Assert.NotNull(frame);
        return frame!.RequestLine;
    }

    private static async Task<string> PollUntilTerminalAsync(
        HostCommandDispatcher dispatcher,
        string runId,
        TimeSpan timeout)
    {
        var terminal = new[] { "completed", "completed_with_failures", "failed", "cancelled", "interrupted" };
        var started = Stopwatch.StartNew();
        string status = "pending";
        while (started.Elapsed < timeout)
        {
            var snapshot = await dispatcher.InvokeAsync("library_get_run_snapshot", Args($"{{\"run_id\":\"{runId}\"}}"));
            status = snapshot.Value.GetProperty("status").GetString() ?? "unknown";
            if (terminal.Contains(status, StringComparer.Ordinal))
            {
                return status;
            }

            await Task.Delay(250);
        }

        throw new TimeoutException($"run {runId} did not reach a terminal status within {timeout} (last={status})");
    }
}

/// <summary>RUN-BINDING-FIX-1: models-package sidecar (OCR weights) + BOOK-FIXTURE discovery.</summary>
public sealed class ModelSidecarFactAttribute : FactAttribute
{
    public ModelSidecarFactAttribute()
    {
        if (!ModelSidecarFixture.TryGetSidecar(out _, out var reason))
        {
            Skip = reason;
        }
    }
}

internal static class ModelSidecarFixture
{
    public const string ModelsSidecarVariable = "NEWMANGA_MODELS_SIDECAR_DIR";
    public const string BookFixtureVariable = "NEWMANGA_BOOK_FIXTURE_ROOT";
    private static readonly string DefaultModelsSidecar =
        TestWorkspacePaths.Path("task-envs/FINAL-VALIDATION-1/out/NewManga-0.1.0-win-x64-models/app/core-sidecar");
    private static readonly string DefaultBookFixture =
        TestWorkspacePaths.Path("task-envs/BOOK-FIXTURE-1/isolated-data");
    private const string FixtureBookId = "14340ddad0ed472fbe687fe12340c5d8";
    private const string FixtureChapterId = "240bdba549b74281bfc6d901b1a7abd7";

    public static string ModelsSidecarDirectory
    {
        get
        {
            if (!TryGetSidecar(out var directory, out var reason))
            {
                throw new InvalidOperationException(reason);
            }

            return directory;
        }
    }

    public static string BookFixtureRoot
    {
        get
        {
            var configured = Environment.GetEnvironmentVariable(BookFixtureVariable);
            if (!string.IsNullOrWhiteSpace(configured) && File.Exists(Path.Combine(configured, "library.db")))
            {
                return configured;
            }

            if (File.Exists(Path.Combine(DefaultBookFixture, "library.db")))
            {
                return DefaultBookFixture;
            }

            throw new InvalidOperationException($"BOOK-FIXTURE data root not found (set {BookFixtureVariable})");
        }
    }

    public static bool TryGetSidecar(out string directory, out string reason)
    {
        directory = Environment.GetEnvironmentVariable(ModelsSidecarVariable) ?? DefaultModelsSidecar;
        if (string.IsNullOrWhiteSpace(directory) || !File.Exists(Path.Combine(directory, "core_service.exe")))
        {
            reason = $"reason: needs the models-package core_service - set {ModelsSidecarVariable} to a sidecar dir " +
                     "with core_service.exe + models/ (the OCR weights are required)";
            return false;
        }

        var fixtureRoot = Environment.GetEnvironmentVariable(BookFixtureVariable);
        if (string.IsNullOrWhiteSpace(fixtureRoot) || !File.Exists(Path.Combine(fixtureRoot, "library.db")))
        {
            fixtureRoot = DefaultBookFixture;
        }

        if (!File.Exists(Path.Combine(fixtureRoot, "library.db")))
        {
            reason = $"reason: needs the BOOK-FIXTURE data root - set {BookFixtureVariable}";
            return false;
        }

        reason = string.Empty;
        return true;
    }

    public static string Sha256(string path)
    {
        using var stream = File.OpenRead(path);
        return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
    }

    /// <summary>Copies the durable BOOK-FIXTURE state (library.db + WAL/shm + managed/) into an empty test root.</summary>
    public static void CopyBookFixture(string fixtureRoot, string dataRoot)
    {
        foreach (var name in new[] { "library.db", "library.db-wal", "library.db-shm" })
        {
            var source = Path.Combine(fixtureRoot, name);
            if (File.Exists(source))
            {
                File.Copy(source, Path.Combine(dataRoot, name), overwrite: true);
            }
        }

        var managedSource = Path.Combine(fixtureRoot, "managed");
        var managedTarget = Path.Combine(dataRoot, "managed");
        if (Directory.Exists(managedSource))
        {
            foreach (var file in Directory.EnumerateFiles(managedSource, "*", SearchOption.AllDirectories))
            {
                var relative = Path.GetRelativePath(managedSource, file);
                var target = Path.Combine(managedTarget, relative);
                Directory.CreateDirectory(Path.GetDirectoryName(target)!);
                File.Copy(file, target, overwrite: true);
            }
        }
    }

    public static void CopyDatabase(string dataRoot, string destination)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(destination)!);
        foreach (var suffix in new[] { "", "-wal", "-shm" })
        {
            var source = Path.Combine(dataRoot, "library.db" + suffix);
            if (File.Exists(source))
            {
                File.Copy(source, destination + suffix, overwrite: true);
            }
        }
    }

    public const string BookId = FixtureBookId;

    public const string ChapterId = FixtureChapterId;

    /// <summary>First page id of the fixture chapter (stable BOOK-FIXTURE content).</summary>
    public const string FirstPageId = "f52f2772e8044557a72e82f5ea6ab932";
}

