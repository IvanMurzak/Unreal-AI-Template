#!/usr/bin/env pwsh
<#
.SYNOPSIS
    End-to-end tool-invocation harness for this extension (one-test-per-tool convention).

.DESCRIPTION
    For each check under Tests/e2e/tools/*.e2e.ps1, invokes the named MCP tool through the running
    project's local MCP server via `unreal-mcp-cli run-tool` (or `run-system-tool`) and asserts a
    well-formed success. This is the cross-dependency on the install/CLI layer described in the design
    note §7: CI boots a headless editor, installs THIS extension with `unreal-mcp-cli install-extension`,
    then runs this harness against the live server.

    Each check file returns a hashtable:
      @{ Tool = "hello-extension"; System = $false; Input = '{"name":"CI"}'; Assert = { param($Json) ... } }
    - Tool   : the tool id to invoke.
    - System : $true to use `run-system-tool` instead of `run-tool`.
    - Input  : optional JSON string passed as --input.
    - Assert : optional scriptblock receiving the parsed JSON result; throw to fail.

.PARAMETER ProjectDir
    The Unreal project directory whose local MCP server is running (resolves URL + token).

.PARAMETER Cli
    The unreal-mcp-cli invocation. Default: "unreal-mcp-cli". Use e.g. "npx unreal-mcp-cli" or an
    absolute path to a local build.

.EXAMPLE
    ./Tests/e2e/Run-ToolChecks.ps1 -ProjectDir "C:/path/to/UEProject"
#>
param(
    [Parameter(Mandatory = $true)][string]$ProjectDir,
    [string]$Cli = "unreal-mcp-cli"
)
$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$toolsDir = Join-Path $scriptDir 'tools'

$checks = Get-ChildItem -Path $toolsDir -Filter '*.e2e.ps1' -ErrorAction SilentlyContinue
if (-not $checks) { Write-Error "No tool checks found under $toolsDir"; exit 1 }

# Split the CLI invocation into exe + leading args (supports "npx unreal-mcp-cli").
$cliParts = $Cli -split '\s+'
$cliExe = $cliParts[0]
$cliLead = @($cliParts[1..($cliParts.Length - 1)])

$failures = 0
foreach ($checkFile in $checks) {
    $check = & $checkFile.FullName
    $tool = $check.Tool
    $verb = if ($check.System) { 'run-system-tool' } else { 'run-tool' }
    Write-Host "==> [$verb] $tool" -ForegroundColor Cyan

    $args = @($cliLead + @($verb, $tool, '--path', $ProjectDir))
    if ($check.Input) { $args += @('--input', $check.Input) }

    try {
        $out = & $cliExe @args 2>&1
        $exit = $LASTEXITCODE
        if ($exit -ne 0) { throw "CLI exited $exit. Output:`n$out" }

        $json = $null
        try { $json = ($out | Out-String).Trim() | ConvertFrom-Json } catch {
            throw "tool output is not valid JSON (a well-formed success is required). Output:`n$out"
        }

        if ($check.Assert) { & $check.Assert $json }
        Write-Host "    PASS" -ForegroundColor Green
    }
    catch {
        Write-Host "    FAIL: $($_.Exception.Message)" -ForegroundColor Red
        $failures++
    }
}

Write-Host ""
if ($failures -gt 0) { Write-Error "$failures tool check(s) failed."; exit 1 }
Write-Host "All tool checks passed." -ForegroundColor Green
