<#
.SYNOPSIS
  Restaura um backup gerado por backup-postgres.ps1 no stack on-premise.

.DESCRIPTION
  Descompacta o .zip informado e recarrega o dump dentro do container "db"
  do docker-compose.prod.yml. ISSO SUBSTITUI OS DADOS ATUAIS DO BANCO.
  Pede confirmacao explicita antes de continuar.

.PARAMETER ZipFile
  Caminho do .zip de backup a restaurar (gerado por backup-postgres.ps1).

.EXAMPLE
  .\restore-postgres.ps1 -ZipFile "..\..\area-verde-backups\area-verde_2026-08-23_09-00.sql.zip"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$ZipFile
)

$ErrorActionPreference = "Stop"
$repoRoot = Join-Path $PSScriptRoot ".."
Set-Location $repoRoot

# Mesma leitura de .env usada em backup-postgres.ps1: "docker compose" le o
# .env sozinho, mas nao expoe as variaveis para este script.
function Get-EnvValue([string]$Name, [string]$Default) {
    $envFile = Join-Path $repoRoot ".env"
    if (Test-Path $envFile) {
        $line = Select-String -Path $envFile -Pattern "^$Name=(.*)$" | Select-Object -First 1
        if ($line) {
            return $line.Matches[0].Groups[1].Value.Trim()
        }
    }
    return $Default
}

$pgUser = Get-EnvValue "POSTGRES_USER" "area_verde"
$pgDb = Get-EnvValue "POSTGRES_DB" "area_verde"

if (-not (Test-Path $ZipFile)) {
    Write-Error "Arquivo nao encontrado: $ZipFile"
    exit 1
}

Write-Warning "Isso vai APAGAR os dados atuais do banco 'area-verde' e substituir pelo conteudo de $ZipFile."
$confirm = Read-Host "Digite RESTAURAR para confirmar"
if ($confirm -ne "RESTAURAR") {
    Write-Host "Cancelado."
    exit 0
}

$tempDir = Join-Path $env:TEMP "area-verde-restore-$(Get-Date -Format 'yyyyMMddHHmmss')"
New-Item -ItemType Directory -Path $tempDir | Out-Null
Expand-Archive -Path $ZipFile -DestinationPath $tempDir -Force
$sqlFile = Get-ChildItem $tempDir -Filter "*.sql" | Select-Object -First 1

if (-not $sqlFile) {
    Write-Error "Nenhum .sql encontrado dentro de $ZipFile"
    exit 1
}

Write-Host "Recriando o banco '$pgDb' antes de restaurar..."
docker compose -f docker-compose.prod.yml exec -T db `
    dropdb -U $pgUser --if-exists $pgDb
docker compose -f docker-compose.prod.yml exec -T db `
    createdb -U $pgUser $pgDb

Write-Host "Restaurando $($sqlFile.FullName) ..."
Get-Content $sqlFile.FullName -Raw | docker compose -f docker-compose.prod.yml exec -T db `
    psql -U $pgUser -d $pgDb

Remove-Item $tempDir -Recurse -Force
Write-Host "Restauracao concluida. Reinicie a API se ela ja estava rodando:"
Write-Host "  docker compose -f docker-compose.prod.yml restart api"
