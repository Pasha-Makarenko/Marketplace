from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import composite

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.product.product import Product
from marketplace.infrastructure.persistence.tables.base import mapper_registry

products_table = Table(
    "products",
    mapper_registry.metadata,
    Column("product_id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(255), nullable=False),
    Column("description", Text, nullable=True),
    Column("price", Numeric(10, 2), nullable=False),
    Column("discount", Integer, nullable=False, default=0),
    Column("stock_quantity", Integer, nullable=False),
    Column(
        "owner_id",
        Integer,
        ForeignKey("seller_profiles.seller_id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "category_id",
        Integer,
        ForeignKey("categories.category_id", ondelete="RESTRICT"),
        nullable=False,
    ),
    CheckConstraint("name <> ''", name="ch_products_name"),
    CheckConstraint("price >= 0", name="ch_products_price"),
    CheckConstraint("discount BETWEEN 0 AND 100", name="ch_products_discount"),
    CheckConstraint("stock_quantity >= 0", name="ch_products_stock_quantity"),
)

mapper_registry.map_imperatively(
    Product,
    products_table,
    properties={
        "identity": composite(Identity, products_table.c.product_id),
        "name": products_table.c.name,
        "description": products_table.c.description,
        "price": products_table.c.price,
        "discount": products_table.c.discount,
        "stock_quantity": products_table.c.stock_quantity,
        "owner_id": composite(Identity, products_table.c.owner_id),
        "category_id": composite(Identity, products_table.c.category_id),
    },
    exclude_properties=["created_at"],
)
