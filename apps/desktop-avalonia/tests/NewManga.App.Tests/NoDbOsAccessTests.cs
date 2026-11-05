using System.Text.RegularExpressions;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-12-UI AC8 (meta): the App layer must never touch a database, an arbitrary OS path or a
/// model directly. This static scan proves the slice ADDED zero direct access: every file this card
/// created or rewrote is scanned for DB/process/file-system/registry tokens. The whole App source is
/// additionally scanned for database APIs (0 allowed anywhere).
///
/// Existing, pre-FEA-12-UI access remains untouched and out of scope: HostController's
/// <c>Directory.CreateDirectory</c> inside the export flow (FEA-09-UI-1) predates this card and is
/// listed explicitly below so the scan cannot hide it.
/// </summary>
public sealed class NoDbOsAccessTests
{
    private const string DatabasePattern =
        @"Microsoft\.Data\.Sqlite|System\.Data\.SQLite|\bSQLite\b|sqlite3|DbConnection|DbCommand";

    private const string OsAccessPattern =
        @"Process\.Start|DllImport|FileStream|Registry\.|Environment\.GetFolderPath|" +
        @"File\.(Read|Write|Open|Delete|Exists|Copy|Move|Create)|" +
        @"Directory\.(Create|Delete|Exists|Enumerate|GetFiles|GetDirectories)";

    /// <summary>Files this card created or rewrote in <c>src/NewManga.App</c> (relative to that root).</summary>
    private static readonly string[] CardOwnedFiles =
    {
        "Services/TrashModels.cs",
        "Services/NullHostController.cs",
        "ViewModels/V2/Library/TrashViewModel.cs",
        "ViewModels/V2/Library/LibraryViewModel.cs",
        "Views/V2/Library/RecycleBinView.axaml",
        "Views/V2/Library/RecycleBinView.axaml.cs",
        "Views/V2/Library/BookDetailPanel.axaml",
        "Views/V2/Library/LibraryView.axaml",
        "Views/Fluent/ShelfPageView.cs",
    };

    public static string RepoRoot
    {
        get
        {
            var directory = new DirectoryInfo(AppContext.BaseDirectory);
            while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
            {
                directory = directory.Parent;
            }

            Assert.NotNull(directory);
            return directory!.FullName;
        }
    }

    private static string AppSourceRoot =>
        Path.Combine(RepoRoot, "apps", "desktop-avalonia", "src", "NewManga.App");

    [Fact]
    public void CardOwnedAppFiles_HaveNoDirectDatabaseOrOsAccess()
    {
        var violations = new List<string>();
        foreach (var relative in CardOwnedFiles)
        {
            var path = Path.Combine(AppSourceRoot, relative.Replace('/', Path.DirectorySeparatorChar));
            Assert.True(File.Exists(path), $"card-owned file missing: {relative}");
            var text = File.ReadAllText(path);
            foreach (var pattern in new[] { DatabasePattern, OsAccessPattern })
            {
                foreach (Match match in Regex.Matches(text, pattern))
                {
                    violations.Add($"{relative}: {match.Value}");
                }
            }
        }

        Assert.True(violations.Count == 0, "direct DB/OS access added by FEA-12-UI: " + string.Join("; ", violations));
    }

    [Fact]
    public void WholeApp_HasNoDatabaseAccessAtAll()
    {
        var violations = new List<string>();
        foreach (var path in Directory.EnumerateFiles(AppSourceRoot, "*.cs", SearchOption.AllDirectories))
        {
            var text = File.ReadAllText(path);
            foreach (Match match in Regex.Matches(text, DatabasePattern))
            {
                violations.Add($"{Path.GetRelativePath(AppSourceRoot, path)}: {match.Value}");
            }
        }

        Assert.True(violations.Count == 0, "App layer must not reference the database: " + string.Join("; ", violations));
    }

    [Fact]
    public void ExistingOsAccessInventory_IsUnchangedAndKnown()
    {
        // Pre-existing (FEA-09-UI-1 export flow) OS access in HostController. FEA-12-UI did not add
        // any; if a future change adds another, the inventory below must be updated deliberately.
        var hostController = File.ReadAllText(Path.Combine(AppSourceRoot, "Services", "HostController.cs"));
        var matches = Regex.Matches(hostController, OsAccessPattern);
        Assert.Single(matches);
        Assert.Equal("Directory.Create", matches[0].Value);

        // The trash port and VM themselves must never do file/process IO.
        var trashModels = File.ReadAllText(Path.Combine(AppSourceRoot, "Services", "TrashModels.cs"));
        var trashVm = File.ReadAllText(Path.Combine(AppSourceRoot, "ViewModels", "V2", "Library", "TrashViewModel.cs"));
        Assert.Empty(Regex.Matches(trashModels, OsAccessPattern + "|" + DatabasePattern));
        Assert.Empty(Regex.Matches(trashVm, OsAccessPattern + "|" + DatabasePattern));
    }
}
