"""
Vertragsdienstleistungen für das Vertragsverwaltungssystem
Dieses Modul enthält die Geschäftslogik für Vertragsoperationen.
Es fungiert als Vermittler zwischen den Routers (API-Endpunkte) und den Models (Datenbank).

"""
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any, cast
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, or_, desc, asc, select, and_
#schemas models
from ..models.contract import Contract, ContractStatus, ContractType
from ..schemas.contract import (
     ContractCreate, 
     ContractUpdate, 
     ContractResponse, 
     ContractListResponse, 
     ContractInDB,
     ContractStats
)

class ContractService:
    """
    Hauptfunktionen des Vertragsoperation
    Funções principais das operações de contrato
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialisiert den Dienst mit einer Datenbanksitzung.
        Inicializa o serviço com uma sessão de banco de dados.
        
        Args / Argumentos:
            db (AsyncSession): SQLAlchemy-sitzung für die Datenbankinteraktion / Sessão SQLAlchemy para interação com banco de dados
        """
        self.db = db
    
    async def create_contract(self, contract_data: ContractCreate, created_by: int) -> ContractResponse:
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
        await self.db.commit()
        await self.db.refresh(db_contract)
        return ContractResponse.model_validate(db_contract)

    async def get_contract(self, contract_id: int) -> Optional[ContractResponse]:
        """
        Vertrag nach ID abrufen / Recuperar contrato por ID
        
        Args / Argumentos:
            contract_id (int): Vertrags-ID / ID do contrato
            
        Returns / Retorna:
            Optional[ContractResponse]: Vertrag oder None / Contrato ou None
        """
        result = await self.db.execute(
            select(Contract).where(Contract.id == contract_id)
        )
        db_contract = result.scalar_one_or_none()
        if db_contract:
            return ContractResponse.model_validate(db_contract)
        return None

    async def update_contract(self, contract_id: int, update_data: ContractUpdate) -> Optional[ContractResponse]:
        """
        Vertrag aktualisieren / Atualizar contrato
        
        Args / Argumentos:
            contract_id (int): Vertrags-ID / ID do contrato
            update_data (ContractUpdate): Aktualisierte Daten / Dados atualizados
            
        Returns / Retorna:
            Optional[ContractResponse]: Aktualisierter Vertrag oder None / Contrato atualizado ou None
        """
        # Bestehenden Vertrag suchen / Buscar contrato existente
        result = await self.db.execute(
            select(Contract).where(Contract.id == contract_id)
        )
        db_contract = result.scalar_one_or_none()
        if not db_contract:
            return None
        
        # Nur bereits gesetzte Felder aktualisieren / Atualizar apenas campos definidos
        update_data_dict = update_data.model_dump(exclude_unset=True)

        # Geschäftsvalidierung / Validação de negócio
        if 'end_date' in update_data_dict and 'start_date' in update_data_dict:
            if update_data_dict['end_date'] <= update_data_dict['start_date']:
                raise ValueError("Enddatum muss nach dem Startdatum liegen. / Data de fim deve ser posterior à data de início.")
        elif 'end_date' in update_data_dict and update_data_dict['end_date'] <= cast(date, db_contract.start_date):
            raise ValueError("Enddatum muss nach dem Startdatum liegen. / Data de fim deve ser posterior à data de início.")
        elif 'start_date' in update_data_dict and db_contract.end_date is not None and update_data_dict['start_date'] >= cast(date, db_contract.end_date):
            raise ValueError("Startdatum muss vor dem Endungsdatum liegen. / Data de início deve ser anterior à data de fim.")
        
        # Aktualisierungen anwenden / Aplicar atualizações
        for key, value in update_data_dict.items():
            setattr(db_contract, key, value)

        # In die Datenbank speichern / Salvar no banco de dados
        await self.db.commit()
        await self.db.refresh(db_contract)
        return ContractResponse.model_validate(db_contract) 

    async def list_contracts(self, skip: int = 0, limit: int = 10, filters: Optional[Dict[str, Any]] = None, search: Optional[str] = None, sort_by: str = "created_at", sort_order: str = "desc") -> ContractListResponse:
        """
        Verträge auflisten / Listar contratos
        
        Args / Argumentos:
            skip (int): Anzahl zu überspringender Einträge / Número de entradas a pular
            limit (int): Maximale Anzahl von Einträgen / Número máximo de entradas
            filters (Optional[Dict[str, Any]]): Filterkriterien / Critérios de filtro
            
        Returns / Retorna:
            ContractListResponse: Liste der Verträge / Lista de contratos
        """
        # Normalize and cap skip/limit to avoid massive queries or negative values
        try:
            skip = int(skip)
        except Exception:
            skip = 0
        skip = max(0, skip)

        try:
            limit = int(limit)
        except Exception:
            limit = 10
        if limit <= 0:
            limit = 10
        max_limit = 100
        limit = min(limit, max_limit)

        # Base query / Query base
        query = select(Contract)
        
        # Filter anwenden / Aplicar filtros
        if filters:
            for attr, value in filters.items():
                if hasattr(Contract, attr) and value is not None:
                    query = query.where(getattr(Contract, attr) == value)
        
         # Search anwenden / Aplicar busca
        if search:
            search_filter = or_(
                Contract.title.ilike(f"%{search}%"),
                Contract.description.ilike(f"%{search}%"),
                Contract.client_name.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        

        # Total count / Contagem total
        count_query = select(func.count(Contract.id))
        if filters:
            for attr, value in filters.items():
                if hasattr(Contract, attr) and value is not None:
                    count_query = count_query.where(getattr(Contract, attr) == value)
        # Search filter also apply to count / Aplicar filtro de busca também na contagem
        if search:
            search_filter = or_(
                Contract.title.ilike(f"%{search}%"),
                Contract.description.ilike(f"%{search}%"),
                Contract.client_name.ilike(f"%{search}%")
            )
            count_query = count_query.where(search_filter)

        total_result = await self.db.execute(count_query)
        total = int(total_result.scalar() or 0)

        # Paginierung und Sortierung anwenden / Aplicar paginação e ordenação
                # Sortierung anwenden / Aplicar ordenação
        sort_column = getattr(Contract, sort_by, Contract.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
        
        # Paginierung anwenden / Aplicar paginação
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        contracts = result.scalars().all()
        contract_list = [ContractResponse.model_validate(c) for c in contracts]
        current_page = (skip // limit) + 1 if limit else 1
        
        return ContractListResponse(total=total, contracts=contract_list, page=current_page, per_page=limit)  






    async def delete_contract(self, contract_id: int) -> bool:
        """
        Vertrag löschen / Deletar contrato
        
        Args / Argumentos:
            contract_id (int): Vertrags-ID / ID do contrato
            
        Returns / Retorna:
            bool: Erfolg der Löschung / Sucesso da exclusão
        """
        result = await self.db.execute(
            select(Contract).where(Contract.id == contract_id)
        )
        db_contract = result.scalar_one_or_none()
        if not db_contract:
            return False
        await self.db.delete(db_contract)
        await self.db.commit()
        return True 

    async def get_contract_stats(self) -> ContractStats:
        """
        Vertragsstatistiken abrufen / Obter estatísticas dos contratos
        
        Returns / Retorna:
            ContractStats: Statistiken / Estatísticas
        """
        # Total contracts / Total de contratos
        total_result = await self.db.execute(select(func.count(Contract.id)))
        total_contracts = int(total_result.scalar() or 0)

        # Active contracts / Contratos ativos
        active_result = await self.db.execute(
            select(func.count(Contract.id)).where(Contract.status == ContractStatus.ACTIVE) # type: ignore
        )
        active_contracts = int(active_result.scalar() or 0)

        # Expired contracts / Contratos expirados
        expired_result = await self.db.execute(
            select(func.count(Contract.id)).where(Contract.status == ContractStatus.EXPIRED) # type: ignore
        )
        expired_contracts = int(expired_result.scalar() or 0)

        # Draft contracts / Contratos em rascunho
        draft_result = await self.db.execute(
            select(func.count(Contract.id)).where(Contract.status == ContractStatus.DRAFT) # type: ignore
        )
        draft_contracts = int(draft_result.scalar() or 0)
        
        # Total value / Valor total
        value_result = await self.db.execute(
            select(func.sum(Contract.value)).where(Contract.value.is_not(None))
        )
        total_value = value_result.scalar() or Decimal('0')
        
        return ContractStats(
            total_contracts=total_contracts,
            active_contracts=active_contracts,
            expired_contracts=expired_contracts,
            draft_contracts=draft_contracts,
            total_value=total_value,
            currency="EUR"
        )

    async def search_contracts(self, query: str, skip: int = 0, limit: int = 10) -> ContractListResponse:
        """
        Verträge suchen / Buscar contratos
        
        Args / Argumentos:
            query (str): Suchbegriff / Termo de busca
            skip (int): Anzahl zu überspringen / Número para pular
            limit (int): Maximale Anzahl / Número máximo
            
        Returns / Retorna:
            ContractListResponse: Suchergebnisse / Resultados da busca
        """
        search_filter = or_(
            Contract.title.ilike(f"%{query}%"),
            Contract.description.ilike(f"%{query}%"),
            Contract.client_name.ilike(f"%{query}%")
        )
        
        # Total count / Contagem total
        count_query = select(func.count(Contract.id)).where(search_filter)
        total_result = await self.db.execute(count_query)
        total = int(total_result.scalar() or 0)
        
        # Search results / Resultados da busca
        query_obj = select(Contract).where(search_filter).order_by(desc(Contract.created_at)).offset(skip).limit(limit)
        result = await self.db.execute(query_obj)
        contracts = result.scalars().all()
        current_page = (skip // limit) + 1 if limit else 1
        return ContractListResponse(
            contracts=[ContractResponse.model_validate(c) for c in contracts],
            total=total,
            page=current_page,
            per_page=limit
        )

    async def get_active_contracts(self, skip: int = 0, limit: int = 10) -> ContractListResponse:
        """
        Aktive Verträge abrufen / Obter contratos ativos
        
        Args / Argumentos:
            skip (int): Anzahl zu überspringen / Número para pular
            limit (int): Maximale Anzahl / Número máximo
            
        Returns / Retorna:
            ContractListResponse: Aktive Verträge / Contratos ativos
        """
        return await self.list_contracts(skip=skip, limit=limit, filters={"status": ContractStatus.ACTIVE})

    async def get_contracts_expiring_within(self, days: int, skip: int = 0, limit: int = 10) -> ContractListResponse:
        """
        Verträge abrufen, die in X Tagen ablaufen / Obter contratos que expiram em X dias
        
        Args / Argumentos:
            days (int): Anzahl Tage / Número de dias
            skip (int): Anzahl zu überspringen / Número para pular
            limit (int): Maximale Anzahl / Número máximo
            
        Returns / Retorna:
            ContractListResponse: Verträge / Contratos
        """
        from datetime import datetime, timedelta
        target_date = datetime.now() + timedelta(days=days)
        
        # Total count / Contagem total
        count_query = select(func.count(Contract.id)).where(
            and_(
                Contract.end_date <= target_date,  # type: ignore
                Contract.status == ContractStatus.ACTIVE # type: ignore
            )
        )
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Contracts / Contratos
        query = select(Contract).where(
            and_(
                Contract.end_date <= target_date,   # type: ignore
                Contract.status == ContractStatus.ACTIVE  # type: ignore
            )
        ).order_by(asc(Contract.end_date)).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        contracts = result.scalars().all()
        
        current_page = (skip // limit) + 1 if limit else 1
        return ContractListResponse(
            contracts=[ContractResponse.model_validate(c) for c in contracts],
            total=total,
            page=current_page,
            per_page=limit
        )

    async def get_expired_contracts(self, skip: int = 0, limit: int = 10) -> ContractListResponse:
        """
        Abgelaufene Verträge abrufen / Obter contratos expirados
        
        Args / Argumentos:
            skip (int): Anzahl zu überspringen / Número para pular
            limit (int): Maximale Anzahl / Número máximo
            
        Returns / Retorna:
            ContractListResponse: Abgelaufene Verträge / Contratos expirados
        """
        return await self.list_contracts(skip=skip, limit=limit, filters={"status": ContractStatus.EXPIRED})

    async def get_contracts_by_client(self, client_name: str, skip: int = 0, limit: int = 10) -> ContractListResponse:
        """
        Verträge nach Kunde abrufen / Obter contratos por cliente
        
        Args / Argumentos:
            client_name (str): Kundenname / Nome do cliente
            skip (int): Anzahl zu überspringen / Número para pular
            limit (int): Maximale Anzahl / Número máximo
            
        Returns / Retorna:
            ContractListResponse: Verträge des Kunden / Contratos do cliente
        """
        return await self.list_contracts(skip=skip, limit=limit, filters={"client_name": client_name})

     
