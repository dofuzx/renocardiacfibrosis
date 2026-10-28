# B 级操作 · Gnina 3D-CNN 重打分（独立交叉验证第二层）

> 配套文件：`D:\docking\cross_poses.pdbqt`（已备好的三套待打分 pose）
> 前置：A 级（Smina vina + vinardo）已完成，详见 `A级操作_Smina交叉对接_手把手教程.md`

---

## 〇、为什么还要做 Gnina？—— 证据层级

| 层 | 程序 | 打分本质 | 与 Vina 关系 |
|---|---|---|---|
| 原对接 | AutoDock Vina 1.2.7 | 经验力场能量（参数化项加权） | 基准 |
| A 级交叉 | Smina + **vinardo** | 经验力场，**换了另一套经验参数** | 同一家族（仍属"经验能量"） |
| **B 级交叉** | **Gnina 3D-CNN** | **卷积网络在实验结构上学出的打分**，非能量参数 | **完全独立** |

Smina(vinardo) 证明"换经验参数后 pose 仍稳定"，但仍是经验力场。
Gnina 的 CNN 是在 thousands of 实验共晶结构上训练出来的，**与 Vina 能量函数零共享**——
如果 CNN 也把这个 pose 判为最佳、且接触残基一致，这才是审稿人要的"**跨方法学家族**"铁证。

> 结论：**Smina 已足够，Gnina 是"锦上添花的独立证据"**。有精力就做（B 级），不做也不阻断投稿。

---

## 一、Windows 现实约束（先说清，免得你踩坑）

- ❌ **官方从不发 Windows 二进制**：所有 GitHub Release 只有 Linux 版（最新 v1.3.3 是 2 GB 的 CUDA 静态包，v1.3 是 1.19 GB 的 `gnina` Linux 二进制）。
- ❌ **conda-forge 也没有 gnina 包**（feedstock 已 404），所以走不了 `conda install gnina`。
- ✅ **不需要 NVIDIA 显卡**：官方明确"无 GPU 时自动回退 CPU，可用 `--no_gpu` 强制"；rescore 模式只给最终 pose 打分，CPU 跑 3 个 pose 几十秒到几分钟。
- ✅ **唯一现实路径：WSL2（Windows 子系统 Linux）+ 官方 Linux 二进制 + `--no_gpu`**。
  （备选：Google Colab 零安装，见文末 Route B）

---

## 二、Route A：WSL2 本地跑（推荐，和你的 Smina 工作流一致）

### Step 1 · 安装 WSL2 + Ubuntu（需管理员 PowerShell，仅一次）
```powershell
# 在【开始】右键 → 终端(管理员) 或 Windows PowerShell(管理员) 里执行：
wsl --install -d Ubuntu
# 装完按提示设用户名/密码，重启一次
```
装好后，开始菜单打开 **Ubuntu** 终端即可进入 Linux。
> D 盘在 WSL 里是 `/mnt/d/`，所以 `D:\docking` = `/mnt/d/docking`。

### Step 2 · 在 Ubuntu 里装 miniforge + 提供 CUDA 运行库（libcudart）
gnina 二进制动态链接 `libcudart.so.12`，即使 `--no_gpu` 也要这个库在场。最干净的做法是用 conda 提供它（避免动系统 CUDA）：
```bash
# 在 Ubuntu 终端里
cd ~
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh -b -p ~/miniforge3
source ~/miniforge3/etc/profile.d/conda.sh
conda create -n gninaenv -y
conda activate gninaenv
conda install -c conda-forge cudatoolkit -y   # 仅提供 libcudart，不装驱动
```
> 若不想用 conda，也可 `sudo apt install nvidia-cuda-runtime-12-8`（需先加 NVIDIA apt 源），但 conda 更省事。

### Step 3 · 下载 gnina Linux 二进制并放行
```bash
cd ~/miniforge3/envs/gninaenv/bin
wget https://github.com/gnina/gnina/releases/download/v1.3/gnina -O gnina
chmod +x gnina
./gnina --version      # 应看到 gnina v1.3 ... ；若报 libcudart 缺失，回头确认 Step2 的 cudatoolkit 已装且在 activated 环境里
```

### Step 4 · 跑重打分（CPU 强制）
```bash
cd /mnt/d/docking
gnina --score_only \
  -r 3PM0_prot.pdbqt \
  -l cross_poses.pdbqt \
  --cnn_scoring rescore \
  --no_gpu \
  -o rescore.sdf \
  --log rescore.log
```
- `--score_only`：只给已有 pose 打分，不重新搜索（这就是"重打分"）。
- `--cnn_scoring rescore`：用 CNN 给最终 pose 排序（默认就是这个，显式写出更清楚）。
- `-l cross_poses.pdbqt`：里面是 3 个 MODEL，依次是 `VINA_orig_best` / `SMINA_vina_pose1` / `SMINA_vinardo_pose1`，一次全打分。
- `--no_gpu`：强制 CPU；无显卡机器必加。

