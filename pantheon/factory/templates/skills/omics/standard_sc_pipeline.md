---
id: standard_sc_pipeline
name: Standard Single-Cell Pipeline
description: |
  Script-first workflow for standard scRNA-seq analysis in PantheonOS.
  Covers project layout, template adaptation, QC decisions, execution, and reporting.
tags: [single-cell, pipeline, scanpy, seurat]
---

# Standard Single-Cell Pipeline

Use this workflow for the common case: QC, normalization, HVG selection,
dimensionality reduction, clustering, marker detection, and optional cell-type
annotation. This skill is optimized for low-overhead execution with one script
rather than an interactive notebook.

## When to use

- The user wants a standard scRNA-seq pipeline
- The analysis can be expressed as a mostly linear workflow
- You can decide parameters from a small set of QC and clustering figures
- The deliverable is a reproducible script plus output artifacts

## Do not use as the primary workflow

- The user explicitly requests exploratory or iterative notebook analysis
- The task depends on repeated branching choices that are not known up front
- The dataset or modality falls outside standard scRNA-seq assumptions

In those cases, switch to the exploration strategy and document why.

## Required reads before coding

1. `./SKILL.md`
2. `./quality_control.md`
3. `./cell_type_annotation.md` if annotation is requested
4. `./parallel_computing.md` for large or slow runs

## Project layout

Create a fresh project under the active workdir:

```text
<workdir>/projects/<task_name>/
  data/
  results/
  script.py or script.R
  report_analysis.md
```

Rules:

- Use absolute paths only
- Never overwrite the original input data
- Keep final outputs inside the project directory

## Template selection

- Use `templates/scanpy_qc_clustering.py` for AnnData and Python workflows
- Use `templates/seurat_qc_clustering.R` for Seurat and R workflows

Read the template first, then adapt only what is needed:

- Input loader and file paths
- Species-specific mitochondrial prefix
- QC thresholds
- Number of PCs, HVGs, and clustering resolution
- Batch variable and correction step if applicable
- Output file names and report summary content

## Minimum execution workflow

1. Read the relevant template and required skills.
2. Inspect the input format and metadata enough to pick the loader and species assumptions.
3. Adapt the script into the project directory.
4. Run the script from the project directory.
5. Review generated QC and clustering figures.
6. If thresholds or clustering are clearly poor, make one focused revision and rerun.
7. Write `report_analysis.md`.

## QC and parameter decisions

Do not hard-code template defaults without checking the data.

- QC thresholds must come from the observed distributions
- Follow the conditional rules in `quality_control.md`
- If raw counts are unavailable and an ambient RNA step is skipped, document why
- If doublet scoring is not feasible, document why and continue only if the rest of the analysis remains interpretable
- If batches exist, inspect whether correction is needed before adding it

## Reporting

Always create `report_analysis.md` with these sections:

```markdown
# Analysis Report

## Summary
## Skills Used
## Data
## Parameters
## Results
## Key Findings
## Next Steps
```

Include:

- Input files used
- Script path
- Key thresholds and analysis parameters
- Output files produced
- Which skills were consulted
- Any major deviations from the standard workflow

## Failure policy

Stop and report the blocker instead of improvising when:

- Required runtimes or packages are missing
- Input files cannot be read with the expected loader
- The dataset is not standard scRNA-seq and needs a different workflow

The fast path is valuable only if the result stays reproducible and scientifically defensible.
