# Review — LICENSE-VARIANT-DECLARATION-1：TIGHTEN_TO_GPL 执行复核（2026-11-17）

> **reviewed_head**: `f475ea155caf291fcbdb2f27a8ed473b79fddbc4`（`main`）
> **reviewer**: `reviewer-tgl`（lead 派发的独立上下文子 agent；**未参与**本次许可收紧的实现、出包、文档修改或取证）
> **reviewed_at**: `2026-11-18T00:18:31+08:00`（任务窗口 2026-11-17；跨零点）
> **scope**: `3f99d0750..f475ea155`，重点 `49d1486b1`（代码/文档/产物）+ `f475ea155`（卡面登记）
> **method**: `git show` / worktree 只读 / `7z x` / python 原始字节扫描 / `web_fetch` / `check.ps1` / `read_image`
> **只读边界**：除本报告外未改仓库文件；未提交、未推送、未 checkout；未改 workspace 内既有 stage/fixture。

---

## 0. 结论摘要

| 项 | 值 |
|---|---|
| **decision** | **`ACCEPTED_WITH_FINDINGS`** |
| **P0 / P1 / P2** | **1 / 2 / 4** |
| TIGHTEN_TO_GPL 执行是否成立 | **事实层面成立**：代码反转、重打包、六份文档逐字节比对、向导实拍、证据链均为真 |
| 能否保持 `closed_with_limitations` | **不能以现状无条件保持**；P0 修正 + 重新打包 + 重新比对后可保持（详见 §6） |

一句话：方向与代码反转是对的，产物哈希/实拍/证据也都对得上；**但随包许可文档没有真正改干净**——`NOTICE.md`、`THIRD_PARTY_LICENSES.md`、`LICENSE_AUDIT.md` 仍残留“models = AGPL-3.0 / 权重待核实 / 两变体许可不同”的旧表述，且这三份文件就在新 `setup.exe` 内。按本卡自己的 P0 口径（随包许可文档与实物矛盾 = 虚假合规披露），这是发布前必须处置的 P0。

---

## 1. 八项逐条判定

| # | 检查项 | 实测结论 | 判定 |
|---|---|---|---|
| 1 | 上游声明是否被记录（URL + 抓取日期 + 引文） | 三项权重各 2–4 条来源，均含 URL/`fetched`/`quote`；抽核 2 条直连 URL + 2 个镜像均确认为 Apache-2.0；AI Studio 与 Roboflow 未能独立复核（见 §3） | **PASS（附注）** |
| 2 | 本地“不可自证”是否成立 | 独立扫描：三项 ONNX 对 `apache`/`license`/`ultralytics`/`agpl` 命中 **0**；`MIT`/`GPL` 命中全是浮点二进制噪声；文件字节数/完整 sha256 与台账一致 | **PASS** |
| 3 | 代码反转是否自洽 | `package.ps1:160` 恒为 `GPL-3.0-or-later`；`:108` 清单含 `LICENSE-Apache-2.0.txt`；`build-installer.ps1:205-233` 三条 fail-closed 均在 | **PASS** |
| 4 | 防回归是否有效 | 只在**安装器阶段**、且只靠 `THIRD_PARTY_LICENSES.md` 文本行拦；`package.ps1` 已先产出错误的 `VERSION.json` 和 zip；文档记载的“改回 AGPL”路径被 `build-installer.ps1:206` 死锁 | **PARTIAL（P1-2）** |
| 5 | 产物核验（6 份文件 + NOTICE 表述） | 6/6 `SAME=True`；`VERSION.json` 与证据 sha256 相同；**但 NOTICE 内容仍有 AGPL 残留** | **PARTIAL（P0-1）** |
| 6 | 实拍与文档一致 | 欢迎页显示 `GPL-3.0-or-later`；许可页顶端清单含 `LICENSE-Apache-2.0.txt` | **PASS** |
| 7 | 门禁与诚实性 | `check.ps1 -TaskPath ...` → `PASS (3 warnings)` / `EXIT=0`；卡面写了 Apache 是上游声明、不做法律认定、未签名、条件 4 仍需证书 | **PASS（附 P2-4）** |
| 8 | 是否越界 | `STATUS`/`REBASELINE_PLAN`/`TASK_LEDGER` 零 diff；`Technical Gate=NOT_SATISFIED` 未变；条件 3 关闭文档未动；19 条 Canonical Evidence blob 全中；旧 stage/旧 exe 字节未覆盖 | **PASS** |

