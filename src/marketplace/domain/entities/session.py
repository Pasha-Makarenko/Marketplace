import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from marketplace.domain.entities.identity import Identity


@dataclass
class Session:
    session_id: str
    user_identity: Identity
    created_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None
    user_agent: str | None = None
    ip_address: str | None = None

    @classmethod
    def create(
        cls,
        user_id: int,
        ttl: timedelta,
        user_agent: str | None = None,
        ip_address: str | None = None,
        created_at: datetime | None = None,
        now: datetime | None = None,
    ) -> "Session":
        now = now or datetime.now(timezone.utc)
        return cls(
            session_id=str(uuid.uuid4()),
            user_identity=Identity(_value=user_id),
            created_at=created_at or datetime.now(timezone.utc),
            expires_at=now + ttl,
            user_agent=user_agent,
            ip_address=ip_address,
        )
