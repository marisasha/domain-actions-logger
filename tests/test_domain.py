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


# =-=-=-=- Тест создания владельца домена =-=-=-=-=-=-=-=-=-=-=-=-
@pytest.mark.asyncio
async def test_owner_success(client):

    login_resp = await client.post(
        "/auth/token",
        json={
            "username": "string",
            "password": "string",
        },
    )
    assert login_resp.status_code == status.HTTP_200_OK
    access_token = login_resp.json()["access"]
    num = random.randint(0, 1000000000)
    response = await client.post(
        "api/owners",
        json={
            "first_name": "Тест",
            "last_name": "Тест",
            "gender": "M",
            "email": f"test{num}@test.test",
            "phone": f"{num}",
            "birth_date": "2000-02-02T00:00:00",
            "birth_place": "Москва",
            "passport_from": "Россия",
            "passport_number": "123456",
            "passport_series": 1234,
            "issue_date": "2000-02-02T00:00:00",
            "expiry_date": None,
            "department_code": "123-123",
            "issue_by": "ГУ МВД ПО МОСКВЕ",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == f"test{num}@test.test"
    print(f"[{datetime.now()}]TEST: owner success. RESULT: passed ✅")


# =-=-=-=- Тест получения владельца по ID =-=-=-=-=-=-=-=-=-=-=-=-=-
@pytest.mark.asyncio
async def test_owner_get(client):
    login_resp = await client.post(
        "/auth/token",
        json={
            "username": "string",
            "password": "string",
        },
    )
    assert login_resp.status_code == status.HTTP_200_OK
    access_token = login_resp.json()["access"]

    owner_id = 5
    response = await client.get(
        f"api/owners/{owner_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "id" in data
    assert data["id"] == owner_id
    assert "first_name" in data
    assert "last_name" in data
    assert "email" in data
    print(f"[{datetime.now()}]TEST: owner get. RESULT: passed ✅")


# =-=-=-=- Тест получения несуществующего владельца =-=-=-=-=-=-=-=-=-=-=-=-=-
@pytest.mark.asyncio
async def test_owner_not_found(client):
    login_resp = await client.post(
        "/auth/token",
        json={
            "username": "string",
            "password": "string",
        },
    )
    assert login_resp.status_code == status.HTTP_200_OK
    access_token = login_resp.json()["access"]

    non_existent_id = 999999

    response = await client.get(
        f"api/owners/{non_existent_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "detail" in data
    assert f"Owner with id {non_existent_id} not found" in data["detail"]
    print(f"[{datetime.now()}]TEST: owner not found. RESULT: passed ✅")