---

## 2. Findings

### P0-1（发布阻塞）随包三份许可文档仍残留“models = AGPL / 待核实”表述，与 GPL-3.0-or-later 结论矛盾

**实测值（仓库 worktree，且已由 7z 证实在 `setup.exe` 内逐字节相同）：**

- `NOTICE.md:37`：
  `| rtdetr-v2-fixed / manga-ocr encoder+decoder 权重 | 见 THIRD_PARTY_LICENSES.md §3 | **待核实**（保守按 AGPL-3.0 声明整包） | ... | 待一手核实 |`
- `NOTICE.md:45`：
  `**当前 models 变体随包的 3 个 ONNX 权重上游许可均未一手核实，故按保守策略整包声明 AGPL-3.0。**`
- `NOTICE.md:52`：仍写“包内这 **4 个**文件必须与仓库根逐字节一致”，漏 `LICENSE-Apache-2.0.txt`（实际 5 份）。
- `THIRD_PARTY_LICENSES.md:54-56`：仍在“**发行后果（强制）**”写
  “**models** 变体包含上述 AGPL-3.0 权重 → **该发行包整体按 AGPL-3.0 分发**；……**base** 变体不含任何模型权重 → 仍按 **GPL-3.0-or-later** 分发”
  —— 与同文件 `:42-47`“两个变体都按 GPL-3.0-or-later”直接冲突，也构成“两变体许可不同”的旧表述。
- `LICENSE_AUDIT.md:22-24` 的权重表仍逐行写“**待核实**”，而同文件 `:27-28` 已写“三项上游均声明 Apache-2.0”；`:12-14` 仍写“随包文件（base 与 models 均含，**4 项**）”，清单中没有 `LICENSE-Apache-2.0.txt`。

**文档值 vs 实测值：**

| 文档值 | 实测值 |
|---|---|
| 卡面 `LICENSE-VARIANT-DECLARATION-1.md:202`：“文档三份……**全部同步**” | 三份都还有旧表述，未同步干净 |
| 包级声明 `VERSION.json.license = GPL-3.0-or-later` | `NOTICE.md:37/:45` 仍称 models 整包 AGPL-3.0 |
| `VERSION.json.license_files` = 5 项（含 Apache） | `LICENSE_AUDIT.md:12-14` 仍称 4 项 |

**影响**：`NOTICE.md` 就是 NSIS 许可页的正文来源（`build-installer.ps1:167-173` 由 stage 的 `NOTICE.md` 生成 `license-page.txt`）。接收者在安装向导里滚动许可页，会同时看到“两变体均为 GPL-3.0-or-later”和“models 整包按 AGPL-3.0 声明”。这是随包许可文档自相矛盾；虽然方向上属于“过度声明”（不是把 AGPL 权重藏在 GPL 声明下的漏声明），但按本卡 `:42` 的既定口径（随包文档与实物矛盾 = P0 发布阻塞、虚假合规披露），仍应判 P0。

**命令：**
```powershell
Select-String -Path NOTICE.md -Pattern '待核实|AGPL-3.0 声明整包|4 个文件'
Select-String -Path THIRD_PARTY_LICENSES.md -Pattern '整体按 AGPL-3.0 分发|仍按.*GPL'
Select-String -Path apps/desktop-avalonia/docs/LICENSE_AUDIT.md -Pattern '待核实|4 项'
7z x <setup.exe> -o<tmp> NOTICE.md THIRD_PARTY_LICENSES.md LICENSE_AUDIT.md
# 抽出文件与仓库根 sha256 全部 SAME=True（见 §5）
```

---

### P1-1 新增的 `RELEASE-GATE4-EXECUTION-CHECKLIST-2026-11-17.md` 仍把条件 4 绑定到 AGPL 旧包

**实测：** 该文件在 `49d1486b1` 与本轮一起新增，但 §1 “已就绪的输入”写的是旧状态：

- `:24` `包级声明 license = AGPL-3.0（保守）`
- `:25` `NewManga-0.1.1-setup.exe 652,150,501 B / sha256 23c04abd…（未签名）`
- `:26` 向导文案“按 AGPL-3.0 分发”
- `:27` 包内合规文件列 4 份

