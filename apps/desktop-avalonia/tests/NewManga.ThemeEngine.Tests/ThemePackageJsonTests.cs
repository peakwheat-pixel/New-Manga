using NewManga.ThemeEngine;

namespace NewManga.ThemeEngine.Tests;

/// <summary>
/// Schema <c>newmanga.theme/1</c> read/write contract: deterministic round-trip, tolerated unknown
/// fields (warnings), forbidden visual-effect declarations (errors), schema versioning and structural
/// failure modes (never a half-parsed package).
/// </summary>
public sealed class ThemePackageJsonTests
{
    private static ThemePackage Default => ThemeFixtures.DefaultPackage;

    [Fact]
    public void Default_theme_round_trips_structurally()
    {
        var json = ThemePackageJson.Write(Default);
        var result = ThemePackageJson.Read(json);

        Assert.True(result.Success);
        Assert.Equal(Default, result.Package);
    }

    [Fact]
    public void Write_is_deterministic_and_lf_terminated()
    {
        var first = ThemePackageJson.Write(Default);
        var second = ThemePackageJson.Write(Default);

        Assert.Equal(first, second);
        Assert.DoesNotContain("\r", first, StringComparison.Ordinal);
        Assert.EndsWith("\n", first, StringComparison.Ordinal);
        Assert.Contains("\"schema\": \"newmanga.theme/1\"", first, StringComparison.Ordinal);
    }

