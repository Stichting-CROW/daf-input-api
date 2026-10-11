import logging
import os

from fastapi import Request
from psycopg.conninfo import make_conninfo
from psycopg_pool import ConnectionPool

logger = logging.getLogger(__name__)


def build_conninfo() -> str:
    kwargs = {"dbname": os.getenv("DB_NAME")}
    if "DB_HOST" in os.environ:
        kwargs["host"] = os.environ["DB_HOST"]
    if "DB_USER" in os.environ:
        kwargs["user"] = os.environ["DB_USER"]
    if "DB_PASSWORD" in os.environ:
        kwargs["password"] = os.environ["DB_PASSWORD"]
    if "DB_PORT" in os.environ:
        kwargs["port"] = os.environ["DB_PORT"]
    logger.info(
        "PostgreSQL connection parameters: %s",
        {**kwargs, "password": "***" if "password" in kwargs else None},
    )
    return make_conninfo(**kwargs)


def create_pool() -> ConnectionPool:
    return ConnectionPool(
        conninfo=build_conninfo(),
        min_size=1,
        max_size=5,
        open=True,
    )


def get_db(request: Request):
    with request.app.state.pool.connection() as conn:
        yield conn