而本轮实际产物是 `652,037,404 B / sha256 6f9a45f3… / license=GPL-3.0-or-later`（`verification/WEIGHTS-LICENSE-PROVENANCE-1/ac2-installer-build-info.json:9-11,26-30`），且同一文件 `:111` 自己写着“**不得**把旧包……的矩阵结果移花接木到新包”。该清单是将来拿到证书后执行条件 4 的唯一操作手册，按现状会把签名/矩阵绑定到错误的旧字节。

**命令：**
```powershell
Select-String -Path doc/reviews/RELEASE-GATE4-EXECUTION-CHECKLIST-2026-11-17.md -Pattern 'AGPL-3.0|652,150,501|23c04abd'
```

---

### P1-2 防回归拦截太晚（只在安装器阶段、且只靠文档文本），并死锁文档写明的“改回 AGPL”路径

按“在 sidecar 放回 `yolo11s-seg.onnx`”逐步推演：

1. `package.ps1:160` 恒写 `license=GPL-3.0-or-later`；`:164-165` 把**当前实际存在的所有 ONNX**一律描述成
   `Apache-2.0 upstream declaration for <files>`；`:178` 写 `VERSION.json`；`:188-190` 直接生成 zip。
   **package.ps1 不运行任何权重许可/身份校验**（grep 无 `verify-package-manifest` 调用），stage 与 zip 在此已经错误。
2. `build-installer.ps1:152` 调 `verify-package-manifest.ps1`，但该护栏 `:124-137` 只核对 onnx 数量/字节与 `VERSION.json` 是否自洽，**不含许可判断** ⇒ 会放行。
3. `build-installer.ps1:205-233` 才会检查：`:206` 要求 `license=GPL-3.0-or-later`（放行）；`:219` 取 `THIRD_PARTY_LICENSES.md` 中匹配该权重路径/文件名的第一行；`:223` 该行不得含“待核实”；`:226-227` 该行必须含 `Apache-2.0`。
   以当前文档，`yolo11s-seg.onnx` 行（`THIRD_PARTY_LICENSES.md:36`）写的是 `AGPL-3.0（Ultralytics）已核实` ⇒ **停在 `:227` throw**。
4. 但这是**文本检查，不是权重身份检查**：没有 ONNX 哈希/身份 allowlist；若有人把该行改成 `Apache-2.0`（或换名后新增一行），即可通过。反过来，若维护者按文档 `NOTICE.md:26`/`THIRD_PARTY_LICENSES.md:47` 的指示“重新打入 AGPL 权重时把 `package.ps1` 判定改回 AGPL”，则 `:206` 仍硬性要求 GPL ⇒ **合法 AGPL 包反而无法构建**，而文档没有要求同时改 `build-installer.ps1`。

**结论**：当前唯一有效拦截是 `build-installer.ps1:226-227`，它发生在 `package.ps1` 已产出错误 `VERSION.json` + zip 之后，且依赖文档未被改错。如实记为 **P1**（不是“完全拦不住”，但拦得晚、拦得软）。

**命令：**
```powershell
Select-String -Path apps/desktop-avalonia/scripts/package.ps1 -Pattern 'licenseDeclaration|bundledWeightsLicense|Compress-Archive'
Select-String -Path apps/desktop-avalonia/scripts/build-installer.ps1 -Pattern 'TIGHTEN_TO_GPL|Apache-2\\.0|must be GPL'
```

---

### P2-1 `LICENSE-Apache-2.0.txt` 不是 Apache-2.0 的完整官方文本（缺 APPENDIX）

**实测：** 仓库文件 10,174 B / 177 行，正文在 `END OF TERMS AND CONDITIONS` 结束；与 `https://www.apache.org/licenses/LICENSE-2.0.txt`（11,358 B）做空白归一化后，仓库文本是官方文本的**严格前缀**，缺少其后 **1,092 字符**的 `APPENDIX: How to apply the Apache License to your work…`。另：文件以空行开头（首字节 `0a`，无 BOM）。

条款 1–9 本身完整，APPENDIX 通常被视为操作说明而非许可条件；但 `NOTICE.md:8`、`THIRD_PARTY_LICENSES.md:45`、`LICENSE_AUDIT.md:10` 均称“Apache-2.0 **全文**”，表述不准确。记 **P2**。

**命令：**
```powershell
python - <<'PY'
import re
a=re.sub(r'\s+',' ',open('LICENSE-Apache-2.0.txt',encoding='utf-8').read()).strip()
b=re.sub(r'\s+',' ',open('apache2-canonical.txt',encoding='utf-8').read()).strip()
print(len(a),len(b),b.startswith(a),b[len(a):][:80])
PY
```

