# StarDist Model Archive

These folders were copied from the read-only `RingCanals` working repository so
the segmentation notebooks in this publication repo can load models locally.
Training logs and transient checkpoint metadata were omitted; each archived
model keeps the config, thresholds when present, and best/last weight files.

## Models

- `Fas3_round9`: loaded by
  `Code/Fig1_WT_Fas3_DAPI_Stardist_segmentation.ipynb`. The source notebook was
  `RingCanals/Code/StardistPrediction_Fas3_DAPI_RGB.ipynb`.
- `ring_canals`: loaded by
  `Code/Fig2_Fig3_Fas3_Vsg_RC_Stardist_segmentation.ipynb`. The source notebook
  was `RingCanals/Code/StardistPrediction_Fas3_Vsg.ipynb`.
- `3D_Stardist_FINETUNED`: copied because this is the named model in the
  manuscript workflow notes. Among the RingCanals prediction notebooks inspected,
  it is loaded by `RingCanals/Code/StardistPrediction_Fas3_DAPI_shrb.ipynb`;
  the cleaned copy is
  `Code/Fig3_Fig4_shrbRNAi_Fas3_DAPI_Stardist_segmentation.ipynb`.

## Provenance Note

The four notebooks originally identified for copying did not all use
`3D_Stardist_FINETUNED`: the WT Fas3/DAPI notebook loaded `Fas3_round9`, and the
Fas3/Vsg notebook loaded `ring_canals`. The `3D_Stardist_FINETUNED` model was
therefore archived alongside those models rather than substituted into notebooks
that did not use it.
