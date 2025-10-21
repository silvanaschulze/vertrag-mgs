# Criar arquivo test_local.py no diretório backend
# test_local.py
from app.utils.security import get_password_hash, verify_password
from app.models.user import User
from app.models.contract import Contract

# Testar hash de senha
password = "minhasenha123"
hashed = get_password_hash(password)
print(f"Hash gerado: {hashed}")

# Testar verificação de senha
is_valid = verify_password(password, hashed)
print(f"Senha válida: {is_valid}")

# Testar modelos
user = User()
print(f"Modelo User criado: {user}")

contract = Contract()
print(f"Modelo Contract criado: {contract}")

print("✅ Todos os testes passaram!")