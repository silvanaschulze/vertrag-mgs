import asyncio
import datetime
import pytest
import sqlalchemy as sa

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.database import Base
from app.models.user import User, UserRole
from app.models.contract import Contract, ContractStatus, ContractType
from app.models.alert import Alert, AlertType


DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.mark.asyncio
async def test_create_and_query_models():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # Create a user
        user = User(email="test@example.com", name="Test User", password_hash="hash", role=UserRole.USER)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        assert user.id is not None

        # Create a contract (use date objects)
        contract = Contract(
            title="Test Contract",
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2026, 1, 1),
            client_name="Client",
            created_by=user.id,
            contract_type=ContractType.OTHER,
            status=ContractStatus.DRAFT,
        )
        session.add(contract)
        await session.commit()
        await session.refresh(contract)
        assert contract.id is not None

        # Create an alert (use datetime)
        alert = Alert(contract_id=contract.id, alert_type=AlertType.T_MINUS_30, scheduled_for=datetime.datetime(2025, 12, 1, 9, 0, 0))
        session.add(alert)
        await session.commit()
        await session.refresh(alert)
        assert alert.id is not None

        # Query counts using sa.text to get scalar
        result = await session.execute(sa.text("SELECT count(*) AS cnt FROM users"))
        count = result.scalar_one()
        assert count >= 1

    await engine.dispose()
