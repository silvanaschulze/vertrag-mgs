#!/bin/bash
# Docker Build Script - Vertrag MGS
# Script de Build Docker
#
# DE: Baut Docker-Images und pusht zu Registry (optional)
# PT: Constrói imagens Docker e envia para registry (opcional)

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

# Configurações / Konfigurationen
IMAGE_NAME="vertrag-mgs-backend"
IMAGE_TAG="${1:-latest}"
REGISTRY="${REGISTRY:-}"  # Definir via variável de ambiente se necessário

# Banner
echo "=================================================================="
echo "  🐳 DOCKER BUILD - VERTRAG MGS"
echo "=================================================================="
echo "  Imagem / Image: $IMAGE_NAME:$IMAGE_TAG"
echo "=================================================================="
echo

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    log_error "Docker não está instalado / Docker ist nicht installiert"
fi

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    log_error "Execute este script da raiz do projeto / Führen Sie dieses Skript aus dem Projektstamm aus"
fi

# ============================================================================
# 1. BUILD DA IMAGEM / IMAGE BUILD
# ============================================================================
log_info "🔨 [1/3] Construindo imagem Docker / Baue Docker-Image..."

cd backend

docker build \
    --tag "$IMAGE_NAME:$IMAGE_TAG" \
    --tag "$IMAGE_NAME:latest" \
    --file Dockerfile \
    --build-arg BUILDTIME=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    .

cd ..

log_success "Imagem construída / Image gebaut: $IMAGE_NAME:$IMAGE_TAG"

# ============================================================================
# 2. VERIFICAR IMAGEM / IMAGE PRÜFEN
# ============================================================================
log_info "🔍 [2/3] Verificando imagem / Überprüfe Image..."

docker images "$IMAGE_NAME:$IMAGE_TAG"

IMAGE_SIZE=$(docker images "$IMAGE_NAME:$IMAGE_TAG" --format "{{.Size}}")
log_success "Tamanho da imagem / Image-Größe: $IMAGE_SIZE"

# ============================================================================
# 3. PUSH PARA REGISTRY (OPCIONAL) / PUSH ZU REGISTRY (OPTIONAL)
# ============================================================================
if [ -n "$REGISTRY" ]; then
    log_info "📤 [3/3] Enviando para registry / Sende zu Registry: $REGISTRY"
    
    FULL_IMAGE="$REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
    
    docker tag "$IMAGE_NAME:$IMAGE_TAG" "$FULL_IMAGE"
    docker push "$FULL_IMAGE"
    
    log_success "Imagem enviada / Image gesendet: $FULL_IMAGE"
else
    log_info "⏭️  [3/3] Pulando push para registry (REGISTRY não definida) / Überspringe Registry-Push (REGISTRY nicht definiert)"
fi

# ============================================================================
# RESUMO / ZUSAMMENFASSUNG
# ============================================================================
echo
echo "=================================================================="
echo "  ✅ BUILD CONCLUÍDO / BUILD ABGESCHLOSSEN"
echo "=================================================================="
echo "  🐳 Imagem / Image: $IMAGE_NAME:$IMAGE_TAG"
echo "  📏 Tamanho / Größe: $IMAGE_SIZE"
echo "=================================================================="
echo
echo "  Para executar / Zum Ausführen:"
echo "  docker run -p 8000:8000 $IMAGE_NAME:$IMAGE_TAG"
echo
echo "  Para usar com docker-compose / Für docker-compose:"
echo "  docker-compose up -d"
echo "=================================================================="
