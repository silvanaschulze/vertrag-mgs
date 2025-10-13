"""
Dokumentgenerierungs-Utilities für das Vertragsverwaltungssystem
Utilitários de geração de documentos para o Sistema de Gerenciamento de Contratos

Dieses Modul enthält Funktionen zur Generierung von PDF-Dokumenten und Berichten.
Este módulo contém funções para geração de documentos PDF e relatórios.
"""

from typing import Dict, Any, Optional
from docxtpl import DocxTemplate
from io import BytesIO
import os

def generate_contract_pdf(
    template_path: str, 
    data: Dict[str, Any],
    output_path: Optional[str] = None
) -> bytes:
    """
    Generiert ein Vertrags-PDF aus einer Vorlage / Gera um PDF de contrato a partir de um template
    
    Args / Argumentos:
        template_path (str): Pfad zur Word-Vorlage / Caminho para o template Word
        data (Dict[str, Any]): Daten für die Vorlage / Dados para o template
        output_path (Optional[str]): Ausgabepfad / Caminho de saída
        
    Returns / Retorna:
        bytes: PDF-Daten / Dados do PDF
    """
    try:
        # Word-Vorlage laden / Carregar template Word
        doc = DocxTemplate(template_path)
        
        # Daten in Vorlage einsetzen / Inserir dados no template
        doc.render(data)
        
        # PDF generieren / Gerar PDF
        if output_path:
            doc.save(output_path)
        
        # Bytes zurückgeben / Retornar bytes
        return doc.get_docx().read()
        
    except Exception as e:
        print(f"PDF-Generierungsfehler / Erro de geração de PDF: {e}")
        return b""

def generate_report_pdf(
    data: Dict[str, Any],
    report_type: str = "contracts_summary"
) -> bytes:
    """
    Generiert einen Berichts-PDF / Gera um PDF de relatório
    
    Args / Argumentos:
        data (Dict[str, Any]): Berichtsdaten / Dados do relatório
        report_type (str): Berichtstyp / Tipo de relatório
        
    Returns / Retorna:
        bytes: PDF-Daten / Dados do PDF
    """
    try:
        # Template-Pfad basierend auf Berichtstyp / Caminho do template baseado no tipo de relatório
        template_path = f"templates/{report_type}_template.docx"
        
        if not os.path.exists(template_path):
            # Standard-Template verwenden / Usar template padrão
            template_path = "templates/default_report_template.docx"
        
        return generate_contract_pdf(template_path, data)
        
    except Exception as e:
        print(f"Berichts-Generierungsfehler / Erro de geração de relatório: {e}")
        return b""

def generate_contract_summary_report(
    contracts_data: Dict[str, Any]
) -> bytes:
    """
    Generiert einen Vertragsübersichtsbericht / Gera um relatório de resumo de contratos
    
    Args / Argumentos:
        contracts_data (Dict[str, Any]): Vertragsdaten / Dados dos contratos
        
    Returns / Retorna:
        bytes: PDF-Daten / Dados do PDF
    """
    return generate_report_pdf(contracts_data, "contracts_summary")

def generate_expiry_report(
    expiring_contracts: Dict[str, Any]
) -> bytes:
    """
    Generiert einen Ablaufbericht / Gera um relatório de vencimento
    
    Args / Argumentos:
        expiring_contracts (Dict[str, Any]): Ablaufende Verträge / Contratos vencendo
        
    Returns / Retorna:
        bytes: PDF-Daten / Dados do PDF
    """
    return generate_report_pdf(expiring_contracts, "expiry_report")