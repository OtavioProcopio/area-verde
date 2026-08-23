<#
.SYNOPSIS
  Faz backup do Postgres do stack on-premise (docker-compose.prod.yml) e
  aplica retencao local. Opcionalmente envia o dump para uma VPS via scp.

.DESCRIPTION
  Roda "docker compose exec db pg_dump", compacta o resultado em .zip e
  guarda em -BackupDir (por padrao, uma pasta FORA do repositorio git).
  Pensado para ser chamado pelo Agendador de Tarefas do Windows uma vez
  por dia. Ver docs/workflows/deploy-onpremise-windows.md.

.PARAMETER BackupDir
  Pasta onde os .zip de backup ficam salvos.

.PARAMETER RetentionDays
  Backups locais mais antigos que isso sao apagados apos um backup com sucesso.

.PARAMETER VpsHost
  Opcional. Ex: "usuario@meu-servidor.com". Se informado, copia o .zip do
  dia para essa maquina via scp (chave SSH ja configurada) como copia
  externa, sem expor o notebook nem rodar nada do sistema na VPS.

.PARAMETER VpsPath
  Caminho remoto de destino quando -VpsHost e usado. Padrao: "~/area-verde-backups/".

.EXAMPLE
  .\backup-postgres.ps1
  .\backup-postgres.ps1 -VpsHost "opr@minha-vps.com"
#>

param(
    [string]$BackupDir = (Join-Path $PSScriptRoot "..\..\area-verde-backups"),
    [int]$RetentionDays = 14,
    [string]$VpsHost = "",
    [string]$VpsPath = "~/area-verde-backups/"
)

$ErrorActionPreference = "Stop"
$repoRoot = Join-Path $PSScriptRoot ".."
Set-Location $repoRoot

# O "docker compose" le o .env sozinho para interpolar o compose file, mas
# isso nao expoe as variaveis para este script — entao lemos o .env aqui
# tambem, pelos mesmos nomes usados no docker-compose.prod.yml.
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

if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
$sqlFile = Join-Path $BackupDir "area-verde_$timestamp.sql"
$zipFile = "$sqlFile.zip"

Write-Host "Gerando dump em $sqlFile ..."
docker compose -f docker-compose.prod.yml exec -T db `
    pg_dump -U $pgUser -d $pgDb `
    | Out-File -Encoding utf8 $sqlFile

if ($LASTEXITCODE -ne 0 -or -not (Test-Path $sqlFile) -or (Get-Item $sqlFile).Length -eq 0) {
    Write-Error "pg_dump falhou ou gerou arquivo vazio. Backup abortado."
    exit 1
}

Compress-Archive -Path $sqlFile -DestinationPath $zipFile -Force
Remove-Item $sqlFile
Write-Host "Backup salvo em $zipFile"

if ($VpsHost) {
    Write-Host "Enviando copia para $VpsHost`:$VpsPath ..."
    scp $zipFile "${VpsHost}:${VpsPath}"
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Falha ao enviar backup para a VPS. O backup local em $zipFile continua valido."
    }
}

Write-Host "Aplicando retencao de $RetentionDays dias em $BackupDir ..."
Get-ChildItem $BackupDir -Filter "area-verde_*.zip" `
    | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$RetentionDays) } `
    | Remove-Item -Force

Write-Host "Backup concluido."
