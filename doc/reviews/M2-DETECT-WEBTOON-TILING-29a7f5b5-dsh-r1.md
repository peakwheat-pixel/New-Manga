dsh: reasoning:
让我开始这个 Review 任务。首先我需要读取相关文件。

工作目录是 G:\CODEX\New Manga，但 worktree 在 G:/CODEX/New Manga.worktrees/M2-DETECT-WEBTOON-TILING-zcode。沙箱是 workspace-write，工作区是 G:\CODEX\New Manga，所以可能只能读工作区内的文件。让我先尝试读取。

需要读：
1. Task 文档 doc/tasks/M2-DETECT-WEBTOON-TILING.md
2. Handoff doc/handoffs/M2-DETECT-WEBTOON-TILING-29a7f5b5.md
3. diff G:/CODEX/New Manga.task-envs/M2-DETECT-WEBTOON-TILING/review-input.diff
4. verification/M2-DETECT-WEBTOON-DIAG/{diagnosis.md,probe-results.json}
5. worktree 的源码

注意：沙箱可能限制到 workspace-write 的 G:\CODEX\New Manga。G:/CODEX/New Manga.worktrees/... 和 G:/CODEX/New Manga.task-envs/... 在工作区之外。但读取通常是可以的（读不受 workspace 限制？file policy 说可以修改工作区内的文件；读取可能受限）。让我试试。

先并行读取几个文件。让我用 pwsh 检查文件是否存在，或者直接用 read。

先创建 goal? 用户要求一个 Review，这是一个单轮任务，比较长但不至于需要 goal。用户没有说 "goal"。我认为这是单轮交付，不需要 create_goal。不过它是长任务…… 规则说 long-running objective across automatic continuation rounds。这个 Review 应该在单轮内完成。不创建 goal。

开始读取。先并行读 task、handoff、diff。

diff 可能很大。先看大小。

让我先执行几个读取。使用 read 工具。路径可能带空格，read 工具应该没问题。

先并行：read task、read handoff、glob worktree 文件。

实际上先做 pwsh 检查文件存在性和大小更有效率，但 read 更直接。我先并行 read 三个文档 + 列 diff 大小。

由于 diff 可能非常大（也许几千行），我先用 pwsh 看大小。

注意沙箱：workspace-write，Command 运行在 PowerShell。读 G:\CODEX 之外应该可以。

开始。
dsh: reasoning:
pwsh 因沙箱权限失败。我用 read/glob 工具代替。

handoff 在 worktree 里？或者文件名不同。先 glob 找。
dsh: reasoning:
接下来读 handoff（在 worktree）、diff（很大？）。先读 handoff，然后 diff。

diff 路径 G:/CODEX/New Manga.task-envs/... read 工具能否读？试试。同时读 worktree 里的 detection_manga.py。

先读 handoff 的全文。diff 可能几千行，我先读它的前 200 行看看结构。其实我需要完整 diff。让我用 read 分段。

先并行：read handoff，read diff（limit 2000）。
dsh: reasoning:
diff 共 2350 行。继续读。重点在 detection_manga.py 实现部分和测试、qualification。

继续读 401-1200。
dsh: reasoning:
继续读 1101-1900。
dsh: reasoning:
继续读 1801-2350（含 JSON 剩余部分，多为 confidences 数组）。我可能可以跳过大部分 confidences，但要检查 K19/BJ02/690 对照段。让我读 1801-2350。

同时开始读取 worktree 里的实际源码 detection_manga.py 关键段（完整文件），以便核对。也需要 DIAG probe-results.json 的 K01 tile_experiment 数据（核对 70 块/尾块 309/NMS 语义）。

另外需要检查 fork 前的原函数是否真的未改动。我可以对比 diff：diff 中 `_detect_text_boxes` 只有 docstring 改动（+4/-2 行的 docstring），函数体未动。这从 diff 可以直接看到。但要核实 "函数本体逐字节未动" 的说法：diff 显示 `-    """Run one page through the pinned model; return (text_boxes, n_bubble).` 被替换为 4 行 docstring，其余是 context 行。这算 docstring 改动，Owner 承认了（"仅 docstring 措辞更新"）。所以"函数本体逐字节未动"需精确表述为 docstring 变更但函数体未变。这是一个可能的小 finding：Owner 声称"函数本体未动"（Task/handoff 说"函数本体逐字节未动"），实际 docstring 有改动（+4/-2）。虽然主体行为不变，但"逐字节"表述不严谨。严格来说 docstring 不是函数体，函数体指 code body。嗯，"函数本体"可以理解为函数实现（不含 docstring）。但 handoff 里 review 指引说 "`_detect_text_boxes` 函数本体应零 diff（仅 docstring 措辞更新）"——他们自己承认 docstring 更新。所以这算诚实。可以列为 P4/说明。

关键点：普通页零行为变化 —— `_detect_text_boxes` 函数体零 diff 意味着普通页调用同一函数，输入相同输出相同。这是强论证。此外 detect() 里新增 `_tiling_config()` 调用在 engine 之后、`_frame_pixels` 之后。等等——原实现顺序是什么？让我看 diff 的上下文：

```
         model, processor = self._engine_or_raise()
         rgb = self._frame_pixels(request)
         width, height = float(rgb.shape[1]), float(rgb.shape[0])
-        boxes, n_bubble = _detect_text_boxes(
-            model, processor, rgb, width, height
-        )
+        tiling_config = _tiling_config()
+        if _tiling_triggered(...):
```

所以 `_tiling_config()` 在 engine 校验之后调用——如果 env 非法，普通页也会 ValueError 失败（即使页面不触发 tiling）。这是 fail-fast 的取舍：env 非法时所有页面都失败，包括普通页。这是"零行为变化"主张的一个边界：如果部署环境设置了非法 env（例如 operator 设置了错的值），普通页此前能工作，现在会抛 ValueError。但这是有意 fail-fast。需注意：`_tiling_config()` 未被 try/except 包裹成 typed error，ValueError 是未捕获异常，会冒泡到 detect() 调用者的上层。生产 detect 一般应返回 typed ProviderError 或抛出 typed 异常。ValueError 不是 typed provider error（如 ProviderError/ProviderNotConfigured）。这可能是 P2 级 finding：env 解析失败抛裸 ValueError 而非 typed provider error，在 handler 层可能变成未处理 500 / step=failed 的 catch-all，取决于上层。需要核对该模块的错误类型体系与调用方（handler/step 层）如何处理非 typed 异常。任务书要求"fail-closed 不放宽（tiling 内部失败 typed；普通页零变化）"。"tiling 内部失败 typed" —— env 解析失败发生在 tiling 判定之前且是裸 ValueError 未 typed。这可能违反 AC 要求。这是个重要 finding，让我核实 detect() 是否在别处捕获 Exception 转 typed。

先读完整 detection_manga.py 源码，尤其 detect() 与模块 docstring、错误类型、engine 校验。

另外要检查：
- `_tiling_config()` 读取时机：在 detect() 内，每次调用都读 env；如果在 engine 校验后，那么缺权重时长条页仍得 PROVIDER_NOT_CONFIGURED（测试覆盖）。OK。
- `_frame_pixels` 在 engine 之后，tiling_config 在 `_frame_pixels` 之后。实际上 diff 显示 `rgb = self._frame_pixels(request)` 保持，`tiling_config = _tiling_config()` 在 width/height 之后。所以非法 env + 坏的 image_bytes → 先 image decode 错误（typed）。顺序合理。
- 关键：`_tiling_config()` 抛 ValueError 未 typed，且 render 是否 catch？让我看 detect 全文和 handler。

还有几个技术审查点：

1. **`_tiling_tiles` 的精确步进**：`origins(total)`: found=[0.0]; while found[-1] + tile_size < total: append(found[-1]+step)。对 height=62133, tile=1024, step=896: 最后一个 origin 是满足 y+1024 < 62133 的最大值。y=61824 时 61824+1024=62848 > 62133，所以循环在 y=60928 时 60928+1024=61952 < 62133 → append 61824；然后 61824+1024=62848 not < 62133 → 停止。origins 数 = 70。最后一个 tile (0, 61824, 690, 62133) → crop_h=309。与 DIAG 一致。

但注意这里是 width=690 < tile=1024：`origins(690)`: found=[0]; 0+1024 < 690? No → [0]。所以 x 只有 0。OK。

潜在问题：当 total 恰好能被覆盖时（test_exact_fit），height=1792: origins: 0 → 0+1024<1792 → append 896; 896+1024=1920 not<1792 → stop. So origins [0,896], tiles 2 个，第二个 y1=min(1920,1792)=1792。覆盖 0..1792。OK。

覆盖性：step>0，且最后一 tile 从 y_last 到 y_last+tile_size ≥ total（因循环停止条件），且前一个 tile 结束于 prev+tile_size > y_last 需要 prev+tile_size > y_last... actually coverage consecutive: tile i covers [o_i, o_i+tile). o_{i+1} = o_i + step < o_i + tile。所以连续 tile 重叠，无洞。OK。

边界：如果 total < tile_size，origins=[0]，tile 为 [0, min(tile,total)] = [0,total]。OK。

2. **DIAG 语义对比**：DIAG 实验说"块内检出按 y+origin 回映；页级 NMS IoU≤0.5"（diagnosis §2.3 写 "页级做置信度序贪心 NMS（IoU≤0.5）去重"，probe 说明删除条件可能不同）。handoff 说 DIAG 探针用 `best_iou > iou_threshold`。需要核实 DIAG 脚本 `experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py` 里的 NMS 实现。这个文件在只读区（禁改面但可读）。让我读它确认：(a) NMS 条件严格大于？(b) pad 带处理是"中心点丢弃"？(c) 步进逻辑是否相同（origins 精确步进 vs 其他）？(d) 是否在 pad 后 crop 前应用了不同的贴边策略。

实际上关键在于"193 逐值复现"这一经验证据。如果生产实现与 DIAG 的 NMS/clip 不同，却复现 193，那说明差异在这页数据上无影响。但要注意：Owner 声称 qualification K01 pre_merge=193 与 DIAG 一致。这一致性本身是很强的证据，但需要检查 qualification 的 `text_boxes_pre_merge` 是否由生产路径产生（是，来自 options）。

不过还有一个关键陷阱：DIAG 的 193 是"合并前文本框"（含 pad 带中心点丢弃）。生产 193 = `len(boxes)` after tiling+NMS，也含 bubble 过滤。DIAG 193 的文本类过滤 `(1,2)` 与生产 `_text_boxes_from_results` 的过滤是否一致？生产 filter 是否也丢弃 bubble（class 0）并统计 n_bubble？DIAG 说文本类过滤 (1,2)。生产 `_text_boxes_from_results` 用 TEXT_CLASSES? 需读源码。若生产 filter 有额外几何校验（如 clip、min size、宽高比），而 DIAG 的 filter 与之相同（DIAG 说"每块走与生产逐字节相同的推理序列...同文本类过滤"—— 但 DIAG 的过滤是它自己实现的还是复用生产纯函数？）。DIAG 的探针说"不含 cluster_words_into_blocks 合并步"，但过滤呢？需要核对该脚本。若 DIAG 自己复制了一份过滤逻辑，那么"193 逐值复现"就交叉验证了两者一致。

3. **clip 语义差异**：生产用 `_text_boxes_from_results(scores, labels, boxes, crop_w, crop_h)` —— 第 4/5 参数大概是 width/height，用于 clip 到 tile 的 crop 尺寸（非 padded 尺寸）。等一下：`_text_boxes_from_results` 是共享纯过滤，接受 width/height 参数用于 clip？在整页路径中它收到整页 width/height。在 tiled 路径中收到 crop_w/crop_h（真实 crop 尺寸，非 padded）。这意味着盒子的坐标先被 clip 到 crop 边界。

DIAG 的做法：在 padded tile 上推理，target_size = padded 尺寸 (1024x1024)（DIAG 说 target=padded 尺寸）。然后丢弃中心在 pad 区的框。生产的 target 也是 padded 尺寸（`_tile_inference` 用 `tile_rgb.shape` = padded → 1024x1024）。然后 filter 时传入 crop 真实尺寸做 clip。

差异情形：一个框部分落在 pad 区、中心在 crop 区内 → DIAG 保留（中心在 crop 内），生产 clip 到 crop 边界后保留（被截断）。坐标不同！例如框 [500,900,800,1100]（tile 690x1024crop→padded 1024 宽；x 800 > 690 在 pad 区），中心 x=650 在 crop 内。DIAG 保留原框（含 pad 区部分，x1=800），生产 clip 到 x1=690。两者坐标不同 → 后续 NMS/IoU 与最终输出框尺寸不同。

再看另一种：中心在 pad 区 → DIAG 丢弃；生产：如果框与 crop 有交集，clip 后保留（部分框）。例如框 [600,900,1200,1100] 中心 x=900 > 690 在 pad 内 → DIAG 丢弃；生产 clip 到 [600,...,690,...] 保留（宽 90 的窄条）。这是两者**实质性不同**：生产会多出 DIAG 丢弃的框（pad 带内的检出的与 crop 相交部分）。

Owner 的等价论证是"DIAG pad 带实测 0 检出"——即 DIAG 在 K01 70 块的 pad 带没有检出，所以两种处理在 K01 上数值等价。但需注意"pad 带零检出"的含义：是框中心落在 pad 带的有 0 个，还是与 pad 带相交的框有 0 个？诊断 §2.3 说"pad 无文字内容，回映后按'中心点落入 pad 区'丢弃"，结果"226 → 226（pad 区丢弃 0）"——即丢弃 0 个。这只证明没有中心落入 pad 区的框。不能证明没有与 pad 带相交的框！如果有框中心在 crop 内但延伸到 pad 带，DIAG 保留原框（延伸进 pad 的坐标），生产会 clip。这会产生坐标差异 → 可能导致 NMS 决策不同 → 数量不同。

但经验证据是生产 K01 pre_merge=193 与 DIAG 逐值一致。若存在延伸进 pad 带的框，坐标会不同，最终经过 NMS 后计数可能仍相同（因为 NMS 计数对小幅坐标变化不敏感），但"逐值一致"指的是计数 193，而不是坐标逐值。handoff 说"K01 180 region（193 框逐值复现）"——"逐值复现"含糊：是框数逐值还是框坐标逐值？JSON 里没有落盘生产侧的 pre_merge 框坐标，所以无法验证坐标。因此"逐值一致"实际只是计数一致。这是 review 需指出的：等价论证不严密；建议补一条断言/单测：pad 带相交框的处理语义，或落盘生产 pre-merge 坐标与 DIAG 比对。

实际上可以用更细的论证估计影响：K01 页宽 690，tile 1024，pad 带 x∈[690,1024) 宽 334px。框中心在 crop 内（x<690）且 x1>690 的框（跨过 pad 边界的框）——模型在 pad 边界右侧是纯灰，检测框通常不会延伸到纯灰区太多，但可能。数量未知。风险 P2/P3：等价论证以"pad 带中心点丢弃 0"为依据，但两者差异还包括"跨 pad 边界的框是否被 clip"，DIAG 数据（丢弃 0）不排除该情形。建议 review 结论：要求集成方（或后续）落盘生产 pre-merge 框坐标与 DIAG 的 `pre_nms_boxes` 逐一比对，或补单测固定"中心在 crop 外/跨边"语义。也可以自己从 DIAG JSON 检查 pad 带统计——但 DIAG JSON 只有统计，没有那时候的 pad 处理分支数据（它说丢弃 0 = 没有中心在 pad 的框）。嗯，如果 DIAG 全量落盘了 pre_nms_boxes 坐标，我可以检查有多少框 x1 > 690（即延伸到 pad 带）或者底边超过尾块 crop 高度等等。可以自己在沙箱里跑脚本？沙箱无 shell（pwsh 失败），所以只能手动用 read 解析 JSON。JSON 有 820 行 + probe-results.json 可能很大。我可以读 probe-results.json 的 pre_nms_boxes 部分并手工审查（用 grep 找 x1 > 690 的框很难）。可以 grep 特定模式。

嗯，也许更高效：DIAG 的 pre_nms_boxes 有 226 个框，每行一个数组，如 `[391.3, 27800.1, 600.8, 27892.3, 0.949]`。要看是否有框第 3 个分量 > 690（跨 pad 边界）。但格式可能是 JSON 单行或多行。让我用 grep 搜索。

也要检查：DIAG 是否也做了"crop 到 tile 边界"的处理？诊断文本说"pad 无文字内容，回映后按中心点落入 pad 区丢弃"。所以 DIAG 保留框原坐标（未 clip）。但生产 clip 到 crop 边界（width=690），因此所有生产框 x ≤ 690。DIAG 的框若 x1>690，则可证明差异存在。这是关键的可验证点。

另外，垂直方向：尾块 crop_h=309，padded 到 1024；框底边可能 > 309 → 生产 clip 到 309，DIAG 保留到 >309 坐标？但 pad 在下部（y>309 是 pad），同样问题。但注意垂直方向 pad 只出现在最后一个 tile（当 tile 未满）。K01 尾块 crop_h=309，其余块都满 1024（因为 690 宽但高度 1024 满）。所以尾部 pad band y∈[309,1024) 高 715px。

此外，跨块边界的框：DIAG 说"跨块截断的框...未观察到病态输出"。生产 clip 到块界后，框不会超出块界，而 DIAG 的框可能超出块界（进入下一个块的重叠区——这实际上不是 pad，因为 target_size=padded 尺寸，超出 crop 但仍在 padded tile 内）。等等，重要：DIAG 的回映是"y+origin"，框可能延伸到 crop 之外（重叠区），因为 target=padded 尺寸（1024）而 crop 也是 1024 高（对满块）。对满块，padded = crop，没有 pad。只有宽度方向 pad（690→1024）和尾块高度 pad。

所以差异面：(a) x ∈ (690, 1024] 的框部分；(b) 尾块 y > 309 的框部分。

所以需检查 DIAG pre_nms_boxes 中是否存在 x1 > 690 或（尾块回映后）y1 > 61824+309=62133（不可能超过，target 上限 1024 → y up to 61824+1024=62848 > 62133）。所以检查：框 x1 > 690（超过页宽——因为页面宽 690，任何 x>690 的坐标在页面外！）注意回映后坐标是页坐标，页宽 690。如果 DIAG 保留了跨 pad 的框，其 x1 会 > 690，即超出页面。生产 clip 后 x1 ≤ 690。那么 DIAG 的 pre_nms_boxes 中若有 x1 > 690 的框，就证明差异存在。可检查！而且如果没有，等价论证在 K01 上就经验成立。

同样 y1 > 62133 的框（超出页高）也是同理（尾块 pad 或 block 边界？不，块内 y 方向 1024 满块，最后一块 y up to 61824+1024=62848 > 62133，即超出页面）。

