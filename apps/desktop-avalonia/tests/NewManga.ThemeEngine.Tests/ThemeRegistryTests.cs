using NewManga.ThemeEngine;

namespace NewManga.ThemeEngine.Tests;

/// <summary>
/// Registry contract: built-in package plus user directory discovery, install/uninstall/export,
/// reserved ids, quarantine of corrupt files and id/duplicate handling. A broken user theme must never
/// be exposed as a theme nor prevent startup.
/// </summary>
public sealed class ThemeRegistryTests
{
    private static string UserPackageId => "ocean";

    private static ThemePackage UserPackage(string id = "ocean") =>
        ThemeFixtures.AsUser(ThemeFixtures.DefaultPackage, id);

    private static string InstallJson(string id = "ocean") => ThemeFixtures.Write(UserPackage(id));

    [Fact]
    public void Builtin_default_theme_is_always_available()
    {
        using var temp = new TempDirectory();
        var registry = new ThemeRegistry(temp.Path);

        var all = registry.All;
        Assert.Contains(all, descriptor => descriptor.Id == ThemeDefaults.DefaultThemeId);
        Assert.Equal(ThemeKind.BuiltIn, registry.Find(ThemeDefaults.DefaultThemeId)!.Kind);
        Assert.Empty(registry.Diagnostics);
        Assert.Equal(ThemeFixtures.DefaultPackage, registry.Load(ThemeDefaults.DefaultThemeId));
    }

    [Fact]
    public void Find_unknown_returns_null_and_load_unknown_throws_a_structured_exception()
    {
        using var temp = new TempDirectory();
        var registry = new ThemeRegistry(temp.Path);

        Assert.Null(registry.Find("missing-theme"));
        var exception = Assert.Throws<ThemePackageException>(() => registry.Load("missing-theme"));
        Assert.Contains(exception.Issues, issue => issue.Code == ThemeIssueCodes.ThemeNotFound);
    }

    [Fact]
    public async Task Install_writes_the_user_theme_and_makes_it_loadable()
    {
        using var temp = new TempDirectory();
        var registry = new ThemeRegistry(temp.Path);

        var result = await registry.InstallAsync(ThemeFixtures.Stream(InstallJson()));

        Assert.True(result.IsValid, string.Join(", ", result.Issues.Select(issue => issue.Message)));
        Assert.True(File.Exists(Path.Combine(temp.Path, UserPackageId + ".nmtheme")));
        Assert.Contains(registry.All, descriptor => descriptor.Id == UserPackageId);
        var loaded = registry.Load(UserPackageId);
        Assert.Equal(ThemeKind.User, loaded.Descriptor.Kind);
        Assert.Equal(ThemeFixtures.DefaultPackage.Light, loaded.Light);
    }

