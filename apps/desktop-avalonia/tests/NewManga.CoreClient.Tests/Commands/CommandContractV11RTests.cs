using System.Text.Json;
using System.Text.RegularExpressions;
using NewManga.CoreClient.Bridge;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Tests.Support;
using NewManga.CoreClient.Wire;

namespace NewManga.CoreClient.Tests.Commands;

/// <summary>
/// V11R-A-3: contract ↔ registry parity for the V1 command contract
/// (<c>doc/contracts/V11R_COMMAND_CONTRACT_V1.md</c>).
///
/// This file is additive on purpose: the legacy 66→76 migration of
/// <c>CommandParityContractTests</c> / <c>CommandWiringB1/B2Tests</c> /
/// <c>CommandIntegrationTests</c> is owned by V11R-F0-1 (Lead ruling), so this test never edits those
/// files and never hardcodes the total command count. It derives everything from
/// <see cref="HostCommandRegistry"/> and the generated contract document:
///   * the baseline C001–C066 rows must parse and their declared commands must exist in the registry;
///   * every declared Core row's protocol minor must equal the registered minor;
///   * the declared channel must equal the registered channel;
///   * every registered command must be declared by the contract (baseline row or PENDING row) —
///     this keeps the 66→76 migration honest without pinning "66";
///   * C067–C077 (increments from V11R-F0-1) must stay PENDING and never enter the frozen set;
///   * the library_start_run minor compatibility conclusion must be present and reference its probe.
/// </summary>
public sealed class CommandContractV11RTests
{
    private const string ContractPath = "doc/contracts/V11R_COMMAND_CONTRACT_V1.md";

    private static readonly Lazy<ContractDocument> Document = new(() => ContractDocument.Load());

    [Fact]
    public void BaselineRows_CoverC001ToC066_AndEveryCommandExistsInRegistry()
    {
        var rows = Document.Value.BaselineRows;

        Assert.Equal(66, rows.Count);
        Assert.Equal(
            Enumerable.Range(1, 66).Select(index => $"C{index:000}").ToArray(),
            rows.Select(row => row.Id).ToArray());
        Assert.Equal(rows.Count, rows.Select(row => row.Command).Distinct(StringComparer.Ordinal).Count());

        foreach (var row in rows)
        {
            Assert.True(
                HostCommandRegistry.All.TryGetValue(row.Command, out var descriptor),
                $"{row.Id} {row.Command} is declared by the contract but missing from HostCommandRegistry");
            Assert.Equal(row.Channel, ChannelName(descriptor!.Channel));
        }
    }

    [Fact]
    public void DeclaredCoreRows_KeepTheRegisteredProtocolMinor()
    {
        var mismatches = new List<string>();
        foreach (var row in Document.Value.BaselineRows.Where(row => row.Channel == "core"))
        {
            var descriptor = HostCommandRegistry.Get(row.Command);
            if (descriptor.CoreMinor != row.Minor)
            {
                mismatches.Add($"{row.Id} {row.Command}: contract minor={row.Minor}, registry minor={descriptor.CoreMinor}");
            }
        }

        Assert.Empty(mismatches);
    }

    [Fact]
    public void RegistrySurface_IsFullyDeclared_WithoutHardcodingTheTotal()
    {
        // FEA-12-PREREQ-1 (DSH 2026-11-05 narrow batch): the delete-preview + trash commands
        // registered by M2-C1 rev 2.13 are declared by M2-C1 itself, not by the V11R command
        // contract. The strict rule stays: every registered command must be declared by one of
        // the authoritative declarations below -- nothing becomes silently undeclared.
        var declared = Document.Value.BaselineRows.Select(row => row.Command)
            .Concat(Document.Value.PendingCommandNames)
            .Concat(HostCommandRegistry.SourceCommandNames)
            .Concat(HostCommandRegistry.SourceSyncCommandNames)
            .Concat(HostCommandRegistry.DeleteTrashCommandNames)
            .ToHashSet(StringComparer.Ordinal);

        var undeclared = HostCommandRegistry.All.Keys
            .Where(name => !declared.Contains(name))
            .OrderBy(name => name, StringComparer.Ordinal)
            .ToArray();

        Assert.True(
            undeclared.Length == 0,
            $"registered commands missing from {ContractPath}: {string.Join(", ", undeclared)}");
        Assert.True(
            HostCommandRegistry.All.Count >= Document.Value.BaselineRows.Count,
            $"registry ({HostCommandRegistry.All.Count}) must not shrink below the signed baseline " +
            $"({Document.Value.BaselineRows.Count})");
    }

