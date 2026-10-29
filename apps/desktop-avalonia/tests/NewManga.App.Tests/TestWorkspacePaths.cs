using System;
using System.IO;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-A-4: resolves workspace/task-env fixture paths without a hardcoded maintainer checkout.
/// Order: NEWMANGA_WORKSPACE_ROOT, then the workspace sibling of the repository root
/// (&lt;repo&gt;/../&lt;repo-name&gt;.workspace), then a clearly missing temp path (tests self-skip).
/// </summary>
internal static class TestWorkspacePaths
{
    private static readonly Lazy<string> Root = new(Resolve);

    public static string Workspace => Root.Value;

    public static string Path(string relative) =>
        System.IO.Path.Combine(Workspace, relative.Replace('/', System.IO.Path.DirectorySeparatorChar));

    private static string Resolve()
    {
        var configured = Environment.GetEnvironmentVariable("NEWMANGA_WORKSPACE_ROOT");
        if (!string.IsNullOrWhiteSpace(configured))
        {
            return configured;
        }

        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            if (File.Exists(System.IO.Path.Combine(directory.FullName, "AGENTS.md")) &&
                Directory.Exists(System.IO.Path.Combine(directory.FullName, "apps", "desktop-avalonia")))
            {
                return System.IO.Path.Combine(directory.Parent!.FullName, directory.Name + ".workspace");
            }

            directory = directory.Parent;
        }

        return System.IO.Path.Combine(System.IO.Path.GetTempPath(), "newmanga-workspace-missing");
    }
}
