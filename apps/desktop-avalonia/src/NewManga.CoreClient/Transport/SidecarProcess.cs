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
    private readonly object _stopGate = new();

    /// <summary>
    /// PIPE-EXCLUSIVE-TRANSPORT-1 / E-7: the ONE exclusive entry for this pipe. The sidecar speaks a
    /// strictly request/response protocol over a single stdin/stdout pair, and <see cref="ExchangeAsync"/>
    /// assumes only one request is in flight. Callers must hold a lease for the WHOLE cycle
    /// (write + read + any event-frame skipping), because both halves touch the same shared streams.
    /// Acquiring a second lease concurrently is what produced
    /// "The stream is currently in use by a previous operation on the stream".
    /// </summary>
    private readonly SemaphoreSlim _exchangeGate = new(1, 1);

    /// <summary>
    /// Takes the pipe exclusively. Dispose the returned lease to release it. Use with <c>using var</c> so
    /// an exception can never leak the lease.
    /// </summary>
    public async Task<IDisposable> AcquireExchangeLeaseAsync(CancellationToken cancellationToken = default)
    {
        await _exchangeGate.WaitAsync(cancellationToken).ConfigureAwait(false);
        return new ExchangeLease(_exchangeGate);
    }

    private sealed class ExchangeLease : IDisposable
    {
        private SemaphoreSlim? _gate;

        public ExchangeLease(SemaphoreSlim gate) => _gate = gate;

        public void Dispose()
        {
            var gate = Interlocked.Exchange(ref _gate, null);
            gate?.Release();
        }
    }
    private Task? _stopTask;

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

        // NM-AUD-0001: a pre-cancelled start must never spawn a child.
        cancellationToken.ThrowIfCancellationRequested();

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
            // NM-AUD-0001: a start cancelled after the spawn must tear the child down
            // before the exception escapes -- otherwise the child outlives the caller.
            cancellationToken.ThrowIfCancellationRequested();
        }
        catch (SidecarException)
        {
            await sidecar.DisposeAsync().ConfigureAwait(false);
            throw;
        }
        catch (OperationCanceledException)
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
        catch (OperationCanceledException)
        {
            // E-7 / R-005: the request line is already on the wire (written above), and cancelling the
            // CALLER does not un-write it. Whether the child answers later or never, the request/response
            // pairing on this pipe becomes unknowable -- a leftover response would be read as the answer
            // to the NEXT request (permanent off-by-one, since the protocol is one line per exchange).
            // So BOTH outcomes poison the channel: timeout and caller cancellation.
            // Only the timeout case is translated into a RequestTimeout; a caller cancellation keeps its
            // OperationCanceledException so callers can still distinguish "I cancelled" from "it timed out".
            _poisoned = true;
            if (cancellationToken.IsCancellationRequested)
            {
                throw;
            }

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

    /// <summary>
    /// NM-AUD-0001: stop/cleanup ownership is single-flight and idempotent. Every caller
    /// (explicit stop, cancellation cleanup, DisposeAsync) awaits the same stop task, so a
    /// second caller can never return while the first one is still tearing the child down.
    /// </summary>
    public Task StopAsync(int gracefulTimeoutMs = 3000)
    {
        lock (_stopGate)
        {
            return _stopTask ??= StopCoreAsync(gracefulTimeoutMs);
        }
    }

    private async Task StopCoreAsync(int gracefulTimeoutMs)
    {
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
        await StopAsync().ConfigureAwait(false);
        if (_disposed)
        {
            return;
        }

        _disposed = true;
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
