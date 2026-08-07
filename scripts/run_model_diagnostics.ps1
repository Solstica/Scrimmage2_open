$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

python modules/30_q2/code/export_q2_diagnostics.py --project .
python modules/40_q3/code/export_q3_identifiability.py --project .
python scripts/verify_model_diagnostics.py
