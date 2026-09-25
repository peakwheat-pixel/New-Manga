# -*- coding: utf-8 -*-
"""Read-only dump of the pipeline failure diagnostic (AC5 evidence)."""
import json
import sqlite3

P = (r"G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926"
     r"\host-simulation-20260926-rerun1\用户配置隔离\AppData\Local\New Manga\library.db")
con = sqlite3.connect("file:" + P.replace("\\", "/") + "?mode=ro", uri=True)
cur = con.cursor()
out = {}
row = cur.execute(
    "SELECT run_id, command_type, scope_type, status, fatal_error, run_json "
    "FROM pipeline_runs ORDER BY rowid DESC LIMIT 1").fetchone()
run_id, command_type, scope_type, status, fatal_error, run_json = row
run = json.loads(run_json)
step_fail = [s for s in run.get("step_runs", []) if s.get("status") == "failed"]
out["pipeline_run"] = {
    "run_id": run_id, "command_type": command_type, "scope_type": scope_type,
    "status": status, "fatal_error": fatal_error,
    "planned_step_units": run.get("planned_step_units"),
    "terminal_step_units": run.get("terminal_step_units"),
    "provider_binding_snapshot": run.get("provider_binding_snapshot"),
    "settings_snapshot": run.get("settings_snapshot"),
}
out["failed_steps"] = [{
    "step_run_id": s.get("step_run_id"), "step_type": s.get("step_type"),
    "status": s.get("status"), "error_code": s.get("error_code"),
    "error_detail": s.get("error_detail"),
    "lock_snapshot": s.get("lock_snapshot"),
} for s in step_fail]
task = cur.execute(
    "SELECT task_id, status, error_code, error_detail FROM pipeline_tasks "
    "WHERE pipeline_run_id = ?", (run_id,)).fetchone()
out["pipeline_task"] = {
    "task_id": task[0], "status": task[1], "error_code": task[2], "error_detail": task[3],
}
con.close()
print(json.dumps(out, ensure_ascii=False, indent=1))
