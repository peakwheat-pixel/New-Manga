using System.Reflection;
using NewManga.ThemeEngine;

namespace NewManga.ThemeEngine.Tests;

/// <summary>
/// Freezes the public contract surface against V11R_AVALONIA_CONTRACT §4: record component names/order,
/// enum declaration order (numeric values are part of the frozen signature), interface member sets and
/// the schema/id constants the rest of the V11R work streams code against.
/// </summary>
public sealed class ThemeContractTests
{
    [Theory]
    [InlineData(typeof(ThemeKind), "BuiltIn,User")]
    [InlineData(typeof(AppearanceMode), "Light,Dark,System")]
    [InlineData(typeof(ContrastMode), "Standard,High")]
    [InlineData(typeof(LayoutNavigation), "TopBand,Sidebar,Dock")]
    [InlineData(typeof(ShelfLayout), "Grid,List,Masonry")]
    [InlineData(typeof(Density), "Comfortable,Compact,Spacious")]
    [InlineData(typeof(WorkbenchLayout), "Stacked,Split")]
    [InlineData(typeof(ReaderLayout), "FitPage,FitWidth,DoublePage,Webtoon")]
    public void Contract_enums_keep_their_declared_member_order(Type enumType, string expected)
    {
        Assert.True(enumType.IsEnum);
        Assert.Equal(expected, string.Join(',', Enum.GetNames(enumType)));
    }

    [Fact]
    public void Appearance_enum_numeric_values_stay_contract_compatible()
    {
        // The frozen declaration is Light, Dark, System: numeric values are observable to consumers.
        Assert.Equal(0, (int)AppearanceMode.Light);
        Assert.Equal(1, (int)AppearanceMode.Dark);
        Assert.Equal(2, (int)AppearanceMode.System);
    }

    [Theory]
    [InlineData(typeof(ThemeDescriptor), "Id,Name,Version,Author,Description,Kind,Tags,SupportsLight,SupportsDark,PreviewHint")]
    [InlineData(typeof(ThemePackage), "Schema,Descriptor,Light,Dark,Metadata")]
    [InlineData(typeof(LayoutProfile), "Id,Navigation,Shelf,Density,Workbench,Reader")]
    [InlineData(typeof(ThemeSettings), "ThemeId,Appearance,Contrast,Layout,ReducedMotion,FollowSystemAccent")]
    [InlineData(typeof(ThemeValidationIssue), "Code,Severity,Message,Path")]
    [InlineData(typeof(ThemeValidationResult), "IsValid,Issues")]
    [InlineData(typeof(ThemeApplyResult), "Success,AppliedThemeId,Issues,Recovered")]
    public void Record_components_match_the_frozen_contract(Type recordType, string expected)
    {
        // Positional record components are the primary constructor parameters; extra members added by
        // the implementation (e.g. ThemeValidationIssue.IsError) are not part of the contract surface.
        var constructor = recordType.GetConstructors(BindingFlags.Public | BindingFlags.Instance)
            .OrderByDescending(candidate => candidate.GetParameters().Length)
            .First();
        var components = constructor.GetParameters().Select(parameter => parameter.Name).ToArray();

        Assert.Equal(expected.Split(','), components);
        Assert.True(recordType.IsSealed, $"{recordType.Name} must be a sealed record");
    }

    [Theory]
    [InlineData(typeof(IThemeService), "Current,Settings,Changed,InitializeAsync,ApplyAsync,SetAppearanceAsync,SetContrastAsync,SetLayoutAsync,SetReducedMotionAsync,ResetToDefaultAsync")]
    [InlineData(typeof(IThemeRegistry), "All,Find,Load,RefreshAsync,InstallAsync,UninstallAsync,ExportAsync")]
    [InlineData(typeof(IThemePreviewEngine), "Begin")]
    [InlineData(typeof(IThemeValidator), "Validate")]
    [InlineData(typeof(IThemePersistence), "Load,SaveAsync")]
    public void Interface_members_match_the_frozen_contract(Type interfaceType, string expected)
    {
        var members = interfaceType.GetMembers()
            .Where(member => member.MemberType is MemberTypes.Property or MemberTypes.Event ||
                             (member.MemberType == MemberTypes.Method && !((MethodInfo)member).IsSpecialName))
            .Select(member => member.Name)
            .OrderBy(name => name, StringComparer.Ordinal)
            .ToArray();
        var expectedNames = expected.Split(',').OrderBy(name => name, StringComparer.Ordinal).ToArray();

        Assert.Equal(expectedNames, members);
    }

    [Fact]
    public void Preview_session_contract_is_exactly_the_three_methods_on_disposable()
    {
        var members = typeof(IThemePreviewSession).GetMembers()
            .Where(member => member.MemberType is MemberTypes.Property or MemberTypes.Event ||
                             (member.MemberType == MemberTypes.Method && !((MethodInfo)member).IsSpecialName))
            .Select(member => member.Name)
            .OrderBy(name => name, StringComparer.Ordinal)
            .ToArray();

        Assert.Equal(["Cancel", "Commit", "Update"], members);
        Assert.Contains(typeof(IDisposable), typeof(IThemePreviewSession).GetInterfaces());
    }

    [Fact]
    public void Schema_constants_match_the_contract()
    {
        Assert.Equal("newmanga.theme/1", ThemeDefaults.Schema);
        Assert.Equal("newmanga.theme-settings/1", ThemeDefaults.SettingsSchema);
        Assert.Equal("newmanga-default", ThemeDefaults.DefaultThemeId);
        Assert.Equal("1", ThemeDefaults.EngineVersion);
        Assert.Equal("themes", ThemeDefaults.ThemeDirectoryName);
        Assert.Equal("theme-settings.json", ThemeDefaults.SettingsFileName);
        Assert.Equal("settings.legacy-theme-id", ThemeIssueCodes.SettingsLegacyThemeId);
    }

    [Fact]
    public void Severity_channel_is_the_contract_string_pair()
    {
        Assert.Equal("error", ThemeValidationIssue.ErrorSeverity);
        Assert.Equal("warning", ThemeValidationIssue.WarningSeverity);
        Assert.True(ThemeValidationIssue.Error("x", "y").IsError);
        Assert.False(ThemeValidationIssue.Warning("x", "y").IsError);
    }
}
