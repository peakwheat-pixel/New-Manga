using System.Diagnostics;
using System.Text;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Wire;

namespace NewManga.CoreClient.Transport;

/// <summary>
/// One stdio JSON-lines sidecar process: spawned with <c>CREATE_NO_WINDOW</c> semantics, integrity
/// checked against the host token, stderr drained to a file (never a console), and every line
/// exchange captured as a <see cref="WireFrame"/>. Faults surface as typed
/// <see cref="SidecarException"/> values — never an unhandled crash path.
/// </summary>
public sealed class SidecarProcess : IAsyncDisposable
{
    private readonly Process _process;
    private readonly StreamWriter _stdin;
    private readonly StreamReader _stdout;
    private readonly Task _stderrPump;
    private readonly List<string> _stderrTail = new();
    private readonly object _stderrGate = new();
    private bool _disposed;
    private bool _poisoned;

    private SidecarProcess(SidecarSpec spec, Process process)
    {
        Spec = spec;
        _process = process;
        _stdin = process.StandardInput;
        _stdin.NewLine = "\n";
        _stdout = process.StandardOutput;
        Log = new WireLog(spec.WireLogPath);
        _stderrPump = PumpStderrAsync(process);
    }

    public SidecarSpec Spec { get; }

    public WireLog Log { get; }

    public bool HasExited
    {
        get
        {
            try
            {
                return _process.HasExited;
            }
            catch (InvalidOperationException)
            {
                return true;
            }
        }
    }

    public int? ExitCode
    {
        get
        {
            try
            {
                return _process.HasExited ? _process.ExitCode : null;
            }
            catch (InvalidOperationException)
            {
                return null;
            }
        }
    }

    public string StderrTail
    {
        get
        {
            lock (_stderrGate)
            {
                return string.Join(Environment.NewLine, _stderrTail);
            }
        }
    }

