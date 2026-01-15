#!/usr/bin/env python3
"""
Script para criar 200 contratos de teste com TODOS os campos preenchidos
Skript zum Erstellen von 200 Testverträgen mit ALLEN ausgefüllten Feldern
"""

import sqlite3
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Conectar ao banco
conn = sqlite3.connect('contracts.db')
cursor = conn.cursor()

print("🗑️  Deletando contratos existentes...")
cursor.execute("DELETE FROM contracts")
deleted = cursor.rowcount
print(f"   ✅ {deleted} contratos deletados")

# Dados realistas para contratos
STATUSES = ['ACTIVE', 'DRAFT', 'EXPIRED', 'TERMINATED']
TYPES = ['SERVICE', 'PRODUCT', 'LEASE', 'RENTAL', 'PARTNERSHIP', 'OTHER']
LEGAL_FORMS = ['gmbh', 'ug', 'ag', 'kg', 'gbr', 'ev', 'other']
PAYMENT_FREQUENCIES = ['monatlich', 'vierteljährlich', 'halbjährlich', 'jährlich', 'alle_x_jahre', 'einmalig']

COMPANIES = [
    'Siemens AG', 'SAP SE', 'Deutsche Telekom AG', 'BMW Group', 'Volkswagen AG',
    'BASF SE', 'Allianz SE', 'Deutsche Bank AG', 'Bayer AG', 'Daimler AG',
    'Adidas AG', 'Continental AG', 'Deutsche Post DHL', 'E.ON SE', 'Fresenius SE',
    'HeidelbergCement AG', 'Infineon Technologies AG', 'Linde plc', 'Merck KGaA',
    'Munich Re', 'Beiersdorf AG', 'Covestro AG', 'Delivery Hero SE', 'Henkel AG',
    'Puma SE', 'RWE AG', 'Symrise AG', 'Vonovia SE', 'Zalando SE'
]

DEPARTMENTS = ['IT und Datenschutz', 'Personal Organization und Finanzen', 'Technischer Bereich', None]
TEAMS = ['Software Development', 'Infrastructure', 'Finance', 'HR', 'Operations', None]

TITLES_BASE = [
    'Software Lizenz', 'Cloud Hosting', 'Hardware Wartung', 'IT Support',
    'Büromietvertrag', 'Fahrzeugleasing', 'Marketingdienstleistung',
    'Reinigungsservice', 'Sicherheitsdienst', 'Beratungsvertrag',
    'Versicherungspolice', 'Telekommunikation', 'Energieversorgung',
    'Wasserversorgung', 'Abfallentsorgung', 'Gebäudemanagement'
]

print("📝 Criando 200 contratos de teste...")

for i in range(1, 201):
    # Dados básicos
    title = f"{random.choice(TITLES_BASE)} #{i:03d}"
    company = random.choice(COMPANIES)
    contract_type = random.choice(TYPES)
    status = random.choice(STATUSES)
    
    # Valores financeiros
    value = round(random.uniform(500, 50000), 2)
    currency = 'EUR'
    
    # Datas
    start_date = datetime.now() - timedelta(days=random.randint(0, 1095))  # Até 3 anos atrás
    duration_days = random.randint(90, 1095)  # 3 meses a 3 anos
    end_date = start_date + timedelta(days=duration_days)
    renewal_date = end_date - timedelta(days=30) if random.random() > 0.3 else None
    
    # Cliente
    client_name = company
    client_document = f"DE{random.randint(100000000, 999999999)}"
    client_address = f"{random.choice(['Hauptstraße', 'Bahnhofstraße', 'Gartenstraße'])} {random.randint(1, 100)}, {random.randint(10000, 99999)} {random.choice(['Berlin', 'München', 'Hamburg', 'Köln', 'Frankfurt'])}"
    client_email = f"kontakt@{company.lower().replace(' ', '').replace('.', '')}.de"
    client_phone = f"+49 {random.randint(100, 999)} {random.randint(1000000, 9999999)}"
    
    # Termos e notas
    description = f"Vertrag für {title} mit {company}. Laufzeit: {duration_days} Tage. Wert: €{value:,.2f}"
    terms_and_conditions = f"Standard AGB gemäß deutschem Recht. Kündigungsfrist: 3 Monate. Zahlungsziel: 14 Tage."
    notes = f"Erstellt am {datetime.now().strftime('%d.%m.%Y')} als Testdaten. Vertragsnummer: TEST-{i:03d}"
    
    # Organização
    department = random.choice(DEPARTMENTS)
    team = random.choice(TEAMS)
    responsible_user_id = random.randint(1, 7)  # IDs de usuários existentes
    created_by = random.randint(1, 7)
    
    # Campos novos
    company_name = company
    legal_form = random.choice(LEGAL_FORMS)
    payment_frequency = random.choice(PAYMENT_FREQUENCIES)
    payment_custom_years = random.randint(2, 10) if payment_frequency == 'alle_x_jahre' else None
    
    # PDF (simulado)
    original_pdf_filename = f"vertrag_{i:03d}.pdf"
    original_pdf_path = f"/uploads/contracts/temp/{original_pdf_filename}"
    
    # Timestamps
    created_at = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d %H:%M:%S')
    updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    uploaded_at = created_at
    
    # Insert
    cursor.execute("""
        INSERT INTO contracts (
            title, description, contract_type, status, value, currency,
            start_date, end_date, renewal_date,
            client_name, client_document, client_address, client_email, client_phone,
            terms_and_conditions, notes,
            created_by, created_at, updated_at,
            original_pdf_path, original_pdf_filename, uploaded_at,
            department, team, responsible_user_id,
            company_name, legal_form,
            payment_frequency, payment_custom_years
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title, description, contract_type, status, value, currency,
        start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), 
        renewal_date.strftime('%Y-%m-%d') if renewal_date else None,
        client_name, client_document, client_address, client_email, client_phone,
        terms_and_conditions, notes,
        created_by, created_at, updated_at,
        original_pdf_path, original_pdf_filename, uploaded_at,
        department, team, responsible_user_id,
        company_name, legal_form,
        payment_frequency, payment_custom_years
    ))
    
    if i % 20 == 0:
        print(f"   ✅ {i}/200 contratos criados...")

conn.commit()

# Verificar resultado
cursor.execute("SELECT COUNT(*) FROM contracts")
total = cursor.fetchone()[0]

cursor.execute("SELECT status, COUNT(*) FROM contracts GROUP BY status")
status_counts = cursor.fetchall()

cursor.execute("SELECT contract_type, COUNT(*) FROM contracts GROUP BY contract_type")
type_counts = cursor.fetchall()

cursor.execute("SELECT payment_frequency, COUNT(*) FROM contracts WHERE payment_frequency IS NOT NULL GROUP BY payment_frequency")
payment_counts = cursor.fetchall()

conn.close()

print(f"\n✅ Criação completa!")
print(f"📊 Total de contratos: {total}")
print(f"\n📋 Por Status:")
for status, count in status_counts:
    print(f"   {status}: {count}")
print(f"\n🏷️  Por Tipo:")
for ctype, count in type_counts:
    print(f"   {ctype}: {count}")
print(f"\n💰 Por Frequência de Pagamento:")
for freq, count in payment_counts:
    print(f"   {freq}: {count}")
print(f"\n🎉 Todos os contratos têm TODOS os campos preenchidos!")
