# File: distilled_code.py
"""
Distilled classifier for CellTypist Immune_All_Low model.
This code must be SELF-CONTAINED - no external model dependencies.
"""

import math

# Cell type labels (exact names from CellTypist)
LABELS = [
    "Plasma cells",
    "Mast cells",
    "Neutrophil-myeloid progenitor",
    "Endothelial cells",
    "gamma-delta T cells",
    "Follicular B cells",
    "pDC",
    "DC1",
    "Kupffer cells",
    "Alveolar macrophages",
]

# NOTE:
# For high-fidelity CellTypist distillation, replace these heuristic coefficients with
# baked-in intercepts/coefficients extracted offline from the original model, and
# also populate MEAN/STD from the training preprocessing parameters.
BIASES = {
    "Plasma cells": 0.0,
    "Mast cells": 0.0,
    "Neutrophil-myeloid progenitor": 0.0,
    "Endothelial cells": 0.0,
    "gamma-delta T cells": 0.0,
    "Follicular B cells": 0.0,
    "pDC": 0.0,
    "DC1": 0.0,
    "Kupffer cells": 0.0,
    "Alveolar macrophages": 0.0,
}

WEIGHTS = {
    "Plasma cells": {
        "MZB1": 2.2,
        "JCHAIN": 2.4,
        "XBP1": 1.6,
        "SDC1": 2.0,  # CD138
        "TNFRSF17": 1.6,  # BCMA
        "PRDM1": 1.2,  # BLIMP1
        "IGHG1": 1.5,
        "IGHG2": 1.2,
        "IGHA1": 1.2,
        "IGKC": 1.0,
        "CD79A": -0.6,
        "MS4A1": -1.2,  # CD20
        "NKG7": -0.5,
        "LYZ": -0.5,
    },
    "Mast cells": {
        "TPSAB1": 2.4,
        "TPSB2": 2.4,
        "KIT": 2.0,
        "CPA3": 2.2,
        "MS4A2": 2.0,  # FCER1B
        "GATA2": 1.0,
        "HDC": 1.5,
        "IL1RL1": 1.0,  # ST2
        "PECAM1": -1.2,
        "LYZ": -0.8,
        "TRAC": -0.8,
        "MS4A1": -0.8,
    },
    "Neutrophil-myeloid progenitor": {
        "S100A8": 2.4,
        "S100A9": 2.4,
        "S100A12": 2.0,
        "LYZ": 1.6,
        "FCGR3B": 2.2,
        "CSF3R": 2.0,
        "FCN1": 1.2,
        "VCAN": 1.0,
        "CTSG": 1.6,
        "PRTN3": 1.6,
        "MPO": 1.8,
        "ELANE": 1.8,
        "CTSS": 0.6,
        "LGALS3": 0.6,
        # Negatives to avoid macrophage/DC bleed-through
        "C1QC": -1.0,
        "HLA-DRA": -0.6,
        "NKG7": -0.6,
        "TRAC": -0.8,
        "MS4A1": -0.8,
        "PECAM1": -0.8,
    },
    "Endothelial cells": {
        "PECAM1": 2.4,  # CD31
        "VWF": 2.4,
        "KDR": 2.0,  # VEGFR2
        "EMCN": 1.6,
        "ENG": 1.4,
        "RAMP2": 1.4,
        "ESAM": 1.6,
        "CLDN5": 2.0,
        "RGS5": -0.3,
        "LYZ": -1.4,
        "PTPRC": -1.8,  # CD45
    },
    "gamma-delta T cells": {
        "TRAC": 1.2,
        "CD3D": 1.2,
        "CD3E": 1.2,
        "TRDC": 2.6,
        "TRGC1": 2.0,
        "TRGC2": 1.6,
        "NKG7": 0.8,
        "KLRD1": 0.6,
        "MS4A1": -1.0,
        "MZB1": -0.6,
        "LYZ": -0.6,
        "PECAM1": -0.8,
    },
    "Follicular B cells": {
        "MS4A1": 2.2,
        "CD79A": 2.0,
        "CD79B": 1.8,
        "CD74": 1.4,
        "HLA-DRA": 1.0,
        "HLA-DPA1": 0.8,
        "HLA-DPB1": 0.8,
        "CD37": 1.2,
        "CD22": 1.4,
        "BANK1": 1.0,
        "IGHM": 1.2,
        "TCL1A": 0.4,
        "MZB1": -1.2,
        "JCHAIN": -1.2,
        "TRAC": -0.8,
        "LYZ": -0.6,
    },
    "pDC": {
        "GZMB": 2.0,
        "IRF7": 1.6,
        "TCF4": 2.2,
        "IL3RA": 2.2,  # CD123
        "CLEC4C": 2.4,  # BDCA2
        "SERPINF1": 1.0,
        "SPIB": 1.6,
        "TLR7": 1.0,
        "PTCRA": 0.6,
        "HLA-DRA": 1.0,
        "HLA-DPA1": 0.8,
        "TRAC": -0.6,
        "NKG7": -0.8,
        "S100A8": -1.2,
        "FCGR3B": -1.2,
    },
    "DC1": {
        "CLEC9A": 2.4,
        "XCR1": 2.4,
        "BATF3": 1.6,
        "IRF8": 1.4,
        "CADM1": 1.2,
        "ID2": 1.0,
        "ITGAX": 0.6,  # CD11c
        "CCR7": 0.4,
        "HLA-DRA": 1.0,
        "HLA-DPA1": 0.8,
        "FCER1A": 0.6,
        "TCF4": -1.0,
        "IL3RA": -1.0,
        "GZMB": -0.8,
        "S100A8": -1.0,
    },
    "Kupffer cells": {
        "C1QA": 1.8,
        "C1QB": 1.8,
        "C1QC": 2.4,
        "MARCO": 2.0,
        "VSIG4": 2.4,
        "CLEC4F": 2.6,
        "TIMD4": 2.2,
        "LYVE1": 1.6,
        "SPIC": 1.2,
        "VCAM1": 0.8,
        "LGALS3": 1.0,
        "CTSS": 0.8,
        "LYZ": 0.6,
        "APOE": 0.8,
        "SPP1": 0.4,
        "PPARG": -0.6,
        "FCGR3B": -1.4,
        "S100A8": -1.0,
        "TRAC": -0.6,
    },
    "Alveolar macrophages": {
        "PPARG": 2.2,
        "MARCO": 1.2,
        "CHIT1": 1.8,
        "FABP4": 1.8,
        "MRC1": 1.4,
        "MSR1": 1.2,
        "SLC40A1": 1.2,
        "LPL": 1.2,
        "FABP5": 0.8,
        "APOE": 1.0,
        "C1QA": 1.0,
        "C1QC": 1.0,
        "LGALS3": 1.0,
        "CTSS": 0.8,
        "LYZ": 0.8,
        "S100A8": -1.4,
        "FCGR3B": -1.6,
        "MS4A1": -0.8,
        "TRDC": -0.6,
        # Negatives to reduce Kupffer pull when liver-resident markers are present
        "CLEC4F": -1.2,
        "TIMD4": -1.0,
    },
}

