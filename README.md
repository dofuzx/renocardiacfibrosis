# renocardiac_fibrosis

Analysis code and processed result tables for the study:

> *Decoding the renocardiac fibrosis axis and a kaempferol–CYP1B1 pro-repair strategy: an integrative transcriptomic and in silico docking analysis*

This repository supports the findings reported in the manuscript submitted to PLOS ONE.
It contains (i) the Python scripts that assemble the manuscript's Supplementary Tables
S1–S9 from exported analysis results, and (ii) the processed result tables themselves.

## Study overview

The study integrates public transcriptomic datasets (renal and cardiac fibrosis) with
machine-learning feature selection, a compound–target–disease network, and molecular
docking of kaempferol against CYP1B1, to decode the shared molecular axis of
reno–cardiac fibrosis and propose a pro-repair therapeutic strategy.

## Data sources

All underlying datasets are publicly available (no new experimental data were generated):

| Repository | Accession(s) | Use |
|---|---|---|
| NCBI GEO | GSE66494, GSE38117, GSE57338, GSE37171, GSE175412, GSE227088, GSE145154 | Transcriptomic analyses (bulk + single-cell) |
| RCSB PDB | 3PM0, 6IQ5 | Human CYP1B1 crystal structures (docking targets) |
| ChEMBL 35 | CHEMBL150 | Kaempferol bioactivity (downloaded 1 May 2026) |
| Open Targets Platform | — | Disease–gene associations |
| STRING v12 | — | Protein–protein interaction networks |

Per-accession download links are listed in Table 3 of the manuscript and in
`data/Supplementary_Tables.xlsx` (sheet `S7_data_resources`).

## Repository contents

```
renocardiac_fibrosis/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── Supplementary_Tables.xlsx      # Processed result tables S1–S9 (deliverable)
└── scripts/
    ├── build_supplementary_final.py   # Assembles S7 (GSE145154 status) + adds S8 (external cardiac validation)
    ├── build_s9.py                    # Writes S9 (cross-docking validation: Vina/Smina/GNINA)
    ├── copy_s8.py                    # Copies the S8 sheet between workbook copies
    ├── A级操作_Smina交叉对接_手把手教程.md   # Smina cross-docking SOP (Chinese)
    ├── B级操作_Gnina 3D-CNN重打分_手把手教程.md # GNINA CNN rescoring SOP (Chinese)
    └── Gnina网页版提交指南_tamarind.bio.md    # GNINA web submission guide (Chinese)
```

## How the supplementary tables were produced

The core statistical analyses — differential expression (limma), WGCNA, and the three
nested-cross-validated machine-learning classifiers (LASSO / SVM-RFE / random forest) —
were performed in R/Bioconductor; the molecular docking (AutoDock Vina 1.2.7, Smina
2020.12.10, GNINA 1.3.3) was performed externally. The scripts in `scripts/` regenerate
and assemble the manuscript's Supplementary Tables **from those exported result files**:

- `build_supplementary_final.py` updates sheet `S7_data_resources` (reclassifies
  GSE145154 as analysed) and appends sheet `S8_external_validation` (CYP1B1 lineage
  restriction / disease response in human ventricular snRNA-seq, GSE145154).
- `build_s9.py` writes sheet `S9_cross_docking` (cross-engine and deep-learning
  docking validation of the kaempferol–CYP1B1 pose).
- `copy_s8.py` duplicates the S8 sheet across workbook copies.

Note: the scripts read the exported CSV/result files from their original local paths
(documented in each script header). To fully re-run them, place the exported results
alongside the script paths or edit the `SRC_*` variables. The **final assembled
workbook `data/Supplementary_Tables.xlsx` is provided as the processed deliverable** and
requires no re-running.

## Environment

Python 3.11+. Install dependencies with:

```bash
pip install -r requirements.txt
```

## License

Code: MIT. Processed data tables inherit the terms of their source repositories
(GEO/PDB/ChEMBL/Open Targets/STRING); see data-source policies for reuse.

## Citation

If you use this code or the processed tables, please cite the associated manuscript
(see the DOI registered with Zenodo for this repository:
https://doi.org/10.5281/zenodo.XXXXXXX — replace with the issued DOI after archiving).
