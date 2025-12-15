import asyncio
import os
from pathlib import Path
from typing import AsyncIterator

import httpx
import pytest
import pytest_asyncio
from dishka import AsyncContainer
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import AsyncEngine
from testcontainers.postgres import PostgresContainer

from marketplace.infrastructure.persistence.tables import base as tables_base
from marketplace.main.config import Config, load_config
from marketplace.main.di.setup import setup_ioc_container
from marketplace.main.web_entrypoint import create_app

# ---------- Containers & config ----------


def _ensure_docker_host() -> None:
    """Pick a reachable docker socket for testcontainers."""
    os.environ.setdefault("TESTCONTAINERS_RYUK_DISABLED", "true")
    if os.environ.get("DOCKER_HOST"):
        return
    candidates = [
        Path.home()
        / ".colima/default/docker.sock",  # macOS Colima (default here)
        Path("/var/run/docker.sock"),  # linux / docker desktop
        Path.home() / ".docker/run/docker.sock",  # docker desktop on mac
        Path.home() / ".orbstack/run/docker.sock",  # OrbStack
    ]
    for sock in candidates:
        if sock.exists():
            os.environ["DOCKER_HOST"] = f"unix://{sock}"
            return
    raise RuntimeError(
        "Docker daemon socket not found. Please set DOCKER_HOST explicitly, "
        "e.g. export DOCKER_HOST=unix://$HOME/.colima/default/docker.sock"
    )


_ensure_docker_host()


@pytest.fixture(scope="session")
def postgres_container() -> AsyncIterator[PostgresContainer]:
    with PostgresContainer(
        image="postgres:16",
        username="test",
        password="test",
        dbname="marketplace",
        driver="psycopg",
    ) as pg:
        yield pg


@pytest.fixture(scope="session")
def config(postgres_container: PostgresContainer) -> Config:
    host = postgres_container.get_container_host_ip()
    port = int(postgres_container.get_exposed_port(5432))

    os.environ["POSTGRES_HOST"] = host
    os.environ["POSTGRES_PORT"] = str(port)
    os.environ["POSTGRES_USER"] = "test"
    os.environ["POSTGRES_PASSWORD"] = "test"
    os.environ["POSTGRES_DB"] = "marketplace"

    return load_config()


@pytest.fixture(scope="session")
def container_factory(config: Config) -> AsyncContainer:
    return setup_ioc_container(config=config)


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def prepare_schema(container_factory: AsyncContainer) -> None:
    async with container_factory() as scope:
        engine = await scope.get(AsyncEngine)
    # wait for DB to be ready
    for attempt in range(20):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(
                    tables_base.mapper_registry.metadata.create_all
                )
            break
        except Exception:  # OperationalError etc.
            if attempt == 19:
                raise
            await asyncio.sleep(0.5)


@pytest.fixture(scope="session")
def app(container_factory: AsyncContainer):
    return create_app(container=container_factory)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def http_client(app) -> AsyncIterator[httpx.AsyncClient]:
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver/api"
    ) as client:
        yield client


async def register_user(client: httpx.AsyncClient, email: str) -> int:
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": email,
        "password": "supersecret",
        "phone": "+380501112233",
    }
    resp = await client.post("/users/", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def login(client: httpx.AsyncClient, email: str, password: str) -> None:
    resp = await client.post(
        "/auth/login", json={"email": email, "password": password}
    )
    assert resp.status_code == 200, resp.text


def _unique_email(prefix: str) -> str:
    return f"{prefix}-{os.urandom(4).hex()}@example.com"


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user(http_client: httpx.AsyncClient) -> None:
    email = _unique_email("register")
    user_id = await register_user(http_client, email)
    assert isinstance(user_id, int)


@pytest.mark.asyncio(loop_scope="session")
async def test_login_sets_session_cookie(
    http_client: httpx.AsyncClient,
) -> None:
    email = _unique_email("login")
    await register_user(http_client, email)
    await login(http_client, email, "supersecret")
    assert "session_id" in http_client.cookies


async def _checkout(client: httpx.AsyncClient) -> int:
    checkout_payload = {
        "items": [
            {
                "product_id": 1,
                "quantity": 2,
                "price_at_purchase": "9.99",
                "title": "Widget",
            }
        ]
    }
    resp = await client.post("/orders/checkout", json=checkout_payload)
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


@pytest.mark.asyncio(loop_scope="session")
async def test_checkout_creates_order(http_client: httpx.AsyncClient) -> None:
    email = _unique_email("checkout")
    await register_user(http_client, email)
    await login(http_client, email, "supersecret")
    order_id = await _checkout(http_client)
    assert isinstance(order_id, int)


@pytest.mark.asyncio(loop_scope="session")
async def test_orders_me_returns_orders(
    http_client: httpx.AsyncClient,
) -> None:
    email = _unique_email("ordersme")
    await register_user(http_client, email)
    await login(http_client, email, "supersecret")
    order_id = await _checkout(http_client)

    resp = await http_client.get("/orders/me")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert any(o["id"] == order_id for o in data)


@pytest.mark.asyncio(loop_scope="session")
async def test_status_stats_returns_dict(
    http_client: httpx.AsyncClient,
) -> None:
    email = _unique_email("stats")
    await register_user(http_client, email)
    await login(http_client, email, "supersecret")
    await _checkout(http_client)

    resp = await http_client.get("/orders/stats/statuses")
    assert resp.status_code == 200, resp.text
    stats = resp.json()
    assert isinstance(stats, dict)
    assert sum(stats.values()) >= 1


@pytest.mark.asyncio(loop_scope="session")
async def test_daily_revenue_returns_list(
    http_client: httpx.AsyncClient,
) -> None:
    email = _unique_email("revenue")
    await register_user(http_client, email)
    await login(http_client, email, "supersecret")
    await _checkout(http_client)

    resp = await http_client.get("/orders/stats/daily-revenue")
    assert resp.status_code == 200, resp.text
    revenue = resp.json()
    assert isinstance(revenue, list)
