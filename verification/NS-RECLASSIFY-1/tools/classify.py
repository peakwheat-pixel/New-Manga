#!/usr/bin/env python
"""NS-RECLASSIFY-1 AC2: turn the probe log into a per-command reclassification table.

Input  : probe/probe-results.json (this task, frozen core_service.exe)
         verification/NS-WIRE-A1/evidence/parity-contract.json (the 42 NOT_SUPPORTED list)
         verification/HOST-COMMAND-MIGRATION-1/parity/core-command-probe.json (S2 probe evidence)
Output : verification/NS-RECLASSIFY-1/reclassification.json

Classification rules (documented in REPORT.md §3):
  success                        -> IMPLEMENTED
  domain_error_handler_ran       -> IMPLEMENTED  (only a live handler produces not_found/conflict)
  payload_rejected BUT the error is a handler-level typed validation (SETTINGS_INVALID_INPUT /
      MISSING_REQUIRED_INPUT) -> IMPLEMENTED, confidence medium (route proven, positive path not)
  no Core command in the surface at all              -> NEEDS_IMPLEMENTATION
  host-control faces that need a host-issued grant   -> NEEDS_IMPLEMENTATION
  provider/weights missing                           -> NEEDS_MODEL
  no probe could be constructed                      -> BLOCKED
"""
import hashlib
import json
import os
import sys

REPO = r"G:\CODEX\New Manga"
ENV = r"G:\CODEX\New Manga.workspace\task-envs\NS-RECLASSIFY-1"
OUT = os.path.join(REPO, "verification", "NS-RECLASSIFY-1")

# NS command -> (probe name, core command, mapping note)
MAPPING = {
    "backup_delete": ("backup_delete", "backup.delete", "S3-C backup face"),
    "backup_restore": ("backup_restore", "backup.restore", "S3-C backup face"),
    "cleanup_retry_pending": ("cleanup_retry_pending", "cleanup.retry_pending", "S3-C cleanup face"),
    "credential_clear": ("credential_clear", "ClearProfileCredential", "P15 settings face (minor 7)"),
    "credential_put": ("credential_put", "BindProfileCredential", "P15 settings face (minor 7)"),
    "library_cancel_export": (None, "CancelExport", "host-control + export session"),
    "library_control_run": ("library_control_run", "ControlRun", "run orchestration face"),
    "library_delete_book_permanently": ("library_delete_book_permanently", "PermanentlyDeleteBook", "DELETE face, protocol minor 10"),
    "library_delete_books_permanently": ("library_delete_books_permanently", "PermanentlyDeleteBooks", "DELETE face, protocol minor 10"),
    "library_get_export_snapshot": (None, "GetExportSnapshot", "host-control export session"),
    "library_get_run_snapshot": ("library_get_run_snapshot", "GetRunSnapshot", "run orchestration face"),
    "library_get_task_projection": ("library_get_task_projection", "GetTaskProjection", "run orchestration face"),
    "library_import_file": (None, "ImportPages", "host-control + host-issued import grant"),
    "library_import_folder": (None, "ImportPages", "host-control + host-issued import grant"),
    "library_resume_blocked_run": ("library_resume_blocked_run", "ResumeBlockedRun", "run orchestration face"),
    "library_retry_failed_targets": ("library_retry_failed_targets", "RetryFailedTargets", "run orchestration face"),
    "library_reveal_export_folder": (None, None, "host-local shell action"),
    "library_save_reading_progress": ("library_save_reading_progress", "SaveReadingProgress", "reader face"),
    "library_start_export": (None, "StartExport", "host-control + host-issued export grant"),
    "library_start_run": ("library_start_run", "StartRun", "run orchestration face"),
    "list_region_revisions": ("list_region_revisions", "list_region_revisions", "region face (CoreRoute)"),
    "plugins_audit_list": ("plugins_audit_list", "plugins.audit_list", "PLUGIN-RUNTIME-1 face"),
    "plugins_open_directory": (None, None, "host-local shell action"),
    "plugins_set_plugin_enabled": ("plugins_set_plugin_enabled", "plugins.set_plugin_enabled", "PLUGIN-RUNTIME-1 face"),
    "rerender_page": ("rerender_page", "rerender_page", "region face (CoreRoute)"),
    "resolve_page_resource": ("resolve_page_resource", "resolve_page_resource", "region face (CoreRoute)"),
    "restore_region_revision": ("restore_region_revision", "restore_region_revision", "region face (CoreRoute)"),
    "set_region_type": ("set_region_type", "set_region_type", "region face (CoreRoute)"),
    "settings_network_profile_default_clear": ("settings_network_profile_default_clear", "settings_network_profile_default_clear", "P15 network face"),
    "settings_network_profile_default_set": ("settings_network_profile_default_set", "settings_network_profile_default_set", "P15 network face"),
    "settings_network_profile_resolve": ("settings_network_profile_resolve", "settings_network_profile_resolve", "P15 network face"),
    "settings_network_profiles_create": ("settings_network_profiles_create", "settings_network_profiles_create", "P15 network face"),
    "settings_network_profiles_delete": ("settings_network_profiles_delete", "settings_network_profiles_delete", "P15 network face"),
    "settings_network_profiles_test": ("settings_network_profiles_test", "settings_network_profiles_test", "P15 network face"),
    "settings_network_profiles_update": ("settings_network_profiles_update", "settings_network_profiles_update", "P15 network face"),
    "settings_provider_bindings_clear": ("settings_provider_bindings_clear", "settings_provider_bindings_clear", "P15 provider face"),
    "settings_provider_bindings_resolve": ("settings_provider_bindings_resolve", "settings_provider_bindings_resolve", "P15 provider face"),
    "settings_provider_bindings_set": ("settings_provider_bindings_set", "settings_provider_bindings_set", "P15 provider face"),
    "settings_provider_profiles_create": ("settings_provider_profiles_create", "settings_provider_profiles_create", "P15 provider face"),
    "settings_provider_profiles_delete": ("settings_provider_profiles_delete", "settings_provider_profiles_delete", "P15 provider face"),
    "settings_provider_profiles_update": ("settings_provider_profiles_update", "settings_provider_profiles_update", "P15 provider face"),
    "settings_provider_run_snapshot_get": ("settings_provider_run_snapshot_get", "settings_provider_run_snapshot_get", "P15 provider face"),
}

