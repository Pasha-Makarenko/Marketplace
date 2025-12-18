from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Table,
    func,
)
from sqlalchemy.orm import composite

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.rating.rating import Rating
from marketplace.infrastructure.persistence.tables.base import mapper_registry

ratings_table = Table(
    "ratings",
    mapper_registry.metadata,
    Column("rating_id", Integer, primary_key=True, autoincrement=True),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        key="user_id_val",
    ),
    Column(
        "product_id",
        Integer,
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False,
        key="product_id_val",
        index=True,
    ),
    Column("value", Integer, nullable=False),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    CheckConstraint("value BETWEEN 1 AND 5", name="ch_ratings_value"),
)

mapper_registry.map_imperatively(
    Rating,
    ratings_table,
    properties={
        "identity": composite(Identity, ratings_table.c.rating_id),
        "user_id": composite(Identity, ratings_table.c.user_id_val),
        "product_id": composite(Identity, ratings_table.c.product_id_val),
        "value": ratings_table.c.value,
        "created_at": ratings_table.c.created_at,
    },
)
