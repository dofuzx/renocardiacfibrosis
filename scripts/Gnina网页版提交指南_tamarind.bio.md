# Gnina 网页版提交指南（tamarind.bio）— 替代 WSL 路线

> 适用场景：你已在 https://app.tamarind.bio 注册，想用网页托管的 GNINA（CNN 集成打分）做独立交叉验证，
> 而不想在本地装 WSL + 官方 Linux 二进制。
> 本指南与 `B级操作_Gnina 3D-CNN重打分_手把手教程.md`（WSL 路线）二选一即可。

---

## 〇、先讲清一个关键限制（务必读）

**网页版 GNINA 不支持“上传自己预先算好的 pose 做残分（--score_only）”。**
它只接受「受体 PDB + 配体」，做**完整对接**（自带 Monte Carlo 采样 + CNN 重打分），不允许你喂入已有的 pose。

➡️ **所以网页路线的证据逻辑与最初设想略有不同，但反而更强：**
让一个**完全独立**的深度学习对接引擎（GNINA，CNN 集成，与 Vina/Smina 经验力场零共享）把 kaempferol **重新**对接进 CYP1B1，
看它的 **CNN 最优 pose** 是否和我们的 AutoDock Vina / Smina pose 落在**同一口袋、亚 2 Å 重合、相同热点残基**。
这就是审稿人要的「跨方法学家族」级证据。

---

## 一、已为你准备好的上传材料（都在 `D:\docking\`）

| 文件 | 用途 | 说明 |
|---|---|---|
| **`receptor_upload.pdb`** | 受体（必传） | 3PM0 蛋白 + **HEM（血红素）**；已移除共晶配体 ANF 与结晶水，避免与 kaempferol 冲突 |
| `receptor_upload_noHEM.pdb` | 受体（备用） | 仅蛋白，不含 HEM。**仅当网页报错“无法处理 HEM”时使用** |
| **`kaempferol_smiles.txt`** | 配体（主用） | 里面是 kaempferol 规范 SMILES：`Oc1ccc(cc1)c1oc2cc(O)cc(c2c(=O)c1O)O`（InChIKey `IYRMWMYZSQPJKC`） |
| **`kaempferol_sdf_rdkit.sdf`** | 配体（备选文件） | **推荐用这份**：RDKit 标准 3D 构象（21 重原子/31 总/23 键），已验证可被 gnina 底层解析器正常读出 1 个分子 |
| `kaempferol.sdf` | 配体（旧版，勿用） | 手工坐标版，**已被 RDKit 验证解析为 0 分子（格式隐患）**，请勿上传 |
| `reference_ANF.pdb` | 备用（本页用不到） | 共晶 ANF 坐标。⚠️ **本 GNINA 网页工具没有“参考配体 / Reference ligand”上传框**（已核实），此文件在当前平台暂不使用；仅在支持该框的本地/其他平台才有用 |

> ⚠️ 本工具页**只有 Receptor + Ligand + 参数**，没有参考配体框。平台在缺省时会**自动以受体为中心做“全蛋白自动建框”（whole-protein autoboxing）**。这会降低精度（GNINA 文档：全蛋白重对接 Top1 ≈31–38%，口袋定义≈58–73%），但仍是有效的独立证据；若页面另有“Box center / 搜索区域”手动输入项，**优先填入我们原 Vina 框：中心 −18.345 / 21.502 / −19.818，边长 24 Å**，即可精确锚定 CYP1B1 口袋。

---

## 二、网页提交步骤（逐步）

1. **登录** https://app.tamarind.bio → 进入 **GNINA** 工具（Tools 列表里找 GNINA，或你注册时看到的入口）。
   页面标题大概显示 “GNINA · AutoDock Vina with CNN scoring · Rescore”。

2. **Receptor（受体）**：点击上传，选 `D:\docking\receptor_upload.pdb`。
   - 格式要求：PDB / ENT，≤ 50 MB。我们这份 300 KB，完全没问题。
   - 网页会用 PDB2PQR 自行把 PDB 转成 pdbqt 并加电荷，不用你操心。
   - **若提交后报错提到 HEM / heme / unknown residue** → 改用 `receptor_upload_noHEM.pdb` 重传。

