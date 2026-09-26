"""Line-level verification of the two remaining Contract §7.1 lifecycle claims
at fixed base 7478f72, plus the list_revisions delegation view.

  * service.py:886 recover_running_runs -> persisted RUNNING runs/tasks/steps
    become INTERRUPTED and are saved.
  * service.py:903 retry_failed_targets -> raises PipelineError("TARGET_NOT_FOUND")
    when there is no failed page.
  * service.py:829-884 control_run transition gates (pause/stop/continue/restart/abandon).
"""
import re
import subprocess

BASE = '7478f72fe6f9872cae29f4fa12888b5e1f2380f1'


def show(path):
    return subprocess.run(['git', 'show', f'{BASE}:{path}'], capture_output=True,
                          text=True, encoding='utf-8').stdout


lines = show('src/application/tasks/service.py').splitlines()


def block(a, b, title):
    """Print source lines with a 1-based line-number gutter.

    Lines are rstripped so the emitted log carries no trailing whitespace and
    passes `git diff --check` when committed as evidence.
    """
    print(f'--- {title} ({a}-{b}) ---')
    for i in range(a, min(b, len(lines)) + 1):
        print(f'{i:4}: {lines[i - 1]}'.rstrip())
    print()


block(829, 884, 'control_run')
block(886, 902, 'recover_running_runs')
block(903, 916, 'retry_failed_targets')

print('=== transition gates inside control_run ===')
seg = '\n'.join(lines[828:884])
for pat in ['PENDING', 'RUNNING', 'PAUSED', 'INTERRUPTED', 'completed_with_failures',
            'INVALID_RUN_TRANSITION', 'abandoned_after_interruption', 'restarted',
            'retry_reason', 'source_run_id']:
    print(f'  {pat:32} -> {len(re.findall(re.escape(pat), seg))} hit(s)')
