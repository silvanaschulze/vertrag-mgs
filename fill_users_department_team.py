import sqlite3

DB_PATH = '/home/sschulze/projects/vertrag-mgs/contracts.db'

# Correto conforme informado pelo usuário
updates = [
    ("Geschäftsführung", "Informationstechnologie", 1),
    ("Personal Organization und Finazen", "PR", 2),
    ("Technische Bereich", "Finanzen und Rechnungswesen", 3),
    ("IT und Datenschutz", "Informationstechnologie", 4),
    ("IT und Datenschutz", "Informationstechnologie", 5),
    ("Geschäftsführung", "PR", 6),
    ("Personal Organization und Finazen", "Finanzen und Rechnungswesen", 7),
    ("Technische Bereich", "PR", 8),
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

for department, team, user_id in updates:
    cursor.execute("UPDATE users SET department = ?, team = ? WHERE id = ?", (department, team, user_id))

conn.commit()
print("Campos 'department' e 'team' atualizados para os primeiros 8 usuários.")

# Exibir resultado
print(f"{'ID':<5} {'Username':<20} {'Name':<30} {'Department':<35} {'Team':<30}")
print('-' * 120)
for row in cursor.execute("SELECT id, username, name, department, team FROM users LIMIT 10;"):
    print(f"{row[0]:<5} {str(row[1]):<20} {str(row[2]):<30} {str(row[3]):<35} {str(row[4]):<30}")

conn.close()