    [Fact]
    public void SourceAdditions_AreDeclaredByFrozenC16_AndRemainHostLocal()
    {
        var sourceContract = File.ReadAllText(Path.Combine(RepoLocator.Root, "doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md"));
        var pairs = new Dictionary<string, string>
        {
            ["source_register_root"] = "source_register_root", ["source_list_roots"] = "source_list_roots",
            ["source_revoke_root"] = "source_revoke_root", ["source_reset_registry"] = "source_reset_registry",
            ["plan_import_references"] = "PlanImportReferences", ["start_import_references"] = "StartImportReferences",
            ["get_import_receipt"] = "GetImportReceipt", ["cancel_import"] = "CancelImport"
        };
        Assert.Equal(pairs.Keys.ToHashSet(StringComparer.Ordinal), HostCommandRegistry.SourceCommandNames);
        foreach (var pair in pairs)
        {
            Assert.Contains(pair.Value, sourceContract, StringComparison.Ordinal);
            Assert.Equal(HostCommandChannel.HostLocal, HostCommandRegistry.Get(pair.Key).Channel);
        }
    }

    [Fact]
    public void PendingIncrements_StayPending_AndNeverEnterTheFrozenSet()
    {
        var pending = Document.Value.PendingRows;
        Assert.NotEmpty(pending);
        Assert.All(pending, row => Assert.StartsWith("PENDING", row.Status, StringComparison.Ordinal));

        var frozen = Document.Value.BaselineRows
            .Where(row => row.Status == "FROZEN")
            .Select(row => row.Command)
            .ToHashSet(StringComparer.Ordinal);
        var pendingNames = Document.Value.PendingCommandNames.ToArray();

        Assert.DoesNotContain(pendingNames, frozen.Contains);
        // PENDING commands are allowed to be absent from the registry until V11R-F0-1 merges; when
        // they do appear the contract stays authoritative for their status (still not FROZEN).
        foreach (var name in pendingNames)
        {
            if (HostCommandRegistry.All.TryGetValue(name, out var descriptor))
            {
                Assert.True(descriptor.IsImplemented, $"{name} is registered but not implemented");
            }
        }
    }

    [Fact]
    public void EveryBaselineRow_HasStatusAndSourceEvidence()
    {
        foreach (var row in Document.Value.BaselineRows)
        {
            Assert.Contains(row.Status, new[] { "FROZEN", "PARTIAL", "GAP" });
            Assert.Contains("registry:", row.Evidence, StringComparison.Ordinal);
            Assert.Contains("样例", row.Evidence, StringComparison.Ordinal);
        }

        var frozen = Document.Value.BaselineRows.Count(row => row.Status == "FROZEN");
        var partial = Document.Value.BaselineRows.Count(row => row.Status == "PARTIAL");
        var gap = Document.Value.BaselineRows.Count(row => row.Status == "GAP");
        Assert.Equal(66, frozen + partial + gap);

        WriteEvidence(frozen, partial, gap);
    }

    [Fact]
    public void LibraryStartRun_MinorCompatibilityConclusion_IsPresent()
    {
        var text = Document.Value.Text;
        Assert.Contains("library_start_run", text, StringComparison.Ordinal);
        Assert.Contains("provider_profiles", text, StringComparison.Ordinal);
        Assert.Contains("minor=7", text, StringComparison.Ordinal);
        Assert.Contains("start-run-minor-probe.json", text, StringComparison.Ordinal);
    }

