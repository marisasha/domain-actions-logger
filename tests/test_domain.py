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
# =-=-=-=- Тест создания владельца домена =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
@pytest.mark.asyncio
async def test_owner_success(client):

    access_token = await get_access_token(client)
    num = random.randint(0, 1000000000)

    owner_json = owner_json = {
        "first_name": "Тест",
        "last_name": "Тест",
        "gender": "M",
        "email": f"test{num}@test.test",
        "phone": f"{num}",
        "birth_date": "2000-02-02T00:00:00",
        "birth_place": "Москва",
        "passport_from": "Россия",
        "passport_number": str(num)[:6],
        "passport_series": str(num)[:4],
        "issue_date": "2000-02-02T00:00:00",
        "expiry_date": None,
        "department_code": "123-123",
        "issue_by": "ГУ МВД ПО МОСКВЕ",
    }

    response = await client.post(
        "api/owners",
        json=owner_json,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == f"test{num}@test.test"
    print(f"[{datetime.now()}]TEST: owner success. RESULT: passed ✅")

    # Тест на создание объекта с существующей почтой
    response = await client.post(
        "api/owners",
        json=owner_json,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "Email already exists" in data["detail"]

    print(f"[{datetime.now()}]TEST: create owner with exists email . RESULT: passed ✅")

    # Тест на создание объекта с существующим номером телефона
    owner_json["email"] = f"new_test{num}@test.test"

    response = await client.post(
        "api/owners",
        json=owner_json,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "Phone already exists" in data["detail"]

    print(f"[{datetime.now()}]TEST: create owner with exists phone . RESULT: passed ✅")

    # Тест на создание объекта с существующим номером паспорта
    owner_json["phone"] = f"+{num}"

    response = await client.post(
        "api/owners",
        json=owner_json,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "Passport number already exists" in data["detail"]

    print(
        f"[{datetime.now()}]TEST: create owner with exists passport number . RESULT: passed ✅"
    )

    # Тест на создание объекта с существующей серией паспорта
    owner_json["passport_number"] = str(num)[:5] + "0"
    response = await client.post(
        "api/owners",
        json=owner_json,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "Passport series already exists" in data["detail"]

    print(
        f"[{datetime.now()}]TEST: create owner with exists passport series . RESULT: passed ✅"
    )


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# =-=-=-=- Тест получения владельца по ID =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
@pytest.mark.asyncio
async def test_owner_get(client):
    access_token = await get_access_token(client)

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
    print(f"[{datetime.now()}]TEST: get owner . RESULT: passed ✅")

    # Тест получения владельца с несуществующим id
    owner_id = 999
    response = await client.get(
        f"api/owners/{owner_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert f"Owner with id {owner_id} not found" in data["detail"]
    print(
        f"[{datetime.now()}]TEST: get owner with not exists owner_id. RESULT: passed ✅"
    )


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# =-=-=-=- Тест создания домена =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
@pytest.mark.asyncio
async def test_domain_success(client):
    access_token = await get_access_token(client)

    owner_id = 5
    num = random.randint(0, 10000)

    response = await client.post(
        "api/domains",
        json={
            "owner_id": owner_id,
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
            "owner_id": owner_id,
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
