# ============================================================================
# RESTORE SYSTEM - VERTRAG MGS (Windows PowerShell)
# Script de Restauração de Backup
# Backup-Wiederherstellungsskript
# ============================================================================
#
# DE: Stellt Vertrag-MGS System aus einem Backup wieder her
# PT: Restaura sistema Vertrag-MGS a partir de um backup
#
# Uso / Verwendung:
#   .\restore-windows.ps1 -BackupFile "backup_20251227_143726.zip"
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$BackupFile,
    [string]$BackupDir = "C:\VertragMGS\backups"
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

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "[AVISO/WARNUNG] $Message" -ForegroundColor $WarningColor
}

# Banner
Write-Host "============================================================================" -ForegroundColor $WarningColor
Write-Host "  ⚠️  RESTAURAÇÃO DE BACKUP - VERTRAG MGS (Windows)" -ForegroundColor $WarningColor
Write-Host "============================================================================" -ForegroundColor $WarningColor
Write-Host ""

# ============================================================================
# SELECIONAR BACKUP / BACKUP AUSWÄHLEN
# ============================================================================
if (-not $BackupFile) {
    Write-Info "Backups disponíveis / Verfügbare Backups:"
    Write-Host ""
    
    $backups = Get-ChildItem -Path $BackupDir -Filter "backup_*.zip" | Sort-Object LastWriteTime -Descending
    
    if ($backups.Count -eq 0) {
        Write-Error-Custom "Nenhum backup encontrado em / Keine Backups gefunden in: $BackupDir"
        exit 1
    }
    
    for ($i = 0; $i -lt $backups.Count; $i++) {
        $backup = $backups[$i]
        $sizeMB = [math]::Round($backup.Length / 1MB, 2)
        $date = $backup.LastWriteTime.ToString("dd/MM/yyyy HH:mm")
        Write-Host "  [$($i + 1)] $($backup.Name) - $sizeMB MB - $date"
    }
    
    Write-Host ""
    $selection = Read-Host "Selecione o número do backup / Wählen Sie die Backup-Nummer"
    
    try {
        $selectedIndex = [int]$selection - 1
        $BackupFile = $backups[$selectedIndex].Name
    } catch {
        Write-Error-Custom "Seleção inválida / Ungültige Auswahl"
        exit 1
    }
}

$backupPath = Join-Path $BackupDir $BackupFile

if (-not (Test-Path $backupPath)) {
    Write-Error-Custom "Backup não encontrado / Backup nicht gefunden: $backupPath"
    exit 1
}

Write-Info "Backup selecionado / Ausgewähltes Backup: $BackupFile"
Write-Host ""

# ============================================================================
# CONFIRMAÇÃO / BESTÄTIGUNG
# ============================================================================
Write-Warning-Custom "⚠️  ATENÇÃO / ACHTUNG:"
Write-Warning-Custom "Esta operação irá SOBRESCREVER os dados atuais!"
Write-Warning-Custom "Diese Operation wird die aktuellen Daten ÜBERSCHREIBEN!"
Write-Host ""

$confirmation = Read-Host "Deseja continuar? (S/N) / Möchten Sie fortfahren? (J/N)"

if ($confirmation -ne 'S' -and $confirmation -ne 's' -and $confirmation -ne 'J' -and $confirmation -ne 'j') {
    Write-Info "Restauração cancelada / Wiederherstellung abgebrochen"
    exit 0
}

# ============================================================================
# FASE 1: CRIAR SAFETY BACKUP / SICHERHEITS-BACKUP ERSTELLEN
# ============================================================================
Write-Info "💾 [1/5] Criando backup de segurança do estado atual / Erstelle Sicherheits-Backup des aktuellen Zustands..."

$safetyBackupDir = "C:\VertragMGS\backups\pre-restore"
$safetyBackupName = "safety_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
$safetyBackupPath = Join-Path $safetyBackupDir $safetyBackupName

New-Item -ItemType Directory -Force -Path $safetyBackupDir | Out-Null

try {
    # Backup rápido dos dados atuais
    $tempDir = Join-Path $env:TEMP "vertrag_safety_backup"
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
    
    if (Test-Path "C:\VertragMGS\data") {
        Copy-Item -Path "C:\VertragMGS\data" -Destination (Join-Path $tempDir "data") -Recurse -Force
    }
    
    if (Test-Path "C:\VertragMGS\uploads") {
        Copy-Item -Path "C:\VertragMGS\uploads" -Destination (Join-Path $tempDir "uploads") -Recurse -Force
    }
    
    Compress-Archive -Path $tempDir -DestinationPath $safetyBackupPath -CompressionLevel Fastest -Force
    Remove-Item -Path $tempDir -Recurse -Force
    
    Write-Success "Safety backup criado / Sicherheits-Backup erstellt: $safetyBackupName"
} catch {
    Write-Warning-Custom "Não foi possível criar safety backup / Sicherheits-Backup konnte nicht erstellt werden: $_"
}

# ============================================================================
# FASE 2: PARAR CONTAINERS / CONTAINER STOPPEN
# ============================================================================
Write-Info "🛑 [2/5] Parando containers Docker / Stoppe Docker-Container..."

Set-Location "C:\VertragMGS"

try {
    docker-compose down
    Write-Success "Containers parados / Container gestoppt"
} catch {
    Write-Warning-Custom "Erro ao parar containers / Fehler beim Stoppen der Container: $_"
}

Start-Sleep -Seconds 2

