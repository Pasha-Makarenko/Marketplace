from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import composite

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.review.review import Review
from marketplace.infrastructure.persistence.tables.base import mapper_registry

reviews_table = Table(
    "reviews",
    mapper_registry.metadata,
    Column("review_id", Integer, primary_key=True, autoincrement=True),
    Column(
        "author_id",
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "product_id",
        Integer,
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("rating", Integer, nullable=False),
    Column("text", Text, nullable=True),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    CheckConstraint("rating BETWEEN 1 AND 5", name="ch_reviews_rating"),
)

mapper_registry.map_imperatively(
    Review,
    reviews_table,
    properties={
        "identity": composite(Identity, reviews_table.c.review_id),
        "author_id": composite(Identity, reviews_table.c.author_id),
        "product_id": composite(Identity, reviews_table.c.product_id),
        "rating": reviews_table.c.rating,
        "text": reviews_table.c.text,
        "created_at": reviews_table.c.created_at,
    },
)
