#!/bin/bash
# Script de Deploy Interno - Vertragsverwaltungssystem
# Script de Deploy Interno - Sistema de Gerenciamento de Contratos
# 
# Uso / Verwendung:
# ./deploy-internal.sh [production|development]

set -e  # Exit on any error / Sair em caso de erro

# Cores para output / Farben für Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações / Konfigurationen
PROJECT_NAME="vertrag-mgs"
PROJECT_DIR="/home/sschulze/projects/vertrag-mgs"
APACHE_DIR="/var/www/html"
APACHE_CONFIG_DIR="/etc/apache2/sites-available"
SERVICE_PORT="8000"
SERVICE_NAME="vertrag-mgs-api"

# Funções de log bilíngues / Zweisprachige Log-Funktionen
log_info() {
    echo -e "${BLUE}ℹ️  DE:${NC} $1"
    echo -e "${BLUE}ℹ️  PT:${NC} $2"
    echo
}

log_success() {
    echo -e "${GREEN}✅ DE:${NC} $1"
    echo -e "${GREEN}✅ PT:${NC} $2"
    echo
}

log_warning() {
    echo -e "${YELLOW}⚠️  DE:${NC} $1"
    echo -e "${YELLOW}⚠️  PT:${NC} $2"
    echo
}

log_error() {
    echo -e "${RED}❌ DE:${NC} $1"
    echo -e "${RED}❌ PT:${NC} $2"
    echo
    exit 1
}

# Banner do sistema / System Banner
show_banner() {
    echo "================================================================================================"
    echo "    🏢 INTERNO DEPLOY - VERTRAGSVERWALTUNGSSYSTEM / SISTEMA DE GERENCIAMENTO DE CONTRATOS    "
    echo "================================================================================================"
    echo "    Deutsch: Automatisches Deployment für Firmenserver"
    echo "    Português: Deploy automático para servidor da empresa"
    echo "================================================================================================"
    echo
}

# Verificar se é root / Check if running as root
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Als Root ausgeführt - Vorsicht bei Berechtigungen!" \
                   "Executando como root - cuidado com permissões!"
    fi
}

# Verificar dependências / Check dependencies
check_dependencies() {
    log_info "Überprüfe Systemabhängigkeiten..." \
             "Verificando dependências do sistema..."

    # Verificar Python / Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 ist nicht installiert!" \
                  "Python3 não está instalado!"
    fi

    # Verificar Apache / Check Apache
    if ! command -v apache2 &> /dev/null; then
        log_warning "Apache2 ist nicht installiert. Installiere Apache2..." \
                   "Apache2 não está instalado. Instalando Apache2..."
        sudo apt update
        sudo apt install -y apache2
    fi

    # Verificar pip / Check pip
    if ! command -v pip3 &> /dev/null; then
        log_warning "pip3 ist nicht installiert. Installiere pip3..." \
                   "pip3 não está instalado. Instalando pip3..."
        sudo apt install -y python3-pip
    fi

    log_success "Alle Abhängigkeiten sind verfügbar!" \
                "Todas as dependências estão disponíveis!"
}

# Setup do ambiente Python / Python environment setup
setup_python_env() {
    log_info "Richte Python-Umgebung ein..." \
             "Configurando ambiente Python..."

    cd "$PROJECT_DIR"

    # Criar/ativar virtual environment / Create/activate virtual environment
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        log_success "Virtuelle Umgebung erstellt!" \
                    "Ambiente virtual criado!"
    fi

    source .venv/bin/activate

    # Instalar dependências / Install dependencies
    if [ -f "backend/requirements.txt" ]; then
        pip install -r backend/requirements.txt
        log_success "Python-Abhängigkeiten installiert!" \
                    "Dependências Python instaladas!"
    else
        log_warning "requirements.txt nicht gefunden!" \
                   "requirements.txt não encontrado!"
    fi
}

# Configurar banco de dados / Configure database
setup_database() {
    log_info "Konfiguriere Datenbank..." \
             "Configurando banco de dados..."

    cd "$PROJECT_DIR"
    source .venv/bin/activate

    # Executar migrações / Run migrations
    if command -v alembic &> /dev/null; then
        alembic upgrade head
        log_success "Datenbankmigrationen ausgeführt!" \
                    "Migrações do banco executadas!"
    else
        log_warning "Alembic nicht gefunden - überspringe Migrationen!" \
                   "Alembic não encontrado - pulando migrações!"
    fi

    # Configurar permissões do banco / Configure database permissions
    if [ -f "contracts.db" ]; then
        chmod 600 contracts.db
        log_success "Datenbankberechtigungen konfiguriert!" \
                    "Permissões do banco configuradas!"
    fi
}

