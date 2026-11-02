using System.Text.Json;
using System.Text.RegularExpressions;
using NewManga.CoreClient.Commands;
using NewManga.CoreClient.Tests.Support;

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
        var declared = Document.Value.BaselineRows.Select(row => row.Command)
            .Concat(Document.Value.PendingCommandNames)
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
        string Evidence);

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
                    baseline.Add(new ContractRow(
                        id,
                        command,
                        route,
                        channel,
                        int.TryParse(minorText, out var minor) ? minor : null,
                        status,
                        evidence));
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
}
