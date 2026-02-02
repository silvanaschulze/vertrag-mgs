import sqlite3

DB_PATH = '/home/sschulze/projects/vertrag-mgs/contracts.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print(f"{'ID':<5} {'Username':<20} {'Name':<30} {'Team':<20}")
print('-' * 75)

for row in cursor.execute("SELECT id, username, name, team FROM users LIMIT 20;"):
    print(f"{row[0]:<5} {str(row[1]):<20} {str(row[2]):<30} {str(row[3]):<20}")

conn.close()
