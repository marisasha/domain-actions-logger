import random
import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status
from src.main import app
from src.database import engine as async_engine


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as ac:
        yield ac


@pytest.fixture(autouse=True)
async def cleanup_db():
    yield
    await async_engine.dispose()


# =-=-=-=- Тест успешной регистрации нового пользователя =-=-=-=-=-=-=-=-=-=-=-=-


@pytest.mark.asyncio
async def test_register_success(client):
    num = random.randint(0, 1000000000)
    username = f"test_{num}"
    email = f"test{num}@example.com"
    phone_number = str(num)

    response = await client.post(
        "/auth/register",
        json={
            "username": username,
            "password": "123456",
            "first_name": "Test",
            "last_name": "User",
            "email": email,
            "birth_date": "2000-01-01",
            "phone": phone_number,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == username


# =-=-=-=- Тест регистрации существующего пользователя =-=-=-=-=-=-=-=-=-=-=-=-


@pytest.mark.asyncio
async def test_register_existing_user(client):
    user_data = {
        "username": "string",
        "password": "123456",
        "first_name": "Test",
        "last_name": "User",
        "email": "string@string.ru",
        "birth_date": "2000-01-01",
        "phone": "+79296782354",
    }
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# =-=-=-=- Тест получения токенов =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
@pytest.mark.asyncio
async def test_login_success(client):

    response = await client.post(
        "/auth/token",
        json={
            "username": "string",
            "password": "string",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access" in data
    assert "refresh" in data


# =-=-=-=- Тест получения токена для несуществующего пользователя =-=-=-=-=-=-=-
@pytest.mark.asyncio
async def test_login_non_existent_user(client):

    response = await client.post(
        "/auth/token",
        json={
            "username": "non-existent-username",
            "password": "non-existent-password",
        },
    )

    assert response.status_code == 400


# =-=-=-=- Тест получения токена для пользователя при неправильном пароле =-=-=-=-
@pytest.mark.asyncio
async def test_login_wrong_password(client):

    response = await client.post(
        "/auth/token",
        json={
            "username": "string",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401


# =-=-=-=- Тест для обновления токена =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
@pytest.mark.asyncio
async def test_refresh_token(client):

    login_resp = await client.post(
        "/auth/token",
        json={"username": "string", "password": "string"},
    )

    refresh_token = login_resp.json()["refresh"]

    response = await client.post(
        "/auth/token/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert response.status_code == 200
    assert "access" in response.json()