### Step 5 · 解析结果（纯 Python，无需 rdkit）
`rescore.sdf` 每个分子带数据字段 `CNNscore`、`CNNaffinity`、`minimizedAffinity`(=Vina kcal/mol)、`vina_affinity`、`vina_raw`。
```bash
cd /mnt/d/docking
cat > parse_rescore.py << 'PY'
import sys
txt=open('rescore.sdf',encoding='utf-8',errors='ignore').read()
blocks=[b for b in txt.split('$$$$') if b.strip()]
for i,b in enumerate(blocks,1):
    name='block%d'%i
    for line in b.splitlines():
        if line.startswith('REMARK POSE_SOURCE'):
            name=line.split('POSE_SOURCE')[-1].strip()
    d={}
    lines=b.splitlines()
    for j,line in enumerate(lines):
        if line.startswith('> <') and line.endswith('>'):
            key=line[3:-1].strip()
            if j+1<len(lines): d[key]=lines[j+1].strip()
    print('%-22s CNNscore=%-8s CNNaffinity=%-10s Vina(kcal/mol)=%s'%(
        name, d.get('CNNscore','?'), d.get('CNNaffinity','?'), d.get('minimizedAffinity', d.get('vina_affinity','?'))))
PY
python parse_rescore.py
```
输出示例（数值仅供格式参考，非真实）：
```
VINA_orig_best        CNNscore=0.96     CNNaffinity=7.1     Vina(kcal/mol)=-10.9
SMINA_vina_pose1      CNNscore=0.95     CNNaffinity=7.0     Vina(kcal/mol)=-11.9
SMINA_vinardo_pose1   CNNscore=0.94     CNNaffinity=6.9     Vina(kcal/mol)=-11.4
```

---

## 三、Route B：Google Colab 零安装（无 WSL 时）

1. 打开 Gnina 官方示例 Colab（README 里有链接），或新建 Colab。
2. 左上「运行时 → 更改运行时类型 → GPU」（免费 T4 即可；rescore 3 个 pose 连 CPU 也行）。
3. 左侧文件面板上传 `3PM0_prot.pdbqt` 和 `cross_poses.pdbqt`。
4. 单元格里：
```bash
!wget -q https://github.com/gnina/gnina/releases/download/v1.3/gnina -O gnina && chmod +x gnina
!./gnina --score_only -r 3PM0_prot.pdbqt -l cross_poses.pdbqt --cnn_scoring rescore --no_gpu -o rescore.sdf --log rescore.log
!cat rescore.log | grep -iE "CNN|affinity" | head
```
5. 下载 `rescore.sdf` 回 `D:\docking`，用上面的 `parse_rescore.py` 解析。

---

## 四、结果怎么读（**分数方向务必搞对**）

| 字段 | 含义 | 方向 |
|---|---|---|
| `CNNscore` | CNN 判该 pose "像不像真实结合构象" 的概率 | **越高越好**（0–1） |
| `CNNaffinity` | CNN 预测亲和力（pK 类尺度） | **越高越好** |
| `minimizedAffinity` / `vina_affinity` | Vina 经验分（kcal/mol） | **越负越好** |

**判据（三项全过才算 PASS）：**
1. 三套 pose 的 `CNNscore` 都 ≥ 0.90（构象被 CNN 判为"真实结合样"）。
2. 三套 `CNNscore` / `CNNaffinity` **排序一致**——即 Vina 原 best pose 与 Smina 两个 pose 被 CNN 判为同等最佳，无某一套被 CNN 显著降级。
3. 与 A 级一致：接触残基同一性（用 `D:\docking\contacts.py` 对 `rescore.sdf` 抽 pose 再算，或直接沿用 A 级已验证的 13/13）。

> ⚠️ **铁律（写稿件时）**：
> - **CNNscore / CNNaffinity 与 Vina 亲和力数值不可混比**——量纲、含义都不同。
> - **绝不要写"Gnina 打分更高所以结合更强"**。被验证的量是：**独立 CNN 方法也认定同一 pose 为最佳构象**，而非 affinity 绝对值。
> - 上报 `CNNscore` 即可（带方向说明），不必把 CNNaffinity 当结合能。

---

## 五、稿件怎么写（拿到真实数值后）

在 **§2.8** 末尾补一句（接 Smina 段之后）：
> "As an orthogonal, learning-based control, the three top poses were additionally rescored with the 3D-convolutional neural-network scoring function implemented in Gnina v1.3 (Koes et al., 2021, default2018/rescore model, CPU execution via `--no_gpu`), which was trained on experimental structures and shares no energy parameters with Vina. A pose was accepted as cross-validated when its Gnina CNNscore remained ≥0.90 and its rank order matched the Vina/Smina result."

**§3.5** 补结果句（占位，替换为真实值）：
> "The CNN rescoring assigned CNNscores of 0.96 / 0.95 / 0.94 to the Vina, Smina-vina, and Smina-vinardo top poses, respectively, with identical rank order, confirming pose reproducibility across an empirical-energy and an independent deep-learning scoring family."

**表格**：在 `Supplementary_Tables.xlsx` 的 **S9_cross_docking** 增加一列 `Gnina CNNscore`（三行），或新建 `S10_CNN_rescore` 也行。正文引用处同步加 `(Supplementary Table S9)`。

---

## 六、坑速查

| 现象 | 原因 | 解决 |
|---|---|---|
| `error while loading shared libraries: libcudart.so.12` | 缺 CUDA 运行库 | Step2 的 `conda install cudatoolkit` 没装或环境没 activate |
| `gnina: command not found` | 不在 PATH / 没 chmod | `cd ~/miniforge3/envs/gninaenv/bin && ./gnina ...` |
| WSL 装完打不开 | 没启用虚拟机平台 | 管理员 PowerShell：`dism /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart` 后重启 |
| CNNscore 出现负数/异常 | 读错字段 | 确认读的是 `> <CNNscore>` 而非 `vina_raw` |
| 误把 CNNaffinity 当结合能比大小 | 量纲不同 | 只上报 CNNscore，方向"越高越好"要写明 |

---

## 七、我这边能不能替你跑？

**不能**——本机沙箱禁用了 `wsl.exe`，且无 Docker、无 GPU，gnina 又无 Windows 版。
你按上面 Run 完把 `rescore.sdf` / `rescore.log` 丢回 `D:\docking`，我立刻帮你解析 + 生成 **v24**（把 Gnina 列写进 S9、补 §2.8/§3.5 段落，并补 Gnina 引用文献 Koes 2021 / 其 CNN 模型文献）。
