using System.Diagnostics;
using System.Text;
using NewManga.Host.Tests.Support;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// SCHEMA-VERSION-ASSERT-1: guards the cross-language mirror between
/// <see cref="CoreSchema.Current"/> (C# test expectation) and the Python Core's real migration chain.
///
/// Why this test exists: three IPC tests hard-coded the schema version and silently went stale when the
/// product reached v14. Bumping the constant alone would just move the trap, so this test asks PYTHON
/// how many migrations it actually registers (<c>default_migrations()</c>) and requires an exact match.
/// Add v15 on the Python side and this test fails until the C# constant follows -- that is the point.
///
/// Adjudication (Codex, 2026-11-15) required two properties that shaped this implementation:
///   1. the expected value must NOT be read from the artifact under test (we ask Python for the COUNT,
///      we do not read the receipt/DB that the failing tests read); and
///   2. it must run by DEFAULT and must FAIL (not skip) when the environment is missing, otherwise the
///      guard silently disappears in environments without Python.
///
/// It is deliberately tagged with a plain [Fact] (not [SidecarFact]/opt-in) so it always runs.
/// </summary>
public sealed class PythonSchemaMigrationGuardTests
{
    [Fact]
    public void PythonMigrationChain_HasExactlyCoreSchemaCurrentMigrations()
    {
        var python = ResolvePython();
        var repoRoot = ResolveRepoRoot();
        var srcRoot = Path.Combine(repoRoot, "src");

        // Ask the real Python module for the number of registered migrations. We deliberately do NOT
        // parse MIGRATION_V14_NAME with a regex (the adjudication called that out): this executes the
        // actual factory that the product uses.
        var script =
            "import sys; "
            + $"sys.path.insert(0, r'{srcRoot}'); "
            + "from infrastructure.sqlite.schema import default_migrations; "
            + "print('COUNT', len(default_migrations()))";

        var (exitCode, stdout, stderr) = Run(python, script);
        Assert.True(
            exitCode == 0,
            $"python failed to import the schema module (exit={exitCode}).\nstdout: {stdout}\nstderr: {stderr}");

        var line = stdout.Split('\n', StringSplitOptions.RemoveEmptyEntries)
            .Select(text => text.Trim())
            .FirstOrDefault(text => text.StartsWith("COUNT ", StringComparison.Ordinal));

        Assert.False(line is null, $"could not find the COUNT line in python output.\nstdout: {stdout}");

        var pythonCount = int.Parse(line!["COUNT ".Length..], System.Globalization.CultureInfo.InvariantCulture);
        Assert.Equal(CoreSchema.Current, pythonCount);
    }

    private static string ResolvePython()
    {
        // Adjudication: a missing environment must FAIL, not skip. So there is no opt-in gate here.
        var configured = Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON");
        if (!string.IsNullOrWhiteSpace(configured))
        {
            Assert.True(
                File.Exists(configured),
                $"NEWMANGA_BUILD_PYTHON points at '{configured}' but that file does not exist");
            return configured;
        }

        return "python";
    }

    private static string ResolveRepoRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            if (Directory.Exists(Path.Combine(directory.FullName, "src", "infrastructure", "sqlite"))
                && File.Exists(Path.Combine(directory.FullName, "AGENTS.md")))
            {
                return directory.FullName;
            }

            directory = directory.Parent;
        }

        throw new InvalidOperationException(
            $"could not locate the repository root (looked for src/infrastructure/sqlite + AGENTS.md) above {AppContext.BaseDirectory}");
    }

    private static (int ExitCode, string Stdout, string Stderr) Run(string fileName, string arguments)
    {
        var info = new ProcessStartInfo(fileName)
        {
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
        };
        info.ArgumentList.Add("-B");
        info.ArgumentList.Add("-c");
        info.ArgumentList.Add(arguments);

        using var process = Process.Start(info)
            ?? throw new InvalidOperationException($"failed to start '{fileName}'");

        var stdout = new StringBuilder();
        var stderr = new StringBuilder();
        process.OutputDataReceived += (_, e) => { if (e.Data is not null) { stdout.AppendLine(e.Data); } };
        process.ErrorDataReceived += (_, e) => { if (e.Data is not null) { stderr.AppendLine(e.Data); } };
        process.BeginOutputReadLine();
        process.BeginErrorReadLine();

        if (!process.WaitForExit(60_000))
        {
            try { process.Kill(entireProcessTree: true); } catch { }
            throw new InvalidOperationException($"python did not finish within 60s: {fileName}");
        }

        process.WaitForExit();
        return (process.ExitCode, stdout.ToString(), stderr.ToString());
    }
}
