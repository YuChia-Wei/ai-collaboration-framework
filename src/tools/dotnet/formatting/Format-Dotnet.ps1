#Requires -Version 7.3
[CmdletBinding(DefaultParameterSetName = 'SelectedFiles')]
param(
    [Parameter(Mandatory)]
    [string] $Workspace,

    [Parameter(Mandatory, ParameterSetName = 'SelectedFiles')]
    [ValidateNotNullOrEmpty()]
    [string[]] $Files,

    [Parameter(Mandatory, ParameterSetName = 'WholeWorkspace')]
    [switch] $WholeWorkspace,

    [ValidateSet('All', 'Whitespace', 'Style', 'Analyzers')]
    [string] $Mode = 'Whitespace',
    [switch] $Apply,
    [switch] $Restore,
    [string[]] $SdkOptions = @()
)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$PSNativeCommandArgumentPassing = 'Standard'
$workspaceFile = Get-Item -LiteralPath $Workspace
if ($workspaceFile -isnot [IO.FileInfo]) {
    throw 'Specify a project or solution file as the workspace.'
}
if ($PSCmdlet.ParameterSetName -eq 'WholeWorkspace' -and !$WholeWorkspace) {
    throw 'Use -Files or explicitly enable -WholeWorkspace.'
}
if ($SdkOptions -match '^(@|--$|--(include|folder|verify-no-changes|no-restore)([=:]|$))') {
    throw 'Use the script parameters to select files, check or apply, and control restore.'
}

$formatArgs = @('format')
if ($Mode -ne 'All') { $formatArgs += $Mode.ToLowerInvariant() }
$formatArgs += $workspaceFile.FullName
if (!$Apply) { $formatArgs += '--verify-no-changes' }
if (!$Restore) { $formatArgs += '--no-restore' }
$formatArgs += $SdkOptions

$workspaceDirectory = $workspaceFile.DirectoryName
$workspacePrefix = $workspaceDirectory
if (!$workspacePrefix.EndsWith([IO.Path]::DirectorySeparatorChar)) {
    $workspacePrefix += [IO.Path]::DirectorySeparatorChar
}
if ($PSCmdlet.ParameterSetName -eq 'SelectedFiles') {
    $formatArgs += '--include'
    foreach ($file in $Files) {
        if ($file.IndexOfAny([char[]]'*?') -ge 0 -or (!$IsWindows -and $file.Contains('\'))) {
            throw "Selected file cannot contain SDK glob characters or a POSIX backslash: $file"
        }
        $fullPath = [IO.Path]::GetFullPath($file, $workspaceDirectory)
        if (![IO.File]::Exists($fullPath)) {
            throw "Selected file does not exist: $file"
        }
        if (!$fullPath.StartsWith($workspacePrefix, [StringComparison]::Ordinal)) {
            throw "Selected file must be under the workspace directory: $file"
        }
        $relative = $fullPath.Substring($workspacePrefix.Length)
        # Prefix the include path to keep names such as @file.cs literal.
        $formatArgs += '.' + [IO.Path]::DirectorySeparatorChar + $relative
    }
}

Push-Location -LiteralPath $workspaceDirectory
try {
    & dotnet @formatArgs
    $formatExit = $LASTEXITCODE
}
finally {
    Pop-Location
}
exit $formatExit
