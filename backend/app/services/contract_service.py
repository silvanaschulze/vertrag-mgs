"""
Vertragsdienstleistungen für das Vertragsverwaltungssystem
Dieses Modul enthält die Geschäftslogik für Vertragsoperationen.
Es fungiert als Vermittler zwischen den Routers (API-Endpunkte) und den Models (Datenbank).

"""
from datetime import date, datetime, timedelta 
from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc, asc
#schemas models
from ..models.contract import Contract, ContractStatus, ContractType, get_contract_by_id, get_active_contracts, get_expired_contracts
from ..schemas.contract import (
     ContractCreate, 
     ContractUpdate, 
     ContractResponse, 
     ContractListResponse, 
     ContractInDB,
     ContractStats,
     ContractListResponse
)

class ContractService:
    """
    Hauptfunktionen des Vertragsoperation
    """
def __init__(self, db: Session):
    """Initialisiert den Dienst mit einer Datenbanksitzung.
     Args:
         db (Session): SQLAlchemy-sitzung für die Datenbankinteraktion.
     """
    self.db = db
 
def create_contract(self, contract_data: ContractCreate, created_by: int) -> ContractResponse:
    #Geschäftsvalidierung
    if contract_data.end_date is not None and contract_data.end_date <= contract_data.start_date:
        raise ValueError("Enddatum muss nach dem Startdatum liegen.")
    
    db_contract = Contract(
        title=contract_data.title,
        description=contract_data.description,
        contract_type=contract_data.contract_type,
        status=contract_data.status or ContractStatus.DRAFT,
        value=contract_data.value,
        currency=contract_data.currency,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        renewal_date=contract_data.renewal_date,
        client_name=contract_data.client_name,
        client_document=contract_data.client_document,
        client_email=contract_data.client_email,
        client_phone=contract_data.client_phone,
        client_address=contract_data.client_address,
        terms_and_conditions=contract_data.terms_and_conditions,
        notes=contract_data.notes,
        notes=contract_data.notes,
        created_by=created_by
    )
    self.db.add(db_contract)
    self.db.commit()
    self.db.refresh(db_contract)
    return ContractResponse.model_validate(db_contract)

def get_contract(self, contract_id: int) -> Optional[ContractResponse]:
    db_contract = get_contract_by_id(self.db, contract_id)
    if db_contract:
        return ContractResponse.model_validate(db_contract)
    return None

def update_contract(self, contract_id: int, update_data: ContractUpdate) -> Optional[ContractResponse]:
    
    #Bestehenden Vertrag suchen
    db_contract = get_contract_by_id(self.db, contract_id)
    if not db_contract:
        return None
    
    #Nur bereits gesetzte Felder aktualisieren
    update_data_dict = update_data.model_dump(exclude_unset=True)

    #Geschäftsvalidierung
    if 'end_date' in update_data_dict and 'start_date' in update_data_dict:
        if update_data_dict['end_date'] <= update_data_dict['start_date']:
            raise ValueError("Enddatum muss nach dem Startdatum liegen.")
    elif 'end_date' in update_data_dict and update_data_dict['end_date'] <= db_contract.start_date:
        raise ValueError("Enddatum muss nach dem Startdatum liegen.")
    elif 'start_date' in update_data_dict and db_contract.end_date and update_data_dict['start_date'] >= db_contract.end_date:
        raise ValueError("Startdatum muss vor dem Endungsdatum liegen.")
    
    #Aktualisierungen anwenden
    for key, value in update_data_dict.items():
        setattr(db_contract, key, value)

    #In die Datenbank speichern
    self.db.commit()
    self.db.refresh(db_contract)
    return ContractResponse.model_validate(db_contract) 

