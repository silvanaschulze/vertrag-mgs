"""
 Sicherheits-Utilities 
Passwort-Hashing und Verifizierungsfunktionen

"""

from passlib.context import CryptContext

# Kontext für Passwort-Hashing 
# Kontext für Passwort-Hashing 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Passwort mit bcrypt hashen
 
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    
    return pwd_context.verify(plain_password, hashed_password)
