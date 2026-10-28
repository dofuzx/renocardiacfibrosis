# -*- coding: utf-8 -*-
"""
把跨引擎交叉对接结果写入 Supplementary_Tables.xlsx 的新 sheet S9_cross_docking
  - 三套 Vina 家族打分 (Vina / Smina-vina / Smina-vinardo) 共用相同网格
  - 新增独立深度学习方法 GNINA 1.3.3 盲对接 (独立网格, 不报单一 RMSD)
数据来源：D:\docking 下 smina / gnina 运行输出 + rmsd.py / contacts.py 计算
同时写入两份 xlsx: 投稿包 (pre Review/FrontPharmacol) 与 Frontiers IPO。
"""
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, PatternFill

XLSX_LIST = [
    r"D:\AIwork\论文投稿\FP\pre Review\FrontPharmacol\Supplementary_Tables.xlsx",
    r"D:\AIwork\论文投稿\FP\Frontiers IPO\Supplementary_Tables.xlsx",
]

HEAD = Font(bold=True, color="FFFFFF")
FILL = PatternFill("solid", fgColor="4472C4")
TITLE = Font(bold=True, size=12)

RES = "ALA133, PHE134, PHE231, PHE268, THR325, ASP326, GLY329, ALA330, " \
      "ASP333, THR334, ILE399, LEU509, HEM900"

blocks = [
    ("Supplementary Table S9. Cross-docking validation of the kaempferol-CYP1B1 pose "
     "(PDB 3PM0) using scoring functions and engines independent of AutoDock Vina, "
     "including an independent deep-learning (GNINA) blind-docking check.", None),
    ("The three Vina-family runs (Vina, Smina-vina, Smina-vinardo) used the identical "
     "receptor (3PM0, alpha-naphthoflavone and waters removed, heme retained), the "
     "identical ligand pdbqt (Gasteiger charges, 5 rotatable bonds), the identical grid "
     "(center -18.345 / 21.502 / -19.818 A; 24 x 24 x 24 A), exhaustiveness 16 and seed "
     "42. GNINA 1.3.3 was run as whole-protein blind docking on the tamarind.bio web "
     "deployment (exhaustiveness 8, seed 1, nine modes, CNN rescoring); it used its own "
     "independent grid and did not receive the haem as a docking constraint. Affinity "
     "values are not directly comparable across engines (differing energy scales and "
     "torsion terms); pose reproducibility is the validated quantity.", None),
    (None, None),
    (["Engine / scoring function", "Program (version)",
      "Best affinity (kcal/mol)", "Top-pose heavy-atom RMSD vs Vina (A)",
      "Contact residues (< 4 A)", "Shared with Vina (%)"], "header"),
    (["AutoDock Vina (vina)", "AutoDock Vina 1.2.7", -10.98,
      "reference", 13, "100"], "row"),
    (["Smina (vina)", "Smina 2020.12.10 (conda-forge)", -11.88,
      0.03, 13, "100"], "row"),
    (["Smina (vinardo)", "Smina 2020.12.10 (conda-forge)", -11.35,
      0.35, 13, "100"], "row"),
    (["GNINA (CNN rescoring)", "GNINA 1.3.3 (tamarind.bio, blind)", -11.93,
      "n/a (independent blind grid)", "7/8 key; 11/12 signature",
      "87.5% (key) / 91.7% (signature)"], "row"),
    (None, None),
    (["Verdict", "Pass criterion", "Observed", "Result"], "header"),
    (["Pose reproducibility (Smina/vina)", "RMSD <= 2.0 A", "0.03 A", "PASS"], "row"),
    (["Pose reproducibility (Smina/vinardo)", "RMSD <= 2.0 A", "0.35 A", "PASS"], "row"),
    (["Affinity within same order", "~ -9 to -12 kcal/mol",
      "-11.88 / -11.35 vs -10.98", "PASS"], "row"),
    (["Contact-residue concordance (Vina-family)", "identity of key residues",
      "13/13 residues shared (100%)", "PASS"], "row"),
    (["Independent ML placement (GNINA)", "same pocket, key contacts retained",
      "centroid 0.74 A; 7/8 key (Asp326 absent), 11/12 signature; CNN pose 0.8015",
      "PASS"], "row"),
    (None, None),
    (["Contact residues shared by all three Vina-family scoring functions (n = 13, < 4 A)"],
     "header"),
    ([RES], "row"),
    (None, None),
    (["Key residues reported in section 3.5 (Asp326, Ala330, Thr325/334, Asp333, "
      "Phe134/231/268): recovered in all three Vina-family runs - 8/8; GNINA recovered "
      "7/8 (all except Asp326), with two newly observed contacts (Asn265, Val126) "
      "reflecting minor sub-pocket relaxation after haem removal."], "note"),
    (["Note: RMSD for the three Vina-family runs was computed by ordered heavy-atom "
      "superposition (21 heavy atoms); kaempferol poses retain identical atom ordering "
      "in pdbqt output, and the values agree with the RMSD upper bounds reported by "
      "Smina itself. GNINA was blind-docked on an independent whole-protein grid, so no "
      "single heavy-atom RMSD vs the Vina reference is reported; agreement is instead "
      "quantified by pocket placement (centroid offset 0.74 A) and contact-residue "
      "identity (7/8 key, 11/12 signature). The GNINA top pose was ranked by a "
      "convolutional-neural-network pose score of 0.8015 and carries a Vina-type "
      "affinity of -11.93 kcal/mol."], "note"),
]


def build(XLSX):
    wb = load_workbook(XLSX)
    if "S9_cross_docking" in wb.sheetnames:
        del wb["S9_cross_docking"]
    ws = wb.create_sheet("S9_cross_docking")

    r = 1
    for payload, kind in blocks:
        if payload is None:
            r += 1
            continue
        if kind is None:                      # 标题/说明段
            ws.cell(row=r, column=1, value=payload).font = TITLE
            ws.cell(row=r, column=1).alignment = Alignment(wrap_text=True, vertical="top")
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
            ws.row_dimensions[r].height = 60
            r += 2
        elif kind == "header":
            for c, v in enumerate(payload, 1):
                cell = ws.cell(row=r, column=c, value=v)
                cell.font = HEAD
                cell.fill = FILL
                cell.alignment = Alignment(wrap_text=True, vertical="center")
            ws.row_dimensions[r].height = 32
            r += 1
        elif kind == "row":
            for c, v in enumerate(payload, 1):
                cell = ws.cell(row=r, column=c, value=v)
                cell.alignment = Alignment(wrap_text=True, vertical="top")
            r += 1
        else:                                  # note
            ws.cell(row=r, column=1, value=payload[0]).alignment = \
                Alignment(wrap_text=True, vertical="top")
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
            ws.row_dimensions[r].height = 60
            r += 2

    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 24
    ws.column_dimensions["E"].width = 22
    ws.column_dimensions["F"].width = 22

    wb.save(XLSX)
    return wb.sheetnames


def main():
    for XLSX in XLSX_LIST:
        names = build(XLSX)
        print("written:", XLSX)
        print("  sheets:", names)


if __name__ == "__main__":
    main()
