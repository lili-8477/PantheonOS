"""
TEMPLATE: Standard scRNA-seq QC + Clustering Pipeline (Scanpy)
==============================================================
Usage: Agent adapts PARAMETERS, writes notebook with python3 kernel, batch executes.

PARAMETERS TO ADAPT (marked with # ADAPT):
  - DATA_PATH, DATA_FORMAT
  - SPECIES (human/mouse)
  - QC thresholds (after observing plots)
  - N_TOP_GENES, N_PCS, RESOLUTION
"""

# == Cell 1: Setup ==
import scanpy as sc
import numpy as np
import matplotlib.pyplot as plt
import os

sc.settings.verbosity = 3
sc.settings.set_figure_params(dpi=150, frameon=False)
OUTPUT_DIR = "./results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# == Cell 2: Load data ==
# ADAPT: data path and format
adata = sc.read_10x_mtx("./data/filtered_feature_bc_matrix/", var_names="gene_symbols", cache=True)
adata.var_names_make_unique()
print(f"Loaded: {adata.n_obs} cells x {adata.n_vars} genes")

# == Cell 3: QC metrics ==
# ADAPT: MT- for human, mt- for mouse
adata.var["mt"] = adata.var_names.str.startswith("MT-")
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True)

# == Cell 4: QC plots ==
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
sc.pl.violin(adata, "n_genes_by_counts", ax=axes[0], show=False)
sc.pl.violin(adata, "total_counts", ax=axes[1], show=False)
sc.pl.violin(adata, "pct_counts_mt", ax=axes[2], show=False)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/01_qc_violin.png", dpi=150, bbox_inches="tight")
plt.show()

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
sc.pl.scatter(adata, x="total_counts", y="n_genes_by_counts", color="pct_counts_mt", ax=axes[0], show=False)
sc.pl.scatter(adata, x="total_counts", y="pct_counts_mt", ax=axes[1], show=False)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/02_qc_scatter.png", dpi=150, bbox_inches="tight")
plt.show()

print(f"Median genes/cell: {np.median(adata.obs['n_genes_by_counts']):.0f}")
print(f"Median counts/cell: {np.median(adata.obs['total_counts']):.0f}")
print(f"Median MT%: {np.median(adata.obs['pct_counts_mt']):.1f}%")

# == Cell 5: Filter ==
# ADAPT: thresholds based on QC plots
adata = adata[adata.obs["n_genes_by_counts"].between(200, 2500)].copy()
adata = adata[adata.obs["pct_counts_mt"] < 5].copy()
sc.pp.filter_genes(adata, min_cells=3)
print(f"After filter: {adata.n_obs} cells x {adata.n_vars} genes")

# == Cell 6: Normalize + HVG ==
adata.layers["counts"] = adata.X.copy()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
adata.raw = adata
sc.pp.highly_variable_genes(adata, n_top_genes=2000)

# == Cell 7: PCA + Cluster + UMAP ==
adata = adata[:, adata.var["highly_variable"]].copy()
sc.pp.scale(adata, max_value=10)
sc.pp.pca(adata)
sc.pp.neighbors(adata, n_pcs=15)
sc.tl.leiden(adata, resolution=0.5)
sc.tl.umap(adata)

sc.pl.umap(adata, color=["leiden"], show=False)
plt.savefig(f"{OUTPUT_DIR}/03_umap.png", dpi=150, bbox_inches="tight")
plt.show()

# == Cell 8: Markers ==
sc.tl.rank_genes_groups(adata, "leiden", method="wilcoxon")
sc.pl.rank_genes_groups(adata, n_genes=10, show=False)
plt.savefig(f"{OUTPUT_DIR}/04_markers.png", dpi=150, bbox_inches="tight")
plt.show()

# == Cell 9: Save ==
adata.write(f"{OUTPUT_DIR}/processed.h5ad")
print(f"Done: {adata.n_obs} cells x {adata.n_vars} genes x {adata.obs['leiden'].nunique()} clusters")