好，用 grep 检查太繁琐（数值格式）。也许我可以读 probe-results.json 的 pre_nms_boxes 段并目视。226 个框，每行约 1 个。可行但要读很多行。我可以用 grep 搜索 `6[9-9][0-9]\.` 之类... 更简单：grep 正则找第 3 个数字 > 690 的模式不容易。

替代方案：让一个 subagent 做这个数值核对？subagent 也有同样的工具与文件访问。其实我可以写一个 pwsh 脚本——但 pwsh 因沙箱 SetNamedSecurityInfoW failed 失败了。这是文件策略/权限问题：workspace-write 模式下 pwsh 尝试 grantWrite 失败。可能重试也一样。让我再试一次 pwsh（可能瞬时错误），或者可以用 `sandbox_permissions: danger-full-access` 重试（需要审批）。任务说"沙箱无 shell 时不执行命令，NOT_VERIFIED 留给集成方"——即预期可能没有 shell。所以应避免依赖 shell。

那就纯静态审查 + read/grep。

让我先读 probe-results.json 结构找到 pre_nms_boxes。用 grep 找 "pre_nms_boxes" 的行号。

另外注意：我可以用 grep 的正则来匹配超界框，例如匹配 `\[\s*\d+\.\d+,\s*\d+\.\d+,\s*(6[9-9]\d|7\d\d|8\d\d|9\d\d|1\d{3})` ... 复杂。ripgrep 支持正则。框行格式 `[391.3, 27800.1, 600.8, 27892.3, 0.949]`（若单行）。我可以搜索第三个数字 ≥ 690.5 的模式：`\[\s*-?\d+(\.\d+)?,\s*-?\d+(\.\d+)?,\s*(69[0-9]|6[0-9]{2}\.\d|[7-9]\d{2}|1\d{3})`。不过数字格式可能有更多小数位。这有点 hacky，但可行。

先看 JSON 中 pre_nms_boxes 的实际格式。grep 上下文。

现在继续：读 diff 剩余部分（1801-2350），读 worktree 源码 detection_manga.py 完整，读 DIAG 脚本关键段，读 probe-results.json 相关段。

我并行执行多个读取。

先读 diff 剩余 + detection_manga.py 的 detect 与 filter 部分（需要知道文件行号，先 read 全文件，可能 600+ 行；读 1-250、250-700？）。让我先 read 整个文件（limit 2000）。

也要读 src/infrastructure/providers/detection_doctr.py 的 cluster_words_into_blocks 与 MERGE_PAD_PX 以核对 merge 行为（可选）。

并行：
1. read diff offset 1801 limit 550
2. read worktree detection_manga.py (limit 2000)
3. grep "pre_nms_boxes" in probe-results.json to locate
4. read DIAG diagnose script (maybe long) — grep for "iou" / "nms" / "pad" first.

让我发出这些调用。注意 read 是全文工具，worktree detection_manga.py 有约 700 行（+369 后）。原文件 538+ 行，现在约 700 行。OK。
dsh: reasoning:
现在需要核对 DIAG 脚本的 NMS 与 pad 处理，以及 probe-results.json 中的 pre_nms_boxes（检查 x1 > 690 的框）。

关键点确认：`_text_boxes_from_results` 对 tiled 路径传入 crop_w/crop_h，执行 clip 到 [0, crop_w] x [0, crop_h]。DIAG 是"pad 带中心点丢弃"。差异面如我分析：
- 中心在 pad 带内但框与 crop 相交 → DIAG 丢，生产保留（clip 后）
- 中心在 crop 内但框延伸到 pad → DIAG 保留原（超页）坐标，生产 clip

DIAG "pad 区丢弃 0" → 第一种在 K01 上为 0。第二种需要检查坐标 x1>690。DIAG 的 pre_nms_boxes 若落盘，可 grep。

注意：DIAG 的 target_sizes 是 padded 尺寸还是 crop 尺寸？诊断说"target=padded 尺寸"。handoff 说生产 `_tile_inference` "target=padded 尺寸=DIAG"。生产用 `tile_rgb.shape`（padded 1024x1024）。这与整页路径不同：整页路径用源尺寸 (height,width) 作为 target_sizes（因为整页被 processor 缩放到 640 后 post_process 会映射回源尺寸）。tiled 路径用 padded 尺寸做 target 是合理的（图就是 padded），然后 clip 到 crop。

现在，DIAG 脚本要确认：
1. NMS 条件（best_iou > threshold）
2. pad 处理（中心点丢弃）
3. target_sizes
4. 是否对框做了 clip（若有 clip 到 crop，则与生产等价，handoff 的"两法不同"陈述就错了——但没什么影响）

读 DIAG 脚本。同时 grep probe-results.json 的 pre_nms_boxes。

还要核对 `experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py` 是否存在（只读区）。

另外还需检查：
- 测试文件在 worktree 的完整版本（diff 已显示大部分新增测试，但 diff 只显示 452 行新增；我看到的内容覆盖了新增部分。还有既有测试改动？handoff 说既有测试零修改。diff 只显示新增 458 行在测试文件，无删除——从 diff hunk header `@@ -368,6 +368,458 @@` 看，只在 368 行后插入。OK。

- 还要看 test 文件前面的既有辅助函数（_provider、_request、_frame_bytes、detection_doctr import）— 应该已存在。

现在关键：env fail-fast 是裸 ValueError，未 typed。任务书要求"fail-closed 不放宽（tiling 内部失败 typed）"。`_tiling_config` 抛 ValueError 会穿过 detect()。检查调用方（handler/step）是否捕获 ValueError。让我 grep 谁调用 provider.detect，以及 ProviderError 的处理方式。

另外 "普通页零变化" 的一个细微点：`_tiling_config()` 现在对所有页面（包括普通页）执行 env 读取。若 env 设了非法值，普通页也失败 —— 这是行为变化（此前不读 env）。但这只在 operator 配置非法时。是否算"零行为变化"破损？应作为 finding 登记（P3）：非法 env 时普通页 detect 由可用变为抛 ValueError；且该异常非 typed provider error，可能逃逸到上层成为未处理异常。建议将 `_tiling_config()` 的 ValueError 包装为 ProviderInputError 或 ProviderError（typed），或至少在文档/测试中明确该 fail-fast 语义。测试有 `test_illegal_values_fail_fast` 只测 `_tiling_config()`，没有测 detect() 在非法 env 下的行为（是否 typed）。这是一个测试缺口。

同时注意：`_tiling_config()` 在 `_frame_pixels` 之后、engine 之后。若 env 非法，engine 已加载（耗时），然后失败。fail-fast 顺序还好。

再看 `detect()` 里 `("text_boxes_pre_merge", str(len(boxes)))` 与 `*tiling_options`。options 是 tuple of tuples。既有的 `dict(result.options)` 断言不受影响。OK。

注意：`_detect_text_boxes_tiled` 里 `tiles = _tiling_tiles(...)` 又被 detect() 重新计算一次以得到 tiles 计数（用于 options）。轻微重复计算（70 块 → 便宜）。不是问题。

潜在的性能问题：`_pad_tile` 每块分配 1024x1024x3 = 3MB 新数组（可以接受）。rgb[..] 是视图，pad 复制。OK。

`_tile_inference` 里 `inputs = {key: value.to(model.device)...}` 与整页路径一致。OK。

**重要**：`_tile_inference` 的 `except (ProviderDependencyMissing, ProviderError): raise` —— 与整页一致。

**回映与 clip 顺序**：生产先 clip 到 crop 边界再回映。DIAG 先回映（+origin）再（可能的）pad 丢弃。数值上 clip 后可加 origin，等价于加 origin 后 clip 到 [x0, x1] 页区间（因为是纯平移）。OK。

**NMS 跨块残留风险**：DIAG 提到"跨块截断的框（一个气泡被块边界切开）"。生产 clip 后，块边界处的框被截断为半个气泡；如果同一气泡在相邻两块都被检出，两个半框的 IoU 可能低于 0.5 → NMS 不去重 → 残留两个半框（下游 OCR 会拿到两个残缺框）。DIAG 说"未观察到病态输出"，但 30/33 删框在重叠带说明大多数是重复。这是一个已知风险，Owner 在 DIAG 已登记（directional）。Review 应登记为 P3 观察项（跨块截断框的合并/丢弃策略未处理：无"边缘框修复"逻辑，例如把被块边界截断的框与相邻块的同目标框 union 或丢弃重叠带边缘框）。注意 DIAG 的 NMS 与生产一样，没有特殊处理，而 DIAG 数据表明 NMS 去掉了 33 个重复框，剩下 193 个"合并前"框。是否包含被截断的半框？无法从统计判断，但 DIAG 落盘了全量坐标，可以检查是否有框的 y0/y1 恰好等于块边界（例如 y1 = 块边界 1024 的整数倍 + 起点），那是被截断的迹象。这可以 grep 检查。

不过我们时间有限，重点是给出可执行 findings。让我看看 probe-results.json 的大小与 pre_nms_boxes 格式。

计划：
1. grep "pre_nms_boxes" in probe-results.json → 找行号
2. read DIAG 脚本的 NMS/pad 段（先 grep "def " 和 "iou"）

并行执行 grep。

另外还要检查禁改面零 diff：从 review-input.diff 看，只包含 5 个文件（handoff、task、qualify_tiling.py、detection_manga.py、test_detection_manga.py、qualification-report.md、qualification-results.json = 7 个）。diff 里出现的 "diff --git a/" 行有：
1. doc/handoffs/...
2. doc/tasks/...
3. experiments/M2-DETECT-WEBTOON-TILING/qualify_tiling.py
4. src/infrastructure/providers/detection_manga.py
5. tests/providers/test_detection_manga.py
6. verification/M2-DETECT-WEBTOON-TILING/qualification-report.md
7. verification/M2-DETECT-WEBTOON-TILING/qualification-results.json
共 7 个文件，都在允许面。用 grep 核对 "diff --git" 行数。

另外要验证 diff 里是否有二进制文件（"Binary files" 或 GIT binary patch）：grep。

还要检查 test 文件被改动区的上下文：`@@ -368,6 +368,458 @@` 后面还有 `@@ -...` 吗？测试文件只有一个 hunk（368→458 行插入）。而末尾的 "identity" 注释重复是 diff 上下文重叠的显示。看起来 `@@ -368,6 +368,458 @@` 里包含了原有 6 行 context（包括 `# --...` 和 `# identity` 注释）。这有点奇怪：diff 显示在 hunk 末尾：
```
+# ---------------------------------------------------------------------------
+# identity
+# ---------------------------------------------------------------------------
+
 # identity
 # ---------------------------------------------------------------------------
```
即新增块以三个注释行结尾，然后接原有 `# identity` 行。这暗示原来的测试文件在 368-373 行处是：
```
...
# ---------------------------------------------------------------------------
# identity
# ---------------------------------------------------------------------------
```
而新增内容插在前面。OK，无删除。

现在 grep 这些。

另外需要确认 tests 里的 `_provider()`、`_request()`、`_frame_bytes()` 辅助函数存在且签名匹配（`_provider(weights_dir=...)`）。grep 测试文件中这些定义。

还有：`test_normal_page_never_enters_the_tiled_branch` 用 30x42（h/w=1.4）→ 不触发。双向哨兵：一个测试禁止 tiled 分支被调用（普通页），另一个测试禁止直到路径被调用（长条页）。这基本足够。但"普通页零变化"的更强证据是 `_detect_text_boxes` 函数体零 diff。但这里有一个细节：`detect()` 在普通页路径上，除了 `_tiling_config()` + `_tiling_triggered` + options 新增两个键之外，其它相同。options 新增 `text_boxes_pre_merge`、`tiling` 键 → 对下游 consumer 有影响吗？options 是 tuple of pairs，某些 consumer 可能断言 options 内容或长度。handoff 说"dict 取键式既有断言不受影响"。需 grep 检查是否有 consumer 依赖 options 的精确列表/长度（例如 m2_acceptance 测试或步骤记录）。这是一个真实的兼容性风险点：新增 options 键可能影响把 options 写入 DB/日志的地方（一般不破坏），但如果某处 assert options == (...) 就会 break。tests 已过（575 passed），说明仓库内测试无破坏。但 Tauri/前端或 acceptance 快照可能记录 options。搜索 options 的使用。

好，让我并行 grep 一批：
1. grep "^diff --git" in review-input.diff
2. grep "pre_nms_boxes" in probe-results.json
3. grep "def .*iou|iou_threshold|pad" in diagnose_webtoon_detect.py — 先看文件行数：read 部分。
4. grep "text_boxes_pre_merge|tiling" 在 src/ 与 apps/ 中（找 consumer）。

由于 grep 工具只接受一个 pattern，我可以并行多个 grep 调用。

先做 4 个 grep。
dsh: reasoning:
好——`src` 中没有其他 tiling 消费方，只有 QML/PySide6 legacy 时代的 TASK-020（不同含义）。`text_boxes_pre_merge` 在 src 中未被使用（只在本 diff 产生）。

现在读 DIAG 脚本 260-300（greedy_nms）和 390-430（pad 丢弃与回映）确认语义，以及 226-260（_pad_tile 与 tile 推理 target_sizes）。

再看 probe-results.json 的 pre_nms_boxes 段（1188-1416），检查 x1 > 690 或 y1 > 62133 的框。我可以读这段（228 行，OK）。行格式 `[x0, y0, x1, y1, score, tile_index]`。

读 probe JSON 1188-1420。然后人工检查数字。这需要仔细读 226 个框的第 3 分量是否 > 690。嗯，视觉扫描不可靠。也许用 grep 正则。格式可能是 `[392.0, 27799.7, 600.2, 27892.4, 0.9534, 30]`。

我可以 grep 匹配第三个数值 ≥ 690.5 的模式。ripgrep 正则：`^\[\s*[-0-9.]+,\s*[-0-9.]+,\s*(69[1-9]|6[9-9][0-9]|[7-9][0-9]{2}|[1-9][0-9]{3})` 但数字带小数："691.0" 也匹配 691。需要 `(69[1-9]|6[9-9][0-9]|[7-9][0-9]{2}|[1-9][0-9]{3})(\.\d+)?`。

问题是 pre_nms_boxes 的行是否以 `[` 开头（缩进）。从格式看 compact block 用 elem_indent，所以行可能以空格 + `[` 开头。

也可以反向检查：搜索行中第 3 个分量大于 690 的。用正则：
`\]` ... 难。

更稳妥：读那段文本（1188-1416），人工扫。226 行里我主要看每行第三个数。人工扫 226 行不可靠但可以注意是否有 >690 的（三位数字以 7、8、9 开头，或四位数）。实际上第三个数若 >690 会是 691..1024 之间的值，即以 7/8/9 或 10 开头的三位/四位数。而正常的 x1 值多在 300-690 之间（也可能 <300）。如果出现 "7xx."、"8xx."、"9xx."、"1xxx." 就是超界。用 grep 找 `, 7` `, 8` `, 9` 也太多。

用正则匹配"第三个数值是 691-999 或 1000-1024"：
`^\[[^,]+,[^,]+,\s*(69[1-9]|[7-9]\d{2}|10[0-2]\d)`

不过坐标可能有负值或格式 `-`。OK。

另一个更重要的检查：DIAG 的 pad 丢弃逻辑是 `if center_x > width` —— 只检查 x！看 line 404 上下文：`if center_x > width:  # center in the right pad band`。那么垂直 pad（尾块的 y > crop_h）没有被丢弃！也就是说 DIAG 只处理了右侧 pad 带，没有处理底部 pad 带。等等，让我读上下文确认，也许有 center_y > height 检查。line 400-410。需要读。

如果 DIAG 只丢 center_x > width，那么尾块 y 超出 crop_h 的框会被保留（比如框 y 在 309..1024 之间，页坐标 61824+309=62133..62848，超出页高）。也就是说 DIAG 的 193 中可能包含超出页底的框，而生产 clip 到 crop_h=309 会把这些框截断或（若框完全在 y>309）变成退化框被丢弃（x1<=x0 或 y1<=y0 → skip，或数值上 clip 后 y1=309=y0 时退化被 skip）。等等：生产 `_text_boxes_from_results(scores,labels,boxes, crop_w, crop_h)` 先 clip 到 crop 边界。若一个框完全在 pad 区（y0>309），clip 后 y0=y1=309 → 退化 → skip。所以生产会丢弃完全在底部 pad 区的框；DIAG 若仅检查 center_x，则保留它们（除非它们也在右侧 pad）。

这可能导致 DIAG 193 vs 生产 193 的巧合——两者数字相同，但框集合不同！还是说 DIAG 也有 y 检查？必须读代码确认。

这是审查的核心点之一。读 DIAG 脚本 380-470。

同时读 1188-1420 的 pre_nms_boxes，并检查是否存在 y1 > 62133 或 x1 > 690 的框（probe 落盘的是"回映后 page pixels"坐标，可能未 clip，所以超界可检测）。注意 probe 里的 pre_nms_boxes 行含 tile_index —— 有帮助。

另外 post_nms_boxes 是最终 193，若其中存在 x1 > 690 或 y1 > 62133 的框，则说明 DIAG 的框超出页面边界，而生产 clip 后会不同 → "193 逐值复现"仅计数相同，坐标不同。这正是我需要验证的。

让我 grep post_nms_boxes 段中第三分量 > 690 的行。段范围 1416-1611。用 grep 正则带路径+行号；grep 只给匹配行。我可以用两个 grep：一个匹配 `^\s*\[[^,]+, [^,]+, (69[1-9]|[7-9][0-9]{2}|10[0-2][0-9])` 之类。但 ripgrep 默认按行匹配，JSON 行以 `[` 开头。

先读 DIAG 代码段，然后处理数据。

另外确认 DIAG 的 greedy_nms 条件：line 289-295: `best_iou` 初始 0.0，`if iou > best_iou` 记录；`if best_keeper >= 0 and best_iou > iou_threshold: removed`。所以删除条件是严格大于 threshold —— 与生产 `any(_iou(box, keeper) > iou_threshold ...)` 语义一致（生产用 any，DIAG 用 best；等价，因为只要存在一个 > threshold 就删）。✓

注意 DIAG 的 `greedy_nms` 排序：需要看它是否按 conf 降序排序（line 275-295）。也要注意 tie-breaking 与稳定性。生产 `sorted(boxes, key=lambda b: b[4], reverse=True)` 是稳定排序，同分保持原顺序（tile 顺序）。DIAG 呢？需读。

读 DIAG 脚本 260-300 和 380-470。並读 probe JSON 的 pad 处理相关字段（"n_dropped_center_in_pad"）。

执行。
dsh: reasoning:
重要发现：DIAG 的 pad 丢弃只检查 `center_x > width`（右侧 pad），**没有** center_y > crop height 的检查（底部 pad）。而生产的 clip 到 crop 边界会同时处理 x 和 y。

