"""
E-Mail-Utilities für das Vertragsverwaltungssystem
Utilitários de e-mail para o Sistema de Gerenciamento de Contratos

Dieses Modul enthält Funktionen zum Versenden von E-Mails und Benachrichtigungen.
Este módulo contém funções para envio de e-mails e notificações.
"""

from typing import Optional, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_email(
    to: str, 
    subject: str, 
    body: str, 
    is_html: bool = False
) -> bool:
    """
    Sendet eine E-Mail / Envia um e-mail
    
    Args / Argumentos:
        to (str): Empfänger-E-Mail-Adresse / Endereço de e-mail do destinatário
        subject (str): E-Mail-Betreff / Assunto do e-mail
        body (str): E-Mail-Inhalt / Conteúdo do e-mail
        is_html (bool): HTML-Format verwenden / Usar formato HTML
        
    Returns / Retorna:
        bool: Erfolg des E-Mail-Versands / Sucesso do envio do e-mail
    """
    try:
        # E-Mail-Konfiguration / Configuração de e-mail
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USER
        msg['To'] = to
        msg['Subject'] = subject
        
        # E-Mail-Inhalt hinzufügen / Adicionar conteúdo do e-mail
        if is_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        # E-Mail senden / Enviar e-mail
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(settings.SMTP_USER, to, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"E-Mail-Fehler / Erro de e-mail: {e}")
        return False

def send_notification_email(
    to: str, 
    contract_title: str, 
    days_remaining: int,
    contract_id: int
) -> bool:
    """
    Sendet eine Vertragsablauf-Benachrichtigung / Envia notificação de vencimento de contrato
    
    Args / Argumentos:
        to (str): Empfänger-E-Mail-Adresse / Endereço de e-mail do destinatário
        contract_title (str): Vertragstitel / Título do contrato
        days_remaining (int): Verbleibende Tage / Dias restantes
        contract_id (int): Vertrags-ID / ID do contrato
        
    Returns / Retorna:
        bool: Erfolg der Benachrichtigung / Sucesso da notificação
    """
    subject = f"Vertragsablauf-Warnung / Aviso de Vencimento de Contrato: {contract_title}"
    
    body = f"""
    Sehr geehrte Damen und Herren, / Prezados Senhores,
    
    Ihr Vertrag "{contract_title}" läuft in {days_remaining} Tagen ab.
    Seu contrato "{contract_title}" vence em {days_remaining} dias.
    
    Bitte überprüfen Sie die Vertragsdetails und ergreifen Sie gegebenenfalls Maßnahmen.
    Por favor, verifique os detalhes do contrato e tome as medidas necessárias.
    
    Vertrags-ID / ID do Contrato: {contract_id}
    
    Mit freundlichen Grüßen / Atenciosamente,
    Contract Management System
    """
    
    return send_email(to, subject, body)

def send_contract_created_notification(
    to: str,
    contract_title: str,
    contract_id: int
) -> bool:
    """
    Sendet eine Vertragserstellungs-Benachrichtigung / Envia notificação de criação de contrato
    
    Args / Argumentos:
        to (str): Empfänger-E-Mail-Adresse / Endereço de e-mail do destinatário
        contract_title (str): Vertragstitel / Título do contrato
        contract_id (int): Vertrags-ID / ID do contrato
        
    Returns / Retorna:
        bool: Erfolg der Benachrichtigung / Sucesso da notificação
    """
    subject = f"Neuer Vertrag erstellt / Novo Contrato Criado: {contract_title}"
    
    body = f"""
    Ein neuer Vertrag wurde erfolgreich erstellt.
    Um novo contrato foi criado com sucesso.
    
    Vertragstitel / Título do Contrato: {contract_title}
    Vertrags-ID / ID do Contrato: {contract_id}
    
    Sie können den Vertrag im System einsehen.
    Você pode visualizar o contrato no sistema.
    
    Mit freundlichen Grüßen / Atenciosamente,
    Contract Management System
    """
    
    return send_email(to, subject, body)