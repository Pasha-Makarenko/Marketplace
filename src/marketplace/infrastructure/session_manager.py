from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from starlette.requests import Request
from starlette.responses import Response

from marketplace.domain.entities.session import Session
from marketplace.infrastructure.exceptions import UnauthorizedError
from marketplace.infrastructure.persistence.session_repo import (
    SQLSessionRepository,
)


@dataclass(frozen=True)
class SessionCookieDTO:
    key: str
    value: str
    httponly: bool
    max_age: int | None = None
    expires: datetime | None = None


class HTTPSessionManager:
    def __init__(
        self,
        session_repo: SQLSessionRepository,
    ) -> None:
        self._session_repo = session_repo
        self._ttl = timedelta(hours=2)

    async def init_session(
        self,
        user_id: int,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> SessionCookieDTO:
        session = Session.create(
            user_id=user_id,
            ttl=self._ttl,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        self._session_repo.add(session)

        return SessionCookieDTO(
            key="session_id",
            value=session.session_id,
            httponly=True,
            expires=session.expires_at,
            max_age=int(self._ttl.total_seconds()),
        )

    async def invalidate_session(self, session_id: str) -> None:
        session = await self._session_repo.by_identity(session_id)

        if not session:
            raise UnauthorizedError()

        session.revoked_at = datetime.now(timezone.utc)


class FastAPISessionManager:
    def __init__(self, http_session_manager: HTTPSessionManager) -> None:
        self._http_session_manager = http_session_manager

    async def init_session(
        self,
        user_id: int,
        response: Response,
        *,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> None:
        session_cookie = await self._http_session_manager.init_session(
            user_id=user_id,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        response.set_cookie(
            key=session_cookie.key,
            value=session_cookie.value,
            httponly=session_cookie.httponly,
            secure=False,
            samesite="lax",
            expires=session_cookie.expires,
            max_age=session_cookie.max_age,
        )

    async def invalidate_session(
        self, request: Request, response: Response
    ) -> None:
        session_id = request.cookies.get("session_id")

        if not session_id:
            raise UnauthorizedError()

        await self._http_session_manager.invalidate_session(session_id)

        response.delete_cookie(key="session_id")
