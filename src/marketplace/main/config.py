import os
from dataclasses import dataclass
from typing import Literal, overload

from sqlalchemy import URL


@overload
def parse_comma_separated_values(
    env_value: str, cast_to_int: Literal[True]
) -> list[int]: ...


@overload
def parse_comma_separated_values(
    env_value: str, cast_to_int: Literal[False]
) -> list[str]: ...


def parse_comma_separated_values(
    env_value: str, cast_to_int: bool
) -> list[int] | list[str]:
    items = env_value.split(",")
    if cast_to_int:
        return [int(x) for x in items]
    else:
        return items


@dataclass(frozen=True)
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    port: int = 5432

    @property
    def url(
        self,
        driver: str = "psycopg",
        host: str | None = None,
        port: int | None = None,
    ) -> str:
        if not host:
            host = self.host
        if not port:
            port = self.port

        url = URL.create(
            drivername=f"postgresql+{driver}",
            username=self.user,
            password=self.password,
            host=host,
            port=port,
            database=self.database,
        )
        return url.render_as_string(hide_password=False)

    @classmethod
    def from_env(cls) -> "DbConfig":
        return cls(
            host=os.environ["POSTGRES_HOST"],
            password=os.environ["POSTGRES_PASSWORD"],
            user=os.environ["POSTGRES_USER"],
            database=os.environ["POSTGRES_DB"],
            port=int(os.environ["POSTGRES_PORT"]),
        )


@dataclass
class Config:
    db: DbConfig


def load_config() -> Config:
    db = DbConfig.from_env()

    return Config(
        db=db,
    )
