# DSH r4 dispatch record

HOST=Windows; CLI=dsh 0.1.7-rc.2
working_directory=G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex
command=dsh --profile headless --json "<self-contained, read-only review task>"
session_id=session-1aa0514a-fb63-474e-8911-1cf78821df49
exit=0
stdout_jsonl=verification/M2-RUNNER-SNAPSHOT-DEBT/raw/resume/dsh-r4-events.jsonl
stderr=verification/M2-RUNNER-SNAPSHOT-DEBT/raw/resume/dsh-r4-stderr.log (empty)
final_report=doc/reviews/M2-RUNNER-SNAPSHOT-DEBT-3d532c1f-dsh-r4.md
workspace_registration=verified in C:/Users/49745/.dsh/storages/workspace.json for the exact linked worktree path
web_visibility=unverified; DSH desktop was not restarted or inspected

Review fixed inputs: review_base=2b780120d1eb94f93afadf073790f65899a618e6; reviewed_head=5c2d047804eb4a802c04e53b5e8e5e5459570b24; code_delivery_head=3d532c1f99e49da703d2076bd67d46b710866637; evidence_commit=ce5ff3fc21bcba082b995ea716a983d2fd4c6a89.
DSH decision=approved; no P0/P1; four nonblocking P2 findings and one non-blocking judgement item. Reviewer-side Windows Gate rerun=NOT_RUN; archived producer logs were used. JSONL and report are stored verbatim from the real CLI response; the dispatch harness wrote the JSONL/stderr/exit files.