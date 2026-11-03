#Requires -Version 7.0
param(
    [Parameter(Mandatory)]
    [string] $ScratchRoot,
    [string] $TemplateRoot = (Join-Path $PSScriptRoot '../../../src/knowledge/dotnet-backend/tooling/generation/dotnet-new')
)

$ErrorActionPreference = 'Stop'
$ScratchRoot = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($ScratchRoot)
if (Test-Path -LiteralPath $ScratchRoot) {
    throw "Supply a new scratch directory: $ScratchRoot"
}

New-Item -ItemType Directory -Path $ScratchRoot | Out-Null
$delivered = Join-Path $ScratchRoot delivered
Copy-Item -LiteralPath (Resolve-Path -LiteralPath $TemplateRoot).Path -Destination $delivered -Recurse
$hive = Join-Path $ScratchRoot hive

function Invoke-Dotnet {
    & dotnet @args
    if ($LASTEXITCODE -ne 0) {
        throw "dotnet $args exited with $LASTEXITCODE"
    }
}

function Invoke-Template {
    Invoke-Dotnet new @args --debug:custom-hive $hive
}

function Test-WorkItemApi {
    param([string] $ProjectRoot, [string] $ProjectName, [string] $Route)

    $stdout = Join-Path $ProjectRoot server.stdout.log
    $stderr = Join-Path $ProjectRoot server.stderr.log
    $dll = Join-Path $ProjectRoot "bin/Debug/net10.0/$ProjectName.dll"
    $dotnetPath = (Get-Command dotnet -CommandType Application | Select-Object -First 1).Source
    $launchOptions = @{}
    if ($IsWindows) { $launchOptions.WindowStyle = 'Hidden' }
    $server = Start-Process -FilePath $dotnetPath -ArgumentList @("`"$dll`"", '--urls', 'http://127.0.0.1:0') `
        -WorkingDirectory $ProjectRoot -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru @launchOptions
    try {
        $deadline = [DateTime]::UtcNow.AddSeconds(20)
        do {
            if ($server.HasExited) { throw "Backend exited: $(Get-Content -Raw $stderr)" }
            $listen = Get-Content -Raw $stdout | Select-String 'Now listening on: (http://127\.0\.0\.1:\d+)'
            if ($listen) { break }
            Start-Sleep -Milliseconds 150
        } while ([DateTime]::UtcNow -lt $deadline)
        if (!$listen) { throw 'Backend did not report a listening address.' }

        $origin = $listen.Matches[0].Groups[1].Value
        $response = Invoke-WebRequest -Uri "$origin$Route" -Method Post -TimeoutSec 10 `
            -ContentType 'application/json' -Body '{"title":"  Count cartons  "}'
        $created = $response.Content | ConvertFrom-Json
        $location = [string] ($response.Headers.Location | Select-Object -First 1)
        if ($response.StatusCode -ne 201 -or $created.title -cne 'Count cartons' -or
            [guid] $created.id -eq [guid]::Empty -or !$location.EndsWith("$Route/$($created.id)")) {
            throw 'Create returned an unexpected status, resource, or location.'
        }

        $saved = Invoke-RestMethod -Uri ([uri]::new([uri] $origin, $location)) -TimeoutSec 10
        if ($saved.id -cne $created.id -or $saved.title -cne 'Count cartons') {
            throw 'Read did not return the resource created through HTTP.'
        }

        $invalid = Invoke-WebRequest -Uri "$origin$Route" -Method Post -TimeoutSec 10 `
            -ContentType 'application/json' -Body '{"title":"   "}' -SkipHttpErrorCheck
        if ($invalid.StatusCode -ne 400) { throw 'Blank title was accepted.' }

        $missing = Invoke-WebRequest -Uri "$origin$Route/00000000-0000-0000-0000-000000000000" `
            -TimeoutSec 10 -SkipHttpErrorCheck
        if ($missing.StatusCode -ne 404) { throw 'Missing resource did not return 404.' }
        $root = Invoke-WebRequest -Uri "$origin/" -TimeoutSec 10 -SkipHttpErrorCheck
        if ($root.StatusCode -ne 404) { throw 'API project unexpectedly served a root page.' }
    }
    finally {
        if (!$server.HasExited) {
            $server.Kill()
            $server.WaitForExit()
        }
        $server.Dispose()
    }
}

$roots = 'miniapi', 'web-api', 'use-case', 'class', 'interface' | ForEach-Object { Join-Path $delivered $_ }
Invoke-Template install @roots
Invoke-Template list aicf
Invoke-Template aicf-usecase --help

$backend = Join-Path $ScratchRoot 'Sample.Warehouse'
Invoke-Template aicf-miniapi --name Sample.Warehouse --output $backend --dry-run
if (Test-Path -LiteralPath $backend) { throw 'Dry run created output.' }
Invoke-Template aicf-miniapi --name Sample.Warehouse --output $backend
$project = Join-Path $backend 'Sample.Warehouse.csproj'
Invoke-Dotnet build $project

Test-WorkItemApi -ProjectRoot $backend -ProjectName Sample.Warehouse -Route /work-items

$webApi = Join-Path $ScratchRoot 'Sample.WarehouseApi'
Invoke-Template aicf-webapi --name Sample.WarehouseApi --output $webApi
$solution = Join-Path $webApi 'Sample.WarehouseApi.slnx'
$referencesByProject = @{
    'Domain/Sample.WarehouseApi.Domain.csproj' = @()
    'Application/Sample.WarehouseApi.Application.csproj' = @('../Domain/Sample.WarehouseApi.Domain.csproj')
    'Infrastructure/Sample.WarehouseApi.Infrastructure.csproj' = @('../Application/Sample.WarehouseApi.Application.csproj')
    'WebApi/Sample.WarehouseApi.WebApi.csproj' = @(
        '../Application/Sample.WarehouseApi.Application.csproj'
        '../Infrastructure/Sample.WarehouseApi.Infrastructure.csproj'
    )
}
[xml] $solutionXml = Get-Content -Raw -LiteralPath $solution
$members = @($solutionXml.SelectNodes('/Solution/Project') | ForEach-Object { $_.Path } | Sort-Object)
$expectedMembers = @($referencesByProject.Keys | Sort-Object)
if (($members -join '|') -cne ($expectedMembers -join '|')) {
    throw 'The Web API solution did not contain the four expected projects.'
}
foreach ($member in $members) {
    [xml] $projectXml = Get-Content -Raw -LiteralPath (Join-Path $webApi $member)
    $references = @($projectXml.SelectNodes('/Project/ItemGroup/ProjectReference') | ForEach-Object { $_.Include } | Sort-Object)
    if (($references -join '|') -cne ($referencesByProject[$member] -join '|')) {
        throw "$member has unexpected project dependencies."
    }
}
$webApiHost = Join-Path $webApi WebApi
$entryPoints = @(Get-ChildItem -LiteralPath $webApi -Filter Program.cs -File -Recurse)
if ($entryPoints.Count -ne 1 -or $entryPoints[0].FullName -cne (Join-Path $webApiHost 'Program.cs')) {
    throw 'The Web API solution must have one Program.cs in the WebApi host.'
}
Invoke-Dotnet build $solution
Test-WorkItemApi -ProjectRoot $webApiHost -ProjectName Sample.WarehouseApi.WebApi -Route /api/work-items

$application = Join-Path $backend Application
$domain = Join-Path $backend Domain
Invoke-Template aicf-usecase --name DescribeLabel --namespace Sample.Warehouse.Labels --output $application
Invoke-Template aicf-class --name PackingNote --namespace Sample.Warehouse.Labels --output $domain
Invoke-Template aicf-interface --name ILabelReader --namespace Sample.Warehouse.Labels --output $application
$integration = @"
global using Sample.Warehouse.Labels;

namespace Sample.Warehouse;

internal sealed class GeneratedItemReferences(
    IDescribeLabelUseCase useCase,
    PackingNote note,
    ILabelReader reader)
{
    public IDescribeLabelUseCase UseCase { get; } = useCase;
    public PackingNote Note { get; } = note;
    public ILabelReader Reader { get; } = reader;
}
"@
Set-Content -LiteralPath (Join-Path $backend 'GeneratedItemReferences.cs') -Value $integration
Invoke-Dotnet build $project

$custom = Join-Path $ScratchRoot custom-class
Copy-Item -LiteralPath (Join-Path $delivered class) -Destination $custom -Recurse
$customConfig = Join-Path $custom '.template.config/template.json'
$metadata = Get-Content -Raw -LiteralPath $customConfig | ConvertFrom-Json
$metadata.identity = 'Example.Warehouse.CustomClass.1'
$metadata.name = 'Warehouse custom class'
$metadata.shortName = 'warehouse-class'
$metadata | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $customConfig
Add-Content -LiteralPath (Join-Path $custom 'AicfClass.cs') -Value '// Warehouse custom marker'
Invoke-Template install $custom
Invoke-Template warehouse-class --name DeliveryNote --namespace Sample.Warehouse.Labels --output $domain
$generated = Join-Path $domain 'DeliveryNote.cs'
if (!(Select-String -LiteralPath $generated -Pattern 'Warehouse custom marker' -SimpleMatch)) {
    throw 'The generated file did not come from the selected custom template.'
}

$original = Join-Path $domain 'PackingNote.cs'
Add-Content -LiteralPath $original -Value '// Target-owned edit'
$before = (Get-FileHash -LiteralPath $original).Hash
& dotnet new aicf-class --name PackingNote --namespace Sample.Warehouse.Labels --output $domain --debug:custom-hive $hive
if ($LASTEXITCODE -eq 0 -or (Get-FileHash -LiteralPath $original).Hash -ne $before) {
    throw 'Collision did not refuse the overwrite and preserve the target bytes.'
}

Invoke-Template uninstall @roots $custom
Write-Output 'Native template acceptance passed.'
