"""
Vertragsdienstleistungen für das Vertragsverwaltungssystem
Dieses Modul enthält die Geschäftslogik für Vertragsoperationen.
Es fungiert als Vermittler zwischen den Routers (API-Endpunkte) und den Models (Datenbank).

"""
from datetime import date, datetime, timedelta, UTC
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
    Funções principais das operações de contrato
    """
    
    def __init__(self, db: Session):
        """
        Initialisiert den Dienst mit einer Datenbanksitzung.
        Inicializa o serviço com uma sessão de banco de dados.
        
        Args / Argumentos:
            db (Session): SQLAlchemy-sitzung für die Datenbankinteraktion / Sessão SQLAlchemy para interação com banco de dados
        """
        self.db = db
    
    def create_contract(self, contract_data: ContractCreate, created_by: int) -> ContractResponse:
        """
        Erstellt einen neuen Vertrag / Cria um novo contrato
        
        Args / Argumentos:
            contract_data (ContractCreate): Vertragsdaten / Dados do contrato
            created_by (int): Benutzer-ID, die den Vertrag erstellt hat / ID do usuário que criou o contrato
            
        Returns / Retorna:
            ContractResponse: Erstellter Vertrag / Contrato criado
        """
        # Geschäftsvalidierung / Validação de negócio
        if contract_data.end_date is not None and contract_data.end_date <= contract_data.start_date:
            raise ValueError("Enddatum muss nach dem Startdatum liegen. / Data de fim deve ser posterior à data de início.")
        
        # Vertrag erstellen / Criar contrato
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
            created_by=created_by
        )
        
        # In Datenbank speichern / Salvar no banco de dados
        self.db.add(db_contract)
        self.db.commit()
        self.db.refresh(db_contract)
        return ContractResponse.model_validate(db_contract)

    def get_contract(self, contract_id: int) -> Optional[ContractResponse]:
        """
        Vertrag nach ID abrufen / Recuperar contrato por ID
        
        Args / Argumentos:
            contract_id (int): Vertrags-ID / ID do contrato
            
        Returns / Retorna:
            Optional[ContractResponse]: Vertrag oder None / Contrato ou None
        """
        db_contract = get_contract_by_id(self.db, contract_id)
        if db_contract:
            return ContractResponse.model_validate(db_contract)
        return None

    def update_contract(self, contract_id: int, update_data: ContractUpdate) -> Optional[ContractResponse]:
        """
        Vertrag aktualisieren / Atualizar contrato
        
        Args / Argumentos:
            contract_id (int): Vertrags-ID / ID do contrato
            update_data (ContractUpdate): Aktualisierte Daten / Dados atualizados
            
        Returns / Retorna:
            Optional[ContractResponse]: Aktualisierter Vertrag oder None / Contrato atualizado ou None
        """
        # Bestehenden Vertrag suchen / Buscar contrato existente
        db_contract = get_contract_by_id(self.db, contract_id)
        if not db_contract:
            return None
        
        # Nur bereits gesetzte Felder aktualisieren / Atualizar apenas campos definidos
        update_data_dict = update_data.model_dump(exclude_unset=True)

        # Geschäftsvalidierung / Validação de negócio
        if 'end_date' in update_data_dict and 'start_date' in update_data_dict:
            if update_data_dict['end_date'] <= update_data_dict['start_date']:
                raise ValueError("Enddatum muss nach dem Startdatum liegen. / Data de fim deve ser posterior à data de início.")
        elif 'end_date' in update_data_dict and update_data_dict['end_date'] <= db_contract.start_date:
            raise ValueError("Enddatum muss nach dem Startdatum liegen. / Data de fim deve ser posterior à data de início.")
        elif 'start_date' in update_data_dict and db_contract.end_date and update_data_dict['start_date'] >= db_contract.end_date:
            raise ValueError("Startdatum muss vor dem Endungsdatum liegen. / Data de início deve ser anterior à data de fim.")
        
        # Aktualisierungen anwenden / Aplicar atualizações
        for key, value in update_data_dict.items():
            setattr(db_contract, key, value)

        # In die Datenbank speichern / Salvar no banco de dados
        self.db.commit()
        self.db.refresh(db_contract)
        return ContractResponse.model_validate(db_contract) 

    def list_contracts(self, skip: int = 0, limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> ContractListResponse:
        """
        Verträge auflisten / Listar contratos
        
        Args / Argumentos:
            skip (int): Anzahl zu überspringender Einträge / Número de entradas a pular
            limit (int): Maximale Anzahl von Einträgen / Número máximo de entradas
            filters (Optional[Dict[str, Any]]): Filterkriterien / Critérios de filtro
            
        Returns / Retorna:
            ContractListResponse: Liste der Verträge / Lista de contratos
        """
        query = self.db.query(Contract)
        
        # Filter anwenden / Aplicar filtros
        if filters:
            for attr, value in filters.items():
                if hasattr(Contract, attr):
                    query = query.filter(getattr(Contract, attr) == value)
        
        total = query.count()

        # Paginierung und Sortierung anwenden / Aplicar paginação e ordenação
        query = query.order_by(desc(Contract.created_at))
        contracts = query.offset(skip).limit(limit).all()
        contract_list = [ContractResponse.model_validate(c) for c in contracts]
        current_page = (skip // limit) + 1 if limit else 1
        
        return ContractListResponse(total=total, contracts=contract_list, page=current_page, per_page=len(contract_list))   
    
    def get_contract_stats(self) -> ContractStats:
        """
        Vertragsstatistiken abrufen / Recuperar estatísticas de contratos
        
        Returns / Retorna:
            ContractStats: Vertragsstatistiken / Estatísticas de contratos
        """
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
        """
        Aktive Verträge abrufen / Recuperar contratos ativos
        
        Returns / Retorna:
            List[ContractResponse]: Liste aktiver Verträge / Lista de contratos ativos
        """
        active_contracts = get_active_contracts(self.db)
        return [ContractResponse.model_validate(c) for c in active_contracts]      

    def get_expired_contracts_service(self) -> List[ContractResponse]:
        """
        Abgelaufene Verträge abrufen / Recuperar contratos expirados
        
        Returns / Retorna:
            List[ContractResponse]: Liste abgelaufener Verträge / Lista de contratos expirados
        """
        expired_contracts = get_expired_contracts(self.db)
        return [ContractResponse.model_validate(c) for c in expired_contracts]  

    def get_contracts_expiring_within(self, days: int) -> List[ContractResponse]:
        """
        Verträge abrufen, die in den nächsten X Tagen ablaufen / Recuperar contratos que vencem nos próximos X dias
        
        Args / Argumentos:
            days (int): Anzahl der Tage / Número de dias
            
        Returns / Retorna:
            List[ContractResponse]: Liste der Verträge / Lista de contratos
        """
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
        """
        Verträge nach Kundenname abrufen / Recuperar contratos por nome do cliente
        
        Args / Argumentos:
            client_name (str): Kundenname / Nome do cliente
            
        Returns / Retorna:
            List[ContractResponse]: Liste der Verträge / Lista de contratos
        """
        contracts = self.db.query(Contract).filter(
            Contract.client_name.ilike(f"%{client_name}%")
        ).all()
        return [ContractResponse.model_validate(c) for c in contracts]  

    def get_contracts_by_type(self, contract_type: ContractType) -> List[ContractResponse]:
        """
        Verträge nach Typ abrufen / Recuperar contratos por tipo
        
        Args / Argumentos:
            contract_type (ContractType): Vertragstyp / Tipo de contrato
            
        Returns / Retorna:
            List[ContractResponse]: Liste der Verträge / Lista de contratos
        """
        contracts = self.db.query(Contract).filter(
            Contract.contract_type == contract_type
        ).all()
        return [ContractResponse.model_validate(c) for c in contracts]

    def search_contracts(self, query_str: str) -> List[ContractResponse]:
        """
        Verträge durchsuchen / Buscar contratos
        
        Args / Argumentos:
            query_str (str): Suchbegriff / Termo de busca
            
        Returns / Retorna:
            List[ContractResponse]: Liste der gefundenen Verträge / Lista de contratos encontrados
        """
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
        """
        Vertragsstatus in Stapel aktualisieren / Atualizar status de contratos em lote
        
        Args / Argumentos:
            contract_ids (List[int]): Liste der Vertrags-IDs / Lista de IDs de contratos
            new_status (ContractStatus): Neuer Status / Novo status
            
        Returns / Retorna:
            int: Anzahl aktualisierter Verträge / Número de contratos atualizados
        """
        update_count = self.db.query(Contract).filter(
            Contract.id.in_(contract_ids)
        ).update(
            {Contract.status: new_status, Contract.updated_at: datetime.now(UTC)},
            synchronize_session=False
        )
        self.db.commit()
        return update_count 

    def bulk_delete_contracts(self, contract_ids: List[int]) -> int:
        """
        Verträge in Stapel löschen / Deletar contratos em lote
        
        Args / Argumentos:
            contract_ids (List[int]): Liste der Vertrags-IDs / Lista de IDs de contratos
            
        Returns / Retorna:
            int: Anzahl gelöschter Verträge / Número de contratos deletados
        """
        delete_count = self.db.query(Contract).filter(
            Contract.id.in_(contract_ids)
        ).delete(synchronize_session=False)
        self.db.commit()
        return delete_count     

    def get_contracts_nearing_renewal(self, days: int) -> List[ContractResponse]:
        """
        Verträge abrufen, die sich der Verlängerung nähern / Recuperar contratos próximos da renovação
        
        Args / Argumentos:
            days (int): Anzahl der Tage / Número de dias
            
        Returns / Retorna:
            List[ContractResponse]: Liste der Verträge / Lista de contratos
        """
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
        """
        Hochwertige Verträge abrufen / Recuperar contratos de alto valor
        
        Args / Argumentos:
            min_value (Decimal): Mindestwert / Valor mínimo
            
        Returns / Retorna:
            List[ContractResponse]: Liste der Verträge / Lista de contratos
        """
        contracts = self.db.query(Contract).filter(
            and_(
                Contract.value.isnot(None),
                Contract.value >= min_value
            )
        ).all()
        return [ContractResponse.model_validate(c) for c in contracts]  

    def get_recently_updated_contracts(self, days: int) -> List[ContractResponse]:
        """
        Kürzlich aktualisierte Verträge abrufen / Recuperar contratos atualizados recentemente
        
        Args / Argumentos:
            days (int): Anzahl der Tage / Número de dias
            
        Returns / Retorna:
            List[ContractResponse]: Liste der Verträge / Lista de contratos
        """
        target_datetime = datetime.now(UTC) - timedelta(days=days)
        contracts = self.db.query(Contract).filter(
            Contract.updated_at.isnot(None),
            Contract.updated_at >= target_datetime
        ).all()
        return [ContractResponse.model_validate(c) for c in contracts]  

    def get_contracts_created_by_user(self, user_id: int) -> List[ContractResponse]:
        """
        Verträge abrufen, die von einem Benutzer erstellt wurden / Recuperar contratos criados por um usuário
        
        Args / Argumentos:
            user_id (int): Benutzer-ID / ID do usuário
            
        Returns / Retorna:
            List[ContractResponse]: Liste der Verträge / Lista de contratos
        """
        contracts = self.db.query(Contract).filter(
            Contract.created_by == user_id
        ).all()
        return [ContractResponse.model_validate(c) for c in contracts]  

    def delete_contract(self, contract_id: int) -> bool:
        """
        Vertrag löschen / Deletar contrato
        
        Args / Argumentos:
            contract_id (int): Vertrags-ID / ID do contrato
            
        Returns / Retorna:
            bool: Erfolg der Löschung / Sucesso da exclusão
        """
        db_contract = get_contract_by_id(self.db, contract_id)
        if not db_contract:
            return False
        self.db.delete(db_contract)
        self.db.commit()
        return True 

     
