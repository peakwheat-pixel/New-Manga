using NewManga.DesignSystem;
using NewManga.ThemeEngine;

namespace NewManga.ThemeEngine.Tests;

/// <summary>
/// Validator contract: required token completeness, color format, the 3px corner hard rule, forbidden
/// effect declarations, WCAG 2.1 floors and schema versioning. Every error branch is pinned here; the
/// shipped default theme must validate cleanly (R-09 remediated baseline).
/// </summary>
public sealed class ThemeValidatorTests
{
    private static ThemeValidator Validator => ThemeValidator.Default;

    private static ThemePackage Default => ThemeFixtures.DefaultPackage;

    private static ThemePackage WithLight(ThemePackage package, ThemeTokenSet light) => package with { Light = light };

    private static ThemePackage WithDark(ThemePackage package, ThemeTokenSet dark) => package with { Dark = dark };

    private static ThemePackage WithDescriptor(ThemePackage package, ThemeDescriptor descriptor) =>
        package with { Descriptor = descriptor };

    private static ThemePackage WithMetadata(ThemePackage package, ThemeMetadata metadata) =>
        package with { Metadata = metadata };

    [Fact]
    public void Shipped_default_theme_validates_without_errors()
    {
        var result = Validator.Validate(Default);

        Assert.True(result.IsValid, Describe(result.Errors));
        Assert.Empty(result.Errors);
    }

    [Fact]
    public void Embedded_default_theme_matches_the_generated_package_and_validates()
    {
        Assert.True(BuiltInThemes.IsDefaultAvailable);
        Assert.Equal(Default, BuiltInThemes.Default);

        var result = Validator.Validate(BuiltInThemes.Default);
        Assert.True(result.IsValid, Describe(result.Errors));
    }

