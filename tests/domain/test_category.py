import pytest
from pydantic import ValidationError

from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.category.category import Category
from marketplace.domain.entities.category.factory import (
    CategoryFactory,
    CreateCategoryRequest,
)
from marketplace.domain.entities.category.repository import CategoryRepository
from marketplace.domain.entities.identity import Identity
from marketplace.domain.exceptions import DomainError, EntityNotFound

# --- Mocks ---


class FakeTransactionManager(TransactionManager):
    async def commit(self) -> None:  # type: ignore[override]
        return None

    async def flush(self) -> None:  # type: ignore[override]
        return None


class FakeCategoryRepository(CategoryRepository):
    def __init__(self) -> None:
        self._categories: dict[int, Category] = {}
        self._seq = 1

    async def by_identity(self, category_id: Identity) -> Category | None:  # type: ignore[override]
        return self._categories.get(category_id.value or -1)

    async def list(self) -> list[Category]:  # type: ignore[override]
        return list(self._categories.values())

    def add(self, category: Category) -> None:  # type: ignore[override]
        if category.identity._value is None:
            new_id = self._seq
            self._seq += 1
            object.__setattr__(category, "identity", Identity(_value=new_id))
        self._categories[category.identity.value] = category

    def remove(self, category: Category) -> None:  # type: ignore[override]
        if category.identity.value in self._categories:
            del self._categories[category.identity.value]


def make_category(
    category_id: int = 1,
    name: str = "Test Category",
    parent_id: int | None = None,
) -> Category:
    return Category(
        identity=Identity(category_id),
        name=name,
        parent_category_id=Identity(parent_id) if parent_id else None,
    )


# --- Entity Tests ---


def test_rename_category_success() -> None:
    category = make_category()
    category.rename("New Category Name")
    assert category.name == "New Category Name"


def test_rename_category_empty_name_raises_error() -> None:
    category = make_category()
    with pytest.raises(DomainError, match="Category name cannot be empty."):
        category.rename("")


def test_set_parent_category_success() -> None:
    category = make_category(category_id=1)
    parent = make_category(category_id=2)
    category.set_parent(parent.identity)
    assert category.parent_category_id is not None
    assert category.parent_category_id.value == 2


def test_set_parent_category_to_none_success() -> None:
    category = make_category(category_id=1, parent_id=2)
    category.set_parent(None)
    assert category.parent_category_id is None


def test_set_parent_category_to_itself_raises_error() -> None:
    category = make_category(category_id=1)
    with pytest.raises(
        DomainError, match="Category cannot be its own parent."
    ):
        category.set_parent(category.identity)


# --- Request Validation Tests ---


def test_create_category_request_valid_root_category() -> None:
    req = CreateCategoryRequest(name="Electronics", parent_category_id=None)
    assert req.name == "Electronics"
    assert req.parent_category_id is None


def test_create_category_request_valid_sub_category() -> None:
    req = CreateCategoryRequest(name="Laptops", parent_category_id=1)
    assert req.name == "Laptops"
    assert req.parent_category_id == 1


def test_create_category_request_name_stripped() -> None:
    req = CreateCategoryRequest(name="  Books  ")
    assert req.name == "Books"


def test_create_category_request_name_too_long() -> None:
    long_name = "a" * 31
    with pytest.raises(ValidationError):
        CreateCategoryRequest(name=long_name)


# --- Factory Tests ---


@pytest.mark.asyncio
async def test_create_root_category_success() -> None:
    repo = FakeCategoryRepository()
    factory = CategoryFactory(repo)

    req = CreateCategoryRequest(name="Electronics", parent_category_id=None)

    category = await factory.create(req)

    assert category.name == "Electronics"
    assert category.parent_category_id is None


@pytest.mark.asyncio
async def test_create_sub_category_success() -> None:
    repo = FakeCategoryRepository()
    factory = CategoryFactory(repo)

    # Create parent category manually
    parent = Category(
        identity=Identity(1), name="Electronics", parent_category_id=None
    )
    repo._categories[1] = parent
    repo._seq = 2

    req = CreateCategoryRequest(name="Laptops", parent_category_id=1)

    category = await factory.create(req)

    assert category.name == "Laptops"
    assert category.parent_category_id is not None
    assert category.parent_category_id.value == 1


@pytest.mark.asyncio
async def test_create_category_parent_not_found() -> None:
    repo = FakeCategoryRepository()
    factory = CategoryFactory(repo)

    req = CreateCategoryRequest(name="Laptops", parent_category_id=999)

    with pytest.raises(EntityNotFound):
        await factory.create(req)
