# FEA11-FULLSYNC-TRIAGE-1 证据：2 个 FullSyncChain 失败的归因

基线 `003ba5fb3`。归因对象：
- `Fea11SourceIpcTests.FullSyncChain_PublishesNewGeneration_AndResolvesV2`
- `Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain_NewKeyOldDigestConserved`

## 1. 实测失败点

断言（`Fea11SourceIpcTests.cs:241-243`）：

```csharp
Assert.True(totals.GetProperty("changed").GetInt32() >= 1,
    "new container must produce a changed page: " + scanResult.GetRawText());
```

实测 `scanResult` 的 totals：

```json
"totals": {"unchanged":0,"added":0,"missing":0,"changed":0,"ambiguous":1}
```

⇒ **`changed = 0`，`ambiguous = 1`**。

## 2. 为什么是 ambiguous 而不是 changed（决定性证据）

抓 `scanResult` 的条目字段：

```
"evidence":"missing_old"
"classification":"ambiguous"
```

对照 `src/application/sources/matcher.py` 的判定：

```python
if not _pixel_present(old):
    # v7-era row (pixel/orientation None; at most W/H present): the
    # positional correspondence is unverifiable — never forge the old
    # profile from the new image (C-17 §7.3 row 4).
    classification, evidence = "ambiguous", "missing_old"
```

**⇒ 旧侧条目是 "v7-era"（没有 pixel/orientation 证据），matcher 按设计拒绝从新图伪造旧画像，
诚实降级为 `ambiguous`。**

**这是产品的正确行为，不是缺陷。** C-17 §7.3 row 4 明确要求如此。

## 3. 为什么旧侧没有 pixel 证据（根因）

`tests/fea11/support/ipc_seed.py`：

```python
old_entries = [
    ("se-001", "001.png", hashlib.sha256(old_pages[0]).hexdigest()),
    ("se-002", "002.png", hashlib.sha256(old_pages[1]).hexdigest()),
]
...
fea11_conftest.add_source_tree(
    conn, source_id="s1", version_id="sv1", digest=old_digest,
    entries=list(old_entries), legacy_v7_evidence=False,     # 明确要求"非 v7"
)
```

- 每个条目只给了 **3 元组**（`entry_id` / `locator` / `content_digest`），**没有 pixel 画像**；
- 虽然传了 `legacy_v7_evidence=False`（明确要求"非 v7"），但 `add_source_tree` 在缺少 pixel 数据时
  只能写出 v7-era 形状的行。

⇒ **测试基础设施缺 pixel 证据**：种子想要"非 v7"，但给的数据不足以生成非 v7 行。

## 4. 结论与分类

| 判断 | 结论 |
|---|---|
| 产品是否有缺陷 | **否** —— matcher 的行为完全符合 C-17 §7.3 row 4（拒绝伪造旧证据） |
| 测试期望是否合理 | **在"能判 changed"的前提下合理**，但**与当前种子数据矛盾** |
| 缺陷归属 | **测试基础设施**（`ipc_seed.py` 的 `old_entries` 缺 pixel 画像，或 `add_source_tree` 未从容器计算像素） |

## 5. 建议修法（**未实施**）

1. 让 `ipc_seed.py` 为 `old_entries` 提供 **pixel 画像**（`pixel_digest` + `width/height` + `orientation`
   + 与 match 所需的七维 profile），或用生产路径（真实 import/scan）生成旧侧证据；
2. 重新登记后可判 `changed`，断言 `changed >= 1` 才真正可满足；
3. **不得**改断言为 `changed + ambiguous >= 1` —— 那是**放宽**，会把"无法验证"当成"已验证"。

## 6. 本卡边界

- 本卡**只做归因**，未改任何代码/种子。
- 这 2 个失败**不是** schema 问题（`SCHEMA-VERSION-ASSERT-1` 已解决那批），也不是产品缺陷。
- 条件 3 仍不判 MET。