    [Fact]
    public void Missing_required_color_is_an_error()
    {
        var colors = new Dictionary<string, string>(Default.Light.Colors, StringComparer.Ordinal);
        colors.Remove(NmKeys.Color.Status.Failed);
        var package = WithLight(Default, Default.Light with { Colors = colors });

        var result = Validator.Validate(package);

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue =>
            issue.Code == ThemeIssueCodes.ColorMissingKey && issue.Path == "light.colors.Nm.Color.Status.Failed");
    }

    [Fact]
    public void Unknown_color_key_is_only_a_warning()
    {
        var set = ThemeFixtures.WithColor(Default.Light, "Nm.Color.Future.Extra", "#123456");
        var result = Validator.Validate(WithLight(Default, set));

        Assert.True(result.IsValid, Describe(result.Errors));
        Assert.Contains(result.Warnings, issue => issue.Code == ThemeIssueCodes.ColorUnknownKey);
    }

    [Fact]
    public void Unparseable_color_is_an_error()
    {
        var set = ThemeFixtures.WithColor(
            Default.Light,
            NmKeys.Color.Bg.Panel,
            "linear-gradient(#fff, #000)");
        var result = Validator.Validate(WithLight(Default, set));

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue =>
            issue.Code == ThemeIssueCodes.ColorInvalidValue && issue.Path == "light.colors.Nm.Color.Bg.Panel");
    }

    [Theory]
    [InlineData(0.0)]
    [InlineData(2.0)]
    [InlineData(3.0)]
    public void Corner_values_up_to_three_pixels_are_legal(double radius)
    {
        var set = ThemeFixtures.WithCorners(Default.Dark, new ThemeCorners(0, radius, radius));
        var result = Validator.Validate(WithDark(Default, set));

        Assert.True(result.IsValid, Describe(result.Errors));
        Assert.DoesNotContain(result.Errors, issue => issue.Code == ThemeIssueCodes.CornerOutOfRange);
    }

    [Theory]
    [InlineData(3.5)]
    [InlineData(4.0)]
    [InlineData(12.0)]
    [InlineData(-1.0)]
    public void Corner_values_outside_zero_to_three_are_errors(double radius)
    {
        var set = ThemeFixtures.WithCorners(Default.Dark, new ThemeCorners(0, radius, radius));
        var result = Validator.Validate(WithDark(Default, set));

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue => issue.Code == ThemeIssueCodes.CornerOutOfRange);
    }

    [Fact]
    public void Font_scale_outside_the_eighty_to_hundred_thirty_percent_range_is_an_error()
    {
        var typography = Default.Dark.Typography with { Scale = 1.5 };
        var set = ThemeFixtures.WithTypography(Default.Dark, typography);
        var result = Validator.Validate(WithDark(Default, set));

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue => issue.Code == ThemeIssueCodes.FontScaleOutOfRange);
    }

    [Fact]
    public void Bundled_font_path_is_an_error()
    {
        var typography = Default.Dark.Typography with { Ui = "fonts/SegoeCool.ttf" };
        var set = ThemeFixtures.WithTypography(Default.Dark, typography);
        var result = Validator.Validate(WithDark(Default, set));

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue => issue.Code == ThemeIssueCodes.FontFamilyInvalid);
    }

    [Fact]
    public void Font_family_of_only_css_generics_is_an_error()
    {
        var typography = Default.Dark.Typography with { Ui = "system-ui, sans-serif" };
        var set = ThemeFixtures.WithTypography(Default.Dark, typography);
        var result = Validator.Validate(WithDark(Default, set));

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue => issue.Code == ThemeIssueCodes.FontFamilyInvalid);
    }

    [Fact]
    public void Motion_durations_outside_the_supported_range_are_errors()
    {
        var set = ThemeFixtures.WithMotion(Default.Dark, new ThemeMotion(-5, 140, 220));
        var result = Validator.Validate(WithDark(Default, set));

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue => issue.Code == ThemeIssueCodes.MotionDurationOutOfRange);
    }

    [Fact]
    public void Fast_motion_slower_than_normal_is_a_warning()
    {
        var set = ThemeFixtures.WithMotion(Default.Dark, new ThemeMotion(500, 140, 220));
        var result = Validator.Validate(WithDark(Default, set));

        Assert.True(result.IsValid, Describe(result.Errors));
        Assert.Contains(result.Warnings, issue => issue.Code == ThemeIssueCodes.MotionDurationOrder);
    }

    [Theory]
    [InlineData("Not A Slug")]
    [InlineData("UPPER")]
    [InlineData("../escape")]
    [InlineData("")]
    [InlineData("trailing-")]
    public void Invalid_descriptor_id_is_an_error(string id)
    {
        var package = WithDescriptor(Default, Default.Descriptor with { Id = id });
        var result = Validator.Validate(package);

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue => issue.Code == ThemeIssueCodes.DescriptorIdInvalid);
    }

    [Fact]
    public void Descriptor_without_any_supported_appearance_is_an_error()
    {
        var package = WithDescriptor(
            Default,
            Default.Descriptor with { SupportsLight = false, SupportsDark = false });
        var result = Validator.Validate(package);

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue => issue.Code == ThemeIssueCodes.DescriptorAppearanceUnsupported);
    }

    [Fact]
    public void Non_semver_version_is_a_warning()
    {
        var package = WithDescriptor(Default, Default.Descriptor with { Version = "latest" });
        var result = Validator.Validate(package);

        Assert.True(result.IsValid, Describe(result.Errors));
        Assert.Contains(result.Warnings, issue => issue.Code == ThemeIssueCodes.DescriptorVersionNonSemver);
    }

    [Fact]
    public void Unsupported_schema_is_an_error()
    {
        var package = Default with { Schema = "newmanga.theme/2" };
        var result = Validator.Validate(package);

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue => issue.Code == ThemeIssueCodes.SchemaUnsupported);
    }

    [Fact]
    public void Reader_forbidden_declaration_makes_the_package_invalid()
    {
        var json = ThemePackageJson.Write(Default).Replace(
            "\"schema\": \"newmanga.theme/1\",",
            "\"schema\": \"newmanga.theme/1\",\n  \"dropShadow\": true,",
            StringComparison.Ordinal);

        var package = ThemePackageJson.Read(json).Package!;
        var result = Validator.Validate(package);

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue => issue.Code == ThemeIssueCodes.ForbiddenDeclaration);
    }

    [Theory]
    [InlineData("Light")]
    [InlineData("Dark")]
    public void Primary_text_below_seven_to_one_is_an_error(string variant)
    {
        var package = variant == "Light"
            ? WithLight(Default, ThemeFixtures.WithColor(Default.Light, NmKeys.Color.Text.Primary, "#777777"))
            : WithDark(Default, ThemeFixtures.WithColor(Default.Dark, NmKeys.Color.Text.Primary, "#666666"));

        var result = Validator.Validate(package);

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue => issue.Code == ThemeIssueCodes.ContrastTextPrimary);
    }

    [Theory]
    [InlineData("Light")]
    [InlineData("Dark")]
    public void Secondary_text_below_four_point_five_to_one_is_an_error(string variant)
    {
        var package = variant == "Light"
            ? WithLight(Default, ThemeFixtures.WithColor(Default.Light, NmKeys.Color.Text.Secondary, "#AAAAAA"))
            : WithDark(Default, ThemeFixtures.WithColor(Default.Dark, NmKeys.Color.Text.Secondary, "#555555"));

        var result = Validator.Validate(package);

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue => issue.Code == ThemeIssueCodes.ContrastTextSecondary);
    }

    [Fact]
    public void Status_hue_below_four_point_five_on_the_panel_is_an_error()
    {
        var set = ThemeFixtures.WithColor(Default.Dark, NmKeys.Color.Status.Failed, "#3A2A26");
        var result = Validator.Validate(WithDark(Default, set));

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue =>
            issue.Code == ThemeIssueCodes.ContrastStatus && issue.Path == "dark.colors.Nm.Color.Status.Failed");
    }

    [Fact]
    public void Edge_surface_status_contrast_is_reported_as_a_warning_not_an_error()
    {
        // The frozen R-09 baseline only guarantees the panel floor, so status hues on raised/canvas
        // surfaces are warnings. Characterization: light has canvas + raised misses, dark only raised.
        var result = Validator.Validate(Default);

        Assert.True(result.IsValid, Describe(result.Errors));
        var edgeWarnings = result.Warnings.Where(issue => issue.Code == ThemeIssueCodes.ContrastStatus).ToArray();
        Assert.Equal(3, edgeWarnings.Length);
        Assert.All(edgeWarnings, issue => Assert.Contains("Bg.", issue.Path!, StringComparison.Ordinal));
        Assert.All(edgeWarnings, issue => Assert.False(issue.IsError));
    }

    [Fact]
    public void Accent_on_color_below_four_point_five_is_an_error()
    {
        var set = ThemeFixtures.WithColor(Default.Light, NmKeys.Color.Accent.On, "#999999");
        var result = Validator.Validate(WithLight(Default, set));

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue => issue.Code == ThemeIssueCodes.ContrastAccentOn);
    }

    [Fact]
    public void Focus_accent_below_three_to_one_is_an_error()
    {
        var set = ThemeFixtures.WithColor(Default.Light, NmKeys.Color.Accent.Base, "#F6F6F6");
        var result = Validator.Validate(WithLight(Default, set));

        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, issue => issue.Code == ThemeIssueCodes.ContrastAccentFocus);
    }

    [Fact]
    public void Threshold_math_is_wcag_2_1()
    {
        Assert.Equal(21.0, ThemeContrast.Ratio("#000000", "#FFFFFF"), precision: 2);
        Assert.Equal(1.0, ThemeContrast.Ratio("#123456", "#123456"), precision: 2);
        Assert.False(ThemeContrast.TryParse("not-a-color", out _));
        Assert.True(ThemeContrast.TryParse("rgba(0,0,0,0.5)", out _));
    }

    private static string Describe(IReadOnlyList<ThemeValidationIssue> issues) =>
        string.Join(" | ", issues.Select(issue => $"{issue.Code}@{issue.Path}: {issue.Message}"));
}
