"""Service wrapper for PDFReader

Este módulo delega para a implementação existente em
`app.services.pdf_reader.PDFReaderService`. Mantém a API estável para
refatorações incrementais.
"""
from typing import Any

def get_pdf_reader_service():
    """Retorna instância do serviço existente (import lazy).

    Faz import dentro da função para evitar carregar dependências do
    projeto quando o pacote scaffold é apenas importado.
    """
    try:
        from app.services.pdf_reader import PDFReaderService as _OrigPDFReaderService
    except Exception as e:
        raise
    return _OrigPDFReaderService()


# Alias para compatibilidade (lazy)
def PDFReaderService(*args, **kwargs):
    svc = get_pdf_reader_service()
    return svc