    // ------------------------------------------------------------------
    // V11R-A-3 AC4「参数特判」 - added 2026-11-16 (DSH).
    //
    // AC4 asks for parity assertions over all 66 registered commands "including parameter
    // special-cases and expected minor". The 66-row coverage and the expected minor were already
    // pinned by BaselineRows_CoverC001ToC066_* and DeclaredCoreRows_KeepTheRegisteredProtocolMinor;
    // the missing half was the PARAMETER contract: the 「入参（校验/实测）」 column was parsed by
    // nobody, so a command could declare `section!: string` and silently accept a payload without it.
    //
    // Fact 1 pins the declaration side (every row declares its parameters, in one of five documented
    // shapes). Fact 2 pins the enforcement side and is the real special-case assertion: an empty
    // payload is never accepted for a command that declares required parameters - and it records
    // WHICH layer refuses it, because the contract genuinely uses two mechanisms.
    // ------------------------------------------------------------------

    [Fact]
    public void EveryBaselineRow_DeclaresItsParameterContract_InTheDocumentedVocabulary()
    {
        var classified = new List<(string Id, string Command, string Kind, string Declared)>();

        foreach (var row in Document.Value.BaselineRows)
        {
            Assert.False(
                string.IsNullOrWhiteSpace(row.Params),
                $"{row.Id} {row.Command} does not declare its parameter contract («入参» column is empty)");

            var declared = row.Params;
            string kind;
            if (declared.StartsWith("透传", StringComparison.Ordinal))
            {
                kind = "pass-through";
            }
            else if (declared.StartsWith("见 Host 实现", StringComparison.Ordinal))
            {
                kind = "host-local";
            }
            else if (declared.Contains("无参数", StringComparison.Ordinal))
            {
                kind = "no-params";
            }
            else if (Regex.IsMatch(declared, "^`\\{[^}]+\\}`"))
            {
                // `` `{title!}`（Core `_CREATE_FIELDS`，…） `` - the required set is declared by a Core
                // field-set constant instead of an inline C# shape.
                kind = "core-fieldset";
            }
            else if (Regex.IsMatch(declared, "`[a-z_]+[!?]?\\s*:"))
            {
                kind = "typed-params";
            }
            else
            {
                Assert.Fail($"{row.Id} {row.Command} declares parameters in an undocumented shape: {declared}");
                kind = "unreachable";
            }

            classified.Add((row.Id, row.Command, kind, declared));
        }

        Assert.Equal(Document.Value.BaselineRows.Count, classified.Count);

        // A column where every row says the same thing would be decorative, not a contract.
        var kinds = classified.Select(row => row.Kind).Distinct(StringComparer.Ordinal).ToList();
        Assert.True(
            kinds.Count >= 3,
            "the «入参» column must distinguish parameter shapes, saw only: " + string.Join(", ", kinds));

        Assert.Contains(classified, row => row.Kind == "typed-params");

        WriteParameterEvidence(classified, kinds);
    }