不过对 K01：每块 crop_h 都是 1024（满高）除了最后一块 309。所以底部 pad 只影响最后一块（tile 69, origin 61824, crop 61824..62133, crop_h=309）。若最后一块有框 y1b > 309（超出页底 62133），DIAG 保留（page y up to 61824+1024=62848），生产 clip 到 309。

同时右侧 pad：每块宽 pad（690→1024）。DIAG 只丢 center_x>690 的框，但保留 center_x ≤ 690 且 x1 > 690 的框（会超出页宽 690）。生产 clip 到 690。

所以 DIAG 的 193 里可能含有超出页边界的框。检查 post_nms_boxes 里是否有 x1 > 690 或 y1 > 62133 的框即可。

从上面 pre_nms_boxes 看，x1 最大可见 671.0（line 1202）、668.2（1207）、667.7（1210）、656.7、644.8、644.1、639.9、636.2、633.6、623.9、623.1 —— 都 ≤ 690。看起来确实没有跨过 690 的框（至少这部分）。但 226 个框我只看了 ~50 个。需要系统地检查。

用 grep 正则匹配 pre/post_nms_boxes 区域中第三个分量 > 690 的行。段范围：pre 1188-1415，post 1416-1610。让我用 grep 匹配形如 `[<num>, <num>, <691-1024>,` 的行。

正则：`^\s*\[-?[0-9.]+,\s*-?[0-9.]+,\s*(69[1-9]|6[9][1-9]|[7-9][0-9]{2}|10[0-2][0-9])(\.[0-9]+)?,`
简化：第三个数是 691-690？ 我关心 > 690：691-999 和 1000-1024。
- 69[1-9] → 691-699
- 6[9]? Hmm 690.x 也 > 690，但我们只关心严格大于 690 的坐标（如 690.5）。用 `69[1-9]|6[9]{2}` 不严谨。
简化：`,\s*(6(9[1-9]|[0-9]{2})|[7-9][0-9]{2}|1[0-9]{3})(\.\d+)?,` 会匹配 690-699（含 690）等，误差可接受——人工复核匹配行。

更简单：匹配第三个数以 7/8/9 开头或 69x/6xx 中的 69x/6[7-9]x→ 太多。

我干脆匹配 `,\s*[6-9][0-9]{2}(\.[0-9]+)?,` （第三个数为 600-999 → 匹配 6xx,7xx,8xx,9xx，都是可疑的高 x1 值）以及 `,\s*1[0-9]{3}(\.[0-9]+)?,`（1000+）。这样匹配结果我人工检查哪些是第三个数位置。但 grep 返回整行，需要区分第三个数还是其他位置——正则里有前两个 `[^,]+,[^,]+` 前缀锚定。

pattern: `^\[\s*[0-9.]+,\s*[0-9.]+,\s*(6[0-9]{2}|[7-9][0-9]{2}|1[0-9]{3})`

注意 JSON 中行可能以空格缩进 + `[`。ripgrep `^\s*\[`。坐标没有负值（页面内）。pre_nms 的 y 可能为负？不会。

同时检查 y1 > 62133：第四个分量 > 62133 → `,\s*6(2[1-9][0-9]{2}|[3-9][0-9]{3})`. 但我更关心 x1（因为 x 方向 pad 每块都有，而 y 方向 pad 只有最后一块）。

先跑 grep 检查第三分量 ≥690（pre 与 post 段均会匹配；我也可以限定 path 与 pattern，然后看行号范围）。

另外还要检查"框中心在 crop 内但 x1>690"的数量。grep 只找 x1>690 的行。若为 0，等价论证就成立（在 K01 上）。若 >0，则说明生产 clip 与 DIAG 保留不同 → 计数 193 相同但坐标集合不同 → 需登记。

还要检查底部：最后一块（tile_index=69）的框 y1 > 62133。grep `,\s*6(2[1-9][0-9]{2}|[3-9][0-9]{3})` 匹配第四分量 ≥62100。

再一个：DIAG 的 tile 循环 `while y < height` + `y += step`，tile 数 70，与生产 `_tiling_tiles` 的 origins 一致（0,896,...,61824）。生产 origins 条件 `found[-1] + tile_size < total`：在 y=60928 时 60928+1024=61952 < 62133 → append 61824；y=61824 时 62848 not< 62133 → stop。70 个。DIAG：y=0,896,...; 循环直到 y≥height。y 序列 = k*896, k=0..；当 y=61824, y1=62133=height，break。k = 61824/896 = 69.0 → k=0..69 = 70 个。一致 ✓。

现在跑 grep。

同时我还要看测试文件中 `_provider` 等辅助函数（确认 `_provider(weights_dir=...)` 支持）。以及读取 tests 文件相关部分以评估"双向哨兵"充分性。grep `def _provider|def _request|def _frame_bytes` in test file。

还想确认 qualification 脚本的 Gate 判定是否程序化（是：`overall = "PASS" if all(v=="PASS")`，且 return 3 on FAIL，`report["gate"]["overall"]`）。注意：`gate_values = list(report["gate"].values())` —— 此时 report["gate"] 只有 K01..K08 五个页面的值（controls 尚未加入，是在 overall 之后才写 controls）。所以 overall 只看 5 个 Gate 页 —— 正确。controls 单独记录但**不参与 overall 判定**。也就是说 K19/BJ02 控制项失败不影响退出码/Gate。这是一个轻微的方法论弱点：control 结果只记录，不 gate。不过 DIAG 冻结口径的 Gate 就是"5 张 webtoon region>0"，控制项是附加证据。可以登记为 P4 说明。

另外：`curve_point` 用 `cluster_words_into_blocks` 重算合并后的 region 数——用 boxes 的 (x0,y0,x1,y1) 和 conf。这与生产 detect 内部的调用一致（page_size=(w,h)）。OK。但注意生产 detect 的 merge 输入 boxes 是 NMS 后的相同结构。所以 0.5 点的 region 数就是生产 region_count。JSON 中 "0.5" 的 region_count_post_merge 直接用了 region_count（生产），OK。

还有一点：qualification 的 Gate 是程序化的（脚本自行判定 PASS/FAIL 并退出码 3）。但 Gate PASS 的**证据**是 JSON 文件；DSH 无法运行复现（沙箱无 shell）→ NOT_VERIFIED（留给集成方重跑）。

现在跑 grep 检查极值，和 test 辅助函数。
dsh: reasoning:
第一个 grep 匹配 111 行，是因为我的正则 `(6[0-9]{2}|[7-9][0-9]{2}|1[0-9]{3})` 匹配了 6xx/7xx/8xx/9xx —— 大部分是 600-689 的值（第三分量 ≤690 是正常的）。没有匹配 69x 以上？看结果：最大值可见 674.4（line 1271/1486）、673.9、672.1、671.0、670.8、668.2... 都 < 690。没有 69x、7xx、8xx、9xx、1xxx 出现（否则会显示）。

需要确认是否真的没有 >690 的值。我的正则包含 6xx 全段（600-699）和 7xx-9xx、1xxx。结果里最高的第三分量是 674.4。因此 pre/post NMS 的所有框中 x1 ≤ 674.4 < 690（页宽 690）。**右侧 pad 跨界框不存在**（K01 上）。这与 DIAG "中心在 pad 带丢弃 0" 一致，并进一步证明没有框延伸到 pad 带。

第二个 grep 找第四分量 ≥ 6200 的（我的正则 `6[2-9][0-9]{3}` = 62000-69999，`[7-9][0-9]{4}` = 70000+）：匹配行 1412/1414/1608/1609，值 y1 = 62055.8、62044.6 —— 都 < 62133（页高）。哦等等，我的正则要求 5 位数 `6[2-9][0-9]{3}` = 6 2xxx-6 9xxx 即 62000-69999。匹配了 62055.8 和 62044.6，都小于 62133。所以没有 y1 > 62133 的框。**底部 pad 跨界框也不存在**。

所以生产 clip 与 DIAG 的中心点丢弃在 K01 上数值等价（框都落在页面范围内，且都在 crop 范围内）。这加强了等价论证：不仅"pad 带中心点 0 个"，而且"没有任何框跨出页面边界"。但注意：生产 clip 到 crop 边界 ≠ clip 到页面边界。对中间块，crop 边界在重叠带内（y 1024 等），框完全在页面内但可能超过某块的 crop 边界；若某框中心在 crop 内且跨过 crop 底边（进入下一块重叠区），DIAG 保留它（不 drop，因为 center_x 检查只针对 x），生产会 clip 到 crop 底边 → 坐标不同！

嗯！这是另一个差异面：块内的框延伸到块底边之外（进入重叠带）的情况。DIAG 保留完整框（不含任何 y clip）；生产把框 clip 到 crop 高度（1024）。这在满块（crop_h=1024）时，若框 y1 > 1024（在 tile-local 坐标，即越过块底边进入下一块区域）→ DIAG 保留 y1 原值（page y = origin + y1 > origin+1024），生产 clip 到 origin+1024。

能否从 DIAG 数据检测？post_nms 坐标中，若某框 y1 超过其 tile 的 origin+1024（或 y0 < origin），则说明 DIAG 保留了跨块边界的框。但 probe JSON 里有 tile_index，可以计算。例如 line 1191 `[94.3, 1627.7, 602.4, 1673.2, 0.943, 1]`：tile 1 的 origin=896，crop 范围 896..1920。y1=1673.2 < 1920 ✓。line 1194 tile 2 origin 1792, range 1792..2816, y=1896-1938 ✓。

要找 tile_index=k 且 y1 > k*896+1024 的框。k=0 → >1024；k=1 → >1920；k=2 → >2816；... 也许存在。上面看到的框基本都在 tile 内（因为模型自然会检出框在 crop 内，pad 区是灰）。检查 line 1207 `[390.9, 6330.2, 668.2, 6372.6, 0.9393, 6]`：k=6 → origin 5376, range 5376..6400；y1=6372.6 < 6400 ✓。line 1411 `[338.0, 61918.2, 632.1, 61952.3, 0.6758, 68]`：k=68 → origin 60928, range 60928..61952。y1=61952.3 > 61952! 超出 0.3px（浮点）。轻微。line 1412 `[287.9, 61918.3, 635.6, 62055.8, 0.738, 69]`：k=69 → origin 61824, crop_h=309 → 范围 61824..62133；y1=62055.8 < 62133 ✓。

所以 k=68 的 y1=61952.3 仅超 0.3px（舍入）。这表明模型的框可能贴着块底边（模型在 tile 内检出，post_process 映射到 1024 target，坐标理论上 ≤1024）。嗯，61952.3 = 60928+1024.3 —— 略微超过 target 尺寸 1024，可能是浮点/rounding。可以忽略。

但潜在差异是存在的：如果模型在一个满块内检出框，该框的 y1 > 1024 是可能的（post_process 一般不裁剪到图像边界？通常 RT-DETR 输出会被 clamp 到 target size，但 diff 显示整页路径的 `_text_boxes_from_results` 有 clip，说明模型输出可能超出）。DIAG 数据表明几乎都在范围内。

总结我的等价性结论：在 K01 实测数据上，两种处理的输出框集合数值等价（因为 (a) 无框中心在 pad 带；(b) 无框超出页面/tile 边界超过 0.3px）。但论证在**一般情形**下不成立（生产 clip 到 crop；DIAG 中心点丢弃）。Owner 的 handoff 措辞"（DIAG pad 带零检出下两者数值等价）"是基于 DIAG 结论，没有提到我额外证实的"无跨边界框"。这属于论证偏弱但结论在 K01 成立。值得作为 P3/P4 finding：建议把等价论证写得更精确（增加"无框跨出 crop 边界"这一条，可从 DIAG JSON 复算），或补一条单测固定 clip 语义。

另外还有一个差异面我需要注意：生产在 clip 后**丢弃退化框**（x1<=x0 or y1<=y0 → skip）。DIAG 只丢 center_x > width 的。若某框中心在 crop 内但完全在 pad 区（不可能，中心在 crop 内则与 crop 相交）。OK。

还有一个：生产对 clip 后的空框 skip，会丢弃"中心在 pad 区"的框（完全在 pad 内 → clip 后退化 → skip）。所以生产实际等价于"与 crop 无交集的框丢弃 + 与 crop 相交的框裁剪"。DIAG = "中心在 x-pad 的丢弃 + 其余保留原坐标"。在 K01 数据上等价。✓

接下来，关于"普通页零变化"的核实方式：Owner 用 `git diff` 论证函数体零 diff。我无法在沙箱运行 git。但从 review-input.diff 中 `_detect_text_boxes` 的 hunk 看，只有 docstring 被替换（`-    """Run one page through...` → +4 行 docstring），函数体（torch 调用、`target_sizes`、`threshold=MANGA_CONF_THRESHOLD`）全部是 context 行。这确实证明函数体未变。✓ 但严格说"逐字节未动"仅对函数体成立，docstring 变了（handoff 自己也承认）。

不过还有 detect() 的变化：普通页分支现在多了 `_tiling_config()`（读 env）与 options 新增 2 个键。因此若 env 非法，普通页 detect 从"可用"变"抛 ValueError"；options 内容变了（对消费方是新增键，非破坏）。这两点需要作为 finding。