3. **Ligand（配体）**：**二选一**
   - 优先：在 **SMILES** 输入框里粘贴 `kaempferol_smiles.txt` 里的字符串：
     ```
     Oc1ccc(cc1)c1oc2cc(O)cc(c2c(=O)c1O)O
     ```
   - 若网页只给“上传文件”不给 SMILES 框 → 上传 **`kaempferol_sdf_rdkit.sdf`**（不要用旧 `kaempferol.sdf`，它会被解析成 0 分子）。
   - 注意：SMILES/3D 构象都由网页自行嵌入并重新采样，不影响结果。

4. **搜索框（无参考配体框时的处理）**：本工具页**没有 Reference ligand 上传项**，平台会自动以受体做“全蛋白自动建框”。
   - 若页面另有 **“Box center / Search region / 自定义框”** 手动输入项 → **强烈建议手动填入我们原 Vina 框**，精确锚定 CYP1B1 口袋：
     - Center X/Y/Z：`−18.345` / `21.502` / `−19.818`
     - Size（边长）：`24` Å（X/Y/Z 都填 24）
   - 若页面**完全没有任何框设置项**（只能全蛋白建框）→ 直接提交即可。CYP1B1 的血红素口袋是该蛋白最深的位点，kaempferol 大概率仍落在此处；若 top CNN pose 与 Vina pose 的 RMSD 偏大（>2 Å），属全蛋白盲对接的正常偏差，我们如实报告“CNN 确认同一口袋但构象略有偏移”即可，不强制 ≤2 Å。

5. **参数**（保持默认即可，不必改）：
   - Scoring function：**Vina**（默认）
   - CNN scoring mode：**Rescore**（默认，即“Vina 采样 + CNN 重排”）
   - Exhaustiveness：默认 8（想更稳可设 16，更贴近我们本地设置）
   - Number of poses：默认（保存多 pose，输出 9 个 mode）
   - Random seed：默认或填 42（与我们本地一致，便于复现）
   - CNN rotations / CNN Score：保持默认

6. **提交**：点 **“Submit job”**。
   - 计费：约 **20 credits/次**（你注册账号应有额度）。
   - 预计耗时：kaempferol 是小分子，通常 **30 秒 ~ 几分钟**（页面标注 <1–65 min 是上限）。