    [Fact]
    public async Task Install_rejects_an_invalid_package_without_writing_a_file()
    {
        using var temp = new TempDirectory();
        var registry = new ThemeRegistry(temp.Path);
        var json = InstallJson().Replace("\"#FFFFFF\"", "\"linear-gradient(#fff,#000)\"", StringComparison.Ordinal);

        var result = await registry.InstallAsync(ThemeFixtures.Stream(json));

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue => issue.Code == ThemeIssueCodes.ColorInvalidValue);
        Assert.DoesNotContain(registry.All, descriptor => descriptor.Id == UserPackageId);
        Assert.False(File.Exists(Path.Combine(temp.Path, UserPackageId + ".nmtheme")));
    }

    [Fact]
    public async Task Install_rejects_a_builtin_id_from_being_shadowed()
    {
        using var temp = new TempDirectory();
        var registry = new ThemeRegistry(temp.Path);
        var package = UserPackage(ThemeDefaults.DefaultThemeId);

        var result = await registry.InstallAsync(ThemeFixtures.Stream(package));

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue => issue.Code == ThemeIssueCodes.RegistryIdReserved);
        Assert.Equal(ThemeKind.BuiltIn, registry.Find(ThemeDefaults.DefaultThemeId)!.Kind);
    }

    [Fact]
    public async Task Install_normalizes_a_declared_builtin_kind_to_user()
    {
        using var temp = new TempDirectory();
        var registry = new ThemeRegistry(temp.Path);
        var package = ThemeFixtures.DefaultPackage with
        {
            Descriptor = ThemeFixtures.DefaultPackage.Descriptor with { Id = "copied-theme", Name = "Copied" },
        };

        var result = await registry.InstallAsync(ThemeFixtures.Stream(package));

        Assert.True(result.IsValid, string.Join(", ", result.Issues.Select(issue => issue.Message)));
        Assert.Contains(result.Warnings, issue => issue.Code == ThemeIssueCodes.InstallKindNormalized);
        Assert.Equal(ThemeKind.User, registry.Find("copied-theme")!.Kind);
    }

    [Fact]
    public async Task Install_rejects_an_oversized_package()
    {
        using var temp = new TempDirectory();
        var registry = new ThemeRegistry(temp.Path);
        var oversized = new MemoryStream(new byte[ThemePackageJson.MaxDocumentBytes + 1024]);

        var result = await registry.InstallAsync(oversized);

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue => issue.Code == ThemeIssueCodes.InstallTooLarge);
    }

    [Fact]
    public async Task Install_rejects_a_path_traversal_id()
    {
        using var temp = new TempDirectory();
        var registry = new ThemeRegistry(temp.Path);
        var package = ThemeFixtures.AsUser(ThemeFixtures.DefaultPackage, "../escape");

        var result = await registry.InstallAsync(ThemeFixtures.Stream(package));

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue => issue.Code == ThemeIssueCodes.DescriptorIdInvalid);
        Assert.False(File.Exists(Path.Combine(temp.Path, "..", "escape.nmtheme")));
    }

    [Fact]
    public async Task Installing_the_same_id_twice_overwrites_the_previous_file()
    {
        using var temp = new TempDirectory();
        var registry = new ThemeRegistry(temp.Path);
        await registry.InstallAsync(ThemeFixtures.Stream(InstallJson()));

        var second = ThemeFixtures.AsUser(ThemeFixtures.DefaultPackage, UserPackageId, name: "Ocean v2");
        await registry.InstallAsync(ThemeFixtures.Stream(second));

        Assert.Single(registry.All, descriptor => descriptor.Id == UserPackageId);
        Assert.Equal("Ocean v2", registry.Find(UserPackageId)!.Name);
    }

    [Fact]
    public async Task Uninstall_removes_installed_themes_but_never_builtins()
    {
        using var temp = new TempDirectory();
        var registry = new ThemeRegistry(temp.Path);
        await registry.InstallAsync(ThemeFixtures.Stream(InstallJson()));

        Assert.False(await registry.UninstallAsync(ThemeDefaults.DefaultThemeId));
        Assert.False(await registry.UninstallAsync("missing-theme"));
        Assert.True(await registry.UninstallAsync(UserPackageId));

        Assert.Null(registry.Find(UserPackageId));
        Assert.False(File.Exists(Path.Combine(temp.Path, UserPackageId + ".nmtheme")));
    }

    [Fact]
    public async Task Export_round_trips_a_package_through_the_schema()
    {
        using var temp = new TempDirectory();
        var registry = new ThemeRegistry(temp.Path);
        await registry.InstallAsync(ThemeFixtures.Stream(InstallJson()));

        var exportedBuiltin = await registry.ExportAsync(ThemeDefaults.DefaultThemeId);
        var exportedUser = await registry.ExportAsync(UserPackageId);

        Assert.Equal(ThemeFixtures.DefaultPackage, ThemePackageJson.Read(exportedBuiltin).Package);
        Assert.Equal(UserPackage(), ThemePackageJson.Read(exportedUser).Package);
    }

    [Fact]
    public void Scan_quarantines_corrupt_files_and_keeps_valid_json_extension_themes()
    {
        using var temp = new TempDirectory();
        File.WriteAllText(Path.Combine(temp.Path, "broken.nmtheme"), "{ half a document");
        File.WriteAllText(Path.Combine(temp.Path, "broken.json"), "{ also broken");
        var jsonTheme = ThemeFixtures.Write(ThemeFixtures.AsUser(ThemeFixtures.DefaultPackage, "json-theme"));
        File.WriteAllText(Path.Combine(temp.Path, "json-theme.json"), jsonTheme);

        var registry = new ThemeRegistry(temp.Path);

        Assert.Contains(registry.All, descriptor => descriptor.Id == "json-theme");
        Assert.Equal(2, registry.Diagnostics.Count(issue => issue.Code == ThemeIssueCodes.RegistryFileInvalid));
        Assert.DoesNotContain(registry.All, descriptor => descriptor.Id == "broken");
    }

    [Fact]
    public void Scan_prefers_the_nmtheme_file_and_reports_duplicate_ids()
    {
        using var temp = new TempDirectory();
        var package = ThemeFixtures.AsUser(ThemeFixtures.DefaultPackage, "dupe");
        File.WriteAllText(Path.Combine(temp.Path, "dupe.nmtheme"), ThemeFixtures.Write(package));
        File.WriteAllText(
            Path.Combine(temp.Path, "dupe-copy.json"),
            ThemeFixtures.Write(package with { Descriptor = package.Descriptor with { Name = "Dupe copy" } }));

        var registry = new ThemeRegistry(temp.Path);

        Assert.Single(registry.All, descriptor => descriptor.Id == "dupe");
        Assert.Contains(registry.Diagnostics, issue => issue.Code == ThemeIssueCodes.RegistryDuplicateId);
    }

    [Fact]
    public void Scan_ignores_files_that_try_to_take_over_a_builtin_id()
    {
        using var temp = new TempDirectory();
        var package = ThemeFixtures.AsUser(ThemeFixtures.DefaultPackage, ThemeDefaults.DefaultThemeId);
        File.WriteAllText(Path.Combine(temp.Path, "shadowing.nmtheme"), ThemeFixtures.Write(package));

        var registry = new ThemeRegistry(temp.Path);

        Assert.Equal(ThemeKind.BuiltIn, registry.Find(ThemeDefaults.DefaultThemeId)!.Kind);
        Assert.Contains(registry.Diagnostics, issue => issue.Code == ThemeIssueCodes.RegistryIdReserved);
    }

    [Fact]
    public async Task Refresh_picks_up_files_written_after_construction()
    {
        using var temp = new TempDirectory();
        var registry = new ThemeRegistry(temp.Path);
        Assert.DoesNotContain(registry.All, descriptor => descriptor.Id == "late-theme");

        var package = ThemeFixtures.AsUser(ThemeFixtures.DefaultPackage, "late-theme");
        File.WriteAllText(Path.Combine(temp.Path, "late-theme.nmtheme"), ThemeFixtures.Write(package));
        await registry.RefreshAsync();

        Assert.Contains(registry.All, descriptor => descriptor.Id == "late-theme");
    }

    [Fact]
    public async Task User_themes_are_listed_after_builtins_in_ordinal_order()
    {
        using var temp = new TempDirectory();
        var registry = new ThemeRegistry(temp.Path);
        await registry.InstallAsync(ThemeFixtures.Stream(InstallJson("zulu")));
        await registry.InstallAsync(ThemeFixtures.Stream(InstallJson("alpha")));

        var ids = registry.All.Select(descriptor => descriptor.Id).ToArray();

        Assert.Equal(ThemeDefaults.DefaultThemeId, ids[0]);
        Assert.Equal(new[] { "alpha", "zulu" }, ids.Skip(1));
    }
}