现在我需要检查 ValueError 是否会逃逸成非 typed 异常。看调用方：谁调用 provider.detect？在 src 中搜索 detect( 的调用，特别是有没有 except Exception 转 typed 的封装。让我 grep `\.detect(` in src。

另外需要检查 settings/env 先例 `NEWMANGA_SFX_CONF_THRESHOLD` 在 detection_sfx.py 里如何处理非法值 —— 是否也是 ValueError？如果先例也是 ValueError，那就一致，我作为 P4/说明。让我 grep。

同时检查 apps/（Tauri、Python Core handler）里 detect 调用与错误处理方式（INVALID_INPUT/PROVIDER_FAILED）。grep "detect(" in apps 与 src/application。

另外：任务书 AC1 说 "块尺寸/重叠/NMS IoU 参数配置化（env 先例 NEWMANGA_SFX_CONF_THRESHOLD 或 settings，Owner 勘察后选型留痕）" —— OK。

还需要检查 `MANGA_TEXT_CLASSES` 过滤在 tiled 路径的 pad 区行为：pad 区灰 114 可能产生 false positive（DIAG 实测 0）。

另外一个技术点：`_tiling_tiles` 返回的 tiles 顺序是 y 外层、x 内层（for y0 ... for x0）。对 K01 单列，顺序 = y 升序。NMS 的 tie-break 用稳定排序保持 tile 顺序。DIAG 的 order = sorted(range(len), key=conf, reverse=True) 也稳定。生产 sorted(boxes, key=...) 输入顺序 = 按 tile 顺序 append → 与 DIAG 的 page_boxes 顺序一致（DIAG 也是 tile 顺序 append，且块内顺序 = 模型输出顺序）。生产块内顺序 = `_text_boxes_from_results` 遍历顺序 = 模型输出顺序；DIAG `run_tile_inference` 的 tile_boxes 顺序 = 模型输出顺序。若过滤逻辑相同，两者顺序一致 → NMS tie-break 一致。✓ 但生产 filter 有额外 clip 与退化 skip，可能删除某些框改变顺序？删除不改变其余相对顺序。✓

还有 `_iou` 除零风险：area_a + area_b - intersection 为 0 时（两个退化框）→ ZeroDivisionError。生产 filter 已排除退化框（x1>x0, y1>y0），所以面积 > 0 → 分母 > 0（因为两框面积均 >0，交集 < min area → 分母 > max(area) > 0）。✓ DIAG 的 `_iou` 未防除零，但同样输入。OK。

现在关于 qualification 证据的审查：
- region 层级计量（合并后）+ 框层级并报 ✓（JSON 两者都有）
- 延迟数字 ✓
- 阈值曲线 ✓（0.5 vs 0.4，程序化）
- 690 对照 ✓
- K19/BJ02 ✓
- GATE PASS 判定程序化 ✓（脚本内 all(...) + 退出码）。但 controls 不参与 overall（P4）。
- 一个可核查点：K01 690 对照的 n_tiles=111 与 `_tiling_tiles(690, 62133, 690, 128)` 一致性。step = 690-128 = 562。origins: 0, 562, 1124, ... 直到 y+690 < 62133。最后一个 origin = ? 计算：origins 数 n = floor((62133-690)/562)+2? 条件 while o+690<62133 → o < 61443 → o = 562k < 61443 → k ≤ 109.3 → k=0..109 = 110 origins? 然后循环再加一个？让我细算：found 初始 [0]。循环：while found[-1]+690 < 62133 (即 found[-1] < 61443) → append。最后一个 found[-1] 满足 <61443 的最大 562k = 562*109 = 61258 < 61443 → append 61258；然后 61258+690=61948 < 62133 → append 61820；然后 61820+690=62510 not< 62133 → stop。所以 origins = 0..61820 step 562 → k=0..110 = 111 个。✓ 111 与报告一致。
  说明 690 对照组 n_tiles=111 ✓（报告说 ≈70×1.6×）。

  但注意：690 对照组的 tile 尺寸 690 与 K01 页宽相同 → x 方向 origins(690) = [0]（0+690 < 690? false）→ 单列。✓

- K05/K08 的 tiling_tiles：52 和 58。核对 K05: height 46000, tile 1024, step 896。origins: 最后一个 o = 896k, 条件 o+1024 < 46000 → o < 44976 → 最大 o = 896*50 = 44800 < 44976 → append 44800；then 44800+1024=45824<46000 → append 45696；then 45696+1024=46720 not< → stop。k=0..51 = 52 ✓（JSON tiling_tiles="52" ✓）。
  K08: 51971 → o < 50947 → 最大 896k = 896*56=50176 <50947；然后 50176+1024=51200<51971 → append 51072；51072+1024=52096 not< → stop。k=0..57 = 58 ✓。
  K02: 18401 → o<17377 → 896*19=17024<17377 → append 17024; 17024+1024=18048<18401 → append 17920; 17920+1024=18944 not< → stop → k=0..20 = 21 ✓。
  K04: 28156 → o<27132 → 896*30=26880<27132 → append; 26880+1024=27904<28156 → append 27776; 27776+1024=28800 not< → stop → k=0..31 = 32 ✓。

很好，块数与 `_tiling_tiles` 精确一致。

- K01 20.1s，预算 25s ✓。K02 5.97s ≤10 ✓，K04 9.27s ≤15 ✓。

关于延迟对发布形态的影响：Owner 登记了（handoff 风险与遗留：长条页最坏 ≈20s；用户提到 CPU 下 detect 从 ~574ms 到 20s）。DIAG 说"最坏页 ≈34× 于常规页"（19811ms vs 574ms）。20.1s vs 574ms = 35×。登记是否充分？handoff 提到"GPU/并发/降块策略=发布形态决策输入，本 Task 不做"。用户重点审查项 6 要求评估"UI/进度面影响"是否登记充分。handoff 里没有明确提到 UI/进度反馈或超时设置（Tauri IPC timeout、Python Core step 超时、UI 是否显示进度）需要集成方核实。这可能是一条 P3 finding：把 20s 单页 detect 暴露给 UI/IPC 的**超时与进度**面未评估（例如 Tauri invoke 默认超时、用户等待体验、是否需要进度事件/取消），仅登记了数值。这符合用户提示。

现在检查 provider.detect 的调用方与错误处理（ValueError 逃逸风险）。grep。

还有 SFX env 先例的处理方式。

并行 grep：
1. `\.detect\(` in src（看调用方）
2. `NEWMANGA_SFX_CONF_THRESHOLD` in src
3. `INVALID_INPUT` / handler in apps
4. 检查 options 消费方：grep `\.options` in src（是否有人按位置/长度断言）

另外还需确认 worktree 的 git 状态是否干净、是否有未提交文件（沙箱无法跑 git）。NOT_VERIFIED。

再检查 tip=36b61c3a（docs commit）在 diff 里吗？diff 包含 handoff 与 task 回填（文档 commit 的内容）。所以 review-input.diff 覆盖 base f99a6c55 → tip？diff 中包含 doc/tasks/... 修改与 handoff 新增 = 文档 commit 内容；implementation = detection_manga.py + tests + qualify + verification。所以 diff 是 f99a6c55..36b61c3a 的完整 diff（7 文件）。而 handoff 说 delivery_head=29a7f5b5（implement commit），文档是后续 commit。用户说 tip=36b61c3a（docs）。因此 diff 包含两者。需要确认 implement commit 29a7f5b5 与文档 commit 都只在允许面。7 文件都在允许面 ✓。

但要注意：Task 文件 frontmatter base_commit 是 f534c3e7（授权时点），而 handoff base_commit 是 f99a6c55。这是已知的（Task 回填里注明了）。diff 的 "for" 是 f99a6c55。OK。

现在跑剩下的 grep。
dsh: reasoning:
关键：`src/bootstrap/core_service.py:412` `result = detector.detect(request)`；line 386 `except Exception as error: # noqa: BLE001 - any decode failure is a bad request`。需要看 detect 调用周围的错误处理，判断裸 ValueError 是否被转成 typed。读 core_service.py 370-430 与 560-640（handlers 等）。

还有 `src/infrastructure/providers/handlers.py:278 detection = self.deps.detector.detect(request)`（detection handler，line 212 except ProviderError）。这是 F4 提到的 handler（把 0 candidates 判 INVALID_INPUT）。读 handlers.py 190-300。

这决定了：非法 env 的 ValueError 是否会让 step 变成未处理异常（可能 crash worker / 变成 INTERNAL 而非 typed step failed）。审查重点 3 问"读取时机（engine 校验后）与 fail-closed 顺序"。需要给出结论。

读 core_service.py 380-430 和 handlers.py 190-300。同时看 detection_sfx.py 的 env 处理（line 115 附近）作为先例对照（它是否 typed）。let me read detection_sfx 100-140 与 530-590（composite）。

并行读取。
dsh: reasoning:
SFX 先例在 `__post_init__` 里 raise ValueError（assembly 阶段解析 env，失败使 assembly 失败）。而 manga 的 env 在 detect 内解析并 raise ValueError。SFX 的 assembly 阶段解析（core_assembly line 851-870）—— 注释说"An unparseable NEWMANGA_SFX_CONF_THRESHOLD fails the assembly"。所以 SFX 先例是 assembly 启动失败（fail-fast at boot），而 manga 是 detect 时失败。

关键：`handle_detect` 中 `detector.detect(request)` 若抛 ValueError（非 ProviderError），`_typed` 包装器只捕 ProviderError，所以 ValueError 会穿透到 ProductionStepExecutor → 被 flatten 成 PROVIDER_FAILED（handlers.py docstring 说 "re-flattens everything else into PROVIDER_FAILED"）。所以不是 crash，而是变成 PROVIDER_FAILED（丢失 fail-fast 的具体信息？detail 可能包含异常文本）。需要确认 executor 行为：`src/application/tasks/service.py:793 except Exception as error: # provider failures become task failures`；`src/infrastructure/pipeline/executor.py:38 except Exception as error`。看 executor.py 30-50 与 service.py 780-800。这决定 ValueError 是否变成 typed step failure（PROVIDER_FAILED）而不是崩溃。若如此，风险级别降为 P3（错误码语义降级为泛化 PROVIDER_FAILED，而非 typed INVALID/INPUT；但 step 仍 fail-closed）。

不过 core.detect 路径（core_service.py:412）没有 try/except ProviderError？它直接 `result = detector.detect(request)` 在 `_handle_detect`（或类似）里，外层 dispatch_request 可能有 catch-all。若 catch-all 返回 internal error envelope —— 对 Tauri UI 来说是一次失败的命令，不是崩溃。看看 dispatch_request 的 catch-all（line 543/582/626 等）。读 core_service.py 540-640。

我认为这足以形成 finding：env 非法时普通页 detect 也 raise 裸 ValueError，非 typed；错误信息虽含 env 名，但走 PROVIDER_FAILED / internal error 通道。任务书要求"tiling 内部失败 typed"。严格说 env 解析失败不是"tiling 内部失败"（是配置错误）。但 AC/纪律"fail-closed 不放宽（tiling 内部失败 typed；普通页零变化）"。可论证 env 非法是配置面，ValueError 与 SFX 先例一致（先例也是 ValueError）。但先例在 assembly（启动时），manga 在请求时。差别：manga 的非法 env 会让**每一页**（含普通页）detect 失败，而 UI 不会在启动时报错——延迟暴露、且是运行期。

这值得一条 P3 finding。

现在检查 qualification 脚本的一个潜在重要问题：`production_detect` 使用 `provider.detect(request)`，其中 provider 是生产构造。但**qualification 脚本没有设置 env**，所以走默认参数 ✓。但 `--weights-dir` default 用 `NEWMANGA_DETECTOR_WEIGHTS` 环境变量 —— 若该 env 指向 doctR .pt 文件（见 manga 的错误提示），脚本会 FATAL。OK。

另一个点：qualification 的 Gate 判定中 `report["gate"]` 的键在 `overall` 计算前只含 5 页，但若某页 sha 不匹配会设 "BLOCKED"，则 overall 为 FAIL ✓（all(v=="PASS") false）。

再检查：`curve_point` 用 `TilingConfig()` 默认，忽略了 env —— 对曲线点这是刻意的（用冻结默认）。但如果在运行 qualification 时设置了 env（例如改 tile_size），生产 detect 会用 env 值而曲线点用默认值 → 不一致。脚本没有清理/校验 tiling env。这是一个小的严谨性缺口（P4）：脚本应显式清除或断言 `NEWMANGA_DETECTOR_TILING_*` 未设置，否则报告可能混合两套参数。JSON 里也没有记录生效的 env 值（只有 "tiling defaults" 的 print 与 tiling_tiles）。handoff 说"tiling 参数=冻结默认（1024/128/0.5/4.0）"，但没有程序化证据（JSON 未落盘解析后的 TilingConfig，只有 tiles 数与 tiling=on/off）。不过可以从 tiling_tiles 反推 tile_size/overlap：K01=70 与 1024/128 一致；tile=690 对照记了 native_scale_tile=690。nms_iou 与 trigger_ratio 无直接落盘（trigger 可从 tiling=on 与页面尺寸推）。可接受，P4 建议落盘 `tiling_config` 解析值。

现在还有一个用户重点：NMS「严格大于删等于保留」与 DIAG 脚本一致性 ✓ 已验证（best_iou > iou_threshold）。

「跨块同目标重复框的残留风险」：生产 NMS 全局 IoU>0.5 删除。残留风险 = 跨块截断的半框（两个半框 IoU < 0.5 → 都保留）。检查 DIAG post_nms 是否有"同一目标的两个部分框"很难。但可以从数据看：DIAG 报告 duplicate_pairs_iou_gt_0_5_total=35，删 33。没有检测"同一目标被切成两半且 IoU<0.5"的机制。这是一个**已知残余风险**，从 K01 的 193 框无法证明不存在。而且现在生产 clip 到 crop 边界会**主动制造**截断框：如果一个框跨过某块的 crop 底边（在重叠带内），生产 clip 后成为"半框"，而相邻块也可能对该目标产出框；如果两个半框 IoU<0.5，NMS 不删 → 残留两个半框。DIAG 的实现在这点上不同：DIAG 不 clip，所以同一目标在两个块中的两个框可能 IoU 更高（因为都是近完整框）→ 更容易被 NMS 去重。

这是 clip 语义差异的一个**功能性**（不只是数值等价）后果：clip 会降低重复框的 IoU，从而削弱 NMS 去重能力。Owner 的等价论证只覆盖了 pad 带（x 方向）和"中心点丢弃 vs clip"，没有覆盖"clip 到块界会截断重叠带内的框、降低 IoU、削弱 NMS"。

等等，仔细想：clip 到 crop 边界，对满块 crop = [origin, origin+1024]。一个真实目标框如果 y 范围跨越 origin+1024（进入下一个块的重叠区），在块 k 中它被 clip 成 y1 = origin+1024；在块 k+1 中（origin' = origin+896），该目标完全在 crop 内（如果目标 y 范围在 [origin+896, origin'+1024]）→ 完整框。那么块 k 的截断框（下半部分被切）与块 k+1 的完整框的 IoU：截断框是完整框的上部分？其实两者都是同一目标的"上部"（块 k 只能看到目标在 y<origin+1024 的部分）。块 k 的框：y0..min(y1, origin+1024)。块 k+1 的框：max(y0, origin+896)..y1 → 完整或下部。如果目标跨越 origin+1024（即目标的 y1 > origin+1024），块 k 的框被裁到 y1'=origin+1024，块 k+1 的框起点在 origin+896（若 y0 < origin+896）。两者 IoU 可能仍 > 0.5（重叠区大），也可能 < 0.5。

关键：目标跨越块底边的情况在 DIAG 数据中，模型在块 k 内检出的框是否能超出 crop（y>1024 in local）？post_process 的 target_sizes = padded size (1024)，输出框通常被 clamp 到 [0,1024]。所以在块 k 内，框不会超过 y=1024（tile-local），即页坐标不超过 origin+1024。所以 DIAG 的框天然就在 crop 范围内（y 方向）——除了前面发现的 0.3px 浮点越界。

同理 x 方向：target=1024（padded 宽），框可到 x=1024（pad 区）。但数据显示 x1 ≤ 674 < 690。

这意味着：**模型输出的框本身已被 post_process clamp 到 padded tile 边界**，所以在 y 方向不会超过 crop（对满块）。那么 clip 到 crop 在 y 方向对满块是 no-op；对尾块（crop_h=309）和 x 方向（crop_w=690 < 1024）才生效。而 x 方向数据证明无框超 690（虽然理论上可能）。因此生产 clip 与 DIAG 在 K01 上数值等价，且"clip 削弱 NMS"的顾虑在 K01 数据上也被事实排除（因为 post_process clamp 使框不超块界）。好，那么这条可以作为"论证需要补强但结论成立"的 finding，而非严重缺陷。

不过要小心：**跨块目标的重复框**在 DIAG 中是如何产生的？DIAG 数据显示 30 对跨块重复（IoU>0.5），说明同一目标在相邻两块都被检出且框坐标接近（因为模型即使在边缘也能输出接近完整的框）。clip 不改变这些框（因为框不超界）。所以生产与 DIAG 的去重行为一致。✓

那么"跨块同目标残留"风险与 DIAG 相同（DIAG 已定性 directional）。OK。

现在还有一个我需要确认的点：生产的 `_tile_inference` 在 pad 后送入 processor，target_sizes = padded (1024,1024)。DIAG 的 run_tile_inference 呢？读 line 226-250 确认（之前 grep 显示 line 243 `target_sizes = torch.tensor(` 在 run_tile_inference 内）。DIAG line 226 `_pad_tile`, line 243 target_sizes。需要确认 DIAG 用的是 padded 尺寸。读 226-255。

还有 DIAG `_text_boxes_from_results` 等价函数 `run_tile_inference` 内部对 label 过滤（line 255: `if int(label) not in (1,2)`），无 clip，无退化检查。生产 filter 多了 clip + 退化 skip + NaN typed。DIAG 的过滤不做 NaN 检查（NaN 会被保留到 box 坐标 → IoU 计算 NaN → 比较 False → 保留）。但不会影响 193 计数（无 NaN）。

OK，现在关于测试的"双向哨兵"足够性：
1. `TestNormalPagePathUnchanged::test_normal_page_never_enters_the_tiled_branch`：monkeypatch `_detect_text_boxes` 记录调用，`_detect_text_boxes_tiled` 禁止；断言 untiled_calls == [(30.0, 42.0)] 且 options tiling=off。这钉住了普通页走原函数 ✓。
2. `TestDetectEndToEndTiled::test_long_strip_page_flows_through_merge_with_tiling_provenance`：禁止 `_detect_text_boxes`（长条页进入 tiled）✓。

但"零变化"的更强保障是 diff 层面的函数体零 diff（无法用测试钉住）。测试覆盖是充分的（对可代码化的部分）。

一个测试缺口：没有断言"普通页的 options 只新增 tiling/text_boxes_pre_merge 而不影响其他键"（比如既有 options 顺序/内容不变）。既有测试 `TestDetectPathHonesty` 已覆盖 options（line 310-360 区域），我应检查它是否断言了 options 的完整内容。读 test 文件 310-380 会更好。让我读测试文件 300-400 与 700-800（哨兵测试）。实际上 diff 已展示新增部分；既有部分我需要看是否对 options 做了 exact 断言。grep "options" in test file.

另外还需要看是否有测试断言 `text_boxes_pre_merge` 在普通页 = 框数（有：line 774-775 `dict(result.options)["text_boxes_pre_merge"] == "1"`）✓。

再一条：`detect()` 中 tiling_tiles 的 options 值是 str。qualification 的 `int(options.get("text_boxes_pre_merge", "-1"))` 处理。OK。

我还想核对 `qualify_tiling.py` 是否在 diff 中完整（441 行）。diff 显示到 579 行结束 qualify 部分 ✓（=`@@ -0,0 +1,441 @@`）。

现在读 DIAG 226-255，并 grep 测试文件 options 断言，读 executor/service 的错误 flatten 行为。

之后我基本可以写报告了。

还有几件事：
- 检查 tests 是否真的"既有测试零修改"：diff 中测试文件只有新增（`@@ -368,6 +368,458 @@`），无 `-` 行删除？在我读的 1001-1464 范围内，所有新增行都是 `+`，且 hunk 头是 `-368,6 +368,458`。6 行 context → 无删除。✓（严格：diff 只显示新增 hunk，没有删除行）。

- 红态 44 failed/29 passed 是会话记录，未落盘 → NOT_VERIFIED（可复算方式：checkout base 只带测试文件？无法，因为测试与实现在同一 commit 29a7f5b5？handoff 说 implement 单 commit 包含实现+测试+qualification。那么"红态"无法通过 git 复现（测试与实现同一 commit），只能手工删实现文件。嗯，红态证据不可复现，这是登记项。不过 pytest 红态本身对 Review 不是关键（可手工复算：用 `git stash` 不行）。作为 NOT_VERIFIED 登记：红态无落盘日志/无法从 commit 复现；绿态可复现。

另外注意：测试文件新增 32 函数/45 条，而红态说"44 failed / 29 passed（73 collected）"。73 - 45 = 28 ≠ 29。嗯，新增 45 条，若全部失败则 45 failed；但红态 44 failed。差 1。Owner 解释"全部失败因 tiling 符号不存在"。但 45 条新增中 44 条失败 → 有 1 条新增测试在红态通过？哪一条？可能是 `test_unrelated_env_has_no_effect`？不，它调 `_tiling_config()`（红态不存在 → AttributeError → fail）。或 parametrize 计数 14 条（矩阵）+ 其他。合计新增条数：

TestTilingConfig: defaults(1) + env_overrides(1) + parametrize(14) + unrelated_env(1) = 17
TestTilingTrigger: 6
TestTilingTiles: 5
TestGreedyNms: 5
TestTiledDetectionPath: test_tiles_are_padded(1) + remapped(1) + cross_tile_dup(1) + distinct(1) + clipped(1) + bubble(1) + nan(1) + threshold_passed(1) = 8
TestDetectEndToEndTiled: 2
TestNormalPagePathUnchanged: 2
合计 17+6+5+5+8+2+2 = 45 ✓。

红态 44 failed → 1 条通过。哪一条可能在红态通过？`test_production_text_filter_runs_per_tile` 用 `_run_tiled` → 调 `_detect_text_boxes_tiled`（不存在）→ fail。`test_threshold_is_passed_through_to_tile_inference` 也调 `_detect_text_boxes_tiled` → fail。`test_unrelated_env_has_no_effect` 调 `_tiling_config` → fail。

Hmm，也许红态时 `_tiling_config` 已存在？不，红态是实现前。也许其中一条测试在红态**error 而非 fail**？pytest 收集/运行中 AttributeError 记为 fail（不是 error，因为发生在测试体内）。73 collected 中 29 passed → 既有测试 28 条？基线测试文件有多少条？既有 collected = 73 - 45 = 28。但红态 29 passed。矛盾 → 说明红态不是"实现前 + 全部新增测试"，或者新增测试 45 条中有 1 条在红态通过，或者既有测试有 29 条而新增 44 条。

也可能 handoff 数字近似/记错。这是一个可核查的矛盾点：44 failed + 29 passed = 73 collected；绿态 73 passed；新增 45 条（我按 diff 逐条数出 45）。则既有 = 73-45 = 28 条。红态 29 passed ≠ 28。差 1。

可能的解释：绿态 73 passed = 既有 28 + 新增 45。红态 44 failed + 29 passed：29 passed 中 28 条既有 + 1 条新增（哪条能在红态通过？）。比如 `test_missing_weights_fails_closed_before_tiling`（新增）——它不调用任何 tiling 符号！它只构造 provider 并断言 `ProviderNotConfigured`。这个测试在红态（实现前）也能通过！✓ 同理 `test_unrelated_env_has_no_effect` 不行（调 _tiling_config）。

对，`test_missing_weights_fails_closed_before_tiling` 在红态通过。所以 44 failed / 29 passed 自洽：73 collected = 28 既有 + 45 新增；其中 1 条新增（missing_weights）通过 + 28 既有通过 = 29 passed；44 新增失败。✓ 完全自洽。好，红绿数字自洽（好证据，说明 Owner 的数字是真的）。

我逐条数出 45 也验证了 handoff 声称的 45 条。很好。

现在继续读 DIAG run_tile_inference 与测试 options 断言。

再确认一个点：`TestTiledDetectionPath` 里 fixture 用 tile 100 / overlap 20，page 50x400。但 `_pad_tile` 会把 crop pad 到 100x100，`_text_boxes_from_results(scores, labels, boxes, crop_w, crop_h)` 用 crop_w=50, crop_h=100（第一块）。测试 `test_tile_boxes_are_clipped_to_the_tile_bounds` 用 local box y1=130 → clip 到 100 ✓（crop_h=100）。✓

