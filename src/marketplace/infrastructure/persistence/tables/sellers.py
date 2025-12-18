from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import composite

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.seller.seller import Seller
from marketplace.infrastructure.persistence.tables.base import mapper_registry

seller_profiles_table = Table(
    "seller_profiles",
    mapper_registry.metadata,
    Column("seller_id", Integer, primary_key=True, autoincrement=True),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    ),
    Column("store_name", String(255), nullable=False),
    Column("store_logs", String(255), nullable=True),
    Column("contact_info", Text, nullable=True),
    Column("return_policy", Text, nullable=True),
    Column("delivery_terms", Text, nullable=True),
    Column("is_active", Boolean, nullable=False, default=True),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    UniqueConstraint("user_id", name="uq_seller_profiles_user_id"),
    CheckConstraint("store_name <> ''", name="ch_seller_profiles_store_name"),
)

mapper_registry.map_imperatively(
    Seller,
    seller_profiles_table,
    properties={
        "identity": composite(Identity, seller_profiles_table.c.seller_id),
        "user_identity": composite(Identity, seller_profiles_table.c.user_id),
        "store_name": seller_profiles_table.c.store_name,
        "store_logs": seller_profiles_table.c.store_logs,
        "contact_info": seller_profiles_table.c.contact_info,
        "return_policy": seller_profiles_table.c.return_policy,
        "delivery_terms": seller_profiles_table.c.delivery_terms,
        "is_active": seller_profiles_table.c.is_active,
    },
    exclude_properties=["created_at"],
)
