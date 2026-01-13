"""Script para copiar usuários do backend/contracts.db para contracts.db"""
import sqlite3

# Conectar aos dois bancos
conn_backend = sqlite3.connect('backend/contracts.db')
conn_raiz = sqlite3.connect('contracts.db')

cursor_backend = conn_backend.cursor()
cursor_raiz = conn_raiz.cursor()

# Buscar todos os usuários do backend
cursor_backend.execute('SELECT * FROM users')
colunas = [desc[0] for desc in cursor_backend.description]
usuarios_backend = cursor_backend.fetchall()

print(f"📊 Encontrados {len(usuarios_backend)} usuários no backend/contracts.db")

# Verificar quais já existem no banco da raiz
cursor_raiz.execute('SELECT email FROM users')
emails_existentes = {row[0] for row in cursor_raiz.fetchall()}

print(f"📊 Existem {len(emails_existentes)} usuários no contracts.db (raiz)")

# Copiar usuários que não existem
usuarios_copiados = 0
usuarios_atualizados = 0

for usuario in usuarios_backend:
    user_dict = dict(zip(colunas, usuario))
    email = user_dict['email']
    
    if email not in emails_existentes:
        # Inserir novo usuário
        placeholders = ', '.join(['?' for _ in colunas])
        query = f"INSERT INTO users ({', '.join(colunas)}) VALUES ({placeholders})"
        cursor_raiz.execute(query, usuario)
        usuarios_copiados += 1
        print(f"✅ Copiado: {email} ({user_dict['name']}) - Role: {user_dict['role']}")
    else:
        # Atualizar usuário existente (manter password_hash atualizado)
        cursor_raiz.execute('''
            UPDATE users 
            SET password_hash = ?, role = ?, access_level = ?, name = ?, is_active = ?
            WHERE email = ?
        ''', (user_dict['password_hash'], user_dict['role'], user_dict['access_level'], 
              user_dict['name'], user_dict['is_active'], email))
        usuarios_atualizados += 1
        print(f"🔄 Atualizado: {email} ({user_dict['name']}) - Role: {user_dict['role']}")

conn_raiz.commit()

print("\n" + "="*60)
print(f"✅ Processo concluído!")
print(f"   Usuários copiados: {usuarios_copiados}")
print(f"   Usuários atualizados: {usuarios_atualizados}")
print("="*60)

conn_backend.close()
conn_raiz.close()
