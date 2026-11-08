[CmdletBinding()]
param(
    [Parameter(Mandatory)][string] $SourceRoot,
    [Parameter(Mandatory)][string] $PackageDirectory,
    [Parameter(Mandatory)][string] $WorkDirectory
)

$ErrorActionPreference = 'Stop'
$SourceRoot = (Get-Item -LiteralPath $SourceRoot).FullName
$project = Join-Path $SourceRoot 'tests/dotnet-generation/templates/artifact/Generation.Templates.ArtifactIntegrationTests.csproj'
if (!(Test-Path -LiteralPath $project -PathType Leaf)) {
    if (Test-Path -LiteralPath (Join-Path $SourceRoot 'src/tools/dotnet/formatting/Format-Dotnet.ps1')) {
        throw 'The selected source is missing its template package acceptance project.'
    }
    Write-Host 'Historical source has no native template package acceptance project; its existing builder checks remain authoritative.'
    exit 0
}
$packages = @(Get-ChildItem -LiteralPath $PackageDirectory -Filter '*.nupkg' -File)
if ($packages.Count -ne 1) { throw 'Expected one actual delivery template package.' }
$work = New-Item -ItemType Directory -Path $WorkDirectory -Force
$oldPackage = $env:AICF_TEMPLATE_PACKAGE
$oldWork = $env:AICF_TEST_WORK
Push-Location -LiteralPath $work.FullName
try {
    $env:AICF_TEMPLATE_PACKAGE = $packages[0].FullName
    $env:AICF_TEST_WORK = Join-Path $work.FullName 'fixtures'
    dotnet test $project -c Release --artifacts-path (Join-Path $work.FullName 'build') --results-directory $work.FullName --logger 'trx;LogFileName=templates-packed.trx' -- RunConfiguration.TreatNoTestsAsError=true
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & (Join-Path $SourceRoot 'tests/dotnet-test-support/Assert-ExecutedTests.ps1') -Report (Join-Path $work.FullName 'templates-packed.trx') -Expected 1
}
finally {
    Pop-Location
    $env:AICF_TEMPLATE_PACKAGE = $oldPackage
    $env:AICF_TEST_WORK = $oldWork
}
