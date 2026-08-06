$ErrorActionPreference = 'Stop'

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$buildRoot = Join-Path $projectRoot 'build\previews'
$previews = @(
    @{ Module = '20_q1'; Entry = 'q1_preview.tex' },
    @{ Module = '30_q2'; Entry = 'q2_preview.tex' },
    @{ Module = '40_q3'; Entry = 'q3_preview.tex' }
)

foreach ($preview in $previews) {
    $paperDir = Join-Path $projectRoot ("modules\{0}\paper" -f $preview.Module)
    $outDir = Join-Path $buildRoot $preview.Module
    New-Item -ItemType Directory -Force $outDir | Out-Null
    Push-Location $paperDir
    try {
        latexmk -xelatex -interaction=nonstopmode -halt-on-error `
            "-outdir=$outDir" $preview.Entry
        if ($LASTEXITCODE -ne 0) {
            throw "Preview build failed: $($preview.Entry) (exit $LASTEXITCODE)"
        }
    }
    finally {
        Pop-Location
    }
}

Get-ChildItem -LiteralPath $buildRoot -Recurse -Filter '*_preview.pdf' |
    Select-Object FullName, Length, LastWriteTime
