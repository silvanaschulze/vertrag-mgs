from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.contract import RentStepCreate, RentStepResponse, RentStepUpdate
from app.services.contract_service import ContractService
from app.core.security import get_current_active_user
from app.core.permissions import require_manager_or_admin
from app.models.user import User


router = APIRouter(
    prefix="/contracts/{contract_id}/rent-steps",
    tags=["rent-steps"],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}}
)


def get_contract_service(db: AsyncSession = Depends(get_db)) -> ContractService:
    return ContractService(db)


@router.get("/", response_model=List[RentStepResponse])
async def list_rent_steps(
    contract_id: int,
    contract_service: ContractService = Depends(get_contract_service),
):
    try:
        return await contract_service.list_rent_steps(contract_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Auflisten der Mietstaffelungen: {str(e)}")


@router.post("/", response_model=RentStepResponse, status_code=status.HTTP_201_CREATED)
async def create_rent_step(
    contract_id: int,
    rent_step: RentStepCreate,
    contract_service: ContractService = Depends(get_contract_service),
    current_user: User = Depends(get_current_active_user),
):
    # Berechtigung prüfen
    require_manager_or_admin(current_user)
    try:
        return await contract_service.create_rent_step(contract_id, rent_step, created_by=current_user.id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen der Mietstaffelung: {str(e)}")


@router.get("/{step_id}", response_model=RentStepResponse)
async def get_rent_step(
    contract_id: int,
    step_id: int,
    contract_service: ContractService = Depends(get_contract_service),
):
    step = await contract_service.get_rent_step(contract_id, step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Mietstaffelung nicht gefunden")
    return step


@router.put("/{step_id}", response_model=RentStepResponse)
async def update_rent_step(
    contract_id: int,
    step_id: int,
    data: RentStepUpdate,
    contract_service: ContractService = Depends(get_contract_service),
    current_user: User = Depends(get_current_active_user),
):
    require_manager_or_admin(current_user)
    try:
        updated = await contract_service.update_rent_step(contract_id, step_id, data)
        if not updated:
            raise HTTPException(status_code=404, detail="Mietstaffelung nicht gefunden")
        return updated
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktualisieren der Mietstaffelung: {str(e)}")


@router.delete("/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rent_step(
    contract_id: int,
    step_id: int,
    contract_service: ContractService = Depends(get_contract_service),
    current_user: User = Depends(get_current_active_user),
):
    require_manager_or_admin(current_user)
    success = await contract_service.delete_rent_step(contract_id, step_id)
    if not success:
        raise HTTPException(status_code=404, detail="Mietstaffelung nicht gefunden")
    return None
