"""
Sicherheits-Utilities
Passwort-Hashing und Verifizierungsfunktionen

Usa o módulo `bcrypt` diretamente em vez de passlib para evitar problemas
de compatibilidade no ambiente. API pública mantida:
 - get_password_hash(password: str) -> str
 - verify_password(plain_password: str, hashed_password: str) -> bool
"""

import bcrypt


def get_password_hash(password: str) -> str:
    """Retorna o hash bcrypt (utf-8 string) do password informado."""
    if password is None:
        raise ValueError("password must be provided")
    # bcrypt aceita no máximo 72 bytes; truncar explicitamente para evitar exceções
    pw_bytes = password.encode("utf-8")[:72]
    hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se plain_password corresponde ao hashed_password (bcrypt)."""
    if plain_password is None or hashed_password is None:
        return False
    try:
        pw_bytes = plain_password.encode("utf-8")[:72]
        return bcrypt.checkpw(pw_bytes, hashed_password.encode("utf-8"))
    except Exception:
        return False
