import pytest
import pytest_asyncio
from sqlalchemy import create_mock_engine,create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine,AsyncSession
from sqlalchemy.orm import Session
from app.models.Base import Base
from app.models.Wallets import Wallets
from app.repository.WalletRepository import WalletRepository,WalletNotCreatedExeption
from app.schema.WalletSchema import WalletSchema,WalletGetSchema,WalletDeleteSchema,WalletUpdateSchema
from typing import Sequence
import datetime
from  uuid import UUID,uuid4
import asyncio
from fastapi.testclient import TestClient
from app.main.app import app
from app.config import settings
from app.database.db import get_async_session
from httpx import AsyncClient,ASGITransport
import logging



@pytest_asyncio.fixture(scope="module")
async def client(db_session):
    def override_get_db():
        return db_session
    app.dependency_overrides[get_async_session] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8080") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="module")
async def db_session():
    url="sqlite+aiosqlite://"
    engine = create_async_engine(url=url,echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        await session.begin()
        yield session
        await session.rollback()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_wallet3(client):
    response = await client.post("/api/v2/wallet/create")
    response  = response.json()
    logging.info(response)
    assert response['status'] == 200
    response = await client.post("/api/v2/wallet/create")
    response  = response.json()
    logging.info(response)
    assert response['status'] == 200
    response = await client.post("/api/v2/wallet/create")
    response  = response.json()
    logging.info(response)
    assert response['status']  == 200

@pytest.mark.asyncio
async def test_create_wallet(client):
    response = await client.post("/api/v2/wallet/create")
    logging.info(response.json())

@pytest.mark.asyncio
async def test_create_update_delete_wallets(client):
    response = await client.post("/api/v2/wallet/create")
    response  = response.json()
    logging.info(response)
    assert response['status'] == 200
    created_uuid:UUID = response['uuid']
    print(created_uuid)
    response = await client.get(f"/api/v2/wallet/{created_uuid}")
    response  = response.json()
    logging.info(response)
    assert response['status'] == 200
    wallet_data = WalletUpdateSchema(uuid=response['uuid'], amount=2000)
    response = await client.post("/api/v2/wallet/update",json=wallet_data.model_dump())
    response  = response.json()
    logging.info(response)
    assert response['status'] == 200
    assert response['balance'] == 2000
    created_uuid:UUID= response['uuid']
    response = await client.post(f"/api/v2/wallet/delete?uuid={created_uuid}")
    logging.info(response.json())
    response  = response.json()
    logging.info(response)
    assert response['status'] == 200


@pytest.mark.asyncio
async def test_get_wallets_all(client):
    answer = await client.post("/api/v2/wallet/get_all_wallets")
    answer  = answer.json()
    logging.debug(answer)
    assert answer['status'] == 200
    print(answer)


@pytest.mark.asyncio
async def test_wallet_get(client):
    response = await client.post("/api/v2/wallet/create")
    response  = response.json()
    logging.info(response)
    assert response['status'] == 200

    id = response['uuid']
    response = await client.get(f"/api/v1/wallets/{id}")
    response  = response.json()
    logging.info(response)
    assert response['status'] == 200


@pytest.mark.asyncio
async def test_wallet_get_404(client):
    response = await client.post("/api/v2/wallet/create")
    response  = response.json()
    logging.info(response)
    assert response['status'] == 200

    id = UUID("00000000-0000-0000-0000-000000000000")
    response = await client.get(f"/api/v1/wallets/{id}")
    logging.info(response.json())
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_wallet_get_422(client):
    response = await client.post("/api/v2/wallet/create")
    response  = response.json()
    logging.info(response)
    assert response['status'] == 200

    response = await client.get(f"/api/v1/wallets/fdfe34sdf")
    logging.info(response.json())
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_wallet_operations_404(client):
    response = await client.post("/api/v2/wallet/create")
    response  = response.json()
    logging.info(response)
    assert response['status'] == 200

    id = uuid4()
    response = await client.post(f"/api/v1/wallets/{id}/operation",json={"operationType":"DEPOSIT","amount":100})
    logging.info(response.json())
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_wallet_operations_200(client):
    response = await client.post("/api/v2/wallet/create")
    response  = response.json()
    logging.info(response)
    assert response['status'] == 200

    id = response['uuid']
    response = await client.post(f"/api/v1/wallets/{id}/operation",json={"operationType":"DEPOSIT","amount":100})
    logging.info(response.json())
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_wallet_operations_422(client):
    response = await client.post("/api/v2/wallet/create")
    response  = response.json()
    logging.info(response)
    assert response['status'] == 200

    id = response['uuid']
    response = await client.post(f"/api/v1/wallets/{id}/operation",json={"oype":"DEPOSIT","amount":100})
    logging.info(response.json())
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_wallet_operations_NotEnoughFunds_425(client):
    response = await client.post("/api/v2/wallet/create")
    response  = response.json()
    logging.info(response)
    assert response['status'] == 200

    id = response['uuid']
    response = await client.post(f"/api/v1/wallets/{id}/operation",json={"operationType":"WITHDRAW","amount":1000})
    logging.info(response.json())
    assert response.status_code == 425


#test_wallet_operations_deposit_200(client)
@pytest.mark.asyncio
async def test_wallet_operations_deposit_withraw_200(client):
    response = await client.post("/api/v2/wallet/create")
    response  = response.json()
    logging.info(response)
    assert response['status'] == 200

    id = response['uuid']
    response = await client.post(f"/api/v1/wallets/{id}/operation",json={"operationType":"DEPOSIT","amount":1000})
    logging.info(response.json())
    assert response.status_code == 200

    response = await client.post(f"/api/v1/wallets/{id}/operation",json={"operationType":"WITHDRAW","amount":100})
    logging.info(response.json())
    assert response.status_code == 200
    assert response.json()['balance'] == 900



