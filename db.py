import logging
import os

from fastapi import Request
from psycopg2.pool import ThreadedConnectionPool

logger = logging.getLogger(__name__)


def build_conninfo() -> dict:
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
    return kwargs


def create_pool() -> ThreadedConnectionPool:
    return ThreadedConnectionPool(
        minconn=1,
        maxconn=5,
        **build_conninfo(),
    )


def get_db(request: Request):
    pool = request.app.state.pool
    conn = pool.getconn()
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)
