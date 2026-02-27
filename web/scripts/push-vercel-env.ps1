param(
  [string]$EnvFile = "..\\.env"
)

$ErrorActionPreference = "Stop"

function Parse-EnvFile {
  param([string]$Path)
  $map = @{}
  if (-not (Test-Path $Path)) {
    throw "Env file not found: $Path"
  }
  foreach ($line in Get-Content $Path) {
    $trim = $line.Trim()
    if ($trim -eq "" -or $trim.StartsWith("#")) { continue }
    $idx = $trim.IndexOf("=")
    if ($idx -lt 1) { continue }
    $k = $trim.Substring(0, $idx).Trim()
    $v = $trim.Substring($idx + 1)
    $map[$k] = $v
  }
  return $map
}

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$parsed = Parse-EnvFile -Path (Resolve-Path $EnvFile)

# Web runtime allowlist
$keys = @(
  "MONGODB_URI",
  "MONGODB_DB",
  "LAW_API_OC",
  "OPENAI_API_KEY",
  "INGEST_SECRET"
)

$targets = @("development", "preview", "production")

Write-Host "[1/3] Verifying vercel CLI..."
npm exec vercel -- --version | Out-Null

Write-Host "[2/3] Ensuring project is linked..."
npm exec vercel -- link --yes | Out-Null

Write-Host "[3/3] Uploading environment variables..."
foreach ($key in $keys) {
  if (-not $parsed.ContainsKey($key)) {
    Write-Host "skip: $key (not found)"
    continue
  }
  $value = $parsed[$key]
  if ([string]::IsNullOrWhiteSpace($value)) {
    Write-Host "skip: $key (empty)"
    continue
  }

  foreach ($target in $targets) {
    npm exec vercel -- env rm $key $target --yes | Out-Null
    $value | npm exec vercel -- env add $key $target | Out-Null
    Write-Host "set: $key ($target)"
  }
}

Write-Host "done"
