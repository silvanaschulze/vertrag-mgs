#!/bin/bash
# Script para configurar permissões do projeto vertrag-mgs
# Script to configure vertrag-mgs project permissions

echo "🔐 Configurando permissões de segurança..."

# Arquivos sensíveis - apenas proprietário
chmod 600 contracts.db 2>/dev/null && echo "✅ contracts.db protegido" || echo "⚠️ contracts.db não encontrado"
chmod 600 alembic.ini && echo "✅ alembic.ini protegido"
chmod 600 backend/app/core/config.py 2>/dev/null && echo "✅ config.py protegido" || echo "⚠️ config.py não encontrado"

# Scripts executáveis
chmod +x clean-cache.sh && echo "✅ clean-cache.sh executável"
chmod +x setup-permissions.sh && echo "✅ setup-permissions.sh executável"

# Diretórios organizados
chmod 755 backend/ docs/ alembic/ 2>/dev/null && echo "✅ Diretórios organizados"

# Arquivos de código legíveis
find . -name "*.py" -not -path "./.venv/*" -exec chmod 644 {} \; 2>/dev/null && echo "✅ Arquivos Python organizados"
find . -name "*.md" -exec chmod 644 {} \; 2>/dev/null && echo "✅ Documentação organizada"

echo "🎉 Permissões configuradas com sucesso!"
echo ""
echo "📋 Resumo:"
echo "- Banco de dados: Protegido (600)"
echo "- Configurações: Protegidas (600)" 
echo "- Scripts: Executáveis (755)"
echo "- Código: Legível (644)"
echo "- Diretórios: Navegáveis (755)"