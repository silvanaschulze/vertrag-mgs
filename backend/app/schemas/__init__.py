"""
Schemas package for Contract Management System

This module contains all Pydantic schemas for data validation and serialization.
Schemas define the structure of data that can be sent to and received from the API.
"""

# Import all schemas here for easy access
from .user import UserCreate, UserUpdate, UserResponse, UserInDB
from .contract import ContractCreate, ContractUpdate, ContractResponse, ContractInDB
from .auth import Token, UserLogin, UserRegister

# Export all schemas
__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate", 
    "UserResponse",
    "UserInDB",
    
    # Contract schemas
    "ContractCreate",
    "ContractUpdate",
    "ContractResponse", 
    "ContractInDB",
    
    # Auth schemas
    "Token",
    "UserLogin",
    "UserRegister"
]