---

### P2-2 `installer.nsi` 两处文案仍带 AGPL 痕迹

- `installer.nsi:68`：`!error "... (-DVARIANT_LICENSE=AGPL-3.0|GPL-3.0-or-later)"` —— 反转后 AGPL 已不是任何受支持 stage 的合法值（含权重时 `build-installer.ps1:206` 必 throw），提示语仍在推荐 AGPL。
- `installer.nsi:80`：`LegalCopyright` 仍写 `see LICENSE and LICENSE-AGPL-3.0.txt`，未提 `LICENSE-Apache-2.0.txt`。

不影响功能，记 **P2**。

---

### P2-3 未找到 base 变体的重打包证据

`49d1486b1` 的产物证据只覆盖 models 变体（`ac2-*`）；`G:\CODEX\New Manga.workspace\tmp\r27` 下只有两个 models 尺寸的 setup：

| 文件 | 字节 | 时间 |
|---|---|---|
| `tmp\r27\inst\NewManga-0.1.1-setup.exe` | 652,215,597 | 2026-11-17 23:56:44 |
| `tmp\r27\inst2\NewManga-0.1.1-setup.exe` | 652,037,404 | 2026-11-18 00:04:07 |

ZCode 第三次裁定 Q3 写的是“重打 **models/base 双包**”。若 base 安装包仍在发布集内，旧 base 包会携带旧 `NOTICE.md` 且缺少 `LICENSE-Apache-2.0.txt`。本次未找到 base 的新产物或新取证，记 **P2**（需 DSH 确认 base 是否属于本轮发布集）。

---

### P2-4 卡面元数据与一处“过度声明”

- 卡面 front matter `delivery_head: 02c3aaeda`、`integration_commit: null` 仍是 AGPL 轮次的值，未登记 `49d1486b1` / `f475ea155`。
- `LICENSE-VARIANT-DECLARATION-1.md:202` 称“文档三份……全部同步”，与 P0-1 的实测不符。
- `:209` 防回归只说“把 `NOTICE.md` 变体表 + `package.ps1` 判定改回 AGPL”，未提 `build-installer.ps1:206` 也必须改（见 P1-2）。

记 **P2**（簿记/表述；不影响本轮代码与产物事实）。

---

## 3. 上游声明与 URL 抽核

`verification/WEIGHTS-LICENSE-PROVENANCE-1/weights-licenses.json` 结构满足“三项权重各至少一条 URL + 抓取日期 + 引文”：

| 权重 | 来源数 | 抓取日期 | 声明 |
|---|---|---|---|
| `models/detector/rtdetr-v2-fixed.onnx` | 4 | 2026-11-17 | Apache-2.0 |
| `models/ocr/manga-ocr-onnx/encoder_model.onnx` | 3 | 2026-11-17 | Apache-2.0 |
| `models/ocr/manga-ocr-onnx/decoder_model.onnx` | 2 | 2026-11-17 | Apache-2.0 |

**我的独立抽核（`web_fetch`）：**

| URL | 结果 | 实际文本 |
|---|---|---|
| `https://raw.githubusercontent.com/NixOS/nixpkgs/release-25.05/pkgs/development/python-modules/manga-ocr/default.nix` | HTTP 200 | `license = licenses.asl20;`（与 JSON 引文一致） |
| `https://kornia.readthedocs.io/en/v0.7.2/models/rt_detr.html` | HTTP 200 | `Licence: Apache 2.0`（与 JSON 引文一致） |
| `https://repo.model.xfyun.cn/kha-white/manga-ocr-base/raw/commit/1d0bb748.../README.md` | **fetch failed（TypeError）** | **未能独立复核该 URL** |
| `https://hf-mirror.com/kha-white/manga-ocr-base/raw/main/README.md`（同一模型卡镜像） | HTTP 200 | `license: apache-2.0` |
| `https://huggingface.co/PekingU/rtdetr_r50vd` | **fetch failed（TypeError）** | **未能独立复核该 URL** |
| `https://hf-mirror.com/PekingU/rtdetr_r50vd`（同一模型卡镜像） | HTTP 200 | `License: apache-2.0` |
| `https://aistudio.baidu.com/modelsdetail/273?modelId=273` | HTTP 200，但正文为 JS 壳 | 只取到标题，**未能独立复核 license 字段** |
| `https://playground.roboflow.com/models/baidu/rt-detr` | HTTP 429（Vercel 人机检查） | **未能独立复核该 URL** |

