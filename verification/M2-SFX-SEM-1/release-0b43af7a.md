# M2-SFX-SEM-1 释放证据（release @0b43af7a，2026-10-01）

## 授权
userselect「SFX OCR/翻译语义」（SFX-PROD-1 收口后候选；自治/全权授权延续）。

## 侦察事实
1. RegionInput=(region_id, text) 无类型槽（ports/translation/protocol.py:37-39）；TRANSLATION_SYSTEM_PROMPT 通用对白（translation_openai.py:42-48）；_build_user_text regions 仅 id+text（:104-107）。
2. bundle entry 有 region_type（context/builder.py:45,112）但 build_provider_request（step.py:76）未传——类型在进 provider 时丢失。
3. gate（step.py:168）已挡 skip/manual——进翻译的 SFX 全部 policy=translate（特化作用域精确）。
4. widening 先例=M2-FIX-LISTBOOKS（rev 1.2 §5 widening+默认值零破坏）；SFX 语义文档出处=D06/TASK-002 契约。

## 代理裁决
RegionInput.region_type 默认 "speech"+RegionType 枚举 fail-closed 校验；user_text 携带类型；system prompt SFX 段（文化对等转换、≤6 字符级、保持强度、禁止直译音节）；mock sfx 确定性输出；TASK-002 契约文档修订；SFX OCR/重绘 out of scope。
