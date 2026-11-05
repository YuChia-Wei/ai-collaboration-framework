#Requires -Version 7.0
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^\d+\.\d+\.\d+(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?$')]
    [string] $Version,
    [Parameter(Mandatory)] [string] $OutputRoot,
    [ValidatePattern('^[a-z0-9]+(?:-[a-z0-9]+)+$')]
    [string] $RuntimeIdentifier = 'win-x64',
    [switch] $NativeAot
)

$ErrorActionPreference = 'Stop'
$OutputRoot = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputRoot)
$platform = if ($IsWindows) { 'win-' } elseif ($IsLinux) { 'linux-' } else { 'osx-' }
if (!$RuntimeIdentifier.StartsWith($platform, [StringComparison]::Ordinal)) {
    throw 'Package on the target OS to preserve executable modes and use its native AOT toolchain.'
}
$mode = if ($NativeAot) { 'aot' } else { 'framework-dependent-coreclr-single-file' }
$name = "SnippetTool-$Version-$RuntimeIdentifier-$mode"
$destination = Join-Path $OutputRoot $name
if (Test-Path -LiteralPath $destination) {
    throw "Choose a fresh output directory; no existing package is replaced: $destination"
}
$project = Join-Path $PSScriptRoot 'snippet-tool/SnippetTool.csproj'
$publish = Join-Path $destination 'publish'
$artifacts = Join-Path $destination 'build'
$archive = Join-Path $destination ($name + $(if ($IsWindows) { '.zip' } else { '.tar.gz' }))
New-Item -ItemType Directory -Path $destination | Out-Null

& dotnet publish $project -c Release -r $RuntimeIdentifier `
    --self-contained "$($NativeAot.IsPresent.ToString().ToLowerInvariant())" `
    --artifacts-path $artifacts -o $publish "-p:Version=$Version" `
    "-p:PublishAot=$($NativeAot.IsPresent.ToString().ToLowerInvariant())" `
    "-p:PublishSingleFile=$((!$NativeAot.IsPresent).ToString().ToLowerInvariant())" `
    -p:DebugType=None -p:DebugSymbols=false
if ($LASTEXITCODE -ne 0) { throw "Snippet publish failed ($mode); keep the output for diagnosis." }

$executable = if ($IsWindows) { 'SnippetTool.exe' } else { 'SnippetTool' }
foreach ($member in @($executable, 'README.md', 'snippets/catalog.json',
        'snippets/interface-method.snippet', 'snippets/string-guard.snippet')) {
    if (!(Test-Path -LiteralPath (Join-Path $publish $member) -PathType Leaf)) {
        throw "Required publish member missing: $member"
    }
}
$catalog = Get-Content -LiteralPath (Join-Path $publish 'snippets/catalog.json') -Raw | ConvertFrom-Json
$package = [ordered]@{
    schemaVersion = 1
    name = 'SnippetTool'
    version = $Version
    runtimeIdentifier = $RuntimeIdentifier
    mode = $mode
    targetFramework = 'net10.0'
    executable = $executable
    source = $catalog.source
}
$package | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $publish 'package.json') -Encoding utf8NoBOM

if ($IsWindows) {
    Compress-Archive -Path (Join-Path $publish '*') -DestinationPath $archive
} else {
    & tar -czf $archive -C $publish .
    if ($LASTEXITCODE -ne 0) { throw 'Archive creation failed.' }
}
$digest = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
"$digest  $([IO.Path]::GetFileName($archive))" |
    Set-Content -LiteralPath ($archive + '.sha256') -Encoding ascii
[ordered]@{
    archive = $archive
    sha256 = $digest
    bytes = (Get-Item -LiteralPath $archive).Length
    package = $package
} | ConvertTo-Json -Depth 6