好，读剩余内容。
dsh: reasoning:
确认：非法 env → `_tiling_config()` raise ValueError → `handle_detect` 里 `detector.detect` 抛 → `_typed` 只捕 ProviderError → 穿透 → ProductionStepExecutor `except Exception` → StepExecutionError("PROVIDER_FAILED", str(error))。所以是 fail-closed，但错误码被降级为 PROVIDER_FAILED（而不是更有诊断性的 typed code），且**普通页也一起失败**。这是 P3 finding（不阻塞，但要求登记）。

core.detect 路径（core_service.py:412）：需要看 dispatch_request 的 catch-all 是否把 ValueError 变成 internal error envelope。line 540-640 有 543/582/626 的 except。读一下 core_service.py 540-640 以确认 UI 面影响（Tauri core.detect 用于 UI 探测）。这对"发布形态"评估有意义。

另外我注意到一个更实质的问题：**`_tiling_config()` 在每次 detect 调用都从 env 读**，若 env 在运行中被外部修改（不太可能）会不一致。测试 monkeypatch env。可接受。

另外：`options` 新增 `text_boxes_pre_merge` 的值是 `len(boxes)`（NMS 后、merge 前）。命名恰当 ✓。

现在再考虑一个重要问题：**"普通页零变化"是否包括 options 变化对下游 Tauri/DB 的影响**。options 被写入 provenance → 存 DB regions 的 provenance 字段？`detection.provenance()` 在 handlers 中作为 provenance 传给 region_creator。新增键只是多两个 key，非破坏。但 M2 的 acceptance 快照可能记录 provenance。既有测试已过（575 passed）。app 层（Tauri sidecar 断言 core.detect 1.0→1.1）不受影响。OK，风险低，登记为"options 新增键的消费面已由 575 绿证明无破坏"。

现在看 core_service 的 catch-all（对 UI 的影响）。

再检查一个我漏掉的：M2-SFX-PROD-1 的 composite 包装（detection_sfx.py line 544-580：composite primary.detect + sfx.detect，捕获 ProviderError 降级）。如果 primary（manga）对长条漫抛 ValueError（非法 env），composite 只捕获 ProviderError → ValueError 穿透 → 同 PROVIDER_FAILED。但正常情况（env 合法）长条漫走 tiling 会返回 180 region，composite 正常。复合包装的语义增强不受影响 ✓（任务书要求核对）。

但等等——composite 包装（`SfxCompositeDetectionProvider`?）在 primary 检测基础上叠加 sfx。长条漫 20s + sfx 推理 → 总时间更长。发布形态影响：两模型叠加后长条漫页耗时可能 > 20s + sfx 时间。值得登记。

让我读 detection_sfx.py 540-609 确认 composite 的行为与潜在耗时。

然后我可以开始写报告了。还需要：
- 检查 `doc/STATUS.md` 是否零 diff：diff 中无 STATUS ✓。
- 检查是否有二进制：grep 已显示无 "Binary files"/"GIT binary patch" ✓。

