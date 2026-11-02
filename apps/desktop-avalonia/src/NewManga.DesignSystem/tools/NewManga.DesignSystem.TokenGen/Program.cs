using NewManga.DesignSystem.Tokens;

namespace NewManga.DesignSystem.TokenGen;

/// <summary>
/// CLI for the reproducible token pipeline.
/// <code>
/// dotnet run --project apps/desktop-avalonia/src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen -- --check
/// </code>
/// Exit codes: 0 = success / up to date, 1 = drift or error, 2 = usage error.
/// </summary>
internal static class Program
{
    private const string DesignSystemProjectRelativePath = "apps/desktop-avalonia/src/NewManga.DesignSystem";

    private static int Main(string[] args)
    {
        try
        {
            return Run(args);
        }
        catch (Exception exception)
        {
            Console.Error.WriteLine($"token generation failed: {exception}");
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
                    Console.WriteLine("usage: NewManga.DesignSystem.TokenGen [--check] [--repo-root <path>]");
                    return 0;
                default:
                    Console.Error.WriteLine($"unknown argument '{args[index]}'");
                    return 2;
            }
        }

        var repositoryRoot = explicitRepositoryRoot ?? FindRepositoryRoot()
            ?? throw new InvalidOperationException(
                $"could not locate repository root (looking for '{TokenGenerator.TokensRelativePath}'); pass --repo-root");

        var tokensPath = Path.Combine(repositoryRoot, TokenGenerator.TokensRelativePath.Replace('/', Path.DirectorySeparatorChar));
        var projectDirectory = Path.Combine(repositoryRoot, DesignSystemProjectRelativePath.Replace('/', Path.DirectorySeparatorChar));

        var tokensJson = File.ReadAllText(tokensPath);
        var result = TokenGenerator.Generate(tokensJson);

        Console.WriteLine($"tokens:  {tokensPath}");
        Console.WriteLine($"project: {projectDirectory}");
        Console.WriteLine($"rows:    {result.Rows.Count}");

        if (checkOnly)
        {
            if (!TokenGenerator.IsUpToDate(result, projectDirectory, out var mismatches))
            {
                Console.Error.WriteLine("generated artifacts are stale:");
                foreach (var mismatch in mismatches)
                {
                    Console.Error.WriteLine($"  - {mismatch}");
                }

                return 1;
            }

            Console.WriteLine("up to date: every generated artifact matches the frozen token source byte-for-byte");
            return 0;
        }

        TokenGenerator.Write(result, projectDirectory);
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
                var candidate = Path.Combine(directory.FullName, TokenGenerator.TokensRelativePath.Replace('/', Path.DirectorySeparatorChar));
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
