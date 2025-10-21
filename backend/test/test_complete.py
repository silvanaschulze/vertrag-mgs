# test_complete.py
import sys
import traceback

def test_imports():
    """Testa todos os imports principais"""
    try:
        # Testar routers
        from app.routers import auth_router, contracts_router, users_router
        print("✅ Routers: OK")
        
        # Testar services
        from app.services import UserService, ContractService
        print("✅ Services: OK")
        
        # Testar utils
        from app.utils.security import get_password_hash, verify_password
        print("✅ Utils: OK")
        
        # Testar models
        from app.models.user import User
        from app.models.contract import Contract
        print("✅ Models: OK")
        
        # Testar schemas
        from app.schemas.user import UserCreate
        from app.schemas.contract import ContractCreate
        print("✅ Schemas: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        traceback.print_exc()
        return False

def test_functions():
    """Testa funções específicas"""
    try:
        from app.utils.security import get_password_hash, verify_password
        
        # Testar hash de senha
        password = "teste123"
        hashed = get_password_hash(password)
        is_valid = verify_password(password, hashed)
        
        if is_valid:
            print("✅ Funções de hash: OK")
            return True
        else:
            print("❌ Funções de hash: FALHARAM")
            return False
            
    except Exception as e:
        print(f"❌ Erro nas funções: {e}")
        return False

if __name__ == "__main__":
    print("�� INICIANDO TESTES COMPLETOS...")
    print("=" * 50)
    
    imports_ok = test_imports()
    functions_ok = test_functions()
    
    print("=" * 50)
    if imports_ok and functions_ok:
        print("🎉 TODOS OS TESTES PASSARAM!")
        sys.exit(0)
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        sys.exit(1)