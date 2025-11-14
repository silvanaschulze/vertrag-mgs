#!/usr/bin/env python3
"""Script para criar um PDF de teste e testar a API"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import requests
import os
import json

def create_test_pdf():
    """Cria um PDF simples para teste"""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Conteúdo que será extraído
    p.drawString(100, 750, "CONTRATO DE LOCAÇÃO")
    p.drawString(100, 720, "Locador: João Silva")
    p.drawString(100, 700, "Locatário: Maria Santos")
    p.drawString(100, 680, "Imóvel: Apartamento 201, Rua das Flores, 123")
    p.drawString(100, 660, "Valor: R$ 1.500,00")
    p.drawString(100, 640, "Início: 01/01/2024")
    p.drawString(100, 620, "Fim: 31/12/2024")
    p.drawString(100, 600, "Reajuste: IGPM anual")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer.getvalue()

def save_test_pdf():
    """Salva PDF de teste no disco"""
    pdf_content = create_test_pdf()
    with open("test_contract.pdf", "wb") as f:
        f.write(pdf_content)
    print("✓ PDF de teste criado: test_contract.pdf")

def test_api_status():
    """Testa se a API está online"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✓ API status: {response.status_code}")
        return True
    except requests.ConnectionError:
        print("✗ API não está rodando")
        return False

def create_test_user():
    """Cria usuário de teste"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Usuário de Teste"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/auth/register",
            json=user_data,
            timeout=10
        )
        print(f"Criação usuário: {response.status_code}")
        if response.status_code == 201:
            print("✓ Usuário criado com sucesso")
            return True
        elif response.status_code == 400:
            print("→ Usuário já existe")
            return True
        else:
            print(f"✗ Erro: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Erro ao criar usuário: {e}")
        return False

def login_user():
    """Faz login e retorna token"""
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/auth/login",
            data=login_data,
            timeout=10
        )
        if response.status_code == 200:
            token_data = response.json()
            print("✓ Login realizado com sucesso")
            return token_data.get("access_token")
        else:
            print(f"✗ Erro no login: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Erro ao fazer login: {e}")
        return None

def test_pdf_upload(token):
    """Testa upload de PDF"""
    if not os.path.exists("test_contract.pdf"):
        print("✗ PDF de teste não encontrado")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open("test_contract.pdf", "rb") as f:
        files = {"file": ("test_contract.pdf", f, "application/pdf")}
        
        try:
            response = requests.post(
                "http://localhost:8000/contracts/import/pdf",
                files=files,
                headers=headers,
                timeout=30
            )
            
            print(f"Upload PDF: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print("✓ Upload realizado com sucesso")
                print(f"  Contract ID: {result.get('id')}")
                print(f"  Original PDF: {result.get('original_pdf_filename')}")
                return result
            else:
                print(f"✗ Erro: {response.text}")
                return None
                
        except Exception as e:
            print(f"✗ Erro no upload: {e}")
            return None

def main():
    """Função principal de teste"""
    print("=== TESTE DA API PDF ===\n")
    
    # 1. Criar PDF de teste
    save_test_pdf()
    
    # 2. Verificar API
    if not test_api_status():
        print("Por favor, inicie o servidor primeiro:")
        print("uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
        return
    
    # 3. Criar usuário
    if not create_test_user():
        return
    
    # 4. Fazer login
    token = login_user()
    if not token:
        return
    
    # 5. Testar upload
    result = test_pdf_upload(token)
    if result:
        print("\n✓ Teste completo realizado com sucesso!")
        print(f"✓ Contrato criado com ID: {result.get('id')}")
    else:
        print("\n✗ Teste falhou")

if __name__ == "__main__":
    main()