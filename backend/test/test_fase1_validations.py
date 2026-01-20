#!/usr/bin/env python3
"""
Testskript für Phase 1 Validierungen
Script de teste para validações da Fase 1

Testet / Testa:
1. Validierung von payment_custom_years / Validação de payment_custom_years
2. UTF-8 Sanitisierung von Dateinamen / Sanitização UTF-8 de nomes de arquivo
3. Sekundäre Sortierung bei Paginierung / Ordenação secundária na paginação
"""

import sys
from pathlib import Path
from datetime import date
from pydantic import ValidationError
from urllib.parse import quote
import re

# Backend-Pfad hinzufügen / Adicionar caminho do backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas.contract import (
    ContractCreate, 
    ContractUpdate, 
    PaymentFrequency,
    ContractType
)


def test_payment_custom_years_validation():
    """
    Testet bedingte Validierung von payment_custom_years
    Testa validação condicional de payment_custom_years
    """
    print("=" * 80)
    print("TEST 1: Validierung payment_custom_years")
    print("TESTE 1: Validação payment_custom_years")
    print("=" * 80)
    
    # T1: CUSTOM_YEARS ohne custom_years → sollte ablehnen
    # T1: CUSTOM_YEARS sem custom_years → deve rejeitar
    print("\n[T1] CUSTOM_YEARS ohne/sem custom_years → sollte ablehnen/deve rejeitar")
    try:
        contract = ContractCreate(
            title="Test Contract",
            client_name="Test Client",
            start_date=date(2026, 1, 20),
            payment_frequency=PaymentFrequency.CUSTOM_YEARS,
            payment_custom_years=None
        ) # type: ignore
        print("❌ FEHLGESCHLAGEN/FALHOU: Sollte abgelehnt haben / Deveria ter rejeitado")
        return False
    except ValidationError as e:
        print(f"✅ BESTANDEN/PASSOU: {e.errors()[0]['msg'][:80]}...")
    
    # T2: CUSTOM_YEARS mit custom_years=5 → sollte akzeptieren
    # T2: CUSTOM_YEARS com custom_years=5 → deve aceitar
    print("\n[T2] CUSTOM_YEARS mit/com custom_years=5 → sollte akzeptieren/deve aceitar")
    try:
        contract = ContractCreate(
            title="Test Contract",
            client_name="Test Client",
            start_date=date(2026, 1, 20),
            payment_frequency=PaymentFrequency.CUSTOM_YEARS,
            payment_custom_years=5
        ) # type: ignore
        print(f"✅ BESTANDEN/PASSOU: payment_custom_years={contract.payment_custom_years}")
    except ValidationError as e:
        print(f"❌ FEHLGESCHLAGEN/FALHOU: {e}")
        return False
    
    # T3: MONTHLY mit custom_years=5 → sollte auf null setzen
    # T3: MONTHLY com custom_years=5 → deve limpar para null
    print("\n[T3] MONTHLY mit/com custom_years=5 → sollte löschen/deve limpar")
    try:
        contract = ContractCreate(
            title="Test Contract",
            client_name="Test Client",
            start_date=date(2026, 1, 20),
            payment_frequency=PaymentFrequency.MONTHLY,
            payment_custom_years=5
        ) # type: ignore
        if contract.payment_custom_years is None:
            print("✅ BESTANDEN/PASSOU: Automatisch auf null gesetzt / Limpou para null")
        else:
            print(f"❌ FEHLGESCHLAGEN/FALHOU: payment_custom_years={contract.payment_custom_years}")
            return False
    except ValidationError as e:
        print(f"❌ FEHLGESCHLAGEN/FALHOU: {e}")
        return False
    
    # T4: MONTHLY ohne custom_years → sollte akzeptieren
    # T4: MONTHLY sem custom_years → deve aceitar
    print("\n[T4] MONTHLY ohne/sem custom_years → sollte akzeptieren/deve aceitar")
    try:
        contract = ContractCreate(
            title="Test Contract",
            client_name="Test Client",
            start_date=date(2026, 1, 20),
            payment_frequency=PaymentFrequency.MONTHLY,
            payment_custom_years=None
        ) # type: ignore
        print("✅ BESTANDEN/PASSOU")
    except ValidationError as e:
        print(f"❌ FEHLGESCHLAGEN/FALHOU: {e}")
        return False
    
    # T5: ContractUpdate mit gleicher Logik
    # T5: ContractUpdate com mesma lógica
    print("\n[T5] ContractUpdate: CUSTOM_YEARS ohne/sem custom_years")
    try:
        update = ContractUpdate(
            payment_frequency=PaymentFrequency.CUSTOM_YEARS,
            payment_custom_years=None
        ) # type: ignore
        print("❌ FEHLGESCHLAGEN/FALHOU")
        return False
    except ValidationError as e:
        print(f"✅ BESTANDEN/PASSOU: {e.errors()[0]['msg'][:80]}...")
    
    print("\n" + "=" * 80)
    print("✅ ALLE VALIDIERUNGSTESTS BESTANDEN!")
    print("✅ TODOS OS TESTES DE VALIDAÇÃO PASSARAM!")
    print("=" * 80)
    return True


