#!/usr/bin/env python3
"""
Script para corrigir caminhos de PDF no banco de dados e criar PDFs de teste
"""
import sqlite3
import os
from pathlib import Path

# Caminho do banco
DB_PATH = "contracts.db"
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads" / "contracts" / "persisted"

def create_simple_pdf(filepath: Path, contract_id: int, title: str):
    """Cria um PDF simples válido"""
    content = f"""%PDF-1.4
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
/Length 100
>>
stream
BT
/F1 16 Tf
100 750 Td
(Contract ID: {contract_id}) Tj
0 -30 Td
(Title: {title[:50]}) Tj
0 -30 Td
(This is a test PDF document) Tj
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
467
%%EOF"""
    
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content)
    print(f"✓ PDF criado: {filepath} ({filepath.stat().st_size} bytes)")

def fix_pdf_paths():
    """Corrige caminhos de PDF no banco e cria arquivos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Buscar contratos com PDF
    cursor.execute("""
        SELECT id, title, original_pdf_path, original_pdf_filename 
        FROM contracts 
        WHERE original_pdf_path IS NOT NULL OR original_pdf_filename IS NOT NULL
        LIMIT 10
    """)
    
    contracts = cursor.fetchall()
    print(f"\n📊 Encontrados {len(contracts)} contratos com PDF\n")
    
    for contract_id, title, old_path, old_filename in contracts:
        # Novo caminho correto
        contract_dir = UPLOAD_DIR / f"contract_{contract_id}"
        new_pdf_path = contract_dir / "original.pdf"
        
        # Criar PDF de teste
        create_simple_pdf(new_pdf_path, contract_id, title or "Untitled")
        
        # Atualizar banco
        relative_path = f"uploads/contracts/persisted/contract_{contract_id}/original.pdf"
        filename = old_filename or f"contract_{contract_id}.pdf"
        
        cursor.execute("""
            UPDATE contracts 
            SET original_pdf_path = ?, 
                original_pdf_filename = ?
            WHERE id = ?
        """, (relative_path, filename, contract_id))
        
        print(f"  ID {contract_id}: '{title[:40]}...' → {relative_path}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ {len(contracts)} contratos atualizados com sucesso!")
    print(f"\n📁 Estrutura criada em: {UPLOAD_DIR}")

if __name__ == "__main__":
    fix_pdf_paths()
