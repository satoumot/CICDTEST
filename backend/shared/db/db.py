from collections.abc import Iterator
from contextlib import contextmanager

import psycopg2
from psycopg2.extensions import connection as PgConnection

DB_CONFIG = {
    "host": "microservice-db",
    "port": "5432",
    "dbname": "appdb",
    "user": "appuser",
    "password": "apppass",
}


@contextmanager
def get_connection() -> Iterator[PgConnection]:
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()
