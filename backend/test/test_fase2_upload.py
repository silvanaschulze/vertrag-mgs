#!/usr/bin/env python3
"""
Testskript für Phase 2 Upload-Integration
Script de teste para integração de upload da Fase 2

Testet / Testa:
1. POST /contracts/with-upload - criar contrato com PDF
2. PUT /contracts/{id}/with-upload - atualizar contrato com PDF
3. Validação de FormData / Validação de FormData
4. Substituição de PDF / Substituição de PDF
"""

import sys
from pathlib import Path
import requests
import io
from datetime import date

# Configuração / Configuração
API_BASE = "http://localhost:8000/api"
USERNAME = "admin@test.com"
PASSWORD = "admin123"

def login() -> str:
    """
    Faz login e retorna token JWT
    Anmelden und JWT-Token zurückgeben
    """
    print("=" * 80)
    print("LOGIN / ANMELDUNG")
    print("=" * 80)
    
    response = requests.post(
        f"{API_BASE}/auth/login",
        data={
            "username": USERNAME,
            "password": PASSWORD
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Login erfolgreich / Login bem-sucedido")
        return token
    else:
        print(f"❌ Login fehlgeschlagen / Falha no login: {response.status_code}")
        print(response.text)
        sys.exit(1)


def create_dummy_pdf() -> bytes:
    """
    Cria um PDF mínimo válido para teste
    Erstellt eine minimale gültige PDF für Tests
    """
    # PDF mínimo válido (header + trailer)
    # Minimales gültiges PDF (Header + Trailer)
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000317 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
409
%%EOF
"""
    return pdf_content


def test_create_with_upload(token: str) -> int:
    """
    Testa POST /contracts/with-upload
    Testet POST /contracts/with-upload
    """
    print("\n" + "=" * 80)
    print("TEST 1: POST /contracts/with-upload")
    print("TESTE 1: POST /contracts/with-upload")
    print("=" * 80)
    
    # Criar PDF de teste / Test-PDF erstellen
    pdf_content = create_dummy_pdf()
    
    # Preparar FormData / FormData vorbereiten
    files = {
        'pdf_file': ('test_contract.pdf', io.BytesIO(pdf_content), 'application/pdf')
    }
    
    data = {
        'title': 'Test Contract with Upload / Testvertrag mit Upload',
        'client_name': 'Test Client GmbH',
        'start_date': '2026-01-20',
        'contract_type': 'SERVICE',
        'status': 'DRAFT',
        'description': 'Contrato de teste da Fase 2 / Testvertrag Phase 2',
        'value': '1500.50',
        'currency': 'EUR',
        'payment_frequency': 'monatlich'
    }
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    print("\n[Enviando / Senden]:")
    print(f"  - Título / Titel: {data['title']}")
    print(f"  - Cliente / Kunde: {data['client_name']}")
    print(f"  - PDF: test_contract.pdf ({len(pdf_content)} bytes)")
    
    response = requests.post(
        f"{API_BASE}/contracts/with-upload",
        files=files,
        data=data,
        headers=headers
    )
    
    if response.status_code == 201:
        contract = response.json()
        print(f"\n✅ BESTANDEN / PASSOU")
        print(f"  - Contract ID: {contract['id']}")
        print(f"  - Título / Titel: {contract['title']}")
        print(f"  - PDF anexado / PDF angehängt: {contract.get('original_pdf_filename', 'N/A')}")
        return contract['id']
    else:
        print(f"\n❌ FEHLGESCHLAGEN / FALHOU")
        print(f"  - Status: {response.status_code}")
        print(f"  - Erro / Fehler: {response.text}")
        return None # type: ignore


def test_update_with_upload(token: str, contract_id: int):
    """
    Testa PUT /contracts/{id}/with-upload
    Testet PUT /contracts/{id}/with-upload
    """
    print("\n" + "=" * 80)
    print(f"TEST 2: PUT /contracts/{contract_id}/with-upload")
    print(f"TESTE 2: PUT /contracts/{contract_id}/with-upload")
    print("=" * 80)
    
    # Criar novo PDF / Neues PDF erstellen
    pdf_content = create_dummy_pdf()
    
    files = {
        'pdf_file': ('updated_contract.pdf', io.BytesIO(pdf_content), 'application/pdf')
    }
    
    data = {
        'title': 'Updated Contract / Aktualisierter Vertrag',
        'value': '2000.00',
        'notes': 'PDF substituído na Fase 2 / PDF ersetzt in Phase 2'
    }
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    print("\n[Atualizando / Aktualisieren]:")
    print(f"  - Novo título / Neuer Titel: {data['title']}")
    print(f"  - Novo valor / Neuer Wert: {data['value']}")
    print(f"  - Novo PDF / Neues PDF: updated_contract.pdf ({len(pdf_content)} bytes)")
    
    response = requests.put(
        f"{API_BASE}/contracts/{contract_id}/with-upload",
        files=files,
        data=data,
        headers=headers
    )
    
    if response.status_code == 200:
        contract = response.json()
        print(f"\n✅ BESTANDEN / PASSOU")
        print(f"  - Título atualizado / Titel aktualisiert: {contract['title']}")
        print(f"  - Valor atualizado / Wert aktualisiert: {contract.get('value', 'N/A')}")
        print(f"  - PDF atualizado / PDF aktualisiert: {contract.get('original_pdf_filename', 'N/A')}")
        return True
    else:
        print(f"\n❌ FEHLGESCHLAGEN / FALHOU")
        print(f"  - Status: {response.status_code}")
        print(f"  - Erro / Fehler: {response.text}")
        return False


def test_update_without_pdf(token: str, contract_id: int):
    """
    Testa atualizar sem PDF (deve manter PDF existente)
    Testet Aktualisierung ohne PDF (sollte bestehendes PDF behalten)
    """
    print("\n" + "=" * 80)
    print(f"TEST 3: PUT /contracts/{contract_id}/with-upload (SEM PDF / OHNE PDF)")
    print(f"TESTE 3: PUT /contracts/{contract_id}/with-upload (SEM PDF / OHNE PDF)")
    print("=" * 80)
    
    data = {
        'notes': 'Atualização sem PDF - deve manter existente / Update ohne PDF - soll bestehendes behalten'
    }
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    print("\n[Atualizando apenas notas / Nur Notizen aktualisieren]")
    
    response = requests.put(
        f"{API_BASE}/contracts/{contract_id}/with-upload",
        data=data,
        headers=headers
    )
    
    if response.status_code == 200:
        contract = response.json()
        pdf_exists = contract.get('original_pdf_filename') is not None
        print(f"\n✅ BESTANDEN / PASSOU")
        print(f"  - PDF mantido / PDF behalten: {'Sim / Ja' if pdf_exists else 'Não / Nein'}")
        print(f"  - Notas / Notizen: {contract.get('notes', 'N/A')[:50]}...")
        return pdf_exists
    else:
        print(f"\n❌ FEHLGESCHLAGEN / FALHOU")
        print(f"  - Status: {response.status_code}")
        print(f"  - Erro / Fehler: {response.text}")
        return False


def test_invalid_file_type(token: str):
    """
    Testa upload de arquivo não-PDF (deve rejeitar)
    Testet Upload von Nicht-PDF-Datei (sollte ablehnen)
    """
    print("\n" + "=" * 80)
    print("TEST 4: POST /contracts/with-upload (ARQUIVO INVÁLIDO / UNGÜLTIGE DATEI)")
    print("TESTE 4: POST /contracts/with-upload (ARQUIVO INVÁLIDO / UNGÜLTIGE DATEI)")
    print("=" * 80)
    
    # Arquivo de texto fingindo ser PDF / Textdatei gibt sich als PDF aus
    fake_pdf = b"This is not a PDF file"
    
    files = {
        'pdf_file': ('fake.txt', io.BytesIO(fake_pdf), 'text/plain')
    }
    
    data = {
        'title': 'Should Fail / Sollte fehlschlagen',
        'client_name': 'Test',
        'start_date': '2026-01-20'
    }
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.post(
        f"{API_BASE}/contracts/with-upload",
        files=files,
        data=data,
        headers=headers
    )
    
    if response.status_code == 400:
        print(f"\n✅ BESTANDEN / PASSOU - Arquivo rejeitado corretamente / Datei korrekt abgelehnt")
        print(f"  - Erro / Fehler: {response.json().get('detail', 'N/A')}")
        return True
    else:
        print(f"\n❌ FEHLGESCHLAGEN / FALHOU - Deveria ter rejeitado / Sollte abgelehnt haben")
        print(f"  - Status: {response.status_code}")
        return False


def main():
    """
    Executa todos os testes / Führt alle Tests aus
    """
    print("\n" + "=" * 80)
    print("PHASE 2 TESTS - UPLOAD-INTEGRATION")
    print("TESTES FASE 2 - INTEGRAÇÃO DE UPLOAD")
    print("=" * 80)
    
    # Login
    token = login()
    
    # Executar testes / Tests ausführen
    results = []
    
    # Test 1: Criar com PDF / Mit PDF erstellen
    contract_id = test_create_with_upload(token)
    results.append(("CREATE with PDF / ERSTELLEN mit PDF", contract_id is not None))
    
    if contract_id:
        # Test 2: Atualizar com novo PDF / Mit neuem PDF aktualisieren
        update_success = test_update_with_upload(token, contract_id)
        results.append(("UPDATE with PDF / AKTUALISIEREN mit PDF", update_success))
        
        # Test 3: Atualizar sem PDF / Ohne PDF aktualisieren
        keep_pdf = test_update_without_pdf(token, contract_id)
        results.append(("UPDATE without PDF (keep existing) / AKTUALISIEREN ohne PDF (behalten)", keep_pdf))
    
    # Test 4: Validação de tipo / Typvalidierung
    reject_invalid = test_invalid_file_type(token)
    results.append(("REJECT invalid file / ABLEHNEN ungültige Datei", reject_invalid))
    
    # Resumo / Zusammenfassung
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG / RESUMO")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✅ BESTANDEN/PASSOU" if passed else "❌ FEHLGESCHLAGEN/FALHOU"
        print(f"{status} - {test_name}")
    
    if all(r[1] for r in results):
        print("\n🎉 ALLE TESTS BESTANDEN! / TODOS OS TESTES PASSARAM! 🎉")
        print("\nNächste Schritte / Próximos passos:")
        print("1. Manuell im Frontend testen / Testar manualmente no frontend")
        print("2. Phase 3 starten / Iniciar Fase 3")
        return 0
    else:
        print("\n❌ EINIGE TESTS FEHLGESCHLAGEN! / ALGUNS TESTES FALHARAM!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