def list_contracts(self, skip: int = 0, limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> ContractListResponse:
    query = self.db.query(Contract)
    
    #Filter anwenden
    if filters:
        for attr, value in filters.items():
            if hasattr(Contract, attr):
                query = query.filter(getattr(Contract, attr) == value)
    
    total = query.count()

    #Paginierung und Sortierung anwenden
    query = query.order_by(desc(Contract.created_at))
    contracts = query.offset(skip).limit(limit).all()
    contract_list = [ContractResponse.model_validate(c) for c in contracts]
    current_page = (skip // limit) + 1 if limit else 1
    
    return ContractListResponse(total=total, contracts=contract_list, page=current_page, size=len(contract_list))   
    
def get_contract_stats(self) -> ContractStats:
    total_contracts = self.db.query(func.count(Contract.id)).scalar()
    active_contracts = self.db.query(func.count(Contract.id)).filter(Contract.status == ContractStatus.ACTIVE).scalar()
    expired_contracts = self.db.query(func.count(Contract.id)).filter(Contract.status == ContractStatus.EXPIRED).scalar()
    draft_contracts = self.db.query(func.count(Contract.id)).filter(Contract.status == ContractStatus.DRAFT).scalar()
    total_value_result = self.db.query(func.sum(Contract.value)).filter(Contract.value.isnot(None)).scalar()
    total_value = total_value_result or Decimal('0')
    
    return ContractStats(
        total_contracts=total_contracts,
        active_contracts=active_contracts,
        expired_contracts=expired_contracts,
        draft_contracts=draft_contracts,
        total_value=total_value,
        currency="EUR"
    )

def get_active_contracts_service(self) -> List[ContractResponse]:
    active_contracts = get_active_contracts(self.db)
    return [ContractResponse.model_validate(c) for c in active_contracts]      

def get_expired_contracts_service(self) -> List[ContractResponse]:
    expired_contracts = get_expired_contracts(self.db)
    return [ContractResponse.model_validate(c) for c in expired_contracts]  

def get_contracts_expiring_within(self, days: int) -> List[ContractResponse]:
    target_date = date.today() + timedelta(days=days)
    contracts = self.db.query(Contract).filter(
        and_(
            Contract.end_date.isnot(None),
            Contract.end_date <= target_date,
            Contract.status == ContractStatus.ACTIVE
        )
    ).all()
    return [ContractResponse.model_validate(c) for c in contracts]      

def get_contracts_by_client(self, client_name: str) -> List[ContractResponse]:
    contracts = self.db.query(Contract).filter(
        Contract.client_name.ilike(f"%{client_name}%")
    ).all()
    return [ContractResponse.model_validate(c) for c in contracts]  

def get_contracts_by_type(self, contract_type: ContractType) -> List[ContractResponse]:
    contracts = self.db.query(Contract).filter(
        Contract.contract_type == contract_type
    ).all()
    return [ContractResponse.model_validate(c) for c in contracts]

def search_contracts(self, query_str: str) -> List[ContractResponse]:
    search_pattern = f"%{query_str}%"
    contracts = self.db.query(Contract).filter(
        or_(
            Contract.title.ilike(search_pattern),
            Contract.description.ilike(search_pattern),
            Contract.client_name.ilike(search_pattern),
            Contract.client_email.ilike(search_pattern),
            Contract.client_phone.ilike(search_pattern),
            Contract.client_address.ilike(search_pattern),
            Contract.terms_and_conditions.ilike(search_pattern),
            Contract.notes.ilike(search_pattern)
        )
    ).all()
    return [ContractResponse.model_validate(c) for c in contracts]      

def bulk_update_contract_status(self, contract_ids: List[int], new_status: ContractStatus) -> int:
    update_count = self.db.query(Contract).filter(
        Contract.id.in_(contract_ids)
    ).update(
        {Contract.status: new_status, Contract.updated_at: datetime.now(datetime.timezone.utc)},
        synchronize_session=False
    )
    self.db.commit()
    return update_count 

def bulk_delete_contracts(self, contract_ids: List[int]) -> int:
    delete_count = self.db.query(Contract).filter(
        Contract.id.in_(contract_ids)
    ).delete(synchronize_session=False)
    self.db.commit()
    return delete_count     

def get_contracts_nearing_renewal(self, days: int) -> List[ContractResponse]:
    target_date = date.today() + timedelta(days=days)
    contracts = self.db.query(Contract).filter(
        and_(
            Contract.renewal_date.isnot(None),
            Contract.renewal_date <= target_date,
            Contract.status == ContractStatus.ACTIVE
        )
    ).all()
    return [ContractResponse.model_validate(c) for c in contracts]  

def get_high_value_contracts(self, min_value: Decimal) -> List[ContractResponse]:
    contracts = self.db.query(Contract).filter(
        and_(
            Contract.value.isnot(None),
            Contract.value >= min_value
        )
    ).all()
    return [ContractResponse.model_validate(c) for c in contracts]  

def get_recently_updated_contracts(self, days: int) -> List[ContractResponse]:
    target_datetime = datetime.utcnow() - timedelta(days=days)
    contracts = self.db.query(Contract).filter(
        Contract.updated_at.isnot(None),
        Contract.updated_at >= target_datetime
    ).all()
    return [ContractResponse.model_validate(c) for c in contracts]  

def get_contracts_created_by_user(self, user_id: int) -> List[ContractResponse]:
    contracts = self.db.query(Contract).filter(
        Contract.created_by == user_id
    ).all()
    return [ContractResponse.model_validate(c) for c in contracts]  


def delete_contract(self, contract_id: int) -> bool:
    db_contract = get_contract_by_id(self.db, contract_id)
    if not db_contract:
        return False
    self.db.delete(db_contract)
    self.db.commit()
    return True 

     