结论：台账的记录方式成立；两条直连 URL 与两个镜像独立证实了 Apache-2.0 声明。AI Studio 与 Roboflow 的“未能独立复核”按任务要求如实登记，不把 JSON 自述当作已核实。

---

## 4. 三项 ONNX 的独立字节扫描

对 `G:\CODEX\New Manga.workspace\tmp\r24\sidecar-models\models\` 下三个文件做**不解析 protobuf** 的原始字节、大小写不敏感扫描（分块 8 MiB，重叠 128 B）：

| 文件 | 字节 | MIT | GPL | Apache | license | Ultralytics | AGPL | GNU |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `rtdetr-v2-fixed.onnx` | 171,618,071 | 15 | 18 | **0** | **0** | **0** | **0** | 14 |
| `encoder_model.onnx` | 343,454,249 | 35 | 33 | **0** | **0** | **0** | **0** | 27 |
| `decoder_model.onnx` | 117,480,262 | 9 | 6 | **0** | **0** | **0** | **0** | 6 |

**命中样本（全部是浮点/二进制噪声，无可读句子）：**

- `rtdetr` @6176940：`\xda\xbb\x01\xa4];MIT<\xe1NG=\x89`
- `rtdetr` @38892438：`\xfe\xbcgPL<FH\xb2<\xd2\xd4F\xbc\xd5`
- `encoder` @15130306：`\xae<\xf7\xc0\x83;MIT;\xdcKD<[`
- `encoder` @221608421：`#<\xf8D/<gpL<>\xf0D<\xce`
- `decoder` @21086125：`\x86=H5`<Gpl<F\xc2\xd4<\x0c`

**与 `ac1-onnx-metadata-probe.log` 的差异**：日志记 7/10/4 条“MIT/GPL”命中；我用大小写不敏感子串得到 33/68/15 条。日志没有记录其精确匹配器，我无法逐条复现其计数；但两边的样本在同一批偏移上重叠（如 6176940、17326061、39928078、87578250、105119047、105593451），且**都呈现为二进制字节中的 3 字母片段**。更关键的是：三项文件对 `apache`、`license`、`ultralytics`、`agpl` 的命中均为 **0**。因此“无可读许可元数据、命中全是二进制噪声”这一结论**成立且被更强的证据支持**。

文件身份核对：

| 文件 | 字节 | sha256（完整） | 与台账 |
|---|---:|---|---|
| `rtdetr-v2-fixed.onnx` | 171,618,071 | `c7fb5af1a8982416b56955e621c1b10397730807956998066e2fbc132c77bbc3` | 与 `THIRD_PARTY_LICENSES.md:37` 一致 |
| `encoder_model.onnx` | 343,454,249 | `15fa8155fe9bc1a7d25d9bb353debaa4def033d0174e907dbd2dd6d995def85f` | 一致 |
| `decoder_model.onnx` | 117,480,262 | `ef7765261e9d1cdc34d89356986c2bbc2a082897f753a89605ae80fdfa61f5e8` | 一致 |

---

## 5. 新 `setup.exe` 六份文件比对

**被测产物**：`G:\CODEX\New Manga.workspace\tmp\r27\inst2\NewManga-0.1.1-setup.exe`
**实测**：`bytes=652,037,404`，`sha256=6f9a45f32ea3450efcfb565fe83db25ee98ed6345934c2c183f86c9208283f08`（与 DSH 记录、`ac2-installer-build-info.json` 完全一致）。

`7z x` 抽出六份后与仓库根逐一 `Get-FileHash SHA256`：

| 文件 | exe 内 sha256 | 仓库 sha256 | SAME |
|---|---|---|---|
| `NOTICE.md` | `2afb0fd22c2004269cd728220d5d5a7318bbc31c6383fe503e8b21ff419fe597` | 同左 | **True** |
| `THIRD_PARTY_LICENSES.md` | `66e4058e952a1a8ccf776c7217a5ef42c617c9302c138dea8464e318561b09e4` | 同左 | **True** |
| `LICENSE_AUDIT.md` | `0bf2bcc04d260f94ec089dd4ee0f6ea37bca5df860b0277e6e4b5ba84e164866` | 同左（`apps/desktop-avalonia/docs/`） | **True** |
| `LICENSE` | `fb981668c18a279e285fc4d83fba1e836cc84dd4daa73c9697d3cfd2d8aca6e0` | 同左 | **True** |
| `LICENSE-Apache-2.0.txt` | `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594` | 同左 | **True** |
| `LICENSE-AGPL-3.0.txt` | `e0eedba615d5cd1b986afb6c5b3a4b1ae33713e7e9dc74d19daec5e3221f9d2e` | 同左 | **True** |

包内 `VERSION.json`：`variant=models`、`license=GPL-3.0-or-later`、`models_bundled=true`、`models_bundled_bytes=632,552,582`、`license_files` 5 项（含 Apache）；其 sha256 `d6ad3b8ee284338596975509563b8dd6753427f98c7a34cabc2d6579f545ed31` 与 `ac2-models-version-gpl.json` 完全相同。

**结论**：六份文件逐字节一致；但一致性恰恰证明 P0-1 的旧表述随包发行，而不是被排除在包外。

---

## 6. 两个问题的明确回答

### 6.1 TIGHTEN_TO_GPL 的执行是否成立？

**成立（事实层面）。** 依据：

1. `package.ps1:160` 无条件 `$licenseDeclaration='GPL-3.0-or-later'`；`:108` 清单加入 `LICENSE-Apache-2.0.txt`。
2. `build-installer.ps1:205-233` 的三条 fail-closed 均在：`:206` 含 ONNX 必须 GPL；`:219-228` 该权重行不得“待核实”且须含 `Apache-2.0`；`:230-233` stage 必须有 Apache 副本。
3. 新 `setup.exe` 的大小/sha256、包内 `VERSION.json`、六份文档逐字节比对、欢迎页/许可页实拍全部与 DSH 记录一致；19 条 Canonical Evidence blob 全中。
4. 上游声明台账结构完整，抽核的 nixpkgs / Kornia 直连 URL 与两个 HF 镜像均确认 Apache-2.0；本地 ONNX 确无可读许可元数据。
5. 未越界：`STATUS`/`REBASELINE_PLAN`/`TASK_LEDGER` 零 diff，`Technical Gate=NOT_SATISFIED` 未动，旧 stage/旧 exe 字节未覆盖。

**但“执行成立”不等于“包可以发”**：P0-1 使随包许可文档仍自相矛盾。

### 6.2 能否保持 `closed_with_limitations`？

**不能以现状无条件保持。** 理由：`closed_with_limitations` 的前提是“限制已如实登记且不冒充完成”；而当前随包 `NOTICE.md` 在安装向导许可页里仍称 models 整包 AGPL-3.0，属于本卡自己定义的“随包文档与实物矛盾 = P0 发布阻塞”，不能仅当作限制保留。

**处置后可保持**：先把 P0-1（三份文档的 AGPL 残留 + 4 项清单）改成与 GPL 结论一致，重新 `package.ps1 -WithModels` + `build-installer.ps1` 出包，重做六份比对与两张实拍，并在卡面把 P1-1（Gate4 清单）、P1-2（防回归）登记为 limitation；完成这些后，可以保持 `closed_with_limitations`。在此之前，新 `setup.exe` 不得作为发布候选，也不得作为条件 4 的取证对象。

---

## 7. 门禁原始输出

```text
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\LICENSE-VARIANT-DECLARATION-1.md
WARN: 存在 2 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3160 bytes / 28 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6724 bytes / 64 lines
Governance check: PASS (3 warnings)
EXIT=0
```

卡面诚实性抽查：`:208` 明写“Apache-2.0 是上游声明、本仓库不做法律认定”；`:210` 明写“`setup.exe` 仍未签名”；`:211` 明写“条件 4 仍需真证书”。三项均在。

---

## 8. 边界声明

**本复核不构成产品发布验收，也不构成对上游许可的法律结论。** 本报告只核对仓库字节、产物字节、外部页面文本与命令输出；不判定 Apache-2.0 / GPL-3.0 / AGPL-3.0 的法律适用，不改变 `Technical Gate=NOT_SATISFIED`，不宣布条件 3/4 通过，也不替代 DSH 的 findings 处置与集成验证责任。复核期间未修改仓库文件、未提交/推送/checkout、未改动 workspace 内既有 stage/fixture。
