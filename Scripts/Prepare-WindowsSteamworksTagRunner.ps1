# CCTO for VPE — interactive Windows Steamworks tag runner preflight/launcher.
# No GitHub runner registration tokens, Steam passwords, or item mutations.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RimWorldRoot,
    [string]$AgentHome = (Join-Path $env:LOCALAPPDATA 'AMJ-SteamworksTagPublisher'),
    [string]$RunnerHome = '',
    [switch]$BuildPinnedAgent,
    [switch]$RunRegisteredRunner
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PinnedUpstream = 'c58f903d1e0220c395c8e305e1b9d3177db6df32'
$UpstreamUrl = 'https://github.com/pardeike/SteamWorkshopAgent.git'

function Require-Program([string]$Name) {
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) { throw "Missing prerequisite: $Name" }
    return $cmd
}

if (-not $IsWindows -and ($PSVersionTable.PSEdition -eq 'Core')) {
    throw 'This launcher only supports an interactive Windows Steam desktop session'
}
if ([Diagnostics.Process]::GetCurrentProcess().SessionId -eq 0) {
    throw 'Windows Session 0/service accounts cannot access the signed-in Steam desktop session'
}
$session = [Diagnostics.Process]::GetCurrentProcess().SessionId
$steam = @(Get-Process -Name steam -ErrorAction SilentlyContinue |
    Where-Object { $_.SessionId -eq $session })
if ($steam.Count -eq 0) {
    throw 'Desktop Steam is not running in the current interactive session'
}
if (-not (Test-Path -LiteralPath $RimWorldRoot -PathType Container)) {
    throw 'RimWorldRoot does not exist'
}
$nativeLibraries = @(Get-ChildItem -LiteralPath $RimWorldRoot -Recurse -File -Filter 'steam_api64.dll')
if ($nativeLibraries.Count -ne 1) {
    throw "Expected exactly one installed RimWorld steam_api64.dll, found $($nativeLibraries.Count). Supply the actual installed RimWorld root."
}
$native = $nativeLibraries[0].FullName

if (-not $env:LOCALAPPDATA -or -not (Test-Path -LiteralPath $env:LOCALAPPDATA)) {
    throw 'LOCALAPPDATA is required for the per-user private Steam tag receipt'
}
$AgentHome = [IO.Path]::GetFullPath($AgentHome)
$local = [IO.Path]::GetFullPath($env:LOCALAPPDATA)
if (-not $AgentHome.StartsWith($local + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'AgentHome must be beneath this Windows user LOCALAPPDATA directory'
}
$sourceRoot = Join-Path $AgentHome 'upstream-source'
$binaryRoot = Join-Path $AgentHome 'bin'
$agentExe = Join-Path $binaryRoot 'SteamWorkshopAgent.exe'
$receipt = Join-Path $AgentHome 'private\tags-receipt.json'

$null = Require-Program 'python'
& python --version
if ($LASTEXITCODE -ne 0) { throw 'Python is not executable' }

if ($BuildPinnedAgent) {
    $null = Require-Program 'git'
    $null = Require-Program 'dotnet'
    if (-not (Test-Path -LiteralPath $sourceRoot)) {
        New-Item -ItemType Directory -Force -Path $AgentHome | Out-Null
        & git clone -- $UpstreamUrl $sourceRoot
        if ($LASTEXITCODE -ne 0) { throw 'Git clone failed' }
    }
    if (-not (Test-Path -LiteralPath (Join-Path $sourceRoot '.git'))) {
        throw 'Existing upstream-source is not a Git checkout; refusing to overwrite'
    }
    & git -C $sourceRoot checkout --detach $PinnedUpstream
    if ($LASTEXITCODE -ne 0) { throw 'Pinned SteamWorkshopAgent revision not found' }
    $head = (& git -C $sourceRoot rev-parse HEAD).Trim()
    if ($head -cne $PinnedUpstream) { throw 'Upstream source commit differs from reviewed pin' }
    $project = Join-Path $sourceRoot 'srcSteamWorkshopAgentSteamWorkshopAgent.csproj'
    if (-not (Test-Path -LiteralPath $project)) { throw 'Reviewed SteamWorkshopAgent project missing' }
    New-Item -ItemType Directory -Force -Path $binaryRoot | Out-Null
    & dotnet publish $project -c Release -r win-x64 --self-contained false -p:BuildBridgeTools=false -o $binaryRoot
    if ($LASTEXITCODE -ne 0) { throw 'Pinned SteamWorkshopAgent build failed' }
    Copy-Item -LiteralPath (Join-Path $sourceRoot 'LICENSE') -Destination (Join-Path $binaryRoot 'LICENSE') -Force
}
if (-not (Test-Path -LiteralPath $agentExe -PathType Leaf)) {
    throw 'SteamWorkshopAgent.exe missing. Run with -BuildPinnedAgent after reviewing upstream source.'
}

# Environment is process-scoped and inherited by run.cmd; no Steam/GitHub tokens.
$env:STEAMWORKS_NATIVE_LIB = $native
$env:CCTO_STEAMWORKS_AGENT_BIN = $agentExe
$env:CCTO_STEAM_TAG_RECEIPT = $receipt

# Upstream probe does not StartItemUpdate/SetItemTags/SubmitItemUpdate.
$raw = (& $agentExe steam-session-probe | Out-String).Trim()
if ($LASTEXITCODE -ne 0) { throw 'SteamWorkshopAgent desktop session probe failed' }
try { $result = $raw | ConvertFrom-Json -ErrorAction Stop }
catch { throw 'SteamWorkshopAgent probe did not return valid JSON' }
if ($result.status -cne 'ok' -or $result.data.ready -ne $true -or
    $result.data.steamUserLoggedOn -ne $true -or
    [int]$result.data.steamAppId -ne 294100) {
    throw 'Steamworks not authenticated for RimWorld app 294100 in this Windows session'
}
Write-Output 'READY — Interactive Windows Steamworks authenticated; no Workshop item changed'
Write-Output ('Agent binary SHA256: ' + (Get-FileHash -LiteralPath $agentExe -Algorithm SHA256).Hash)
Write-Output ('RimWorld Steam API SHA256: ' + (Get-FileHash -LiteralPath $native -Algorithm SHA256).Hash)

if ($RunRegisteredRunner) {
    if (-not $RunnerHome) { throw 'RunnerHome is required when -RunRegisteredRunner is set' }
    $run = Join-Path ([IO.Path]::GetFullPath($RunnerHome)) 'run.cmd'
    $registered = Join-Path ([IO.Path]::GetFullPath($RunnerHome)) '.runner'
    if (-not (Test-Path -LiteralPath $run -PathType Leaf) -or
        -not (Test-Path -LiteralPath $registered -PathType Leaf)) {
        throw 'A separately registered GitHub Actions Windows runner is required'
    }
    Write-Output 'Launching registered runner interactively; it inherits host-only Steamworks settings'
    & $run
    if ($LASTEXITCODE -ne 0) { throw 'Windows GitHub Actions runner exited nonzero' }
}
