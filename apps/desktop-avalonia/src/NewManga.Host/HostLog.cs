using System.Collections.Concurrent;
using NewManga.CoreClient.Diagnostics;

namespace NewManga.Host;

/// <summary>
/// Minimal structured host log: one file for host decisions, one per sidecar stderr stream. All
/// paths stay inside the host log directory; the UI only shows a friendly code + hint.
/// </summary>
public sealed class HostLog : IDisposable
{
    private readonly object _gate = new();
    private readonly StreamWriter _writer;

    public HostLog(string logDirectory)
    {
        Directory.CreateDirectory(logDirectory);
        LogDirectory = logDirectory;
        _writer = new StreamWriter(new FileStream(
            Path.Combine(logDirectory, "host.log"),
            FileMode.Append,
            FileAccess.Write,
            FileShare.ReadWrite))
        {
            AutoFlush = true,
        };
    }

    public string LogDirectory { get; }

    public string HostLogPath => Path.Combine(LogDirectory, "host.log");

    public string CoreServiceStderrPath => Path.Combine(LogDirectory, "core_service.stderr.log");

    public string HostBridgeStderrPath => Path.Combine(LogDirectory, "host_bridge.stderr.log");

    public string? WireLogPath { get; set; }

    public void Info(string message) => Write("INFO", message);

    public void Warn(string message) => Write("WARN", message);

    public void Error(SidecarException error) =>
        Write("ERROR", $"code={error.Code} sidecar={error.Sidecar} {error.Message}");

    public void Error(string code, string message) => Write("ERROR", $"code={code} {message}");

    private void Write(string level, string message)
    {
        var line = $"{DateTimeOffset.UtcNow:O} {level} {message}";
        lock (_gate)
        {
            _writer.WriteLine(line);
        }
    }

    public void Dispose()
    {
        lock (_gate)
        {
            _writer.Dispose();
        }
    }
}

/// <summary>Bounded in-memory log used by unit tests (no filesystem writes).</summary>
public sealed class InMemoryLog
{
    public ConcurrentQueue<string> Lines { get; } = new();

    public void Info(string message) => Lines.Enqueue("INFO " + message);

    public void Error(string code, string message) => Lines.Enqueue($"ERROR {code} {message}");
}
