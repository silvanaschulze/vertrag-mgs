#!/bin/bash
# Setup Script para Deploy Interno - Vertrag MGS
# Script de Configuração para Deploy Interno
# 
# Este script faz a configuração inicial do ambiente
# This script performs initial environment setup

set -e

# Cores / Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logs bilíngues / Bilingual logs
log_info() {
    echo -e "${BLUE}ℹ️  DE: $1${NC}"
    echo -e "${BLUE}ℹ️  PT: $2${NC}"
    echo
}

log_success() {
    echo -e "${GREEN}✅ DE: $1${NC}"
    echo -e "${GREEN}✅ PT: $2${NC}"
    echo
}

log_warning() {
    echo -e "${YELLOW}⚠️  DE: $1${NC}"
    echo -e "${YELLOW}⚠️  PT: $2${NC}"
    echo
}

# Header
echo "=================================================================="
echo "    🚀 SETUP - VERTRAGSVERWALTUNGSSYSTEM / DEPLOY SETUP"
echo "=================================================================="
echo "    Deutsch: Vorbereitung für internen Deploy"
echo "    Português: Preparação para deploy interno"
echo "=================================================================="
echo

# Verificar se estamos na raiz do projeto
if [ ! -f "backend/main.py" ]; then
    echo -e "${RED}❌ Erro: Execute este script da raiz do projeto!${NC}"
    echo -e "${RED}❌ Error: Run this script from project root!${NC}"
    exit 1
fi

# Copiar configurações da pasta deploy para locais corretos
log_info "Kopiere Apache-Konfiguration..." \
         "Copiando configuração do Apache..."

# Criar backup da configuração atual se existir
if [ -f "/etc/apache2/sites-available/vertrag-mgs.conf" ]; then
    sudo cp /etc/apache2/sites-available/vertrag-mgs.conf /etc/apache2/sites-available/vertrag-mgs.conf.bak
fi

# Copiar nova configuração
sudo cp deploy/apache-internal.conf /etc/apache2/sites-available/vertrag-mgs.conf

log_success "Apache-Konfiguration installiert!" \
            "Configuração Apache instalada!"

# Verificar estrutura de permissões
log_info "Überprüfe Dateiberechtigungen..." \
         "Verificando permissões de arquivos..."

# Executar setup de permissões
if [ -f "setup-permissions.sh" ]; then
    chmod +x setup-permissions.sh
    ./setup-permissions.sh
else
    log_warning "setup-permissions.sh nicht gefunden!" \
                "setup-permissions.sh não encontrado!"
fi

log_success "Setup abgeschlossen! Jetzt können Sie deploy ausführen." \
            "Setup concluído! Agora você pode executar o deploy."

echo "=================================================================="
echo "  📋 NÄCHSTE SCHRITTE / PRÓXIMOS PASSOS:"
echo "=================================================================="
echo "  1. ./deploy-internal.sh deploy"
echo "  2. ./deploy-internal.sh status"
echo "=================================================================="
