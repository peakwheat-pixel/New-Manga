# P02PRE-R1H 独立静态 Review（首轮）

- Reviewer：Codex 非作者子代理 `/root/p02_r1h_review_fallback`。
- Owner：Antigravity；Integrator/Adjudicator：Codex `/root`。
- Candidate：`agent/antigravity/P02PRE-R1H`，base=`946938bd0696dfddd01f87d61fe6723c63ecdc86`，HEAD=`256e3ea622cba7a658020ddcf015b18894d88b38`。
- Verdict：`CHANGES_REQUESTED`；P0/P1/P2/P3=`0/1/3/0`。
- 根 Codex 以 Windows PowerShell 7 对相同 7 个冻结输入完成 post-pin：7/7 与 pre-review pins 匹配，详见 `codex-p02pre-r1h-review-input-pins-post-20261012.json`。

## Findings

1. **R1H-001 / P1：非-reparse skip 未核验冻结 status/index。** 分类分支比较路径、HEAD/tree/branch；status exit 0 仅代表查询成功，status 字节未与冻结值比较；index 仅作运行前后稳定性比较，未比冻结 index。冻结后发生且保持稳定的 mode/content 工作区偏差仍可能被 skip。main inventory 先于 scratch 基线核验。违反 AC1/manifest 的冻结 refs/index/status 条件。
2. **R1H-002 / P2：Git stage 1–3 可接受并丢弃。** parser 接受 stage 0–3，后续仅保留 mode；无冲突 stage 的 mode=`120000` 非-reparse leaf 可能进入 skip。应明确保留并核验 stage 0，其他 stage fail-stop。
3. **R1H-003 / P2：非目录、非-reparse、leaf 不足以证明 ordinary file。** 设备或未知对象可能与普通 leaf 传入相同布尔值而被 skip；须以既有 metadata 证明 ordinary file，否则 STOP，不增加目标读取。
4. **R1H-004 / P2：self-check 控制流断言与候选注释不兼容，且没有证明宣称的禁止操作。** 当前 regex 要求赋值后紧邻 `break`，但注释使断言无法匹配；另外没有绑定真实 AST 分支/退出路径，也未覆盖冻结 status/index、非零 stage 和设备/未知对象负例。

## 范围与限制

Reviewer 仅读取获准的 7 个文件，未写文件、运行命令/脚本/parser/test、计算 hash、搜索/枚举目录或访问 `.tmp.driveupload`。未验证 runtime、OS 写入/进程闭包、Gate 或 AC。独立 Review 仅支持上述静态 finding，不支持集成或执行。

DeepSeek Harness 的原始 review dispatch session `88308` 仍为 `DISPATCH_STALLED / NO_REVIEW_RESULT`；它不是另一份 Review，也不改变本结论。