最后确认一下 experiments/ 与 verification/ 是否允许（任务书允许面包含 experiments/M2-DETECT-WEBTOON-TILING/** 和 verification/M2-DETECT-WEBTOON-TILING/**）✓。

再检查 Task frontmatter 是否被正确回填（AC 表）：Task 文件中没有 AC 表（原文档只有"交付（AC）"列表 + 交付记录）。允许。

一个范围纪律问题：Task 文件 frontmatter `status: implemented`（改动）——允许（Task 回填）。`base_commit: f534c3e7` 保持（不改为 f99a6c55）但加了 delivery_head/tip_note 说明。可接受。

现在读 core_service 540-640 与 detection_sfx 540-609。
dsh: reasoning:
确认：core.detect 面上，非 typed 异常 → `E_UNKNOWN` / "Detection failed"（丢失具体信息）。所以非法 env 时 UI 探针会看到 E_UNKNOWN，而不是明确的配置错误码。P3 级别（不阻塞）。

现在关于发布形态：composite（M2-SFX-PROD-1）会在 primary 之上再跑 sfx。长条漫 primary 20s + sfx（ONNX yolo11s-seg 1024 imgsz，CPU？）。这是 UI/进度面影响：一次 detect step 可能在长条漫上耗时 >20s（未含 sfx）。Owner 的登记只写"长条页最坏 ≈20s（K01，CPU）"，未提 composite 叠加与 IPC 超时/进度。这是用户重点审查项 6 要求的。作为 P2/P3 finding。

我还应该确认 composite 是否是生产装配的默认路径（M2-SFX-PROD-1 已释放/集成？）。任务说"M2-SFX-PROD-1 的 composite 包装不受影响（primary 检测语义增强）"。若 composite 已在生产装配中，长条漫总耗时 = manga tiling + sfx。sfx 的 detect 对长条漫页也会做自己的 letterbox 处理（SFX_LETTERBOX_GRAY=114，imgsz 1024）。值得登记为发布形态输入（P3）。

现在还有一件事：qualification 只测了 primary（MangaDetectionProvider），没有测 composite 路径下的长条漫页。可登记为"集成方闭合清单"项。

让我现在检查 Task 允许面的"禁改面零 diff"——我只有 review-input.diff，它不含禁改面文件 ✓。但"worktree 的 git status 是否干净"无法验证 → NOT_VERIFIED。

再想想重点审查项 1 的"逐字节零 diff 的核实方式"：Owner 的方式=git diff 人工阅读+测试哨兵+BJ02 qualification 对照。作为 DSH 我核对的正是 review-input.diff 中 `_detect_text_boxes` 的 hunk：函数体全是 context 行，仅 docstring 改动。✓ 但 diff 是 f99a6c55..36b61c3a 的整体 diff，能否保证 `_detect_text_boxes` 函数体没有在 diff 之外被改？diff 就是全部变更，所以能。

但注意：diff 中 `_detect_text_boxes` 的 hunk 是 `@@ -328,7 +538,12 @@`，包含 `-    """Run one page through the pinned model; return (text_boxes, n_bubble).` 和 +5 行 docstring。上下文 7 行。函数体（torch 调用等）不在 hunk 内 → 未变 ✓。

还有一点：`_detect_text_boxes` 的 docstring 说 "byte-identical to the pre-tiling implementation" —— 但 docstring 本身变了，严格说函数对象不是 byte-identical（源码文本）。措辞小瑕疵，P4。

现在关于 `detect()` 的普通页分支：原来直接调 `_detect_text_boxes`，现在多了一个 `_tiling_config()` 调用（在分支外）。这就是"普通页零变化"唯一的语义差异（env 非法时）。已捕获。

另一个细节：`_tiling_config()` 在 `_frame_pixels` 之后调用。若请求的 image_bytes 长度错误 → `_validate_request` 先抛 typed ProviderInputError（不受影响）✓。

还有：`tiling_options` 在普通页是 `(("tiling","off"),)`，未包含 `tiling_tiles`。qualification 的 `options.get("tiling_tiles")` → None ✓。

测试：`test_normal_page_records_tiling_off` 检查 tiling=off + pre_merge=1 ✓。

现在关于 NMS 的一个潜在正确性问题：`_greedy_nms` 的 `sorted(boxes, key=lambda b: b[4], reverse=True)` —— 如果 conf 相同（例如完全相同的重复框），稳定排序保持原顺序（tile 顺序）。DIAG order 同样。✓

还有 `_iou` 的 NaN 风险：filter 已保证 finite ✓。

现在关于"env fail-fast 非法值矩阵"：
- trigger_ratio: "0" → not > 0 → ValueError ✓；"-4" ✓；"abc" ✓；但没有测 `inf`/`nan`！`float("nan")` → `not nan > 0.0` → True → raise ✓（NaN 比较 False → not False = True）。`float("inf")` → inf > 0 → 通过！trigger_ratio=inf 意味着永不触发 tiling（普通页路径）——不危险。但 `float("nan")` 被拒绝 ✓。
- tile_size: "10.5" → int("10.5") ValueError → raise ✓
- overlap: 负、≥tile、abc ✓；但没有测 `overlap` 在 tile_size 自定义下的联合校验（例如 TILE_SIZE=512 + OVERLAP=128 默认 → 512>128 OK；TILE_SIZE=64 + 默认 overlap 128 → 报错）。测试矩阵有 check：`("...TILE_SIZE", "0"), ("-1024"), ("10.5"), ("abc")`，overlap 的 "1024"（=默认 tile）→ ≥ tile ✓。但**没有**测 "自定义小 tile + 默认 overlap" 的联合校验路径（handoff 声称"自定义小 tile 必须自带 overlap"，即 TILE_SIZE=64 且无 OVERLAP → overlap 默认 128 ≥ 64 → ValueError，报错信息 names both variables）。这个联合路径未被测试覆盖！handoff 说"env fail-fast 矩阵（14 条 parametrize：非数字/零/负/超域/overlap≥tile）"覆盖了 overlap≥tile（用 OVERLAP=1024 显式设置），但没覆盖"tile 变小导致默认 overlap 越界"。这是测试缺口，P3/P4：联合校验只在显式 OVERLAP 场景测过，隐式路径（小 tile + 默认 overlap）无测试。实际代码确实会报错（`if not 0 <= overlap < tile_size` 对默认 overlap=128, tile=64 → raise）✓ 逻辑正确，只是缺测试。

- nms_iou: 0.0/-0.1/1.0/abc ✓；但 "nan" 未测：`float("nan")` → `not 0.0 < nan < 1.0` → not False = True → raise ✓（逻辑正确）。
- trigger_ratio 无 range 上界（inf 允许）——可登记为 P4。

- 空字符串 env（`raw.strip()` 为空）→ 视为未设置（默认）。例如 `NEWMANGA_DETECTOR_TILING_TILE_SIZE=""` → 用默认。这是"silent default"的边界：Owner 声称"present-but-illegal value is a fail-fast ValueError, never a silent default"，但 present-and-empty（或纯空白）是 silent default。这是一个**与文档声明不一致**的边界（P3）：`raw and raw.strip()` 使空/空白字符串静默回落默认值，与"never a silent default"的 docstring/注释声明相矛盾。虽然实际影响小（空 env 罕见），但这是可核查的语义缺口，值得一条 finding。

好，这条我很有信心：`os.environ.get(X)` 返回 "" 时 `if raw and raw.strip()` 为 False → 静默用默认。测试矩阵没有 empty-string 用例。

另外：`overlap` 的校验当 `raw` 为空时用默认 128 并与 tile_size 比较 ✓。

现在再看"读取时机"：`_tiling_config()` 在 engine 构建之后。若 env 非法且权重缺失 → 先 PROVIDER_NOT_CONFIGURED（typed），env 非法不被暴露。fail-closed 顺序"先 engine 后配置"意味着配置错误被 engine 错误遮蔽。这是取舍，handoff 已登记（"读取时机=detect 内（engine 校验之后）"）。测试 `test_missing_weights_fails_closed_before_tiling` 钉住了该顺序 ✓。合理。

另一个角度：为什么不把 `_tiling_config()` 放在 detect 最开始（在 engine 之前）？因为若放在最前，非法 env 会让"缺权重"场景报 ValueError 而非 typed PROVIDER_NOT_CONFIGURED，破坏既有 fail-closed 语义。当前顺序更保既有语义。可接受 ✓。

好，接下来"红绿"证据的 NOT_VERIFIED：红态无落盘日志。绿态 575 passed 无落盘日志。我无法复现（无 shell）。集成方需重跑。

再检查 `verification/M2-DETECT-WEBTOON-TILING/qualification-results.json` 中 K01 的 `bubble_class_dropped` = 168（跨 70 块累计）。DIAG 未记录 bubble 计数。无法交叉核对，但合理。

还有 `conf_min` 在 0.5 点未落盘（只有 confidences 数组，可算 min = 0.5013 从数组看）。JSON 里 K01 confidences 含 0.501322865486145 ✓（>0.5，符合阈值）。

现在关于"region 层级计量与框层级并报"：JSON 中 `region_count` + `text_boxes_pre_merge` ✓。

"GATE PASS 判定是否被脚本程序化"：✓ `report["gate"][case_id] = "PASS" if region_count > 0 else "FAIL"`，`overall` 由 all() 得出，exit code 0/3。但 controls 不参与 overall（P4 观察）。

最后，K01 的 `matches_diag_probe` 是硬编码 `diag_reference_region_count = 5`（脚本内常量），不是从 DIAG 的 probe-results.json 读取。也就是说 BJ02 对照的"逐值一致"是脚本作者写死的期望值 5，而非程序化对比 DIAG JSON。虽然 5 与 DIAG 证据一致（我核对了 diagnosis.md 的 §2.2 BJ02 region 5），但"程序化"程度较低，且若 DIAG JSON 变化不会自动发现。P4：建议从 probe-results.json 读取而非硬编码。

另外 K19 也硬编码期望 0。

还有一点（重要，qualification 方法论）：`curve_point` 的 0.4 点是在**同一进程内**对同一页再次运行 tiled 推理，但 `production_detect` 的 0.5 点已经跑过；两次推理之间没有 seed/确定性声明。DIAG 说 193 两次复现。qualification 各跑 1 次。报告已登记"运行次数：各 1 次（非 determinism gate）" ✓。

现在还有"690 对照"的一个方法论问题：690 对照用 tile 690、overlap 128（step 562）。报告说"水平重采样 ≈0.93×≈1.0×"—— 等等：tile 690 被 processor 缩到 640 → 640/690 = 0.928 ✓。而 1024 tile → 640/1024 = 0.625。所以 690 对照的重采样率是 0.93（更接近原生），但**垂直方向**：690 tile 高 690 → 640 → 0.928 ✓。所以 690 对照确实是"≈1.0× 重采样"。但 report §3 写"水平重采样 ≈0.93×≈1.0×"，表述略含糊（垂直同样 0.93）。且"tile 690（=K01 原生宽）"—— K01 宽 690 ✓。结论"+2.6%"（198 vs 193 框；177 vs 180 region）✓ 数值核对：198/193 = 1.0259 → +2.6% ✓。region 177 vs 180 = -1.7%（报告只说框级 +2.6%）。OK。

还有 K01 native 对照 `n_tiles=111` 是脚本用 `_tiling_tiles` 计算的 ✓，但 `curve_point` 里用 `TilingConfig(tile_size=690, overlap=128)` → 与 n_tiles 计算一致 ✓。

好，最后检查一下 experiments/M2-DETECT-WEBTOON-TILING/qualify_tiling.py 的实际文件（worktree）与 diff 一致（diff 已展示完整 441 行）✓。我读的 diff 覆盖 132-578 行 = 441 行 + diff 头。✓

还有一个隐藏风险：qualify_tiling.py 直接 import 私有函数 `_detect_text_boxes_tiled`、`_tiling_tiles` 并调用 `provider._engine_or_raise()`（私有）。这是实验脚本，任务书允许 experiments/**。可接受（登记为"实验脚本依赖私有符号，若 provider 内部重构则 qualification 脚本需同步"——P4）。

另外：`_engine_or_raise()` 返回 (model, processor)，然后脚本用 `model, processor` 调 `_detect_text_boxes_tiled`。这暴露了 provider 内部引擎，但仅实验脚本。OK。

现在还有一个我需要确认的：qualification 里 `_detect_text_boxes_tiled(..., config, threshold=threshold)` 调用的 user 语义 —— 生产 detect 里用默认 threshold。✓

好了，现在还有一个用户重点审查项："跨块同目标重复框的残留风险"。我可以用 DIAG 数据做一个粗略检查：post_nms 中是否存在"同一 tile 内两个框 IoU 恰好 ≤0.5 但明显是同一目标被截断"的情况？DIAG 的 `duplicate_pairs_same_tile=5`（同块 IoU>0.5 对），pairs_outside=3。这些对在 NMS 后应该只留一个（因为 IoU>0.5 会被删；除非两个都是 keeper —— 但 NMS 会删掉后者）。等等：`duplicate_pairs_iou_gt_0_5_total=35` 是 pre-NMS 的对数；删了 33 个框。若有 35 对但只删 33 个框，可能残留一些 IoU>0.5 的对？不可能——NMS 保证 kept 集合两两 IoU ≤ 0.5（生产 _greedy_nms 的 any 检查）。DIAG 的 greedy_nms 也是 best_iou > threshold 才删，也保证 kept 两两 IoU ≤ 0.5。35 对 / 33 删框：一个删框可能与多个 keeper 成对（例如删框 A 与 keeper B、C 都 IoU>0.5）。所以 35 对 ≠ 35 删。✓ 自洽。

那么"同目标被切成两半且 IoU≤0.5"的残留无法从这些统计检测到。登记为"无残余量测"即可。

我还想验证一下"生产 193 = DIAG 193"是否真的来自同一路径（qualification 的 production detect 用的是 `_detect_text_boxes_tiled` 默认 threshold=MANGA_CONF_THRESHOLD=0.5，与 DIAG 相同）。✓ 这是很强的经验证据。

不过有个隐患：DIAG 用 tile 1024 + overlap 128 + x 方向 pad 到 1024；生产同。DIAG 的过滤无 clip；生产 clip。数据证明无差异。✓

现在，我还应该确认 DIAG 的 tile 循环对 x 方向：DIAG 只做 1D 垂直切块（`crop = rgb[y:y1]` 保留全宽 690），然后 pad 到 1024x1024。生产 `_tiling_tiles` 是 2D 网格：x origins(690) = [0] → x 方向单块，同一行。所以两者切块方式一致 ✓（对 K01 宽 690 < 1024）。但对**宽页**（width > 1024，例如 webtoon 更宽的条漫），生产会做 2D 网格，而 DIAG 未验证。这是"未验证面"：2D 网格路径（width > tile_size）没有真实数据验证（只有合成的 `test_wide_page_cuts_a_two_dimensional_grid` 几何测试）。触发条件 h/w > 4.0 的页通常窄高，但一个 2000×10000 的页（h/w=5）会触发且走 2D 网格 → 未验证。P3 finding：2D 路径仅合成几何测试，无真实页验证；且 x 方向切块会引入水平重叠带，缺少像 y 方向那样的经验证据。

这个挺有价值。可提为 R 项。

另外，`overlap_band_stats` 的 DIAG 分析只覆盖 y 方向带（垂直）。若走 2D，x 方向带同样需要 NMS 去重（生产 NMS 是 2D 全局的，能处理）✓ 逻辑上没问题。

还有：`_tiling_tiles` 对**超高窄页**的块数线性增长 → 内存/时间。K01 70 块 20s。若页高 200000（webtoon 可能更长），块数 ~224 → 60s+。无块数上限/降级策略。P3 登记（发布形态）。

再看一个边界：`h/w > 4.0` 且 width 很大（如 5000×25000, h/w=5）→ 触发；tile 1024 → x 5 列 × y 28 行 = 140 块。OK。

另一件事：**触发阈值 4.0 与"普通页 h/w ≤ 1.41"**，但真实漫画里双页跨页（2-up）可能 h/w 高？例如竖排双页 1000×4000（h/w=4）→ 不触发（严格大于）。普通漫画单页 h/w ~1.4。日漫长条（如某些 webtoon 日漫）？登记为已论证（~20× 余量）✓。

还有：**旋转/横向长图**（宽 > 高）不会触发 ✓。

现在我觉得证据充分，可以写报告了。但还有几个点需要核实：

1. `tests` 文件 828 行附近 `_provider()`、`TestAssemblyBackendSelection` 等既有测试 —— 与新增部分无冲突。diff 显示新增块插入在 identity 注释之前，既有 identity 注释区（842+）保留 ✓（diff 末尾显示 `# identity` context 行重复出现，因为插在了它前面）。

2. 需要确认 diff 中测试新增部分是否包含对 `_detect_text_boxes` 的既有测试破坏（例如既有测试计数从 28 → 28）✓。

3. `doc/tasks/M2-DETECT-WEBTOON-TILING.md` 的 frontmatter 新增 `delivery_head` 和 `tip_note`。Task 模板是否允许额外 frontmatter 键？大概可以。P4 无需。

4. 无二进制 ✓；无 `doc/STATUS.md` 改动 ✓（SUMMARY 要求 STATUS 零 diff，任务书禁改面）✓。

现在整理 findings 列表（R1...），带 P0-P4 与文件:行。

Findings 草稿：

**R1（P3）env 非法值导致的 ValueError 是非 typed 异常，且打破"普通页零变化"**
- 文件：`src/infrastructure/providers/detection_manga.py:326`（detect 内 `tiling_config = _tiling_config()`，位于 if 分支之外）；`detection_manga.py:189-260`（raise ValueError）；调用链 `src/infrastructure/providers/handlers.py:278` + `:212`（`_typed` 只捕 ProviderError）→ `src/infrastructure/pipeline/executor.py:38-39`（flatten 成 PROVIDER_FAILED）；`src/bootstrap/core_service.py:626-641`（core.detect → E_UNKNOWN "Detection failed"）。
- 后果：(a) 任何非法 `NEWMANGA_DETECTOR_TILING_*` 会让**所有**页面（含不触发的普通页）detect 失败——这不满足"普通页走原路径零行为变化"的严格读法（配置错误下普通页行为变化）；(b) 错误码降级：pipeline 侧变 PROVIDER_FAILED、core.detect 侧变 E_UNKNOWN，丢失 env 名这一唯一诊断信息（虽然 stderr 有 `str(error)`）。任务书纪律写"tiling 内部失败 typed"。
- 建议：将 `_tiling_config()` 的失败包装为 `ProviderInputError`（或新建 typed config 错误），或在 detect() 入口先做一次配置校验使错误 typed；并补一条测试 `detect()` 在非法 env 下抛 typed 错误。
- 缓解：SFX 先例（`detection_sfx.py:158-165`）也用 ValueError，但其调用点在 assembly 启动时，暴露更早。

嗯，注意：SFX 先例的 ValueError 在 `__post_init__`，而 assembly 在构建 provider 时解析 env → app 启动失败。manga 的 env 在 detect 时才读。所以 manga 是运行期延迟失败。合理。

**R2（P3）"pad 带零检出 ⇒ 两种处理等价"的论证不完整（clip vs 中心点丢弃）**
- 文件：`detection_manga.py:718-720`（以 crop_w/crop_h 复用共享纯过滤做块界 clip）vs `experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py:401-407`（仅 `center_x > width` 丢弃，y 方向无 pad 丢弃、无 clip）。
- 我核对了 DIAG 落盘数据（`verification/M2-DETECT-WEBTOON-DIAG/probe-results.json` 的 `pre_nms_boxes` 1188-1415 / `post_nms_boxes` 1416-1610）：全部框 `x1 ≤ 674.4 < 690`、`y1 ≤ 62055.8 < 62133`（页高），唯一"越界"是 tile 68 的 y1=61952.3 超其 crop 边界 0.3px（浮点舍入）。因此 K01 上两法**数值等价**成立，但成立理由是"没有任何框跨出 crop 边界"，比 Owner 记录的"pad 带零检出"更强（后者只覆盖"中心在 pad 带"，不覆盖"框跨越 crop 边界"）。
- 一般情形不等价：DIAG 保留跨 pad/跨块边界的原始框，生产 clip 到块界并丢弃退化框（`detection_manga.py:784-785`）；clip 会降低跨块重复框的 IoU，理论上削弱 NMS 去重。
- 建议：把等价论证补为"无框跨出 crop 边界"（可由 DIAG JSON 复算），并补一条合成单测固定"跨块边界框"的生产语义（现测试只覆盖跨 crop 底边 130→100 的 clip，即 `test_tile_boxes_are_clipped_to_the_tile_bounds`）。
- 严重度：P3（K01 证据成立，属论证/文档精度）。

**R3（P3）env 空字符串静默回落默认，与"never a silent default"声明相矛盾**
- `detection_manga.py:200,214,228,243`（`if raw and raw.strip():`）；docstring 171-172 与 189-197 声称 present-but-illegal 才 fail-fast，但 `NEWMANGA_DETECTOR_TILING_TILE_SIZE=""` / `"   "` 静默用默认。
- 测试矩阵（test_detection_manga.py:435-441 区域 parametrize 14 条）无空串用例。
- 建议：要么把空串也视为非法（fail-fast），要么在 docstring/交接中把语义写准（"absent or blank"）。P3/P4。

我把这条定为 P3（对"fail-fast 完备性"的直接影响）。

**R4（P3）fail-fast 矩阵缺"tile 变小 + 默认 overlap"联合路径与 nan/inf 用例**
- `detection_manga.py:235-239` 是"对生效 tile_size 联合校验"的关键分支；测试 14 条中只有显式 `OVERLAP=1024` 一条命中"overlap ≥ tile"，没有"tile_size=64 + overlap 未设置（默认 128）"这条实际最可能被运维踩到的路径。
- 逻辑上正确（已读代码），但无回归保护。
- 另：`TRIGGER_RATIO=inf` 通过校验（永不触发），`NMS_IOU=nan` 被拒（逻辑正确）。P4。

**R5（P3）qualification 的 2D（横向）切块路径无真实页验证**
- `_tiling_tiles`（271-296）是 2D 网格；DIAG 实验只做垂直切块（`diagnose_webtoon_detect.py:395-425`，`crop = rgb[y:y1]` 全宽）；qualification 的 5 张 Gate 页全部 width < 1024（600/690）。真实数据只覆盖 x 方向单块。
- 触发条件 `h/w > 4.0` 的页通常窄，但 2000×12000（h/w=6）这类"宽长条"会落入 2D 路径且未验证（重叠带在 x 方向、块数倍增）。
- 建议：登记为未验证面（或补一张 width > 1024 的页；TA3-B 清单里是否有？未核）。P3。

**R6（P3）发布形态：20.1s/页的性能影响登记未覆盖 UI/IPC/超时/进度与 composite 叠加**
- 登记见于 handoff §风险与遗留（78 行）与 Task 交付记录，仅数值+“发布形态输入”。
- 缺口：(a) `src/infrastructure/providers/detection_sfx.py:569-609` 的 composite 会在 primary 之上再跑一次 sfx 推理，长条页总耗时 = tiling 20s + sfx（未测）；(b) core.detect 是同步请求-响应（`core_service.py:563-644`），20s 阻塞 worker，Tauri 侧超时/取消/进度未评估；(c) 无块数上限（页高线性，K08 51971→58 块 16.3s；更长的条漫按线性外推 60s+）。
- 建议：把这三项写进集成方闭合清单（超时配置、进度/取消、块数上限或降采样策略）。P3。

**R7（P4）qualification 的 gate/controls 判定与硬编码参照**
- `experiments/M2-DETECT-WEBTOON-TILING/qualify_tiling.py`：`overall` 只聚合 5 张 Gate 页（`report["gate"]` 在 `overall` 计算时尚未含 controls，548-561 行）；K19/BJ02 控制项只记录不参与 PASS/退出码。
- 528 行 `diag_reference_region_count = 5` 硬编码，而非读 `probe-results.json`；K19 期望 0 同理。
- 脚本未清除/断言 `NEWMANGA_DETECTOR_TILING_*`，也未把解析后的 `TilingConfig` 落盘（JSON 只有 `tiling_tiles`/`tiling=on`；`native_scale_tile` 单独记录）——若运行时 env 被污染，生产点与曲线点会用不同参数（`curve_point` 用 `TilingConfig()` 默认，296-304/461 行）且报告无法察觉。
- 建议：JSON 落盘 resolved TilingConfig；从 DIAG JSON 读参照；controls 纳入 overall 或明确标注"非 Gate"。P4。

**R8（P4）"函数体逐字节未动"的表述与 docstring 修改**
- `detection_manga.py:541-554`：`_detect_text_boxes` 的 docstring 由 1 行变 5 行（diff `@@ -328,7 +538,12 @@`），函数体（555-582）为 context 未变。handoff/Task 用"函数本体逐字节未动"表述；review 指引自认"仅 docstring 措辞更新"。行为零变化成立（docstring 不影响执行），表述宜精确为"函数体（可执行语句）零 diff，docstring 更新"。
- 同时该 docstring 自称 "kept byte-identical"，字面上不成立。P4。

**R9（P4）红态证据不可复现 + 新增测试符号耦合私有 API**
- implement 单 commit 同时落实现与测试，故"红态 44 failed/29 passed"无法从 git 直接复现（无落盘日志）。我按 diff 逐条数出新增 45 条（与 handoff 一致），并验算 44+29=73=28(既有)+45(新增)、其中 `test_missing_weights_fails_closed_before_tiling` 在无 tiling 符号时也能通过 → 数字自洽。建议在 qualification/CI 之外保留红态日志，或说明复现方式。
- qualification 脚本 import 私有符号 `_detect_text_boxes_tiled`/`_tiling_tiles`/`provider._engine_or_raise()`（qualify_tiling.py:296, 374, 480），provider 内部重构会静默打断复现链。P4。

还有没有 P1/P2？让我想想有没有更严重的问题。

潜在的 **P2**：`_tiling_config()` 是普通页路径新增的调用，会读 env；这是"零变化"的唯一破口。我把它定为 P3 还是 P2？用户特别要求核实"普通页零变化主张"。严格来说：在**合法环境**（默认 env）下普通页零变化（函数体未动+options 新增非破坏键）；在**非法 env** 下普通页从可用变为失败。这是配置错误场景，且 fail-fast 是设计意图。我认为 P3 合理（不阻塞合并），但要在 Verdict 里明确"零变化的成立条件"。

另一个潜在 P2：**未对 `tiling_tiles` options 的重复计算**（detect 里调 `_tiling_tiles` 两次：一次在 `_detect_text_boxes_tiled` 内、一次为计数）。开销可忽略（70 个 tuple）。P4 甚至不提。

再考虑一个可能的 P2：**`_pad_tile` 在 crop 大于 tile_size 时会抛 ValueError/广播错误**。`_tiling_tiles` 保证 x1-x0 ≤ tile_size（min(x0+tile, width) 且 step ≤ tile）。若 width < x0+... 不成立。crop 尺寸 ≤ tile_size 恒成立 ✓（因为 x1 = min(x0+tile, width) 且 x0 < width，所以 crop_w = min(tile, width-x0) ≤ tile ✓）。所以 `tile[:crop_h, :crop_w] = crop` 总成立 ✓。

另一个：**重叠 ≥ tile_size 被拒** ✓；overlap = 0 允许（tile_size-0 = tile → 无重叠网格）✓。

**内存**：`page_boxes` 对 K01 226 个框 ✓。

**`n_bubble` 语义**：跨块累计 bubble 计数 → options `bubble_class_dropped` 值比整页路径大得多（K01=168）。这是语义变化：这个 options 值此前代表"整页推理中 bubble 类框数"，现在代表"所有块累计"。任何依赖该值做校准的下游会受影响。登记为 P3/P4：`bubble_class_dropped` 在 tiling 页是跨块累计值，与整页路径不可比（供审计可以，但应说明）。测试 `test_bubble_count_accumulates_across_tiles` 钉住了行为 ✓。我认为 P4（审计字段，无功能消费者）。

嗯，还有一个可能更重要的：**`text_boxes_pre_merge` 与 `bubble_class_dropped` 在普通页的语义不变** ✓。

**触发判定的分母**：`height / max(width, 1.0)` — width 来自 rgb.shape，实际不可能为 0（validate_request 已拒）。✓

**region 数 180 vs DIAG 合并前 193 的层级** ✓ 两者并报。

现在，qualification 证据能否从静态上再验证一些数字？例如 K02 region 93 与框 97：合并率 4.1% ✓ 在 1.6-7.2% 范围。

K01: 193→180 = 6.7% ✓。

阈值曲线：0.4 conf_min 值都在 0.40-0.45 ✓ 合理。

690 对照 198 框/177 region（合并率 10.6%——比 1024 的 6.7% 高；report 未提）。OK。

还有一个我该验证的：K01 的 `tiling_tiles="70"` 与 `text_boxes_pre_merge=193` 与 DIAG 完全一致 —— 这是最强证据。✓

**Gate 五页 region>0** ✓ 全部 >0。

现在写 Verdict：REVIEW PASS（有条件）？Review 结论通常是 PASS / PASS with findings / REQUEST CHANGES。没有 P0/P1/P2 阻塞项，7 项 P3/P4。我倾向 **PASS（无 P0/P1；7 条 P3/P4 建议项，均为文档/测试/发布形态登记强化，可在集成时由集成方一次性闭合或作为 follow-up）**。

但等等——R1（普通页在非法 env 下的行为变化 + 非 typed 错误）是否需要返修？任务书要求"tiling 内部失败 typed"。严格读，env 解析失败不属于"tiling 内部失败"（它发生在触发判定之前）。而"普通页零变化"在合法配置下成立。DSH 的职责是给出判断。我倾向 P3 不阻塞，但要求集成方在合并前记录该行为（或 Owner 在下一轮把 ValueError 包装为 typed）。

用户的输出格式要求含"集成方闭合清单"和"NOT_VERIFIED"。我会把 R1/R6 中需要集成方决策/动作的项列入闭合清单。

我需要给出文件:行 精确定位。让我确认几个行号：
- detection_manga.py:326 `tiling_config = _tiling_config()` ✓（我读的 worktree 文件行号 326）
- detection_manga.py:200/214/228/243 空串判断 ✓
- detection_manga.py:235-239 overlap 联合校验 ✓
- detection_manga.py:718-720 clip 调用 ✓
- detection_manga.py:784-785 退化跳过 ✓
- detection_manga.py:541-554 docstring ✓；555-582 函数体 ✓
- detection_manga.py:268 `_tiling_triggered` ✓
- detection_manga.py:271-296 `_tiling_tiles` ✓
- detection_manga.py:660-675 `_greedy_nms` ✓
- diagnose_webtoon_detect.py:401-407 pad 丢弃 ✓；285-298 NMS ✓；395-425 tile 循环 ✓
- probe-results.json:1188-1415 pre_nms_boxes、1416-1610 post_nms_boxes ✓（greg 显示 post 从 1416 开始，到 1610 附近；nms_removed 从 1611）
- qualify_tiling.py:296-304（curve_point 调私有函数）、374（_engine_or_raise）、480（_tiling_tiles）、528（硬编码 5）、548-561（gate/controls）
- handlers.py:212（_typed 只捕 ProviderError）、278（detect 调用）
- executor.py:38-39
- core_service.py:626-641
- detection_sfx.py:569-609 composite

测试文件行号（worktree）：TestTilingConfig 387；parametrize 用例在 435-441？我需要精确行号。grep 显示 `_clean_tiling_env` 在 382，`class TestTilingConfig` 387，`class TestTilingTrigger` 444，`class TestTilingTiles` 474，`class TestGreedyNms` 519，`_stub_tile_inference` 555，`class TestTiledDetectionPath` 573，`class TestDetectEndToEndTiled` 721，`class TestNormalPagePathUnchanged` 779。

parametrize 的具体行号我可以用 diff 推算：diff 中 1101 行附近是 test_zero_width；diff 行号不好映射。让我 grep 一下 `test_illegal_values_fail_fast` 与 `test_missing_weights_fails_closed_before_tiling` 的行号，以及 `test_tile_boxes_are_clipped_to_the_tile_bounds`。顺便 grep `NEWMANGA_DETECTOR_TILING_TILE_SIZE"` 出现位置（参数化列表）。

一次 grep：`def test_illegal_values_fail_fast|def test_missing_weights_fails_closed_before_tiling|def test_tile_boxes_are_clipped_to_the_tile_bounds|def test_tiles_are_padded_to_the_square_tile_size|def test_normal_page_never_enters_the_tiled_branch|def test_long_strip_page_flows_through_merge`。

另外确认 tests 里是否有测试覆盖"普通页走原路径时 options 只增键"——无。

另外，为了核对"既有测试零修改"，可以确认 diff 中测试部分没有删除行：我已经看到 hunk 只有 `+` 行和 context。用一个 grep 检查测试 diff 区域是否有 `^-` 行：grep `^-[^-]` in diff 且行号 > 1001。可以 grep `^-[^-]` 在 diff 中看所有删除行：应该只有 docstring 那一行、以及 task frontmatter status 行、base_commit 等。让我 grep 确认删除行清单。

并行执行两个 grep。
dsh: reasoning:
删除行确认：只有 5 处删除 —— Task status、detect() 中的 4 行（替换为分支编排）、以及 `_detect_text_boxes` docstring 首行。测试文件零删除 ✓ → "既有测试零修改"成立 ✓。禁改面零 diff ✓（diff 仅 7 文件）。

注意 `detect()` 的删除行：`boxes, n_bubble = _detect_text_boxes(...)` 3 行被替换成分支。这符合"detect() 加分支"。

现在测试行号已获得。parametrize 列表行号大概是 407-420 左右，`test_illegal_values_fail_fast` 在 431。我在 findings 里引用 431 即可，或引用 405-431。让我确认参数列表范围：diff 显示 parametrize 在 1050-1068（diff 行），映射到测试文件 ~407-428。我引用 `tests/providers/test_detection_manga.py:407-431`。

嗯，为了准确，我用 grep 查 `("NEWMANGA_DETECTOR_TILING_TILE_SIZE", "0")` 的行号。快速一次 grep。

另外我还想确认 tests 中 `_clean_tiling_env` 在 373-385（grep 显示 def _clean_tiling_env 在 382？grep 显示 `Line 382: def _clean_tiling_env(monkeypatch) -> None:` 而 diff 中它是新增的。等等 grep 之前显示 `Line 382: def _clean_tiling_env` 和 `Line 387: class TestTilingConfig`。但 `_TILING_ENV_VARS` 在哪？大约 374。OK。

还有一点值得检查：测试文件顶部的 import 是否新增了 tiling 相关符号（diff 显示测试文件 hunk 只有 368 行后的插入，没有修改 import 区）→ 测试通过 `detection_manga._tiling_config` 访问，无需新增 import ✓。但 `_provider`/`_frame_bytes` 等已有 ✓。

好，最后一个小核对：`TestTiledDetectionPath._run_tiled` 里 `pytest.importorskip("numpy", reason="numpy is not installed")` 调了两次（第 1222-1223 行 diff：先 `pytest.importorskip("numpy", reason=...)` 再 `numpy = pytest.importorskip("numpy")`）—— 冗余但无害。`test_threshold_is_passed_through_to_tile_inference` 也有同样冗余。P4 微不足道，可提一句"重复 importorskip 冗余"。不值得列 finding。可以在 findings 里合并或省略。我会省略或作为观察。

现在，还需要确认一个重要点：**qualification 脚本是否验证了 `_tiling_config()` 的默认值就是 DIAG 值**（除 print 外）。脚本 print 硬编码字符串 "tiling defaults: tile=1024 overlap=128 nms_iou=0.5 trigger_ratio=4.0 (DIAG-frozen)" —— 是硬编码文本而非读取实际常量。若 env 被污染，这行 print 仍显示默认。这加强了 R7。✓

另外 JSON 里没有 `tiling_config` 字段，也没有 env 快照。R7 成立。

我现在准备写报告。报告要包含：
## Verdict
## 逐项核对表（A 普通页零变化 / B tiling 实现 / C env fail-fast / D qualification / E 范围纪律与发布形态）
## Findings（R1…，P0-P4，文件:行）
## NOT_VERIFIED（集成方运行时项）
## 集成方闭合清单
## 推荐下一步（一句）

逐项核对表应逐条核对 Owner 声称。我要覆盖用户列的 6 个重点审查项。

让我组织表：每条 = 声称 → 我的核对 → 判定（成立/成立但需补强/不成立）。

A 普通页零变化：
1. 触发严格 >4.0：`_tiling_triggered` line 268 `height / max(width,1.0) > trigger_ratio` ✓ 严格；测试 444-472 覆盖 K01/K02/K04 触发、BJ02 不触发、h/w==ratio 不触发、width=0、ratio 可配 ✓
2. 不触发走原 `_detect_text_boxes`：diff 中该函数体全为 context（555-582 未变），detect() 分支 line 327-355 ✓
3. "函数本体逐字节未动"：docstring 由 1 行改 5 行（838 删除行），函数体零 diff → 措辞需精确（R8）
4. 零变化边界：`tiling_config = _tiling_config()`（326）在分支外 → 非法 env 时普通页也失败，且错误非 typed（R1）；options 新增 2 键（383-384），既有测试按 dict 取键（test line 366-367）不受影响 ✓
5. 双向哨兵：test 782-807（普通页必走原函数、tiled 禁入）+ test 725-777（长条页禁止原函数）✓ 足够钉住"分支编排"；但无法钉住"函数体零 diff"（需 diff 核对，我已做）
6. BJ02 qualification 对照：JSON 2330-2347 region=5 tiling=off matches_diag_probe=true ✓（但参照值硬编码，R7）

B tiling 实现：
1. 精确步进：`_tiling_tiles` 271-296 origins 条件 `o+tile < total`；K01 → 70 块、尾块 309 ✓（我按公式复算 K01/K02/K04/K05/K08 = 70/21/32/52/58，与 JSON tiling_tiles 全部一致；690 对照 111 一致）
2. pad：`_pad_tile` 585-595 常量灰 114、右下 padding、crop 尺寸 ≤ tile_size 恒成立 ✓（DIAG `_pad_tile` 226-233 同）
3. 逐块推理同 engine：`_detect_text_boxes_tiled` 709-728 循环内复用传入 model/processor，无重建 ✓；`_tile_inference` 598-641 与整页序列同构（processor→model.no_grad→post_process，target=padded 尺寸）✓ 与 DIAG run_tile_inference 236-248 逐句一致
4. 回映：line 722-727 `+ (x0, y0)` ✓（DIAG 402 同）
5. clip 语义：718-720 传 crop_w/crop_h → `_text_boxes_from_results` 765-768 clip + 784-785 退化丢弃；DIAG 401-407 仅 center_x 丢弃、不 clip → 一般情形不等价；K01 数据上等价（我复算：无框跨出页/块界；最大 x1=674.4<690，最大 y1=62055.8<62133）→ R2
6. NMS：660-675 conf 降序稳定排序 + `any(_iou > t)`；DIAG 285-298 `best_iou > threshold` → 语义一致（"等于保留"）✓；kept 两两 IoU ≤ t 构造性成立 ✓
7. 跨块重复残留：35 对/33 删、30 在带内（DIAG 1181-1186）✓；"被块界截断且 IoU≤0.5 的同目标残留"无度量 → 登记（无阻塞）
8. 2D 网格未经验证 → R5

C env fail-fast：
1. 4 个 env 名 + 默认值 4.0/1024/128/0.5 ✓（153-155/162/173-176/183-186）
2. 非数/负数/零/overlap≥tile → ValueError 含 env 名 ✓（189-260），测试 431 覆盖 14 条 ✓
3. 读取时机 engine 之后 ✓（323-326）+ 测试 809 钉住缺权重仍 typed ✓
4. 但错误非 typed（R1）；空串静默默认（R3）；联合校验隐式路径与 nan/inf 无测试（R4）
5. overlap 对生效 tile_size 联合校验 ✓（235-239 用局部 tile_size）

D qualification：
1. Gate region 层级 >0，5/5 ✓（JSON gate.overall=PASS，程序化 548-554 + 退出码 574）
2. 框层级并报 ✓ text_boxes_pre_merge
3. 延迟 K01 20104≤25000 ✓ K02 5968≤10000 ✓ K04 9271≤15000 ✓；脚本对超预算只登记 `latency_within_budget` 不判 FAIL ✓（与注释一致；但预算在任务书是 AC，脚本不 fail → 迟钝点，可登记 P4）
4. 阈值曲线 0.5/0.4 ✓ 五点齐全，conf_min 0.40-0.45 ✓
5. 690 对照 111 块/198 框/177 region/31887ms ✓ 与我按 `_tiling_tiles` 复算 111 一致
6. K19=0/tiling=off ✓；BJ02=5/tiling=off ✓
7. 程序化程度：Gate 程序化 ✓；controls 不参与 overall、DIAG 参照硬编码、resolved config 未落盘 → R7
8. K01 193 与 DIAG 逐值（计数）✓；坐标级未落盘比对（R2 中我做了静态抽查）

E 范围纪律与发布形态：
1. 7 文件全在允许面（diff 7 个）✓
2. 禁改面零 diff：detection_sfx/doctr/ports/bootstrap/contracts/packaging/apps/TA3-*/DIAG experiments/STATUS 无匹配 ✓（diff 文件清单）
3. 无二进制 ✓（无 Binary/GIT binary patch）
4. 既有测试零修改：测试 diff 零删除行 ✓
5. 无新依赖：仅 `import os` + numpy/torch 既有 ✓（diff 620）
6. 发布形态：20.1s 数值已登记；UI/IPC 超时/进度/composite 叠加/块数上限未评估 → R6

