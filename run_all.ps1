# Rebuild every table and figure from data/raw/ (writes data/processed/ and outputs/).
# Run from the repository root:   powershell -ExecutionPolicy Bypass -File .\run_all.ps1
# Optional switch:                -SkipModels   skip the 5,000-split steps (03, 05, 06); needs their outputs from an earlier run
# 00_anonymize_raw.py is not run here: it needs the original exports, which are not shared.
param([switch]$SkipModels)
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root

# Rscript and Pandoc: edit these lines if your installation lives elsewhere.
$Rscript = (Get-Command Rscript -ErrorAction SilentlyContinue).Source
if (-not $Rscript) { throw "Rscript not found: add R 4.5 to PATH, or set `$Rscript at the top of this script." }
if (-not $env:RSTUDIO_PANDOC -and -not (Get-Command pandoc -ErrorAction SilentlyContinue)) {
  $env:RSTUDIO_PANDOC = "C:\Program Files\RStudio\resources\app\bin\quarto\bin\tools"
}

$Reports = "$Root\outputs\reports"
New-Item -ItemType Directory -Force $Reports | Out-Null

function Render-Rmd($file) {          # knit one R Markdown file to HTML (code with its output)
  & $Rscript -e "rmarkdown::render('$file', output_dir = '../outputs/reports', quiet = TRUE)"
  if ($LASTEXITCODE) { throw "$file failed" }
}
function Run-Notebook($file) {        # execute one notebook and save it, with its output, as HTML
  python -m jupyter nbconvert --to html --execute --ExecutePreprocessor.timeout=7200 --output-dir $Reports $file
  if ($LASTEXITCODE) { throw "$file failed" }
}
function Run-Script($file) {          # run one Python script
  python $file
  if ($LASTEXITCODE) { throw "$file failed" }
}

Push-Location "$Root\analysis"        # all analysis files run from analysis/
Write-Host "`n[1/6] 01_data_processing.Rmd (Method; data/processed)" -ForegroundColor Cyan
Render-Rmd "01_data_processing.Rmd"
Write-Host "`n[2/6] 02_quality_and_visual.Rmd (Table 1, Figure 2)" -ForegroundColor Cyan
Render-Rmd "02_quality_and_visual.Rmd"
if (-not $SkipModels) {
  Write-Host "`n[3/6] 03_classification.ipynb (Tables 2 to 4, Figure 3, Tables S1 to S3; about 4 minutes)" -ForegroundColor Cyan
  Run-Notebook "03_classification.ipynb"
}
Write-Host "`n[4/6] 04_agea_data_processing.Rmd (AGEA sample)" -ForegroundColor Cyan
Render-Rmd "04_agea_data_processing.Rmd"
if (-not $SkipModels) {
  Write-Host "`n[5/6] 05_agea_cross_agent.py (Table S5)" -ForegroundColor Cyan
  Run-Script "05_agea_cross_agent.py"
  Write-Host "`n[6/6] 06_threshold_scenarios.py (Table S4)" -ForegroundColor Cyan
  Run-Script "06_threshold_scenarios.py"
}
Pop-Location
Write-Host "`nDone. Tables and figures are in outputs/." -ForegroundColor Green
