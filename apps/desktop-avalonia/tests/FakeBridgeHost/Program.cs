// Test-only fake host_bridge: answers the wire-v1 control plane on stdin/stdout with one JSON object
// per line, exactly like the real sidecar. Scenario is selected via the M2RC1_DERIVED_ROOT environment
// variable (see doc/reviews/BRIDGE-FAKE-HARNESS-DESIGN-2026-11-16.md) because HostBridgeClient cannot
// pass command-line arguments through HostBridgeOptions.

using System.Text;
using System.Text.Json;

var derivedRoot = Environment.GetEnvironmentVariable("M2RC1_DERIVED_ROOT") ?? string.Empty;
var scenario = "plain";
foreach (var segment in derivedRoot.Split(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar))
{
    if (segment.StartsWith("scenario-", StringComparison.Ordinal))
    {
        scenario = segment["scenario-".Length..];
        break;
    }
}

var stdout = new StreamWriter(Console.OpenStandardOutput(), new UTF8Encoding(false)) { AutoFlush = true };
var stdin = new StreamReader(Console.OpenStandardInput(), new UTF8Encoding(false));

const string ResultOk = """{"id":"fake-grant","size":1}""";

var served = 0;
while (stdin.ReadLine() is { } line)
{
    if (string.IsNullOrWhiteSpace(line))
    {
        continue;
    }

    JsonDocument request;
    try
    {
        request = JsonDocument.Parse(line);
    }
    catch (JsonException)
    {
        continue;
    }

    using (request)
    {
        var root = request.RootElement;
        var hasId = root.TryGetProperty("id", out var id) && id.ValueKind == JsonValueKind.Number;
        var method = root.TryGetProperty("method", out var m) && m.ValueKind == JsonValueKind.String
            ? m.GetString()
            : string.Empty;
        served++;

        // The handshake must always succeed, otherwise StartAsync never returns and no test can run.
        if (method == "ping")
        {
            Emit(stdout, hasId ? id.GetInt32() : null, """{"pong":true}""", null);
            continue;
        }

        switch (scenario)
        {
            case "missing-then-match":
                // First non-handshake frame deliberately omits id => production ParseResponse must reject it
                // and SendAsync must poison the channel. A later correct frame must NOT rescue the call.
                if (served == 2)
                {
                    Emit(stdout, null, ResultOk, null);
                    Emit(stdout, hasId ? id.GetInt32() : null, ResultOk, null);
                    continue;
                }
                break;

            case "mismatch-then-match":
                if (served == 2)
                {
                    Emit(stdout, hasId ? id.GetInt32() + 1000 : null, ResultOk, null);
                    Emit(stdout, hasId ? id.GetInt32() : null, ResultOk, null);
                    continue;
                }
                break;
        }

        Emit(stdout, hasId ? id.GetInt32() : null, """{"ok":true}""", null);
    }
}

static void Emit(StreamWriter stdout, int? id, string resultJson, string? errorJson)
{
    var sb = new StringBuilder();
    sb.Append('{');
    if (id is { } value)
    {
        sb.Append("\"id\":").Append(value).Append(',');
    }

    if (errorJson is not null)
    {
        sb.Append("\"error\":").Append(errorJson);
    }
    else
    {
        sb.Append("\"result\":").Append(resultJson);
    }

    sb.Append('}');
    stdout.WriteLine(sb.ToString());
}
