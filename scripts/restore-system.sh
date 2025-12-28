#!/bin/bash
# Sistema de Restauração de Backup - Vertrag MGS
# Backup-Wiederherstellungssystem - Vertrag MGS
#
# DE: Stellt System aus Backup wieder her
# PT: Restaura sistema a partir de backup
#
# Uso/Verwendung: ./restore-system.sh backup_20251227_100000.tar.gz

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
echo "  ♻️  RESTAURAÇÃO DE BACKUP / BACKUP-WIEDERHERSTELLUNG"
echo "=================================================================="
echo "  ⚠️  ATENÇÃO: Esta operação irá SOBRESCREVER dados atuais!"
echo "  ⚠️  WARNUNG: Dieser Vorgang überschreibt aktuelle Daten!"
echo "=================================================================="
echo

# Verificar argumento
if [ -z "$1" ]; then
    log_error "Uso / Verwendung: $0 <arquivo_backup.tar.gz>"
fi

BACKUP_FILE="$1"

# Se não for caminho absoluto, buscar no diretório de backups
if [[ ! "$BACKUP_FILE" = /* ]]; then
    BACKUP_FILE="$BACKUP_DIR/$BACKUP_FILE"
fi

# Verificar se arquivo existe
if [ ! -f "$BACKUP_FILE" ]; then
    log_error "Arquivo de backup não encontrado / Backup-Datei nicht gefunden: $BACKUP_FILE"
fi

log_info "Arquivo de backup / Backup-Datei: $BACKUP_FILE"
log_info "Tamanho / Größe: $(du -h "$BACKUP_FILE" | cut -f1)"
echo

# Confirmação / Bestätigung
read -p "Deseja continuar com a restauração? (s/N) / Möchten Sie mit der Wiederherstellung fortfahren? (j/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[SsJj]$ ]]; then
    log_warning "Restauração cancelada pelo usuário / Wiederherstellung vom Benutzer abgebrochen"
    exit 0
fi

# ============================================================================
# 1. CRIAR BACKUP DOS DADOS ATUAIS / BACKUP DER AKTUELLEN DATEN ERSTELLEN
# ============================================================================
log_info "📦 [1/5] Criando backup de segurança dos dados atuais / Erstelle Sicherung der aktuellen Daten..."

SAFETY_BACKUP="$BACKUP_DIR/pre_restore_$(date +%Y%m%d_%H%M%S).tar.gz"
cd "$PROJECT_DIR"
tar -czf "$SAFETY_BACKUP" contracts.db uploads/ 2>/dev/null || true

log_success "Backup de segurança criado / Sicherungsbackup erstellt: $SAFETY_BACKUP"

# ============================================================================
# 2. PARAR SERVIÇOS / DIENSTE STOPPEN
# ============================================================================
log_info "⏸️  [2/5] Parando serviços / Stoppe Dienste..."

# Parar FastAPI
sudo systemctl stop vertrag-mgs-api 2>/dev/null || log_warning "Serviço FastAPI não encontrado / FastAPI-Dienst nicht gefunden"

# Parar Apache
sudo systemctl stop apache2 2>/dev/null || log_warning "Apache não encontrado / Apache nicht gefunden"

log_success "Serviços parados / Dienste gestoppt"

# ============================================================================
# 3. EXTRAIR BACKUP / BACKUP EXTRAHIEREN
# ============================================================================
log_info "📂 [3/5] Extraindo backup / Extrahiere Backup..."

TEMP_DIR=$(mktemp -d)
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Encontrar diretório do backup
BACKUP_CONTENT=$(find "$TEMP_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)

if [ -z "$BACKUP_CONTENT" ]; then
    log_error "Estrutura de backup inválida / Ungültige Backup-Struktur"
fi

log_success "Backup extraído em / Backup extrahiert in: $TEMP_DIR"

# ============================================================================
# 4. RESTAURAR ARQUIVOS / DATEIEN WIEDERHERSTELLEN
# ============================================================================
log_info "♻️  [4/5] Restaurando arquivos / Stelle Dateien wieder her..."

# Restaurar banco de dados
if [ -f "$BACKUP_CONTENT/contracts.db" ]; then
    cp "$BACKUP_CONTENT/contracts.db" "$PROJECT_DIR/contracts.db"
    log_success "✓ Banco de dados restaurado / Datenbank wiederhergestellt"
fi

# Restaurar uploads
if [ -d "$BACKUP_CONTENT/uploads" ]; then
    rm -rf "$PROJECT_DIR/uploads"
    cp -r "$BACKUP_CONTENT/uploads" "$PROJECT_DIR/"
    log_success "✓ Uploads restaurados / Uploads wiederhergestellt"
fi

# Restaurar configurações (opcional, com confirmação)
if [ -d "$BACKUP_CONTENT/config" ]; then
    read -p "Restaurar configurações também? (s/N) / Konfigurationen auch wiederherstellen? (j/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[SsJj]$ ]]; then
        cp -r "$BACKUP_CONTENT/config/"* "$PROJECT_DIR/" 2>/dev/null || true
        log_success "✓ Configurações restauradas / Konfigurationen wiederhergestellt"
    fi
fi

# Limpar diretório temporário
rm -rf "$TEMP_DIR"

# ============================================================================
# 5. REINICIAR SERVIÇOS / DIENSTE NEU STARTEN
# ============================================================================
log_info "▶️  [5/5] Reiniciando serviços / Starte Dienste neu..."

# Definir permissões corretas
chmod 600 "$PROJECT_DIR/contracts.db" 2>/dev/null || true
chmod -R 755 "$PROJECT_DIR/uploads" 2>/dev/null || true

# Reiniciar serviços
sudo systemctl start apache2 2>/dev/null || log_warning "Erro ao iniciar Apache / Fehler beim Starten von Apache"
sudo systemctl start vertrag-mgs-api 2>/dev/null || log_warning "Erro ao iniciar FastAPI / Fehler beim Starten von FastAPI"

log_success "Serviços reiniciados / Dienste neu gestartet"

# ============================================================================
# RESUMO / ZUSAMMENFASSUNG
# ============================================================================
echo
echo "=================================================================="
echo "  ✅ RESTAURAÇÃO CONCLUÍDA / WIEDERHERSTELLUNG ABGESCHLOSSEN"
echo "=================================================================="
echo "  📦 Backup restaurado / Wiederhergestelltes Backup: $(basename "$BACKUP_FILE")"
echo "  🔒 Backup de segurança / Sicherungsbackup: $(basename "$SAFETY_BACKUP")"
echo "  📅 Data / Datum: $(date '+%d/%m/%Y %H:%M:%S')"
echo "=================================================================="
echo
echo "  ⚠️  IMPORTANTE / WICHTIG:"
echo "  - Verifique se o sistema está funcionando corretamente"
echo "  - Überprüfen Sie, ob das System ordnungsgemäß funktioniert"
echo "  - O backup de segurança está em / Sicherungsbackup ist in:"
echo "    $SAFETY_BACKUP"
echo "=================================================================="
