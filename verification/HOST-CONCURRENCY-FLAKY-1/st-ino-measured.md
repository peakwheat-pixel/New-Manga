# FILE_IDENTITY_CHANGED 实测验证：`st_ino` 确实超过 53 位（7 个样本中 6 个）

- head: `062918039`
- 探针：`probe_st_ino.py`（只读 stat，不修改任何产品代码或测试）

## 实测输出

```
_FILE_MASK   = 9007199254740991  (2^53-1)
_VOLUME_MASK = 0xFFFFFFFF

path                    st_ino                  > 2^53?  masked                丢位?
alpha.png               844424931403221         no       844424931403221       no
page-01.png             36873221950633840       YES      844424931669872       YES
page-02.png             27021597765760890       YES      1537914               YES
page-03.png             19703248371283835       YES      1688849861801851      YES
page-04.png             27021597765760892       YES      1537916               YES
page-05.png             25051272928786301       YES      7036874419304317      YES
page-06.png             22799473115101054       YES      4785074605619070      YES

样本总数 7，其中 st_ino > _FILE_MASK 的：6
```

`st_dev` 同样溢出 32 位：

```
alpha.png     st_dev=15333285442011643084  0xCAC5BCCC  (mask 改变=True)
page-01.png   st_dev=2763106124046938139   0x5886301B  (mask 改变=True)
```

## 结论：物理条件已被证实

**`%TEMP%` 下新建文件的 `st_ino` 普遍超过 2^53**（6/7），
`mask` 会把它改成一个完全不同的数值（例如 `36873221950633840 -> 844424931669872`）。

⇒ **只要链路上有任何一处用未 mask 的 64 位值参与比较，就必然报 `FILE_IDENTITY_CHANGED`。**
这不是"偶发"，而是**默认会失败** —— 只有 file index 恰好 ≤ 2^53 时才偶然通过。

对比：repo 内的 `alpha.png`（长期存在的文件）`st_ino = 844424931403221 < 2^53`，
mask 不改变数值 —— 这正是"用 repo 里的既有文件测就没事、用 `%TEMP%` 新建文件就失败"的原因。

## 与 `GrantIssuerTests` 的连接

`FixtureImages`（`GrantIssuerTests.cs:44-50`）：

```csharp
var folder = Path.Combine(Path.GetTempPath(), "grant-fixtures-" + Guid.NewGuid().ToString("N")[..10]);
Directory.CreateDirectory(folder);
var path = Path.Combine(folder, $"page-{index + 1:00}.png");
File.WriteAllBytes(path, bytes);
```

⇒ **测试的 import 源全部是 `%TEMP%` 下新建文件 ⇒ `st_ino` 必然 > 2^53**（实测 6/6）。
所以这两个测试只要真正执行，就**必然**触发 mask 相关的身份比较问题。

这彻底解释了：
- 裸跑 `[SKIP]`（没执行）→ 看不到问题；
- `test.ps1` 下执行 → 2 个测试稳定失败（不是 flaky）。

## 还差最后一环（下一轮）

已证明「物理条件成立」（`st_ino` 超 53 位、mask 会改变数值），
还差「链路上哪一处没有 mask」。两个候选：

1. `HostIssuer.cs:591-596` 的 handle probe 返回完整 64 位 `FileIndex`；
2. `source_read_refs.py:1080` 的 `GrantFacts(*numbers, raw["sha256"])` 是否 mask 了 `numbers`。

**取证方法**：在 `test.ps1` 跑 `GrantIssuerTests` 时抓 IPC 报文里的 `file_id`
（wire log 里应有 grant 注册的 payload），与 `os.stat()` 的原始值/掩码值对比。

## 本轮不改代码

理由不变：修 Host 侧（契约要求的 producer 责任）还是 core 侧反序列化（纵深防御），
取决于最后一环的实测结果。**先取证，再改**。
