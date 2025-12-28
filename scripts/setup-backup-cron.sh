#!/bin/bash
# Configuração de Backup Automático via Cron
# Automatische Backup-Konfiguration über Cron
#
# DE: Konfiguriert tägliches automatisches Backup um 2 Uhr morgens
# PT: Configura backup automático diário às 2h da manhã

set -e

# Cores / Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCESSO/ERFOLG]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERRO/FEHLER]${NC} $1"
    exit 1
}

# Banner
echo "=================================================================="
echo "  ⏰ CONFIGURAR BACKUP AUTOMÁTICO / AUTOMATISCHES BACKUP KONFIGURIEREN"
echo "=================================================================="
echo

# Verificar se cron está instalado
if ! command -v crontab &> /dev/null; then
    log_error "Cron não está instalado / Cron ist nicht installiert"
fi

# Caminho completo do script de backup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="$SCRIPT_DIR/backup-system.sh"

if [ ! -f "$BACKUP_SCRIPT" ]; then
    log_error "Script de backup não encontrado / Backup-Script nicht gefunden: $BACKUP_SCRIPT"
fi

# Tornar script executável
chmod +x "$BACKUP_SCRIPT"

# Criar entrada do cron
CRON_ENTRY="0 2 * * * $BACKUP_SCRIPT >> /var/log/vertrag-mgs-backup.log 2>&1"

log_info "Configurando backup diário às 2:00 AM / Konfiguriere tägliches Backup um 2:00 Uhr..."

# Verificar se entrada já existe
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    log_info "Entrada de cron já existe, atualizando / Cron-Eintrag existiert bereits, aktualisiere..."
    # Remover entrada antiga
    crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT" | crontab -
fi

# Adicionar nova entrada
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

log_success "✅ Backup automático configurado / Automatisches Backup konfiguriert!"

# Criar diretório de logs
sudo mkdir -p /var/log
sudo touch /var/log/vertrag-mgs-backup.log
sudo chown $USER:$USER /var/log/vertrag-mgs-backup.log

echo
echo "=================================================================="
echo "  ✅ CONFIGURAÇÃO CONCLUÍDA / KONFIGURATION ABGESCHLOSSEN"
echo "=================================================================="
echo "  ⏰ Horário / Zeit: Diariamente às 2:00 AM / Täglich um 2:00 Uhr"
echo "  📋 Log: /var/log/vertrag-mgs-backup.log"
echo "  📦 Backups: /var/backups/vertrag-mgs/"
echo "  🔄 Retenção / Aufbewahrung: 30 dias / 30 Tage"
echo "=================================================================="
echo
echo "  Para verificar cron / Zum Überprüfen von Cron:"
echo "  crontab -l"
echo
echo "  Para testar backup manualmente / Zum manuellen Testen des Backups:"
echo "  $BACKUP_SCRIPT"
echo "=================================================================="
