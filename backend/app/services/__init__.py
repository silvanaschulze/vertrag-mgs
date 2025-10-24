"""Service package with lazy factories to avoid importing heavy dependencies at package import time."""

def get_user_service(*args, **kwargs):
    """Import and return the UserService class lazily."""
    from .user_service import UserService
    return UserService(*args, **kwargs)


def get_contract_service(*args, **kwargs):
    """Import and return the ContractService class lazily."""
    from .contract_service import ContractService
    return ContractService(*args, **kwargs)


def get_pdf_reader_service(*args, **kwargs):
    """Import and return the PDFReaderService class lazily."""
    from .pdf_reader import PDFReaderService
    return PDFReaderService(*args, **kwargs)


__all__ = [
    "get_user_service",
    "get_contract_service",
    "get_pdf_reader_service",
]
