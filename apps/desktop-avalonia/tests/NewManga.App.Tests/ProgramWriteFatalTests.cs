using NewManga.App;
using NewManga.Host;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-A-8 P2: Program.WriteFatal must never throw — an empty / invalid / too-long / unwritable log
/// path degrades to stderr instead of crashing the process and masking the real startup error.
/// </summary>
public sealed class ProgramWriteFatalTests
{
    private static AppOptions OptionsWithLogDirectory(string logDirectory)
    {
        var options = AppOptions.Parse(new[] { "--data-root=" + Path.Combine(Path.GetTempPath(), "nm-a8-data") });
        Assert.Null(options.InvalidReason);
        // Parse rejects an empty --log-dir, so the guard is exercised through the resolved host option.
        typeof(AppOptions).GetProperty(nameof(AppOptions.LogDirectory))!
            .SetValue(options, logDirectory);
        return options;
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    public void EmptyLogDirectory_DoesNotThrow(string logDirectory)
    {
        var options = OptionsWithLogDirectory(logDirectory);

        Program.WriteFatal(options, "fatal", "simulated startup failure");
    }

    [Fact]
    public void LogPathUnderAFile_DoesNotThrow()
    {
        var root = Path.Combine(Path.GetTempPath(), "nm-a8-file-" + Guid.NewGuid().ToString("N")[..8]);
        Directory.CreateDirectory(root);
        var filePath = Path.Combine(root, "not-a-directory");
        File.WriteAllText(filePath, "x");
        try
        {
            var options = OptionsWithLogDirectory(filePath);
            Program.WriteFatal(options, "fatal", "simulated startup failure");
        }
        finally
        {
            File.Delete(filePath);
            Directory.Delete(root, recursive: true);
        }
    }

    [Fact]
    public void TooLongLogPath_DoesNotThrow()
    {
        var logDirectory = Path.Combine(
            Path.GetTempPath(),
            new string('x', 400) + "-nm-a8-logs");
        var options = OptionsWithLogDirectory(logDirectory);

        Program.WriteFatal(options, "fatal", "simulated startup failure");
    }

    [Fact]
    public void UnwritableLogFile_DoesNotThrow()
    {
        // A directory whose target file is exclusively locked simulates an unwritable log destination
        // without depending on ACLs (works the same for elevated and normal test runs).
        var root = Path.Combine(Path.GetTempPath(), "nm-a8-lock-" + Guid.NewGuid().ToString("N")[..8]);
        Directory.CreateDirectory(root);
        var target = Path.Combine(root, "fatal.log");
        var lockStream = new FileStream(target, FileMode.Create, FileAccess.Write, FileShare.None);
        try
        {
            var options = OptionsWithLogDirectory(root);
            Program.WriteFatal(options, "fatal", "simulated startup failure");
        }
        finally
        {
            lockStream.Dispose();
            File.Delete(target);
            Directory.Delete(root, recursive: true);
        }
    }

    [Fact]
    public void HostOptions_WithEmptyLogDirectory_IsReachableOnlyThroughTheGuard()
    {
        // Sanity: the parser itself refuses the empty value, so users get exit 2 before this path.
        var options = AppOptions.Parse(new[] { "--log-dir=" });
        Assert.NotNull(options.InvalidReason);
        Assert.Contains("non-empty", options.InvalidReason, StringComparison.Ordinal);
    }
}
