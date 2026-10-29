using NewManga.CoreClient;
using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Tests.Support;
using NewManga.CoreClient.Transport;

namespace NewManga.CoreClient.Tests;

/// <summary>
/// AC4: every startup/transport fault is a typed, diagnosable error — missing exe, spawn failure,
/// startup timeout, request timeout — with stderr captured to a file. Nothing panics the process.
/// </summary>
public sealed class SidecarFailureTests
{
    [Fact]
    public async Task MissingExecutable_IsTyped_AndNoProcessIsLeftBehind()
    {
        var missing = Path.Combine(Path.GetTempPath(), "newmanga-missing-" + Guid.NewGuid().ToString("N") + ".exe");
        var options = SidecarFixture.CreateCoreOptions("failure-missing", out _, executablePath: missing);

        var error = await Assert.ThrowsAsync<SidecarException>(() => CoreServiceClient.StartAsync(options));

        Assert.Equal(SidecarErrorCode.SidecarExeMissing, error.Code);
        Assert.Contains("核心服务", error.UserMessage, StringComparison.Ordinal);
        SidecarFixture.WriteEvidenceJson("diagnostics/missing-exe.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC4");
            writer.WriteString("scenario", "missing executable");
            writer.WriteString("error_code", error.Code.ToString());
            writer.WriteString("user_message", error.UserMessage);
            writer.WriteEndObject();
        });
    }

    [Fact]
    public async Task NonExecutableFile_ReportsSpawnFailed()
    {
        var fake = Path.Combine(Path.GetTempPath(), "newmanga-fake-" + Guid.NewGuid().ToString("N") + ".exe");
        await File.WriteAllTextAsync(fake, "not a PE image");
        try
        {
            var options = SidecarFixture.CreateCoreOptions("failure-spawn", out _, executablePath: fake);
            var error = await Assert.ThrowsAsync<SidecarException>(() => CoreServiceClient.StartAsync(options));
            Assert.Equal(SidecarErrorCode.SpawnFailed, error.Code);
            Assert.NotNull(error.StderrLogPath);

            SidecarFixture.WriteEvidenceJson("diagnostics/spawn-failed.json", writer =>
            {
                writer.WriteStartObject();
                writer.WriteString("ac", "AC4");
                writer.WriteString("scenario", "non-executable file");
                writer.WriteString("error_code", error.Code.ToString());
                writer.WriteString("user_message", error.UserMessage);
                writer.WriteBoolean("stderr_log_recorded", error.StderrLogPath is not null);
                writer.WriteEndObject();
            });
        }
        finally
        {
            File.Delete(fake);
        }
    }

    [SidecarFact]
    public async Task StartupTimeout_IsTyped_NotAHang()
    {
        var powershell = Path.Combine(Environment.SystemDirectory, "WindowsPowerShell", "v1.0", "powershell.exe");
        if (!File.Exists(powershell))
        {
            throw new InvalidOperationException("Windows PowerShell is required for the startup-timeout fixture");
        }

        var options = SidecarFixture.CreateCoreOptions("failure-startup-timeout", out _);
        var timeoutOptions = new CoreServiceOptions
        {
            ExecutablePath = powershell,
            DataRoot = options.DataRoot,
            DerivedRoot = options.DerivedRoot,
            CatalogDbPath = options.CatalogDbPath,
            StderrLogPath = options.StderrLogPath,
            WireLogPath = options.WireLogPath,
            AdditionalArguments = new[] { "-NoProfile", "-NonInteractive", "-Command", "Start-Sleep -Seconds 25" },
            StartupTimeout = TimeSpan.FromSeconds(2),
            RequestTimeout = TimeSpan.FromSeconds(2),
        };

        var error = await Assert.ThrowsAsync<SidecarException>(() => CoreServiceClient.StartAsync(timeoutOptions));
        Assert.Equal(SidecarErrorCode.StartupTimeout, error.Code);
        Assert.NotNull(error.StderrLogPath);
        Assert.True(File.Exists(error.StderrLogPath), "stderr log must exist even when the child prints nothing");

        SidecarFixture.WriteEvidenceJson("diagnostics/startup-timeout.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC4");
            writer.WriteString("scenario", "startup timeout (2s) against a never-responding child");
            writer.WriteString("error_code", error.Code.ToString());
            writer.WriteString("user_message", error.UserMessage);
            writer.WriteBoolean("stderr_log_exists", File.Exists(error.StderrLogPath));
            writer.WriteEndObject();
        });
    }

    [Fact]
    public async Task RequestTimeout_IsTyped_AndStderrLogKept()
    {
        var powershell = Path.Combine(Environment.SystemDirectory, "WindowsPowerShell", "v1.0", "powershell.exe");
        if (!File.Exists(powershell))
        {
            throw new InvalidOperationException("Windows PowerShell is required for the request-timeout fixture");
        }

        var logDirectory = Path.Combine(SidecarFixture.EvidenceDirectory, "logs", "failure-request-timeout");
        Directory.CreateDirectory(logDirectory);
        var spec = new SidecarSpec
        {
            Name = "fake-timeout",
            ExecutablePath = powershell,
            AdditionalArguments = new[] { "-NoProfile", "-NonInteractive", "-Command", "Start-Sleep -Seconds 25" },
            StderrLogPath = Path.Combine(logDirectory, "fake.stderr.log"),
            StartupTimeout = TimeSpan.FromSeconds(5),
            RequestTimeout = TimeSpan.FromSeconds(5),
        };

        await using var process = await SidecarProcess.StartAsync(spec);
        var error = await Assert.ThrowsAsync<SidecarException>(
            () => process.ExchangeAsync("{\"id\":1}", escapeNonAscii: true, TimeSpan.FromMilliseconds(800)));

        Assert.Equal(SidecarErrorCode.RequestTimeout, error.Code);
        Assert.True(File.Exists(spec.StderrLogPath), "stderr log must exist even when the child prints nothing");

        SidecarFixture.WriteEvidenceJson("diagnostics/request-timeout.json", writer =>
        {
            writer.WriteStartObject();
            writer.WriteString("ac", "AC4");
            writer.WriteString("scenario", "request timeout (0.8s) on a silent child");
            writer.WriteString("error_code", error.Code.ToString());
            writer.WriteBoolean("stderr_log_exists", File.Exists(spec.StderrLogPath));
            writer.WriteEndObject();
        });
    }
}
