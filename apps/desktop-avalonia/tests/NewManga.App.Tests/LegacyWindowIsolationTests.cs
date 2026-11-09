using System.Text.RegularExpressions;
using Avalonia.Headless.XUnit;
using Avalonia.Threading;
using NewManga.App.Views;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07-RESIDUAL-4 / L-R4b-1 / D-R4b-7: the default headless suite must never write to the real
/// <c>%APPDATA%\com.newmanga.desktop\logs\window-material.log</c>.
///
/// <para>
/// Legacy <see cref="MainWindow"/> resolves its diagnostics root from <c>AppOptions.LogDirectory</c>
/// only; <c>--data-root</c> alone does NOT isolate that file. Every test that calls
/// <see cref="MainWindow.Show"/> in the default suite must therefore pass an explicit isolated
/// <c>--log-dir</c> (see <see cref="LegacyUiTestOptions.Isolated"/>).
/// </para>
/// </summary>
public sealed class LegacyWindowIsolationTests
{
    private static readonly (string File, int ExpectedIsolatedSites)[] LegacyShowSiteFiles =
    {
        ("CredentialUiTests.cs", 1),
        ("F11HotkeyTests.cs", 1),
        ("LegacyAppearanceSyncTests.cs", 1),
        ("ImportExportUiTests.cs", 3),
        ("RegionWorkbenchUiTests.cs", 1),
        ("ThemeRetirementR4Tests.cs", 2),
    };

    [Fact]
    public void AllDefaultSuiteLegacyWindowShows_AreExplicitlyIsolated()
    {
        var testsDirectory = FindTestsSourceRoot();
        var defaultOptions = new Regex(
            @"new\s+MainWindow\s*\([^;{}]*?new\s+AppOptions\s*\(\s*\)",
            RegexOptions.Singleline | RegexOptions.CultureInvariant);

        foreach (var (file, expected) in LegacyShowSiteFiles)
        {
            var path = Path.Combine(testsDirectory, file);
            Assert.True(File.Exists(path), "missing legacy UI test source: " + path);
            var text = File.ReadAllText(path);

            Assert.False(
                defaultOptions.IsMatch(text),
                file + " still constructs a legacy MainWindow with the default AppOptions (real %APPDATA% log root). "
                + "Use LegacyUiTestOptions.Isolated() instead.");

            var isolated = Regex.Matches(
                text,
                @"LegacyUiTestOptions\.Isolated\s*\(",
                RegexOptions.CultureInvariant).Count;
            Assert.True(
                isolated >= expected,
                $"{file}: expected at least {expected} LegacyUiTestOptions.Isolated() call site(s) but found {isolated}.");
        }
    }

    [Fact]
    public void IsolatedOptions_PointAtTemporaryDirectoriesOnly()
    {
        var options = LegacyUiTestOptions.Isolated();
        var host = options.ToHostOptions();
        var temp = Path.GetFullPath(Path.GetTempPath());

        Assert.StartsWith(temp, Path.GetFullPath(host.LogDirectory), StringComparison.OrdinalIgnoreCase);
        Assert.StartsWith(temp, Path.GetFullPath(host.DataRoot), StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("com.newmanga.desktop", host.LogDirectory, StringComparison.OrdinalIgnoreCase);
    }

    [AvaloniaFact]
    public void LegacyMainWindow_Show_WritesMaterialLogOnlyUnderIsolatedLogDir()
    {
        var realLog = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "com.newmanga.desktop",
            "logs",
            "window-material.log");
        var realBefore = CountLines(realLog);
        var cwdMarker = Path.Combine(Directory.GetCurrentDirectory(), "com.newmanga.desktop");
        var cwdExistedBefore = Directory.Exists(cwdMarker);

        var options = LegacyUiTestOptions.Isolated();
        var isolatedLog = Path.Combine(options.ToHostOptions().LogDirectory, "window-material.log");
        var controller = new FakeHostController(FakeHostController.ReadySnapshot());

        var window = new MainWindow(controller, options);
        window.Show();
        Dispatcher.UIThread.RunJobs();
        window.Close();
        Dispatcher.UIThread.RunJobs();

        Assert.True(
            File.Exists(isolatedLog),
            "expected the isolated --log-dir to receive window-material.log: " + isolatedLog);
        Assert.True(CountLines(isolatedLog) >= 1, "isolated window-material.log should contain at least one material line");

        // Read-only comparison against the real user directory: Show() must not append anything there.
        Assert.Equal(realBefore, CountLines(realLog));

        if (!cwdExistedBefore)
        {
            Assert.False(Directory.Exists(cwdMarker), "Show() must not create a cwd-relative com.newmanga.desktop directory");
        }
    }

    private static int CountLines(string path)
    {
        if (!File.Exists(path))
        {
            return 0;
        }

        var count = 0;
        using var reader = new StreamReader(path);
        while (reader.ReadLine() is not null)
        {
            count++;
        }

        return count;
    }

    private static string FindTestsSourceRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            var candidate = Path.Combine(
                directory.FullName, "apps", "desktop-avalonia", "tests", "NewManga.App.Tests");
            if (Directory.Exists(candidate))
            {
                return candidate;
            }

            directory = directory.Parent;
        }

        throw new InvalidOperationException(
            "apps/desktop-avalonia/tests/NewManga.App.Tests not found above the test binaries");
    }
}

/// <summary>
/// Shared isolated options for default-suite legacy <see cref="MainWindow"/> tests. Each call creates a
/// unique temporary root (so parallel tests cannot collide) and registers cleanup on process exit.
/// </summary>
internal static class LegacyUiTestOptions
{
    private static readonly object Gate = new();
    private static readonly List<string> Roots = new();
    private static bool _cleanupRegistered;

    internal static AppOptions Isolated()
    {
        var root = Path.Combine(Path.GetTempPath(), "nm-legacy-ui-" + Guid.NewGuid().ToString("N"));
        var logs = Path.Combine(root, "logs");
        Directory.CreateDirectory(logs);

        lock (Gate)
        {
            Roots.Add(root);
            if (!_cleanupRegistered)
            {
                _cleanupRegistered = true;
                AppDomain.CurrentDomain.ProcessExit += (_, _) => Cleanup();
            }
        }

        return AppOptions.Parse(new[]
        {
            "--data-root", Path.Combine(root, "data"),
            "--log-dir", logs,
        });
    }

    internal static void Cleanup()
    {
        lock (Gate)
        {
            foreach (var root in Roots)
            {
                try
                {
                    if (Directory.Exists(root))
                    {
                        Directory.Delete(root, recursive: true);
                    }
                }
                catch
                {
                    // Best effort: temp cleanup failures must never fail a test run.
                }
            }

            Roots.Clear();
        }
    }
}