现在 Verdict：我认为是 **PASS（有条件，无 P0/P1/P2）**，7-9 条 P3/P4 建议项。合入前集成方需闭合若干登记项（非代码返修，或 Owner 下一轮小修）。

不过要小心：Review 结论如果是"PASS"但 R1 涉及"普通页在非法 env 下失败且非 typed"，集成方是否必须处理？我建议：R1 与 R3 建议同一轮小修（把 `_tiling_config` 的失败改为 typed，并把空串纳入 fail-fast），因为改动小、测试可补。但也可以作为 follow-up 登记。我会在集成方闭合清单中给两个选项：最小闭合（登记 + 追踪）或建议返修（人工判断）。

由于我是非作者 Reviewer，且这是 round 1 静态 review，通常给出"PASS with findings（建议 R1/R3 小修后合入）"较合适。我会写：**判定：PASS（无阻塞项）**；但明确"若集成方要求 fail-closed typed 严格对齐任务书纪律，R1/R3 应在合并前由 Owner 小修（改动局限在 detection_manga.py `_tiling_config` 与 2 条测试）"。

再检查 NOT_VERIFIED 项：
1. 三套件 575 passed + 1 skipped 0 failed —— 无落盘日志，我无法在沙箱运行 pytest（pwsh 被文件策略拒绝）→ 集成方重跑。
2. qualification GATE PASS 的重跑复现（约 2.5 分钟 CPU）—— 数字逐值一致期望未验证。
3. 红态 44/29 —— 无 commit 级复现路径（实现与测试同 commit），需手工构造（临时移除实现）或查会话记录。
4. worktree git status 干净 / 禁改面 porcelain 零 —— 我依 review-input.diff 判定，未跑 git。
5. `git diff --check` EXIT=0（空白错误）—— 未运行；我目视 diff 无 trailing whitespace? 无法完全确认。可静态检查：grep 行尾空格。实际上我可以 grep `[ \t]+$` 在 diff 中找新增行的行尾空白。这值得做（Owner 声称 diff --check EXIT=0）。让我做一个 grep：pattern `^\+.*[ \t]$` 在 diff。这能静态验证新增行无 trailing whitespace ✓。加上删除行。

让我跑这个 grep，同时 grep 参数列表行号。

另外还有：qualification 脚本 assert 输出目录写权限等（无）。

还有一件事：**K01 20 104ms 与 DIAG 19 811ms 相近** ✓（同一 CPU 环境）。

跑最后的 grep。
dsh: reasoning:
trailing whitespace 检查：无匹配 ✓（支持 diff --check EXIT=0）。

参数表在 412-428，test 431。

现在我有足够材料。写报告。

格式要求：直接输出全文（不写文件，用户说"直接输出全文"）。所以我在回答中输出 Markdown。

引用行号：
- detection_manga.py（worktree @29a7f5b5）：
  - 44-68 模块 docstring tiling 段
  - 145-176 常量/env 名
  - 189-260 `_tiling_config`
  - 200/214/228/243 空串判断
  - 235-239 overlap 联合校验
  - 263-268 `_tiling_triggered`
  - 271-296 `_tiling_tiles`
  - 320-387 `detect`（326 配置读取、327 触发、331-333 tiled、350-355 untiled、383-384 options）
  - 538-582 `_detect_text_boxes`（541-554 docstring、555-582 体）
  - 585-595 `_pad_tile`
  - 598-641 `_tile_inference`
  - 644-657 `_iou`
  - 660-675 `_greedy_nms`
  - 678-728 `_detect_text_boxes_tiled`
  - 731-787 `_text_boxes_from_results`（765-768 clip、784-785 退化）
- tests/providers/test_detection_manga.py: 374 `_TILING_ENV_VARS`? (grep 显示 382 `_clean_tiling_env`)，387 TestTilingConfig，412-431 参数矩阵，444-472 trigger，478-517 tiles，523-553 NMS，573-719 tiled path，608/660，725-777，782-807，809-816
- qualifying: experiments/M2-DETECT-WEBTOON-TILING/qualify_tiling.py: 285-320 curve_point，296-304 私有调用，373-374 provider/_engine_or_raise，411-498 Gate 循环，479-498 690 对照，500-522 K19，524-546 BJ02，528 硬编码，548-561 overall/controls，563-574 输出与退出码
- DIAG: experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py: 226-233 pad，236-260 run_tile_inference，263-298 iou/greedy_nms，378-434 tile_experiment，395-425 循环，401-407 pad 丢弃
- probe-results.json: 1188-1415 pre_nms，1416-1610 post_nms，1181-1186 删除统计
- handlers.py:212 `_typed`，278 detect
- executor.py:34-39
- core_service.py:563-644（626-641 catch-all）
- detection_sfx.py:158-165 sfx ValueError 先例；569-609 composite

Findings 编号 R1-R9。严重度：无 P0/P1/P2；R1-R6 P3；R7-R9 P4。等等，R6（发布形态/UI 超时）用户很关注，我给 P3。R5（2D 未验证）P3。

要不要把某条提到 P2？考虑 R1：普通页在非法 env 下失败 + 非 typed。它的触发条件是运维设置非法 env（低频）。而且 SFX 先例同类。P3 合适。

好。还需在"逐项核对表"里体现用户 6 个重点审查项。

关于 Verdict 措辞：PASS（round 1；无 P0/P1/P2 阻塞项；9 条 P3/P4）→ 建议集成方按闭合清单处理，并建议 Owner 在合并前或紧邻 follow-up 完成 R1/R3 的最小修（可选）。

推荐下一步（一句）：由编排会话代行 Codex 按集成次序 TILING→BACKFILL→SFX-UI 合并 29a7f5b5+36b61c3a，并在集成验证中重跑两条复现命令 + 决定 R1/R3 是否随合并小修。

我需要写"可直接转发"的指令吗？AGENTS.md 说每次结束要给出推荐下一步；这个 Review 输出格式最后是"推荐下一步（一句）"。遵守。

现在写。注意用简体中文，技术标识保留英文。

逐项核对表用 Markdown 表格，列：面/核对项/证据（文件:行）/判定。

写得紧凑但完整。开始。

关于"我的静态复算"要写清楚方法（用 read/grep 逐值核），因为这是我这轮的独立证据：
1. 块数复算：K01=70、K02=21、K04=32、K05=52、K08=58、K01@690=111 —— 与 JSON tiling_tiles 全部一致（按 `_tiling_tiles` origins 公式手算）。
2. 越界框检查：对 DIAG `pre_nms_boxes`(1188-1415)/`post_nms_boxes`(1416-1610) 全量 226 框，正则筛第三分量 ≥600 得 111 行、最大 674.4；第四分量 ≥62000 得 4 行、最大 62055.8 → 无框跨出页界 690/62133；唯一贴边 0.3px（tile68 y1=61952.3 vs 其 crop 上界 61952）。
3. 删除行全清单（5 行）→ 既有测试零修改、禁改面零触碰。
4. 新增测试条数 = 45（逐条计数），红态 44+29=73=28+45 自洽（`test_missing_weights_fails_closed_before_tiling` 在红态可通过）。
5. trailing whitespace 0 命中 → 支持 diff --check EXIT=0。

这些放在核对表或"我独立做的静态复算"小节。用户格式没给这一节，我可以放进 Verdict 里简述或表格里。我会在 Verdict 后加一小段"独立静态复算（本轮）"，但用户格式是固定的四段+两段。我可以在 Verdict 段内写。保持格式：## Verdict 下写判定 + 复算摘要。

好，开始写正文。长度适中但信息密度高。
## Verdict

**PASS（round 1，无 P0/P1/P2 阻塞项）**：M2-DETECT-WEBTOON-TILING @ 29a7f5b5 + 文档 tip 36b61c3a 的 7 个变更文件全部落在授权允许面，Owner 的逐条声称经静态核对**全部成立**（含 1 处表述需精确化、若干论证需补强）；共 **9 条 P3/P4 建议项**（R1–R9），其中 R1/R3 触及任务书「fail-closed typed」与「never a silent default」的措辞边界，建议由 Owner 小修或由集成方登记为紧邻 follow-up，不构成合并阻塞。

本轮独立静态复算（无 shell，纯 read/grep 逐值核对，均来自 worktree 源码、`review-input.diff`、DIAG 只读证据）：
1. **块数逐值**：按 `_tiling_tiles`（`detection_manga.py:271-296`）origins 公式手算 K01=70 / K02=21 / K04=32 / K05=52 / K08=58 / K01@tile690=111，与 `qualification-results.json` 的 `tiling_tiles` 与报告 111 块**全部一致**；K01 尾块 309px、原点 0..61824 步 896 与 DIAG 一致。
2. **clip 等价性的经验核验**（Owner 未做）：对 DIAG `pre_nms_boxes`(probe-results.json:1188-1415) 与 `post_nms_boxes`(1416-1610) 全量 226 框做正则筛值 —— 第三分量（x1）最大 **674.4 < 690**（页宽）、第四分量（y1）最大 **62055.8 < 62133**（页高），唯一贴边是 tile68 的 y1=61952.3 超出其 crop 上界 61952 **0.3px**（浮点舍入）。即"无任何框跨出 crop/页边界"，这是两法数值等价**比 Owner 论证更强**的成立理由。
3. **删除行全清单**：全 diff 仅 5 行删除（Task `status`、`detect()` 中 4 行原调用、`_detect_text_boxes` docstring 首行）→ **既有测试零删除、"函数体"零 diff、禁改面零触碰**均成立。
4. **红绿数字自洽**：按 diff 逐条计数新增测试 = 45 条（与 handoff 一致）；73 collected = 既有 28 + 新增 45，红态 29 passed = 28 既有 + `test_missing_weights_fails_closed_before_tiling`（不引用任何 tiling 符号，红态即可通过）→ 44 failed/29 passed 完全自洽，数字非编造。
5. **空白纪律**：`^\+.*[ \t]+$` 零命中，支持 `git diff --check EXIT=0`。

## 逐项核对表

### A 普通页零变化

| # | 核对项 | 证据（文件:行） | 判定 |
|---|---|---|---|
| A1 | 触发 = `height/max(width,1) > ratio` **严格大于** | `detection_manga.py:263-268`（`>`）；测试 `test_boundary_is_strict_greater_than`（test:466-470）、`test_zero_width_is_defended` | ✅ 成立 |
| A2 | 不触发页走**原函数** | diff 中 `_detect_text_boxes` 函数体（555-582）全为 context 行；`detect()` 分支 327-355 · 不触发调用点 352-354 | ✅ 成立 |
| A3 | 「函数本体逐字节未动」表述 | 全 diff 仅删除 docstring 首行（diff:838），docstring 1→5 行（541-554），可执行语句零 diff | ⚠️ 行为成立，**表述需精确化**（R8） |
| A4 | 普通页「零变化」的真实边界 | `tiling_config = _tiling_config()`（326）位于 if 分支**之外** → 非法 env 时普通页也失败，且异常非 typed（R1）；options 新增 2 键（383-384） | ⚠️ 合法配置下零变化，配置错误下不成立（R1） |
| A5 | 「双向哨兵」充分性 | test:782-807（普通页必走原函数 + tiled 分支禁入 + options `tiling=off`）、test:725-777（长条页禁止进入 untiled） | ✅ 对**分支编排**充分；对"函数体零 diff"由 diff 事实保证 |
| A6 | BJ02 对照 | `qualification-results.json:2322-2347`（region 5 / tiling off / matches_diag_probe true），与 `diagnosis.md:41` 一致 | ✅ 成立（参照值硬编码，见 R7） |
| A7 | options 兼容面 | 既有断言按 `dict(result.options)` 取键（test:366-367）；全仓 `text_boxes_pre_merge/tiling` 无第二消费方（src 全域 grep 零命中） | ✅ 非破坏 |

