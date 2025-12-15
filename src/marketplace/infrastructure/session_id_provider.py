from abc import abstractmethod
from datetime import datetime, timezone
from typing import Protocol

from starlette.requests import Request

from marketplace.application.common.id_provider import IdProvider
from marketplace.domain.entities.identity import Identity
from marketplace.domain.entities.session import Session
from marketplace.domain.entities.user.repository import UserRepository
from marketplace.domain.entities.user.user import User
from marketplace.infrastructure.exceptions import UnauthorizedError
from marketplace.infrastructure.persistence.session_repo import (
    SQLSessionRepository,
)


class SessionIDGetter(Protocol):
    @abstractmethod
    def get(self) -> str | None: ...


class FastAPISessionIDGetter(SessionIDGetter):
    def __init__(self, request: Request) -> None:
        self._request = request

    def get(self) -> str | None:
        return self._request.cookies.get("session_id")


class HTTPIdentityProvider(IdProvider):
    def __init__(
        self,
        session_id_getter: SessionIDGetter,
        session_repo: SQLSessionRepository,
        user_repo: UserRepository,
    ):
        self._session_repo = session_repo
        self._user_repo = user_repo
        self._session_id_getter = session_id_getter
        self._active_session: Session | None = None

    async def _get_active_session(self) -> Session:
        if self._active_session:
            return self._active_session

        session_id = self._session_id_getter.get()
        if not session_id:
            raise UnauthorizedError()

        active_session = await self._session_repo.by_identity(session_id)

        if not active_session:
            raise UnauthorizedError()

        now = datetime.now(timezone.utc)
        if active_session.revoked_at or active_session.expires_at <= now:
            raise UnauthorizedError()

        ttl = active_session.expires_at - active_session.created_at
        active_session.expires_at = now + ttl

        self._session_repo.add(active_session)

        self._active_session = active_session
        return active_session

    async def get_current_user_id(self) -> int:
        session = await self._get_active_session()
        return int(session.user_identity.value)

    async def get_user(self) -> User:
        user_id = await self.get_current_user_id()
        user = await self._user_repo.by_identity(Identity(_value=user_id))

        if not user:
            raise UnauthorizedError()

        return user
