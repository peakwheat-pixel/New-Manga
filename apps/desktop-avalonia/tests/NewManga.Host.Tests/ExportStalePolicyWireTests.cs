using System.Text.Json;
using NewManga.CoreClient.Issuer;
using NewManga.CoreClient.Wire;
using NewManga.Host.Tests.Support;

namespace NewManga.Host.Tests;

/// <summary>
/// V11R-A-7: both legal stale policies must reach the Core as real StartExport frames. The Core
/// (core_service.py:2854-2863) requires the field to be exactly <c>abort</c> or <c>continue_existing</c>;
/// the Host issuer mirrors that validation (HostIssuer.cs:382-386). A fresh data root makes the Core
/// answer TARGET_NOT_FOUND — that is still proof the policy passed validation and was sent, which is the
/// contract gap this task closes (the full artifact path is covered by ExportE2ETests).
/// </summary>
public sealed class ExportStalePolicyWireTests
{
    [HostSidecarFact]
    public async Task BothPolicies_AreSentToTheCore_AsStartExportFrames()
    {
        var dataRoot = HostFixture.NewDataRoot("export-stale-policy");
        var options = new HostOptions
        {
            DataRoot = dataRoot,
            LogDirectory = Path.Combine(HostFixture.EvidenceDirectory, "host-logs", "export-stale-policy"),
            SidecarDirectoryOverride = HostFixture.SidecarDirectory,
            MutexName = @"Local\NewManga.Host.Test." + Guid.NewGuid().ToString("N")[..12],
            DetectLegacyShell = false,
            EnableWireEvidence = true,
            StartupTimeout = TimeSpan.FromSeconds(90),
            RequestTimeout = TimeSpan.FromSeconds(90),
        };

        try
        {
            await using var runtime = await HostRuntime.StartAsync(options);
            Assert.True(runtime.Result.IsReady, runtime.Result.ErrorCode);
            Assert.NotNull(runtime.Grants);
            var exportDirectory = Path.Combine(dataRoot, "exports");
            Directory.CreateDirectory(exportDirectory);

            foreach (var policy in new[] { "abort", "continue_existing" })
            {
                var framesBefore = runtime.CoreService!.Wire.Frames.Count;
                var request = BuildRequest(policy);
                var target = Path.Combine(exportDirectory, $"stale-{policy}.zip");

                string? typedError = null;
                try
                {
                    await runtime.Grants!.StartExportAsync(request, target);
                }
                catch (Exception ex) when (ex is CoreOperationException or HostIssuerException)
                {
                    typedError = ex switch
                    {
                        CoreOperationException core => core.Code,
                        HostIssuerException issuer => issuer.Code,
                        _ => ex.GetType().Name,
                    };
                }

                // The field must have been accepted (not INVALID_REQUEST) and the frame must be on the wire.
                Assert.NotEqual("INVALID_REQUEST", typedError);
                var frames = runtime.CoreService.Wire.Frames.Skip(framesBefore).ToArray();
                var startExport = frames.FirstOrDefault(frame =>
                    frame.RequestLine.Contains("\"command\":\"StartExport\"", StringComparison.Ordinal));
                Assert.NotNull(startExport);
                Assert.Contains($"\"stale_policy\":\"{policy}\"", startExport!.RequestLine, StringComparison.Ordinal);

                HostFixture.WriteEvidenceJson($"export-stale-policy/{policy}.json", writer =>
                {
                    writer.WriteStartObject();
                    writer.WriteString("stale_policy", policy);
                    writer.WriteBoolean("frame_sent", true);
                    writer.WriteString("typed_error", typedError);
                    writer.WriteNumber("frames_in_call", frames.Length);
                    writer.WriteString("request_line", startExport.RequestLine);
                    writer.WriteString("response_line", startExport.ResponseLine);
                    writer.WriteEndObject();
                });
            }
        }
        finally
        {
            HostFixture.TryDeleteDirectory(dataRoot);
        }
    }

    private static JsonElement BuildRequest(string stalePolicy)
    {
        using var stream = new MemoryStream();
        using (var writer = new Utf8JsonWriter(stream))
        {
            writer.WriteStartObject();
            writer.WriteString("book_id", "00000000000000000000000000000000");
            writer.WritePropertyName("chapter_ids");
            writer.WriteStartArray();
            writer.WriteStringValue("11111111111111111111111111111111");
            writer.WriteEndArray();
            writer.WritePropertyName("ordered_page_ids");
            writer.WriteStartArray();
            writer.WriteStringValue("22222222222222222222222222222222");
            writer.WriteEndArray();
            writer.WriteString("format", "zip");
            writer.WritePropertyName("format_options");
            writer.WriteStartObject();
            writer.WriteString("compression", "standard");
            writer.WriteEndObject();
            writer.WriteString("stale_policy", stalePolicy);
            writer.WriteEndObject();
        }

        using var document = JsonDocument.Parse(stream.ToArray());
        return document.RootElement.Clone();
    }
}
