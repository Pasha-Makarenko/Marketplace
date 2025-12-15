from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    text,
)
from sqlalchemy.orm import composite

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.session import Session
from marketplace.infrastructure.persistence.tables.base import mapper_registry

SESSION_ID_LENGTH = 128
USER_AGENT_LENGTH = 256
IP_ADDRESS_LENGTH = 45  # supports IPv6

sessions_table = Table(
    "sessions",
    mapper_registry.metadata,
    Column(
        "session_id",
        String(length=SESSION_ID_LENGTH),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "user_id",
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    Column("revoked_at", DateTime(timezone=True), nullable=True),
    Column("user_agent", String(length=USER_AGENT_LENGTH), nullable=True),
    Column("ip_address", String(length=IP_ADDRESS_LENGTH), nullable=True),
)

mapper_registry.map_imperatively(
    Session,
    sessions_table,
    properties={
        "user_identity": composite(Identity, sessions_table.c.user_id),
    },
)