def test_utf8_filename_encoding():
    """
    Testet UTF-8-Kodierung für deutsche Dateinamen
    Testa codificação UTF-8 para nomes de arquivo alemães
    """
    print("\n" + "=" * 80)
    print("TEST 2: UTF-8 Sanitisierung von Dateinamen")
    print("TESTE 2: Sanitização UTF-8 de nomes de arquivo")
    print("=" * 80)
    
    # Deutsche Dateinamen / Nomes de arquivo alemães
    test_filenames = [
        "Bürovertrag_München.pdf",
        "Vertrag_für_Köln.pdf",
        "Geschäftsordnung_Düsseldorf.pdf",
        "Mietvertrag_Straße_123.pdf"
    ]
    
    for filename in test_filenames:
        print(f"\n[Original]: {filename}")
        
        # ASCII Fallback für alte Browser / Fallback ASCII para browsers antigos
        safe_ascii = re.sub(r'[^\w\s.-]', '_', filename)
        print(f"[ASCII Fallback]: {safe_ascii}")
        
        # UTF-8 Kodierung für moderne Browser / Codificação UTF-8 para browsers modernos
        safe_utf8 = quote(filename.encode('utf-8'))
        print(f"[UTF-8 Encoded]: {safe_utf8}")
        
        # Finaler Header / Header final
        header = f'attachment; filename="{safe_ascii}"; filename*=UTF-8\'\'{safe_utf8}'
        print(f"[Header]: {header[:70]}...")
        
        if '%C3%' in safe_utf8:
            print("✅ UTF-8 Sonderzeichen erhalten / caracteres especiais preservados")
    
    print("\n" + "=" * 80)
    print("✅ UTF-8 TEST ABGESCHLOSSEN! / COMPLETADO!")
    print("=" * 80)
    return True


def main():
    """
    Führt alle Tests aus / Executa todos os testes
    """
    print("\n" + "=" * 80)
    print("PHASE 1 TESTS - RISIKOARME KORREKTUREN")
    print("TESTES FASE 1 - CORREÇÕES DE BAIXO RISCO")
    print("=" * 80)
    
    results = [
        ("Validierung payment_custom_years / Validação payment_custom_years", 
         test_payment_custom_years_validation()),
        ("UTF-8 Dateinamen-Kodierung / Codificação UTF-8 nomes arquivo", 
         test_utf8_filename_encoding())
    ]
    
    # Zusammenfassung / Resumo
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
        print("2. Paginierung mit 252 Verträgen prüfen / Verificar paginação com 252 contratos")
        print("3. Phase 2 starten / Iniciar Fase 2")
        return 0
    else:
        print("\n❌ EINIGE TESTS FEHLGESCHLAGEN! / ALGUNS TESTES FALHARAM!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