# Configurar Apache para servir frontend / Configure Apache to serve frontend
setup_apache() {
    log_info "Konfiguriere Apache für Frontend..." \
             "Configurando Apache para frontend..."

    # Criar configuração do site / Create site configuration
    cat > "/tmp/vertrag-mgs.conf" << EOF
<VirtualHost *:80>
    ServerName vertrag-mgs.local
    DocumentRoot $APACHE_DIR/vertrag-mgs

    # Servir arquivos estáticos do frontend / Serve frontend static files
    <Directory "$APACHE_DIR/vertrag-mgs">
        AllowOverride All
        Require all granted
    </Directory>

    # Proxy para API FastAPI / Proxy to FastAPI API
    ProxyPreserveHost On
    ProxyPass /api/ http://localhost:$SERVICE_PORT/
    ProxyPassReverse /api/ http://localhost:$SERVICE_PORT/

    # Log files / Arquivos de log
    ErrorLog \${APACHE_LOG_DIR}/vertrag-mgs-error.log
    CustomLog \${APACHE_LOG_DIR}/vertrag-mgs-access.log combined
</VirtualHost>
EOF

    # Mover configuração / Move configuration
    sudo mv "/tmp/vertrag-mgs.conf" "$APACHE_CONFIG_DIR/vertrag-mgs.conf"

    # Ativar site e módulos / Enable site and modules
    sudo a2enmod proxy
    sudo a2enmod proxy_http
    sudo a2ensite vertrag-mgs.conf
    sudo a2dissite 000-default.conf

    # Restart Apache / Reiniciar Apache
    sudo systemctl restart apache2

    log_success "Apache konfiguriert und neu gestartet!" \
                "Apache configurado e reiniciado!"
}

# Criar serviço systemd para FastAPI / Create systemd service for FastAPI
setup_fastapi_service() {
    log_info "Erstelle FastAPI-Systemdienst..." \
             "Criando serviço systemd para FastAPI..."

    cat > "/tmp/$SERVICE_NAME.service" << EOF
[Unit]
Description=Vertragsverwaltungssystem API / Sistema de Gerenciamento de Contratos API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/.venv/bin"
ExecStart=$PROJECT_DIR/.venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port $SERVICE_PORT
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    # Mover e ativar serviço / Move and enable service
    sudo mv "/tmp/$SERVICE_NAME.service" "/etc/systemd/system/"
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    sudo systemctl start "$SERVICE_NAME"

    log_success "FastAPI-Dienst erstellt und gestartet!" \
                "Serviço FastAPI criado e iniciado!"
}

# Configurar permissões de arquivos / Configure file permissions
setup_file_permissions() {
    log_info "Konfiguriere Dateiberechtigungen..." \
             "Configurando permissões de arquivos..."

    cd "$PROJECT_DIR"

    # Executar script de permissões existente / Run existing permissions script
    if [ -f "setup-permissions.sh" ]; then
        chmod +x setup-permissions.sh
        ./setup-permissions.sh
    fi

    # Configurar propriedade Apache / Configure Apache ownership
    if [ -d "$APACHE_DIR/vertrag-mgs" ]; then
        sudo chown -R www-data:www-data "$APACHE_DIR/vertrag-mgs"
    fi

    log_success "Dateiberechtigungen konfiguriert!" \
                "Permissões de arquivos configuradas!"
}

# Função de limpeza / Cleanup function
cleanup_old_deployment() {
    log_info "Bereinige alte Deployment-Dateien..." \
             "Limpando arquivos de deploy antigos..."

    # Parar serviços antigos / Stop old services
    sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true

    # Remover configurações antigas / Remove old configurations
    sudo rm -f "$APACHE_CONFIG_DIR/vertrag-mgs.conf.bak"

    log_success "Bereinigung abgeschlossen!" \
                "Limpeza concluída!"
}

# Deploy principal / Main deployment
deploy_application() {
    local mode=${1:-development}
    
    log_info "Starte Deployment im $mode Modus..." \
             "Iniciando deploy em modo $mode..."

    cleanup_old_deployment
    check_dependencies
    setup_python_env
    setup_database
    setup_apache
    setup_fastapi_service
    setup_file_permissions

    log_success "Deployment erfolgreich abgeschlossen!" \
                "Deploy concluído com sucesso!"
}