    public static async Task<SidecarProcess> StartAsync(SidecarSpec spec, CancellationToken cancellationToken = default)
    {
        if (!File.Exists(spec.ExecutablePath))
        {
            throw new SidecarException(
                SidecarErrorCode.SidecarExeMissing,
                spec.Name,
                $"executable not found: {spec.ExecutablePath}",
                spec.StderrLogPath);
        }

        var logDirectory = Path.GetDirectoryName(spec.StderrLogPath);
        if (!string.IsNullOrEmpty(logDirectory))
        {
            Directory.CreateDirectory(logDirectory);
        }

        var startInfo = new ProcessStartInfo
        {
            FileName = spec.ExecutablePath,
            WorkingDirectory = spec.WorkingDirectory ?? Path.GetDirectoryName(spec.ExecutablePath) ?? Environment.CurrentDirectory,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardInput = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            StandardInputEncoding = new UTF8Encoding(false),
            StandardOutputEncoding = new UTF8Encoding(false),
            StandardErrorEncoding = new UTF8Encoding(false),
        };
        foreach (var pair in spec.Environment)
        {
            startInfo.Environment[pair.Key] = pair.Value;
        }

        foreach (var argument in spec.AdditionalArguments)
        {
            startInfo.ArgumentList.Add(argument);
        }

        Process process;
        try
        {
            process = Process.Start(startInfo)
                ?? throw new SidecarException(SidecarErrorCode.SpawnFailed, spec.Name, "Process.Start returned null", spec.StderrLogPath);
        }
        catch (Exception ex) when (ex is not SidecarException)
        {
            throw new SidecarException(
                SidecarErrorCode.SpawnFailed,
                spec.Name,
                $"spawn failed: {ex.Message}",
                spec.StderrLogPath,
                ex);
        }

        var sidecar = new SidecarProcess(spec, process);
        try
        {
            File.AppendAllText(spec.StderrLogPath, string.Empty);
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
        {
            // diagnostics are best effort
        }

        try
        {
            ProcessIntegrity.EnsureChildMatchesParent(spec.Name, process.Handle, spec.StderrLogPath);
        }
        catch (SidecarException)
        {
            await sidecar.DisposeAsync().ConfigureAwait(false);
            throw;
        }
        catch (Exception ex)
        {
            await sidecar.DisposeAsync().ConfigureAwait(false);
            throw new SidecarException(
                SidecarErrorCode.IntegrityMismatch,
                spec.Name,
                $"integrity check failed: {ex.Message}",
                spec.StderrLogPath,
                ex);
        }

        cancellationToken.ThrowIfCancellationRequested();
        return sidecar;
    }

    public Task<WireFrame> ExchangeAsync(string requestLine, CancellationToken cancellationToken = default) =>
        ExchangeAsync(requestLine, escapeNonAscii: true, Spec.RequestTimeout, cancellationToken);

    public async Task<WireFrame> ExchangeAsync(
        string requestLine,
        bool escapeNonAscii,
        TimeSpan timeout,
        CancellationToken cancellationToken = default)
    {
        ThrowIfPoisoned();
        if (HasExited)
        {
            throw ProcessExitedFailure();
        }

        var wireLine = escapeNonAscii ? AsciiWire.Escape(requestLine) : requestLine;
        var stopwatch = Stopwatch.StartNew();
        try
        {
            await _stdin.WriteLineAsync(wireLine).ConfigureAwait(false);
            await _stdin.FlushAsync().ConfigureAwait(false);
        }
        catch (Exception ex) when (ex is IOException or ObjectDisposedException or InvalidOperationException)
        {
            throw ProcessExitedFailure(ex);
        }

        string? responseLine;
        using var timeoutSource = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        timeoutSource.CancelAfter(timeout);
        try
        {
            responseLine = await _stdout.ReadLineAsync(timeoutSource.Token).ConfigureAwait(false);
        }
        catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            _poisoned = true;
            throw new SidecarException(
                SidecarErrorCode.RequestTimeout,
                Spec.Name,
                $"no response within {timeout.TotalMilliseconds:F0} ms; stderr tail: {Truncate(StderrTail)}",
                Spec.StderrLogPath);
        }
        catch (Exception ex) when (ex is IOException or ObjectDisposedException or InvalidOperationException)
        {
            throw ProcessExitedFailure(ex);
        }

        stopwatch.Stop();
        if (responseLine is null)
        {
            throw ProcessExitedFailure();
        }

        var requestBytes = Encoding.UTF8.GetBytes(wireLine);
        var responseBytes = Encoding.UTF8.GetBytes(responseLine);
        var frame = new WireFrame(
            Spec.Name,
            wireLine,
            responseLine,
            AsciiWire.Hex(requestBytes),
            AsciiWire.Hex(responseBytes),
            AsciiWire.IsAscii(wireLine),
            AsciiWire.IsAscii(responseLine),
            stopwatch.Elapsed.TotalMilliseconds,
            DateTimeOffset.UtcNow);
        Log.Add(frame);
        return frame;
    }

    /// <summary>
    /// READER-PROGRESS-1: drains one line that arrived on the response channel without a request of
    /// ours — the frozen core_service pushes <c>ReadingProgressChanged</c>/<c>ExportProgressChanged</c>
    /// event frames on the same stdout pipe before answering the command that caused them. The caller
    /// keeps reading until the frame carries the actual response envelope.
    /// </summary>
    public async Task<string> ReadNextResponseLineAsync(
        TimeSpan timeout,
        CancellationToken cancellationToken = default)
    {
        ThrowIfPoisoned();
        if (HasExited)
        {
            throw ProcessExitedFailure();
        }

        var stopwatch = Stopwatch.StartNew();
        string? line;
        using var timeoutSource = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        timeoutSource.CancelAfter(timeout);
        try
        {
            line = await _stdout.ReadLineAsync(timeoutSource.Token).ConfigureAwait(false);
        }
        catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            _poisoned = true;
            throw new SidecarException(
                SidecarErrorCode.RequestTimeout,
                Spec.Name,
                $"no event/response line within {timeout.TotalMilliseconds:F0} ms; stderr tail: {Truncate(StderrTail)}",
                Spec.StderrLogPath);
        }
        catch (Exception ex) when (ex is IOException or ObjectDisposedException or InvalidOperationException)
        {
            throw ProcessExitedFailure(ex);
        }

