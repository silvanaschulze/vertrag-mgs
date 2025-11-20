#!/bin/bash
# Script para otimizar performance do projeto
# Performance optimization script

echo "🧹 Limpando cache Python..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete

echo "🧹 Limpando cache de ferramentas..."
rm -rf .mypy_cache .pytest_cache

echo "🧹 Limpando logs..."
rm -f *.log mypy.log pytest.log flake8.log

echo "🧹 Limpando node_modules se existir..."
find . -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true

echo "✅ Limpeza concluída!"
echo "📊 Tamanho atual:"
du -sh .