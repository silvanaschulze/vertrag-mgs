# ============================================================================
# BACKUP SYSTEM - VERTRAG MGS (Windows PowerShell)
# Script de Backup Automatizado
# Automatisiertes Backup-Skript
# ============================================================================
#
# DE: Führt vollständige Sicherung des Vertrag-MGS Systems durch
# PT: Executa backup completo do sistema Vertrag-MGS
#
# Uso / Verwendung:
#   .\backup-windows.ps1
#
# Agendamento / Zeitplanung:
#   Task Scheduler - Diariamente às 2:00 AM / Täglich um 2:00 Uhr
# ============================================================================

param(
    [string]$BackupDir = "C:\VertragMGS\backups",
    [int]$RetentionDays = 30
)

# Cores / Farben
$ErrorColor = "Red"
$SuccessColor = "Green"
$InfoColor = "Cyan"
$WarningColor = "Yellow"

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $InfoColor
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCESSO/ERFOLG] $Message" -ForegroundColor $SuccessColor
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERRO/FEHLER] $Message" -ForegroundColor $ErrorColor
}

# Banner
Write-Host "============================================================================" -ForegroundColor $InfoColor
Write-Host "  🔄 BACKUP AUTOMÁTICO - VERTRAG MGS (Windows)" -ForegroundColor $InfoColor
Write-Host "============================================================================" -ForegroundColor $InfoColor
Write-Host ""

# Timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupName = "backup_$timestamp"
$backupPath = Join-Path $BackupDir $backupName
$backupZip = "$backupPath.zip"

# Criar diretório de backup / Backup-Verzeichnis erstellen
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
New-Item -ItemType Directory -Force -Path $backupPath | Out-Null

Write-Info "Backup será salvo em / Backup wird gespeichert in: $backupPath"
Write-Host ""

# ============================================================================
# FASE 1: BACKUP DO BANCO DE DADOS / DATENBANK SICHERN
# ============================================================================
Write-Info "📦 [1/5] Fazendo backup do banco de dados / Sichere Datenbank..."

$dbSource = "C:\VertragMGS\data\contracts.db"
$dbDest = Join-Path $backupPath "database"

if (Test-Path $dbSource) {
    New-Item -ItemType Directory -Force -Path $dbDest | Out-Null
    Copy-Item -Path $dbSource -Destination $dbDest -Force
    
    $dbSize = (Get-Item (Join-Path $dbDest "contracts.db")).Length
    $dbSizeKB = [math]::Round($dbSize / 1KB, 2)
    Write-Success "Banco de dados copiado / Datenbank kopiert: $dbSizeKB KB"
} else {
    Write-Error-Custom "Banco de dados não encontrado / Datenbank nicht gefunden: $dbSource"
}

# ============================================================================
# FASE 2: BACKUP DOS UPLOADS / UPLOADS SICHERN
# ============================================================================
Write-Info "📁 [2/5] Fazendo backup dos arquivos enviados / Sichere hochgeladene Dateien..."

$uploadsSource = "C:\VertragMGS\uploads"
$uploadsDest = Join-Path $backupPath "uploads"

if (Test-Path $uploadsSource) {
    Copy-Item -Path $uploadsSource -Destination $uploadsDest -Recurse -Force
    
    $uploadFiles = (Get-ChildItem -Path $uploadsDest -Recurse -File).Count
    $uploadSize = (Get-ChildItem -Path $uploadsDest -Recurse | Measure-Object -Property Length -Sum).Sum
    $uploadSizeMB = [math]::Round($uploadSize / 1MB, 2)
    
    Write-Success "Uploads copiados / Uploads kopiert: $uploadFiles arquivos / Dateien ($uploadSizeMB MB)"
} else {
    Write-Error-Custom "Diretório de uploads não encontrado / Upload-Verzeichnis nicht gefunden: $uploadsSource"
}

# ============================================================================
# FASE 3: BACKUP DAS CONFIGURAÇÕES / KONFIGURATIONEN SICHERN
# ============================================================================
Write-Info "⚙️  [3/5] Fazendo backup das configurações / Sichere Konfigurationen..."

$configDest = Join-Path $backupPath "config"
New-Item -ItemType Directory -Force -Path $configDest | Out-Null

# .env
if (Test-Path "C:\VertragMGS\.env") {
    Copy-Item -Path "C:\VertragMGS\.env" -Destination $configDest -Force
    Write-Success "✓ .env"
}

# docker-compose.yml
if (Test-Path "C:\VertragMGS\docker-compose.yml") {
    Copy-Item -Path "C:\VertragMGS\docker-compose.yml" -Destination $configDest -Force
    Write-Success "✓ docker-compose.yml"
}

# alembic.ini
if (Test-Path "C:\VertragMGS\alembic.ini") {
    Copy-Item -Path "C:\VertragMGS\alembic.ini" -Destination $configDest -Force
    Write-Success "✓ alembic.ini"
}

