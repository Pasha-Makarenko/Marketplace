from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Table,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import composite

from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.user.user import User
from marketplace.domain.entities.user.value_objects import Phone
from marketplace.domain.validators import EMAIL_LENGTH
from marketplace.infrastructure.persistence.tables.base import mapper_registry

FIRST_NAME_LENGTH = 30
LAST_NAME_LENGTH = 30
PHONE_MAX_LENGTH = 20
HASHED_PASSWORD_LENGTH = 128

users_table = Table(
    "users",
    mapper_registry.metadata,
    Column("user_id", Integer, primary_key=True, autoincrement=True),
    Column("first_name", String(length=FIRST_NAME_LENGTH), nullable=False),
    Column("last_name", String(length=LAST_NAME_LENGTH), nullable=False),
    Column("email", String(length=EMAIL_LENGTH), nullable=False, unique=True),
    Column("hashed_password", String(HASHED_PASSWORD_LENGTH), nullable=False),
    Column(
        "phone",
        String(length=PHONE_MAX_LENGTH),
        nullable=False,
        key="phone_value",
    ),
    Column(
        "registered_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    UniqueConstraint("email", name="uq_users_email"),
)

mapper_registry.map_imperatively(
    User,
    users_table,
    properties={
        "identity": composite(Identity, users_table.c.user_id),
        "first_name": users_table.c.first_name,
        "last_name": users_table.c.last_name,
        "email": users_table.c.email,
        "hashed_password": users_table.c.hashed_password,
        "phone": composite(Phone, users_table.c.phone_value),
        "registered_at": users_table.c.registered_at,
    },
)
