"""
认证 API 测试
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    """测试用户注册"""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Test1234", "nickname": "TestUser"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """测试重复邮箱注册"""
    # 第一次注册
    await client.post(
        "/api/v1/auth/register", json={"email": "duplicate@example.com", "password": "Test1234"}
    )

    # 第二次注册应该失败
    response = await client.post(
        "/api/v1/auth/register", json={"email": "duplicate@example.com", "password": "Test1234"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """测试用户登录"""
    # 先注册
    await client.post(
        "/api/v1/auth/register", json={"email": "login@example.com", "password": "Test1234"}
    )

    # 再登录
    response = await client.post(
        "/api/v1/auth/login", json={"email": "login@example.com", "password": "Test1234"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """测试错误密码登录"""
    # 先注册
    await client.post(
        "/api/v1/auth/register", json={"email": "wrong@example.com", "password": "Test1234"}
    )

    # 用错误密码登录
    response = await client.post(
        "/api/v1/auth/login", json={"email": "wrong@example.com", "password": "WrongPassword"}
    )
    assert response.status_code == 401