    [Fact]
    public void Written_package_declares_no_layout_navigation_or_density()
    {
        var json = ThemePackageJson.Write(Default);

        // Contract §4 / DESIGN_SYSTEM §1 decoupling: layout is a separate, independently persisted
        // concern and must never leak into a theme package.
        Assert.DoesNotContain("\"layout\"", json, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("\"navigation\"", json, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("\"density\"", json, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("\"shelf\"", json, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("\"reader\"", json, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("\"workbench\"", json, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void Read_tolerates_unknown_fields_with_warnings()
    {
        var json = ThemePackageJson.Write(Default).Replace(
            "\"schema\": \"newmanga.theme/1\",",
            "\"schema\": \"newmanga.theme/1\",\n  \"futureField\": 42,\n  \"nested\": { \"anything\": true },",
            StringComparison.Ordinal);

        var result = ThemePackageJson.Read(json);

        Assert.True(result.Success);
        Assert.Contains(result.Issues, issue =>
            issue.Code == ThemeIssueCodes.UnknownField && issue.Severity == "warning");
        Assert.Contains(result.Issues, issue => issue.Path == "futureField");
        // Reader diagnostics are attached to the package so the validator can fold them in.
        Assert.Contains(result.Package!.Metadata.LoadWarnings, issue => issue.Code == ThemeIssueCodes.UnknownField);
    }

    [Fact]
    public void Read_reports_forbidden_visual_effect_fields_as_errors()
    {
        var json = ThemePackageJson.Write(Default).Replace(
            "\"schema\": \"newmanga.theme/1\",",
            "\"schema\": \"newmanga.theme/1\",\n  \"boxShadow\": \"0 2px 8px rgba(0,0,0,.4)\",\n  \"backdropBlur\": 8,",
            StringComparison.Ordinal);

        var result = ThemePackageJson.Read(json);

        Assert.True(result.Success);
        Assert.Contains(result.Issues, issue =>
            issue.Code == ThemeIssueCodes.ForbiddenDeclaration && issue.IsError);
        Assert.Contains(result.Issues, issue => issue.Path == "boxShadow");
        Assert.Contains(result.Issues, issue => issue.Path == "backdropBlur");
    }

    [Fact]
    public void Read_rejects_an_unsupported_schema_generation()
    {
        var json = ThemePackageJson.Write(Default).Replace(
            "newmanga.theme/1", "newmanga.theme/2", StringComparison.Ordinal);

        var result = ThemePackageJson.Read(json);

        Assert.True(result.Success);
        Assert.Contains(result.Issues, issue =>
            issue.Code == ThemeIssueCodes.SchemaUnsupported && issue.IsError);
    }

    [Fact]
    public void Read_rejects_malformed_json_without_throwing()
    {
        var result = ThemePackageJson.Read("{ not json");

        Assert.False(result.Success);
        Assert.Contains(result.Issues, issue => issue.Code == ThemeIssueCodes.JsonInvalid && issue.IsError);
    }

    [Fact]
    public void Read_rejects_a_missing_descriptor_section()
    {
        var json = ThemePackageJson.Write(Default).Replace(
            "\"descriptor\": {", "\"descriptorRenamed\": {", StringComparison.Ordinal);

        var result = ThemePackageJson.Read(json);

        Assert.False(result.Success);
        Assert.Contains(result.Issues, issue => issue.Code == ThemeIssueCodes.FieldMissing && issue.IsError);
    }

    [Fact]
    public void Read_rejects_a_missing_required_descriptor_field()
    {
        var json = ThemePackageJson.Write(Default).Replace(
            "\"id\": \"newmanga-default\",", "\"idAlias\": \"newmanga-default\",", StringComparison.Ordinal);

        var result = ThemePackageJson.Read(json);

        Assert.False(result.Success);
        Assert.Contains(result.Issues, issue =>
            issue.Code == ThemeIssueCodes.FieldMissing && issue.Path == "descriptor.id");
    }

    [Fact]
    public void Read_reports_duplicate_fields_as_warnings_and_keeps_the_last_value()
    {
        var json = ThemePackageJson.Write(Default).Replace(
            "\"id\": \"newmanga-default\",",
            "\"id\": \"newmanga-default\",\n    \"id\": \"second-id\",",
            StringComparison.Ordinal);

        var result = ThemePackageJson.Read(json);

        Assert.True(result.Success);
        Assert.Contains(result.Issues, issue => issue.Code == ThemeIssueCodes.DuplicateField);
        Assert.Equal("second-id", result.Package!.Descriptor.Id);
    }

    [Fact]
    public void Read_reports_an_unknown_enum_value_and_falls_back()
    {
        var json = ThemePackageJson.Write(Default).Replace(
            "\"material\": \"solid\"", "\"material\": \"mica\"", StringComparison.Ordinal);

        var result = ThemePackageJson.Read(json);

        Assert.True(result.Success);
        Assert.Contains(result.Issues, issue => issue.Code == ThemeIssueCodes.EnumInvalid && issue.IsError);
        Assert.Equal(ThemeMaterial.Solid, result.Package!.Light.Material);
    }

    [Fact]
    public void Read_preserves_metadata_extra_pairs()
    {
        var package = Default with
        {
            Metadata = Default.Metadata with
            {
                Extra = new Dictionary<string, string>(StringComparer.Ordinal)
                {
                    ["studioVersion"] = "1",
                    ["note"] = "hand edited",
                },
            },
        };

        var roundTripped = ThemePackageJson.Read(ThemePackageJson.Write(package));

        Assert.Equal(package.Metadata.Extra.Count, roundTripped.Package!.Metadata.Extra.Count);
        Assert.Equal("hand edited", roundTripped.Package.Metadata.Extra["note"]);
    }

    [Fact]
    public void ReadOrThrow_throws_with_structured_issues_for_unusable_documents()
    {
        var exception = Assert.Throws<ThemePackageException>(() => ThemePackageJson.ReadOrThrow("{}"));

        Assert.NotEmpty(exception.Issues);
        Assert.Contains(exception.Issues, issue => issue.IsError);
    }

    [Fact]
    public void Read_attaches_reader_warnings_to_the_metadata()
    {
        var json = ThemePackageJson.Write(Default).Replace(
            "\"schema\": \"newmanga.theme/1\",",
            "\"schema\": \"newmanga.theme/1\",\n  \"ignoredExtra\": \"x\",",
            StringComparison.Ordinal);

        var package = ThemePackageJson.Read(json).Package!;

        Assert.Single(package.Metadata.LoadWarnings);
        Assert.Equal("ignoredExtra", package.Metadata.LoadWarnings[0].Path);
    }
}
