# Mendoza Ring Canal

Analysis code and source data for the Mendoza ring canal manuscript.

## Repository layout

- `Code/`: R Markdown and Jupyter notebooks for each figure panel or supporting analysis.
- `Code/analysis_helpers.R`: shared plotting, import, and summary helpers used by the notebooks.
- `Code/utils/`: Python helper functions used by the image segmentation notebooks.
- `Data/`: CSV inputs required by the included notebooks, named by the figure panel they support.
- `Models/Stardist/`: archived StarDist model configs and weights used by the segmentation notebooks.
- `Results/`: generated figure PDFs, named by the figure panel they support.
- `Figures.pdf`: assembled figure file.
- `Ring Canal manuscript.docx`: manuscript draft containing values reported from these analyses.

## Reproducing the analyses

Open `MendozaRingCanal.Rproj` in RStudio, then run the relevant `.Rmd` file from
the `Code/` directory. Each notebook reads from `../Data/` and writes its figure
PDF to `../Results/`. The R Markdown headers use `output: null` so the files can
serve as readable source notebooks without creating a separate knitted document.

To execute all analysis chunks from the command line without rendering HTML:

```bash
Rscript -e "old <- getwd(); setwd('Code'); for (f in list.files(pattern='[.]Rmd$')) { message('Checking ', f); r <- tempfile(fileext='.R'); knitr::purl(f, output=r, quiet=TRUE); source(r, echo=FALSE) }; setwd(old)"
```

To render a standalone HTML/PDF/Word notebook later, temporarily replace
`output: null` in that file with the desired R Markdown output format.

## Main analysis notebooks

- `Fig1D_WT_germarium_late_stage_RC_composition.Rmd`: Fig. 1D ring canal composition in germaria and late-stage follicles.
- `Fig1E_L_SuppFig2E_WT_RC_cell_count_quantification.Rmd`: Fig. 1E/L and Supp. Fig. 2E WT ring canal-to-cell ratios and Pnut+ ring canal summaries.
- `Fig2I_pnutRNAi_DAPI_ploidy.Rmd`: Fig. 2I Pnut RNAi DAPI intensity/ploidy comparison.
- `Fig2L_pnutRNAi_Vsg_RC_to_cell_ratio.Rmd`: Fig. 2L Pnut RNAi Vsg+ ring canal-to-cell ratios.
- `Fig3E_shrbRNAi_Vsg_RC_to_cell_ratio.Rmd`: Fig. 3E Shrb RNAi Vsg+ ring canal-to-cell ratios.
- `Fig4C_shrbRNAi_Cas_LamC_phenotype_penetrance.Rmd`: Fig. 4C Shrb RNAi Cas/LamC phenotype penetrance.
- `Fig4F_shrbRNAi_EdU_positive_cells.Rmd`: Fig. 4F Shrb RNAi EdU-positive follicle cell percentages.
- `Fig4I_shrbRNAi_LamC_EdU_cells_per_germarium.Rmd`: Fig. 4I Shrb RNAi LamC+/EdU+ cells per germarium.
- `SuppFig3E_F_WT_pTyr_Pav_Vsg_quantification.Rmd`: Supp. Fig. 3E/F WT pTyr enrichment among Vsg and Pav/Vsg structures.
- `SuppFig4H_pnutRNAi_EdU_positive_cells.Rmd`: Supp. Fig. 4H Pnut RNAi EdU-positive follicle cell percentages.
- `Methods_Stardist_model_assessment.Rmd`: Stardist segmentation precision and recall assessment for the methods.

The matching CSV inputs in `Data/` and generated PDFs in `Results/` use the same
figure-panel prefixes where possible.

## Image segmentation notebooks

These cleaned Jupyter notebooks were copied from the read-only `RingCanals`
working repository, stripped of transient outputs, and renamed by figure/pipeline
role. Raw image stacks are not included in this publication repo; update the
path-setting cell at the top of each notebook before rerunning locally.

- `Fig1_WT_Fas3_DAPI_Stardist_segmentation.ipynb`: Fig. 1 WT Fas3/DAPI segmentation, cleaned from `StardistPrediction_Fas3_DAPI_RGB.ipynb`; loads `Models/Stardist/Fas3_round9`.
- `Fig2_Fig3_Fas3_Vsg_RC_Stardist_segmentation.ipynb`: Fig. 2/Fig. 3 Fas3/Vsg ring-canal segmentation, cleaned from `StardistPrediction_Fas3_Vsg.ipynb`; loads `Models/Stardist/ring_canals`.
- `Fig2I_pnutRNAi_DAPI_label_correction_napari.ipynb`: Fig. 2I pnut(RNAi) DAPI label generation and napari correction, cleaned from `Pnut_napari.ipynb`.
- `Fig2I_pnutRNAi_DAPI_label_postprocessing.ipynb`: Fig. 2I pnut(RNAi) label post-processing, cleaned from `Pnut_LabelProcessing.ipynb`.
- `Fig3_Fig4_shrbRNAi_Fas3_DAPI_Stardist_segmentation.ipynb`: shrb(RNAi) Fas3/DAPI segmentation notebook added because it is the source prediction notebook that loads `3D_Stardist_FINETUNED`.

See `Models/Stardist/README.md` for model provenance and the note on which
source notebooks actually loaded each StarDist model.
