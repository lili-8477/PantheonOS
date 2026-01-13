### 1. Data Integration

This section mainly evaluates the ability of different algorithms to remove batch effects and the effectiveness of retaining biological variation after integration.

-   **Tools used:**

    -   **Scanorama**: Used for batch correction of multiple datasets (such as 293t/jurkat mixed data, PBMC, pancreas data, etc.).
    -   **Harmony**: Mainly performs correction on PCA-reduced data, testing the impact of different iteration parameters.
    -   **BBKNN**: Graph-based method, testing the effect of different neighbor counts (neighbors_within_batch) and pruning parameters on the integrated graph structure.
    -   **scVI** (scvi-tools): Variational autoencoder-based generative model, testing different hyperparameters (such as latent variable dimension n_latent, number of layers n_layers, gene likelihood distribution, etc.).

-   **Completed tasks:**

    -   Batch correction for data from multiple sources and technological platforms (such as 10x, Smart-seq2, inDrop, etc.).
    -   Generation of corrected low-dimensional embeddings (such as UMAP or Latent Space).
    -   Comparison of integration effects before and after correction or under different parameter settings.

-   **Evaluation metrics:**
    -   **iLiSi (integrated Local Inverse Simpson’s Index)**: This is the core metric for measuring the degree of batch mixing; higher values indicate better mixing of cells from different batches (i.e., more thorough removal of batch effects).
    -   **ELBO (Evidence Lower Bound)**: Evaluates the model’s training fit for the scVI model.
    -   **Reconstruction Loss (MSE)**: Assesses the accuracy of the model in reconstructing gene expression profiles.
    -   **Mean Connectivity**: Evaluates the connectivity of the constructed nearest neighbor graph.

---

### 2. Single-cell Type Annotation

This section focuses on the accuracy of predicting cell types in new data using reference datasets.

-   **Tools used:**

    -   **Celltypist**: Uses pre-trained models (such as "Immune_All_Low.pkl") for automated annotation.
    -   **SVM (Support Vector Machine)**: Used as a traditional machine learning baseline.
    -   **scANVI** (scvi-tools): Semi-supervised learning model that uses partially labeled data for prediction.
    -   **Random Forest**: Ensemble learning method based on sklearn.

-   **Completed tasks:**

    -   Training models on training sets and predicting cell types on test sets.
    -   Identifying specific cell types (e.g., "Mast cells", "Gamma-delta T cells").
    -   Detecting specific misclassification cases (e.g., misclassifying "Macrophages" as "Alveolar macrophages").
    -   Verifying whether specific single-cell predictions match the Ground Truth.

-   **Evaluation metrics:**
    -   **Accuracy**: Overall proportion of correct predictions.
    -   **F1-Score**: Metric balancing precision and recall.
    -   **Specific Counts**: Number of predictions for specific categories or occurrences of specific error types.
    -   **Boolean Matching (True/False)**: Whether the prediction for a specific cell is correct.

---

### 3. Multimodal Prediction

Focused on CITE-seq data (which contains both RNA and surface protein data), evaluating models’ cross-modal learning and denoising capabilities.

-   **Tools used:**

    -   **TotalVI** (scvi-tools): A generative model specifically designed for handling CITE-seq data.

-   **Completed tasks:**

    -   Joint analysis of RNA and protein data.
    -   Predicting denoised protein expression and RNA expression.
    -   Calculating protein foreground probability.
    -   Performing Leiden clustering based on the joint latent space.

-   **Evaluation metrics:**
    -   **Mean Expression/Median Probability**: Evaluates the numerical distribution of model outputs.
    -   **Pearson Correlation**: Measures the correlation between denoised protein expression and corresponding RNA expression.
    -   **Number of Clusters**: Assesses the latent space’s ability to retain biological heterogeneity.
    -   **Distance Metrics**: Euclidean distances between cells in latent space.
    -   **Log-fold Change (LFC)**: Compares expression differences between groups.

---

### 4. Spatial Deconvolution

For spatial transcriptomics data, aiming to use single-cell sequencing data as a reference to resolve cell type composition in spatial locations.

-   **Tools used:**

    -   **CondSCVI** and **DestVI** (scvi-tools).

-   **Completed tasks:**

    -   Using scRNA-seq data as reference and smFISH data as spatial query.
    -   Inferring proportions of different cell types at each spatial spot.
    -   Denoising spatial gene expression of specific cell types.

-   **Evaluation metrics:**
    -   **ELBO**: Model training convergence metric.
    -   **Proportion Statistics**: Includes average proportion, maximum proportion, variance, etc., of specific cell types.
    -   **Pearson Correlation**: Correlation between estimated cell proportions and original gene counts at the location (validating the reasonableness of deconvolution).

---

### 5. Data Cleaning & Analysis

This is the cornerstone of single-cell analysis workflows, covering preprocessing (QC) and exploratory data analysis (EDA).

-   **Tools used:**

    -   Standard Python scientific computing stack (based on **Scanpy**, **NumPy**, **Scikit-learn**, etc.).

-   **Completed tasks:**

    -   **Data Cleaning**:
        -   Normalization: Log-CPM (Counts Per Million) transformation.
        -   Sample filtering: Removing cells with abnormal library sizes based on IQR rules.
        -   Gene filtering: Removing low-expression genes (e.g., genes with counts <5 in less than 50% of samples).
        -   Complexity filtering: Removing low-quality cells based on detected gene counts or the proportion of highly expressed genes (Top 50).
    -   **Data Analysis**:
        -   Sparsity calculation: Calculating the proportion of zero values in the matrix.
        -   Coefficient of Variation (CV): Measuring the dispersion of gene expression.
        -   Correlation analysis: Calculating Pearson correlation coefficients between genes.
        -   Dimensionality reduction and clustering: Calculating PCA explained variance ratios, followed by K-Means clustering.

-   **Evaluation metrics:**
    -   **Statistical values**: Maximum, average, remaining sample/gene counts.
    -   **Percentages**: Sparsity, variance explained ratios.
    -   **Correlation coefficients**: Pearson r values.
    -   **Silhouette Coefficient**: Evaluates the effectiveness of K-Means clustering.
