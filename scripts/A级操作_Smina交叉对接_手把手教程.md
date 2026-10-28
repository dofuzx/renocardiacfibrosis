# A 级操作：Smina 交叉对接 —— Windows 手把手教程

**目标**：用与 Vina 不同的打分函数（Vinardo）在同一 grid、同一配体准备流程下重对接 kaempferol–CYP1B1（3PM0），
把 top pose 与原 Vina pose 比较重原子 RMSD，作为"pose 可复现"的独立证据。
**预计耗时**：安装 30–40 min，运行 10–20 min。

---

## Step 0 — 先备齐 4 样东西（最关键，别跳过）

在原来的 docking 工作目录里找到并记下：

| 需要的东西 | 通常是 | 怎么找 |
|---|---|---|
| ① 受体 pdbqt | `3PM0_prot.pdbqt`（去除 ANF 与水、保留 HEM） | 找 `*.pdbqt`，排除配体文件 |
| ② 配体 pdbqt | `kaempferol.pdbqt`（Gasteiger 电荷） | 同上 |
| ③ grid 中心与大小 | `center_x/y/z`、`size_x/y/z = 24 24 24` | 若当初用了配置文件（如 `vina_config.txt` / `conf.txt`），直接打开它；若是命令行跑的，翻终端历史 |
| ④ 原 Vina 最佳 pose | best pose 的 `pdbqt` 或 `sdf` | 若已删除，可用 Vina 用原参数重跑一次生成 |

> 把这 4 个文件**复制**（不要移动）到一个新目录，例如 `D:\docking\smina_check\`：
> ```
> mkdir D:\docking\smina_check
> copy 3PM0_prot.pdbqt D:\docking\smina_check\
> copy kaempferol.pdbqt   D:\docking\smina_check\
> copy vina_best.pdbqt    D:\docking\smina_check\
> ```
> ⚠️ 只复制、不移动、不覆盖原文件；原目录保持原样。

---

## Step 1 — 安装 smina（Windows 原生，conda-forge 提供 win-64）

打开 **Anaconda Prompt**（或 Miniforge Prompt），逐行执行：

```bat
conda config --add channels conda-forge
conda config --set channel_priority strict
conda create -n dockx python=3.11 -y
conda activate dockx
conda install -c conda-forge smina rdkit -y
```

验证：

```bat
smina --version
smina --help | findstr /i scoring
```
能看到 `--scoring` 且出现 `vinardo` 字样即安装成功。

### ⚠️ Miniforge 26.9.4 已知坑（2026-10-25 实测于本机）

**症状 A**：`conda create` 报
`DirectoryNotACondaEnvironmentError: The target directory exists, but it is not a conda environment`
→ 上一次 `conda create` 只留下空壳目录。先删空壳再重建：
```bat
rmdir /s /q D:\miniforge3\envs\dockx
conda create -p D:\miniforge3\envs\dockx python=3.11 -y
```

**症状 B**：`conda create` 报
`FileNotFoundError: Could not find 'share/conda-launchers/cli-64.exe' in the conda-launchers package`
→ base 环境里的 `conda-launchers` 装的是有缺陷的 `74da2fe_gcc_5` build（其 `paths_data` 为空，0 条记录），
conda 因此找不到 Windows 启动器模板。换成 `5387cfd_zig_5` build 即可（该 build 有 6 条记录）：
```bat
conda install -p D:\miniforge3 -c conda-forge --force-reinstall "conda-launchers=24.7.1=5387cfd_zig_5" -y
```

**症状 C**：`CondaValueError: You have chosen a non-default solver backend (libmamba) but it was not recognized`
→ 求解器插件未加载，改用 classic：
```bat
conda config --set solver classic
```

> 建议全程用 `-p D:\miniforge3\envs\dockx`（显式路径）代替 `-n dockx`，可绕开 env 名解析问题；
> 后续所有 `conda install` 也带同一个 `-p`。

> 如果 conda 彻底装不上（网络/频道问题），备选：装 WSL2（`wsl --install -d Ubuntu`），
> 在 Ubuntu 里 `wget https://downloads.sourceforge.net/project/smina/smina.static && chmod +x smina.static`，
> 用 `./smina.static` 替代下面所有 `smina` 命令。

---

## Step 2 — 先跑一遍 Vina 打分（基线核对，必做）

这一步不是重复劳动：用它确认 grid 中心、box 尺寸、电荷与原始 Vina 完全一致。
**如果这一步的亲和力与你原文的 −10.98 kcal/mol 接近（±0.5 内），说明参数对齐正确，才可继续。**

```bat
cd /d D:\docking\smina_check
smina --receptor 3PM0_prot.pdbqt --ligand kaempferol.pdbqt ^
      --center_x <X> --center_y <Y> --center_z <Z> ^
      --size_x 24 --size_y 24 --size_z 24 ^
      --exhaustiveness 16 --seed 42 --num_modes 9 ^
      --scoring vina ^
      --out base_vina.sdf --log base_vina.log
```
把 `<X> <Y> <Z>` 换成 Step 0 记下的坐标（`^` 是 Windows 的换行续行符，一行写完也可）。

看结果：终端/log 末尾会出现打分表，第一行 `1  -10.xx` 即最佳亲和力。

