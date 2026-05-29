param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]] $ArgsFromUser
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$BundledPython = "C:\Users\hyperchain\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if (-not (Test-Path -LiteralPath $BundledPython)) {
  Write-Error "找不到 Codex 内置 Python: $BundledPython"
  exit 1
}

Push-Location $RepoRoot
try {
  & $BundledPython -m codex_check.sync_tool @ArgsFromUser
  exit $LASTEXITCODE
}
finally {
  Pop-Location
}