    [SidecarFact]
    public async Task EveryDeclaredRequiredParameter_IsRefused_AndNeverSilentlyAccepted()
    {
        // Required parameters are the ones the contract marks with a trailing '!'. Two declaration
        // forms carry them, and BOTH must be refused:
        //   `` `section!: string` ``          -> typed, refused at the dispatcher boundary;
        //   `` `{title!, chapter_number?}` ``  -> Core field-set, refused by the Core itself.
        // The invariant that matters is that an empty payload is NEVER accepted for a command that
        // declares required parameters. Which layer refuses it is recorded, not assumed.
        var withRequired = new List<(string Id, string Command, string[] Required, string Form)>();
        foreach (var row in Document.Value.BaselineRows)
        {
            var required = new List<string>();
            var form = "none";
            foreach (Match typed in Regex.Matches(row.Params, "`([a-z_]+)!\\s*:"))
            {
                required.Add(typed.Groups[1].Value);
                form = "typed";
            }

            foreach (Match set in Regex.Matches(row.Params, "\\{([^}]*)\\}"))
            {
                var fromFieldSet = 0;
                foreach (Match name in Regex.Matches(set.Groups[1].Value, "([a-z_]+)!"))
                {
                    required.Add(name.Groups[1].Value);
                    fromFieldSet++;
                }

                if (fromFieldSet > 0)
                {
                    form = form == "typed" ? "typed+fieldset" : "fieldset";
                }
            }

            var names = required.Distinct(StringComparer.Ordinal).ToArray();
            if (names.Length > 0)
            {
                withRequired.Add((row.Id, row.Command, names, form));
            }
        }

        Assert.NotEmpty(withRequired);

        await using var context = await ParameterProbeContext.StartAsync("commands-v11r-a3-required-params");

        var accepted = new List<string>();
        var atDispatcher = new List<(string Id, string Command, string[] Required, string Form)>();
        var atCore = new List<(string Id, string Command, string[] Required, string Form)>();
        foreach (var (id, command, required, form) in withRequired)
        {
            var framesBefore = context.Core.Wire.Frames.Count;
            try
            {
                await context.Dispatcher.InvokeAsync(command, Args("{}"));
                accepted.Add($"{id} {command} (required: {string.Join(",", required)})");
            }
            catch (HostCommandInvalidArgumentsException error)
            {
                Assert.Equal("INVALID_ARGUMENTS", error.Code);
                // Refused BEFORE the frame: the dispatcher owns this rejection.
                Assert.Equal(framesBefore, context.Core.Wire.Frames.Count);
                atDispatcher.Add((id, command, required, form));
            }
            catch (CoreOperationException error)
            {
                Assert.Equal("INVALID_REQUEST", error.Code);
                // Refused BY the Core: exactly one frame went out and came back typed-failed.
                Assert.Equal(framesBefore + 1, context.Core.Wire.Frames.Count);
                atCore.Add((id, command, required, form));
            }
        }

        Assert.True(
            accepted.Count == 0,
            "commands that declare required parameters yet ACCEPT an empty payload: "
            + string.Join("; ", accepted));
        Assert.Equal(withRequired.Count, atDispatcher.Count + atCore.Count);

        // Direction that MUST hold: a command declaring inline typed parameters has to be refused by
        // the dispatcher - that is what «the dispatcher enforces these» means. If that ever regresses,
        // this names the command instead of quietly letting a frame through.
        //
        // The opposite direction (a Core-field-set command that the dispatcher ALSO refuses) is harmless
        // hardening, so it is recorded rather than asserted. It does happen today: C040/C041 are declared
        // against a Core field-set yet the dispatcher refuses them first, i.e. those contract cells
        // under-describe the wiring. Registered as finding A-1 in the card instead of being tolerated.
        foreach (var (id, command, _, form) in atCore)
        {
            Assert.True(
                form is "fieldset" or "typed+fieldset",
                $"{id} {command} declares inline typed parameters ({form}) "
                + "but ONLY the Core refused it - the dispatcher is supposed to enforce those");
        }

        WriteRequiredParameterEvidence(atDispatcher, atCore);
    }

    private static JsonElement Args(string json)
    {
        using var document = JsonDocument.Parse(json);
        return document.RootElement.Clone();
    }