7. **下载结果**（关键！）：任务完成后页面给出
   - **3D 视图** + 可排序的**打分表（CSV）**：每行一个 pose，含 `CNNscore`、`CNNaffinity`、`Vina(经验分)`。
   - **排好序的 poses SDF**（点 “Download SDF”）。
   - **GNINA log**。
   - 👉 **把下面两样存回 `D:\docking\` 并发给我**：
     1. 排序后的 poses 文件（SDF 或 CSV 都可，最好要 **top pose 的 3D 坐标**）；
     2. 打分 CSV（含 CNNscore / CNNaffinity 数值）。
   - 我会立刻算 **GNINA top pose 与我们 Vina best pose 的 RMSD + 接触残基交集**，并据此生成 **v24**（S9 加 Gnina 列、§2.8/§3.5 补段、补 Gnina 引用）。

---

## 三、写稿件时的两条铁律（与 Smina 一致）

1. **分数方向相反**：`CNNscore` / `CNNaffinity` **越高越好**（0–1 / pK 尺度）；
   而 Vina / Smina 输出 **越负越好（kcal/mol）**。两者量纲、含义完全不同。
2. **绝不可跨程序比亲和力数值**。被验证的量是：
   > “一个独立的深度学习对接方法（GNINA CNN 集成）也把 kaempferol 放入了**同一口袋**，其 CNN 最优 pose 与 AutoDock Vina/Smina pose 的 **RMSD ≤ 2 Å**，且**热点残基一致**。”
   证据在 **pose 可复现性 + 残基同一性**，不在能量大小。

---

## 四、预期结果与话术模板（拿到网页数值后填）

当 GNINA top pose 与 Vina best pose 的 RMSD ≤ 2 Å 且热点残基一致时，可在 §3.5 这样写（占位符待填真实值）：

> *An independent deep-learning docking engine (GNINA 1.3.3; CNN ensemble rescoring, McNutt et al., 2021) re-docked kaempferol into CYP1B1. The top CNN-ranked pose superposed with the AutoDock Vina/Smina pose within **X.XX Å** (heavy-atom RMSD) and shared the identical hotspot residues (Asp326, Phe134, Phe231, Phe268, Thr325, Thr334, Asp333, Ile399, Leu509), with a CNNscore of **0.XX**, confirming pose robustness across empirical and learned scoring families.*

> 注：GNINA 1.3.3 引用（已联网核实）：McNutt AT, Francoeur P, Aggarwal R, et al. *GNINA 1.0: molecular docking with deep learning.* J Cheminform. 2021;13(1):43. doi:10.1186/s13321-021-00522-2.

---

## 五、故障速查

| 现象 | 处理 |
|---|---|
| 受体上传后报 “unknown residue HEM / heme” | 改用 `receptor_upload_noHEM.pdb`（仅蛋白）。代价：失去 HEM 相互作用，pose 可能略偏，但口袋位置由 ANF 参考配体锚定 |
| 没有“参考配体”上传项 | 选 Whole-protein autoboxing；RMSD 可能偏大，如实报告即可 |
| 只给 SMILES 框、不要文件 | 直接粘 `kaempferol_smiles.txt` 内容 |
| 结果 CNNscore 偏低（<0.8） | 正常现象（交叉对接本就更难）；只要 top pose 与 Vina pose ≤2 Å 即达标 |
| 网页跑太久 / credits 不足 | 默认参数下小配体通常 <5 min；credits 不够联系平台或改用 WSL 路线（`B级操作_Gnina 3D-CNN重打分_手把手教程.md`） |

---

## 六、★★ 本次运行报错修正（"0 molecules converted"）

你贴的日志关键行：
```
Commandline: ... gnina -r receptor.pdb -l ligand.sdf --autobox_ligand receptor.pdb ...
0 molecules converted
docked-complex merge skipped: receptor or ligand contains no atoms
```

### 根因（已用 RDKit 实测定位）
1. **`0 molecules converted` 的真正原因 = 配体 SDF 解析失败**，不是框填错。我用 RDKit 实测：旧的 `kaempferol.sdf` 被解析器读成 **0 个分子**（手工坐标版有格式隐患），而新 `kaempferol_sdf_rdkit.sdf` 读成 **1 个分子**。gnina 底层 OpenBabel 同样会拒读旧文件 → 配体缺位 → 0 分子。
2. **`--autobox_ligand receptor.pdb` 是平台自动加的，并非你填错**：本工具页**根本没有 Reference ligand 上传框**。平台在缺省时自动以受体做“全蛋白自动建框”（whole-protein autoboxing），命令行里才会看到 `--autobox_ligand receptor.pdb`。这属于正常 fallback，不影响提交。

### 修正后的字段对照表（重新提交时照抄）

| 网页字段 | 正确内容 | 说明 |
|---|---|---|
| **Receptor（受体）** | 上传 `receptor_upload.pdb` | 蛋白+血红素，已移除共晶配体 |
| **Ligand（配体）** | **SMILES 框粘 `kaempferol_smiles.txt`**；或上传 **`kaempferol_sdf_rdkit.sdf`** | ❌ 不要再用旧 `kaempferol.sdf`（解析为 0 分子） |
| **搜索框 / Box** | 若有手动框输入 → 中心 `−18.345/21.502/−19.818`、边长 `24`；若无 → 留空（平台全蛋白自动建框） | 本页无参考配体框，`reference_ANF.pdb` 暂不用 |

### 配体文件已升级
- ❌ 旧 `kaempferol.sdf`（手工坐标，RDKit 验证解析为 0 分子）→ **勿用**。
- ✅ 新增 **`kaempferol_sdf_rdkit.sdf`**（RDKit ETKDGv3 + UFF 优化，21 重原子/31 总/23 键，标准 V2000 块，已验证 3D 可读）→ **推荐上传此份**。
- 若网页只给 SMILES 输入框（无文件上传），直接用 `kaempferol_smiles.txt` 内容即可，连文件都不用传，最省事。

### 重新提交后应看到的日志（对照判断是否成功）
```
1 molecules converted        ← 不再是 0（说明配体解析成功）
...
Affinity: -X.XX (kcal/mol)  ← 出现这行就成功了
CNNscore: 0.XX
```
> 注意：因本页无参考配体框，命令行里仍会看到 `--autobox_ligand receptor.pdb`（全蛋白自动建框），这是正常的，不必惊慌。
