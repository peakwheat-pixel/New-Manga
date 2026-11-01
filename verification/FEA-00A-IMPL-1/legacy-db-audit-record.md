# AC7②：旧库只读核验记录

脚本：audit_legacy_db_readonly.py。通过 SQLite URI mode=ro 打开指定数据库，并执行 PRAGMA query_only=ON；核验 regions.text_json 与 current_revision_id 指向 revision 的 snapshot text 一致性、region_revisions 行数，以及 step_result_candidates 可读性。脚本不创建、恢复、复制或修改数据库/备份。

执行结果：**PASS（一次性临时 Core-assembly fixture）**。输入是测试创建的临时数据库，不是用户旧库。JSON 记录为 legacy-db-audit-result.json：open_mode=read-only、query_only=1、1 个 region、1 个可解析 current revision、1 条 region revision、0 条 candidate，consistent=true。测试过程中的临时绝对路径记录在 JSON 文件内；该文件来自一次性临时 fixture。

没有收到或扫描用户既有库；因此该记录验证只读核验脚本流程，不声称核验任何用户旧库。未创建/恢复备份，也未触碰用户数据。
