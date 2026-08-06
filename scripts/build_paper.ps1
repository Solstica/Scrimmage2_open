$ErrorActionPreference = 'Stop'

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$paperDir = Join-Path $projectRoot 'paper'
$buildDir = Join-Path $projectRoot 'build'
$outputDir = Join-Path $projectRoot 'output\pdf'
New-Item -ItemType Directory -Force $buildDir, $outputDir | Out-Null

Push-Location $paperDir
try {
    latexmk -xelatex -interaction=nonstopmode -halt-on-error `
        "-outdir=$buildDir" main.tex
    if ($LASTEXITCODE -ne 0) {
        throw "Full paper build failed (exit $LASTEXITCODE)"
    }
}
finally {
    Pop-Location
}

$builtPdf = Join-Path $buildDir 'main.pdf'
# Windows PowerShell 5.1 reads UTF-8 files without a BOM using the active ANSI
# code page. Build the Chinese delivery name from code points so the script
# remains encoding-safe in both Windows PowerShell and PowerShell 7.
$finalPdfName = 'run_02_' + (-join @(
    [char]0x771F, [char]0x9898, [char]0x89E3, [char]0x6790
)) + '.pdf'
$finalPdf = Join-Path $outputDir $finalPdfName
Copy-Item -LiteralPath $builtPdf -Destination $finalPdf -Force
Get-FileHash -Algorithm SHA256 -LiteralPath $finalPdf
