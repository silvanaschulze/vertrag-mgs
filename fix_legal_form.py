#!/usr/bin/env python3
"""Fix legal_form values in database to match enum"""
import sqlite3

conn = sqlite3.connect('contracts.db')
cursor = conn.cursor()

# Map database values to correct enum values
# Database has 'other' but enum expects 'sonstiges'
mapping = {
    'other': 'sonstiges'
}

print("Before fix:")
result = cursor.execute('SELECT legal_form, COUNT(*) FROM contracts GROUP BY legal_form').fetchall()
for row in result:
    print(f"  {row[0] if row[0] else 'NULL'}: {row[1]}")

# Apply fixes
for old_val, new_val in mapping.items():
    count = cursor.execute('UPDATE contracts SET legal_form = ? WHERE legal_form = ?', (new_val, old_val)).rowcount
    print(f"\nUpdated {count} contracts: '{old_val}' -> '{new_val}'")

conn.commit()

print("\nAfter fix:")
result = cursor.execute('SELECT legal_form, COUNT(*) FROM contracts GROUP BY legal_form').fetchall()
for row in result:
    print(f"  {row[0] if row[0] else 'NULL'}: {row[1]}")

conn.close()
print("\n✅ Database values fixed!")