# Status do sistema / System status
show_status() {
    echo "================================================================================================"
    echo "    📊 SYSTEMSTATUS / STATUS DO SISTEMA"
    echo "================================================================================================"
    
    # Apache Status / Status do Apache
    if systemctl is-active --quiet apache2; then
        echo -e "${GREEN}✅ Apache2: Aktiv / Ativo${NC}"
    else
        echo -e "${RED}❌ Apache2: Inaktiv / Inativo${NC}"
    fi

    # FastAPI Status / Status do FastAPI
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ FastAPI: Aktiv / Ativo (Port $SERVICE_PORT)${NC}"
    else
        echo -e "${RED}❌ FastAPI: Inaktiv / Inativo${NC}"
    fi

    # URLs de acesso / Access URLs
    echo
    echo "🌐 ZUGRIFF / ACESSO:"
    echo "   Frontend: http://$(hostname -I | awk '{print $1}')"
    echo "   API:      http://$(hostname -I | awk '{print $1}')/api/"
    echo "   Docs:     http://$(hostname -I | awk '{print $1}')/api/docs"
    echo
}

# Logs do sistema / System logs
show_logs() {
    local service=${1:-all}
    
    case $service in
        apache)
            echo "📋 APACHE LOGS:"
            sudo tail -n 20 /var/log/apache2/vertrag-mgs-error.log 2>/dev/null || echo "Keine Apache-Logs gefunden / Logs do Apache não encontrados"
            ;;
        fastapi)
            echo "📋 FASTAPI LOGS:"
            sudo journalctl -u "$SERVICE_NAME" -n 20 --no-pager
            ;;
        all|*)
            show_logs apache
            echo
            show_logs fastapi
            ;;
    esac
}

# Menu principal / Main menu
show_menu() {
    echo "================================================================================================"
    echo "    🎛️  OPTIONEN / OPÇÕES"
    echo "================================================================================================"
    echo "  1) deploy     - Vollständiges Deployment / Deploy completo"
    echo "  2) status     - Systemstatus anzeigen / Mostrar status do sistema"
    echo "  3) logs       - Logs anzeigen / Mostrar logs"
    echo "  4) restart    - Services neu starten / Reiniciar serviços"
    echo "  5) stop       - Services stoppen / Parar serviços"
    echo "  6) help       - Hilfe anzeigen / Mostrar ajuda"
    echo "================================================================================================"
}

# Menu de ajuda / Help menu
show_help() {
    echo "================================================================================================"
    echo "    📖 HILFE / AJUDA"
    echo "================================================================================================"
    echo
    echo "VERWENDUNG / USO:"
    echo "  $0 [command]"
    echo
    echo "BEFEHLE / COMANDOS:"
    echo "  deploy     - Führt vollständiges Deployment durch / Executa deploy completo"
    echo "  status     - Zeigt aktuellen Systemstatus / Mostra status atual do sistema"
    echo "  logs       - Zeigt Systemlogs / Mostra logs do sistema"
    echo "  restart    - Startet alle Services neu / Reinicia todos os serviços"
    echo "  stop       - Stoppt alle Services / Para todos os serviços"
    echo "  help       - Zeigt diese Hilfe / Mostra esta ajuda"
    echo
    echo "BEISPIELE / EXEMPLOS:"
    echo "  $0 deploy          # Deployment durchführen / Fazer deploy"
    echo "  $0 status          # Status prüfen / Verificar status"
    echo "  $0 logs fastapi    # FastAPI logs / Logs do FastAPI"
    echo
    echo "FIREWALL-KONFIGURATION / CONFIGURAÇÃO DE FIREWALL:"
    echo "  sudo ufw allow 80/tcp    # HTTP-Port öffnen / Abrir porta HTTP"
    echo "  sudo ufw allow 8000/tcp  # FastAPI-Port öffnen / Abrir porta FastAPI"
    echo
}

# Restart services / Reiniciar serviços
restart_services() {
    log_info "Starte Services neu..." \
             "Reiniciando serviços..."

    sudo systemctl restart apache2
    sudo systemctl restart "$SERVICE_NAME"

    log_success "Services neu gestartet!" \
                "Serviços reiniciados!"
}

# Stop services / Parar serviços
stop_services() {
    log_info "Stoppe Services..." \
             "Parando serviços..."

    sudo systemctl stop "$SERVICE_NAME"
    sudo systemctl stop apache2

    log_success "Services gestoppt!" \
                "Serviços parados!"
}

# Main function / Função principal
main() {
    show_banner
    check_permissions

    case ${1:-menu} in
        deploy)
            deploy_application ${2:-development}
            show_status
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs ${2:-all}
            ;;
        restart)
            restart_services
            show_status
            ;;
        stop)
            stop_services
            ;;
        help|--help|-h)
            show_help
            ;;
        menu|*)
            show_menu
            ;;
    esac
}

# Executar função principal / Run main function
main "$@"