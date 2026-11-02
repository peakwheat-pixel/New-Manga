namespace NewManga.ThemeEngine.ThemeGen;

/// <summary>
/// CLI for the reproducible theme pipeline.
/// <code>
/// dotnet run --project apps/desktop-avalonia/src/NewManga.ThemeEngine/tools/NewManga.ThemeEngine.ThemeGen -- --check
/// </code>
/// Exit codes: 0 = success / up to date, 1 = drift or error, 2 = usage error.
/// </summary>
internal static class Program
{
    private const string ThemeEngineProjectRelativePath = "apps/desktop-avalonia/src/NewManga.ThemeEngine";

    private static int Main(string[] args)
    {
        try
        {
            return Run(args);
        }
        catch (Exception exception)
        {
            Console.Error.WriteLine($"theme generation failed: {exception}");
            return 1;
        }
    }

    private static int Run(string[] args)
    {
        var checkOnly = false;
        string? explicitRepositoryRoot = null;

        for (var index = 0; index < args.Length; index++)
        {
            switch (args[index])
            {
                case "--check":
                    checkOnly = true;
                    break;
                case "--repo-root" when index + 1 < args.Length:
                    explicitRepositoryRoot = args[++index];
                    break;
                case "--help" or "-h":
                    Console.WriteLine("usage: NewManga.ThemeEngine.ThemeGen [--check] [--repo-root <path>]");
                    return 0;
                default:
                    Console.Error.WriteLine($"unknown argument '{args[index]}'");
                    return 2;
            }
        }

        var repositoryRoot = explicitRepositoryRoot ?? FindRepositoryRoot()
            ?? throw new InvalidOperationException(
                $"could not locate repository root (looking for '{BuiltInThemeGenerator.TokensRelativePath}'); pass --repo-root");

        var tokensPath = Path.Combine(
            repositoryRoot,
            BuiltInThemeGenerator.TokensRelativePath.Replace('/', Path.DirectorySeparatorChar));
        var projectDirectory = Path.Combine(
            repositoryRoot,
            ThemeEngineProjectRelativePath.Replace('/', Path.DirectorySeparatorChar));

        var tokensJson = File.ReadAllText(tokensPath);
        var result = BuiltInThemeGenerator.Generate(tokensJson);

        Console.WriteLine($"tokens:  {tokensPath}");
        Console.WriteLine($"project: {projectDirectory}");
        Console.WriteLine($"theme:   {result.Package.Descriptor.Id} {result.Package.Descriptor.Version} " +
                          $"(light {result.Package.Light.Colors.Count} colors, dark {result.Package.Dark.Colors.Count} colors)");
        foreach (var warning in result.Warnings)
        {
            Console.WriteLine($"  derived: {warning}");
        }

        if (checkOnly)
        {
            if (!BuiltInThemeGenerator.IsUpToDate(result, projectDirectory, out var mismatches))
            {
                Console.Error.WriteLine("generated theme artifacts are stale:");
                foreach (var mismatch in mismatches)
                {
                    Console.Error.WriteLine($"  - {mismatch}");
                }

                return 1;
            }

            Console.WriteLine("up to date: generated theme artifacts match the frozen token source byte-for-byte");
            return 0;
        }

        BuiltInThemeGenerator.Write(result, projectDirectory);
        foreach (var file in result.Files)
        {
            Console.WriteLine($"wrote {file.RelativePath} ({file.Content.Length} chars)");
        }

        return 0;
    }

    private static string? FindRepositoryRoot()
    {
        foreach (var start in new[] { Directory.GetCurrentDirectory(), AppContext.BaseDirectory })
        {
            var directory = new DirectoryInfo(start);
            while (directory is not null)
            {
                var candidate = Path.Combine(
                    directory.FullName,
                    BuiltInThemeGenerator.TokensRelativePath.Replace('/', Path.DirectorySeparatorChar));
                if (File.Exists(candidate))
                {
                    return directory.FullName;
                }

                directory = directory.Parent;
            }
        }

        return null;
    }
}
