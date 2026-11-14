using System.Text.Json;
using NewManga.CoreClient;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;
using NewManga.CoreClient.Tests.Support;
using Xunit;

namespace NewManga.CoreClient.Tests.Commands;

/// <summary>
/// CORE-PIPE-EXCLUSIVE-1 / E-6 (P1): core_service speaks a STRICTLY request/response protocol on a single
/// stdin/stdout pipe, and <c>Transport/SidecarProcess.ExchangeAsync</c> assumes only one request is in
/// flight at a time. The Host guards its reader methods with <c>_readerIoGate</c>, but background callers
/// (SourceScanScheduler / SourceOperationCoordinator) call the client directly and therefore bypass that
/// gate — so two commands can be in flight and the client can hand one command's response to the other.
///
/// The observed production symptom: <c>list_chapters</c> received the response of
/// <c>source_list_scan_targets</c> ({"targets": []}), whose JSON has no "chapters" property, and
/// <c>ListChaptersAsync</c> silently returned an empty list — the reader showed an empty chapter list.
///
/// This test pins the general defect rather than one command pair: it interleaves a command whose result
/// is a JSON ARRAY (<c>ListBooks</c>) with one whose result is a JSON OBJECT holding "targets"
/// (<c>source_list_scan_targets</c>). The two shapes are unmistakable, so a crossed response fails here
/// immediately. Both commands are valid on a brand-new (empty) data root, so the test needs no fixture rows.
/// </summary>
public sealed class PipeResponsePairingTests
{
    private const int Rounds = 6;

    [SidecarFact]
    public async Task ConcurrentCommands_DoNotCrossResponses()
    {
        var options = SidecarFixture.CreateCoreOptions("pipe-exclusive", out var dataRoot);
        try
        {
            await using var client = await CoreServiceClient.StartAsync(options);

            // Warm the session up first so the concurrent phase is not racing the handshake.
            var ping = await client.PingAsync();
            Assert.True(ping.Ready);

            var tasks = new List<(string Command, Task<CoreResponse> Pending)>(Rounds * 2);
            for (var round = 0; round < Rounds; round++)
            {
                tasks.Add((
                    "ListBooks",
                    client.SendAsync(
                        "ListBooks",
                        CoreProtocol.DefaultMinor,
                        WireJson.EmptyObject,
                        TimeSpan.FromSeconds(60))));
                tasks.Add((
                    "source_list_scan_targets",
                    client.SendAsync(
                        "source_list_scan_targets",
                        CoreProtocol.DefaultMinor,
                        WireJson.EmptyObject,
                        TimeSpan.FromSeconds(60))));
            }

            await Task.WhenAll(tasks.Select(item => item.Pending));

            foreach (var (command, pending) in tasks)
            {
                var response = pending.Result;
                Assert.Null(response.Error);
                Assert.True(response.Result.HasValue, $"{command} returned no result element");
                var result = response.Result!.Value;

                if (command == "ListBooks")
                {
                    // A crossed response (the scan-targets object) would land here.
                    Assert.True(
                        result.ValueKind == JsonValueKind.Array,
                        $"ListBooks received a non-array result (crossed response? raw={Truncate(result.GetRawText())})");
                }
                else
                {
                    Assert.True(
                        result.ValueKind == JsonValueKind.Object,
                        $"source_list_scan_targets received a non-object result (crossed response? raw={Truncate(result.GetRawText())})");
                    Assert.True(
                        result.TryGetProperty("targets", out var targets),
                        $"source_list_scan_targets response has no 'targets' (crossed response? raw={Truncate(result.GetRawText())})");
                    Assert.Equal(JsonValueKind.Array, targets.ValueKind);
                }
            }
        }
        finally
        {
            TryDelete(dataRoot);
        }
    }

    private static string Truncate(string text) =>
        text.Length <= 200 ? text : text[..200] + "…";

    private static void TryDelete(string path)
    {
        try
        {
            if (Directory.Exists(path))
            {
                Directory.Delete(path, recursive: true);
            }
        }
        catch (IOException)
        {
            // best effort: the test result must not hinge on cleaning a temp dir
        }
        catch (UnauthorizedAccessException)
        {
        }
    }
}
