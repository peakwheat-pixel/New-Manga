using System.IO;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-07 AC5: the shipped Windows manifest must actually declare PerMonitorV2 awareness (mixed-DPI
/// commit/restore is meaningless if the process runs DPI-unaware).
/// </summary>
public sealed class DpiManifestTests
{
    [Fact]
    public void AppManifest_DeclaresPerMonitorV2()
    {
        var manifest = LocateManifest();
        Assert.NotNull(manifest);
        var text = File.ReadAllText(manifest!);

        Assert.Contains("PerMonitorV2", text, StringComparison.Ordinal);
        Assert.Contains("<dpiAware ", text, StringComparison.Ordinal);
        Assert.Contains("true/pm", text, StringComparison.Ordinal);
    }

    private static string? LocateManifest()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            var candidate = Path.Combine(directory.FullName, "apps", "desktop-avalonia", "src", "NewManga.App", "app.manifest");
            if (File.Exists(candidate))
            {
                return candidate;
            }

            directory = directory.Parent;
        }

        return null;
    }
}
