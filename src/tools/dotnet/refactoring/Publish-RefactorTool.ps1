param(
  [Parameter(Mandatory = $true)][string]$Destination,
  [string]$Archive,
  [string]$Version = '0.1.0-dev.1'
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$refactorDestination = [IO.Path]::GetFullPath($Destination)
$refactorArchive = if ($Archive) { [IO.Path]::GetFullPath($Archive) }
if ((Test-Path -LiteralPath $refactorDestination) -or ($refactorArchive -and (Test-Path -LiteralPath $refactorArchive))) {
  throw 'Destination and archive must both be new paths. No existing installation is overwritten.'
}
if ($refactorArchive -and $refactorArchive.StartsWith($refactorDestination.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
  throw 'Archive must be outside the published directory.'
}

$refactorProject = Join-Path $PSScriptRoot 'RefactorTool.csproj'
& dotnet publish $refactorProject -c Release -r win-x64 --self-contained false `
  "-p:Version=$Version" -p:CopyOutputSymbolsToPublishDirectory=false -o $refactorDestination
if ($LASTEXITCODE -ne 0) { throw 'Publish failed; preserve the partial destination for diagnosis and choose a new path after repair.' }

$refactorExpected = @('README.md', 'RefactorTool.exe', 'THIRD-PARTY-NOTICES.txt') | Sort-Object
$refactorPublished = @(Get-ChildItem -LiteralPath $refactorDestination -Force | Select-Object -ExpandProperty Name | Sort-Object)
if (($refactorPublished -join ',') -cne ($refactorExpected -join ',')) { throw 'Unexpected single-file publish inventory.' }

# NuGet dependencies are explicit build inputs. Retain their actual metadata and
# supplemental notices with the artifact; none is loaded from a source checkout
# at runtime. project.assets.json selects exact versions and package roots.
$refactorAssets = Get-Content (Join-Path $PSScriptRoot 'obj/project.assets.json') -Raw | ConvertFrom-Json
$refactorLicenses = Join-Path $refactorDestination 'licenses'
New-Item -ItemType Directory -Path $refactorLicenses | Out-Null
foreach ($refactorLibrary in $refactorAssets.libraries.PSObject.Properties) {
  if ($refactorLibrary.Value.type -ne 'package') { continue }
  $refactorPackage = $null
  foreach ($refactorFolder in $refactorAssets.packageFolders.PSObject.Properties.Name) {
    $refactorCandidate = Join-Path $refactorFolder $refactorLibrary.Value.path
    if (Test-Path -LiteralPath $refactorCandidate -PathType Container) { $refactorPackage = $refactorCandidate; break }
  }
  if ($null -eq $refactorPackage) { throw "Missing restored package: $($refactorLibrary.Name)" }
  $refactorNoticeDestination = Join-Path $refactorLicenses ($refactorLibrary.Name.Replace('/', '-'))
  New-Item -ItemType Directory -Path $refactorNoticeDestination | Out-Null
  Get-ChildItem -LiteralPath $refactorPackage -File |
    Where-Object { $_.Extension -eq '.nuspec' -or $_.Name -match '^(LICENSE|THIRD.?PARTY.?NOTICES)' } |
    Copy-Item -Destination $refactorNoticeDestination
}
& (Join-Path $refactorDestination 'RefactorTool.exe') --version
if ($LASTEXITCODE -ne 0) { throw 'Published tool did not start.' }
if ($refactorArchive) {
  $refactorArchiveParent = [IO.Path]::GetDirectoryName($refactorArchive)
  New-Item -ItemType Directory -Force -Path $refactorArchiveParent | Out-Null
  Compress-Archive -Path (Join-Path $refactorDestination '*') -DestinationPath $refactorArchive -CompressionLevel Optimal
  Get-FileHash -Algorithm SHA256 -LiteralPath $refactorArchive
}
