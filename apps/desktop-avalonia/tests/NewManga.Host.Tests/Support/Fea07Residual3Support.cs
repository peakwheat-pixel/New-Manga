using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using Xunit;

namespace NewManga.Host.Tests.Support;

/// <summary>
/// FEA-07-RESIDUAL-3 AC-R4b-1（AC1 / A03）：gated 真实 Host/Core 用例的门禁。默认 skip + reason，
/// 只在 <c>NEWMANGA_FEA07_A03=1</c> 时启用（真实 Python Core + 真实 <c>library.db</c> + 内嵌 Python 读库）。
/// </summary>
public sealed class Fea07Residual3A03FactAttribute : FactAttribute
{
    public const string GateVariable = "NEWMANGA_FEA07_A03";

    public Fea07Residual3A03FactAttribute()
    {
        if (Environment.GetEnvironmentVariable(GateVariable) != "1")
        {
            Skip = $"reason: gated real Host/Core A03 matrix; set {GateVariable}=1 " +
                   "(needs the repository Python at NEWMANGA_BUILD_PYTHON or C:/Python314/python.exe)";
        }
    }
}

/// <summary>
/// AC-R4b-1 的隔离夹具：仓库根、Python 解释器、隔离数据根（<c>&lt;repo&gt;.workspace/FEA-07-RESIDUAL-3/</c>，
/// 不写仓库跟踪文件、不碰真实 <c>%APPDATA%</c>），以及「内嵌 Python 脚本读库」的先例通路
/// （<c>Fea11RunGrantIpcTests.cs:1178-1197</c> 形态：不新增 SQLite 依赖，只 shell 出仓库自带的 Python）。
/// </summary>
public static class Fea07Residual3Fixture
{
    public const string ResultMarker = "RESULT_JSON:";

    /// <summary>仓库根（含 <c>.git</c> 的目录）。</summary>
    public static string ResolveRepositoryRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
        {
            directory = directory.Parent;
        }

        return directory?.FullName ?? throw new InvalidOperationException("repository not found");
    }

    public static string ResolvePython() =>
        Environment.GetEnvironmentVariable("NEWMANGA_BUILD_PYTHON") ?? "C:/Python314/python.exe";

    /// <summary>隔离数据根：派生产物只落在仓外 workspace（WORKSPACE_GOVERNANCE）。</summary>
    public static string NewDataRoot(string repositoryRoot, string label)
    {
        var root = Path.Combine(
            repositoryRoot + ".workspace",
            "FEA-07-RESIDUAL-3",
            "fixtures",
            label + "-" + Guid.NewGuid().ToString("N")[..12]);
        Directory.CreateDirectory(root);
        Directory.CreateDirectory(Path.Combine(root, "derived"));
        return root;
    }

    /// <summary>
    /// 运行内嵌 Python 脚本并返回 <c>RESULT_JSON:</c> 行的 JSON（不引入任何 SQLite 托管依赖）。
    /// </summary>
    public static async Task<JsonElement> RunPythonForJsonAsync(
        string repositoryRoot,
        string python,
        string script,
        string workingRoot)
    {
        var receipt = await RunPythonAsync(repositoryRoot, python, script, workingRoot);
        var line = receipt.Stdout
            .Split('\n')
            .Select(text => text.TrimEnd('\r'))
            .LastOrDefault(text => text.StartsWith(ResultMarker, StringComparison.Ordinal));
        Assert.True(line is not null, "embedded Python produced no result line; stdout:" + receipt.Stdout +
                                       " stderr:" + receipt.Stderr);
        try
        {
            using var document = JsonDocument.Parse(line![ResultMarker.Length..]);
            return document.RootElement.Clone();
        }
        catch (JsonException exception)
        {
            Assert.Fail($"embedded Python result line is not valid JSON ({exception.Message}); " +
                        $"stdout:{receipt.Stdout} stderr:{receipt.Stderr}");
            throw;
        }
    }

    public static async Task<(int ExitCode, string Stdout, string Stderr)> RunPythonAsync(
        string repositoryRoot,
        string python,
        string script,
        string workingRoot)
    {
        Assert.True(File.Exists(python), $"python interpreter not found: {python}");
        var startInfo = new ProcessStartInfo(python)
        {
            WorkingDirectory = repositoryRoot,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            // The child runs with `-X utf8`; decode its pipes as UTF-8 instead of the ANSI code page
            // (the fixture text is Unicode, and an ANSI decode corrupts the result JSON).
            StandardOutputEncoding = new System.Text.UTF8Encoding(encoderShouldEmitUTF8Identifier: false),
            StandardErrorEncoding = new System.Text.UTF8Encoding(encoderShouldEmitUTF8Identifier: false),
        };
        startInfo.ArgumentList.Add("-X");
        startInfo.ArgumentList.Add("utf8");
        startInfo.ArgumentList.Add("-c");
        startInfo.ArgumentList.Add(script);
        startInfo.ArgumentList.Add(workingRoot);

        using var process = Process.Start(startInfo)
            ?? throw new InvalidOperationException($"failed to start {python}");
        var stdout = process.StandardOutput.ReadToEndAsync();
        var stderr = process.StandardError.ReadToEndAsync();
        await process.WaitForExitAsync();
        Assert.True(process.ExitCode == 0,
            $"embedded Python failed ({process.ExitCode}):{await stderr}{await stdout}");
        return (process.ExitCode, await stdout, await stderr);
    }

    public static void TryDeleteDirectory(string path)
    {
        try
        {
            if (Directory.Exists(path))
            {
                Directory.Delete(path, recursive: true);
            }
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
        {
            // best effort: the isolated workspace root is disposable
        }
    }

    public static IReadOnlyList<string> Diff(IReadOnlyDictionary<string, string> before, IReadOnlyDictionary<string, string> after)
    {
        var differences = new List<string>();
        foreach (var (key, value) in before.OrderBy(pair => pair.Key, StringComparer.Ordinal))
        {
            if (!after.TryGetValue(key, out var current))
            {
                differences.Add($"{key}: removed ({value})");
            }
            else if (!string.Equals(value, current, StringComparison.Ordinal))
            {
                differences.Add($"{key}: {value} -> {current}");
            }
        }

        foreach (var key in after.Keys.Except(before.Keys, StringComparer.Ordinal).OrderBy(text => text, StringComparer.Ordinal))
        {
            differences.Add($"{key}: added ({after[key]})");
        }

        return differences;
    }
}