# Per-gene preprocessing parameters (placeholders).
# Populate with training-set mean/std for each gene for true CellTypist-like z-scoring.
MEAN = {}
STD = {}


# Gene universe: align to the baked-in model features.
# Keep gating genes, but avoid hand-maintaining a separate, drifting list.
GATING_GENES = {
    "MZB1",
    "JCHAIN",
    "XBP1",
    "SDC1",
    "MS4A1",
    "CD79A",
    "CD79B",
    "TRAC",
    "CD3D",
    "CD3E",
    "TRDC",
    "TRGC1",
    "TRGC2",
    "TPSAB1",
    "TPSB2",
    "KIT",
    "CPA3",
    "PECAM1",
    "VWF",
    "KDR",
    "CLDN5",
    "S100A8",
    "S100A9",
    "S100A12",
    "FCGR3B",
    "CSF3R",
    "CLEC9A",
    "XCR1",
    "BATF3",
    "GZMB",
    "TCF4",
    "IL3RA",
    "CLEC4C",
    "C1QC",
    "VSIG4",
    "MARCO",
    "CLEC4F",
    "TIMD4",
    "PPARG",
    "CHIT1",
    "FABP4",
    "MRC1",
    "SLC40A1",
    "LYZ",
    "CTSS",
}
GENES = sorted(set(GATING_GENES).union(*(set(w.keys()) for w in WEIGHTS.values())))
def predict_cell_type(expression: dict) -> str:
    """
    Predict cell type from gene expression.

    Args:
        expression: Dict mapping gene names to expression values

    Returns:
        Predicted cell type name
    """

    # --- CellTypist-like fixed preprocessing ---
    # 1) library-size normalize to 1e4
    # 2) log1p
    # 3) optional per-gene z-score using baked-in MEAN/STD (if provided)
    lib = 0.0
    for v in expression.values():
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if fv > 0:
            lib += fv

    def _preprocess(gene: str, raw: float) -> float:
        if raw <= 0 or lib <= 0:
            x = 0.0
        else:
            x = math.log1p(1e4 * raw / lib)

        mu = MEAN.get(gene)
        sd = STD.get(gene)
        if mu is None or sd is None or sd == 0:
            return x
        return (x - mu) / sd

    # --- Precompute preprocessed features once ---
    xt = {}
    for g in GENES:
        v = expression.get(g, 0.0)
        try:
            fv = float(v)
        except (TypeError, ValueError):
            fv = 0.0
        xt[g] = _preprocess(g, fv)

    # ----- Soft gating (mixture-of-experts) -----
    # Use the same transformed values for gating and scoring to avoid double-influence.
    plasma_marker = xt.get("MZB1", 0.0) + xt.get("JCHAIN", 0.0) + xt.get("XBP1", 0.0) + xt.get("SDC1", 0.0)
    b_marker = xt.get("MS4A1", 0.0) + xt.get("CD79A", 0.0) + xt.get("CD79B", 0.0)
    t_marker = xt.get("TRAC", 0.0) + xt.get("CD3D", 0.0) + xt.get("CD3E", 0.0)
    gd_marker = xt.get("TRDC", 0.0) + xt.get("TRGC1", 0.0) + 0.5 * xt.get("TRGC2", 0.0)
    mast_marker = xt.get("TPSAB1", 0.0) + xt.get("TPSB2", 0.0) + xt.get("KIT", 0.0) + xt.get("CPA3", 0.0)
    endo_marker = xt.get("PECAM1", 0.0) + xt.get("VWF", 0.0) + xt.get("KDR", 0.0) + xt.get("CLDN5", 0.0)
    neut_marker = (
        xt.get("S100A8", 0.0)
        + xt.get("S100A9", 0.0)
        + xt.get("FCGR3B", 0.0)
        + xt.get("CSF3R", 0.0)
        + 0.5 * xt.get("S100A12", 0.0)
    )
    dc1_marker = xt.get("CLEC9A", 0.0) + xt.get("XCR1", 0.0) + xt.get("BATF3", 0.0)
    pdc_marker = xt.get("GZMB", 0.0) + xt.get("TCF4", 0.0) + xt.get("IL3RA", 0.0) + xt.get("CLEC4C", 0.0)
    kup_marker = (
        xt.get("C1QC", 0.0)
        + xt.get("VSIG4", 0.0)
        + xt.get("MARCO", 0.0)
        + xt.get("CLEC4F", 0.0)
        + 0.7 * xt.get("TIMD4", 0.0)
    )
    alv_marker = (
        xt.get("PPARG", 0.0)
        + xt.get("CHIT1", 0.0)
        + xt.get("FABP4", 0.0)
        + xt.get("MARCO", 0.0)
        + 0.6 * xt.get("MRC1", 0.0)
        + 0.6 * xt.get("SLC40A1", 0.0)
    )

    # Thresholds are now in the (library-normalized log1p, optionally z-scored) space.
    # If MEAN/STD are populated, features are z-scored and these thresholds should be revisited.
    myeloidish = (xt.get("LYZ", 0.0) + 0.5 * xt.get("CTSS", 0.0)) >= 0.8

    gate_scores = {
        "Mast": mast_marker,
        "Endo": endo_marker,
        "Plasma": plasma_marker,
        "B": b_marker,
        "T": t_marker,
        "gdt": gd_marker,
        "Neut": neut_marker,
        "pDC": pdc_marker,
        "DC1": dc1_marker,
        "Kup": kup_marker,
        "Alv": alv_marker,
    }

    # ----- Linear scoring for all labels -----
    def linear_score(label: str) -> float:
        s = BIASES.get(label, 0.0)
        weights = WEIGHTS.get(label, {})
        for gene, w in weights.items():
            s += w * xt.get(gene, 0.0)
        return s

    # ----- Non-blocking gating: add a small prior bonus -----
    gate_bonus = {
        "Mast cells": mast_marker,
        "Endothelial cells": endo_marker,
        "Plasma cells": plasma_marker,
        "Follicular B cells": b_marker,
        "gamma-delta T cells": gd_marker,
        "Neutrophil-myeloid progenitor": neut_marker,
        "pDC": pdc_marker,
        "DC1": dc1_marker,
        "Kupffer cells": kup_marker,
        "Alveolar macrophages": alv_marker,
    }
    alpha = 0.2

    def final_score(label: str) -> float:
        return linear_score(label) + alpha * gate_bonus.get(label, 0.0)

    # Optional mild restriction only for broad myeloid vs non-myeloid ambiguity.
    # Keep it non-blocking by retaining a reasonably large candidate set.
    if myeloidish:
        candidates = ["Kupffer cells", "Alveolar macrophages", "Neutrophil-myeloid progenitor", "pDC", "DC1"]
        # Still allow other labels to win if their linear score is much higher.
        candidates = candidates + ["Mast cells", "Endothelial cells", "Plasma cells", "Follicular B cells", "gamma-delta T cells"]
    else:
        candidates = list(LABELS)

    return max(candidates, key=final_score)
