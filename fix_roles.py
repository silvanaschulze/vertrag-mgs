#!/usr/bin/env python3
"""Fix user roles to match enum values"""
import sqlite3

conn = sqlite3.connect('contracts.db')
cursor = conn.cursor()

# Atualizar TODOS os roles para MAIÚSCULAS
updates = [
    ('STAFF', 'staff'),
    ('SYSTEM_ADMIN', 'system_admin'), 
    ('DIRECTOR', 'director'),
    ('DEPARTMENT_USER', 'department_user'),
    ('DEPARTMENT_ADM', 'department_adm'),
    ('TEAM_LEAD', 'team_lead'),
    ('READ_ONLY', 'read_only'),
]

print("Atualizando roles...")
total = 0
for correct_value, wrong_value in updates:
    cursor.execute('UPDATE users SET role = ? WHERE role = ?;', (correct_value, wrong_value))
    if cursor.rowcount > 0:
        print(f'  {wrong_value} → {correct_value}: {cursor.rowcount} registros')
        total += cursor.rowcount

print(f'\nTotal: {total} registros atualizados')

# Verificar
result = cursor.execute('SELECT DISTINCT role FROM users;').fetchall()
print('\nRoles finais:')
for r in result:
    print(f'  - {r[0]}')

# Verificar todos os usuários
result = cursor.execute('SELECT id, email, role FROM users;').fetchall()
print('\nTodos os usuários:')
for r in result:
    print(f'  ID={r[0]}, Email={r[1]}, Role={r[2]}')

conn.commit()
conn.close()
print('\n✅ Concluído!')