### B tiling 实现（切块/回映/NMS/clip）

| # | 核对项 | 证据 | 判定 |
|---|---|---|---|
| B1 | 精确步进公式与尾块 | `_tiling_tiles` 271-296：`step=tile-overlap`，`while o+tile < total`，末块 `min(o+tile, total)`；K01→70 块/尾块 309 = DIAG（`diagnose_webtoon_detect.py:395-425` 同款步进） | ✅ 成立（本轮复算 6 组块数全中） |
| B2 | 灰 114 pad 到方形 | `_pad_tile` 585-595 vs DIAG 226-233（同常量 `TILING_PAD_VALUE=114` / `TILE_PAD_VALUE=114`）；crop 尺寸恒 ≤ tile_size（293 行 min 保证），无越界赋值风险 | ✅ 成立 |
| B3 | 逐块同 engine、不重建 | `_detect_text_boxes_tiled` 709-728 循环内复用入参 model/processor；`_tile_inference` 598-641 与 `_detect_text_boxes` 555-582 同为 `processor→model.no_grad→post_process`，inference 目标 = padded 尺寸，与 DIAG `run_tile_inference:236-248` 逐句一致 | ✅ 成立 |
| B4 | 回映 `+块原点` | 722-727；DIAG 402 同式 | ✅ 成立 |
| B5 | clip 语义 vs DIAG「pad 带中心点丢弃」 | 生产：`_text_boxes_from_results(scores,labels,boxes,crop_w,crop_h)`（718-720）→ 765-768 clip + 784-785 退化丢弃；DIAG：401-407 **仅** `center_x > width` 丢弃，无 y 检查、无 clip。**一般情形两法不等价**（跨 crop 边界框坐标不同、clip 会降低跨块重复框 IoU 而削弱 NMS）；在 K01 上经本轮全量框值核验**数值等价**（见 Verdict 复算 2） | ⚠️ 结论成立，Argument 不完整（R2） |
| B6 | NMS「严格大于删 / 等于保留」 | 生产 660-675（`any(_iou(box,keeper) > iou_threshold)`，conf 降序稳定排序）；DIAG 285-298（`best_keeper>=0 and best_iou > iou_threshold`）——语义一致；kept 两两 IoU ≤ t 构造性成立 | ✅ 成立 |
| B7 | 跨块重复残留风险 | DIAG 实测 35 对 IoU>0.5 / 删 33 / 30 在重叠带（probe-results.json:1177-1186）：去重有效、无重复爆炸；「同目标被块界截断且 IoU≤0.5」的残留量**无度量**（DIAG 已声明 directional） | ⚠️ 已登记，属已知残余风险 |
| B8 | 2D（横向）切块 | `_tiling_tiles` 是 2D 网格（294-295）；但 DIAG 实验只做垂直切块（`crop = rgb[y:y1]` 全宽，395-397），5 张 Gate 页宽 600/690 < 1024 | ❌ 真实数据未覆盖（R5，不阻塞） |

### C env fail-fast

| # | 核对项 | 证据 | 判定 |
|---|---|---|---|
| C1 | 4 个 env 名 + 默认 4.0/1024/128/0.5 | 173-176（名）、153-155/162/183-186（默认，与 DIAG 冻结值一致） | ✅ 成立 |
| C2 | 非法矩阵：非数/零/负/超域/overlap≥tile | 189-260 全覆盖且消息含 env 名；测试 412-431（14 条 parametrize） | ✅ 成立 |
| C3 | overlap 对**生效** tile_size 联合校验 | 235-239（用解析后的 `tile_size` 比较，错误消息同时含两变量名） | ✅ 逻辑成立，隐式路径无测试（R4） |
| C4 | 读取时机（engine 之后）与 fail-closed 顺序 | detect 322-326：`_validate_request→_engine_or_raise→_frame_pixels→_tiling_config`；测试 809-816 钉住缺权重仍 `PROVIDER_NOT_CONFIGURED` | ✅ 成立（顺序取舍已在 handoff 登记） |
| C5 | 失败形态是否 typed | `_tiling_config` 抛裸 `ValueError`；`handlers.py:212-218` 的 `_typed` 只捕 `ProviderError` → `executor.py:38-39` flatten 成 `PROVIDER_FAILED`；core.detect 面 `core_service.py:626-641` → `E_UNKNOWN`「Detection failed」（env 名仅进 stderr） | ❌ 非 typed（R1） |
| C6 | 「never a silent default」 | `if raw and raw.strip():`（200/214/228/243）：`""`/`"   "` 静默回落默认 | ❌ 与声明矛盾（R3） |

### D qualification

| # | 核对项 | 证据 | 判定 |
|---|---|---|---|
| D1 | Gate = 5 张 region>0，**程序化** | `qualify_tiling.py:442-444`（逐页 PASS/FAIL）、548-553（`all(...)` 得 overall）、574（`return 0 if PASS else 3`）；JSON `gate.overall="PASS"` | ✅ 程序化成立 |
| D2 | region 层级 + 框层级并报 | JSON `provider_detect.region_count` + `text_boxes_pre_merge`（同一次 `provider.detect` 的 options） | ✅ 成立 |
| D3 | 延迟与预算 | K01 20104≤25000、K02 5968≤10000、K04 9271≤15000（`latency_within_budget=true`）；超预算**只登记不判 FAIL**（脚本 docstring 141-146/439-441） | ✅ 数字成立；预算不参与退出码（🟡 提示，见 R7） |
| D4 | ≥2 阈值点曲线 | 0.5（生产 detect）/0.4（同 tiled 代码 + 生产 merge，285-320）：193→214、97→103、117→120、64→65、61→65；conf_min 0.40–0.45 | ✅ 成立 |
| D5 | 690×690 原生尺度对照 | 111 块 / 198 框 / 177 region / 31887ms（JSON 1802-1811）；*1.6× 块数、框级 +2.6% 与报告一致；本轮复算 111 块 ✅ | ✅ 成立 |
| D6 | K19=0 / BJ02=5 | JSON 2301-2321 / 2322-2347，均 `tiling=off` | ✅ 成立 |
| D7 | K01 与 DIAG 逐值复现 | JSON `text_boxes_pre_merge=193`、`tiling_tiles=70` = DIAG 块级实验 | ✅ **计数级**逐值；坐标级未落盘比对（R2） |
| D8 | 参数可审计性 | JSON **无** resolved `TilingConfig` 落盘；脚本 print 的「tiling defaults」是硬编码文本（377-381）；`curve_point` 恒用 `TilingConfig()` 默认（461），不读 env；脚本未清理/断言 `NEWMANGA_DETECTOR_TILING_*` | ❌ 审计缺口（R7） |
| D9 | controls 是否 Gate | `overall` 计算时 `report["gate"]` 尚未含 controls（548-561 顺序）；K19/BJ02 只记录 | ⚠️ 与「DIAG 冻结口径只裁 5 页」相容，但需明示（R7） |

### E 范围纪律与发布形态

| # | 核对项 | 证据 | 判定 |
|---|---|---|---|
| E1 | 7 文件允许面 | `review-input.diff` 仅 7 个 `diff --git`：Task/Handoff、`detection_manga.py`、`test_detection_manga.py`、`qualify_tiling.py`、`qualification-results.json`、`qualification-report.md` | ✅ 成立 |
| E2 | 禁改面零触碰 | detection_sfx / detection_doctr / ports / bootstrap / contracts / packaging / apps / TA3-* / DIAG experiments / STATUS 在 diff 中零出现 | ✅ 成立（依 diff；porcelain 未运行 → NOT_VERIFIED） |
| E3 | 无二进制 | 无 `Binary files` / `GIT binary patch` 标记 | ✅ 成立 |
| E4 | 既有测试零修改 | 测试 diff 零删除行（全 diff 仅 5 行删除，均在 Task/实现 docstring） | ✅ 成立 |
| E5 | 无新依赖 | diff 仅新增 `import os`（620）+ 既有 numpy/torch 调用；`_lazy_import` 复用 | ✅ 成立 |
| E6 | 发布形态影响 | handoff:78-79 + Task 交付记录：登记「最坏 ≈20s、块数线性、GPU/并发/降块=发布形态输入」；**未覆盖** UI/IPC 同步阻塞与超时、进度/取消、composite（M2-SFX-PROD-1）叠加耗时、块数上限 | ⚠️ 登记不充分（R6） |

## Findings

**R1（P3，fail-closed 语义）`_tiling_config()` 的失败是裸 `ValueError`，既打破「普通页零变化」又降级错误码**
- `src/infrastructure/providers/detection_manga.py:326`（配置读取在 if 分支外，所有页面都执行）+ `:189-260`（raise `ValueError`）
- 调用链：`src/infrastructure/providers/handlers.py:278` → `:212-218`（`_typed` 只捕 `ProviderError`）→ `src/infrastructure/pipeline/executor.py:38-39`（flatten 为 `PROVIDER_FAILED`）；core.detect 面 `src/bootstrap/core_service.py:626-641`（→ `E_UNKNOWN`「Detection failed」，env 名丢失于线上，仅 stderr）
- 后果：(a) 任一非法 `NEWMANGA_DETECTOR_TILING_*` 会让**不触发的普通页**也 detect 失败（合法配置下才零变化）；(b) 任务书纪律写「tiling 内部失败 typed」，此处配置失败未 typed。缓解：SFX 先例 `detection_sfx.py:158-165` 也是 `ValueError`，但其失败点在 assembly 启动期而非请求期。
- 建议：将 `_tiling_config()` 的解析/范围失败包装为 `ProviderInputError`（或专用 typed 错误），并补 `detect()` 在非法 env 下抛 typed 错误的测试。

**R2（P3，论证精度）clip（生产）与「中心点丢弃」（DIAG）的等价论证不完整**
- `detection_manga.py:718-720` + `:765-768` + `:784-785` vs `experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py:401-407`
- DIAG 只丢弃「中心在**右侧** pad 带」的框，不检查底部 pad、不做任何 clip；生产 clip 到 crop 并在退化时丢弃。两法只在「无框跨出 crop 边界」时等价 —— 本轮已用 DIAG 全量落盘框证明 K01 满足（最大 x1 674.4<690、最大 y1 62055.8<62133，唯一 0.3px 浮点贴边），但 Owner 记录的理由仅是「pad 带零检出」（只覆盖中心点在带内），未覆盖「框跨越 crop 边界」。理论后果：clip 会截断重叠带内框并降低跨块重复框 IoU，从而削弱 NMS 去重（K01 数据实测未发生）。
- 建议：把论证补为「无框跨出 crop 边界（可由 DIAG JSON 复算，含本轮数值）」，并补一条合成单测固定「跨块底边框」的生产语义（现有 `test_tile_boxes_are_clipped_to_the_tile_bounds` 只测 130→100 的 crop 内截断）。

**R3（P3，fail-fast 完备性）空/空白 env 值静默回落默认，与「never a silent default」声明矛盾**
- `detection_manga.py:200/214/228/243`（`if raw and raw.strip():`）；声明见 `:171-172`、`:189-197`
- `NEWMANGA_DETECTOR_TILING_TILE_SIZE=""`（或 `"   "`）→ 用默认值，无 `ValueError`；测试矩阵（`test_detection_manga.py:412-431`）无空串用例。
- 建议：把空/空白视为非法（fail-fast），或把 docstring/handoff 措辞改为「absent or blank → default」。

**R4（P3/P4，测试覆盖）fail-fast 矩阵缺最容易踩的联合路径与 nan/inf 用例**
- `detection_manga.py:235-239` 是「overlap 对**生效** tile_size 联合校验」的关键分支，但 14 条 parametrize 中只有显式 `OVERLAP=1024`（`test_detection_manga.py:420`）命中「overlap ≥ tile」；**没有**「`TILE_SIZE=64` + overlap 未设置（默认 128）」这条运维最可能遇到的隐式路径。
- 另：`TRIGGER_RATIO=inf` 通过校验（语义=永不触发，风险低）、`NMS_IOU=nan` 被正确拒绝（逻辑已核），两者均无测试。

**R5（P3，未验证面）2D（横向）切块路径无真实页证据**
- `_tiling_tiles` 是 2D 网格（`detection_manga.py:294-295`），而 DIAG 实验与 qualification 只覆盖 x 方向单块（`diagnose_webtoon_detect.py:395-397`；Gate 页宽 600/690 < 1024）。宽长条页（如 2000×12000，h/w=6）会走 2D 路径：块数倍增、新增 x 向重叠带，仅有一条合成几何测试（`test_wide_page_cuts_a_two_dimensional_grid`）。
- 建议：在 handoff/qualification 报告显式登记为未验证面，或补一张 width > 1024 的真实页。

**R6（P3，发布形态）20.1s/页的影响登记未覆盖 UI/IPC 超时、进度与 composite 叠加**
- 现状登记：handoff:78-79（数值 + 「发布形态输入」）。
- 缺口：(a) `src/infrastructure/providers/detection_sfx.py:569-609` 的 composite 在 primary 之上**再跑一次**推理，长条页总耗时 = tiling（20.1s）+ sfx（未测）；(b) core.detect 是同步请求-响应（`core_service.py:563-644`），单页阻塞 worker 20s+，Tauri 侧超时/取消/进度未评估；(c) 块数随页高线性且**无上限/降级**（K08 51971→58 块 16.3s，更长条漫线性外推 60s+）。
- 建议：把「IPC 超时配置、进度/取消、块数上限或降采样策略、composite 总耗时实测」写入集成方闭合清单。

**R7（P4，qualification 方法论）Gate 之外的判定与审计项**
- `experiments/M2-DETECT-WEBTOON-TILING/qualify_tiling.py:548-561`：`overall` 只聚合 5 张 Gate 页，K19/BJ02 controls 在其后写入、**不参与** PASS/退出码。
- `:528` `diag_reference_region_count = 5` 硬编码（应从 `probe-results.json` 读取）；K19 期望 0 同理。
- 预算（`LATENCY_BUDGET_S`，227）只写 `latency_within_budget` 字段、不影响退出码 —— 与脚本注释自洽，但任务书 AC3 把预算列为交付项，**超预算时会静默 PASS**。
- 脚本不清理/断言 `NEWMANGA_DETECTOR_TILING_*`，且 `curve_point` 恒用 `TilingConfig()` 默认（461）而生产点读 env（`:326`）：env 污染会导致两个曲线点用不同参数且报告无法察觉；JSON 亦无 resolved config 落盘。
- 建议：JSON 增加 `tiling_config`（resolved）与 env 快照；从 DIAG JSON 读参照值；把 controls/预算纳入 overall 或在报告显式标注「非 Gate」。

**R8（P4，表述）「函数本体逐字节未动」应改为「可执行语句零 diff，docstring 更新」**
- `detection_manga.py:541-554`：docstring 1→5 行（diff 删除行见 `review-input.diff:838`），函数体 555-582 零 diff；同一 docstring 自称 `kept byte-identical`，字面不成立（行为不受影响）。

**R9（P4/登记）红态不可从 commit 复现 + 实验脚本耦合私有符号**
- implement 单 commit 同时落实现与测试，故「红态 44 failed/29 passed」无落盘日志、无法 checkout 复现（建议下一轮保留红态日志或写明构造方式；数字本身已自洽，见 Verdict 4）。
- `qualify_tiling.py:296-304/374/480` 直接使用 `_detect_text_boxes_tiled`、`_tiling_tiles`、`provider._engine_or_raise()`：provider 内部重构会静默打断复现链（实验面可接受，登记即可）。

## NOT_VERIFIED（集成方运行时项）

1. **三套件绿态**：`PYTHONPATH=src <venv> -m pytest tests/providers tests/core tests/m2_acceptance -q` = 575 passed + 1 skipped 0 failed（handoff 未落盘日志；本轮沙箱无 shell，pwsh 被文件策略拒绝 `SetNamedSecurityInfoW failed (Win32 5)`）。**集成方必须重跑**。
2. **qualification GATE PASS 重跑**：`qualify_tiling.py`（真权重、CPU ≈2.5min）数字逐值复现（K01 193/180/70104ms、K02 97/93、K04 117/113、K05 64/62、K08 61/60、690 对照 111/198/177、K19=0、BJ02=5）。JSON 是否被重跑覆盖需注意（脚本会覆盖 `--output`）。
3. **红态复现**：44 failed / 29 passed 的构造与日志（无 commit 级路径）。
4. **worktree 洁净度**：`git status --porcelain`（仅 4 个允许面路径）、`git diff --check`、以及禁改面 porcelain 零 —— 本轮仅由 `review-input.diff` 反推（7 文件、5 删除行、无 trailing whitespace），未运行 git。
5. **本 Task 之外的运行时行为**：非法 env 时 pipeline `PROVIDER_FAILED` / core.detect `E_UNKNOWN` 的实际线上表现（R1），以及 composite（M2-SFX-PROD-1）在长条页上的总耗时（R6）。

## 集成方闭合清单

1. 重跑第 1、2 项 NOT_VERIFIED 命令并归档输出（Gate 五页 region>0 与 575 passed 保持）；确认重跑前后 `qualification-results.json` 数值逐值一致。
2. 决定 **R1/R3** 处置：建议在合并前或紧邻 follow-up 由 Owner 小修（`_tiling_config` 失败改 typed + 空串纳入 fail-fast + 各 1 条测试）；若选择登记，请在 Task/Handoff 明确「非法 env 会让普通页一并失败且线上错误码为 `PROVIDER_FAILED`/`E_UNKNOWN`」这一行为。
3. 按 R7 补 `/verification/M2-DETECT-WEBTOON-TILING/qualification-results.json` 的 `tiling_config`（resolved）+ env 快照；把 controls/预算的「非 Gate」语义写进报告（可并入手 2 的文档 follow-up）。
4. 把 **R6** 四项（IPC 超时、进度/取消、块数上限或降采样、composite 总耗时实测）登记为发布形态待办，指定 Owner/里程碑。
5. 在 Handoff/Task 中登记 **R5**（2D 横向切块未验证）、**R2**（clip 等价论证补「无框跨出 crop 边界」，并附本轮数值）、**R8**（「函数体零 diff」措辞）。
6. 合并次序按批次 release f99a6c55 的 TILING → BACKFILL → SFX-UI；合并后确认 7 文件落点与 `detection_sfx.py` 零触碰。

## 推荐下一步（一句）

由编排会话代行 Codex 按 TILING → BACKFILL → SFX-UI 次序集成 29a7f5b5 + 36b61c3a，并在集成验证中重跑两条复现命令、同时裁定 R1/R3 是否随合并做最小 typed 化返修。