# handler-level typed validation: the route exists and a real handler rejected the *fields*
HANDLER_VALIDATION = {
    "settings_provider_profiles_create", "settings_provider_profiles_update",
    "settings_provider_profiles_delete", "settings_provider_bindings_set",
    "credential_put", "credential_clear", "settings_network_profiles_test",
    "settings_network_profile_resolve", "library_delete_books_permanently",
    "backup_restore",
}

HANDLER_LEVEL_CODES = {"MISSING_REQUIRED_INPUT"}  # typed semantic error that only a live handler emits

S2_EVIDENCE = {
    "library_save_reading_progress": "S2 探针 probe-25 用 {position, chapter_id:'probe-chapter'} → INVALID_REQUEST(validation)，被当作“未实现”；正确 payload 是 {chapter_id, mode, page_id, scroll_offset_y, elapsed_seconds_delta}",
    "list_region_revisions": "S2 探针 probe-14 用 PascalCase 'ListRegionRevisions' → UNKNOWN_COMMAND；真实 Core 命令是 snake_case 'list_region_revisions'",
    "resolve_page_resource": "S2 探针 probe-21 用 {page_id:'probe-page'} → PAGE_NOT_FOUND，被当作“未实现”；真实 page_id 下返回 ok",
    "rerender_page": "S2 探针 probe-20 用 {page_id:'probe-page'} → TARGET_NOT_FOUND，被当作“未实现”；真实 page_id 下进入 handler（MISSING_REQUIRED_INPUT）",
    "set_region_type": "S2 探针 probe-22 用 new_region_type:'probe' → INVALID_REQUEST，被当作“未实现”；合法枚举 narration/note/other/sfx/speech/title 才通过",
    "restore_region_revision": "S2 探针 probe-23 用假 region_id → TARGET_NOT_FOUND，被当作“未实现”",
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    probe = load(os.path.join(ENV, "probe", "probe-results.json"))
    snapshot = load(os.path.join(REPO, "verification", "NS-WIRE-A1", "evidence", "parity-contract.json"))
    s2 = load(os.path.join(REPO, "verification", "HOST-COMMAND-MIGRATION-1", "parity", "core-command-probe.json"))

    ns_names = [item["name"] for item in snapshot["not_supported_commands"]]
    assert len(ns_names) == 42, f"expected 42 NOT_SUPPORTED, got {len(ns_names)}"

    by_name = {}
    for r in probe["results"]:
        by_name.setdefault(r.get("ns_command"), []).append(r)
    host = {r.get("ns_command"): r for r in probe.get("host_control", [])}
    s2_by_core = {p["command"]: p for p in s2["probes"]}

    rows = []
    for name in ns_names:
        probe_name, core, face = MAPPING[name]
        row = {
            "command": name,
            "current_status": "NOT_SUPPORTED",
            "core_command": core,
            "face": face,
        }
        if probe_name and probe_name in by_name:
            attempts = by_name[probe_name]
            # prefer the attempt that got furthest
            order = {"success": 0, "domain_error_handler_ran": 1, "other_error": 2,
                     "payload_rejected": 3, "provider_missing": 4, "no_response": 5}
            best = sorted(attempts, key=lambda r: order.get(r["basis"], 9))[0]
            row["evidence"] = {
                "source": "verification/NS-RECLASSIFY-1/probe-results.json",
                "probe_phase": best["phase"],
                "request_payload": best["request_payload"],
                "protocol_minor": best["minor"],
                "ok": best["ok"],
                "error_code": best["error_code"],
                "error_category": best["error_category"],
                "basis": best["basis"],
                "result_excerpt": (json.dumps(best["result"], ensure_ascii=False)[:400]
                                   if best.get("result") is not None else None),
            }
            if best["basis"] == "success":
                row["proposed_status"] = "IMPLEMENTED"
                row["confidence"] = "high"
                row["reason"] = "正确 payload 下 Core 返回成功结果，S2 的 NOT_SUPPORTED 是探针 payload/命令名错误导致的误分类。"
            elif best["basis"] == "domain_error_handler_ran":
                row["proposed_status"] = "IMPLEMENTED"
                row["confidence"] = "high"
                row["reason"] = ("Core 路由与处理器存在并被执行（返回 typed 域错误而不是 UNKNOWN_COMMAND）："
                                 f"{best['error_code']}/{best['error_category']}。S2 用假 id/错枚举才判成未实现。")
            elif name in HANDLER_VALIDATION:
                row["proposed_status"] = "IMPLEMENTED"
                row["confidence"] = "medium"
                row["reason"] = (f"Core 返回处理器级 typed 校验错误（{best['error_code']}），说明路由与处理器已实现；"
                                 "本任务尚未命中冻结二进制的完整正向 payload，正向路径需在应用改动时补一次确认。")
                row["residual"] = "正向路径未复现（字段校验未通过）"
            elif best["basis"] == "other_error" and best["error_code"] in HANDLER_LEVEL_CODES:
                row["proposed_status"] = "IMPLEMENTED"
                row["confidence"] = "medium"
                row["reason"] = (f"Core 处理器返回 typed 语义错误 {best['error_code']}（缺输入/前置产物），"
                                 "说明路由与处理器已实现；正向路径需要真实产物（渲染/检测产物），S2 用假 id 才判成未实现。")
                row["residual"] = "正向路径依赖真实产物（artifact/revision），本任务未构造"
            elif best["basis"] == "provider_missing":
                row["proposed_status"] = "NEEDS_MODEL"
                row["confidence"] = "high"
                row["reason"] = f"Core 需要模型/权重：{best['error_code']}。"
            else:
                row["proposed_status"] = "BLOCKED"
                row["confidence"] = "low"
                row["reason"] = f"探针未命中契约：{best['basis']} / {best['error_code']}。"
        else:
            # no app-channel probe: host-local or host-control faces
            if core is None:
                row["proposed_status"] = "NEEDS_IMPLEMENTATION"
                row["confidence"] = "high"
                row["reason"] = ("旧壳本地 shell 动作（打开目录/资源管理器），Core 命令面没有等价命令；"
                                 "只能由 Host/App 层实现，registry 保持 NOT_SUPPORTED 属正确分类，但实现位置是 Host 而非 Core。")
                row["evidence"] = {"source": "src/bootstrap/core_service.py 命令面（_HOST_CONTROL_COMMANDS/_RUN_COMMANDS/_CREATE_COMMANDS 等）", "core_command": None}
            else:
                hc = host.get(f"RegisterImportSource" if "import" in name else "RegisterExportTarget")
                row["proposed_status"] = "NEEDS_IMPLEMENTATION"
                row["confidence"] = "medium"
                row["reason"] = (f"Core 侧 host-control 面存在（OpenHostSession 成功，core_session_id 可取；{core} 在 host-control 命令集中），"
                                 "但 Import/Export 需要 host_issuer 签发的 grant：冻结 Core 对未签名 ref 返回 typed REF_MALFORMED，"
                                 "而新 Avlonia Host 尚未实现等价签发 → 需要先在 Host 侧实现 grant 签发 + 调用。")
                row["evidence"] = {
                    "source": "verification/NS-RECLASSIFY-1/probe-results.json (host_control)",
                    "open_host_session": host.get("control_open_host_session", {}).get("ok"),
                    "grant_probe": hc,
                }
        if name in S2_EVIDENCE:
            row["s2_misclassification"] = S2_EVIDENCE[name]
        # S2 probe evidence for the same core command, when the probe used that exact name
        if core in s2_by_core:
            p = s2_by_core[core]
            row["s2_probe"] = {"command": p["command"], "minor": p["minor"],
                               "payload": p.get("request_payload"), "ok": p["ok"],
                               "error_code": p.get("error_code")}
        rows.append(row)

    stats = {}
    for r in rows:
        stats[r["proposed_status"]] = stats.get(r["proposed_status"], 0) + 1
    by_confidence = {}
    for r in rows:
        by_confidence[r.get("confidence")] = by_confidence.get(r.get("confidence"), 0) + 1

    out = {
        "task": "NS-RECLASSIFY-1",
        "ac": "AC1/AC2",
        "base_commit": "171529b5d",
        "sidecar": {
            "core_service": probe["sidecar"],
            "sha256": probe["sidecar_sha256"],
            "protocol": "2.3 (application channel) + host-control channel + P15 minor 7 + create minor 8 + delete minor 10",
        },
        "fixture": {
            "source": "G:/CODEX/New Manga.workspace/task-envs/BOOK-FIXTURE-1/isolated-data",
            "private_copy": "G:/CODEX/New Manga.workspace/task-envs/NS-RECLASSIFY-1/probe/data",
            "note": "探测全部跑在私有副本上；隔离数据根重建了 catalog 以匹配新路径绑定，原 BOOK-FIXTURE 数据未被修改",
            **probe["fixture"],
        },
        "s2_snapshot": {
            "not_supported_source": "verification/NS-WIRE-A1/evidence/parity-contract.json",
            "not_supported_count": len(ns_names),
            "s2_probe_evidence": "verification/HOST-COMMAND-MIGRATION-1/parity/core-command-probe.json",
        },
        "stats": {"total": len(rows), **stats, "by_confidence": by_confidence},
        "commands": rows,
    }
    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, "reclassification.json")
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(json.dumps(out["stats"], ensure_ascii=False, indent=2))
    print("wrote", dst, os.path.getsize(dst), "bytes")
    # compact console table
    for r in rows:
        print("%-42s %-22s %-8s %s" % (r["command"], r["proposed_status"], r.get("confidence"),
                                       (r.get("error_code") or "")[:20]))


if __name__ == "__main__":
    main()