    private static void WriteParameterEvidence(
        IReadOnlyList<(string Id, string Command, string Kind, string Declared)> all,
        IReadOnlyList<string> kinds)
    {
        var directory = Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_DIR");
        if (string.IsNullOrWhiteSpace(directory))
        {
            return;
        }

        var target = Path.Combine(directory, "contract-v11r");
        Directory.CreateDirectory(target);
        using var stream = File.Create(Path.Combine(target, "parameter-contract.json"));
        using var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true });
        writer.WriteStartObject();
        writer.WriteString("task", "V11R-A-3");
        writer.WriteString("ac", "AC4 参数特判（声明面）");
        writer.WriteNumber("baseline_rows", all.Count);
        writer.WriteStartArray("shapes");
        foreach (var kind in kinds)
        {
            writer.WriteStringValue(kind);
        }

        writer.WriteEndArray();
        writer.WriteStartArray("rows");
        foreach (var row in all)
        {
            writer.WriteStartObject();
            writer.WriteString("id", row.Id);
            writer.WriteString("command", row.Command);
            writer.WriteString("shape", row.Kind);
            writer.WriteString("declared", row.Declared);
            writer.WriteEndObject();
        }

        writer.WriteEndArray();
        writer.WriteEndObject();
    }

    private static void WriteRequiredParameterEvidence(
        IReadOnlyList<(string Id, string Command, string[] Required, string Form)> atDispatcher,
        IReadOnlyList<(string Id, string Command, string[] Required, string Form)> atCore)
    {
        var directory = Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_DIR");
        if (string.IsNullOrWhiteSpace(directory))
        {
            return;
        }

        var target = Path.Combine(directory, "contract-v11r");
        Directory.CreateDirectory(target);
        using var stream = File.Create(Path.Combine(target, "parameter-enforcement.json"));
        using var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true });
        writer.WriteStartObject();
        writer.WriteString("task", "V11R-A-3");
        writer.WriteString("ac", "AC4 参数特判：声明了必填参数的命令，空 payload 一律被拒（并记录拒在哪一层）");
        writer.WriteNumber("commands_with_required_params", atDispatcher.Count + atCore.Count);
        writer.WriteNumber("refused_at_dispatcher", atDispatcher.Count);
        writer.WriteNumber("refused_by_core", atCore.Count);
        writer.WriteNumber("silently_accepted", 0);

        void WriteRows(string name, IReadOnlyList<(string Id, string Command, string[] Required, string Form)> rows)
        {
            writer.WriteStartArray(name);
            foreach (var row in rows)
            {
                writer.WriteStartObject();
                writer.WriteString("id", row.Id);
                writer.WriteString("command", row.Command);
                writer.WriteString("declaration_form", row.Form);
                writer.WriteStartArray("required");
                foreach (var parameter in row.Required)
                {
                    writer.WriteStringValue(parameter);
                }

                writer.WriteEndArray();
                writer.WriteEndObject();
            }

            writer.WriteEndArray();
        }

        WriteRows("refused_at_dispatcher_detail", atDispatcher);
        WriteRows("refused_by_core_detail", atCore);
        writer.WriteEndObject();
    }

    private static string ChannelName(HostCommandChannel channel) => channel switch
    {
        HostCommandChannel.CoreService => "core",
        HostCommandChannel.HostBridge => "bridge",
        HostCommandChannel.HostLocal => "host-local",
        _ => "—",
    };

    private static void WriteEvidence(int frozen, int partial, int gap)
    {
        var directory = Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_DIR");
        if (string.IsNullOrWhiteSpace(directory))
        {
            return;
        }

        var target = Path.Combine(directory, "contract-v11r");
        Directory.CreateDirectory(target);
        using var stream = File.Create(Path.Combine(target, "command-contract-v11r.json"));
        using var writer = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = true });
        writer.WriteStartObject();
        writer.WriteString("task", "V11R-A-3");
        writer.WriteString("contract", ContractPath);
        writer.WriteNumber("baseline_rows", 66);
        writer.WriteNumber("frozen", frozen);
        writer.WriteNumber("partial", partial);
        writer.WriteNumber("gap", gap);
        writer.WriteNumber("registry_commands", HostCommandRegistry.All.Count);
        writer.WriteNumber("pending_rows", Document.Value.PendingRows.Count);
        writer.WriteEndObject();
    }

    private sealed record ContractRow(
        string Id,
        string Command,
        string Route,
        string Channel,
        int? Minor,
        string Status,
        string Evidence,
        string Params);

    private sealed record PendingRow(string Id, string Name, string Status);

    private sealed class ContractDocument
    {
        private ContractDocument(string text, IReadOnlyList<ContractRow> baselineRows, IReadOnlyList<PendingRow> pendingRows)
        {
            Text = text;
            BaselineRows = baselineRows;
            PendingRows = pendingRows;
        }

        public string Text { get; }

        public IReadOnlyList<ContractRow> BaselineRows { get; }

        public IReadOnlyList<PendingRow> PendingRows { get; }

        public IReadOnlyList<string> PendingCommandNames => PendingRows
            .Select(row => row.Name.Trim('`'))
            .Where(name => Regex.IsMatch(name, "^[a-z][a-z0-9_]*$"))
            .ToArray();

        public static ContractDocument Load()
        {
            var path = Path.Combine(RepoLocator.Root, ContractPath);
            Assert.True(File.Exists(path), $"contract document missing: {ContractPath}");
            var text = File.ReadAllText(path);
            var baseline = new List<ContractRow>();
            var pending = new List<PendingRow>();
            var section = string.Empty;

            foreach (var line in text.Split('\n'))
            {
                var trimmed = line.Trim();
                if (trimmed.StartsWith("## ", StringComparison.Ordinal) ||
                    trimmed.StartsWith("### ", StringComparison.Ordinal))
                {
                    section = trimmed;
                    continue;
                }

                if (!trimmed.StartsWith('|'))
                {
                    continue;
                }

                var cells = trimmed.Split('|');
                if (cells.Length < 4)
                {
                    continue;
                }

                var id = cells[1].Trim();
                if (!Regex.IsMatch(id, "^C\\d{3}$"))
                {
                    continue;
                }

                var index = int.Parse(id[1..]);
                if (index <= 66 && section.StartsWith("### 4.", StringComparison.Ordinal))
                {
                    // Baseline table: | ID | 前端命令 | 路由 | 通道 | minor | ... | 状态 | 证据 |
                    Assert.True(cells.Length >= 12, $"malformed baseline row {id}: {trimmed}");
                    var command = cells[2].Trim().Trim('`');
                    var route = cells[3].Trim().Trim('`');
                    var channel = cells[4].Trim();
                    var minorText = cells[5].Trim();
                    var status = cells[10].Trim().Trim('*').Trim();
                    var evidence = cells[11].Trim();
                    // cells[6] is the 「入参（校验/实测）」 column - the declared parameter contract.
                    var parameters = cells[6].Trim();
                    baseline.Add(new ContractRow(
                        id,
                        command,
                        route,
                        channel,
                        int.TryParse(minorText, out var minor) ? minor : null,
                        status,
                        evidence,
                        parameters));
                }
                else if (index > 66 && section.StartsWith("## 8.", StringComparison.Ordinal))
                {
                    // PENDING table: | ID | 前端命令（待合入） | 域 | 通道 | minor | 参数外形 | 状态 |
                    var name = cells[2].Trim().Trim('`');
                    var status = cells[^2].Trim().Trim('`').Trim();
                    pending.Add(new PendingRow(id, name, status));
                }
            }

            return new ContractDocument(text, baseline, pending);
        }
    }
    /// <summary>
    /// Minimal dispatcher fixture for the AC4 enforcement fact: a real Core sidecar + real bridge, so
    /// «refused at the dispatcher boundary» means what it says and frame counts are real.
    /// Mirrors the per-file fixture pattern already used by CommandWiringB1/B2 and CommandIntegrationTests.
    /// </summary>
    private sealed class ParameterProbeContext : IAsyncDisposable
    {
        private ParameterProbeContext(
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

        public static async Task<ParameterProbeContext> StartAsync(string name)
        {
            var environment = SidecarFixture.CreateCommandEnvironment(name);
            var core = await CoreServiceClient.StartAsync(environment.CoreOptions);
            try
            {
                var bridge = await HostBridgeClient.StartAsync(environment.BridgeOptions);
                return new ParameterProbeContext(environment, core, bridge, new HostCommandDispatcher(core, bridge));
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

}