# config.py
if (Test-Path "C:\VertragMGS\backend\app\core\config.py") {
    Copy-Item -Path "C:\VertragMGS\backend\app\core\config.py" -Destination $configDest -Force
    Write-Success "✓ config.py"
}

# ============================================================================
# FASE 4: BACKUP DOS LOGS / PROTOKOLLE SICHERN
# ============================================================================
Write-Info "📋 [4/5] Fazendo backup dos logs / Sichere Protokolle..."

$logsSource = "C:\VertragMGS\logs"
$logsDest = Join-Path $backupPath "logs"

if (Test-Path $logsSource) {
    Copy-Item -Path $logsSource -Destination $logsDest -Recurse -Force
    Write-Success "Logs salvos / Protokolle gesichert"
} else {
    Write-Host "[AVISO/WARNUNG] Logs não encontrados / Protokolle nicht gefunden" -ForegroundColor $WarningColor
}

# ============================================================================
# FASE 5: COMPACTAR BACKUP / BACKUP KOMPRIMIEREN
# ============================================================================
Write-Info "🗜️  [5/5] Comprimindo backup / Komprimiere Backup..."

try {
    Compress-Archive -Path $backupPath -DestinationPath $backupZip -CompressionLevel Optimal -Force
    
    # Remover pasta temporária / Temporären Ordner entfernen
    Remove-Item -Path $backupPath -Recurse -Force
    
    $zipSize = (Get-Item $backupZip).Length
    $zipSizeKB = [math]::Round($zipSize / 1KB, 2)
    $zipSizeMB = [math]::Round($zipSize / 1MB, 2)
    
    if ($zipSizeMB -gt 1) {
        Write-Success "Backup comprimido / Backup komprimiert: $backupName.zip ($zipSizeMB MB)"
    } else {
        Write-Success "Backup comprimido / Backup komprimiert: $backupName.zip ($zipSizeKB KB)"
    }
} catch {
    Write-Error-Custom "Erro ao compactar backup / Fehler beim Komprimieren: $_"
    exit 1
}

# ============================================================================
# LIMPEZA: REMOVER BACKUPS ANTIGOS / ALTE BACKUPS LÖSCHEN
# ============================================================================
Write-Info "🧹 Limpando backups antigos (>$RetentionDays dias) / Lösche alte Backups (>$RetentionDays Tage)..."

$cutoffDate = (Get-Date).AddDays(-$RetentionDays)
$oldBackups = Get-ChildItem -Path $BackupDir -Filter "backup_*.zip" | Where-Object { $_.LastWriteTime -lt $cutoffDate }

foreach ($oldBackup in $oldBackups) {
    Remove-Item -Path $oldBackup.FullName -Force
    Write-Host "  Removido / Gelöscht: $($oldBackup.Name)" -ForegroundColor $WarningColor
}

$remainingBackups = (Get-ChildItem -Path $BackupDir -Filter "backup_*.zip").Count
Write-Success "Backups mantidos / Behaltene Backups: $remainingBackups"

# ============================================================================
# VERIFICAR INTEGRIDADE / INTEGRITÄT ÜBERPRÜFEN
# ============================================================================
Write-Info "🔍 Verificando integridade do backup / Überprüfe Backup-Integrität..."

try {
    $testZip = [System.IO.Compression.ZipFile]::OpenRead($backupZip)
    $testZip.Dispose()
    Write-Success "✅ Backup íntegro e válido / Backup integer und gültig"
} catch {
    Write-Error-Custom "❌ Backup corrompido / Backup beschädigt: $_"
    exit 1
}

# ============================================================================
# RESUMO / ZUSAMMENFASSUNG
# ============================================================================
Write-Host ""
Write-Host "============================================================================" -ForegroundColor $SuccessColor
Write-Host "  ✅ BACKUP CONCLUÍDO COM SUCESSO / BACKUP ERFOLGREICH ABGESCHLOSSEN" -ForegroundColor $SuccessColor
Write-Host "============================================================================" -ForegroundColor $SuccessColor
Write-Host "  📦 Arquivo / Datei: $backupName.zip" -ForegroundColor White
Write-Host "  📏 Tamanho / Größe: $zipSizeMB MB" -ForegroundColor White
Write-Host "  📍 Local / Ort: $BackupDir" -ForegroundColor White
Write-Host "  📅 Data / Datum: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')" -ForegroundColor White
Write-Host "============================================================================" -ForegroundColor $SuccessColor
Write-Host ""
Write-Host "  Para restaurar / Zum Wiederherstellen:" -ForegroundColor $InfoColor
Write-Host "  .\restore-windows.ps1 -BackupFile '$backupName.zip'" -ForegroundColor White
Write-Host "============================================================================" -ForegroundColor $SuccessColor
