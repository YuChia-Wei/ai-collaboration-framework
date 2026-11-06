param(
  [Parameter(Mandatory = $true)][string]$Destination,
  [Parameter(Mandatory = $true)][string]$Archive
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$refactorDestination = [IO.Path]::GetFullPath($Destination)
$refactorArchive = [IO.Path]::GetFullPath($Archive)
if ((Test-Path -LiteralPath $refactorDestination) -or (Test-Path -LiteralPath $refactorArchive)) {
  throw 'Destination and archive must both be new paths. No existing installation is overwritten.'
}
if ($refactorArchive.StartsWith($refactorDestination.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
  throw 'Archive must be outside the published directory.'
}

$refactorProject = Join-Path $PSScriptRoot 'RefactorTool.csproj'
& dotnet publish $refactorProject -c Release -r win-x64 --self-contained true `
  -p:PublishAot=false -p:PublishTrimmed=false -p:PublishSingleFile=false `
  -p:CopyOutputSymbolsToPublishDirectory=false -o $refactorDestination
if ($LASTEXITCODE -ne 0) { throw 'Publish failed; preserve the partial destination for diagnosis and choose a new path after repair.' }

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
# SDK runtime packs are downloadDependencies, not ordinary NuGet libraries.
$refactorRuntime = @($refactorAssets.project.frameworks.'net10.0'.downloadDependencies |
  Where-Object { $_.name -eq 'Microsoft.NETCore.App.Runtime.win-x64' })
if ($refactorRuntime.Count -ne 1 -or $refactorRuntime[0].version -notmatch '^\[([^,]+), \1\]$') {
  throw 'Cannot resolve the exact restored runtime pack; do not distribute this directory.'
}
$refactorRuntimeVersion = $Matches[1]
$refactorRuntimeDirectory = $null
foreach ($refactorFolder in $refactorAssets.packageFolders.PSObject.Properties.Name) {
  $refactorCandidate = Join-Path $refactorFolder "microsoft.netcore.app.runtime.win-x64/$refactorRuntimeVersion"
  if (Test-Path -LiteralPath $refactorCandidate -PathType Container) { $refactorRuntimeDirectory = $refactorCandidate; break }
}
if ($null -eq $refactorRuntimeDirectory) { throw 'Restored runtime pack is missing.' }
$refactorRuntimeLicenses = Join-Path $refactorLicenses "Microsoft.NETCore.App.Runtime.win-x64-$refactorRuntimeVersion"
New-Item -ItemType Directory -Path $refactorRuntimeLicenses | Out-Null
foreach ($refactorNotice in @('LICENSE.TXT', 'THIRD-PARTY-NOTICES.TXT')) {
  Copy-Item -LiteralPath (Join-Path $refactorRuntimeDirectory $refactorNotice) -Destination $refactorRuntimeLicenses
}
foreach ($refactorRequired in @('RefactorTool.exe', 'RefactorTool.dll', 'RefactorTool.deps.json', 'RefactorTool.runtimeconfig.json', 'README.md', 'THIRD-PARTY-NOTICES.txt', 'BuildHost-netcore/Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.dll')) {
  if (-not (Test-Path -LiteralPath (Join-Path $refactorDestination $refactorRequired) -PathType Leaf)) { throw "Published dependency is missing: $refactorRequired" }
}
& (Join-Path $refactorDestination 'RefactorTool.exe') --version
if ($LASTEXITCODE -ne 0) { throw 'Published tool did not start.' }
$refactorArchiveParent = [IO.Path]::GetDirectoryName($refactorArchive)
New-Item -ItemType Directory -Force -Path $refactorArchiveParent | Out-Null
Compress-Archive -Path (Join-Path $refactorDestination '*') -DestinationPath $refactorArchive -CompressionLevel Optimal
Get-FileHash -Algorithm SHA256 -LiteralPath $refactorArchive
