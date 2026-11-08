[CmdletBinding()]
param(
    [Parameter(Mandatory)][string] $Report,
    [Parameter(Mandatory)][int] $Expected
)

$ErrorActionPreference = 'Stop'
[xml] $testRun = Get-Content -LiteralPath $Report -Raw
$counters = $testRun.TestRun.ResultSummary.Counters
if ([int]$counters.total -ne $Expected -or [int]$counters.executed -ne $Expected -or [int]$counters.passed -ne $Expected) {
    throw "Expected $Expected passing tests in '$Report'. Found $($counters.total) selected, $($counters.executed) executed, $($counters.passed) passed."
}
Write-Host "$Expected required tests passed ($Report)."
