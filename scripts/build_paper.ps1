$ErrorActionPreference = 'Stop'

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$paperDir = Join-Path $projectRoot 'paper'
$buildDir = Join-Path $projectRoot 'build'
$outputDir = Join-Path $projectRoot 'output\pdf'
$abstractSource = Join-Path $projectRoot 'modules\00_abstract\paper\abstract.tex'
$abstractCompat = Join-Path $paperDir 'abstract_content.tex'
$sectionDir = Join-Path $paperDir 'sections'

# Fail closed on stale numerical results or unregistered body figures before
# spending time on the full XeLaTeX build.
& python (Join-Path $projectRoot 'scripts\verify_paper_a_results.py')
if ($LASTEXITCODE -ne 0) { throw 'Frozen-result verification failed.' }
& python (Join-Path $projectRoot 'scripts\check_writing_quality.py')
if ($LASTEXITCODE -ne 0) { throw 'Writing/figure verification failed.' }

New-Item -ItemType Directory -Force $buildDir, $outputDir, $sectionDir | Out-Null
Copy-Item -LiteralPath $abstractSource -Destination $abstractCompat -Force

$sectionMap = @{
    'modules\10_restatement\paper\restatement.tex' = '01_restatement.tex'
    'modules\12_assumptions\paper\assumptions.tex' = '02_assumptions.tex'
    'modules\11_notation\paper\notation.tex' = '03_notation.tex'
    'modules\20_q1\paper\q1.tex' = 'Q1.tex'
    'modules\30_q2\paper\q2.tex' = 'Q2.tex'
    'modules\40_q3\paper\q3.tex' = 'Q3.tex'
    'modules\50_evaluation\paper\evaluation.tex' = '90_evaluation.tex'
    'modules\60_references\paper\references.tex' = '91_references.tex'
    'modules\70_appendix\paper\appendix_code.tex' = '92_appendix_code.tex'
    'modules\80_ai_report\paper\ai_report.tex' = '93_ai_report.tex'
}
foreach ($relativeSource in $sectionMap.Keys) {
    Copy-Item -LiteralPath (Join-Path $projectRoot $relativeSource) `
        -Destination (Join-Path $sectionDir $sectionMap[$relativeSource]) -Force
}

Push-Location $paperDir
try {
    latexmk -xelatex -interaction=nonstopmode -halt-on-error `
        "-outdir=$buildDir" paper_template.tex
    if ($LASTEXITCODE -ne 0) { throw 'Full paper build failed.' }
}
finally {
    Pop-Location
}

$builtPdf = Join-Path $buildDir 'paper_template.pdf'
# Windows PowerShell 5.1 reads UTF-8 files without a BOM using the active ANSI
# code page. Build the Chinese delivery name from code points so the script
# remains encoding-safe in both Windows PowerShell and PowerShell 7.
$finalPdfName = 'run_02_' + (-join @(
    [char]0x771F, [char]0x9898, [char]0x89E3, [char]0x6790
)) + '.pdf'
$finalPdf = Join-Path $outputDir $finalPdfName
Copy-Item -LiteralPath $builtPdf -Destination $finalPdf -Force
Get-FileHash -Algorithm SHA256 -LiteralPath $finalPdf