from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import composite

from marketplace.domain.entities.category.category import Category
from marketplace.domain.entities.identity import Identity
from marketplace.infrastructure.persistence.tables.base import mapper_registry

CATEGORY_NAME_LENGTH = 30

categories_table = Table(
    "categories",
    mapper_registry.metadata,
    Column("category_id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(CATEGORY_NAME_LENGTH), nullable=False),
    Column(
        "parent_category_id",
        Integer,
        ForeignKey("categories.category_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    ),
    CheckConstraint(
        "category_id <> parent_category_id", "ch_categories_parent_category_id"
    ),
)

mapper_registry.map_imperatively(
    Category,
    categories_table,
    properties={
        "identity": composite(Identity, categories_table.c.category_id),
        "name": categories_table.c.name,
        "parent_category_id": composite(
            Identity, categories_table.c.parent_category_id
        ),
        "_parent_category_id_raw": categories_table.c.parent_category_id,
    },
)
