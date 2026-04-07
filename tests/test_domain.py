from datetime import datetime
import random
import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status
from src.main import app
from src.database import engine as async_engine


@pytest.fixture()
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as ac:
        yield ac


@pytest.fixture(autouse=True)
async def cleanup_db():
    yield
    await async_engine.dispose()


async def get_access_token(client):
    login_resp = await client.post(
        "/auth/token",
        json={
            "username": "string",
            "password": "string",
        },
    )
    access_token = login_resp.json()["access"]
    return access_token


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# =-=-=-=- Тест создания домена =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
@pytest.mark.asyncio
async def test_domain_success(client):
    access_token = await get_access_token(client)

    num = random.randint(0, 10000)

    response = await client.post(
        "api/domains",
        json={
            "name": f"test{num}.com",
            "registration_date": "2026-02-02T00:00:00",
            "expiry_date": "2026-04-02T00:00:00",
            "status": "registered",
            "registration_certificate_url": "22.pdf",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == f"test{num}.com"
    print(f"[{datetime.now()}]TEST: domain success. RESULT: passed ✅")

    # Тест создания домена с существующим именем домена
    response = await client.post(
        "api/domains",
        json={
            "name": f"test{num}.com",
            "registration_date": "2026-02-02T00:00:00",
            "expiry_date": "2026-04-02T00:00:00",
            "status": "registered",
            "registration_certificate_url": "22.pdf",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert f"Domain with name test{num}.com already exists" in data["detail"]
    print(f"[{datetime.now()}]TEST: create exists domain name. RESULT: passed ✅")
