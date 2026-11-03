#requires -Version 7.0
param(
    [Parameter(Mandatory)] [string] $Executable,
    [Parameter(Mandatory)] [string] $Scratch
)

$ErrorActionPreference = 'Stop'
$Executable = (Resolve-Path -LiteralPath $Executable).Path
$Scratch = [IO.Path]::GetFullPath($Scratch)
if (Test-Path -LiteralPath $Scratch) {
    throw 'Choose a fresh acceptance scratch directory.'
}
$null = New-Item -Path $Scratch -ItemType Directory

function Write-Utf8([string] $File, [string] $Text) {
    [IO.File]::WriteAllText((Join-Path $Scratch $File), $Text, [Text.UTF8Encoding]::new($false))
}

function Assert-Equal($Actual, $Expected, [string] $Label) {
    if ($Actual -cne $Expected) {
        throw "$Label expected <$Expected>, got <$Actual>."
    }
}

function Invoke-Request($Request, [string] $ExpectedError = '') {
    $requestText = if ($Request -is [string]) { $Request } else {
        $Request | ConvertTo-Json -Depth 15 -Compress
    }
    Write-Utf8 'request.json' $requestText

    $start = [Diagnostics.ProcessStartInfo]::new($Executable)
    $start.WorkingDirectory = $Scratch
    $start.UseShellExecute = $false
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $start.StandardOutputEncoding = [Text.Encoding]::UTF8
    $start.StandardErrorEncoding = [Text.Encoding]::UTF8
    $start.ArgumentList.Add('--request')
    $start.ArgumentList.Add('request.json')

    $process = [Diagnostics.Process]::Start($start)
    try {
        $outTask = $process.StandardOutput.ReadToEndAsync()
        $errTask = $process.StandardError.ReadToEndAsync()
        if (!$process.WaitForExit(15000)) {
            $process.Kill($true)
            throw 'Snippet invocation exceeded 15 seconds.'
        }
        $stdout = $outTask.GetAwaiter().GetResult()
        $stderr = $errTask.GetAwaiter().GetResult()
        if ($ExpectedError) {
            Assert-Equal $process.ExitCode 1 'Failure exit code'
            Assert-Equal $stdout '' 'Failure stdout'
            $failure = ConvertFrom-Json -InputObject $stderr
            Assert-Equal $failure.error.code $ExpectedError 'Failure code'
            Assert-Equal $failure.schemaVersion 1 'Failure schema'
            return
        }
        if ($process.ExitCode -ne 0 -or $stderr) {
            throw "Unexpected CLI result ($($process.ExitCode)) $stderr"
        }
        $result = ConvertFrom-Json -InputObject $stdout
        Assert-Equal $result.schemaVersion 1 'Success schema'
        return $result
    }
    finally {
        $process.Dispose()
    }
}

$listed = Invoke-Request @{schemaVersion=1; operation='list'}
Assert-Equal ($listed.snippets.id -join ',') 'interface-method,string-guard' 'Packaged catalog IDs'
$search = Invoke-Request @{schemaVersion=1; operation='search'; query='GUARD'}
Assert-Equal ($search.snippets.id -join ',') 'string-guard' 'Search result'
$inspect = Invoke-Request @{schemaVersion=1; operation='inspect'; id='interface-method'}
Assert-Equal $inspect.snippet.context 'interface-member' 'Inspect context'
Assert-Equal ($inspect.snippet.requiredUsings -join ',') 'System.Threading.Tasks' 'Inspect using'
Assert-Equal $inspect.snippet.parameters.parameterName.default 'value' 'Inspect parameter schema'
Assert-Equal $inspect.source.id 'framework-dotnet' 'Inspect source'
Assert-Equal $inspect.body.Replace("`r`n", "`n") ('${returnType} ${methodName}(${parameterType} ${parameterName});' + "`n") 'Inspect body'

$declaration = (Invoke-Request @{
    schemaVersion=1; operation='render'; id='interface-method'; indent=4
    parameters=@{methodName='ReadAsync'; returnType='Task<string>'}
}).text
Assert-Equal $declaration "    Task<string> ReadAsync(string value);`n" 'Interface fragment'
$guard = (Invoke-Request @{
    schemaVersion=1; operation='render'; id='string-guard'; indent=4
    parameters=@{parameterName='label'}
}).text
Assert-Equal $guard "    ArgumentException.ThrowIfNullOrWhiteSpace(label);`n" 'Guard fragment'

Invoke-Request @{schemaVersion=1; operation='render'; id='string-guard'} 'missing-parameter'
Invoke-Request @{
    schemaVersion=1; operation='render'; id='string-guard'; parameters=@{parameterName='label'; extra='value'}
} 'unknown-parameter'
Invoke-Request @{
    schemaVersion=1; operation='render'; id='string-guard'; parameters=@{parameterName='class'}
} 'invalid-parameter'
Invoke-Request @{
    schemaVersion=1; operation='render'; id='interface-method'; parameters=@{methodName='Read'; returnType='List<int>'}
} 'invalid-parameter'
Invoke-Request '{"schemaVersion":1,"operation":"list","extra":0}' 'invalid-request'
Invoke-Request '{"schemaVersion":1,"operation":"list","operation":"render"}' 'invalid-request'
Invoke-Request '{"schemaVersion":2,"operation":"list"}' 'unsupported-request-schema'
Invoke-Request @{schemaVersion=1; operation='list'; source='missing.json'} 'unreadable-catalog'

