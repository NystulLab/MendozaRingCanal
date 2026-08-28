# Nystul Lab Template Repo

Standard project structure for Nystul Lab work.

## Folder structure

- `Code/`  
  Analysis scripts, notebooks, and reusable functions (R, Python, etc.).

- `Data/`  
  Small/processed data that can reasonably live in git (CSV, RDS, small TIFFs, etc.).  
  **Do not** put huge raw data here; use `LargeImages/` or external storage.

- `LargeImages/`  
  Large raw image data (e.g. multi-GB TIFF/OME-TIFF). Usually not tracked by git; see `.gitignore`.

- `Results/`  
  Output from analyses: figures, tables, summary data, etc.

- `WyntonLogs/` (optional)  
  SLURM log files from Wynton jobs.

- `LargeFiles/` (optional)  
  Other large non-image files you don’t want in git.

## Getting started

1. Create a new repo using this template on GitHub.
2. Clone it locally.
3. If you use RStudio, open the `.Rproj` file.  
   If you use Python, create the conda env:

   ```bash
   conda env create -f env.yml
   conda activate nystul-lab

