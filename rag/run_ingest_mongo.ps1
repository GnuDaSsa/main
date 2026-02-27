$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$env:LAW_RAG_STORE = 'mongo'

if (-not $env:MONGODB_URI) {
  Write-Host 'MONGODB_URI is not set in current shell. It can still be loaded from .env via mongo_env.py.'
}

if (-not $env:LAW_API_OC) {
  Write-Host 'LAW_API_OC is not set in current shell. It can still be loaded from .env via mongo_env.py.'
}

$queries = Get-Content "$PSScriptRoot\queries.txt" | Where-Object { $_.Trim() -ne '' }
python scripts/law_rag_ingest.py --queries $queries --max-pages 2 --page-size 100