        stopwatch.Stop();
        if (line is null)
        {
            throw ProcessExitedFailure();
        }

        var bytes = Encoding.UTF8.GetBytes(line);
        Log.Add(new WireFrame(
            Spec.Name,
            string.Empty,
            line,
            string.Empty,
            AsciiWire.Hex(bytes),
            true,
            AsciiWire.IsAscii(line),
            stopwatch.Elapsed.TotalMilliseconds,
            DateTimeOffset.UtcNow));
        return line;
    }

    public async Task StopAsync(int gracefulTimeoutMs = 3000)
    {        if (_disposed)
        {
            return;
        }

        try
        {
            _stdin.Close();
        }
        catch (Exception ex) when (ex is IOException or ObjectDisposedException or InvalidOperationException)
        {
            // closing stdin is best effort; the kill below is the guarantee
        }

        try
        {
            using var timeout = new CancellationTokenSource(gracefulTimeoutMs);
            await _process.WaitForExitAsync(timeout.Token).ConfigureAwait(false);
        }
        catch (OperationCanceledException)
        {
            TryKill();
        }

        if (!HasExited)
        {
            TryKill();
            try
            {
                await _process.WaitForExitAsync().ConfigureAwait(false);
            }
            catch (Exception ex) when (ex is InvalidOperationException or OperationCanceledException)
            {
                // process already gone
            }
        }
    }

    public async ValueTask DisposeAsync()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;
        await StopAsync().ConfigureAwait(false);
        try
        {
            await _stderrPump.WaitAsync(TimeSpan.FromSeconds(2)).ConfigureAwait(false);
        }
        catch (TimeoutException)
        {
            // stderr reader is stuck on a dead pipe; process is already gone
        }
        catch (Exception ex) when (ex is AggregateException or OperationCanceledException)
        {
            // pump observed the process exit
        }

        _process.Dispose();
    }

    private void ThrowIfPoisoned()
    {
        if (_poisoned)
        {
            throw new SidecarException(
                SidecarErrorCode.RequestTimeout,
                Spec.Name,
                "sidecar channel is poisoned after a timeout; restart required",
                Spec.StderrLogPath);
        }
    }

    private SidecarException ProcessExitedFailure(Exception? inner = null) => new(
        SidecarErrorCode.ProcessExited,
        Spec.Name,
        $"process exited (code={ExitCode?.ToString() ?? "unknown"}); stderr tail: {Truncate(StderrTail)}",
        Spec.StderrLogPath,
        inner);

    private static string Truncate(string value) =>
        value.Length <= 800 ? value : value[^800..];

    private void TryKill()
    {
        try
        {
            if (!_process.HasExited)
            {
                _process.Kill(entireProcessTree: true);
            }
        }
        catch (Exception ex) when (ex is InvalidOperationException or System.ComponentModel.Win32Exception or NotSupportedException)
        {
            // already gone
        }
    }

    private async Task PumpStderrAsync(Process process)
    {
        try
        {
            var reader = process.StandardError;
            while (true)
            {
                var line = await reader.ReadLineAsync().ConfigureAwait(false);
                if (line is null)
                {
                    break;
                }

                lock (_stderrGate)
                {
                    _stderrTail.Add(line);
                    if (_stderrTail.Count > 200)
                    {
                        _stderrTail.RemoveAt(0);
                    }
                }

                try
                {
                    await File.AppendAllTextAsync(Spec.StderrLogPath, line + Environment.NewLine).ConfigureAwait(false);
                }
                catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
                {
                    // diagnostics are best effort; never crash the host for a log write
                }
            }
        }
        catch (Exception ex) when (ex is IOException or ObjectDisposedException or InvalidOperationException)
        {
            // process/pipe closed
        }
    }
}