---

## Step 3 — 换 Vinardo 打分函数（A 级核心）

```bat
smina --receptor 3PM0_prot.pdbqt --ligand kaempferol.pdbqt ^
      --center_x <X> --center_y <Y> --center_z <Z> ^
      --size_x 24 --size_y 24 --size_z 24 ^
      --exhaustiveness 16 --seed 42 --num_modes 9 ^
      --scoring vinardo ^
      --out vina_vinardo.sdf --log vina_vinardo.log
```

> 可选加跑（更稳）：把 seed 换成 1、7 各跑一次，看 pose 是否稳定：
> `... --seed 1 --out vina_vinardo_s1.sdf --log vina_vinardo_s1.log`

---

## Step 4 — 计算 pose RMSD（用 RDKit，避免额外工具依赖）

把下面内容保存为 `D:\docking\smina_check\rmsd.py`：

```python
import sys
from rdkit import Chem
from rdkit.Chem import rdMolAlign, AllChem, RemoveHs

def first_mol(fn):
    if fn.lower().endswith(".sdf"):
        sup = Chem.SDMolSupplier(fn, removeHs=False)
        for m in sup:
            if m is not None:
                m = RemoveHs(m)          # 只比非氢（重）原子
                return m
        raise SystemExit("no molecule in " + fn)
    raise SystemExit("please give .sdf (got " + fn + ")")

ref = first_mol(sys.argv[1])   # 原 Vina 最佳 pose
prb = first_mol(sys.argv[2])   # Smina/Vinardo 最佳 pose
rms = rdMolAlign.GetBestRMS(prb, ref)
print("BEST_POSE_RMSD = %.3f A" % rms)
```

运行：

```bat
cd /d D:\docking\smina_check
python rmsd.py vina_best.sdf vina_vinardo.sdf
```

> 若你手上的 best pose 是 `.pdbqt`：让 smina 直接输出 `.sdf`（上面已这么做）；
> 或把原 Vina 结果用 smina 重跑得到的 `base_vina.sdf` 当作参考：`python rmsd.py base_vina.sdf vina_vinardo.sdf`。

---

## Step 5 — 判读（写进稿件的门槛）

| 判据 | 通过标准 | 含义 |
|---|---|---|
| 重原子 RMSD | **≤ 2.0 Å** | pose 可复现（与 redocking 阈值一致） |
| 亲和力量级 | 与 Vina 值同量级（如 −9 ~ −12 kcal/mol） | 打分函数间一致 |
| 关键残基交集 | 与原文 13 个接触残基有 ≥8 个重合 | 结合模式一致 |

把结果填进这张表（即稿件的 Supplementary Table S9 雏形）：

| 引擎 / 打分 | 最佳亲和力 (kcal/mol) | top-pose RMSD vs Vina (Å) | 接触残基交集 (n/13) |
|---|---|---|---|
| AutoDock Vina 1.2.7（原文） | −10.98 | — | 13/13 |
| Smina — vina（基线） |  | ~0（自比） | |
| Smina — vinardo |  |  | |

---

## Step 6 — 写进稿件（可直接套用）

**§2.8 末尾加一段**（把 X.XX / Y.Y 换成实测值）：

> "As a robustness check independent of the Vina empirical scoring function, the top pose was regenerated with
> Smina (v2020.12.10) using the Vinardo scoring function under the identical receptor preparation, grid box
> (24 × 24 × 24 Å, centred on the α-naphthoflavone centroid) and ligand preparation pipeline (Gasteiger charges;
> exhaustiveness 16; seed 42). The Vinardo top pose reproduced the Vina pose with a heavy-atom RMSD of X.XX Å and
> an affinity of Y.Y kcal/mol, and retained n/13 of the contact residues."

**局限性段保留**（不要删）：

> "Docking affinities remain protocol-dependent estimates rather than measured binding free energies."

---

## Step 7 — 常见故障速查

| 现象 | 原因 / 解决 |
|---|---|
| `smina` 不是内部或外部命令 | 没 `conda activate dockx`，或 conda 不在 PATH |
| Step 2 的亲和力与 −10.98 差 >1 kcal/mol | grid 中心或配体电荷不一致 → 回去核对 Step 0 ③ |
| 提示 box 超出受体范围 | center/size 单位写错（应为 Å） |
| `rmsd.py` 报 "no molecule" | 输出不是 sdf；改用 `--out xxx.sdf` 重跑 |
| GetBestRMS 报原子数不一致 | 参考 pose 与待测 pose 氢原子数不同 → 脚本已 RemoveHs，确认两文件都是同一配体 |

---

## 若 Smina 实在装不上 → 退回 C 级（零新软件，同样能回应审稿人）

1. 用备份结构 **6IQ5**（3.7 Å）独立对接，看是否仍落在 heme pocket。
2. **多种子稳定性**：Vina 用 seed = 1 / 2 / 3 / 42 / 2024 各跑一次 → 报告 5 次 top pose 两两 RMSD 与亲和力 mean ± SD。
3. **对照**：α-naphthoflavone（阳性，已有 RMSD 0.10 Å）、naringenin（弱结合，−8.96 kcal/mol）。

这三项只用现有 Vina 即可完成，产出同样可写入 Supplementary Table S9。
