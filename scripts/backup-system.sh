#!/bin/bash
# Sistema de Backup Automático - Vertrag MGS
# Automatisches Backup-System - Vertrag MGS
#
# DE: Erstellt vollständiges Backup von Datenbank, Uploads und Konfigurationen
# PT: Cria backup completo de banco de dados, uploads e configurações

set -e

# Cores / Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurações / Konfigurationen
PROJECT_DIR="/home/sschulze/projects/vertrag-mgs"
BACKUP_DIR="/var/backups/vertrag-mgs"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="backup_${DATE}"
RETENTION_DAYS=30  # Manter backups por 30 dias / Backups für 30 Tage aufbewahren

# Log / Protokoll
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCESSO/ERFOLG]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[AVISO/WARNUNG]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERRO/FEHLER]${NC} $1"
    exit 1
}

# Banner
echo "=================================================================="
echo "  🔄 BACKUP AUTOMÁTICO / AUTOMATISCHES BACKUP"
echo "=================================================================="
echo "  Data/Datum: $(date '+%d/%m/%Y %H:%M:%S')"
echo "=================================================================="
echo

# Verificar se está no diretório correto
if [ ! -f "$PROJECT_DIR/backend/main.py" ]; then
    log_error "Diretório do projeto não encontrado / Projektverzeichnis nicht gefunden: $PROJECT_DIR"
fi

# Criar diretório de backup se não existir
log_info "Criando diretório de backup / Erstelle Backup-Verzeichnis..."
sudo mkdir -p "$BACKUP_DIR"
sudo chown $USER:$USER "$BACKUP_DIR"

# Criar diretório temporário para este backup
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
mkdir -p "$BACKUP_PATH"

log_info "Backup será salvo em / Backup wird gespeichert in: $BACKUP_PATH"
echo

# ============================================================================
# 1. BACKUP DO BANCO DE DADOS / DATENBANK-BACKUP
# ============================================================================
log_info "📦 [1/5] Fazendo backup do banco de dados / Sichere Datenbank..."

if [ -f "$PROJECT_DIR/contracts.db" ]; then
    cp "$PROJECT_DIR/contracts.db" "$BACKUP_PATH/contracts.db"
    log_success "Banco de dados copiado / Datenbank kopiert: $(du -h "$BACKUP_PATH/contracts.db" | cut -f1)"
else
    log_warning "Banco de dados não encontrado / Datenbank nicht gefunden"
fi

# ============================================================================
# 2. BACKUP DOS UPLOADS / UPLOAD-BACKUP
# ============================================================================
log_info "📁 [2/5] Fazendo backup dos arquivos enviados / Sichere hochgeladene Dateien..."

if [ -d "$PROJECT_DIR/uploads" ]; then
    cp -r "$PROJECT_DIR/uploads" "$BACKUP_PATH/"
    UPLOAD_SIZE=$(du -sh "$BACKUP_PATH/uploads" 2>/dev/null | cut -f1 || echo "0B")
    log_success "Uploads copiados / Uploads kopiert: $UPLOAD_SIZE"
else
    log_warning "Diretório uploads não encontrado / Upload-Verzeichnis nicht gefunden"
    mkdir -p "$BACKUP_PATH/uploads"
fi

# ============================================================================
# 3. BACKUP DAS CONFIGURAÇÕES / KONFIGURATIONS-BACKUP
# ============================================================================
log_info "⚙️  [3/5] Fazendo backup das configurações / Sichere Konfigurationen..."

# Criar diretório de configs
mkdir -p "$BACKUP_PATH/config"

# Copiar arquivos de configuração importantes
CONFIG_FILES=(
    "alembic.ini"
    "backend/app/core/config.py"
    ".env"
    "deploy/apache-internal.conf"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$PROJECT_DIR/$file" ]; then
        # Preservar estrutura de diretórios
        FILE_DIR=$(dirname "$file")
        mkdir -p "$BACKUP_PATH/config/$FILE_DIR"
        cp "$PROJECT_DIR/$file" "$BACKUP_PATH/config/$file"
        log_success "✓ $file"
    fi
done

# ============================================================================
# 4. BACKUP DOS LOGS / LOG-BACKUP
# ============================================================================
log_info "📋 [4/5] Fazendo backup dos logs / Sichere Protokolle..."

mkdir -p "$BACKUP_PATH/logs"

# Logs do sistema
if [ -d "/var/log/apache2" ]; then
    find /var/log/apache2 -name "vertrag-mgs-*.log" -exec cp {} "$BACKUP_PATH/logs/" \; 2>/dev/null || true
fi

# Logs do backend
if [ -f "$PROJECT_DIR/backend/server.log" ]; then
    cp "$PROJECT_DIR/backend/server.log" "$BACKUP_PATH/logs/" 2>/dev/null || true
fi

log_success "Logs salvos / Protokolle gesichert"

# ============================================================================
# 5. COMPRIMIR BACKUP / BACKUP KOMPRIMIEREN
# ============================================================================
log_info "🗜️  [5/5] Comprimindo backup / Komprimiere Backup..."

cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME/"

COMPRESSED_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
log_success "Backup comprimido / Backup komprimiert: ${BACKUP_NAME}.tar.gz ($COMPRESSED_SIZE)"

# Remover diretório temporário
rm -rf "$BACKUP_PATH"

# ============================================================================
# 6. LIMPEZA DE BACKUPS ANTIGOS / ALTE BACKUPS LÖSCHEN
# ============================================================================
log_info "🧹 Limpando backups antigos (>${RETENTION_DAYS} dias) / Lösche alte Backups (>${RETENTION_DAYS} Tage)..."

find "$BACKUP_DIR" -name "backup_*.tar.gz" -type f -mtime +${RETENTION_DAYS} -delete 2>/dev/null || true

TOTAL_BACKUPS=$(find "$BACKUP_DIR" -name "backup_*.tar.gz" -type f | wc -l)
log_success "Backups mantidos / Behaltene Backups: $TOTAL_BACKUPS"

# ============================================================================
# 7. VERIFICAR INTEGRIDADE / INTEGRITÄT PRÜFEN
# ============================================================================
log_info "🔍 Verificando integridade do backup / Überprüfe Backup-Integrität..."

if tar -tzf "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" >/dev/null 2>&1; then
    log_success "✅ Backup íntegro e válido / Backup integer und gültig"
else
    log_error "❌ Backup corrompido / Backup beschädigt!"
fi

# ============================================================================
# RESUMO / ZUSAMMENFASSUNG
# ============================================================================
echo
echo "=================================================================="
echo "  ✅ BACKUP CONCLUÍDO COM SUCESSO / BACKUP ERFOLGREICH ABGESCHLOSSEN"
echo "=================================================================="
echo "  📦 Arquivo / Datei: ${BACKUP_NAME}.tar.gz"
echo "  📏 Tamanho / Größe: $COMPRESSED_SIZE"
echo "  📍 Local / Ort: $BACKUP_DIR"
echo "  📅 Data / Datum: $(date '+%d/%m/%Y %H:%M:%S')"
echo "=================================================================="
echo
echo "  Para restaurar / Zum Wiederherstellen:"
echo "  ./scripts/restore-system.sh ${BACKUP_NAME}.tar.gz"
echo "=================================================================="
