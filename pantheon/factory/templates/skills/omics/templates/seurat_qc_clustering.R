#' TEMPLATE: Standard scRNA-seq QC + Clustering Pipeline (Seurat)
#' ==============================================================
#' Usage: Agent adapts PARAMETERS, writes notebook with ir kernel, batch executes.
#'
#' PARAMETERS TO ADAPT (marked with # ADAPT):
#'   - DATA_PATH, DATA_FORMAT
#'   - SPECIES (human/mouse)
#'   - QC thresholds (after observing plots)
#'   - N_FEATURES, N_PCS, RESOLUTION

# == Cell 1: Setup ==
library(Seurat)
library(ggplot2)
library(patchwork)
dir.create("results", showWarnings = FALSE)

# == Cell 2: Load data ==
# ADAPT: data path and format
pbmc.data <- Read10X(data.dir = "./data/filtered_feature_bc_matrix/")
pbmc <- CreateSeuratObject(counts = pbmc.data, project = "analysis", min.cells = 3, min.features = 200)
cat(sprintf("Loaded: %d cells x %d genes
", ncol(pbmc), nrow(pbmc)))

# == Cell 3: QC metrics ==
# ADAPT: "^MT-" for human, "^mt-" for mouse
pbmc[["percent.mt"]] <- PercentageFeatureSet(pbmc, pattern = "^MT-")

# == Cell 4: QC plots ==
p <- VlnPlot(pbmc, features = c("nFeature_RNA", "nCount_RNA", "percent.mt"), ncol = 3)
ggsave("results/01_qc_violin.png", p, width = 12, height = 4, dpi = 150)
print(p)

p2 <- FeatureScatter(pbmc, feature1 = "nCount_RNA", feature2 = "nFeature_RNA") +
      FeatureScatter(pbmc, feature1 = "nCount_RNA", feature2 = "percent.mt")
ggsave("results/02_qc_scatter.png", p2, width = 10, height = 4, dpi = 150)
print(p2)

# == Cell 5: Filter ==
# ADAPT: thresholds based on QC plots
pbmc <- subset(pbmc, subset = nFeature_RNA > 200 & nFeature_RNA < 2500 & percent.mt < 5)
cat(sprintf("After filter: %d cells
", ncol(pbmc)))

# == Cell 6: Normalize + HVG ==
pbmc <- NormalizeData(pbmc)
pbmc <- FindVariableFeatures(pbmc, selection.method = "vst", nfeatures = 2000)

# == Cell 7: Scale + PCA + Cluster + UMAP ==
pbmc <- ScaleData(pbmc)
pbmc <- RunPCA(pbmc)
pbmc <- FindNeighbors(pbmc, dims = 1:15)
pbmc <- FindClusters(pbmc, resolution = 0.5)
pbmc <- RunUMAP(pbmc, dims = 1:15)

p3 <- DimPlot(pbmc, reduction = "umap", label = TRUE)
ggsave("results/03_umap.png", p3, width = 8, height = 6, dpi = 150)
print(p3)

# == Cell 8: Markers ==
markers <- FindAllMarkers(pbmc, only.pos = TRUE, min.pct = 0.25, logfc.threshold = 0.25)
top5 <- markers |> dplyr::group_by(cluster) |> dplyr::slice_max(n = 5, order_by = avg_log2FC)
p4 <- DoHeatmap(pbmc, features = top5$gene) + NoLegend()
ggsave("results/04_heatmap.png", p4, width = 12, height = 10, dpi = 150)
print(p4)

# == Cell 9: Save ==
saveRDS(pbmc, file = "results/processed.rds")
cat(sprintf("Done: %d cells x %d clusters
", ncol(pbmc), length(unique(Idents(pbmc)))))
