import sqlite3

DB_PATH = '/home/sschulze/projects/vertrag-mgs/contracts.db'

updates = [
    ("Equipe Alpha", 1),
    ("Equipe Beta", 2),
    ("Equipe Gamma", 3),
    ("Equipe Alpha", 4),
    ("TI", 5),
    ("Diretoria", 6),
    ("Financeiro", 7),
    ("RH", 8),
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

for team, user_id in updates:
    cursor.execute("UPDATE users SET team = ? WHERE id = ?", (team, user_id))

conn.commit()
print("Campo 'team' atualizado para os primeiros 8 usuários.")

# Exibir resultado
print(f"{'ID':<5} {'Username':<20} {'Name':<30} {'Team':<20}")
print('-' * 75)
for row in cursor.execute("SELECT id, username, name, team FROM users LIMIT 10;"):
    print(f"{row[0]:<5} {str(row[1]):<20} {str(row[2]):<30} {str(row[3]):<20}")

conn.close()
