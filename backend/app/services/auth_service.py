"""
Auth service helpers (stub)

Este arquivo fornece funções de autenticação de alto nível usadas pelos routers.
No momento é um stub com documentação e helpers mínimos; implementação completa
deve integrar JWT/token, expiração e políticas de senha.

Funções previstas (stubs):
 - create_access_token(data: dict, expires_delta: Optional[timedelta]) -> str
 - verify_token(token: str) -> dict | None

Manter a API mínima aqui evita alterações na interface com o restante do sistema.
"""

from typing import Optional, Dict, Any
from datetime import timedelta


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
	"""Stub: retornar token de acesso (string vazia por enquanto).

	Implementação futura: gerar JWT assinado com `app.core.config.settings.SECRET_KEY`.
	"""
	# placeholder para integração futura
	return ""


def verify_token(token: str) -> Optional[Dict[str, Any]]:
	"""Stub: valida token e retorna payload ou None se inválido."""
	if not token:
		return None
	# placeholder: decodificar e validar o token
	return None

