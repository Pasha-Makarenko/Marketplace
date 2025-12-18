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

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

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
    if isinstance(host, str) and host.startswith("npipe://"):
        host = "localhost"
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


async def create_seller(
    client: httpx.AsyncClient, user_id: int, store_name: str
) -> int:
    payload = {
        "user_id": user_id,
        "store_name": store_name,
        "contact_info": "contact@store.com",
        "return_policy": "No returns",
        "delivery_terms": "2 weeks",
    }
    resp = await client.post("/sellers/", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


@pytest.mark.asyncio(loop_scope="session")
async def test_create_seller(http_client: httpx.AsyncClient) -> None:
    email = _unique_email("createseller")
    user_id = await register_user(http_client, email)
    seller_id = await create_seller(http_client, user_id, "My Store")
    assert isinstance(seller_id, int)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_seller(http_client: httpx.AsyncClient) -> None:
    email = _unique_email("getseller")
    user_id = await register_user(http_client, email)
    seller_id = await create_seller(http_client, user_id, "Get Store")

    resp = await http_client.get(f"/sellers/{seller_id}")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["id"] == seller_id
    assert data["store_name"] == "Get Store"


@pytest.mark.asyncio(loop_scope="session")
async def test_list_sellers(http_client: httpx.AsyncClient) -> None:
    email = _unique_email("listsellers")
    user_id = await register_user(http_client, email)
    await create_seller(http_client, user_id, "List Store")

    resp = await http_client.get("/sellers/")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio(loop_scope="session")
async def test_update_seller(http_client: httpx.AsyncClient) -> None:
    email = _unique_email("updateseller")
    user_id = await register_user(http_client, email)
    seller_id = await create_seller(http_client, user_id, "Update Store")

    update_payload = {
        "seller_id": seller_id,
        "store_name": "Updated Store Name",
        "contact_info": "new@contact.com",
        "return_policy": None,
        "delivery_terms": None,
    }

    resp = await http_client.patch(
        f"/sellers/{seller_id}", json=update_payload
    )
    assert resp.status_code == 204, resp.text

    resp = await http_client.get(f"/sellers/{seller_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["store_name"] == "Updated Store Name"
    assert data["contact_info"] == "new@contact.com"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_top_sellers(http_client: httpx.AsyncClient) -> None:
    resp = await http_client.get("/sellers/analytics/top")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)


async def create_category(
    client: httpx.AsyncClient, name: str, parent_id: int | None = None
) -> int:
    payload = {"name": name}
    if parent_id is not None:
        payload["parent_category_id"] = parent_id
    resp = await client.post("/categories/", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


@pytest.mark.asyncio(loop_scope="session")
async def test_create_category(http_client: httpx.AsyncClient) -> None:
    category_id = await create_category(http_client, "Electronics")
    assert isinstance(category_id, int)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_category(http_client: httpx.AsyncClient) -> None:
    category_id = await create_category(http_client, "Books")
    resp = await http_client.get(f"/categories/{category_id}")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["name"] == "Books"


@pytest.mark.asyncio(loop_scope="session")
async def test_list_categories(http_client: httpx.AsyncClient) -> None:
    await create_category(http_client, "Toys")
    resp = await http_client.get("/categories/")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    assert any(c["name"] == "Toys" for c in data)


@pytest.mark.asyncio(loop_scope="session")
async def test_create_subcategory(http_client: httpx.AsyncClient) -> None:
    parent_id = await create_category(http_client, "Parent")
    child_id = await create_category(http_client, "Child", parent_id)
    assert isinstance(child_id, int)

    resp = await http_client.get(f"/categories/{child_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Child"
    # Depending on serialization, check parent info if possible,
    # or just assume successful creation implies link.


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_category(http_client: httpx.AsyncClient) -> None:
    category_id = await create_category(http_client, "To Delete")
    resp = await http_client.delete(f"/categories/{category_id}")
    assert resp.status_code == 204, resp.text

    # Verify it's gone
    resp = await http_client.get(f"/categories/{category_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_category_distribution(http_client: httpx.AsyncClient) -> None:
    resp = await http_client.get("/categories/analytics/distribution")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)


async def create_product(
    client: httpx.AsyncClient, category_id: int, name: str
) -> int:
    payload = {
        "name": name,
        "description": "A great product",
        "price": 100.0,
        "stock_quantity": 10,
        "category_id": category_id,
        "discount": 0,
    }
    resp = await client.post("/products/", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


@pytest.mark.asyncio(loop_scope="session")
async def test_create_product(http_client: httpx.AsyncClient) -> None:
    email = _unique_email("createproduct")
    user_id = await register_user(http_client, email)
    await login(http_client, email, "supersecret")
    await create_seller(http_client, user_id, "Product Store")
    cat_id = await create_category(http_client, "Product Category")

    product_id = await create_product(http_client, cat_id, "New Product")
    assert isinstance(product_id, int)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_product(http_client: httpx.AsyncClient) -> None:
    email = _unique_email("getproduct")
    user_id = await register_user(http_client, email)
    await login(http_client, email, "supersecret")
    await create_seller(http_client, user_id, "Get Product Store")
    cat_id = await create_category(http_client, "Get Product Category")

    product_id = await create_product(http_client, cat_id, "Get Product")

    resp = await http_client.get(f"/products/{product_id}")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["name"] == "Get Product"
    assert data["id"] == product_id


@pytest.mark.asyncio(loop_scope="session")
async def test_list_products(http_client: httpx.AsyncClient) -> None:
    email = _unique_email("listproducts")
    user_id = await register_user(http_client, email)
    await login(http_client, email, "supersecret")
    await create_seller(http_client, user_id, "List Product Store")
    cat_id = await create_category(http_client, "List Product Category")

    await create_product(http_client, cat_id, "List Product 1")
    await create_product(http_client, cat_id, "List Product 2")

    resp = await http_client.get("/products/")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 2


@pytest.mark.asyncio(loop_scope="session")
async def test_update_product(http_client: httpx.AsyncClient) -> None:
    email = _unique_email("updateproduct")
    user_id = await register_user(http_client, email)
    await login(http_client, email, "supersecret")
    await create_seller(http_client, user_id, "Update Product Store")
    cat_id = await create_category(http_client, "Update Product Category")

    product_id = await create_product(http_client, cat_id, "Old Name")

    update_payload = {
        "name": "New Name",
        "description": "Updated desc",
        "price": 150.0,
        "stock_quantity": 20,
        "category_id": cat_id,
        "discount": 10,
    }

    resp = await http_client.patch(
        f"/products/{product_id}", json=update_payload
    )
    assert resp.status_code == 204, resp.text

    resp = await http_client.get(f"/products/{product_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "New Name"
    assert data["price"] == 150.0


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_product(http_client: httpx.AsyncClient) -> None:
    email = _unique_email("deleteproduct")
    user_id = await register_user(http_client, email)
    await login(http_client, email, "supersecret")
    await create_seller(http_client, user_id, "Delete Product Store")
    cat_id = await create_category(http_client, "Delete Product Category")

    product_id = await create_product(http_client, cat_id, "Delete Me")

    resp = await http_client.delete(f"/products/{product_id}")
    assert resp.status_code == 204, resp.text

    resp = await http_client.get(f"/products/{product_id}")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["is_active"] is False


@pytest.mark.asyncio(loop_scope="session")
async def test_top_rated_products(http_client: httpx.AsyncClient) -> None:
    resp = await http_client.get("/products/analytics/top-rated")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio(loop_scope="session")
async def test_low_stock_products(http_client: httpx.AsyncClient) -> None:
    resp = await http_client.get("/products/analytics/low-stock")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio(loop_scope="session")
async def test_create_rating(http_client: httpx.AsyncClient) -> None:
    email = _unique_email("createrating")
    await register_user(http_client, email)
    await login(http_client, email, "supersecret")
    # Need a seller and product
    seller_email = _unique_email("ratingseller")
    seller_id = await register_user(http_client, seller_email)
    # Login as seller to create product
    await login(http_client, seller_email, "supersecret")
    await create_seller(http_client, seller_id, "Rating Store")
    cat_id = await create_category(http_client, "Rating Category")
    product_id = await create_product(http_client, cat_id, "Rated Product")

    # Login as user to rate
    await login(http_client, email, "supersecret")
    payload = {"product_id": product_id, "value": 5}
    resp = await http_client.post("/ratings/", json=payload)
    assert resp.status_code == 201, resp.text
    assert "id" in resp.json()


@pytest.mark.asyncio(loop_scope="session")
async def test_list_ratings(http_client: httpx.AsyncClient) -> None:
    # Setup
    email = _unique_email("listrating")
    await register_user(http_client, email)
    await login(http_client, email, "supersecret")

    seller_email = _unique_email("listratingseller")
    seller_id = await register_user(http_client, seller_email)
    await login(http_client, seller_email, "supersecret")
    await create_seller(http_client, seller_id, "List Rating Store")
    cat_id = await create_category(http_client, "List Rating Category")
    product_id = await create_product(
        http_client, cat_id, "List Rated Product"
    )

    await login(http_client, email, "supersecret")
    await http_client.post(
        "/ratings/", json={"product_id": product_id, "value": 4}
    )

    resp = await http_client.get(f"/ratings/?product_id={product_id}")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["value"] == 4


@pytest.mark.asyncio(loop_scope="session")
async def test_rating_analytics(http_client: httpx.AsyncClient) -> None:
    # Setup
    email = _unique_email("ratinganalytics")
    await register_user(http_client, email)
    await login(http_client, email, "supersecret")

    seller_email = _unique_email("analytics_seller")
    seller_id = await register_user(http_client, seller_email)
    await login(http_client, seller_email, "supersecret")
    await create_seller(http_client, seller_id, "Analytics Store")
    cat_id = await create_category(http_client, "Analytics Category")
    product_id = await create_product(http_client, cat_id, "Analytics Product")

    await login(http_client, email, "supersecret")
    await http_client.post(
        "/ratings/", json={"product_id": product_id, "value": 5}
    )
    # Another user
    email2 = _unique_email("ratinganalytics2")
    await register_user(http_client, email2)
    await login(http_client, email2, "supersecret")
    await http_client.post(
        "/ratings/", json={"product_id": product_id, "value": 3}
    )

    # Distribution
    resp = await http_client.get(
        f"/ratings/distribution?product_id={product_id}"
    )
    assert resp.status_code == 200, resp.text
    dist = resp.json()
    # Keys might be strings in JSON
    assert str(5) in dist or 5 in dist
    assert str(3) in dist or 3 in dist

    # Average
    resp = await http_client.get(f"/ratings/average?product_id={product_id}")
    assert resp.status_code == 200, resp.text
    avg_data = resp.json()
    assert avg_data["average_rating"] == 4.0


@pytest.mark.asyncio(loop_scope="session")
async def test_create_review(http_client: httpx.AsyncClient) -> None:
    email = _unique_email("createreview")
    await register_user(http_client, email)
    await login(http_client, email, "supersecret")

    seller_email = _unique_email("reviewseller")
    seller_id = await register_user(http_client, seller_email)
    await login(http_client, seller_email, "supersecret")
    await create_seller(http_client, seller_id, "Review Store")
    cat_id = await create_category(http_client, "Review Category")
    product_id = await create_product(http_client, cat_id, "Reviewed Product")

    await login(http_client, email, "supersecret")
    payload = {"product_id": product_id, "text": "Great product!"}
    resp = await http_client.post("/reviews/", json=payload)
    assert resp.status_code == 201, resp.text
    assert "id" in resp.json()


@pytest.mark.asyncio(loop_scope="session")
async def test_list_reviews(http_client: httpx.AsyncClient) -> None:
    email = _unique_email("listreview")
    await register_user(http_client, email)
    await login(http_client, email, "supersecret")

    seller_email = _unique_email("listreviewseller")
    seller_id = await register_user(http_client, seller_email)
    await login(http_client, seller_email, "supersecret")
    await create_seller(http_client, seller_id, "List Review Store")
    cat_id = await create_category(http_client, "List Review Category")
    product_id = await create_product(
        http_client, cat_id, "List Reviewed Product"
    )

    await login(http_client, email, "supersecret")
    await http_client.post(
        "/reviews/", json={"product_id": product_id, "text": "Review 1"}
    )

    resp = await http_client.get(f"/reviews/?product_id={product_id}")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["text"] == "Review 1"


@pytest.mark.asyncio(loop_scope="session")
async def test_recent_reviews(http_client: httpx.AsyncClient) -> None:
    resp = await http_client.get("/reviews/recent")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio(loop_scope="session")
async def test_leave_feedback(http_client: httpx.AsyncClient) -> None:
    email = _unique_email("feedback")
    await register_user(http_client, email)
    await login(http_client, email, "supersecret")

    seller_email = _unique_email("feedbackseller")
    seller_id = await register_user(http_client, seller_email)
    await login(http_client, seller_email, "supersecret")
    await create_seller(http_client, seller_id, "Feedback Store")
    cat_id = await create_category(http_client, "Feedback Category")
    product_id = await create_product(http_client, cat_id, "Feedback Product")

    await login(http_client, email, "supersecret")
    payload = {
        "product_id": product_id,
        "rating": 5,
        "comment": "Excellent!",
    }
    resp = await http_client.post("/feedback/", json=payload)
    assert resp.status_code == 201, resp.text
    assert resp.json()["status"] == "success"

    # Verify rating and review were created
    resp = await http_client.get(f"/ratings/?product_id={product_id}")
    assert resp.status_code == 200
    ratings = resp.json()
    assert any(r["value"] == 5 for r in ratings)

    resp = await http_client.get(f"/reviews/?product_id={product_id}")
    assert resp.status_code == 200
    reviews = resp.json()
    assert any(r["text"] == "Excellent!" for r in reviews)
