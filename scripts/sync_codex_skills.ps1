param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$CodexHome = "$env:USERPROFILE\.codex"
)

$source = Join-Path $RepoRoot "codex_skills"
$target = Join-Path $CodexHome "skills"

if (-not (Test-Path $source)) {
    throw "Source path not found: $source"
}

New-Item -ItemType Directory -Path $target -Force | Out-Null

$skillFiles = Get-ChildItem -Path $source -Recurse -File -Filter "SKILL.md"

foreach ($file in $skillFiles) {
    $relativeDir = $file.DirectoryName.Substring($source.Length).TrimStart('\')
    $dstPath = Join-Path $target $relativeDir
    try {
        New-Item -ItemType Directory -Path $dstPath -Force | Out-Null
        Copy-Item -Path (Join-Path $file.DirectoryName '*') -Destination $dstPath -Recurse -Force -ErrorAction Stop
        Write-Host "Synced: $relativeDir"
    }
    catch {
        Write-Warning "Failed to sync $relativeDir : $($_.Exception.Message)"
    }
}

Write-Host "Done. Skills synced from repo to $target"