$custom = @{
    id='custom-probe'; title='Probe'; description='Custom method body'; context='method-body'
    bodyFile='custom-probe.snippet'; tags=@(); requiredUsings=@(); preconditions=@()
    parameters=@{variable=@{kind='identifier'}; comment=@{kind='text'}}
}
$lazy = @{
    id='unreadable'; title='Unreadable'; description='A catalog row with no body on disk'; context='method-body'
    bodyFile='missing.snippet'; tags=@(); requiredUsings=@(); preconditions=@(); parameters=@{}
}
$catalog = @{schemaVersion=1; source=@{id='custom'; version='2.0.0'}; snippets=@($custom, $lazy)}
Write-Utf8 'custom.json' ($catalog | ConvertTo-Json -Depth 15)
$customList = Invoke-Request @{schemaVersion=1; operation='list'; source='custom.json'}
Assert-Equal ($customList.snippets.id -join ',') 'custom-probe,unreadable' 'Lazy metadata list'
$customSearch = Invoke-Request @{schemaVersion=1; operation='search'; source='custom.json'; query='Unreadable'}
Assert-Equal ($customSearch.snippets.id -join ',') 'unreadable' 'Lazy metadata search'
Invoke-Request @{schemaVersion=1; operation='inspect'; source='custom.json'; id='unreadable'} 'unreadable-body'
Invoke-Request @{schemaVersion=1; operation='inspect'; source='custom.json'; id='string-guard'} 'snippet-not-found'

Write-Utf8 'custom-probe.snippet' ''
Invoke-Request @{schemaVersion=1; operation='inspect'; source='custom.json'; id='custom-probe'} 'invalid-body'
if ($IsLinux) {
    Remove-Item -LiteralPath (Join-Path $Scratch 'custom-probe.snippet')
    & mkfifo -- (Join-Path $Scratch 'custom-probe.snippet')
    if ($LASTEXITCODE -ne 0) { throw 'Could not create FIFO regression fixture.' }
    try {
        Invoke-Request @{schemaVersion=1; operation='inspect'; source='custom.json'; id='custom-probe'} 'invalid-body'
    }
    finally {
        Remove-Item -LiteralPath (Join-Path $Scratch 'custom-probe.snippet')
    }
}

Write-Utf8 'custom-probe.snippet' @'
// ${comment}

if (true) {
    var ${variable} = "$${顯示}";
    return ${variable};
}
'@
$customRequest = @{
    schemaVersion=1; operation='render'; source='custom.json'; id='custom-probe'; indent=4; newline='crlf'
    parameters=@{variable='result'; comment=('first' + "`r`n" + '// second ${verbatim}')}
}
$customRender = Invoke-Request $customRequest
Assert-Equal $customRender.source.version '2.0.0' 'Custom source version'
$expectedCustom = @(
    '    // first',
    '    // second ${verbatim}',
    '',
    '    if (true) {',
    '        var result = "${顯示}";',
    '        return result;',
    '    }'
) -join "`r`n"
Assert-Equal $customRender.text $expectedCustom 'Custom literal, repeated, escaped and multiline output'

Write-Utf8 'custom-probe.snippet' 'return ${unknown};'
Invoke-Request $customRequest 'unknown-placeholder'
Write-Utf8 'custom-probe.snippet' 'return ${variable;'
Invoke-Request @{schemaVersion=1; operation='inspect'; source='custom.json'; id='custom-probe'} 'invalid-placeholder'
$catalog.schemaVersion = 2
Write-Utf8 'wrong-schema.json' ($catalog | ConvertTo-Json -Depth 15)
Invoke-Request @{schemaVersion=1; operation='list'; source='wrong-schema.json'} 'unsupported-catalog-schema'
$catalog.schemaVersion = 1
$catalog.snippets = @($custom, $custom)
Write-Utf8 'duplicate.json' ($catalog | ConvertTo-Json -Depth 15)
Invoke-Request @{schemaVersion=1; operation='list'; source='duplicate.json'} 'duplicate-snippet-id'
$catalog.snippets = @($custom)
$custom.parameters.comment.kind = 'script'
Write-Utf8 'invalid-kind.json' ($catalog | ConvertTo-Json -Depth 15)
Invoke-Request @{schemaVersion=1; operation='list'; source='invalid-kind.json'} 'invalid-catalog'

Write-Utf8 'Consumer.csproj' @'
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
</Project>
'@
Write-Utf8 'Program.cs' (@'
using System;
using System.Threading.Tasks;

Guard("ok");
ExpectRejected(null, typeof(ArgumentNullException));
ExpectRejected("", typeof(ArgumentException));
ExpectRejected(" 	", typeof(ArgumentException));

if (Probe() != "${顯示}")
    throw new InvalidOperationException("Unexpected custom fragment result.");

static void ExpectRejected(string? label, Type expectedType)
{
    try
    {
        Guard(label);
    }
    catch (ArgumentException error) when (error.GetType() == expectedType && error.ParamName == "label")
    {
        return;
    }

    throw new InvalidOperationException("Guard did not reject the supplied value as expected.");
}

static void Guard(string? label)
{
'@ + "`n" + $guard + @'
}

static string Probe()
{
'@ + "`n" + $customRender.text + "`n" + @'
}

interface IReader
{
'@ + "`n" + $declaration + "}`n")

dotnet run --project (Join-Path $Scratch 'Consumer.csproj') --configuration Release
if ($LASTEXITCODE -ne 0) {
    throw "Rendered C# consumer failed with exit code $LASTEXITCODE."
}
'Snippet CLI and rendered C# consumer acceptance passed.'