# ============================================================================
# FASE 3: EXTRAIR BACKUP / BACKUP EXTRAHIEREN
# ============================================================================
Write-Info "📦 [3/5] Extraindo backup / Extrahiere Backup..."

$extractPath = Join-Path $env:TEMP "vertrag_restore"

if (Test-Path $extractPath) {
    Remove-Item -Path $extractPath -Recurse -Force
}

try {
    Expand-Archive -Path $backupPath -DestinationPath $extractPath -Force
    Write-Success "Backup extraído / Backup extrahiert"
} catch {
    Write-Error-Custom "Erro ao extrair backup / Fehler beim Extrahieren: $_"
    exit 1
}

# ============================================================================
# FASE 4: RESTAURAR ARQUIVOS / DATEIEN WIEDERHERSTELLEN
# ============================================================================
Write-Info "♻️  [4/5] Restaurando arquivos / Stelle Dateien wieder her..."

# Banco de dados / Datenbank
if (Test-Path (Join-Path $extractPath "database\contracts.db")) {
    New-Item -ItemType Directory -Force -Path "C:\VertragMGS\data" | Out-Null
    Copy-Item -Path (Join-Path $extractPath "database\contracts.db") -Destination "C:\VertragMGS\data\contracts.db" -Force
    Write-Success "✓ Banco de dados restaurado / Datenbank wiederhergestellt"
}

# Uploads
if (Test-Path (Join-Path $extractPath "uploads")) {
    if (Test-Path "C:\VertragMGS\uploads") {
        Remove-Item -Path "C:\VertragMGS\uploads" -Recurse -Force
    }
    Copy-Item -Path (Join-Path $extractPath "uploads") -Destination "C:\VertragMGS\uploads" -Recurse -Force
    Write-Success "✓ Uploads restaurados / Uploads wiederhergestellt"
}

# Configurações (opcional - perguntar)
if (Test-Path (Join-Path $extractPath "config")) {
    Write-Host ""
    $restoreConfig = Read-Host "Restaurar configurações (.env, etc)? (S/N) / Konfigurationen wiederherstellen? (J/N)"
    
    if ($restoreConfig -eq 'S' -or $restoreConfig -eq 's' -or $restoreConfig -eq 'J' -or $restoreConfig -eq 'j') {
        if (Test-Path (Join-Path $extractPath "config\.env")) {
            Copy-Item -Path (Join-Path $extractPath "config\.env") -Destination "C:\VertragMGS\.env" -Force
            Write-Success "✓ .env restaurado / .env wiederhergestellt"
        }
        
        if (Test-Path (Join-Path $extractPath "config\docker-compose.yml")) {
            Copy-Item -Path (Join-Path $extractPath "config\docker-compose.yml") -Destination "C:\VertragMGS\docker-compose.yml" -Force
            Write-Success "✓ docker-compose.yml restaurado / docker-compose.yml wiederhergestellt"
        }
    }
}

# Limpar extração / Extraktion bereinigen
Remove-Item -Path $extractPath -Recurse -Force

# ============================================================================
# FASE 5: REINICIAR CONTAINERS / CONTAINER NEU STARTEN
# ============================================================================
Write-Info "🚀 [5/5] Reiniciando containers / Starte Container neu..."

try {
    docker-compose up -d
    Write-Success "Containers iniciados / Container gestartet"
} catch {
    Write-Error-Custom "Erro ao iniciar containers / Fehler beim Starten der Container: $_"
    Write-Info "Tente executar manualmente / Versuchen Sie manuell auszuführen: docker-compose up -d"
}

Start-Sleep -Seconds 5

# ============================================================================
# VERIFICAÇÃO / ÜBERPRÜFUNG
# ============================================================================
Write-Info "🔍 Verificando sistema / Überprüfe System..."

try {
    $healthCheck = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
    if ($healthCheck.StatusCode -eq 200) {
        Write-Success "✅ Sistema online e funcionando / System online und funktionsfähig"
    }
} catch {
    Write-Warning-Custom "Sistema ainda não respondeu ao health check / System hat noch nicht auf Health Check geantwortet"
    Write-Info "Aguarde alguns segundos e verifique / Warten Sie einige Sekunden und überprüfen Sie: http://localhost:8000/health"
}

# ============================================================================
# RESUMO / ZUSAMMENFASSUNG
# ============================================================================
Write-Host ""
Write-Host "============================================================================" -ForegroundColor $SuccessColor
Write-Host "  ✅ RESTAURAÇÃO CONCLUÍDA / WIEDERHERSTELLUNG ABGESCHLOSSEN" -ForegroundColor $SuccessColor
Write-Host "============================================================================" -ForegroundColor $SuccessColor
Write-Host "  📦 Backup usado / Verwendetes Backup: $BackupFile" -ForegroundColor White
Write-Host "  💾 Safety backup: $safetyBackupName" -ForegroundColor White
Write-Host "  📅 Data / Datum: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')" -ForegroundColor White
Write-Host "============================================================================" -ForegroundColor $SuccessColor
Write-Host ""
Write-Host "  Próximos passos / Nächste Schritte:" -ForegroundColor $InfoColor
Write-Host "  1. Verificar logs / Protokolle überprüfen: docker-compose logs" -ForegroundColor White
Write-Host "  2. Testar sistema / System testen: http://localhost:8000/health" -ForegroundColor White
Write-Host "  3. Se algo deu errado / Falls etwas schief ging:" -ForegroundColor White
Write-Host "     .\restore-windows.ps1 -BackupFile '$safetyBackupName'" -ForegroundColor White
Write-Host "============================================================================" -ForegroundColor $SuccessColor
