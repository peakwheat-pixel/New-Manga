using System.Runtime.CompilerServices;

// E9-FILE-ROOT-RECOVERY-1 / E9-NEGATIVE-TEST-1: the recovery-root predicate
// (SourceOperationCoordinator.IsRecoverableRoot) is internal so callers cannot widen it by accident;
// the Host test project needs to pin the negative case (a DIRECTORY root must stay rejected).
[assembly: InternalsVisibleTo("NewManga.Host.Tests")]
