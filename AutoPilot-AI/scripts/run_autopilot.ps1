# AutoPilot AI PowerShell Launcher
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path "$ScriptDir\.."
Set-Location $ProjectRoot

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  AutoPilot AI - Universal Coding Agent Automation" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan

try {
    $pythonVersion = & python --version 2>&1
    Write-Host "Using: $pythonVersion" -ForegroundColor Gray
} catch {
    Write-Error "Python was not found in PATH. Please install Python 3.10+."
    exit 1
}

$env:PYTHONPATH = $ProjectRoot
& python -m autopilot.main $args
