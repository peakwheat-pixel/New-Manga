using System.Runtime.CompilerServices;

// V11R-A-8: Program.WriteFatal is internal so the CLI-robustness tests can prove it never throws on an
// empty/invalid log path (it must degrade to Console.Error instead of crashing the process).
[assembly: InternalsVisibleTo("NewManga.App.Tests")]
